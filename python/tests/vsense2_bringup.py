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
import os
import sys
from time import sleep
import datetime
import time
import atexit
import numpy as np
import matplotlib.pyplot as plt

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
from boards import Daq, Clamp, Vsense2
from calibration.electrodes import EphysSystem
from observer import Observer
from filters.filter_tools import butter_lowpass_filter

from pyabf.abfWriter import writeABF1 
from pyabf.tools.covg import interleave_np

from instrbuilder.instrument_opening import open_by_name 
osc = open_by_name('msox_scope')


DAC_FS = 2.5e6
FS = 5e6
SAMPLE_PERIOD = 1/FS
ADS_FS = 1e6
dc_mapping = {'bath': 0, 'clamp': 1, 'vsense': 3, 'guard': 2} 
DC_NUMS = [0, 1, 3]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3

eps = Endpoint.endpoints_from_defines
pwr_setup = "two_supplies" # at the system without the Faraday cage and two DP832s

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
else:
	dc_pwr.set("out_state", "ON", configs={"chan": 1})	

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

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamps = [None] * 4
for dc_num in DC_NUMS:
    clamp = Clamp(f, dc_num=dc_num, version=2)
    print(f'Clamp {dc_num} Init'.center(35, '-'))
    clamp.init_board()
    clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
    clamps[dc_num] = clamp

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
gain2 = vsense.gain_dict[41]
vsense.setOffsetVoltage(0)
vsense.set_gain(gain1, gain2) #requires DAC offset voltage set before running function. Could be combined easily.

#test UID chip
vsense.UID_read_test()
    
#TODO:
# UID serial number just 32 1's
# I2C pot has no pyriphreal

#Done
#write to DAC 
#test DAC offset circuit with multimeter
#write to TCA outputs
#removed the jumper to neg capacitance circuit
#gains are validated, they all work. Gain function written and works with gain dict
