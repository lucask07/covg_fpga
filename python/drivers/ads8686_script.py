import numpy as np
from utils import rev_lookup, bin, test_bit, twos_comp, two2dec
import logging

# import ads8686

############# Set up the Logging feature/lib ############
logging.basicConfig(filename = 'ads8686data.log', encoding = 'utf-8', level = logging.INFO)

############ List and Class of Registers Addresses for the ADS8686 #############
dictofRegs = {} # now make a blank dictionary that will help us connect the reglist we have and use indices so we can grab the right class object to get it's reset code, etc

class regs(object): # define a class that sorts registers by their order (r1, r2, etc), name, reset value, address, and default value after reset    
    def __init__(self, addr, default):
        # list the attributes specific to each object (passed in as self) to the class
        self.addr = addr
        self.default = default

    '''
    NOTE: the default value of the devID reg according to the datasheet is 0x2002. It is located at address 0x10.
        --> However, value read back from FPGA is 0x2. MOSI shows 0x2000 and MISO shows 0x0002.
         This is because the first byte (MSB byte) is for master out slave in and the last byte (LSB) is for master in slave out
        *** To reset a register, ONLY send the MSB value because the chip should send back the least significant byte's value
            for example: the rangeA1 is at an address of 0x4. The reset code is the address shifted left 1 bit (0x8) in the MSB place
            So we would send a value of 0x800 along the wishbone bus and the chip should hand back the default/expected value of 0xFF 
                (unless it was programmed otherwise)
    '''

class chip(): # new class that attaches the index of the dictionary to the object within the regs class so we can grab the address of a reg
    # put in a dummy register that has a fake reset code and reserved address for testing
    dictofRegs['not_real']    = regs(0x0, 0x0)
    # the 43 registers of the ADS8686, change for other boards
    dictofRegs['config']      = regs(0x2, 0x0)
    dictofRegs['chan_sel']    = regs(0x3, 0x0)
    dictofRegs['rangeA1']     = regs(0x4, 0xFF)
    dictofRegs['rangeA2']     = regs(0x5, 0xFF)
    dictofRegs['rangeB1']     = regs(0x6, 0xFF)
    dictofRegs['rangeB2']     = regs(0x7, 0xFF)
    ''' Status is a read only register... don't think we need a case for this? '''
    dictofRegs['status']      = regs(0x8, 0x0) 
    dictofRegs['over_rangeA'] = regs(0xA, 0x0)
    dictofRegs['over_rangeB'] = regs(0xB, 0x0)
    dictofRegs['lpf']  = regs(0xD, 0x0)
    dictofRegs['devID']       = regs(0x10, 0x2)
    dictofRegs['seq0']        = regs(0x20, 0x0)
    dictofRegs['seq1']        = regs(0x21, 0x11)
    dictofRegs['seq2']        = regs(0x22, 0x22)
    dictofRegs['seq3']        = regs(0x23, 0x33)
    dictofRegs['seq4']        = regs(0x24, 0x44)
    dictofRegs['seq5']        = regs(0x25, 0x55)
    dictofRegs['seq6']        = regs(0x26, 0x66)
    dictofRegs['seq7']        = regs(0x27, 0x77) 
    ''' Should this be  0x4E00???'''
    dictofRegs['seq8']        = regs(0x28, 0x0)
    dictofRegs['seq9']        = regs(0x29, 0x0)
    dictofRegs['seq10']       = regs(0x2A, 0x0)
    dictofRegs['seq11']       = regs(0x2B, 0x0)
    dictofRegs['seq12']       = regs(0x2C, 0x0)
    dictofRegs['seq13']       = regs(0x2D, 0x0)
    dictofRegs['seq14']       = regs(0x2E, 0x0)
    dictofRegs['seq15']       = regs(0x2F, 0x0)
    dictofRegs['seq16']       = regs(0x30, 0x0)
    dictofRegs['seq17']       = regs(0x31, 0x0)
    dictofRegs['seq18']       = regs(0x32, 0x0)
    dictofRegs['seq19']       = regs(0x33, 0x0)
    dictofRegs['seq20']       = regs(0x34, 0x0)
    dictofRegs['seq21']       = regs(0x35, 0x0)
    dictofRegs['seq22']       = regs(0x36, 0x0)
    dictofRegs['seq23']       = regs(0x37, 0x0)
    dictofRegs['seq24']       = regs(0x38, 0x0)
    dictofRegs['seq25']       = regs(0x39, 0x0)
    dictofRegs['seq26']       = regs(0x3A, 0x0)
    dictofRegs['seq27']       = regs(0x3B, 0x0)
    dictofRegs['seq28']       = regs(0x3C, 0x0)
    dictofRegs['seq29']       = regs(0x3D, 0x0)
    dictofRegs['seq30']       = regs(0x3E, 0x0)
    dictofRegs['seq31']       = regs(0x3F, 0x0)

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

# Used to  organize the code for building write commands to chip
msg_w = 0x8000 # This is used to tell the ADS8686 board that we are going to write to one of it's registers by setting bit 15 high

################ Handles configuratoin, reading, and writing data to/from the chip via SPI ###################
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
        for val in [wb_r | Txreg_addr, message, # go to the Tx register, store data to send (from cmd)
                    wb_r | creg_addr,  wb_w | (creg_set | (1 << 8))]: # Tells the Control register - GO (bit 8)
            f.set_wire(control.addr, val, mask = 0xffffffff) # sets the wire to the ADS8686 and adds mask to get correct data back
            send_trig(valid)

    # Now read the result back and store it print to the console and return
    addr = read_wire(one_deep_fifo)    

    return addr 

def writeReg(msg, reg_name):
    ''' Writes to a specific register on the ads8686 by using wishbone commands and stored Hex
    values above to either configure a register to its default value or change a register appropriately
    (For example: setting the board to read voltages off the A channel instead of the B channel)
    '''
    print('--'*40) # for a clean terminal
    if(msg == 0): # if we want to read a register
        print('Reading the %s register'%reg_name) # for debugging and to keep track: tell us which reg we are looking at
        cmd = ((dictofRegs[reg_name].addr) * 0x100) # get the MSB digits so we can set the register correctly
        cmd = (cmd << 1) # to reset the register, shift it's address 1 to the left
        # cmd = hex(cmd) # make sure that the command is in hex so it can be bitwise or-ed with the wishbone commands
        cmd = (cmd | wb_w) # concatenate the reg addr w/a wishbone write (no message) to build a complete SPI command
    else: # otherwise, we're sending a message
        print('Write 0x{:X} to the {} register'.format(msg, reg_name)) # for debugging and to keep track: tell us which reg we are looking at
        # get the MSB digits so we can set the register correctly
        cmd = ((dictofRegs[reg_name].addr) * 0x100)
        cmd = (cmd << 1) # to reset the register, shift it's address 1 to the left
        # cmd = hex(cmd) # make sure that the command is in hex so it can be bitwise or-ed with the wishbone commands
        cmd = (cmd | wb_w | msg | msg_w) # concatenate the reg addr w/a wishbone write and message to build a complete SPI command
        ''' Add 0x8000 to set the MSB bit (bit 15) to 1? '''
    
    print('Your command is 0x{:X}'.format(cmd)) # print to the console to double check our math
    check = sendSPI(cmd) # store the sent result

    print('Read back 0x{:X}'.format(check))

    # check if the read address matches the defauly value and log the result
    if(check == dictofRegs[reg_name].default): # if the correct address was read back
        logging.info('     {} register: Default 0x{:X}, read {}'.format(reg_name, dictofRegs[reg_name].default, hex(check)))
    else: # if another register address was given
        logging.warning('  {} register: Default 0x{:X}, read {}'.format(reg_name, dictofRegs[reg_name].default, hex(check)))

    return check

def readAll(): # reads all 43 reg's and prints their values
    logging.info('------------------------------------------------------------------------------------------')
    for register in dictofRegs: # lists are indexed starting at 0, so i should too
        writeReg(0, str(register)) # use writeReg to send a blank message to see a reg's value
    print('All registers read.')

''' Eventually will move to the ads8686.py file since it is specific to this chip, but for now it'll stay here'''
################ Reads a V off the ads8686 #################
vset = 5 # what is the digital voltage of the power supply set to?

def readVsetup(vset): # sets up the appropriate vars and chip settings before reading a V
    # for 5V digital voltage in. Codes built from reading the datasheet and configuring the channels appropriately
    A15V = 0x8AA # A1 Range reg
    A25V = 0xAAA # A2 Range reg
    B15V = 0xCAA # B1 Range reg
    B25V = 0xEAA # B2 Range reg (same for below)

    # for 2.5V digital voltage in. Codes from reading datasheet and configuring the analog channels appropriately
    A125V = 0x855
    A225V = 0xA55
    B125V = 0xC55
    B225V = 0xE55

    # Now beging sending commands to the config, chan_sel, range(A1, A2, B1, and B2), over range A/B, and lpf_config 
    configCmd = writeReg(0, 'config') # config the reg using default val (no overrange, oversampling, etc)
    chan_selCmd = writeReg(0, 'chan_sel') # selects AIN_0A/0B to be read

    # to set the range correctly, evaluate the status of vset (digital volt)
    # NO OVERRANGE support yet
    if(vset == 10): # set all channels to vin = 10V (only need rangeA1, but set all to be safe)
        A1Cmd = writeReg(0, 'rangeA1')
        A2Cmd = writeReg(0, 'rangeA2')
        B1Cmd = writeReg(0, 'rangeB1')
        B2Cmd = writeReg(0, 'rangeB2')
    elif(vset == 5): # set all channels to vin = 5V
        A1Cmd = writeReg(A15V, 'rangeA1')
        A2Cmd = writeReg(A25V, 'rangeA2')
        B1Cmd = writeReg(B15V, 'rangeB1')
        B2Cmd = writeReg(B25V, 'rangeB2')
    else: # when vset = 2.5v for vin
        A1Cmd = writeReg(A125V, 'rangeA1')
        A2Cmd = writeReg(A225V, 'rangeA2')
        B1Cmd = writeReg(B125V, 'rangeB1')
        B2Cmd = writeReg(B225V, 'rangeB2')

    # ensure that the over range and the cutoff freq is disabled
    overACmd = writeReg(0, 'over_rangeA')
    overBCmd = writeReg(0, 'over_rangeB')
    lpfCmd = writeReg(0, 'lpf')

    # get the code we need to analyze from AIN_0A (shows up on SDOA) and analyze with readV()
    code = writeReg(0, 'rangeA1') # just want to read so use 0
    
    '''
    for i in range(16):
        sendSPI(wb_w) # use a NOP code and see what the reg gives
    '''
    return code

    # readV(code) # setup complete! now decode

def readV(code):
    ''' Analyzes a 16 bit code (in binary 2's complement) that can be converted
    into the v read from the chip using basic math (see fig 54) '''
        # positive codes: 000...001 - 011...111
        # negative codes: 111...111 - 100...000
        # zero code: 000_000

    # set the LSB w/respect to current power supply (accounts for over range) to calculate v (see equation in figure 54)
    if(vset == 12):
        LSB = 0.000366 # in V! Tells how accurate (large/small) step size is
    elif(vset == 10):
        LSB = 0.000305
    elif(vset == 6):
        LSB = 0.000183
    elif(vset == 5):
        LSB = 0.000152
    elif(vset == 3):
        LSB = 0.000092
    elif(vset == 2.5):
        LSB = 0.000076
    elif(vset == 1):
        LSB = 0.0000305
    else: # for a value that isn't on the datasheet, calculate the LSB value
        LSB = ((2*vset)/65536) # or (2*vset)/2^16
    
    code = float(code) # change to a float since we can't make a float into an int
    # calculate the v that was read and hand the res back
    v = (code*LSB) - vset

    return v

################ Changes a setting of the SPI controller ################
    # to change the clock edge, set view to 'clkedge' and then choice to 'f' for falling or 'r' for rising edge
    # to change the clk divider, set view to 'clkfreq' and then set choice to the desired frequency of the clock in Hz, like '10'

# eventually these vars will be passed in from another file, place here for testing
view = 'clkfreq'
choice = 10_000_000

def changeSettings(view, choice): 
    # makes creg_set and clk_div changeable and then returned to update their values (not permanent??)
    global creg_set
    global clk_div

    if(view == 'clkedge'): # view and possibly modify the clkedge
        if(creg_set == 0x3010): # clock is being sampled on the rising edge
            print('The clock is currently sampled on the rising edge.')

            if(choice == 'f'): # if the user wants to change the edge, update creg_set and notify them
                creg_set = 0x3610
                print('The clock will now be sampled on the falling edge. Please reset to reconfigure the board.')
            else: # otherwise, keep creg the same (set it to make sure it wasn't a weird value)
                creg_set = 0x3010
                print('The clock will continue to be sampled on the rising edge.')
        
        else: # clock is set to be sampled on the falling edge
            print('The clock is currently sampled on the falling edge.')
            if(choice == 'r'): # if the user wants to change the edge, update creg_set and notify them
                creg_set = 0x3010
                print('The clock will now be sampled on the rising edge. Please reset to reconfigure the board')
            else: # otherwise, keep creg the same (set it to make sure it wasn't a weird value)
                creg_set = 0x3610
                print('The clock will continue to be sampled on the falling edge.')
        
        return hex(creg_set) # return creg_set so the change of clk edge can be saved
    
    elif(view == 'clkfreq'):
        print('The maximum speed for sclk is 50 MHz (50000000 Hz).')
        current_freq = int(50_000_000/(int(clk_div) + 1)) # calculate the current frequency (see spi.doc for equation)
        print('The current frequency of sclk is %d Hz.'%current_freq)
        
        if(choice == current_freq): # if the same frequency is entered, leave clk_div alone
            print('The clock will continue to run at %d Hz'%current_freq)
        elif(int(choice) < 0): # negative frequency was given, abort
            print('An invalid frequency was detected. Frequency must be nonzero, non-negative, and between 0 Hz and 50 MHz')
        elif(int(choice) > 50_000_000): # too large of a frequency was given, abort
            print('An invalid frequency was detected. Frequency must be nonzero, non-negative, and between 0 Hz and 50 MHz')
        elif(int(choice) <= 195_312):
            clk_div = 0xFF
            current_freq = int(50_000_000/(int(clk_div) + 1)) # calculate the current frequency (see spi.doc for equation)
            print('The clock is set to operate at the minimum setting of %d Hz'%current_freq)
        else: # a valid frequency was entered, so calculate the new clk_div value, set it, and tell the suer the new operating frequency
            calc = int(((1/(choice/50_000_000)) - 1)) # find the new value of the clock divider
            print('calc: %d'%calc)
            current_freq = int(50_000_000/(int(calc) + 1)) # calculate the new frequency and notify the user
            clk_div = hex(calc) # update the clk_div setting
            print('The new frequency will run at %d Hz. Please reset to reconfigure the board'%current_freq)
        
        return clk_div # return clk_div so the new clk_freq will be saved
    
    else: # if neither clkedge or clkfreq were entered, tell the user of the invalid entry
        print('Neither clkedge or clkfreq were entered. Please call the function again.')        
