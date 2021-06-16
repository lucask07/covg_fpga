import sys
from fpga import FPGA
import time
import numpy as np
# import matplotlib.pyplot as plt
import pickle as pkl
import os
cwd = os.getcwd() # gets the current working directory
path = os.path.join(cwd, "covg_fpga/python")
sys.path.append(path)
from drivers.utils import rev_lookup, bin, test_bit, twos_comp

from collections import namedtuple
ep = namedtuple('ep', 'addr bits type') # address of the DEVICE_ID reg so we can read it
# formats the signal so wishbone bus understands it (32 bits --> 34 bits)
control = ep(0x00, [i for i in range(32)], 'wi')  # note this is active low 

# wires out: how to connect to FPGA
mux_control = ep(0x01, 0b111, 'wo') # tells mux to choose the ADS8686 board
one_deep_fifo = ep(0x20, [i for i in range(32)], 'wo') # hands back the reset value of DEVICE_ID... should be 0x2002. Set to 1 for debugging

# triggers in 
valid      = ep(0x40, 0, 'ti')
fpga_reset = ep(0x40, 1, 'ti') 
fifo_reset = ep(0x40, 2, 'ti')

# triggers out
hall_full = ep(0x60, 0, 'to')

# pipeout (bits are meaningless)
adc_pipe = ep(0xA0, [i for i in range(32)], 'po') 

## SPI Register Map (copied from readLEDs)
manual_mode = 1   #bits 15-12
auto1_mode = 2    #bits 15-12
auto2_mode = 3    #bits 15-12
auto1_program = 8 #bits 15-12

# AD5453 (DAC)
load_update = 0 # bits 14-15 
rising_edge_load = 3 # bits 14-15 : switch to loading data on the rising edge of SCLK

# Settings for ADS8585SEVM-PDK - sets channels and registers (software mode, channel select...)
config_val = 0x40004200 # 16 bits, Fig 77. Hex = 0x8400 to write (was 0x4200 for read)
    # bit 15: write access = 1
    # bits 14-9: accesses reg. by writing the address (which is 0x2 == 0'b000010)
    # bits 8-7: read only... so put 0's
    # bits 6-0: disable burst mode, sequencer, oversampling, status register output control, and crc control

chan_sel_val = 0x400086B0 # 16 bits, Fig 78. Hex = 0x86B0
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (which is 0x3 == 0'b000011)
    # bit 8: reserved - 0
    # bits 7-4: B channel select. Only using SDOA (1 output) so set to fixed code
        # by writing 1011b (should give us the fixed result 0x5555)
    # bits 3-0: A channel select. Keep It Simple so go with 0000b to selet AIN_0A

rangeA1_val = 0x40008800 # 16 bits, Fig 79. Hex = 0x8800
    # bit 15: write
    # bits 14-9: access reg. by writing address (0x4 == 0b000100)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 10V = 00
    # bits 5-4: voltage selection for +/- 10V = 00
    # bits 3-2: voltage selection for +/- 10V = 00
    # bits 1-0: voltage selection for +/- 10V = 00

dev_ID_val = 0x4000A000 # 16 bits, Fig 87. Hex = 0xA000
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (0x10 == 0'b010000)
    # bits 8-2: reserved - 000000
    # bits 1-0: DEV_ID register - read only so write 00

''' Building the address into a generated command we can pass into loc of the build_cmd function
# build into a fx that decides where we need to go for a specific operation
address = 0x51 # where do we want to go?
reg = "ctrl"

# SDI will change based on our operation... for now want to access config. to start data aquisition
write_val= 0x40000000 # gives us the base for a write command
read_val = 0x80000000 # gives us the base for a read command

### eventually we'll be reading/writing more than once and will need this ###
# gets user input to choose a read/write command
def get_cmd(command):
    while True:
        if(command == "w"):
            return command # write command selected
        elif(command == "r"):
            return command # read command selected
        else:
            return 0 # if no command is selected, leave null

command = 0 
command = get_cmd(command)

# check what command was entered
print("Your command is: %s" % command)

def choose_address(address): # chooses the correct address for the task we want to complete
    if(reg == "ctrl" && command == "read"):
        address = 0x41
        return address # hand this back so we can create the command
    elif(reg == "ctrl" && command == "write"):
        address = 0x3610 # see creg_val
        return address
    elif(reg == "div" && command == "read"):
        address = 0x51
        return address
    elif(reg == "div" && command == "write"):
        address = 0x4
        return address
    elif(reg == "ss" && command == "read"):
        address = 0x61
        return address

    # can this have the same address as data_reg???
    elif(reg == "ss" && command == "write"):
        address = 0x1
        return address
    # can this have the same address as ss during write???
    elif(reg == "data" && command == "write"): # Remember: Rx and Tx are in the same register (0x00) to send/store data
        address = 0x1
        return address
    
    else
        print("Error: no valid command and/or register was detected")
    
    # One possible command is missing: data-r. Do we need it?

def build_cmd(command, read_cmd, write_cmd, loc): 
    if(command == "read"): # implement a read command and send via SPI
        read_cmd = 0x80000000 + loc # gives us what we want to do and where we want to go
        return read_cmd
    else: # otherwise, we're using a write command
        write_cmd = 0x40000000 + loc # gives us what we want to do and where we want to go
        return write_cmd

# build the command we want to R/W data
cmd = build_cmd(command, write_val, read_val, address)

print("your command is: %d" % cmd)
'''

# sets up the fpga by setting up f and initializing the device
f = FPGA()
f.init_device()

# there are only 2 modes the device can be in: hardware or software
mode = 'auto-1'
mode = 'manual'

f.set_wire(mux_control.addr, 1, mask = mux_control.bits)

def send_trig(ep_bit):
    # expects a single bit in to control posedge (the ep_bit acts as that bit/var)
    f.xem.ActivateTriggerIn(ep_bit.addr, ep_bit.bits)

def read_wire(ep_bit): # reads the wire and returns the value back
    f.xem.UpdateWireOuts()
    a = f.xem.GetWireOutValue(ep_bit.addr) 
    return a # returns the wire value into the var a

### lines 113 - 112 - command MODIFIED to accomodate wishbone... Modifies the address due to being a "slave node". Learn more about wishbone
# value written to the command register of the SPI controller
creg_val = 0x40003610 # Char length of 16. Will set Tx_NEG, Rx_NEG; set ASS, IE.  ADS8686

def SPI_config():
    if mode == 'manual':
    # from manual mode
        for val in [0x80000051, 0x40000008, #8? was 4 # divider (need to look into settings of 1 and 2 didn't show 16 clock cycles) 
                    0x80000041, creg_val,  # control register (CHAR_LEN = 16, bits 10,9, 13 and 12)
                    0x80000061, 0x40000001]: # slave select (just setting bit0)

            f.set_wire(control.addr, val, mask = 0xffffffff)
            send_trig(valid) 
    else:
    # when in auto mode
        for val in [0x80000001, 0x40008000,  # enter auto-1 program sequence
                    0x80000041, creg_val | (1 << 8),
                    0x80000001, 0x4000000f,  # channels 0,1,2,3   
                    0x80000041, creg_val | (1 << 8),
                    0x80000001, 0x40002840,  # enter auto-1  
                    0x80000041, creg_val | (1 << 8)]: # Control register - GO (bit 8)
            f.set_wire(control.addr, val, mask = 0xffffffff)
            send_trig(valid) 
    

def send_SPI(loc): # what needs to be writted\n to the ADS?
    if mode == 'manual':
    # when in manual mode
        # use vals create to configure, select, and look for dev_ID reg
        for val in [0x80000001, loc,  # go to the Tx register, store data to send (from cmd) 
                    0x80000041, creg_val | (1 << 8)]: # Tells the Control register - GO (bit 8) - sends val to ADS8686
            f.set_wire(control.addr, val, mask = 0xffffffff) # sets the wire to the ADS8686 w/val and adds mask to get correct data back
            a = read_wire(one_deep_fifo)
            # v,chan = to_voltage(a) # we're not capping the voltage on the FPGA, just want the address
            send_trig(valid)
            print('Address is {}'.format(a))
        # doesn't need to return since it'll print the register address to the console      
    
    else:
    # when in auto mode
        # for i in range(128):
        for val in [0x80000001, 0x40002040,  # retain
                    0x80000041, creg_val | (1 << 8)]: # Control register - GO (bit 8)
            f.set_wire(control.addr, val, mask = 0xffffffff) # sets the wire to the ADS8686 w/val and adds mask to get correct data back
            a = read_wire(one_deep_fifo)
            # v,chan = to_voltage(a) # we're not capping the voltage on the FPGA, just want the address
            send_trig(valid)
            print('Address is {}'.format(a))
            # doesn't need to return since it'll print the register address to the console
    

# runs send_SPI with each of the values in order to get the correct data
# send_SPI(config_val) # configure the ADS board
# send_SPI(chan_sel_val) # choose which channels we want to access
# send_SPI(rangeA1_val) # set up the voltage we're using
send_SPI(dev_ID_val) # access the device_ID register and read it's address (*remember: uses a WRITE command to do so)

'''
// SPI Master addresses (leave alone)
//      Rx0 0x00 32 R Data receive register 0
//      CTRL 0x10 32 R/W Control and status register w/ offset 4
//      DIVIDER 0x14 32 R/W Clock divider register : w/ offset 5 
//      SS 0x18 32 R/W Slave select register: w/ offset 6
//
// Wishbone Reference (from readLEDs)
// Purpose: An example debug bus. This bus takes commands from an incoming
//      34-bit command word, and issues those commands across a wishbone
//      bus, returning the result from the bus command.  Basic bus commands are:
// 
//  2'b00   Read 
//  2'b01   Write (lower 32-bits are the value to be written)
//  2'b10   Set address
//      Next 30 bits are the address
//      bit[1] is an address difference bit
//      bit[0] is an increment bit
//  2'b11   Special command
'''