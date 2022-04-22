import os
import sys
import time


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

while(True):
    print('tri1 Pull-Up:', bin(f.read_wire(i2c_controller.endpoints['PULL_UP_EX'].address)))
    print()

    print('CLK_CNT:', f.read_wire(i2c_controller.endpoints['CLK_CNT'].address))
    print('=== WRITE ===')
    i2c_controller.i2c_write_long(devAddr=0xAA, regAddr=[0xAA], data_length=2, data=[0x55, 0x55])
    
    print('CLK_CNT:', f.read_wire(i2c_controller.endpoints['CLK_CNT'].address))
    print('=== READ ===')
    i2c_controller.i2c_read_long(devAddr=0xAA, regAddr=[0xAA], data_length=2)

    time.sleep(1)
    print('\n\n')
