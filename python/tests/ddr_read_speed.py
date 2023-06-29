"""This script studies the read and write speed to and from 
DDR using the address pointers available from the FPGA.

corresponding Excel sheet is in docs/ddr_rates.xlsx

June 2023

Dervied from clamp_step_response.py 
Lucas Koerner, koerner.lucas@stthomas.edu
"""

from math import ceil
import os
import sys
from time import sleep
import datetime
import time
import atexit
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
import copy

from pyripherals.utils import to_voltage, from_voltage, create_filter_coefficients
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3
import matlab.engine 
from control.matlab import stepinfo

# The boards.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == "covg_fpga":
        boards_path = os.path.join(covg_fpga_path, "python")
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(boards_path)

from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5, separate_ads_sequence
from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp
from calibration.electrodes import EphysSystem
from observer import Observer
from filters.filter_tools import butter_lowpass_filter

from instrbuilder.instrument_opening import open_by_name 
osc = open_by_name('msox_scope')

eng = matlab.engine.start_matlab()
eng.addpath('..\\Matlab\\control_system\\observer\\full_closed_loop\\')

def make_cmd_cc(cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None):
    """Return the CMD and CC signals determined by the parameters.
    
    Parameters
    ----------
    
    Returns
    -------
    np.ndarray, np.ndarray : the CMD signal data, the CC signal data.
    """

    dac_offset = 0x2000

    cmd_signal = ddr.make_step(
        low=dac_offset - int(cmd_val), high=dac_offset + int(cmd_val), length=step_len)  # 1.6 ms between edges

    if fc is not None:
        cmd_signal = butter_lowpass_filter(cmd_signal, cutoff=fc, fs=2.5e6, order=1)

    # create the cc using multiple methods
    if cc_pickle_num is not None:
        cc_impulse_scale = -2600/7424
        out = get_cc_optimize(cc_pickle_num)
        cc_wave = adjust_step2(
            out['x'], cmd_signal.astype(np.int32) - dac_offset)
        cc_wave = cc_wave * cc_impulse_scale
        cc_wave = cc_wave + dac_offset
        if cc_delay != 0:
            # 2.5e6 is the sampling rate
            cc_wave = delayseq_interp(cc_wave, cc_delay, 2.5e6)
        cc_signal = cc_wave.astype(np.uint16)

    elif cc_val is None:  # get the cc signal from scaling the cmd signal
        if fc is not None:
            cc_signal = butter_lowpass_filter(
                cmd_signal - dac_offset, cutoff=fc, fs=2.5e6, order=1)*cc_scale + dac_offset
        else:
            cc_signal = (
                cmd_signal - dac_offset)*cc_scale + dac_offset
        if cc_delay != 0:
            cc_signal = delayseq_interp(
                cc_signal, cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    else:  # needed so that the cmd signal can be zero with a non-zero cc signal
        cc_signal = ddr.make_step(low=dac_offset - int(cc_val),
                                               high=dac_offset + int(cc_val),
                                               length=step_len)  # 1.6 ms between edges
        if fc is not None:
            cc_signal = butter_lowpass_filter(
                cc_signal, cutoff=fc, fs=2.5e6, order=1)
        if cc_delay != 0:
            cc_signal = delayseq_interp(
                cc_signal, cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    return cmd_signal, cc_signal


def set_cmd_cc(dc_nums, cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None):
    """Write the CMD and CC signals to the DDR for the specified daughtercards.
    
    Parameters
    ----------
    dc_nums : int or list
        The port number(s) of the daughtercard(s) to write signals for.

    Returns
    -------
    None
    """

    # TODO: move to Clamp board class in boards.py
    if (type(dc_nums) == int):
        dc_nums = [dc_nums]
    elif (type(dc_nums) != list):
        raise TypeError('dc_nums must be int or list')

    for dc_num in dc_nums:
        cmd_ch = dc_num * 2 + 1 # TODO: replace with daq.parameters['fast_dac_map']
        cc_ch = dc_num * 2
        ddr.data_arrays[cmd_ch], ddr.data_arrays[cc_ch] = make_cmd_cc(cmd_val=cmd_val, cc_scale=cc_scale, cc_delay=cc_delay, fc=fc, step_len=step_len, cc_val=cc_val, cc_pickle_num=cc_pickle_num)
    
    # write channels to the DDR
    ddr.write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()


def stepinfo_range(ds, time_range):
    t = ds.create_time()
    idx = (t>=time_range[0]) & (t<=time_range[1])
    y = ds.data[idx]
    t = t[idx]

    try:
        si = stepinfo(y, t)
    except:
        si = None

    return si


FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6
dc_mapping = {'bath': 0, 'clamp': 1} 
DC_NUMS = [0, 1]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3


eps = Endpoint.endpoints_from_defines
pwr_setup = "3dual"

# TODO: at data directories like this to a config file
data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    pass
elif sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp_test/{}{:02d}{:02d}"
elif sys.platform == "win32":
    if os.path.exists('C:/Users/ajstr/OneDrive - University of St. Thomas/Research Internship/clamp_step_response_data'):
        data_dir_covg = 'C:/Users/ajstr/OneDrive - University of St. Thomas/Research Internship/clamp_step_response_data/{}{:02d}{:02d}'
    else:
        data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')

today = datetime.datetime.today()
data_dir = data_dir_covg.format(
    today.year, today.month, today.day
)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)
if pwr_setup == "3dual":
    atexit.register(pwr_off, [dc_pwr])
else:
    atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)

# turn on the 7V
dc_pwr.set("out_state", "ON", configs={"chan": 1})

if pwr_setup != "3dual":
    # turn on the +/-16.5 V input
    for ch in [1, 2]:
        dc_pwr2.set("out_state", "ON", configs={"chan": ch})
elif pwr_setup == "3dual":
    # turn on the +/-16.5 V input
    for ch in [2, 3]:
        dc_pwr.set("out_state", "ON", configs={"chan": ch})


# Initialize FPGA
f = FPGA()
f.init_device()
sleep(2)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)
ddr = daq.ddr
ad7961s = daq.ADC
ad7961s[0].reset_wire(1)    # Only actually one WIRE_RESET for all AD7961s

ads = daq.ADC_gp

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

# configure the SPI debug MUXs
gpio = Daq.GPIO(f)
gpio.spi_debug("ads")
gpio.ads_misc("convst")  # to check sample rate of ADS

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamps = [None] * 4
for dc_num in DC_NUMS:
    clamp = Clamp(f, dc_num=dc_num)
    print(f'Clamp {dc_num} Init'.center(35, '-'))
    clamp.init_board()
    clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
    clamps[dc_num] = clamp

dac_range = 5
feedback_resistors = [2.1]
capacitors = [47]
bath_res = [10] # Clamp.configs['ADG_RES_dict'].keys()

# -------- configure the ADS8686
ads_voltage_range = 5  # need this for to_voltage later 
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range) 
ads.set_lpf(376)
#ads_sequencer_setup = [('0', '0'), ('1', '1'), ('2', '2')]
ads_sequencer_setup = [('1', '0'), ('2', '0')] # with Vm jumpered to U4 relay on the clamp board so it goes to CAL_ADC

codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge() # 1 MSPS rate 
ads.set_fpga_mode()

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channels setup
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    #daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("DDR")
    #daq.DAC[i].set_data_mux("DDR_norepeat", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name
    daq.DAC[i].set_data_mux("DDR", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, dac_range)  # 5V 

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.5)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(2)
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset
time.sleep(1)

# ------ Collect Data --------------
file_name = 'test' + time.strftime("%Y%m%d-%H%M%S") + '_{}'
idx = 0

# set all fast-DAC DDR data to midscale
set_cmd_cc(dc_nums=[0,1,2,3], cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)
# Set CMD and CC signals - only for the bath clamp
fc_cmd = 10e3
#fc_cmd = None
set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=0x0800, cc_scale=0, cc_delay=0, fc=fc_cmd,
        step_len=16384, cc_val=None, cc_pickle_num=None)

dc_configs = {}
clamp_fb_res = 60 # resistors and cap have changed so this does not correspond to typical bath clamp board  LJK was 3
clamp_res = 10000 # should be zero with modified board when set to 10 MOhms 
clamp_cap = 47

for dc_num in [dc_mapping['clamp']]:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1", # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize jumpered Vm 
        DAC_SEL="noDrive", # must not be drive_CAL2 
        CCOMP=clamp_cap,
        RF1=clamp_fb_res,  # feedback circuit
        ADG_RES=clamp_res,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=0,
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict
    
    
cap = capacitors[0]
fb_res = feedback_resistors[0]
# Try with 5 different resistors
res = [x for x in bath_res if type(x) == int][0]
                # Choose resistor; setup
for dc_num in [dc_mapping['bath']]:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1",  # required to digitize P2 
        DAC_SEL="noDrive",
        CCOMP=cap,
        RF1=fb_res,  # feedback circuit
        ADG_RES=res,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=1,
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict


ephys_sys = EphysSystem()
sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)

def get_ddr_pointers():
    adc_start_idx = daq.ddr.PORT1_INDEX
    dac_rd = daq.ddr.fpga.read_wire(daq.ddr.endpoints['ADDR_DAC_RD'].address)
    adc_rd = daq.ddr.fpga.read_wire(daq.ddr.endpoints['ADDR_ADC_RD'].address) - adc_start_idx
    adc_wr = daq.ddr.fpga.read_wire(daq.ddr.endpoints['ADDR_ADC_WR'].address) - adc_start_idx

    print('ADDR_DAC_WR:', daq.ddr.fpga.read_wire(daq.ddr.endpoints['ADDR_DAC_WR'].address))
    print('ADDR_DAC_RD:', dac_rd)
    print('ADDR_ADC_WR:', adc_wr)
    print('ADDR_ADC_RD:', adc_rd) #896 difference from index without a DDR.save_data (probably because some fills the FIFO)

    return dac_rd, adc_rd, adc_wr

def capture_track_pointers(loops, READ=True):

    pointers = {'dac_rd': np.array([]), 'adc_rd': np.array([]), 'adc_wr': np.array([]), 'time': np.array([])}

    for idx in range(loops):
        
        print(idx)
        # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
        chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                            blk_multiples=400)  # blk multiples must be multiple of 10 
        # each block multiple is 256 bytes 
        dac_rd, adc_rd, adc_wr = get_ddr_pointers()

        pointers['dac_rd'] = np.append(pointers['dac_rd'], dac_rd)
        pointers['adc_rd'] = np.append(pointers['adc_rd'], adc_rd)
        pointers['adc_wr'] = np.append(pointers['adc_wr'], adc_wr)
        pointers['time'] = np.append(pointers['time'], time.time_ns())

        if adc_rd > 2.0e8 and adc_wr == 209715200: # if the adc_rd pointer is nearly done and the adc_wr pointer is stalled at the end
            # allow adc_wr to roll-over and reset the ADC input FIFO 
            print('Setting ADC Write rollover bit')
            dac_rd, adc_rd, adc_wr = get_ddr_pointers()
            daq.fpga.set_wire_bit(daq.ddr.endpoints['FIFO_ADC_IN_RST'].address, 
                        daq.ddr.endpoints['FIFO_ADC_IN_RST'].bit_index_low)
            daq.fpga.set_wire_bit(daq.ddr.endpoints['ADC_WRITE_ROLLOVER'].address, 
                                  daq.ddr.endpoints['ADC_WRITE_ROLLOVER'].bit_index_low)
            daq.fpga.clear_wire_bit(daq.ddr.endpoints['FIFO_ADC_IN_RST'].address, 
                        daq.ddr.endpoints['FIFO_ADC_IN_RST'].bit_index_low)
            daq.fpga.clear_wire_bit(daq.ddr.endpoints['ADC_WRITE_ROLLOVER'].address, 
                        daq.ddr.endpoints['ADC_WRITE_ROLLOVER'].bit_index_low)                        
            print('Done setting ADC Write rollover bit')
            dac_rd, adc_rd, adc_wr = get_ddr_pointers()

        if READ == True:
            # to get the deswizzled data of all repeats need to read the file
            _, chan_data = read_h5(data_dir, file_name=file_name.format(
                idx) + '.h5', chan_list=np.arange(8))
            # Long data sequence -- entire file
            # adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = ddr.data_to_names(chan_data)
            # Plot using datastreams 
            datastreams, log_info = rawh5_to_datastreams(data_dir, infile, ddr.data_to_names, daq, sys_connections, outfile = None)

    return pointers

ddr.repeat_setup() # Get data
pointers = capture_track_pointers(200, READ=False) # multiple reads and track the DDR address pointers 
fig, ax = plt.subplots(2,1)
ax[0].plot(pointers['adc_wr'], 'k', label='write', marker='o') # each address pointer is 4 bytes 
ax[0].plot(pointers['adc_rd'], 'r', label='read', marker='o')
ax[0].plot(pointers['dac_rd'], 'g', label='DAC read', marker='o')
ax[1].plot((pointers['time']-pointers['time'][0])/1e9)
ax[0].legend()
# 1.6 read to 7.2 write 
# 5.7 with the time.sleep removed 