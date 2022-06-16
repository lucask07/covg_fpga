from SPIFifoDriven import SPIFifoDriven

class DAC80508(SPIFifoDriven):
    """Class for SPI DAC chip DAC80508.

    Subclass of the SPIFifoDriven class. Listed methods do not include SPIFifoDriven methods.

    Attributes
    ----------
    WRITE_OPERATION : int
        SPI data prefix for writing to the DAC.
    READ_OPERATION : int
        SPI data prefix for reading from the DAC.
    registers : dict
        Name-Register pairs for the internal registers of the DAC80508.
    data_mux : dict
        Matches data source names in the MUX to their select values.
    """

    default_data_mux = {
        'DDR': 0,
        'host': 1,
        'ads8686_chA': 2,
        'ads8686_chB': 3,  # different for the AD5453
        'ad7961_ch0': 4,
        'ad7961_ch1': 5,
        'ad7961_ch2': 6,
        'ad7961_ch3': 7,
    }

    WRITE_OPERATION = 0x000000
    READ_OPERATION = 0x800000

    registers = Register.get_chip_registers('DAC80508')

    def __init__(self, fpga, master_config=0x3218, endpoints=None, data_mux=default_data_mux):
        # master_config=0x3218 Sets CHAR_LEN=24, Rx_NEG, ASS, IE
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('DAC80508')
        super().__init__(fpga=fpga, master_config=master_config,
                         endpoints=endpoints, data_mux=data_mux)
        self.current_data_mux = None
        self.set_data_mux('host')

    # Method to write to any register on the chip.
    def write_chip_reg(self, register_name, data):
        """Write to any register on the chip."""

        # .get instead of [brackets] because .get will return None if the register name is not in the dictionary
        reg = DAC80508.registers.get(register_name)
        if reg == None:
            print(f'{register_name} not in registers')
            return False

        # 23=0 (write), [22:20]=000 (reserved), [19:16]=A[3:0] (reg address), [15:0]=D[15:0] (data)
        transmission = DAC80508.WRITE_OPERATION + \
            (reg.address << 16) + data

        self.write(transmission)

    def write_voltage(self, voltage, outputs=[0, 1, 2, 3, 4, 5, 6, 7], auto_gain=False):
        """Write the voltage to the outputs of the DAC.

        Parameters
        ----------
        voltage : int or float
            The decimal voltage to write. This will be rounded to a
            representable binary value.
        ouptuts : int or list(int)
            The output or list of outputs to write the voltage to.
        auto_gain : bool
            True to automatically set the gain for the
            outputs, False otherwise.
        """

        if auto_gain:
            if voltage <= 1.25:
                gain = 1
                divide_reference = True
                voltage *= 2  # Double voltage so we can write as if output unaffected
            elif voltage <= 2.5:
                # *2 and /2 is recommended instead of *1 and /1
                gain = 2
                divide_reference = True
                # Don't need to change the voltage here because it is in our expected range
            elif voltage <= 5:
                gain = 2
                divide_reference = False
                voltage /= 2  # Halve voltage so we can write as if output unaffected
            else:
                print(f'ERROR: cannot write voltage {voltage}V, max 5V')
            self.set_gain(gain=gain, outputs=outputs,
                          divide_reference=divide_reference)
            gain_info = {'gain': gain, 'divide_reference': divide_reference}
        else:
            gain_info = {}

        voltage_bin = from_voltage(
            voltage=voltage, num_bits=16, voltage_range=2.5, with_negatives=False)
        if type(outputs) is list:
            for output in outputs:
                self.write_chip_reg('DAC' + str(output), voltage_bin)
        elif type(outputs) is int:
            self.write_chip_reg('DAC' + str(outputs), voltage_bin)

        return gain_info

    def set_config_bin(self, data):
        """Set the configuration register with a binary number."""

        # Write new config
        return self.write_chip_reg('CONFIG', data)

    def set_config(self, ALM_SEL=0, ALM_EN=0, CRC_EN=0, FSDO=0, DSDO=0, REF_PWDWN=0, DAC7_PWDWN=0, DAC6_PWDWN=0, DAC5_PWDWN=0, DAC4_PWDWN=0, DAC3_PWDWN=0, DAC2_PWDWN=0, DAC1_PWDWN=0, DAC0_PWDWN=0):
        """Set the configuration register using keyword arguments."""

        params = [ALM_SEL, ALM_EN, CRC_EN, FSDO,
                  DSDO, REF_PWDWN, DAC7_PWDWN, DAC6_PWDWN, DAC5_PWDWN, DAC4_PWDWN, DAC3_PWDWN, DAC2_PWDWN, DAC1_PWDWN, DAC0_PWDWN]

        # TODO: is this right?
        bit = 13
        data = 0
        for i in range(len(params)):
            data += params[i]*2**bit
        self.set_config_bin(data)

    def set_gain_bin(self, data):
        """Set the gain register with a binary value.

        1 gives a gain of 2 for the output at that bit index (0-7). 0 gives a
        gain of 1.
        The 8th bit from the right is the REFDIV-EN: 1 divides the
        internal reference voltage by 2. 0 leaves the reference voltage
        unaffected.
        """

        return self.write_chip_reg('GAIN', data)

    def set_gain(self, gain, outputs=[0, 1, 2, 3, 4, 5, 6, 7], divide_reference=False):
        """Set the output gain (x1 or x2) and reference divider (VREF=2.5 V).
            Suggested settings are: 
            gain = 2, div_ref = /2 
            gain = 2, div_ref = /1
            gain = 1, div_ref = /1 (not recommended)
            gain = 1, div_ref = /2 

        Parameters
        ----------
        gain : int
            The gain for the outputs. 1 or 2.
        ouptuts : int or list(int)
            The output or list of outputs to set the gain for.
        divide_reference : bool
            True to divide the reference voltage by 2, False to leave the it
            unaffected.
        """

        # The reference divider bit is the 8th bit from the LSB in the gain
        # register. Output gain 0 is 0 bits in, output gain 1 1 bit in, etc.
        if gain != 1 and gain != 2:
            print(f'ERROR: gain value must be 1 or 2. Got {gain}')
        gain_bin = divide_reference << 8
        if type(outputs) is list:
            for output in outputs:
                gain_bin |= (gain - 1) << output
        elif type(outputs) is int:
            gain_bin |= (gain - 1) << outputs
        self.set_gain_bin(data=gain_bin)

    def reset(self):
        """Soft reset the chip."""

        ack = self.write_chip_reg('TRIGGER', 0b1010, 0x000f)
        # if self.debug:
        #     if ack:
        #         print('Reset: SUCCESS')
        #     else:
        #         print('Reset: FAIL')
        # return ack
