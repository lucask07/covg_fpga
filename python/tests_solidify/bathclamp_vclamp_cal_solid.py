import os
from time import sleep
import time
import atexit
import numpy as np
import matplotlib.pyplot as plt
import copy
import pandas as pd
import json
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
from bath_clamp_setup_steps import *


DAQ_V = "2.1"

results_dir = os.path.join(boards_path, 'results') # within the Git repo there is a results directory; 
                                                   # this allows the calibration results to be viewed on GitHub
UPDATE_RESULTS = True

FS = 5e6
SAMPLE_PERIOD = 1 / FS
FS_ADS = 1e6
dac80508_offset = 0x8000
DC_NUMS = [0, 1, 2, 3] # step response -> VSENSE2 is True
ads_voltage_range = 5  # need this for to_voltage later 

file_name = time.strftime("%Y%m%d-%H%M%S")
idx = 0
chan = 3 # TODO: Questionable

dc_under_test = 0 # Initial dc_under_test

# daughter-card settings should be a do not care since the analog feedback loop is disconnected
fb_res = 2.1  # resistors and cap have changed so this does not correspond to typical bath clamp board
res = 100  # kOhm
cap = 47

## TODO: Add a conditional function here
device_compilation = None
if __name__ == '__main__' and device_compilation == None:
    device_compilation = device_setup(allfour=True)

# Set the dac channel
adc_chan0 = device_compilation.fpga_board.daq.parameters['ads_map'][dc_under_test]['CAL_ADC']  # ('A', 0)
adc_chan1 = device_compilation.fpga_board.daq.parameters['ads_map'][dc_under_test]['AMP_OUT']  # ('A', 1)
adc_v1 = device_compilation.fpga_board.daq.parameters['ads_map'][device_compilation.fpga_board.dc_mapping['clamp']]['AMP_OUT']  # ('A', 1)



#####################################################################
## GENERAL DICT TO LOG EXPERIMENT PROCESS ###########################
EXPERIMENTS = dict()
#####################################################################






def dac_waveform(dc_under_test, amp, freq=1000, shape='SINE', source='v', periods=None):
    """
    dc_under_test: the daughter card the calibration signal should be sent to
    amp: float either voltage or current in uA (amplitude, not pk-pk)
    freq: waveform frequency in Hz or nd.array if shape is 'CHIRP'
    shape: 'SINE' or 'SQ' or 'CHIRP'
    source: either 'v' or 'i'
    periods: nd.array of periods or int 
    """
    for i in range(6):
        # set all fast-DAC DDR data to midscale
        device_compilation.fpga_board.ddr.data_arrays[i][:] = 0x2000

    if source == 'v':
        # source voltage
        sdac_amp_volt = amp / 3  # 1 Volt amplitude. 2 V peak to peak # amplitude was checked on oscilloscope (bipolar creates gain of *3 with 0 mean)
        # at 1 V the DAC code is max=58928, min=6554
    if source == 'i':
        # max is 1.25 V which gives 0.8 uA 
        sdac_amp_volt = 1.25 * (amp / 0.8)  # TODO make property of DAQ board

    sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)
    # subtract one since if this value is precisely 2^15 we in effect get 0 for both high and low amplitude.
    if sdac_amp_code == 2 ** 15:
        sdac_amp_code = sdac_amp_code - 1
    print(f'Max sdac amp {sdac_amp_code}')

    # Data for the 2 DAC80508 "Slow DACs"
    if shape == 'SINE':
        sdac_wave, freq = device_compilation.fpga_board.ddr.make_sine_wave(amplitude=sdac_amp_code,
                                             frequency=freq, offset=dac80508_offset)
        indices = None
    elif shape == 'SQ':
        # low, high
        sq_length = int(1 / DDR3.UPDATE_PERIOD / freq)
        if sdac_amp_code > dac80508_offset:
            print(f'error, square-wave amplitude of {sdac_amp_code} too large ')
        sdac_wave = device_compilation.fpga_board.ddr.make_step(low=int(dac80508_offset - sdac_amp_code),
                                  high=int(dac80508_offset + sdac_amp_code),
                                  length=sq_length)
        indices = None
    elif shape == 'CHIRP':
        if sdac_amp_code > dac80508_offset:
            print(f'error, square-wave amplitude of {sdac_amp_code} too large ')
        sdac_wave, freq, indices = device_compilation.fpga_board.ddr.make_chirp(amplitude=sdac_amp_code,
                                                  frequencies=freq, periods=periods,
                                                  offset=dac80508_offset)

    # Specify output channel for DAC80508
    sdac_ch = device_compilation.fpga_board.daq.parameters['gp_dac_map'][dc_under_test]['CAL']
    if sdac_ch[0] == 1:
        sdac_1_out_chan = sdac_ch[1]
    if sdac_ch[0] == 2:
        sdac_2_out_chan = sdac_ch[1]  # don't care, this channel is not connected to CAL
    else:
        sdac_2_out_chan = 0  # need a default channel
    # Clear bits in the FDAC DDR stream that store the slow DAC channel

    # TODO: make this a method of the DDR class 
    for i in range(6):
        device_compilation.fpga_board.ddr.data_arrays[i] = np.bitwise_and(
            device_compilation.fpga_board.ddr.data_arrays[i], 0x3fff
        )
    # Load data into DDR
    # Set channel bits
    device_compilation.fpga_board.ddr.data_arrays[0] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13
    )
    device_compilation.fpga_board.ddr.data_arrays[1] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14
    )
    device_compilation.fpga_board.ddr.data_arrays[2] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13
    )
    device_compilation.fpga_board.ddr.data_arrays[3] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14
    )

    # load slow DAC sine-wave in DDR channels 6
    device_compilation.fpga_board.ddr.data_arrays[6] = sdac_wave
    # ddr.data_arrays[7] = sdac_sine # TODO: all cal channels are on the first DAC so setting [7] is not needed

    device_compilation.fpga_board.ddr.write_setup()
    block_pipe_return, speed_MBs = device_compilation.fpga_board.ddr.write_channels(set_ddr_read=False)
    device_compilation.fpga_board.ddr.reset_mig_interface()
    device_compilation.fpga_board.ddr.write_finish()

    return sdac_wave, freq, indices


def get_ads_voltages(ddr, num_repeats=1, blk_multiples=10):
    """
    read a short series from DDR in order to calculate the DC value of ADS channels 
        like a volt meter 
    
    Returns 
        volts: dict [chan][num]
            average voltage value of given channel ('A' or 'B') and number
    """
    ddr.repeat_setup()  # Setup for reading new data without writing to the DDR again.

    # saves data to a file
    chan_data_one_repeat = ddr.save_data(data_dir, 'voltage_read.h5', num_repeats=num_repeats,
                                         blk_multiples=blk_multiples)  # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name='voltage_read.h5', chan_list=np.arange(8))

    adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, reading_error = ddr.data_to_names(chan_data)

    ############### extract the ADS data ############
    ads_data_v = {}
    for letter in ['A', 'B']:
        ads_data_v[letter] = np.array(to_voltage(
            ads_data_tmp[letter], num_bits=16, voltage_range=ADS8686_VOLTAGE_RANGE * 2, use_twos_comp=False))

    total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1]))  # get the right length
    total_seq_cnt[::2] = ads_seq_cnt[0]
    total_seq_cnt[1::2] = ads_seq_cnt[1]
    ads_separate_data = separate_ads_sequence(ADS8686_SEQUENCER_SETUP, ads_data_v, total_seq_cnt, slider_value=4)

    volts = {}

    for chan in ads_separate_data:
        volts[chan] = {}
        for num in ads_separate_data[chan]:
            v = np.mean(ads_separate_data[chan][num])
            volts[chan][num] = v
            print(f'Channel {chan}{num} at {v:.4g} [V]')

    # update system connections since the daughtercard configurations have changed
    sys_connections = create_sys_connections(
        dc_configs, 
        device_compilation.fpga_board.daq, 
        device_compilation.instrument.ephys_sys
    )
    # Plot using datastreams 
    datastreams, log_info = rawh5_to_datastreams(data_dir, 'voltage_read.h5', ddr.data_to_names,
                                                 device_compilation.fpga_board.daq, 
                                                 sys_connections, outfile=None)

    return volts, datastreams

def collect_data(ddr, PLT=True, ads_chan=('A', 0), num_repeats=10, blk_multiples=40):
    ddr.repeat_setup()  # Setup for reading new data without writing to the DDR again.

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    # 2,40 captures 2 periods of a sine-wave at 1 kHz
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5',
                                         num_repeats=num_repeats,
                                         blk_multiples=blk_multiples)  # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(
        idx) + '.h5', chan_list=np.arange(8))

    adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, reading_error = ddr.data_to_names(chan_data)
    print(f'Timestamp spans {5e-9 * (timestamp[-1] - timestamp[0]) * 1000} [ms]')

    ############### extract the ADS data ############
    ads_data_v = {}
    for letter in ['A', 'B']:
        ads_data_v[letter] = np.array(to_voltage(
            ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range * 2, use_twos_comp=False))

    total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1]))  # get the right length
    total_seq_cnt[::2] = ads_seq_cnt[0]
    total_seq_cnt[1::2] = ads_seq_cnt[1]
    ads_separate_data = separate_ads_sequence(ADS8686_SEQUENCER_SETUP, ads_data_v, total_seq_cnt, slider_value=4)

    # ADS8686 data and plot 
    volt = ads_separate_data[ads_chan[0]][ads_chan[1]] # letter and number 
    t_ads = np.arange(0, len(volt)) * (1 / FS_ADS) * len(ADS8686_SEQUENCER_SETUP)
    if PLT:
        fig, ax = plt.subplots()
        ax.plot(t_ads * 1e6, volt, marker='+', label=f'ADS: {chan}')
        ax.legend()
        ax.set_xlabel('s [us]')
        ax.set_title('ADS8686 data')
    else:
        ax = None
    return volt, t_ads, ads_separate_data, ax

def setup_clamps(dc_under_test, dc_disconnect):
    """
    setup clamp boards including the relay connections 

    dc_under_test : (int) the index of the daughter card that is being tested 
    dc_disconnect : (int) the index of the daughter card this is not being tested. Both electrode relays are disconnected. 
    
    """

    dc_configs = {}
    log_info_test, dc_configs[dc_under_test] = device_compilation.fpga_board.clamps[dc_under_test].configure_clamp(
        ADC_SEL=None,
        DAC_SEL="gnd_both",
        CCOMP=cap,
        RF1=fb_res,  # feedback circuit
        ADG_RES=res,
        PClamp_CTRL=1, # keep open for calibration (default) 0 1 1 1 1
        P1_E_CTRL=1, # open relay
        P1_CAL_CTRL=1, # close relay 
        P2_E_CTRL=1,  # open relay
        P2_CAL_CTRL=1,  # close relay 
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )

    log_info_disconnect,  dc_configs[dc_disconnect] = device_compilation.fpga_board.clamps[dc_disconnect].configure_clamp(
        ADC_SEL=None, # since the electrodes are disconnect there will be no calibration signal  
        DAC_SEL="gnd_both",
        CCOMP=cap,
        RF1=fb_res,  # feedback circuit
        ADG_RES=res,
        PClamp_CTRL=1,  # open relay (default) 0 1 0 1 0
        P1_E_CTRL=1,  # open relay
        P1_CAL_CTRL=0,  # open relay (default)
        P2_E_CTRL=1,  # open relay
        P2_CAL_CTRL=0,  # open relay (default)
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1, # 0 1
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    log_info, dc_configs[device_compilation.fpga_board.dc_mapping['guard']] = device_compilation.fpga_board.clamps[device_compilation.fpga_board.dc_mapping['guard']].configure_clamp(
        ADC_SEL="CAL_SIG2",  # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize P1; must also close the corresponding relay. Note that CAL_SIG1 and P1_CAL_CTRL=1 caused oscillations.
        DAC_SEL="gnd_both",
        CCOMP=cap,
        RF1=fb_res,  # feedback circuit
        ADG_RES=res,
        PClamp_CTRL=1, # we can also close the clamp control to trap the current within the circle only
        P1_E_CTRL=1,
        P1_CAL_CTRL=0,
        P2_E_CTRL=1,
        P2_CAL_CTRL=0,
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
     # with the VCLAMP board these configurations are not impactful 
    log_info_vclamp, dc_configs[device_compilation.fpga_board.dc_mapping['vclamp']] = device_compilation.fpga_board.clamps[device_compilation.fpga_board.dc_mapping['vclamp']].configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="gnd_both",
        CCOMP=cap,
        RF1=fb_res,  # feedback circuit
        ADG_RES=res,
        PClamp_CTRL=0,  # open relay (default)
        P1_E_CTRL=1,  # open relay
        P1_CAL_CTRL=0,  # open relay (default)
        P2_E_CTRL=1,  # open relay
        P2_CAL_CTRL=0,  # open relay (default)
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    
    dc_configs[device_compilation.fpga_board.dc_mapping['vclamp']]['VSENSE'] = 60.24 # extra information for the system_connections. Gain of the voltage clamp amplifier # TODO: uncomment when done
    # dc_configs[dc_mapping['clamp']]['VSENSE'] = 60.24*10**(-11.7868/20) 
    sys_connections = create_sys_connections(dc_configs, device_compilation.fpga_board.daq, device_compilation.instrument.ephys_sys)

    return dc_configs, sys_connections

def measure_resistance(config_dict_test, dc_configs, dc_under_test, testing='bath', step=1, 
                        plt_data=True, plt_fit=False,
                        write_ddr=True):
    """
    Source a current to measure Re1 + Re2 
    
    works for bath electrode using DC response 
    needs to use RC response 300 kOhm * 2 pF 
    connect a relay to the vsense electrode 

    Parameters 
    config_dict_test : dictionary of the configuration of the daughtercard under test
    dc_under_test : 
    testing : (str) configures the stimulus waveform based on 'bath' or 'clamp'
    step : (int)
    data : (dict) describes the measured voltage vs. time and the stimulus waveform configuration (amplitude, frequency, source) but does not store data 
    """
    # configure the waveforms based on the electrodes under test 
    if testing=='bath':
        freq = 200
        num_repeats=10 
        blk_multiples=40
        current_amp = 0.8 # amplitude not peak-to-peak 
    if testing=='clamp':
        freq = 40 # chirp frequencies were confirmed on the oscilloscope. First three frequencies: 40, 69, 120 which is consistent with hte analysis. 
        num_repeats=50 
        blk_multiples=40
        current_amp = 0.01 # 10 nA TODO: ensure that current is sourced only for a short amount of time so that we don't blow up the cell

    device_compilation.fpga_board.daq.set_isel(port=1, channels=[dc_under_test]) # current based on DC#  
    config_dict_test['ADC_SEL'] = 'CAL_SIG2' # this is the force terminal; drive and measure on the same channel 
    # Cannot share same data acquisation
    dc_configs[device_compilation.fpga_board.dc_mapping['clamp' if testing=='bath' else 'bath']]['ADC_SEL'] = 'CAL_SIG1'

    # TODO: How is the disconnected clamp board configured? 
    if testing == 'bath':
        config_dict_test['DAC_SEL'] = 'drive_CAL2_gnd_CAL1'
        dc_configs[device_compilation.fpga_board.dc_mapping['clamp']]['DAC_SEL'] = 'drive_CAL1'
    # elif testing == 'vlcamp':
    elif testing == "clamp":
        config_dict_test['DAC_SEL'] = 'drive_CAL2'
        dc_configs[device_compilation.fpga_board.dc_mapping['bath']]['DAC_SEL'] = 'drive_CAL1'
    log_info_bath, config_dict_test = device_compilation.fpga_board.clamps[dc_under_test].configure_clamp(**config_dict_test)
    dc_dis = device_compilation.fpga_board.dc_mapping['clamp' if testing=='bath' else 'bath']
    log_info_dut, dc_configs[dc_dis] = device_compilation.fpga_board.clamps[dc_dis].configure_clamp(**dc_configs[dc_dis])

    print(testing)
    print(dc_configs)

    # inject current square wave, expect around 8 mV amplitude from 0.8 uA*10e3, 16 mV pk-pk         
    if write_ddr:
        dac_wave, freq, _ = dac_waveform(0, amp=current_amp, freq=freq, shape='SQ',
                                         source='i')  # howland pump is always driven by BP_OUT0
    else:
        device_compilation.fpga_board.ddr.reset_mig_interface()
        device_compilation.fpga_board.ddr.write_finish()

    volt, t, ads_separate_data, ax = collect_data(
        device_compilation.fpga_board.ddr, PLT=plt_data, 
        ads_chan=device_compilation.fpga_board.daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
        num_repeats=num_repeats, 
        blk_multiples=blk_multiples
    )
    
    fig = None
    if testing == 'clamp':
        v_vclamp = ads_separate_data[adc_v1[0]][adc_v1[1]]  # TODO: generalize if boards swap DAQ sockets
        idx = np.min([len(t), len(v_vclamp)])
        ax.plot(t[:idx]*1e6, v_vclamp[:idx]/20.15, label='V1 [V]')    
        ax.legend()

        idx = np.min([len(t), len(v_vclamp), len(volt)])
        fig, ax = plt.subplots()
        ax.plot(t[:idx]*1e6, v_vclamp[:idx]/20.15 - volt[:idx], label='V1 - V(I) [V]')
        volt = v_vclamp[:idx]/20.15 - volt[:idx] # fit this difference of voltages. #TODO: parameterize this specific gain of the voltage clamp 
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
                   'bath_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['bath']]),
                   'voltage_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['clamp']]),
                   'vsense': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['vclamp']])}
    try:
        fit_resistance, pcov, mesg = r_from_square(r_total_guess, rdata, PLT=plt_fit)
    except:
        fit_resistance = pcov = mesg = None
    
    # For measure resistance, the value is the list, whose first value refers to plot object, 
    # second refers to relays states, ADC, DAC, and third the measuring parameters
    EXPERIMENTS.update({f"measure resistance of {testing}" : 
                        [fig, 
                        {k : dc_configs[dc_under_test][k] for k in ['ADC_SEL', 
                                                                    'DAC_SEL',  
                                                                    'PClamp_CTRL', 
                                                                    'P1_E_CTRL', 
                                                                    'P2_E_CTRL', 
                                                                    'P1_CAL_CTRL', 
                                                                    'P2_CAL_CTRL']}, 
                        copy.deepcopy(rdata[step])]})

    return config_dict_test, rdata, fit_resistance, pcov, mesg, ads_separate_data

def chirp_test(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp):
    """
    Measure a transfer function versus frequency using a chirp signal.
    For each drive electrode measure at driving point (as a calibration) and at the other electrode

    Parameters: 
        testing : (str)
        data_chirp : (list of dicts) input so this can be appended 
        dc_configs : configuration of daughter cards 
        dc_under_test : (int)
        voltage_amp : (float) voltage amplitude of chirp stimulus 
        step_chirp : (int) the step index for the list of dicts that store the final results 
    """
    # A dictionary to keep track of relay states + measured parameters
    measured_params = dict()

    for drive_elec in [1,2]:
        if drive_elec == 1:  # upload the chirp signal to DDR only for drive 1 since we repeat for drive electrode 2 
            periods = np.ones(len(freq_arr))*30
            dac_wave, freq_chirp, indices = dac_waveform(dc_under_test, amp=voltage_amp, 
                                                    freq=freq_arr, shape='CHIRP', source='v', 
                                                    periods=periods)
            total_chirp_time = np.sum(1/freq_arr*periods)
            print(f'Total chirp time = {total_chirp_time}')
            # find the last index to 'download' using the starting index of the last frequency
            end_index = indices[-1][0] + periods[-1] * ((1 / DDR3.UPDATE_PERIOD) / freq_arr[-1])

        # measure at same point as drive, this acts as an amplitude calibration (for a transfer function of Vout/Vin this measures Vin)
        if drive_elec == 1:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG1'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL1'  # do not ground CAL2; won't work for isolated Vsense board
            dc_configs[dc_disconnect]['ADC_SEL'] = 'CAL_SIG2'
            dc_configs[dc_disconnect]['DAC_SEL'] = 'drive_CAL2'
        elif drive_elec == 2:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG2'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL2' # do not ground CAL1 
            dc_configs[dc_disconnect]['ADC_SEL'] = 'CAL_SIG1'
            dc_configs[dc_disconnect]['DAC_SEL'] = 'drive_CAL1'

        # dc_configs[dc_under_test]['P1_CAL_CTRL'] = 1
        # dc_configs[dc_under_test]['P2_CAL_CTRL'] = 1

        log_info_bath, dc_configs[dc_under_test] = device_compilation.fpga_board.clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])
        log_info_dut, dc_configs[dc_disconnect] = device_compilation.fpga_board.clamps[dc_disconnect].configure_clamp(**dc_configs[dc_disconnect])

        

        # download ADC data so that np.max(t_chirp) = total_chirp_time 
        # This can also be checked by the indices (2.5 MSPS)
        #   versus the length of volt_chirp (@ 1 MSPS / len(ads_sequencer_setup))
        blk_mult = 120
        num_repeats_chirp = int(np.ceil(end_index * 2 / (2048 / 16) / blk_mult))
        volt_chirp, t_chirp, ads_separate_data_chirp, ax = collect_data(device_compilation.fpga_board.ddr, PLT=False,
                                                                        ads_chan=
                                                                        device_compilation.fpga_board.daq.parameters['ads_map'][dc_under_test][
                                                                            'CAL_ADC'],
                                                                        num_repeats=num_repeats_chirp,
                                                                        blk_multiples=blk_mult)
        
        # Round up relays states first
        param_list = list()
        measured_params[f'drive_elec_{drive_elec}'] = param_list
        param_list.extend([
            {
                    k : dc_configs[dc_under_test][k] for k in [
                        'ADC_SEL', 'DAC_SEL', 
                        'PClamp_CTRL', 'P1_E_CTRL', 'P2_E_CTRL', 'P1_CAL_CTRL', 
                        'P2_CAL_CTRL'
                    ]
                }, dict()]
        )

        for freq, idx in zip(freq_arr, indices):
            chirp_idx = []
            chirp_idx.append(int(idx[0] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))
            chirp_idx.append(int(idx[1] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))

            if dc_under_test==device_compilation.fpga_board.dc_mapping['bath']:
                v1_gain = 1
            else:
                v1_gain = 60.24*10**(-11.7868/20)
            data_chirp[step_chirp] = {'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]],  # measured stimulus data
                                      't': t_chirp[chirp_idx[0]:chirp_idx[1]],
                                      'v1': ads_separate_data_chirp[adc_v1[0]][adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
                                      'v1_gain': v1_gain, 
                                      'src': 'v',
                                      'shape': 'SINE',
                                      'freq': freq,  # stimulus frequency
                                      'amp': voltage_amp,
                                      'dc_under_test': dc_under_test,
                                      'bath_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['bath']]),
                                      'voltage_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['clamp']]),
                                      'vsense': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['vclamp']])}
            param_list[1].update({step_chirp : 
                                    {k : copy.deepcopy(v) for k,v in data_chirp[step_chirp].items() if k not in ['bath_clamp', 'voltage_clamp', 'vsense']}})
            step_chirp += 1

        # swap roles ADC_SEL electrode; keep drive electrode the same  
        # for the clamp board cannot drive CAL_SIG1 since that is the buffered output of the vsense board 
        # consider disconnecting the membrane capacitance and use that as a calibration measurement
        if drive_elec == 1:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG2'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL1'  # do not ground CAL2
            dc_configs[dc_disconnect]['ADC_SEL'] = 'CAL_SIG1'
            dc_configs[dc_disconnect]['DAC_SEL'] = 'drive_CAL2'
        elif drive_elec == 2:
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG1'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL2'  # do not ground CAL1
            dc_configs[dc_disconnect]['ADC_SEL'] = 'CAL_SIG2'
            dc_configs[dc_disconnect]['DAC_SEL'] = 'drive_CAL1'
        log_info_bath, dc_configs[dc_under_test] = device_compilation.fpga_board.clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])
        log_info_dut, dc_configs[dc_disconnect] = device_compilation.fpga_board.clamps[dc_disconnect].configure_clamp(**dc_configs[dc_disconnect])

        volt_chirp, t_chirp, ads_separate_data_chirp, ax = collect_data(device_compilation.fpga_board.ddr, PLT=False,
                                                                        ads_chan=
                                                                        device_compilation.fpga_board.daq.parameters['ads_map'][dc_under_test][
                                                                            'CAL_ADC'],
                                                                        num_repeats=num_repeats_chirp,
                                                                        blk_multiples=blk_mult)

        # Also do the same thing when drive elecs swap their roles
        param_list_swap = list()
        measured_params[f'drive_elec_{drive_elec}_swap'] = param_list_swap
        param_list_swap.extend([
            {
                    k : dc_configs[dc_under_test][k] for k in [
                        'ADC_SEL', 'DAC_SEL', 
                        'PClamp_CTRL', 'P1_E_CTRL', 'P2_E_CTRL', 'P1_CAL_CTRL', 
                        'P2_CAL_CTRL'
                    ]
                }, dict()]
        )
        for freq, idx in zip(freq_arr, indices):
            chirp_idx = []
            chirp_idx.append(int(idx[0] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))
            chirp_idx.append(int(idx[1] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))

            data_chirp[step_chirp] = {'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]],  # measured data
                                      't': t_chirp[chirp_idx[0]:chirp_idx[1]],
                                      'v1': ads_separate_data_chirp[adc_v1[0]][adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
                                      'v1_gain': v1_gain, 
                                      'src': 'v',
                                      'shape': 'SINE',
                                      'freq': freq,  # stimulus frequency
                                      'amp': voltage_amp,
                                      'dc_under_test': dc_under_test,
                                      'vclamp': 'disconnect',
                                      'bath_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['bath']]),
                                      'voltage_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['clamp']]),                                
                                      'vsense': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['vclamp']])}
            param_list_swap[1].update({
                step_chirp : 
                {k : copy.deepcopy(v) for k,v in data_chirp[step_chirp].items() if k not in ['bath_clamp', 'voltage_clamp', 'vsense']}})
            step_chirp += 1

    # save Chirp data 
    filename_chirp = f'imp_all_steps_chirp_{file_name}' + '_{}'
    np.savez(os.path.join(data_dir, filename_chirp.format(testing)), data_chirp) # saved to a Numpy npz file 

    return data_chirp, measured_params, filename_chirp, step_chirp

def chirp_test_vclamp(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp):
    """
    Measure a transfer function versus frequency using a chirp signal.
    Optimized for the voltage clamp 

    For each drive electrode measure at driving point (as a calibration) and at the other electrode

    Parameters: 
        testing : (str)
        data_chirp : (list of dicts) input so this can be appended 
        dc_configs : configuration of daughter cards 
        dc_under_test : (int)
        voltage_amp : (float) voltage amplitude of chirp stimulus 
        step_chirp : (int) the step index for the list of dicts that store the final results 
    """
    # Create a dict to track measured parameters
    measured_params = dict()

    for float_dut in [True, False]:
        if float_dut:  # upload the chirp signal to DDR only for drive 1 since we repeat for the next measurement
            periods = np.ones(len(freq_arr))*30
            dac_wave, freq_chirp, indices = dac_waveform(dc_under_test, amp=voltage_amp, 
                                                    freq=freq_arr, shape='CHIRP', source='v', 
                                                    periods=periods)
            total_chirp_time = np.sum(1/freq_arr*periods)
            print(f'Total chirp time = {total_chirp_time}')
            # find the last index to 'download' using the starting index of the last frequency
            end_index = indices[-1][0] + periods[-1] * ((1 / DDR3.UPDATE_PERIOD) / freq_arr[-1])

        # measure at same point as drive, this acts as an amplitude calibration (for a transfer function of Vout/Vin this measures Vin)
        """
        if float_dut:
            dc_configs[dc_mapping['bath']]['P1_E_CTRL'] = 1 # open
            dc_configs[dc_mapping['bath']]['P2_E_CTRL'] = 1 # open
            dc_configs[dc_mapping['bath']]['P1_CAL_CTRL'] = 0 # open
            dc_configs[dc_mapping['bath']]['P2_CAL_CTRL'] = 0 # open 
        else:
            dc_configs[dc_mapping['bath']]['P1_E_CTRL'] = 1 # open
            dc_configs[dc_mapping['bath']]['P2_E_CTRL'] = 1 # open
            dc_configs[dc_mapping['bath']]['P1_CAL_CTRL'] = 1 # open
            dc_configs[dc_mapping['bath']]['P2_CAL_CTRL'] = 1 # open 
        dc_configs[dc_mapping['bath']]['DAC_SEL'] = 'gnd_both' 
        """

        # setup the voltage clamp board 
        dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG2'
        dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL2' # do not ground CAL1 
        dc_configs[dc_disconnect]['ADC_SEL'] = 'CAL_SIG1'
        dc_configs[dc_disconnect]['DAC_SEL'] = 'drive_CAL1'

        # dc_configs[dc_under_test]['P1_CAL_CTRL'] = 1
        # dc_configs[dc_under_test]['P2_CAL_CTRL'] = 1

        log_info_dut, dc_configs[dc_under_test] = device_compilation.fpga_board.clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])
        log_info_dut, dc_configs[dc_disconnect] = device_compilation.fpga_board.clamps[dc_disconnect].configure_clamp(**dc_configs[dc_disconnect])
        # log_info_load, dc_configs[dc_mapping['bath']] = clamps[dc_mapping['bath']].configure_clamp(**dc_configs[dc_mapping['bath']])

        # download ADC data so that np.max(t_chirp) = total_chirp_time 
        # This can also be checked by the indices (2.5 MSPS)
        #   versus the length of volt_chirp (@ 1 MSPS / len(ads_sequencer_setup))
        blk_mult = 120
        num_repeats_chirp = int(np.ceil(end_index * 2 / (2048 / 16) / blk_mult))
        volt_chirp, t_chirp, ads_separate_data_chirp, ax = collect_data(device_compilation.fpga_board.ddr, PLT=False,
                                                                        ads_chan=
                                                                        device_compilation.fpga_board.daq.parameters['ads_map'][dc_under_test][
                                                                            'CAL_ADC'],
                                                                        num_repeats=num_repeats_chirp,
                                                                        blk_multiples=blk_mult)
        
        # Round up the relays states first, the second element in the list refers to data in each step chirp
        param_list = list()
        measured_params[f'float_dut_{float_dut}'] = param_list
        param_list.extend(
            [
                 {
                    k : dc_configs[dc_under_test][k] for k in [
                        'ADC_SEL', 'DAC_SEL', 
                        'PClamp_CTRL', 'P1_E_CTRL', 'P2_E_CTRL', 'P1_CAL_CTRL', 
                        'P2_CAL_CTRL'
                    ]
                }, dict()]
            )
        
        for freq, idx in zip(freq_arr, indices):
            chirp_idx = []
            chirp_idx.append(int(idx[0] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))
            chirp_idx.append(int(idx[1] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))

            if dc_under_test==device_compilation.fpga_board.dc_mapping['bath']:
                v1_gain = 1
            else:
                v1_gain = 60.24*10**(-11.7868/20)
            data_chirp[step_chirp] = {'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]],  # measured stimulus data
                                      't': t_chirp[chirp_idx[0]:chirp_idx[1]],
                                      'v1': ads_separate_data_chirp[adc_v1[0]][adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
                                      'v1_gain': v1_gain, 
                                      'src': 'v',
                                      'shape': 'SINE',
                                      'freq': freq,  # stimulus frequency
                                      'amp': voltage_amp,
                                      'dc_under_test': dc_under_test,
                                      'bath_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['bath']]),
                                      'voltage_clamp': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['clamp']]),
                                      'vsense': copy.deepcopy(dc_configs[device_compilation.fpga_board.dc_mapping['vclamp']])}
            # Round all the step chirp data into the second dict of the list
            param_list[1].update({
                step_chirp : 
            {k : copy.deepcopy(v) for k,v in data_chirp[step_chirp].items() if k not in ['bath_clamp', 'voltage_clamp', 'vsense']}
            })
            step_chirp += 1

        # Doesn't help to swap roles of ADC_SEL electrode; keep drive electrode the same  
        # for the clamp board cannot drive CAL_SIG1 since that is the buffered output of the vsense board 
        # consider disconnecting the membrane capacitance and use that as a calibration measurement
        # if drive_elec == 1:
        #     dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG2'
        #     dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL1'  # do not ground CAL2
        # elif drive_elec == 2:
        #     dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG1'
        #     dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL2'  # do not ground CAL1
        # log_info_bath, dc_configs[dc_under_test] = clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])

        # volt_chirp, t_chirp, ads_separate_data_chirp, ax = collect_data(ddr, PLT=False,
        #                                                                 ads_chan=
        #                                                                 daq.parameters['ads_map'][dc_under_test][
        #                                                                     'CAL_ADC'],
        #                                                                 num_repeats=num_repeats_chirp,
        #                                                                 blk_multiples=blk_mult)

        # for freq, idx in zip(freq_arr, indices):
        #     chirp_idx = []
        #     chirp_idx.append(int(idx[0] / len(ads_sequencer_setup) / (2.5)))
        #     chirp_idx.append(int(idx[1] / len(ads_sequencer_setup) / (2.5)))

        #     data_chirp[step_chirp] = {'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]],  # measured data
        #                               't': t_chirp[chirp_idx[0]:chirp_idx[1]],
        #                               'v1': ads_separate_data_chirp[adc_v1[0]][adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
        #                               'v1_gain': v1_gain, 
        #                               'src': 'v',
        #                               'shape': 'SINE',
        #                               'freq': freq,  # stimulus frequency
        #                               'amp': voltage_amp,
        #                               'dc_under_test': dc_under_test,
        #                               'vclamp': 'disconnect',
        #                               'bath_clamp': copy.deepcopy(dc_configs[dc_mapping['bath']]),
        #                               'voltage_clamp': copy.deepcopy(dc_configs[dc_mapping['clamp']]),                                
        #                               'vsense': copy.deepcopy(dc_configs[dc_mapping['vclamp']])}
        #     step_chirp += 1

    # save Chirp data 
    filename_chirp = f'imp_all_steps_chirp_floatdut_{file_name}' + '_{}'
    np.savez(os.path.join(data_dir, filename_chirp.format(testing)), data_chirp) # saved to a Numpy npz file 

    return data_chirp, measured_params, filename_chirp, step_chirp

def transfer_functions_fit(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp, 
                           r_total_guess, data_dir, filename_chirp, PLT=True):
    measured_params = None
    if testing == 'bath':
        data_chirp, measured_params, filename_chirp, step_chirp = chirp_test(testing, data_chirp, dc_configs, dc_under_test, 
                                                                voltage_amp, step_chirp)
    elif testing=='clamp':
        data_chirp, measured_params, filename_chirp, step_chirp = chirp_test_vclamp(testing, data_chirp, dc_configs, dc_under_test, 
                                                            voltage_amp, step_chirp)
    # process data
    if testing == 'clamp':
        tf_type = 'vclamp'
        r_total_guess = 300e3
    elif testing == 'bath':
        tf_type = 'elec_r_cc'
        r_total_guess = 8e3

    # calculates both the total resistance (measured via current injection) and the isolated resistance infered by transfer functions 
    # fails with tf_type = 'vclamp'
    predicted_res, res_fit_mesg, component_fits, fit_notes, components, figures_table = total_res_iso_res(data_dir, filename_chirp.format(testing) + '.npz',  
                                                                                        r_total_guess, tf_type, PLT=True)
    print(components)

    # For transfer function fit: a list [plot object, measured parameters]
    EXPERIMENTS.update({
        f'Transfer functions fit for {testing}' : 
        [
            figures_table, 
            measured_params
        ]
    })

    return predicted_res, res_fit_mesg, component_fits, fit_notes, components, data_chirp, filename_chirp, step_chirp

#############################################################
####### MAIN SCRIPT FOR CALIBRATION ########################
#############################################################
if __name__ == '__main__':
    device_compilation.fpga_board.ddr.data_version = 'TIMESTAMPS'

    device_compilation.fpga_board.configure_dac_80508()

    device_compilation.fpga_board.daq.set_isel(port=1, channels=None)
    device_compilation.fpga_board.daq.set_isel(port=2, channels=None)

    vsense = Vsense(fpga=device_compilation.fpga_board.f, dc_num=2)

    # ----------------- Colect Data -------------------
    setup_info = {
        'dut': 'model_cell', 
        'hookup': 'all_connected', 
        'board': 2, 'rej1': 200e3, 
        'rpcj1':10e3, 'srj1': 1e3, 
        'dc_mapping': device_compilation.fpga_board.dc_mapping, 
        'guard': 'removed_rsb1_rl2'
    }
    with open(os.path.join(data_dir, 'setup_info' + file_name + '.json'), 'w') as fp:
        json.dump(setup_info, fp, sort_keys=True, indent=4)

    for i in range(6):
        # set all fast-DAC DDR data to midscale
        device_compilation.fpga_board.ddr.data_arrays[i][:] = 0x2000

    # TODO: make more amenable to membrane voltage 
    sdac_amp_volt = 1  # 1 Volt amplitude. 2 V peak to peak # amplitude was checked on oscilloscope (bipolar creates gain of *3 with 0 mean)
    # at 1 V the DAC code is max=58928, min=6554
    target_freq_sdac = 1000.0  # Hz
    sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

    # Data for the 2 DAC80508 "Slow DACs"
    sdac_sine, sdac_freq = device_compilation.fpga_board.ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq_sdac, offset=dac80508_offset)

    # Specify output channel for DAC80508
    sdac_ch = device_compilation.fpga_board.daq.parameters['gp_dac_map'][dc_under_test]['CAL']
    if sdac_ch[0] == 1:
        sdac_1_out_chan = sdac_ch[1]
    if sdac_ch[0] == 2:
        sdac_2_out_chan = sdac_ch[1]  # don't care, this channel is not connected to CAL
    else:
        sdac_2_out_chan = 0  # need a default channel
    # Clear bits in the FDAC DDR stream that store the slow DAC channel
    for i in range(6):
        device_compilation.fpga_board.ddr.data_arrays[i] = np.bitwise_and(
            device_compilation.fpga_board.ddr.data_arrays[i], 0x3fff
        )

    # Load data into DDR
    # Set channel bits # TODO: make this a method of the DDR
    device_compilation.fpga_board.ddr.data_arrays[0] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13
    )
    device_compilation.fpga_board.ddr.data_arrays[1] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14
    )
    device_compilation.fpga_board.ddr.data_arrays[2] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13
    )
    device_compilation.fpga_board.ddr.data_arrays[3] = np.bitwise_or(
        device_compilation.fpga_board.ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14
    )

    # load slow DAC sine-wave in DDR channels 6
    device_compilation.fpga_board.ddr.data_arrays[6] = sdac_sine  # TODO: just one
    device_compilation.fpga_board.ddr.data_arrays[7] = sdac_sine

    # for testing in ['bath']:
    # TODO: Potential segment that caused the lmfit issue!
    for testing in ['bath', 'clamp']:
        if testing == 'bath':
            dc_under_test = device_compilation.fpga_board.dc_mapping['bath']  # TODO: get these indices from the boards configuration
            dc_disconnect = device_compilation.fpga_board.dc_mapping['clamp']
        elif testing == 'clamp':
            dc_under_test = device_compilation.fpga_board.dc_mapping['clamp']
            dc_disconnect = device_compilation.fpga_board.dc_mapping['bath']

        dc_configs, sys_connections = setup_clamps(dc_under_test=dc_under_test, dc_disconnect=dc_disconnect)

        device_compilation.fpga_board.ddr.write_setup()
        block_pipe_return, speed_MBs = device_compilation.fpga_board.ddr.write_channels(
            set_ddr_read=False)  # TODO: is this actually used or just promptly overwritten?
        device_compilation.fpga_board.ddr.reset_mig_interface()
        device_compilation.fpga_board.ddr.write_finish()

        if testing == 'bath':
            freq = 200
            num_repeats = 10
            blk_multiples = 40
            r_total_guess = 8e3
            voltage_amp = 0.2
        if testing == 'clamp':
            freq = 40 # from LTSpice sims the 3db is at 50 Hz ... so ideally would go to a slightly lower frequency 
            num_repeats = 50
            blk_multiples = 40
            r_total_guess = 300e3
            voltage_amp = 0.05 # must be small otherwise voltage sense amplifier (high gain) will saturate
        step = 1
        data = {}
        # TODO: Comment out when done debugging
        # breakpoint()
        # measure resistance 
        dc_configs[dc_under_test], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(
            dc_configs[dc_under_test], dc_configs=dc_configs, dc_under_test=dc_under_test, testing=testing,
            step=1, plt_data=True, plt_fit=True,
            write_ddr=True)
        if testing == 'clamp':  # needs extra time to settle
            dc_configs[dc_under_test], rdata, fit_resistance, pcov, mesg, ads_separate_data = measure_resistance(
                dc_configs[dc_under_test], dc_configs=dc_configs, dc_under_test=dc_under_test,
                testing=testing,
                step=1, plt_data=True, plt_fit=True,
                write_ddr=False)
        data[step] = rdata[step]

        # the resistance data does not need to be saved because it is prepended onto the data_chirp dictionary  
        filename_chirp = 'dc_resistance_{}'
        np.savez(os.path.join(data_dir, filename_chirp.format(testing)), data) # saved to a Numpy npz file 

        # ------------- Prepare the daughtercards for chirp testing -----------------
        if testing == 'bath':
            # dc_configs[dc_disconnect]['P1_CAL_CTRL'] = 0 # disconnect the vclamp board and use CC as the load capacitance 
            # dc_configs[dc_disconnect]['P2_CAL_CTRL'] = 0
            # dc_configs[dc_disconnect]['DAC_SEL'] = 'drive_CAL2'  # irrelevant since disconnected 
            freq_arr = np.logspace(np.log10(400), np.log10(50000), 8)
        elif testing == 'clamp':  # ground the bath clamp electrodes since 5k is small compared to the 200kOhm of the voltage clamp
            # dc_configs[dc_disconnect]['P1_CAL_CTRL'] = 0
            # dc_configs[dc_disconnect]['P2_CAL_CTRL'] = 0
            # dc_configs[dc_disconnect]['DAC_SEL'] = 'gnd_both'
            # freq_arr = np.logspace(np.log10(40), np.log10(2000), 8)
            freq_arr = np.logspace(np.log10(10), np.log10(2000), 8)

        log_info_bath, dc_configs[dc_disconnect] = device_compilation.fpga_board.clamps[dc_disconnect].configure_clamp(**dc_configs[dc_disconnect])

        # disable the current source 
        device_compilation.fpga_board.daq.set_isel(port=1, channels=None) # channel select works correctly -- this turns off the signal 
        # ---- CHIRP testing ------------
        data_chirp = {}
        data_chirp[1] = data[1] # add resistance data 
        step_chirp = 2

    #    if testing == 'bath' or testing == 'vclamp':
        predicted_res, res_fit_mesg, component_fits, fit_notes, components, data_chirp, filename_chirp, step_chirp = transfer_functions_fit(
            testing=testing, 
            data_chirp=data_chirp, 
            dc_configs=dc_configs, 
            dc_under_test=dc_under_test, 
            voltage_amp=voltage_amp, 
            step_chirp=step_chirp, 
            r_total_guess=r_total_guess, 
            data_dir=data_dir, 
            filename_chirp=filename_chirp
        )
        # components is calculated from component_fits so its ok to not capture component_fits
        component_results = {}
        component_results[testing] = components
        component_results[testing]['total_resistance'] = predicted_res
        component_results[testing]['resistance_msg'] = res_fit_mesg
        component_results[testing]['fit_notes'] = fit_notes
        # save final results to a JSON and to a CSV
        # directory for CSV is different than directory for JSON 

        with open(os.path.join(data_dir, 'cal_data_' + file_name + f"{testing}" + '.json'), 'w') as fp:
            json.dump(component_results, fp, sort_keys=True, indent=4)

        if UPDATE_RESULTS:
            df = pd.DataFrame.from_dict(component_results)
            df.to_csv(os.path.join(results_dir, 'calibration.csv'))
            df.to_csv(os.path.join(data_dir, 'calibration_' + file_name + f"{testing}" + '.csv'))

    print('final component results ' + '-' * 40)
    print(component_results)
