"""
Test of AD7961 and DDR transfer of this data 
Function generator connected to one channel specified in the script

With Sine Wave for verification check:
1) DN vs. voltage 
2) Frequency 

With Step function check:
1) DN vs. voltage 
2) Frequency 
3) Noise away from edges 

Realtime plots and maximum record length 

1) check timestamps 

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
import logging
import os
import sys
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import h5py
from pyripherals.utils import from_voltage
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


from boards import Daq, Clamp
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from analysis.adc_data import read_plot, read_h5, peak_area, get_impulse, im_conv, idx_timerange
from analysis.utils import calc_fft


FS = 5e6
SAMPLE_PERIOD = 1/FS
dac80508_offset = 0x8000
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
handler = logging.FileHandler("AD7961_test.log", "w", "utf-8")
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

# --------  Initialize ADCs  --------
for chan in [0,1,2,3]:
    ad7961s[chan].power_up_adc()  # standard sampling

ad7961s[0].reset_wire(0)
time.sleep(1)

for chan in [0,1,2,3]:
    ad7961s[chan].reset_fifo()

# configure I/O expanders 
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channel 0 and 1
filt_type = '500kHz'
#filt_type = 'passthru'
for i in [0,1,2,3,4,5]:
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    # daq.DAC[i].filter_select(operation="set")
    daq.DAC[i].filter_select(operation="clear")
    # daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("DDR")
    if i == 0:
        daq.DAC[i].change_filter_coeff(target=filt_type)
        #daq.DAC[i].set_data_mux("ad7961_ch1")
    if i == 1:
        daq.DAC[i].change_filter_coeff(target=filt_type)
        #daq.DAC[i].set_data_mux("ad7961_ch1")
    if i == 2:
        daq.DAC[i].change_filter_coeff(target=filt_type)
        #daq.DAC[i].filter_select(operation="clear")
    if i == 3:
        daq.DAC[i].change_filter_coeff(target=filt_type)
        #daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, 500)  # 500 mV full-scale
    print('Checking filter settings')
    daq.DAC[0].read_coeff_debug()

# 0xA0 = 1.25 MHz, 0x50 = 2.5 MHz
daq.DAC[0].set_clk_divider(divide_value=0x50)
print('Checking filter settings')
daq.DAC[0].read_coeff_debug()

ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(5)
ads.set_lpf(376)
# codes = ads.setup_sequencer(chan_list=[('FIXED', 'FIXED')])
# 4B - clear sine wave set by the Slow DAC
codes = ads.setup_sequencer(chan_list=[('4', '4')])
ads.write_reg_bridge(clk_div=200) # 1 MSPS update rate 
ads.set_fpga_mode()


# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x8)
    daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
    daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
    daq.DAC_gp[dac_gp_ch].set_gain(gain=1, outputs=[4], divide_reference=False)
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

ddr = DDR3(f, data_version='TIMESTAMPS')
# ddr = DDR3(f, data_version='ADC_NO_TIMESTAMPS')
NUM_CHAN = 8

def ddr_write_setup():
    # adjust the DDR settings of both DACs
    # quiet both DACs
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()

def ddr_write_finish():
     # reenable both DACs
    ddr.set_dac_read()  # enable DAC playback and ADC reading
    ddr.set_adc_write()

def read_adc(ddr, blk_multiples=2048):

    t, bytes_read_error = ddr.read_adc(  # just reads from the block pipe out
        sample_size=ddr.parameters["BLOCK_SIZE"] * blk_multiples
    )
    d = np.frombuffer(t, dtype=np.uint8).astype(np.uint32)
    print(f'Bytes read: {bytes_read_error}')
    return d, bytes_read_error


def save_adc_data(data_dir, file_name, num_repeats = 4, blk_multiples = 40, 
                    PLT_ADC=False, scaling=1, ylabel='DN', ax=None):

    # Continuous Graph
    if PLT_ADC:
        plt.ion()
        if ax is None:
            fig, ax = plt.subplots()
        # ax.plot(data)
        ax.set_xlabel("Time")
        ax.set_ylabel(ylabel)
    chunk_size = int(ddr.parameters["BLOCK_SIZE"] * blk_multiples / (NUM_CHAN*2))  # readings per ADC
    print(f'Anticipated chunk size {chunk_size}')
    repeat = 0
    adc_readings = chunk_size*num_repeats

    print(f'Reading {adc_readings*2/1024} kB per ADC channel for a total of {adc_readings*SAMPLE_PERIOD*1000} ms of data')

    full_data_name = os.path.join(data_dir, file_name)
    try:
        os.remove(full_data_name)
    except OSError:
        pass

    ddr.set_adc_read()  # enable data into the ADC reading FIFO
    time.sleep(adc_readings*SAMPLE_PERIOD*2)

    # Save ADC DDR data to a file
    with h5py.File(full_data_name, "w") as file:
        data_set = file.create_dataset("adc", (NUM_CHAN, chunk_size), maxshape=(NUM_CHAN, None))
        while repeat < num_repeats:
            d, bytes_read_error = read_adc(ddr, blk_multiples)
            if ddr.parameters['data_version'] == 'ADC_NO_TIMESTAMPS':
                chan_data = ddr.deswizzle(d)
                timestamp = np.nan
                read_check = np.nan
                dac_data = np.nan
            elif ddr.parameters['data_version'] == 'TIMESTAMPS':
                chan_data, timestamp, read_check, dac_data, ads = ddr.deswizzle(d)

            if NUM_CHAN==4:
                chan_stack = np.vstack((chan_data[0], chan_data[1], chan_data[2], chan_data[3]))

            if NUM_CHAN==8:
                chan_stack = np.vstack((chan_data[0], chan_data[1], chan_data[2], chan_data[3],
                                        chan_data[4], chan_data[5], chan_data[6], chan_data[7]))
            if PLT_ADC:
                if repeat == 0:
                    t = np.arange(len(chan_data[1])) * SAMPLE_PERIOD
                ax_hdl = ax.plot(t, chan_data[0]*scaling, color="blue", scalex=True, scaley=False)
                ax.set_ylim(bottom=-(2 ** 15)*scaling, top= (2 ** 15)*scaling, auto=False)
                plt.draw()
                plt.pause(0.001)

            repeat += 1
            if repeat == 0:
                print(f'Chunk size by chan data size {chunk_size}')
                data_set[:] = chan_stack
            else:
                data_set[:, -chunk_size:] = chan_stack
            if repeat < num_repeats:
                if PLT_ADC:
                    ax_hdl[0].remove()
                data_set.resize(data_set.shape[1] + chunk_size, axis=1)


    print(f'Done with ADC reading: saved as {full_data_name}')
    return chan_data, timestamp, read_check, dac_data, ads

for i in range(7):
    # ddr.data_arrays[i] = ddr.make_ramp(start=2**10 + 64*i,
    #                                    stop=2**14-1,
    #                                    step=1)
    # ddr.data_arrays[i] = ddr.make_step(low=2**7 + 64*i,
    #                                    high=2**13,
    #                                    length=200)

    # ddr.data_arrays[i] = ddr.make_step(low=2**7,
    #                                 high=2**13,
    #                                 length=200)
    ddr.data_arrays[i] = ddr.make_sine_wave(0x800, 5e3,
                                        offset=0x1000)[0]


# FDAC: 1V 1KHz sine wave; SDAC: 1V 1KHz sine wave
sdac_amp_volt = 1
target_freq = 12000.0
sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

# Data for the 2 DAC80508 "Slow DACs"
sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq, offset=dac80508_offset)

# Specify output channel for DAC80508
sdac_1_out_chan = 5
sdac_2_out_chan = 5

# Clear channel bits
for i in range(6):
    ddr.data_arrays[i] = np.bitwise_and(ddr.data_arrays[i], 0x3fff)

# Load data into DDR
# Set channel bits
ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

for i in range(2):
    ddr.data_arrays[i + 6] = sdac_sine

ddr_write_setup()
g_buf = ddr.write_channels()
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
PAUSE = False
if REPEAT:
    ddr.clear_adc_read()
    ddr.clear_adc_write()

    ddr.reset_fifo(name='ADC_IN')
    ddr.reset_fifo(name='ADC_TRANSFER')
    ddr.reset_mig_interface()

    ddr.set_adc_write()
    time.sleep(0.01)

if PAUSE:
    time.sleep(0.01)

for i in range(6):
    daq.DAC[i].filter_select(operation="set")
chan_data, timestamp, read_check, dac, ads = save_adc_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 8,
                                                            blk_multiples=40) # blk multiples multiple of 10

crop_start = 0 
print(f'Timestamp spans {1/FS*(timestamp[-1] - timestamp[0])} [ms]')

t = np.arange(0,len(chan_data[0]))*1/FS

# DACs from ADC ch1 
t_dacs = t[crop_start::2]

for dac_ch in range(4):
    fig,ax=plt.subplots()
    y = dac[dac_ch][crop_start:]
    lbl = f'Ch{dac_ch}'
    ax.plot(t_dacs*1e6, y, marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Filtered ADC data')

fig,ax=plt.subplots()
for dac_ch in [2,3]:
    y = dac[dac_ch][crop_start:]
    if dac_ch == 2:
        lbl = 'Filtered: ch2'
    if dac_ch == 3:
        lbl = 'passthru: ch3'
    ax.plot(t_dacs*1e6, y, marker = '+', label = lbl)
ax.legend()
ax.set_title('Filtered DDR data')

t_ads = t[crop_start::5]
fig,ax=plt.subplots()
ax.plot(t_ads*1e6, ads['A'], marker = '+', label = 'ADS: A')
ax.plot(t_ads*1e6, ads['B'], marker = '+', label = 'ADS: B')
ax.legend()
ax.set_xlabel('s [us]')

"""
for CHAN_UNDER_TEST in range(8):
    t, adc_data = read_h5(data_dir, file_name=file_name.format(idx) + '.h5', chan_list=[CHAN_UNDER_TEST])

    fig,ax=plt.subplots()
    t = t[crop_start:]
    y = adc_data[CHAN_UNDER_TEST][crop_start:]
    ax.plot(t*1e6, y, marker = '+')
    ax.set_title(f'Chan #: {CHAN_UNDER_TEST}')

    ffreq, famp, max_freq = calc_fft(y, 1/(t[1]-t[0]))
    print(f'Frequency of maximum amplitude {max_freq} [Hz]')
    rms = np.std(y)
    print(f'RMS amplitude: {rms}, peak amplitude: {rms*1.414}')
"""