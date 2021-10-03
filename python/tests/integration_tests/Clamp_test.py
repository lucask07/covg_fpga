"""Integration test for the Clamp board class

Relies on FPGA class working
October 2021

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

top_level_module_bitfile = os.path.join(interfaces_path, 'top_level_module.bit')

# Fixtures
@pytest.fixture(scope='module')
def clamp():
    global i2c_test_bitfile
    from interfaces.interfaces import FPGA, Endpoint
    from interfaces.boards import Clamp
    f = FPGA(bitfile=top_level_module_bitfile)
    assert f.init_device()
    Endpoint.update_endpoints_from_defines(
        ep_defines_path='../../../fpga_XEM7310/fpga_XEM7310.srcs/sources_1/ep_defines.v')
    yield Clamp(fpga=f)
    # Teardown
    f.xem.Close()


# Tests
def test_multiple_instances():
    from interfaces.interfaces import FPGA, Endpoint
    from interfaces.boards import Clamp
    f = FPGA()
    clamps = []
    for i in range(4):
        clamps.append(Clamp(f))
        # Must use endpoints_from_defines directly rather than get_chip_endpoints
        # so we increment the reference dictionary rather than a copy.
        Endpoint.increment_endpoints(
            Endpoint.endpoints_from_defines.get('I2CDC'))

    # Make sure all the endpoints for chips within a Clamp are the same
    # Skip the first chip because that is what we will compare against
    for clamp in clamps:
        assert all([chip.endpoints == clamp.TCA_0.endpoints for chip in [clamp.TCA_1, clamp.UID, clamp.DAC]])

    # Make sure the endpoints for different Clamps are different from using increment_endpoints()
    # Skip the first element in clamps because that is what we will compare against
    # Can just use TCA_0 since we already checked that all the chips have the same endpoints
    assert all(
        [x.TCA_0.endpoints != clamps[0].TCA_0.endpoints for x in clamps[1:]])
