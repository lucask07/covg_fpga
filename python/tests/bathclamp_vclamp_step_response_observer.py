"""This script attempts to replicate Figure 4 on the biophysical poster. This
consists of measuring the membrane current (Im) with the AD7961 after
supplying a step voltage of 0-50mV by the AD5453.
The system uses two Daughtercards with:
 1) the bath clamp - has a non-zero CMD voltage measures Im 
 2) the voltage clamp - zero CMD voltage, goal is to hold capacitor plate at ground 

Sept 2022

Dervied from clamp_step_response.py 

Abe Stroschein, ajstroschein@stthomas.edu
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

FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6
dc_mapping = {'bath': 0, 'clamp': 1} 
DC_NUMS = [0, 1]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3

feedback_resistors = [2.1]                  # list of RF1 values; use None to get all options
capacitors = [47, 200, 1000, 4700]          # list of CCOMP values; use None to get all options

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

feedback_resistors = [2.1]
capacitors = [0,47]
bath_res = [100] # Clamp.configs['ADG_RES_dict'].keys()

# Try with different capacitors
if feedback_resistors is None:
    feedback_resistors = [x for x in Clamp.configs['RF1_dict'].keys() if type(x) == int or type(x) == float] # RF1 Resistor values in kilo-ohms for Offset Adjust amplifier
    feedback_resistors.sort()
if capacitors is None:
    capacitors = [x for x in Clamp.configs['CCOMP_dict'] if type(x) == int or type(x) == np.int32]  # CCOMP Capacitor values in pF
    capacitors.sort()

voltage_data = dict([(x, None) for x in bath_res if type(x) == int])    # Rf Resistor values in kilo-ohms for Figure 4 graph
for key in voltage_data:
    voltage_data[key] = []  # Lists to hold voltage data at each resistor value

dc_data = {}    # To store voltage data for each configuration of each daughtercard
ads_data = {}    # To store voltage data for each configuration of each daughtercard
ads_data_dict = {}
ads_seq_cnt_dict = {}

for dc_num in DC_NUMS:
    # access data with dc_data[dc_num][fb_res][cap][res]
    dc_data[dc_num] = dict([(fb_res, dict([(cap, dict(voltage_data)) for cap in capacitors])) for fb_res in feedback_resistors])
    ads_data[dc_num] = dict([(fb_res, dict([(cap, dict(voltage_data)) for cap in capacitors])) for fb_res in feedback_resistors])
    ads_data_dict[dc_num] = dict([(fb_res, dict([(cap, dict(voltage_data)) for cap in capacitors])) for fb_res in feedback_resistors])
    ads_seq_cnt_dict[dc_num]= dict([(fb_res, dict([(cap, dict(voltage_data)) for cap in capacitors])) for fb_res in feedback_resistors])

errors = copy.deepcopy(dc_data)  # Instead of voltage data, this dict will store whether an error occurred on the DDR read

# -------- configure the ADS8686
ads_voltage_range = 5  # need this for to_voltage later 
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range) 
ads.set_lpf(376)
#ads_sequencer_setup = [('0', '0'), ('1', '1'), ('2', '2')]
ads_sequencer_setup = [('1', '0')] # with Vm jumpered to U4 relay on the clamp board so it goes to CAL_ADC

codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge() # 1 MSPS rate 
ads.set_fpga_mode()

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# set observer data input muxes
obsv = Observer(f)
obsv.set_im_data_mux("ad7961_ch0")
obsv.set_vcmd_data_mux("ad5453_ch1")
obsv.set_vp1_data_mux("ads8686_chA")
obsv.set_rdy_data_mux("sync_im")

RF = bath_res[0]*1.0e3
in_amp = 1
diff_buf = 499/(120+1500) # correct, refering to signal_chain.py 
dn_per_amp = (2**15/4.096)*(RF*in_amp*diff_buf) # correct 
Im_scale = dn_per_amp/2  # DN/Amp 
Im_scale = dn_per_amp  # DN/Amp 

ads_full_scale = 10
dn_per_volt = (2**16/ads_full_scale) # correct
VP1_scale = dn_per_volt*11.0*1.7

dac_range = 5
dac_scale = 2**14*4.0/(10/(dac_range*2)) # DN/Volt TODO: verify this  # /0.58 ? 

obsv_scale = dac_scale
total_scale = 1.0/(dac_range/5)

Ldp, Bdp, Adp = eng.observer_coeff_total(400e-9, RF, capacitors[-1]*1e-12, Im_scale, VP1_scale, dac_scale, total_scale, nargout=3)

# observer coeffs
obsv_coeff = {}
max_bit_width = 0xFFFFFFFF
obsv_coeff[0] = Ldp[0][0] & max_bit_width
obsv_coeff[1] = Ldp[1][0] & max_bit_width
obsv_coeff[2] = Ldp[0][1] & max_bit_width
obsv_coeff[3] = Ldp[1][1] & max_bit_width

obsv_coeff[4] = Adp[0][0] & max_bit_width
obsv_coeff[5] = Adp[1][0] & max_bit_width
obsv_coeff[6] = Adp[0][1] & max_bit_width
obsv_coeff[7] = Adp[1][1] & max_bit_width

# zero out all but the DAC coefficients
#for i in range(8):
#    obsv_coeff[i] = 0

obsv_coeff[8] = Bdp[0][0] & max_bit_width
obsv_coeff[9] = Bdp[1][0] & max_bit_width

for oc in obsv_coeff:
    print(f'{oc}: {hex(obsv_coeff[oc])}')

obsv.change_observer_coeff(obsv_coeff)
obsv.write_observer_coeffs()

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
file_name = time.strftime("%Y%m%d-%H%M%S")
idx = 0

# set all fast-DAC DDR data to midscale
set_cmd_cc(dc_nums=[0,1,2,3], cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)
# Set CMD and CC signals - only for the bath clamp
set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=0x0600, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)

dc_configs = {}
clamp_fb_res = 2.1  # gain is 1 + clamp_fb_res/3.0 
clamp_res = 100 # kOhm should be stable 
clamp_cap = 0
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

if 1:
    for fb_res in feedback_resistors:
        for cap in capacitors:
            # Try with 5 different resistors
            for res in [x for x in bath_res if type(x) == int]:
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

                ddr.repeat_setup()
                # Get data
                # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
                infile = file_name.format(idx) + '.h5'
                chan_data_one_repeat = ddr.save_data(data_dir, infile, num_repeats=8,
                                                    blk_multiples=40)  # blk multiples multiple of 10

                # to get the deswizzled data of all repeats need to read the file
                _, chan_data = read_h5(data_dir, infile, chan_list=np.arange(8))

                adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, reading_error = ddr.data_to_names(chan_data)
                print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

                ############### extract the ADS data just for the last run and plot as a demonstration ############
                ads_data_v = {}
                for letter in ['A', 'B']:
                    ads_data_v[letter] = np.array(to_voltage(
                        ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

                total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
                total_seq_cnt[::2] = ads_seq_cnt[0]
                total_seq_cnt[1::2] = ads_seq_cnt[1]
                ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)

                ephys_sys = EphysSystem()
                sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)
                datastreams, log_info = rawh5_to_datastreams(data_dir, infile, ddr.data_to_names, daq, sys_connections, outfile = None)

                # Store voltage in list; plot
                for dc_num in DC_NUMS:
                    dc_data[dc_num][fb_res][cap][res] = to_voltage(
                        adc_data[dc_num], num_bits=16, voltage_range=10, use_twos_comp=True)
                    ads_data_dict[dc_num][fb_res][cap][res] = ads_data    
                    ads_seq_cnt_dict[dc_num][fb_res][cap][res] = ads_seq_cnt    
                    errors[dc_num][fb_res][cap][res] = reading_error

                # TODO: save as datastream h5s


    print('Data collected. DDR read error report below.')
    print('|'.join([x.center(6, ' ') for x in ['dc_num', 'fb_res', 'cap', 'res', 'ERROR']]))
    error_cnt = 0
    for dc_num in errors:
        for fb_res in errors[dc_num]:
            for cap in errors[dc_num][fb_res]:
                for res in errors[dc_num][fb_res][cap]:
                    if errors[dc_num][fb_res][cap][res]:
                        # An error occurred in the DDR read
                        print('|'.join([str(x).center(6, ' ') for x in [dc_num, fb_res, cap, res, 'ERROR']]))
                        error_cnt += 1
    print('Total DDR read errors:', error_cnt)
    print('Plotting...')

    # Time in seconds
    t = np.arange(0, len(adc_data[0]))*1/FS
    for dc_num in DC_NUMS:
        for fb_res in dc_data[dc_num].keys():
            rows = ceil(len(capacitors)**(1/2))
            fig, axes = plt.subplots(rows, rows)
            fig.suptitle(f'DC{dc_num} Current response to CMD step voltage (RF1={fb_res})')

            for i in range(len(capacitors)):
                cap = capacitors[i]
                current_ax = axes[i // rows][i % rows]
                current_ax.set_title(f'CCOMP={cap}pF')
                current_ax.set_xlabel('Time (\N{GREEK SMALL LETTER MU}s)')
                current_ax.set_ylabel('Current (\N{GREEK SMALL LETTER MU}A)')
                
                for res in dc_data[dc_num][fb_res][cap].keys():
                    # Plot current (uA) against time (us) -> uA because resistor values are in kilo-ohms, we multiply current by 1e3
                    current_ax.plot(t * 1e6, [(v / res) * 1e3 for v in dc_data[dc_num][fb_res][cap][res]], label=str(res) + 'k\N{GREEK CAPITAL LETTER OMEGA}')
                    # Zoom in on the data
                    current_ax.set_xlim(6550, 7000)
                    current_ax.set_ylim(-10, 40)
                
                # Set up the legend after the first subplot so there are no repeat labels from following subplots
                if i == 0:
                    fig.legend(loc='lower right')

ddr.repeat_setup() # Get data

# saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                    blk_multiples=40)  # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(
    idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file
adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = ddr.data_to_names(chan_data)

def ads_plot_zoom(ax):
    for ax_s in ax:
        ax_s.set_xlim([3250, 3330])
        ax_s.grid('on')

# update system connections since the daughtercard configurations have changed
sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)

# Plot using datastreams 
datastreams, log_info = rawh5_to_datastreams(data_dir, infile, ddr.data_to_names, daq, sys_connections, outfile = None)
fig, ax = plt.subplots(2,1)
fig.suptitle('ADS data')
# AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane
datastreams['P1'].plot(ax[0], {'marker':'.'})
# CAL ADC : observing electrode P2 (configured by CAL_SIG2)
try:
    datastreams['P2'].plot(ax[1], {'marker':'.'})
except:
    print('P2 is not measured')

fig, ax = plt.subplots()
fig.suptitle('Overlay P1 and CMD')
datastreams['P1'].plot(ax, {'marker':'.'})
datastreams['CMD0'].plot(ax, {'marker':'.'})  

fig, ax = plt.subplots(4,1)
fig.suptitle('Overlay OBSERVER and I')
datastreams['OBSV'].plot(ax[0], {'marker':'.'})
datastreams['I'].plot(ax[1], {'marker':'.'})  
ax[2].plot(dac_data[1].astype(np.int32)-0x1FFF, marker='.')  
ax[2].set_ylabel('CMD offset DAC')
#datastreams['PI_ERR'].plot(ax[3], {'marker':'.'})  

print(f'Max - min of Observer: {np.max(datastreams["OBSV"].data)-np.min(datastreams["OBSV"].data)}')
print(f'Max - min of DDR: {np.max(ddr.data_arrays[1]) - np.min(ddr.data_arrays[1])}')
print(f'Max - min of DAC data: {np.max(dac_data[1]) - np.min(dac_data[1])}')

fig, ax = plt.subplots()
cmd_arr = ((dac_data[1].astype(np.int16)-0x1fff)[::5])
obsv_arr = dac_data[4][::2].astype(np.int16)
pi_error_est = cmd_arr - obsv_arr
ax.plot(pi_error_est, label='pi_error')
ax.plot(cmd_arr, label='cmd')
ax.plot(obsv_arr, label='obsv')
ax.legend()

# estimate Im 
Cm = 33e-9
fig, ax = plt.subplots()
fig.suptitle('Overlay Meas. Im and Im estimate')
datastreams['Im'].plot(ax, {'marker':'.', 'label': 'Meas. Im'})
t = datastreams['P1'].create_time()
dt = t[1] - t[0]
p1_diff = np.diff(datastreams['P1'].data)/dt
ax.plot(t[:-1]*1e6, -Cm*p1_diff, label='Im estimate via p1')
ax.legend()

# subplot of Observer Vm and measured Vm
fig,ax=plt.subplots(3,1)
fig.suptitle('Observer Vm vs ADS8686')
# Observer - stored in DDR at 1 MSPS -- dac_data[4] is observer output 0, dac_data[5] is observer output 1, dac_data[6] is obs. output 0 shifted by 400 ns
datastreams['OBSV'].plot(ax[0], {'marker':'.', 'label': 'Obsv.'})
datastreams['PI_ERR'].plot(ax[0], {'marker':'.', 'label': 'PI_ERR.'})
ax[0].legend()
datastreams['I'].plot(ax[1], {'marker':'.', 'label': 'Vm Meas.'})
datastreams['P1'].plot(ax[1], {'marker':'*', 'label': 'P1'})
ax[1].plot(datastreams['OBSV'].create_time()*1e6, datastreams['OBSV'].data/3000*0.1, marker='o', label='OBSV')
ax[1].legend()
datastreams['CMD0'].plot(ax[2])

ax[1].set_ylabel('Vm measured [V]')
for axi in ax:
    axi.set_xlim([3250, 3400])

# add log info to datastreams -- any dictionary is ok  
datastreams.add_log_info(ephys_sys.__dict__)  # all properties of ephys_sys 
datastreams.add_log_info({'dc_configs': dc_configs})

print(datastreams.__dict__)
# test writing and reading datastream h5
datastreams.to_h5(data_dir, 'test.h5', log_info)
datastreams2 = h5_to_datastreams(data_dir, 'test.h5')
# this datastreams has the log info but as a dictionary, not as Python classes
# if the original objects are needed could use these methods https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object

for n in datastreams:
    assert (datastreams[n].data == datastreams2[n].data).all(), f'Datastream data with key {n} after writing and reading from file are not equal!'


print(f'CMD scaling for observer {1/dac_scale} [DN/Volt] and from datastreams {datastreams["CMD0"].conversion_factor}')
print(f'Im scaling for observer  {1/Im_scale} [DN/Amp] and from datastreams {datastreams["Im"].conversion_factor}')
print(f'P1 scaling for observer {1/VP1_scale} [DN/Volt] and from datastreams {datastreams["P1"].conversion_factor}')

def stepinfo_range(ds, time_range):
    t = ds.create_time()
    idx = (t>=time_range[0]) & (t<=time_range[1])
    y = ds.data[idx]
    t = t[idx]

    si = stepinfo(y, t)

    return si

t_step = 3.277e-3
print('-'*100)
for sig in ['I', 'OBSV', 'P1', 'CMD0']:
    sig_name = sig 
    if sig_name == 'I':
        sig_name = 'Vm'
    si = stepinfo_range(datastreams[sig], [t_step-0.02e-3, t_step+170e-6])
    print(f'{sig} step info: {si}')
    print('-'*100)

for oc in obsv_coeff:
    print(f'{oc}: {hex(obsv_coeff[oc])}')