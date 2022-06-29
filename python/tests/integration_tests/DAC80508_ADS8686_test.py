"""Integration test for the DAC80508 and ADS8686 chips on the DAQ board.

Relies on DAC80508 and ADS8686 working separately. Requires DAC1_OUT7
connected to GP_ADC_IN7.
https://github.com/lucask07/open_covg_daq_pcb/blob/main/docs/covg_daq_v2.pdf
October 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
import os
import sys
import time
from pyripherals.core import FPGA
from pyripherals.peripherals.DAC80508 import DAC80508
from pyripherals.peripherals.ADS8686 import ADS8686
from pyripherals.utils import to_voltage


# The boards.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
cwd = os.getcwd()
if 'covg_fpga' in cwd:
    covg_fpga_index = cwd.index('covg_fpga')
    covg_fpga_path = cwd[:covg_fpga_index + len('covg_fpga') + 1]
else:
    print('covg_fpga folder not found. Please navigate to the covg_fpga folder.')
    assert False
boards_path = os.path.join(covg_fpga_path, 'python')
sys.path.append(boards_path)


from boards import Daq


pytestmark = [pytest.mark.usable]


tolerance = 0.009765625
dac_out = 7
ads_in = 7


# Fixtures
@pytest.fixture(scope='module')
def fpga(power_supply):
    """Reused FPGA instance for DAC80508 and ADS8686.
    
    Also powers on the DAQ board so the other chips can do setup in their
    instantiations.
    """

    f = FPGA()
    assert f.init_device()
    # Power on
    pwr = Daq.Power(f)
    pwr.all_off()

    for name in ['1V8', '5V', '3V3']:
        pwr.supply_on(name)
        time.sleep(0.05)

    gpio = Daq.GPIO(f)
    gpio.fpga.debug = True
    gpio.spi_debug('ads')
    gpio.ads_misc('convst')

    yield f
    # Teardown
    f.xem.Close()


@pytest.fixture(scope='module')
def dac(fpga):
    dac = DAC80508(fpga=fpga)
    dac.set_spi_sclk_divide(0x8)
    dac.set_ctrl_reg(0x3218)
    dac.set_config_bin(0x00)
    return dac


@pytest.fixture(scope='module')
def ads(fpga):
    global ads_in
    ads = ADS8686(fpga=fpga)
    ads.hw_reset(val=False)
    ads.set_host_mode()
    ads.setup()
    ads.set_range(5)
    ads.set_lpf(376)
    codes = ads.setup_sequencer(chan_list=[(str(ads_in), 'FIXED')])
    print(f'Setup Sequencer Codes: {codes}')
    ads.write_reg_bridge()
    ads.set_fpga_mode()
    return ads


# Tests


def test_delay(dac: DAC80508, ads: ADS8686):
    dac.write_voltage(5, outputs=dac_out)
    print(f'Waiting for ADS8686 to yield nonzero data (max wait 23s)...')
    time_increment = 0.25
    for i in range(int(23 / time_increment) + 1):
        if ads.read_last()['A'][0] == 0:
            time.sleep(time_increment)
    print(f'Waited {i * time_increment} seconds')


@pytest.mark.parametrize('gain_code, expected_gain', [
    ((0 << dac_out) | (0 << 8), 1),   # Output gain: 1, REFDIV gain: 1,   Total gain: 1
    ((0 << dac_out) | (1 << 8), 1/2), # Output gain: 1, REFDIV gain: 1/2, Total gain: 1/2
    ((1 << dac_out) | (0 << 8), 2),   # Output gain: 2, REFDIV gain: 1,   Total gain: 2
    ((1 << dac_out) | (1 << 8), 1), # Output gain: 2, REFDIV gain: 1/2, Total gain: 1
])
def test_dac_gain_bin(dac: DAC80508, ads: ADS8686, gain_code, expected_gain):
    """Test DAC80508.set_gain_bin() method."""

    # Looking for values within 1 LSB of expected
    global tolerance
    global dac_out
    global ads_in
    # Set the output on DAC80508 (1/2 scale)
    voltage_data = 0x7fff
    # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
    # adjusted by the gain of the output and whether the internal reference is
    # divided by 2 or not.
    expected = to_voltage(data=voltage_data, num_bits=16, voltage_range=2.5 * expected_gain)

    dac.write_chip_reg('DAC' + str(dac_out), voltage_data)
    dac.set_gain_bin(gain_code)
    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    # We double the range used in the to_voltage calculation to account for
    # both +/- sides of the range.
    # Ex. set_range(5) == +/-5V which spans a total of 10V
    read = to_voltage(data=read_data, num_bits=ads.num_bits, voltage_range=ads.ranges[ads_in] * 2, use_twos_comp=True)
    # Compare
    assert abs(read - expected) <= tolerance


@pytest.mark.parametrize('gain, divide_reference, expected_gain', [
    (1, False, 1),  # Output gain: 1, REFDIV gain: 1,   Total gain: 1
    (1, True, 1/2), # Output gain: 1, REFDIV gain: 1/2, Total gain: 1/2
    (2, False, 2),  # Output gain: 2, REFDIV gain: 1,   Total gain: 2
    (2, True, 1),   # Output gain: 2, REFDIV gain: 1/2, Total gain: 1
])
def test_dac_gain(dac: DAC80508, ads: ADS8686, gain, divide_reference, expected_gain):
    """Test DAC80508.set_gain() method."""

    # Looking for values within 1 LSB of expected
    global tolerance
    global dac_out
    global ads_in
    # Set the output on DAC80508 (1/2 scale)
    voltage_data = 0x7fff
    # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
    # adjusted by the gain of the output and whether the internal reference is
    # divided by 2 or not.
    expected = to_voltage(data=voltage_data, num_bits=16, voltage_range=2.5 * expected_gain)

    dac.write_chip_reg('DAC' + str(dac_out), voltage_data)
    dac.set_gain(gain=gain, outputs=dac_out, divide_reference=divide_reference)
    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    # We double the range used in the to_voltage calculation to account for
    # both +/- sides of the range.
    # Ex. set_range(5) == +/-5V which spans a total of 10V
    read = to_voltage(data=read_data, num_bits=ads.num_bits, voltage_range=ads.ranges[ads_in] * 2, use_twos_comp=True)
    # Compare
    assert abs(read - expected) <= tolerance


# @pytest.mark.parametrize('voltage', [x for x in range(0, 0xffff + 1)])
# def test_dac_write(dac: DAC80508, ads: ADS8686, voltage):
#     """Test DAC80508.write() method to write output voltage."""

#     # Looking for values within 1 LSB of expected
#     global tolerance
#     global dac_out
#     global ads_in
#     # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
#     # adjusted by the gain of the output and whether the internal reference is
#     # divided by 2 or not.
#     expected = to_voltage(data=voltage, num_bits=16,
#                           voltage_range=2.5)
#     dac.write_chip_reg('DAC4', voltage)
#     dac.set_gain_bin(0x0000)

#     # Read value with ADS8686
#     read_dict = ads.read_last()
#     read_data = int(read_dict['A'][0])
#     # We double the range used in the to_voltage calculation to account for
#     # both +/- sides of the range.
#     # Ex. set_range(5) == +/-5V which spans a total of 10V
#     read = to_voltage(data=read_data, num_bits=ads.num_bits,
#                       voltage_range=ads.ranges[ads_in] * 2, use_twos_comp=True)
#     # Compare
#     assert abs(read - expected) <= tolerance


@pytest.mark.parametrize('voltage', [x * (10 ** -5) for x in range(0, 5 * (10 ** 5) + 4, 4)])
def test_dac_write_voltage(dac: DAC80508, ads: ADS8686, voltage):
    """Test DAC80508.write() method to write output voltage."""

    # Looking for values within 1 LSB of expected
    global tolerance
    global dac_out
    global ads_in
    # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
    # adjusted by the gain of the output and whether the internal reference is
    # divided by 2 or not.
    # dac.set_gain(gain=1, divide_reference=False)
    gain_info = dac.write_voltage(voltage=voltage, outputs=dac_out, auto_gain=True)

    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    # We double the range used in the to_voltage calculation to account for
    # both +/- sides of the range.
    # Ex. set_range(5) == +/-5V which spans a total of 10V
    read = to_voltage(data=read_data, num_bits=ads.num_bits,
                      voltage_range=ads.ranges[ads_in] * 2, use_twos_comp=True)
    # Compare
    assert abs(read - voltage) <= tolerance
