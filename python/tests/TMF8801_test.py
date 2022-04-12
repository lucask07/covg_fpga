"""Test of I2C for AMS TMF8801

April 2022

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

from interfaces.interfaces import FPGA, DAC53401, Endpoint
from interfaces.boards import TOF
import logging

logging.basicConfig(filename='DAC53401_test.log',
                    encoding='utf-8', level=logging.INFO)

# Initialize FPGA
top_level_module_bitfile = os.path.join(covg_fpga_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit')
f = FPGA(bitfile=top_level_module_bitfile)
f.init_device()

# Instantiate the TMF8801 controller.
tof = TOF(f)
tof.TMF.get_id()

