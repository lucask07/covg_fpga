"""Test of I2C for AMS TMF8801

April 2022

Lucas Koerner koer2434@stthomas.edu
"""

import os, sys
from time import sleep

hex_dir = '/Users/koer2434/My Drive/UST/research/tof_comparison/material_classification/TMF8801/'


# bl: boot loader commands, read .hex file and process line by line. 
def bl_intel_hex(hex_dir, filename='main_app_3v3_k2.hex'):
    ''' read intel HEX file line by line 
    Parameters
    ----------
    hex_dir : string
        directory of the hex file
    filename : string
        name of the hex file

    Returns
    -------
    line_list : list 
        list of each line in the file

    '''
    with open(os.path.join(hex_dir, filename), 'r') as f:
        line_list = [l for l in f] 

    return line_list

def bl_checksum(data):
    """ create checksum as described in section 6.3
        of the host driver manual (AN000597)
    
    Parameters
    ----------
    data : list
        bytes that will be sent

    Returns
    -------
    ones_comp : int 
        list of each line in the file    
    """

    low_byte = sum(data) & 0xff  # only use lowest byte of sum
    ones_comp = low_byte ^ 0xff  # ones complement op. via XOR
    return ones_comp

def bl_process_line(l):
    """
    interpret a HEX record line and prepare for i2c write
    
    Parameters
    ----------
    l : string
        a line from the HEX record

    Returns
    -------
    data : list 
        list of bytes to write  
    """

    # https://en.wikipedia.org/wiki/Intel_HEX

    cmd_addr = 0x08
    ram_addr_cmd = 0x43
    data_cmd = 0x41

    # data command
    if l[7:9] == '00':
        data = l[9:]
        data = data.strip()[:-2]
        data_bytes = bytearray.fromhex(data)
        data_len = len(data_bytes)
        data = [cmd_addr, data_cmd, data_len] + list(data_bytes)

    # extended address 
    elif l[7:9] == '04':
        addr = l[9:13]
        addr_bytes = bytearray.fromhex('0' + addr + '0')
        data_len = 0
        data = [cmd_addr, ram_addr_cmd] + list(addr_bytes) 

    else: 
        return None
    
    data.append(bl_checksum(data[1:]))

    return data


bl_hex_lines = bl_intel_hex(hex_dir, filename='main_app_3v3_k2.hex')
print(f'RAM patch is {len(bl_hex_lines)} lines long')

# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == 'covg_fpga':
        interfaces_path = os.path.join(covg_fpga_path, 'python')
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(interfaces_path)

from interfaces.interfaces import FPGA, DAC53401, Endpoint
from interfaces.boards import TOF
import logging

logging.basicConfig(filename='DAC53401_test.log',
                    encoding='utf-8', level=logging.INFO)

# Initialize FPGA
top_level_module_bitfile = os.path.join(covg_fpga_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit')
f = FPGA(bitfile=top_level_module_bitfile)
f.init_device()

# Instantiate the TMF8801 controller.
tof = TOF(f)

# check ID 
id = tof.TMF.get_id()
print(f'Chip id 0x{id:04x}')
tof.TMF.cpu_reset()
app = tof.TMF.read_app()
major,minor,patch = tof.TMF.rom_fw_version()
print(f'CPU ready? {tof.TMF.cpu_ready()}')

if FW_PATCH:
    # download firmware to bootloader (i.e. RAM patch in section 7 of AN000597)
    tof.TMF.download_init()
    status = tof.TMF.ram_write_status()
    print(f'RAM write status: {status}')

    for l in bl_hex_lines:
        d = bl_process_line(l)
        if d is not None:
            addr = d[0]
            data = d[1:]

            tof.TMF.i2c_write_long(tof.TMF.ADDRESS, 
                [addr],
                (len(data)),
                data)
            # reads back 3 bytes from 'CMD_DATA7'
            status = tof.TMF.ram_write_status()
            # TODO: check that status is 00,00,FF
            # TODO: consider skipping status check to reduce time for upload
            if not (status == [0,0,0xFF]):
                print(f'Bootloader status unexpected value of {status}')

    tof.TMF.ramremap_reset()

    for i in range(10):
        print(f'CPU ready? {tof.TMF.cpu_ready()}')

    major,minor,patch = tof.TMF.rom_fw_version()

# the write function reads back the register so that it is possible to write just bit-fields 

# configure the app 

# tof.TMF.load_app(app='measure')
# app = tof.TMF.read_app()

# factory calibration 
CAL = False 
MEASURE = True

# perform factory calibration 
if CAL:
    tof.TMF.write(0x0A, 'COMMAND') # Command is register 0x10
    sleep(2)
    cal_done = 0
    count = 0
    while (cal_done != 0x0A) and (count < 20):
        cal_done = tof.TMF.read('REGISTER_CONTENTS')
        sleep(0.1)
        count = count + 1
        print(f'Cal done 0x{cal_done:02x}')

    cal_data = tof.TMF.read_by_addr(0x20, num_bytes=14) 
    for d in cal_data:
        print(d)

if MEASURE:

    CAL_DATA = True
    STATE_DATA = True

    if (CAL_DATA is False) and (STATE_DATA is True):
        state_addr = 0x20
    else:
        state_addr = 0x2E

    # These registers shall be pre-loaded by the host before command=0x02 or 0x0B is executed
    if CAL_DATA:
        # factory calibration data. TODO: capture the specific calibration for this sensor?
        data = [0x01, 0x17, 0x00, 0xff, 0x04, 0x20, 0x40, 0x80, 0x00, 0x01, 0x02, 0x04, 0x00, 0xFC]
        tof.TMF.i2c_write_long(tof.TMF.ADDRESS, 
            [0x20], # cal_data
            (len(data)),
            data)

    if STATE_DATA:
        # state data 
        data = [0xb1, 0xa9, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        tof.TMF.i2c_write_long(tof.TMF.ADDRESS, 
            [state_addr], # state_data
            (len(data)),
            data)

    ### -------- Configure the sensor for measurements ---------------
    # Continuous mode, period of 100 ms 
    # S 41 W 08 03 23 00 00 00 64 D8 04 02 P
    #       cmd_data7, cmd_data6, cmd_data5, cmd_data4, cmd_data3, cmd_data2 (repeat period), iterations, interations, start-command
    data = [0x03,      0x23,      0x00,      0x00,      0x00,      0x64,  0xd8, 0x04, 0x02] 
    # data = [0x00, 0x23, 0x00, 0x00, 0x00, 0x64, 0xd8, 0x04, 0x02] # calibraion and state data is not provided -- changes first byte to 0x00 

    tof.TMF.i2c_write_long(tof.TMF.ADDRESS, 
        [0x08], # CMD_DATA7
        (len(data)),
        data)
    app = tof.TMF.read_app()

    # check configuation 
    print(tof.TMF.read_by_addr(0x1c))
    print(tof.TMF.read_by_addr(0x1d))

    # Read measurement data
    # S 41 W 1D Sr 41 R A A A A A A A A A A N P
    vals, data = tof.TMF.read_data()

    # to write a register without a readback use directly (with the named registers a readback happens first):
    # i2c_write_long(self, devAddr, regAddr, data_length, data)

    """
    The I2C controller command memory is 64 bytes deep so can send a payload of up to 64 - 4 - preamble_length 
    for a write the preamble length is 2 or 3 bytes (depending on length of register address)
    for a read the preamble length is 3 or 4 bytes (depending on length of register address)

    TODO: change the FPGA to increase the memory depth to speed up long reads and writes by reducing the number 
    of host <-> FPGA transactions.
    """

READ_HIST = False
if READ_HIST:

    # Stop any command
    tof.TMF.write(0xFF, 'COMMAND')
    last_cmd = tof.TMF.read('PREVIOUS')
    assert (last_cmd == 0xFF), 'previous command not FF!'

    # clear interrupt
    tof.TMF.write(0x01, 'INT_STATUS')
    tof.TMF.read('INT_STATUS')

    short_range_hist_cfg = [0x10, 0x00, 0x00, 0x00, 0x30]
    tof.TMF.i2c_write_long(tof.TMF.ADDRESS, 
        [0x0C], # CMD_DATA3
        (len(short_range_hist_cfg)),
        short_range_hist_cfg)

    cyclic_meas = [0x00,0x23,0x00,0x00,0x00,0x80,0xD0,0x07,0x02]
    tof.TMF.i2c_write_long(tof.TMF.ADDRESS, 
        [0x08], # CMD_DATA3
        (len(cyclic_meas)),
        cyclic_meas)

    cnt = 0
    bit_1 = 0
    while ((cnt < 10) or bit_1): # any number other than 0 evaluates to true
        st = tof.TMF.read('INT_STATUS')
        bit_1 = st & 0x0003  # check bit 1 
        time.sleep(0.1)

    #Read out COMMAND, PREV_COMMAND ... STATE STATUS REGISTER_CONTENTS -> store TID
    cmd_etc = tof.TMF.read_by_addr(0x10, num_bytes=16) 
    tid = cmd_etc[-1] # last data should be TID (transaction ID)

    # setup histogram readout
    tof.TMF.write(0x80, 'COMMAND') # see command codes in the datasheet 8.9.11

    tid2 = tof.TMF.read('TID')

    # wait for tid2 to be different than tid -- not sure why we need to read this twice 
    #   (but App note says so)
    tid3_etc = tof.TMF.read_by_addr(0x1C, num_bytes=4)     
    tid3 = tid3_etc[-1]

    hist_data = {}
    for tdc in range(5):
        hist_data[tdc] = np.array([])
        for quarter in range(4):
            hist_data_q = tof.TMF.read_by_addr(0x20, num_bytes=128) 
            hist_data = np.append(hist_data, hist_data_q)

        # LSB + MSB 
        hist_data[tdc] = (hist_data[tdc][0::2]) + (hist_data[tdc][1::2]<<8)


# Need: 
# def i2c pipe read: specify number of bytes  
# def i2c_re_run: re run a read transaction using the data already stored in the RAM 
#             must reset the address pointer; maybe at the end of previous or at start here 
# def i2c_multiple_re_run: re-run multiple times 
# def i2c_reset_pipe_fifo: reset the FIFO -- generally not needed if we read the entire buffer 

# somehow have this all free-run with polling to check for when the pipe must be readout. Would need an 
#   on-chip state machine to send the START signal (and maybe a counter for the number of start signals) 

# initiate multiple i2c transaction with the number set by the depth of the FIFO. 
#   then readout the results. 

# ---- possible expansions 
# store a few different commands in the RAM and specify the address to start at for command 2 or command 3
#   even have this sequence of commands be something that could be programmed  