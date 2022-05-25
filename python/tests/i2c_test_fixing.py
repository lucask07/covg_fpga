import os
import sys
import time
import pandas as pd


# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
cwd = os.getcwd()
if 'covg_fpga' in cwd:
    covg_fpga_index = cwd.index('covg_fpga')
    covg_path = cwd[:covg_fpga_index + len('covg_fpga') + 1]
else:
    print('covg_fpga folder not found. Please navigate to the covg_fpga folder.')
    assert False
interfaces_path = os.path.join(covg_path, 'python')
sys.path.append(interfaces_path)

top_level_module_bitfile = os.path.join(covg_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit')

from interfaces.interfaces import FPGA, I2CController, Endpoint

f = FPGA(bitfile=top_level_module_bitfile)
f.init_device()
Endpoint.update_endpoints_from_defines(
    ep_defines_path='C:/Users/ajstr/OneDrive - University of St. Thomas/Research Internship/Programs/covg_fpga/fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ep_defines.v')
i2c_controller = I2CController(fpga=f, addr_pins=0, endpoints=Endpoint.get_chip_endpoints('I2CTEST'))

print('MESSAGE_0: ', hex(f.read_wire(i2c_controller.endpoints['MESSAGE_0'].address)))
print('MESSAGE_1: ', hex(f.read_wire(i2c_controller.endpoints['MESSAGE_1'].address)))
print('CLK_CNT:   ', hex(f.read_wire(i2c_controller.endpoints['CLK_CNT'].address)))
i2c_lines = f.read_wire(i2c_controller.endpoints['PULL_UP_EX'].address) & 0b11
scl = (i2c_lines & 0b10) >> 1
sda = i2c_lines & 0b1
# print(f'SCL={scl}\nSDA={sda}')
input()

d = {'devAddr': [], 'regAddr': [], 'data': [], 'memdin': [], 'message': []}

while(1):
    print('=============================================================================')
    
    i2c_lines = f.read_wire(i2c_controller.endpoints['PULL_UP_EX'].address) & 0b11
    scl = (i2c_lines & 0b10) >> 1
    sda = i2c_lines & 0b1
    print(f'MEMDIN={(i2c_lines & (0xFF << 2) >> 2)}')
    print(f'SCL={scl}\nSDA={sda}')
    read_out_0 = i2c_controller.fpga.read_wire(i2c_controller.endpoints['MESSAGE_0'].address) # Bits [31:0] (newest 32 bits)
    read_out_1 = i2c_controller.fpga.read_wire(i2c_controller.endpoints['MESSAGE_1'].address) # Bits [63:32]
    transmission_data = ((read_out_1 << 32) | read_out_0) % 2**37 # 8 * 4 = 32 bits + 4 NACKS + 1 STOP = 37 bits [36:0]
    print('Message:', bin(transmission_data))

    print('CLK_CNT:', f.read_wire(i2c_controller.endpoints['CLK_CNT'].address))
    print('=== WRITE ===')
    i2c_controller.i2c_write_long(devAddr=0xAA, regAddr=[0xAA], data_length=2, data=[0x55, 0x55])

    i2c_lines = f.read_wire(i2c_controller.endpoints['PULL_UP_EX'].address) & 0b11
    scl = (i2c_lines & 0b10) >> 1
    sda = i2c_lines & 0b1
    print(f'MEMDIN={(i2c_lines & (0xFF << 2) >> 2)}')
    print(f'SCL={scl}\nSDA={sda}')
    read_out_0 = i2c_controller.fpga.read_wire(i2c_controller.endpoints['MESSAGE_0'].address) # Bits [31:0] (newest 32 bits)
    read_out_1 = i2c_controller.fpga.read_wire(i2c_controller.endpoints['MESSAGE_1'].address) # Bits [63:32]
    transmission_data = ((read_out_1 << 32) | read_out_0) % 2**37 # 8 * 4 = 32 bits + 4 NACKS + 1 STOP = 37 bits [36:0]
    print('Message:', bin(transmission_data))

    print('CLK_CNT:', f.read_wire(i2c_controller.endpoints['CLK_CNT'].address))
    print('=== WRITE ===')
    i2c_controller.i2c_write_long(devAddr=0x99, regAddr=[0x99], data_length=2, data=[0x99, 0x99])
    
    print('CLK_CNT:', f.read_wire(i2c_controller.endpoints['CLK_CNT'].address))
    print('=== READ ===')
    i2c_controller.i2c_read_long(devAddr=0xAA, regAddr=[0xAA], data_length=2)

    time.sleep(1)
    print('\n\n')

# for devAddr in range(0xFF + 1):
#     for regAddr in range(0xFF + 1):
#         for data in range(0xFFFF + 1):
#             print(devAddr, regAddr, data)
#             i2c_controller.i2c_write_long(devAddr=devAddr, regAddr=[regAddr], data_length=2, data=[
#                                           (data & 0xFF00) >> 8, (data & 0x00FF)])
#             memdin = (f.read_wire(i2c_controller.endpoints['PULL_UP_EX'].address) & (0xFF << 2)) >> 2
#             read_out_0 = i2c_controller.fpga.read_wire(i2c_controller.endpoints['MESSAGE_0'].address) # Bits [31:0] (newest 32 bits)
#             read_out_1 = i2c_controller.fpga.read_wire(i2c_controller.endpoints['MESSAGE_1'].address) # Bits [63:32]
#             message = ((read_out_1 << 32) | read_out_0) % 2**37 # 8 * 4 = 32 bits + 4 NACKS + 1 STOP = 37 bits [36:0]
#             d['devAddr'].append(devAddr)
#             d['regAddr'].append(data)
#             d['data'].append(data)
#             d['data'].append(data)
#             d['data'].append(data)
