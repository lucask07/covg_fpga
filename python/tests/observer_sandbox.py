"""This script is written for the purpose of testing Dr. Secord's PI controller design w/ Luenberger Observer.

January 2023

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
from matplotlib.pyplot import cm
import pickle as pkl
import copy
from pyripherals.utils import to_voltage, from_voltage, create_filter_coefficients, gen_mask
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

from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams
from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5, separate_ads_sequence
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp
from calibration.electrodes import EphysSystem

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
    ddr.write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()


def plot_dac_im_vm(datastreams, clr, fig, ax, dc_num=0):

    if fig is None:
        fig, ax = plt.subplots(4,1)

    # DAC CMD signal 
    lbl = ''
    datastreams[f'CMD{dc_num}'].plot(ax[0], {'label': lbl})

    # ADCs 
    datastreams[f'Im'].plot(ax[1], {'marker':'*', 'label': lbl})
    # AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane
    datastreams['P1'].plot(ax[2], {'marker': '.'})
    datastreams['I'].plot(ax[3], {'marker': '.'}) # this net is being repurposed to directly measure Vm
    ax[3].set_ylabel('Vm measured [V]')

    return fig, ax

# Class for Luenberger Observer
class Observer():
    """Class for Luenberger Observer on the FPGA

    Attributes
    ----------
    default_im_data_mux : dict
        Class attribute. Default im_data_mux dictionary.
    default_vcmd_mux : dict
        Class attribute. Default vcmd_data_mux dictionary.
    default_vp1_data_mux : dict
        Class attribute. Default vp1_data_mux dictionary.
    fpga : FPGA
        FPGA instance this controller uses to communicate.
    endpoints : dict
        Endpoints on the FPGA this controller uses to communicate.
    master_config : int
        Value of the CTRL register in the Wishbone.
    im_data_mux: dict
        Name to select value dictionary for source data MUX.
    vcmd_data_mux: dict
        Name to select value dictionary for source data MUX.
    vp1_data_mux: dict
        Name to select value dictionary for source data MUX.
    current_im_data_mux : str
        Name of the current MUX data source.
    current_vcmd_data_mux : str
        Name of the current MUX data source.
    current_vp1_data_mux : str
        Name of the current MUX data source.
    
    """

    default_im_data_mux = {
        'ad7961_ch0': 0,
        'ad7961_ch1': 1,
        'ad7961_ch2': 2,
        'ad7961_ch3': 3,
    }

    default_vcmd_data_mux = {
        'ad5453_ch0': 0,
        'ad5453_ch1': 1,
        'ad5453_ch2': 2,
        'ad5453_ch3': 3,
        'ad5453_ch4': 4,
        'ad5453_ch5': 5,
    }

    default_vp1_data_mux = {
        'ads8686_chA': 0,
        'ads8686_chB': 1,
    }

    default_rdy_data_mux = {
        'sync_im': 0,
        'sync_vp1': 1,
        'sync_vcmd': 2,
    }

    def __init__(self, fpga, endpoints=None, im_data_mux=default_im_data_mux, 
    vcmd_data_mux=default_vcmd_data_mux, vp1_data_mux=default_vp1_data_mux, rdy_data_mux=default_rdy_data_mux):

        self.fpga = fpga
        if endpoints is None:
            self.endpoints = Endpoint.get_chip_endpoints('OBSV')
        #self.endpoints = endpoints
        self.im_data_mux = im_data_mux
        self.vcmd_data_mux = vcmd_data_mux
        self.vp1_data_mux = vp1_data_mux
        self.rdy_data_mux = rdy_data_mux
        # Start with ad7961_ch0 to minimize unintentional commands from other sources on startup
        self.current_im_data_mux = None
        if self.set_im_data_mux('ad7961_ch0') == -1:
            # 'ad7961_ch0' was not in data_mux dict
            print("WARNING: no 'ad7961_ch0' in data_mux dict")
        # Start with ad5453_ch0 to minimize unintentional commands from other sources on startup
        self.current_vcmd_data_mux = None
        if self.set_vcmd_data_mux('ad5453_ch0') == -1:
            # 'ad5453_ch0' was not in data_mux dict
            print("WARNING: no 'ad5453_ch0' in data_mux dict")
        # Start with ads8686_chA to minimize unintentional commands from other sources on startup
        self.current_vp1_data_mux = None
        if self.set_vp1_data_mux('ads8686_chA') == -1:
            # 'ads8686_chA' was not in data_mux dict
            print("WARNING: no 'ads8686_chA' in data_mux dict")

        # Observer coefficients
        self.observer_offset = 0
        self.observer_coeff = {0:0x00000000,
                               1:0x00000000,
                               2:0x00000000,
                               3:0x00000000,
                               4:0x00000000,
                               5:0x00000000,
                               6:0x00000000,
                               7:0x00000000,
                               8:0x00000000,
                               9:0x00000000}
        self.observer_len = np.max(
            list(self.observer_coeff.keys())) - np.min(list(self.observer_coeff.keys()))
    
    def set_im_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.im_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'IM_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.im_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_im_data_mux = source
    
    def set_vcmd_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.vcmd_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'VCMD_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.vcmd_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_vcmd_data_mux = source

    def set_vp1_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.vp1_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'VP1_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.vp1_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_vp1_data_mux = source

    def set_rdy_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.rdy_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'RDY_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.rdy_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_rdy_data_mux = source

    def write_observer_coeffs(self):
        # TODO: add method docstring

        # TODO is this correct? and how to parameterize?
        for i in np.arange(self.observer_offset, 1 + self.observer_offset + self.observer_len):
            if (i-self.observer_offset) in self.observer_coeff:
                addr = int(
                    self.endpoints['REGBRIDGE_OFFSET'].address + i)
                val = int(self.observer_coeff[i-self.observer_offset])
                print(
                    'Write filter addr=0x{:02X}  value=0x{:02X}'.format(addr, val))
                self.fpga.xem.WriteRegister(addr, val)

    def change_observer_coeff(self, value=None):
        self.observer_coeff = value
        self.observer_len = np.max(
            list(self.observer_coeff.keys())) - np.min(list(self.observer_coeff.keys()))

FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6
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
        data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/rs_comp/{}{:02d}{:02d}')

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
ddr = DDR3(f, data_version='TIMESTAMPS')
ad7961s = daq.ADC
ad7961s[0].reset_wire(1)    # Only actually one WIRE_RESET for all AD7961s
ads = daq.ADC_gp

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


# -------- configure the ADS8686
ads_voltage_range = 5  # need this for to_voltage later 
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range) 
ads.set_lpf(376)
#ads_sequencer_setup = [('5', '4'), ('1', '1')]
# ads_sequencer_setup = [('1', '4')]
ads_sequencer_setup = [('1', '0')] # with Vm jumpered to 

ads_b_chan = 0
codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge(clk_div=200) # 1 MSPS rate (do not use default value which is 200 ksps)
ads.set_fpga_mode()


# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.1)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(1)
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S") + '_{}' # to append index 
idx = 0

# Set CMD and CC signals
set_cmd_cc(dc_nums=DC_NUMS, cmd_val=0x0100, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)

dc_configs = {}
for dc_num in DC_NUMS:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1", # required for comparative Vm measurement 
        DAC_SEL="drive_CAL2",
        CCOMP=47,
        RF1=2.1,  # feedback circuit
        ADG_RES=332,
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
    if dc_num < 2:
        dc_configs[dc_num] = config_dict

color = iter(cm.rainbow(np.linspace(0, 1, 4))) 

PI_coeff = {0: 0x7fffffff,
            1:0x50404ea5,
            2:0xb0404ea5,
            3: 0x00000000,
            4: 0xc0000000,
            5: 0x00000000,
            8: 0x7fffffff,
            9: 0x20000000,
            10: 0x00000000,
            11: 0x00000000,
            12: 0x00000000,
            13: 0x00000000,
            7: 0x7fffffff,
            15: 0x0000_089a}

# set observer data input muxes
obsv = Observer(f)
obsv.set_im_data_mux("ad7961_ch0")
obsv.set_vcmd_data_mux("ad5453_ch1")
obsv.set_vp1_data_mux("ads8686_chA")
obsv.set_rdy_data_mux("sync_im")

# observer coeffs
obsv_coeff = {0:0x00fd4c52,
1:0x000009ac,
2:0x054ecf2e,
3:0xfffec841,
4:0x00fb6f97,
5:0x00000005,
6:0xfcb79653,
7:0x00f674ae,
8:0x01987ac9,
9:0x0004a391}

obsv.change_observer_coeff(obsv_coeff)
obsv.write_observer_coeffs()

# TODO: note that only 2 DACs are configured 
for i in [1]:
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="set")
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("DDR")
    daq.DAC[i].set_data_mux("DDR_norepeat", filter_data=True)
    daq.DAC[i].filter_sum("clear")
    daq.DAC[i].filter_downsample("clear")
    daq.DAC[i].change_filter_coeff(target="generated", value=PI_coeff)
    #daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain((i-1), 5)  # 5V to see easier on oscilloscope

for i in [3]:
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="set")
    daq.DAC[i].write(int(0))
    #daq.DAC[i].set_data_mux("DDR")
    #daq.DAC[i].set_data_mux("ads8686_chA", filter_data=True)
    #daq.DAC[i].filter_sum("set")
    #daq.DAC[i].filter_downsample("set")
    #daq.DAC[i].change_filter_coeff(target="generated", value=PI_coeff)
    #daq.DAC[i].write_filter_coeffs()
    #daq.set_dac_gain((i-1), 5)  # 5V to see easier on oscilloscope

time.sleep(0.1)
ddr.repeat_setup()
# Get data
# saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
#chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
#                                    blk_multiples=40)  # blk multiples multiple of 10
data_dir_ian = r"C:\Users\delg5279\OneDrive - University of St. Thomas\covg_pi_ctrl_files"
file_name = 'PI_ctrl_data.h5'
chan_data_one_repeat = ddr.save_data(data_dir, file_name, num_repeats=8,
                                    blk_multiples=40)  # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))

# Long data sequence -- entire file
# Grab Observer data from here -- dac_data
adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = ddr.data_to_names(chan_data)
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

ephys_sys = EphysSystem()
sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)
datastreams, log_info = rawh5_to_datastreams(data_dir, file_name, ddr.data_to_names, daq, sys_connections, outfile = None)


if idx in [0, 5, 10, 15]:
    clr = next(color)
    if idx == 0:
        fig = None
        ax = None
    fig, ax = plot_dac_im_vm(datastreams, clr, fig, ax, dc_num=0)
idx = idx + 1

fig,ax=plt.subplots()
datastreams['CMD0'].plot(ax)

fig,ax=plt.subplots()
datastreams['CMD1'].plot(ax)

fig,ax=plt.subplots()
datastreams['Im'].plot(ax)

fig,ax=plt.subplots()
datastreams['Itop'].plot(ax)

fig, ax = plt.subplots(2,1)
fig.suptitle('ADS data')
# AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane

datastreams['P1'].plot(ax[0], {'marker':'.'})
datastreams['I'].plot(ax[1], {'marker':'.'})
ax[1].set_ylabel('Vm measured [V]')



# plot dac channel 4 data
fig,ax=plt.subplots()
datastreams['OBSV'].plot(ax)

# plot dac channel 5 data
fig,ax=plt.subplots()
datastreams['OBSV_CH1'].plot(ax)

# subplot of Observer Vm and measured Vm
fig,ax=plt.subplots(2,1)
fig.suptitle('Observer Vm vs ADS8686')
# Observer - stored in DDR at 1 MSPS -- dac_data[4] is observer output 0, dac_data[5] is observer output 1, dac_data[6] is obs. output 0 shifted by 400 ns
datastreams['OBSV'].plot(ax[0], {'marker':'.'})
datastreams['I'].plot(ax[1], {'marker':'.'})
ax[1].set_ylabel('Vm measured [V]')


def ads_plot_zoom(ax):
    for ax_s in ax:
        ax_s.set_xlim([3250, 3330])
        ax_s.grid('on')
