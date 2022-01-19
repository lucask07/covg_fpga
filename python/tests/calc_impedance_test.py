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
from scipy.fft import ifft, fft, fftfreq, rfft, rfftfreq
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
# Frequency in Hertz
freq = 1000
amp_in = 1
amp_out = 0.7072
dac80508_offset = 0x8000
t = np.arange(0, ddr.parameters['update_period']*ddr.parameters['sample_size'], ddr.parameters['update_period'])

# Input 1V amplitude at 1KHz
amp_in_code = from_voltage(voltage=amp_in, num_bits=16, voltage_range=2.5, with_negatives=False)
v_in_codes, freq_in_calc = ddr.make_sine_wave(amplitude=amp_in_code, frequency=freq, offset=dac80508_offset)
v_in = to_voltage(data=v_in_codes, num_bits=16, voltage_range=2.5, use_twos_comp=False)

# These values according to MultiSim simulation at https://www.multisim.com/content/iosH7R4mMVBJ4s2L7RcdvK/impedance-analyzer-test/open/
amp_out_code = from_voltage(voltage=amp_out, num_bits=16, voltage_range=2.5, with_negatives=False)
v_out_codes, freq_out_calc = ddr.make_sine_wave(amplitude=amp_out_code, frequency=freq, offset=dac80508_offset)
v_out = to_voltage(data=v_out_codes, num_bits=16, voltage_range=2.5, use_twos_comp=False)

# 45 degrees behind for about -1000j Ohms impedance
shift_amt = (len(t) // 16)
new_len = min(len(v_in), len(v_out)) - shift_amt
v_in = v_in[:new_len]
v_out = v_out[-new_len:]
t = t[:new_len]

# Remove offset
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

# Plot input, output over time
plt.plot(t, v_in, c='b', label='v_in')    # Input in blue
plt.plot(t, v_out, c='r', label='v_out')   # Output in red
plt.title('v_in, v_out')
plt.legend(loc='upper left')
plt.show()

# Plot current over time
current = [(v_in[i] - v_out[i]) / resistor for i in range(len(v_in))]
plt.plot(t, current, c='orange', label='current = (v_in - v_out) / resistance')
plt.title('Current')
plt.show()

# Calculate frequencies from time
# x_frequencies = fftfreq(len(t), ddr.parameters['update_period'])
x_frequencies = rfftfreq(len(t), ddr.parameters['update_period'])

# Plot input, output transforms against frequencies
plt.plot(x_frequencies, np.abs(rfft(v_in)), c='b', label='v_in')
plt.plot(x_frequencies, np.abs(rfft(v_out)), c='r', label='v_out')
plt.legend(loc='upper left')
plt.title('v_in and v_out against Frequencies')
plt.show()

# Plot current transform against frequencies
plt.plot(x_frequencies, np.abs(rfft(current)), c='orange', label='current')
plt.title('Current against Frequencies')
plt.show()

# Calculate impedance
impedance_calc = calc_impedance(v_in=v_in, v_out=v_out, resistance=resistor)
magnitude = np.abs(impedance_calc)
avg = sum(impedance_calc) / len(impedance_calc)
print('Average magnitude:', sum(magnitude) / len(magnitude))
print('Average impedance:', avg)
i = 0
for f in x_frequencies:
    if f < freq_in_calc:
        i += 1
    else:
        break
z = impedance_calc[i]
print(f'Impedance at {freq_in_calc}: {z}')

# Plot magnitude impedance over frequencies
plt.plot(x_frequencies, magnitude, c='b', label='Impedance Magnitude')
plt.title('Impedance Magnitude over Frequencies')
plt.show()

# Plot impedance magnitude over time
# plt.plot(t[::2], magnitude, c='g')
# plt.title('calc_impedance Magnitude over Time')
# plt.show()

# Plot impedance real and imaginary parts over time
# plt.plot(t[::2], [x.real for x in impedance_calc], c='b', label='real')
# plt.plot(t[::2], [x.imag for x in impedance_calc], c='r', label='imaginary')
# plt.legend(loc='upper left')
# plt.title('Parts of Impedance over Time')
# plt.show()

# This graphs reals against imaginary parts
section_len = len(impedance_calc) // 5
plt.scatter([x.real for x in impedance_calc[0: section_len]], [x.imag for x in impedance_calc[0: section_len]], c='b', label='Section 1')
plt.scatter([x.real for x in impedance_calc[1 * section_len: 2 * section_len]], [x.imag for x in impedance_calc[1 * section_len: 2 * section_len]], c='g', label='Section 2')
plt.scatter([x.real for x in impedance_calc[2 * section_len: 3 * section_len]], [x.imag for x in impedance_calc[2 * section_len: 3 * section_len]], c='c', label='Section 3')
plt.scatter([x.real for x in impedance_calc[3 * section_len: 4 * section_len]], [x.imag for x in impedance_calc[3 * section_len: 4 * section_len]], c='m', label='Section 4')
plt.scatter([x.real for x in impedance_calc[4 * section_len:]], [x.imag for x in impedance_calc[4 * section_len:]], c='k', label='Section 5')
plt.title('Real vs. Imaginary calc_impedance')
plt.show()
