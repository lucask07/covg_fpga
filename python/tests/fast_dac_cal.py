"""This script uses a multimeter to calibrate the fast DACs 
2024/05/02

"""
import os
import sys
from time import sleep
import datetime
import time
import atexit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 

from pyripherals.utils import to_voltage, from_voltage, create_filter_coefficients
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3

# Defines data_dir_covg and adds the path to boards.py into the sys.path 
from setup_paths import *

from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5, separate_ads_sequence
from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp, Vsense
from calibration.electrodes import EphysSystem
from observer import Observer
from filters.filter_tools import butter_lowpass_filter

from pyabf.abfWriter import writeABF1 
from pyabf.tools.covg import interleave_np

from instrbuilder.instrument_opening import open_by_name 
dmm = open_by_name('my_multi') # use for reading DC values of fast DAC outputs

DAC_FS = 2.5e6
FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6

eps = Endpoint.endpoints_from_defines
pwr_setup = "3dual"
# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)
if pwr_setup == "3dual" or pwr_setup == 'boland_lab' or pwr_setup=="3dual_16v5neg":
    atexit.register(pwr_off, [dc_pwr])
else:
    atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)

# turn on the 7V
if pwr_setup == "3dual" or pwr_setup=="3dual_16v5neg":
    dc_pwr.set("out_state", "ON", configs={"chan": 1})
elif pwr_setup == 'boland_lab':
    dc_pwr.set("out_state", "ON", configs={"chan": 3})

if pwr_setup == "3dual" or pwr_setup=="3dual_16v5neg":
    # turn on the +/-16.5 V input
    for ch in [2, 3]:
        dc_pwr.set("out_state", "ON", configs={"chan": ch})
elif pwr_setup == "boland_lab":
    # turn on the +/-16.5 V input
    for ch in [1, 2]:
        dc_pwr.set("out_state", "ON", configs={"chan": ch})        
else:
    for ch in [1, 2]:
        dc_pwr2.set("out_state", "ON", configs={"chan": ch})

sleep(1)
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

sleep(0.2)
# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

# configure the SPI debug MUXs
gpio = Daq.GPIO(f)
gpio.spi_debug("ads")
gpio.ads_misc("convst")  # to check sample rate of ADS

# -------- configure the ADS8686
ads_voltage_range = 5  # need this for to_voltage later 
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range) 
ads.set_lpf(376)
ads_sequencer_setup = [('1', '0'), ('2', '2')] # using clamp at socket 3; misses I (voltage) 

codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge() # 1 MSPS rate 
ads.set_fpga_mode()

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

dac_range = 5
dac_scale = 2**14*4.0/(10/(dac_range*2)) # DN/Volt TODO: verify this  # /0.58 ? 

# fast DAC channels setup
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write(int(0x2000))
    daq.DAC[i].set_data_mux("host")
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

dac_gain = []
dac_val = []
dmm_v = []

# pick a single channel 
ch_test = 1

gain_dict = daq.parameters['dac_gain_fs']
gain_dict.pop(200) # remove the values in mV since duplicated and confusing 
gain_dict.pop(500)

# sweep through the dac_gains 
for k in gain_dict:
    daq.set_dac_gain(ch_test, k)
    daq.set_dac_gain(0, k) # DAC channels for gains are swapped! use 0 to change the gain for 1

    print(f'DAC gain: {k}')
    daq.DAC[ch_test].write(0)
    sleep(0.2)
    # measure over a few cmd value ranges 
    for cv in [0, 0x0800, 0x1000, 0x1fd0, 0x1ffe, 0x1fff, 0x2000, 0x2001, 0x2002, 0x2020, 0x3000, 0x3800, 0x3fff]:
        daq.DAC[ch_test].write(cv)
        sleep(0.02)
        v = dmm.get('meas_volt', configs={'ac_dc': 'DC'})
        print(f'Measured {v}')
        dac_gain.append(k)
        dac_val.append(cv)
        dmm_v.append(v)

data_dir = data_dir.replace('clamp', 'calibration')
try:
    os.makedirs(data_dir)
except:
    print(f'Will not make directory: {data_dir}')

df = pd.DataFrame( {'gain': dac_gain, 'dac_value': dac_val, 'v_meas': dmm_v})
df.to_csv(os.path.join(data_dir, f'DAC_calibration_ch{ch_test}.csv'), index=False)

gains = []
slope = []
fixed_offset = 0x2000
dac_offset = []
meas_offset = []

for gain_val in gain_dict:
    fig, ax=plt.subplots()
    x = df[df.gain==gain_val].dac_value
    y = df[df.gain==gain_val].v_meas
    ax.plot(x, y, marker='o')
    ax.set_xlabel('DAC')
    ax.set_ylabel('V')

    idx = (x > 0) & (x < 0x3fff)
    m, b = np.polyfit(x[idx] - fixed_offset, y[idx], 1) # adjust for DAC offset 
    print(f'Calibration slope {m}, calibration offset {b}')

    gains.append(gain_val)
    slope.append(m)
    dac_offset.append(fixed_offset)
    meas_offset.append(b)

    calc_gain = 1/(2**14/(gain_val*2))
    print(f'Measured cal {m}; calculated calibration {calc_gain}; percent error {100*(m-calc_gain)/m}')

dfs = pd.DataFrame( {'gain': gains, 'slope': slope, 'fixed_offset': meas_offset})
dfs.to_csv(os.path.join(data_dir, f'DAC_calibration_ch{ch_test}_summaryfits.csv'), index=False)