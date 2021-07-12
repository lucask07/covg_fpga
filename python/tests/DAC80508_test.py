# Test the configuration, read, and most importantly write functionality of the DAC
import logging
import sys, os

# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
interfaces_path = os.getcwd()
for i in range(15):
    if os.path.basename(interfaces_path) == 'covg_fpga':
        interfaces_path = os.path.join(interfaces_path, 'python')
        break
    else:
        interfaces_path = os.path.dirname(interfaces_path)  # If we aren't in covg_fpga, move up a folder and check again
sys.path.append(interfaces_path)

from interfaces import FPGA, GeneralDACController

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'DAC80508_test.log'), filemode='w',
                    encoding='utf-8', level=logging.INFO)

# Set up FPGA
f = FPGA(bitfile='../fpga_XEM7310/fpga_XEM7310.runs/impl_1/top_level_module.bit')
f.init_device()

# Set up DAC
gp_dac = GeneralDACController(f)

id = gp_dac.get_id(display=True)
if id == False:
    logging.warning(f'ID={id}')
else:
    logging.info(f'ID={id}')

reset_success = gp_dac.reset()
if reset_success:
    logging.info('Reset: SUCCESS')
else:
    logging.warning('Reset: FAIL')

# Read configuration register
config = gp_dac.get_config(display_values=True)
if config == False:
    logging.warning(f'Configuration={config}')
else:
    logging.info(f'Configuration={config}')

# Write to dac0
for voltage in range(0x0006):
    if gp_dac.write('DAC0', voltage):
        message = f'Write {hex(voltage)}={voltage}V SUCCESS'
        print(message)
        logging.info(message)
    else:
        message = f'Write {hex(voltage)}={voltage}V FAIL'
        logging.warning(message)
