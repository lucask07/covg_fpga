"""Integration test for the DAC80508 and ADS8686 chips on the DAQ board.

Relies on DAC80508 and ADS8686 working separately. Requires DAC1_OUT4
connected to GP_ADC_IN5.
https://github.com/lucask07/open_covg_daq_pcb/blob/main/docs/covg_daq_v2.pdf
October 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
import os
import sys
from instrbuilder.instrument_opening import open_by_name
import time


# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
cwd = os.getcwd()
if 'covg_fpga' in cwd:
    covg_fpga_index = cwd.index('covg_fpga')
    covg_fpga_path = cwd[:covg_fpga_index + len('covg_fpga') + 1]
else:
    print('covg_fpga folder not found. Please navigate to the covg_fpga folder.')
    assert False
interfaces_path = os.path.join(covg_fpga_path, 'python')
sys.path.append(interfaces_path)

top_level_module_bitfile = os.path.join(covg_fpga_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit')

from interfaces.interfaces import FPGA, DAC80508, ADS8686
from interfaces.boards import Daq
from interfaces.utils import to_voltage, twos_comp

dc_pwr = open_by_name(name='rigol_pwr1')  # 7V in
dc_pwr2 = open_by_name(name='rigol_ps2')  # +/-16.5V -> needed for REFDIV going to Op-Amp buffers
tolerance = 0.008

def pwr_off():
    for ch in [1, 2, 3]:
        dc_pwr.set('out_state', 'OFF', configs={'chan': ch})
    for ch in [1, 2, 3]:
        dc_pwr2.set('out_state', 'OFF', configs={'chan': ch})

# Fixtures
@pytest.fixture(scope='module')
def fpga():
    """Reused FPGA instance for DAC80508 and ADS8686.
    
    Also powers on the DAQ board so the other chips can do setup in their
    instantiations.
    """

    global top_level_module_bitfile
    f = FPGA(bitfile=top_level_module_bitfile)
    assert f.init_device()
    # Power on
    pwr = Daq.Power(f)
    pwr.all_off()

    # Channel 1 on supply1 for Vin
    dc_pwr.set('i', 0.55, configs={'chan': 1})
    dc_pwr.set('v', 7, configs={'chan': 1})
    dc_pwr.set('ovp', 7.2, configs={'chan': 1})
    dc_pwr.set('ocp', 0.75, configs={'chan': 1})
    dc_pwr.set('out_state', 'ON', configs={'chan': 1})

    # Channel 1 and 2 setup
    for ch in [1, 2]:
        dc_pwr2.set('i', 0.39, configs={'chan': ch})
        dc_pwr2.set('v', 16.5, configs={'chan': ch})
        dc_pwr2.set('ovp', 16.7, configs={'chan': ch})
        dc_pwr2.set('ocp', 0.400, configs={'chan': ch})
        dc_pwr2.set('out_state', 'ON', configs={'chan': ch})

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
    # Power off
    # pwr_off()


@pytest.fixture(scope='module')
def dac(fpga):
    dac = DAC80508(fpga=fpga)
    dac.set_host_mode()
    dac.set_divider(0x8)
    dac.configure_master_bin(0x3218)
    dac.select_slave(1)
    dac.set_config_bin(0x00)
    return dac


@pytest.fixture(scope='module')
def ads(fpga):
    ads = ADS8686(fpga=fpga)
    ads.hw_reset(val=False)
    ads.set_host_mode()
    ads.setup()
    ads.set_range(5)
    ads.set_lpf(376)
    codes = ads.setup_sequencer(chan_list=[('5', 'FIXED')])
    print(f'Setup Sequencer Codes: {codes}')
    ads.write_reg_bridge()
    ads.set_fpga_mode()
    return ads


# Tests


@pytest.mark.parametrize('gain_code, expected_gain', [
    ((0 << 4) | (0 << 8), 1),   # Output gain: 1, REFDIV gain: 1,   Total gain: 1
    ((0 << 4) | (1 << 8), 1/2), # Output gain: 1, REFDIV gain: 1/2, Total gain: 1/2
    ((1 << 4) | (0 << 8), 2),   # Output gain: 2, REFDIV gain: 1,   Total gain: 2
    ((1 << 4) | (1 << 8), 1), # Output gain: 2, REFDIV gain: 1/2, Total gain: 1
])
def test_dac_gain_bin(dac, ads, gain_code, expected_gain):
    """Test DAC80508.set_gain_bin() method."""

    # Looking for values within 1 LSB of expected
    global tolerance
    # Set the output on DAC80508
    voltage_data = 0xffff
    # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
    # adjusted by the gain of the output and whether the internal reference is
    # divided by 2 or not.
    expected = to_voltage(data=voltage_data, num_bits=16, voltage_range=2.5 * expected_gain)

    dac.write('DAC4', voltage_data)
    dac.set_gain_bin(gain_code)
    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    # We double the range used in the to_voltage calculation to account for
    # both +/- sides of the range.
    # Ex. set_range(5) == +/-5V which spans a total of 10V
    read = to_voltage(data=read_data, num_bits=ads.num_bits, voltage_range=ads.ranges[5] * 2, use_twos_comp=True)
    print(read_dict)
    print(read, expected)
    # Compare
    assert abs(read - expected) <= tolerance


@pytest.mark.parametrize('gain, divide_reference, expected_gain', [
    (1, False, 1),  # Output gain: 1, REFDIV gain: 1,   Total gain: 1
    (1, True, 1/2), # Output gain: 1, REFDIV gain: 1/2, Total gain: 1/2
    (2, False, 2),  # Output gain: 2, REFDIV gain: 1,   Total gain: 2
    (2, True, 1),   # Output gain: 2, REFDIV gain: 1/2, Total gain: 1
])
def test_dac_gain(dac, ads, gain, divide_reference, expected_gain):
    """Test DAC80508.set_gain() method."""

    # Looking for values within 1 LSB of expected
    global tolerance
    # Set the output on DAC80508
    voltage_data = 0xffff
    # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
    # adjusted by the gain of the output and whether the internal reference is
    # divided by 2 or not.
    expected = to_voltage(data=voltage_data, num_bits=16, voltage_range=2.5 * expected_gain)

    dac.write('DAC4', voltage_data)
    dac.set_gain(gain=gain, outputs=4, divide_reference=divide_reference)
    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    # We double the range used in the to_voltage calculation to account for
    # both +/- sides of the range.
    # Ex. set_range(5) == +/-5V which spans a total of 10V
    read = to_voltage(data=read_data, num_bits=ads.num_bits, voltage_range=ads.ranges[5] * 2, use_twos_comp=True)
    print(read_dict)
    print(read, expected)
    # Compare
    assert abs(read - expected) <= tolerance


# @pytest.mark.parametrize('voltage', [x for x in range(0, 0xffff + 1)])
# def test_dac_write(dac, ads, voltage):
#     """Test DAC80508.write() method to write output voltage."""

#     # Looking for values within 1 LSB of expected
#     global tolerance
#     # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
#     # adjusted by the gain of the output and whether the internal reference is
#     # divided by 2 or not.
#     expected = to_voltage(data=voltage, num_bits=16,
#                           voltage_range=2.5)
#     dac.write('DAC4', voltage)
#     dac.set_gain_bin(0x0000)

#     # Read value with ADS8686
#     read_dict = ads.read_last()
#     read_data = int(read_dict['A'][0])
#     # We double the range used in the to_voltage calculation to account for
#     # both +/- sides of the range.
#     # Ex. set_range(5) == +/-5V which spans a total of 10V
#     read = to_voltage(data=read_data, num_bits=ads.num_bits,
#                       voltage_range=ads.ranges[5] * 2, use_twos_comp=True)
#     print(read_dict)
#     print(read, expected)
#     # Compare
#     assert abs(read - expected) <= tolerance


@pytest.mark.parametrize('voltage', [x * (10 ** -5) for x in range(0, 5 * (10 ** 5) + 4, 4)])
def test_dac_write_voltage(dac, ads, voltage):
    """Test DAC80508.write() method to write output voltage."""

    # Looking for values within 1 LSB of expected
    global tolerance
    # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
    # adjusted by the gain of the output and whether the internal reference is
    # divided by 2 or not.
    # dac.set_gain(gain=1, divide_reference=False)
    gain_info = dac.write_voltage(voltage=voltage, outputs=4, auto_gain=True)
    print(gain_info)

    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    # We double the range used in the to_voltage calculation to account for
    # both +/- sides of the range.
    # Ex. set_range(5) == +/-5V which spans a total of 10V
    read = to_voltage(data=read_data, num_bits=ads.num_bits,
                      voltage_range=ads.ranges[5] * 2, use_twos_comp=True)
    print(read_dict)
    print(read, voltage)
    # Compare
    assert abs(read - voltage) <= tolerance
