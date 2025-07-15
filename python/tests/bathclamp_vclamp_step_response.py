"""

Summer 2024
Dervied from clamp_step_response.py

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""
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
from tests_solidify.bathclamp_vclamp_utils import *
from tests.clamp_sandbox import get_cc_optimize

# from analysis.cc_calibration import cc_waveform
from analysis.cc_inference import cat_cc_wave, infer_ccwave_spline

# this is a workaround for an issue once pytorch was installed
os.environ['KMP_DUPLICATE_LIB_OK'] = "TRUE"
sys.path.append('C:\\Users\\Public\\Documents\\covg\\my_pyabf\\pyABF\\src\\')  # need to use pyABF fork

from pyabf.abfWriter import writeABF1 
from pyabf.tools.covg import interleave_np

from instrbuilder.instrument_opening import open_by_name

osc = open_by_name('msox_scope')

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

def make_cmd_cc(cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
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

    cmd_signal = ddr.make_step(
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
        cc_signal = ddr.make_step(low=dac_offset - int(cc_val),
                                               high=dac_offset + int(cc_val),
                                               length=step_len) 
        if fc is not None:
            cc_signal = bessel_lowpass_filter(
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
        cmd_ch = dc_num * 2 + 1 # TODO: replace with daq.parameters['fast_dac_map']
        cc_ch = dc_num * 2
        ddr.data_arrays[cmd_ch], ddr.data_arrays[cc_ch] = make_cmd_cc(cmd_val=cmd_val, cc_scale=cc_scale, cc_delay=cc_delay, fc=fc, step_len=step_len, cc_val=cc_val, cc_pickle_num=cc_pickle_num)
    write_ddr()

def write_ddr():    
    # write channels to the DDR
    ddr.write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()

model_cell = {}
model_cell['number'] = 3 # guard
# jumper configurable
model_cell['Rs'] = 1e3
model_cell['Rp1'] = 5e3
model_cell['Rv1'] = 200e3
# coupling cap back onto V1 might be DNI
model_cell['coupling_cap_c20'] = 0
model_cell['Rleak'] = 47e5 # this was misinterpreted. Its always been 4.7 Meg. 

def ds_add_log(datastreams):
    datastreams.add_log_info(ephys_sys.__dict__)  # all properties of ephys_sys 
    datastreams.add_log_info({'dc_configs': dc_configs})
    datastreams.add_log_info({'ddr_step_peak': first_pos_step})
    datastreams.add_log_info({'dut': 'model_cell'})
    datastreams.add_log_info({'quiet_dacs': QUIET_DACS})
    datastreams.add_log_info({'cmd_val': cmd_val})
    datastreams.add_log_info({'cc_val': cc_val})
    datastreams.add_log_info({'step_len': step_len})
    datastreams.add_log_info({'fc_cmd': fc_cmd})
    datastreams.add_log_info({'model_cell': model_cell})
    datastreams.add_log_info({'sys_connections': sys_connections})
    if VSENSE2:
        datastreams.add_log_info({'notes': 'vsense2_board, guard, connect CC'})

    return datastreams

DAC_FS = 2.5e6
FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6

dc_mapping = {'bath': 0, 'guard': 1, 'clamp': 3, 'vsense': 2}  # LJK, 8/30/2024 move clamp to 2 to prepare for adding guard -- this will mess up some of the ADS8686 numbers
# dc_mapping = {'bath': 0, 'clamp': 1, 'vsense': 3, 'guard': 2} # Guard is not actually used and not connected  

eps = Endpoint.endpoints_from_defines
pwr_setup = "3dual"

# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)
if pwr_setup == "3dual":
    atexit.register(pwr_off, [dc_pwr])
else:
    atexit.register(pwr_off, [dc_pwr, dc_pwr2])
# change to 16.5 if the negative regulator is still populated
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
ddr = daq.ddr
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

# instantiate the Clamp boards providing a daughter card number (from 0 to 3)
# list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3
VSENSE2 = True 
if VSENSE2 is False:
    DC_NUMS = [0,1,3] # DC_NUMS are the indices of the clamp boards. 
else:
    DC_NUMS = [0,1,2] # the VSENSE2 board cannot be a Clamp board -- initialize all three to include the guard 

clamps = [None]*4

for dc_num in DC_NUMS:
    if dc_num == dc_mapping['vsense']: # skip this with VSENSE2 
        clamp = Clamp(f, dc_num=dc_num, DAC_addr_pins=0b000, version=2)
    else:
        clamp = Clamp(f, dc_num=dc_num, version=2)
    print(f'Clamp {dc_num} Init'.center(35, '-'))
    clamp.init_board()
    clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
    clamps[dc_num] = clamp

feedback_resistors = [2.1]
capacitors = [47]
bath_res = [10, 100, 332, 1000] # Clamp.configs['ADG_RES_dict'].keys()
bath_res = [100]


# -------- configure the ADS8686
ads_voltage_range = 5  # need this for to_voltage later 
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range) 
ads.set_lpf(376)

'''
sys_connections['A2'].name  -> 'V1_1'

In [7]: sys_connections['A0'].name
Out[7]: 'P2_0'

In [8]: sys_connections['B0'].name
Out[8]: 'I_1'

In [9]: sys_connections['A1'].name
Out[9]: 'P1_0'
'''
'''
        self.parameters["ads_map"] = { # first key is daughter-card number, 2nd key is HDMI signal, tuple is ADS converter channel (letter) and number 
            0: {"CAL_ADC": ('A',0), "AMP_OUT": ('A',1)},
            1: {"CAL_ADC": ('B',0), "AMP_OUT": ('A',2)},
            2: {"CAL_ADC": ('B',1), "AMP_OUT": ('A',3)},
            3: {"CAL_ADC": ('A',4), "AMP_OUT": ('B',2)},
        }
'''

ads_sequencer_setup = [('0', '0'), ('1', '1'), ('2', '2')]
ads_sequencer_setup = [('0', '0'), ('1', '1'), ('3', '2')] # with the guard added, want AMP_OUT on socket 2 which is at A3; CAL_ADC of the Guard is digitized 

#ads_sequencer_setup = [('1', '0'), ('2', '0')] 

codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge() # 1 MSPS rate 
ads.set_fpga_mode()

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# in_amp = 1 # 05/02 step response was 2; 05/04 in_amp = 1
in_amp = 2 # 05/02 step response was 2; 05/04 in_amp = 1
dac_range = 5  # 5V full-scale range of the fast DACs 

# ------ Collect Data --------------
QUIET_DACS = False # if True use the host driven DAC mode to quiet all DACs to test noise
file_name = time.strftime("%Y%m%d-%H%M%S")
datastream_out_fname = 'clamptest1_quietdacs{}_rtia{}_ccomp{}_inamp{}.h5'
idx = 0

# fast DAC channels setup
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    if QUIET_DACS:
        daq.DAC[i].write(int(0x2000)) # midscale 
        daq.DAC[i].set_data_mux("host")
    else:
        daq.DAC[i].write(int(0x2000))
        daq.DAC[i].set_data_mux("DDR")
        daq.DAC[i].set_data_mux("DDR", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, dac_range)  # 5V 

# Quiet unused DACs (add 2024/09/12)
for i in [2,4,5]:
    daq.DAC[i].write(int(0x2000)) # midscale 
    daq.DAC[i].set_data_mux("host")

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.5)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(0.1)
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset
time.sleep(0.1)

# set all fast-DAC DDR data to midscale
set_cmd_cc(dc_nums=[0,1,2,3], cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)
# Set CMD and CC signals - only for the bath clamp
fc_cmd = None
step_len = 16384*8 # 2^17
first_pos_step = step_len/2*1/DAC_FS # in seconds 
cmd_val = 0x0200 # will be overriden by setting in mV below 
cc_val = 0

dc_configs = {}
clamp_fb_res = 60 # resistors and cap have changed so this does not correspond to typical bath clamp board  LJK was 3
clamp_res = 1000 # modified board: set to 10 MOhms -> 0 Ohms; 3.32 MOhms -> Open; 1 MOhms -> 50 Ohms (snubber)
clamp_cap = 47
# to digitize I1 use ADC_SEL = "CAL_SIG2"; P2_CAL_CTRL=1; DAC_SEL="noDrive"
for dc_num in [dc_mapping['clamp']]:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG2", 
        DAC_SEL="noDrive", # must not be drive_CAL2 
        CCOMP=clamp_cap,
        RF1=clamp_fb_res,  # feedback circuit
        ADG_RES=clamp_res,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=1,
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict

fb_res = 60  # this is disconnected and now in unity-gain! 60 is what configures the calibration to be at x1 
# Try with 5 different resistors
adg_r = 33
ccomp = 47
# Choose resistor; setup
for dc_num in [dc_mapping['bath']]:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG2",  # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize P1
        DAC_SEL="noDrive",
        CCOMP=ccomp,
        RF1=fb_res,  # feedback circuit
        ADG_RES=adg_r,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=0,
        gain=in_amp,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict

fb_res = 60  # this is disconnected and now in unity-gain! 
# Try with 5 different resistors
adg_r = 332
ccomp = 4700
for dc_num in [dc_mapping['guard']]:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG2",  # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize P1; must also close the corresponding relay. Note that CAL_SIG1 and P1_CAL_CTRL=1 caused oscillations.
        DAC_SEL="noDrive",
        CCOMP=ccomp,
        RF1=fb_res,  # feedback circuit
        ADG_RES=adg_r,
        PClamp_CTRL=1,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=0,
        gain=in_amp,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict

if VSENSE2:
    # declare the Vsense2 class as the operating vsense board
    vsense = Vsense2(fpga=f, DAC_addr_pins=0b001, dc_num=dc_mapping['vsense'], TCA_addr_pins=0b111) # I don't know why this needs to be 0b001 for DAC
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

ephys_sys = EphysSystem(system='Dagan_guard')
sys_connections = create_sys_connections(dc_configs, daq, ephys_sys, inamp_gain_correct=clamps[dc_mapping['bath']].correct_inamp_gain)

def ads_plot_zoom(ax, t_range=[3250,3300]):
    try:
        for ax_s in ax:
            ax_s.set_xlim(t_range)
            ax_s.grid('on')
    except:
        ax.set_xlim(t_range)
        ax.grid('on')   

plt.close('all')
first_time = True
cmd_mv = 50
cmd_val, actual_v = cmd_mv2dac(cmd_mv, sys_connections, dac_chan='D1')
set_cmd_cc(dc_nums=[dc_mapping['bath'], dc_mapping['guard']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=fc_cmd,
        step_len=step_len, cc_val=cc_val, cc_pickle_num=None)

ddr.repeat_setup() # Get data

def capture_data(idx=0, filename=None):
    ddr.repeat_setup() # Get data

    if filename is None:
        filename = file_name.format(idx) + '.h5'

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    chan_data_one_repeat = ddr.save_data(data_dir, filename, num_repeats=128,
                                        blk_multiples=200)  # blk multiples must be multiple of 10 
    # each block multiple is 256 bytes 

    # update system connections since the daughtercard configurations have changed
    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys, inamp_gain_correct=clamps[dc_mapping['bath']].correct_inamp_gain)
    # Plot using datastreams 
    datastreams, log_info = rawh5_to_datastreams(data_dir, filename, ddr.data_to_names, 
                                                 daq, sys_connections, outfile = None)
 
    return datastreams, log_info

"""
def update_plots(first_time, datastreams, lines1=None, lines2=None, figs=None, adg_r=100):

    # Two plots that are updated in realtime 
    # First plot is 2x2 
    if first_time:
        figs = []
        fig, ax = plt.subplots(2,2, figsize=(10,8))
        fig.canvas.manager.window.move(0,0)
        figs.append(fig)
        # AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane
        l1 = datastreams['P1'].plot(ax[0,0], {'marker':'.'})
        ax[0,0].set_ylim([-100e-3, 100e-3])
        # CAL ADC : observing electrode P2 (configured by CAL_SIG2)
        try:
            l2 = datastreams['P2'].plot(ax[0,1], {'marker':'.'})
            ax[1].set_title('P2')
        except:
            l2 = datastreams['CMD0'].plot(ax[0,1], {'marker':'.'})
            ax[0,1].set_ylim([-100e-3, 100e-3])

        l3 = datastreams['V1'].plot(ax[1,0], {'marker':'.'})
        l4 = datastreams['I'].plot(ax[1,1], {'marker':'.'})
        lines1 = [l1,l2,l3,l4]
    else:
        datastreams['P1'].update_lines(lines1[0][0])
        # CAL ADC : observing electrode P2 (configured by CAL_SIG2)
        try:
            datastreams['P2'].update_lines(lines1[1][0])
        except:
            datastreams['CMD0'].update_lines(lines1[1][0])
        datastreams['V1'].update_lines(lines1[2][0])
        datastreams['I'].update_lines(lines1[3][0])

    # second plot, membrane current and CMD 
    if first_time:
        fig, axs = plt.subplots(2,1,figsize=(10,8))
        fig.canvas.manager.window.move(600,0)
        figs.append(fig)
        lines2 = []
        for idx,ax in enumerate(axs):
            ax_right = ax.twinx()
            l1 = datastreams['CMD0'].plot(ax_right, {'linestyle':'--', 'color':'r', 'label': 'CMD'})
            l2 = datastreams['P1'].plot(ax_right, {'linestyle':'-', 'color': 'b', 'label': 'P1'})
            l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'decimate':[5,5], 'invert':-1})
            #l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'invert':-1})

            if idx==1:
                ax.set_ylim([-60e-6, 60e-6])
            else:
                ax.set_ylim([-60e-6, 60e-6])           
            lns = l1+l2+l3
            labs = [l.get_label() for l in lns]
            ax.legend(lns, labs, loc=2)
            lines2.append([l1,l2,l3])

            if idx==1: # zoom in at edge 
                ads_plot_zoom(ax, t_range=[first_pos_step*1e6-50, first_pos_step*1e6+200])
                ads_plot_zoom(ax_right, t_range=[first_pos_step*1e6-50, first_pos_step*1e6+200])
            else: 
                ads_plot_zoom(ax, t_range=[first_pos_step*1e6-300, first_pos_step*1e6*2+300])
                ads_plot_zoom(ax_right, t_range=[first_pos_step*1e6-300, first_pos_step*1e6*2+300])

    else:
        for l2 in lines2:
            datastreams['CMD0'].update_lines(l2[0][0]) # TODO: why is this a list?
            datastreams['P1'].update_lines(l2[1][0])
            datastreams['Im'].update_lines(l2[2][0], {'decimate':[10,10], 'invert':-1})
        
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

    return first_time, lines1, lines2, figs
"""
def update_plots(first_time, datastreams, lines1=None, lines2=None, figs=None, adg_r=100):

    # Two plots that are updated in realtime 
    # First plot is 2x2 
    if first_time:
        figs = []
        fig, ax = plt.subplots(2,2, figsize=(10,8))
        fig.canvas.manager.window.move(0,0)
        figs.append(fig)
        lines1 = PlotManager(datastreams)
        # AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane
        # l1 = datastreams['P1'].plot(ax[0,0], {'marker':'.'})
        lines1.positional_plot_with_datastream(type='P1', ax=ax, row=0, col=0, aes_key={'marker' : '.'})
        # ax[0,0].set_ylim([-100e-3, 100e-3])
        lines1.set_ax_properties(type='P1', ylimit=[-100e-3, 100e-3])
        # CAL ADC : observing electrode P2 (configured by CAL_SIG2)
        try:
            # l2 = datastreams['P2'].plot(ax[0,1], {'marker':'.'})
            lines1.positional_plot_with_datastream(type='P2', ax=ax, row=0, col=1, aes_key={'marker':'.'})
            # ax[1].set_title('P2')
            lines1.set_ax_properties(ax=ax, row=1, title='P2')
            # wipe out the 'CMD0' from the map
            print("plotted from P2")
            lines1.pop('CMD0', None)
        except:
            # l2 = datastreams['CMD0'].plot(ax[0,1], {'marker':'.'})
            lines1.positional_plot_with_datastream(type='CMD0', ax=ax, row=0, col=1, aes_key={'marker':'.'})
            # ax[0,1].set_ylim([-100e-3, 100e-3])
            lines1.set_ax_properties(type='CMD0', ylimit=[-100e-3, 100e-3])
            # wipe out the 'P2' from the map
            print("plotted from CMD0")
            lines1.pop('P2', None)

        # l3 = datastreams['V1'].plot(ax[1,0], {'marker':'.'})
        lines1.positional_plot_with_datastream(type='V1', ax=ax, row=1, col=0, aes_key={'marker':'.'})
        # l4 = datastreams['I'].plot(ax[1,1], {'marker':'.'})
        lines1.positional_plot_with_datastream(type='I', ax=ax, row=1, col=1, aes_key={'marker':'.'})
    else:
        # reset the datastream since in the experiment we reassigned the datastreams object
        lines1.reset_datastreams(datastreams)
        # datastreams['P1'].update_lines(lines1[0][0])
        # CAL ADC : observing electrode P2 (configured by CAL_SIG2)
        # try:
        #     datastreams['P2'].update_lines(lines1[1][0])
        # except:
        #     datastreams['CMD0'].update_lines(lines1[1][0])
        # datastreams['V1'].update_lines(lines1[2][0])
        # datastreams['I'].update_lines(lines1[3][0])
        lines1.update_lines('P1')
        # This complex handling scheme happens because we try to plot two things on the same ax, which is a very bad practice to 
        # differentiate P2 from CMD0 and to know which parameter is being measured at real time
        second_key = 'P2' if 'P2' in lines1 else 'CMD0'
        try:
            lines1.update_lines(second_key, custom_type='P2')
        except:
            lines1.update_lines(second_key, custom_type='CMD0')
        lines1.update_lines('V1')
        lines1.update_lines('I')

    # second plot, membrane current and CMD 
    if first_time:
        fig, axs = plt.subplots(2,1,figsize=(10,8))
        fig.canvas.manager.window.move(600,0)
        figs.append(fig)
        lines2 = []
        for idx,ax in enumerate(axs):
            ax_right = ax.twinx()
            component_plot = PlotManager(datastreams)
            # l1 = datastreams['CMD0'].plot(ax_right, {'linestyle':'--', 'color':'r', 'label': 'CMD'})
            component_plot.positional_plot_with_datastream('CMD0', ax_right, aes_key={'linestyle':'--', 'color':'r', 'label': 'CMD'})
            # l2 = datastreams['P1'].plot(ax_right, {'linestyle':'-', 'color': 'b', 'label': 'P1'})
            component_plot.positional_plot_with_datastream('P1', ax_right, aes_key={'linestyle':'-', 'color': 'b', 'label': 'P1'})
            # l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'decimate':[5,5], 'invert':-1})
            component_plot.positional_plot_with_datastream('Im', ax, aes_key={'marker':'.', 'color': 'k', 'label': 'Im', 'decimate':[5,5], 'invert':-1})
            #l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'invert':-1})

            # if idx==1:
            #     ax.set_ylim([-60e-6, 60e-6])
            # else:
            #     ax.set_ylim([-60e-6, 60e-6])
            component_plot.set_ax_properties(ax=ax, ylimit=[-60e-6, 60e-6])
            # lns = l1+l2+l3
            lns = []
            for type in component_plot:
                lns += component_plot.get_type_line_obj(type)
            
            labs = [l.get_label() for l in lns]
            ax.legend(lns, labs, loc=2)
            # lines2.append([l1,l2,l3])
            lines2.append(component_plot)

            if idx==1: # zoom in at edge 
                ads_plot_zoom(ax, t_range=[first_pos_step*1e6-50, first_pos_step*1e6+200])
                ads_plot_zoom(ax_right, t_range=[first_pos_step*1e6-50, first_pos_step*1e6+200])
            else: 
                ads_plot_zoom(ax, t_range=[first_pos_step*1e6-300, first_pos_step*1e6*2+300])
                ads_plot_zoom(ax_right, t_range=[first_pos_step*1e6-300, first_pos_step*1e6*2+300])

    else:
        for l2 in lines2:
            # Reset the datastreams
            l2.reset_datastreams(datastreams)
            # datastreams['CMD0'].update_lines(l2[0][0]) # TODO: why is this a list?
            # datastreams['P1'].update_lines(l2[1][0])
            # datastreams['Im'].update_lines(l2[2][0], {'decimate':[10,10], 'invert':-1})
            for type in l2:
                if type != 'Im':
                    l2.update_lines(type)
                else:
                    l2.update_lines(type, custom_keys={'decimate':[10,10], 'invert':-1})
        
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

    return first_time, lines1, lines2, figs
# """

datastreams, log_info = capture_data(idx=0)
first_time, lines1, lines2, figs = update_plots(first_time, datastreams)
# run twice to remove initial transient 
idx = 1
datastreams = ds_add_log(datastreams)
datastreams.to_h5(data_dir, f"initial_startup_{adg_r}rf_{ccomp}ccomp.h5", log_info)

# measure CMD and CC impulse 
CC_IMPULSE = False 

for adg_r, ccomp in ([(100, 47)]):
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
        clamps[0].configure_clamp(**dc_configs[0])

        for test in ['CMD', 'CC']:
            if test=='CMD':
                cmd_val = cmd_val_set
                cc_val = 0
            elif test=='CC':
                cmd_val = 0
                cc_val = cc_val_set
            set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=fc_cmd,
                step_len=step_len, cc_val=cc_val, cc_pickle_num=None)        
            time.sleep(0.2)
            
            datastreams, log_info = capture_data(idx=idx)
            update_plots(first_time, datastreams, lines1, lines2, figs, adg_r)
            datastreams = ds_add_log(datastreams)

            if test == 'CMD':
                datastreams.to_h5(data_dir, "cmd_impulse.h5", log_info)
                # copy to include the filename so we don't overwrite 
                shutil.copy2(os.path.join(data_dir, "cmd_impulse.h5"), os.path.join(data_dir, f"cmd_impulse_{filename_imp}.h5"))
            else:
                datastreams.to_h5(data_dir, "cc_impulse.h5", log_info)
                shutil.copy2(os.path.join(data_dir, "cc_impulse.h5"), os.path.join(data_dir, f"cc_impulse_{filename_imp}.h5"))

    # measure cc cancellation 
    CC_CANCEL = False
    method = 'spline'

    if CC_CANCEL:
        # read impulse files into datastreams
        ds = {}
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
            set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=cmd_val, cc_scale=None, cc_delay=0, fc=None,
                    step_len=16384*8, cc_val=cc_val, cc_pickle_num=None)
        
        if 'spline' in method:
            cmd_val = cmd_val_set
            set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=cmd_val, cc_scale=None, cc_delay=0, fc=None,
                    step_len=16384*8, cc_val=cc_val, cc_pickle_num=None)
            cc_wave, configs, results = infer_ccwave_spline(DEBUG_PLOTS=True, run_date = '20240417', 
                            run_time = '163357', rtia=adg_r, ccomp=ccomp)
            cc_wave = decimate(cc_wave, q=2)
            norm_factor = cc_wave[-1] # so that we can concatenate rising and falling edges we need the the left most value to equal 0 and the right most to equal 1
            cc_wave = cc_wave/norm_factor
            cmd_wave = ddr.data_arrays[dc_mapping['bath']+1]
            # restore the amplitude below. Multiply by x2 due to difference in amplitude and pk-pk. FS due to discrete convolution "missing" the time step.  
            cc_wave_full = cat_cc_wave(cmd_wave, cc_wave, amplitude=-(cmd_val*2)*norm_factor*FS, midpt=8192)
            ddr.data_arrays[dc_mapping['bath']] = cc_wave_full.astype(np.uint16)

        # show the waveforms used 
        fig,ax = plt.subplots()
        ax.plot(ddr.data_arrays[dc_mapping['bath']][0:2**19], label='CC')
        ax.plot(ddr.data_arrays[dc_mapping['bath'] + 1][0:2**19], 'tab:orange', label='CMD')
        fig.suptitle('Cancelation waveforms')
        ax.legend()

        # write channels to the DDR
        write_ddr()

        idx = 2
        datastreams, log_info = capture_data(idx=2)
        update_plots(first_time, datastreams, lines1, lines2, figs, adg_r)
        datastreams = ds_add_log(datastreams)
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
            ddr.data_arrays[dc_mapping['bath'] + 1] = 8192 # zero CMD 
            # write channels to the DDR
            write_ddr()
            time.sleep(0.1)
            idx = 2
            datastreams, log_info = capture_data(idx=2)
            update_plots(first_time, datastreams, lines1, lines2, figs, adg_r)
            datastreams = ds_add_log(datastreams)
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

# large parameter sweep 
if 1: 
    OSCOPE = False
    if OSCOPE:
        scope_data = {} 
        components = ['CC', 'RTIA', 'CLAMP_TIA', 'CLAMP_RF']
        scope_meas = ['OVER', 'RIS']
        for sm in scope_meas:
            scope_data[sm] = np.array([])
        for c in components:
            scope_data[c] = np.array([])
        osc.set('run_acq')

    # extensive sweep
    adg_r_arr = [10, 33, 100, 332] # JOB: fft through all of these 
    ccomp_arr = [47, 200, 247, 1000, 1247, 4700]

    ccomp_arr = [47, 247, 1000, 4700]
    ccomp_arr = [47, 4700]
    adg_r_arr = [33, 100, 332, 1000]

    # ccomp_arr = [None, 47, 247, 1000, 1247, 4700]
    # ccomp_arr = [4700]
    # adg_r_arr = [100]
    # adg_r_arr = [100, 100, 100, 100, 100, 100]

    # at a DAC gain of x5 limit will be about 500 mV due to the x1/11 at the clamp board 
    # mv_val_arr = np.concatenate( ([0,5,10,15,20,25,30,35,40], [50,60,70,80,90,100], [120, 140, 160, 180], [200, 240, 280, 320, 360, 400]) )
    mv_val_arr = np.concatenate( ([0,5], [50,60]) )
    # short cmd step -- for noise investigations
    # mv_val_arr = np.concatenate( ([0],[40]) )

    UPDATE_CMD = True

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
                clamps[0].configure_clamp(**dc_configs[0])
                if UPDATE_CMD: # 9/6/2024, add the guard to the cmd update. 
                    set_cmd_cc(dc_nums=[dc_mapping['bath'], dc_mapping['guard']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=fc_cmd,
                        step_len=step_len, cc_val=None, cc_pickle_num=None)
                    time.sleep(0.2) # extend for noise analysis
                
                filename = 'step_rtia{}_ccomp{}_cmd{}.h5'.format(adg_r, ccomp, cmd_val)
                datastreams, log_info = capture_data(idx=1, filename=filename)
                update_plots(first_time, datastreams, lines1, lines2, figs, adg_r)

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

                TO_CLAMPFIT = False # doesn't work with 3 sequences in the ADS8686 
                if TO_CLAMPFIT:
                    datastreams.to_clampfit(data_dir, 'step_rtia{}_ccomp{}_cmd{}.abf'.format(adg_r, ccomp, cmd_val),
                                            names_pclamp = ['Im', 'CMD0', 'V1', 'P1'],
                                            dac_len=len(datastreams['CMD0'].data), dac_sample_rate=2.5e6, sweeps=1)

                # add log info to datastreams -- any dictionary is ok  
                datastreams = ds_add_log(datastreams)

                datastreams.to_h5(data_dir, filename, log_info)

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

    PLT_IM_EST = False 
    if PLT_IM_EST:
        # estimate Im 
        Cm = 33e-9
        fig, ax = plt.subplots()
        fig.suptitle('Overlay Meas. Im and Im estimate')
        datastreams['Im'].plot(ax, {'marker':'.', 'label': 'Meas. Im'})
        t = datastreams['P1'].create_time()
        dt = t[1] - t[0]
        p1_diff = np.diff(datastreams['P1'].data)/dt
        #ax.plot(t[:-1]*1e6, -Cm*p1_diff, label='Im estimate via p1')
        ax.legend()

    # test writing and reading datastream h5
    TST_DATASTREAM_RW = False
    if TST_DATASTREAM_RW:
        datastreams2 = h5_to_datastreams(data_dir, 'test.h5')
        # this datastreams has the log info but as a dictionary, not as Python classes
        # if the original objects are needed could use these methods https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object
        for n in datastreams:
            assert (datastreams[n].data == datastreams2[n].data).all(), f'Datastream data with key {n} after writing and reading from file are not equal!'

    print('-'*100)
    for sig in ['I', 'P1', 'CMD0']:
        sig_name = sig 
        if sig_name == 'I':
            sig_name = 'Vm'
        try:
            si = datastreams[sig].stepinfo_range([first_pos_step-20e-6, first_pos_step+170e-6])
            print(f'{sig} step info: {si}')
            print('-'*100)
        except:
            print(f'Step info failed for signal: {sig}')

    if 0:
        # sweep the gain of the voltage clamp; to check on the oscilloscope 
        for rf in Clamp.configs['RF1_dict']:
            dc_configs[1]['RF1'] = rf
            clamps[1].configure_clamp(**dc_configs[1])
            print(f'RF = {rf}')
            input('next?')

    dc_configs[0]['ADG_RES'] = 100
    dc_configs[0]['CCOMP'] = 47
    clamps[0].configure_clamp(**dc_configs[0])
    print(f'Configure at known good config to measure on oscope')
