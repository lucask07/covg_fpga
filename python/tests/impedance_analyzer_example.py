"""Example application of the package as an impedance analyzer.

Uses an Opal Kelly XEM7310 board, a DAC80508 Digital-Analog converter, a
ADS8686 Analog-Digital converter and a circuit containing a known resistance
and the unknown impedance. A sine wave in the form of an array of voltage
codes is loaded into the DDR, which automatically sends SPI commands to the
DAC80508 to output the sine wave to the circuit. The original sine wave and
the output signal across the unknown impedance are read back at the same time
using the sequencer of the ADS8686. These signals and the known resistance
value are used to calculate the current through the unknown impedance, which
is used with the read voltage to find the impedance using a Fourier Transform.

Circuit Setup
-------------
Connect the following in series
- DAC80508 output 7 (output channel can be changed at DAC80508_OUT_CHAN constant)
- Known resistance
- Unknown impedance
- GND (same as DAC80508 GND)

Connect the 2 ADS8686 inputs (A7, B3) to the following components
- Input A7 -> DAC80508 output 0
- Input B3 -> Unknown impedance positive side (the side connected to the known resistance)
- Input channels can be changed at ADS8686_A_CHAN, ADS8686_B_CHAN as long as
  A still takes the DAC80508 output and B takes the unknown impedance
  positive side.
- Make sure the ADS8686 shares the same GND as the DAC80508 GND

Usage
-----
RESISTANCE: Enter the resistance you used (a resistance closer to the real part of the
unknown impedance will yield more accurate results) as RESISTANCE in Ohms below.

FREQUENCY: You can also change the frequency of the output sine wave (a frequency that brings
the magnitude of the imaginary impedance closer to the magnitude of the
resistance you chose for the known resistance will yield better results) by
changing the FREQUENCY value in Hertz below.

AMPLITUDE: If needed, change the amplitude of the sine wave in the range of
0-2.5 Volts. The signal will be offset to keep the entire sine wave positive
since the DAC80508 cannot output negative voltages.

BITFILE_PATH: Change this to the string path to your top_level_module.bit
file. This will be loaded onto the FPGA and contains all the Opal Kelly
endpoints that allow us to communicate with the DDR, DAC80508, and ADS8686.

PLOT: To make sure the DAC80508 and ADS8686 are sending and receiving the sine
wave correctly, you can set this to True to create a graph of the voltages the
ADS8686 reads.


Abe Stroschein, ajstroschein@stthomas.edu
March 2022
"""
# TODO: include package name in script docstring above
# TODO: remove this comment when in new repo -> MUST TURN ON POWER SUPPLY YOURSELF (7V, 16.5V, -15V)

import numpy as np
from scipy.fft import rfftfreq
import matplotlib.pyplot as plt
# TODO: replace with package import when this script is moved to the package repo
import sys, os
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

top_level_module_bitfile = os.path.join(covg_fpga_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1',
                                        'top_level_module.bit')
from interfaces.interfaces import FPGA, DDR3, DAC80508, ADS8686
from interfaces.utils import calc_impedance, from_voltage, to_voltage


# USER SET CONSTANTS
RESISTANCE = 10000  # Resistance of the known resistance in Ohms
FREQUENCY = 200     # Desired frequency of the output sine wave in Hertz
AMPLITUDE = 1.0     # Desired amplitude of the output sine wave in Voltz
BITFILE_PATH = top_level_module_bitfile   # Path to top_level_module.bit
PLOT = False        # True to create a graph of ADS8686 readings, False otherwise

# Other constants
DAC80508_OFFSET = 0x8000                # DAC80508 voltage offset code for keeping sine wave positive
ADS8686_UPDATE_PERIOD = 4.950495e-06    # Time (seconds) between ADS8686 voltage reads
# TODO: remove this comment once in new repository -> DAC80508 is using DAC1 on the DAQ board in this example so we don't have to change the endpoints
DAC80508_OUT_CHAN = 7                   # DAC80508 sine wave output channel
ADS8686_A_CHAN = 7                      # ADS8686 input from side A reading DAC80508 output voltage
ADS8686_B_CHAN = 3                      # ADS8686 input from side B reading unknown impedance voltage


# --- Set up FPGA, DDR3, DAC80508, ADS8686 ---
f = FPGA(bitfile=BITFILE_PATH)
f.init_device()

# TODO:remove power part when in package repository?
import time
from interfaces.boards import Daq
# Turn on DAQ board Power
pwr = Daq.Power(f)
pwr.all_off()
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

ddr = DDR3(fpga=f)
dac = DAC80508(fpga=f)
adc = ADS8686(fpga=f)

# --- Configure DAC80508 for DDR driven ---
dac.set_spi_sclk_divide(0x8)
dac.set_ctrl_reg(0x3218)
dac.set_config_bin(0x00)

# TODO: switch this from AD5453 to DDR3 method
from interfaces.interfaces import AD5453
ad5453 = AD5453(fpga=f)
# Need in order to set frequency of input wave correctly
ad5453.set_clk_divider(divide_value=0x50)

# Change gain and reference divider for DAC80508 to get maximum precision
# Check (AMPLITUDE * 2) because we will shift all values up since DAC80508 cannot output negative values
if (AMPLITUDE * 2) <= 1.25:
    gain = 1
    divide_reference = True
    voltage_range = 1.25
elif (AMPLITUDE * 2) <= 2.5:
    # *2 and /2 is recommended instead of *1 and /1
    gain = 2
    divide_reference = True
    voltage_range = 2.5
elif (AMPLITUDE * 2) <= 5:
    gain = 2
    divide_reference = False
    voltage_range = 5
else:
    print(f'WARNING: cannot use AMPLITUDE {AMPLITUDE}V, limiting to maximum 2.5V')
dac.set_gain(gain=gain, outputs=DAC80508_OUT_CHAN, divide_reference=divide_reference)
dac.set_data_mux('DDR')

# --- Configure ADS8686 for read on specified channel ---
adc.hw_reset(val=False)
adc.set_host_mode()
adc.setup()
adc.set_range(5)
adc.set_lpf(376)
# "A" side takes input, "B" side takes output
chan_list = (str(ADS8686_A_CHAN), str(ADS8686_B_CHAN))
input_side = 'A'
output_side = 'B'
codes = adc.setup_sequencer(chan_list=[chan_list])
adc.write_reg_bridge()
adc.set_fpga_mode()

# --- Generate input voltage signal ---
amplitude_code = from_voltage(voltage=AMPLITUDE, num_bits=16, voltage_range=voltage_range, with_negatives=False)
v_in_code, actual_freq = ddr.make_sine_wave(amplitude=amplitude_code, frequency=FREQUENCY, offset=DAC80508_OFFSET, actual_frequency=True)

# --- Send input signal ---
# Last 2 bits of first array are first 2 bits of channel for DAC80508
# Second-to-last bit of second array is last bit of channel for DAC80508
# Clear channel bits
ddr.data_arrays[0] = np.bitwise_and(ddr.data_arrays[0], 0x3fff).astype(np.uint16)
ddr.data_arrays[1] = np.bitwise_and(ddr.data_arrays[1], 0x3fff).astype(np.uint16)
# Set channel bits
ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (DAC80508_OUT_CHAN & 0b110) << 13).astype(np.uint16)
ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (DAC80508_OUT_CHAN & 0b001) << 14).astype(np.uint16)
# Set voltage
ddr.data_arrays[6] = v_in_code.astype(np.uint16)
ddr.write_channels()
ddr.write_channels()   # Double write to ensure good output

# --- Read input and ouput voltage signals ---
throw_away = 15     # TODO: remove this (and in boards.py)
for i in range(throw_away):
    data_stream = adc.stream_mult(twos_comp_conv=False)
v_in_code = data_stream[input_side]
v_out_code = data_stream[output_side]

# --- Calculate impedance across frequencies ---
# Convert back to voltage
v_in_voltage = to_voltage(data=v_in_code, num_bits=16, voltage_range=10, use_twos_comp=True)
v_out_voltage = to_voltage(data=v_out_code, num_bits=16, voltage_range=10, use_twos_comp=True)
impedance_arr = calc_impedance(v_in=v_in_voltage, v_out=v_out_voltage, resistance=RESISTANCE)

# --- Set up x frequencies ---
x_freq = rfftfreq(len(v_in_voltage), ADS8686_UPDATE_PERIOD)

# --- Find nearest x frequency to input frequency ---
distances_from_actual = [abs(x - actual_freq) for x in x_freq]
desired_index = distances_from_actual.index(min(distances_from_actual))
frequency_found = x_freq[desired_index]

# --- Print impedance at that frequency ---
z = impedance_arr[desired_index]
print(f'Impedance of {z} Ohms found at {frequency_found} Hz')
print(f'Phasor Notation Impedance: {np.abs(z)}\N{ANGLE}{np.angle(z, deg=True)}\N{DEGREE SIGN}')

# --- Optionally plot input and output ---
if PLOT:
    # Continuous Graph
    plt.ion()
    fig, ax = plt.subplots()
    stop = False

    def set_stop(event):
        global stop
        stop = True

    fig.canvas.mpl_connect('close_event', set_stop)

    ax.set_xlabel('Time')
    ax.set_ylabel('Voltage')
    while not stop:
        data_stream = adc.stream_mult(twos_comp_conv=False)
        v_in = to_voltage(
            data=data_stream['A'], num_bits=16, voltage_range=10, use_twos_comp=True)
        v_out = to_voltage(
            data=data_stream['B'], num_bits=16, voltage_range=10, use_twos_comp=True)
        x = [len(v_out) + j for j in range(len(v_out))]
        ax.plot(x, v_in, color='blue', scalex=True, scaley=False, label='v_in')
        ax.plot(x, v_out, color='red', scalex=True, scaley=False, label='v_out')
        ax.set_ylim(bottom=-5, top=5, auto=False)
        ax.legend(loc='upper left')
        ax.set_xlabel('Time (index)')
        ax.set_ylabel('Voltage (Volts)')
        ax.set_title(label='v_in and v_out over time')
        plt.draw()
        plt.pause(0.01)
        plt.cla()
