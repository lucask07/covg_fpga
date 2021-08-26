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

from interfaces import IOExpanderController, Register

# This is our main function. All parameters should pass through here. The function should get the codes
# corresponding to the parameters, assemble them as 2 bytes to set on the I/O Expander (with masking for
# bits we do not change), set the pins to those 2 bytes, and return the configuration information so the
# file that uses this function can log the configuration.


def configure_clamp(fpga, ADC_SEL=None, DAC_SEL=None, CCOMP=None, RF1=None,
                    ADG_RES=None, PClamp_CTRL=None, P1_E_CTRL=None, P1_CAL_CTRL=None, P2_E_CTRL=None, P2_CAL_CTRL=None, gain=None, FDBK=None, mode=None, EN_ipump=None, RF_1_Out=None,
                    addr_pins_1=0b110, addr_pins_2=0b000):
    # Define configuration params for mask later
    input_params_1 = {'ADC_SEL' : ADC_SEL, 'DAC_SEL' : DAC_SEL, 'CCOMP' : CCOMP, 'RF1' : RF1}
    input_params_2 = {'ADG_RES': ADG_RES, 'PClamp_CTRL' : PClamp_CTRL, 'P1_E_CTRL' : P1_E_CTRL, 'P1_CAL_CTRL' : P1_CAL_CTRL,
                      'P2_E_CTRL': P2_E_CTRL, 'P2_CAL_CTRL': P2_CAL_CTRL, 'gain' : gain, 'FDBK' : FDBK, 'mode' : mode, 'EN_ipump' : EN_ipump, 'RF_1_Out' : RF_1_Out}

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
    num = 0
    s0 = ''
    s1 = ''
    upper_byte_1 = reverse_bits((ADC_SEL_code << 4) | DAC_SEL_code)
    lower_byte_1 = reverse_bits((CCOMP_code << 4) | RF1_code)
    message1 = (upper_byte_1 << 8) | lower_byte_1
    for i in range(15,-1,-1):
        cur=(message1>>i) & 1 #(right shift operation on num and i and bitwise AND with 1)
        s0+=str(cur)

    upper_byte_2 = reverse_bits((ADG_RES_code << 5) | (PClamp_CTRL_code << 4) | (P1_E_CTRL_code << 3) | (P1_CAL_CTRL_code << 2) | (P2_E_CTRL_code << 1) | P2_CAL_CTRL_code)
    lower_byte_2 = reverse_bits((gain_code << 5) | (FDBK_code << 4) | (mode_code << 2) | (EN_ipump_code << 1) | RF_1_Out_code)
    message2 = (upper_byte_2 << 8) | lower_byte_2
    for i in range(15,-1,-1):
        cur=(message2>>i) & 1 #(right shift operation on num and i and bitwise AND with 1)
        s1+=str(cur)

    # Create masks
    mask1 = 0
    for key in input_params_1:
        if input_params_1[key] == None: # If the parameter was not set by the user, do not add it to the mask.
            continue
        else:
            mask1 += ((2**config_params[key].bit_width - 1) << config_params[key].bit_index_low)

    mask2 = 0
    for key in input_params_2:
        # If the parameter was not set by the user, do not add it to the mask.
        if input_params_2[key] == None:
            continue
        else:
            mask2 += ((2**config_params[key].bit_width - 1) << config_params[key].bit_index_low)

    # Reverse bytes in masks
    mask1 = (reverse_bits(mask1 // 16**2) << 8) | reverse_bits(mask1 % 16**2)
    mask2 = (reverse_bits(mask2 // 16**2) << 8) | reverse_bits(mask2 % 16**2)

    # I/O Expander chips
    io1 = IOExpanderController(fpga)
    io2 = IOExpanderController(fpga)

    # Set pins to outputs
    io1.configure_pins(addr_pins_1, [0x00, 0x00])
    io2.configure_pins(addr_pins_2, [0x00, 0x00])

    # Write messages
    print(f'Writing 1: {s0} ({hex(message1)} {message1})')
    print(f'   Mask 1: {bin(mask1)}')
    io1.write(addr_pins_1, message1, mask1)

    print(f'Writing 2: {s1} ({hex(message2)} {message2})')
    print(f'   Mask 2: {bin(mask2)}')
    io2.write(addr_pins_2, message2, mask2)

    # Read messages
    list_read1 = io1.read(addr_pins_1)
    list_read2 = io2.read(addr_pins_2)
    read1 = (list_read1[0] << 8) | list_read1[1]
    read2 = (list_read2[0] << 8) | list_read2[1]

    read1_bin = '{:016b}'.format(read1) #making the read outputs into 16 bits so that they are easjer to analyze
    read2_bin = '{:016b}'.format(read2)

    read1_bin1 = read1_bin[0:8]#slicing the first 8 bits of read 1
    read1_bin2 = read1_bin[8:16]#slicing the second 8 bits of read 1
    read2_bin1 = read2_bin[0:8]#slicing the first 8 bits of read 2
    read2_bin2 = read2_bin[8:16]#slicing the second 8 bits of read 2

    read1_rev1 = read1_bin1[::-1]#Reversing the first 8 bits and second 8 bits since the FPGA reads back the bits in reverse
    read1_rev2 = read1_bin2[::-1]
    read2_rev1 = read2_bin1[::-1]
    read2_rev2 = read2_bin2[::-1]

    print('Reading 1: 0b'+read1_rev1+read1_rev2, hex(read1), read1)
    print('Reading 2: 0b'+read2_rev1+read2_rev2, hex(read2), read2)

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

# Function to reverse the bits in a byte. Use for writing each byte to the I/O Expander because the MSB goes to pin 07 or 17 rather than 00 or 10
def reverse_bits(number, bit_width=8):
    reversed_number = 0
    for i in range(bit_width):
        reversed_number <<= 1
        reversed_number |= number & 0b1
        number >>= 1
    return reversed_number

config_params = Register.dict_from_excel('clamp_configuration')

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
