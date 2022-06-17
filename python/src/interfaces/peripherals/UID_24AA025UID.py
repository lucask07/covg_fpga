from ..interfaces import Endpoint, Register
from ..utils import int_to_list
from I2CController import I2CController

class UID_24AA025UID(I2CController):
    """Class for the ID chip 24AA025UID.

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

    ADDRESS_HEADER = 0b10100000
    registers = Register.get_chip_registers('24AA025UID')

    def write(self, data, word_address=0x00, num_bytes=None):
        """Write data into memory at word_address."""

        dev_addr = UID_24AA025UID.ADDRESS_HEADER | (self.addr_pins << 1)
        print(
            f'word_address: {hex(word_address)}\ndata: {hex(data)}\nnum_bytes: {num_bytes}')

        # Convert data into a list
        if num_bytes is None:
            # User did not specify a number of bytes
            list_data = int_to_list(integer=data)
            num_bytes = len(list_data)
        else:
            # User specified a number of bytes
            list_data = int_to_list(integer=data, num_bytes=num_bytes)

        if list_data is False:
            # int_to_list returns False when the data is longer than the number of bytes
            print('ERROR: data exceeds given number of bytes')
            return False

        if num_bytes > 16:
            # After 16 bytes (1 page), the UID chip will rollover and overwrite data from ealier.
            # To fix this, we start a new I2C write command at the next page
            self.i2c_write_long(devAddr=dev_addr, regAddr=[
                                word_address], data_length=16, data=list_data[:16])
            # We can recursively call this function instead of looping through multiple times.
            # recurse_data = data % (0x1 << (8 * (num_bytes - 16)))
            recurse_data = data
            for i in range(16):
                recurse_data -= list_data[i] << (8 * i)
            recurse_data >>= 16 * 8
            # print(f'{data} % {(0x1 << (8 * (num_bytes - 16)))} = {recurse_data}')
            self.write(data=recurse_data, word_address=(word_address
                       + 16) % 0x80, num_bytes=num_bytes - 16)
            return True

        # Data is no more than 16 bytes (1 page) and can be written with 1 I2C command.
        self.i2c_write_long(devAddr=dev_addr, regAddr=[
                            word_address], data_length=num_bytes, data=list_data)
        return True

    def read(self, word_address=0x00, words_read=1):
        """Return words_read words of data from memory at word_address."""

        # A word is a byte, 8 bits
        dev_addr = UID_24AA025UID.ADDRESS_HEADER | (
            self.addr_pins << 1) | 0b1
        # Bug when reading more than 64 bytes, only 128 bytes possible so check and split to 2 operations
        if words_read > 64:
            d0 = self.i2c_read_long(dev_addr, [word_address], 64)
            d1 = self.i2c_read_long(
                dev_addr, [word_address + 64], words_read - 64)
            return d0 + d1
        return self.i2c_read_long(dev_addr, [word_address], words_read)

    def get_serial_number(self):
        """Return the unique 32-serial number stored in memory on the chip."""

        serial_list = self.read(
            word_address=UID_24AA025UID.registers['SERIAL_NUMBER'].address, words_read=4)
        serial_number = 0
        for byte in serial_list:
            serial_number <<= 8
            serial_number |= byte

        return serial_number

    def get_manufacturer_code(self):
        """Return the chip's manufacturer code.

        For the chips we are using, it should be 0x29.
        """

        return self.read(word_address=UID_24AA025UID.registers['MANUFACTURER_CODE'].address)[0]

    def get_device_code(self):
        """Return the chip's device code.

        For the chips we are using, it should be 0x41.
        """

        return self.read(word_address=UID_24AA025UID.registers['DEVICE_CODE'].address)[0]
