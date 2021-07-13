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


def configure_clamp(fpga, ADC_SEL=None, DAC_SEL=None, CCOMP=None, RF1=None,
                    ADG_RES=None, PClamp_CTRL=None, P1_E_CTRL=None, P1_CAL_CTRL=None, P2_E_CTRL=None, P2_CAL_CTRL=None, gain=None, FDBK=None, mode=None, EN_ipump=None, RF_1_Out=None,
                    addr_pins_1=0b000, addr_pins_2=0b001):  # TODO: correct defaults for addr_pins
    # Define configuration params for mask later
    config_params_1 = [ADC_SEL, DAC_SEL, CCOMP, RF1]
    config_params_2 = [ADG_RES, PClamp_CTRL, P1_E_CTRL, P1_CAL_CTRL,
                       P2_E_CTRL, P2_CAL_CTRL, gain, FDBK, mode, EN_ipump, RF_1_Out]

    # Get codes from the corresponding dictionaries
    # I/O Expander 1 (io1)
    # Using .get so if the value is not in the dictionary it returns None
    ADC_SEL_code = ADC_SEL_dict.get(ADC_SEL)
    DAC_SEL_code = DAC_SEL_dict.get(DAC_SEL)
    CCOMP_code   = CCOMP_dict.get(CCOMP)
    RF1_code     = RF1_dict.get(RF1)

    # I/O Expander 2 (io2)
    ADG_RES_code     = ADG_RES_dict.get(ADG_RES)
    PClamp_CTRL_code = PClamp_CTRL_dict.get(PClamp_CTRL)
    P1_E_CTRL_code   = P1_E_CTRL_dict.get(P1_E_CTRL)
    P1_CAL_CTRL_code = P1_CAL_CTRL_dict.get(P1_CAL_CTRL)
    P2_E_CTRL_code   = P2_E_CTRL_dict.get(P2_E_CTRL)
    P2_CAL_CTRL_code = P2_CAL_CTRL_dict.get(P2_CAL_CTRL)
    gain_code        = gain_dict.get(gain)
    FDBK_code        = FDBK_dict.get(FDBK)
    mode_code        = mode_dict.get(mode)
    EN_ipump_code    = EN_ipump_dict.get(EN_ipump)
    RF_1_Out_code    = RF_1_Out_dict.get(RF_1_Out)

    # Assemble messages
    message1 = (ADC_SEL_code << 12) + (DAC_SEL_code << 8) + \
        (CCOMP_code << 4) + (RF1_code)
    message2 = (ADG_RES_code << 13) + (PClamp_CTRL_code << 12) + (P1_E_CTRL_code << 11) + (P1_CAL_CTRL_code << 10) + (P2_E_CTRL_code <<
        9) + (P2_CAL_CTRL_code << 8) + (gain_code << 5) + (FDBK_code << 4) + (mode_code << 2) + (EN_ipump_code << 1) + (RF_1_Out_code)

    # Create masks
    mask1 = ''
    for bit in range(len(config_params_1)):
        if config_params_1[bit] == None:
            mask1 += '0'
        else:
            mask1 += '1'
    mask1 = int(mask1, 2)

    mask2 = ''
    for bit in range(len(config_params_2)):
        if config_params_2[bit] == None:
            mask2 += '0'
        else:
            mask2 += '1'
    mask2 = int(mask2, 2)

    # I/O Expander chips
    io1 = IOExpanderController(fpga)
    io2 = IOExpanderController(fpga)

    # Set pins to outputs
    io1.configure_pins(addr_pins_1, [0x00, 0x00])
    io2.configure_pins(addr_pins_2, [0x00, 0x00])

    # Write messages
    io1.write(addr_pins_1, message1, mask1)
    io2.write(addr_pins_2, message2, mask2)

    # Return configuration and code for logging or other purposes.
    return [
        f'ADC_SEL = {ADC_SEL}',
        f'DAC_SEL = {DAC_SEL}',
        f'CCOMP = {CCOMP}',
        f'RF1 = {RF1}',
        f'ADG_RES = {ADG_RES}',
        f'PClamp_CTRL = {PClamp_CTRL}',
        f'P1_E_CTRL = {P1_E_CTRL}',
        f'P1_CAL_CTRL = {P1_CAL_CTRL}',
        f'P2_E_CTRL = {P2_E_CTRL}',
        f'P2_CAL_CTRL = {P2_CAL_CTRL}',
        f'gain = {gain}',
        f'FDBK = {FDBK}',
        f'mode = {mode}',
        f'EN_ipump = {EN_ipump}',
        f'RF_1_Out = {RF_1_Out}',
        f'Code 1 = {message1}',
        f'Code 2 = {message2}'
    ]

#Dictonaries
ADC_SEL_dict = { #Select the signal to output (Usually only output one signal at a time)
    'CAL_SIG1'  : 0b0111,
    'CAL_SIG2'  : 0b1011,
    'INAMP_OUT' : 0b1101,
    'CC'        : 0b1110,
    None        : 0b0000
}
DAC_SEL_dict = {#Choose to drive/store CAL_Sig1 and CAL_Sig2
    'drive_CAL1' : 0b0111,
    'drive_CAL2' : 0b1011,
    'gnd_CAL2'   : 0b1101,
    'gnd_CAL1'   : 0b1110,
    'store_CAL1' : 0b0110,
    'store_CAL2' : 0b1001,
    None         : 0b0000
}
CCOMP_dict = {#Choosing the capacitor value for Compensation Switching Circuit
    0     : 0b0000,
    4.7   : 0b0001,
    1     : 0b0010,
    5.7   : 0b0011,
    200   : 0b0100,
    204.7 : 0b0101,
    201   : 0b0110,
    205.7 : 0b0111,
    47    : 0b1000,
    51.7  : 0b1001,
    48    : 0b1010,
    52.7  : 0b1011,
    247   : 0b1100,
    251.7 : 0b1101,
    248   : 0b1110,
    252.7 : 0b1111,
    None  : 0b0000
}
RF1_dict = {#Selecting the resistor value for the feedback circuit
    0    : 0b0000,
    60   : 0b0001,
    30   : 0b0010,
    20   : 0b0011,
    12   : 0b0100,
    10   : 0b0101,
    8    : 0b0110,
    7    : 0b0111,
    3    : 0b1000,
    2.8  : 0b1001,
    2.7  : 0b1010,
    2.6  : 0b1011,
    2.4  : 0b1100,
    2.3  : 0b1101,
    2.2  : 0b1110,
    2.1  : 0b1111,
    None : 0b0000
}
ADG_RES_dict = {#Select resistance acroos P2 and RF_1 (ADG)
    'current' : 0b000,
    10        : 0b001,
    33        : 0b010,
    100       : 0b011,
    332       : 0b100,
    '1 MEG'   : 0b101,
    '3 MEG'   : 0b110,
    '10 MEG'  : 0b111,
    None      : 0b000
}

PClamp_CTRL_dict = {
    0    : 0,
    1    : 1,
    None : 0
}

P1_E_CTRL_dict = {
    0    : 0,
    1    : 1,
    None : 0
}

P1_CAL_CTRL_dict = {
    0    : 0,
    1    : 1,
    None : 0
}

P2_E_CTRL_dict = {
    0    : 0,
    1    : 1,
    None : 0
}

P2_CAL_CTRL_dict = {
    0    : 0,
    1    : 1,
    None : 0
}

gain_dict = {#Selecet the gain of the instrumentation AMP in ADC Driver circuit
    50   : 0b000,
    51   : 0b001,
    54   : 0b010,
    55   : 0b011,
    59   : 0b100,
    60   : 0b101,
    63   : 0b110,
    64   : 0b111,
    None : 0b000
}

FDBK_dict = {
    0    : 0,
    1    : 1,
    None : 0
}

mode_dict = {#select the mode for the ADC driver
    'voltage' : 0b00,
    'current' : 0b11,
    None      : 0b00
}

EN_ipump_dict = {
    0    : 0,
    1    : 1,
    None : 0
}

RF_1_Out_dict = {
    0    : 0,
    1    : 1,
    None : 0
}
