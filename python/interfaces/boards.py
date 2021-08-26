"""Module implementing interfaces module for sets of chips on a board.

This module serves to organize instantiations of chips from the interfaces
module for use in boards common to the project. This allows simpler top level
instantiation and the ability to more easily swap to a different board.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

from interfaces.interfaces import *
from interfaces.utils import reverse_bits

class Clamp:
    """Class for the Clamp board daughtercards.
    
    Clamp board daughtercard: https://github.com/lucask07/covg_clamp/blob/main/docs/bath_clamp_v1.pdf
    
    Attributes
    ----------
    TCA_0 : TCA9555
        First I/O Expander controlling Clamp board configuration.
    TCA_1 : TCA9555
        Second I/O Expander controlling Clamp board configuration.
    UID : UID_24AA025UID
        Unique ID chip for serial number and general memory.
    DAC : DAC53401
        Digital to Analog converter for the feedback buffer.

    Methods
    -------
    init_board()
        Checks the board's chips for connectivity and sets the I/O Expanders
        to configure the board for Voltage Clamp Feedback Loop. Also gets the
        serial number from the UID chip.
    configure_clamp(ADC_SEL=None, DAC_SEL=None, CCOMP=None, RF1=None,
                    ADG_RES=None, PClamp_CTRL=None, P1_E_CTRL=None,
                    P1_CAL_CTRL=None, P2_E_CTRL=None, P2_CAL_CTRL=None,
                    gain=None, FDBK=None, mode=None, EN_ipump=None,
                    RF_1_Out=None, addr_pins_1=0b110, addr_pins_2=0b000)
        Sets the I/O Expanders according to the arguments given.
    """

    def __init__(self, fpga, TCA_addr_pins_0=0b110, TCA_addr_pins_1=0b000, UID_addr_pins=0b000, DAC_addr_pins=0b000):
        # cwd = python/interfaces/
        # i2c_bitfile = python/i2c.bit
        self.TCA_0 = TCA9555(fpga=fpga, addr_pins=TCA_addr_pins_0)
        self.TCA_1 = TCA9555(fpga=fpga, addr_pins=TCA_addr_pins_1)
        self.UID = UID_24AA025UID(fpga=fpga, addr_pins=UID_addr_pins)
        self.DAC = DAC53401(fpga=fpga, addr_pins=DAC_addr_pins)
        self.serial_number = None # Will get serial code from UID chip in setup()

    def init_board(self):
        """Tests and configures the board.
        
        Tests connectivity with each chip, configures board for Voltage Clamp
        Feedback Loop, and gets the serial number from the UID chip.
        """
        # Check chips
        # TCA_0, TCA_1
        for register_name in [
            # Not checking input register because it defaults to a high-impedance state so we cannot check it against something
            'OUTPUT',
            'POLARITY',
            'CONFIG'
        ]:
            # TCA_0
            dev_addr = self.TCA_0.parameters['ADDRESS_HEADER'] | (
                    self.TCA_0.addr_pins << 1) | 0b1
            read_out = self.TCA_0.i2c_read_long(dev_addr, [self.TCA_0.parameters[register_name].address], 2)[
                1]  # Only the second byte to come back is what we want
            default = self.TCA_0.parameters[register_name].default
            if read_out != default:
                print(f'TCA_0 register: {register_name} FAILED\n    '
                      f'(read_out) {read_out} != (default) {default}')
                return False

            # TCA_1
            dev_addr = self.TCA_1.parameters['ADDRESS_HEADER'] | (
                    self.TCA_1.addr_pins << 1) | 0b1
            read_out = self.TCA_1.i2c_read_long(dev_addr, [self.TCA_1.parameters[register_name].address], 2)[
                1]  # Only the second byte to come back is what we want
            default = self.TCA_1.parameters[register_name].default
            if read_out != default:
                print(f'TCA_1 register: {register_name} FAILED\n    '
                      f'(read_out) {read_out} != (default) {default}')

                return False

        # Configure clamp
        # Command for Voltage Clamp Feedback loop
        self.configure_clamp(ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2',
                             CCOMP=47, RF1=3, ADG_RES=10, PClamp_CTRL=1,
                             P1_E_CTRL=1, P1_CAL_CTRL=0, P2_E_CTRL=1,
                             P2_CAL_CTRL=0, gain=2, FDBK=1, mode='voltage',
                             EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110,
                             addr_pins_2=0b000)

        # UID
        read = self.UID.get_manufacturer_code()
        default = self.UID.parameters['MANUFACTURER_CODE'].default
        if read != default:
            print(f'UID MANUFACTURER_CODE FAILED\n    '
                  f'(read) {read} != (default) {default}')
            return False

        read = self.UID.get_device_code()
        default = self.UID.parameters['DEVICE_CODE'].default
        if read != default:
            print(f'UID DEVICE_CODE FAILED\n    '
                  f'(read) {read} != (default) {default}')
            return False

        # DAC
        read = self.DAC.get_id()
        # Device and Version ID share the same default value across their combined bits
        default = self.DAC.parameters['DEVICE_ID'].default
        if read != default:
            print(f'DAC ID FAILED\n    (read) {read} != (default) {default}')
            return False

        # Get serial code
        self.serial_number = self.UID.get_serial_number()
        print(f'Serial Code: {hex(self.serial_number)}')

        return True

    def configure_clamp(self, ADC_SEL=None, DAC_SEL=None, CCOMP=None, RF1=None,
                        ADG_RES=None, PClamp_CTRL=None, P1_E_CTRL=None,
                        P1_CAL_CTRL=None, P2_E_CTRL=None, P2_CAL_CTRL=None,
                        gain=None, FDBK=None, mode=None, EN_ipump=None,
                        RF_1_Out=None, addr_pins_1=0b110, addr_pins_2=0b000):
        config_params = registers_from_excel('clamp_configuration')
        """Configures the board using the I/O Expanders."""

        #Dictonaries
        ADC_SEL_dict = {  # Select the signal to output (Usually only output one signal at a time)
            'CAL_SIG1': 0b0111,
            'CAL_SIG2': 0b1011,
            'INAMP_OUT': 0b1101,
            'CC': 0b1110,
            'noDrive': 0b1111,
            None: 0b0000
        }
        DAC_SEL_dict = {  # Choose to drive/store CAL_Sig1 and CAL_Sig2
            'drive_CAL1': 0b0111,
            'drive_CAL2': 0b1011,
            'gnd_CAL2': 0b1101,
            'gnd_CAL1': 0b1110,
            'store_CAL1': 0b0110,
            'store_CAL2': 0b1001,
            'noDrive': 0b1111,
            None: 0b0000
        }
        CCOMP_dict = {  # Choosing the capacitor value for Compensation Switching Circuit
            0: 0b0000,
            4.7: 0b0001,
            1: 0b0010,
            5.7: 0b0011,
            200: 0b0100,
            204.7: 0b0101,
            201: 0b0110,
            205.7: 0b0111,
            47: 0b1000,
            51.7: 0b1001,
            48: 0b1010,
            52.7: 0b1011,
            247: 0b1100,
            251.7: 0b1101,
            248: 0b1110,
            252.7: 0b1111,
            None: 0b0000
        }
        RF1_dict = {  # Selecting the resistor value for the feedback circuit
            0: 0b0000,
            60: 0b0001,
            30: 0b0010,
            20: 0b0011,
            12: 0b0100,
            10: 0b0101,
            8: 0b0110,
            7: 0b0111,
            3: 0b1000,
            2.8: 0b1001,
            2.7: 0b1010,
            2.6: 0b1011,
            2.4: 0b1100,
            2.3: 0b1101,
            2.2: 0b1110,
            2.1: 0b1111,
            None: 0b0000
        }
        ADG_RES_dict = {  # Select resistance acroos P2 and RF_1 (ADG)
            'current': 0b000,
            10: 0b001,
            33: 0b010,
            100: 0b011,
            332: 0b100,
            '1 MEG': 0b101,
            '3 MEG': 0b110,
            '10 MEG': 0b111,
            None: 0b000
        }

        PClamp_CTRL_dict = {
            0: 0,
            1: 1,
            None: 0
        }

        P1_E_CTRL_dict = {
            0: 0,
            1: 1,
            None: 0
        }

        P1_CAL_CTRL_dict = {
            0: 0,
            1: 1,
            None: 0
        }

        P2_E_CTRL_dict = {
            0: 0,
            1: 1,
            None: 0
        }

        P2_CAL_CTRL_dict = {
            0: 0,
            1: 1,
            None: 0
        }

        gain_dict = {  # Selecet the gain of the instrumentation AMP in ADC Driver circuit
            2: 0b100,
            5: 0b010,
            10: 0b001,
            55: 0b011,
            60: 0b101,
            63: 0b110,
            64: 0b111,
            None: 0b000
        }

        FDBK_dict = {
            0: 0,
            1: 1,
            None: 0
        }

        mode_dict = {  # select the mode for the ADC driver
            'voltage': 0b00,
            'current': 0b11,
            None: 0b00
        }

        EN_ipump_dict = {
            0: 0,
            1: 1,
            None: 0
        }

        RF_1_Out_dict = {
            0: 0,
            1: 1,
            None: 0
        }  

        # Define configuration params for mask later
        input_params_1 = {'ADC_SEL': ADC_SEL,
                        'DAC_SEL': DAC_SEL, 'CCOMP': CCOMP, 'RF1': RF1}
        input_params_2 = {'ADG_RES': ADG_RES, 'PClamp_CTRL': PClamp_CTRL, 'P1_E_CTRL': P1_E_CTRL, 'P1_CAL_CTRL': P1_CAL_CTRL,
                        'P2_E_CTRL': P2_E_CTRL, 'P2_CAL_CTRL': P2_CAL_CTRL, 'gain': gain, 'FDBK': FDBK, 'mode': mode, 'EN_ipump': EN_ipump, 'RF_1_Out': RF_1_Out}

        # Get codes from the corresponding dictionaries
        # I/O Expander 1 (self.TCA_0)
        # Using .get so if the value is not in the dictionary it returns None
        ADC_SEL_code = ADC_SEL_dict.get(ADC_SEL)
        DAC_SEL_code = DAC_SEL_dict.get(DAC_SEL)
        CCOMP_code = CCOMP_dict.get(CCOMP)
        RF1_code = RF1_dict.get(RF1)

        # I/O Expander 2 (self.TCA_1)
        ADG_RES_code = ADG_RES_dict.get(ADG_RES)
        PClamp_CTRL_code = PClamp_CTRL_dict.get(PClamp_CTRL)
        P1_E_CTRL_code = P1_E_CTRL_dict.get(P1_E_CTRL)
        P1_CAL_CTRL_code = P1_CAL_CTRL_dict.get(P1_CAL_CTRL)
        P2_E_CTRL_code = P2_E_CTRL_dict.get(P2_E_CTRL)
        P2_CAL_CTRL_code = P2_CAL_CTRL_dict.get(P2_CAL_CTRL)
        gain_code = gain_dict.get(gain)
        FDBK_code = FDBK_dict.get(FDBK)
        mode_code = mode_dict.get(mode)
        EN_ipump_code = EN_ipump_dict.get(EN_ipump)
        RF_1_Out_code = RF_1_Out_dict.get(RF_1_Out)

        # Assemble messages
        s0 = ''
        s1 = ''
        upper_byte_1 = reverse_bits((ADC_SEL_code << 4) | DAC_SEL_code)
        lower_byte_1 = reverse_bits((CCOMP_code << 4) | RF1_code)
        message1 = (upper_byte_1 << 8) | lower_byte_1
        for i in range(15, -1, -1):
            # (right shift operation on cur and i and bitwise AND with 1)
            cur = (message1 >> i) & 1
            s0 += str(cur)

        upper_byte_2 = reverse_bits((ADG_RES_code << 5) | (PClamp_CTRL_code << 4) | (
            P1_E_CTRL_code << 3) | (P1_CAL_CTRL_code << 2) | (P2_E_CTRL_code << 1) | P2_CAL_CTRL_code)
        lower_byte_2 = reverse_bits((gain_code << 5) | (FDBK_code << 4) | (
            mode_code << 2) | (EN_ipump_code << 1) | RF_1_Out_code)
        message2 = (upper_byte_2 << 8) | lower_byte_2
        for i in range(15, -1, -1):
            # (right shift operation on cur and i and bitwise AND with 1)
            cur = (message2 >> i) & 1
            s1 += str(cur)

        # Create masks
        mask1 = 0
        for key in input_params_1:
            # If the parameter was not set by the user, do not add it to the mask.
            if input_params_1[key] == None:
                continue
            else:
                mask1 += ((2**config_params[key].bit_width - 1)
                        << config_params[key].bit_index_low)

        mask2 = 0
        for key in input_params_2:
            # If the parameter was not set by the user, do not add it to the mask.
            if input_params_2[key] == None:
                continue
            else:
                mask2 += ((2**config_params[key].bit_width - 1)
                        << config_params[key].bit_index_low)

        # Reverse bytes in masks
        mask1 = (reverse_bits(mask1 // 16**2) << 8) | reverse_bits(mask1 % 16**2)
        mask2 = (reverse_bits(mask2 // 16**2) << 8) | reverse_bits(mask2 % 16**2)

        # Set pins to outputs
        self.TCA_0.configure_pins([0x00, 0x00])
        self.TCA_1.configure_pins([0x00, 0x00])

        # Write messages
        self.TCA_0.write(message1, mask1)
        self.TCA_1.write(message2, mask2)

        # Read messages
        list_read1 = self.TCA_0.read()
        list_read2 = self.TCA_1.read()
        read1 = (list_read1[0] << 8) | list_read1[1]
        read2 = (list_read2[0] << 8) | list_read2[1]

        # making the read outputs into 16 bits so that they are easjer to analyze
        read1_bin = '{:016b}'.format(read1)
        read2_bin = '{:016b}'.format(read2)

        read1_bin1 = read1_bin[0:8]  # slicing the first 8 bits of read 1
        read1_bin2 = read1_bin[8:16]  # slicing the second 8 bits of read 1
        read2_bin1 = read2_bin[0:8]  # slicing the first 8 bits of read 2
        read2_bin2 = read2_bin[8:16]  # slicing the second 8 bits of read 2

        # Reversing the first 8 bits and second 8 bits since the FPGA reads back the bits in reverse
        read1_rev1 = read1_bin1[::-1]
        read1_rev2 = read1_bin2[::-1]
        read2_rev1 = read2_bin1[::-1]
        read2_rev2 = read2_bin2[::-1]

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
