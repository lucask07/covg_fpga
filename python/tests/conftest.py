import os
import sys
import pytest

# The instruments.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
cwd = os.getcwd()
if 'covg_fpga' in cwd:
    covg_fpga_index = cwd.index('covg_fpga')
    covg_fpga_path = cwd[:covg_fpga_index + len('covg_fpga') + 1]
else:
    print('covg_fpga folder not found. Please navigate to the covg_fpga folder.')
    assert False
instruments_path = os.path.join(covg_fpga_path, 'python')
sys.path.append(instruments_path)

from instruments.power_supply import open_rigol_supply, pwr_off, config_supply

@pytest.fixture(scope='session')
def power_supply():
    pwr_setup = '3dual'
    dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)  # 7V and +/-16.5V, None
    # Configure and turn on power supplies
    config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)
    dc_pwr.set("out_state", "ON", configs={"chan": 1})  # +7V
    for ch in [2, 3]:
        dc_pwr.set("out_state", "ON", configs={"chan": ch})  # +/- 16.5V
    yield dc_pwr

    # Power off
    pwr_off([dc_pwr])
