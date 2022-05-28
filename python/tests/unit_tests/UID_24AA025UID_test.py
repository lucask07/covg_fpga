"""Unit test for the UID_24AA025UID class.

Relies on the I2CController, FPGA classes working. The UID_24AA025UID is a Unique ID chip with a unique serial number.

May 2022

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
import os
import sys

# 24AA025UID chip is on the Clamp board
# pytestmark = pytest.mark.Clamp


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



# Fixtures
@pytest.fixture(scope='module')
def dut():
    global top_level_module_bitfile
    from interfaces.interfaces import FPGA, UID_24AA025UID, Endpoint, advance_endpoints_bynum
    f = FPGA(bitfile=top_level_module_bitfile)
    assert f.init_device()
    yield UID_24AA025UID(fpga=f,
                         endpoints=advance_endpoints_bynum(
                             Endpoint.get_chip_endpoints('I2CDAQ'), 1),
                         addr_pins=0b000)
    # Teardown
    f.xem.Close()


# Tests
# Get codes first to confirm the device is there and communicating
def test_get_manufacturer_code(dut):
    got = dut.get_manufacturer_code()
    expected = dut.registers['MANUFACTURER_CODE'].default
    assert got == expected


def test_get_device_code(dut):
    got = dut.get_device_code()
    expected = dut.registers['DEVICE_CODE'].default
    assert got == expected


@pytest.mark.parametrize('data', [(0b1 << (x + 1)) - 1 for x in range(0, 1024, 4)])
def test_write_read(dut, data):
    from interfaces.utils import count_bytes, int_to_list
    dut.write(data)
    got = dut.read(word_address=0, words_read=count_bytes(data))
    assert got == int_to_list(data)


@pytest.mark.skip(reason='Cannot know the serial number to compare against.')
def test_get_serial_number(dut):
    dut.get_serial_number()


