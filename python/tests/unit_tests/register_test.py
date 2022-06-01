"""Unit test for Register class.

'Register' is often abbreviated to 'reg' below.

Abe Stroschein, ajstroschein@stthomas.edu
January 2022
"""

import pytest
import os
import sys
from random import randint
import pandas as pd


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

from interfaces.interfaces import Register

pytestmark = [pytest.mark.usable, pytest.mark.no_fpga]


# We will choose some random sets of values from these ranges and test only those
num_test_params = 200
test_params = []
num_chips = 5

for i in range(num_test_params):
    address = randint(0, 0xff)
    default = randint(0, 0xffffffff)
    bit_index_high = randint(0, 32)
    bit_index_low = randint(0, 32)
    bit_width = randint(0, 32)
    while (address, default, bit_index_high, bit_index_low, bit_width) in test_params:
        # Repeat register, make a new one
        address = randint(0, 0xff)
        default = randint(0, 0xffffffff)
        bit_index_high = randint(0, 32)
        bit_index_low = randint(0, 32)
        bit_width = randint(0, 32)
    test_params.append(
        (address, default, bit_index_high, bit_index_low, bit_width))

# Fixtures
@pytest.fixture(scope='module')
def test_regs():
    return [Register(address=address, default=default, bit_index_high=bit_index_high, bit_index_low=bit_index_low, bit_width=bit_width) for (address, default, bit_index_high, bit_index_low, bit_width) in test_params]

@pytest.fixture(scope='module')
def test_file():
    file_name = 'test_registers.xlsx'
    file_loc = os.path.join(interfaces_path, 'tests', 'unit_tests', file_name)
    with pd.ExcelWriter(path=file_loc, engine='openpyxl') as writer:
        # Write the file so it is there when the tests go to use it
        for i in range(num_chips):
            # Since we made sure the test_params are all different, we can use all
            # params of the register for the name to avoid duplicate names.
            data = [(f'reg{address}{default}{bit_index_high}{bit_index_low}{bit_width}', hex(address), hex(default), bit_index_high, bit_index_low, bit_width) for (address, default, bit_index_high,
                                                                                                    bit_index_low, bit_width) in test_params[(len(test_params) // num_chips) * i:(len(test_params) // num_chips) * (i + 1)]]
            df = pd.DataFrame(data=data, columns=['Name', 'Hex Address', 'Default Value', 'Bit Index (High)', 'Bit Index (Low)', 'Bit Width'])
            df.to_excel(excel_writer=writer, sheet_name=f'CHIP{i}')

    # Return only the path to the file, which gets passed to any tested functions
    return file_loc

@pytest.fixture(scope='module')
def gotten_regs(test_file):
    all_regs = {}
    for chip_num in range(num_chips):
        all_regs.update(Register.get_chip_registers(sheet=f'CHIP{chip_num}', workbook_path=test_file))
    return list(all_regs.values())

# Tests


@pytest.mark.parametrize('address, default, bit_index_high, bit_index_low, bit_width', test_params)
def test_eq(address, default, bit_index_high, bit_index_low, bit_width):
    reg1 = Register(address=address, default=default, bit_index_high=bit_index_high, bit_index_low=bit_index_low, bit_width=bit_width)
    reg2 = Register(address=address, default=default, bit_index_high=bit_index_high, bit_index_low=bit_index_low, bit_width=bit_width)
    assert reg1 == reg2

@pytest.mark.parametrize('address, default, bit_index_high, bit_index_low, bit_width', test_params)
def test_str(address, default, bit_index_high, bit_index_low, bit_width):
    reg2 = Register(address=address, default=default, bit_index_high=bit_index_high, bit_index_low=bit_index_low, bit_width=bit_width)
    expected_str = f'{hex(address)}[{bit_index_low}:{bit_index_high}]'
    assert str(reg2) == expected_str

def test_get_chip_registers(gotten_regs, test_regs):
    for expected in test_regs:
        assert expected in gotten_regs
