"""Unit test for the TCA9555 class.

Relies on the I2CController, FPGA classes working. The TCA9555 is an I2C interface I/O Expander.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
import os
import sys

# TCA9555 chip is on the Clamp board
pytestmark = pytest.mark.Clamp


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

top_level_module_bitfile = os.path.join(interfaces_path, 'top_level_module.bit')
i2c_bitfile = os.path.join(interfaces_path, 'i2c.bit')

from interfaces.utils import int_to_list


# Fixtures
@pytest.fixture(scope='module')
def dut():
    # global top_level_module_bitfile
    global i2c_bitfile
    from interfaces.interfaces import FPGA, TCA9555, Endpoint
    # f = FPGA(bitfile=top_level_module_bitfile)
    f = FPGA(bitfile=i2c_bitfile)
    assert f.init_device()
    yield TCA9555(fpga=f, endpoints=Endpoint.get_chip_endpoints('I2C-DC'), addr_pins=0b000)
    # Teardown
    f.xem.Close()


# Tests
@pytest.mark.parametrize('register_name', [
    # Not checking input register because it defaults to a high-impedance state so we cannot check it against something
    'OUTPUT',
    'POLARITY',
    'CONFIG'
])
def test_power_up_defaults(dut, register_name):
    # Only want to know if the chip is connected in this first test.
    # Note: this test will likely fail if run after using the chip
    from interfaces.interfaces import TCA9555
    dev_addr = TCA9555.ADDRESS_HEADER | (dut.addr_pins << 1) | 0b1
    got = dut.i2c_read_long(dev_addr, [TCA9555.registers[register_name].address], 2)
    expected = int_to_list(TCA9555.registers[register_name].default)
    if len(expected) == 1:
        # Data was only 1 byte, read will return a list of 2 bytes
        expected.append(0)
    assert got == expected


@pytest.mark.parametrize('data', [
    [0b0000_1111, 0b0000_1111],
    [0b1111_0000, 0b1111_0000],
    [0b1111_1111, 0b0000_0000],
    [0b1111_1111, 0b1111_1111],
    [0b0000_0000, 0b0000_0000], # Last, set all as outputs
])
def test_configure_pins(dut, data):
    dut.configure_pins(data)
    got = dut.read('CONFIG')
    assert got == data


@pytest.mark.parametrize('data, register_name',
    [(0b1 << x, 'OUTPUT') for x in range(16)] +
    [(0b1 << x, 'POLARITY') for x in range(16)] +
    [(0b1 << x, 'CONFIG') for x in range(16)]
)
def test_write_read(dut, data, register_name):
    dut.write(data, register_name)
    got = dut.read(register_name)
    expected = int_to_list(integer=data, num_bytes=2)
    assert got == expected


@pytest.mark.parametrize('data', [2**x for x in range(16)])
def test_write_default_read(dut, data):
    dut.write(data)
    got = dut.read('OUTPUT')
    expected = int_to_list(integer=data, num_bytes=2)
    assert got == expected


@pytest.mark.skip(reason='Cannot set input values to read from INPUT register.')
def test_read(dut):
    dut.read()
