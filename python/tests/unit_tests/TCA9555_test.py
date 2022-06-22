"""Unit test for the TCA9555 class.

Relies on the I2CController, FPGA classes working. The TCA9555 is an I2C interface I/O Expander.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
from interfaces.utils import int_to_list
from interfaces.interfaces import FPGA, Endpoint
from interfaces.peripherals.TCA9555 import TCA9555

# TCA9555 chip is on the Clamp board
pytestmark = pytest.mark.Clamp


# Fixtures
@pytest.fixture(scope='module')
def dut() -> TCA9555:
    f = FPGA()
    assert f.init_device()
    yield TCA9555(fpga=f, addr_pins=0b000, endpoints=Endpoint.get_chip_endpoints('I2CDAQ'))
    # Teardown
    f.xem.Close()


# Tests
@pytest.mark.parametrize('register_name', [
    # Not checking input register because it defaults to a high-impedance state so we cannot check it against something
    'OUTPUT',
    'POLARITY',
    'CONFIG'
])
def test_power_up_defaults(dut: TCA9555, register_name):
    # Only want to know if the chip is connected in this first test.
    # Note: this test will likely fail if run after using the chip
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
def test_configure_pins(dut: TCA9555, data):
    dut.configure_pins(data)
    got = dut.read('CONFIG')
    assert got == data


@pytest.mark.parametrize('data, register_name',
    [(0b1 << x, 'OUTPUT') for x in range(16)] +
    [(0b1 << x, 'POLARITY') for x in range(16)] +
    [(0b1 << x, 'CONFIG') for x in range(16)]
)
def test_write_read(dut: TCA9555, data, register_name):
    dut.write(data, register_name)
    got = dut.read(register_name)
    expected = int_to_list(integer=data, num_bytes=2)
    assert got == expected


@pytest.mark.parametrize('data', [2**x for x in range(16)])
def test_write_default_read(dut: TCA9555, data):
    dut.write(data)
    got = dut.read('OUTPUT')
    expected = int_to_list(integer=data, num_bytes=2)
    assert got == expected


@pytest.mark.skip(reason='Cannot set input values to read from INPUT register.')
def test_read(dut: TCA9555):
    dut.read()
