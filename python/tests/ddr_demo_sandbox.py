"""
This code demonstrates DDR reading and writing. 
Works in a mode with two DDR input buffers and two DDR output buffers. 

Data loaded into DDR for playback (port 1):
* AD5453 DAC and DAC80508 

Data buffered into and then read from DDR (port 2):
 * AD7961 @ 5 MSPS
 * output data to DAC AD5453 (allows for filter tests) @ 2.5 MSPS
 * ADS8686 data @ 1 MSPS
 * Timestamp (clock at 200 MHz)

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

import os
import sys
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
from interfaces.utils import twos_comp, from_voltage
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle as pkl
import h5py
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from analysis.adc_data import read_plot, read_h5, peak_area, get_impulse, im_conv, idx_timerange
from analysis.utils import calc_fft

# constants 
FS = 5e6  # sampling frequency 
dac80508_offset = 0x8000


eps = Endpoint.endpoints_from_defines

data_dir_base = covg_fpga_path
if sys.platform == "linux" or sys.platform == "linux2":
    print('Linux directory not configured... Error')
    pass
elif sys.platform == "darwin":
    print('MAC directory not configured... Error')
    pass
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'covg/data/clamp/{}{:02d}{:02d}')

today = datetime.datetime.today()
data_dir = data_dir_covg.format(
    today.year, today.month, today.day
)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# alternative for Python<3.9
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler("AD7961_test.log", "w", "utf-8")
root_logger.addHandler(handler)


pwr_setup = "3dual"
dc_num = 0  # the Daughter-card channel under test. Order on board from L to R: 1,0,2,3

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
# osc = open_by_name("msox_scope")

# --------  function generator  --------
fg_freq = 10e3
fg_v = 2
fg = open_by_name("new_function_gen")
fg.set("load", "INF")
fg.set("offset", 2)
fg.set("v", fg_v)
fg.set("freq", fg_freq)
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
ads = daq.ADC_gp # ADS8686
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
# TODO: could skip Clamp board setup ... but it is another source of ADC data 
clamp = {}
for dc_num in [0]:
    clamp[dc_num] = Clamp(f, dc_num=dc_num)
    clamp[dc_num].init_board()

    # configure the clamp board, settings default to None so that a setting that is not
    # included is masked and stays the same
    # TODO: configure_clamp errors out if not connected

    log_info, config_dict = clamp[dc_num].configure_clamp(
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

# --------  Initialize fast ADCs  --------
for chan in [0,1,2,3]:
    ad7961s[chan].power_up_adc()  # standard sampling

ad7961s[0].reset_wire(0)
time.sleep(1)

# configure I/O expanders 
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channel 0 and 1
filt_type = '500kHz'
#filt_type = 'passthru'
for i in [0,1,2,3,4,5]:
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="set")
    #daq.DAC[i].filter_select(operation="clear")
    # daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("DDR")
    if i == 0:
        daq.DAC[i].change_filter_coeff(target=filt_type)
    if i == 1:
        daq.DAC[i].change_filter_coeff(target=filt_type)
    if i == 2:
        daq.DAC[i].change_filter_coeff(target=filt_type)
    if i == 3:
        daq.DAC[i].change_filter_coeff(target=filt_type)
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, 500)  # 500 mV full-scale

# daq.DAC[0].set_clk_divider(divide_value=0x50) #TODO: this is no longer used. All timing is from one module

# -------- configure the ADS8686
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(5)
ads.set_lpf(376)
# 4B - clear sine wave set by the Slow DAC
codes = ads.setup_sequencer(chan_list=[('7', '3')])
ads.write_reg_bridge(clk_div=200) # 1 MSPS update rate. Write register for SPI configuration reg. But update rate is controlled by top-level timer
ads.set_fpga_mode()


# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x8)
    daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
    daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
    daq.DAC_gp[dac_gp_ch].set_gain(gain=1, outputs=[4], divide_reference=False)
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

ddr = DDR3(f, data_version='TIMESTAMPS')

def ddr_write_setup():
    ddr.set_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()
    ad7961s[0].reset_trig()

def ddr_write_finish():
     # reenable both DACs
    ddr.set_adc_dac_simultaneous()  # enable DAC playback and ADC writing to DDR

FAST_DAC_FREQ = 7e3
for i in range(7):
    ddr.data_arrays[i], fdac_freq = ddr.make_sine_wave(0x800, FAST_DAC_FREQ,
                                        offset=0x1000)

# ---------- configure "slow" DAC DAC80508
sdac_amp_volt = 1
target_freq_sdac = 12000.0
sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

# Data for the 2 DAC80508 "Slow DACs"
sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq_sdac, offset=dac80508_offset)

# Specify output channel for DAC80508
sdac_1_out_chan = 5
sdac_2_out_chan = 5

# Clear bits in the FDAC DDR stream that store the slow DAC channel
for i in range(6):
    ddr.data_arrays[i] = np.bitwise_and(ddr.data_arrays[i], 0x3fff)

# Load data into DDR
# Set channel bits
ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

# load slow DAC sine-wave in DDR channels 7 and 8 
for i in range(2):
    ddr.data_arrays[i + 6] = sdac_sine

ddr_write_setup()
g_buf = ddr.write_channels()
ddr.reset_mig_interface()
ddr_write_finish()

CHAN_UNDER_TEST = 0
output = pd.DataFrame()
data = {}
file_name = 'test'
data['filename'] = file_name
output = output.append(data, ignore_index=True)

print(output.head())
output.to_csv(os.path.join(data_dir, file_name + '.csv'))
idx = 0

REPEAT = True
if REPEAT:  # to repeat data capture without rewriting the DAC data
    ddr.clear_adc_read()
    ddr.clear_adc_write()

    ddr.reset_fifo(name='ADC_IN')
    ddr.reset_fifo(name='ADC_TRANSFER')
    ddr.reset_mig_interface()

    ddr_write_finish()
    time.sleep(0.01)

# saves data to a file; returns to teh workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 8,
                          blk_multiples=40) # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file 
adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data)

# Shorter data sequence, just one of the repeats
# adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data_one_repeat)

t = np.arange(0,len(adc_data[0]))*1/FS

crop_start = 0 # placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

# fast ADC. AD7961
for ch in range(4):
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

# ADS8686 
t_ads = t[crop_start::5] # ADS8686 data is saved every fifth 5 MSPS tick
fig,ax=plt.subplots()
ax.plot(t_ads*1e6, ads['A'], marker = '+', label = 'ADS: A')
ax.plot(t_ads*1e6, ads['B'], marker = '+', label = 'ADS: B')
ax.legend()
ax.set_xlabel('s [us]')
ax.set_title('ADS8686 data')

# ----- Check frequency of results ----------
def check_fft(t, y, predicted_freq):
    ffreq, famp, max_freq = calc_fft(y, 1/(t[1]-t[0]))
    print(f'Frequency of maximum amplitude {max_freq} [Hz]')
    print(f'Predicted frequency: {predicted_freq}')
    rms = np.std(y)
    print(f'RMS amplitude: {rms}, peak amplitude: {rms*1.414}')
    print('-'*40)

# check AD7961 channel 0. Frequency from clamp board
print('FFT of AD7961 channel 0')
check_fft(t, adc_data[0], FAST_DAC_FREQ)

# check AD7961 channel 1. Frequency from function generator 
print('FFT of AD7961 channel 1')
check_fft(t, adc_data[1], fg_freq)

# check ADS8686 channel B. Frequency from ADC80508
print('FFT of ADS8686 channel B: set by slow DAC')
check_fft(t_ads, ads['B'], target_freq_sdac)
