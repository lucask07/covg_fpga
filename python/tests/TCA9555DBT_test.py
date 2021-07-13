import os, sys

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

from interfaces import FPGA, IOExpanderController
import logging

logging.basicConfig(filename='TCA9555DBT_test.log',
                    encoding='utf-8', level=logging.INFO)

# Initialize FPGA
f = FPGA(bitfile='C:/Users/ajstr/OneDrive/Documents/Research Internship/Programs/xem7310_starter/i2c.bit')
f.init_device()
f.set_wire(0x00, value=0xff00, mask=0xff00)

# Instantiate and reset TCA9555DBT chip
device = IOExpanderController(f)
device.reset_device()
address_pins = 0b000

# Configure pins[0x07:0x00] as outputs, pins[0x17:0x10] as inputs
device.configure_pins(address_pins, [0x00, 0xff])

# Write to outputs
device.write(address_pins, [0xcc, 0x00]) # 0x88 = 0b1000_1000

# Read from inputs
read_out = device.read(address_pins)
print(f'Read: {[hex(x) for x in read_out]}')

# Test sequence of writes and reads
# Note: using the chip soldered to the proto-board, pins 10 and 11 are soldered together so pins[0x07:0x06] are soldered together
# causing any number in which one pin is 0 and the other is 1 to appear as if both pins are 0
# [0x40:0xb0] will be incorrect
print('Testing Sequence')
for i in range(256):
    print(f'Write: {hex(i)}', end=', ')
    device.write(address_pins, [i, 0x00])
    read_out = device.read(address_pins)
    print(f'Read: {[hex(x) for x in read_out]}')
    if read_out[0] == i:
        logging.info(f'{hex(i)} Match')
    else:
        logging.warning(f'Wrote {hex(i)}, Read {hex(read_out[0])}')

# Close device
f.xem.Close()
