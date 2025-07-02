"""
The system uses two Daughtercards with:
 1) the bath clamp - has a non-zero CMD voltage measures Im 
 2) the voltage clamp - zero CMD voltage, goal is to hold capacitor plate at ground 
 and 
 3) a voltage sense board that cannot be disconnected via relays (combines with the voltage clamp board to create feedback loop)

Demonstrate calibrations to determine voltage clamp electrode impedances
by measuring the time constant of a step applied to I electrode and measured by the V1 terminal 

Setup:
CAL_DAC voltage source connected to I terminal 
I drive relay opened to disconnect amplifier 
ADS8686 sequencer configured for just one sequence (Amp out) of the voltage clamp board and CAL ADC of the voltage clamp board to maximize sampling rate. 
must disconnect CC otherwise the Cm load is too significant 
must disconnect with relays P1 and P2 otherwise the Cm load is too significant 

Sept 2022/June 2023/May 2024

Lucas Koerner, koerner.lucas@stthomas.edu

"""
import os
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

results_dir = os.path.join(boards_path, 'results') # within the Git repo there is a results directory; 
                                                   # this allows the calibration results to be viewed on GitHub
UPDATE_RESULTS = True

FS = 5e6
SAMPLE_PERIOD = 1/FS
FS_ADS = 1e6
dac80508_offset = 0x8000
DC_NUMS = [0, 1, 3]

# bath: has P1, P2, and CC electrodes. Connects to 5 kOhm-ish electrodes. 
# clamp: drives the I electrode. The V1 electrode is amplified by the vclamp board (on micromanipulator) and is an input to this board 
#        just past the buffer amplifier (which is removed)
# vclamp: (other name is vsense) amplifies V1 but no drive circuitry 

dc_mapping = {'bath': 0, 'clamp': 1, 'vclamp': 3}  # TODO get from System class in electrodes.py

eps = Endpoint.endpoints_from_defines

pwr_setup = "3dual"
# -------- power supplies -----------
try:
    dc_pwr.get('id')
except:
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
        3: {'CAL_ADC': ('A', 4), 'AMP_OUT': ('B', 2)}}  # amp out will always be connected for vsense 
    if using daughter cards: 0,1,2 need A0,A1,A2,A3; B0,B1 
    '''
    dc_under_test = 0 
    adc_chan0 = daq.parameters['ads_map'][dc_under_test]['CAL_ADC'] # ('A', 0)
    adc_chan1 = daq.parameters['ads_map'][dc_under_test]['AMP_OUT'] # ('A', 1)
    adc_v1 = daq.parameters['ads_map'][dc_mapping['vclamp']]['AMP_OUT'] # ('A', 1)
    ads_sequencer_setup = [('2', '0')] # connect CAL_ADC and AMP_OUT of DC 1 which is the clamp board 
    ads_sequencer_setup = [('2', '0'), ('2','2')] # connect CAL_ADC and AMP_OUT of DC 1 which is the clamp board. Add in the vsense AMP_OUT 

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

    # turn off Current source calibration 
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
    print(f'SDAC chan 1: {sdac_1_out_chan}')
    ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
    ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
    ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
    ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

    # load slow DAC wave into DDR channels 6
    ddr.data_arrays[6] = sdac_wave
    # ddr.data_arrays[7] = sdac_sine # TODO: all cal channels are on the first DAC so setting [7] is not needed

    ddr.write_setup()
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()

    return sdac_wave, freq, indices
 

def collect_data(ddr, PLT=True, ads_chan=('A', 0), num_repeats=10, blk_multiples=40):
    
    ddr.repeat_setup() #Setup for reading new data without writing to the DDR again.

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    # 2,40 captures 2 periods of a sine-wave at 1 kHz
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', 
                                         num_repeats=num_repeats, blk_multiples=blk_multiples)  # blk multiples multiple of 10

    # update system connections since the daughtercard configurations have changed
    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys, inamp_gain_correct=clamps[dc_mapping['bath']].correct_inamp_gain)
    # Plot using datastreams 
    datastreams, log_info = rawh5_to_datastreams(data_dir, file_name.format(idx) + '.h5', ddr.data_to_names, 
                                                 daq, sys_connections, outfile = None)
 
    if PLT:
        fig, ax = plt.subplots()
        for n in ['V1', 'I', 'V1s']:
            datastreams[n].plot(ax, {'label': n})
        ax.legend()

        # TODO: measure with model cell disconnected to remove slow decays, 
        #       fit to determine amplitude 
        #       measure with 2 different attenuators 
        #       check datastreams code to figure out V1 vs V1s -- Vls is from the voltage sense board, V1 is AMP_OUT on the clamp board. Difference is only the attenuation.
        #       confirm that AMP_OUT on the clamp board has x1 gain -- must be since correction for the attenuation is all that's needed to align
        fig, ax = plt.subplots()
        gain = 60
        for n in ['V1', 'I', 'V1s']:
            if n == 'V1':
                scale = 10**(-13/20)*gain
            elif n == 'V1s':
                scale = gain
            else:
                scale = 1
            data = datastreams[n].data/datastreams[n].conversion_factor/scale # convert to ADS8686 codes since we are trying to determine various gains!
            t =  datastreams[n].create_time()
            ax.plot(t, data, label=n)
        ax.legend()
        fig.canvas.draw()
        fig.canvas.flush_events()

    else:
        ax=None

    return datastreams, log_info


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

def setup_clamps(dc_under_test='clamp', dc_disconnect='bath'):
    """
    setup clamp boards including the relay connections 

    dc_under_test : (int) the index of the daughter card that is being tested 
    dc_disconnect : (int) the index of the daughter card this is not being tested. Both electrode relays are disconnected. 
    
    """

    dc_configs = {}
    log_info_test, dc_configs[dc_under_test] = clamps[dc_under_test].configure_clamp(
        ADC_SEL="CAL_SIG2",
        DAC_SEL="drive_CAL2",
        CCOMP=cap,
        RF1=fb_res,  # feedback circuit
        ADG_RES=res,
        PClamp_CTRL=0, # keep open for calibration (default)
        P1_E_CTRL=0, # relay is closed to measure via AMP_OUT 
        P1_CAL_CTRL=0, # open relay (default) 
        P2_E_CTRL=1,  # open relay -- disconnect the amplifier and hence the feedback loop 
        P2_CAL_CTRL=1,  # close relay 
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )

    log_info_disconnect,  dc_configs[dc_disconnect] = clamps[dc_disconnect].configure_clamp(
        ADC_SEL="CAL_SIG1", # since the electrodes are disconnect there will be no calibration signal  
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
     # with the VCLAMP board these configurations are not impactful 
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
    dc_configs[dc_mapping['vclamp']]['VSENSE'] = 20.15 # extra information for the system_connections. Gain of the voltage clamp amplifier 

    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)

    return dc_configs, sys_connections

def measure_step(config_dict_test, dc_under_test, testing='vclamp', step=1, 
                        plt_data=True, plt_fit=False,
                        write_ddr=True):
    """
    
    Parameters 
    config_dict_test : dictionary of the configuration of the daughtercard under test
    dc_under_test : 
    testing : (str) configures the stimulus waveform based on 'bath' or 'clamp'
    step : (int)
    data : (dict) describes the measured voltage vs. time and the stimulus waveform configuration (amplitude, frequency, source) but does not store data 
    """
    # configure the waveforms based on the electrodes under test 
    if testing=='vclamp':
        freq = 40
        num_repeats=50 
        blk_multiples=40
        voltage_amp = 0.02 # saturates the vsense amp at 100 mV. This is 1/2 pk-pk 

    # DO NOT enable the current source 
    # daq.set_isel(port=1, channels=[dc_under_test]) # current based on DC#  

    if write_ddr: 
        dac_wave, freq, _ = dac_waveform(dc_under_test=dc_mapping['clamp'], amp=voltage_amp, 
                                         freq=freq, shape='SQ', source='v') # howland pump is always driven by BP_OUT0
    else:
        ddr.reset_mig_interface()
        ddr.write_finish()

    datastreams, log_info = collect_data(ddr, PLT=plt_data, ads_chan=daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
                                                    num_repeats=num_repeats, blk_multiples=blk_multiples)
    


    return datastreams, log_info

# Testing the vclamp side 
dc_under_test = dc_mapping['clamp'] 
dc_disconnect = dc_mapping['bath']

dc_configs, sys_connections = setup_clamps(dc_under_test=dc_under_test, dc_disconnect=dc_disconnect)

ddr.write_setup()
block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False) # TODO: is this actually used or just promptly overwritten?
ddr.reset_mig_interface()
ddr.write_finish()

# measure resistance 

#for re in [100, 200, 475, 1000]:
for re in [100]:
    for att in [13, 10]:

        input(f'Configure V1 electrode R to {re}')

        datastreams, log_info = measure_step(dc_configs[dc_under_test], dc_under_test=dc_under_test, testing='vclamp', 
                                                                                step=1, plt_data=True, plt_fit=True,
                                                                                write_ddr=True)

        filename = file_name + f'Re1_{re}k' + f'att_{att}dB'
        datastreams.to_h5(data_dir, filename + '.h5', log_info=log_info)

        # find edges and measure rise-time 
        step_info = datastreams['V1'].stepinfo_range([12000e-6, 13000e-6])

        # save this data as 

        # predicted capacitance 
        par_cap = step_info['RiseTime']/np.log(9)/(100e3 + re*1e3)
        step_info['capacitance'] = par_cap

        print(f'Rise-time {step_info["RiseTime"]}, capacitance {par_cap}')
        np.savez(os.path.join(data_dir, filename + 'stepinfo'), step_info) # saved to a Numpy npz file 

