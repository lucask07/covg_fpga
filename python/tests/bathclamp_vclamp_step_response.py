"""This script attempts to replicate Figure 4 on the biophysical poster. This
consists of measuring the membrane current (Im) with the AD7961 after
supplying a step voltage of 0-50mV by the AD5453.
The system uses two Daughtercards with:
 1) the bath clamp - has a non-zero CMD voltage measures Im 
 2) the voltage clamp - zero CMD voltage, goal is to hold capacitor plate at ground 

Sept 2022

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

sys.path.append('C:\\Users\\koer2434\\Documents\\covg\\my_pyabf\\pyABF\\src\\') # need to use pyABF fork
from pyabf.abfWriter import writeABF1 
from pyabf.tools.covg import interleave_np

from instrbuilder.instrument_opening import open_by_name 
osc = open_by_name('msox_scope')

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
                                               length=step_len) 
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
        cmd_ch = dc_num * 2 + 1 # TODO: replace with daq.parameters['fast_dac_map']
        cc_ch = dc_num * 2
        ddr.data_arrays[cmd_ch], ddr.data_arrays[cc_ch] = make_cmd_cc(cmd_val=cmd_val, cc_scale=cc_scale, cc_delay=cc_delay, fc=fc, step_len=step_len, cc_val=cc_val, cc_pickle_num=cc_pickle_num)
    
    # write channels to the DDR
    ddr.write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr.write_finish()

DAC_FS = 2.5e6
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

feedback_resistors = [2.1]
capacitors = [47]
bath_res = [10, 100, 332, 1000] # Clamp.configs['ADG_RES_dict'].keys()

# Try with different capacitors
if feedback_resistors is None:
    feedback_resistors = [x for x in Clamp.configs['RF1_dict'].keys() if type(x) == int or type(x) == float] # RF1 Resistor values in kilo-ohms for Offset Adjust amplifier
    feedback_resistors.sort()
if capacitors is None:
    capacitors = [x for x in Clamp.configs['CCOMP_dict'] if type(x) == int or type(x) == np.int32]  # CCOMP Capacitor values in pF
    capacitors.sort()

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

# set observer data input muxes
obsv = Observer(f)
obsv.set_im_data_mux("ad7961_ch0")
obsv.set_vcmd_data_mux("ad5453_ch1")
obsv.set_vp1_data_mux("ads8686_chA")
obsv.set_rdy_data_mux("sync_im")

RF = bath_res[0]*1.0e3
in_amp = 10
diff_buf = 499/(120+1500) # correct, refering to signal_chain.py 
dn_per_amp = (2**15/4.096)*(RF*in_amp*diff_buf) # correct 
Im_scale = dn_per_amp/2  # DN/Amp 
Im_scale = dn_per_amp  # DN/Amp 

ads_full_scale = 10
dn_per_volt = (2**16/ads_full_scale) # correct
VP1_scale = dn_per_volt*11.0*1.7

dac_range = 5
dac_scale = 2**14*4.0/(10/(dac_range*2)) # DN/Volt TODO: verify this  # /0.58 ? 

# ------ Collect Data --------------
QUIET_DACS = False # if True use the host driven DAC to test noise
file_name = time.strftime("%Y%m%d-%H%M%S")
datastream_out_fname = 'clamptest6_quietdacs{}_rtia{}_ccomp{}.h5'
idx = 0

# fast DAC channels setup
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    if QUIET_DACS:
        daq.DAC[i].write(int(0x2000)) # midscale 
    else:
        daq.DAC[i].write(int(0x2000))
        daq.DAC[i].set_data_mux("DDR")
        daq.DAC[i].set_data_mux("DDR", filter_data=True) # this selects the Observer data into the filter data input. TODO: update name
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, dac_range)  # 5V 

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
fc_cmd = 100e3
#fc_cmd = None
step_len = 16384*8
first_pos_step = step_len/2*1/DAC_FS # in seconds 
set_cmd_cc(dc_nums=[dc_mapping['bath']], cmd_val=0x0200, cc_scale=0, cc_delay=0, fc=fc_cmd,
        step_len=16384*8, cc_val=None, cc_pickle_num=None)

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
        gain=in_amp,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict

cap = capacitors[0]
fb_res = feedback_resistors[0]
fb_res = 2.1
# Try with 5 different resistors
res = [x for x in bath_res if type(x) == int][0]
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
        gain=in_amp,  # instrumentation amplifier
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
ddr.repeat_setup() # Get data

def capture_data(idx=0):
    ddr.repeat_setup() # Get data

    filename = file_name.format(idx) + '.h5'

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    chan_data_one_repeat = ddr.save_data(data_dir, filename, num_repeats=32,
                                        blk_multiples=80)  # blk multiples must be multiple of 10 
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
        im_data_filt = butter_lowpass_filter(im_data, cutoff=fc, fs=1/(t[1]-t[0]), order=5)
        idx = (t > first_pos_step + 2e-3) & (t < first_pos_step + 5e-3)
        im_noise_wb = np.std(im_data[idx])
        im_noise_filt = np.std(im_data_filt[idx])
        print(f'Im gain of {adg_r} kOhm = {(adg_r*1e3)*1e3*1e-9} mV/nA. Current noise of {im_noise_wb*1e9} nA full-bw; {im_noise_filt*1e9} nA {fc} bw')

    for fig in figs:
        fig.canvas.draw()
        fig.canvas.flush_events()
    
    first_time = False

    return first_time, lines1, lines2, figs

datastreams, log_info = capture_data()
# run twice to remove initial transient 
datastreams, log_info = capture_data()
first_time, lines1, lines2, figs = update_plots(first_time, datastreams)

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
adg_r_arr = [10, 33, 100, 332]
ccomp_arr = [47, 200, 247, 1000, 1247, 4700]

ccomp_arr = [47, 247, 1000, 4700]
adg_r_arr = [33, 100, 332, 1000]

#ccomp_arr = [None, 47, 247, 1000, 1247, 4700]
ccomp_arr = [47]
adg_r_arr = [33, 100, 332, 1000, 3000, 10000]

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
        
        for i in range(10):
            time.sleep(0.2)
            datastreams, log_info = capture_data(idx=1)
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
            t = osc.save_display_data(os.path.join(data_dir, 'test_scope_ccomp{}_rtia{}'.format(ccomp, adg_r)))
            osc.set('run_acq')

        TO_CLAMPFIT = True
        if TO_CLAMPFIT:
            datastreams.to_clampfit(data_dir, 'test2_step_quietdacs_rtia{}_ccomp{}.abf'.format(adg_r, ccomp),
                                    names_pclamp = ['Im', 'CMD0', 'V1', 'P1'],
                                    dac_len=len(datastreams['CMD0'].data), dac_sample_rate=2.5e6, sweeps=1)

        # add log info to datastreams -- any dictionary is ok  
        datastreams.add_log_info(ephys_sys.__dict__)  # all properties of ephys_sys 
        datastreams.add_log_info({'dc_configs': dc_configs})
        datastreams.add_log_info({'ddr_step_peak': first_pos_step})
        datastreams.add_log_info({'dut': 'model_cell'})
        datastreams.add_log_info({'quiet_dacs': QUIET_DACS})
        datastreams.to_h5(data_dir, datastream_out_fname.format(QUIET_DACS, adg_r, ccomp), log_info)

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
    si = datastreams[sig].stepinfo_range([first_pos_step-20e-6, first_pos_step+170e-6])
    print(f'{sig} step info: {si}')
    print('-'*100)

if 0:
    # sweep the gain of the voltage clamp 
    for rf in Clamp.configs['RF1_dict']:
        dc_configs[1]['RF1'] = rf
        clamps[1].configure_clamp(**dc_configs[1])
        print(f'RF = {rf}')
        input('next?')