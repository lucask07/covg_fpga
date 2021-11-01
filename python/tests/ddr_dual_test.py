""" Test of DDR3 with two writing FIFOs and two reading FIFOs
Does not require the DAQ v2 PCB
Nov 2021

Lucas Koerner, koer2434@stthomas.edu

"""
import logging
import sys
import os
import time
import datetime
import numpy as np
import atexit
# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == 'covg_fpga':
        interfaces_path = os.path.join(covg_fpga_path, 'python')
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(interfaces_path)

from interfaces.interfaces import Endpoint, advance_endpoints_bynum
from interfaces.interfaces import FPGA, AD5453
from interfaces.interfaces import DebugFIFO, DDR3, disp_device
eps = Endpoint.endpoints_from_defines
from interfaces.boards import Daq  # TODO: should I instantiate the Daq board or just pieces from it?
                                   # TODO: for now, pieces, eventually the DAQ board

# Set up FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset


gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug('ads')
gpio.ads_misc('sdoa')

ddr = DDR3(f)
ddr.reset_fifo()
ddr.set_index(int(ddr.parameters['sample_size']/8),
              int(ddr.parameters['sample_size']))
flat_buf = ddr.write_flat_voltage(600)  # input is digital code

fdac = []
for i in range(6):
    fdac.append(AD5453(f,
                endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('AD5453'),i),
                channel=i))
    fdac[0].set_spi_sclk_divide()
    fdac[i].set_data_mux('DDR')
    fdac[i].write(0x2000)
    t, ddr.data_arrays['chan{}'.format(i)] = ddr.make_flat_voltage(256 + 256*i)

fdac[i].set_clk_divider()  # default value is 0xA0 (expect 1.25 MHz, getting 250 kHz, set by SPI SCLK??)
g_buf = ddr.write_channels()


ddr.clear_write()
ddr.set_read()

t, bytes_read = ddr.read_adc()

"""
fifo_debug = DebugFIFO(f)
fifo_debug.reset_fifo()
dt = fifo_debug.stream_mult(swps=4, twos_comp_conv=False)
"""
