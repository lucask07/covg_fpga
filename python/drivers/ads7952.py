import sys
from fpga import FPGA
import time
import numpy as np
import matplotlib.pyplot as plt 
import pickle as pkl
from drivers.utils import rev_lookup, bin, test_bit, twos_comp


from collections import namedtuple
ep = namedtuple('ep', 'addr bits type')
control =   ep(0x00, [i for i in range(32)], 'wi')  # note this is active low 

# wire outs for "1 deep FIFO" 
adc_pll_lock =   ep(0x20, [i for i in range(32)], 'wo')

# triggers in 
valid      = ep(0x40, 0, 'to')
fpga_reset = ep(0x40, 1, 'to')
fifo_reset = ep(0x40, 2, 'to')

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


if __name__ == "__main__":

    f = FPGA()
    f.init_device()

    # SPI Master configuration
    for val in [0x80000051, 0x40000001, 
                    0x80000041, 0x40003610,
                    0x80000061, 0x40000001]:

        f.set_wire(control.addr, val, mask = 0xffffffff)
        send_trig(valid) 

    # now send SPI command 
    for val in [0x80000001, 0x40001000, 
                0x80000041, 0x40003710]:
        f.set_wire(control.addr, val, mask = 0xffffffff)
        send_trig(valid) 

