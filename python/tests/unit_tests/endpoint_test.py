"""Unit test for Endpoint class.

'Endpoint' is often abbreviated to 'ep' below.

Abe Stroschein, ajstroschein@stthomas.edu
January 2022
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

from interfaces.interfaces import Endpoint

# Total params for typical use = (0xff + 1) * 32 * 32 * 2 * 2 = 1048576
# We will choose some random sets of values from these ranges and test only those
num_test_params = 200
test_params = []

for i in range(num_test_params):
    address = randint(0, 0xff)
    bit_index_low = randint(0, 32)
    bit_width = randint(0, 32)
    gen_bit = bool(randint(0, 1))
    gen_address = bool(randint(0, 1))
    test_params.append(
        (address, bit_index_low, bit_width, gen_bit, gen_address))

# Tests


@pytest.mark.parametrize('address, bit_index_low, bit_width, gen_bit, gen_address', test_params)
def test_eq(address, bit_index_low, bit_width, gen_bit, gen_address):
    ep1 = Endpoint(address=address, bit_index_low=bit_index_low,
                   bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)
    ep2 = Endpoint(address=address, bit_index_low=bit_index_low,
                   bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)
    assert ep1 == ep2


@pytest.mark.parametrize('address, bit_index_low, bit_width, gen_bit, gen_address', test_params)
def test_str(address, bit_index_low, bit_width, gen_bit, gen_address):
    ep = Endpoint(address=address, bit_index_low=bit_index_low,
                  bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)
    expected_str = f'{hex(address)}[{bit_index_low}:{bit_index_low + bit_width}]'
    assert str(ep) == expected_str


@pytest.mark.parametrize('test_params', [test_params])
def test_update_endpoints_from_defines(test_params):
    # --- First, write the defines file in the current directory ---
    file_name = 'test_defines.v'
    file_loc = os.path.join(interfaces_path, 'tests', 'unit_tests', file_name)
    file_text = ''
    # Group 1 - Addresses
    # Group 2 - Bits referenced to group 1
    # Group 3 - Bits with absolute addresses
    num_groups = 3
    group1_eps = []
    group2_eps = []
    group3_eps = []
    taken_names = []

    # Start at num_groups - 1 so we can always subtract to get to available endpoints for other groups
    for i in range(len(test_params[num_groups - 1::num_groups])):
        # Convert range index to test_params index
        i = i * num_groups
        # Create Group 1 endpoint with no bit, only address
        address, bit_index_low_unused, bit_width, gen_bit, gen_address = test_params[i]
        name1_base = f'GROUP1_EP_ADDR{address}'
        if name1_base not in taken_names:
            taken_names.append(name1_base)

            if gen_bit and gen_address:
                name1 = name1_base + '_GEN_BIT_GEN_ADDR'
            elif gen_bit:
                name1 = name1_base + '_GEN_BIT'
            elif gen_address:
                name1 = name1_base + '_GEN_ADDR'
            else:
                name1 = name1_base
            line1 = f"`define {name1} 8'h{hex(address)[2:]} // bit_width={bit_width}"
            ep = Endpoint(address=address, bit_index_low=None,
                          bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)
            group1_eps.append(ep)

        # Create Group 2 endpoint with address pointing to Group 1 endpoint
        address_unused, bit_index_low, bit_width, gen_bit, gen_address = test_params[i + 1]
        name2 = f'GROUP2_EP{bit_index_low}'
        if name2 not in taken_names:
            taken_names.append(name2)
            if gen_bit:
                name2 += '_GEN_BIT'
            if gen_address:
                name2 += '_GEN_ADDR'
            line2 = f"`define {name2} {bit_index_low} // address={name1_base} bit_width={bit_width}"
            ep = Endpoint(address=address, bit_index_low=bit_index_low,
                          bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)
            group2_eps.append(ep)

        # Create Group 3 endpoint with bit and absolute address
        address, bit_index_low, bit_width, gen_bit, gen_address = test_params[i + 2]
        name3 = f'GROUP3_EP{bit_index_low}'
        if name3 not in taken_names:
            taken_names.append(name3)
            if gen_bit:
                name3 += '_GEN_BIT'
            if gen_address:
                name3 += '_GEN_ADDR'
            line3 = f"`define {name3} {bit_index_low} // address={hex(address)} bit_width={bit_width}"
            ep = Endpoint(address=address, bit_index_low=bit_index_low,
                          bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)
            group3_eps.append(ep)

        # Append lines to file text
        file_text += line1 + '\n' + line2 + '\n' + line3 + '\n'

    # Write to file
    with open(file_loc, 'w') as file:
        file.write(file_text)

    # --- Second, compare update_endpoints_from_defines output with endpoints created earlier ---
    Endpoint.update_endpoints_from_defines(ep_defines_path=file_loc)
    for created, read in [(group1_eps, Endpoint.endpoints_from_defines['GROUP1']), (group2_eps, Endpoint.endpoints_from_defines['GROUP2']), (group3_eps, Endpoint.endpoints_from_defines['GROUP3'])]:
        i = 0
        for read_ep in read.values():
            print(read_ep, '==', created[i])
            print(read_ep.gen_bit, created[i].gen_bit)
            print(read_ep.gen_address, created[i].gen_address)
            assert read_ep == created[i]
            i += 1
