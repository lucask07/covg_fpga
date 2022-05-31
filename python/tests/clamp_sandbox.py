"""Test of the clamp board (v1), initial bring-up for biophys society meeting
   data
December 2021
April 2022: modified for a 2nd daughter card to serve as voltage clamp

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

from interfaces.boards import Daq, Clamp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
import logging
from interfaces.interfaces import (
    FPGA,
    AD5453,
    Endpoint,
    DAC80508,
    AD7961,
    disp_device,
    DDR3,
    advance_endpoints_bynum,
    TCA9555,
)
from interfaces.boards import Daq, Clamp
from interfaces.utils import twos_comp
import os
import sys
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, basinhopping
import pandas as pd
import pickle as pkl
import h5py
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from analysis.adc_data import read_plot, read_h5, peak_area, get_impulse, im_conv, idx_timerange
from analysis.clamp_data import adjust_step2, adjust_step, adjust_step_delay, adjust_step_scale

FS = 5e6
SAMPLE_PERIOD = 1/FS
#import matplotlib

# matplotlib.use("TkAgg")  # or "Qt5agg" depending on you version of Qt

# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == "covg_fpga":
        interfaces_path = os.path.join(covg_fpga_path, "python")
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(interfaces_path)

eps = Endpoint.endpoints_from_defines

data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    pass
elif sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp_test/{}{:02d}{:02d}"
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')

today = datetime.datetime.today()
data_dir = data_dir_covg.format(
    today.year, today.month, today.day
)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

pwr_setup = "3dual"
dc_num = 0  # the Daughter-card channel under test. Order on board from L to R: 1,0,2,3

# encoding was added as an option at Python 3.9
# logging.basicConfig(filename='DAC53401_test.log',
#                     encoding='utf-8', level=logging.INFO)

# alternative for Python<3.9
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler("DAC53401_test.log", "w", "utf-8")
root_logger.addHandler(handler)

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

# ------ oscilloscope -----------------
if 0:
    osc = open_by_name("msox_scope")
    osc.set("chan_label", '"P2"', configs={"chan": 1})
    osc.set("chan_label", '"CC"', configs={"chan": 3})
    osc.set("chan_label", '"Vm"', configs={"chan": 4}) # label must be in "" for the scope to accept
    osc.comm_handle.write(':DISP:LAB 1')  # turn on the labels
    osc.set('chan_display', 0, configs={'chan': 2})

# --------  function generator  --------
fg = open_by_name("new_function_gen")

fg.set("load", "INF")
fg.set("offset", 2)
fg.set("v", 2)
fg.set("freq", 10e3)
fg.set("output", "ON")

atexit.register(fg.set, "output", "OFF")

# Initialize FPGA
f = FPGA(
    bitfile=os.path.join(
        covg_fpga_path,
        "fpga_XEM7310",
        "fpga_XEM7310.runs",
        "impl_1",
        "top_level_module.bit",
    )
)
f.init_device()
sleep(2)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)
ad7961s = daq.ADC
ad7961s[0].reset_wire(1)

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug("dfast1")
gpio.ads_misc("sdoa")  # do not care for this experiment

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamp = {}
for dc_num in [0,1]:
    clamp[dc_num] = Clamp(f, dc_num=dc_num)
    clamp[dc_num].init_board()

    # configure the clamp board, settings default to None so that a setting that is not
    # included is masked and stays the same
    # TODO: configure_clamp errors out if not connected

    if dc_num == 1:
        pclamp_ctrl = 1 # short P1 and P2 since not connected 
        adg_r = 10  #TODO: add 0 ohm to board option
    else:
        pclamp_ctrl = 0
        adg_r = 100

    log_info, config_dict = clamp[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="drive_CAL2",
        CCOMP=47,
        RF1=2.1,  # feedback circuit
        ADG_RES=adg_r,
        PClamp_CTRL=pclamp_ctrl,
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

# --------  Enable fast ADCs  --------
for chan in [0,1,2,3]:
    ad7961s[chan].power_up_adc()  # standard sampling

ad7961s[0].reset_wire(0)
time.sleep(1)

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channels setup 
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("DDR")
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, 500)  # 500 mV full-scale

# configure clamp board Utility pin to be the offset voltage for the feedback
# at this point the slow DA Ccan be set by the host 
for i in range(2):
    # Reset the Wishbone controller and SPI core
    # daq.DAC_gp[i].reset_master()
    daq.DAC_gp[i].set_ctrl_reg(daq.DAC_gp[i].master_config)
    daq.DAC_gp[i].set_spi_sclk_divide()
    daq.DAC_gp[i].filter_select(operation="clear")
    daq.DAC_gp[i].set_data_mux("host")
    # daq.DAC_gp[i].set_gain(gain=1, divide_reference=False) #TODO: check default values
    daq.DAC_gp[i].set_config_bin(0x00)
    print('Outputs powered on')

#DAC1_BP_OUT4, J11 pin #11 -- connected to utility pin to daughter card -- offset voltage
# clamp board TP1
daq.DAC_gp[0].write_voltage(1.457, 4) # 0.6125 V, which approx centers P1 and P2
#DAC1_BP_OUT5, J11 pin #13 -- connected to utility pin to daughter card -- offset voltage
# clamp board TP1
daq.DAC_gp[0].write_voltage(1.457, 5) # 0.6125 V, which approx centers P1 and P2 -- for DC #2
# for the 3.3 V "supply voltage" to the op-amp
daq.DAC_gp[1].write_voltage(2.36, 7)

# ------------- configure ADS8686
ads = daq.ADC_gp # ADS8686
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(5)
ads.set_lpf(376)

codes = ads.setup_sequencer(chan_list=[('0', '0'), ('1', '1'), ('2','2')])
ads.write_reg_bridge(clk_div=200) # 1 MSPS update rate. Write register for SPI configuration reg. Update rate is controlled by top-level timer
ads.set_fpga_mode()
# -------------------

cmd_dac = daq.DAC[1]  # DAC channel 0 is connected to dc clamp ch 0 CMD signal
cc = daq.DAC[0]
ddr = DDR3(f, data_version='TIMESTAMPS')

def ddr_write_setup():
    ddr.set_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()
    ad7961s[0].reset_trig()  # TODO: what does this do?

def ddr_write_finish():
    # reenable both DACs
    ddr.set_adc_dac_simultaneous()  # enable DAC playback and ADC writing to DDR

def get_cc_optimize(nums):

    data_dir_base = os.path.expanduser('~')
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')
    data_dir = data_dir_covg.format(2022,1,19)

    #for nums in ([20,21], [30,31], [14,15], [40,41]):
    with open(os.path.join(data_dir, 'basin_hop_cc_nums{}.pickle'.format(nums[0])), 'rb') as fp:
        out = pkl.load(fp)
    return out


def set_cmd_cc(cmd_val = 0x1d00, cc_scale = 0.351, cc_delay=0, fc=4.8e3, step_len=8000,
            cc_val=None, cc_pickle_num=None):

    dac_offset = 0x2000
    cmd_ch = 1
    cc_ch = 0

    ddr.data_arrays[cmd_ch] = ddr.make_step(
        low=dac_offset - int(cmd_val), high=dac_offset + int(cmd_val), length=step_len) # 1.6 ms between edges

    # create the cc using multiple methods
    if cc_pickle_num is not None:
        cc_impulse_scale = -2600/7424
        out = get_cc_optimize(cc_pickle_num)
        cc_wave = adjust_step2(out['x'], ddr.data_arrays[cmd_ch].astype(np.int32) - dac_offset)
        cc_wave = cc_wave * cc_impulse_scale
        cc_wave = cc_wave + dac_offset
        if cc_delay !=0:
            cc_wave = delayseq_interp(cc_wave, cc_delay, 2.5e6)  # 2.5e6 is the sampling rate
        ddr.data_arrays[cc_ch] = cc_wave.astype(np.uint16)

    elif cc_val is None: # get the cc signal from scaling the cmd signal
        if fc is not None:
            ddr.data_arrays[cc_ch] = butter_lowpass_filter(ddr.data_arrays[cmd_ch] - dac_offset, cutoff=fc, fs=2.5e6, order=1)*cc_scale + dac_offset
        else:
            ddr.data_arrays[cc_ch] = (ddr.data_arrays[cmd_ch] - dac_offset)*cc_scale + dac_offset
        if cc_delay !=0:
            ddr.data_arrays[cc_ch] = delayseq_interp(ddr.data_arrays[cc_ch], cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    else: # needed so that the cmd signal can be zero with a non-zero cc signal
        ddr.data_arrays[cc_ch] = ddr.make_step(low=dac_offset - int(cc_val),
                                                high=dac_offset + int(cc_val),
                                                length=step_len) # 1.6 ms between edges
        if fc is not None:
            ddr.data_arrays[cc_ch] = butter_lowpass_filter(ddr.data_arrays[cc_ch], cutoff=fc, fs=2.5e6, order=1)
        if cc_delay !=0:
            ddr.data_arrays[cc_ch] = delayseq_interp(ddr.data_arrays[cc_ch], cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    # write channels to the DDR
    ddr_write_setup()
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False) # clear read, set write, etc. handled within write_channels
    ddr.reset_mig_interface()
    ddr_write_finish()

ddr.data_arrays[3] = ddr.make_step(0x2000 - 0x800, 0x2000 + 0x800,
                                    length=2048)
ddr.data_arrays[2] = ddr.make_step(0x2000 - 0x800, 0x2000 + 0x800,
                                    length=2048)                                    
set_cmd_cc(cmd_val=0x400, cc_scale=0, cc_delay=0, fc=None,step_len=16384, cc_val=None, cc_pickle_num=None)


#CHAN_UNDER_TEST = 0
#output = pd.DataFrame()
#data = {}
file_name = 'test'
#data['filename'] = file_name
#output = output.append(data, ignore_index=True)

#print(output.head())
#output.to_csv(os.path.join(data_dir, file_name + '.csv'))

idx = 0

REPEAT = False
if REPEAT:  # to repeat data capture without rewriting the DAC data
    ddr.clear_adc_read()
    ddr.clear_adc_write()

    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()

    ddr_write_finish()
    time.sleep(0.01)

# saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 8,
                          blk_multiples=40) # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file 
adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data)

# Shorter data sequence, just one of the repeats
# adc_data, timestamp, read_check, dac_data, ads = ddr.data_to_names(chan_data_one_repeat)

t = np.arange(0,len(adc_data[0]))*1/FS

crop_start = 0 # placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

# fast ADC. AD7961
for ch in [0]:
    fig,ax=plt.subplots()
    y = adc_data[ch][crop_start:]
    lbl = f'Ch{ch}'
    ax.plot(t*1e6, y, marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Fast ADC data')
    ax.set_xlabel('s [us]')

# DACs 
t_dacs = t[crop_start::2]  # fast DACs are saved every other 5 MSPS tick
for dac_ch in range(4):
    fig,ax=plt.subplots()
    y = dac_data[dac_ch][crop_start:]
    lbl = f'Ch{dac_ch}'
    ax.plot(t_dacs*1e6, y, marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Fast DAC data')
    ax.set_xlabel('s [us]')

# ADS8686. ToDo will need to chop up based on sequencer settings 
t_ads = t[crop_start::5] # ADS8686 data is saved every fifth 5 MSPS tick
skip = 3 # sequencer has 3 channels to cycle through

AC_COUPLE = False
fig,ax=plt.subplots()
for start_num in [0, 1, 2]:
    if AC_COUPLE:
        ax.plot(t_ads[start_num::skip]*1e6, ads['A'][start_num::skip] - np.mean(ads['A'][start_num::skip]), 
            marker = '+', label = f'ADS: A:{start_num}')
        ax.plot(t_ads[start_num::skip]*1e6, ads['B'][start_num::skip] - np.mean(ads['B'][start_num::skip]), 
            marker = '+', label = f'ADS: B:{start_num}')
    else:
        ax.plot(t_ads[start_num::skip]*1e6, ads['A'][start_num::skip], 
            marker = '+', label = f'ADS: A:{start_num}')
        ax.plot(t_ads[start_num::skip]*1e6, ads['B'][start_num::skip], 
            marker = '+', label = f'ADS: B:{start_num}')
ax.legend()
ax.set_xlabel('s [us]')
ax.set_title('ADS8686 data')




def tune_cc(data_dir, file_name, rf, ccomp, cmd_impulse_scaling=7424, cc_impulse_scaling=2600, PLT_DEBUG=True):

    log_info, config_dict = clamp.configure_clamp(
        ADC_SEL="CAL_SIG1",DAC_SEL="drive_CAL2",CCOMP=ccomp, RF1=2.1,  # feedback circuit
        ADG_RES=rf,PClamp_CTRL=0,P1_E_CTRL=0,P1_CAL_CTRL=0,P2_E_CTRL=0,P2_CAL_CTRL=0,
        gain=1,  # instrumentation amplifier
        FDBK=1,mode="voltage",EN_ipump=0,RF_1_Out=1,addr_pins_1=0b110,
        addr_pins_2=0b000)

    idx = 0
    # cmd_scaling -- set to avoid saturation
    set_cmd_cc(cmd_val=cmd_impulse_scaling, cc_scale=0, cc_delay=0, fc=None, step_len=16384)
    time.sleep(0.04) # a few periods to settle after stoping and starting CMD voltage
    save_adc_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 4)
    cmd_impulse, t, t0 = get_impulse(data_dir, file_name.format(idx))

    idx += 1
    # cc_scaling -- set to avoid saturation (filename?)
    set_cmd_cc(cmd_val=0, cc_scale=0, cc_delay=0, fc=None, step_len=16384, cc_val=cc_impulse_scaling)
    time.sleep(0.04) # a few periods to settle after stoping and starting CMD voltage
    save_adc_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 4)
    cc_impulse, _,_ = get_impulse(data_dir, file_name.format(idx))

    if PLT_DEBUG:
        fig, ax = plt.subplots() # plot before normalizing by scaling so that
        ax.plot( (t-t0)*1e6, cmd_impulse, marker='+', label=r'$h_{CMD}$')
        ax.plot( (t-t0)*1e6, cc_impulse, marker='o', label=r'$h_{CC}$') 
        ax.set_xlim([-10, +60])
        ax.set_xlabel('t [$\mu$s]')
        ax.set_ylabel('h(t) [DN/s]')
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(data_dir, 'impulse_response_rf{}_cc{}_.png'.format(rf, ccomp)))

    # create a step function
    step_func = np.zeros(len(t))
    step_func[t>t0] = 1
    runt_idx = np.argmax(step_func>0.5)

    # normalize impulse function
    cmd_impulse = cmd_impulse/cmd_impulse_scaling
    cc_impulse = cc_impulse/cc_impulse_scaling
    cmd_over_cc = cmd_impulse_scaling/cc_impulse_scaling

    bnds = ((-1, 1), (-5e-6, 5e-6),
            (-1, 1), (2e3, 2.45e6), (-5e-6, 5e-6),
            (-1, 1), (2e3, 2.45e6),(-5e-6, 5e-6),
            (-1, 1), (2e3, 2.45e6), (-5e-6, 5e-6),
            (-0.3, 0.3), (runt_idx-50, runt_idx+50), (runt_idx-20, runt_idx+80))
    out_min = minimize(im_conv, x0=[-0.16, 0e-6,
                                    -0.16, 100e3, 0e-6,
                                    -0.05,100e3, 0e-6,
                                    0.1, 100e3, 0e-6,
                                    0.02, runt_idx, runt_idx+20],
                        args=(cmd_impulse, step_func, cc_impulse, step_func, adjust_step2), bounds=bnds, method='L-BFGS-B')
    new_cc_step = adjust_step2(out_min['x'], step_func)

    # now minimize just delay and global scale separately
    bnds = ((-3e-6, 3e-6), )
    minimizer_kwargs = { "method": "L-BFGS-B","bounds":bnds,"args":(cmd_impulse, step_func, cc_impulse, new_cc_step, adjust_step_delay) }
    out_min = basinhopping(im_conv, x0=[0],
                        minimizer_kwargs = minimizer_kwargs)

    new_cc_step = adjust_step_delay(out_min['x'], new_cc_step)
    print('delay shift {}'.format(out_min['x']))
    out_min_dly = out_min

    bnds = ((0.95, 1.05), ) # trailing comma required for len(bnds)==1
    minimizer_kwargs = { "method": "L-BFGS-B","bounds":bnds,"args":(cmd_impulse, step_func, cc_impulse, new_cc_step, adjust_step_scale) }
    out_min = basinhopping(im_conv, x0=[0],
                        minimizer_kwargs = minimizer_kwargs)
    new_cc_step = adjust_step_scale(out_min['x'], new_cc_step)
    print('scale shift {}'.format(out_min['x']))

    if PLT_DEBUG:
        fig, ax = plt.subplots()
        y = np.convolve(cmd_impulse, step_func, mode='same') + np.convolve(-cc_impulse, step_func*1/cmd_over_cc, mode='same')
        t_im = np.linspace(0, (len(y) - 1)*SAMPLE_PERIOD, len(y))
        ax.plot(t_im*1e6, y, 'b', label='CMD + CC; no tuning')
        ax.plot(t_im*1e6, np.convolve(cmd_impulse, step_func, mode='same') + \
                np.convolve(cc_impulse, new_cc_step, mode='same'),
                'r', label='CMD + CC; tuned')
        ax.plot(t_im*1e6, np.convolve(cmd_impulse, step_func, mode='same'), 'k', label='CMD only')
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(data_dir, 'im_result_rf{}_cc{}_.png'.format(rf, ccomp)))

        fig, ax = plt.subplots()
        ax.plot(t*1e6, step_func, 'k', label='CMD step')
        ax.plot(t*1e6, new_cc_step, 'm', label='CC step')
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(data_dir, 'step_functions_rf{}_cc{}_.png'.format(rf, ccomp)))

    # optimize cc function with given impulse responses (pass a given cc-creation function)
    # adjust_step2(x, cc_func)
    return out_min, new_cc_step, step_func, out_min_dly, t0
    # tune cc function using experimental measurements -- create function


def cc_search():
    output = pd.DataFrame()

    cc_scale = -0.36
    cc_delay = 20e-6
    cc_fc = 8e3
    idx = 0
    for cc_fc in np.linspace(4e3, 15e3, 12):  # 12
        for cc_delay in np.linspace(-10e-6, 40e-6, 12):  # 16
            for cc_scale in np.concatenate((np.array([0]), np.linspace(-0.4, -0.3, 10))):  # 18
                data = {}
                file_name = f'cc_swp4_{idx}'

                set_cmd_cc(cc_scale=cc_scale, cc_delay=cc_delay, fc=cc_fc)
                time.sleep(0.04) # a few periods to settle after stoping and starting CMD voltage

                data['cc_scale'] = cc_scale
                data['cc_delay'] = cc_delay
                data['cc_fc'] = cc_fc

                result_ok = False
                num_tries = 0
                while ((not result_ok) and (num_tries<5)):
                    try:
                        save_adc_data(data_dir, file_name + '.h5', num_repeats = 2)
                        t, adc_data = read_h5(os.path.join(data_dir, file_name + '.h5'), chan_list=[0])
                        pa, num_found = peak_area(t[64:], adc_data[0][64:])  # crop the first 64 since might be from stale FIFO
                        result_ok=True
                    except:
                        print('retry')
                        num_tries += 1
                if num_tries==5:
                    raise ValueError('A very specific bad thing happened')

                data['peak_area'] = pa
                data['peaks_found'] = num_found
                osc.set('single_acq')
                time.sleep(0.10)

                # general measure -- input measure type
                for ch in [1,3,4]:
                    rt = osc.get('meas', configs={'meas_type':'RIS', 'chan':ch})
                    data[f'rise_{ch}'] = rt
                    va = osc.get('meas', configs={'meas_type':'VAMP', 'chan':ch})
                    data[f'amp_{ch}'] = va

                # save a PNG screen-shot to host computer
                t = osc.save_display_data(os.path.join(data_dir, file_name))
                osc.set('run_acq')

                data['filename'] = file_name
                output = output.append(data, ignore_index=True)
                idx = idx + 1

    print(output.head())
    output.to_csv(os.path.join(data_dir, file_name + '.csv'))
    return output

SCOPE_SCREENSHOT = False

def vs_rf_ccomp(rf_arr=[10,33,100,332,3000,10000],
                ccomp_arr=[47,247,1047,4747,5900], file_name='rf_swp_{}'):
    output = pd.DataFrame()

    # optimal cc parameters
    cc_scale = -0.33
    cc_delay = 10e-6
    cc_fc = 15e3

    idx = 0

    for rf in rf_arr:
        for ccomp in ccomp_arr:
            log_info, config_dict = clamp.configure_clamp(
                ADC_SEL="CAL_SIG1",
                DAC_SEL="drive_CAL2",
                CCOMP=ccomp,
                RF1=2.1,  # feedback circuit
                ADG_RES=rf,
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
            for cmd_val in [0, 0x1d00]:
                for cc_adj in [False, True]:
                    data = {}
                    data['rf'] = rf
                    data['ccomp'] = ccomp

                    if cc_adj:
                        set_cmd_cc(cmd_val = cmd_val, cc_scale=cc_scale, cc_delay=cc_delay, fc=cc_fc,step_len=16384)
                        data['cc_scale'] = cc_scale
                        data['cc_delay'] = cc_delay
                        data['cc_fc'] = cc_fc
                    else:
                        set_cmd_cc(cmd_val = cmd_val, cc_scale=0, cc_delay=0, fc=1e3, step_len=16384)
                        data['cc_scale'] = 0
                        data['cc_delay'] = 0
                        data['cc_fc'] = 1e3
                    data['cmd_val'] = cmd_val

                    time.sleep(0.04) # a few periods to settle after stoping and starting CMD voltage

                    save_adc_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 4)
                    t, adc_data = read_h5(os.path.join(data_dir, file_name.format(idx) + '.h5'), chan_list=[0])

                    try:
                        pa, num_found = peak_area(t[64:], adc_data[0][64:])  # crop the first 64 since might be from stale FIFO
                    except:
                        print('no peaks found')
                        pa = -1
                        num_found = 0

                    data['peak_area'] = pa
                    data['peaks_found'] = num_found
                    # general measure -- input measure type
                    for ch in [1,3,4]:
                        rt = osc.get('meas', configs={'meas_type':'RIS', 'chan':ch})
                        data[f'rise_{ch}'] = rt
                        va = osc.get('meas', configs={'meas_type':'VAMP', 'chan':ch})
                        data[f'amp_{ch}'] = va

                    if SCOPE_SCREENSHOT:
                        osc.set('single_acq')
                        time.sleep(0.10)
                        # save a PNG screen-shot to host computer -- would like to check for a trigger first but osc.get('is_running') doesn't seem to work
                        osc.set('stop_acq') # in case the trigger didn't work
                        t = osc.save_display_data(os.path.join(data_dir, file_name.format(idx)))
                        osc.set('run_acq')

                    data['filename'] = file_name.format(idx)
                    output = output.append(data, ignore_index=True)
                    idx = idx + 1

    print(output.head())
    output.to_csv(os.path.join(data_dir, file_name.format(idx) + '.csv'))

    return output

# enable only cmd or only cc to measure the step response (to get the impulse response)
def step_responses(rf_arr=[10,33,100,332,3000,10000],
                    ccomp_arr=[47,247,1047,4747,5900],
                    cc_delay_arr = np.linspace(-5e-6,5e-6,16),
                    file_name='step_swp_{}'):
    output = pd.DataFrame()

    # cc parameters
    cc_scale = 0
    cc_delay = 0
    cc_fc = 0

    idx = 0

    for rf in rf_arr:
        for ccomp in ccomp_arr:
            log_info, config_dict = clamp.configure_clamp(
                ADC_SEL="CAL_SIG1",
                DAC_SEL="drive_CAL2",
                CCOMP=ccomp,
                RF1=2.1,  # feedback circuit
                ADG_RES=rf,
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
            for cmd_val, cc_val in [(0x1d00, 0), (0x1d00, -2600), (0x1d00, 'cc_basin')]:
                for cc_delay in cc_delay_arr:

                    data = {}
                    data['rf'] = rf
                    data['ccomp'] = ccomp

                    if cc_val == 'cc_basin':
                        if rf == 33:
                            nums = [14,15]
                        elif rf == 100:
                            nums = [20,21]
                        elif rf == 332:
                            nums = [30,31]
                        elif rf == 3000:
                            nums = [40,41]
                        else:
                            nums = None
                            cc_scale = 0
                            cc_val = 0
                        set_cmd_cc(cmd_val = cmd_val, cc_scale=0, cc_delay=cc_delay, fc=None,step_len=16384, cc_val=cc_val, cc_pickle_num=nums)
                    else:
                        set_cmd_cc(cmd_val = cmd_val, cc_scale=0, cc_delay=cc_delay, fc=None,step_len=16384, cc_val=cc_val)
                    data['cc_val'] = cc_val
                    data['cc_delay'] = cc_delay
                    data['cc_fc'] = cc_fc
                    data['cmd_val'] = cmd_val

                    time.sleep(0.04) # a few periods to settle after stoping and starting CMD voltage
                    save_adc_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 4)
                    t, adc_data = read_h5(data_dir, file_name=file_name.format(idx) + '.h5', chan_list=[0])

                    try:
                        pa, num_found = peak_area(t[64:], adc_data[0][64:])  # crop the first 64 since might be from stale FIFO
                    except:
                        print('no peaks found')
                        pa = -1
                        num_found = 0

                    data['peak_area'] = pa
                    data['peaks_found'] = num_found
                    # general measure -- input measure type
                    for ch in [1,3,4]:
                        rt = osc.get('meas', configs={'meas_type':'RIS', 'chan':ch})
                        data[f'rise_{ch}'] = rt
                        va = osc.get('meas', configs={'meas_type':'VAMP', 'chan':ch})
                        data[f'amp_{ch}'] = va

                    if SCOPE_SCREENSHOT:
                        osc.set('single_acq')
                        time.sleep(0.10)
                        # save a PNG screen-shot to host computer -- would like to check for a trigger first but osc.get('is_running') doesn't seem to work
                        osc.set('stop_acq') # in case the trigger didn't work
                        t = osc.save_display_data(os.path.join(data_dir, file_name.format(idx)))
                        osc.set('run_acq')

                    data['filename'] = file_name.format(idx)
                    output = output.append(data, ignore_index=True)
                    idx = idx + 1

    print(output.head())
    output.to_csv(os.path.join(data_dir, file_name.format(idx) + '.csv'))

    return output

def cc_comp():

    set_cmd_cc(cmd_val = 0x1d00, cc_scale = 0.351, cc_delay=0, fc=4.8e3, step_len=8000,
            cc_val=None, cc_pickle_num=[20,21])

    plt.plot(ddr.data_arrays[0])
    plt.plot(ddr.data_arrays[1])




if 0:
    for rf,ccomp in ([(10,47), (100,47), (332,47), (3000,4747), (10000, 4747)]):
        # TODO: the impulse function processing needs different time ranges based on RF and ccomp. 
        file_name = f'test_tune_rf{rf}_ccomp{ccomp}' + '_{}'

        if rf <= 100:
            scale = 7424
            cc_scale = 2600
            tr = 160
        if rf == 332:
            scale = 7424//2
            cc_scale = 2600//2
            tr = 160
        if rf == 3000:
            scale = 7424//5
            cc_scale = 2600//5
            tr = 600
        if rf == 10000:
            scale = 7424//5
            cc_scale = 2600//5
            tr = 600

        out_min, cc_step_func, step_func, out_min_dly, t0 = tune_cc(data_dir, file_name, rf=rf, ccomp=ccomp, 
                                                                    cmd_impulse_scaling=scale, cc_impulse_scaling=cc_scale)

        total_len = 16384 
        dac_offset = 0x2000
        cmd_ch = 1
        cc_ch = 0

        # pad left and right so that the result is the same length as original step function (find center)
        center = np.argmax(step_func>0.5)
        len_step = len(step_func)
        step_func = np.pad(step_func, (total_len//2-(center), total_len//2-(len_step-center)), 'edge')
        cc_step_func = np.pad(cc_step_func, (total_len//2-(center), total_len//2-(len_step-center)), 'edge')

        # adjust steps to zero mean, scale, then add offset, convert to uint16
        step_func = ((step_func - np.mean(step_func))*scale + dac_offset).astype(np.uint16)
        cc_step_func = ((cc_step_func - np.mean(cc_step_func))*scale + dac_offset).astype(np.uint16) # both impulses are normalized so scale equally

        # need to repeat the array -- total length of array is 256*16384
        ddr.data_arrays[cc_ch] = np.tile(cc_step_func, 256)
        ddr.data_arrays[cmd_ch] = np.tile(step_func, 256)

        ddr_write_setup()
        g_buf = ddr.write_channels(set_ddr_read=False) # clear read, set write, etc. handled within write_channels
        ddr_write_finish()

        idx = 2
        time.sleep(0.04) # a few periods to settle after stoping and starting CMD voltage
        save_adc_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 4)
        fig,ax=plt.subplots()
        adc_min = {}
        for i in [0,2]:
            t, adc_data = read_h5(data_dir, file_name.format(i) + '.h5', chan_list=[0])
            if i == 0:
                lbl='$I_m$: CMD only'
            elif i == 2:
                lbl='$I_m$: CMD + tuned CC'
            idx = idx_timerange(t, t0-10e-6, t0+tr*1e-6)
            ax.plot((t[idx]-t0)*1e6, adc_data[0][idx], marker = '+', label=lbl)
            adc_min[i] = np.min(adc_data[0][idx])
        ax.set_xlim([-10, tr])
        ax.set_xlabel('t [$\mu$s]')
        ax.set_ylabel('$I_m$ [DN]')
        ax.legend()
        ymin, ymax = ax.get_ylim()
        ax.set_ylim([np.min([adc_min[0], adc_min[2]])-500, ymax])
        fig.tight_layout()
        fig.savefig(os.path.join(data_dir, 'final_comparison_rf{}_cc{}_.png'.format(rf, ccomp)))
