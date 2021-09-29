"""Unit test for the ADS8686 class

Relies on FPGA, SPIController classes working
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

# ads8686_test_bitfile =


# Fixtures
@pytest.fixture(scope='module')
def chip():
    # global ADS8686_test_bitfile
    from interfaces.interfaces import FPGA, ADS8686
    f = FPGA()
    assert f.init_device()
    yield ADS8686(f)
    # Teardown
    f.xem.Close()


# Tests
def test_multiple_instances():
    from interfaces.interfaces import FPGA, ADS8686, Endpoint
    f = FPGA()
    group1 = [
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686'))
    ]
    # Must use endpoints_from_defines directly rather than get_chip_endpoints
    # so we increment the reference dictionary rather than a copy.
    Endpoint.increment_endpoints(
        Endpoint.endpoints_from_defines.get('ADS8686'))
    group2 = [
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686'))
    ]

    assert all([x.endpoints == group1[0].endpoints for x in group1])
    assert all([x.endpoints == group2[0].endpoints for x in group2])
    assert group1[0].endpoints != group2[0].endpoints


@pytest.mark.parametrize('number_of_chips', [x for x in range(10)])
def test_create_chips(number_of_chips):
    from interfaces.interfaces import FPGA, ADS8686, Endpoint
    f = FPGA()
    # Update the endpoints so they get reset when this test runs multiple times
    Endpoint.update_endpoints_from_defines()
    chips = ADS8686.create_chips(fpga=f, number_of_chips=number_of_chips)
    # Skip the first element in compare_chips because that is what we will compare against
    assert all([x.endpoints != chips[0].endpoints for x in chips[1:]])
