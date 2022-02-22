"""Early test file for the I2C DAC chip DAC53401. Tests writes and configuration.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import os, sys
from time import sleep
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

from interfaces.interfaces import FPGA, Endpoint, disp_device, advance_endpoints_bynum,UID_24AA025UID
import logging
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from interfaces.boards import Daq
eps = Endpoint.endpoints_from_defines

# encoding was add as an option at Python 3.9
# logging.basicConfig(filename='DAC53401_test.log',
#                     encoding='utf-8', level=logging.INFO)

# alternative for Python<3.9
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler('UID_test.log', 'w', 'utf-8')
root_logger.addHandler(handler)

# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply()
atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2)
# turn on the 7V in, but keep +/-16.6 down
dc_pwr.set('out_state', 'ON', configs={'chan': 1})
# turn on the +/-16.5 V input
for ch in [1, 2]:
    dc_pwr2.set('out_state', 'ON', configs={'chan': ch})


# Initialize FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

# power supply turn on via FPGA enables
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True

clamp_uid = UID_24AA025UID(fpga=f,
                     endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDC'), 1),
                     addr_pins=0b000)

read = clamp_uid.get_manufacturer_code()
default = clamp_uid.registers['MANUFACTURER_CODE'].default
if read != default:
    print(f'UID MANUFACTURER_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')

read = clamp_uid.get_device_code()
default = clamp_uid.registers['DEVICE_CODE'].default
if read != default:
    print(f'UID DEVICE_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')


# Stop function generation
# i2c_dac.stop_func()
# logging.info('Stopped function generation')
# print('Stopped function generation')
