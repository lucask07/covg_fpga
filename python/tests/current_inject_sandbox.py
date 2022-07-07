"""This script attempts to replicate Figure 4 on the biophysical poster. This
consists of measuring the membrane current (Im) with the AD7961 after
supplying a step voltage of 0-50mV by the AD5453. This is repeated for
feedback resistors of 10K, 33K, 100K, 332K, and 3000K. The membrane current
(Im) is graphed against time with all of these responses together.

Biophysical poster: https://uofstthomasmn.sharepoint.com/:b:/r/sites/COVGsummer2022/Shared%20Documents/biophysical_2022_poster_covg_v1.pdf?csf=1&web=1&e=gbUPQi

June 2022

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
               cc_val=None, cc_pickle_num=None, write_ddr=True):
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
    
    if write_ddr:
        # write channels to the DDR
        ddr.write_setup()
        # clear read, set write, etc. handled within write_channels
        block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
        ddr.reset_mig_interface()
        ddr.write_finish()

FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6
DC_NUMS = [0, 1, 2, 3]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3

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
ads_sequencer_setup = [('1', '1'), ('2', '2')]
codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge(clk_div=200) # 1 MSPS rate (do not use default value of 1000 which is 200 ksps)
ads.set_fpga_mode()

# TODO: are the TCA pins already configured in Clamp.configure_clamp()?
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# configure General Purpose DACs, ensure not as a current source
# DAC_gp[1] channel 0 is connected to bottom plate of Membrane capacitor
for i in range(2):
    daq.set_isel(port=i+1, channels=None)
    # Reset the Wishbone controller and SPI core
    daq.DAC_gp[i].set_ctrl_reg(daq.DAC_gp[i].master_config)
    daq.DAC_gp[i].set_spi_sclk_divide()
    daq.DAC_gp[i].filter_select(operation="clear")
    daq.DAC_gp[i].set_data_mux("host")
    daq.DAC_gp[i].set_config_bin(0x00)
    print('Outputs powered on')

#DAC2_CAL0, DAC2_CAL1 
daq.DAC_gp[1].write_voltage(0.635, 0) # 50 mV offset 
daq.DAC_gp[1].set_gain(2, outputs=[0,1,2,3,4,5,6,7])

# Use DAC2_CAL0 as a current source driven by the DDR 
daq.set_isel(port=2, channels=[0,1])
# -3.5 V to 3.5 V out from the bipolar amplifier with gain of x1.
# Howland current pump gain is Vin*1/4.7e6
daq.DAC_gp[1].set_gain(1, outputs=[0,1])

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

currents_to_inj = [500, -300, -100, 100, 300, 500, 700] # in nA

dc_data = {}    # To store voltage data for each configuration of each daughtercard
ads_data = {}    # To store ADS voltage data for each configuration (not associated with a specific daughtercard)

for dc_num in DC_NUMS:
    # access data with dc_data[dc_num][i_inj]
    dc_data[dc_num] = {}
errors = copy.deepcopy(dc_data)  # Instead of voltage data, this dict will store whether an error occurred on the DDR read

# Setup CMD and CC signals but do not write to DDR
set_cmd_cc(dc_nums=DC_NUMS, cmd_val=0x0020, cc_scale=0, cc_delay=0, fc=None, # was 0x0300
        step_len=16384, cc_val=None, cc_pickle_num=None, write_ddr=False)

def current_inj(on_current=700):

    daq.DAC_gp[0].set_data_mux("DDR")
    daq.DAC_gp[1].set_data_mux("DDR")

    sdac_1_out_chan = 7  # Do not care for this experiment -- able to connect DAC1_OUT7 to the scope. Have voltage mirror current
    sdac_2_out_chan = 0  # Howland current source -- connecting to DAC2_CAL0 

    # Clear channel bits
    for i in range(4):
        ddr.data_arrays[i] = np.bitwise_and(ddr.data_arrays[i], 0x3fff)
    cmd_signal = ddr.data_arrays[1] 

    # Set channel bits for the General purpose DAC
    ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
    ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
    ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
    ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

    # CMD is DDR channels 1, 3. Derive current source value from the CMD signal 
    i_na_per_lsb = 796.6/2**15   # nA/LSB 

    # Fast DAC offset is 0x2000 
    ddr.data_arrays[7] = np.where(cmd_signal > 0x2000, int(on_current/i_na_per_lsb), 0) + 0x8000
    ddr.data_arrays[6] = ddr.data_arrays[7]  # observe on the oscilloscope 

    # re-write channels to the DDR
    ddr.write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()

# Configure clamp board. Use a large resistor for small currents 
rs = 3000
ccomp = 47
rf = 2.1
print(f'Configuring for oscilloscope: CCOMP={ccomp}, RF1={rf}, ADG_RES={rs}')
# Configure for better oscilloscope viewing
for dc_num in DC_NUMS:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG2",
        DAC_SEL="drive_CAL2",
        CCOMP=ccomp,
        RF1=rf,  # feedback circuit
        ADG_RES=rs,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0, 
        P2_E_CTRL=0,
        P2_CAL_CTRL=0, # close just for this demonstration of the ADS CAL_ADC
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S") + '_{}' # to append the index
idx = 0

for i_inj in currents_to_inj:

    current_inj(on_current = i_inj)
    if idx == 0:
        time.sleep(0.4)

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

    ############### extract the ADS data ############
    ads_data_v = {}
    for letter in ['A', 'B']:
        ads_data_v[letter] = np.array(to_voltage(
            ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

    total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
    total_seq_cnt[::2] = ads_seq_cnt[0]
    total_seq_cnt[1::2] = ads_seq_cnt[1]
    ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)

    for dc_num in range(4):
        dc_data[dc_num][i_inj] = adc_data[dc_num]
    ads_data[i_inj] = ads_separate_data

    idx = idx + 1

for ch in [0,1]:
    fig, ax = plt.subplots(2,1)
    fig.suptitle('')

    for i_inj in currents_to_inj:

        # Store voltage in list; plot
        y = to_voltage(dc_data[ch][i_inj], num_bits=16, voltage_range=4.096, use_twos_comp=True)
        y_filt = butter_lowpass_filter(y, 10e3, FS, order=5)
        # y_filt = np.array(y)
        t = np.arange(0,len(y_filt))*1/FS
        lbl = f'{i_inj} [nA]'
        ax[0].plot(t*1e6, y_filt/rs*1e3*(1500+120)/499, marker = '+', label = lbl)

        # AMP OUT : observing (buffered/amplified) electrode P1 -- represents estimate of Vmembrane
        if ch == 0:
            vm = ads_data[i_inj]['A'][1] # AMP out dc# 0
        if ch == 1:
            vm = ads_data[i_inj]['A'][2] # AMP out dc# 1
        t_ads = np.arange(len(vm))*1/(ADS_FS / len(ads_sequencer_setup))
        ax[1].plot(t_ads*1e6, vm, marker='.')

    for ax_s in ax:
        ax_s.set_xlabel('t [$\mu$s]')

    ax[0].legend()
    ax[0].set_ylabel('I [uA]')

    ax[1].set_ylabel('P1 (tracks Vm) [V]')

    def ads_plot_zoom(ax):
        for ax_s in ax:
            ax_s.set_xlim([3250, 3330])
            ax_s.grid('on')
