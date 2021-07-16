# Test the configuration, read, and most importantly write functionality of the DAC
import logging
import sys, os

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

from interfaces import FPGA, GeneralDACController

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'DAC80508_test.log'), filemode='w',
                    encoding='utf-8', level=logging.INFO)

# Set up FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310', 'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()

# Set up DAC
gp_dac = GeneralDACController(f, slave_address=0x3fffffff, debug=True)
gp_dac.set_divider(0x40000000) # Set frequency TODO: figure out what frequency this should be
gp_dac.configure_master(ASS=1, CHAR_LEN=24) # Set automatic slave select and character length to 24 for the 24-bit SPI messages

id = gp_dac.get_id(display=False)
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

# Write to all outputs
for i in range(8):
    for voltage in range(3, 4):
        if gp_dac.write('DAC'+str(i), voltage):
            message = f'Write {hex(voltage)}={voltage}V SUCCESS'
            print(message)
            logging.info(message)
        else:
            message = f'Write {hex(voltage)}={voltage}V FAIL'
            logging.warning(message)
