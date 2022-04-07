from asyncore import write
import os, sys
import time
import atexit
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

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

from interfaces.interfaces import DDR3, FPGA, DAC80508, AD5453
from interfaces.boards import Daq
from interfaces.utils import from_voltage
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply


def cycle_power():
    pwr.all_off()
    for name in ['1V8', '5V', '3V3']:
        pwr.supply_on(name)
        time.sleep(0.05)

# --- Variables ---
pwr_setup = '3dual'
dac80508_offset = 0x8000
# FDAC: 1V 1KHz sine wave; SDAC: 1V 1KHz sine wave
fdac_amp_volt = 1
sdac_amp_volt = 1
target_freq = 1000.0
# Specify output channel for DAC80508
sdac_1_out_chan = 7
sdac_2_out_chan = 7
# Variables for which writes to run and how many
loop_num = 10   # Number of times to turning on, writing, turning off
# The path for the CSV storing the speed and quality of the data write
# DO NOT include .csv, that will be added automatically along with the date and time
csv_file = 'dac80508_ddr_write_CSV/'
USE_ORIGINAL = True
USE_PAUSE = True
USE_DOUBLE = True


# --- Instantiations ---
f = FPGA(bitfile=top_level_module_bitfile)
f.init_device()
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)  # 7V and +/-16.5V, None
pwr = Daq.Power(f)
gpio = Daq.GPIO(f)
ddr = DDR3(fpga=f)
# Since dac2 is the one with OUT0 on a pin we can access easily, we will use 
# that one to make the addressing easier.
dac1, dac2 = DAC80508.create_chips(fpga=f, number_of_chips=2)


# --- Configure and turn on power supplies ---
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)
dc_pwr.set("out_state", "ON", configs={"chan": 1})  # +7V
for ch in [2, 3]:
    dc_pwr.set("out_state", "ON", configs={"chan": ch})  # +/- 16.5V

# Turn off power at exit
atexit.register(pwr_off, [dc_pwr])


# --- Set up FPGA ---
cycle_power()

# --- Set up GPIO ---
# gpio.fpga.debug = True
gpio.spi_debug('ds1')

# --- Configure for DDR read to DAC80508 ---
for dac in [dac1, dac2]:
    dac.set_spi_sclk_divide(0x8)
    dac.set_ctrl_reg(0x3218)
    dac.set_config_bin(0x00)
    dac.set_gain(gain=1, outputs=[sdac_1_out_chan, sdac_2_out_chan], divide_reference=False)
    dac.set_data_mux('DDR')

# Change DDR read clock using AD5453 chip (only one with correct endpoints for this)
# TODO: make set_clk_divider a DDR3 method rather than a SPIFifoDriven method
# 0xA0 = 1.25 MHz, 0x50 = 2.5 MHz
ad5453 = AD5453(fpga=f)
ad5453.set_clk_divider(divide_value=0x50)

# --- Write to the DDR ---
# [0:13]    FDAC_1 [14:15] ADDR SDAC_1
# [16:29]   FDAC_2 [31:32] ADDR SDAC_1 and SDAC_2
# [32:45]   FDAC_3 [46:47] ADDR SDAC_2
# [48:61]   FDAC_4 [62:63] 0's
# [64:77]   FDAC_5 [78:79] 0's
# [80:93]   FDAC_6 [94:95] 0's
# [96:111]  SDAC_1
# [112:127] SDAC_2

# TODO: figure out what the voltage range should be for fdac, 3.3 is just a guess
fdac_amp_code = from_voltage(voltage=fdac_amp_volt, num_bits=14, voltage_range=3.3, with_negatives=False)
sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

# Data for the 6 AD5453 "Fast DACs"
fdac_sine, fdac_freq = ddr.make_sine_wave(amplitude=fdac_amp_code, frequency=target_freq)
# Data for the 2 DAC80508 "Slow DACs"
sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq, offset=dac80508_offset)

# Clear channel bits
fdac_sine = np.bitwise_and(fdac_sine, 0x3fff)

# Load data into DDR
# Set channel bits
ddr.data_arrays[0] = np.bitwise_or(fdac_sine, (sdac_1_out_chan & 0b110) << 13)
ddr.data_arrays[1] = np.bitwise_or(fdac_sine, (sdac_1_out_chan & 0b001) << 14)
ddr.data_arrays[2] = np.bitwise_or(fdac_sine, (sdac_2_out_chan & 0b110) << 13)
ddr.data_arrays[3] = np.bitwise_or(fdac_sine, (sdac_2_out_chan & 0b001) << 14)
for i in range(2):
    ddr.data_arrays[i + 4] = fdac_sine
for i in range(2):
    ddr.data_arrays[i + 6] = sdac_sine

# speed_out_data will be a list of tuples telling (speed of write, quality of data, type of write)
# Speed of write is in MB/s
# For quality of data, True is good data, False is bad data
speed_out_data = []
ORIGINAL = 0
PAUSE = 1
DOUBLE = 2
print('Enter q to quit the loop')

for i in range(loop_num):
    print(f'--- Loop Number {i}/{loop_num} ---')

    if USE_ORIGINAL is True:
        print('-- ORIGINAL --')
        _, speed = ddr.write_channels()
        user_in = input('Was the output good? (y/n)')
        if user_in == 'q':
            break
        speed_out_data.append((speed, user_in != 'n', ORIGINAL))
    cycle_power()

    if USE_PAUSE is True:
        print('-- PAUSE --')
        time.sleep(0.5)
        _, speed = ddr.write_channels()
        user_in = input('Was the output good? (y/n)')
        if user_in == 'q':
            break
        speed_out_data.append((speed, user_in != 'n', PAUSE))
    cycle_power()

    if USE_DOUBLE is True:
        print('-- DOUBLE --')
        ddr.write_channels()
        _, speed = ddr.write_channels()
        user_in = input('Was the output good? (y/n)')
        if user_in == 'q':
            break
        speed_out_data.append((speed, user_in != 'n', DOUBLE))
    cycle_power()

print('Loops complete')

# Write data to CSV
today = datetime.today()
date = str(today.date())
hour = str(today.hour)
minute = str(today.minute)
full_csv_file = csv_file + date + '_' + hour + minute + '.csv'
csv_string = '\n'.join([','.join([str(x) for x in row]) for row in speed_out_data])
with open(full_csv_file, 'w') as file:
    print('Writing CSV')
    file.write(csv_string)

# Print result statistics
print('--- Result Statistics ---')
write_speeds = [data[0] for data in speed_out_data]
output_qualities = [data[1] for data in speed_out_data]
print(f'Write Speed Range: [{min(write_speeds)}:{max(write_speeds)}]')
print(f'Mean Write Speed: {sum(write_speeds) / len(write_speeds)}')
print(f'Good Output: {sum(output_qualities)}')
print(f'Bad Output: {len(output_qualities) - sum(output_qualities)}')

write_types = [ORIGINAL, PAUSE, DOUBLE]
write_type_strs = ['Original', 'Pause', 'Double']
for write_type in write_types:
    print(f'-- {write_type_strs[write_type]} --')
    type_specific_data = [data for data in speed_out_data if data[2] == write_type]
    write_speeds = [data[0] for data in type_specific_data]
    output_qualities = [data[1] for data in type_specific_data]
    print(f'    Write Speed Range: [{min(write_speeds)}:{max(write_speeds)}]')
    print(f'    Mean Write Speed: {sum(write_speeds) / len(write_speeds)}')
    print(f'    Good Output: {sum(output_qualities)}')
    print(f'    Bad Output: {len(output_qualities) - sum(output_qualities)}')

# Graph scatter plot of data
colors = ['r', 'g', 'b']
for write_type in write_types:
    x_speed = [data[0] for data in speed_out_data if data[2] == write_type]
    y_quality = [data[1] for data in speed_out_data if data[2] == write_type]
    plt.scatter(x_speed, y_quality, color=colors[write_type], label=write_type_strs[write_type])
plt.legend()
plt.title('Quality of Data against Write Speeds')
plt.show()
