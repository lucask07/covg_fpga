"""Testing interfaces.utile.calc_impedance function.

We assume a circuit with a voltage source, resistor, and unknown impedance all
in series. We would like to set the voltage source as a sine wave, read the
output voltage across the unknown impedance, and use these values with the
known value of the resistor to solve for the unknown impedance.

Abe Stroschein, ajstroschein@stthomas.edu
January 2022
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import ifft
import os, sys

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

from interfaces.interfaces import FPGA, DDR3
from interfaces.utils import calc_impedance, from_voltage, to_voltage

f = FPGA()
f.init_device()
ddr = DDR3(fpga=f)
resistor = 1000  # 1000 Ohm resistor
# Without phase shift, we should get a 184.86 Ohm resistor for the unkown impedance
capacitor = 1e-6  # 1 microFarad capacitor for unknown impedance
freq = 1
amp_in = 1
amp_out = 0.15602
dac80508_offset = 0x8000
t = np.arange(0, ddr.parameters['update_period']*ddr.parameters['sample_size'], ddr.parameters['update_period'])

# Input 1V amplitude at 1KHz
amp_in_code = from_voltage(voltage=amp_in, num_bits=16, voltage_range=2.5, with_negatives=False)
v_in_codes, freq_in_calc = ddr.make_sine_wave(amplitude=amp_in_code, frequency=freq, offset=dac80508_offset)
v_in = to_voltage(data=v_in_codes, num_bits=16, voltage_range=2.5, use_twos_comp=False)

# Output would be 156.02 mV amplitude at 1KHz shifted __ degrees
# These values according to MultiSim simulation at https://www.multisim.com/content/iosH7R4mMVBJ4s2L7RcdvK/impedance-analyzer-test/open/
amp_out_code = from_voltage(voltage=amp_out, num_bits=16, voltage_range=2.5, with_negatives=False)
v_out_codes, freq_out_calc = ddr.make_sine_wave(amplitude=amp_out_code, frequency=freq, offset=dac80508_offset)
v_out = to_voltage(data=v_out_codes, num_bits=16, voltage_range=2.5, use_twos_comp=False)

# Minor shift to see if it smooths out data
# shift_amt = ddr.parameters['sample_size'] // 20
# 90 degrees off matching inductor simulation: https://www.multisim.com/content/bB8jZR4bvDyNKYP5kx4TcX/impedance-analyzer-test-inductor/open/
shift_amt = (len(t) // 4)
new_len = min(len(v_in), len(v_out)) - shift_amt
v_in = v_in[:new_len]
v_out = v_out[-new_len:]
t = t[:new_len]

# Plot input, output
plt.plot(t, v_in, c='b')    # Input in blue
plt.plot(t, v_out, c='r')   # Output in red
plt.show()

# Plot impedance
impedance_calc = calc_impedance(v_in=v_in, v_out=v_out, resistance=resistor)
magnitude = [abs(x) for x in impedance_calc]
print('Average magnitude:', sum(magnitude) / len(magnitude))
plt.plot(t, magnitude, c='g')  # Impedance magnitude in green
plt.show()

# This graphs reals against imaginary parts
section_len = len(impedance_calc) // 5
# plt.scatter([x.real for x in impedance_calc[0: section_len]], [x.imag for x in impedance_calc[0: section_len]], c='b')
plt.scatter([x.real for x in impedance_calc[1 * section_len: 2 * section_len]], [x.imag for x in impedance_calc[1 * section_len: 2 * section_len]], c='g')
plt.scatter([x.real for x in impedance_calc[2 * section_len: 3 * section_len]], [x.imag for x in impedance_calc[2 * section_len: 3 * section_len]], c='c')
plt.scatter([x.real for x in impedance_calc[3 * section_len: 4 * section_len]], [x.imag for x in impedance_calc[3 * section_len: 4 * section_len]], c='m')
# plt.scatter([x.real for x in impedance_calc[4 * section_len:]], [x.imag for x in impedance_calc[4 * section_len:]], c='k')
plt.show()

# inverse_impedance_calc = ifft(impedance_calc)
# plt.scatter([x.real for x in inverse_impedance_calc], [x.imag for x in inverse_impedance_calc], c='purple')
# plt.show()
