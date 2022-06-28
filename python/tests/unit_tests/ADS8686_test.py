"""Unit test for the ADS8686 class

Relies on FPGA, SPIController classes working
August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

import pytest
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.ADS8686 import ADS8686


# Fixtures
@pytest.fixture(scope='module')
def f():
    f = FPGA()
    assert f.init_device()
    yield f
    # Teardown
    f.xem.Close()


@pytest.fixture(scope='module')
def chip(f):
    yield ADS8686(f)


# Tests
def test_multiple_instances(f):
    group1 = [
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686'))
    ]
    # Must use endpoints_from_defines directly rather than get_chip_endpoints
    # so we increment the reference dictionary rather than a copy.
    Endpoint.advance_endpoints(
        Endpoint.endpoints_from_defines.get('ADS8686'))
    group2 = [
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686')),
        ADS8686(fpga=f, endpoints=Endpoint.get_chip_endpoints('ADS8686'))
    ]

    assert all([x.endpoints == group1[0].endpoints for x in group1])
    assert all([x.endpoints == group2[0].endpoints for x in group2])
    assert group1[0].endpoints != group2[0].endpoints


@pytest.mark.parametrize('number_of_chips',
                         [pytest.param('a', marks=pytest.mark.xfail), pytest.param(0, marks=pytest.mark.xfail)] +
                         [x for x in range(1, 10)]
                         )
def test_create_chips(number_of_chips, f):
    # Update the endpoints so they get reset when this test runs multiple times
    Endpoint.update_endpoints_from_defines()
    chips = ADS8686.create_chips(fpga=f, number_of_chips=number_of_chips)
    # Skip the first element in compare_chips because that is what we will compare against
    assert all([x.endpoints != chips[0].endpoints for x in chips[1:]])
