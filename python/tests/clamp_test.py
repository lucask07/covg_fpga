"""Test of the clamp board (v1), initial bring-up for biophys society meeting
   data
December 2021

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu

TODO: connect CC using 6.8 kOhm

"""

import os, sys
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
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

from interfaces.interfaces import FPGA, AD5453, Endpoint, disp_device, DAC80508, AD7961, disp_device, DDR3, advance_endpoints_bynum, TCA9555
import logging
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from interfaces.boards import Daq, Clamp
eps = Endpoint.endpoints_from_defines

today = datetime.datetime.today()
data_dir = '/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/ad7961/{}{}{}'.format(today.year,
                                                                                                                   today.month,
                                                                                                                   today.day)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

pwr_setup = '3dual'
dc_num = 0  # the Daughter-card channel under test. Order on board from L to R: 1,0,2,3

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
    # turn on the +/-16.5 V input  # TODO: do we set the negative supply to positive or negative?
    for ch in [2, 3]:
        dc_pwr.set('out_state', 'ON', configs={'chan': ch})

# ------ oscilloscope -----------------
osc = open_by_name('msox_scope')


# Initialize FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

# power supply turn on via FPGA enables
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug('dfast1')
gpio.ads_misc('sdoa')  # do not care for this experiment

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamp = Clamp(f, dc_num=dc_num)

clamp.init_board()

disp_device(clamp.TCA[0])
disp_device(clamp.TCA[1])
disp_device(clamp.UID)
disp_device(clamp.DAC)

# configure the clamp board, settings default to None so that a setting that is not
# included is masked and stays the same
# TODO: configure_clamp errors out if not connected

# log_info = clamp.configure_clamp(ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2', CCOMP=4.7,
#                            RF1=2.1,ADG_RES=10, PClamp_CTRL=0, P1_E_CTRL=0, P1_CAL_CTRL=0,
#                            P2_E_CTRL=0, P2_CAL_CTRL=0, gain=1, FDBK=1, mode='voltage',
#                            EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110, addr_pins_2=0b000)

# log_info = clamp.configure_clamp(P2_E_CTRL=0, addr_pins_1=0b110, addr_pins_2=0b000)

AD7961_CHANS = 4
ad7961s = AD7961.create_chips(fpga=f, number_of_chips=AD7961_CHANS)
test_channel = 1
ADC_TEST_PATTERN = False

# --------  Run ADC tests  --------
# for chan in [0, test_channel]:
#     for num in [1, 2, 3]:
#         if chan == 0:
#             setup = ad7961s[chan].setup(reset_pll=True)  # resets FIFO and ADC controller
#             time.sleep(0.2)  # this pause is required. Failed at 100 ms.
#         else:
#             setup = ad7961s[chan].setup(reset_pll=False)  # resets FIFO and ADC controller
#             time.sleep(0.2) # this pause is required. Failed at 100 ms.
#
#         if ADC_TEST_PATTERN:
#             ad7961s[chan].test_pattern()
#             time.sleep(0.2)
#             ad7961s[chan].reset_fifo()
#             time.sleep(0.2)  # FIFO fills in 204 us
#             d1 = ad7961s[chan].stream_mult(swps=4, twos_comp_conv=False)
#             with open(os.path.join(data_dir,
#                                    'test_pattern_chan{}_num{}.npy'.format(chan, num)), 'wb') as file1:
#                 np.save(file1, d1)
#
#         ad7961s[chan].power_up_adc()  # standard sampling
#         time.sleep(1)
#         ad7961s[chan].reset_fifo()
#         d2 = ad7961s[chan].stream_mult(swps=4)
#
#         with open(os.path.join(data_dir,
#                                'test_data_chan{}_num{}.npy'.format(chan, num)), 'wb') as file1:
#             np.save(file1, d2)

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

daq.DAC[0].set_clk_divider(divide_value=0x50)  # 0xA0 = 1.25 MHz, 0x50 = 2.5 MHz
daq.TCA[0].configure_pins([0,0])
daq.TCA[0].write( ((0xf)<<(4+8)) + 0xfff)

cmd_dac = daq.DAC[1]  # DAC channel 0 is connected to dc clamp ch 0 CMD signal
cc = daq.DAC[0]

ddr = DDR3(f)
ddr.reset_fifo()
port1_index = 0x7_ff_ff_f8  # fixed in the HDL
ddr.parameters['sample_size'] = int( (port1_index + 8)/2)
ddr.reset_fifo()
for i in range(8):
    ddr.data_arrays[i] = ddr.make_step(low=0x2000,
                                       high=0x2080,
                                       length=2000)

ddr.clear_fg_read()
g_buf = ddr.write_channels()
ddr.reset_fifo()
ddr.clear_write()
ddr.set_read()
time.sleep(0.5)  # allow the ADC data to accumulate into DDR
#ddr.clear_read()
# ddr.set_fg_read()

# port1_index = 0x7_ff_ff_f8
# port1_index = 0x800
# ddr.set_index(port1_index)
# ddr.parameters['sample_size'] = int( (port1_index + 8)/2)
#
# low_val = 0x2000
# high_val = 0x2040
# for i in [0, 1]:
#     ddr.data_arrays['chan{}'.format(i)][0:(port1_index//2)] = np.uint16(low_val*np.ones(port1_index//2))
#     ddr.data_arrays['chan{}'.format(i)][(port1_index//2):port1_index] = np.uint16(high_val*np.ones(port1_index//2))
#
cmd_dac.set_data_mux('DDR')
cc.set_data_mux('host')
cc.write(int(0))
# cc.change_filter_coeff(target='passthru')
# cc.filter_select(operation='set')
# cc.set_data_mux('ad7961_ch0')
cc.set_data_mux('DDR')


# TODO - a way to assign parts of the Daq TCAs to specific DACs so as to write the gain

# slow DAC: DAC1_BP_OUT4 -- utility pin, replacing I2C DAC on daughter card
