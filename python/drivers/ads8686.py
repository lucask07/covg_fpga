import sys
import time
import os
from collections import namedtuple
import logging

cwd = os.getcwd() # gets the current working directory
path = os.path.join(cwd, "covg_fpga/python/drivers")
sys.path.append(path)

from fpga import FPGA

path1 = os.path.join(cwd, "covg_fpga/python/drivers")
sys.path.append(path1)
from utils import rev_lookup, bin, test_bit, twos_comp

############# TODO: Integrate the Logging feature/lib ############
logging.basicConfig(filename = 'ads8686data.log', encoding = 'utf-8', level = logging.INFO)
logging.info('------------------------------------------------------------------------------------------')
logging.warning('this is a way')
logging.critical('to check if logging works')

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

############### SPI Controller Addresses and Configuration ###############
# SPI Register Addresses
ssreg_addr = 0x61 # ss register
divreg_addr = 0x51 # clk divider register
creg_addr = 0x41 # control register
Txreg_addr = 0x01 # Tx/Rx register (at the same address! But has dual functionality)

# Configuring the SPI controller
creg_set = 0x3010 # Char length of 16. Samples Tx/Rx on POS edge; sets ASS, IE
clk_div = 0x18 # Takes the given clk at 10MHz and divides it so you get a 2MHz clk instead
ss = 0x1 # sets the active ss line by setting the LSB of a SPI command to 1 during configuration

# SPI write and read commands
wb_w = 0x40000000  # indicates a wishbone transfer via writing to a chip (ADS8686) register (don't change)
wb_r = 0x80000000 # indicates a wishbone transfer by reading a chip register (don't change)

################## Register Addresses for the ADS8686 ##########################
config = 0x400 # 16 bits, Fig 77. 
''' Hex = 0x8400 '''
    # bit 15: write access = 1
    # bits 14-9: accesses reg. by writing the address (which is 0x2 == 0'b000010)
    # bits 8-7: read only... so put 0's
    # bits 6-0: disable burst mode, sequencer, oversampling, status register output control, and crc control

chan_sel = 0x600 # 16 bits, Fig 78.
''' Hex 0x8600 '''
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (which is 0x3 == 0'b000011)
    # bit 8: reserved - 0
    # bits 7-4: B channel select. Only using SDOA (1 output) so set to fixed code
        # write 1011b (should give us the fixed result 0x5555)
    # bits 3-0: A channel select. Keep It Simple so go with 0000b to selet AIN_0A
        # write 1011b (should give us the fixed result 0x5555)

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
devID = 0x2000 # 16 bits, Fig 87. Hex = 0x4000 [address 0x10]
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
    ''' Configures the SPI controller by setting the clock divider, control register, and ss
    register. ONLY RUN 1x to avoid improper configuration! '''
    for val in [wb_r | divreg_addr, wb_w | clk_div, # divider (need to look into settings of 1 and 2 didn't show 16 clock cycles) 
                wb_r | creg_addr,   wb_w | creg_set,  # control register (CHAR_LEN = 16, bits 10,9, 13 and 12)
                wb_r | ssreg_addr,  wb_w | ss]: # slave select (just setting bit0) [the controller has 8 ss lines]
        # sets a wire to the FPGA to send each command and then triggers the Opal Kelly
        f.set_wire(control.addr, val, mask = 0xffffffff)
        send_trig(valid) 

# Expects a 8-digit hex command!!
def sendSPI(message): # what needs to be written to the ADS?
    ''' Send 16 bits (2 bytes) of SPI data and read any result sent back along SDO.
    Writes to a register by storing the message in the Tx register, then tells
    the control register to go (1 in LSB) and receives the read value '''

    for i in range(2):
        for val in [wb_r | Txreg_addr, wb_w | message, # go to the Tx register, store data to send (from cmd)
                    wb_r | creg_addr,  wb_w | (creg_set | (1 << 8))]: # Tells the Control register - GO (bit 8)
            f.set_wire(control.addr, val, mask = 0xffffffff) # sets the wire to the ADS8686 and adds mask to get correct data back
            send_trig(valid)

    # Now read the result back, store it, print to the console, and return
    addr = read_wire(one_deep_fifo)
    print('Value read is 0x{:02X}'.format(addr))
    return addr 

################## Actual executing code ##################

# sets up the fpga by grabbing an instance of the class (as f) and initializing the device
f = FPGA()
f.init_device() # programs the FPGA (loads bit file)

# set the SPI output mux to select a device other than the ADS7952 to avoid contention on SDO
f.set_wire(mux_control.addr, 1, mask = mux_control.bits)

################## Configure the SPI controller ##################
SPI_config()

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