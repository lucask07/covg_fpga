"""This script takes series resistance copmensation measurements for varying 
alpha values. This consists of measuring the membrane current (Im) with the AD7961 after
supplying a step voltage of 0-50mV by the AD5453 and adding it back to the AD5453
command voltage. This is done with a feedback resistance of 100K.

July 2022

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
Ian Delgadillo Bonequi, delg5279@stthomas.edu
"""

from math import ceil
import os
import sys
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
import copy
from pyripherals.utils import to_voltage, from_voltage, create_filter_coefficients
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3

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
from analysis.adc_data import read_h5
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp


def ddr_write_setup():
    ddr.set_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.clear_adc_read()    # Stop putting data in outgoing FIFO for Pipe read
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()


def ddr_repeat_setup():
    """Setup for reading new data without writing to the DDR again."""

    # stop access to the FIFOs so that after reset of the FIFO(s) no new data is added/extracted
    ddr.clear_adc_read()
    ddr.clear_adc_write()
    ddr.clear_dac_read()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()  # self.fpga.send_trig(self.endpoints['UI_RESET'])
    # note that the MIG interface addresses are driven by the FIFOs so will idle
    # until the FIFOs are reenable with ddr_write_finish()
    ddr_write_finish()
    time.sleep(0.01)


def ddr_write_finish():
    # reenable both DACs
    ddr.set_adc_dac_simultaneous()  # enable DAC playback and ADC writing to DDR


def get_cc_optimize(nums):

    data_dir_base = os.path.expanduser('~')
    data_dir_covg = os.path.join(
        data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')
    data_dir = data_dir_covg.format(2022, 1, 19)

    #for nums in ([20,21], [30,31], [14,15], [40,41]):
    with open(os.path.join(data_dir, 'basin_hop_cc_nums{}.pickle'.format(nums[0])), 'rb') as fp:
        out = pkl.load(fp)
    return out


def make_cmd_cc(cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None):
    """Return the CMD and CC signals determined by the parameters.
    
    Parameters
    ----------
    
    Returns
    -------
    np.ndarray, np.ndarray : the CMD signal data, the CC signal data.
    """

    # TODO: move to Clamp board class in boards.py
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
        cmd_ch = dc_num * 2 + 1
        cc_ch = dc_num * 2
        ddr.data_arrays[cmd_ch], ddr.data_arrays[cc_ch] = make_cmd_cc(cmd_val=cmd_val, cc_scale=cc_scale, cc_delay=cc_delay, fc=fc, step_len=step_len, cc_val=cc_val, cc_pickle_num=cc_pickle_num)
    
    # write channels to the DDR
    ddr_write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr_write_finish()

FS = 5e6
SAMPLE_PERIOD = 1/FS
DC_NUMS = [0, 1, 2, 3]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3

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

# ------ oscilloscope -----------------
osc = open_by_name("msox_scope")
osc.set("chan_label", '"Vm"', configs={"chan": 1})
#osc.set("chan_label", '"Vm1"', configs={"chan": 4}) # label must be in "" for the scope to accept
osc.comm_handle.write(':DISP:LAB 1')  # turn on the labels
osc.set('chan_display', 0, configs={"chan": 4})
osc.set('chan_display', 0, configs={'chan': 2})
osc.set('chan_display', 0, configs={"chan": 3})

# Initialize FPGA
f = FPGA()
f.init_device()
sleep(2)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)
ddr = DDR3(f, data_version='TIMESTAMPS')
ad7961s = daq.ADC
ad7961s[0].reset_wire(1)    # Only actually one WIRE_RESET for all AD7961s

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

# configure the SPI debug MUXs
gpio = Daq.GPIO(f)
gpio.spi_debug("dfast1")
gpio.ads_misc("sdoa")  # do not care for this experiment

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamps = [None] * 4
for dc_num in DC_NUMS:
    clamp = Clamp(f, dc_num=dc_num)
    print(f'Clamp {dc_num} Init'.center(35, '-'))
    clamp.init_board()
    clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
    clamps[dc_num] = clamp

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.1)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(1)

# TODO: are the TCA pins already configured in Clamp.configure_clamp()?
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S")
idx = 0

# Set CMD and CC signals
set_cmd_cc(dc_nums=DC_NUMS, cmd_val=0x0300, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)

print('Configuring for oscilloscope: CCOMP=47, RF1=2.1, ADG_RES=100')
# Configure for better oscilloscope viewing
for dc_num in DC_NUMS:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="drive_CAL2",
        CCOMP=47,
        RF1=2.1,  # feedback circuit
        ADG_RES=100,
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

#specify number of alpha values to loop through
num_alphas = 20
start_alpha = 0
end_alpha = 0.95
alpha = np.linspace(start_alpha, end_alpha, num_alphas)

for alphas in range (num_alphas):

    #define values for ADG_RES (in kilo-ohms), inamp gain, and DAC output amplitude (in millivolts)
    ADG_RES_Val = 100
    inamp_gain = 1
    DAC_gain_amplitude = 5000
    fbck_gain = 1.697
    #scale value is calculated as:
    series_res_scale = (1/(ADG_RES_Val*1e3))*(1/0.308)*(1/inamp_gain)*1000*(8192/DAC_gain_amplitude)*(fbck_gain*0.5)*10*alpha[alphas]
    print("scale value =", series_res_scale)

    filter_coeff_generated = create_filter_coefficients(fc=500e3, output_scale=series_res_scale*2**13)
    #for i in range (num_alphas):
    #    filter_coeff_generated = create_filter_coefficients(fc=500e3, output_scale=series_res_scale[i]*2**13)
    #    print(filter_coeff_generated)

    for i in [1]:
        daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
        daq.DAC[i].set_spi_sclk_divide()
        daq.DAC[i].filter_select(operation="set")
        daq.DAC[i].write(int(0))
        daq.DAC[i].set_data_mux("DDR")
        daq.DAC[i].set_data_mux("ad7961_ch0", filter_data=True)
        daq.DAC[i].filter_sum("set")
        daq.DAC[i].filter_downsample("set")
        daq.DAC[i].change_filter_coeff(target="generated", value=filter_coeff_generated)
        daq.DAC[i].write_filter_coeffs()
        daq.set_dac_gain(0, 5)  # 5V to see easier on oscilloscope

    for i in [3]:
        daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
        daq.DAC[i].set_spi_sclk_divide()
        daq.DAC[i].filter_select(operation="set")
        daq.DAC[i].write(int(0))
        daq.DAC[i].set_data_mux("DDR")
        daq.DAC[i].set_data_mux("ad7961_ch1", filter_data=True)
        daq.DAC[i].filter_sum("set")
        daq.DAC[i].filter_downsample("set")
        daq.DAC[i].change_filter_coeff(target="generated", value=filter_coeff_generated)
        daq.DAC[i].write_filter_coeffs()
        daq.set_dac_gain(2, 5)  # 5V to see easier on oscilloscope

    time.sleep(0.1)
    ddr_repeat_setup()
    # Get data
    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                        blk_multiples=40)  # blk multiples multiple of 10

    osc.set('single_acq')
    time.sleep(0.1)

    # general measure -- input measure type
    #for ch in [1,4]:
    #    time.sleep(0.01)
    #    rt = osc.get('meas', configs={'meas_type':'RIS', 'chan':ch})
    #    #data[f'rise_{ch}'] = rt
    #    va = osc.get('meas', configs={'meas_type':'VAMP', 'chan':ch})
    #    #data[f'amp_{ch}'] = va

    # save a PNG screen-shot to host computer
    series_res_file_name = "alpha_equals_" + str(round(alpha[alphas], 2))
    t = osc.save_display_data(os.path.join(r"C:\Users\delg5279\OneDrive - University of St. Thomas\SeriesResistanceTests", series_res_file_name))
    time.sleep(0.1)
    osc.set('run_acq')

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(
        idx) + '.h5', chan_list=np.arange(8))

    # Long data sequence -- entire file
    adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data)

    # Shorter data sequence, just one of the repeats
    # adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data_one_repeat)

    t = np.arange(0,len(adc_data[0]))*1/FS

    crop_start = 0 # placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
    print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')


# DACs
t_dacs = t[crop_start::2]  # fast DACs are saved every other 5 MSPS tick
for dac_ch in range(4):
    fig,ax=plt.subplots()
    y = dac_data[dac_ch][crop_start:]
    lbl = f'Ch{dac_ch}'
    ax.plot(t_dacs*1e6, y, marker = '+', label = lbl)
    print(f'Min {np.min(y[2:])}, Max {np.max(y)}') # skip the first 2 readings which are 0
    if (dac_ch == 1 or dac_ch == 3):
        y = to_voltage(adc_data[round((dac_ch-1)/2)][crop_start:], num_bits=16, voltage_range=2**14, use_twos_comp=True)
        lbl = f'Ch{round((dac_ch-1)/2)}'
        ax.plot(t*1e6, y, marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Fast DAC data')
    ax.set_xlabel('s [us]')

# fast ADC. AD7961
for ch in range(2):
    fig,ax=plt.subplots()
    # Store voltage in list; plot
    y = to_voltage(adc_data[ch][crop_start:], num_bits=16, voltage_range=2**16, use_twos_comp=True)
    lbl = f'Ch{ch}'
    ax.plot(t*1e6, y, marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Fast ADC data')
    ax.set_xlabel('s [us]')
    ax.set_ylabel('ADC codes')