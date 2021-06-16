import sys
from fpga import FPGA
import time
import numpy as np
# import matplotlib.pyplot as plt 
import pickle as pkl
import os
cwd = os.getcwd()
path = os.path.join(cwd, "covg_fpga/python/drivers")
sys.path.append(path)
from drivers.utils import rev_lookup, bin, test_bit, twos_comp

from collections import namedtuple
ep = namedtuple('ep', 'addr bits type')
control =   ep(0x00, [i for i in range(32)], 'wi')  # note this is active low 

# wire outs for "1 deep FIFO" 
one_deep_fifo =   ep(0x20, [i for i in range(32)], 'wo')

# triggers in 
valid      = ep(0x40, 0, 'ti')
fpga_reset = ep(0x40, 1, 'ti')
fifo_reset = ep(0x40, 2, 'ti')

# triggers out 
hall_full = ep(0x60, 0, 'to')

# pipeout (bits are meaningless)
adc_pipe = ep(0xA0, [i for i in range(32)], 'po') 

## SPI register maps 
manual_mode = 1   #bits 15-12
auto1_mode = 2    #bits 15-12
auto2_mode = 3    #bits 15-12
auto1_program = 8 #bits 15-12

# AD5453 (DAC)
load_update = 0 # bits 14-15 
rising_edge_load = 3 # bits 14-15 : switch to loading data on the rising edge of SCLK
'''
Serial Data Input. Data is clocked into the 16-bit input register upon the active edge of the serial
clock input. By default, in power-up mode data is clocked into the shift register upon the falling
edge of SCLK. The control bits allow the user to change the active edge to a rising edge.


Settings for AD5453

# creg_val = 0x40003010 # Char length of 16; clear both Tx_NEG, Rx_NEG; set ASS, IE. AD5453    
# val = 0x40001fff # AD5453 (half-scale)


'''

def set_bit(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, mask, mask) # set
    f.xem.UpdateWireIns()

def clear_bit(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask) # clear
    f.xem.UpdateWireIns()

def toggle_low(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask) # toggle low 
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(ep_bit.addr, mask, mask)   # back high 
    f.xem.UpdateWireIns()

def toggle_high(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])
    f.xem.SetWireInValue(ep_bit.addr, mask, mask) # toggle high 
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask)   # back low 
    f.xem.UpdateWireIns()

def send_trig(ep_bit):
    ''' 
        expects a single bit, not yet implement for list of bits 
    '''
    f.xem.ActivateTriggerIn(ep_bit.addr, ep_bit.bits)


def read_wire(ep_bit):

    f.xem.UpdateWireOuts()
    a = f.xem.GetWireOutValue(ep_bit.addr) 
    return a 

def to_voltage(a):
    bits = 12
    vref = 2.5*2 
    masked = a & 0xfff  # 12 bit ADC        
    v = masked/(2**bits - 1)*vref
    chan = (a & 0xf000) >> 12
    return v, chan

'''
cmd_word = {ep_dataout[31:30], 2'b0, ep_dataout[29:0]};


// Wishbone Master
// Purpose: An example debug bus.  This bus takes commands from an incoming
//      34-bit command word, and issues those commands across a wishbone
//  bus, returning the result from the bus command.  Basic bus commands are:
//
//  2'b00   Read
//  2'b01   Write (lower 32-bits are the value to be written)
//  2'b10   Set address
//      Next 30 bits are the address
//      bit[1] is an address difference bit
//      bit[0] is an increment bit
//  2'b11   Special command

// SPI Master addresses 

Rx0 0x00 32 R Data receive register 0
CTRL 0x10 32 R/W Control and status register w/ offset 4
DIVIDER 0x14 32 R/W Clock divider register : w/ offset 5 
SS 0x18 32 R/W Slave select register: w/ offset 6

'''

if __name__ == "__main__":

    f = FPGA()
    f.init_device()

    # FPGA reset 

    mode = 'manual'
    mode = 'auto-1'

    # MUX control (0 picks ADS7952)
    ads7952 = 0
    dacs = [1,2,3,4]
    f.set_wire(0x01, ads7952, mask = 0xffffffff)

    # SPI Master configuration: divide reg, ctrl reg, SS register 
    # MSB: 8 - set address, 4 - write data  

    creg_val = 0x40003610 # Char length of 16; set both Tx_NEG, Rx_NEG; set ASS, IE. ADS7952

    for val in [0x80000051, 0x40000004,  # divider (need to look into settings of 1 and 2 didn't show 16 clock cycles) 
                0x80000041, creg_val,  # control register (CHAR_LEN = 16, bits 10,9, 13 and 12)
                0x80000061, 0x40000001]: # slave select (just setting bit0)

        f.set_wire(control.addr, val, mask = 0xffffffff)
        send_trig(valid) 

    print('mode is: {}' .format(mode))

    if mode == 'manual':
        # now send SPI command 
        #val = 0x40001840 # ADS manual read of channel 0
        val = 0x400018C0 # ADS manual read of channel 1
        val = 0x400018C0 # ADS manual read of channel 3

        for val in [0x80000001, val,  # Tx register, data to send  
                    0x80000041, creg_val | (1 << 8)]: # Control register - GO (bit 8)
            f.set_wire(control.addr, val, mask = 0xffffffff)
            send_trig(valid) 

        # TODO: test block throttle pipe, use an auto mode to cycle through ~4 channels 
        # 128 transfers and then will be ready to read a block 

        # TODO: 
        # 1) setup auto mode by sending wire in commands to the wishbone master
        # 2) wait for trigger out "half full"
        # 3) read block throttle pipe  

        # test wire out using manual reads of CH0 and CH3 
        a = read_wire(one_deep_fifo)
        v,chan = to_voltage(a)
        print('Measured voltage on channel {} = {} [V]'.format(chan, v))

    elif mode == 'auto-1':

        # setup 
        for val in [0x80000001, 0x40008000,  # enter auto-1 program sequence
                    0x80000041, creg_val | (1 << 8),
                    0x80000001, 0x4000000f,  # channels 0,1,2,3   
                    0x80000041, creg_val | (1 << 8),
                    0x80000001, 0x40002840,  # enter auto-1  
                    0x80000041, creg_val | (1 << 8)]: # Control register - GO (bit 8)
            
            f.set_wire(control.addr, val, mask = 0xffffffff)
            send_trig(valid) 

        # now cycle through 
        for i in range(128):
            for val in [0x80000001, 0x40002040,  # retain
                        0x80000041, creg_val | (1 << 8)]: # Control register - GO (bit 8)
                

                f.set_wire(control.addr, val, mask = 0xffffffff)
                send_trig(valid) 

            a = read_wire(one_deep_fifo)
            v,chan = to_voltage(a)
            print('Measured voltage on channel {} = {} [V]'.format(chan, v))

'''
val = 0x400018C0 # ADS manual read of channel 3
creg_val = 0x40003610 

for val in [0x80000001, 0x40002040,  # Tx register, data to send  
            0x80000041, creg_val | (1 << 8)]: # Control register - GO (bit 8)
    f.set_wire(control.addr, val, mask = 0xffffffff)
    send_trig(valid) 

'''
