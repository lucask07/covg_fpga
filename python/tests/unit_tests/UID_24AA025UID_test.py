"""Unit test for the UID_24AA025UID class.

Relies on the I2CController, FPGA classes working. The UID_24AA025UID is a Unique ID chip with a unique serial number.

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

top_level_module_bitfile = os.path.join(
    interfaces_path, 'top_level_module.bit')
i2c_bitfile = os.path.join(interfaces_path, 'i2c.bit')


# Fixtures
@pytest.fixture(scope='module')
def dut():
    # global top_level_module_bitfile
    global i2c_bitfile
    from interfaces.interfaces import FPGA, UID_24AA025UID
    # f = FPGA(bitfile=top_level_module_bitfile)
    f = FPGA(bitfile=i2c_bitfile)
    assert f.init_device()
    yield UID_24AA025UID(fpga=f, addr_pins=0b000)
    # Teardown
    f.xem.Close()


# Tests
# Get codes first to confirm the device is there and communicating
def test_get_manufacturer_code(dut):
    got = dut.get_manufacturer_code()
    expected = dut.parameters['MANUFACTURER_CODE'].default
    assert got == expected


def test_get_device_code(dut):
    got = dut.get_device_code()
    expected = dut.parameters['DEVICE_CODE'].default
    assert got == expected


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


def test_get_serial_number(dut):
    dut.get_serial_number()

