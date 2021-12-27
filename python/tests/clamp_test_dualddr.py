"""Test of the clamp board (v1), initial bring-up for biophys society meeting
   data
December 2021

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu

TODO: connect CC using 6.8 kOhm

"""

from interfaces.boards import Daq, Clamp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
import logging
from interfaces.interfaces import FPGA, AD5453, Endpoint, disp_device, DAC80508, AD7961, disp_device, DDR3, advance_endpoints_bynum, TCA9555
import os
import sys
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
import h5py


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

today = datetime.datetime.today()
data_dir = '/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp_test/{}{}{}'.format(today.year,
                                                                                                                   today.month,
                                                                                                                   today.day)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

pwr_setup = '3dual'
dc_num = 0  # the Daughter-card channel under test. Channel order on DAQ board from L to R: 1,0,2,3

# encoding was added as an option at Python 3.9
# logging.basicConfig(filename='DAC53401_test.log',
#                     encoding='utf-8', level=logging.INFO)

# alternative for Python<3.9
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler('DAC53401_test.log', 'w', 'utf-8')
root_logger.addHandler(handler)

# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)
if pwr_setup == '3dual':
    atexit.register(pwr_off, [dc_pwr])
else:
    atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup)

# turn on the 7V
dc_pwr.set('out_state', 'ON', configs={'chan': 1})

if pwr_setup != '3dual':
    # turn on the +/-16.5 V input
    for ch in [1, 2]:
        dc_pwr2.set('out_state', 'ON', configs={'chan': ch})
elif pwr_setup == '3dual':
    # turn on the +/-16.5 V input
    for ch in [2, 3]:
        dc_pwr.set('out_state', 'ON', configs={'chan': ch})

# ------ oscilloscope -----------------
osc = open_by_name('msox_scope')


# --------  function generator  --------
fg = open_by_name('new_function_gen')

fg.set('load', 'INF')
fg.set('offset', 2)
fg.set('v', 2)
fg.set('freq', 10e3)
fg.set('output', 'ON')

atexit.register(fg.set, 'output', 'OFF')

# Initialize FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables


AD7961_CHANS = 4
ad7961s = AD7961.create_chips(fpga=f, number_of_chips=AD7961_CHANS)
for i in range(4):
    ad7961s[i].chan = i

ad7961s[0].reset_wire(1)
for chan in range(4):
    ad7961s[chan].power_down_adc()

# power supply turn on via FPGA enables
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug('dfast1')
gpio.ads_misc('sdoa')  # do not care for this experiment

# # instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamp = Clamp(f, dc_num=dc_num)

clamp.init_board()

disp_device(clamp.TCA[0])
disp_device(clamp.TCA[1])
disp_device(clamp.UID)
disp_device(clamp.DAC)

# configure the clamp board, settings default to None so that a setting that is not
# included is masked and stays the same
# TODO: configure_clamp errors out if not connected

log_info = clamp.configure_clamp(ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2', CCOMP=4.7,
                                 RF1=2.1, ADG_RES=10, PClamp_CTRL=0, P1_E_CTRL=0, P1_CAL_CTRL=0,
                                 P2_E_CTRL=0, P2_CAL_CTRL=0, gain=1, FDBK=1, mode='voltage',
                                 EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110, addr_pins_2=0b000)


# test_channel = 1
# ADC_TEST_PATTERN = False
# d1 = {}
# d2 = {}
# --------  Run ADC tests  --------
# for chan in [1, 1]:
#     for num in [1, 2, 3]:
#         if chan == 12:
#             # resets FIFO and ADC controller
#             setup = ad7961s[chan].setup(reset_pll=True)
#             time.sleep(0.2)  # this pause is required. Failed at 100 ms.
#         else:
#             # resets FIFO and ADC controller
#             setup = ad7961s[chan].setup(reset_pll=False)
#             time.sleep(0.2)  # this pause is required. Failed at 100 ms.
#
#         if ADC_TEST_PATTERN:
#             ad7961s[chan].test_pattern()
#             time.sleep(0.2)
#             ad7961s[chan].reset_fifo()
#             time.sleep(0.2)  # FIFO fills in 204 us
#             d1[chan] = ad7961s[chan].stream_mult(swps=4, twos_comp_conv=False)
#             with open(os.path.join(data_dir,
#                                    'test_pattern_chan{}_num{}.npy'.format(chan, num)), 'wb') as file1:
#                 np.save(file1, d1)
#
#         ad7961s[chan].power_up_adc()  # standard sampling
#         time.sleep(1)
#         ad7961s[chan].reset_fifo()
#         d2[chan] = ad7961s[chan].stream_mult(swps=4)
#
#         with open(os.path.join(data_dir,
#                                'test_data_chan{}_num{}.npy'.format(chan, num)), 'wb') as file1:
#             np.save(file1, d2)

test_channel = 1
ADC_TEST_PATTERN = False
d1 = {}
d2 = {}

chan = 0
ad7961s[chan].reset_wire(1)
ad7961s[chan].reset_pll()
time.sleep(1)
pll_cnt = 0
while not ad7961s[chan].get_pll_status():
    time.sleep(0.01)
    pll_cnt += 1
    if pll_cnt > 20:
        print('PLL lock timeout')

for chan in range(4):
    ad7961s[chan].power_up_adc()
ad7961s[0].reset_wire(0)

fifo_status = {}
for chan in range(4):
    fifo_status[chan] = ad7961s[chan].reset_fifo()
    d2[chan] = ad7961s[chan].stream_mult(swps=4)

num = 0
with open(os.path.join(data_dir,
                       'test_data_chan{}_num{}.npy'.format(chan, num)), 'wb') as file1:
    np.save(file1, d2)

# disp_device(ad7961s[0])

daq = Daq(f)

# fast DAC channel 0 and 1
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation='clear')
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux('host')
    daq.DAC[i].change_filter_coeff(target='passthru')
    daq.DAC[i].write_filter_coeffs()

# 0xA0 = 1.25 MHz, 0x50 = 2.5 MHz
daq.DAC[0].set_clk_divider(divide_value=0x50)

daq.TCA[0].configure_pins([0, 0])
daq.TCA[0].write(((0xf) << (4+8)) + 0xfff)

# DAC channel 1 on the DAQ board is connected to dc clamp ch 0 CMD signal
cmd_dac = daq.DAC[1]
cc = daq.DAC[0]

# ADC streaming still works to here
ddr = DDR3(f)
ddr.reset_fifo()

if 0:

    for i in range(8):
        ddr.data_arrays[i] = ddr.make_step(low=0x2000,
                                           high=0x2800,
                                           length=10000)

    ddr.clear_adc_read()
    ddr.clear_adc_debug()  # TODO: this routes DACs and a counter to DDR rather than ADCs
    g_buf = ddr.write_channels()
    ddr.reset_fifo()
    ddr.clear_write()
    ddr.set_read()
    time.sleep(0.5)  # allow the ADC data to accumulate into DDR
    ddr.set_adc_read()

    cmd_dac.set_data_mux('DDR')

    cc.set_data_mux('host')
    cc.write(int(0))

    cc.change_filter_coeff(target='passthru')
    cc.filter_select(operation='set')
    cc.set_data_mux('ad7961_ch0')
    cc.set_data_mux('DDR')
    # ADC streaming works up to here. Except channel 0 is all 0s

    def read_adc(ddr, blk_multiples=2048):
        # block size is 2048.
        # bits 0:63 of the DDR, first 4 channels of the
        t, bytes_read = ddr.read_adc(  # just reads from the block pipe out
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
    blk_multiples = 64
    chunk_size = int(ddr.parameters['BLOCK_SIZE']*blk_multiples/8)
    num_repeats = 4

    data_name = 'out_clamp.h5'
    full_data_name = os.path.join(data_dir, data_name)
    try:
        os.remove(data_name)
    except OSError:
        pass

    # Save ADC DDR data to a file
    with h5py.File(data_name, 'a') as file:
        data_set = file.create_dataset(
            'adc', (4, chunk_size), maxshape=(4, None))
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
    file = h5py.File(data_name, 'r')
    list(file.keys())  # this returns adc
    dset = file['adc']
    t = np.arange(len(dset[0, :]))*sample_rate
    for i in range(4):
        ax.plot(t, dset[i, :], label=f'Ch: {i}')
    ax.legend()
    ax.set_xlabel('Time')
    ax.set_ylabel('DN')

    # TODO - a way to assign parts of the Daq TCAs to specific DACs so as to write the gain
    # slow DAC: DAC1_BP_OUT4 -- utility pin, replacing I2C DAC on daughter card
