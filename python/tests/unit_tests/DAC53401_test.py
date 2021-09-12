"""Unit test for the DAC53401 class.

Relies on the I2CController, FPGA classes working. The DAC53401 is an I2C interface 10-bit digital to analog converter.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
import os
import sys

# DAC53401 chip is on the Clamp board
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

top_level_module_bitfile = os.path.join(
    interfaces_path, 'top_level_module.bit')
i2c_bitfile = os.path.join(interfaces_path, 'i2c.bit')


# Fixtures
@pytest.fixture(scope='module')
def dut():
    # global top_level_module_bitfile
    global i2c_bitfile
    from interfaces.interfaces import FPGA, DAC53401, Endpoint
    # f = FPGA(bitfile=top_level_module_bitfile)
    f = FPGA(bitfile=i2c_bitfile)
    assert f.init_device()
    yield DAC53401(fpga=f, endpoints=Endpoint.get_chip_endpoints('I2C-DC'), addr_pins=0b000)
    # Teardown
    f.xem.Close()


# Tests
def test_get_id(dut):
    # fake_read = dut.i2c_read_long(0b11110000, [0xc], 2)
    # print(fake_read)

    # This test goes first to make sure the chip is communicating
    got = dut.get_id()
    # Device and Version ID share the same default value across their combined bits
    expected = dut.parameters['DEVICE_ID'].default
    assert got == expected


@pytest.mark.parametrize('data', [
    0b00,
    0b01,
    0b10,
    0b11
])
def test_write_read(dut, data):
    # These are both read/write registers, we just want to see if what we put
    # in is what we get out.
    dut.write(data, 'FUNC_CONFIG')
    got = dut.read('FUNC_CONFIG')
    assert got == data

    dut.write(data, 'DAC_SPAN')
    got = dut.read('DAC_SPAN')
    assert got == data


@pytest.mark.skip(reason='Test not finished')
@pytest.mark.parametrize('voltage', [2**x for x in range(10)])
def test_write_voltage(dut, voltage):
    dut.write_voltage(voltage)


@pytest.mark.skip(reason='Test not finished')
def test_enable_internal_reference(dut):
    dut.enable_internal_reference()


@pytest.mark.skip(reason='Test not finished')
@pytest.mark.parametrize('gain', [
    1.5,
    2,
    3,
    4
])
def test_set_gain(dut, gain):
    dut.set_gain(gain)


@pytest.mark.parametrize('gain, expected', [
    1.5,
    2,
    3,
    4
])
def test_get_gain(dut, gain):
    dut.set_gain(gain)
    got = dut.get_gain()
    assert got == gain


@pytest.mark.skip(reason='Test not finished')
@pytest.mark.parametrize('function_name', [
    'triangle',
    'sawtooth_falling',
    'sawtooth_rising',
    'square'
])
def test_config_func(dut, function_name):
    dut.config_func(function_name)


@pytest.mark.skip(reason='Test not finished')
def test_start_func(dut):
    dut.start_func()


@pytest.mark.skip(reason='Test not finished')
def test_stop_func(dut):
    dut.stop_func()


@pytest.mark.skip(reason='Test not finished')
@pytest.mark.parametrize('margin_high, margin_low', [
    (0b11_1111_1111, 0b00_0000_0000),
    (0b00_0001_1111, 0b00_0000_0000),
    (0b11_1110_0000, 0b00_0000_0000),
    (0b11_1111_1111, 0b11_1110_0000),
    (0b11_1111_1111, 0b00_0001_1111),
])
def test_config_margins(dut, margin_high, margin_low):
    dut.config_margins(margin_high, margin_low)


@pytest.mark.skip(reason='Test not finished')
@pytest.mark.parametrize('step', [x for x in range(0b1000)])
def test_config_step(dut, step):
    dut.config_step(step)


@pytest.mark.skip(reason='Test not finished')
@pytest.mark.parametrize('rate', [x for x in range(0b1_0000)])
def test_config_rate(dut, rate):
    dut.config_rate(rate)


def test_reset(dut):
    from interfaces.interfaces import DAC53401
    dut.reset()
    for register in DAC53401.registers:
        assert dut.read(register) == register.default


def test_lock_unlock(dut):
    original = 0b00
    new = 0b11
    # These are both read/write registers, we just want to see if what we put
    # in is what we get out.
    dut.write(original, 'FUNC_CONFIG')
    dut.write(original, 'DAC_SPAN')
    dut.lock()

    dut.write(new, 'FUNC_CONFIG')
    got = dut.read('FUNC_CONFIG')
    assert got == original

    dut.write(new, 'DAC_SPAN')
    got = dut.read('DAC_SPAN')
    assert got == original

    dut.unlock()

    dut.write(new, 'FUNC_CONFIG')
    got = dut.read('FUNC_CONFIG')
    assert got == new

    dut.write(new, 'DAC_SPAN')
    got = dut.read('DAC_SPAN')
    assert got == new


@pytest.mark.skip(reason='Test not finished')
def test_power_up(dut):
    dut.power_up()


@pytest.mark.skip(reason='Test not finished')
def test_power_down_10k(dut):
    dut.power_down_10k()


@pytest.mark.skip(reason='Test not finished')
def test_power_down_high_impedance(dut):
    dut.power_down_high_impedance()
