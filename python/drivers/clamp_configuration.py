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

#Dictonaries
    ADC_SEL = { #Select the signal to output (Usually only output one signal at a time)
        'CAL_SIG1' : 0b0111,
        'CAL_SIG2' : 0b1011,
        'INAMP_OUT' : 0b1101,
        'CC' : 0b1110
    }
    CAL_ADC = {#Choose to drive/store CAL_Sig1 and CAL_Sig2
        'drive_CAL1' : 0b0111,
        'drive_CAL2' : 0b1011,
        'gnd_CAL2' : 0b1101,
        'gnd_CAL1' : 0b1110,
        'store_CAL1' : 0b0110,
        'store_CAL2' : 0b1001
    }
    CCOMP = {#Choosing the capacitor value for Compensation Switching Circuit
        0 : 0b0000,
        4.7 : 0b0001,
        1 : 0b0010,
        5.7 : 0b0011,
        200 : 0b0100,
        204.7 : 0b0101,
        201 : 0b0110,
        205.7 : 0b0111,
        47 : 0b1000,
        51.7 : 0b1001,
        48 : 0b1010,
        52.7 : 0b1011,
        247 : 0b1100,
        251.7 : 0b1101,
        248 : 0b1110,
        252.7 : 0b1111
    }
    RF1 = {#Selecting the resistor value for the feedback circuit
        0 : 0b0000,
        60 : 0b0001,
        30 : 0b0010,
        20 : 0b0011,
        12 : 0b0100,
        10 : 0b0101,
        8 : 0b0110,
        7 : 0b0111,
        3 : 0b1000,
        2.8 : 0b1001,
        2.7 : 0b1010,
        2.6 : 0b1011,
        2.4 : 0b1100,
        2.3 : 0b1101,
        2.2 : 0b1110,
        2.1 : 0b1111
    }
    ADG_RES = {#Select resistance acroos P2 and RF_1 (ADG)
        'current' : 0b000,
        10 : 0b001,
        33 : 0b010,
        100 : 0b011,
        332 : 0b100,
        '1 MEG' : 0b101,
        '3 MEG' : 0b110,
        '10 MEG' :0b111
    }

    gain = {#Selecet the gain of the instrumentation AMP in ADC Driver circuit
        50 : 0b000,
        51 : 0b001,
        54 : 0b010,
        55 : 0b011,
        59 : 0b100,
        60 : 0b101,
        63 : 0b110,
        64 : 0b111
    }

    mode = {#select the mode for the ADC driver
        'voltage' : 0b00,
        'current' : 0b11
    }
