import sys
import os
import logging


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

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'clamp_configuration_test.log'), filemode='w',
                    encoding='utf-8', level=logging.INFO)

from interfaces import FPGA

sys.path.append(os.path.join(interfaces_path, 'drivers'))

from clamp_configuration import configure_clamp

# TODO: make this a relative path
f = FPGA(bitfile='C:/Users/ajstr/OneDrive/Documents/Research Internship/Programs/xem7310_starter/i2c.bit')
f.init_device()

log_info = configure_clamp(f, ADC_SEL='CC', DAC_SEL='drive_CAL1', CCOMP=0, RF1=60)
for info in log_info:
    logging.info(info)
# Expecting 0b1110, 0b0111, 0b0000, 0b0001
