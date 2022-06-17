from ..interfaces import Endpoint, Register
from I2CController import I2CController


class DAC101C081(I2CController):
    """Class for the DAC101C081.

    Subclass of the I2CController class. Attributes and methods below are
    differences in this class from I2CController only.

    Attributes
    ----------
    ADDRESS_HEADER : int
        7-bit device address with R/W bit space.
    registers : dict
        Name-Register pairs (this chip has only 1 register! PD[13:12], DATA[9:0])
        PD = b00 for normal operation  
    addr_pins : int
        3 LSBs of the 7-bit device address formed alongside the address header
        used to differentiate between different instances using the ADDR pins.
    """

    ADDRESS_HEADER = (0b000_1101 << 1)  # ADR0=Gnd -- Bath Clamp. ADR0 to GND
    # The device address table in the data sheet is strange
    # see here:
    #   https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/955893/dac101c081-dac101c081-i2c-address-selection
    registers = Register.get_chip_registers('DAC101C081')
    addr_pins = 0
    dac_res_bits = 10

    def write(self, data):
        """Write DAC data and set the PD bits to 00
           DAC data should be no greater than 2^{dac_res_bits} - 1
        """
        dev_addr = self.ADDRESS_HEADER | (self.addr_pins << 1)
        if self.dac_res_bits == 10:
            data = data << 2  # for the 10 bit DAC the 2 LSBs are zeros.
        elif self.dac_res_bits == 12:
            pass  # don't need to shift the data
        else:
            raise ValueError('Incorrect DAC resolution in bits')
        # set PD bits to b00 [13:12] also bits 15:14 are do not care
        data = data & 0x0fff
        # Turn data into a list of bytes for i2c_write method
        # equivalent to [((data & 0xff00)>>8), (data & 0x00ff)]
        list_data = [data // (16**2), data % (16**2)]
        self.i2c_write_long(dev_addr, [None], 2, list_data)

    def read(self):
        """Read 2 bytes of data from the chip register"""

        dev_addr = self.ADDRESS_HEADER | (self.addr_pins << 1) | 0b1
        data_list = self.i2c_read_long(dev_addr, [None], 2)
        data = ((data_list[0] & 0x0f) << 6) + (data_list[1] >> 2)
        pd = ((data_list[0] & 0x30) >> 4)
        return data, pd

    def power_down(self):
        data = 0b0010_0000_0000_0000  # this is the 100 kOhm power down mode
        dev_addr = self.ADDRESS_HEADER | (self.addr_pins << 1)

        # Turn data into a list of bytes for i2c_write method
        # equivalent to [((data & 0xff00)>>8), (data & 0x00ff)]
        list_data = [data // (16**2), data % (16**2)]
        self.i2c_write_long(dev_addr, [None], 2, list_data)
