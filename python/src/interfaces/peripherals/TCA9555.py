from ..interfaces import Endpoint, Register
from .I2CController import I2CController


class TCA9555(I2CController):
    """Class for the I/O Expander TCA9555.

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

    ADDRESS_HEADER = 0b0100_0000
    registers = Register.get_chip_registers('TCA9555')

    def configure_pins(self, data):
        """Configure the chip's pins as inputs (1's) or outputs (0's)."""

        # Inputs = 1
        # Outputs = 0
        dev_addr = self.ADDRESS_HEADER + (self.addr_pins << 1)
        self.i2c_write_long(
            dev_addr, [TCA9555.registers['CONFIG'].address], 2, data)

    def write(self, data, register_name='OUTPUT', mask=0xffff):
        """Write 2 bytes of data to the pins."""

        dev_addr = self.ADDRESS_HEADER | (self.addr_pins << 1)

        # Compare with current data to mask unchanged values
        if mask == 0xffff:
            new_data = data
        else:
            read_out = self.read()
            current_data = (read_out[0] << 8) | read_out[1]
            if current_data == None:
                print('Read for masking FAILED')
                return False
            new_data = (data & mask) | (current_data & ~mask)

        # Turn data into a list of bytes for i2c_write method
        list_data = [new_data // (16**2), new_data % (16**2)]
        self.i2c_write_long(
            dev_addr, [TCA9555.registers[register_name].address], 2, list_data)

    def read(self, register_name='INPUT'):
        """Read 2 bytes of data from the pins."""

        dev_addr = self.ADDRESS_HEADER | (self.addr_pins << 1) | 0b1
        return self.i2c_read_long(dev_addr, [TCA9555.registers[register_name].address], 2)
