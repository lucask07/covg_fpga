import sys
import os
from collections import namedtuple

cwd = os.getcwd() # gets the current working directory
path = os.path.join(cwd, "covg_fpga/python/drivers")
sys.path.append(path)

from fpga import FPGA
from utils import rev_lookup, bin, test_bit, twos_comp

# Import the necessary functions from the script so we can initialize the device

################## Opal Kelly End Points ##################
ep = namedtuple('ep', 'addr bits type') # address of the DEVICE_ID reg so we can read it

# wires out
# mux_control   = ep(0x01, 0b111, 'wo') # tells mux to choose the ADS8686 board
one_deep_fifo = ep(0x24, [i for i in range(32)], 'wo') # should hand back the same data as the fifo?

# wire ins
control       = ep(0x0, [i for i in range(32)], 'wi')  # note this is active low 
# convst is not longer implemented 
# convst        = ep(0x1, 3, 'wi') # the input signal used to start converting data (helps us read a voltage from the chip)
spi_driver    = ep(0x1, 0, 'wi') # who is driving SPI commands? High for host, low for FPGA
# ads_reset = ep(0x03, 4, 'wi') # used to reset the chip instead of pushing the button
FPGA_data     = ep(0x5, [i for i in range(32)], 'wi') # reads data from the FPGA (holds the last read back value)

# triggers in 
valid      = ep(0x40, 11, 'ti') # tells the FPGA to read good data (same as host_wb)
fpga_reset = ep(0x40, 1, 'ti') # this resets the entire system
fifo_reset = ep(0x40, 2, 'ti') # empties the fifo
clk_reset  = ep(0x40, 10, 'ti') # resets the clk divider of the SPI controller
# host_wb    = ep(0x40, 11, 'ti') # initates host wishbone transactions (same as valid, remove?)

# triggers out
half_full = ep(0x60, 0, 'to') # tells the FPGA that the fifo is half full

# pipeout (bits are meaningless)
adc_pipe = ep(0xA0, [i for i in range(32)], 'po') # reads the fifo in bytes (used in graphing)

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
    res = f.xem.GetWireOutValue(ep_bit.addr) 
    return res # returns the wire value into the var a

################## Actual executing code ##################
# sets up the fpga by grabbing an instance of the class (as f) and initializing the device
f = FPGA(bitfile = 'fixDefines.bit')
f.init_device() # programs the FPGA (loads bit file)

# setup the control wire so we can drive signals coming from host to FPGA and vice versa
f.set_wire(0x1, 1, 1) # Host driven SPI reads/write 
send_trig(clk_reset)

# setup the data wire to the FPGA so it can get data from the FPGA
# no setup needed of the wire 
# f.set_wire(0x05, 0xFFFF, mask = 0xFFFF)