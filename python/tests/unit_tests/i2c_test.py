"""Unit test for the I2CController class

Relies on FPGA class working
August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
import os
import sys


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

i2c_test_bitfile = os.path.join(interfaces_path, 'i2c_test.bit')

NACK = 1
ACK = 0
START = 1
STOP = 0


# Fixtures
@pytest.fixture(scope='module')
def i2c_controller():
    global i2c_test_bitfile
    from interfaces.interfaces import FPGA, I2CController, Endpoint
    f = FPGA(bitfile=i2c_test_bitfile)
    assert f.init_device()
    Endpoint.update_endpoints_from_defines(
        ep_defines_path='../../../fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ep_defines.v')
    yield I2CController(fpga=f, endpoints=Endpoint.endpoints_from_defines)
    # Teardown
    f.xem.Close()


# Tests
def test_multiple_instances():
    from interfaces.interfaces import FPGA, I2CController, Endpoint
    f = FPGA()
    i2c_types = ['I2CDC', 'I2CDAQ']
    for i2c_type in i2c_types:
        group1 = [
            I2CController(fpga=f, endpoints=Endpoint.get_chip_endpoints(i2c_type)),
            I2CController(fpga=f, endpoints=Endpoint.get_chip_endpoints(i2c_type)),
            I2CController(fpga=f, endpoints=Endpoint.get_chip_endpoints(i2c_type))
        ]
        # Must use endpoints_from_defines directly rather than get_chip_endpoints
        # so we increment the reference dictionary rather than a copy.
        Endpoint.increment_endpoints(Endpoint.endpoints_from_defines.get(i2c_type))
        group2 = [
            I2CController(fpga=f, endpoints=Endpoint.get_chip_endpoints(i2c_type)),
            I2CController(fpga=f, endpoints=Endpoint.get_chip_endpoints(i2c_type)),
            I2CController(fpga=f, endpoints=Endpoint.get_chip_endpoints(i2c_type))
        ]
        assert all([x.endpoints == group1[1].endpoints for x in group1])
        assert all([x.endpoints == group2[1].endpoints for x in group2])
        assert group1[0].endpoints != group2[0].endpoints

    compare_chips = []
    for i2c_type in i2c_types:
        compare_chips.append(I2CController(fpga=f, endpoints=Endpoint.get_chip_endpoints(i2c_type)))
    assert all([x.endpoints != compare_chips[0].endpoints for x in compare_chips])

@pytest.mark.parametrize('dev_addr, reg_addr, data', [
    (0b0000_0000, [0b0000_0000], [0b0000_0000, 0b0000_0000]),
    (0b1111_1111, [0b0000_0000], [0b0101_0101, 0b0101_0101]),
    (0b1111_1111, [0b1111_1111], [0b1111_1111, 0b1111_1111]),
    (0b0101_0100, [0b0101_0101], [0b0101_0101, 0b0101_0101]),
    (0b1010_1010, [0b1010_1010], [0b1010_1010, 0b1010_1010]),
])
def test_i2c_write_long(i2c_controller, dev_addr, reg_addr, data):
    # dev_addr must have a 0 at the end because this is a write
    dev_addr = dev_addr & 0b1111_1110
    # transmission = dev_addr, reg_addr, data[0], data[1] -> 8 * 4 = 32 bits
    i2c_controller.i2c_write_long(dev_addr, reg_addr, 2, data)
    read_out_0 = i2c_controller.fpga.read_wire(0x21) # Bits [31:0] (newest 32 bits)
    read_out_1 = i2c_controller.fpga.read_wire(0x22) # Bits [63:32]
    transmission_data = ((read_out_1 << 32) | read_out_0) % 2**37 # 8 * 4 = 32 bits + 4 NACKS + 1 STOP = 37 bits [36:0]
    print(f'{bin(transmission_data)} == {bin((dev_addr << 29) | NACK << 28 | (reg_addr[0] << 20) | NACK << 19 | (data[0] << 11) | NACK << 10 | data[1] << 2 | NACK << 1 | STOP)}')
    assert transmission_data == (dev_addr << 29) | NACK << 28 | (
        reg_addr[0] << 20) | NACK << 19 | (data[0] << 11) | NACK << 10 | data[1] << 2 | NACK << 1 | STOP

@pytest.mark.parametrize('dev_addr, reg_addr', [
    (0b0000_0000, [0b0000_0000]),
    (0b1111_1111, [0b0000_0000]),
    (0b1111_1111, [0b1111_1111]),
    (0b0101_0101, [0b0101_0101]),
    (0b1010_1010, [0b1010_1010]),
])
def test_i2c_read_long(i2c_controller, dev_addr, reg_addr):
    # dev_addr must have a 1 at the end because this is a read
    dev_addr_write = dev_addr & 0b1111_1110
    dev_addr_read = dev_addr | 0b0000_0001
    # transmission = dev_addr, reg_addr, dev_addr, data[0], data[1] -> 8 * 5 = 40 bits
    i2c_controller.i2c_read_long(dev_addr, reg_addr, 2)
    read_out_0 = i2c_controller.fpga.read_wire(0x21) # Bits [31:0] (newest 32 bits)
    read_out_1 = i2c_controller.fpga.read_wire(0x22) # Bits [63:32]
    transmission_data = ((read_out_1 << 32) | read_out_0) % 2**47 # 8 * 5 = 40 bits + 5 NACKS + 1 START + 1 STOP = 47 bits [46:0]
    print(
        f'{bin(transmission_data)} == {bin((dev_addr_write << 39) | NACK << 38 | reg_addr[0] << 30 | NACK << 29 | START << 28 | (dev_addr_read << 20) | NACK << 19 | (0b11111111 << 11) | ACK << 10 | 0b11111111 << 2 | NACK << 1 | STOP)}')
    assert transmission_data == (dev_addr_write << 39) | NACK << 38 | reg_addr[0] << 30 | NACK << 29 | START << 28 | (
        dev_addr_read << 20) | NACK << 19 | (0b11111111 << 11) | ACK << 10 | 0b11111111 << 2 | NACK << 1 | STOP
