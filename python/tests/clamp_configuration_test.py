"""Test for the clamp_configuration.py configure_clamp function.
Configures the clamp board using 2 I2C TCA9555DBT I/O Expanders
August 2021
Abe Stroschein, ajstroschein@stthomas.edu
"""

import sys
import os
import logging


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

logging.basicConfig(filename=os.path.join(interfaces_path, 'tests', 'clamp_configuration_test.log'), filemode='w',
                    encoding='utf-8', level=logging.INFO)

from interfaces.interfaces import FPGA

sys.path.append(os.path.join(interfaces_path, 'drivers'))

from clamp_configuration import configure_clamp

# Requires i2c.bit or First.bit for the bitfile.
bitfile = os.path.join(interfaces_path, 'i2c.bit')

f = FPGA(bitfile=bitfile)
f.init_device()
#Resistance Capacitance IN_AMP_OUT Gain can all be changed independently.

#Command for Voltage Clamp Feedback loop
log_info = configure_clamp(f, ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2', CCOMP=47, RF1=3,ADG_RES=10, PClamp_CTRL=1, P1_E_CTRL=1, P1_CAL_CTRL=0, P2_E_CTRL=1, P2_CAL_CTRL=0, gain=2, FDBK=1, mode='voltage', EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110, addr_pins_2=0b000)
#Command for voltage clamp with cell connected
#log_info = configure_clamp(f, ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2', CCOMP=47, RF1=3,ADG_RES=10, PClamp_CTRL=0, P1_E_CTRL=0, P1_CAL_CTRL=0, P2_E_CTRL=0, P2_CAL_CTRL=0, gain=2, FDBK=1, mode='voltage', EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110, addr_pins_2=0b000)
#Command for currrent clamp Feedback Loop
#log_info = configure_clamp(f, ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2', CCOMP=47, RF1=3,ADG_RES='current', PClamp_CTRL=1, P1_E_CTRL=1, P1_CAL_CTRL=0, P2_E_CTRL=1, P2_CAL_CTRL=0, gain=2, FDBK=1, mode='current', EN_ipump=1, RF_1_Out=1, addr_pins_1=0b110, addr_pins_2=0b000)
#command for current clamp with cell connected
#log_info = configure_clamp(f, ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2', CCOMP=47, RF1=3,ADG_RES='current', PClamp_CTRL=0, P1_E_CTRL=0, P1_CAL_CTRL=0, P2_E_CTRL=0, P2_CAL_CTRL=0, gain=2, FDBK=1, mode='current', EN_ipump=1, RF_1_Out=1, addr_pins_1=0b110, addr_pins_2=0b000)


for info in log_info:
    logging.info(info)
# Expecting 0b0111, 0b1011, 0b0010, 0b0001    0xde84
#11011110. 10000100
#100000 10 1100 1110   000
