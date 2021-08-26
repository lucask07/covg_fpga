"""Early test file for the I2C DAC chip DAC53401. Tests writes and configuration.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import os, sys
from time import sleep

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

from interfaces.interfaces import FPGA, DAC53401
import logging

logging.basicConfig(filename='DAC53401_test.log',
                    encoding='utf-8', level=logging.INFO)

# Initialize FPGA
bitfile = os.path.join(interfaces_path, 'i2c.bit')
f = FPGA(bitfile=bitfile)
f.init_device()
f.set_wire(0x00, value=0xff00, mask=0xff00)

# Instantiate the DAC53401 controller.
i2c_dac = DAC53401(fpga=f, addr_pins=0b000)
logging.info(f'Address Pins = {i2c_dac.addr_pins}')
print(f'Address Pins = {i2c_dac.addr_pins}')

# Configure Slew Rate
slew_rate = 16
i2c_dac.config_rate(slew_rate)
logging.info(f'Slew Rate = {slew_rate}')
print(f'Slew Rate = {slew_rate}')

# Write voltage
voltage = 0b1111111111
i2c_dac.write_voltage(voltage)
logging.info(f'Voltage = {voltage}')
print(f'Voltage = {voltage}')

# Power on, wait
i2c_dac.power_up()
logging.info('Power ON')
print('Power ON')
logging.info('Sleeping...')
print('Sleeping...')
sleep(3)

# Change gain, wait
gain = 3
i2c_dac.set_gain(gain)
logging.info(f'Gain = {gain}')
print(f'Gain = {gain}')
i2c_dac.enable_internal_reference()
logging.info('Internal Reference Enabled')
print('Internal Reference Enabled')
logging.info('Sleeping...')
print('Sleeping...')
sleep(3)

# Power off
i2c_dac.power_down_high_impedance()
logging.info('Power down High Impedance')
print('Power down High Impedance')

# Configure slew rate, margins, function generation
rate = 8
i2c_dac.config_rate(8)
logging.info(f'Rate = {rate}')
print(f'Rate = {rate}')
margin_high = 0b1111111111
margin_low = 0b0000000000
i2c_dac.config_margins(margin_high=margin_high, margin_low=margin_low)
logging.info(f'Margin High = {margin_high}')
print(f'Margin High = {margin_high}')
logging.info(f'Margin Low = {margin_low}')
print(f'Margin Low = {margin_low}')
func = 'triangle'
i2c_dac.config_func(func)
logging.info(f'Function = {func}')
print(f'Function = {func}')

# Power on, start function generation, wait
i2c_dac.power_up()
logging.info('Power ON')
print('Power ON')
i2c_dac.start_func()
logging.info('Starting function generation...')
print('Starting function generation...')
logging.info('Sleeping...')
print('Sleeping...')
sleep(3)

# Stop function generation
i2c_dac.stop_func()
logging.info('Stopped function generation')
print('Stopped function generation')
