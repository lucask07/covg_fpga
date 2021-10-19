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
# Shouldn't need +/-16.5V for just ADS8686 and DAC80508

def pwr_off():
    for ch in [1, 2, 3]:
        dc_pwr.set('out_state', 'OFF', configs={'chan': ch})


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

    dc_pwr.set('i', 0.55, configs={'chan': 1})
    dc_pwr.set('v', 7, configs={'chan': 1})
    dc_pwr.set('ovp', 7.2, configs={'chan': 1})
    dc_pwr.set('ocp', 0.75, configs={'chan': 1})
    dc_pwr.set('out_state', 'ON', configs={'chan': 1})

    for name in ['1V8', '5V', '3V3']:
        pwr.supply_on(name)
        time.sleep(0.05)

    gpio = Daq.GPIO(f)
    gpio.fpga.debug = True
    gpio.spi_debug('ads')
    gpio.ads_misc('convst')

    yield f
    # Teardown
    # f.xem.Close()
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
def test_dac_gain(dac, ads, gain_code, expected_gain):
    # Looking for values within 5% (will be much smaller once working) of expected
    tolerance = 0.05
    # Set the output on DAC80508
    voltage_data = 0xffff
    # The DAC80508 operates on 16-bit resolution with a voltage range of 2.5V
    # adjusted by the gain of the output and whether the internal reference is
    # divided by 2 or not.
    expected = to_voltage(data=voltage_data, num_bits=16, voltage_range=2.5 * expected_gain)

    dac.write('DAC4', voltage_data)
    dac.set_gain(gain_code)
    print('Waiting...')
    time.sleep(2)
    # Read value with ADS8686
    read_dict = ads.read_last()
    read_data = int(read_dict['A'][0])
    read = to_voltage(data=read_data, num_bits=ads.num_bits, voltage_range=5, use_twos_comp=True)
    print(read_dict)
    print(read, expected)
    # Compare
    assert abs(read - expected) / expected <= tolerance


def test_dac_write_0(dac, ads):
    # Our error calculation doesn't work at 0, this tolerance is a voltage +/- range
    tolerance_voltage = 0.0001
    # Set the output on DAC80508
    dac.set_gain(0x0000)
    dac.write('DAC4', 0x0000)
    # Read value with ADS8686
    read_dict = ads.read_last() # TODO: convert data
    read = read_dict['A'][0]
    print(read_dict)
    # Compare
    assert abs(read) <= tolerance_voltage


@pytest.mark.parametrize('voltage', [x + 1 for x in range(0xffff)])
def test_dac_write(dac, ads, voltage):
    # Looking for values within 5% (will be much smaller once working) of expected
    tolerance = 0.05
    # Set the output on DAC80508
    dac.set_gain(0x0000)
    dac.write('DAC4', voltage)
    # Read value with ADS8686
    read_dict = ads.read_last() # TODO: convert data
    read = read_dict['A'][0]
    print(read_dict)
    print(read, voltage)
    # Compare
    assert abs(read - voltage) / voltage <= tolerance
