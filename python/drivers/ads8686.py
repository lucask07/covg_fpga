import sys
import time
import os
from collections import namedtuple

cwd = os.getcwd() # gets the current working directory
path = os.path.join(cwd, "covg_fpga/python")
sys.path.append(path)

from fpga import FPGA
from drivers.utils import rev_lookup, bin, test_bit, twos_comp
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

################## SPI Controller configuration ##################

wb_wr_msbs = 0x40000000  # the value to indicate a wishbone transfer (don't change)
spi_ctrl_creg_val = 0x3610 # Char length of 16. Will set Tx_NEG, Rx_NEG; set ASS, IE.  ADS8686
spi_ctrl_divider = 0x0004 # clock divider
spi_ctrl_ss = 0x0001 # determine which of eight slave select lines are active

################## Register Addresses for the ADS8686 ##########################
config_val = 0x4200 # 16 bits, Fig 77. Hex = 0x8400 to write (was 0x4200 for read)
    # bit 15: write access = 1
    # bits 14-9: accesses reg. by writing the address (which is 0x2 == 0'b000010)
    # bits 8-7: read only... so put 0's
    # bits 6-0: disable burst mode, sequencer, oversampling, status register output control, and crc control

chan_sel_val = 0x86B0 # 16 bits, Fig 78. Hex = 0x86B0
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (which is 0x3 == 0'b000011)
    # bit 8: reserved - 0
    # bits 7-4: B channel select. Only using SDOA (1 output) so set to fixed code
        # by writing 1011b (should give us the fixed result 0x5555)
    # bits 3-0: A channel select. Keep It Simple so go with 0000b to selet AIN_0A

rangeA1_val = 0x8800 # 16 bits, Fig 79. Hex = 0x8800 
    # bit 15: write
    # bits 14-9: access reg. by writing address (0x4 == 0b000100)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 10V = 00
    # bits 5-4: voltage selection for +/- 10V = 00
    # bits 3-2: voltage selection for +/- 10V = 00
    # bits 1-0: voltage selection for +/- 10V = 00

dev_ID_val = 0x4000 # 16 bits, Fig 87. Hex = 0x4000 [address 0x10]
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (0x10 == 0'b010000)
    # bits 8-2: reserved - 000000
    # bits 1-0: DEV_ID register - read only so write 00

################## Define functions ##################

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


def SPI_config():
    '''
    Configure the SPI controller within the FPGA 
    only need to run once.
    Configures 
    1) clock divider, 
    2) the control register and 
    3) the slave select lines
    '''
    for val in [0x80000051, wb_wr_msbs | spi_ctrl_divider_val, # divider (need to look into settings of 1 and 2 didn't show 16 clock cycles) 
                0x80000041, wb_wr_msbs | spi_ctrl_creg_val,  # control register (CHAR_LEN = 16, bits 10,9, 13 and 12)
                0x80000061, wb_wr_msbs | spi_ctrl_ss]: # slave select (just setting bit0) [the controller has 8 ss lines]

        f.set_wire(control.addr, val, mask = 0xffffffff)
        send_trig(valid) 


def send_SPI(value_tosend): # what needs to be written to the ADS?
    '''
    Send 16 bits (2 bytes) of SPI data
    Read any result sent back along SDO
    '''

    send = wb_wr_msbs | value_tosend

    for val in [0x80000001, send,  # go to the Tx register, store data to send (from cmd) 
                0x80000041, wb_wr_msbs | (spi_ctrl_creg_val | (1 << 8))]: # Tells the Control register - GO (bit 8) - sends val to ADS8686
        f.set_wire(control.addr, val, mask = 0xffffffff) # sets the wire to the ADS8686 w/val and adds mask to get correct data back
        send_trig(valid)

    a = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(a))
    return a    


################## Actual executing code ##################

# sets up the fpga by grabbing an instance of the class (as f) and initializing the device
f = FPGA()
f.init_device() # programs the FPGA (loads bit file)

# set the SPI output mux to select a device other than the ADS7952 to avoid contention on SDO
f.set_wire(mux_control.addr, 1, mask = mux_control.bits)

################## Configure the SPI controller ##################
SPI_config()

################## Send commands to the device ##################

# runs send_SPI with each of the values in order to get the correct data
# send_SPI(config_val) # configure the ADS chip
# send_SPI(chan_sel_val) # choose which channels we want to access
# send_SPI(rangeA1_val) # set up the voltage we're using

# read the device ID -- this should return 2 (or maybe 0x2002)
dev_id = send_SPI(dev_ID_val) # access the device_ID register and read it's address (*remember: uses a WRITE command to do so)

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