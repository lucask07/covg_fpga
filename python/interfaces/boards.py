"""Module implementing interfaces module for sets of chips on a board.

This module serves to organize instantiations of chips from the interfaces
module for use in boards common to the project. This allows simpler top level
instantiation and the ability to more easily swap to a different board.

August 2021

Abe Stroschein, ajstroschein@stthomas.edu
"""

from interfaces.interfaces import *
from interfaces.interfaces import Endpoint
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
                    RF_1_Out=None, addr_pins_1=0b110, addr_pins_2=0b000, dc_num=0)
        Sets the I/O Expanders according to the arguments given.
    """

    def __init__(self, fpga, TCA_addr_pins_0=0b110, TCA_addr_pins_1=0b000,
                 UID_addr_pins=0b000, DAC_addr_pins=0b000, dc_num=0):
        # dc_num is the daughter card channel number since there are 0-3 channels

        self.TCA = [None, None]
        self.TCA[0] = TCA9555(fpga=fpga, addr_pins=TCA_addr_pins_0,
                              endpoints=advance_endpoints_bynum(Endpoint.endpoints_from_defines['I2CDC'], dc_num))
        self.TCA[1] = TCA9555(fpga=fpga, addr_pins=TCA_addr_pins_1,
                              endpoints=advance_endpoints_bynum(Endpoint.endpoints_from_defines['I2CDC'], dc_num))
        self.UID = UID_24AA025UID(fpga=fpga, addr_pins=UID_addr_pins,
                                  endpoints=advance_endpoints_bynum(Endpoint.endpoints_from_defines['I2CDC'], dc_num))
        self.DAC = DAC53401(fpga=fpga, addr_pins=DAC_addr_pins,
                            endpoints=advance_endpoints_bynum(Endpoint.endpoints_from_defines['I2CDC'], dc_num))
        self.serial_number = None  # Will get serial code from UID chip in setup()

    def init_board(self, skip_dac=True):
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

    def configure_clamp(self, ADC_SEL=None, DAC_SEL=None, CCOMP=None, RF1=None,
                        ADG_RES=None, PClamp_CTRL=None, P1_E_CTRL=None,
                        P1_CAL_CTRL=None, P2_E_CTRL=None, P2_CAL_CTRL=None,
                        gain=None, FDBK=None, mode=None, EN_ipump=None,
                        RF_1_Out=None, addr_pins_1=0b110, addr_pins_2=0b000):
        config_params = Register.get_chip_registers('clamp_configuration')
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
            10: 0b100,
            33: 0b010,
            100: 0b110,
            332: 0b001,
            1000: 0b101,
            3000: 0b011,
            10000: 0b111,
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
            1: 0b000
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


class Daq:
    """Class for the DAQ board.

    DAQ board: https://github.com/lucask07/open_covg_daq_pcb/blob/main/docs/covg_daq_v2.pdf

    Attributes
    ----------
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
        self.serial_number = None  # Will get serial code from UID chip in setup()
        # I2C
        i2c_eps = advance_endpoints_bynum(
            Endpoint.endpoints_from_defines['I2CDAQ'], 1)
        self.TCA = [None, None]
        self.TCA[0] = TCA9555(
            fpga=fpga, addr_pins=TCA_addr_pins_0, endpoints=i2c_eps)
        self.TCA[1] = TCA9555(
            fpga=fpga, addr_pins=TCA_addr_pins_1, endpoints=i2c_eps)
        self.UID = UID_24AA025UID(
            fpga=fpga, addr_pins=UID_addr_pins, endpoints=i2c_eps)

        # Endpoint advancing is not working with advances that are not a full 32 bits
        for ch in [0, 1]:
            self.TCA[ch].endpoints['IN'].bit_index_high = 32
            self.TCA[ch].endpoints['IN'].bit_index_low = 16

            self.TCA[ch].endpoints['OUT'].bit_index_high = 16
            self.TCA[ch].endpoints['OUT'].bit_index_low = 8
        self.UID.endpoints['OUT'].bit_index_high = 16
        self.UID.endpoints['OUT'].bit_index_low = 8
        self.UID.endpoints['IN'].bit_index_high = 32
        self.UID.endpoints['IN'].bit_index_low = 16

        # self.DAC_I2C = DAC53401(fpga=fpga, addr_pins=DAC_addr_pins, endpoints=Endpoint.endpoints_from_defines['I2CDAQ'])
        # SPI
        self.DAC_gp = []
        self.DAC_gp = DAC80508.create_chips(fpga=fpga, number_of_chips=2)
        for ch in [0,1]:
            self.DAC_gp[ch].channel = ch
        self.DAC = []
        self.DAC = AD5453.create_chips(fpga=fpga, number_of_chips=6)
        for i in range(len(self.DAC)):
            self.DAC[i].channel = i  # TODO: fix this hack in the create chips
        #self.DAC_0, self.DAC_1, self.DAC_2, self.DAC_3, self.DAC_4, self.DAC_5 = AD5453.create_chips(fpga=fpga, number_of_chips=6)
        # TODO: does this use a "channel"
        self.ADC_gp = ADS8686.create_chips(fpga=fpga, number_of_chips=1)
        self.ADC = []
        self.ADC = AD7961.create_chips(fpga=fpga, number_of_chips=4)
        for i in range(len(self.ADC)):
            self.ADC[i].chan = i  # TODO: fix this hack in the create chips

        self.parameters = {}
        self.parameters["dac_gain_fs"] = {
            15: 0xF,
            5: 0xE,
            2: 0xD,  # in volts full-scale
            500: 0xB,
            200: 0x7,
        }  # in milli-volts full-scale

        # exapander number, nibble_number
        self.parameters["dac_expander_nibble"] = {
            0: (0, 3),
            1: (0, 2),
            2: (0, 1),
            3: (0, 0),
            4: (1, 3),
            5: (1, 2),
        }

        self.parameters["dac_resistors"] = {
            "input": 49.9e3,
            "fixed": 243e3,
            "switched": [121e3, 37.4e3,  8.25e3, 3.24e3],
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
