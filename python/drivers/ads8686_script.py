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
import logging

################ TODO: implement logging #################


################## Register Addresses for the ADS8686 ##########################
config = 0x400 # 16 bits, Fig 77. 
''' Hex = 0x8400 '''
    # bit 15: write access = 1
    # bits 14-9: accesses reg. by writing the address (which is 0x2 == 0'b000010)
    # bits 8-7: read only... so put 0's
    # bits 6-0: disable burst mode, sequencer, oversampling, status register output control, and crc control

chan_sel = 0x600 # 16 bits, Fig 78. Hex = 0x86B0
''' Hex 0x8600 '''
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (which is 0x3 == 0'b000011)
    # bit 8: reserved - 0
    # bits 7-4: B channel select. Only using SDOA (1 output) so set to 0000b
    # bits 3-0: A channel select. Keep It Simple so go with 0000b to selet AIN_0A

'''yield address 0x10 or occasionally 0x8... Why?? '''
rangeB1 = 0xC00 # 16 bits, Figure 81
    # bit 15: read - 0
    # bits 14-9: register address (0x6 = 0b000110b)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 5V = 10b
    # bits 5-4: voltage selection for +/- 5V = 10b
    # bits 3-2: voltage selection for +/- 5V = 10b
    # bits 1-0: voltage selection for +/- 5V = 10b

################# No response from the board ##################
dev_ID = 0x2000 # 16 bits, Fig 87. Hex = 0x4000 [address 0x10]
''' Hex 0xA000? ''' 
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (0x10 == 0'b010000)
    # bits 8-2: reserved - 000000
    # bits 1-0: DEV_ID register - read only so write 00

rangeA1 = 0x800 # 16 bits, Fig 79. 
''' Hex = 0x8800? '''
    # bit 15: read (0)
    # bits 14-9: access reg. by writing address (0x4 == 0b000100)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 5V = 10b
    # bits 5-4: voltage selection for +/- 5V = 10b
    # bits 3-2: voltage selection for +/- 5V = 10b
    # bits 1-0: voltage selection for +/- 5V = 10b

rangeA2 = 0xA00 # 16 bits, Figure 80
''' Hex 0x8A00? '''
    # bit 15: read (0)
    # bits 14-9: register addresss (0x5 == 0b000101)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 5V = 10b
    # bits 5-4: voltage selection for +/- 5V = 10b
    # bits 3-2: voltage selection for +/- 5V = 10b
    # bits 1-0: voltage selection for +/- 5V = 10b

rangeB2 = 0xE00 # 16 bits, Figure 82
''' Hex 0x8E00? '''
    # bit 15: read - 0
    # bits 14-9: register address (0x7 = 0b000111b)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 5V = 10b
    # bits 5-4: voltage selection for +/- 5V = 10b
    # bits 3-2: voltage selection for +/- 5V = 10b
    # bits 1-0: voltage selection for +/- 5V = 10b

lpf = 0x1A00 # 16 bits, Fig 86
    # bit 15: read - 0
    # bits 14-9: register address (0xD = 0b001101)
    # bits 8-2: reserved - 0
    # bits 1-0: set the cutoff frequency for the low pass filter: 00b = 39kHz, 01b = 15kHz, and 10b = 376kHz

stack0 = 0x4000 # 16 bits, Fig 88.
''' Hex 0xC000? or 0xC000? '''
    # bit 15: read (0)
    # bits 14-9: register address (0x20 == 0b100000)
    # bit 8: reserved - 0
    # bits 7-4: CHSEL_B[3:0] 0b1011 for code 0x5555
    # bits 3-0: CHSEL_A[3:0] 0b1011 for code 0x5555


print('--'*40)

print('Write to the configuration register')
read_back = send_SPI(config | 0x8000 | 0x55)  # write a value of 0x55

print('--'*40)

print('Now read the configuration reg')
for i in range(3):
    read_back = send_SPI(config) # send SPI cmd to read the reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Write to the channel selection register')
read_back = send_SPI(chan_sel | 0x8000 | 0x7A)  # write a value of 0x55

print('--'*40)

print('Now read the channel selection reg')
for i in range(3):
    read_back = send_SPI(chan_sel) # send SPI cmd to read the reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Write to reg A1')
read_back = send_SPI(rangeA1 | 0x8000 | 0x55)  # write a value of 0x55

print('--'*40)

print('Now read reg A1')
time.sleep(0.001)
for i in range(3):
    read_back = send_SPI(rangeA1)  # send SPI cmd to read the reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the A2 reg')
time.sleep(0.001)
for i in range(3):
    read_back = send_SPI(rangeA2)  # send SPI cmd to read the reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the B1 reg')
time.sleep(0.001)
for i in range(3):
    read_back = send_SPI(rangeB1)  # send SPI cmd to read the reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the B2 reg')
time.sleep(0.001)
for i in range(3):
    read_back = send_SPI(rangeB2)  # send SPI cmd to read the reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the LPF reg')
for i in range(3):
    read_back = send_SPI(lpf) # read the low pass filter reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the seq_stack0 reg (wire low)')
for i in range(3):
    read_back = send_SPI(stack0) # read the stack 0 reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)
print('--'*40)

print('Setting the wire high')
f.set_wire(0x01, 0xF)

time.sleep(0.001) # wait for 1 ms

print('--'*40)
print('--'*40)

'''
print('Setting the wire low')
f.set_wire(0x01, 0x0)
print('--'*40)
print('--'*40)


print('Reading the seq_stack0 reg (wire set high but back to low)')
for i in range(3):
    read_back = send_SPI(stack0) # read the stack 0 reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)
print('--'*40)

print('Setting the wire high')
f.set_wire(0x01, 0xF)

time.sleep(0.001) # wait for 1 ms

print('--'*40)
print('--'*40)
'''

print('Reading the seq_stack0 reg (wire high)')
for i in range(3):
    read_back = send_SPI(stack0) # read the stack 0 reg
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the device ID')
# read the device ID -- this should return 2 (or maybe 0x2002)
for i in range(3):
    read_back = send_SPI(dev_ID) # send SPI cmd to read the ID
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

'''

stack1 = 0x4200 # 16 bits, Fig. 89
stack2 = 0x4400 # 16 bits, Fig. 90

print('Reading the seq_stack1 reg')
# read the device ID -- this should return 2 (or maybe 0x2002)
for i in range(3):
    read_back = send_SPI(stack1) # send SPI cmd to read the ID
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)

print('Reading the seq_stack2 reg')
# read the device ID -- this should return 2 (or maybe 0x2002)
for i in range(3):
    read_back = send_SPI(stack2) # send SPI cmd to read the ID
    time.sleep(0.001)
    read_back = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(read_back))

print('--'*40)
'''