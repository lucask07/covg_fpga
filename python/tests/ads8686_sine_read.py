import os, sys
import time
import matplotlib.pyplot as plt
import atexit

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
                                        'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit')

from interfaces.interfaces import FPGA, ADS8686
from interfaces.boards import Daq
from interfaces.utils import to_voltage
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply


# Setup
f = FPGA(bitfile=top_level_module_bitfile)
pwr = Daq.Power(f)
ads = ADS8686.create_chips(fpga=f, number_of_chips=1)[0]
data_list = []
row_plots = 3
col_plots = 3
pwr_setup = '3dual'

if not f.init_device():
    exit()

# --- Configure and turn on power supplies ---
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)  # 7V and +/-16.5V, None
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)
dc_pwr.set("out_state", "ON", configs={"chan": 1})  # +7V
for ch in [2, 3]:
    dc_pwr.set("out_state", "ON", configs={"chan": ch})  # +/- 16.5V

# Turn off power at exit
atexit.register(pwr_off, [dc_pwr])

pwr.all_off()
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(5)
ads.set_lpf(376)
codes = ads.setup_sequencer(chan_list=[('FIXED', '4')])
ads.write_reg_bridge()
ads.set_fpga_mode()


# Initial Graph
# fig, axes = plt.subplots(row_plots, col_plots)
# for i in range(row_plots):
#     for j in range(col_plots):
#         data = [to_voltage(data=int(x), num_bits=16, voltage_range=10, use_twos_comp=True) for x in ads.stream_mult(twos_comp_conv=False)['B']]
#         ax = axes[i, j]
#         ax.set_xlabel('Time')
#         ax.set_ylabel('Voltage')
#         ax.plot(data)
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
    data = [to_voltage(data=int(x), num_bits=16, voltage_range=10, use_twos_comp=True) for x in ads.stream_mult(twos_comp_conv=False)['B']]
    x = [len(data) + j for j in range(len(data))]
    ax.plot(x, data, color='blue', scalex=True, scaley=False)
    ax.set_ylim(bottom=-5, top=5, auto=False)
    plt.draw()
    plt.pause(0.01)
    plt.cla()
