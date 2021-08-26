"""Early test file for the configuration, read, and write functionality of the DAC.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import logging
import sys, os
import time 

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

from interfaces.interfaces import FPGA, DAC80508

#logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'DAC80508_test.log'), filemode='w',
#                    encoding='utf-8', level=logging.INFO)

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'DAC80508_test.log'), filemode='w',
                    level=logging.INFO)


# Set up FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310', 'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)


# Set up DAC
gp_dac = DAC80508(f, slave_address=0x1, debug=True)
# Reset the Wishbone controller and SPI core
gp_dac.reset_master()

print('Setting divider...')
gp_dac.set_divider(0x8) # XEM6310 worked with divider of 4, XEM7310 runs twice as fast so divider of 8.

print('Configuring Wishbone...')
spi_ctrl_reg_val = 0x3218 # Sets CHAR_LEN=24, Rx_NEG, ASS, IE
gp_dac.configure_master_bin(spi_ctrl_reg_val)

# print('Getting ID...')
# id = gp_dac.get_id(display=False)
# if id == False:
#     logging.warning(f'ID={id}')
# else:
#     logging.info(f'ID={id}')

# reset_success = gp_dac.reset()
# if reset_success:
#     logging.info('Reset: SUCCESS')
# else:
#     logging.warning('Reset: FAIL')

# # Read configuration register
# print('Reading chip configuration...')
# config = gp_dac.get_config(display_values=True)
# if config == False:
#     logging.warning(f'Configuration={config}')
# else:
#     logging.info(f'Configuration={config}')

# Write 0x1ff to 0x04 (GAIN register)
input('\nAbout to change GAIN... ')
gp_dac.set_gain(0x01ff)
print('Gain changed')

# Write 0xff to 0x03 (CONFIG register)
input('\nAbout to power down all outputs... ')
gp_dac.set_config_bin(0xff)
print('Outputs powered down')

# Write 0x00 to 0x03 (CONFIG register)
input('\nAbout to power on all outputs... ')
gp_dac.set_config_bin(0x00)
print('Outputs powered on')

# Write to all outputs
input('\nAbout to write chip outputs... ')
voltage = 0xffff
for i in range(8):
    if gp_dac.write('DAC'+str(i), voltage):
        message = f'Write {hex(voltage)}={voltage}V SUCCESS'
        # print(message)
        logging.info(message)
    else:
        message = f'Write {hex(voltage)}={voltage}V FAIL'
        logging.warning(message)
    
    input(f'DAC{str(i)} write complete... ')
