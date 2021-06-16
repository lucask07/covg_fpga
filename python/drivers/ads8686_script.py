'''
2021/06/15

Run this script after running ads8686.py 
to initialize and configure the FPGA

Steps:
1) %run ads8686.py
2) press physical reset button on ADS8686 eval board
3) %run ads8686_script.py 

'''

import time 

################## Register Addresses for the ADS8686 ##########################
config = 0x400 # 16 bits, Fig 77. Hex = 0x8400 to write (was 0x4200 for read)
    # bit 15: write access = 1
    # bits 14-9: accesses reg. by writing the address (which is 0x2 == 0'b000010)
    # bits 8-7: read only... so put 0's
    # bits 6-0: disable burst mode, sequencer, oversampling, status register output control, and crc control

chan_sel = 0x600 # 16 bits, Fig 78. Hex = 0x86B0
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (which is 0x3 == 0'b000011)
    # bit 8: reserved - 0
    # bits 7-4: B channel select. Only using SDOA (1 output) so set to fixed code
        # by writing 1011b (should give us the fixed result 0x5555)
    # bits 3-0: A channel select. Keep It Simple so go with 0000b to selet AIN_0A

# was 0x800
rangeA1 = 0xCFF # 16 bits, Fig 79. Hex = 0x8800 
    # bit 15: write
    # bits 14-9: access reg. by writing address (0x4 == 0b000100)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 10V = 00
    # bits 5-4: voltage selection for +/- 10V = 00
    # bits 3-2: voltage selection for +/- 10V = 00
    # bits 1-0: voltage selection for +/- 10V = 00

dev_ID = 0x2000 # 16 bits, Fig 87. Hex = 0x4000 [address 0x10]
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (0x10 == 0'b010000)
    # bits 8-2: reserved - 000000
    # bits 1-0: DEV_ID register - read only so write 00

# read the device ID -- this should return 2 (or maybe 0x2002)

print('--'*40)

print('Reading the device ID')
for i in range(3):
    read_back = send_SPI(dev_ID) 
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the configuration reg')
for i in range(3):
    read_back = send_SPI(config) #
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading range A1')
for i in range(3):
    read_back = send_SPI(rangeA1) 
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)
print('Write to range A1')
read_back = send_SPI(rangeA1 | 0x8000 | 0x55)  # write a value of 0x55
print('--'*40)
print('Now read range A1')
time.sleep(0.001)
for i in range(3):
    read_back = send_SPI(rangeA1)  # write a value of 0x55
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

