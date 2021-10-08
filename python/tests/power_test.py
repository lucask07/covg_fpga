"""Early test file of the daq_v2 board
   Enable power supplies using the FPGA

August 2021

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu

TODO:
1) move 7 V to CH3
2) add +/-16.5V to CH1 and CH2
3) meas current of each -- current function
4) add ADS8686 for Simple SPI reads
5) add UID
6) switch back to name of IO expander -- change register sheet
7) setup AD7961 to continuously stream (one channel)

"""
import logging
import sys
import os
import time
import datetime
import numpy as np
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

from interfaces.interfaces import Endpoint
eps1 = Endpoint.update_endpoints_from_defines()

from interfaces.interfaces import FPGA, UID_24AA025UID, AD7961, DAC80508, AD5453
from interfaces.interfaces import TCA9555, disp_device, ADS8686, advance_endpoints_bynum, DebugFIFO, DDR3

eps = Endpoint.endpoints_from_defines

from interfaces.boards import Daq  # TODO: should I instantiate the Daq board or just pieces from it?
                                   # TODO: for now, pieces, eventually the DAQ board


def get_timestamp():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'power_test.log'), filemode='w',
                    level=logging.INFO)

# eps = Endpoint.endpoints_from_defines
ADS_EN = False
AD7961_EN = False
EN_15V = True
DAC_80508_EN = False
DDR_EN = True
FIFO_DEBUG_EN = False

# set up DC power supply
# name within the configuration file (config.yaml)
dc_pwr = open_by_name(name='rigol_pwr1')  # 7V in
dc_pwr2 = open_by_name(name='rigol_ps2')  # +/-16.5V

current_meas = {}
for ch in range(1, 4):
    # create dictionary for each channel
    current_meas['ch{}'.format(ch)] = {}
    for n in ['val', 'timestamp']:
        current_meas['ch{}'.format(ch)][n] = np.array([])
    # create a list
    current_meas['ch{}'.format(ch)]['description'] = []


def log_dc_pwr(dc_pwr, dc_pwr2, data, desc='none'):
    """ measure current from CH1 and  CH1,CH2 of two PWR supplies channels and
        update into dictionary with timestamp (ms)
    """
    for ch in [1]:
        data['ch{}'.format(ch)]['val'] = np.append(data['ch{}'.format(ch)]['val'],
                                        dc_pwr.get('meas_i', configs={'chan': ch}))
        data['ch{}'.format(ch)]['timestamp'] = np.append(data['ch{}'.format(ch)]['timestamp'], get_timestamp())
        data['ch{}'.format(ch)]['description'].append(desc)
    # second supply
    for ch in [1, 2]:
        data['ch{}'.format(ch)]['val'] = np.append(data['ch{}'.format(ch)]['val'],
                                        dc_pwr2.get('meas_i', configs={'chan': ch}))
        data['ch{}'.format(ch)]['timestamp'] = np.append(data['ch{}'.format(ch)]['timestamp'], get_timestamp())
        data['ch{}'.format(ch)]['description'].append(desc)


def pwr_off():
    for ch in [1, 2, 3]:
        dc_pwr.set('out_state', 'OFF', configs={'chan': ch})
    for ch in [1, 2, 3]:
        dc_pwr2.set('out_state', 'OFF', configs={'chan': ch})


atexit.register(pwr_off)

# pwr off all channels
pwr_off()

# Channel 1 and 2 setup
for ch in [1, 2]:
    dc_pwr2.set('i', 0.39, configs={'chan': ch})
    dc_pwr2.set('v', 16.5, configs={'chan': ch})
    dc_pwr2.set('ovp', 16.7, configs={'chan': ch})
    dc_pwr2.set('ocp', 0.400, configs={'chan': ch})

# Channel 1 on supply1 for Vin
dc_pwr.set('i', 0.55, configs={'chan': 1})
dc_pwr.set('v', 7, configs={'chan': 1})
dc_pwr.set('ovp', 7.2, configs={'chan': 1})
dc_pwr.set('ocp', 0.75, configs={'chan': 1})

# turn on the 7V in, but keep +/-16.6 down
dc_pwr.set('out_state', 'ON', configs={'chan': 1})

log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='startup_nobitfile')

time.sleep(2)
# Set up FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)
f.send_trig(eps['GP']['SYSTEM_RESET'])  # system reset

log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='startup_bitfile')

uid = UID_24AA025UID(fpga=f,
                     endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDAQ'), 1),
                     addr_pins=0b000)

ads = ADS8686(fpga=f,
              endpoints=Endpoint.get_chip_endpoints('ADS8686'))

dac0 = DAC80508(fpga=f)
dac1 = DAC80508(fpga=f, endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('DAC80508'), 1))

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug('dfast0')
gpio.ads_misc('convst')

AD7961_CHANS = 4
ad7961s = []
for i in range(AD7961_CHANS):
    ad7961s.append(AD7961(f, endpoints=advance_endpoints_bynum(Endpoint.get_chip_endpoints('AD7961'),i)))

for i in range(AD7961_CHANS):
    ad7961s[i].power_down_all()
    ad7961s[i].reset_wire(1)

if FIFO_DEBUG_EN:
    fifo_debug = DebugFIFO(f)
    fifo_debug.reset_fifo()
    dt = fifo_debug.stream_mult(swps=4, twos_comp_conv=False)

# TODO wrpt endpoints stuff:
"""
4) are the multiple SPI controllers setup with endpoints correctly?
5) when is endpoints intended to be read?
"""

#  TODO: wirein and wireout bit indices are not at 0
#  TODO: input the name of the excel worksheet

ads.hw_reset(val=True)  # put ADS into hardware reset

# power supply turn on and check current (AD7961 - 1.8 V first, then 5V)
for name in ['1V8', '5V', '3V3']:
    pwr.supply_on(name)
    log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='turnon_{}'.format(name))
    time.sleep(0.05)

# +15 and -15V simultaneously
# pwr.all_on()
if EN_15V:
    for ch in [1, 2]:
        dc_pwr2.set('out_state', 'ON', configs={'chan': ch})
    time.sleep(0.05)
    log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='turnon_15n15V')

time.sleep(0.01)
#  pwr.all_off()
print(current_meas)

# UID
read = uid.get_manufacturer_code()
default = uid.registers['MANUFACTURER_CODE'].default
if read != default:
    print(f'UID MANUFACTURER_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')

read = uid.get_device_code()
default = uid.registers['DEVICE_CODE'].default
if read != default:
    print(f'UID DEVICE_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')

# check to see if i2c is consistent
read_test = []
for i in range(100):
    read_test.append(uid.get_manufacturer_code())

unq_sn = uid.get_serial_number()

ddr = DDR3(f)
ddr.write_flat_voltage(0.8)
ddr_readback_flat = ddr.read()
ddr_readback_sin = ddr.write_sin_wave(1.1)

fdac = []
fdac.append(AD5453(f))

# AD7961
# set enable for AD7961 to low-power (11.4 mA from 5 V )
#  Q: what supplies need to be configured for this enable to work?
#  A: just 1.8 V (high-side is 2.5 V)

# disable the AD7961 FPGA block for reading (clk and conv output)
#  Q: is this possible?
#  A: possible, but not setup in the FPGA now. Reset is controlled by a trigger-in

# set reset for the ADS8686 (draws 55 mA when static)
#  Q: what is the default output setting in Xilinx?

# TODO: error in schematic note
#       should be "high-Z or high will enable"
for bit_pos in range(eps['GP']['CURRENT_PUMP_ENABLE'].bit_index_low,
                     eps['GP']['CURRENT_PUMP_ENABLE'].bit_index_high + 1):

    f.clear_wire_bit(eps['GP']['CURRENT_PUMP_ENABLE'].address,
                     bit_pos)

log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='ipump_disable')

# check amps for 14-bit DAC

# check diff term for LVDS inputs?
# -- what was it for the XEM6310? - in constraints
# diff term is specified as true in the IBUFDS instantiation (so OK)

# add up current for LVDS
#  Q: current per pin
#  A: ~4mA

# need a supply power up procedure/order and a prediction of the current of PWR only
# Q: what was supply draw alone?
# A: 34 mA with all supplies enabled; 5 mA with none enabled

# need calculator based on input voltage -- more current required at lower voltages --> DONE

# check DAC80508:
# Q: does it have CLR pin?
# A: yes, the manf# is ZC - zero and clear
# TODO: change FPGA output pins (tie high? since CLRB) --> DONE

# setup QW I2C bus for I/O expanders
# Note: the VREF gain for the high-speed DACs defaults to x4.88 if the I/O
#       expanders are not configured. So no concern of damage if we don't configure these

# desired I/O expander:
# DAC gains and current output select
io_0 = TCA9555(fpga=f, endpoints=Endpoint.get_chip_endpoints('I2CDAQ'),
               addr_pins=0b000)  # DAC gains 0,1,2,3
io_1 = TCA9555(fpga=f, endpoints=Endpoint.get_chip_endpoints('I2CDAQ'),
               addr_pins=0b100)  # DAC gains 4,5;
                                                  # ISEL1[3:0]; ISEL2[3:0]

io_0.configure_pins([0x00, 0x00])  # set all pins to outputs (=0)
io_0.write(0x0000)  # set all pins to zero --
                    # minimizes the DAC gain and should lower current draw

io_1.configure_pins([0x00, 0x00])  # set all pins to outputs

# ISEL = 1 gives voltage outputs
# ISEL = 0 routes Howland Ipump out
io_1.write(0x00FF)  # set all gain pins to zero & all ISEL to have the voltage output
 # TODO: check ordering of the io write; seems correct

log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='io_expanders_0')
setup = ad7961s[0].setup(reset_pll=True)
time.sleep(0.05)
# enable one AD7961 and remeasure current
chan = 2
num = 13
if AD7961_EN:
    for chan in [3]:
        for num in [13,14]:
            if chan == 0:
                setup = ad7961s[chan].setup(reset_pll=True)  # resets FIFO and ADC controller
            else:
                setup = ad7961s[chan].setup(reset_pll=False)  # resets FIFO and ADC controller
            ad7961s[chan].test_pattern()
            time.sleep(0.2)
            ad7961s[chan].reset_fifo()
            time.sleep(0.2)  # FIFO fills in 204 us
            log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='enable_ad7961')
            d1 = ad7961s[chan].stream_mult(swps=4, twos_comp_conv=False)

            ad7961s[chan].power_up_adc()  # standard sampling
            ad7961s[chan].reset_fifo()
            time.sleep(0.2)
            ad7961s[chan].reset_fifo()
            time.sleep(0.2)
            d2 = ad7961s[chan].stream_mult(swps=4)
            with open('test_pattern_chan{}_num{}.npy'.format(chan, num), 'wb') as f:
                np.save(f, d1)
            with open('test_data_chan{}_num{}.npy'.format(chan, num), 'wb') as f:
                np.save(f, d2)

# enable ADS868 and remeasure current
if ADS_EN:
    ads.hw_reset(val=False)  # release reset
    time.sleep(0.01)
    log_dc_pwr(dc_pwr, dc_pwr2, current_meas, desc='ads_release_reset')
    time.sleep(1)
    ads.set_host_mode()
    ads.setup()
    cfg = ads.read('config')
    chan_sel = ads.read('chan_sel')
    range_a1 = ads.read('rangeA1')
    ads.set_range(5)
    lpf1 = ads.read('lpf')
    ads.set_lpf(376)
    lpf2 = ads.read('lpf')
    ads.setup_sequencer(chan_list=['FIXED_A', 'FIXED_B', '5A', '5B'])
    ads.write_reg_bridge()
    ads.set_fpga_mode()
    data_ads = ads.stream_mult(swps=4, twos_comp_conv=False)

    # ads.hw_reset(val=True)  # back to reset
print(current_meas)

if DAC_80508_EN:
    # these DAC signals come out before the bipolar amplifier
    for dac in [dac0, dac1]:
        # dac.reset_master()  # TODO -- I don't think this works?
        dac.set_host_mode()
        print('Setting divider...')
        dac.set_divider(0x8)  # XEM6310 worked with divider of 4, XEM7310 runs twice as fast so divider of 8.
        print('Configuring Wishbone...')
        spi_ctrl_reg_val = 0x3218  # Sets CHAR_LEN=24, Rx_NEG, ASS, IE
        dac.configure_master_bin(spi_ctrl_reg_val)
        dac.select_slave(1)

        dac.set_gain(0x01ff)
        print('Gain changed')

        # Write 0xff to 0x03 (CONFIG register)
        dac.set_config_bin(0xff)
        print('Outputs powered down')

        # Write 0x00 to 0x03 (CONFIG register)
        dac.set_config_bin(0x00)
        print('Outputs powered on')

        # Write to all outputs
        voltage = 0xffff
        for i in range(8):
            if dac.write('DAC'+str(i), voltage):
                message = f'Write {hex(voltage)}={voltage}V SUCCESS'
                # print(message)
                logging.info(message)
            else:
                message = f'Write {hex(voltage)}={voltage}V FAIL'
                logging.warning(message)

# lower all I/O wires
# pwr.all_off()

# probe these signals with a multimeter:
# 1) VCM_OUT from the AD7961
# 2) EN to the AD7961
