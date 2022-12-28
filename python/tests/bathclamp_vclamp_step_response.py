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
from datastream.datastream import create_sys_connections, rawh5_to_datastreams
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp


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
        cmd_ch = dc_num * 2 + 1
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
ddr = daq.ddr    # Or reference as daq.ddr throughout the file
ddr.parameters['data_version'] = 'TIMESTAMPS'
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

# -------- configure the ADS8686
ads_voltage_range = 5  # need this for to_voltage later 
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range) # TODO: make an ads.current_voltage_range a property of the ADS so we always know it
ads.set_lpf(376)
# 4B - clear sine wave set by the Slow DAC
ads_sequencer_setup = [('0', '0'), ('1', '1')]
codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge(clk_div=200) # 1 MSPS rate (do not use default value which is 200 ksps)
ads.set_fpga_mode()

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channels setup
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("DDR")
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.1)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(1)
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S")
idx = 0

feedback_resistors = [2.1]
capacitors = [0, 47, 247, 1247]
bath_res = [100, 332, 1000] # Clamp.configs['ADG_RES_dict'].keys()

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

# set all fast-DAC DDR data to midscale
set_cmd_cc(dc_nums=[0,1,2,3], cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)
# Set CMD and CC signals - only for the bath clamp
set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=0x0300, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)

dc_configs = {}
clamp_fb_res = 2.1
clamp_res = 332 # kOhm should be stable 
clamp_cap = 47
for dc_num in [dc_mapping['clamp']]:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="drive_CAL2",
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

if 1:
    for fb_res in feedback_resistors:
        for cap in capacitors:
            # Try with 5 different resistors
            for res in [x for x in bath_res if type(x) == int]:
                # Choose resistor; setup
                for dc_num in [dc_mapping['bath']]:
                    log_info, config_dict = clamps[dc_num].configure_clamp(
                        ADC_SEL="CAL_SIG1",
                        DAC_SEL="drive_CAL2",
                        CCOMP=cap,
                        RF1=fb_res,  # feedback circuit
                        ADG_RES=res,
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

                ddr.repeat_setup()
                # Get data
                # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
                infile = file_name=file_name.format(idx) + '.h5'
                chan_data_one_repeat = ddr.save_data(data_dir, infile, num_repeats=8,
                                                    blk_multiples=40)  # blk multiples multiple of 10

                # to get the deswizzled data of all repeats need to read the file
                _, chan_data = read_h5(data_dir, infile, chan_list=np.arange(8))

                adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, reading_error = ddr.data_to_names(chan_data)
                print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

                create_sys_connections(dc_configs, daq, ads, system='daq_v2')
                datastreams = rawh5_to_datastreams(data_dir, infile, ddr.data_to_names, ads_sequencer_setup, outfile = None)

                # Store voltage in list; plot
                for dc_num in DC_NUMS:
                    dc_data[dc_num][fb_res][cap][res] = to_voltage(
                        adc_data[dc_num], num_bits=16, voltage_range=10, use_twos_comp=True)
                    ads_data_dict[dc_num][fb_res][cap][res] = ads_data    
                    ads_seq_cnt_dict[dc_num][fb_res][cap][res] = ads_seq_cnt    
                    errors[dc_num][fb_res][cap][res] = reading_error


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


ddr.repeat_setup()
# Get data
# saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                    blk_multiples=40)  # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(
    idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file
adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = ddr.data_to_names(chan_data)

############### extract the ADS data just for the last run and plot as a demonstration ############
ads_data_v = {}
for letter in ['A', 'B']:
    ads_data_v[letter] = np.array(to_voltage(
        ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
total_seq_cnt[::2] = ads_seq_cnt[0]
total_seq_cnt[1::2] = ads_seq_cnt[1]
ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)

fig, ax = plt.subplots(2,1)
fig.suptitle('ADS data')
# AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane
t_ads = np.arange(len(ads_separate_data['A'][1]))*1/(ADS_FS / len(ads_sequencer_setup))
ax[0].plot(t_ads*1e6, ads_separate_data['A'][1], marker='.')
ax[0].set_ylabel('P1 (tracks Vm) [V]')
# CAL ADC : observing electrode P2 (configured by CAL_SIG2)
t_ads = np.arange(len(ads_separate_data['A'][0]))*1/(ADS_FS / len(ads_sequencer_setup))
ax[1].plot(t_ads*1e6, ads_separate_data['A'][0], marker='.')
ax[1].set_ylabel('P2 [V]')

for ax_s in ax:
    ax_s.set_xlabel('t [$\mu$s]')

def ads_plot_zoom(ax):
    for ax_s in ax:
        ax_s.set_xlim([3250, 3330])
        ax_s.grid('on')

####### RS compensation test #############
RS_COMP_TESTS = False
if RS_COMP_TESTS:
    #specify number of alpha values to loop through
    num_alphas = 10
    start_alpha = 0.5
    end_alpha = 0.95
    alpha = np.linspace(start_alpha, end_alpha, num_alphas)

    for alphas in range (num_alphas):

        #define values for ADG_RES (in kilo-ohms), inamp gain, and DAC output amplitude (in millivolts)
        ADG_RES_Val = 100
        inamp_gain = 1
        DAC_gain_amplitude = 500
        correction_factor = 0.5*0.161
        #scale value is calculated as:
        #series_res_scale = (1/(ADG_RES_Val*1e3))*(1/0.308)*(1/inamp_gain)*1000*(8192/DAC_gain_amplitude)*(4096/DAC_gain_amplitude)*10*alpha[alphas]
        series_res_scale = (1/(ADG_RES_Val*1e3))*(1/0.308)*(1/inamp_gain)*1000*(8192/DAC_gain_amplitude)*(correction_factor)*10*alpha[alphas]
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
            daq.set_dac_gain(i, 500)  # 5V to see easier on oscilloscope

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
            daq.set_dac_gain(i, 500)  # 5V to see easier on oscilloscope

        ddr.repeat_setup()
        # Get data
        # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
        chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                            blk_multiples=40)  # blk multiples multiple of 10

        # to get the deswizzled data of all repeats need to read the file
        _, chan_data = read_h5(data_dir, file_name=file_name.format(
            idx) + '.h5', chan_list=np.arange(8))

        # Long data sequence -- entire file
        adc_data, timestamp, dac_data, ads_data_tmp, ads_seq, read_errors = ddr.data_to_names(chan_data)

        # Shorter data sequence, just one of the repeats
        # adc_data, timestamp, dac_data, ads, ads_seq_cnt, read_errors = ddr.data_to_names(chan_data_one_repeat)

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
