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
import matlab.engine 
from control.matlab import stepinfo

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
from observer import Observer

eng = matlab.engine.start_matlab()
eng.addpath('..\\Matlab\\control_system\\observer\\full_closed_loop\\')

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
sleep(0.4)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset
f.send_trig(eps["GP"]["FILTER_DATA_RESET"])  # data reset
f.send_trig(eps["GP"]["FILTER_COEFF_RESET"])  # coeff reset
f.send_trig(eps["OBSV"]["RESET_DATA"])  # data reset

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
ads_sequencer_setup = [('1', '0')] # with Vm jumpered to U4 relay on the clamp board so it goes to CAL_ADC

ads_b_chan = 0
codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge(clk_div=200) # 1 MSPS rate (do not use default value which is 200 ksps)
ads.set_fpga_mode()


# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.1)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
time.sleep(0.1)
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S") + '_{}' # to append index 
idx = 0

# Set CMD and CC signals
set_cmd_cc(dc_nums=DC_NUMS, cmd_val=0x0200, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)

bath_res = 100 # in kOhm
c_comp = 47 # in pF
dc_configs = {}
for dc_num in DC_NUMS:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1", # required for comparative Vm measurement 
        DAC_SEL="drive_CAL2",
        CCOMP=c_comp,
        RF1=2.1,  # feedback circuit
        ADG_RES=bath_res,
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
1: 0x5080adfd,
2: 0xb080adfd,
9: 0x40000000,
3: 0x00000000,
4: 0xc0000000, # a1, keep this at -1 
5: 0x00000000,
8: 0x7fffffff,
9: 0x40000000, # gain 
10: 0x00000000,
11: 0x00000000,
12: 0x00000000,
13: 0x00000000,
7: 0x7fffffff,
15: 0x0000_089a} # this coefficient is not used but must write something to ensure coefficient writing works.

# set observer data input muxes
obsv = Observer(f)
obsv.set_im_data_mux("ad7961_ch0")
obsv.set_vcmd_data_mux("ad5453_ch1")
obsv.set_vp1_data_mux("ads8686_chA")
obsv.set_rdy_data_mux("sync_im")

dac_range = 5
RF = bath_res*1.0e3

in_amp = 1
diff_buf = 499/(120+1500) # correct, refering to signal_chain.py 
dn_per_amp = (2**15/4.096)*(RF*in_amp*diff_buf) # correct 
Im_scale = dn_per_amp  # DN/Amp 

ads_full_scale = 10
dn_per_volt = (2**16/ads_full_scale) # correct
VP1_scale = dn_per_volt*11.0*1.7

dac_range = 5
dac_scale = 2**14*4.0/(10/(dac_range*2)) # DN/Volt 

obsv_scale = dac_scale
total_scale = 1.0/(dac_range/5)  # this scaling gets the steady-state value in closed-loop to match the steady-state value in open-loop

Ldp, Bdp, Adp = eng.observer_coeff_total(400e-9, RF, c_comp*1e-12, Im_scale, VP1_scale, dac_scale, total_scale, nargout=3)

# observer coeffs
obsv_coeff = {}
max_bit_width = 0xFFFFFFFF
obsv_coeff[0] = Ldp[0][0] & max_bit_width
obsv_coeff[1] = Ldp[1][0] & max_bit_width
obsv_coeff[2] = Ldp[0][1] & max_bit_width
obsv_coeff[3] = Ldp[1][1] & max_bit_width

obsv_coeff[4] = Adp[0][0] & max_bit_width
obsv_coeff[5] = Adp[1][0] & max_bit_width
obsv_coeff[6] = Adp[0][1] & max_bit_width
obsv_coeff[7] = Adp[1][1] & max_bit_width

obsv_coeff[8] = Bdp[0][0] & max_bit_width
obsv_coeff[9] = Bdp[1][0] & max_bit_width

obsv.change_observer_coeff(obsv_coeff)
obsv.write_observer_coeffs()

for i in [0,2,3,4,5]:
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="set")
    daq.DAC[i].write(int(0))

for pi_gain in [5,5,5,5]:
    [b0_h, b1_h, a1_h] = eng.pi_coeff_total(pi_gain, 5e3, 400e-9, False, nargout=3)

    max_bit_width = 0xFFFFFFFF
    PI_coeff[1] = b0_h & max_bit_width
    PI_coeff[2] = b1_h & max_bit_width
    PI_coeff[9] = a1_h & max_bit_width

    # TODO: note that only 2 DACs are configured 
    for i in [1]:
        daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
        daq.DAC[i].set_spi_sclk_divide()
        daq.DAC[i].filter_select(operation="set")
        daq.DAC[i].write(int(0))
        daq.DAC[i].set_data_mux("host") 
        daq.DAC[i].set_data_mux("host", filter_data=True) 
        f.send_trig(eps["GP"]["FILTER_DATA_RESET"])  # data reset
        daq.DAC[i].filter_sum("clear")
        daq.DAC[i].filter_downsample("clear")
        daq.DAC[i].change_filter_coeff(target="generated", value=PI_coeff)
        #daq.DAC[i].change_filter_coeff(target="passthru")
        daq.DAC[i].write_filter_coeffs()
        daq.set_dac_gain((i-1), dac_range)  # 5V to see easier on oscilloscope
        daq.DAC[i].set_data_mux("DDR") 
        daq.DAC[i].set_data_mux("DDR_norepeat", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name

    f.send_trig(eps["OBSV"]["RESET_DATA"])  # data reset

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
    datastreams['Im'].plot(ax)

    fig,ax=plt.subplots()
    datastreams['Itop'].plot(ax)

    fig, ax = plt.subplots(2,1)
    fig.suptitle('ADS data')
    # AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane

    datastreams['P1'].plot(ax[0], {'marker':'.'})
    datastreams['I'].plot(ax[1], {'marker':'.'})
    ax[1].set_ylabel('Vm measured [V]')
    for axi in ax:
        axi.set_xlim([3200, 3400])

    # plot dac channel 4 data
    fig,ax=plt.subplots(3,1)
    datastreams['OBSV'].plot(ax[0])
    datastreams['OBSV_CH1'].plot(ax[1])
    datastreams['PI_ERR'].plot(ax[2])
    for axi in ax:
        axi.set_xlim([3200, 3400])

    # subplot of Observer Vm and measured Vm
    fig,ax=plt.subplots(3,1)
    fig.suptitle('Observer Vm vs ADS8686')
    # Observer - stored in DDR at 1 MSPS -- dac_data[4] is observer output 0, dac_data[5] is observer output 1, dac_data[6] is obs. output 0 shifted by 400 ns
    datastreams['OBSV'].plot(ax[0], {'marker':'.', 'label': 'Obsv.'})
    datastreams['PI_ERR'].plot(ax[0], {'marker':'.', 'label': 'PI_ERR.'})
    ax[0].legend()
    datastreams['I'].plot(ax[1], {'marker':'.', 'label': 'Vm Meas.'})
    datastreams['P1'].plot(ax[1], {'marker':'*', 'label': 'P1'})
    ax[1].legend()
    datastreams['CMD0'].plot(ax[2])

    ax[1].set_ylabel('Vm measured [V]')
    for axi in ax:
        axi.set_xlim([3250, 3400])

    def ads_plot_zoom(ax):
        for ax_s in ax:
            ax_s.set_xlim([3250, 3330])
            ax_s.grid('on')


    def stepinfo_range(ds, time_range):
        t = ds.create_time()
        idx = (t>=time_range[0]) & (t<=time_range[1])
        y = ds.data[idx]
        t = t[idx]

        si = stepinfo(y, t)

        return si

    t_step = 3.277e-3
    print('-'*100)
    for sig in ['I', 'OBSV', 'P1', 'CMD0']:
        sig_name = sig 
        if sig_name == 'I':
            sig_name = 'Vm'
        si = stepinfo_range(datastreams[sig], [t_step-0.02e-3, t_step+170e-6])
        print(f'{sig} step info: {si}')
        print('-'*100)

    for oc in obsv_coeff:
        print(f'{oc}: {hex(obsv_coeff[oc])}')