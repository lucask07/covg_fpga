"""Unit test for the SPIController class

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

spi_test_bitfile = os.path.join(interfaces_path, 'spi_test.bit')


# Fixtures
@pytest.fixture(scope='module')
def spi_controller():
    global spi_test_bitfile
    from interfaces.interfaces import FPGA, SPIController
    f = FPGA(bitfile=spi_test_bitfile)
    assert f.init_device()
    yield SPIController(f)
    # Teardown
    f.xem.Close()


# Tests
@pytest.mark.parametrize('command', [
    0x8000_0000,
    0x4000_0000,
    0x0000_0000,

    0x8000_4256,
    0x4000_9375,
    0x0000_1685,

    0x8188_8218,
    0x4796_1342,
    0x0164_5973
])
def test_wb_send_cmd(spi_controller, command):
    spi_controller.wb_send_cmd(command)
    expected = (command >> 30) << 32 | 0b00 << 30 | command % 2**30
    got = ((spi_controller.fpga.read_wire(0x22) % 2**2) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'Got:      {hex(got).rjust(15)}\nExpected: {hex(expected).rjust(15)}')
    assert got == expected


@pytest.mark.skip(reason='Unfinished function')
def test_wb_is_acknowledged(spi_controller):
    pass


@pytest.mark.parametrize('address', [x for x in range(0x00, 0x19, 0x4)])
def test_wb_set_address(spi_controller, address):
    spi_controller.wb_set_address(address)
    command = 0x8000_0000 | (address << 2) | 0x01
    expected = (command >> 30) << 32 | 0b00 << 30 | command % 2**30
    got = ((spi_controller.fpga.read_wire(0x22) % 2**2) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'Got:      {hex(got).rjust(15)}\nExpected: {hex(expected).rjust(15)}')
    assert got == expected


@pytest.mark.parametrize('data', [
    0x0000_0000,
    0x0000_0001,
    0x0000_0011,
    0x0000_0111,
    0x0000_1111,
    0x0001_1111,
    0x0011_1111,
    0x0111_1111,
    0x1111_1111
])
def test_wb_write(spi_controller, data):
    spi_controller.wb_write(data)
    command = 0x4000_0000 | data
    expected = (command >> 30) << 32 | 0b00 << 30 | command % 2**30
    got = ((spi_controller.fpga.read_wire(0x22) % 2**2) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'Got:      {hex(got).rjust(15)}\nExpected: {hex(expected).rjust(15)}')
    assert got == expected


@pytest.mark.parametrize('test_data, address', [
    (0x0000_0000, 0x00), # Transfer register with different data writes
    (0x0000_0001, 0x00),
    (0x0000_0011, 0x00),
    (0x0000_0111, 0x00),
    (0x0000_1111, 0x00),
    (0x0001_1111, 0x00),
    (0x0011_1111, 0x00),
    (0x0111_1111, 0x00),
    (0x1111_1111, 0x00),

    (0x0000_3618, 0x10), # CTRL register
    (0x0000_5632, 0x14), # DIVIDER register
    (0x0000_0001, 0x18)  # SS register TODO: figure out why this only works as 1 or 0
])
def test_wb_read(spi_controller, test_data, address):
    # Assumes wb_write is working
    spi_controller.wb_set_address(address)
    spi_controller.wb_write(test_data)
    got = spi_controller.wb_read()
    assert got == test_data


def test_wb_go(spi_controller):
    # TODO: fix the reset on the wire checking for SS to have gone low
    # Reset the wire checking for SS to go low
    # from interfaces import Register
    # print(spi_controller.fpga.read_wire(0x24))
    # spi_controller.fpga.send_trig(Register(address=40, default=0x0, bit_width=1, bit_index_low=4, bit_index_high=4))
    # print(spi_controller.fpga.read_wire(0x24))
    # assert spi_controller.fpga.read_wire(0x24) % 2**1 == 0x0

    # Send go bit
    spi_controller.wb_go()
    print(spi_controller.fpga.read_wire(0x24))

    # Check for wire checking SS to have seen SS go low
    assert spi_controller.fpga.read_wire(0x24) % 2**1 == 0x1


@pytest.mark.parametrize('slave_address', [
    0x0000_0000,
    0x0000_0001,
    0x0000_0010,
    0x0000_0100,
    0x0000_1000,
    0x0001_0000,
    0x0010_0000,
    0x0100_0000,
    0x1000_0000
])
def test_select_slave(spi_controller, slave_address):
    spi_controller.select_slave(slave_address)

    address = 0x18
    set_address_cmd = (0x8000_0000 << 2) | (address << 2) | (0x01)

    data = slave_address
    write_cmd = (0x4000_0000 << 2) | data

    expected = set_address_cmd << 34 | write_cmd
    got = (spi_controller.fpga.read_wire(0x23) % 2**4 << 32 * 2) | (spi_controller.fpga.read_wire(0x22) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'----- Pre-concat -----\nExpected:\n{hex(set_address_cmd).rjust(15)}\n{hex(write_cmd).rjust(15)}')
    print(f'Got:      {hex(got).rjust(15)}\nExpected: {hex(expected).rjust(15)}')
    assert got == expected


@pytest.mark.parametrize('divider', [2**x for x in range(16)])
def test_set_divider(spi_controller, divider):
    spi_controller.set_divider(divider)
    
    address = 0x14
    set_address_cmd = (0x8000_0000 << 2) | (address << 2) | (0x01)

    data = divider
    write_cmd = (0x4000_0000 << 2) | data
    
    expected = set_address_cmd << 34 | write_cmd
    got = (spi_controller.fpga.read_wire(0x23) % 2**4 << 32 * 2) | (spi_controller.fpga.read_wire(0x22) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'----- Pre-concat -----\nExpected:\n{hex(set_address_cmd).rjust(15)}\n{hex(write_cmd).rjust(15)}')
    print(f'Got:      {hex(got).rjust(15)} -> {bin(got).rjust(75)}\nExpected: {hex(expected).rjust(15)} -> {bin(expected).rjust(75)}')
    assert got == expected


@pytest.mark.parametrize('frequency', [
    200,
    150,
    100,
    50,
    25,
    10
])
def test_set_frequency(spi_controller, frequency):
    spi_controller.set_frequency(frequency)
    divider = max(round(200/(frequency * 2)), 1) - 1
    print(hex(divider))
    
    address = 0x14
    set_address_cmd = (0x8000_0000 << 2) | (address << 2) | (0x01)

    data = divider
    write_cmd = (0x4000_0000 << 2) | data
    
    expected = set_address_cmd << 34 | write_cmd
    got = (spi_controller.fpga.read_wire(0x23) % 2**4 << 32 * 2) | (spi_controller.fpga.read_wire(0x22) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'Got:      {hex(got).rjust(15)} -> {bin(got).rjust(75)}\nExpected: {hex(expected).rjust(15)} -> {bin(expected).rjust(75)}')
    assert got == expected


@pytest.mark.parametrize('data', [2**x for x in range(30)])
def test_write(spi_controller, data):
    spi_controller.write(data)

    # Check MOSI line
    read_out = spi_controller.fpga.read_wire(0x25)
    expected = data
    assert read_out == expected


@pytest.mark.skip(reason='Function incomplete')
@pytest.mark.parametrize('register,data', [(x, 0xabcd_ef01) for x in range(0x00, 0x19, 0x4)])
def test_read(spi_controller, register, data):
    spi_controller.write(data, register)
    read_out = spi_controller.read(register)
    assert read_out == data


@pytest.mark.parametrize('configuration', [
    0x3010,
    0x3210,
    0x3410,
    0x3610,
    0x3618
])
def test_configure_master_bin(spi_controller, configuration):
    spi_controller.configure_master_bin(configuration)

    address = 0x10
    set_address_cmd = (0x8000_0000 << 2) | (address << 2) | (0x01)

    data = configuration
    write_cmd = (0x4000_0000 << 2) | data

    expected = set_address_cmd << 34 | write_cmd
    got = (spi_controller.fpga.read_wire(0x23) % 2**4 << 32 * 2) | (
        spi_controller.fpga.read_wire(0x22) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'Got:      {hex(got).rjust(15)} -> {bin(got).rjust(75)}\nExpected: {hex(expected).rjust(15)} -> {bin(expected).rjust(75)}')
    assert got == expected


@pytest.mark.parametrize('ASS, IE, LSB, Tx_NEG, Rx_NEG, CHAR_LEN, corresponding_code', [
    (1, 1, 0, 0, 0, 16, 0x3010), # ASS=1, IE=1, CHAR_LEN=16
    (1, 1, 0, 0, 1, 16, 0x3210), # ASS=1, IE=1, Rx_NEG=1, CHAR_LEN=16
    (1, 1, 0, 1, 0, 16, 0x3410), # ASS=1, IE=1, Tx_NEG=1, CHAR_LEN=16
    (1, 1, 0, 1, 1, 16, 0x3610), # ASS=1, IE=1, Tx_NEG=1, Rx_NEG=1, CHAR_LEN=16
    (1, 1, 0, 1, 1, 24, 0x3618)  # ASS=1, IE=1, Tx_NEG=1, Rx_NEG=1, CHAR_LEN=24
])
def test_configure_master(spi_controller, ASS, IE, LSB, Tx_NEG, Rx_NEG, CHAR_LEN, corresponding_code):
    spi_controller.configure_master(ASS, IE, LSB, Tx_NEG, Rx_NEG, CHAR_LEN)
    
    address = 0x10
    set_address_cmd = (0x8000_0000 << 2) | (address << 2) | (0x01)

    data = corresponding_code
    write_cmd = (0x4000_0000 << 2) | data

    expected = set_address_cmd << 34 | write_cmd
    got = (spi_controller.fpga.read_wire(0x23) % 2**4 << 32 * 2) | (
        spi_controller.fpga.read_wire(0x22) << 32) | spi_controller.fpga.read_wire(0x21)
    print(f'Got:      {hex(got).rjust(15)} -> {bin(got).rjust(75)}\nExpected: {hex(expected).rjust(15)} -> {bin(expected).rjust(75)}')
    assert got == expected


@pytest.mark.skip(reason='Relies on wb_read which is incomplete')
def test_get_master_configuration(spi_controller):
    spi_controller.get_master_configuration()
    expected = 1
    got = (spi_controller.fpga.read_wire(0x23) % 2**4 << 32 * 2) | (spi_controller.fpga.read_wire(0x22) << 32) | spi_controller.fpga.read_wire(0x21)
    assert got == expected


def test_reset_master(spi_controller):
    spi_controller.reset_master()
    assert spi_controller.fpga.read_wire(0x26) == 1
