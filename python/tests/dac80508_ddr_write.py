import os, sys
import time
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
                                        'fpga_XEM7310.runs', 'impl_1',
                                        'top_level_module.bit')

from interfaces.interfaces import DDR3, FPGA, DAC80508
from interfaces.boards import Daq
from interfaces.utils import to_voltage, from_voltage
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply


# --- Variables ---
pwr_setup = '3dual'
num_fast_dacs = 6
num_slow_dacs = 2
dac_out_channel = 0


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
pwr.all_off()
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

# --- Set up GPIO ---
# gpio.fpga.debug = True
gpio.spi_debug('ds0')

# --- Configure for DDR read to DAC80508 ---
dac2.set_spi_sclk_divide(0x8)
dac2.set_ctrl_reg(0x3218)
dac2.set_config_bin(0x00)
dac2.set_data_mux('DDR')

# --- Write to the DDR ---
# [0:13]    FDAC_1 [14:15] ADDR SDAC_1
# [16:29]   FDAC_2 [31:32] ADDR SDAC_1 and SDAC_2
# [32:45]   FDAC_3 [46:47] ADDR SDAC_2
# [48:61]   FDAC_4 [62:63] 0's
# [64:77]   FDAC_5 [78:79] 0's
# [80:93]   FDAC_6 [94:95] 0's
# [96:111]  SDAC_1
# [112:127] SDAC_2

# For now, we are only going to write to DAC OUT 0 on the SDAC (DAC80508) so we don't have to worry about the address bits

# FDAC: 5V; SDAC: 2.5V
# Data for the 6 AD5453 "Fast DACs"
for i in range(6):
    ddr.data_arrays[i] = ddr.make_flat_voltage(5)
# Data for the 2 DAC80508 "Slow DACs"
for i in range(2):
    ddr.data_arrays[i + 6] = ddr.make_flat_voltage(5)

g_buf = ddr.write_channels()

input()

# FDAC: 5V 1KHz sine wave; SDAC: 1V 1KHz sine wave
# Data for the 6 AD5453 "Fast DACs"
for i in range(6):
    ddr.data_arrays[i] = ddr.make_sine_wave(amplitude=5, frequency=1000.0)
# Data for the 2 DAC80508 "Slow DACs"
for i in range(2):
    ddr.data_arrays[i + 6] = ddr.make_sine_wave(amplitude=2.5, frequency=1000.0)