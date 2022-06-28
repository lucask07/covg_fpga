"""Unit test for the UID_24AA025UID class.

Relies on the I2CController, FPGA classes working. The UID_24AA025UID is a Unique ID chip with a unique serial number.

May 2022

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.UID_24AA025UID import UID_24AA025UID


pytestmark = [pytest.mark.usable]


# Fixtures
@pytest.fixture(scope='module')
def f(power_supply):
    f = FPGA()
    assert f.init_device()
    yield f
    # Teardown
    f.xem.Close()


@pytest.fixture(scope='module')
def dut(f):
    yield UID_24AA025UID(fpga=f,
                         endpoints=Endpoint.advance_endpoints(
                             Endpoint.get_chip_endpoints('I2CDAQ'), 1),
                         addr_pins=0b000)


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
    from pyripherals.utils import count_bytes, int_to_list
    dut.write(data)
    got = dut.read(word_address=0, words_read=count_bytes(data))
    assert got == int_to_list(data)


@pytest.mark.skip(reason='Cannot know the serial number to compare against.')
def test_get_serial_number(dut):
    dut.get_serial_number()


