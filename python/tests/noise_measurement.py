"""Test of the clamp board (v1), initial bring-up for biophys society meeting
   data
December 2021

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
from calibration.signal_chain import dn_per_nA


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
# gpio.spi_debug("ds0")
gpio.ads_misc("sdoa")  # do not care for this experiment

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamp = Clamp(f, dc_num=dc_num)
clamp.init_board()

# configure the clamp board, settings default to None so that a setting that is not
# included is masked and stays the same
# TODO: configure_clamp errors out if not connected

log_info, config_dict = clamp.configure_clamp(
    ADC_SEL="CAL_SIG1",
    DAC_SEL="drive_CAL2",
    CCOMP=47,
    RF1=2.1,  # feedback circuit
    ADG_RES=100,
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

# log_info, config_dict = clamp.configure_clamp(P2_E_CTRL=0, addr_pins_1=0b110, addr_pins_2=0b000)

test_channel = 1
ADC_TEST_PATTERN = False

# --------  Run ADC tests  --------
# setup = ad7961s[0].setup(reset_pll=True)
# time.sleep(1)  # this pause is required. Failed at 100 ms.

d1 = {}
d2 = {}

for chan in [0,1,2,3]:
    ad7961s[chan].power_up_adc()  # standard sampling

ad7961s[0].reset_wire(0)
time.sleep(1)

for chan in [0,1,2,3]:
    for num in [1, 2]:
        # resets FIFO and ADC controller
        # setup = ad7961s[chan].setup(reset_pll=False)
        # time.sleep(0.2)  # this pause is required. Failed at 100 ms.

        if ADC_TEST_PATTERN:
            ad7961s[chan].test_pattern()
            time.sleep(0.2)
            ad7961s[chan].reset_fifo()
            time.sleep(0.2)  # FIFO fills in 204 us
            d1[chan] = ad7961s[chan].stream_mult(swps=4, twos_comp_conv=False)

        ad7961s[chan].reset_fifo()
        d2[chan] = ad7961s[chan].stream_mult(swps=4)

# disp_device(ad7961s[0])
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channel 0 and 1
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("host")
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, 500)  # 500 mV full-scale

# 0xA0 = 1.25 MHz, 0x50 = 2.5 MHz
daq.DAC[0].set_clk_divider(divide_value=0x50)
# daq.TCA[0].write(((0xF) << (4 + 8)) + 0xFFF) accomplished using set_dac_gain

# configure clamp board Utility pin to be the offset voltage for the feedback
for i in range(2):
    # Reset the Wishbone controller and SPI core
    # daq.DAC_gp[i].reset_master()
    daq.DAC_gp[i].set_ctrl_reg(daq.DAC_gp[i].master_config)
    daq.DAC_gp[i].set_spi_sclk_divide()
    daq.DAC_gp[i].filter_select(operation="clear")
    daq.DAC_gp[i].set_data_mux("host")
    #daq.DAC_gp[i].set_gain(0x01ff)
    print('Gain changed')
    daq.DAC_gp[i].set_config_bin(0x00)
    print('Outputs powered on')

#DAC1_BP_OUT4, J11 pin #14 -- connected to utility pin -- offset voltage
# clamp board TP1
daq.DAC_gp[0].write_voltage(1.25, 4)  # after bipolar conversion this produces about 0 V
daq.DAC_gp[0].write_voltage(1.457, 4) # 0.6125 V, which approx centers P1 and P2

# for the 3.3 V "supply voltage" to the op-amp
daq.DAC_gp[1].write_voltage(2.36, 7)

cmd_dac = daq.DAC[1]  # DAC channel 0 is connected to dc clamp ch 0 CMD signal
cc = daq.DAC[0]
ddr = DDR3(f)


def ddr_write_setup():
    # adjust the DDR settings of both DACs
    # quiet both DACs
    cc.set_data_mux("host")
    cmd_dac.set_data_mux("host")
    ddr.reset_fifo()

def ddr_write_finish():
     # reenable both DACs
    cmd_dac.set_data_mux("DDR")
    cc.set_data_mux("DDR")
    ddr.set_read()  # enable DAC playback and ADC reading


def set_cmd_cc(cmd_val = 0x1d00, cc_scale = 0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None):

    ddr_write_setup()

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
    g_buf = ddr.write_channels(set_ddr_read=False) # clear read, set write, etc. handled within write_channels

    ddr_write_finish()

def read_adc(ddr, blk_multiples=2048):
    # block size is 2048.
    # bits 0:63 of the DDR, first 4 channels of the
    t, bytes_read_error = ddr.read_adc(  # just reads from the block pipe out
        sample_size=ddr.parameters["BLOCK_SIZE"] * blk_multiples
    )
    d = np.frombuffer(t, dtype=np.uint8).astype(np.uint32)
    print(f'Bytes read: {bytes_read_error}')
    return d, bytes_read_error


def deswizzle(d, convert_twos=True):

    bits = 16
    chan_data_swz = {}  # this data is swizzled
    for i in range(4):
        chan_data_swz[i] = (d[(0 + i * 2) :: 8] << 0) + (d[(1 + i * 2) :: 8] << 8)

    chan_data = {}
    chan_data[0] = chan_data_swz[2]
    chan_data[1] = chan_data_swz[3]
    chan_data[2] = chan_data_swz[0]
    chan_data[3] = chan_data_swz[1]
    if convert_twos:
        for i in range(4):
            chan_data[i] = twos_comp(chan_data[i], bits)

    return chan_data


def save_adc_data(data_dir, file_name, num_repeats = 4, blk_multiples = 64, PLT_ADC=False, scaling=1, ylabel='DN', ax=None):

    # Continuous Graph
    if PLT_ADC:
        plt.ion()
        if ax is None:
            fig, ax = plt.subplots()
        # ax.plot(data)
        ax.set_xlabel("Time")
        ax.set_ylabel(ylabel)
    sample_rate = 2e-7  # 1 / 5e6
    chunk_size = int(ddr.parameters["BLOCK_SIZE"] * blk_multiples / (4*2))  # readings per ADC
    repeat = 0
    adc_readings = chunk_size*num_repeats

    print(f'Reading {adc_readings*2/1024} kB per ADC channel for a total of {adc_readings*sample_rate*1000} ms of data')

    full_data_name = os.path.join(data_dir, file_name)
    try:
        os.remove(full_data_name)
    except OSError:
        pass

    ddr.set_adc_read()  # enable data into the ADC reading FIFO
    time.sleep(adc_readings*sample_rate*2)


    # TODO: the first FIFO (or 1/2 FIFO) worth of data might be stale
    # Save ADC DDR data to a file
    with h5py.File(full_data_name, "w") as file:
        data_set = file.create_dataset("adc", (4, chunk_size), maxshape=(4, None))
        while repeat < num_repeats:
            d, bytes_read_error = read_adc(ddr, blk_multiples)
            chan_data = deswizzle(d)
            chan_stack = np.vstack((chan_data[0], chan_data[1], chan_data[2], chan_data[3]))
            if PLT_ADC:
                if repeat == 0:
                    t = np.arange(len(chan_data[1])) * sample_rate
                ax_hdl = ax.plot(t, chan_data[0]*scaling, color="blue", scalex=True, scaley=False)
                ax.set_ylim(bottom=-(2 ** 15)*scaling, top= (2 ** 15)*scaling, auto=False)
                plt.draw()
                plt.pause(0.001)

            repeat += 1
            if repeat == 0:
                data_set[:] = chan_stack
            else:
                data_set[:, -chunk_size:] = chan_stack
            if repeat < num_repeats:
                if PLT_ADC:
                    ax_hdl[0].remove()
                data_set.resize(data_set.shape[1] + chunk_size, axis=1)

    print(f'Done with ADC reading: saved as {full_data_name}')
    return chan_data



def noise_measurement(rf, idx=0, PLT=True):

    file_name = f'noise_{idx}'
    adc_chan = 0

    set_cmd_cc(cmd_val = 0x0000, cc_scale = 0, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=0)
    time.sleep(0.04) # a few periods to settle after stoping and starting CMD voltage
    save_adc_data(data_dir, file_name + '.h5', num_repeats = 4)

    t, adc_data = read_h5(data_dir, file_name + '.h5', chan_list=[0, 3])

#    for adc_chan in [0,3]:
    for adc_chan in [0]:
        if PLT:
            fig,ax=plt.subplots()
            idx = idx_timerange(t, 100e-6, 100e-3) # entire range
            lbl = ''
            ax.plot((t[idx])*1e6, adc_data[adc_chan][idx], marker = '+', label=lbl)
            ax.set_xlabel('t [$\mu$s]')
            ax.set_ylabel('$I_m$ [DN]')
            ax.legend()

        noise_dn = np.std(adc_data[adc_chan][idx])
        adc_data_filter = butter_lowpass_filter(adc_data[adc_chan][idx], cutoff=3e3, fs=FS, order=5)
        noise_nA = noise_dn/dn_per_nA(rf)
        noise_nA_filter = np.std(adc_data_filter)/dn_per_nA(rf)

        print('ADC chan:{} Noise {:0.2f}; {:0.2f} nA (full BW and 3 kHz cutoff) noise in {:0.2f} DN'.format(adc_chan, noise_nA, noise_nA_filter, noise_dn))

    return noise_nA, noise_nA_filter

output = pd.DataFrame()
data = {}
for rf in [10, 100, 332]:
    for passive in [0,1]:
        log_info, config_dict = clamp.configure_clamp(
            ADC_SEL="CAL_SIG1",
            DAC_SEL="drive_CAL2",
            CCOMP=47,
            RF1=2.1,  # feedback circuit
            ADG_RES=rf,
            PClamp_CTRL=passive,
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
        time.sleep(0.1)
        nA, nA_filter = noise_measurement(rf*1e3)
        data['rf'] = rf
        data['nA'] = nA
        data['nA_filter'] = nA_filter
        data['passive'] = passive
        output = output.append(data, ignore_index=True)

output.to_csv(os.path.join(data_dir, 'noise_measurement' + '.csv'))