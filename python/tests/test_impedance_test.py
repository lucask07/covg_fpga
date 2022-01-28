"""Sandbox type test file for interfaces.boards.Daq.test_impedance method.

Abe Stroschein, ajstroschein@stthomas.edu
January 2022
"""

import os, sys
import atexit
import time
import matplotlib.pyplot as plt
import numpy as np

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

from interfaces.interfaces import FPGA
from interfaces.boards import Daq
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from interfaces.utils import to_voltage

# --- Variables ---
pwr_setup = '3dual'

# --- Instantiations ---
f = FPGA(bitfile=top_level_module_bitfile)
f.init_device()
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)  # 7V and +/-16.5V, None
daq = Daq(fpga=f)
pwr = Daq.Power(f)
gpio = Daq.GPIO(f)

# --- Configure and turn on power supplies ---
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)
dc_pwr.set("out_state", "ON", configs={"chan": 1})  # +7V
for ch in [2, 3]:
    dc_pwr.set("out_state", "ON", configs={"chan": ch})  # +/- 16.5V

# Turn off power at exit
atexit.register(pwr_off, [dc_pwr])


# --- Set up FPGA ---
pwr.all_off()
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

# --- Set up GPIO ---
# gpio.fpga.debug = True
gpio.spi_debug('ds1')

# --- Testing ---
ads8686_chan_a = 7
ads8686_chan_b = 3
z, f = daq.test_impedance(frequency=1000.0, resistance=9843, amplitude=1.0, dac80508_num=2, dac80508_chan=7, ads8686_chan_a=ads8686_chan_a, ads8686_chan_b=ads8686_chan_b, plot=False)
print(z, f)
print(f'{np.abs(z)}\N{ANGLE}{np.angle(z, deg=True)}\N{DEGREE SIGN}')

# --- Graph incoming data ---
# Initial data
# row_plots = 3
# col_plots = 3
# fig, axes = plt.subplots(row_plots, col_plots)
# for i in range(row_plots):
#     for j in range(col_plots):
#         data = [to_voltage(data=int(x), num_bits=16, voltage_range=10, use_twos_comp=True) for x in daq.ADC_gp.stream_mult(twos_comp_conv=False)['B']]
#         ax = axes[i, j]
#         ax.set_xlabel('Time')
#         ax.set_ylabel('Voltage')
#         ax.plot(data[::8])
# plt.show()

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
    data_stream = daq.ADC_gp.stream_mult(twos_comp_conv=False)
    v_in = to_voltage(data=data_stream['A'], num_bits=16, voltage_range=10, use_twos_comp=True)
    v_out = to_voltage(data=data_stream['B'], num_bits=16, voltage_range=10, use_twos_comp=True)
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
