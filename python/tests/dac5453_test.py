# AD7961 tests; test pattern and data saved to file
import logging
import sys
import os
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
from instrbuilder.instrument_opening import open_by_name
import atexit
# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == 'covg_fpga':
        interfaces_path = os.path.join(covg_fpga_path, 'python')
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(interfaces_path)

from interfaces.interfaces import AD7961, AD5453, FPGA, Endpoint, disp_device, advance_endpoints_bynum, DDR3
from interfaces.boards import Daq
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
eps = Endpoint.endpoints_from_defines

today = datetime.datetime.today()
# data_dir = '/Users/koer2434/Google Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/ad7961/{}{}{}'.format(today.year,
#                                                                                                                    today.month,
#                                                                                                                    today.day)
# if not os.path.exists(data_dir):
#     os.makedirs(data_dir)

# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply()
atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2)
# turn on the 7V in, but keep +/-16.6 down
dc_pwr.set('out_state', 'ON', configs={'chan': 1})
# turn on the +/-16.5 V input
for ch in [1, 2]:
    dc_pwr2.set('out_state', 'ON', configs={'chan': ch})
######################################
time.sleep(2)

# --------  function generator  --------
fg = open_by_name('new_function_gen')

fg.set('load', 'INF')
fg.set('offset', 2)
fg.set('v', 2)
fg.set('freq', 10e3)
fg.set('output', 'ON')

atexit.register(fg.set, 'output', 'OFF')
######################################

# --------  Set up FPGA  --------
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

# power supply turn on via FPGA enables
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug('dfast0')
gpio.ads_misc('sdoa')  # do not care for this experiment

ddr = DDR3(f)
ddr.reset_fifo()

fdac = []
for i in range(6):
    fdac.append(AD5453(f,
                endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('AD5453'),i),
                channel=i))
    fdac[i].set_spi_sclk_divide()
    fdac[i].set_data_mux('host')
    fdac[i].write_filter_coeffs()
    fdac[i].filter_select(operation='clear')

# fdac[0].set_clk_divider()  # default value is 0xA0 (expect 1.25 MHz, getting 250 kHz, set by SPI SCLK??)

fdac[0].change_filter_coeff(target='passthrough')
fdac[0].write_filter_coeffs()
fdac[0].filter_select(operation='clear')

fdac[1].change_filter_coeff(target='passthrough')
fdac[1].write_filter_coeffs()
fdac[1].filter_select(operation='clear')


# pass through tests - ramp up from mid-scale go to mid-scale then ramp down
for ch in [0, 1]:
    for i in np.arange(0, 0xffff, step=16, dtype=np.int32):
        fdac[ch].write(int(i))

# filter tests using host driven reads
for ch in [0, 1]:
    fdac[ch].filter_select(operation='set')
    fdac[ch].change_filter_coeff(target='500kHz')
    # fdac[ch].change_filter_coeff(target='passthrough')
    fdac[ch].write_filter_coeffs()

for ch in [0, 1]:
    # positive going square wave
    # fill with midscale
    for i in range(200):
        fdac[ch].write(0)
    for i in range(200):
        # positive going step
        fdac[ch].write(0x4000)
    for i in range(200):
        # negative going step
        fdac[ch].write(0xc000)

# both channels simultaneously with different cutoff freq.
fdac[0].change_filter_coeff(target='500kHz')
fdac[0].write_filter_coeffs()

fdac[1].change_filter_coeff(target='100kHz')
fdac[1].write_filter_coeffs()


for k in range(100):
    for i in range(200):
        for ch in [0, 1]:
            # fill with midscale
            fdac[ch].write(0x1000)
    for i in range(200):
        for ch in [0, 1]:
            # positive going square wave
            fdac[ch].write(0x1200)
    for i in range(200):
        for ch in [0, 1]:
            # negative going step
            fdac[ch].write(0x0800)


x = 0x1000*np.sin(np.arange(0,1000)/20) + 0x1000

for i in x:
    fdac[0].write(int(i))
