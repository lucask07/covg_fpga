# Test the configuration, read, and most importantly write functionality of the DAC
import logging
import sys, os
cwd = os.getcwd()
interfaces_path = os.path.join(cwd, '..')
registers_path = os.path.join(cwd, '..', '..')
sys.path.append(interfaces_path)
sys.path.append(registers_path)

from interfaces import FPGA, GeneralDACController

logging.basicConfig(filename='DAC80508_test.log',
                    encoding='utf-8', level=logging.INFO)

# Set up FPGA
f = FPGA(bitfile='../fpga_XEM7310/fpga_XEM7310.runs/impl_1/top_level_module.bit')
f.init_device()

# Set up DAC
gp_dac = GeneralDACController(f)
id = gp_dac.get_id(display=True)
logging.info(f'ID={id}')
reset_success = gp_dac.reset()
if reset_success:
    logging.info('Reset succesful')
else:
    logging.warning('Reset failed')

# Read configuration register
configuration = gp_dac.get_config(display_values=True)
logging.info(f'Configuration={configuration}')

# Write to dac0
for voltage in range(0x0005):
    if gp_dac.write('DAC0', voltage):
        logging.info('Write {hex(voltage)}={voltage}V Successful')
    else:
        logging.info('Write {hex(voltage)}={voltage}V Failed')
