# AD7961 tests; test pattern and data saved to file
import logging
import sys
import os
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
from instrbuilder.instrument_opening import open_by_name
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

from interfaces.interfaces import AD7961, AD5453, FPGA, Endpoint, disp_device, advance_endpoints_bynum
from interfaces.boards import Daq
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
eps = Endpoint.endpoints_from_defines

today = datetime.datetime.today()
data_dir = '/Users/koer2434/Google Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/ad7961/{}{}{}'.format(today.year,
                                                                                                                   today.month,
                                                                                                                   today.day)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply()
atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2)
# turn on the 7V in, but keep +/-16.6 down
dc_pwr.set('out_state', 'ON', configs={'chan': 1})
# turn on the +/-16.5 V input
for ch in [1, 2]:
    dc_pwr2.set('out_state', 'ON', configs={'chan': ch})
######################################
time.sleep(2)

# --------  function generator  --------
fg = open_by_name('new_function_gen')

fg.set('load', 'INF')
fg.set('offset', 2)
fg.set('v', 2)
fg.set('freq', 10e3)
fg.set('output', 'ON')

atexit.register(fg.set, 'output', 'OFF')
######################################

# --------  Set up FPGA  --------
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

# power supply turn on via FPGA enables
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    time.sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug('dfast0')
gpio.ads_misc('sdoa')  # do not care for this experiment

# --------  ADC instances  --------
AD7961_CHANS = 4
ad7961s = AD7961.create_chips(fpga=f, number_of_chips=AD7961_CHANS)

# --------  Run ADC tests  --------
for chan in [0, 1]:
    for num in [1, 2, 3]:
        if chan == 0:
            setup = ad7961s[chan].setup(reset_pll=True)  # resets FIFO and ADC controller
        else:
            setup = ad7961s[chan].setup(reset_pll=False)  # resets FIFO and ADC controller

        d1 = ad7961s[chan].stream_mult(swps=4, twos_comp_conv=False)
        ad7961s[chan].power_up_adc()  # standard sampling
        time.sleep(1)
        ad7961s[chan].reset_fifo()

        d2 = ad7961s[chan].stream_mult(swps=4)
        with open(os.path.join(data_dir,
                               'test_data_chan{}_num{}.npy'.format(chan, num)), 'wb') as file1:
            np.save(file1, d2)


def stream_plot(adc, swps=4, name=None):
    adc.reset_fifo()
    d = adc.stream_mult(swps=swps)
    plt.figure()
    plt.plot(d)
    if name is not None:
        plt.title(name)
    print('ADC data: min = {}, max={}, avg={}'.format(np.min(d),
                                                      np.max(d),
                                                      np.average(d)))
    return d


def save_array(d, chan, test_name='test', number=1):
    with open(os.path.join(data_dir,
                           '{}_ch{}_num{}.npy'.format(test_name, chan, number)),
                           'wb') as file1:

        np.save(file1, d)

fdac = []
for i in range(6):
    fdac.append(AD5453(f,
                endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('AD5453'),i),
                channel=i))
    fdac[i].set_spi_sclk_divide()
    fdac[i].set_data_mux('ad7961_ch0')
    # fdac[i].write_filter_coeffs()
    # fdac[i].write(0x2000)
    fdac[i].set_clk_divider()  # default value is 0xA0 (expect 1.25 MHz, getting 250 kHz, set by SPI SCLK??)

c1, c2 = fdac[0].read_coeff_debug()
