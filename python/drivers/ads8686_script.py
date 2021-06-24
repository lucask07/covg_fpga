import numpy as np
import logging

############# Set up the Logging feature/lib ############
logging.basicConfig(filename = 'ads8686data.log', encoding = 'utf-8', level = logging.INFO)
logging.info('------------------------------------------------------------------------------------------')

############ List and Class of Registers Addresses for the ADS8686 #############
class regs: # define a class that sorts registers by their order (r1, r2, etc), name, reset value, address, and default value after reset
    def __init__(self, name, addr, reset, default):
        # list the attributes specific to each object (passed in as self) to the class
        self.name = name
        self.addr = addr
        self.reset = reset
        self.default = default
    '''
    NOTE: the default value of the devID reg according to the datasheet is 0x2002. It is located at address 0x10.
        --> However, value read back from FPGA is 0x2.
        *** The reset code is really the address of a register shifted left 1 bit with the expected result in the 2 LSB hex bits.
            However, the ads8686 only has 1 byte to send a command, which is why when commands are sent the reset code only shows 
            the first byte, the expected value out is where the LSB byte of the default value comes from
            // data sheet shows reset | default as the reset code, but it's broken up here into the MSB and LSB
                to help with logging and debugging
    '''
    
r0 = regs('not_real', 0x0, 0x0, 0x0) # put in a dummy register that has a fake reset code and reserved address for testing

# the 43 registers of the ADS8686, change for other boards
r1 = regs('config', 0x2, 0x400, 0x0)
r2 = regs('chan_sel', 0x3, 0x600, 0x0)
r3 = regs('rangeA1', 0x4, 0x800, 0xFF)
r4 = regs('rangeA2', 0x5, 0xA00, 0xFF)
r5 = regs('rangeB1', 0x6, 0xC00, 0xFF)
r6 = regs('rangeB2', 0x7, 0xE00, 0xFF)
r7 = regs('status', 0x8, 0x0, 0x0)
r8 = regs('over_rangeA', 0xA, 0x1400, 0x0)
r9 = regs('over_rangeB', 0xB, 0x1600, 0x0)
r10 = regs('lpf_config', 0xD, 0x1A00, 0x0)
r11 = regs('devID', 0x10, 0x2000, 0x2)
r12 = regs('seq0', 0x20, 0x4000, 0x0)
r13 = regs('seq1', 0x21, 0x4200, 0x11)
r14 = regs('seq2', 0x22, 0x4400, 0x22)
r15 = regs('seq3', 0x23, 0x4600, 0x33)
r16 = regs('seq4', 0x24, 0x4800, 0x44)
r17 = regs('seq5', 0x25, 0x4A00, 0x55)
r18 = regs('seq6', 0x26, 0x4C00, 0x66)
r19 = regs('seq7', 0x27, 0x4F00, 0x77)
r20 = regs('seq8', 0x28, 0x5000, 0x0)
r21 = regs('seq9', 0x29, 0x5200, 0x0)
r22 = regs('seq10', 0x2A, 0x5400, 0x0)
r23 = regs('seq11', 0x2B, 0x5600, 0x0)
r24 = regs('seq12', 0x2C, 0x5800, 0x0)
r25 = regs('seq13', 0x2D, 0x5A00, 0x0)
r26 = regs('seq14', 0x2E, 0x5C00, 0x0)
r27 = regs('seq15', 0x2F, 0x5E00, 0x0)
r28 = regs('seq16', 0x30, 0x6000, 0x0)
r29 = regs('seq17', 0x31, 0x6200, 0x0)
r30 = regs('seq18', 0x32, 0x6400, 0x0)
r31 = regs('seq19', 0x33, 0x6600, 0x0)
r32 = regs('seq20', 0x34, 0x6800, 0x0)
r33 = regs('seq21', 0x35, 0x6A00, 0x0)
r34 = regs('seq22', 0x36, 0x6C00, 0x0)
r35 = regs('seq23', 0x37, 0x6E00, 0x0)
r36 = regs('seq24', 0x38, 0x7000, 0x0)
r37 = regs('seq25', 0x39, 0x7200, 0x0)
r38 = regs('seq26', 0x3A, 0x7400, 0x0)
r39 = regs('seq27', 0x3B, 0x7600, 0x0)
r40 = regs('seq28', 0x3C, 0x7800, 0x0)
r41 = regs('seq29', 0x3D, 0x7A00, 0x0)
r42 = regs('seq30', 0x3E, 0x7C00, 0x0)
r43 = regs('seq31', 0x3F, 0x7E00, 0x0)

# list of all r values from regs class to connect to the named tuple object
reglist = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17,
r18, r19, r20, r21, r22, r23, r24, r25, r26, r27, r28, r29, r30, r31, r32, r33, r34, r35, 
r36, r37, r38, r39, r40, r41, r42, r43]

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
        for val in [wb_r | Txreg_addr, wb_w | message, # go to the Tx register, store data to send (from cmd)
                    wb_r | creg_addr,  wb_w | (creg_set | (1 << 8))]: # Tells the Control register - GO (bit 8)
            f.set_wire(control.addr, val, mask = 0xffffffff) # sets the wire to the ADS8686 and adds mask to get correct data back
            send_trig(valid)

    # Now read the result back and store it print to the console and return
    addr = read_wire(one_deep_fifo)    

    return addr 

def writeReg(msg, reg_number):
    print('--'*40) # for a clean terminal
    which_reg = reglist[reg_number].name
    if(msg == 'r'): # if we don't have a blank message, we're sending a message
        print('Reading the %s register'%which_reg) # for debugging and to keep track: tell us which reg we are looking at
        cmd = reglist[reg_number].reset
        cmd = (cmd | wb_w) # concatenate the reg addr w/a wishbone write (no message) to build a complete SPI command
    else: # otherwise, we're reading the register
        print('Write 0x{:X} to the {} register'.format(msg, which_reg)) # for debugging and to keep track: tell us which reg we are looking at
        cmd = reglist[reg_number].reset
        cmd = (cmd | wb_w | msg | msg_w) # concatenate the reg addr w/a wishbone write and message to build a complete SPI command
    
    print('Your command is 0x{:X}'.format(cmd))
    check = sendSPI(cmd) # store the sent result

    # check if the read address matches the defauly value and log the result
    if(check == reglist[reg_number].default): # if the correct address was read back
        logging.info('  {} register: Default 0x{:X}, read {}'.format(which_reg, reglist[reg_number].default, hex(check)))
    else: # if another register address was given
        logging.warning('  {} register: Default 0x{:X}, read {}'.format(which_reg, reglist[reg_number].default, hex(check)))

def readAll(): # reads all 43 reg's and prints their values
    for i in range(len(reglist)):
        writeReg(0x0, i)
    print('All registers read.')

################ Changes a setting of the SPI controller ################
    # to change the clock edge, type 'clkedge' and then 'f' for falling or 'r' for rising edge
    # to change the clk divider, type 'clkfreq' and then the desired frequency of the clock in Hz, like '10'

# eventually these vars will be passed in from another file, place here for testing
view = 'clkfreq'
choice = 10

def changeSettings(view, choice): 
    # makes creg_set and clk_div changeable and then returned to update their values (not permanent??)
    global creg_set
    global clk_div
    
    # prints the available settings to config the SPI controller
    print('Here are the following settings you may configure: ')
    print('\t clock frequency,')
    print('\t clock edge\n')

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
            # new_freq = int(choice) # take the input and turn it into a int, not a string
            calc = int(np.log2((50_000_000/int(choice)) - 1)) # find the new value of the clock divider
            current_freq = int(50_000_000/(int(calc) + 1)) # calculate the new frequency and notify the user
            clk_div = hex(calc) # update the clk_div setting
            print('The new frequency will run at %d Hz. Please reset to reconfigure the board'%current_freq)
        
        return clk_div # return clk_div so the new clk_freq will be saved
    
    else: # if neither clkedge or clkfreq were entered, tell the user of the invalid entry
        print('Neither clkedge or clkfreq were entered. Please call the function again.')        

################ Run these statements when the program is initialized ################
readAll()

'''
################## Register Addresses for the ADS8686 ##########################
config = 0x400 # 16 bits, Fig 77. 
    # Hex = 0x8400 
    # bit 15: write access = 1
    # bits 14-9: accesses reg. by writing the address (which is 0x2 == 0'b000010)
    # bits 8-7: read only... so put 0's
    # bits 6-0: disable burst mode, sequencer, oversampling, status register output control, and crc control

chan_sel = 0x600 # 16 bits, Fig 78.
    # Hex 0x8600 
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (which is 0x3 == 0'b000011)
    # bit 8: reserved - 0
    # bits 7-4: B channel select. Only using SDOA (1 output) so set to fixed code
        # write 1011b (should give us the fixed result 0x5555)
    # bits 3-0: A channel select. Keep It Simple so go with 0000b to selet AIN_0A
        # write 1011b (should give us the fixed result 0x5555)

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
    # Hex 0xA000? 
    # bit 15: write access
    # bits 14-9: access reg. by writing the address (0x10 == 0'b010000)
    # bits 8-2: reserved - 000000
    # bits 1-0: DEV_ID register - read only so write 00

rangeA1 = 0x800 # 16 bits, Fig 79. 
    # Hex = 0x8800? 
    # bit 15: read (0)
    # bits 14-9: access reg. by writing address (0x4 == 0b000100)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 5V = 10b
    # bits 5-4: voltage selection for +/- 5V = 10b
    # bits 3-2: voltage selection for +/- 5V = 10b
    # bits 1-0: voltage selection for +/- 5V = 10b

rangeA2 = 0xA00 # 16 bits, Figure 80
    # Hex 0x8A00? 
    # bit 15: read (0)
    # bits 14-9: register addresss (0x5 == 0b000101)
    # bit 8: reserved - 0
    # bits 7-6: voltage selection for +/- 5V = 10b
    # bits 5-4: voltage selection for +/- 5V = 10b
    # bits 3-2: voltage selection for +/- 5V = 10b
    # bits 1-0: voltage selection for +/- 5V = 10b

rangeB2 = 0xE00 # 16 bits, Figure 82
    # Hex 0x8E00? 
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
    # Hex 0xC000? or 0xC000? 
    # bit 15: read (0)
    # bits 14-9: register address (0x20 == 0b100000)
    # bit 8: reserved - 0
    # bits 7-4: CHSEL_B[3:0] 0b1011 for code 0x5555
    # bits 3-0: CHSEL_A[3:0] 0b1011 for code 0x5555
'''