"""Guess tolerance for DAC80508_ADS8686_test.py

The DAC80508_ADS8686_test.py tests use a tolerance to determine whether the
voltage output by the DAC80508 and read by the ADS8686 is close enough to the
intended voltage to pass. Assuming everything is working correctly, this
script gives a tolerance based on the error measured at voltages near 5V.
Edit the 'tolerance' variable near the top of the DAC80508_ADS8686_test.py
file to change the tolerance.

May 2022
Abe Stroschein, ajstroschein@stthomas.edu
"""

import os
import sys
import time
from pyripherals.core import FPGA
from pyripherals.peripherals.DAC80508 import DAC80508
from pyripherals.peripherals.ADS8686 import ADS8686
from pyripherals.utils import to_voltage


# The boards.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
cwd = os.getcwd()
if 'covg_fpga' in cwd:
    covg_fpga_index = cwd.index('covg_fpga')
    covg_fpga_path = cwd[:covg_fpga_index + len('covg_fpga') + 1]
else:
    print('covg_fpga folder not found. Please navigate to the covg_fpga folder.')
    assert False
boards_path = os.path.join(covg_fpga_path, 'python')
sys.path.append(boards_path)

from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq


pwr_setup = '3dual'
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)  # 7V and +/-16.5V, None
dac_out = 7
ads_in = 7

NUM_REPEATS = 100    # Number of times to get the tolerance
voltage = 5.0   # 5.0 Volts


f = FPGA()
f.init_device()
# Power on
pwr = Daq.Power(f)
pwr.all_off()
# Configure and turn on power supplies
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)
dc_pwr.set("out_state", "ON", configs={"chan": 1})  # +7V
for ch in [2, 3]:
    dc_pwr.set("out_state", "ON", configs={"chan": ch})  # +/- 16.5V

for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
gpio.spi_debug('ads')
gpio.ads_misc('convst')

dac = DAC80508(fpga=f)
dac.set_spi_sclk_divide(0x8)
dac.set_ctrl_reg(0x3218)
dac.set_config_bin(0x00)

ads = ADS8686(fpga=f)
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(5)
ads.set_lpf(376)
codes = ads.setup_sequencer(chan_list=[(str(ads_in), 'FIXED')])
print(f'Setup Sequencer Codes: {codes}')
ads.write_reg_bridge()
ads.set_fpga_mode()

# The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
# adjusted by the gain of the output and whether the internal reference is
# divided by 2 or not.
gain_info = dac.write_voltage(
    voltage=voltage, outputs=dac_out, auto_gain=True)

# Make sure the ADS8686 is giving output before we calculate tolerance
# DAC80508_ADS8686_test.py uses a 23 second delay, so that will be our maximum wait
print('Waiting for ADS8686 (maximum wait 23 seconds)...')
for i in range(23):
    if ads.read_last()['A'][0] == 0:
        time.sleep(1)
if ads.read_last()['A'][0] == 0:
    print('WARNING: reading 0 from ADS8686. Tolerance may be wrong.')

print(f'Getting tolerance ({NUM_REPEATS} repeats)...')
tolerance = 0
for i in range(NUM_REPEATS):
    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    # We double the range used in the to_voltage calculation to account for
    # both +/- sides of the range.
    # Ex. set_range(5) == +/-5V which spans a total of 10V
    read = to_voltage(data=read_data, num_bits=ads.num_bits,
                        voltage_range=ads.ranges[5] * 2, use_twos_comp=True)
    # Compare
    last_tolerance = abs(read - voltage)
    if last_tolerance > tolerance:
        tolerance = last_tolerance
print(f'tolerance: {tolerance} V')

f.xem.Close()
pwr_off([dc_pwr])
