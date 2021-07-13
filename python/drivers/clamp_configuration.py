# This module should configure the clamp components controlled by the I/O Expander chip (TCA9555)
import sys, os

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

from interfaces import FPGA, IOExpanderController

# This is our main function. All parameters should pass through here. The function should get the codes
# corresponding to the parameters, assemble them as 2 bytes to set on the I/O Expander (with masking for 
# bits we do not change), set the pins to those 2 bytes, and return the configuration information so the
# file that uses this function can log the configuration.
def configure_clamp():
    pass