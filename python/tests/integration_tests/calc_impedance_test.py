"""Integration test for calculating impedance.

Requires host computer only. Uses these functions:
- interfaces.interfaces.DDR3.make_sine_wave
- interfaces.utils.calc_impedance
- interfaces.utils.from_voltage
- interfaces.utils.to_voltage

Abe Stroschein, ajstroschein@stthomas.edu
January 2022
"""

import pytest
import os
import sys
import numpy as np
from scipy.fft import rfftfreq

# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
cwd = os.getcwd()
if 'covg_fpga' in cwd:
    covg_fpga_index = cwd.index('covg_fpga')
    covg_path = cwd[:covg_fpga_index + len('covg_fpga') + 1]
else:
    print('covg_fpga folder not found. Please navigate to the covg_fpga folder.')
    assert False
interfaces_path = os.path.join(covg_path, 'python/src')
sys.path.append(interfaces_path)
top_level_module_bitfile = os.path.join(covg_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit')

from interfaces.interfaces import FPGA
from interfaces.peripherals.DDR3 import DDR3
from interfaces.utils import from_voltage, to_voltage, calc_impedance

pytestmark = [pytest.mark.usable, pytest.mark.no_fpga]

# Fixtures


@pytest.fixture(scope='module')
def ddr():
    global top_level_module_bitfile
    f = FPGA(bitfile=top_level_module_bitfile)
    f.init_device()
    ddr = DDR3(fpga=f)
    yield ddr
    # Teardown
    f.xem.Close()

# Tests


def test_calc_impedance(ddr):
    accepted_error = 0.002  # Accepting 0.2% error (calculated by 0.2% of magnitude being allowed for real and imaginary parts)
    # Expected according to https://www.multisim.com/content/iosH7R4mMVBJ4s2L7RcdvK/impedance-analyzer-test/open/
    expected = complex(0, -1000)  # Expecting 0 - 1000j Ohms impedance

    resistor = 1000  # 1000 Ohm resistor
    freq = 1000  # Frequency in Hertz
    amp_in = 1
    amp_out = 0.7072
    dac80508_offset = 0x8000
    t = np.arange(0,
              ddr.parameters['update_period'] * ddr.parameters['sample_size'],
              ddr.parameters['update_period'])

    # Input 1V amplitude at 1KHz
    amp_in_code = from_voltage(voltage=amp_in,
                            num_bits=16,
                            voltage_range=2.5,
                            with_negatives=False)
    v_in_codes, freq_in_calc = ddr.make_sine_wave(amplitude=amp_in_code,
                                                frequency=freq,
                                                offset=dac80508_offset)
    v_in = to_voltage(data=v_in_codes,
                    num_bits=16,
                    voltage_range=2.5,
                    use_twos_comp=False)

    # Output 0.7072V amplitude at 1KHz
    # These values according to MultiSim simulation at
    # https://www.multisim.com/content/iosH7R4mMVBJ4s2L7RcdvK/impedance-analyzer-test/open/
    amp_out_code = from_voltage(voltage=amp_out,
                                num_bits=16,
                                voltage_range=2.5,
                                with_negatives=False)
    v_out_codes, freq_out_calc = ddr.make_sine_wave(amplitude=amp_out_code,
                                                    frequency=freq,
                                                    offset=dac80508_offset)
    v_out = to_voltage(data=v_out_codes,
                    num_bits=16,
                    voltage_range=2.5,
                    use_twos_comp=False)

    # 45 degrees behind for about -1000j Ohms impedance
    shift_amt = (len(t) // 16)
    new_len = min(len(v_in), len(v_out)) - shift_amt
    v_in = v_in[:new_len]
    v_out = v_out[-new_len:]
    t = t[:new_len]

    # Remove offset before transform
    v_in = [x - 1.25 for x in v_in]
    v_out = [x - 1.25 for x in v_out]

    # We need to cut off the signals so they appear periodic for the transform
    max_time = t[-1]
    # Period in seconds
    period = 1 / freq_in_calc
    num_complete_periods = max_time // period
    target_time = period * num_complete_periods
    end_index = int(target_time / ddr.parameters['update_period'])
    t = t[:end_index]
    v_in = v_in[:end_index]
    v_out = v_out[:end_index]

    # Calculate frequencies from time
    x_frequencies = rfftfreq(len(t), ddr.parameters['update_period'])

    # Calculate impedance
    impedance_calc = calc_impedance(v_in=v_in, v_out=v_out, resistance=resistor)
    # Find nearest frequency to frequency we sent in v_in
    i = 0
    for f in x_frequencies:
        if f < freq_in_calc:
            i += 1
        else:
            break
    # Get impedance at that frequency
    z = impedance_calc[i]
    print(z)
    error = accepted_error * np.abs(z)
    real_upper_bound = expected.real + error
    real_lower_bound = expected.real - error
    imag_upper_bound = expected.imag + error
    imag_lower_bound = expected.imag - error
    assert real_lower_bound < z.real < real_upper_bound
    assert imag_lower_bound < z.imag < imag_upper_bound
