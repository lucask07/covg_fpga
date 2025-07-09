import os
import sys
from time import sleep
import datetime
import time
import atexit
import numpy as np
import matplotlib.pyplot as plt
import copy
import shutil
import itertools
from collections import UserDict
from scipy.signal import decimate

from pyripherals.utils import to_voltage, from_voltage, create_filter_coefficients
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3

# Defines data_dir_covg and adds the path to boards.py into the sys.path 
from setup_paths import *

from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5, separate_ads_sequence
from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams
from filters.filter_tools import bessel_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp, Vsense2
from calibration.electrodes import EphysSystem
from observer import Observer

# from analysis.cc_calibration import cc_waveform
from analysis.cc_inference import cat_cc_wave, infer_ccwave_spline

# this is a workaround for an issue once pytorch was installed
os.environ['KMP_DUPLICATE_LIB_OK'] = "TRUE"
sys.path.append('C:\\Users\\Public\\Documents\\covg\\my_pyabf\\pyABF\\src\\')  # need to use pyABF fork

from pyabf.abfWriter import writeABF1 
from pyabf.tools.covg import interleave_np

from instrbuilder.instrument_opening import open_by_name

def cmd_mv2dac(mv, sys_connections, dac_chan='D1'):
    """
    Convert a mV amplitude target of the CMD value to a DAC value 
    to upload to the DDR 
    Parameters
    ----------
    mv : target amplitude in milli-volts 
    sys_connections : Class of datastream.PhysicalConnections. Contains the conversion factor 
    dac_chan : The fast DAC that generates the CMD signal. Almost always default value of D1 

    Returns
    -------
    uint16: the DAC value in the range of 0 <-> 2^14 
    float:  the actual value in mV (since not exact due to rounding)
    """
    # convert to float because if numpy type assumption is array and then from_voltage returns a 0d array
    dac_amplitude = from_voltage(float(mv/1000), num_bits=sys_connections[dac_chan].bits, 
                                 voltage_range=sys_connections[dac_chan].conv_factor)

    cmd_voltage = to_voltage(dac_amplitude, num_bits=sys_connections[dac_chan].bits, 
                             voltage_range=sys_connections[dac_chan].conv_factor)

    return dac_amplitude, cmd_voltage

class BathclampVclampStepResponse:

    eps = Endpoint.endpoints_from_defines

    def __init__(self,* , set_vsense2, quiet_dacs : bool, ephys_system_name : str, 
                 model_cell_config : dict):
        """
        self.model_cell['number'] = 3 # guard
        # jumper configurable
        self.model_cell['Rs'] = 1e3
        self.model_cell['Rp1'] = 5e3
        self.model_cell['Rv1'] = 200e3
        # coupling cap back onto V1 might be DNI
        self.model_cell['coupling_cap_c20'] = 0
        self.model_cell['Rleak'] = 47e5 # this was misinterpreted. Its always been 4.7 Meg.
        """
        self.model_cell = dict()
        self.model_cell['number'] = model_cell_config['number'] # guard
        # jumper configurable
        self.model_cell['Rs'] = model_cell_config['Rs']
        self.model_cell['Rp1'] = model_cell_config['Rp1']
        self.model_cell['Rv1'] = model_cell_config['Rv1']
        # coupling cap back onto V1 might be DNI
        self.model_cell['coupling_cap_c20'] = model_cell_config['coupling_cap_c20']
        self.model_cell['Rleak'] = model_cell_config['Rleak'] # this was misinterpreted. Its always been 4.7 Meg.
        # ------------------ set VSENSE2 ------------------------ #
        self.VSENSE2 = set_vsense2
        # ------------------ set QUIET_DACS --------------------- #
        self.QUIET_DACS = quiet_dacs
        # EphysSystem Name -> ephys_sys = EphysSystem(system='Dagan_guard')
        self.ephys_sys = EphysSystem(system=ephys_system_name)
    
    def set_sample_params(self, *, DAC_FS, FS, SAMPLE_PERIOD, ADS_FS):
        """
        DAC_FS = 2.5e6
        FS = 5e6
        SAMPLE_PERIOD = 1/FS
        ADS_FS = 1e6
        """
        self.DAC_FS = DAC_FS
        self.FS = FS
        self.SAMPLE_PERIOD = SAMPLE_PERIOD
        self.ADS_FS = ADS_FS
    
    def setup_power(self, *, pwr_setup : str, neg):
        """
        pwr_setup = "3dual"
        """
        self.pwr_setup = pwr_setup
        # -------- power supplies -----------
        self.dc_pwr, self.dc_pwr2 = open_rigol_supply(setup=self.pwr_setup)

        atexit.register(pwr_off, [self.dc_pwr] if pwr_setup == "3dual" else [self.dc_pwr, self.dc_pwr2])
        # change to 16.5 if the negative regulator is still populated -> neg=15
        config_supply(self.dc_pwr, self.dc_pwr2, setup=pwr_setup, neg=neg)

        # turn on the 7V
        self.dc_pwr.set("out_state", "ON", configs={"chan": 1})

        if pwr_setup != "3dual":
            # turn on the +/-16.5 V input
            for ch in [1, 2]:
                self.dc_pwr2.set("out_state", "ON", configs={"chan": ch})
        elif pwr_setup == "3dual":
            # turn on the +/-16.5 V input
            for ch in [2, 3]:
                self.dc_pwr.set("out_state", "ON", configs={"chan": ch})

# Consider extending the FPGA class itself
class FPGAInterface:
    def __init__(self, experiment_class, dc_mapping : dict):
        self.experiment_class = experiment_class
        # Initialize FPGA
        self.f = FPGA()
        self.f.init_device()
        sleep(2)
        self.f.send_trig(self.experiment_class.eps["GP"]["SYSTEM_RESET"])  # system reset

        self.pwr = Daq.Power(self.f)
        self.pwr.all_off()  # disable all power enables

        self.daq = Daq(self.f)
        self.ddr = self.daq.ddr
        self.ad7961s = self.daq.ADC
        self.ad7961s[0].reset_wire(1)    # Only actually one WIRE_RESET for all AD7961s

        self.ads = self.daq.ADC_gp
        # clamp boards
        self.clamps = [None] * 4
        # Set dc_mapping
        self.set_dc_map(dc_mapping)
    
    def set_dc_map(self, dc_mapping : dict):
        """
        # Set dc_mapping -> dc_mapping = {'bath': 0, 'guard': 1, 'clamp': 2, 'vsense': 3}
        """
        self.dc_mapping = {'bath': None, 'guard': None, 'clamp': None, 'vsense': None}
        for key in dc_mapping:
            if key not in self.dc_mapping:
                raise ValueError("key can only be 1 in 4 components of the board, bath, guard, clamp, and vsense.")
            self.dc_mapping[key] = dc_mapping[key]

    
    def turn_on_power_supply(self, name_supply : list):
        # power supply turn on via FPGA enables -> name_supply = ["1V8", "5V", "3V3"]
        for name in name_supply:
            self.pwr.supply_on(name)
            sleep(0.05)
    
    def config_spi_debug_mux(self, *, spi_debug : str, ads_misc : str):
        # configure the SPI debug MUXs
        self.gpio = Daq.GPIO(self.f)
        self.gpio.spi_debug(spi_debug) # 'ads'
        self.gpio.ads_misc(ads_misc)  # -> 'convst' -> to check sample rate of ADS
    
    def organize_clamp_board(self):
        # instantiate the Clamp boards providing a daughter card number (from 0 to 3)
        # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3
        VSENSE2 = self.experiment_class.VSENSE2
        # not vsense2 -> indices of clamp boards, vsense2 -> can't be clamp. include the guard
        self.DC_NUMS = [0,1,2] if VSENSE2 else [0,1,3]
        self.init_board()

    def init_board(self):
        for dc_num in self.DC_NUMS:
            if dc_num == self.dc_mapping['vsense']: # skip this with VSENSE2 
                clamp = Clamp(self.f, dc_num=dc_num, DAC_addr_pins=0b000, version=2)
            else:
                clamp = Clamp(self.f, dc_num=dc_num, version=2)
            print(f'Clamp {dc_num} Init'.center(35, '-'))
            clamp.init_board()
            clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
            self.clamps[dc_num] = clamp
    
    def configure_ads8686(self, *, ads_voltage_range, ads_hw_reset=False, lpf, ads_sequencer_setup: list):
        # -------- configure the ADS8686
        # ads_voltage_range = 5  # need this for to_voltage later 
        self.ads.hw_reset(val=ads_hw_reset)
        self.ads.set_host_mode()
        self.ads.setup()
        self.ads.set_range(ads_voltage_range) 
        self.ads.set_lpf(lpf) # lpf=376
        # Set up the ads sequencer
        # ads_sequencer_setup = [('0', '0'), ('1', '1'), ('2', '2')]
        # ads_sequencer_setup = [('0', '0'), ('1', '1'), ('3', '2')] # with the guard added, want AMP_OUT on socket 2 which is at A3; CAL_ADC of the Guard is digitized 
        #ads_sequencer_setup = [('1', '0'), ('2', '0')] 
        codes = self.ads.setup_sequencer(chan_list=ads_sequencer_setup)
        self.ads.write_reg_bridge() # 1 MSPS rate 
        self.ads.set_fpga_mode()
        # TODO: may we change these two lines?????
        self.daq.TCA[0].configure_pins([0, 0])
        self.daq.TCA[1].configure_pins([0, 0])
        # in_amp = 1 # 05/02 step response was 2; 05/04 in_amp = 1
        # in_amp = 2 # 05/02 step response was 2; 05/04 in_amp = 1
        # dac_range = 5  # 5V full-scale range of the fast DACs 
    
    # TODO: Function in question!!
    def fast_dac_chan_setup(self, dac_range):
        for i in range(6):
            self.daq.DAC[i].set_ctrl_reg(self.daq.DAC[i].master_config)
            self.daq.DAC[i].set_spi_sclk_divide()
            self.daq.DAC[i].filter_select(operation="clear")
            if self.experiment_class.QUIET_DACS:
                self.daq.DAC[i].write(int(0x2000)) # midscale 
                self.daq.DAC[i].set_data_mux("host")
            else:
                self.daq.DAC[i].write(int(0x2000))
                self.daq.DAC[i].set_data_mux("DDR")
                self.daq.DAC[i].set_data_mux("DDR", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name
            self.daq.DAC[i].change_filter_coeff(target="passthru")
            self.daq.DAC[i].write_filter_coeffs()
            self.daq.set_dac_gain(i, dac_range)  # 5V 
    
    # TODO: so the dacs is from 0 to 5 ???
    def quiet_unused_dacs(self, list_unused_dac: list):
        # Quiet unused DACs (add 2024/09/12) 2, 4, 5
        for i in list_unused_dac:
            if i not in range(6):
                raise ValueError("DAC values are only from 0 to 5.")
            self.daq.DAC[i].write(int(0x2000)) # midscale 
            self.daq.DAC[i].set_data_mux("host")
    
    def enable_fast_adcs(self, fast_adc_chans: list): # [0, 1, 2, 3]
        for chan in fast_adc_chans:
            self.ad7961s[chan].power_up_adc()  # standard sampling
        time.sleep(0.5)
        self.ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
        time.sleep(0.1)
        self.ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset
        time.sleep(0.1)
    
    def operate_vsense2(self):
        """
        Only used during the experiment step
        """
        if self.experiment_class.VSENSE2:
            # declare the Vsense2 class as the operating vsense board
            vsense = Vsense2(fpga=self.f, DAC_addr_pins=0b001, dc_num=self.dc_mapping['vsense'], TCA_addr_pins=0b111) # I don't know why this needs to be 0b001 for DAC
            #vsense.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))

            #read/write testing for DAC and I/O expander
            message = 0xBF
            vsense.DAC.write(message)
            r = vsense.DAC.read()
            print('-----READ/WRITE TESTS-----')
            print(f'DAC - write: {message}, DAC read: {r}')

            message = 0xAAAA #I/O expander writes 2 bytes
            vsense.TCA.write(message)
            r2 = vsense.TCA.read(register_name='OUTPUT') #need to specify here that I am reading from output
            print(f'TCA OUTPUT - write: {message}, TCA read: {r2}')

            message = 0x6666
            vsense.TCA.write(message, register_name='INPUT') #defaults to writing to OUTPUT, so specify otherwise
            r3 = vsense.TCA.read(register_name='INPUT') #defaults to reading input
            print(f'TCA INPUT - write: {message}, TCA read: {r3}')

            #calling gain setting method
            #vsense.set_gains(0b0000, 0b0000)
            gain1 = vsense.gain_dict[31]
            gain2 = vsense.gain_dict[31]
            vsense.setOffsetVoltage(0)
            vsense.set_gain(0b1011, 0b1011) #requires DAC offset voltage set before running function. Could be combined easily.
            return vsense, gain1, gain2

        



def make_cmd_cc(fpga_board : FPGAInterface, cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None):
    """Return the CMD and CC signals determined by the parameters.
        Does not write to DDR 

    Parameters
    ----------
    
    Returns
    -------
    np.ndarray, np.ndarray : the CMD signal data, the CC signal data.
    """
    dac_offset = 0x2000

    cmd_signal = fpga_board.ddr.make_step(
        low=dac_offset - int(cmd_val), high=dac_offset + int(cmd_val), length=step_len)  # 1.6 ms between edges

    if fc is not None:
        cmd_signal = bessel_lowpass_filter(cmd_signal, cutoff=fc, fs=2.5e6, order=1)

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
            cc_signal = bessel_lowpass_filter(
                cmd_signal - dac_offset, cutoff=fc, fs=2.5e6, order=1)*cc_scale + dac_offset
        else:
            cc_signal = (
                cmd_signal - dac_offset)*cc_scale + dac_offset
        if cc_delay != 0:
            cc_signal = delayseq_interp(
                cc_signal, cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    else:  # needed so that the cmd signal can be zero with a non-zero cc signal
        cc_signal = fpga_board.ddr.make_step(low=dac_offset - int(cc_val),
                                            high=dac_offset + int(cc_val),
                                            length=step_len) 
        if fc is not None:
            cc_signal = bessel_lowpass_filter(
                cc_signal, cutoff=fc, fs=2.5e6, order=1)
        if cc_delay != 0:
            cc_signal = delayseq_interp(
                cc_signal, cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    return cmd_signal, cc_signal

def set_cmd_cc(fpga_board : FPGAInterface, dc_nums, cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
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
        fpga_board.ddr.data_arrays[cmd_ch], fpga_board.ddr.data_arrays[cc_ch] = make_cmd_cc(fpga_board=fpga_board, cmd_val=cmd_val, cc_scale=cc_scale, cc_delay=cc_delay, fc=fc, step_len=step_len, cc_val=cc_val, cc_pickle_num=cc_pickle_num)
    write_ddr(fpga_board)

# TODO: the second function call, let's add some return values as in impulse file
def write_ddr(fpga_board : FPGAInterface):    
    # write channels to the DDR
    fpga_board.ddr.write_setup()
    # clear read, set write, etc. handled within write_channels
    fpga_board.ddr.write_channels(set_ddr_read=False)
    fpga_board.ddr.reset_mig_interface()
    fpga_board.ddr.write_finish()

def render_sys_connections(dc_configs, fpga_board : FPGAInterface, experiment_setup : BathclampVclampStepResponse):
    sys_connections = create_sys_connections(dc_configs, fpga_board.daq, experiment_setup.ephys_sys, 
                                             inamp_gain_correct=fpga_board.clamps[fpga_board.dc_mapping['bath']].correct_inamp_gain)
    return sys_connections

def capture_data(fpga_board : FPGAInterface, experiment_setup : BathclampVclampStepResponse, *, file_name_raw, data_dir, dc_configs, idx=0, filename=None):
    fpga_board.ddr.repeat_setup() # Get data

    if filename is None:
        filename = file_name_raw.format(idx) + '.h5'

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    fpga_board.ddr.save_data(data_dir, filename, num_repeats=128,
                                        blk_multiples=200)  # blk multiples must be multiple of 10 
    # each block multiple is 256 bytes 

    # update system connections since the daughtercard configurations have changed
    sys_connections = render_sys_connections(dc_configs, fpga_board, experiment_setup)
    # Plot using datastreams 
    datastreams, log_info = rawh5_to_datastreams(data_dir, filename, fpga_board.ddr.data_to_names, 
                                                 fpga_board.daq, sys_connections, outfile = None)
 
    return datastreams, log_info

def ds_add_log(experiment_setup : BathclampVclampStepResponse, datastreams, dc_configs, first_pos_step, *, cmd_val, 
               step_len, 
               cc_val, 
               fc_cmd, 
               sys_connections):
    datastreams.add_log_info(experiment_setup.ephys_sys.__dict__)  # all properties of ephys_sys 
    datastreams.add_log_info({'dc_configs': dc_configs})
    datastreams.add_log_info({'ddr_step_peak': first_pos_step})
    datastreams.add_log_info({'dut': 'model_cell'})
    datastreams.add_log_info({'quiet_dacs': experiment_setup.QUIET_DACS})
    datastreams.add_log_info({'cmd_val': cmd_val})
    datastreams.add_log_info({'cc_val': cc_val})
    datastreams.add_log_info({'step_len': step_len})
    datastreams.add_log_info({'fc_cmd': fc_cmd})
    datastreams.add_log_info({'model_cell': experiment_setup.model_cell})
    datastreams.add_log_info({'sys_connections': sys_connections})
    if experiment_setup.VSENSE2:
        datastreams.add_log_info({'notes': 'vsense2_board, guard, connect CC'})

    return datastreams

def ads_plot_zoom(ax, t_range=[3250,3300]):
    try:
        for ax_s in ax:
            ax_s.set_xlim(t_range)
            ax_s.grid('on')
    except:
        ax.set_xlim(t_range)
        ax.grid('on')

class PlotManager(UserDict):
    def __init__(self, datastreams):
        super().__init__()
        self.datastreams = datastreams
    def reset_datastreams(self, datastreams):
        self.datastreams = datastreams
    class Item:
        def __init__(self, *, ax, row=None, col=None, aes_key=None):
            self.set_ax(ax=ax, row=row, col=col)
            if aes_key is not None:
                self.set_attribute(aes_key=aes_key)
        def set_ax(self, *, ax, row=None, col=None):
            if ax is None:
                raise ValueError('ax cannot be None')
            if row == None:
                if col == None:
                    self.ax = ax
                else:
                    raise ValueError("col only exists if row exists")
            else:
                if col == None:
                    self.ax = ax[row]
                else:
                    self.ax = ax[row, col]
        def set_ax_properties(self, *, xlimit=None, ylimit=None, title=None):
            # Set x and y limits and title:
            if title is not None:
                self.ax.set_title(title)
            if xlimit is not None:
                self.ax.set_xlim(xlimit)
            if ylimit is not None:
                self.ax.set_ylim(ylimit)
        def set_attribute(self, aes_key : dict):
            self.aes_key = aes_key
        def set_line(self, line_object):
            self.line_object = line_object
    def positional_plot_with_datastream(self, type : str, ax, row=None, col=None, aes_key=None):
        try:
            self[type] = self.Item(ax=ax, row=row, col=col, aes_key=aes_key)
            line = self.datastreams[type].plot(self[type].ax, self[type].aes_key)
            self[type].set_line(line)
        except:
            self.pop(type, None)
            raise Exception()
    def __setitem__(self, key : str, item : Item):
        return super().__setitem__(key, item)
    def set_ax_properties(self, *, type=None, ax=None, row=None, col=None, xlimit=None, ylimit=None, title=None):
        if type is not None:
            self[type].set_ax_properties(xlimit=xlimit, ylimit=ylimit, title=title)
        else:
            if ax is None:
                raise ValueError("Once type is not specified, at least the ax must be provided")
            else:
                ax_dest = ax
                if row is None and col is not None:
                    raise ValueError("row must be provided before the col could be")
                if row is not None and col is None:
                    ax_dest = ax[row]
                if row is not None and col is not None:
                    ax_dest = ax[row, col]
                if title is not None:
                    ax_dest.set_title(title)
                if xlimit is not None:
                    ax_dest.set_xlim(xlimit)
                if ylimit is not None:
                    ax_dest.set_ylim(ylimit)
    def get_type_ax(self, type : str):
        return self[type].ax
    def get_type_line_obj(self, type : str) -> list:
        return self[type].line_object
    def get_type_aestheme(self, type : str):
        return self[type].aes_key
    def update_lines(self, type : str, custom_type=None, custom_keys=None):
        try:
            if custom_type is None:
                if custom_keys is None:
                    self.datastreams[type].update_lines(self.get_type_line_obj(type)[0])
                else:
                    self.datastreams[type].update_lines(self.get_type_line_obj(type)[0], custom_keys)
            else:
                if custom_keys is None:
                    self.datastreams[custom_type].update_lines(self.get_type_line_obj(type)[0])
                else:
                    self.datastreams[custom_type].update_lines(self.get_type_line_obj(type)[0], custom_keys)
        except:
            raise Exception()

def update_plots(first_time, datastreams, first_pos_step, plotmanager1=None, plotmanager2=None, figs=None, adg_r=100):

    # Two plots that are updated in realtime 
    # First plot is 2x2
    if first_time:
        figs = []
        fig, ax = plt.subplots(2,2, figsize=(10,8))
        plotmanager1 = PlotManager(datastreams)
        fig.canvas.manager.window.move(0,0)
        figs.append(fig)
        # AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane
        plotmanager1.positional_plot_with_datastream('P1', ax, 0, 0, {'marker':'.'})
        plotmanager1.set_ax_properties(type='P1', ylimit=[-100e-3, 100e-3])
        # CAL ADC : observing electrode P2 (configured by CAL_SIG2)
        try:
            plotmanager1.positional_plot_with_datastream('P2', ax, 0, 1, {'marker':'.'})
            plotmanager1.set_ax_properties(ax=ax, row=1, title='P2')
            plotmanager1.pop('CMD0', None)
        except:
            plotmanager1.positional_plot_with_datastream(type='CMD0', ax=ax, row=0, col=1, aes_key={'marker':'.'})
            plotmanager1.set_ax_properties(type='CMD0', ylimit=[-100e-3, 100e-3])
            plotmanager1.pop('P2', None)

        plotmanager1.positional_plot_with_datastream('V1', ax, 1, 0, {'marker':'.'})
        plotmanager1.positional_plot_with_datastream('I', ax, 1, 1, {'marker':'.'})
    else:
        # datastreams['P1'].update_lines(lines1[0][0])
        # When we come back and replot, we reassigned with a different `Datastream` object so we need to reset 
        # datastreams to get the underlying data updated
        plotmanager1.reset_datastreams(datastreams)
        plotmanager1.update_lines('P1')
        second_key = 'P2' if 'P2' in plotmanager1 else 'CMD0'
        try:
            plotmanager1.update_lines(second_key, custom_type='P2')
        except:
            plotmanager1.update_lines(second_key, custom_type='CMD0')
        plotmanager1.update_lines('V1')
        plotmanager1.update_lines('I')
        # CAL ADC : observing electrode P2 (configured by CAL_SIG2)

    # second plot, membrane current and CMD 
    if first_time:
        plotmanager2 = list()
        fig, axs = plt.subplots(2,1,figsize=(10,8))
        fig.canvas.manager.window.move(600,0)
        figs.append(fig)
        for idx,ax in enumerate(axs):
            ax_right = ax.twinx()
            component_plot = PlotManager(datastreams)
            component_plot.positional_plot_with_datastream('CMD0', ax=ax_right, aes_key={'linestyle':'--', 'color':'r', 'label': 'CMD'})
            component_plot.positional_plot_with_datastream('P1', ax=ax_right, aes_key={'linestyle':'-', 'color': 'b', 'label': 'P1'})
            component_plot.positional_plot_with_datastream('Im', ax=ax, aes_key={'marker':'.', 'color': 'k', 'label': 'Im', 'decimate':[5,5], 'invert':-1})
            # l1 = datastreams['CMD0'].plot(ax_right, {'linestyle':'--', 'color':'r', 'label': 'CMD'})
            # l2 = datastreams['P1'].plot(ax_right, {'linestyle':'-', 'color': 'b', 'label': 'P1'})
            # l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'decimate':[5,5], 'invert':-1})
            #l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'invert':-1})

            component_plot.set_ax_properties(ax=ax, ylimit=[-60e-6, 60e-6])
          
            # lns = l1+l2+l3
            lns = []
            for type in component_plot:
                lns += component_plot.get_type_line_obj(type)
            
            labs = [l.get_label() for l in lns]
            ax.legend(lns, labs, loc=2)
            plotmanager2.append(component_plot)

            if idx==1: # zoom in at edge 
                ads_plot_zoom(ax, t_range=[first_pos_step*1e6-50, first_pos_step*1e6+200])
                ads_plot_zoom(ax_right, t_range=[first_pos_step*1e6-50, first_pos_step*1e6+200])
            else: 
                ads_plot_zoom(ax, t_range=[first_pos_step*1e6-300, first_pos_step*1e6*2+300])
                ads_plot_zoom(ax_right, t_range=[first_pos_step*1e6-300, first_pos_step*1e6*2+300])

    else:
        # for l2 in lines2:
        #     datastreams['CMD0'].update_lines(l2[0][0]) # TODO: why is this a list?
        #     datastreams['P1'].update_lines(l2[1][0])
        #     datastreams['Im'].update_lines(l2[2][0], {'decimate':[10,10], 'invert':-1})
        for component_plot in plotmanager2:
            component_plot.reset_datastreams(datastreams)
            for type in component_plot:
                if type == 'Im':
                    component_plot.update_lines(type=type, custom_keys={'decimate':[10,10], 'invert':-1})
                else:
                    component_plot.update_lines(type)
        
        im_data = datastreams['Im'].data
        t = datastreams['Im'].create_time()
        fc = 500e3 #5e3
        im_data_filt = bessel_lowpass_filter(im_data, cutoff=fc, fs=1/(t[1]-t[0]), order=5)
        idx = (t > first_pos_step + 2e-3) & (t < first_pos_step + 5e-3)
        im_noise_wb = np.std(im_data[idx])
        im_noise_filt = np.std(im_data_filt[idx])
        print(f'Im gain of {adg_r} kOhm = {(adg_r*1e3)*1e3*1e-9} mV/nA. Current noise of {im_noise_wb*1e9} nA full-bw; {im_noise_filt*1e9} nA {fc} bw')

    for fig in figs:
        fig.canvas.draw()
        fig.canvas.flush_events()
    
    first_time = False

    return first_time, plotmanager1, plotmanager2, figs, datastreams, idx

def measure_cmd_cc_impulse(fpga_board: FPGAInterface, experiment_class : BathclampVclampStepResponse, *, FS,
                           sys_connections, 
                           cmd_cc_scale : dict, plot_setting : dict, ccomp, first_pos_step, adgr_ccomp_combination, 
                           data_dir, h5_file_name, dc_configs, 
                           CC_IMPULSE : bool, CC_CANCELATION : bool, method_cc_cancelation : str, 
                           plot_cancel : bool):
    file_name = h5_file_name
    # measure CMD and CC impulse 
    ds = {}

    for adg_r, ccomp in adgr_ccomp_combination:
    # for adg_r, ccomp in ([(10, 47), (33,47), (100, 47), (33,4700), (100,4700), (332,47), (332,4700)]):

        if CC_IMPULSE:
            if adg_r > 100:
                cmd_val_set = 0x0080
                cc_val_set = 0x0040            
            else:
                cmd_val_set = 0x0200
                cc_val_set = 0x0100
            filename_imp = '{}_rtia{}_ccomp{}'.format(file_name, adg_r, ccomp)
            dc_configs[0]['ADG_RES'] = adg_r
            dc_configs[0]['CCOMP'] = ccomp
            fpga_board.clamps[0].configure_clamp(**dc_configs[0])

            for test in ['CMD', 'CC']:
                if test=='CMD':
                    cmd_val = cmd_val_set
                    cc_val = 0
                elif test=='CC':
                    cmd_val = 0
                    cc_val = cc_val_set
                set_cmd_cc(fpga_board=fpga_board, dc_nums=[fpga_board.dc_mapping['bath']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=cmd_cc_scale['fc_cmd'],
                    step_len=cmd_cc_scale['step_len'], cc_val=cc_val, cc_pickle_num=None)        
                time.sleep(0.2)
                
                datastreams, log_info = capture_data(fpga_board=fpga_board, 
                                                     experiment_setup=experiment_class, 
                                                     file_name_raw=file_name, 
                                                     data_dir=data_dir, 
                                                     dc_configs=dc_configs, 
                                                     idx=plot_setting['idx'])
                first_time, plotmanager1, plotmanager2, figs, datastreams, idx = update_plots(plot_setting['first_time'], 
                                                                                         datastreams, 
                                                                                         first_pos_step, 
                                                                                         plot_setting['plotmanager1'], 
                                                                                         plot_setting['plotmanager2'], 
                                                                                         plot_setting['figs'], adg_r)
                plot_setting['first_time'] = first_time
                plot_setting['plotmanager1'] = plotmanager1
                plot_setting['plotmanager2'] = plotmanager2
                plot_setting['figs'] = figs
                datastreams = ds_add_log(experiment_setup=experiment_class, 
                                         datastreams=datastreams, 
                                         dc_configs=dc_configs, 
                                         first_pos_step=first_pos_step, 
                                         cmd_val=cmd_val, 
                                         step_len=cmd_cc_scale['step_len'], 
                                         cc_val=cc_val, 
                                         fc_cmd=cmd_cc_scale['fc_cmd'], 
                                         sys_connections=sys_connections)

                if test == 'CMD':
                    datastreams.to_h5(data_dir, "cmd_impulse.h5", log_info)
                    # copy to include the filename so we don't overwrite 
                    shutil.copy2(os.path.join(data_dir, "cmd_impulse.h5"), os.path.join(data_dir, f"cmd_impulse_{filename_imp}.h5"))
                else:
                    datastreams.to_h5(data_dir, "cc_impulse.h5", log_info)
                    shutil.copy2(os.path.join(data_dir, "cc_impulse.h5"), os.path.join(data_dir, f"cc_impulse_{filename_imp}.h5"))

        # measure cc cancellation 
        CC_CANCEL = CC_CANCELATION
        method = method_cc_cancelation

        if CC_CANCEL:
            # read impulse files into datastreams
            ds['CMD0'] = h5_to_datastreams(data_dir, "cmd_impulse.h5")
            ds['CC0'] = h5_to_datastreams(data_dir, "cc_impulse.h5")

            if adg_r > 100:
                cmd_val_set = 0x0080
                cc_val_set = 0x0040            
            else:
                cmd_val_set = 0x0200
                cc_val_set = 0x0100

            if 'wiener' in method: 
                pass
                """
                windowed_filtered_cc_wave, filtered_cc_wave, cc_wave, impulse_c = cc_waveform(ds, l=0.0035, fc=20e3)

                # now use the filtered_cc_wave to replace CC 
                set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=None,
                step_len=16384*8, cc_val=cmd_val, cc_pickle_num=None)

                cc_nofilt = copy.deepcopy(ddr.data_arrays[dc_mapping['bath']])

                set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=fc_cmd,
                step_len=16384*8, cc_val=cmd_val, cc_pickle_num=None)

                idx = np.where(np.abs(np.diff(cc_nofilt)) > 0)
                span_l = int(len(filtered_cc_wave)/2)
                span_r = len(filtered_cc_wave) - span_l
                filtered_cc_wave_scale = filtered_cc_wave*0x200/1e-6*6
                dac_offset = 0x2000

                low = filtered_cc_wave_scale[0]
                high = filtered_cc_wave_scale[-1]
                low_replace = np.min(cc_nofilt)
                high_replace = np.max(cc_nofilt)
                ddr.data_arrays[dc_mapping['bath']][cc_nofilt < dac_offset] = low + dac_offset
                ddr.data_arrays[dc_mapping['bath']][cc_nofilt > dac_offset] = high + dac_offset

                for s in idx[0]:
                    pos = (ddr.data_arrays[dc_mapping['bath']][(s-span_l)] > dac_offset)
                    if pos:
                        ddr.data_arrays[dc_mapping['bath']][(s-span_l):(s+span_r)] = (filtered_cc_wave_scale + dac_offset).astype(np.uint16)
                    else:
                        ddr.data_arrays[dc_mapping['bath']][(s-span_l):(s+span_r)] = (-filtered_cc_wave_scale + dac_offset).astype(np.uint16)

                """
            if 'guess' in method: 
                # now use the filtered_cc_wave to replace CC 
                cc_val = int(-0.9*cmd_val_set)
                cmd_val = cmd_val_set
                set_cmd_cc(fpga_board=fpga_board, 
                           dc_nums=[fpga_board.dc_mapping['bath']], cmd_val=cmd_val, cc_scale=None, cc_delay=0, fc=None,
                        step_len=16384*8, cc_val=cc_val, cc_pickle_num=None)
            
            if 'spline' in method:
                cmd_val = cmd_val_set
                set_cmd_cc(dc_nums=[fpga_board.dc_mapping['bath']], cmd_val=cmd_val, cc_scale=None, cc_delay=0, fc=None,
                        step_len=16384*8, cc_val=cc_val, cc_pickle_num=None)
                cc_wave, configs, results = infer_ccwave_spline(DEBUG_PLOTS=True, run_date = '20240417', 
                                run_time = '163357', rtia=adg_r, ccomp=ccomp)
                cc_wave = decimate(cc_wave, q=2)
                norm_factor = cc_wave[-1] # so that we can concatenate rising and falling edges we need the the left most value to equal 0 and the right most to equal 1
                cc_wave = cc_wave/norm_factor
                cmd_wave = fpga_board.ddr.data_arrays[fpga_board.dc_mapping['bath']+1]
                # restore the amplitude below. Multiply by x2 due to difference in amplitude and pk-pk. FS due to discrete convolution "missing" the time step.  
                cc_wave_full = cat_cc_wave(cmd_wave, cc_wave, amplitude=-(cmd_val*2)*norm_factor*FS, midpt=8192)
                fpga_board.ddr.data_arrays[fpga_board.dc_mapping['bath']] = cc_wave_full.astype(np.uint16)
            plot_setting['idx'] = plot_setting['idx'] + 1
            if plot_cancel:
                first_time, plotmanager1, plotmanager2, figs, datastreams, idx = plot_if_cancellation(fpga_board, experiment_setup=experiment_class, dc_configs=dc_configs, 
                                                   sys_connections=sys_connections,  
                                                   plot_setting=plot_setting, 
                                                   cmd_cc_scale=cmd_cc_scale, 
                                                   first_pos_step=first_pos_step, cmd_val=cmd_val, cc_val=cc_val, adg_r=adg_r, 
                                                   data_dir=data_dir, h5_file_name=h5_file_name, 
                                    method=method, ccomp=ccomp, ds=ds)
    return ds, datastreams, first_time, plotmanager1, plotmanager2, figs, idx

def plot_if_cancellation(fpga_board : FPGAInterface, *, experiment_setup, dc_configs, 
                         sys_connections, 
                         plot_setting : dict, 
                         cmd_cc_scale : dict, 
                         first_pos_step, 
                         cmd_val, 
                         cc_val, 
                         adg_r, 
                         data_dir, 
                         h5_file_name, 
                         method, 
                         ccomp, 
                         ds : dict
                         ):
    file_name = h5_file_name
    # show the waveforms used 
    fig,ax = plt.subplots()
    ax.plot(fpga_board.ddr.data_arrays[fpga_board.dc_mapping['bath']][0:2**19], label='CC')
    ax.plot(fpga_board.ddr.data_arrays[fpga_board.dc_mapping['bath'] + 1][0:2**19], 'tab:orange', label='CMD')
    fig.suptitle('Cancelation waveforms')
    ax.legend()

    # write channels to the DDR
    write_ddr()

    idx = plot_setting['idx']
    datastreams, log_info = capture_data(fpga_board, 
                                             experiment_setup=experiment_setup, 
                                             file_name_raw=file_name, 
                                             data_dir=data_dir, 
                                             dc_configs=dc_configs, idx=idx)
    first_time, plotmanager1, plotmanager2, figs, datastreams, idx = update_plots(plot_setting['first_time'], 
                                                                             datastreams, 
                                                                             first_pos_step, 
                                                                             plot_setting['plotmanager1'], 
                                                                             plot_setting['plotmanager2'], 
                                                                             plot_setting['figs'], adg_r)
    plot_setting['first_time'] = first_time
    plot_setting['plotmanager1'] = plotmanager1
    plot_setting['plotmanager2'] = plotmanager2
    plot_setting['figs'] = figs
    datastreams = ds_add_log(fpga_board=fpga_board, experiment_setup=experiment_setup, 
                                 datastreams=datastreams, dc_configs=dc_configs, first_pos_step=first_pos_step, 
                                 cmd_val=cmd_val, step_len=cmd_cc_scale['step_len'], cc_val=cc_val, fc_cmd=cmd_cc_scale['fc_cmd'], sys_connections=sys_connections)
    datastreams.to_h5(data_dir, f"cancelation_{method}_{file_name}_rtia{adg_r}_ccomp{ccomp}.h5", log_info)
    ds['cancel'] = h5_to_datastreams(data_dir, f"cancelation_{method}_{file_name}_rtia{adg_r}_ccomp{ccomp}.h5")

    fig,ax = plt.subplots()
    clr = itertools.cycle(['k','b','r'])
    for meas in ['CMD0', 'CC0', 'cancel']:
        ds[meas]['Im'].plot(ax, {'marker':'.', 'color': next(clr), 'label': f'Im:{meas}', 'decimate':[5,5], 'invert':-1})
    fig.suptitle('Cancelation measurements')
    ax.legend()

    CAPTURE_CC_ALONE = True
    if CAPTURE_CC_ALONE:
        fpga_board.ddr.data_arrays[fpga_board.dc_mapping['bath'] + 1] = 8192 # zero CMD 
        # write channels to the DDR
        write_ddr()
        time.sleep(0.1)
        datastreams, log_info = capture_data(fpga_board, 
                                             experiment_setup=experiment_setup, 
                                             file_name_raw=file_name, 
                                             data_dir=data_dir, 
                                             dc_configs=dc_configs, idx=idx)
        first_time, plotmanager1, plotmanager2, figs, datastreams, idx = update_plots(plot_setting['first_time'], 
                                                                                 datastreams, 
                                                                                 first_pos_step, 
                                                                                 plot_setting['plotmanager1'], 
                                                                                 plot_setting['plotmanager2'], 
                                                                                 plot_setting['figs'], adg_r)
        datastreams = ds_add_log(experiment_setup=experiment_setup, 
                                 datastreams=datastreams, dc_configs=dc_configs, first_pos_step=first_pos_step, 
                                 cmd_val=cmd_val, step_len=cmd_cc_scale['step_len'], cc_val=cc_val, fc_cmd=cmd_cc_scale['fc_cmd'], sys_connections=sys_connections)
        datastreams.to_h5(data_dir, f"canceling_cc_{method}_{file_name}_rtia{adg_r}_ccomp{ccomp}.h5", log_info)
        ds['canceling_cc'] = h5_to_datastreams(data_dir, f"canceling_cc_{method}_{file_name}_rtia{adg_r}_ccomp{ccomp}.h5")

    fig,ax = plt.subplots()
    clr = itertools.cycle(['k','b','r', 'g'])
    for meas in ['CMD0', 'CC0', 'cancel', 'canceling_cc']:
        try:
            ds[meas]['Im'].plot(ax, {'marker':'.', 'color': next(clr), 'label': f'Im:{meas}', 'decimate':[5,5], 'invert':-1})
        except:
            pass
    fig.suptitle('Cancelation measurements')
    ax.legend()
    return first_time, plotmanager1, plotmanager2, figs, datastreams, idx

def large_param_sweep(fpga_board : FPGAInterface, experiment_setup : BathclampVclampStepResponse, file_name_before_format, 
                      *, 
                      osc, 
                      data_dir, 
                      dc_configs, 
                      mv_val_arr : np.ndarray, 
                      ccomp_arr, 
                      adg_r_arr, 
                      scope_meas, 
                      OSCOPE : bool, 
                      scope_data : dict, 
                      cmd_cc_scale : dict, 
                      plot_setting : dict, 
                      cc_val, 
                      clamp_fb_res, 
                      clamp_res, 
                      first_pos_step, 
                      TO_CLAMPFIT, 
                      sys_connections):
    for cmd_mv in mv_val_arr:
        cmd_val, actual_v = cmd_mv2dac(float(cmd_mv), sys_connections, dac_chan='D1') # if the input to from_voltage is numpy then assumption is array and it returns a 0d array
        for ccomp in ccomp_arr:
            for adg_r in adg_r_arr:
                print(f'Im-gain = {adg_r} kOhm = {(adg_r*1e3)*1e3*1e-9} mV/nA')

                if OSCOPE: 
                    scope_data['CC'] = np.append(scope_data['CC'], ccomp)
                    scope_data['RTIA'] = np.append(scope_data['RTIA'], adg_r)
                    scope_data['CLAMP_RF'] = np.append(scope_data['CLAMP_RF'], clamp_fb_res)
                    scope_data['CLAMP_TIA'] = np.append(scope_data['CLAMP_TIA'], clamp_res)

                dc_configs[0]['ADG_RES'] = adg_r
                dc_configs[0]['CCOMP'] = ccomp
                fpga_board.clamps[0].configure_clamp(**dc_configs[0])
                set_cmd_cc(fpga_board, dc_nums=[fpga_board.dc_mapping['bath'], fpga_board.dc_mapping['guard']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=cmd_cc_scale['fc_cmd'],
                    step_len=cmd_cc_scale['step_len'], cc_val=None, cc_pickle_num=None)
                time.sleep(0.2) # extend for noise analysis
                
                filename = 'step_rtia{}_ccomp{}_cmd{}.h5'.format(adg_r, ccomp, cmd_val)
                datastreams, log_info = capture_data(fpga_board=fpga_board, experiment_setup=experiment_setup, 
                                                     file_name_raw=file_name_before_format, data_dir=data_dir, dc_configs=dc_configs, 
                                                     idx=1, filename=filename)
                first_time, plotmanager1, plotmanager2, figs, datastreams, idx = update_plots(plot_setting['first_time'], 
                                                                                         datastreams, 
                                                                                         first_pos_step, 
                                                                                         plot_setting['plotmanager1'], 
                                                                                         plot_setting['plotmanager2'], 
                                                                                         plot_setting['figs'], adg_r)
                plot_setting['first_time'] = first_time
                plot_setting['plotmanager1'] = plotmanager1
                plot_setting['plotmanager2'] = plotmanager2
                plot_setting['figs'] = figs

                sig = 'Im' 
                si = datastreams[sig].stepinfo_range([first_pos_step-0.02e-3, first_pos_step+170e-6])
                print(f'Ccomp = {ccomp} and TIA resistance = {adg_r}; vclamp RF = {clamp_fb_res} and TIA {clamp_res}')
                print(f'{sig} step info: {si}')
                print('-'*100)

                if OSCOPE:
                    osc.set('single_acq')
                    time.sleep(0.05)
                    for sm in scope_meas:
                        scope_data[sm] = np.append(scope_data[sm], float(osc._ask(f'MEAS:{sm}? MATH1')))
                    t = osc.save_display_data(os.path.join(data_dir, 'scope__rtia{}_ccomp{}_cmd{}.abf'.format(adg_r, ccomp, cmd_val)))
                    osc.set('run_acq')
                if TO_CLAMPFIT:
                    datastreams.to_clampfit(data_dir, 'step_rtia{}_ccomp{}_cmd{}.abf'.format(adg_r, ccomp, cmd_val),
                                            names_pclamp = ['Im', 'CMD0', 'V1', 'P1'],
                                            dac_len=len(datastreams['CMD0'].data), dac_sample_rate=2.5e6, sweeps=1)

                # add log info to datastreams -- any dictionary is ok  
                datastreams = ds_add_log(experiment_setup=experiment_setup, 
                                         datastreams=datastreams, 
                                         dc_configs=dc_configs, 
                                         first_pos_step=first_pos_step, 
                                         cmd_val=cmd_val, 
                                         step_len=cmd_cc_scale['step_len'], 
                                         cc_val=cc_val, 
                                         fc_cmd=cmd_cc_scale['fc_cmd'], 
                                         sys_connections=sys_connections)
                datastreams.to_h5(data_dir, filename, log_info)
    return first_time, plotmanager1, plotmanager2, figs, datastreams, idx

def plot_oscilloscope(*, OSCOPE, 
                      adg_r_arr, 
                      scope_data):
    # plot oscilloscope data vs. parameters 
    if OSCOPE:
        for adg_r in adg_r_arr:
            idx = scope_data['RTIA']==adg_r
            fig,ax=plt.subplots(2,1)
            ax[0].plot(scope_data['CC'][idx], scope_data['OVER'][idx], marker='o')
            fig.suptitle(f'RTIA = {adg_r}')
            ax[0].set_ylabel('Vm Overshoot [%]')
            ax[1].plot(scope_data['CC'][idx], scope_data['RIS'][idx]*1e6, marker='o')
            ax[1].set_xlabel('CCOMP [pF]')
            ax[1].set_ylabel('Rise time [us]')
            fig.suptitle(f'RTIA = {adg_r}')

def plot_im_est(datastreams):
    Cm = 33e-9
    fig, ax = plt.subplots()
    fig.suptitle('Overlay Meas. Im and Im estimate')
    datastreams['Im'].plot(ax, {'marker':'.', 'label': 'Meas. Im'})
    t = datastreams['P1'].create_time()
    dt = t[1] - t[0]
    p1_diff = np.diff(datastreams['P1'].data)/dt
    #ax.plot(t[:-1]*1e6, -Cm*p1_diff, label='Im estimate via p1')
    ax.legend()
    return p1_diff
