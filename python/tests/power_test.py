"""Early test file of the daq_v2 board
   Enable power supplies using the FPGA

August 2021

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu
"""
from interfaces.interfaces import FPGA, UID_24AA025UID, AD7961
from boards import Daq
import logging
import sys
import os
import time
from instrbuilder.instrument_opening import open_by_name
import atexit

from interfaces.interfaces import FPGA, UID_24AA025UID, AD7961, TCA9555
from boards.Daq import Power  # TODO: should I instantiate the Daq board or just pieces from it?
                              # TODO: for now, pieces, eventually the DAQ board

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


#logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'DAC80508_test.log'), filemode='w',
#                    encoding='utf-8', level=logging.INFO)

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'power_test.log'), filemode='w',
                    level=logging.INFO)

ADS_EN = False
AD7961_EN = False

# set up DC power supply
# name within the configuration file (config.yaml)
pwr = open_by_name(name='rigol_ps2')


def pwr_off():
    pwr.set('out_state', 'OFF', configs={'chan': 1})


atexit.register(pwr_off)

# setup channel 1
pwr.set('out_state', 'OFF', configs={'chan': 1})

# Channel 1 setup
pwr.set('i', 0.95, configs={'chan': 1})
pwr.set('v', 7, configs={'chan': 1})
pwr.set('ovp', 7.2, configs={'chan': 1})
pwr.set('ocp', 1.1, configs={'chan': 1})

meas_i_status = {}
meas_i = pwr.get('meas_i', configs={'chan': 1})
meas_i_status.update({'startup_nobitfile': meas_i})

# Set up FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)
meas_i = pwr.get('meas_i', configs={'chan': 1})
meas_i_status.update({'startup_bitfile': meas_i})

# reset FPGA using trigger in
TI40_RST = 1
f.xem.ActivateTriggerIn(0x40, TI40_RST)

pwr = Power(f)
pwr.all_off()  # disable all power enables

AD7961_CHANS = 4
ad7961s = []
for i in range(AD7961_CHANS):
    ad7961s.append(AD7961(f, chan=i))

for i in range(AD7961_CHANS):
    ad7961s[i].power_down_all()

# Instantiate ID chip
uid = UID_24AA025UID(fpga=f, addr_pins=0b000)
#  TODO: wirein and wireout bit indices are not at 0
#  TODO: input the name of the excel worksheet

WI02_ADS_RESETB = 25
f.clear_wire_bit(0x02, WI02_ADS_RESETB)
# time.sleep(0.01)
# f.set_wire_bit(0x02, WI02_ADS_RESETB)

# power supply turn on and check current
for name in ['1V8', '5V', '3.3']:
    pwr.supply_on(name)
    meas_i = pwr.get('meas_i', configs={'chan': 1})
    meas_i_status.update({name: meas_i})

# +15 and -15V simultaneously
pwr.all_on()
meas_i = pwr.get('meas_i', configs={'chan': 1})
meas_i_status.update({'15V_N15V': meas_i})

# UID
read = uid.get_manufacturer_code()
default = uid.parameters['MANUFACTURER_CODE'].default
if read != default:
    print(f'UID MANUFACTURER_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')

read = uid.get_device_code()
default = uid.parameters['DEVICE_CODE'].default
if read != default:
    print(f'UID DEVICE_CODE FAILED\n    '
          f'(read) {read} != (default) {default}')

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
WI02_IPUMP_EN = 23
WI02_IPUMP_EN_LEN = 2
for i in range(WI02_IPUMP_EN_LEN):
    f.clear_wire_bit(0x02, WI02_IPUMP_EN + i)

meas_i = pwr.get('meas_i', configs={'chan': 1})
meas_i_status.update({'IPUMP_DISABLE': meas_i})

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
io_0 = TCA9555(fpga=f, addr_pins=0b000)  # DAC gains 0,1,2,3
io_1 = TCA9555(fpga=f, addr_pins=0b100)  # DAC gains 4,5; ISEL

io_0.configure_pins(0xffff)  # set all pins to outputs
io_0.write(0x0000)  # set all pins to zero

io_1.configure_pins(0xffff)  # set all pins to outputs
io_1.write(0x0000)  # set all pins to zero

meas_i = pwr.get('meas_i', configs={'chan': 1})
meas_i_status.update({'io_expanders_0': meas_i})


# enable one AD7961 and remeasure current
if AD7961_EN:
    ad7961s[0].power_up_adc()
    time.sleep(0.05)
    meas_i = pwr.get('meas_i', configs={'chan': 1})
    meas_i_status.update({'enable_ad7961': meas_i})
    ad7961s[0].power_down_adc()

# enable ADS868 and remeasure current
if ADS_EN:
    f.set_wire_bit(0x02, WI02_ADS_RESETB)
    time.sleep(0.01)
    meas_i = pwr.get('meas_i', configs={'chan': 1})
    meas_i_status.update({'enable_ads8686': meas_i})

print(meas_i_status)

# lower all I/O wires
pwr.all_off()

# probe these signals with a multimeter:
# 1) VCM_OUT from the AD7961
# 2) EN to the AD7961
