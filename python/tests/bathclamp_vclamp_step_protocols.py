"""
The system uses three Daughtercards with:
 1) the bath clamp - has a non-zero CMD voltage measures Im 
 2) the voltage clamp I source  zero CMD voltage, goal is to hold capacitor plate at ground 
 3) the voltage clamp - sensing board 

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
import matlab.engine 

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
from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp
from calibration.electrodes import EphysSystem
from observer import Observer
from filters.filter_tools import butter_lowpass_filter

from ephys.core import Sequence, Protocol

protocol = Protocol.create_from_csv(filepath=r'ephys/protocol.csv', num_sweeps=10)
protocol.preview()
first_step_time_us = protocol.sweeps[0].epochs[0].first_duration*1e3 # in milliseconds *1e3 to microseconds 

def make_cmd_cc(cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, 
                fc=4.8e3, step_len=8000,
                cc_val=None, cc_pickle_num=None):
    """Return the CMD and CC signals determined by the parameters.
    This does not write to the DDR
    
    Parameters
    ----------
    
    Returns
    -------
    np.ndarray, np.ndarray : the CMD signal data, the CC signal data.
    """
    dac_offset = 0x2000

    cmd_signal = ddr.make_step(
        low=dac_offset - int(cmd_val), high=dac_offset + int(cmd_val), length=step_len)  # 1.6 ms between edges

    # TODO: ensure cutoff frequency is not so low that it causes instability
    if fc is not None:
        cmd_signal = butter_lowpass_filter(cmd_signal, cutoff=fc, fs=2.5e6, order=1)

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

def write_ddr(ddr):
    # write channels to the DDR
    ddr.write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()

    return block_pipe_return, speed_MBs

def set_cmd_cc(dc_nums, cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None, WRITE_DDR=True):
    """Write the CMD and CC signals to the DDR for the specified daughtercards.
    This writes to the DDR via USB 

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
    
    if WRITE_DDR:
        write_ddr(ddr)

FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6
dc_mapping = {'bath': 0, 'clamp': 1, 'vsense': 3} 
DC_NUMS = [0, 1, 3]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3

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
#ads_sequencer_setup = [('0', '0'), ('1', '1'), ('2', '2')]
ads_sequencer_setup = [('1', '0'), ('2', '0')] # with Vm jumpered to U4 relay on the clamp board so it goes to CAL_ADC

codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge() # 1 MSPS rate 
ads.set_fpga_mode()

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

dac_range = 5 # +/-5V 
dac_offset = 0x2000  # TODO - change to the holding voltage

# fast DAC channels setup
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write(int(dac_offset))
    daq.DAC[i].set_data_mux("DDR")
    #daq.DAC[i].set_data_mux("DDR_norepeat", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name
    daq.DAC[i].set_data_mux("DDR", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, dac_range)  # 5V 

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.5) # TODO - reduce sleep time
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(2) # TODO - reduce sleep time
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset
time.sleep(1) # TODO - reduce sleep time

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S") + '_{}'
idx = 0

# set all fast-DAC DDR data to midscale
set_cmd_cc(dc_nums=[0,1,2,3], cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None, WRITE_DDR=False)

# Set CMD and CC signals - only for the bath clamp
sequence_repeat=int(np.floor(len(daq.ddr.data_arrays[0])/len(protocol)))
sequence = Sequence(protocols=[protocol]*sequence_repeat)
# sequence.to_ddr(0, daq, inject_current=False, low_scaling_factor=0, cutoff=-10, high_scaling_factor=1/7)
# pipe_return, write_speed = write_ddr(daq.ddr)

fc_cmd = None
set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=0x0200, cc_scale=0, cc_delay=0, fc=fc_cmd,
        step_len=16384, cc_val=None, cc_pickle_num=None, WRITE_DDR=False)

sequence.to_ddr(0, daq, inject_current=False, low_scaling_factor=0, cutoff=-10, high_scaling_factor=1/7)
# daq.ddr.data_arrays[1] = daq.ddr.data_arrays[1] + 3000
pipe_return, write_speed = write_ddr(daq.ddr)

if 1:
    dc_configs = {}
    clamp_fb_res = 60 # resistors and cap have changed so this does not correspond to typical bath clamp board  LJK was 3
    clamp_res = 10000 # should be zero with modified board when set to 10 MOhms 
    clamp_cap = 47
    for dc_num in [dc_mapping['clamp']]:
        log_info, config_dict = clamps[dc_num].configure_clamp(
            ADC_SEL="CAL_SIG1", # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize jumpered Vm 
            DAC_SEL="noDrive", # must not be drive_CAL2 
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

    cap = 47
    fb_res = 2.1
    res = 100
    # Choose resistor; setup
    for dc_num in [dc_mapping['bath']]:
        log_info, config_dict = clamps[dc_num].configure_clamp(
            ADC_SEL="CAL_SIG1",  # required to digitize P2 
            DAC_SEL="noDrive",
            CCOMP=cap,
            RF1=fb_res,  # feedback circuit
            ADG_RES=res,
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

    ephys_sys = EphysSystem()
    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)

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

    # update system connections since the daughtercard configurations have changed
    sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)
    # TODO - switch to DDR here 
    ddr.repeat_setup() # prepare to Get data -- clear FIFOs and resets the address of the MIG interface 

    def capture_data(idx=0, num_repeats=8, blk_multiples=40, RESTART=False):

        if RESTART:
            ddr.repeat_setup() # Get data

        filename = file_name.format(idx) + '.h5'

        # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
        chan_data_one_repeat = ddr.save_data(data_dir, filename, num_repeats=num_repeats,
                                             blk_multiples=blk_multiples)  # blk multiples must be multiple of 10 
        # each block multiple is 256 bytes 

        # update system connections since the daughtercard configurations have changed
        sys_connections = create_sys_connections(dc_configs, daq, ephys_sys)
        # Plot using datastreams 
        datastreams, log_info = rawh5_to_datastreams(data_dir, filename, ddr.data_to_names, 
                                                    daq, sys_connections, outfile = None)
    
        return datastreams, log_info
        
    def update_plots(first_time, datastreams, lines1=None, lines2=None, figs=None, adg_r=100):

        # Two plots that can be updated in realtime 
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
                l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'decimate':[10,10], 'invert':-1})
                #l3 = datastreams['Im'].plot(ax, {'marker':'.', 'color': 'k', 'label': 'Im', 'invert':-1})

                if idx==1:
                    ax.set_ylim([-60e-6, 60e-6])
                else:
                    ax.set_ylim([-60e-6, 60e-6])           
                lns = l1+l2+l3
                labs = [l.get_label() for l in lns]
                ax.legend(lns, labs, loc=2)
                lines2.append([l1,l2,l3])

                if idx==1:
                    ads_plot_zoom(ax, t_range=[first_step_time_us-100, first_step_time_us + 200])
                    ads_plot_zoom(ax_right, t_range=[first_step_time_us-100, first_step_time_us + 200])
                else:
                    ads_plot_zoom(ax, t_range=[first_step_time_us-100, first_step_time_us + 4000])
                    ads_plot_zoom(ax_right, t_range=[first_step_time_us-100, first_step_time_us + 4000])

        else:
            for l2 in lines2:
                datastreams['CMD0'].update_lines(l2[0][0]) # TODO: why is this a list?
                datastreams['P1'].update_lines(l2[1][0])
                datastreams['Im'].update_lines(l2[2][0], {'decimate':[10,10], 'invert':-1})
                #datastreams['Im'].update_lines(l2[2][0], {'fc':500e3, 'invert':-1})
                #datastreams['Im'].update_lines(l2[2][0], {'invert':-1})
            
            im_data = datastreams['Im'].data
            t = datastreams['Im'].create_time()
            fc = 500e3 #5e3
            im_data_filt = butter_lowpass_filter(im_data, cutoff=fc, fs=1/(t[1]-t[0]), order=5)
            idx = (t > 4500e-6) & (t < 5500e-6)
            im_noise_wb = np.std(im_data[idx])
            im_noise_filt = np.std(im_data_filt[idx])
            print(f'Im gain of {adg_r} kOhm = {(adg_r*1e3)*1e3*1e-9} mV/nA. Current noise of {im_noise_wb*1e9} nA full-bw; {im_noise_filt*1e9} nA {fc} bw')

        for fig in figs:
            fig.canvas.draw()
            fig.canvas.flush_events()
        
        first_time = False

        return first_time, lines1, lines2, figs

    # first sweep
    # TODO: why 40 and 100? 
    datastreams, log_info = capture_data(idx=0, num_repeats=40, blk_multiples=100, RESTART=False)
    first_time, lines1, lines2, figs = update_plots(first_time, datastreams)

    for i in range(len(protocol.sweeps) - 1):
        datastreams2, log_info = capture_data(idx=i+1, num_repeats=40, blk_multiples=100, RESTART=False)
        update_plots(first_time, datastreams2, lines1, lines2, figs, res)
        datastreams.append(datastreams2)

    TO_CLAMPFIT = True
    if TO_CLAMPFIT: # TODO 
        datastreams.to_clampfit(data_dir, 'protocol_tests_rtia{}_ccomp{}.abf'.format(res, cap),
                        names_pclamp = ['Im', 'CMD0', 'V1', 'P1'],
                        dac_len=len(datastreams['CMD0'].data), dac_sample_rate=2.5e6, sweeps=len(protocol.sweeps))

        # sys.path.append('C:\\Users\\koer2434\\Documents\\covg\\my_pyabf\\pyABF\\src\\')
        # from pyabf.abfWriter import writeABF1 
        # from pyabf.tools.covg import interleave_np



        # t = ds_equal['Im'].create_time()

        # names_pclamp = ['Im', 'CMD0', 'V1', 'P1']
        # # if the current is in Amps the 16-bit precision makes it all zero 
        # im = np.reshape(ds_equal['Im'].data, (1,-1))
        # cmd = np.reshape(ds_equal['CMD0'].data, (1,-1))
        # v1 = np.reshape(ds_equal['V1'].data, (1,-1))
        # p1 = np.reshape(ds_equal['P1'].data, (1,-1))

        # x_write = interleave_np([im, cmd, v1, p1])
        # x_write = np.reshape(x_write, (len(protocol.sweeps), -1))
        # num_channels = len(names_pclamp)
        # # the sample-rate is assumed to be divided among all ADC channels
        # # so if we are sampling in parallel increase the sample rate by the number of channels
        # writeABF1(x_write, os.path.join(data_dir, 'test_step.abf'), 1/(t[1]-t[0])*num_channels, 
        #        units=['A', 'V', 'V', 'V'], nADCNumChannels=num_channels, FLOAT=True, names_input = names_pclamp)

    ds_equal = datastreams.equalize_sampling(names=['Im', 'CMD0', 'V1', 'P1'])
    dac_sample_rate = 2.5e6
    downsample_factor = int(dac_sample_rate/ds_equal['CMD0'].sample_rate)        
    ds_equal.crop(int(len(protocol)/downsample_factor))
    # Plot various sweeps 
    fig,ax = plt.subplots(2,1)
    sweeps = ds_equal.to_sweeps(len(protocol.sweeps))
    
    for sw in sweeps:
        sw['Im'].plot(ax[0])
        sw['CMD0'].plot(ax[1])

    # add log info to datastreams -- any dictionary is ok  
    datastreams.add_log_info(ephys_sys.__dict__)  # all properties of ephys_sys 
    datastreams.add_log_info({'dc_configs': dc_configs})
    print(datastreams.__dict__)
    datastreams.to_h5(data_dir, 'datastreams_output.h5', log_info)