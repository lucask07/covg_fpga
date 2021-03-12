import sys
from fpga import FPGA
import time
import numpy as np
import matplotlib.pyplot as plt 
import pickle as pkl
from drivers.utils import rev_lookup, bin, test_bit, twos_comp


## TODO: move this to a generic I2C folder 
signed = false
def read(reg_name, signed):
    # code to read multiple bytes 
    multi_first = regs[reg_name].first
    if regs[reg_name].length == 1:
        t = dev.i2c_read8(devAddr, regs[reg_name].addr, 1)
        return t[0] & regs[reg_name].mask
    else:
        t = dev.i2c_read8(devAddr, regs[reg_name].addr, regs[reg_name].length)
        val = 0
        if multi_first == 'msb':
            t.reverse()
        for i,v in enumerate(t):
            val += v<<(8*i)
        
        if signed:
            return twos_comp(val, 8*regs[reg_name].length)
        else:
            return val

def write(reg_name, val):
    mask = regs[reg_name].mask
    if regs[reg_name].length == 1:
        t = dev.i2c_write8(devAddr, regs[reg_name].addr, 1, [val & mask])
        return t
    else:
        print('write greater than 1 byte not yet implemented')

# MAX5802 : 00011 + 2 bits configured by Address pin

ADDR = 'NC' # daq_v1 PCB -- this pin is connected to Gnd but thru a 100k pull-down 
if ADDR == 'Gnd':
    i2c_addr = '0001111'
elif ADDR == 'NC':
    i2c_addr = '0001110'
elif ADDR == 'Vdd':
    i2c_addr = '0001100'

devAddr = int(i2c_addr, 2) << 1

# basic is a 4 byte write
#  1) slave  address 
#  2) command
#  3) data (high byte)
#  4) data (low byte)

# DAC selection: 
#  A: 0000 
#  B: 0001  
#  ALL DACs: 0100 


if __name__ == "__main__":

    f = FPGA()
    f.init_device()
    f.one_shot(1)

    read_back = f.i2c_read_long(devAddr, [0xF2], 2)
    print('\n'.join('{}: 0x{:X}'.format(*k) for k in enumerate(read_back)))

    # set DAC0 to mid-scale (around 2.5V)
    val_12bit = 2048
    data = [(val_12bit & 0xff0)>>4, (val_12bit & 0x00f)]
    f.i2c_write_long(devAddr, [0x20], len(data), data)

    # set DAC1 to 1.623
    voltage = 1.623
    vref = 5
    N = 12
    val_12bit = int(np.round(voltage/vref*(2**N)))
    data = [(val_12bit & 0xff0)>>4, (val_12bit & 0x00f)]
    f.i2c_write_long(devAddr, [0x21], len(data), data)



'''
class Register():
    def __init__(self, addr, rw, def_val, length, mask, first = None):
        self.addr = addr
        self.rw = rw 
        self.def_val = def_val 
        self.length = length 
        self.mask = mask 
        self.first = first # 'lsb' or 'msb'

# addr, r or rw, default value, length (in bytes), mask 
reg_map = {'WHO_AM_I':  [0xFF, 'r', 0x69, 1, 0xD0C0],  # but check REF MODE [1:0]
        'CODE0_LOAD_ALL' :  [0x10, 'rw', 0x00, 1, 0xFF],
        'CTRL2_G' :   [0x11, 'rw', 0x00, 1, 0xFF],
        'CTRL3_C' :   [0x12, 'rw', 0x04, 1, 0xFF],
        'CTRL4_C' :   [0x13, 'rw', 0x00, 1, 0xFF],
        'CTRL5_C' :   [0x14, 'rw', 0x00, 1, 0xFF],
        'CTRL6_C' :   [0x15, 'rw', 0x00, 1, 0xF0],
        'CTRL7_C' :   [0x16, 'rw', 0x00, 1, 0xFF],
        'CTRL8_XL' :  [0x17, 'rw', 0x00, 1, 0xFF],
        'CTRL9_XL' :  [0x18, 'rw', 0x38, 1, 0xFF],
        'CTRL10_C' :  [0x19, 'rw', 0x38, 1, 0xFF],
        'MASTER_CONFIG' :  [0x1A, 'rw', 0x00, 1, 0xFF],
        'TEMP' :      [0x20, 'r', 0x00, 2, 0xFF, 'lsb'],
        'OUTX_G' :    [0x22, 'r', 0x00, 2, 0xFF, 'lsb'],
        'OUTY_G' :    [0x24, 'r', 0x00, 2, 0xFF, 'lsb'],
        'OUTZ_G' :    [0x26, 'r', 0x00, 2, 0xFF, 'lsb'],
        'OUTX_XL' :   [0x28, 'r', 0x00, 2, 0xFF, 'lsb'],
        'OUTY_XL' :   [0x2A, 'r', 0x00, 2, 0xFF, 'lsb'],
        'OUTZ_XL' :   [0x2C, 'r', 0x00, 2, 0xFF, 'lsb'],
        'TIMESTAMP0': [0x40, 'r', 0x00, 3, 0xFF, 'lsb'],
        'TIMESTAMP3': [0x42, 'w', 0x00, 1, 0xFF],
        'FIFO_CTRL1': [0x06, 'rw', 0x00, 1, 0xFF], # waterlevel settings
        'FIFO_CTRL2': [0x07, 'rw', 0x00, 1, 0xFF], # waterlevel and pedometer
        'FIFO_CTRL3': [0x08, 'rw', 0x00, 1, 0xFF], # gyro[5:3], accel[2:0] decimation 
        'FIFO_CTRL4': [0x09, 'rw', 0x00, 1, 0xFF], # only high, ch4_dec[5:3], ch3_dec[2:0]
        'FIFO_CTRL5': [0x0A, 'rw', 0x00, 1, 0xFF], # odr[6:3], mode[2:0] 
        'FIFO_STATUS1': [0x3A, 'r', 0x00, 1, 0xFF], # 
        'FIFO_STATUS2': [0x3B, 'r', 0x00, 1, 0xFF], # 
        'FIFO_STATUS3': [0x3C, 'r', 0x00, 1, 0xFF], # 
        'FIFO_STATUS4': [0x3D, 'r', 0x00, 1, 0xFF], # 
        'FIFO_DATA_OUT_L':  [0x3E, 'r', 0x00, 2, 0xFF, 'lsb'], # 
        'FIFO_DATA_OUT_H':  [0x3F, 'r', 0x00, 1, 0xFF] # 
        }
        
regs = {}
for name in reg_map:
    first = None
    if len(reg_map[name]) == 6:
        first = reg_map[name][5]
    
    regs[name] = Register(  reg_map[name][0],
                            reg_map[name][1],
                            reg_map[name][2],
                            reg_map[name][3],
                            reg_map[name][4],
                            first)

# Check ID
print('Confirm correct ID registers')
who_am = read('WHO_AM_I')  
assert who_am == regs['WHO_AM_I'].def_val, "ID registers incorrect read of {}".format(who_am)



    write('CTRL1_XL', (odr << 4) + (full_scale << 2) + anti_alias )
    write('CTRL2_G', (odr_gyro << 4) + (full_scale_gyro << 1) + full_scale2 )

    # enable high performance mode of accel  
    write('CTRL6_C', 0x10)

    # enable high performance mode of gyro  
    # do something with the HPF? 
    write('CTRL7_C', 0x80)

    # setup FIFO
    write('FIFO_CTRL1', 0xFF) # basically a don't care
    write('FIFO_CTRL2', 0x3F) # basically a don't care
    write('FIFO_CTRL3', 0x01) # disable gryo, enable accel with no decimation
    write('FIFO_CTRL4', 0x00) # disable 3rd and 4th channels 
    # write('FIFO_CTRL5', 0x56) # odr is 6.66 kHz, continuous
    write('FIFO_CTRL5', 0x50) # odr is 6.66 kHz, bypass - resets the FIFO


    # accelerometer slope filter??
    # master configuration: default seems fine 
    # read temperature 
    t = read('TEMP', signed = True)
    print('Read temperature = {} deg C'.format(temp_conversion(t)))

# LSM6D
#write('FIFO_CTRL5', 0x51) # odr is 6.66 kHz, FIFO mode
#devAddr = 0xD4 # 8-bit address if SDO to Supply
#write('FIFO_CTRL5', 0x51) # odr is 6.66 kHz, FIFO mode
#time.sleep(1.5)

devAddr = 0xD4 # 8-bit address if SDO to Supply
devAddr1 = 0xD6 # 8-bit address if SDO is Gnd  

dev.one_shot(0)
dev.i2c_write_mult(2, [devAddr, devAddr1], regs['FIFO_CTRL5'].addr, 1, [0x51])

# orange leads by 8
# dev.i2c_write_mult(2, [devAddr1, devAddr], regs['FIFO_CTRL5'].addr, 1, [0x51])

time.sleep(1.5) 

fctrl5_0 = read('FIFO_CTRL5')
'''
