"""
The system uses two Daughtercards with:
 1) the bath clamp - has a non-zero CMD voltage measures Im 
 2) the voltage clamp - zero CMD voltage, goal is to hold capacitor plate at ground 

 and 
 3) a voltage sense board that cannot be disconnected via relays (combines with the voltage clamp board to create feedback loop)

Demonstrate calibrations to determine electrode impedances
Step 1) measure CAL_SIG2 when injecting sinusoid at CAL_SIG1. Disconnect active feedback loop 

Sept 2022/June 2023 

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu

TODO:
separate bath and vclamp 
Ensure no transient voltages -- check with oscilloscope; create function to put all DACs to host driven and midscale 
create a chirp upload to the DDR to capture multiple frequencies at once -- DONE and works 
clamp: freq_arr = np.logspace(np.log10(400), np.log10(50000), 8)
bath : freq_arr = np.logspace(np.log10(40), np.log10(2000), 8)

"""
import os
import sys
from time import sleep
import time
import atexit
import numpy as np
import matplotlib.pyplot as plt
import copy
import pandas as pd
from pyripherals.utils import to_voltage, from_voltage
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3

# Defines data_dir_covg and adds the path to boards.py into the sys.path 
from setup_paths import *


from analysis.adc_data import read_h5, separate_ads_sequence
from analysis.utils import calc_fft
from analysis.calibration_analysis import total_res_iso_res, r_from_square
from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp, Vsense
from calibration.electrodes import EphysSystem

ephys_sys = EphysSystem(system='Dagan_vclamp_no_guard')

results_dir = os.path.join(boards_path, 'results') 
UPDATE_RESULTS = True

FS = 5e6
SAMPLE_PERIOD = 1/FS
FS_ADS = 1e6
dac80508_offset = 0x8000
DC_NUMS = [0,1,3]
dc_mapping = {'bath': 0, 'clamp': 1, 'vclamp': 3}  # TODO get from System class in electrodes.py

eps = Endpoint.endpoints_from_defines

pwr_setup = "3dual"
pwr_setup = "boland_lab"

# -------- power supplies -----------
try:
    dc_pwr.get('id')
except:
    # -------- power supplies -----------
    dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)
    if pwr_setup == "3dual" or pwr_setup == 'boland_lab':
        atexit.register(pwr_off, [dc_pwr])
    else:
        atexit.register(pwr_off, [dc_pwr, dc_pwr2])
    config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)

    # turn on the 7V
    if pwr_setup == '3dual':
        dc_pwr.set("out_state", "ON", configs={"chan": 1})
    elif pwr_setup == 'boland_lab':
        dc_pwr.set("out_state", "ON", configs={"chan": 3})

    if pwr_setup == "3dual":
        # turn on the +/-16.5 V input
        for ch in [2, 3]:
            dc_pwr.set("out_state", "ON", configs={"chan": ch})
    elif pwr_setup == "boland_lab":
        # turn on the +/-16.5 V input
        for ch in [1, 2]:
            dc_pwr.set("out_state", "ON", configs={"chan": ch})        
    else:
        for ch in [1, 2]:
            dc_pwr2.set("out_state", "ON", configs={"chan": ch})

sleep(1)
try: # only initialize systeam and FPGA if needed. Allows us to repeat with %run -i tests/bathclamp_vclamp_step_response.py 
    f.xem.IsOpen()
except NameError:
    f = FPGA()
    f.init_device()
    sleep(0.2)
    f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

    pwr = Daq.Power(f)
    pwr.all_off()  # disable all power enables

    daq = Daq(f)
    ddr = daq.ddr    # Or reference as daq.ddr throughout the file
    ddr.data_version = 'TIMESTAMPS'
    ad7961s = daq.ADC
    ad7961s[0].reset_wire(1)    # Only actually one WIRE_RESET for all AD7961s

    ads = daq.ADC_gp

    sleep(0.2)
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
        if dc_num == dc_mapping['vclamp']:
            clamp = Clamp(f, dc_num=dc_num, DAC_addr_pins=0b000, version=2) # DAC ADDR is floating on VSENSE board 
        else:
            clamp = Clamp(f, dc_num=dc_num, version=2)
        print(f'Clamp {dc_num} Init'.center(35, '-'))
        clamp.init_board()
        clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
        clamps[dc_num] = clamp

    vsense = Vsense(f, dc_num=3)

    # -------- configure the ADS8686
    ads_voltage_range = 5  # need this for to_voltage later 
    ads.hw_reset(val=False)
    ads.set_host_mode()
    ads.setup()
    ads.set_range(ads_voltage_range) # 
    ads.set_lpf(376)

    '''
    daq.parameters['ads_map']
        {0: {'CAL_ADC': ('A', 0), 'AMP_OUT': ('A', 1)},
        1: {'CAL_ADC': ('B', 0), 'AMP_OUT': ('A', 2)},
        2: {'CAL_ADC': ('B', 1), 'AMP_OUT': ('A', 3)},
        3: {'CAL_ADC': ('A', 4), 'AMP_OUT': ('B', 2)}}
    if using daughter cards: 0,1,2 need A0,A1,A2,A3; B0,B1 
    '''
    dc_under_test = 0 
    adc_chan0 = daq.parameters['ads_map'][dc_under_test]['CAL_ADC'] # ('A', 0)
    adc_chan1 = daq.parameters['ads_map'][dc_under_test]['AMP_OUT'] # ('A', 1)
    adc_v1 = daq.parameters['ads_map'][dc_mapping['vclamp']]['AMP_OUT'] # ('A', 1)
    ads_sequencer_setup = [('0', '0'), ('1', '1'), ('2', '2')] #DC 0 has both to ADS 'A'.
    codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
    ads.write_reg_bridge(clk_div=200) # 1 MSPS rate with clk_div=200 (do not use default value which is 200 ksps)
    ads.set_fpga_mode()

    daq.TCA[0].configure_pins([0, 0])
    daq.TCA[1].configure_pins([0, 0])

    # fast DAC channels setup
    fast_dac_offset = 0x2000
    for i in range(6):
        daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
        daq.DAC[i].set_spi_sclk_divide()
        daq.DAC[i].filter_select(operation="clear")
        daq.DAC[i].write(int(fast_dac_offset))
        daq.DAC[i].set_data_mux("DDR")
        daq.DAC[i].change_filter_coeff(target="passthru")
        daq.DAC[i].write_filter_coeffs()
        daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

    # --- Configure for DDR read to DAC80508 ---
    for dac_gp_ch in [0, 1]:
        daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x2)
        daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
        daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
        #daq.DAC_gp[dac_gp_ch].set_data_mux('host')
        daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

    daq.set_isel(port=1, channels=None)
    daq.set_isel(port=2, channels=None)

    # --------  Enable fast ADCs  --------
    for chan in [0, 1, 2, 3]:
        ad7961s[chan].power_up_adc()  # standard sampling
    time.sleep(0.1)
    ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
    time.sleep(0.05)
    ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset


def dac_waveform(dc_under_test, amp, freq=1000, shape='SINE', source='v', periods=None):

    """
    dc_under_test: the daughter card the calibration signal should be sent to
    amp: float either voltage or current in uA (amplitude, not pk-pk)
    freq: waveform frequency in Hz or nd.array is shape is 'CHIRP'
    shape: 'SINE' or 'SQ' or 'CHIRP'
    source: either 'v' or 'i'
    periods: nd.array of periods or int 
    """

    for i in range(6):
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
    if sdac_amp_code == 2**15:
        sdac_amp_code = sdac_amp_code - 1
    print(f'Max sdac amp {sdac_amp_code}')
    
    # Data for the 2 DAC80508 "Slow DACs"
    if shape == 'SINE':
        sdac_wave, freq = ddr.make_sine_wave(amplitude=sdac_amp_code, 
                                                  frequency=freq, offset=dac80508_offset)
        indices = None
    elif shape == 'SQ':
        # low, high
        sq_length = int(1/DDR3.UPDATE_PERIOD/freq)
        if sdac_amp_code > dac80508_offset:
            print(f'error, square-wave amplitude of {sdac_amp_code} too large ')
        sdac_wave = ddr.make_step(low=int(dac80508_offset - sdac_amp_code), 
                                             high= int(dac80508_offset + sdac_amp_code), 
                                                  length=sq_length)
        indices = None
    elif shape == 'CHIRP':
        if sdac_amp_code > dac80508_offset:
            print(f'error, square-wave amplitude of {sdac_amp_code} too large ')        
        sdac_wave, freq, indices = ddr.make_chirp(amplitude=sdac_amp_code,
                                             frequencies=freq, periods=periods, 
                                             offset=dac80508_offset)

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

    return sdac_wave, freq, indices
 

def get_ads_voltages(ddr, num_repeats=1, blk_multiples=10):
    """
    read a short series from DDR in order to calculate the DC value of ADS channels 
        like a volt meter 
    
    Returns 
        volts: dict [chan][num]
            average voltage value of given channel ('A' or 'B') and number
    """
    ddr.repeat_setup() #Setup for reading new data without writing to the DDR again.

    # saves data to a file
    chan_data_one_repeat = ddr.save_data(data_dir, 'voltage_read.h5', num_repeats=num_repeats, blk_multiples=blk_multiples)  # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name='voltage_read.h5', chan_list=np.arange(8))

    adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, reading_error = ddr.data_to_names(chan_data)

    ############### extract the ADS data ############
    ads_data_v = {}
    for letter in ['A', 'B']:
        ads_data_v[letter] = np.array(to_voltage(
            ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range*2, use_twos_comp=False))

    total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
    total_seq_cnt[::2] = ads_seq_cnt[0]
    total_seq_cnt[1::2] = ads_seq_cnt[1]
    ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)

    volts = {}

    for chan in ads_separate_data:
        volts[chan] = {}
        for num in ads_separate_data[chan]:
            v = np.mean(ads_separate_data[chan][num])
            volts[chan][num] = v
            print(f'Channel {chan}{num} at {v:.4g} [V]')

    # update system connections since the daughtercard configurations have changed
    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)
    # Plot using datastreams 
    datastreams, log_info = rawh5_to_datastreams(data_dir, 'voltage_read.h5', ddr.data_to_names, 
                                                daq, sys_connections, outfile = None)
    

    return volts, datastreams


def collect_data(ddr, PLT=True, ads_chan=('A', 0), num_repeats=10, blk_multiples=40):
    
    ddr.repeat_setup() #Setup for reading new data without writing to the DDR again.

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    # 2,40 captures 2 periods of a sine-wave at 1 kHz
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', 
                                         num_repeats=num_repeats, blk_multiples=blk_multiples)  # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(
        idx) + '.h5', chan_list=np.arange(8))

    adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, reading_error = ddr.data_to_names(chan_data)
    print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

    ############### extract the ADS data ############
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
    if PLT:
        fig, ax = plt.subplots()
        ax.plot(t_ads*1e6, volt, marker = '+', label = f'ADS: {chan}')
        ax.legend()
        ax.set_xlabel('s [us]')
        ax.set_title('ADS8686 data')
    else:
        ax=None
    return volt, t_ads, ads_separate_data, ax

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S")
idx = 0

for i in range(6):
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
# Set channel bits # TODO: make this a method of the DDR
ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

# load slow DAC sine-wave in DDR channels 6
ddr.data_arrays[6] = sdac_sine # TODO: just one 
ddr.data_arrays[7] = sdac_sine

# daughter-card settings should be a do not care 
fb_res = 2.1 # resistors and cap have changed so this does not correspond to typical bath clamp board
res = 100 # kOhm 
cap = 47
component_results = {} 

def setup_clamps(dc_under_test, dc_disconnect):
    dc_configs = {}
    log_info_test, dc_configs[dc_under_test] = clamps[dc_under_test].configure_clamp(
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

    log_info_disconnect,  dc_configs[dc_disconnect] = clamps[dc_disconnect].configure_clamp(
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
     # with the VCLAMP board none of these configurations will change anything
    log_info_vclamp, dc_configs[dc_mapping['vclamp']] = clamps[dc_mapping['vclamp']].configure_clamp(
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
    dc_configs[dc_mapping['vclamp']]['VSENSE'] = 78 # extra information for the system_connections

    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)

    return dc_configs, sys_connections

def measure_resistance(config_dict_test, dc_under_test, testing='bath', step=1, 
                        plt_data=True, plt_fit=False,
                        write_ddr=True):
    # Measure a current For Re1 + Re2 
    if testing=='bath':
        freq = 200
        num_repeats=10 
        blk_multiples=40
        current_amp = 0.8
    if testing=='vclamp':
        freq = 40
        num_repeats=50 
        blk_multiples=40
        current_amp = 0.01 # 10 nA TODO: ensure that current is source only for a short amount of time so that we don't blow up the cell

    daq.set_isel(port=1, channels=[dc_under_test]) # current based on DC#  
    config_dict_test['ADC_SEL'] = 'CAL_SIG2' # this is the force terminal 

    if testing == 'bath':
        config_dict_test['DAC_SEL'] = 'drive_CAL2_gnd_CAL1'
    elif testing == 'vlcamp':
        config_dict_test['DAC_SEL'] = 'drive_CAL2'
        config_dict_test['P1_E_CTRL'] = 0 # open relay
    log_info_bath, config_dict_test = clamps[dc_under_test].configure_clamp(**config_dict_test)
    # inject current square wave, expect around 8 mV amplitude from 0.8 uA*10e3, 16 mV pk-pk         
    if write_ddr:
        dac_wave, freq, _ = dac_waveform(0, amp=current_amp, freq=freq, shape='SQ', source='i') # howland pump is always driven by BP_OUT0
    else:
        ddr.reset_mig_interface()
        ddr.write_finish()

    volt, t, ads_separate_data, ax = collect_data(ddr, PLT=plt_data, ads_chan=daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
                            num_repeats=num_repeats, blk_multiples=blk_multiples)
    
    if testing == 'vclamp':
        v_vclamp = ads_separate_data[adc_v1[0]][adc_v1[1]] # TODO: generalize if boards swap DAQ sockets 
        idx = np.min([len(t), len(v_vclamp)])
        ax.plot(t[:idx]*1e6, v_vclamp[:idx]/78.07, label='V1 [V]')    
        ax.legend()

        idx = np.min([len(t), len(v_vclamp), len(volt)])
        fig, ax = plt.subplots()
        ax.plot(t[:idx]*1e6, v_vclamp[:idx]/78.07 - volt[:idx], label='V1 - V(I) [V]')
        volt = v_vclamp[:idx]/78.07 - volt[:idx] # fit this difference of voltages 
        ax.legend()

    rdata = {}
    # ensure that t and volt are the same length 
    idx = np.min([len(t), len(volt)])
    volt = volt[:idx]
    t = t[:idx]
    rdata[step] = {'volt': volt,
                't': t,
                'src': 'i',
                'shape': 'SQ',
                'freq': freq,
                'amp': current_amp,
                'vclamp': 'disconnect',
                'bath_clamp': copy.deepcopy(config_dict_test),
                'voltage_clamp': copy.deepcopy(dc_configs[dc_disconnect])}
    try:
        fit_resistance, pcov, mesg = r_from_square(r_total_guess, rdata, PLT=plt_fit)
    except:
        fit_resistance = pcov = mesg = None

    return config_dict_test, rdata, fit_resistance, pcov, mesg, ads_separate_data


def chirp_test(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp):

    for drive_elec in [1,2]:
        if drive_elec == 1:  # upload the chirp signal to DDR 
            periods = np.ones(len(freq_arr))*30
            dac_wave, freq_chirp, indices = dac_waveform(dc_under_test, amp=voltage_amp, 
                                                    freq=freq_arr, shape='CHIRP', source='v', 
                                                    periods=periods)
            total_chirp_time = np.sum(1/freq_arr*periods)
            print(f'Total chirp time = {total_chirp_time}')
            # find the last index to 'download' using the starting index of the last frequency
            end_index = indices[-1][0] + periods[-1]*((1/DDR3.UPDATE_PERIOD)/freq_arr[-1])

        # measure at same point as drive 
        if drive_elec == 1:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG1' 
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL1' # do not ground CAL2; won't work for isolated Vsense board
        elif drive_elec == 2:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG2'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL2' # do not ground CAL1 
        
        log_info_bath, dc_configs[dc_under_test] = clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])

        # download ADC data so that np.max(t_chirp) = total_chirp_time 
        # This can also be checked by the inidices (2.5 MSPS) 
        #   versus the length of volt_chirp (@ 1 MSPS / len(ads_sequencer_setup))
        blk_mult = 120
        num_repeats_chirp = int(np.ceil(end_index*2/(2048/16)/blk_mult))
        volt_chirp, t_chirp, ads_separate_data_chirp, ax = collect_data(ddr, PLT=False, 
                                                                        ads_chan=daq.parameters['ads_map'][dc_under_test]['CAL_ADC'], 
                                                                        num_repeats=num_repeats_chirp, blk_multiples=blk_mult)

        for freq, idx in zip(freq_arr, indices):
            chirp_idx = []
            chirp_idx.append(int(idx[0]/len(ads_sequencer_setup)/(2.5)))
            chirp_idx.append(int(idx[1]/len(ads_sequencer_setup)/(2.5)))

            data_chirp[step_chirp] = {'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]], # measured data 
                    't': t_chirp[chirp_idx[0]:chirp_idx[1]],
                    'v1': ads_separate_data_chirp[adc_v1[0]][adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
                    'src': 'v',
                    'shape': 'SINE',
                    'freq': freq, # stimulus frequency 
                    'amp': voltage_amp,
                    'vclamp': 'disconnect',                  
                    'bath_clamp': copy.deepcopy(dc_configs[dc_under_test]),
                    'voltage_clamp': copy.deepcopy(dc_configs[dc_disconnect])}
            step_chirp += 1

        # swap roles ADC_SEL electrode; keep drive electrode the same  
        if drive_elec == 1:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG2'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL1' # do not ground CAL2 
        elif drive_elec == 2:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG1'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL2' # do not ground CAL1 
        log_info_bath, dc_configs[dc_under_test] = clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])

        volt_chirp, t_chirp, ads_separate_data_chirp, ax = collect_data(ddr, PLT=False, 
                                                                        ads_chan=daq.parameters['ads_map'][dc_under_test]['CAL_ADC'], 
                                                                        num_repeats=num_repeats_chirp, blk_multiples=blk_mult)

        for freq, idx in zip(freq_arr, indices):
            chirp_idx = []
            chirp_idx.append(int(idx[0]/len(ads_sequencer_setup)/(2.5)))
            chirp_idx.append(int(idx[1]/len(ads_sequencer_setup)/(2.5)))

            data_chirp[step_chirp] = {'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]], # measured data 
                    't': t_chirp[chirp_idx[0]:chirp_idx[1]],
                    'v1': ads_separate_data_chirp[adc_v1[0]][adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
                    'src': 'v',
                    'shape': 'SINE',
                    'freq': freq, # stimulus frequency 
                    'amp': voltage_amp,
                    'vclamp': 'disconnect',                  
                    'bath_clamp': copy.deepcopy(dc_configs[dc_under_test]),
                    'voltage_clamp': copy.deepcopy(dc_configs[dc_disconnect])}
            step_chirp += 1

    # save data 
    filename_chirp = 'imp_all_steps_chirp_{}'
    np.savez(os.path.join(data_dir, filename_chirp.format(testing)), data_chirp)

    return data_chirp, filename_chirp, step_chirp


# for testing in ['bath']:
for testing in ['bath', 'vclamp']:
    if testing == 'bath':
        dc_under_test = dc_mapping['bath']  # TODO: get these indices from the boards configuration
        dc_disconnect = dc_mapping['clamp']
    elif testing == 'vclamp':
        dc_under_test = dc_mapping['clamp'] 
        dc_disconnect = dc_mapping['bath']

    dc_configs, sys_connections = setup_clamps(dc_under_test=dc_under_test, dc_disconnect=dc_disconnect)

    ddr.write_setup()
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False) # TODO: is this actually used or just promptly overwritten?
    ddr.reset_mig_interface()
    ddr.write_finish()

    if testing=='bath':
        freq = 200
        num_repeats=10 
        blk_multiples=40
        r_total_guess = 8e3 
        voltage_amp = 0.2 
    if testing=='vclamp':
        freq = 40
        num_repeats=50 
        blk_multiples=40
        r_total_guess = 300e3 
        voltage_amp = 0.05 
    step = 1
    data = {}

    # measure resistance 
    dc_configs[dc_under_test], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(dc_configs[dc_under_test], dc_under_test=dc_under_test, testing=testing, 
                                                                             step=1, plt_data=True, plt_fit=True,
                                                                             write_ddr=True)
    if testing == 'vclamp': # needs extra time to settle 
        dc_configs[dc_under_test], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(dc_configs[dc_under_test], dc_under_test=dc_under_test, 
                                                                                                             testing=testing, 
                                                                                                                step=1, plt_data=True, plt_fit=True,
                                                                                                                write_ddr=False)
    data[step] = rdata[step]

    if testing == 'bath':
        dc_configs[dc_disconnect]['P1_CAL_CTRL'] = 0
        dc_configs[dc_disconnect]['P2_CAL_CTRL'] = 0
        dc_configs[dc_disconnect]['DAC_SEL'] = 'drive_CAL2'  
        freq_arr = np.logspace(np.log10(400), np.log10(50000), 8)
    elif testing == 'vclamp': # ground the bath clamp electrodes since 5k is small compared to the 200kOhm of the voltage clamp 
        dc_configs[dc_disconnect]['P1_CAL_CTRL'] = 1
        dc_configs[dc_disconnect]['P2_CAL_CTRL'] = 1
        dc_configs[dc_disconnect]['DAC_SEL'] = 'gnd_both' 
        freq_arr = np.logspace(np.log10(40), np.log10(2000), 8)

    log_info_bath, dc_configs[dc_disconnect] = clamps[dc_disconnect].configure_clamp(**dc_configs[dc_disconnect])

    # disable the current source 
    daq.set_isel(port=1, channels=None) # channel select works correctly -- this turns off the signal 

    # ---- CHIRP testing ------------
    data_chirp = {}
    data_chirp[1] = data[1]
    step_chirp = 2

    if testing == 'bath' or testing == 'vclamp':
        data_chirp, filename_chirp, step_chirp = chirp_test(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp)

    # process data
    if testing == 'vclamp':
        tf_type = 'vclamp'
        r_total_guess = 300e3 
    elif testing == 'bath':
        tf_type = 'elec_r_cc'
        r_total_guess = 8e3

    # calculates both the total resistance (measured via current injection)
    # and the isolated resistance infered by transfer functions 
    predicted_res, res_fit_mesg, component_fits, fit_notes, components = total_res_iso_res(data_dir, filename_chirp.format(testing) + '.npz',  
                                                                                           r_total_guess, tf_type, PLT=True)
    print(components)
    # components is calculated from component_fits so its ok to not capture component_fits
    component_results[testing] = components
    component_results[testing]['total_resistance'] = predicted_res
    component_results[testing]['resistance_msg'] = res_fit_mesg
    component_results[testing]['fit_notes'] = fit_notes
        
print('final component results ' + '-'*40)
print(component_results)

# save final results to a JSON and to a CSV
# directory for CSV is different than directory for JSON 
import json
with open(os.path.join(data_dir, 'cal_data_' + file_name + '.json'), 'w') as fp:
    json.dump(component_results, fp, sort_keys=True, indent=4)

if UPDATE_RESULTS:
    df = pd.DataFrame.from_dict(component_results)
    df.to_csv(os.path.join(results_dir, 'calibration.csv'))
    df.to_csv(os.path.join(data_dir, 'calibration_' + file_name + '.csv'))

def config_dacs(config='host', ch=[None, None]):

    if ch[0] is None:
        fast_chs = range(6)
    else:
        fast_chs = ch[0]

    if ch[1] is None:
        slow_chs = [0,1]
    else:
        slow_chs = ch[1]

    # fast DAC channels setup
    for i in fast_chs:
        daq.DAC[i].write(int(fast_dac_offset)) 
        daq.DAC[i].set_data_mux(config)
        print(f'DAC {i} current data MUX = {daq.DAC[i].current_data_mux}') 

    # --- Configure for host read to DAC80508 ---
    for dac_gp_ch in slow_chs:
        daq.DAC_gp[dac_gp_ch].write(int(dac80508_offset))
        daq.DAC_gp[dac_gp_ch].set_data_mux(config)
        print(f'DAC General Purpose {i} current data MUX = {daq.DAC_gp[dac_gp_ch].current_data_mux}') 


def quiet_dacs(ch=[None, None]):
    config_dacs(config='host', ch=ch)


def ddr_dacs(ch=[None, None]):
    config_dacs(config='DDR', ch=ch)


def measure_offsets(setup_relays=False):
    '''
    Measure and report all electrode offsets 
    '''
    if setup_relays:
        for dc_num in dc_configs:
            dcc = dc_configs[dc_num]
            dcc['ADC_SEL']="CAL_SIG2"  # required to digitize P2 
            dcc['DAC_SEL']="noDrive"
            dcc.pop('VSENSE', None)
            log_info, dc_configs[dc_num] = clamps[dc_num].configure_clamp(**dcc)

    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)
    v, datastreams = get_ads_voltages(ddr)

    for ds_name in datastreams:
        ds = datastreams[ds_name]
        if ds.units == 'V' and ds.name not in ['D0','D1','D2','D3']:
            print(f'Net {ds.net} = {np.mean(ds.data):2.4f} (ADC name {ds.name})')

    return v, datastreams


def electrode_offset_cal(clamp_num=2, chan=('A', 3), v_range=[-0.04, 0.04], target_v=0):
    '''
    adjust the clamp board offset adjust DAC and search for DAC value with closest to zero output 
    # The LSB step size is ~4.8 mV
    # offset adjustment is vdac*1.662 - 0.9940 

    # Does not setup relays 

    Parameters
        ----------
        clamp_num : int
            0,1,2,3 number of the clamp board 
        chan : tuple
            Converter and number for the relevant ADS8686 channel
        v_range : list of floats
            a high range and a low range to sweep around 0
        target_v : float
            target voltage to tune the offset to (nominally zero)

        Returns
        -------
        dac_val : int 
            the dac code with minimum offset      
    '''

    dac_v = (v_range[0] + 0.9940)/1.662
    dac_low = from_voltage(voltage=float(dac_v), num_bits=10, voltage_range=5, with_negatives=False)
    dac_v = (v_range[1] + 0.9940)/1.662
    dac_high = from_voltage(voltage=float(dac_v), num_bits=10, voltage_range=5, with_negatives=False)

    dac_val_arr = np.arange(dac_low, dac_high)
    print(dac_val_arr)
    dac_v_arr = to_voltage(data = dac_val_arr, num_bits=10, voltage_range=5, use_twos_comp=False)

    vclamp_v = np.array([])
    for dac_val in dac_val_arr:
        # if the input to from_voltage is a numpy. then it makes an array which causes the i2c write to fail
        clamps[clamp_num].DAC.write(int(dac_val))
        v, datastreams = get_ads_voltages(ddr)

        vclamp_v = np.append(vclamp_v, v[chan[0]][chan[1]])

    fig, ax = plt.subplots()
    ax.plot(dac_v_arr, vclamp_v, marker='o')

    idx = np.argmin(np.abs(vclamp_v - target_v))
    print(f'Writing DAC value of {int(dac_val_arr[idx])}')
    clamps[clamp_num].DAC.write(int(dac_val_arr[idx]))
    v, datastreams = get_ads_voltages(ddr)
    print(f'Check of optimized voltage gives {v[chan[0]][chan[1]]}')

    return dac_val_arr[idx]


# this continuously runs the bath clamp DC resistance measurement -- needs the batch clamp board to be the config_dict_test board 
if 0:
    setup_clamps(dc_under_test=dc_mapping['bath'], dc_disconnect=dc_mapping['clamp'])
    dc_configs[dc_mapping['bath']], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(dc_configs[dc_mapping['bath']],
                                                                                                              dc_under_test = dc_mapping['bath'],
                                                                                testing='bath', step=1, plt_data=True, 
                                                                                plt_fit=True, write_ddr=True); print(fit_resistance)

    for i in range(20):
        dc_configs[dc_mapping['bath']], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(dc_configs[dc_mapping['bath']], 
                                                                                                              dc_under_test = dc_mapping['bath'],
                                                                                    testing='bath', step=1, plt_data=True, 
                                                                                    plt_fit=True, write_ddr=False); print(fit_resistance)
        plt.pause(1) # plt.pause instead of time.sleep ensures that the plot is updated 
        plt.close('all')

# continuously run the vclamp measurement -- needs the voltage clamp (i) board to be the config_dict_test board 
if 0:
    setup_clamps(dc_under_test=dc_mapping['clamp'], dc_disconnect=dc_mapping['bath'])
    dc_configs[dc_mapping['clamp']], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(dc_configs[dc_mapping['clamp']], 
                                                                                                              dc_under_test = dc_mapping['clamp'],
                                                                                testing='vclamp', step=1, plt_data=True, 
                                                                                plt_fit=True, write_ddr=True); print(fit_resistance)

    for i in range(40):
        dc_configs[dc_mapping['clamp']], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(dc_configs[dc_mapping['clamp']], 
                                                                                    dc_under_test = dc_mapping['clamp'],
                                                                                    testing='vclamp', step=1, plt_data=True, 
                                                                                    plt_fit=True, write_ddr=False); print(fit_resistance)
        plt.pause(1) # plt.pause instead of time.sleep ensures that the plot is updated 
        plt.close('all')

if 0:
    # gnd I electrode via CAL relay, disconnect from the amplifier 
    dc_num = dc_mapping['bath']
    dc_configs[dc_num]['PClamp_CTRL'] = 1
    dc_configs[dc_num]['P1_E_CTRL'] = 1
    dc_configs[dc_num]['P2_E_CTRL'] = 1
    dc_configs[dc_num]['P1_CAL_CTRL'] = 1
    dc_configs[dc_num]['P2_CAL_CTRL'] = 1
    dc_configs[dc_num]['ADC_SEL'] = 'CAL_SIG1' # swap roles to check offsets 
    dc_configs[dc_num]['DAC_SEL'] = 'gnd_CAL2'
    clamps[dc_num].configure_clamp(**dc_configs[dc_num])  

    dc_num = dc_mapping['clamp']
    dc_configs[dc_num]['PClamp_CTRL'] = 1
    dc_configs[dc_num]['P1_E_CTRL'] = 1
    dc_configs[dc_num]['P2_E_CTRL'] = 1
    dc_configs[dc_num]['P1_CAL_CTRL'] = 0
    dc_configs[dc_num]['P2_CAL_CTRL'] = 0
    dc_configs[dc_num]['ADC_SEL'] = 'CAL_SIG1'
    dc_configs[dc_num]['DAC_SEL'] = 'gnd_CAL2'
    clamps[dc_num].configure_clamp(**dc_configs[dc_num])  

    v, datastreams = measure_offsets()
    # clamp_dac_val = electrode_offset_cal(clamp_num=dc_num, chan=daq.parameters['ads_map'][dc_num]['CAL_ADC'], v_range=[-0.04, 0.04], target_v=0)

    # measure offset of P1 electrode 
    # measure offset of V1 

    # calibrate offset of Clamp electrode 
    dc_num = dc_mapping['clamp']
    # relays for passive clamp and disconnect calibration 
    dc_configs[dc_num]['PClamp_CTRL'] = 1
    dc_configs[dc_num]['P1_E_CTRL'] = 0
    dc_configs[dc_num]['P2_E_CTRL'] = 0
    dc_configs[dc_num]['P1_CAL_CTRL'] = 1
    dc_configs[dc_num]['P2_CAL_CTRL'] = 0
    dc_configs[dc_num]['ADC_SEL'] = 'CAL_SIG1'
    dc_configs[dc_num]['DAC_SEL'] = 'noDrive'
    log_info_bath, dc_configs[dc_num] = clamps[dc_num].configure_clamp(**dc_configs[dc_num])    
    # zero DACs 
    quiet_dacs(ch=[None, None])
    clamp_dac_val = electrode_offset_cal(clamp_num=dc_num, chan=daq.parameters['ads_map'][dc_num]['CAL_ADC'], v_range=[-0.04, 0.04], target_v=0)

# TODO - measure holding current 

# TODO - square wave to check response 