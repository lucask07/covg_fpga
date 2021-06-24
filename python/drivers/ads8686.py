import sys
import os
from collections import namedtuple

cwd = os.getcwd() # gets the current working directory
path = os.path.join(cwd, "covg_fpga/python/drivers")
sys.path.append(path)

from fpga import FPGA

path1 = os.path.join(cwd, "covg_fpga/python/drivers")
sys.path.append(path1)
from utils import rev_lookup, bin, test_bit, twos_comp

################## Opal Kelly End Points ##################
ep = namedtuple('ep', 'addr bits type') # address of the DEVICE_ID reg so we can read it

# wire ins
control = ep(0x00, [i for i in range(32)], 'wi')  # note this is active low 

# wires out
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

################## Define functions for fpga reading/sending data  ##################
def send_trig(ep_bit):
    ''' send a trigger to the opal kelly FPGA '''
    # expects a single bit in to control posedge (the ep_bit acts as that bit/var)
    f.xem.ActivateTriggerIn(ep_bit.addr, ep_bit.bits)

def read_wire(ep_bit): # reads the wire and returns the value back
    ''' read a wire in from the opal kelly FPGA 
        returns the value read
    '''
    f.xem.UpdateWireOuts()
    a = f.xem.GetWireOutValue(ep_bit.addr) 
    return a # returns the wire value into the var a

################## Actual executing code ##################
# sets up the fpga by grabbing an instance of the class (as f) and initializing the device
f = FPGA()
f.init_device() # programs the FPGA (loads bit file)

# set the SPI output mux to select a device other than the ADS7952 to avoid contention on SDO
f.set_wire(mux_control.addr, 1, mask = mux_control.bits)


'''
Wishbone information 
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
//  2'b01   Write (lower 32-bits are the value to be written) --> why commands that write are prefixed with 0x4000 
//  2'b10   Set address why commands that read are prefixed with 0x8000 
//      Next 30 bits are the address
//      bit[1] is an address difference bit
//      bit[0] is an increment bit
//  2'b11   Special command
'''