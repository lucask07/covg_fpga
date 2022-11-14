"""
The system uses two Daughtercards with:
 1) the bath clamp - has a non-zero CMD voltage measures Im 
 2) the voltage clamp - zero CMD voltage, goal is to hold capacitor plate at ground 

Demonstrate calibrations to determine electrode impedances

Step 1) measure CAL_SIG2 when injecting sinusoid at CAL_SIG1. Disconnect active feedback loop 


Sept 2022

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
from analysis.utils import calc_fft
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp


def make_cmd_cc(cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None):
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


    if cc_val is None:  # get the cc signal from scaling the cmd signal
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
FS_ADS = 1e6
dac80508_offset = 0x8000
DC_NUMS = [0,1]
dc_mapping = {'bath': 0, 'clamp': 1}  # TODO get from System class in electrodes.py


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
ddr = daq.ddr    # Or reference as da   q.ddr throughout the file
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

dc_under_test = 0
adc_chan0 = daq.parameters['ads_map'][dc_under_test]['CAL_ADC']
adc_chan1 = daq.parameters['ads_map'][dc_under_test]['AMP_OUT']
ads_sequencer_setup = [('0', '0'), ('1', '1')] #DC 0 has both to ADS 'A'.
#TODO - setup sequencer has default values for voltage range and lpf. Will over-write previous settings
codes = ads.setup_sequencer(chan_list=ads_sequencer_setup, voltage_range=ads_voltage_range, lpf=376)
ads.write_reg_bridge(clk_div=200) # 1 MSPS rate (do not use default value which is 200 ksps)
ads.set_fpga_mode()

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])
# TODO: set FPGA pins to enable the Howland pump amplifiers

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

# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x2)
    daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
    daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
    daq.DAC_gp[dac_gp_ch].set_data_mux('host')
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

daq.set_isel(port=1, channels=None)
daq.set_isel(port=2, channels=None)

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.1)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(1)
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset

# ------ Default configuration of clamp boards ------
board_to_test = 'bath'
board_to_disconnect = 'clamp'

# for dc_num in [dc_mapping[board_to_test]]:
    # log_info_bath, config_dict_test = clamps[dc_num].open_all_relays()

# for dc_num in [dc_mapping[board_to_disconnect]]:
    # log_info, config_dict_disconnect = clamps[dc_num].close_cal_relays()

def dac_waveform(dc_under_test, amp, freq=1000, shape='SINE', source='v'):

    """
    dc_under_test: the daughter card the calibration signal should be sent to
    amp: float either voltage or current in uA (amplitude, not pk-pk)
    freq: waveform frequency in Hz
    shape: 'SINE' or 'SQ'
    source: either 'v' or 'i'
    """

    for i in range(4):
        # set all fast-DAC DDR data to midscale
        ddr.data_arrays[i][:] = 0x2000

    if source == 'v':
        # this is a voltage
        sdac_amp_volt = amp/3 # 1 Volt amplitude. 2 V peak to peak # amplitude was checked on oscilloscope (bipolar creates gain of *3 with 0 mean)
        # at 1 V the DAC code is max=58928, min=6554
    if source == 'i':
        # max is 1.25 V which gives 0.8 uA 
        sdac_amp_volt = 1.25*(amp/0.8) # TODO make property of DAQ board 

    sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)
    # subtract one since if this value is precisely 2^15 we in effect get 0 for both high and low amplitude.
    sdac_amp_code = sdac_amp_code - 1
    print(f'Max sdac amp {sdac_amp_code}')
    
    # Data for the 2 DAC80508 "Slow DACs"
    if shape == 'SINE':
        sdac_wave, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, 
                                                  frequency=freq, offset=dac80508_offset)
    if shape == 'SQ':
        # low, high
        sq_length = int(2.5e6/freq)
        if sdac_amp_code > dac80508_offset:
            print(f'error, square-wave amplitude of {sdac_amp_code} too large ')
        sdac_wave = ddr.make_step(low=int(dac80508_offset - sdac_amp_code), 
                                             high= int(dac80508_offset + sdac_amp_code), 
                                                  length=sq_length)

    # Specify output channel for DAC80508
    sdac_ch = daq.parameters['gp_dac_map'][dc_under_test]['CAL']
    if sdac_ch[0] == 1:
        sdac_1_out_chan = sdac_ch[1]
    if sdac_ch[0] == 2:
        sdac_2_out_chan = sdac_ch[1] # don't care, this channel is not connected to CAL 
    else:
        sdac_2_out_chan = 0 # need a default channel
    # Clear bits in the FDAC DDR stream that store the slow DAC channel
    for i in range(6):
        ddr.data_arrays[i] = np.bitwise_and(ddr.data_arrays[i], 0x3fff)

    # Load data into DDR
    # Set channel bits
    ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
    ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
    ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
    ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

    # load slow DAC sine-wave in DDR channels 6
    ddr.data_arrays[6] = sdac_wave
    # ddr.data_arrays[7] = sdac_sine # TODO: all cal channels are on the first DAC so setting [7] is not needed

    ddr.write_setup()
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()

    return sdac_wave
    
# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S")
idx = 0

for i in range(4):
    # set all fast-DAC DDR data to midscale
    ddr.data_arrays[i][:] = 0x2000

sdac_amp_volt = 1 # 1 Volt amplitude. 2 V peak to peak # amplitude was checked on oscilloscope (bipolar creates gain of *3 with 0 mean)
# at 1 V the DAC code is max=58928, min=6554
target_freq_sdac = 1000.0 # Hz
sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

# Data for the 2 DAC80508 "Slow DACs"
sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq_sdac, offset=dac80508_offset)

# Specify output channel for DAC80508
sdac_ch = daq.parameters['gp_dac_map'][dc_under_test]['CAL']
if sdac_ch[0] == 1:
    sdac_1_out_chan = sdac_ch[1]
if sdac_ch[0] == 2:
    sdac_2_out_chan = sdac_ch[1] # don't care, this channel is not connected to CAL 
else:
    sdac_2_out_chan = 0 # need a default channel
# Clear bits in the FDAC DDR stream that store the slow DAC channel
for i in range(6):
    ddr.data_arrays[i] = np.bitwise_and(ddr.data_arrays[i], 0x3fff)

# Load data into DDR
# Set channel bits
ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

# load slow DAC sine-wave in DDR channels 6
ddr.data_arrays[6] = sdac_sine
ddr.data_arrays[7] = sdac_sine


# should be a do not care 
fb_res = 2.1
res = 100
cap = 47

testing = 'bath'
# testing = 'vclamp'
if testing == 'bath':
	dc_under_test = dc_mapping['bath']  # TODO: get these indices from the boards configuration
	dc_disconnect = dc_mapping['clamp']
elif testing == 'vclamp':
	dc_under_test = dc_mapping['clamp'] 
	dc_disconnect = dc_mapping['bath']


for dc_num in [dc_under_test]:
	log_info_test, config_dict_test = clamps[dc_num].configure_clamp(
		ADC_SEL="CAL_SIG2",
		DAC_SEL="drive_CAL2",
		CCOMP=cap,
		RF1=fb_res,  # feedback circuit
		ADG_RES=res,
		PClamp_CTRL=0, # keep open for calibration 
		P1_E_CTRL=1,
		P1_CAL_CTRL=1,
		P2_E_CTRL=1,
		P2_CAL_CTRL=1,
		gain=1,  # instrumentation amplifier
		FDBK=1,
		mode="voltage",
		EN_ipump=0,
		RF_1_Out=1,
		addr_pins_1=0b110,
		addr_pins_2=0b000,
	)

for dc_num in [dc_disconnect]:
	log_info_disconnect, config_dict_disconnect = clamps[dc_num].configure_clamp(
		ADC_SEL="CAL_SIG1",
		DAC_SEL="gnd_both",
		CCOMP=cap,
		RF1=fb_res,  # feedback circuit
		ADG_RES=res,
		PClamp_CTRL=0, # open relay (default)
		P1_E_CTRL=1,  # open relay
		P1_CAL_CTRL=0, # open relay (default)
		P2_E_CTRL=1,   # open relay
		P2_CAL_CTRL=0, # open relay (default)
		gain=1,  # instrumentation amplifier
		FDBK=1,
		mode="voltage",
		EN_ipump=0,
		RF_1_Out=1,
		addr_pins_1=0b110,
		addr_pins_2=0b000,
	)

ddr.write_setup()
block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
ddr.reset_mig_interface()
ddr.write_finish()
    
def collect_data(ddr, PLT=True, ads_chan=('A', 0), num_repeats=10, blk_multiples=40):
    
    ddr.repeat_setup() #Setup for reading new data without writing to the DDR again.

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    # 2,40 captures 2 periods of a sine-wave at 1 kHz
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=num_repeats, blk_multiples=blk_multiples)  # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(
        idx) + '.h5', chan_list=np.arange(8))

    adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, reading_error = ddr.data_to_names(chan_data)
    print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

    ############### extract the ADS data just for the last run and plot as a demonstration ############
    ads_data_v = {}
    for letter in ['A', 'B']:
        ads_data_v[letter] = np.array(to_voltage(
            ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range*2, use_twos_comp=False))

    total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
    total_seq_cnt[::2] = ads_seq_cnt[0]
    total_seq_cnt[1::2] = ads_seq_cnt[1]
    ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)

    # ADS8686 data and plot 
    volt = ads_separate_data[ads_chan[0]][ads_chan[1]]
    t_ads = np.arange(0,len(volt))*(1/FS_ADS)*len(ads_sequencer_setup)
    fig,ax = plt.subplots()
    if PLT:
        ax.plot(t_ads*1e6, volt, marker = '+', label = f'ADS: {chan}')
        ax.legend()
        ax.set_xlabel('s [us]')
        ax.set_title('ADS8686 data')
    return volt, t_ads

current_amp = 0.8 # uA
voltage_amp = 0.2 

data = {}

# Measure a current For Re1 + Re2 
step = 1
if testing=='bath':
	freq = 200
	num_repeats=10 
	blk_multiples=40
if testing=='vclamp':
	freq = 40
	num_repeats=50 
	blk_multiples=40
	
daq.set_isel(port=1, channels=[dc_under_test]) # current on CH 0 TODO: parameterize based on DC#  
config_dict_test['ADC_SEL'] = 'CAL_SIG2'
config_dict_test['DAC_SEL'] = 'drive_CAL2_gnd_CAL1'
log_info_bath, config_dict_test = clamps[dc_under_test].configure_clamp(**config_dict_test)
# inject current square wave, expect around 8 mV amplitude from 0.8 uA*10e3, 16 mV pk-pk 
dac_wave = dac_waveform(0, amp=current_amp, freq=freq, shape='SQ', source='i') # howland pump is always driven by BP_OUT0
volt, t = collect_data(ddr, PLT=True, ads_chan=daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
						num_repeats=num_repeats, blk_multiples=blk_multiples)
np.savez(os.path.join(data_dir, f'imp_step{step}.npy'), dac_wave, volt, t)

data[step] = {'volt': volt,
              't': t,
              'src': 'i',
              'shape': 'SQ',
              'freq': freq,
			  'amp': current_amp,
              'vclamp': 'disconnect',
              'bath_clamp': copy.deepcopy(config_dict_test),
              'voltage_clamp': copy.deepcopy(config_dict_disconnect)}

if testing == 'bath':
	config_dict_disconnect['P1_CAL_CTRL'] = 0
	config_dict_disconnect['P2_CAL_CTRL'] = 0
	config_dict_disconnect['DAC_SEL'] = 'drive_CAL2'  
	#freq_arr = [400, 1000, 4000, 7000, 10000, 20000, 50000]
	freq_arr = np.logspace(np.log10(400), np.log10(50000), 20)
elif testing == 'vclamp': # ground the bath clamp electrodes since 5k is small compared to the 200kOhm of the voltage clamp 
	config_dict_disconnect['P1_CAL_CTRL'] = 1
	config_dict_disconnect['P2_CAL_CTRL'] = 1
	config_dict_disconnect['DAC_SEL'] = 'gnd_both' 
	#freq_arr = [40, 100, 200, 500, 1000]
	freq_arr = np.logspace(np.log10(40), np.log10(10000), 20)
	

log_info_bath, config_dict_disconnect = clamps[dc_disconnect].configure_clamp(**config_dict_disconnect)

SWAP = True
VCLAMP_CAL = True
VCLAMP_TEST = False
daq.set_isel(port=1, channels=None) # channel select works correctly -- this turns off the signal 

# Measure voltage with CC load connected at two different frequencies 
for drive_elec in [1,2]:
	for idx,freq in enumerate(freq_arr):
		print(freq)
		# inject voltage sine wave of 1 V amplitude 
		step += 1
		
		if drive_elec == 1:
			config_dict_test['ADC_SEL'] = 'CAL_SIG1'
			config_dict_test['DAC_SEL'] = 'drive_CAL1' # do not ground CAL2 
		elif drive_elec == 2:
			config_dict_test['ADC_SEL'] = 'CAL_SIG2'
			config_dict_test['DAC_SEL'] = 'drive_CAL2' # do not ground CAL1 
		
		log_info_bath, config_dict_test = clamps[dc_under_test].configure_clamp(**config_dict_test)

		# load into DDR voltage sine wave
		dac_wave = dac_waveform(dc_under_test, amp=voltage_amp, freq=freq, shape='SINE', source='v')
		volt, t = collect_data(ddr, PLT=True, ads_chan=daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
								num_repeats=num_repeats, blk_multiples=blk_multiples)
		np.savez(os.path.join(data_dir, f'imp_step{step}.npy'), dac_wave, volt, t)

		data[step] = {'volt': volt, # data 
					  't': t,
					  'src': 'v',
					  'shape': 'SINE',
					  'freq': freq,
					  'amp': voltage_amp,
					  'vclamp': 'disconnect',                  
					  'bath_clamp': copy.deepcopy(config_dict_test),
					  'voltage_clamp': copy.deepcopy(config_dict_disconnect)}

		# swap roles of electrodes 
		step += 1
		if drive_elec == 1:
			config_dict_test['ADC_SEL'] = 'CAL_SIG2'
			config_dict_test['DAC_SEL'] = 'drive_CAL1' # do not ground CAL2 
		elif drive_elec == 2:
			config_dict_test['ADC_SEL'] = 'CAL_SIG1'
			config_dict_test['DAC_SEL'] = 'drive_CAL2' # do not ground CAL1 

		log_info_bath, config_dict_test = clamps[dc_under_test].configure_clamp(**config_dict_test)

		# use same injection waveform as in previous test
		volt, t = collect_data(ddr, PLT=True, ads_chan=daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
								num_repeats=num_repeats, blk_multiples=blk_multiples)
		np.savez(os.path.join(data_dir, f'imp_step{step}.npy'), dac_wave, volt, t)
		data[step] = {'volt': volt,
					  't': t,
					  'src': 'v',
					  'shape': 'SINE',
					  'freq': freq,
					  'amp': voltage_amp,
					  'vclamp': 'disconnect',
					  'bath_clamp': copy.deepcopy(config_dict_test),
					  'voltage_clamp': copy.deepcopy(config_dict_disconnect)}

np.savez(os.path.join(data_dir, f'imp_all_steps.npy'), data)


if VCLAMP_TEST:
	for vclamp in ['passive', 'active']:
		step += 1
		# same configuration of the bath clamp 
		# but also ground the membrane capacitor through the clamp board (due to high resistance of electrodes this probably wont be visible
		# passive clamp

		if vclamp == 'passive':
			config_dict_disconnect['P1_CAL_CTRL'] = 1
			config_dict_disconnect['P2_CAL_CTRL'] = 1
			config_dict_disconnect['P1_E_CTRL'] = 1
			config_dict_disconnect['P2_E_CTRL'] = 1 # close relay (connect electrode)
			config_dict_disconnect['DAC_SEL'] = 'gnd_both'  
		elif vclamp == 'active':
			config_dict_disconnect['P1_CAL_CTRL'] = 0
			config_dict_disconnect['P2_CAL_CTRL'] = 0
			config_dict_disconnect['P1_E_CTRL'] = 0
			config_dict_disconnect['P2_E_CTRL'] = 0 # close relay (connect electrode)
			config_dict_disconnect['DAC_SEL'] = 'gnd_both'      
		
		log_info_bath, config_dict_disconnect = clamps[1].configure_clamp(**config_dict_disconnect)

		# use same injection waveform as in previous test  
		volt, t = collect_data(ddr, PLT=True, ads_chan=('A', 0))
		np.savez(os.path.join(data_dir, f'imp_step{step}.npy'), dac_wave, volt, t)
		data[step] = {'dac_wave': dac_wave,
					  'volt': volt,
					  't': t,
					  'src': 'v',
					  'shape': 'SINE',
					  'freq': freq,
					  'vclamp': vclamp,
					  'bath_clamp': config_dict_test,
					  'voltage_clamp': config_dict_disconnect}

# Measure voltage with CC load connected at f = 1 kHz
# step += 1
# inject voltage sine wave of 1 V amplitude 
#dac_wave = dac_waveform(dc_under_test, amp=1, freq=10000, shape='SINE', source='v')
#volt, t = collect_data(ddr, PLT=True, ads_chan=('A', 0))

from calibration.cal_fits import fit_sine_fft, soft_sq_wave, sine_wave
from scipy.optimize import curve_fit

ADS_CHAN_FS = 2e-6
tau_to_settle = 3
if testing=='bath':
	predicted_rc = (5e3+6.8e3)*4.7e-9
	start_idx = int(tau_to_settle*predicted_rc/ADS_CHAN_FS)
elif testing=='vclamp':
	predicted_rc = (200e3)*33e-9
	start_idx = int(tau_to_settle*predicted_rc/ADS_CHAN_FS)


# TODO - add frequency bounds set by what we set 
for data_key in data:
	d = data[data_key]
	t = d['t'][start_idx:]
	y = d['volt'][start_idx:] # if I chop at an arbitrary point there will be a phase shift that varies with frequency
	freq = d['freq']
	amp_dac = d['amp'] # in uA or in volts 

	if d['shape'] == 'SQ':
		yfit = curve_fit(soft_sq_wave, t,y , p0=(freq, 0.016, 0, 0, 0)) #,
						#bounds = ([0,0,-15,0,0], [10e6, np.inf, 15, 2*np.pi, np.inf]))  # bounds cause problems. Not sure why
		predicted_res = yfit[0][1]/(amp_dac*1e-6)
		print(f'Predicted resistance {predicted_res}')
	elif d['shape'] == 'SINE':
		max_freq, amp, phase = fit_sine_fft(t, y)
		print(f'Amp. of sine from fft: {amp:.2f}. Phase: {np.degrees(phase):.2f} at freq of {max_freq} [Hz] vclamp of {d["vclamp"]}') 
	
	plt.figure(data_key)
	if d['shape'] == 'SQ':
		plt.plot(t*1e6, soft_sq_wave(t, *yfit[0]))
	elif d['shape'] == 'SINE':
		plt.plot(t*1e6, sine_wave(t, max_freq, amp, np.average(y), phase))

# TODO: use frequency data to estimate Rs individual