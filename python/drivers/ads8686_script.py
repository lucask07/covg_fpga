import time
from collections import namedtuple
import logging

################ TODO: implement logging ################


############ List and namedtuple of Register Addresses for the ADS8686 #############
regs = namedtuple('regs', 'name reset address') # registers in order by name, reset value, and addr

r0 = regs('not_real', 0x1, 0x1) # put in a dummy register that has a fake reset code and reserved address for testing
# the 43 registers of the ADS8686
r1 = regs('config', 0x400, 0x2)
r2 = regs('chan_sel', 0x600, 0x3)
r3 = regs('rangeA1', 0x800, 0x4)
r4 = regs('rangeA2', 0xA00, 0x5)
r5 = regs('rangeB1', 0xC00, 0x6)
r6 = regs('rangeB2', 0xE00, 0x7)
r7 = regs('status', 0x0, 0x8)
r8 = regs('over_rangeA', 0x1400, 0xA)
r9 = regs('over_rangeB', 0x1600, 0xB)
r10 = regs('lpf_config', 0x1A00, 0xD)
r11 = regs('devID', 0x2000, 0x10)
r12 = regs('seq0', 0x4000, 0x20)
r13 = regs('seq1', 0x4200, 0x21)
r14 = regs('seq2', 0x4400, 0x22)
r15 = regs('seq3', 0x4600, 0x23)
r16 = regs('seq4', 0x4800, 0x24)
r17 = regs('seq5', 0x4A00, 0x25)
r18 = regs('seq6', 0x4C00, 0x26)
r19 = regs('seq7', 0x4F00, 0x27)
r20 = regs('seq8', 0x5000, 0x28)
r21 = regs('seq9', 0x5200, 0x29)
r22 = regs('seq10', 0x5400, 0x2A)
r23 = regs('seq11', 0x5600, 0x2B)
r24 = regs('seq12', 0x5800, 0x2C)
r25 = regs('seq13', 0x5A00, 0x2D)
r26 = regs('seq14', 0x5C00, 0x2E)
r27 = regs('seq15', 0x5E00, 0x2F)
r28 = regs('seq16', 0x6000, 0x30)
r29 = regs('seq17', 0x6200, 0x31)
r30 = regs('seq18', 0x6400, 0x32)
r31 = regs('seq19', 0x6600, 0x33)
r32 = regs('seq20', 0x6800, 0x34)
r33 = regs('seq21', 0x6A00, 0x35)
r34 = regs('seq22', 0x6C00, 0x36)
r35 = regs('seq23', 0x6E00, 0x37)
r36 = regs('seq24', 0x7000, 0x38)
r37 = regs('seq25', 0x7200, 0x39)
r38 = regs('seq26', 0x7400, 0x3A)
r39 = regs('seq27', 0x7600, 0x3B)
r40 = regs('seq28', 0x7800, 0x3C)
r41 = regs('seq29', 0x7A00, 0x3D)
r42 = regs('seq30', 0x7C00, 0x3E)
r43 = regs('seq31', 0x7E00, 0x3F)

# list of all r values in order to connect to the named tuple object
reglist = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17,
r18, r19, r20, r21, r22, r23, r24, r25, r26, r27, r28, r29, r30, r31, r32, r33, r34, r35, 
r36, r37, r38, r39, r40, r41, r42, r43]

# Varibles used to prevent mistyping and to better organize the code
msg_w = 0x8000 # This is used to tell the ADS8686 board that we are going to write to one of it's registers by setting bit 15 high

################ Handles reading and writing data to/from the chip ###################
def writeReg(msg, reg_number):
    print('--'*40) # for a clean terminal
    which_reg = reglist[reg_number].name
    if(msg > 0): # if we don't have a blank message, we're sending a message
        print('Write 0x{:X} to the {} register'.format(msg, which_reg)) # for debugging and to keep track: tell us which reg we are looking at
        cmd = (reglist[reg_number].reset | wb_w | msg | msg_w) # concatenate the reg addr w/a wishbone write and message to build a complete SPI command
    else: # otherwise, we're reading the register
        print('Reading the %s register'%which_reg) # for debugging and to keep track: tell us which reg we are looking at
        cmd = (reglist[reg_number].reset | wb_w) # concatenate the reg addr w/a wishbone write (no message) to build a complete SPI command
    print('Your command is 0x{:02X}'.format(cmd))
    sendSPI(cmd)

################ Changes a setting of the SPI controller ################
def changeSettings():
    global creg_set
    global clk_div
    print('Here are the following settings you may configure: ')
    print('\t clock frequency,')
    print('\t clock edge\n')
    print('Please type clkedge or clkfreq to view the variable status or change their values')

    view = input() # stores which var the user wants to view/change

    if(view == 'clkedge'):
        print('The clock can be sampled on the rising or falling edge')
        if(creg_set == 0x3010): # clock is being sampled on the rising edge
            print('The clock is currently sampled on the rising edge. Press y to change to falling edge or press a different key to cancel')
            choice = input() # determines if clk edge will be changed

            if(choice == 'y'): # if the user wants to change the edge, update creg_set and notify them
                creg_set = 0x3610
                print('The clock will now be sampled on the falling edge. Please reset to reconfigure the board.')
            else: # otherwise, keep creg the same (but set it here to make sure it wasn't a weird value)
                creg_set = 0x3010
                print('The clock will continue to be sampled on the rising edge since y was not entered')
        else: # clock is set to be sampled on the falling edge
            print('The clock is currently sampled on the falling edge. Press y to chnage to rising edge or press a different key to cancel')
            choice = input()
            if(choice == 'y'): # if the user wants to change the edge, update creg_set and notify them
                creg_set = 0x3010
                print('The clock will now be sampled on the rising edge. Please reset to reconfigure the board')
            else: #otherwise, keep creg the same
                creg_set = 0x3610
                print('The clock will continue to be sampled on the falling edge since y was not entered')
        return hex(creg_set)
    elif(view == 'clkfreq'):
        print('The maximum speed for sclk is 50 MHz (50000000 Hz).')
        current_freq = (int)(50_000_000/((int)(clk_div) + 1)) # calculate the current frequency (see spi.doc)
        print('The current frequency of sclk is %d Hz. Please enter the desired frequency of sclk (in Hz)'%current_freq)
        
        new_freq = input() # user enters the desired frequency

        if(new_freq == current_freq): # if the same frequency is entered, leave clk_div alone
            print('The same sclk frequency was entered so the clock will continue to run at %d Hz'%current_freq)
        elif((int)(new_freq) < 0): # negative frequency was given, abort
            print('An invalid frequency was detected. Please enter a frequency that is nonzero, non-negative, and is between the range of 0 Hz and 50 MHz')
        elif((int)(new_freq) > 50_000_000): # too large of a frequency was given, abort
            print('An invalid frequency was detected. Please enter a frequency that is nonzero, non-negative, and is between the range of 0 Hz and 50 MHz')
        else: # a valid frequency was entered, so calculate the new clk_div value, set it, and tell the suer the new operating frequency
            new_freq = (int)(new_freq) # take the input and turn it into a int, not a string
            calc = (int)((50_000_000/(new_freq)) - 1) # find the new value of the clock divider
            current_freq = (int)(50_000_000/((int)(calc) + 1)) # calculate the new frequency and notify the user
            clk_div = (hex)(calc)
            print('Settings have been updated. The new frequency will run at %d Hz. Please reset to reconfigure the board'%current_freq)
        return clk_div
    else: # if neither clkedge or clkfreq were entered, tell the user of the invalid entry
        print('Neither clkedge or clkfreq were entered. Please call the function again if you would like to change the settings.')        
