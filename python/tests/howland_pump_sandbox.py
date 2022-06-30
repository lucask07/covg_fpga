"""
This code demonstrates the Howland current pump on the DAQ board
configure EN_IPUMP and ISEL
measures at DAC2_CAL0
which corresponds to DAC_gp[1] channel 0

R = 2.358 kOhm 

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

import os
import sys
import logging
from interfaces.interfaces import FPGA, Endpoint
from interfaces.peripherals.DDR3 import DDR3
from interfaces.utils import from_voltage, to_voltage
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

# constants 
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

pwr_setup = "3dual"
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

# two bits to enable Howland pump (EN_IPUMP)
f.set_wire_bit(eps['GP']['CURRENT_PUMP_ENABLE'].address,
               eps['GP']['CURRENT_PUMP_ENABLE'].bit_index_low)
f.set_wire_bit(eps['GP']['CURRENT_PUMP_ENABLE'].address,
               eps['GP']['CURRENT_PUMP_ENABLE'].bit_index_high)


pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)

ad7961s = daq.ADC
ads = daq.ADC_gp # ADS8686
ad7961s[0].reset_wire(1) # keep reset 

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

# configure I/O expanders 
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

daq.set_isel(port=2, channels=[0,1])

# configure clamp board Utility pin to be the offset voltage for the feedback
# at this point the slow DA Ccan be set by the host 
for i in range(2):
    # Reset the Wishbone controller and SPI core
    daq.DAC_gp[i].set_ctrl_reg(daq.DAC_gp[i].master_config)
    daq.DAC_gp[i].set_spi_sclk_divide()
    daq.DAC_gp[i].filter_select(operation="clear")
    daq.DAC_gp[i].set_data_mux("host")
    daq.DAC_gp[i].set_config_bin(0x00)
    print('Outputs powered on')

#DAC2_CAL0, DAC2_CAL1 
daq.DAC_gp[1].write_voltage(1.457, 0) 
daq.DAC_gp[1].write_voltage(1.25, 1) 


daq.DAC_gp[1].set_gain(2)
