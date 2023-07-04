"""Module implementing interfaces module for sets of chips on a board.

This module serves to organize instantiations of chips from the interfaces
module for use in boards common to the project. This allows simpler top level
instantiation and the ability to more easily swap to a different board.

August 2021

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu
"""

from pyripherals.core import Endpoint, Register
from pyripherals.peripherals.DDR3 import DDR3
from pyripherals.peripherals.TCA9555 import TCA9555
from pyripherals.peripherals.UID_24AA025UID import UID_24AA025UID
from pyripherals.peripherals.DAC101C081 import DAC101C081
from pyripherals.peripherals.DAC80508 import DAC80508
from pyripherals.peripherals.AD5453 import AD5453
from pyripherals.peripherals.ADS8686 import ADS8686
from pyripherals.peripherals.AD7961 import AD7961
from pyripherals.peripherals.TMF8801 import TMF8801
from pyripherals.utils import reverse_bits, test_bit, calc_impedance, from_voltage, to_voltage
from scipy.fft import rfftfreq
import matplotlib.pyplot as plt
import time
import copy
import numpy as np

# Assign I2CDAQ busses
Endpoint.I2CDAQ_level_shifted = Endpoint.get_chip_endpoints('I2CDAQ')
# We want the endpoints_from_defines to be the same make a copy before incrementing
Endpoint.I2CDAQ_QW = Endpoint.advance_endpoints(
    endpoints_dict=copy.deepcopy(Endpoint.I2CDAQ_level_shifted))


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
                    RF_1_Out=None, addr_pins_1=0b110, addr_pins_2=0b000, dc_num=0)
        Sets the I/O Expanders according to the arguments given.
    """

    configs = {}
    # Dictonaries
    # None is the default configuration
    configs['ADC_SEL_dict'] = {  # Select the signal to output (Usually only output one signal at a time)
        'CAL_SIG1': 0b0111,
        'CAL_SIG2': 0b1011,
        'INAMP_OUT': 0b1101,
        'CC': 0b1110,
        'noDrive': 0b1111,
        None: 0b0000
    }

    configs['DAC_SEL_dict'] = {  # Choose to drive, gnd, or high-z CAL_Sig1 and CAL_Sig2
        'drive_CAL1': 0b0111,
        'drive_CAL2': 0b1011,
        'drive_CAL1_gnd_CAL2': 0b0101,
        'drive_CAL2_gnd_CAL1': 0b1010,
        'drive_CAL2_gnd_CAL2': 0b1001,
        'drive_CAL1_gnd_CAL1': 0b0110,
        'gnd_CAL2': 0b1101,
        'gnd_CAL1': 0b1110,
        'gnd_both': 0b1100,
        'drive_both': 0b0011,
        'noDrive': 0b1111,
        None: 0b0000
    }

    comp_caps = np.array([4700, 1000, 200, 47])
    CCOMP_dict = {}
    for i in range(16):
        cap_val = 0
        for bit, j in enumerate(comp_caps):
            if test_bit(i, bit) == 0:  # a zero closes the switch
                cap_val += comp_caps[bit]
        CCOMP_dict[cap_val] = i
    configs['CCOMP_dict'] = CCOMP_dict
    configs['CCOMP_dict'][None] = 0 # default

    configs['RF1_dict'] = {  # Selecting the resistor value for the feedback circuit, all in kilo-ohms
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
    configs['ADG_RES_dict'] = {  # Select resistance acroos P2 and RF_1 (ADG), all listed in kilo-ohms
        'current': 0b000,
        10: 0b100,
        33: 0b010,
        100: 0b110,
        332: 0b001,
        1000: 0b101,
        3000: 0b011,
        10000: 0b111,
        None: 0b000
    }

    configs['PClamp_CTRL_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    configs['P1_E_CTRL_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    configs['P1_CAL_CTRL_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    configs['P2_E_CTRL_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    configs['P2_CAL_CTRL_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    configs['gain_dict'] = {  # Selecet the gain of the instrumentation AMP in ADC Driver circuit
        2: 0b100,
        5: 0b010,
        10: 0b001,
        55: 0b011,
        60: 0b101,
        63: 0b110,
        64: 0b111,
        1: 0b000,
        None: 0
    }

    configs['FDBK_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    configs['mode_dict'] = {  # select the mode for the ADC driver
        'voltage': 0b00,
        'current': 0b11,
        None: 0b00
    }

    configs['EN_ipump_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    configs['RF_1_Out_dict'] = {
        0: 0,
        1: 1,
        None: 0
    }

    def __init__(self, fpga, TCA_addr_pins_0=0b110, TCA_addr_pins_1=0b000,
                 UID_addr_pins=0b000, DAC_addr_pins=0b001, dc_num=0, version=None):
        # dc_num is the daughter card channel number since there are 0-3 channels
        # DAC_addr_pins = 0b010 since default HW config of Gnd is 0001101 

        self.TCA = [None, None]
        eps_i2cdc = copy.deepcopy(Endpoint.endpoints_from_defines['I2CDC'])
        i2c_eps = Endpoint.advance_endpoints(eps_i2cdc, dc_num)
        self.TCA[0] = TCA9555(fpga=fpga, addr_pins=TCA_addr_pins_0,
                              endpoints=i2c_eps)
        self.TCA[1] = TCA9555(fpga=fpga, addr_pins=TCA_addr_pins_1,
                              endpoints=i2c_eps)
        self.UID = UID_24AA025UID(fpga=fpga, addr_pins=UID_addr_pins,
                                  endpoints=i2c_eps)
        # self.DAC = DAC53401(fpga=fpga, addr_pins=DAC_addr_pins,
        #                     endpoints=i2c_eps)
        self.DAC = DAC101C081(fpga=fpga, addr_pins=DAC_addr_pins,
                            endpoints=i2c_eps)

        self.serial_number = None  # Will get serial code from UID chip in setup()
        self.default_fb_res = 2.1 # defaults especially for when disconnected
        self.default_res = 100
        self.default_cap = 47
        self.default_gain = 1
        self.version=version

        self.config_open_all_relays = {
        'ADC_SEL': "CAL_SIG1",
        'DAC_SEL': "gnd_both",
        'CCOMP': self.default_cap,
        'RF1': self.default_fb_res,  # feedback circuit
        'ADG_RES': self.default_res,
        'PClamp_CTRL': 0, # open relay (default)
        'P1_E_CTRL': 1,  # open relay (disconnect electrode)
        'P1_CAL_CTRL': 0, # open relay (default)
        'P2_E_CTRL': 1,   # open relay
        'P2_CAL_CTRL': 0, # open relay (default)
        'gain': self.default_gain,  # instrumentation amplifier
        'FDBK': 1,
        'mode': "voltage",
        'EN_ipump': 0,
        'RF_1_Out': 1,
        'addr_pins_1': 0b110,
        'addr_pins_2': 0b000}

        self.config_close_cal_relays = {
        'ADC_SEL': "CAL_SIG1",
        'DAC_SEL': "gnd_both",
        'CCOMP': self.default_cap,
        'RF1': self.default_fb_res,  # feedback circuit
        'ADG_RES': self.default_res,
        'PClamp_CTRL': 0, # open relay (default)
        'P1_E_CTRL': 1,  # open relay (disconnect electrode)
        'P1_CAL_CTRL': 1, # close relay (for calibration)
        'P2_E_CTRL': 1,   # open relay
        'P2_CAL_CTRL': 1, # close relay (for calibration)
        'gain': self.default_gain,  # instrumentation amplifier
        'FDBK': 1,
        'mode': "voltage",
        'EN_ipump': 0,
        'RF_1_Out': 1,
        'addr_pins_1': 0b110,
        'addr_pins_2': 0b000}


    def init_board(self, relay_options=None, skip_dac=True):
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
            for ch in [0, 1]:
                dev_addr = self.TCA[ch].ADDRESS_HEADER | (
                        self.TCA[ch].addr_pins << 1) | 0b1
                try:
                    read_out = self.TCA[ch].i2c_read_long(dev_addr, [self.TCA[ch].registers[register_name].address], 2)[
                        1]  # Only the second byte to come back is what we want
                except:
                    read_out = None
                default = self.TCA[ch].registers[register_name].default
                if read_out != default:
                    print(f'TCA_{ch} register: {register_name} FAILED\n    '
                          f'(read_out) {read_out} != (default) {default}')
                    return False

        # Configure clamp
        # Command for Voltage Clamp Feedback loop
        if relay_options=='GND2':
            self.configure_clamp(ADC_SEL='CAL_SIG1', DAC_SEL='gnd_CAL2',
                                CCOMP=47, RF1=3, ADG_RES=10, PClamp_CTRL=1,
                                P1_E_CTRL=1, P1_CAL_CTRL=0, P2_E_CTRL=1,
                                P2_CAL_CTRL=1, gain=2, FDBK=1, mode='voltage',
                                EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110,
                                addr_pins_2=0b000)            
        elif relay_options=='NoCoils':
            self.configure_clamp(ADC_SEL='CAL_SIG1', DAC_SEL='gnd_CAL2',
                                CCOMP=47, RF1=3, ADG_RES=10, PClamp_CTRL=0,
                                P1_E_CTRL=0, P1_CAL_CTRL=0, P2_E_CTRL=0,
                                P2_CAL_CTRL=0, gain=2, FDBK=1, mode='voltage',
                                EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110,
                                addr_pins_2=0b000)            
        else:
            self.configure_clamp(ADC_SEL='CAL_SIG1', DAC_SEL='drive_CAL2',
                                CCOMP=47, RF1=3, ADG_RES=10, PClamp_CTRL=1,
                                P1_E_CTRL=1, P1_CAL_CTRL=0, P2_E_CTRL=1,
                                P2_CAL_CTRL=0, gain=2, FDBK=1, mode='voltage',
                                EN_ipump=0, RF_1_Out=1, addr_pins_1=0b110,
                                addr_pins_2=0b000)

        # UID
        read = self.UID.get_manufacturer_code()
        default = self.UID.registers['MANUFACTURER_CODE'].default
        if read != default:
            print(f'UID MANUFACTURER_CODE FAILED\n    '
                  f'(read) {read} != (default) {default}')
            return False

        read = self.UID.get_device_code()
        print(f'READ UID DEVICE_CODE of \n    '
                  f'(read) {read}')    
        default = self.UID.registers['DEVICE_CODE'].default
        if read != default:
            print(f'UID DEVICE_CODE FAILED\n    '
                  f'(read) {read} != (default) {default}')
            return False

        # DAC
        if not skip_dac:
            read = self.DAC.get_id()
            # Device and Version ID share the same default value across their combined bits
            default = self.DAC.registers['DEVICE_ID'].default
            if read != default:
                print(
                    f'DAC ID FAILED\n    (read) {read} != (default) {default}')
                return False

            # Get serial code
            self.serial_number = self.UID.get_serial_number()
            print(f'Serial Code: {hex(self.serial_number)}')

        return True


    @staticmethod
    def print_config_options():
        print('Compensation capacitor: ')
        print(Clamp.configs['CCOMP_dict'].keys())
        print('Inamp gain: ')
        print(Clamp.configs['gain_dict'].keys())
        print('Feedback gain: ')
        print(Clamp.configs['RF1_dict'].keys())
        print('Feedback gain: ')
        print(Clamp.configs['ADG_RES_dict'].keys())

    def configure_clamp(
            self,
            ADC_SEL=None,
            DAC_SEL=None,
            CCOMP=None,
            RF1=None,
            ADG_RES=None,
            PClamp_CTRL=None,
            P1_E_CTRL=None,
            P1_CAL_CTRL=None,
            P2_E_CTRL=None,
            P2_CAL_CTRL=None,
            gain=None,
            FDBK=None,
            mode=None,
            EN_ipump=None,
            RF_1_Out=None,
            addr_pins_1=0b110,
            addr_pins_2=0b000):

        config_params = Register.get_chip_registers('clamp_configuration')
        """Configures the board using the I/O Expanders."""

        # Define configuration params for mask later
        input_params_1 = {'ADC_SEL': ADC_SEL,
                          'DAC_SEL': DAC_SEL, 'CCOMP': CCOMP, 'RF1': RF1}
        input_params_2 = {'ADG_RES': ADG_RES, 'PClamp_CTRL': PClamp_CTRL, 'P1_E_CTRL': P1_E_CTRL, 'P1_CAL_CTRL': P1_CAL_CTRL,
                          'P2_E_CTRL': P2_E_CTRL, 'P2_CAL_CTRL': P2_CAL_CTRL, 'gain': gain, 'FDBK': FDBK, 'mode': mode, 'EN_ipump': EN_ipump, 'RF_1_Out': RF_1_Out}

        # Get codes from the corresponding dictionaries
        # All dictionaries are set up with a {None: 0} key-value pair for default use
        # Using try, except, finally blocks to catch all unknown arguments
        # This lets us find every mistake the user makes rather than forcing
        # the user to run the program and fix them one at a time
        unknown_arguments = []
        def get_record_unknown(d, k):
            """get method that records any KeyError keys in unknown_arguments list.
            
            Parameters
            ----------
            d : dict
                Dictionary to access.
            k : any
                Key to access dictionary with.
            
            Returns
            -------
            any : value associated with key k, or None.
            """

            try:
                return d[k]
            except KeyError:
                unknown_arguments.append(k)
                return None

        # I/O Expander 1 (self.TCA_0)
        ADC_SEL_code = get_record_unknown(Clamp.configs['ADC_SEL_dict'], ADC_SEL)
        DAC_SEL_code = get_record_unknown(Clamp.configs['DAC_SEL_dict'], DAC_SEL)
        CCOMP_code = get_record_unknown(Clamp.configs['CCOMP_dict'], CCOMP)
        RF1_code = get_record_unknown(Clamp.configs['RF1_dict'], RF1)

        # I/O Expander 2 (self.TCA_1)
        ADG_RES_code = get_record_unknown(Clamp.configs['ADG_RES_dict'], ADG_RES)
        PClamp_CTRL_code = get_record_unknown(Clamp.configs['PClamp_CTRL_dict'], PClamp_CTRL)
        P1_E_CTRL_code = get_record_unknown(Clamp.configs['P1_E_CTRL_dict'], P1_E_CTRL)
        P1_CAL_CTRL_code = get_record_unknown(Clamp.configs['P1_CAL_CTRL_dict'], P1_CAL_CTRL)
        P2_E_CTRL_code = get_record_unknown(Clamp.configs['P2_E_CTRL_dict'], P2_E_CTRL)
        P2_CAL_CTRL_code = get_record_unknown(Clamp.configs['P2_CAL_CTRL_dict'], P2_CAL_CTRL)
        gain_code = get_record_unknown(Clamp.configs['gain_dict'], gain)
        FDBK_code = get_record_unknown(Clamp.configs['FDBK_dict'], FDBK)
        mode_code = get_record_unknown(Clamp.configs['mode_dict'], mode)
        EN_ipump_code = get_record_unknown(Clamp.configs['EN_ipump_dict'], EN_ipump)
        RF_1_Out_code = get_record_unknown(Clamp.configs['RF_1_Out_dict'], RF_1_Out)

        # Raise error for any unrecognized arguments
        if len(unknown_arguments) > 0:
            raise ValueError(f'Unrecognized arguments: {", ".join(unknown_arguments)}')

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
            if input_params_1[key] is None:
                continue
            else:
                mask1 += ((2**config_params[key].bit_width - 1)
                          << config_params[key].bit_index_low)

        mask2 = 0
        for key in input_params_2:
            # If the parameter was not set by the user, do not add it to the mask.
            if input_params_2[key] is None:
                continue
            else:
                mask2 += ((2**config_params[key].bit_width - 1)
                          << config_params[key].bit_index_low)

        # Reverse bytes in masks
        mask1 = (reverse_bits(mask1 // 16**2)
                 << 8) | reverse_bits(mask1 % 16**2)
        mask2 = (reverse_bits(mask2 // 16**2)
                 << 8) | reverse_bits(mask2 % 16**2)

        # Set pins to outputs
        self.TCA[0].configure_pins([0x00, 0x00])
        self.TCA[1].configure_pins([0x00, 0x00])

        # Write messages
        # register_name defaults to 'OUTPUT'
        self.TCA[0].write(message1, mask=mask1)
        self.TCA[1].write(message2, mask=mask2)

        # Read messages
        list_read1 = self.TCA[0].read()
        list_read2 = self.TCA[1].read()
        read1 = (list_read1[0] << 8) | list_read1[1]
        read2 = (list_read2[0] << 8) | list_read2[1]

        # making the read outputs into 16 bits so that they are easier to analyze
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
        log_string = [
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
            f'addr_pins_1 = {addr_pins_1}',
            f'addr_pins_2 = {addr_pins_2}',
            f'Code 1 = {message1}',
            f'Code 2 = {message2}'
        ]
        config_dict = {}
        for i in log_string:
            split_str = i.strip().split('=')
            try:
                config_dict[split_str[0].strip()] = float(split_str[1].strip())
            except:
                config_dict[split_str[0].strip()] = split_str[1].strip()
        del config_dict['Code 1'] # this allows us to reuse the dictionary the next time arround
        del config_dict['Code 2']
        return log_string, config_dict

    def open_all_relays(self):
        log, config = self.configure_clamp(
            **self.config_open_all_relays)
        return log, config 

    def close_cal_relays(self):
        log, config = self.configure_clamp(
            **self.config_close_cal_relays)
        return log, config 
    
    def correct_inamp_gain(self, gain):
        """ 
        The 2nd version of the clamp board using a different part for the instrumentation amplifier
        and the gain setting resistors on the PCB were not changed 
        v1: AD8421
        v2: AD8429 
        """
        if gain == 1:
            return gain 
        
        if self.version==2:            
            res = 9.9e3/(gain-1) # AD8421 -- original version 1 design, but was out of stock for clamp board v2 
            gain = 1+6e3/res     # AD8429 

        # do nothing for other gains
        return gain 



class Daq:
    """Class for the DAQ board.

    DAQ board: https://github.com/lucask07/open_covg_daq_pcb/blob/main/docs/covg_daq_v2.pdf

    Attributes
    ----------
    fpga : FPGA
        The FPGA instance the DAQ board communicates with. This should be
        initiated with init_device() outside the Daq class.
    ddr : DDR3
        The DDR instance used to write hardware driven signals to chips.
    TCA_0 : TCA9555
        First I/O Expander controlling DAC output gain.
    TCA_1 : TCA9555
        Second I/O Expander controlling DAC output gain.
    UID : UID_24AA025UID
        Unique ID chip for serial number and general memory.
    Power : ENABLE GPIOs that control power supplies
        Signals that enable power supplies
    DAC :

    DAC :

    ADC : AD7961

    Methods
    -------
    init_board()

    """

    def __init__(self, fpga, TCA_addr_pins_0=0b000,
                 TCA_addr_pins_1=0b100,
                 UID_addr_pins=0b000,
                 DAC_addr_pins=0b000
                 ):
        self.fpga = fpga
        self.ddr = DDR3(fpga=self.fpga)
        self.serial_number = None  # Will get serial code from UID chip in setup()
        # I2C
        self.TCA = TCA9555.create_chips(fpga=fpga, addr_pins=[TCA_addr_pins_0, TCA_addr_pins_1], endpoints=Endpoint.I2CDAQ_QW)
        self.UID = UID_24AA025UID(
            fpga=fpga, addr_pins=UID_addr_pins, endpoints=Endpoint.I2CDAQ_QW)

        # self.DAC_I2C = DAC53401(fpga=fpga, addr_pins=DAC_addr_pins, endpoints=Endpoint.endpoints_from_defines['I2CDAQ'])
        # SPI
        self.DAC_gp = DAC80508.create_chips(fpga=fpga, number_of_chips=2)
        self.DAC = AD5453.create_chips(fpga=fpga, number_of_chips=6)
        #self.DAC_0, self.DAC_1, self.DAC_2, self.DAC_3, self.DAC_4, self.DAC_5 = AD5453.create_chips(fpga=fpga, number_of_chips=6)
        self.ADC_gp = ADS8686.create_chips(fpga=fpga, number_of_chips=1)[0]
        self.ADC = AD7961.create_chips(fpga=fpga, number_of_chips=4)

        self.current_dac_gain = {}
        default_gain = 200 #TODO - what is the default gain
        for i in range(6):
            self.current_dac_gain[i] = default_gain

        self.parameters = {}
        self.parameters["dac_gain_fs"] = {
            15: 0xF,
            5: 0xE,
            2: 0xD,  # in volts full-scale
            500: 0xB, # in milli-volts full-scale
            200: 0x7,
            0.5: 0xB, # in volts full-scale adding to deprecate mV scaling
            0.2: 0x7
        }  

        # exapander number, nibble_number
        self.parameters["dac_expander_nibble"] = {
            0: (0, 3),
            1: (0, 2),
            2: (0, 1),
            3: (0, 0),
            4: (1, 3),
            5: (1, 2),
        }

        # ISEL bank: (I/O exapander number, nibble_number)
        self.parameters["isel_expander_nibble"] = {
            1: (1, 0),
            2: (1, 1),
        }

        self.parameters["dac_resistors"] = {
            "input": 49.9e3,
            "fixed": 243e3,
            "switched": [121e3, 37.4e3,  8.25e3, 3.24e3],
        }

        self.parameters["ads_map"] = { # first key is daughter-card number, 2nd key is HDMI signal, tuple is ADS converter channel (letter) and number 
            0: {"CAL_ADC": ('A',0), "AMP_OUT": ('A',1)},
            1: {"CAL_ADC": ('B',0), "AMP_OUT": ('A',2)},
            2: {"CAL_ADC": ('B',1), "AMP_OUT": ('A',3)},
            3: {"CAL_ADC": ('A',4), "AMP_OUT": ('B',2)},
        }

        self.parameters["gp_dac_map"] = { # first key is daughter-card number, 2nd key is HDMI signal, tuple is ADS converter channel (letter) and number 
            0: {"CAL": (1,0), "CAL2": None, "UTIL": (1,4)}, #UTIL may not be connected to GP_DAC
            1: {"CAL": (1,1), "CAL2": None, "UTIL": (1,5)}, 
            2: {"CAL": (1,2), "CAL2": (2,2),"UTIL": (2,5)}, #not expecting to use CAL2
            3: {"CAL": (1,3), "CAL2": (2,3),"UTIL": (2,6)},
        }

        self.parameters['fast_dac_map'] = {
            0: 'CC0',
            1: 'CMD0',
            2: 'CC1',
            3: 'CMD1',
            4: 'CMD2',
            5: 'CMD3'
        }

    def set_dac_gain(self, dac_num, gain, bit_value=None):
        """ set the gain of the AD5453 DACs by configuring switch TMUX6111
        Args:
            dac_num: desired frequency
            gain: desired gain options are 15, 5, 2, 500, 200 (see self.parameters["dac_gain_fs"])
            bit_value: instead of using gain dictionary directly specify
                        bits to write to io expander (default of None)

        Returns:
            result of i2c transaction to TCA io expander

        """
        tca_ch = self.parameters["dac_expander_nibble"][dac_num][0]
        tca_nibble = self.parameters["dac_expander_nibble"][dac_num][1]
        if gain not in self.parameters["dac_gain_fs"].keys():
            print(f"Error invalid gain: {gain} in set_dac_gain")
            return -1
        if bit_value is not None:
            gain_val = bit_value
        else:
            gain_val = self.parameters["dac_gain_fs"][gain]
        mask = 0xF << (tca_nibble * 4)
        gain_val = (gain_val) << (tca_nibble * 4)
        print(
            "Setting DAC gain value = 0x{:02X} with mask = 0x{:02X}".format(
                gain_val, mask))
        self.current_dac_gain[dac_num] = gain

        return self.TCA[tca_ch].write(gain_val, mask=mask)

    def predict_gain(self, bit_value):
        """ predict the DAC gain given the bit value written to the io Expander
            depends on the resistor values in the "dac_resistors" dictionary

        Args:
            bit_value: bits to write to io expander (default of None)

        Returns:
            expected gain, currently relative (float)
            TODO: verify with measurements to have an absolute gain
        """
        feedback_inv = 1 / self.parameters["dac_resistors"]["fixed"]
        for idx, sw_res in enumerate(self.parameters["dac_resistors"]["switched"]):
            r = (1 / sw_res) if ((bit_value & (1 << idx)) >> idx) == 0 else 0
            print(r)
            print(feedback_inv)
            feedback_inv = feedback_inv + r
        feedback = 1 / feedback_inv
        gain = feedback / self.parameters["dac_resistors"]["input"]
        print(f"Expected gain of {gain}")
        return gain

    def set_isel(self, port, channels):
        """ set the gain of the TMUX6136 switch so that the Howland current source is the DAC_CAL output
        Args:
            port: The X in IX_SELn. Options are 1 or 2. Determine which general purpose DAC (of two) and which Howland pump is used
            channels: channels to set as list or 'all'. Channels are [0,1,2,3]
                      (channels not included will be cleared -- hence there is no clear function)
        Returns:
            result of i2c transaction to TCA io expander
        """
        tca_ch = self.parameters["isel_expander_nibble"][port][0]
        tca_nibble = self.parameters["isel_expander_nibble"][port][1]

        if channels == 'all':
            val = 0xF
        elif channels is None:
            val = 0x0
        elif isinstance(channels, list):
            val = 0
            for c in channels:
                val += (1<<c)
        else:
            print(f'Error invalid channels for isel {channels}')
            print("Must be a list, 'all' or None ")
            return -1 

        mask = 0xF << (tca_nibble * 4)
        val = (val) << (tca_nibble * 4)
        print(
            "Setting I sel to = 0x{:02X} with mask = 0x{:02X}".format(
                val, mask))

        return self.TCA[tca_ch].write(val, mask=mask)

    def test_impedance(self, resistance, frequency, amplitude, dac80508_num=1, dac80508_chan=4, ads8686_chan_a=7, ads8686_chan_b=3, swap_chan=False, plot=False):
        """Calculate the impedance of a component that is in series with the given resistance.
        
        Uses DDR, DAC80508 to send input voltage, ADS8686 to read output voltage.
        
        Arguments
        ---------
        resistance : float
            The resistance in Ohms of the resistor in series with the unknown impedance.
        frequency : float
            The test frequency in Hertz to use for the input voltage sine wave.
            Values below 200 Hz are not recommended because the rfftfreq
            function will have to round significantly, resulting in larger
            error.
        amplitude : float
            The voltage amplitude of the sign wave. The sine wave will end up
            shifted so all points are positive, but the amplitude will remain
            the same. Because of the shift, amplitude must be 0.0-2.5V.
        dac80508_num : int
            The number of the DAC80508 to use. Expecting 1 or 2 matching with https://github.com/lucask07/open_covg_daq_pcb/blob/main/docs/covg_daq_v2.pdf.
        dac80508_chan : int
            The output channel to send the input voltage on. Expecting 0-7.
        ads8686_chan_a : int
            The "A" side channel of the ADS8686 to receive the input voltage on. Expecting 0-7.
        ads8686_chan_b : int
            The "B" side channel of the ADS8686 to receive the output voltage on. Expecting 0-7.
        swap_chan : bool
            If True, ads8686_chan_b receives input while ads8686_chan_a receives output. False for normal operation.
        plot: bool
            Whether to plot data.

        Returns
        -------
        numpy.complex128, float : the calculated impedance, the calculated frequency that impedance was found at. 
        """

        dac80508_offset = 0x8000
        ads8686_update_period = 4.950495e-06

        # --- Configure DAC80508 for DDR driven ---
        self.DAC_gp[dac80508_num - 1].set_spi_sclk_divide(0x8)
        self.DAC_gp[dac80508_num - 1].set_ctrl_reg(0x3218)
        self.DAC_gp[dac80508_num - 1].set_config_bin(0x00)
        # Change gain and reference divider for DAC80508 to get maximum precision
        # Check (amplitude * 2) because we will shift all values up since DAC80508 cannot output negative values
        if (amplitude * 2) <= 1.25:
            gain = 1
            divide_reference = True
            voltage_range = 1.25
        elif (amplitude * 2) <= 2.5:
            # *2 and /2 is recommended instead of *1 and /1
            gain = 2
            divide_reference = True
            voltage_range = 2.5
        elif (amplitude * 2) <= 5:
            gain = 2
            divide_reference = False
            voltage_range = 5
        else:
            print(f'WARNING: cannot use amplitude {amplitude}V, limiting to maximum 2.5V')
        self.DAC_gp[dac80508_num - 1].set_gain(gain=gain, outputs=dac80508_chan, divide_reference=divide_reference)
        self.DAC_gp[dac80508_num - 1].set_data_mux('DDR')
        # TODO: switch this from AD5453 to DDR3 method
        self.DAC[0].set_clk_divider(divide_value=0x50)  # Need in order to set frequency of input wave correctly

        # --- Configure ADS8686 for read on specified channel ---
        self.ADC_gp.hw_reset(val=False)
        self.ADC_gp.set_host_mode()
        self.ADC_gp.setup()
        self.ADC_gp.set_range(5)
        self.ADC_gp.set_lpf(376)
        if swap_chan is False:
            # Normal operation: "A" side takes input, "B" side takes output
            chan_list = (str(ads8686_chan_a), str(ads8686_chan_b))
            input_side = 'A'
            output_side = 'B'
        else:
            # Reverse operation: "B" side takes input, "A" side takes output
            chan_list = (str(ads8686_chan_b), str(ads8686_chan_a))
            input_side = 'B'
            output_side = 'A'
        codes = self.ADC_gp.setup_sequencer(chan_list=[chan_list])
        self.ADC_gp.write_reg_bridge()
        self.ADC_gp.set_fpga_mode()

        # --- Generate input voltage signal ---
        amplitude_code = from_voltage(voltage=amplitude, num_bits=16, voltage_range=voltage_range, with_negatives=False)
        v_in_code, actual_freq = self.ddr.make_sine_wave(
            amplitude=amplitude_code, frequency=frequency, offset=dac80508_offset, actual_frequency=True)

        # --- Send input signal ---
        # Last 2 bits of first array are first 2 bits of channel for DAC1
        # Second-to-last bit of second array is last bit of channel for DAC1
        # Same for third and fourth arrays but with DAC2
        # dac80508_num should be 1 or 2

        # Clear channel bits
        self.ddr.data_arrays[2 * (dac80508_num - 1)] = np.bitwise_and(self.ddr.data_arrays[2 * (dac80508_num - 1)], 0x3fff).astype(np.uint16)
        self.ddr.data_arrays[2 * (dac80508_num - 1) + 1] = np.bitwise_and(self.ddr.data_arrays[2 * (dac80508_num - 1) + 1], 0x3fff).astype(np.uint16)
        # Set channel bits
        self.ddr.data_arrays[2 * (dac80508_num - 1)] = np.bitwise_or(self.ddr.data_arrays[2 * (dac80508_num - 1)], (dac80508_chan & 0b110) << 13).astype(np.uint16)
        self.ddr.data_arrays[2 * (dac80508_num - 1) + 1] = np.bitwise_or(self.ddr.data_arrays[2 * (dac80508_num - 1) + 1], (dac80508_chan & 0b001) << 14).astype(np.uint16)
        # Last 2 arrays (of 8) are for DAC80508 1 and 2 data only
        self.ddr.data_arrays[5 + dac80508_num] = v_in_code.astype(np.uint16)
        for i in self.ddr.data_arrays:
            print(type(i[0]))
        self.ddr.write_channels()
        self.ddr.write_channels()   # Double write to ensure good output

        # --- Read input and ouput voltage signals ---
        throw_away = 15     # TODO: remove this
        for i in range(throw_away):
            data_stream = self.ADC_gp.stream_mult(twos_comp_conv=False)
        v_in_code = data_stream[input_side]
        v_out_code = data_stream[output_side]

        # --- Calculate impedance across frequencies ---
        # Convert back to voltage
        v_in_voltage = to_voltage(data=v_in_code, num_bits=16, voltage_range=10, use_twos_comp=True)
        v_out_voltage = to_voltage(data=v_out_code, num_bits=16, voltage_range=10, use_twos_comp=True)
        impedance_arr = calc_impedance(v_in=v_in_voltage, v_out=v_out_voltage, resistance=resistance)

        # --- Set up x frequencies ---
        x_freq = rfftfreq(len(v_in_voltage), ads8686_update_period)

        # --- Find nearest x frequency to input frequency ---
        distances_from_actual = [abs(x - actual_freq) for x in x_freq]
        desired_index = distances_from_actual.index(min(distances_from_actual))
        frequency_found = x_freq[desired_index]

        # --- Optionally plot input and output ---
        if plot:
            x = [i * DDR3.UPDATE_PERIOD * 99 for i in range(len(v_in_voltage))]

            # First, codes
            plt.plot(x, v_in_code, c='b', label='v_in')
            plt.plot(x, v_out_code, c='r', label='v_out')
            plt.legend(loc='upper left')
            plt.title('v_in vs. v_out (codes)')
            plt.show()

            # Second, voltages
            plt.plot(x, v_in_voltage, c='b', label='v_in')
            plt.plot(x, v_out_voltage, c='r', label='v_out')
            plt.legend(loc='upper left')
            plt.title('v_in vs. v_out (voltages)')
            plt.show()

            # Third, impedance
            plt.plot(x_freq, np.abs(impedance_arr), c='purple', label='Impedance')
            plt.title('Impedance vs. Frequency')
            plt.show()

        # --- Return impedance at that frequency ---
        return impedance_arr[desired_index], frequency_found


    class Power:

        DEFAULT_PARAMETERS = dict(  # forces keys to string
            WI02_15V_EN=18,
            WI02_1V8_EN=19,
            WI02_3V3_EN=20,
            WI02_5V_EN=21,
            WI02_N15V_EN=22,
            PWR_REG_ADC_EN_WIRE_IN_ADDR=0x02,
            SUPPLY_NAMES=['1V8', '5V', '3V3', '15V', 'N15V']
            )
        endpoints = Endpoint.get_chip_endpoints('GP')

        # def __init__(self, fpga, endpoints,
        #              parameters=DEFAULT_PARAMETERS, debug=False):
        def __init__(self, fpga,
                     parameters=DEFAULT_PARAMETERS, debug=False):

            self.fpga = fpga
            self.parameters = parameters
            #self.endpoints = endpoints  # TODO switch Power to endpoints
            self.debug = debug  # TODO: Turning on debug will show more output

        def supply_on(self, name):
            """ turn a single power supply on
                input:  name is a string. options are 15V, 3V3, 1V8, 5V, N15V
            """
            if name in self.parameters['SUPPLY_NAMES']:
                self.fpga.set_wire_bit(self.parameters['PWR_REG_ADC_EN_WIRE_IN_ADDR'],
                                       self.parameters['WI02_{}_EN'.format(name)])
            else:
                print('{} not in list of power supplies'.format(name))

        def supply_off(self, name):
            """ turn a single power supply on
                input:  name is a string. options are 15V, 3V3, 1V8, 5V, N15V
            """
            if name in self.parameters['SUPPLY_NAMES']:
                return self.fpga.clear_wire_bit(self.parameters['PWR_REG_ADC_EN_WIRE_IN_ADDR'],
                                                self.parameters['WI02_{}_EN'.format(name)])
            else:
                print('{} not in list of power supplies'.format(name))

        def all_on(self):
            """ turn on all supplies following a power-on sequencing procedure

            AD7961 has a power-up sequence:
            When powering up the AD7961 device, first apply 1.8 V (VDD2,
            VIO) to the device, then ramp 5 V (VDD1). Set the reference
            configuration pins, EN0, EN1, and EN2, to the correct values.
            When an internal reference buffer is used (governed by the EN1
            and EN0 values), apply the external reference of 2.048 V to the
            REFIN pin or 5 V/4.096 V to the REF pin.
            """
            # turn on 1.8 V
            self.fpga.set_wire_bit(self.parameters['PWR_REG_ADC_EN_WIRE_IN_ADDR'],
                                   self.parameters['WI02_1V8_EN'])
            # time.sleep unnecessary due to delay of the wire in API calls
            # turn on 5V
            self.fpga.set_wire_bit(self.parameters['PWR_REG_ADC_EN_WIRE_IN_ADDR'],
                                   self.parameters['WI02_5V_EN'])

            # turn on 3.3 V
            self.fpga.set_wire_bit(self.parameters['PWR_REG_ADC_EN_WIRE_IN_ADDR'],
                                   self.parameters['WI02_3V3_EN'])

            # turn on 15V and neg15V simultaneously
            mask = (1 << self.parameters['WI02_15V_EN']) | \
                (1 << self.parameters['WI02_N15V_EN'])
            value = mask
            self.fpga.set_wire(self.parameters['PWR_REG_ADC_EN_WIRE_IN_ADDR'],
                               value, mask)

            return True

        def all_off(self):
            """ turn off all supplies simultaneously
            """
            # create multi-bit mask
            mask = 0
            for name in self.parameters['SUPPLY_NAMES']:
                mask = mask | (1 << self.parameters['WI02_{}_EN'.format(name)])

            value = 0
            self.fpga.set_wire(self.parameters['PWR_REG_ADC_EN_WIRE_IN_ADDR'],
                               value, mask)

            return True

    class GPIO:

        DEFAULT_PARAMETERS = dict(chips=dict(
                ads=0,
                ds0=1,
                ds1=2,
                dfast0=3,
                dfast1=4,
                dfast2=5,
                dfast3=6,
                dfast4=7),
            misc_ads=dict(
                sdoa=0,
                sdob=1,
                convst=2,
                busy=3
            ))

        def __init__(self, fpga, parameters=DEFAULT_PARAMETERS, endpoints=None, debug=False):
            if endpoints is None:
                endpoints = Endpoint.get_chip_endpoints('GPIO')

            self.fpga = fpga
            self.parameters = parameters
            self.endpoints = endpoints
            self.debug = debug  # TODO: Turning on debug will show more output

        def spi_debug(self, chip):
            """Configure the GPIO pins with SPI debug signals.

            Arguments
            ---------
            chip : str
                Abbreviated name of the chip to debug.
                ads
                ds0
                ds1
                dfast0
                dfast1
                dfast2
                dfast3
                dfast4
            """

            if chip not in self.parameters['chips'].keys():
                print('Incorrect chip name in spi_debug')
                return -1
            for spi_signal in ['SCLK', 'CSB', 'SDI']:
                value = self.parameters['chips'][chip]
                ep_name = spi_signal + '_DEBUG'
                self.fpga.set_wire(self.endpoints[ep_name].address,
                                   value << self.endpoints[ep_name].bit_index_low,
                                   mask=(0b111 << self.endpoints[ep_name].bit_index_low))

        def ads_misc(self, pin):
            if pin not in self.parameters['misc_ads'].keys():
                print('Incorrect pin name in ads_misc')
                return -1
            value = self.parameters['misc_ads'][pin]
            ep_name = 'ADS_CONVST_DEBUG'
            return self.fpga.set_wire(self.endpoints[ep_name].address,
                                      value << self.endpoints[ep_name].bit_index_low,
                                      mask=(0b111 << self.endpoints[ep_name].bit_index_low))


class TOF:

    def __init__(self, fpga):
        self.fpga = fpga
        # I2C
        self.TMF = TMF8801(fpga=fpga, addr_pins=0x00, endpoints=Endpoint.I2CDAQ_QW)

class Vsense:
    """
    voltage sense board which only has an offset DAC and no other I2C periperhals 

    will either be connected to a daughter-card socket 
    or jumpered to another daughter-card board 
    
    """
    def __init__(self, fpga, dc_num = 3, DAC_addr_pins=0b001, endpoints=None):
        # dc_num is the daughter card channel number since there are 0-3 channels

        if dc_num is not None:
            eps_i2cdc = copy.deepcopy(Endpoint.endpoints_from_defines['I2CDC'])
            i2c_eps = Endpoint.advance_endpoints(eps_i2cdc, dc_num)
        elif dc_num is None and endpoints is None:
            print('error')
            return -1
        else:
            i2c_eps = endpoints

        self.DAC = DAC101C081(fpga=fpga, addr_pins=DAC_addr_pins,
                            endpoints=i2c_eps)