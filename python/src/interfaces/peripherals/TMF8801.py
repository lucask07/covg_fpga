from ..interfaces import Endpoint, Register
from ..utils import int_to_list
from I2CController import I2CController
import time


class TMF8801(I2CController):
    """Class for the Time-of-flight I2C device

    Subclass of the I2CController class. Attributes and methods below are
    differences in this class from I2CController only.

    Attributes
    ----------
    ADDRESS : int
        7-bit device address with R/W bit space 
    registers : dict
        Name-Register pairs for the internal registers of the chip.
    """

    ADDRESS = 0b0100_0001 << 1
    registers = Register.get_chip_registers('TMF8801')
    apps = {'measure': 0xC0, 'bootloader': 0x80}
    MULTI_BYTE_ORDER = 'LSB_1st'

    def write(self, data, register_name):
        """Write data to any register on the chip.
            first reads to enable writing of (just) bit-fields within the register
        """

        dev_addr = self.ADDRESS
        register = self.registers[register_name]
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
        list_data = int_to_list(new_data)
        number_of_bytes = len(list_data)
        list_data_str = ''.join(" ".join(f'0x{x:02x}' for x in list_data))
        print(
            f'i2c write long: 0x{dev_addr:02x}, reg addr 0x{register.address:02x}, data {list_data_str}')
        self.i2c_write_long(
            dev_addr, [register.address], number_of_bytes, list_data)

    def read(self, register_name, number_of_bytes=None):
        """Return data from any register on the chip."""

        dev_addr = self.ADDRESS
        register = self.registers[register_name]
        # This is the total number of bytes to read
        byte_number = (register.bit_index_high // 8) + 1
        # e.g. 16-bit register = 2 bytes, i2c_read_long starts at the MSB so we read 2 bytes to get Byte 0
        if number_of_bytes is None:
            number_of_bytes = byte_number
        # print(f'Read slave address: 0x{dev_addr:02x}, reg addr 0x{register.address:02x}')
        read_back_list = self.i2c_read_long(
            dev_addr, [register.address], number_of_bytes)

        # Turn the list into an integer
        read_back_data = 0
        if read_back_list == None:
            return None

        if self.MULTI_BYTE_ORDER == 'MSB_1st':
            for byte in read_back_list:
                # print('Readback byte of 0x{:02X}'.format(byte))
                read_back_data <<= 8
                read_back_data |= byte
        elif self.MULTI_BYTE_ORDER == 'LSB_1st':
            for byte in read_back_list[::-1]:  # flip list order
                # print('Readback byte of 0x{:02X}'.format(byte))
                read_back_data <<= 8
                read_back_data |= byte

        # Get only the bits for the specified register from what was read back.
        desired_bits = 0
        for bit in range(register.bit_index_high, register.bit_index_low - 1, -1):
            desired_bits += 0x1 << bit
        desired_data = (read_back_data
                        & desired_bits) >> register.bit_index_low

        return desired_data

    def power_down_high_impedance(self):
        """Power down the DAC output to high impedance (default)."""

        pass
        # self.write(0b10, 'DAC_PDN')

    def get_id(self):
        """Return the device ID and rev ID as one integer."""

        device_id = self.read('ID')
        version_id = self.read('REVID')
        return (device_id << self.registers['ID'].bit_index_low) | (version_id << self.registers['ID'].bit_index_low)

    def cpu_reset(self):
        self.write(1, 'CPU_RESET')

    def cpu_ready(self):
        return self.read('CPU_READY', 1)

    def load_app(self, app='measure'):

        if app == 'measure':
            val = 0xC0
        elif app == 'bootloader':
            val = 0x80
        self.write(val, 'APPREQID')

        return self.read('APPID')

    def read_app(self):

        appid = self.read('APPID')
        appname = list(self.apps.keys())[list(self.apps.values()).index(appid)]
        print(f'In app {appname}')
        return appid

    def rom_fw_version(self):
        rev_major = self.read('APPREV_MAJOR', number_of_bytes=1)
        rev_minor = self.read('APPREV_MINOR', number_of_bytes=1)
        patch = self.read('APPREV_PATCH', number_of_bytes=1)

        print(f'major: {rev_major}, minor: {rev_minor}, patch: {patch}')

        return rev_major, rev_minor, patch

    def bl_command(self, cmd):

        appid = self.read('APPID')
        if appid == self.apps['bootloader']:
            print('cannot send boatloader command when in measure app')
            return 0
        if cmd == 'ramremap_reset':
            val = 0x11
        elif cmd == 'download_init':
            val = 0x14

        self.write(val, 'CMD_DATA7')

    def ram_write_status(self):
        # TODO: Host_Driver_Comm document suggests this reads back 3 bytes
        return self.read('CMD_DATA7', number_of_bytes=3)

    def download_init(self):

        dev_addr = self.ADDRESS
        reg_addr = self.registers['CMD_DATA7'].address
        # TODO: why 0x29 - specified by host driver comms
        data = [0x14, 0x01, 0x29, 0xC1]
        self.i2c_write_long(dev_addr, [reg_addr],
                            len(data), data)

    def ramremap_reset(self):

        dev_addr = self.ADDRESS
        reg_addr = self.registers['CMD_DATA7'].address
        data = [0x11, 0x00, 0xEE]
        self.i2c_write_long(dev_addr, [reg_addr],
                            len(data), data)

    def read_dist_peak(self):

        dev_addr = self.ADDRESS
        reg_addr = self.registers['DISTANCE_PEAK'].address
        num_bytes = self.registers['DISTANCE_PEAK'].bit_width//8
        return self.i2c_read_long(dev_addr, [reg_addr],
                                  data_length=num_bytes)

    def read_data(self):
        """ For correctly updating of these registers by TMF8801, an I²C block read starting from address 0x1D
        until 0x27 shall be done.
        0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27"""

        dev_addr = self.ADDRESS
        reg_addr = self.registers['STATUS'].address

        read_data = self.i2c_read_long(dev_addr, [reg_addr],
                                       data_length=11)

        vals = {'status': read_data[0],
                'register_contents': read_data[1],
                'transaction_id': read_data[2],
                'result_num': read_data[3],
                'result_info': read_data[4],
                'dist_mm': read_data[5] + (read_data[6] << 8),
                'sys_clk': read_data[7] + (read_data[8] << 8) + (read_data[9] << 16) + (read_data[10] << 24)}
        vals['sys_clk_seconds'] = vals['sys_clk']*0.2e-6
        return vals, read_data

    def read_by_addr(self, reg_addr, num_bytes=1):
        dev_addr = self.ADDRESS
        return self.i2c_read_long(dev_addr, [reg_addr],
                                  data_length=num_bytes)

    def factory_calibration(self, filename=None):
        """
        Perform factory calibration and return 14 bytes of data
        See AN000597 -- Factor Calibration 8.1

        Calibration Environment: Device has to be in the final (correct) optical stack
        Clear glass (no smudge on the glass)
        No target in front of the device within 40 cm (see datasheet)
        Dark room or low ambient light
        """
        print('Factory calibration: device should be in dark room with no objects within 40 cm')

        self.write(0x0A, 'COMMAND')  # Command is register 0x10
        time.sleep(2)
        cal_done = 0
        count = 0
        while (cal_done != 0x0A) and (count < 20):
            cal_done = self.read('REGISTER_CONTENTS')
            time.sleep(0.1)
            count = count + 1
            print(f'Cal done 0x{cal_done:02x}')

        cal_data = self.read_by_addr(0x20, num_bytes=14)
        print('Calibration data')
        for d in cal_data:
            print(d)

        with open(filename, 'w') as f:
            f.write(','.join(cal_data))

        return cal_data
