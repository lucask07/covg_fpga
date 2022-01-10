from math import ceil
from instrbuilder.instrument_opening import open_by_name
import os, sys
import time
import atexit

# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
cwd = os.getcwd()
if 'covg_fpga' in cwd:
    covg_fpga_index = cwd.index('covg_fpga')
    covg_fpga_path = cwd[:covg_fpga_index + len('covg_fpga') + 1]
else:
    print(
        'covg_fpga folder not found. Please navigate to the covg_fpga folder.')
    assert False
interfaces_path = os.path.join(covg_fpga_path, 'python')
sys.path.append(interfaces_path)

top_level_module_bitfile = os.path.join(covg_fpga_path, 'fpga_XEM7310',
                                        'fpga_XEM7310.runs', 'impl_1',
                                        'top_level_module.bit')

from interfaces.interfaces import DDR3, FPGA, DAC80508
from interfaces.boards import Daq
from interfaces.utils import to_voltage, from_voltage


# --- Instantiations ---
f = FPGA(bitfile=top_level_module_bitfile)
dc_pwr = open_by_name(name='rigol_pwr1')  # 7V in
dc_pwr2 = open_by_name(name='rigol_ps2')  # +/-16.5V -> needed for REFDIV going to Op-Amp bufferspwr = Daq.Power(f)
pwr = Daq.Power(f)
gpio = Daq.GPIO(f)
ddr = DDR3(fpga=f)
dac = DAC80508(fpga=f)
num_fast_dacs = 6
num_slow_dacs = 2
dac_out_channel = 0


# --- Set up power supplies ---
def pwr_off():
    for ch in [1, 2, 3]:
        dc_pwr.set('out_state', 'OFF', configs={'chan': ch})
    for ch in [1, 2, 3]:
        dc_pwr2.set('out_state', 'OFF', configs={'chan': ch})

# Channel 1 on supply1 for Vin
dc_pwr.set('i', 0.55, configs={'chan': 1})
dc_pwr.set('v', 7, configs={'chan': 1})
dc_pwr.set('ovp', 7.2, configs={'chan': 1})
dc_pwr.set('ocp', 0.75, configs={'chan': 1})
dc_pwr.set('out_state', 'ON', configs={'chan': 1})

# Channel 1 and 2 setup
for ch in [1, 2]:
    dc_pwr2.set('i', 0.39, configs={'chan': ch})
    dc_pwr2.set('v', 16.5, configs={'chan': ch})
    dc_pwr2.set('ovp', 16.7, configs={'chan': ch})
    dc_pwr2.set('ocp', 0.400, configs={'chan': ch})
    dc_pwr2.set('out_state', 'ON', configs={'chan': ch})

# Turn off power at exit
atexit.register(pwr_off)


# --- Set up FPGA ---
f.init_device()
pwr.all_off()
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

# --- Set up GPIO ---
gpio.fpga.debug = True
gpio.spi_debug('ds0')

# --- Configure for DDR read to DAC80508 ---
dac.set_spi_sclk_divide(0x8)
dac.set_ctrl_reg(0x3218)
dac.set_config_bin(0x00)
dac.set_data_mux('DDR')
# Need byte index value
ddr.set_index(ddr.parameters['sample_size']) # For now set the sample size and index the same.
# TODO: figure out what the index needs to be in a general form

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
# Data for the 6 AD5453 "Fast DACs"
for i in range(6):
    t, ddr.data_arrays[f'chan{i}'] = ddr.make_flat_voltage(from_voltage(voltage=5, num_bits=14, voltage_range=10, with_negatives=False))
# Data for the 2 DAC80508 "Slow DACs"
for i in range(2):
    t, ddr.data_arrays[f'chan{i}'] = ddr.make_flat_voltage(
        from_voltage(voltage=2.5,
                     num_bits=16,
                     voltage_range=2.5,
                     with_negatives=False))

g_buf = ddr.write_channels()