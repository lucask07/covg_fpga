""" Test of DDR3 with two writing FIFOs and two reading FIFOs
Does not require the DAQ v2 PCB
Nov 2021

Lucas Koerner, koer2434@stthomas.edu

"""
from interfaces.boards import Daq  # TODO: should I instantiate the Daq board or just pieces from it?
from interfaces.interfaces import DDR3, disp_device
from interfaces.interfaces import FPGA, AD5453
from interfaces.interfaces import Endpoint, advance_endpoints_bynum
import matplotlib
from filters.filter_tools import delayseq
import logging
import sys
import os
import time
import datetime
import numpy as np
import atexit
import matplotlib.pyplot as plt
import h5py
from scipy import signal

matplotlib.use("Qt4agg")  # or "Qt5agg" depending on you version of Qt


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

eps = Endpoint.endpoints_from_defines
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

fdac = []
for i in range(6):
    fdac.append(AD5453(f,
                endpoints=advance_endpoints_bynum(
                    Endpoint.get_chip_endpoints('AD5453'), i),
                channel=i))
    fdac[0].set_spi_sclk_divide()
    fdac[i].set_data_mux('DDR')

    ddr.reset_fifo()
    time.sleep(0.001)

# default value is 0xA0 (expect 1.25 MHz, getting 250 kHz, set by SPI SCLK??)
fdac[0].set_clk_divider(divide_value=0x50)

# sin_buf = ddr.write_sine_wave(amplitude=2, frequency=10e3, dignum_volt=546)

#t, ddr.data_arrays['chan{}'.format(i)] = ddr.make_flat_voltage(256 + 256*i)
# t, ddr.data_arrays['chan{}'.format(i)] = ddr.make_sine_wave(amplitude=1+i*0.25,
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

ddr.data_arrays[2], actual_frequency = ddr.make_sine_wave(amplitude=2**14,
                                                          frequency=500, offset=2**15,
                                                          actual_frequency=False)

# flat_len = 183
# for i in [0]:
#     for t in np.arange(64):
#         ddr.data_arrays['chan{}'.format(i)][0 + flat_len*t:flat_len + flat_len*t] = np.uint16(240*(t+1)*np.ones(flat_len))


ddr.reset_fifo()
ddr.set_adc_debug()  # TODO: this routes DACs and a counter to DDR rather than ADCs
ddr.clear_adc_read()
g_buf = ddr.write_channels(SET_READ=False)

ddr.reset_fifo()
ddr.clear_write()
fdac[0].set_data_mux('DDR')
fdac[1].set_data_mux('DDR')

ddr.set_read()
time.sleep(0.5)  # allow the ADC data to accumulate into DDR
#ddr.clear_read()
ddr.set_adc_read()


def read_adc(ddr, blk_multiples=2048):
    # block size is 2048.
    # bits 0:63 of the DDR, first 4 channels of the
    t, bytes_read = ddr.read_adc(
        sample_size=ddr.parameters['BLOCK_SIZE']*blk_multiples)
    d = np.frombuffer(t, dtype=np.uint8).astype(np.uint32)
    return d


def deswizzle(d):
    chan_data_swz = {}  # this data is swizzled
    for i in range(4):
        chan_data_swz[i] = (d[(0 + i*2)::8] << 0) + (d[(1 + i*2)::8] << 8)

    chan_data = {}
    chan_data[0] = chan_data_swz[2]
    chan_data[1] = chan_data_swz[3]
    chan_data[2] = chan_data_swz[0]
    chan_data[3] = chan_data_swz[1]

    return chan_data


"""
plt_length = 2048
for i in range(4):
    plt.plot(chan_data[i][0:plt_length], marker='*', label=f'Ch:{i}')

# check readback with write by channel given length
readback = check_readback(ddr.data_arrays, chan_data, [0, 1, 2, 3])
"""

# Continuous Graph
plt.ion()
fig, ax = plt.subplots()
# ax.plot(data)
ax.set_xlabel('Time')
ax.set_ylabel('DN')
repeat = 0
sample_rate = 1/5e6
blk_multiples = 1024
chunk_size = int(ddr.parameters['BLOCK_SIZE']*blk_multiples/8)
num_repeats = 8

path = 'out.h5'
try:
    os.remove(path)
except OSError:
    pass

# Save ADC DDR data to a file
with h5py.File('out.h5', 'a') as file:
    data_set = file.create_dataset('adc', (4, chunk_size), maxshape=(4, None))
    while repeat < num_repeats:
        d = read_adc(ddr, blk_multiples)
        chan_data = deswizzle(d)
        chan_stack = np.vstack(
            (chan_data[0], chan_data[1], chan_data[2], chan_data[3]))
        if repeat == 0:
            t = np.arange(len(chan_data[1]))*sample_rate
        ax_hdl = ax.plot(
            t, chan_data[1], color='blue', scalex=True, scaley=False)
        ax.set_ylim(bottom=0, top=2**16, auto=False)
        plt.draw()
        plt.pause(0.001)
        repeat += 1
        if repeat == 0:
            data_set[:] = chan_stack
        else:
            data_set[:, -chunk_size:] = chan_stack
        if repeat < num_repeats:
            ax_hdl[0].remove()
            data_set.resize(data_set.shape[1] + chunk_size, axis=1)


# Post processing: read in h5 data and plot
fig, ax = plt.subplots()
file = h5py.File('out.h5', 'r')
list(file.keys())  # this returns adc
dset = file['adc']
t = np.arange(len(dset[0, :]))*sample_rate
for i in range(4):
    ax.plot(t, dset[i, :], label=f'Ch: {i}')
ax.legend()
ax.set_xlabel('Time')
ax.set_ylabel('DN')
