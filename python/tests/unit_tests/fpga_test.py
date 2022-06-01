"""Unit test for the FPGA class

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
import os
import sys
from random import randint


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

from interfaces.interfaces import FPGA, Endpoint

pytestmark = [pytest.mark.usable, pytest.mark.fpga_only]


# Fixtures
@pytest.fixture(scope='module')
def configured_fpga() -> FPGA:
    f = FPGA(bitfile=top_level_module_bitfile)
    assert f.init_device()
    yield f
    # Teardown
    f.xem.Close()

@pytest.fixture(scope='module')
def test_endpoints():
    return Endpoint.get_chip_endpoints('FPGATEST')

# Tests
def test_read_pipe_out(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint]):
    import numpy as np
    from interfaces.utils import int_to_list
    test_num = 1234567890987654321
    test_list = int_to_list(test_num, byteorder='little')
    data_len = 16
    output = bytearray(test_list + ([0] * (data_len - len(test_list))))
    output_int = int.from_bytes(output, byteorder='little')
    read_out = configured_fpga.read_pipe_out(test_endpoints['STATIC_READ_PO'].address, data_len)[0]
    read_out_int = int.from_bytes(read_out, byteorder='little')
    assert read_out_int == output_int


def test_read_wire(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint]):
    assert configured_fpga.read_wire(test_endpoints['STATIC_READ_WO'].address) == 123456789


@pytest.mark.parametrize('data', [randint(0x0000_0000, 0xFFFF_FFFF) for x in range(250)])
def test_looped_wires(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], data):
    configured_fpga.set_wire(test_endpoints['LOOPED_WI'].address, data)
    assert configured_fpga.read_wire(test_endpoints['LOOPED_WO'].address) == data


@pytest.mark.parametrize('data', [randint(0x0000_0000, 0xFFFF_FFFF) for x in range(250)])
def test_looped_wires_mask(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], data):
    configured_fpga.set_wire(test_endpoints['LOOPED_WI'].address, 0xFF00_0000)
    configured_fpga.set_wire(test_endpoints['LOOPED_WI'].address, data, 0x00FF_FFFF)
    assert configured_fpga.read_wire(test_endpoints['LOOPED_WO'].address) == 0xFF00_0000 | data


def test_send_trig(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint]):
    configured_fpga.send_trig(test_endpoints['TI'])
    assert configured_fpga.read_wire(test_endpoints['TI_CONFIRM'].address) == 1


def test_read_trig(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint]):
    # The TriggerOut in the bitfile is repeatedly triggered and should appear always triggered to the Python
    for i in range(3):
        assert configured_fpga.read_trig(test_endpoints['TO'])

# Skipping some below


@pytest.mark.skip(reason='Method may be unused')
def test_set_endpoint(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], ep_bit_half):
    configured_fpga.set_wire(ep_bit_half.address, 0x00000000)
    configured_fpga.set_endpoint(ep_bit_half)
    assert configured_fpga.read_wire(ep_bit_half.address + 0x20) == 0xffff0000


@pytest.mark.skip(reason='Method may be unused')
def test_clear_endpoint(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], ep_bit_half):
    configured_fpga.set_wire(ep_bit_half.address, 0xffffffff)
    configured_fpga.clear_endpoint(ep_bit_half)
    assert configured_fpga.read_wire(ep_bit_half.address + 0x20) == 0x0000ffff


@pytest.mark.skip(reason='Method may be unused')
def test_toggle_low(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], ep_bit):
    configured_fpga.set_wire(ep_bit.address, 0xffffffff)
    configured_fpga.set_wire(0x06, 1)  # Enable toggle checking
    configured_fpga.toggle_low(ep_bit)
    configured_fpga.set_wire(0x06, 0)  # Disable toggle checking
    assert (configured_fpga.read_wire(ep_bit.address + 0x20) == 0xffffffff) and (configured_fpga.read_wire(0x27) == 1)


@pytest.mark.skip(reason='Method may be unused')
def test_toggle_high(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], ep_bit):
    configured_fpga.set_wire(ep_bit.address, 0x00000000)
    configured_fpga.set_wire(0x07, 1)  # Enable toggle checking
    configured_fpga.toggle_high(ep_bit)
    configured_fpga.set_wire(0x07, 0)  # Disable toggle checking
    assert (configured_fpga.read_wire(ep_bit.address + 0x20) == 0x00000000) and (configured_fpga.read_wire(0x28) == 1)


@pytest.mark.skip(reason='Method may be unused')
def test_read_ep(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], ep_bit):
    assert configured_fpga.read_ep(ep_bit) == configured_fpga.read_wire(ep_bit.address + 0x20)


@pytest.mark.skip(reason='Not relevant for XEM7310, possibly relevant for XEM6310')
@pytest.mark.parametrize('output', [x for x in range(5)])
def test_get_pll_freq(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint], output):
    assert configured_fpga.get_pll_freq(output) == 10.0


@pytest.mark.skip(reason='Function does not work yet')
def test_get_available_endpoints(configured_fpga: FPGA, test_endpoints: dict[str, Endpoint]):
    # configured_fpga uses default bitfile fpga_test.bit
    expected = []
    got = configured_fpga.get_available_endpoints()
    print(got)
    assert got == expected
