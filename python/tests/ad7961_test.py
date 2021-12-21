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

plt.ion()

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

from interfaces.interfaces import AD7961, FPGA, Endpoint, disp_device
from interfaces.boards import Daq
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
eps = Endpoint.endpoints_from_defines

today = datetime.datetime.today()
data_dir = '/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/ad7961/{}{}{}'.format(today.year,
                                                                                                                   today.month,
                                                                                                                   today.day)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

pwr_setup = '3dual'
# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)
atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup)
# turn on the 7V in, but keep +/-16.6 down
dc_pwr.set('out_state', 'ON', configs={'chan': 1})


# turn on the +/-16.5 V input
if pwr_setup != '3dual':
    # turn on the +/-16.5 V input
    for ch in [1, 2]:
        dc_pwr2.set('out_state', 'ON', configs={'chan': ch})
elif pwr_setup == '3dual':
    # turn on the +/-16.5 V input  # TODO: do we set the negative supply to positive or negative?
    for ch in [2, 3]:
        dc_pwr.set('out_state', 'ON', configs={'chan': ch})

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

# --------  ADC instances  --------
ADC_TEST_PATTERN = False
AD7961_CHANS = 4
ad7961s = AD7961.create_chips(fpga=f, number_of_chips=AD7961_CHANS)
test_channel = 1

# --------  Run ADC tests  --------
for chan in [0, test_channel]:
    for num in [1, 2, 3]:
        if chan == 0:
            setup = ad7961s[chan].setup(reset_pll=True)  # resets FIFO and ADC controller
            time.sleep(0.2)  # this pause is required. Failed at 100 ms.
        else:
            setup = ad7961s[chan].setup(reset_pll=False)  # resets FIFO and ADC controller
            time.sleep(0.2) # this pause is required. Failed at 100 ms.

        if ADC_TEST_PATTERN:
            ad7961s[chan].test_pattern()
            time.sleep(0.2)
            ad7961s[chan].reset_fifo()
            time.sleep(0.2)  # FIFO fills in 204 us
            d1 = ad7961s[chan].stream_mult(swps=4, twos_comp_conv=False)
            with open(os.path.join(data_dir,
                                   'test_pattern_chan{}_num{}.npy'.format(chan, num)), 'wb') as file1:
                np.save(file1, d1)

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
