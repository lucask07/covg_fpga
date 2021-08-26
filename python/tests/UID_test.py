"""Early test file for the read and write functionality of the 24AA025UID ID chip.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

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
from interfaces.interfaces import FPGA, UID_24AA025UID, count_bytes, int_to_list

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'UID_test.log'), filemode='w',
                    encoding='utf-8', level=logging.INFO)


sys.path.append(interfaces_path)


# Requires i2c.bit or First.bit for the bitfile.
bitfile = os.path.join(interfaces_path, 'i2c.bit')

f = FPGA(bitfile=bitfile)
f.init_device()

# Instantiate ID chip
uid = UID_24AA025UID(fpga=f, addr_pins=0b000)

# Read serial number, check manufacturer and device codes
serial_number = uid.get_serial_number()
#expecting serial code = [0, 188, 123, 132]
message = f'Serial Number: {serial_number}'
print(message)
logging.info(message)

manufacturer_code = uid.get_manufacturer_code()
message = f'Manufacturer Code: {manufacturer_code}'
print(message)
logging.info(message)
print(uid.parameters['MANUFACTURER_CODE'].default)
if manufacturer_code == uid.parameters['MANUFACTURER_CODE'].default:
    logging.info('Manufacturer Code MATCH')
else:
    logging.warning('Manufacurer Code NOT MATCHED')

device_code = uid.get_device_code()
print(f'Device Code: {device_code}')
if device_code == uid.parameters['DEVICE_CODE'].default:
    logging.info('Device Code MATCH')
else:
    logging.warning('Device Code NOT MATCHED')

# Test writing data
data = 0x237583
print(f'Writing data = {hex(data)}')
logging.info(f'Write data = {hex(data)}')
uid.write(data)

# Read back the data we wrote
read_back = uid.read(word_address=0, words_read=count_bytes(data))
print(f'Read back data = {read_back}')
if read_back == None:
    logging.warning(f'Read data = {read_back}')
else:
    read_back_hex = [hex(x) for x in read_back]
    logging.info(f'Read data = {read_back_hex}')


# Check if it is the same
if read_back == int_to_list(data):
    logging.info('Read data and Write data MATCH')
else:
    logging.warning('Read data and Write data NOT MATCHED')
