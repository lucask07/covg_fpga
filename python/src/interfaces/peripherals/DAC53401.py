from ..interfaces import Endpoint, Register
from ..utils import int_to_list, from_voltage
from .I2CController import I2CController

class DAC53401(I2CController):
    """Class for the I2C DAC chip DAC53401.

    Subclass of the I2CController class. Attributes and methods below are
    differences in this class from I2CController only.

    Attributes
    ----------
    ADDRESS_HEADER : int
        7-bit device address with R/W bit space and 4 MSBs filled in specific
        to this chip. The rest is left as 0 to be filled in later.
    registers : dict
        Name-Register pairs for the internal registers of the TCA9555 chip.
    addr_pins : int
        3 LSBs of the 7-bit device address formed alongside the address header
        used to differentiate between different instances of the TCA9555 chip.
    """

    ADDRESS_HEADER = 0b10010000
    registers = Register.get_chip_registers('DAC53401')

    #        Address Pins Guide
    # Slave Address   |   A0 Pin
    #           000   |   AGND
    #           001   |   VDD
    #           010   |   SDA
    #           011   |   SCL

    def write(self, data, register_name='DAC_DATA'):
        """Write data to any register on the chip."""

        dev_addr = DAC53401.ADDRESS_HEADER | (self.addr_pins << 1)
        register = DAC53401.registers[register_name]
        data <<= register.bit_index_low

        # Mask only the bits for the specified register.
        mask = 0
        for bit in range(register.bit_index_high, register.bit_index_low - 1, -1):
            mask |= 0x1 << bit

        # Compare with current data to mask unchanged values
        read_out = self.read(register_name)
        if read_out == None:
            print('Read for masking FAILED')
            return False
        new_data = (data & mask) | (read_out & ~mask)

        # Turn data into a list of bytes for i2c_write method
        # Essentially round up to the closest byte
        #number_of_bytes = (register.bit_width + 7) // 8
        list_data = int_to_list(new_data)
        number_of_bytes = len(list_data)
        self.i2c_write_long(
            dev_addr, [register.address], number_of_bytes, list_data)

    def read(self, register_name='DAC_DATA'):
        """Return data from any register on the chip."""

        dev_addr = DAC53401.ADDRESS_HEADER | (self.addr_pins << 1)
        register = DAC53401.registers[register_name]
        # Ex. 16-bit register: | Byte 1 [15:8] | Byte 0 [7:0] |
        byte_number = register.bit_index_high // 8
        # 16-bit register = 2 bytes, i2c_read_long starts at the MSB so we read 2 bytes to get Byte 0
        number_of_bytes = 2 - byte_number
        read_back_list = self.i2c_read_long(
            dev_addr, [register.address], number_of_bytes)

        # Turn the list into an integer
        read_back_data = 0
        if read_back_list == None:
            return None
        # First byte in the list is the MSB, shift and append the next byte
        for byte in read_back_list:
            print('Readback byte of {:02X}'.format(byte))
            read_back_data <<= 8
            read_back_data |= byte
        # Get only the bits for the specified register from what was read back.
        desired_bits = 0
        for bit in range(register.bit_index_high, register.bit_index_low - 1, -1):
            desired_bits += 0x1 << bit
        desired_data = (read_back_data
                        & desired_bits) >> register.bit_index_low

        return desired_data

    def write_voltage(self, voltage):
        """Write a voltage output from the DAC."""

        voltage_data = from_voltage(
            voltage=voltage, num_bits=10, voltage_range=5, with_negatives=False)

        self.write(voltage_data, 'DAC_DATA')

    def enable_internal_reference(self):
        """Enable the DAC's internal reference.

        This is necessary to set the gain value.
        """

        self.write(0x1, 'REF_EN')

    def set_gain(self, gain):
        """Set the DAC's output gain value.

        Gain can be set to 1.5x, 2x, 3x, or 4x the internal reference.
        Internal reference must be enabled.
        """

        gain_dict = {
            1.5: 0b00,
            2: 0b01,
            3: 0b10,
            4: 0b11
        }

        gain_code = gain_dict.get(gain)
        if gain_code == None:
            print('Invalid gain')
            return False
        self.write(gain_code, 'DAC_SPAN')

    def get_gain(self):
        """Return the DAC's current output gain value."""

        gain_dict = {
            0b00: 1.5,
            0b01: 2,
            0b10: 3,
            0b11: 4
        }

        gain_code = self.read('DAC_SPAN')
        return gain_dict.get(gain_code)

    def config_func(self, function_name):
        """Configure the function generator.

        'triangle': Triangle wave between MARGIN_HIGH code to MARGIN_LOW code
            with slope defined by SLEW_RATE.
        'sawtooth_falling': Saw-Tooth wave between MARGIN_HIGH code to
            MARGIN_LOW code with slope defined by SLEW_RATE and immeidate falling edge.
        'sawtooth_rising': Saw-Tooth wave between MARGIN_HIGH code to
            MARGIN_LOW code with slope defined by SLEW_RATE and immeidate rising edge.
        'square': Square wave between MARGIN_HIGH code to MARGIN_LOW code with
            pulse high and low period defined by defined by SLEW_RATE.
        """

        func_dict = {
            'triangle': 0b00,
            'sawtooth_falling': 0b01,
            'sawtooth_rising': 0b10,
            'square': 0b11
        }

        func_code = func_dict.get(function_name.lower())
        if func_code == None:
            print('Invalid function name')
            return False
        self.write(func_code, 'FUNC_CONFIG')

    def start_func(self):
        """Start function generation.

        Waveform configured through config_func() and config_margins() functions.
        """
        self.write(0b1, 'START_FUNC_GEN')

    def stop_func(self):
        """Stop function generation."""

        self.write(0b0, 'START_FUNC_GEN')

    def config_margins(self, margin_high=None, margin_low=None):
        """Configure margin high and low values."""

        if margin_high != None:
            self.write(margin_high, 'MARGIN_HIGH')

        if margin_low != None:
            self.write(margin_low, 'MARGIN_LOW')

    def config_step(self, step):
        """Configure the number of bits to step through."""

        step_dict = {
            1: 0b000,
            2: 0b001,
            3: 0b010,
            4: 0b011,
            6: 0b100,
            8: 0b101,
            16: 0b110,
            32: 0b111
        }

        step_code = step_dict.get(step)
        if step_code == None:
            print('Invalid step')
            return False
        self.write(step_code, 'CODE_STEP')

    def config_rate(self, rate):
        """Configure the rate to step through each bit."""

        # Instead of asking the user to type in the timing, the rates are organized slowest to fastest and numbered 1-16
        rate_dict = {
            1: 0b1011,  # 1638.4 * 1.75 us
            2: 0b1010,  # 1638.4 * 1.50 us
            3: 0b1001,  # 1638.4 * 1.25 us
            4: 0b1000,  # 1638.4        us
            5: 0b0111,  # 204.8  * 1.75 us
            6: 0b0110,  # 204.8  * 1.50 us
            7: 0b0101,  # 204.8  * 1.25 us
            8: 0b0100,  # 204.8         us
            9: 0b0011,  # 25.6   * 1.75 us
            10: 0b0010,  # 25.6   * 1.50 us
            11: 0b0001,  # 25.6   * 1.25 us
            12: 0b0000,  # 25.6          us
            13: 0b1100,  # 12            us
            14: 0b1101,  # 8             us
            15: 0b1110,  # 4             us
            16: 0b1111  # None
        }

        rate_code = rate_dict.get(rate)
        if rate_code == None:
            print('Invalid rate')
            return False
        self.write(rate_code, 'SLEW_RATE')

    def reset(self):
        """Reset the chip using a software reset."""

        self.write(0b1010, 'SW_RESET')

    def lock(self):
        """Lock the registers of the device so they cannot be changed."""

        self.write(0b1, 'DEVICE_LOCK')

    def unlock(self):
        """Unlock the registers of the device so they can be changed again."""

        self.write(0b0101, 'DEVICE_UNLOCK_CODE')

    def power_up(self):
        """Power up the DAC output."""

        self.write(0b00, 'DAC_PDN')

    def power_down_10k(self):
        """Power down the DAC output to 10K ohms."""

        self.write(0b01, 'DAC_PDN')

    def power_down_high_impedance(self):
        """Power down the DAC output to high impedance (default)."""

        self.write(0b10, 'DAC_PDN')

    def get_id(self):
        """Return the device ID and version ID as one integer."""

        device_id = self.read('DEVICE_ID')
        version_id = self.read('VERSION_ID')
        return (device_id << DAC53401.registers['DEVICE_ID'].bit_index_low) | (version_id << DAC53401.registers['VERSION_ID'].bit_index_low)
