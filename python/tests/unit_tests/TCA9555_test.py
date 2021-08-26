"""Unit test for the TCA9555 class.

Relies on the I2CController, FPGA classes working. The TCA9555 is an I2C interface I/O Expander.

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

top_level_module_bitfile = os.path.join(interfaces_path, 'top_level_module.bit')
i2c_bitfile = os.path.join(interfaces_path, 'i2c.bit')


# Fixtures
@pytest.fixture(scope='module')
def dut():
    # global top_level_module_bitfile
    global i2c_bitfile
    from interfaces.interfaces import FPGA, TCA9555
    # f = FPGA(bitfile=top_level_module_bitfile)
    f = FPGA(bitfile=i2c_bitfile)
    assert f.init_device()
    yield TCA9555(fpga=f, addr_pins=0b000)
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
    dev_addr = dut.parameters['ADDRESS_HEADER'] | (dut.addr_pins << 1) | 0b1
    read_out = dut.i2c_read_long(dev_addr, [dut.parameters[register_name].address], 2)[1] # Only the second byte to come back is what we want
    default = dut.parameters[register_name].default
    assert read_out == default


@pytest.mark.parametrize('data', [
    [0b0000_0000, 0b0000_0000],
    [0b0000_1111, 0b0000_1111],
    [0b1111_0000, 0b1111_0000],
    [0b1111_1111, 0b1111_1111]
])
def test_configure_pins(dut, data):
    dut.configure_pins(data)


@pytest.mark.parametrize('data', [
    0b0000_0000,
    0b0000_0011,
    0b0000_1100,
    0b0011_0000,
    0b1100_0000,
    0b0000_1111,
    0b1111_0000,
    0b1111_1111
])
def test_write(dut, data):
    dut.write(data)


def test_read(dut):
    dut.read()
