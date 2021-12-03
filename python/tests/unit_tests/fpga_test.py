"""Unit test for the FPGA class

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

i2c_bitfile = os.path.join(interfaces_path, 'i2c.bit')
top_level_module_bitfile = os.path.join(covg_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit')

# Fixtures
@pytest.fixture(scope='module')
def configured_fpga():
    from interfaces.interfaces import FPGA
    f = FPGA()
    assert f.init_device()
    yield f
    # Teardown
    f.xem.Close()


@pytest.fixture(scope='module')
def ep_bit_half():
    from interfaces.interfaces import Register
    # Wire 0x01 bits [31:16]
    return Register(address=0x01, default=0x0000, bit_width=32, bit_index_high=31, bit_index_low=16)


@pytest.fixture(scope='module')
def ep_bit():
    from interfaces.interfaces import Register
    # Wire 0x01 bits [31:0]
    return Register(address=0x01, default=0x0000, bit_width=32, bit_index_high=31, bit_index_low=0)


@pytest.fixture(scope='module')
def ep_trig():
    from interfaces.interfaces import Register
    # Trigger 0x41 bit [0]
    return Register(address=0x41, default=0x0000, bit_width=1, bit_index_high=0, bit_index_low=0)


# Tests
def test_init_device_default_bitfile():
    sys.path.append(interfaces_path)
    from interfaces.interfaces import FPGA

    f = FPGA() # Default bitfile
    assert f.init_device()
    f.xem.Close()


@pytest.mark.parametrize('bitfile', [
    i2c_bitfile,
    top_level_module_bitfile
])
def test_init_device(bitfile):
    from interfaces.interfaces import FPGA

    f = FPGA(bitfile)
    assert f.init_device()
    f.xem.Close()
    

def test_read_pipe_out(configured_fpga):
    import numpy as np
    from interfaces.interfaces import int_to_list
    test_num = 259451498578944966172687952835494371493
    test_list = int_to_list(test_num)
    data_len = 16
    output = bytearray(test_list + ([0] * (data_len - len(test_list))))
    output_int = int.from_bytes(output, byteorder='big')
    read_out = configured_fpga.read_pipe_out(1, data_len)[0]
    read_out_int = int.from_bytes(read_out, byteorder='little')
    assert read_out_int == output_int


def test_read_wire(configured_fpga):
    assert configured_fpga.read_wire(0x20) == 4262308911


@pytest.mark.parametrize('ep', [x for x in range(0x01, 0x06)])
def test_set_wire_and_read_wire(configured_fpga, ep):
    for data in range(0xffff):
        configured_fpga.set_wire(ep, data)
        assert configured_fpga.read_wire(ep + 0x20) == data


@pytest.mark.parametrize('ep', [x for x in range(0x01, 0x06)])
def test_set_wire_mask_with_read_wire(configured_fpga, ep):
    configured_fpga.set_wire(ep, 0xffff)
    configured_fpga.set_wire(ep, 0xaaaa, 0x00ff)
    assert configured_fpga.read_wire(ep + 0x20) == 0xffaa


def test_set_endpoint(configured_fpga, ep_bit_half):
    configured_fpga.set_wire(ep_bit_half.address, 0x00000000)
    configured_fpga.set_endpoint(ep_bit_half)
    assert configured_fpga.read_wire(ep_bit_half.address + 0x20) == 0xffff0000


def test_clear_endpoint(configured_fpga, ep_bit_half):
    configured_fpga.set_wire(ep_bit_half.address, 0xffffffff)
    configured_fpga.clear_endpoint(ep_bit_half)
    assert configured_fpga.read_wire(ep_bit_half.address + 0x20) == 0x0000ffff


def test_toggle_low(configured_fpga, ep_bit):
    configured_fpga.set_wire(ep_bit.address, 0xffffffff)
    configured_fpga.set_wire(0x06, 1)  # Enable toggle checking
    configured_fpga.toggle_low(ep_bit)
    configured_fpga.set_wire(0x06, 0)  # Disable toggle checking
    assert (configured_fpga.read_wire(ep_bit.address + 0x20) == 0xffffffff) and (configured_fpga.read_wire(0x27) == 1)


def test_toggle_high(configured_fpga, ep_bit):
    configured_fpga.set_wire(ep_bit.address, 0x00000000)
    configured_fpga.set_wire(0x07, 1)  # Enable toggle checking
    configured_fpga.toggle_high(ep_bit)
    configured_fpga.set_wire(0x07, 0)  # Disable toggle checking
    assert (configured_fpga.read_wire(ep_bit.address + 0x20) == 0x00000000) and (configured_fpga.read_wire(0x28) == 1)


def test_send_trig(configured_fpga, ep_trig):
    configured_fpga.send_trig(ep_trig)
    assert configured_fpga.read_wire(0x26) == 1


def test_read_ep(configured_fpga, ep_bit):
    assert configured_fpga.read_ep(ep_bit) == configured_fpga.read_wire(ep_bit.address + 0x20)


@pytest.mark.skip(reason='Not relevant for XEM7310, possibly relevant for XEM6310')
@pytest.mark.parametrize('output', [x for x in range(5)])
def test_get_pll_freq(configured_fpga, output):
    assert configured_fpga.get_pll_freq(output) == 10.0


@pytest.mark.skip(reason='Function does not work yet')
def test_get_available_endpoints(configured_fpga):
    # configured_fpga uses default bitfile fpga_test.bit
    expected = []
    got = configured_fpga.get_available_endpoints()
    print(got)
    assert got == expected
