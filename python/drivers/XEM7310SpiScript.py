import numpy as np
from utils import twos_comp
import logging

############# Set up the Logging feature/lib ############
logging.basicConfig(filename = 'XEM7310data.log', encoding = 'utf-8', level = logging.INFO)

############ List and Class of Registers Addresses for the ADS8686 #############
dictofRegs = {} # now make a blank dictionary that will help us connect the reglist we have and use indices so we can grab the right class object to get it's reset code, etc

class regs(object): # define a class that sorts registers by their order (r1, r2, etc), name, reset value, address, and default value after reset    
    def __init__(self, addr, default):
        # list the attributes specific to each object (passed in as self) to the class
        self.addr = addr
        self.default = default

class chip(): # new class that attaches the index of the dictionary to the object within the regs class so we can grab the address of a reg
    # the 43 registers of the ADS8686, change for other boards
    dictofRegs['config']      = regs(0x2, 0x0)
    dictofRegs['chan_sel']    = regs(0x3, 0x0)
    dictofRegs['rangeA1']     = regs(0x4, 0xFF)
    dictofRegs['rangeA2']     = regs(0x5, 0xFF)
    dictofRegs['rangeB1']     = regs(0x6, 0xFF)
    dictofRegs['rangeB2']     = regs(0x7, 0xFF)
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
creg_set = 0x3710 # Char length of 16. Samples Tx/Rx on NEG edge; sets ASS, IE
clk_div = 0x12 # 200 MHz / 0x12 / 2 = 5.555 MHz  ==> 2.88 us for 16 SPI clocks
ss = 0x1 # sets the active ss line by setting the LSB of a SPI command to 1 during configuration

# SPI write and read commands
wb_w_reg = 0x40000000  # writes to the wishbone register 
wb_set_reg = 0x80000000  # sets the wishbone address to access  

# Used to  organize the code for building write commands to chip
msg_w = 0x8000 # This is used to tell the ADS8686 board that we are going to write to one of it's registers by setting bit 15 high

################ Handles configuration, reading, and writing data to/from the chip via SPI ###################
def SPI_config():
    ''' First sets triggers to listen to host(python) commands, resets the clk divider and fifo, and resets the fpga. Then
    it configures the SPI controller by setting the clock divider, control register, and ss
    register. ONLY RUN 1x to avoid improper configuration! '''
    
    # first: reset fpga, fifo, spi controller clk_divider, and set to listen to host commands
    # f.xem.ActivateTriggerIn(0x40, 1)    # resets the fpga

    # write to the register bridge to setup the device (okRegBridge needs an addr and the value to send to the clk)
    # f.xem.WriteRegister(0, 6) # pass in the address (0) and value to divide the clk (must be a multiple of 2)   
    # f.xem.ActivateTriggerIn(0x40, 11) # tell the wb to start the data transmission process

    # f.xem.ActivateTriggerIn(0x40, 10)   # resets the spi controller clock divider
    # f.xem.ActivateTriggerIn(0x40, 2)    # empties the fifo for the ads8686
    # f.xem.ActivateTriggerIn(0x40, 11)   # initiates host wishbone and SPI transactions
    f.set_wire(0x1, 1, 0xFFFF)             # sets the wire for spi_driver so the host is driving commands

    for val in [wb_set_reg | divreg_addr, wb_w_reg | clk_div, # divider (need to look into settings of 1 and 2 didn't show 16 clock cycles) 
                wb_set_reg | creg_addr,   wb_w_reg | creg_set,  # control register (CHAR_LEN = 16, bits 10,9, 13 and 12)
                wb_set_reg | ssreg_addr,  wb_w_reg | ss]: # slave select (just setting bit0) [the controller has 8 ss lines]
        # print('Sending command 0x{:X}'.format(val))
        # print('Control address is 0x{:X}'.format(control.addr))
        # sets a wire to the FPGA to send each command and then triggers the Opal Kelly
        f.set_wire(control.addr, val, mask = 0xffffffff)
        send_trig(valid) 

# Expects a 8-digit hex command!!
def sendSPI(message): # what needs to be sent to the ADS?
    ''' Send 16 bits (2 bytes) of SPI data and read any result sent back along SDO.
    Writes to a register by storing the message in the Tx register, then tells
    the control register to go (1 in LSB) and receives the read value '''

    print('Sending 0x{:X}'.format(message))

    for i in range(2): # do this twice so that the read back result is correct? 
        for val in [wb_set_reg | Txreg_addr, wb_w_reg | message, # go to the Tx register, store data to send (from cmd)
                    wb_set_reg | creg_addr,  wb_w_reg | (creg_set | (1 << 8))]: # Tells the Control register - GO (bit 8)
            # print('Sending command 0x{:X}'.format(val))
            # print('Control address is 0x{:X}'.format(control.addr))
            f.set_wire(control.addr, val, mask = 0xffffffff) # sets the wire to the ADS8686 and adds mask to get correct data back
            send_trig(valid)
    
    # Now read the result back and store it print to the console and return
    data = read_wire(one_deep_fifo) 
    print('Read back 0x{:X}'.format(data))

    return data

def writeRegBridge():
    ''' Goes to the register bridge and writes a value that will be used during FPGA driven SPI '''
    
    # Configures the clock divider to determine the CONVST frequency 
    res = f.xem.WriteRegister(0x0, 1000) # (1/200e6)*1000 = 5 us period  
    f.xem.ActivateTriggerIn(0x40, 11) # load the register bridge data 

    # now load the sequence of wishbone commands that will be sent to the SPI converter 
    res = f.xem.WriteRegister(0x1, 0x8000_0001) # Tx data register  
    f.xem.ActivateTriggerIn(0x40, 11) # load the register bridge data 

    res = f.xem.WriteRegister(0x2, 0x4000_0000) # 0x0000 loaded into the Tx register -- i.e. NOP
    f.xem.ActivateTriggerIn(0x40, 11) # load the register bridge data 

    res = f.xem.WriteRegister(0x3, 0x8000_0041) # opal kelly function that writes to a register
    f.xem.ActivateTriggerIn(0x40, 11) # load the register bridge data 

    res = f.xem.WriteRegister(0x4, 0x4000_3710) # opal kelly function that writes to a register
    f.xem.ActivateTriggerIn(0x40, 11) # load the register bridge data 

    send_trig(clk_reset) # reset the clk divider 
    f.set_wire(0x1, 0, 1) # lower the control bit for host vs. FPGA driven so the FPGA can take control of sending SPI commands, won't listen to python anymore

def readRegBridge(reg):
    pass 
    ''' This is not supported by the Verilog 
    ### Checks the status of a register bridge register and hands back the value 
    res = f.xem.ReadRegister(reg) # opal kelly function to write to a register
    f.xem.ActivateTriggerIn(0x40, 11) # tell the wb to start the data transmission process

    return res
    ''' 
    
def writeReg(msg, reg_name):
    ''' Writes to a specific register on the ads8686 by using wishbone commands and stored Hex
    values above to either configure a register to its default value or change a register appropriately
    (For example: setting the board to read voltages off the A channel instead of the B channel)

    This should be only about the ADS8686 and nothing about wishbone

    Build a 16-bit command to send on SPI

    '''
    ads_write = 0x8000 # set bit 15 
    if(msg == 0): # if we want to read a register
        cmd = ((dictofRegs[reg_name].addr) << 9) # The address is from bits 14-9 (so shift left 9)
        cmd = (cmd) # send the address only 
    elif(msg == 'c'): # if we want to clear the register's contents
        cmd = ((dictofRegs[reg_name].addr) << 9) # The address is from bits 14-9 (so shift left 9)
        cmd = (cmd | ads_write) # concatenate the reg addr w/ the ADS write bit to build a complete SPI command
    else: # otherwise, we're sending a message
        cmd = ((dictofRegs[reg_name].addr) << 9) # The address is from bits 14-9 (so shift left 9)
        cmd = (cmd | ads_write | msg ) # concatenate the addr the ADS write bit and the data to send 
    
    # print('Your command is 0x{:X}'.format(cmd)) # print to the console to double check our math
    check = sendSPI(cmd) # store the sent result

    # print('Read back 0x{:X}'.format(check))

    # check if the read address matches the default value and log the result
    if(check == dictofRegs[reg_name].default): # if the correct address was read back
        logging.info('     {} register: Default 0x{:X}, read {}'.format(reg_name, dictofRegs[reg_name].default, hex(check)))
    else: # if another register address was given
        logging.warning('  {} register: Default 0x{:X}, read {}'.format(reg_name, dictofRegs[reg_name].default, hex(check)))

    return check

def readAll(): # reads all 43 reg's and prints their values
    logging.info('------------------------------------------------------------------------------------------')
    for register in dictofRegs: # lists are indexed starting at 0, so i should too
        writeReg(0, str(register)) # use writeReg to send a blank message to see a reg's value


def configure_ads():
    ''' configure the ADS8686 for CONVST driven ADC reads '''

    # control register 
    base_creg = 0x0000 # default value 
    writeReg('config', base_creg)

    # set channels to be the fixed digital code 
    writeReg('chan_sel', (0xb | 0xb << 4) )

    # set the range of all channels to +/-5V 
    range_val = 0x00AA # +/- 5V
    writeReg('rangeA1', range_val) 
    writeReg('rangeA2', range_val) 
    writeReg('rangeB1', range_val) 
    writeReg('rangeB2', range_val) 

    # status register is read-only
    # keep over range A,B as default 
    writeReg('lpf', 0x0002)

    # setup the sequencer 
    # sequence0: fixed values and then continue 
    #   8 SSREN; 7-4 CHSEL_B; 3-0 CHSEL_A 
    backto_first_stack = 0x100

    writeReg('seq0', (0xb | 0xb << 4))   # fixed pattern 0xaaaa on CHA; 0x5555 on CHB
    writeReg('seq1', (0x8 | 0x8 << 4))   # AVDD
    writeReg('seq2', (0x9 | 0x9 << 4))   # ALDO
    writeReg('seq3', (0x0 | 0x0 << 4) | backto_first_stack)) #CH0 and cycle back to seq0

    # enable the sequencer 
    writeReg('config', base_creg | 0x40)

''' Eventually will move to the ads8686.py file since it is specific to this chip, but for now it'll stay here'''
################ Reads a V off the ads8686 #################
def seqControl(): 
    ''' Configures the chan_sel reg, range regs, sequencer stack regs we want to use (up to 32 of them)
    so we can go through and read voltage conversion readings from the ADC from the channels we want '''
    seqCmds = [] # list of the commands we want to send
    seqRegs = [] # list of regnames we need to access

    # step 1: configure the channel select reg for the first reg we read
    seqchan_sel = 0x0 # sets board to look at channel AIN_0A/0B first. cmd 0x8611
    seqCmds.append(seqchan_sel) # add cmd to the cmd list
    seqRegs.append('chan_sel') # add reg name to list of seq regs

    # step 2: configure the rangeA1, rangeA2, rangeB1, and rangeB2 regs
    seqA1 = 0xAA # set range to 5V
    seqCmds.append(seqA1)
    seqRegs.append('rangeA1')

    seqA2 = 0xAA # set range to 5V
    seqCmds.append(seqA2)
    seqRegs.append('rangeA2')

    seqB1 = 0xAA # set range to 5V
    seqCmds.append(seqB1)
    seqRegs.append('rangeB1')

    # seqB2 = 0xFF # set range to 10V
    seqB2 = 0xAA # set range to 5V
    seqCmds.append(seqB2)
    seqRegs.append('rangeB2')

    # step 3: setup the sequencer stack regs for each channel we want to read (up to 32 reads)
    s0 = 0x100 # reads channel 0A/0B, STOP, cmd 0xC100
    seqCmds.append(s0)
    seqRegs.append('seq0')
    '''
    s1 = 0x111 # reads channel 1A/1B, STOP, cmd 0xC211
    seqCmds.append(s1)
    seqRegs.append('seq1')
    
    s2 = 0x00 # reads channel 0A/0B, go next, cmd 0xC600
    seqCmds.append(s2)
    seqRegs.append('seq2')

    s3 = 0x11 # reads channel 1A/1B, STOP, cmd 0xC611
    seqCmds.append(s3)
    seqRegs.append('seq3')

    s4 = 0x00 # reads channel 0A/0B, go next reg, cmd 0xC900
    seqCmds.append(s4)
    seqRegs.append('seq4')

    s5 = 0x111 # reads channel 1A/1B, STOP, cmd 0xCB11
    seqCmds.append(s5)
    seqRegs.append('seq5')
    
    s6 = 0x122 # reads channel 6A/6B, go next reg, cmd 0xCD44
    seqCmds.append(s6)
    seqRegs.append('seq6')

    s7 = 0x33 # reads channel 7A/7B, STOP, cmd 0xCF44
    seqCmds.append(s7)
    seqRegs.append('seq7')

    s8 = 0x133 # reads channel 3A/3B, go next reg, cmd 0xD133
    seqCmds.append(s8)
    seqRegs.append('seq8')

    s9 = 0x133 # reads channel 3A/3B, go next reg, cmd 0xD333
    seqCmds.append(s9)
    seqRegs.append('seq9')

    s10 = 0x122 # reads channel 2A/2B, go next reg, cmd 0xD522
    seqCmds.append(s10)
    seqRegs.append('seq10')

    s11 = 0x122 # reads channel 2A/2B, go next reg, cmd 0xD722
    seqCmds.append(s11)
    seqRegs.append('seq11')

    s12 = 0x111 # reads channel 1A/1B, go next reg, cmd 0xD911
    seqCmds.append(s12)
    seqRegs.append('seq12')

    s13 = 0x111 # reads channel 1A/1B, go next reg, cmd 0xDB11
    seqCmds.append(s13)
    seqRegs.append('seq13')

    s14 = 0x100 # reads channel 0A/0B, go next reg, cmd 0xDD00
    seqCmds.append(s14)
    seqRegs.append('seq14')

    s15 = 0x0 # reads channel 0A/0B, this is the LAST REG so stop the sequencer, cmd 0xDE00
    seqCmds.append(s15)
    seqRegs.append('seq15')
    '''
    # step 4: setup the configuration register
    seqconfig = 0x20 # enables sequencer, cmd 0x8420
    seqCmds.append(seqconfig)
    seqRegs.append('config')

    # step 5: write to setup all the registers we need
    for x in range(len(seqCmds)): # while we haven't setup each reg 
        writeReg(seqCmds[x], seqRegs[x]) # formulate command and send msg
  
def readSequence(seqCmds, seqRegs, reads):
    ## LK: I don't understand this function and for now should not be used

    ''' sends CONVST pulses to start reading, then sends a pulse for each register we want 
    conversion results for (off the ADC) readCode to take the readings and convert them into a v  '''
    voltVals = np.array([], dtype = np.single) # stores each V that was read (after converting from 2's comp to float)
    
    # step 6: now provide a dummy CONVST pulse
    f.set_wire(0x01, 0x8, mask = 0xFFFF) # wire high
    f.set_wire(0x01, 0x0, mask = 0xFFFF) # wire low

    # step 7: provide a CONVST pulse for each seq_stack reg we want to read a v from and decipher the code!
    for i in range(reads): # if we want to read the sequencer multiple times, repeat the process x number of times
        ''' Find a better way to iterate through the list '''
        stop = (len(seqCmds) - 1) # when do we want to stop iterating through the list of registers?
        for x in range(5, stop, 1): # if we haven't read all the regs (but stop before the config reg!!)
            # remember, starts at seq0 (index 5), stops at total length - 1, step size 1 (might change later)
            f.set_wire(0x01, 0x8, mask = 0xFFFF) # wire high
            f.set_wire(0x01, 0x0, mask = 0xFFFF) # wire low

            print('\nReading {}'.format(seqRegs[x]))

            code = sendSPI(0x4000_0000) # NOP code to "listen"
            # print('code is: {}'.format(int(code))) # int code

            global LSB
            # find the setting of the voltage by reading the correct range register
            rng = writeReg(0x0, 'rangeA1') # range is set in register rangeA1

            if(rng == 0x55 or rng == 0x7F or rng == 0x2A): # if the analog range is set to 2.5V 
                LSB = 0.000076 # in V! Tells how accurate (large/small) step size is
            elif(rng == 0xAA): # if the analog range is set to 5V
                LSB = 0.000152
            elif(rng == 0xFF): # if the analog range is set to 10V
                LSB = 0.000305
            else: # for a value that isn't on the datasheet, calculate the LSB value
                LSB = ((2*rng)/65536) # or (2*rng)/2^16

            # print('{} LSB'.format(LSB))
            voltVals = readCode(code, voltVals) # convert code into a v

    # done reading, reset the sequencer to stack 0
    f.set_wire(0x01, 0x8, mask = 0xFFFF) # wire high
    f.set_wire(0x01, 0x0, mask = 0xFFFF) # wire low

    return voltVals

def readCode(v, voltVals): 
    ''' Uses the calculated voltage and gives us a decimal and 2's comp representation
    of what the expected code would be to check if we're reading good data '''
    # now calculate and print the voltage
    exp = (float(v)*LSB)
    voltVals = np.append(voltVals, exp) # append the now converted float into the list of read values
    print('V is: {}'.format(exp))
    exp = (exp/LSB) # undo the calculation so we can find the expected code

    # now calculate the code in two's complement
    exp = twos_comp(exp, 16) # code always has 16 bits, so hard code

    return voltVals # so the user can see/modify the data

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


print('Configuring the SPI controller')
SPI_config() # this sets SPI to be host driven 

print('Configuring the ADS with host driven SPI')
configure_ads()

print('writing the register bridge')
writeRegBridge() # this switches to host driven SPI 

# Not certain if the pipeOut is at 0xA0 (or 0xA5)?
s,e = f.read_pipe_out(addr_offset = 0, data_len = 1024) 
