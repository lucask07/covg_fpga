import os
from time import sleep
import time
from typing import Literal
import atexit
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import copy
import pandas as pd
import json
import math
import io
import logging
from itertools import permutations
from logging import getLogger
from bidict import bidict
from pyripherals.utils import to_voltage, from_voltage
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3

# Defines data_dir_covg and adds the path to boards.py into the sys.path 
from setup_paths import *

from analysis.adc_data import read_h5, separate_ads_sequence
from analysis.utils import my_savedata, fig_dir
from analysis.calibration_analysis import total_res_iso_res, r_from_square
from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Vsense2
from calibration.electrodes import EphysSystem
from bathclamp_vclamp_utils import HardwareSetup
from bath_clamp_setup_steps import *
from DAC_TCA_reads_test import ReadTest


DAQ_V = "2.1"

results_dir = os.path.join(boards_path, 'results') # within the Git repo there is a results directory; 
                                                   # this allows the calibration results to be viewed on GitHub
fig_dir = os.path.join(fig_dir, "bath_clamp_headstage")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)


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
cap = 47 # nF

class Headstage:
    """
    Represents the headstage hardware and manages calibration, data collection, and analysis routines.

    Attributes
    ----------
    hardware : HardwareSetup
        The hardware setup instance.
    adc_chan0, adc_chan1, adc_v1 : tuple
        ADC channel mappings for calibration and amplifier output.
    EXPERIMENTS : dict
        Logs of experiment processes and results.
    RELAYS_DAQS : dict
        Logs of relay and DAQ states for each experiment.
    FIT_RESULTS : dict
        Stores fit results for calibration and transfer function experiments.
    vsense : Vsense2
        Vsense2 board instance for voltage sensing.
    
    Methods
    -------
    save_plot(directory, plt_dict)
        Save matplotlib figures to a directory.
    define_directory_for_plots(desired_path)
        Create a directory for saving plots if it does not exist.
    dac_waveform(dc_under_test, amp, freq, shape, source, periods)
        Generate and upload a waveform to the DAC for calibration.
    get_ads_voltages(ddr, dc_configs, num_repeats, blk_multiples)
        Read a short series from DDR to calculate DC value of ADS channels.
    collect_data(ddr, PLT, ads_chan, num_repeats, blk_multiples)
        Collect and plot data from DDR and ADS channels.
    setup_clamps(dc_under_test, dc_disconnect)
        Configure clamp boards and relay connections for calibration.
    measure_resistance(config_dict_test, dc_configs, dc_under_test, testing, step, plt_data, plt_fit, write_ddr, r_total_guess)
        Source a current and measure electrode resistance using DC response.
    read_cal_adc()
        Download ADC data for calibration.
    inspect_DAC_ADC_clamp(lowerbound, upperbound, uppergain, lowergain)
        Sweep DAC offsets and record ADC readings for clamp calibration.
    optimize_ADC_to_zero(lowerbound, upperbound, plot_batches, verbose_batch)
        Find DAC offset and gain settings that minimize ADC reading.
    chirp_test(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp, freq_arr)
        Measure transfer function versus frequency using a chirp signal.
    chirp_test_vclamp(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp, freq_arr)
        Measure transfer function for voltage clamp using a chirp signal.
    transfer_functions_fit(testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp, freq_arr, r_total_guess)
        Fit transfer functions and extract component resistances.
    save_log(logtype, filename)
        Save experiment logs, fit notes, or relay/DAQ states to JSON.
    """

    def __init__(self, hardware : HardwareSetup, lowergain_clamp, uppergain_clamp):
        """
        Initialize the Headstage with hardware and gain settings.

        Parameters
        ----------
        hardware : HardwareSetup
            The hardware setup instance.
        lowergain_clamp : int
            Lower gain setting for clamp amplifier.
        uppergain_clamp : int
            Upper gain setting for clamp amplifier.
        """
        # Logger for headstage instantiation
        logger = getLogger("Headstage Instantiation")
        logger.setLevel(logging.INFO)
        self.hardware = hardware

        # Set the dac channel
        self.adc_chan0 = self.hardware.daq.parameters['ads_map'][dc_under_test]['CAL_ADC']  # ('A', 0)
        self.adc_chan1 = self.hardware.daq.parameters['ads_map'][dc_under_test]['AMP_OUT']  # ('A', 1)
        self.adc_v1 = self.hardware.daq.parameters['ads_map'][hardware.dc_mapping['clamp']]['AMP_OUT']  # ('A', 1)

        #####################################################################
        ## GENERAL DICT TO LOG EXPERIMENT PROCESS ###########################
        self.EXPERIMENTS = dict()
        self.RELAYS_DAQS = dict()
        self.FIT_RESULTS = dict()
        #####################################################################

        self.vsense = Vsense2(
            fpga=hardware.f, 
            dc_num=hardware.dc_mapping['vclamp'], 
            DAC_addr_pins=0b001, 
            TCA_addr_pins=0b111
        )
    
        self.vsense.DAC.write(
            data=100
        )
        # Explicitly set the gain for vsense
        self.vsense.set_gain(lowergain_clamp, uppergain_clamp)
        logger.info(f"ADC for clamp is {self.hardware.daq.parameters['ads_map'][hardware.dc_mapping['clamp']]['CAL_ADC']}")
    
    @staticmethod
    def save_plot(directory : str, plt_dict : dict[str, Figure]) -> dict[str, str]:
        """
        Save matplotlib figures in plt_dict to the specified directory.

        Parameters
        ----------
        directory : str
            Directory to save figures.
        plt_dict : dict[str, Figure]
            Dictionary mapping figure names to matplotlib Figure objects.

        Returns
        -------
        dict[str, str]
            Dictionary mapping figure names to their saved directory.
        """
        path_dict = {}
        for key, value in plt_dict.items():
            value.savefig(os.path.join(directory, f"{key}.png"))
            path_dict = path_dict | {key : directory}
        return path_dict
    
    @staticmethod
    def define_directory_for_plots(desired_path : str) -> str:
        """
        Create the desired directory for saving plots if it does not exist.

        Parameters
        ----------
        desired_path : str
            Path to the directory.

        Returns
        -------
        str
            The created or existing directory path.
        """
        if not os.path.exists(desired_path):
            os.makedirs(desired_path)
        return desired_path


    def dac_waveform(self, dc_under_test, amp, freq=1000, shape='SINE', source='v', periods=None):
        """
        Generate and upload a waveform to the DAC for calibration.

        Parameters
        ----------
        dc_under_test : int
            Daughter card to send calibration signal to.
        amp : float
            Amplitude of waveform (voltage or current).
        freq : float or np.ndarray
            Frequency of waveform (Hz) or array for chirp.
        shape : str
            'SINE', 'SQ', or 'CHIRP'.
        source : str
            'v' for voltage, 'i' for current.
        periods : int or np.ndarray, optional
            Number of periods for chirp.

        Returns
        -------
        tuple
            (waveform array, frequency, indices)
        """
        # Log inside the dac_waveform method
        logger = getLogger("DAC Waveform Generation")
        logger.setLevel(logging.INFO)

        for i in range(6):
            # set all fast-DAC DDR data to midscale
            self.hardware.ddr.data_arrays[i][:] = 0x2000

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
        logger.info(f'Max sdac amp {sdac_amp_code}')

        # Data for the 2 DAC80508 "Slow DACs"
        if shape == 'SINE':
            sdac_wave, freq = self.hardware.ddr.make_sine_wave(amplitude=sdac_amp_code,
                                                frequency=freq, offset=dac80508_offset)
            indices = None
        elif shape == 'SQ':
            # low, high
            sq_length = int(1 / DDR3.UPDATE_PERIOD / freq)
            if sdac_amp_code > dac80508_offset:
                logger.error(f'Square-wave amplitude of {sdac_amp_code} too large ')
            sdac_wave = self.hardware.ddr.make_step(low=int(dac80508_offset - sdac_amp_code),
                                    high=int(dac80508_offset + sdac_amp_code),
                                    length=sq_length)
            indices = None
        elif shape == 'CHIRP':
            if sdac_amp_code > dac80508_offset:
                logger.error(f'Square-wave amplitude of {sdac_amp_code} too large ')
            sdac_wave, freq, indices = self.hardware.ddr.make_chirp(amplitude=sdac_amp_code,
                                                    frequencies=freq, periods=periods,
                                                    offset=dac80508_offset)

        # Specify output channel for DAC80508
        sdac_ch = self.hardware.daq.parameters['gp_dac_map'][dc_under_test]['CAL']
        if sdac_ch[0] == 1:
            sdac_1_out_chan = sdac_ch[1]
        if sdac_ch[0] == 2:
            sdac_2_out_chan = sdac_ch[1]  # don't care, this channel is not connected to CAL
        else:
            sdac_2_out_chan = 0  # need a default channel
        # Clear bits in the FDAC DDR stream that store the slow DAC channel

        # TODO: make this a method of the DDR class 
        for i in range(6):
            self.hardware.ddr.data_arrays[i] = np.bitwise_and(
                self.hardware.ddr.data_arrays[i], 0x3fff
            )
        # Load data into DDR
        # Set channel bits
        self.hardware.ddr.data_arrays[0] = np.bitwise_or(
            self.hardware.ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13
        )
        self.hardware.ddr.data_arrays[1] = np.bitwise_or(
            self.hardware.ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14
        )
        self.hardware.ddr.data_arrays[2] = np.bitwise_or(
            self.hardware.ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13
        )
        self.hardware.ddr.data_arrays[3] = np.bitwise_or(
            self.hardware.ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14
        )

        # load slow DAC sine-wave in DDR channels 6
        self.hardware.ddr.data_arrays[6] = sdac_wave
        # ddr.data_arrays[7] = sdac_sine # TODO: all cal channels are on the first DAC so setting [7] is not needed

        self.hardware.ddr.write_setup()
        block_pipe_return, speed_MBs = self.hardware.ddr.write_channels(set_ddr_read=False)
        self.hardware.ddr.reset_mig_interface()
        self.hardware.ddr.write_finish()

        return sdac_wave, freq, indices


    def get_ads_voltages(self, ddr, dc_configs, num_repeats=1, blk_multiples=10):
        """
        Read a short series from DDR to calculate DC value of ADS channels.

        Parameters
        ----------
        ddr : DDR3
            DDR3 memory interface.
        dc_configs : dict
            Daughtercard configurations.
        num_repeats : int, optional
            Number of repeats for averaging.
        blk_multiples : int, optional
            Block multiples for data capture.

        Returns
        -------
        volts : dict
            Average voltage value for each channel and number.
        datastreams : Datastreams
            Datastreams object for plotting and analysis.
        """
        # Log inside the get_ads_voltages method
        logger = getLogger("Get ADS Voltages")
        logger.setLevel(logging.INFO)

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
                logger.info(f'Channel {chan}{num} at {v:.4g} [V]')

        # update system connections since the daughtercard configurations have changed
        sys_connections = create_sys_connections(
            dc_configs, 
            self.hardware.daq, 
            self.hardware.ephys_sys
        )
        # Plot using datastreams 
        datastreams, log_info = rawh5_to_datastreams(data_dir, 'voltage_read.h5', ddr.data_to_names,
                                                    self.hardware.daq, 
                                                    sys_connections, outfile=None)

        return volts, datastreams

    def collect_data(self, ddr, PLT=True, ads_chan=('A', 0), num_repeats=10, blk_multiples=40):
        """
        Collect and plot data from DDR and ADS channels.

        Parameters
        ----------
        ddr : DDR3
            DDR3 memory interface.
        PLT : bool, optional
            Whether to plot the data.
        ads_chan : tuple, optional
            ADS channel to read.
        num_repeats : int, optional
            Number of repeats for averaging.
        blk_multiples : int, optional
            Block multiples for data capture.

        Returns
        -------
        volt : np.ndarray
            Voltage data from ADS.
        t_ads : np.ndarray
            Time array for ADS data.
        ads_separate_data : dict
            Separated ADS data.
        fig : Figure or None
            Matplotlib figure if PLT is True.
        ax : Axes or None
            Matplotlib axes if PLT is True.
        """
        # Log inside the collect_data method
        logger = getLogger("Collect Data")
        logger.setLevel(logging.INFO)

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
        logger.info(f'Timestamp spans {5e-9 * (timestamp[-1] - timestamp[0]) * 1000} [ms]')

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
        fig = None
        if PLT:
            fig, ax = plt.subplots()
            ax.plot(t_ads * 1e6, volt, marker='+', label=f'ADS: {chan}')
            ax.legend()
            ax.set_xlabel('s [us]')
            ax.set_title('ADS8686 data')
            plt.close(fig)
        else:
            ax = None
        return volt, t_ads, ads_separate_data, fig, ax

    def setup_clamps(self, dc_under_test, dc_disconnect):
        """
        Configure clamp boards and relay connections for calibration.

        Parameters
        ----------
        dc_under_test : int
            Index of daughter card being tested.
        dc_disconnect : int
            Index of daughter card to disconnect.

        Returns
        -------
        dc_configs : dict
            Updated daughtercard configurations.
        sys_connections : dict
            System connections mapping.
        """

        dc_configs = {}
        self.dc_under_test = dc_under_test
        self.dc_disconnect = dc_disconnect

        log_info_test, dc_configs[dc_under_test] = self.hardware.clamps[dc_under_test].configure_clamp(
            **self.hardware.clamps[dc_under_test].config_close_cal_relays
        )

        log_info_disconnect, dc_configs[dc_disconnect] = self.hardware.clamps[dc_disconnect].configure_clamp(
            **self.hardware.clamps[dc_disconnect].config_open_all_relays
        )

        dc_guard = self.hardware.dc_mapping['guard']
        log_info, dc_configs[dc_guard] = self.hardware.clamps[dc_guard].configure_clamp(
            **self.hardware.clamps[dc_guard].config_open_all_relays
        )
        
        # self.hardware.clamps[self.hardware.dc_mapping['vclamp']].TCA[0].write(15496)
        # self.hardware.clamps[self.hardware.dc_mapping['vclamp']].TCA[1].write(15496)
        
        # dc_configs[self.hardware.dc_mapping['clamp']]['VSENSE'] = 60.24 # extra information for the system_connections. Gain of the voltage clamp amplifier # TODO: uncomment when done
        # dc_configs[dc_mapping['clamp']]['VSENSE'] = 60.24*10**(-11.7868/20) 
        sys_connections = create_sys_connections(dc_configs, self.hardware.daq, self.hardware.ephys_sys)

        return dc_configs, sys_connections

    def measure_resistance(self, config_dict_test, dc_configs, dc_under_test, testing='bath', step=1, 
                            plt_data=True, plt_fit=False,
                            write_ddr=True, r_total_guess=0):
        """
        Source a current and measure electrode resistance using DC response.

        Parameters
        ----------
        config_dict_test : dict
            Configuration for daughtercard under test.
        dc_configs : dict
            Daughtercard configurations.
        dc_under_test : int
            Index of daughtercard under test.
        testing : str, optional
            'bath' or 'clamp' to select test type.
        step : int, optional
            Step index for experiment.
        plt_data : bool, optional
            Whether to plot collected data.
        plt_fit : bool, optional
            Whether to plot fit results.
        write_ddr : bool, optional
            Whether to write waveform to DDR.
        r_total_guess : float, optional
            Initial guess for resistance fit.
        
        Returns
        -------
        config_dict_test : dict
            Updated configuration for daughtercard under test.
        rdata : dict
            Measured voltage and time data.
        fit_resistance : float or None
            Fitted resistance value.
        pcov : Any
            Covariance of fit.
        mesg : str or None
            Fit message.
        ads_separate_data : dict
            Separated ADS data.
        """
        # Log inside the measure_resistance method
        logger = getLogger("Measure Resistance")
        logger.setLevel(logging.INFO)

        # Determine the directory where figures specific to measure resistant are stored
        figure_path = Headstage.define_directory_for_plots(
            os.path.join(fig_dir, f"Measure_resistance_for_{testing}")
        )
        # Dictionary storing figures objects
        figures_table = dict()
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

        self.hardware.daq.set_isel(port=1, channels=[dc_under_test]) # current based on DC#  
        config_dict_test['ADC_SEL'] = 'CAL_SIG2' # this is the force terminal; drive and measure on the same channel 

        # TODO: How is the disconnected clamp board configured? 
        if testing == 'bath':
            config_dict_test['DAC_SEL'] = 'drive_CAL2_gnd_CAL1'
        elif testing == "clamp":
            config_dict_test['DAC_SEL'] = 'drive_CAL2'


        log_info_bath, config_dict_test = self.hardware.clamps[dc_under_test].configure_clamp(**config_dict_test)

        # inject current square wave, expect around 8 mV amplitude from 0.8 uA*10e3, 16 mV pk-pk         
        if write_ddr:
            dac_wave, freq, _ = self.dac_waveform(0, amp=current_amp, freq=freq, shape='SQ',
                                            source='i')  # howland pump is always driven by BP_OUT0
        else:
            self.hardware.ddr.reset_mig_interface()
            self.hardware.ddr.write_finish()

        volt, t, ads_separate_data, fig_collect, ax = self.collect_data(
            self.hardware.ddr, PLT=plt_data, 
            ads_chan=self.hardware.daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
            num_repeats=num_repeats, 
            blk_multiples=blk_multiples
        )

        figures_table[f"Collect_data_for_{testing}"] = fig_collect
        
        fig = None
        if testing == 'clamp':
            v_vclamp = ads_separate_data[self.adc_v1[0]][self.adc_v1[1]]  # TODO: generalize if boards swap DAQ sockets
            idx = np.min([len(t), len(v_vclamp)])
            #ax.plot(t[:idx]*1e6, v_vclamp[:idx]/20.15, label='V1 [V]')    
            #ax.legend()

            idx = np.min([len(t), len(v_vclamp), len(volt)])
            fig, ax = plt.subplots()
            ax.plot(t[:idx]*1e6, v_vclamp[:idx]/20.15 - volt[:idx], label='V1 - V(I) [V]')
            volt = v_vclamp[:idx]/20.15 - volt[:idx] # fit this difference of voltages. #TODO: parameterize this specific gain of the voltage clamp 
            ax.legend()
            plt.close(fig)
            figures_table[f"Resistance_plot_for_{testing}"] = fig

        rdata = {}
        # ensure that t and volt are the same length 
        idx = np.min([len(t), len(volt)])
        volt = volt[:idx]
        t = t[:idx]
        rdata[step] = {
            'volt': volt,
            't': t,
            'src': 'i',
            'shape': 'SQ',
            'freq': freq,
            'amp': current_amp,
            'vclamp': 'disconnect',
            'bath_clamp': copy.deepcopy(dc_configs[self.hardware.dc_mapping['bath']]),
            'voltage_clamp': copy.deepcopy(dc_configs[self.hardware.dc_mapping['clamp']])
        }
        try:
            fit_resistance, pcov, mesg, fig_sqr = r_from_square(r_total_guess, rdata, PLT=plt_fit, name=testing)
            # Account for if the figure is shown
            if isinstance(fig_sqr, Figure):
                figures_table[f"fit_resistance_plot_for_{testing}"] = fig_sqr
                plt.close(fig_sqr)
        except Exception as e:
            logger.error(f"Failed to fit resistance function -> {e}")
            fit_resistance = pcov = mesg = None

        # Save the plots and pinpoint the directory where they are stored
        figure_paths_table = Headstage.save_plot(figure_path, figures_table)
        
        # For measure resistance, the value is the list, whose first value refers to plot object, 
        # second refers to relays states, ADC, DAC, and third the measuring parameters
        dc_status = {
            self.hardware.dc_mapping.inverse[dc] : 
            copy.deepcopy({
                k : dc_configs[dc][k] for k in [
                    'ADC_SEL', 
                    'DAC_SEL',  
                    'PClamp_CTRL', 
                    'P1_E_CTRL', 
                    'P2_E_CTRL', 
                    'P1_CAL_CTRL', 
                    'P2_CAL_CTRL'
            ]}) for dc in dc_configs
        }
        self.EXPERIMENTS.update({
            f"measure resistance of {testing}" : [
                figure_paths_table, 
                dc_status, 
                {k : copy.deepcopy(rdata[step][k]) for k in rdata[step] if k not in [
                    "vclamp", "bath_clamp", "voltage_clamp", "vsense"
                ]}, {
                    f"fit resistance for {testing}" : fit_resistance
                }
            ]
        })
        self.RELAYS_DAQS[f"measure resistance of {testing}"] = dc_status
        self.FIT_RESULTS[f"measure resistance of {testing}"] = fit_resistance

        return config_dict_test, rdata, fit_resistance, pcov, mesg, ads_separate_data
    
    def read_cal_adc(self):
        """
        Download ADC data for calibration.

        Returns
        -------
        ads_separate_data_chirp : dict
            Separated ADS data for calibration.
        """
        blk_mult = 120
        num_repeats_chirp = 1
        volt_chirp, t_chirp, ads_separate_data_chirp, fig, ax = self.collect_data(self.hardware.ddr, PLT=False,
                                                                        ads_chan=
                                                                        self.hardware.daq.parameters['ads_map'][
                                                                            self.hardware.dc_mapping['clamp']
                                                                        ]['CAL_ADC'],
                                                                        num_repeats=num_repeats_chirp,
                                                                        blk_multiples=blk_mult)
        return ads_separate_data_chirp
    
    def inspect_DAC_ADC_clamp(self, lowerbound=0, upperbound=100, uppergain=31, lowergain=36):
        """
        Sweep DAC offsets and record ADC readings for clamp calibration.

        Parameters
        ----------
        lowerbound : int, optional
            Lower bound for DAC offset sweep.
        upperbound : int, optional
            Upper bound for DAC offset sweep.
        uppergain : int, optional
            Upper gain setting for clamp.
        lowergain : int, optional
            Lower gain setting for clamp.

        Returns
        -------
        None

        Notes
        -----
        Saves results to CSV and PNG files.
        """
        DAC_offsets = [-100 for x in range(lowerbound, upperbound+1)]
        mean_ADC_clamp = [0 for _ in range(len(DAC_offsets))]
        self.vsense.set_gain(uppergain, lowergain)
        for i, val in enumerate(DAC_offsets):
            self.vsense.DAC.write(val)
            ads_arr = self.read_cal_adc()
            mean = np.mean(ads_arr['A'][4])
            mean_ADC_clamp[i] = mean
        
        my_savedata("DAC_ADC_clamp_read.csv", DAC_offsets = np.array(DAC_offsets, dtype=np.int32), mean_ADC_clamp = np.array(mean_ADC_clamp))
        fig, ax = plt.subplots(1, 1)
        ax.plot(DAC_offsets, mean_ADC_clamp)
        ax.set_xlabel("DAC offset")
        ax.set_ylabel("ADC read for clamp")
        fig.savefig("DAC_ADC_clamp_read.png")
    
    def optimize_ADC_to_zero(self, lowerbound=-100, upperbound=2000, plot_batches=20, verbose_batch=5):
        """
        Find DAC offset and gain settings that minimize ADC reading.

        Parameters
        ----------
        lowerbound : int, optional
            Lower bound for DAC offset sweep.
        upperbound : int, optional
            Upper bound for DAC offset sweep.
        plot_batches : int, optional
            Number of batches for plotting.
        verbose_batch : int, optional
            Frequency of verbose output.

        Returns
        -------
        optimized : dict
            Optimized gain and DAC settings.
        """
        from contextlib import contextmanager

        # Logger for optimization
        logger = getLogger("Optimize ADC to Zero")
        logger.setLevel(logging.INFO)

        @contextmanager
        def suppress_stdout():
            original_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                yield
            finally:
                sys.stdout = original_stdout

        my_dict = copy.deepcopy(Vsense2.gain_dict)
        del my_dict[None]
        gain_dict = my_dict.keys()

        base_dir = os.path.join(os.getcwd(), 'optimized_ADC_CAL')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        # Get the gain permutations
        permutation_list = permutations(gain_dict, 2)

        # Size of permutation
        perm_size = math.factorial(len(gain_dict)) // math.factorial(len(gain_dict) - 2)

        # Number of plots chosen - sampling
        batches = plot_batches
        verbose_batches = verbose_batch

        # Optimized gains, DAC offset
        optimized = {
            'uppergain': 0, 
            'lowergain': 0, 
            'DAC': 0, 
            'ADC': None
        }

        # Iterate
        for i in range(perm_size):
            current_gains = next(permutation_list)
            inner_optimized = {
                'DAC': 0, 
                'ADC': None
            }
            DAC_offsets = [x for x in range(lowerbound, upperbound+1)]
            mean_ADC_clamp = [0 for _ in range(len(DAC_offsets))]
            with suppress_stdout():
                self.vsense.set_gain(*current_gains)
            iter_size = 0
            for j, val in enumerate(DAC_offsets):
                iter_size += 1
                self.vsense.DAC.write(val)
                # Prevent this function from outputing to stdout
                with suppress_stdout():
                    ads_arr = self.read_cal_adc()
                ###############
                mean = np.mean(ads_arr['A'][4])
                mean_ADC_clamp[j] = mean
                del ads_arr
                if inner_optimized['ADC'] is None or inner_optimized['ADC'] > mean or mean == 0.0:
                    inner_optimized['DAC'] = val
                    inner_optimized['ADC'] = mean
                if mean == 0.0:
                    break
                

            DAC_offsets = DAC_offsets[:iter_size]
            mean_ADC_clamp = mean_ADC_clamp[:iter_size]

            if optimized['ADC'] is None or optimized['ADC'] > inner_optimized['ADC'] or inner_optimized['ADC'] == 0.0:
                optimized['uppergain'] = current_gains[0]
                optimized['lowergain'] = current_gains[1]
                optimized['DAC'] = inner_optimized['DAC']
                optimized['ADC'] = inner_optimized['ADC']
            

            if i % batches == 0 or i == (perm_size - 1):
                fig, ax = plt.subplots(1, 1)
                ax.plot(DAC_offsets, mean_ADC_clamp)
                ax.set_xlabel("DAC offset")
                ax.set_ylabel("ADC read for clamp")
                fig.savefig(os.path.join(base_dir, f"DAC_ADC_clamp_read_{i}.png"))
                del fig, ax
            
            del DAC_offsets, mean_ADC_clamp
            
            if i % verbose_batches == 0 or i == (perm_size - 1):
                logger.info(f"ITER {i}, gain = ({optimized['uppergain']}, {optimized['lowergain']}), DAC = {optimized['DAC']}, value = {inner_optimized['ADC']}")
            
            if inner_optimized['ADC'] == 0.0:
                break

            logger.info(f"-----------------\nFinal result = {optimized}")
        
        return optimized

        

    def chirp_test(self, testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp, 
                   freq_arr):
        """
        Measure transfer function versus frequency using a chirp signal.

        Parameters
        ----------
        testing : str
            Test type ('bath' or 'clamp').
        data_chirp : dict
            Dictionary to store chirp data.
        dc_configs : dict
            Daughtercard configurations.
        dc_under_test : int
            Index of daughtercard under test.
        voltage_amp : float
            Voltage amplitude of chirp stimulus.
        step_chirp : int
            Step index for chirp data.
        freq_arr : np.ndarray
            Array of frequencies for chirp.

        Returns
        -------
        data_chirp : dict
            Updated chirp data.
        measured_params : dict
            Measured parameters and relay states.
        filename_chirp : str
            Filename for saved chirp data.
        step_chirp : int
            Updated step index.
        """
        # Log inside the chirp_test method
        logger = getLogger("Chirp Test")
        logger.setLevel(logging.INFO)

        # Announce the start of the chirp test
        logger.info(f"Starting chirp test for {testing} with voltage amplitude {voltage_amp} V")
        # A dictionary to keep track of relay states + measured parameters
        measured_params = dict()
        relays_daqs = dict()
        self.RELAYS_DAQS[f"Transfer fit function for {testing}"] = relays_daqs

        for drive_elec in [1,2]:
            for swap in [False, True]:
                if drive_elec == 1:  # upload the chirp signal to DDR only for drive 1 since we repeat for drive electrode 2 
                    periods = np.ones(len(freq_arr))*30
                    dac_wave, freq_chirp, indices = self.dac_waveform(dc_under_test, amp=voltage_amp, 
                                                            freq=freq_arr, shape='CHIRP', source='v', 
                                                            periods=periods)
                    total_chirp_time = np.sum(1/freq_arr*periods)
                    logger.info(f'Total chirp time = {total_chirp_time}')
                    # find the last index to 'download' using the starting index of the last frequency
                    end_index = indices[-1][0] + periods[-1] * ((1 / DDR3.UPDATE_PERIOD) / freq_arr[-1])

                # measure at same point as drive, this acts as an amplitude calibration (for a transfer function of Vout/Vin this measures Vin)
                dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL1' if drive_elec == 1 else 'drive_CAL2'
                adc_sel_phase_1 = 'CAL_SIG1' if not swap else 'CAL_SIG2'
                adc_sel_phase_2 = 'CAL_SIG2' if not swap else 'CAL_SIG1'
                dc_configs[dc_under_test]['ADC_SEL'] = adc_sel_phase_1 if drive_elec == 1 else adc_sel_phase_2

                ### Compile the new configs ###

                log_info_bath, dc_configs[dc_under_test] = self.hardware.clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])
                

                # download ADC data so that np.max(t_chirp) = total_chirp_time 
                # This can also be checked by the indices (2.5 MSPS)
                #   versus the length of volt_chirp (@ 1 MSPS / len(ads_sequencer_setup))
                blk_mult = 120
                num_repeats_chirp = int(np.ceil(end_index * 2 / (2048 / 16) / blk_mult))
                volt_chirp, t_chirp, ads_separate_data_chirp, fig, ax = self.collect_data(
                    self.hardware.ddr, PLT=False,
                    ads_chan=self.hardware.daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
                    num_repeats=num_repeats_chirp,
                    blk_multiples=blk_mult
                )
                assert fig is None
                
                # Round up relays states first
                param_list = list()
                # To save the plot in the dictionary
                name_key = f'drive_elec_{drive_elec}' if not swap else f'drive_elec_{drive_elec}_swap'
                measured_params[name_key] = param_list
                relays_daqs[name_key] = {
                    self.hardware.dc_mapping.inverse[dc] : 
                    copy.deepcopy({
                        k : dc_configs[dc][k] for k in [
                            'ADC_SEL', 
                            'DAC_SEL',  
                            'PClamp_CTRL', 
                            'P1_E_CTRL', 
                            'P2_E_CTRL', 
                            'P1_CAL_CTRL', 
                            'P2_CAL_CTRL'
                        ]
                    }) for dc in dc_configs
                }
                param_list.extend([
                    relays_daqs[name_key], 
                    dict()
                ])
                

                for freq, idx in zip(freq_arr, indices):
                    chirp_idx = []
                    chirp_idx.append(int(idx[0] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))
                    chirp_idx.append(int(idx[1] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))

                    if dc_under_test==self.hardware.dc_mapping['bath']:
                        v1_gain = 1
                    else:
                        v1_gain = 60.24*10**(-11.7868/20)
                    data_chirp[step_chirp] = {
                        'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]],  # measured stimulus data
                        't': t_chirp[chirp_idx[0]:chirp_idx[1]],
                        'v1': ads_separate_data_chirp[self.adc_v1[0]][self.adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
                        'v1_gain': v1_gain, 
                        'src': 'v',
                        'shape': 'SINE',
                        'freq': freq,  # stimulus frequency
                        'amp': voltage_amp,
                        'dc_under_test': dc_under_test,
                        'bath_clamp': copy.deepcopy(dc_configs[self.hardware.dc_mapping['bath']]),
                        'voltage_clamp': copy.deepcopy(dc_configs[self.hardware.dc_mapping['clamp']])
                    }
                    param_list[1].update({
                        step_chirp : {
                            k : copy.deepcopy(v) for k,v in data_chirp[step_chirp].items() if k not in [
                                'bath_clamp', 'voltage_clamp', 'vsense'
                                ]
                        }})
                    step_chirp += 1

        # save Chirp data 
        filename_chirp = f'imp_all_steps_chirp_{file_name}' + '_{}'
        np.savez(os.path.join(data_dir, filename_chirp.format(testing)), data_chirp) # saved to a Numpy npz file 

        # Announce the completion of the chirp test
        logger.info(f"Completed chirp test for {testing}. Data saved to {filename_chirp.format(testing)}")

        return data_chirp, measured_params, filename_chirp, step_chirp

    def chirp_test_vclamp(self, testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp, 
                          freq_arr):
        """
        Measure transfer function for voltage clamp using a chirp signal.

        Parameters
        ----------
        testing : str
            Test type ('clamp').
        data_chirp : dict
            Dictionary to store chirp data.
        dc_configs : dict
            Daughtercard configurations.
        dc_under_test : int
            Index of daughtercard under test.
        voltage_amp : float
            Voltage amplitude of chirp stimulus.
        step_chirp : int
            Step index for chirp data.
        freq_arr : np.ndarray
            Array of frequencies for chirp.

        Returns
        -------
        data_chirp : dict
            Updated chirp data.
        measured_params : dict
            Measured parameters and relay states.
        filename_chirp : str
            Filename for saved chirp data.
        step_chirp : int
            Updated step index.
        """
        # Log inside the chirp_test_vclamp method
        logger = getLogger("Chirp Test VClamp")
        logger.setLevel(logging.INFO)
        # Announce the start of the chirp test for voltage clamp
        logger.info(f"Starting chirp test for voltage clamp with voltage amplitude {voltage_amp} V")
        # Create a dict to track measured parameters
        measured_params = dict()
        relays_daqs = dict()
        self.RELAYS_DAQS[f"Transfer fit function for {testing}"] = relays_daqs

        dc_guard = self.hardware.dc_mapping['guard']

        # Close calibration relays for DAC grounding
        dc_configs[dc_guard]['P1_CAL_CTRL'] = 1
        dc_configs[dc_guard]['P2_CAL_CTRL'] = 1
        dc_configs[self.dc_disconnect]['P1_CAL_CTRL'] = 1
        dc_configs[self.dc_disconnect]['P2_CAL_CTRL'] = 1

        # Configure all these changes
        self.hardware.clamps[dc_guard].configure_clamp(
            **dc_configs[dc_guard]
        )
        self.hardware.clamps[self.dc_disconnect].configure_clamp(
            **dc_configs[self.dc_disconnect]
        )

        for float_dut in [True, False]:
            if not float_dut:
                logger.info("Waiting time for clamp transfer function")
                input("Hit enter to continue")
                
            if float_dut:  # upload the chirp signal to DDR only for drive 1 since we repeat for the next measurement
                periods = np.ones(len(freq_arr))*30
                dac_wave, freq_chirp, indices = self.dac_waveform(dc_under_test, amp=voltage_amp, 
                                                        freq=freq_arr, shape='CHIRP', source='v', 
                                                        periods=periods)
                total_chirp_time = np.sum(1/freq_arr*periods)
                logger.info(f'Total chirp time = {total_chirp_time}')
                # find the last index to 'download' using the starting index of the last frequency
                end_index = indices[-1][0] + periods[-1] * ((1 / DDR3.UPDATE_PERIOD) / freq_arr[-1])
            # setup the voltage clamp board 
            dc_configs[dc_under_test]['ADC_SEL'] = 'CAL_SIG2' if float_dut else 'CAL_SIG1'
            dc_configs[dc_under_test]['DAC_SEL'] = 'drive_CAL2' # do not ground CAL1 


            ### Compile the new configs ###
            log_info_dut, dc_configs[dc_under_test] = self.hardware.clamps[dc_under_test].configure_clamp(**dc_configs[dc_under_test])

            # download ADC data so that np.max(t_chirp) = total_chirp_time 
            # This can also be checked by the indices (2.5 MSPS)
            #   versus the length of volt_chirp (@ 1 MSPS / len(ads_sequencer_setup))
            blk_mult = 120
            num_repeats_chirp = int(np.ceil(end_index * 2 / (2048 / 16) / blk_mult))
            volt_chirp, t_chirp, ads_separate_data_chirp, fig, ax = self.collect_data(
                self.hardware.ddr, PLT=False,
                ads_chan=self.hardware.daq.parameters['ads_map'][dc_under_test]['CAL_ADC'],
                num_repeats=num_repeats_chirp,
                blk_multiples=blk_mult
            )
            assert fig is None
            
            # Round up the relays states first, the second element in the list refers to data in each step chirp
            param_list = list()
            measured_params[f'float_dut_{float_dut}'] = param_list
            relays_daqs[f'float_dut_{float_dut}'] = {
                self.hardware.dc_mapping.inverse[dc] : 
                copy.deepcopy({
                    k : dc_configs[dc][k] for k in [
                        'ADC_SEL', 
                        'DAC_SEL',  
                        'PClamp_CTRL', 
                        'P1_E_CTRL', 
                        'P2_E_CTRL', 
                        'P1_CAL_CTRL', 
                        'P2_CAL_CTRL'
                    ]
                }) 
                for dc in dc_configs
            }
            param_list.extend([
                relays_daqs[f'float_dut_{float_dut}'], dict()
            ])
            
            for freq, idx in zip(freq_arr, indices):
                chirp_idx = []
                chirp_idx.append(int(idx[0] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))
                chirp_idx.append(int(idx[1] / len(ADS8686_SEQUENCER_SETUP) / (2.5)))

                v1_gain = 31 * 31 * (10**(-13/20)) if float_dut else 1

                data_chirp[step_chirp] = {
                    'volt': volt_chirp[chirp_idx[0]:chirp_idx[1]],  # measured stimulus data
                    't': t_chirp[chirp_idx[0]:chirp_idx[1]],
                    'v1': ads_separate_data_chirp[self.adc_v1[0]][self.adc_v1[1]][chirp_idx[0]:chirp_idx[1]],
                    'v1_gain': v1_gain, 
                    'src': 'v',
                    'shape': 'SINE',
                    'freq': freq,  # stimulus frequency
                    'amp': voltage_amp,
                    'dc_under_test': dc_under_test,
                    'bath_clamp': copy.deepcopy(dc_configs[self.hardware.dc_mapping['bath']]),
                    'voltage_clamp': copy.deepcopy(dc_configs[self.hardware.dc_mapping['clamp']])
                }
                # Round all the step chirp data into the second dict of the list
                param_list[1].update({
                    step_chirp : {k : copy.deepcopy(v) for k,v in data_chirp[step_chirp].items() if k not in [
                        'bath_clamp', 'voltage_clamp', 'vsense'
                        ]
                    }
                })
                step_chirp += 1
        # save Chirp data 
        filename_chirp = f'imp_all_steps_chirp_floatdut_{file_name}' + '_{}'
        np.savez(os.path.join(data_dir, filename_chirp.format(testing)), data_chirp) # saved to a Numpy npz file 
        # Announce the completion of the chirp test for voltage clamp
        logger.info(f"Completed chirp test for voltage clamp. Data saved to {filename_chirp.format(testing)}")

        return data_chirp, measured_params, filename_chirp, step_chirp

    def transfer_functions_fit(self, testing, data_chirp, dc_configs, dc_under_test, voltage_amp, step_chirp, freq_arr, 
                            r_total_guess):
        """
        Fit transfer functions and extract component resistances.

        Parameters
        ----------
        testing : str
            Test type ('bath' or 'clamp').
        data_chirp : dict
            Chirp data for fitting.
        dc_configs : dict
            Daughtercard configurations.
        dc_under_test : int
            Index of daughtercard under test.
        voltage_amp : float
            Voltage amplitude of chirp stimulus.
        step_chirp : int
            Step index for chirp data.
        freq_arr : np.ndarray
            Array of frequencies for chirp.
        r_total_guess : float
            Initial guess for resistance fit.
        
        Returns
        -------
        predicted_res : float
            Predicted total resistance.
        res_fit_mesg : str
            Fit message.
        component_fits : dict
            Fitted component values.
        fit_notes : str
            Notes from fitting process.
        components : dict
            Component results.
        data_chirp : dict
            Updated chirp data.
        filename_chirp : str
            Filename for saved chirp data.
        step_chirp : int
            Updated step index.
        """
        # Log inside the transfer_functions_fit method
        logger = getLogger("Transfer Functions Fit")
        logger.setLevel(logging.INFO)
        # Path to save figures
        figure_path = Headstage.define_directory_for_plots(
            os.path.join(fig_dir, f"Transfer_function_figures_for_{testing}")
        )
        measured_params = None
        if testing == 'bath':
            data_chirp, measured_params, filename_chirp, step_chirp = self.chirp_test(
                testing, data_chirp, dc_configs, dc_under_test, 
                voltage_amp, step_chirp, freq_arr=freq_arr
            )
        elif testing=='clamp':
            data_chirp, measured_params, filename_chirp, step_chirp = self.chirp_test_vclamp(
                testing, data_chirp, dc_configs, dc_under_test, 
                voltage_amp, step_chirp, freq_arr
            )
        # process data
        if testing == 'clamp':
            tf_type = 'vclamp'
            r_total_guess = 300e3
        elif testing == 'bath':
            tf_type = 'elec_r_cc'
            r_total_guess = 8e3

        # calculates both the total resistance (measured via current injection) and the isolated resistance infered by transfer functions 
        # fails with tf_type = 'vclamp'
        predicted_res, res_fit_mesg, component_fits, fit_notes, components, figures_table = total_res_iso_res(
            data_chirp, r_total_guess, tf_type, PLT=True
        )
        logger.info(json.dumps(components))

        # Save the figure and create the look up table based on paths
        figure_paths_table = Headstage.save_plot(figure_path, figures_table)

        # For transfer function fit: a list [plot object, measured parameters]
        self.EXPERIMENTS.update({
            f'Transfer functions fit for {testing}' : [
                figure_paths_table, 
                measured_params, 
                {f"fit notes for {testing}" : copy.deepcopy(components) | {"fit notes" : fit_notes}}
            ]
        })
        self.FIT_RESULTS[f'Transfer functions fit for {testing}'] = copy.deepcopy(components) | {"fit notes" : fit_notes}

        return predicted_res, res_fit_mesg, component_fits, fit_notes, components, data_chirp, filename_chirp, step_chirp
    def save_log(self, logtype= Literal["all", "fit_notes", "relays_DAQs"], filename = None):
        """
        Save experiment logs, fit notes, or relay/DAQ states to JSON.

        Parameters
        ----------
        logtype : Literal["all", "fit_notes", "relays_DAQs"], optional
            Type of log to save.
        filename : str, optional
            Filename for saved log.

        Returns
        -------
        None
        """
        class NonSerializableHandler(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, Figure):
                    return o.__str__()
                if isinstance(o, np.ndarray):
                    return o.tolist()
                if isinstance(o, bidict):
                    return dict(o)
                return super().default(o)
        if filename is None:
            filename = logtype + ".json"
        with open(filename, 'w') as f:
            if logtype == "all":
                json.dump(self.EXPERIMENTS, f, indent=4, cls=NonSerializableHandler)
            elif logtype == "fit_notes":
                json.dump(self.FIT_RESULTS, f, indent=4, cls=NonSerializableHandler)
            elif logtype == "relays_DAQs":
                json.dump(self.RELAYS_DAQS, f, indent=4, cls=NonSerializableHandler)
            else:
                raise ValueError("Only use hints shown")

#############################################################
####### MAIN SCRIPT FOR CALIBRATION ########################
#############################################################
def experiment(hardware : HardwareSetup, lowergain_clamp, uppergain_clamp) -> Headstage:
    """
    Main script for calibration experiment.

    Initializes hardware, configures boards, collects data, measures resistance, performs chirp testing,
    fits transfer functions, and saves results.

    Parameters
    ----------
    hardware : HardwareSetup
        Hardware setup instance.
    lowergain_clamp : int
        Lower gain setting for clamp amplifier.
    uppergain_clamp : int
        Upper gain setting for clamp amplifier.

    Returns
    -------
    headstage : Headstage
        Headstage instance with experiment results.

    Notes
    -----
    Results are saved to JSON and CSV files in the results and data directories.
    """
    # Root logger for the experiment
    logging.basicConfig(level=logging.INFO)

    read_test = ReadTest()

    for i, daughtercard in enumerate(hardware.clamps):
        if daughtercard is not None:
            read_test.add_board(
                daughtercard, 
                name = hardware.dc_mapping.inverse[i], 
                allow_DAC_write=False, 
                allow_TCA_write=False
            )

    headstage = Headstage(hardware=hardware, lowergain_clamp=lowergain_clamp, uppergain_clamp=uppergain_clamp)
    headstage.hardware.ddr.data_version = 'TIMESTAMPS'

    headstage.hardware.configure_dac_80508()

    headstage.hardware.daq.set_isel(port=1, channels=None)
    headstage.hardware.daq.set_isel(port=2, channels=None)


    # ----------------- Colect Data -------------------
    setup_info = {
        'dut': 'model_cell', 
        'hookup': 'all_connected', 
        'board': 2, 'rej1': 200e3, 
        'rpcj1':10e3, 'srj1': 1e3, 
        'dc_mapping': dict(headstage.hardware.dc_mapping), 
        'guard': 'removed_rsb1_rl2'
    }
    with open(os.path.join(data_dir, 'setup_info' + file_name + '.json'), 'w') as fp:
        json.dump(setup_info, fp, sort_keys=True, indent=4)

    for i in range(6):
        # set all fast-DAC DDR data to midscale
        headstage.hardware.ddr.data_arrays[i][:] = 0x2000

    # TODO: make more amenable to membrane voltage 
    sdac_amp_volt = 1  # 1 Volt amplitude. 2 V peak to peak # amplitude was checked on oscilloscope (bipolar creates gain of *3 with 0 mean)
    # at 1 V the DAC code is max=58928, min=6554
    target_freq_sdac = 1000.0  # Hz
    sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

    # Data for the 2 DAC80508 "Slow DACs"
    sdac_sine, sdac_freq = headstage.hardware.ddr.make_sine_wave(
        amplitude=sdac_amp_code, 
        frequency=target_freq_sdac, 
        offset=dac80508_offset
    )

    # Specify output channel for DAC80508
    sdac_ch = headstage.hardware.daq.parameters['gp_dac_map'][0]['CAL']
    if sdac_ch[0] == 1:
        sdac_1_out_chan = sdac_ch[1]
    if sdac_ch[0] == 2:
        sdac_2_out_chan = sdac_ch[1]  # don't care, this channel is not connected to CAL
    else:
        sdac_2_out_chan = 0  # need a default channel
    # Clear bits in the FDAC DDR stream that store the slow DAC channel
    for i in range(6):
        headstage.hardware.ddr.data_arrays[i] = np.bitwise_and(
            headstage.hardware.ddr.data_arrays[i], 0x3fff
        )

    # Load data into DDR
    # Set channel bits # TODO: make this a method of the DDR
    headstage.hardware.ddr.data_arrays[0] = np.bitwise_or(
        headstage.hardware.ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13
    )
    headstage.hardware.ddr.data_arrays[1] = np.bitwise_or(
        headstage.hardware.ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14
    )
    headstage.hardware.ddr.data_arrays[2] = np.bitwise_or(
        headstage.hardware.ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13
    )
    headstage.hardware.ddr.data_arrays[3] = np.bitwise_or(
        headstage.hardware.ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14
    )

    # load slow DAC sine-wave in DDR channels 6
    headstage.hardware.ddr.data_arrays[6] = sdac_sine  # TODO: just one
    headstage.hardware.ddr.data_arrays[7] = sdac_sine


    # for testing in ['bath']:
    # TODO: Potential segment that caused the lmfit issue!
    for testing in ['bath', 'clamp']:
        step = 1
        data = {}
        data_chirp = {}
        if testing == 'bath':
            dc_under_test = headstage.hardware.dc_mapping['bath']  # TODO: get these indices from the boards configuration
            dc_disconnect = headstage.hardware.dc_mapping['clamp']
        elif testing == 'clamp':
            dc_under_test = headstage.hardware.dc_mapping['clamp']
            dc_disconnect = headstage.hardware.dc_mapping['bath']

        dc_configs, sys_connections = headstage.setup_clamps(dc_under_test=dc_under_test, dc_disconnect=dc_disconnect)
        read_test.get_log()

        headstage.hardware.ddr.write_setup()
        block_pipe_return, speed_MBs = headstage.hardware.ddr.write_channels(
            set_ddr_read=False)  # TODO: is this actually used or just promptly overwritten?
        headstage.hardware.ddr.reset_mig_interface()
        headstage.hardware.ddr.write_finish()

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
        # TODO: Comment out when done debugging
        # breakpoint()
        # measure resistance 
        dc_configs[dc_under_test], rdata, fit_resistance, pcov, mesg, ads_separate_data = headstage.measure_resistance(
            dc_configs[dc_under_test], dc_configs=dc_configs, dc_under_test=dc_under_test, testing=testing,
            step=1, plt_data=True, plt_fit=True,
            write_ddr=True, r_total_guess=r_total_guess)
        if testing == 'clamp':  # needs extra time to settle
            dc_configs[dc_under_test], rdata, fit_resistance, pcov, mesg, ads_separate_data = headstage.measure_resistance(
                dc_configs[dc_under_test], dc_configs=dc_configs, dc_under_test=dc_under_test,
                testing=testing,
                step=1, plt_data=True, plt_fit=True,
                write_ddr=False, r_total_guess=r_total_guess)
        data[step] = rdata[step]

        # the resistance data does not need to be saved because it is prepended onto the data_chirp dictionary  
        filename_chirp = 'dc_resistance_{}'
        np.savez(os.path.join(data_dir, filename_chirp.format(testing)), data) # saved to a Numpy npz file 

        # ------------- Prepare the daughtercards for chirp testing -----------------
        
        if testing == 'bath':
            freq_arr = np.logspace(np.log10(400), np.log10(50000), 8)
        elif testing == 'clamp':  # ground the bath clamp electrodes since 5k is small compared to the 200kOhm of the voltage clamp
            freq_arr = np.logspace(np.log10(10), np.log10(2000), 8)

        # log_info_bath, dc_configs[dc_disconnect] = headstage.hardware.clamps[dc_disconnect].configure_clamp(**dc_configs[dc_disconnect])

        # disable the current source 
        headstage.hardware.daq.set_isel(port=1, channels=None) # channel select works correctly -- this turns off the signal 
        # ---- CHIRP testing ------------
        data_chirp[1] = data[1] # add resistance data 
        step_chirp = 2

    #    if testing == 'bath' or testing == 'vclamp':
        predicted_res, res_fit_mesg, component_fits, fit_notes, components, data_chirp, filename_chirp, step_chirp = headstage.transfer_functions_fit(
            testing=testing, 
            data_chirp=data_chirp, 
            dc_configs=dc_configs, 
            dc_under_test=dc_under_test, 
            freq_arr=freq_arr, 
            voltage_amp=voltage_amp, 
            step_chirp=step_chirp, 
            r_total_guess=r_total_guess
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
        
        del data, data_chirp
    
    # Log the experiment results

    logging.info('Final Component Results ' + '-' * 40)
    logging.info(json.dumps(component_results))
    logging.info(f"CALIBRATION FINISHED")
    logging.info(f"To inspect the process with figures, visit path={fig_dir}")
    return headstage
