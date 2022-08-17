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

Connectivity:
 * Daughtercard position 0 to clamp board (v2) + model cell
 * Daughtercard position 1 to 2nd clamp board (v2) + model cell
 * Position 2: empty
 * Position 3 daughter card with just differential buffer connected to function generator (note this is showing as adc channel 2)

Daughtercard 0: 
* GP_ADC_0: pin 9 --> CAL_ADC
* GP_ADC_1: pin 19 --> AMP_OUT
* DAC1_CAL0: pin 3 --> CAL_DAC

Daughtercard 1:
* GP_ADC_8: pin 9 --> CAL_ADC
* GP_ADC_2: pin 19 --> AMP_OUT
* DAC1_CAL1: pin 3 --> CAL_DAC

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

import os
import sys
import logging
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3
from pyripherals.utils import  to_voltage, from_voltage, create_filter_coefficients
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


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


from boards import Daq, Clamp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from analysis.adc_data import read_h5, separate_ads_sequence
from analysis.utils import calc_fft

# constants 
FS = 5e6  # sampling frequency 
dac80508_offset = 0x8000
FS_ADS = 1e6

eps = Endpoint.endpoints_from_defines

data_dir_base = covg_fpga_path
if sys.platform == "linux" or sys.platform == "linux2":
    print('Linux directory not configured... Error')
    pass
elif sys.platform == "darwin":
    print('MAC directory not configured... Error')
    pass
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'covg/data/ddr_demo/{}{:02d}{:02d}')

today = datetime.datetime.today()
data_dir = data_dir_covg.format(
    today.year, today.month, today.day
)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

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
fg_freq = 160e3
fg_v = 2
fg = open_by_name("new_function_gen")
fg.set("load", "INF")
fg.set("offset", 2)
fg.set("v", fg_v)
fg.set("freq", fg_freq)
fg.set("function", "SIN")
fg.set("output", "ON")

atexit.register(fg.set, "output", "OFF")

# Initialize FPGA
f = FPGA()
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
for dc_num in [0,1]:
    clamp[dc_num] = Clamp(f, dc_num=dc_num)
    clamp[dc_num].init_board()
    clamp[dc_num].DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
    # configure the clamp board, settings default to None so that a setting that is not
    # included is masked and stays the same
    # TODO: configure_clamp errors out if not connected

    log_info, config_dict = clamp[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="drive_CAL1",
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

time.sleep(0.1)
ad7961s[0].reset_wire(0)
time.sleep(1)

# configure I/O expanders 
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
    daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

# -------- configure the ADS8686
ads_voltage_range = 5
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range)
ads.set_lpf(376)
#ads_sequencer_setup = [('0', '0'), ('1', '1')]
ads_sequencer_setup = [('1', '0')]

codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge(clk_div=200) # 1 MSPS update rate. Write register for SPI configuration reg. But update rate is controlled by top-level timer
ads.set_fpga_mode()

# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x2)
    daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
    daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
    daq.DAC_gp[dac_gp_ch].set_data_mux('host')
    # daq.DAC_gp[dac_gp_ch].set_gain(gain=1, outputs=[4], divide_reference=False)
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

daq.set_isel(port=1, channels=None)
daq.set_isel(port=2, channels=None)

ad7961s[0].reset_trig()

# ---- Configure DDR data 
ddr = DDR3(f, data_version='TIMESTAMPS')

FAST_DAC_FREQ = 7e3
fast_dac_amp = 0x400 # 0x040
dac_offset = 0x2000
step_len = 8000

#for i in range(6):
    #ddr.data_arrays[i], fdac_freq = ddr.make_sine_wave(fast_dac_amp, FAST_DAC_FREQ,
    #                                    offset=0x1000)

# CMD voltage for Daughter card 0,1
ddr.data_arrays[1] = ddr.make_step(low=dac_offset - int(fast_dac_amp),
                                               high=dac_offset + int(fast_dac_amp),
                                               length=step_len)  # 1.6 ms between edges

if 0: # use Daughtercard 1 just for GP DAC to GP ADC via the calibration line 
    ddr.data_arrays[3] = ddr.make_step(low=dac_offset - int(fast_dac_amp),
                                                   high=dac_offset + int(fast_dac_amp),
                                                   length=step_len)  # 1.6 ms between edges

# ---------- configure "slow" DAC DAC80508
SLOW_DAC = True
if SLOW_DAC:
    sdac_amp_volt = 1 # 1
    target_freq_sdac = 12000.0
    sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

    # Data for the 2 DAC80508 "Slow DACs"
    sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq_sdac, offset=dac80508_offset)

    # Specify output channel for DAC80508
    sdac_1_out_chan = 1
    sdac_2_out_chan = 0

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

ddr.write_setup()
block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
ddr.reset_mig_interface()
ddr.write_finish()

file_name = 'test'
idx = 0

REPEAT = False
if REPEAT:  # to repeat data capture without rewriting the DAC data
    ddr.clear_adc_read()
    ddr.clear_adc_write()
    ddr.clear_dac_write()

    ddr.reset_fifo(name='ALL')
    # ddr.reset_fifo(name='ADC_TRANSFER')
    ddr.reset_mig_interface()

    ddr_write_finish()
    time.sleep(0.01)
    idx = idx + 1

# saves data to a file; returns to teh workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 8,
                          blk_multiples=40) # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file 
adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = ddr.data_to_names(
    chan_data)

############### extract the ADS data just for the last run and plot as a demonstration ############
ads_data_v = {}
for letter in ['A', 'B']:
    ads_data_v[letter] = np.array(to_voltage(
        ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
total_seq_cnt[::2] = ads_seq_cnt[0]
total_seq_cnt[1::2] = ads_seq_cnt[1]
ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)
#########

# ----- Check frequency of results ----------
def check_fft(t, y, predicted_freq):
    ffreq, famp, max_freq = calc_fft(y, 1/(t[1]-t[0]))
    print(f'Frequency of maximum amplitude {max_freq} [Hz]')
    print(f'Predicted frequency: {predicted_freq}')
    rms = np.std(y)
    print(f'RMS amplitude: {rms}, peak amplitude: {rms*1.414}')
    print('-'*40)

t = np.arange(0,len(adc_data[0]))*1/FS
crop_start = 0 # placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

# DACs 
t_dacs = t[crop_start::2]  # fast DACs are saved every other 5 MSPS tick

for dac_ch in range(4):
    fig,ax=plt.subplots()
    y = dac_data[dac_ch][crop_start:]
    lbl = f'Ch{dac_ch}'
    ax.plot(t_dacs*1e6, y, marker = '+', label = lbl)
    print(f'Min {np.min(y[2:])}, Max {np.max(y)}') # skip the first 2 readings which are 0
    ax.legend()
    ax.set_title('Fast DAC data')
    ax.set_xlabel('s [us]')


# fast ADC. AD7961
adc_data_v = {}
for ch in range(4):
    adc_data_v[ch] = to_voltage(adc_data[ch], num_bits=16, voltage_range=4.096, use_twos_comp=True)
    fig,ax=plt.subplots()
    lbl = f'Ch{ch}'
    ax.plot(t*1e6, adc_data_v[ch], marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Fast ADC data')
    ax.set_xlabel('s [us]')

# ADS8686 
fig,ax=plt.subplots()
for chan, ch_idx in [('A',1), ('B',0)]:
    y = ads_separate_data[chan][int(ch_idx)]
    t_ads = np.arange(0,len(y))*(1/FS_ADS)*len(ads_sequencer_setup)
    ax.plot(t_ads*1e6, y, marker = '+', label = f'ADS: {chan}')
    # check ADS8686
    print('FFT of ADS8686')
    check_fft(t_ads, y, target_freq_sdac)

ax.legend()
ax.set_xlabel('s [us]')
ax.set_title('ADS8686 data')

# check AD7961 channel 0. Frequency from clamp board
print('FFT of AD7961 channel 0')
check_fft(t, adc_data_v[0], FAST_DAC_FREQ)

# check AD7961 channel 2. Frequency from function generator 
print('FFT of AD7961 channel 2')
check_fft(t, adc_data_v[2], fg_freq)

