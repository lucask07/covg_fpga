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
import matplotlib.pyplot as plt

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


def check_readback(data_array, adc_data, chan):
    """
    data_array: dict of arrays written to DDR (keys are 0,1,2,3,...)
    adc_data: dict of arrays written to DDR
    chan: int or list of ints for channels to check
    """
    results = {}
    for c in list(chan):
        diffs = data_array[c][0:len(adc_data[c])] != adc_data[c]
        print('Chan {} number of diffs. {}'.format(c,
                                                   np.sum(diffs)))
        results[c] = diffs
    return results

# Set up FPGA
if 'f' not in locals():  # run script with %run -i to pass workspace variables back in
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

# the index is the DDR address that the circular buffer stops at.
# need to write all the way up to this stoping point otherwise the SPI output will glitch

port1_index = 0x7_ff_ff_f8
ddr.set_index(port1_index,
              int(port1_index*2))
ddr.parameters['sample_size'] = int( (port1_index + 8)/2)

fdac = []
for i in range(6):
    fdac.append(AD5453(f,
                endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('AD5453'),i),
                channel=i))
    fdac[0].set_spi_sclk_divide()
    fdac[i].set_data_mux('DDR')

    ddr.reset_fifo()
    time.sleep(0.001)
    fdac[i].set_clk_divider()  # default value is 0xA0 (expect 1.25 MHz, getting 250 kHz, set by SPI SCLK??)

    # sin_buf = ddr.write_sin_wave(amplitude=2, frequency=10e3, dignum_volt=546)

    #t, ddr.data_arrays['chan{}'.format(i)] = ddr.make_flat_voltage(256 + 256*i)
    # t, ddr.data_arrays['chan{}'.format(i)] = ddr.make_sin_wave(amplitude=1+i*0.25,
    #                                                           frequency=10e3,
    #                                                           dignum_volt=546)
ddr.reset_fifo()
for i in range(6):
    ddr.data_arrays[i] = ddr.make_ramp(start=0 + 64*i,
                                        stop=2**16-1,
                                        step=1)
for i in [6, 7]:
    ddr.data_arrays[i] = ddr.make_ramp(start=0 + 64*i,
                                        stop=2**16-1,
                                        step=1)
# flat_len = 183
# for i in [0]:
#     for t in np.arange(64):
#         ddr.data_arrays['chan{}'.format(i)][0 + flat_len*t:flat_len + flat_len*t] = np.uint16(240*(t+1)*np.ones(flat_len))


ddr.reset_fifo()
ddr.clear_fg_read()
g_buf = ddr.write_channels()

ddr.reset_fifo()
ddr.clear_write()
fdac[0].set_clkenable_mux('spi_clk_en')  # shared between all DACs (only need to set one channel)
ddr.set_read()
time.sleep(0.5)  # allow the ADC data to accumulate into DDR
#ddr.clear_read()
ddr.set_fg_read()

# block size is 2048. So expect 2048*4*128*128 bytes read (128 MB)
t, bytes_read = ddr.read_adc(ddr.parameters['BLOCK_SIZE']*128*16)  # bits 0:63 of the DDR, first 4 channels of the FDAC
# t, bytes_read = ddr.read(8192)  # bits 0:63 of the DDR, first 4 channels of the FDAC

d = np.frombuffer(t, dtype=np.uint8).astype(np.uint32)
chan_data_swz = {}  # this data is swizzled
for i in range(4):
    chan_data_swz[i] = (d[(0 + i*2)::8] << 0) + (d[(1 + i*2)::8] << 8)

chan_data = {}
chan_data[0] = chan_data_swz[2]
chan_data[1] = chan_data_swz[3]
chan_data[2] = chan_data_swz[0]
chan_data[3] = chan_data_swz[1]

for i in range(4):
    plt.plot(chan_data[i], marker='*')

# check readback with write by channel given length
readback = check_readback(ddr.data_arrays, chan_data, [0, 1, 2, 3])

"""
# Continuous Graph
plt.ion()
fig, ax = plt.subplots()
# ax.plot(data)
ax.set_xlabel('Time')
ax.set_ylabel('Voltage')
while True:
    for i in range(2):
        data = [to_voltage(data=int(x), num_bits=16, voltage_range=10, use_twos_comp=True) for x in ads.stream_mult(twos_comp_conv=False)['A']]
        x = [i*len(data) + j for j in range(len(data))]
        ax.plot(x, data, color='blue', scalex=True, scaley=False)
        ax.set_ylim(bottom=-5, top=5, auto=False)
    plt.draw()
    plt.pause(0.01)
    plt.cla()
"""

"""
(unique, counts) = np.unique((d[0::2] << 0) + (d[1::2] << 8),
                             return_counts=True)

"""
