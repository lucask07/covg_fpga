"""Early test file of the daq_v2 board
   Enable power supplies using the FPGA

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

from interfaces.interfaces import FPGA
import logging
import sys
import os
import time


def enable_wire_bit(f, wire_addr, bit):
    return f.set_wire(0x02, value=1 << bit, mask=1 << bit)


def clear_wire_bit(f, wire_addr, bit):
    return f.set_wire(0x02, value=0, mask=1 << bit)


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

WI02_15V_EN = 18
WI02_1V8_EN = 19
WI02_3V3_EN = 20
WI02_5V_EN = 21
WI02_N15V_EN = 22

# Set up FPGA
f = FPGA(bitfile=os.path.join(covg_fpga_path, 'fpga_XEM7310',
                              'fpga_XEM7310.runs', 'impl_1', 'top_level_module.bit'))
f.init_device()
time.sleep(2)

# do this more carefully. What is needed? What resets are used in the FPGA?
f.set_wire(0x00, value=0, mask=0xffff)
f.set_wire(0x01, value=0, mask=0xffff)
f.set_wire(0x02, value=0, mask=0xffff)

WI02_A_EN0 = 1 # EN0 for each channel
WI02_A_EN0_LEN = 4

WI02_A_EN = 15 # EN 1,2,3; shared by all channels
WI02_A_EN_LEN = 3

# 0000 - power down
# 0001 - enabled with ref buffer on; 28 MHZ
# 0100 - test patterns on LVDS
# 0101 - enabled with ref buffer on; 9 MHZ

# set enable for AD7961 to low-power (11.4 mA from 5 V )
#  Q: what supplies need to be configured for this enable to work?
#  A: just 1.8 V (high-side is 2.5 V)

# disable the AD7961 FPGA block for reading (clk and conv output)
#  Q: is this possible?
#  A: possible, but not setup in the FPGA now. Reset is controlled by a trigger-in

# set reset for the ADS8686 (draws 55 mA when static)
#  Q: what is the default output setting in Xilinx?

# check amps for 14-bit DAC

# check diff term for LVDS inputs?
# -- what was it for the XEM6310?

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

# need instrbuilder setup to read the current

# setup QW I2C bus for I/O expanders

# probe these signals with a multimeter:
# 1) VCM_OUT from the AD7961
# 2) EN to the AD7961

# AD7961


# enable power supplies and wait for user input
en = '5V'
#enable_wire_bit(f, 0x02, WI02_5V_EN)
input('Enabled {}: Press Enter to continue'.format(en))
# clear_wire_bit(f, 0x02, 'WI02_{}_EN'.format(en))

en = '1V8'
#enable_wire_bit(f, 0x02, WI02_1V8_EN)
input('Enabled {}: Press Enter to continue'.format(en))
# clear_wire_bit(f, 0x02, 'WI02_{}_EN'.format(en))
