"""Module for configuring OpalKelly XEM7310
and use it as an I2C controller, SPI controller, and Serial LVDS controller.

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu
August 2021
"""

import ok
import numpy as np
import pandas as pd
import os
import sys
import time
from collections import namedtuple
from interfaces.utils import gen_mask, twos_comp, test_bit, int_to_list
import copy

class Register:
    """Class for internal registers on a device.

    Attributes
    ----------
    address : int
        Address location of the register.
    default : int
        Default value of the register.
    bit_index_high : int
        Index of the MSB in the register.
    bit_index_low : int
        Index of the LSB in the register.
    bit_width : int
        Width of the register in bits.

    Methods
    -------
    get_chip_registers(sheet, workbook_path=None)
        Returns a dictionary of Registers from a page in an Excel spreadsheet.
    """

    def __init__(self, address, default, bit_index_high, bit_index_low, bit_width):
        self.address = address
        self.default = default
        self.bit_index_high = bit_index_high
        self.bit_index_low = bit_index_low
        self.bit_width = bit_width

    def __str__(self):
        str_rep = 'Register with address 0x{:0x}, bit-high {} to low {}, width = {}'.format(
            self.address, self.bit_index_high, self.bit_index_low, self.bit_width)
        return str_rep

    @classmethod
    def get_chip_registers(cls, sheet, workbook_path=None):
        """Return a dictionary of Registers from a page in an Excel spreadsheet."""

        if workbook_path == None:
            workbook_path = os.getcwd()
            # The Registers spreadsheet is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
            for i in range(15):
                if os.path.basename(workbook_path) == 'covg_fpga':
                    workbook_path = os.path.join(workbook_path, 'Registers.xlsx')
                    break
                else:
                    # If we aren't in covg_fpga, move up a folder and check again
                    workbook_path = os.path.dirname(workbook_path)

        reg_dict = {}
        sheet_data = pd.read_excel(workbook_path, sheet)
        for row in range(len(sheet_data)):
            row_data = sheet_data.iloc[row]
            reg_dict[row_data['Name']] = Register(
                address=int(row_data['Hex Address'], 16),
                default=int(row_data['Default Value'], 16),
                bit_width=int(row_data['Bit Width']),
                bit_index_high=(None if row_data['Bit Index (High)'] == 'None' else int(
                    row_data['Bit Index (High)'])),  # Bit Index of None means the register takes up the whole endpoint
                bit_index_low=(None if row_data['Bit Index (Low)'] == 'None' else int(row_data['Bit Index (Low)'])))
        return reg_dict


class Endpoint:
    """Class for Opal Kelly endpoints on the FPGA.

    Attributes
    ----------
    endpoints_from_defines : dict
        Dictionary of each group of endpoints paired with inner dictionaries
        of endpoint names to Endpoint objects, starts empty.
    address : int
        Address location of the Endpoint.
    bit_index_low : int
        Index of the LSB of the Endpoint.
    bit_index_high : int
        Index of the MSB of the Endpoint.
    bit_width : int
        Width of the Endpoint in bits.
    gen_bit : bool
        Whether to increment the bits when incrementing the endpoint.
    gen_address : bool
        Whether to increment the address when incrementing the endpoint.

    Methods
    -------
    update_endpoints_from_defines(ep_defines_path=None)
        Return and store Endpoints in ep_defines.v in endpoints_from_defines.
    get_chip_endpoints(chip_name)
        Return the dictionary of Endpoints for a specific chip or group.
    increment_endpoints(endpoints_dict)
        Increment all Endpoints in endpoints_dict according to their gen_bit
        and gen_address values.
    """

    endpoints_from_defines = dict()

    def __init__(self, address, bit_index_low, bit_width, gen_bit, gen_address):
        self.address = address
        self.bit_index_low = bit_index_low
        self.bit_index_high = bit_index_low + bit_width
        self.bit_width = bit_width
        self.gen_bit = gen_bit
        self.gen_address = gen_address

    def __str__(self):
        str_rep = 'Endpoint at address 0x{:0x}, [high {} to low {}]'.format(
            self.address, self.bit_index_high, self.bit_index_low)
        return str_rep

    @classmethod
    def update_endpoints_from_defines(cls, ep_defines_path=None):
        """Store and return a dictionary of Endpoints for each chip in ep_defines.v."""

        # Find ep_defines.v path
        if ep_defines_path == None:
            ep_defines_path = os.getcwd()
            # The Registers spreadsheet is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
            for i in range(15):
                if os.path.basename(ep_defines_path) == 'covg_fpga':
                        ep_defines_path = os.path.join(ep_defines_path, 'fpga_XEM7310', 'fpga_XEM7310.srcs', 'sources_1', 'ep_defines.v')
                        break
                else:
                    # If we aren't in covg_fpga, move up a folder and check again
                    ep_defines_path = os.path.dirname(ep_defines_path)

        # Get all lines
        with open(ep_defines_path, 'r') as file:
            lines = file.readlines()

        # Get all the endpoints from the lines
        for line in lines:
            # Check if the line defines an endpoint
            pieces = line.split(' ')
            # Ex. line = "`define AD7961_PIPE_OUT_GEN_ADDR 8'hA1 // address=TEST_ADDRESS bit_width=32"
            #   pieces = ["`define", "AD7961_PIPE_OUT_GEN_ADDR", "8'hA1", "//", "address=TEST_ADDRESS", "bit_width=32"]
            if pieces[0] != '`define':
                # Line does not define an endpoint, skip
                continue

            # Extract data from definition
            # Class name
            class_name_end = pieces[1].find('_')
            if class_name_end == -1:
                # .find() returns -1 if not found, without an underscore we cannot
                # tell where the class and endpoint names are separated
                print('FAIL: no endpoint name found')
                print(line)
                continue
            class_name = pieces[1][:class_name_end]

            # Whether to generate bits
            remaining_name = pieces[1][class_name_end + 1:]
            previous_len = len(remaining_name)
            remaining_name = remaining_name.replace('_GEN_BIT', '')
            # If the remaining name is shorter it is because GEN_BIT was replaced
            gen_bit = len(remaining_name) < previous_len

            # Whether to generate address
            previous_len = len(remaining_name)
            remaining_name = remaining_name.replace('_GEN_ADDR', '')
            # If the remaining name is shorter it is because GEN_ADDR was replaced
            gen_address = len(remaining_name) < previous_len

            # Endpoint name
            ep_name = remaining_name
            if ep_name == 'NUM_OUTGOING_EPS':
                # This is not an endpoint and does not match the
                # format of the others so we skip it
                continue

            # Address, bit, and bit_widt
            if "8'h" in pieces[2]:
                # Definition holds an address, take that value
                address = int(pieces[2][3:], base=16)
                bit = 0
                bit_width = int(pieces[4].split('=')[1])
            else:
                # Definition holds a bit, take address from comment
                comment_address = pieces[4].split('=')[1]
                if '0x' in comment_address:
                    # Address comment has a hex value
                    address = int(comment_address[2:], 16)
                else:
                    # Address comment has the name of another endpoint so store
                    # the interfaces.py name of that endpoint so we can look it
                    # up going through all lines
                    address_name = pieces[4].split('=')[1]
                    address_name_no_gen = address_name.split('_GEN', maxsplit=1)[0]
                    address = address_name_no_gen
                bit = int(pieces[2])
                bit_width = int(pieces[5].split('=')[1])

            endpoint = Endpoint(address, bit, bit_width, gen_bit, gen_address)

            # Put defined endpoint in endpoints_from_defines dictionary
            if Endpoint.endpoints_from_defines.get(class_name) is None:
                # Class doesn't exist yet in the dictionary
                Endpoint.endpoints_from_defines[class_name] = {ep_name: endpoint}
            else:
                # Class already exists in the dictionary
                Endpoint.endpoints_from_defines[class_name][ep_name] = endpoint

        # Go through endpoints_from_defines and find hex addresses for those with endpoint
        # name references instead
        for group_name in Endpoint.endpoints_from_defines:
            group = Endpoint.endpoints_from_defines[group_name]
            for endpoint_name in group:
                endpoint = group[endpoint_name]
                if type(endpoint.address) == str:
                    # Address is a name
                    class_name, ep_name = endpoint.address.split('_', maxsplit=1)
                    referenced_group = Endpoint.endpoints_from_defines.get(class_name)
                    if referenced_group is None:
                        print(f'{group_name}[{endpoint_name}]: Referenced group "{class_name}" not found.')
                        continue
                    print(f'{group_name}[{endpoint_name}]: Referenced group "{class_name}{ep_name}" not found.') #LJK
                    endpoint.address = referenced_group.get(ep_name).address
                    if endpoint.address is None:
                        print(f'{group_name}[{endpoint_name}]: Referenced address "{"_".join((class_name, ep_name))}" not found.')
                        continue

        return Endpoint.endpoints_from_defines

    @classmethod
    def get_chip_endpoints(cls, chip_name):
        """Return a copy of the dictionary of Endpoints for a specific chip or group."""

        if Endpoint.endpoints_from_defines == dict():
            Endpoint.update_endpoints_from_defines()

        # copy.deepcopy() is important here because it makes a copy of the
        # dictionary so that when we increment it for multiple instantiations
        # of the chip, each previously instantiated chip will not have its
        # endpoints affected by the increment, only future instantiations.
        # Using deepcopy() ensures that any dictionaries inside the dictionary
        # we copy also get copied, not left as references.
        return copy.deepcopy(Endpoint.endpoints_from_defines.get(chip_name))

    @classmethod
    def increment_endpoints(cls, endpoints_dict):
        """Increment all Endpoints in endpoints_dict.

        Use each Endpoint's gen_bit and gen_addr values to determine whether to
        increment bits and addresses, respectively.
        """

        for key in endpoints_dict:
            endpoint = endpoints_dict[key]
            if endpoint.gen_bit:
                #endpoint.bit += endpoint.bit_width
                endpoint.bit_index_low += endpoint.bit_width
                endpoint.bit_index_high = endpoint.bit_index_low + endpoint.bit_width
            if endpoint.gen_address:
                # TODO: also keep track of bit_high, bit_low within the address?
                endpoint.address += 1


def advance_endpoints_bynum(endpoints_dict, num):
    """
    advance endpoints by a specific number; calculates based on the bit_widths
    and knowing that the width of the OK interface is 32 bits.
    Just a method of an Endpoint (not a classmethod).
    Goal is to not impact future device instantiations.

    Example usage:
        endpoints=Endpoint.advance_endpoints_bynum(Endpoint.get_chip_endpoints('I2CDAQ'),1)
    """
    print('Number to advance is {}'.format(num))
    # num is the number to advance from the base addresses and bits
    for key in endpoints_dict:
        endpoint = endpoints_dict[key]
        if endpoint.gen_bit:
            # endpoint.bit = (endpoint.bit + (endpoint.bit_width*num)) % 32
            endpoint.bit_index_low = (endpoint.bit_index_low + (endpoint.bit_width*num)) % 32
            endpoint.bit_index_high = endpoint.bit_index_low + endpoint.bit_width
        if endpoint.gen_address:
            # endpoint.bit = (endpoint.bit + (endpoint.bit_width*num)) % 32
            endpoint.bit_index_low = (endpoint.bit_index_low + (endpoint.bit_width*num)) % 32
            endpoint.bit_index_high = endpoint.bit_index_low + endpoint.bit_width
            endpoint.address += ((endpoint.bit_width*num)//32)
        endpoints_dict[key] = endpoint
    return endpoints_dict

# Class for the FPGA itself. Handles FPGA configuration, setting wire values,
# and other FPGA specific functions.

class FPGA:
    """Class for the Opal Kelly FPGA itself.

    Attributes
    ----------
    bitfile : str
        Path to the bitfile to load on the FPGA.
    xem : ok.okCFrontPanel
        Opal Kelly API connection to the FPGA.
    device_info : ok.okTDeviceInfo
        General information about the FPGA.

    Methods
    -------
    init_device()
        Initialize the FPGA for use.
    """

    # TODO: change to complete bitfile when Verilog is combined
    def __init__(self, bitfile=os.path.join('..', '..', 'fpga_test.bit')):

        self.bitfile = bitfile
        # self.pll = ok.PLL22150()
        # I don't know why, but uncommenting this makes things fail
        return

    def init_device(self):
        """Initialize the FPGA for use and print device information.

        Connect to the FPGA and load the bitfile. Return False on any errors.
        Only run this once or the FPGA connection will fail.
        """

        # Open the first device we find.
        self.xem = ok.okCFrontPanel()
        if (self.xem.NoError != self.xem.OpenBySerial("")):
            print("A device could not be opened.  Is one connected?")
            return(False)

        # Get some general information about the device.
        self.device_info = ok.okTDeviceInfo()
        if (self.xem.NoError != self.xem.GetDeviceInfo(self.device_info)):
            print("Unable to retrieve device information.")
            return(False)
        print("         Product: " + self.device_info.productName)
        print("Firmware version: %d.%d" %
              (self.device_info.deviceMajorVersion, self.device_info.deviceMinorVersion))
        print("   Serial Number: %s" % self.device_info.serialNumber)
        print("       Device ID: %s" % self.device_info.deviceID)

        self.xem.LoadDefaultPLLConfiguration()

        # Download the configuration file.
        if self.bitfile is not None:
            if (self.xem.NoError != self.xem.ConfigureFPGA(self.bitfile)):
                print("FPGA configuration failed.")
                return(False)
            else:
                print('Loaded bit-file: {}'.format(self.bitfile))
        else:
            print('Skipped bit-file update')

        # Check for FrontPanel support in the FPGA configuration.
        if (False == self.xem.IsFrontPanelEnabled()):
            print("FrontPanel support is not available.")
            return(False)

        print("FrontPanel support is available.")
        return self

    def read_pipe_out(self, addr, data_len=1024):
        """Return the filled buffer and error code after reading an OK PipeOut.
            data_len is length in bytes (must be multiple of 16)
            returns: bytearray; error code
        """
        buf = bytearray(data_len)
        e = self.xem.ReadFromPipeOut(addr, buf)
        print('read_pipe_out:', addr, buf)

        if (e < 0):
            print('Error code {}'.format(e))
        return buf, e

    def set_wire(self, address, value, mask=0xFFFF):
        """Return the error code after setting an OK WireIn value."""

        # DEBUG: temporary for logging DAC80508 test
        # print(f'set_wire(address={hex(address)}, value={hex(value)}, mask={hex(mask)}')
        error_code = self.xem.SetWireInValue(address, value, mask)
        self.xem.UpdateWireIns()
        return error_code

    def read_wire(self, address):
        """Return the read data after reading an OK WireOut."""

        self.xem.UpdateWireOuts()
        return self.xem.GetWireOutValue(address)

    def set_bit(self, ep_bit, adc_chan=None):
        """Set all bits in an Endpoint high."""

        if adc_chan is None:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        else:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1))[adc_chan])
        self.xem.SetWireInValue(ep_bit.address, mask, mask)  # set
        self.xem.UpdateWireIns()

    def clear_bit(self, ep_bit, adc_chan=None):
        """Set all bits in an Endpoint low."""

        if adc_chan is None:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        else:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1))[adc_chan])
        self.xem.SetWireInValue(ep_bit.address, 0x0000, mask)  # clear
        self.xem.UpdateWireIns()

    def toggle_low(self, ep_bit, adc_chan=None):
        """Toggle all bits in an Endpoint low then back to high."""

        if adc_chan is None:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        else:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1))[adc_chan])
        self.xem.SetWireInValue(
            ep_bit.address, 0x0000, mask)  # toggle low
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(ep_bit.address, mask, mask)   # back high
        self.xem.UpdateWireIns()

    def toggle_high(self, ep_bit, adc_chan=None):
        """Toggle all bits in an Endpoint high then back to low."""

        if adc_chan is None:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        else:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1))[adc_chan])
        self.xem.SetWireInValue(ep_bit.address, mask, mask)  # toggle high
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(ep_bit.address, 0x0000, mask)   # back low
        self.xem.UpdateWireIns()

    def send_trig(self, ep_bit):
        """Return the error code after activating an OK TriggerIn Endpoint.

        Expects a single bit, not yet implement for multiple bits and will only
        activate the LSB if the Endpoint containts multiple bits.
        """

        return self.xem.ActivateTriggerIn(ep_bit.address, ep_bit.bit_index_low)

    def read_ep(self, ep_bit):
        """Return the error code after reading an OK WireOut Endpoint."""
        self.xem.UpdateWireOuts()
        read_out = self.xem.GetWireOutValue(ep_bit.address)
        return read_out

    # def get_pll_freq(self, output):
    #     f = self.pll.GetOutputFrequency(output)
    #     print('Pll f = {} [MHz]'.format(f))
    #     return f

    def get_time(self):
        """Return the total time from the FPGA since initializing the bitfile."""
        self.send_trig(Endpoint(0x40, 10, 10, 1))
        low_end = self.read_wire(0x25)
        high_end = self.read_wire(0x26)
        total_time = (high_end << 32 | low_end)
        total_time /= 200000000
        return total_time

    def get_available_endpoints(self):
        """Return a list of available OK endpoints."""

        # PipeIns (Includes Block-Throttled) [0x80:0x9F] return ??? if the endpoint is not there
        print('Gathering PipeIns...')
        pipe_ins = []
        for ep in range(0x80, 0x9F + 1):
            result = self.xem.WriteToPipeIn(ep, bytearray(81920))
            print(hex(ep), result)
            if result == None:
                continue
            elif result >= 0:
                if result is False:  # Need is because False == 0 is True
                    continue
                print('Appending...')
                # Not an error, add to list
                pipe_ins.append(hex(ep))

        # PipeOuts (Includes Block-Throttled) [0xA0:0xBF] return -2 if the endpoint is not there
        print('Gathering PipeOuts...')
        pipe_outs = []
        # for offset in range(0x00, 0x1f + 1):
        for offset in range(32):
            # buf, result = self.read_pipe_out(addr=addr, data_len=16)
            buf, result = self.read_pipe_out(0xA0 + offset, 16)
            print(offset, buf, result)
            if result == None:
                # Intermediate step to get the FPGA to do some sort of "reset"
                self.set_wire(0, 0)
                continue
            elif result >= 0:
                if result is False:  # Need is because False == 0 is True
                    continue
                print('Appending...')
                # Not an error, add to list
                pipe_outs.append(hex(offset + 0xa0))

        available_endpoints = [pipe_ins, pipe_outs]
        return available_endpoints

    def set_wire_bit(self, address, bit):
        """Set a single bit to 1 in a OpalKelly wire in."""
        return self.set_wire(address, value=1 << bit, mask=1 << bit)

    def clear_wire_bit(self, address, bit):
        """Clear a single bit to 0 in a OpalKelly wire in."""
        return self.set_wire(address, value=0, mask=1 << bit)

    def read_wire_bit(self, address, bit):
        """Read a single bit in a OpalKelly wire in."""
        value = self.read_wire(address)
        return (value & (1 << bit)) >> bit

class I2CController:
    """Class for controllers on the FPGA using I2C protocol.

    Attributes
    ----------
    I2C_MAX_TIMEOUT_MS : int
        Maximum wait time until transmission timeout in milliseconds.
    i2c : dict
        Dictionary of I2C memory buffer and data start location.
    fpga : FPGA
        FPGA instance this controller uses to communicate.
    endpoints : dict
        Endpoints on the FPGA this controller uses to communicate.

    Methods
    -------
    i2c_configure(data_length, starts, stops, preamble)
        Configure the buffer for the next transmission.
    i2c_transmit(data, data_length)
        Send data along the SCL and SDA lines.
    i2c_receive(data_length, results='wire')
        Take in data from the SCL and SDA lines.
    i2c_write_long(devAddr, regAddr, data_length, data)
        Send a write command with given data to regAddr on devAddr.
    i2c_read_long(devAddr, regAddr, data_length)
        Read data_length bytes from regAddr on devAddr.
    reset_device()
        Reset the I2C controller using an OK TriggerIn.
    """

    I2C_MAX_TIMEOUT_MS = 50

    def __init__(self, fpga, endpoints, i2c={'m_pBuf': [], 'm_nDataStart': 7}):
        self.i2c = i2c
        self.fpga = fpga
        self.endpoints = endpoints

    # STARTS - Defines the preamble bytes after which a start bit is
    #      transmitted. For example, if STARTS=0x04, a start bit is
    #      transmitted after the 3rd preamble byte.
    # STOPS - Defines the preamble bytes after which a stop bit is
    #      transmitted. For example, if STOPS=0x04, a stop bit is
    #      transmitted after the 3rd preamble byte.
    # LENGTH - Length of the preamble in bytes.
    #
    # Note: If there is a one in the same position for both STARTS and STOPS,
    #       the stop takes precedence.

    # The preamble is the device address, byte address, and (if a write) device address again:
    #   preamble[0] = 0xA0; // devAddr (write)
    #   preamble[1] = 0x00; // byteAddress (MSB)
    #   preamble[2] = 0x00; // byteAddress (LSB)
    #   preamble[3] = 0xA1; // devAddr (read)

    # from the HDL

    def i2c_configure(self, data_length, starts, stops, preamble):
        """Configure the buffer for the next transmission."""

        if data_length > 7:
            print('Data too long')
            # throw DataTooLongException();

        self.i2c['m_pBuf'] = [None]*(4+data_length)
        self.i2c['m_pBuf'][0] = data_length
        self.i2c['m_pBuf'][1] = starts
        self.i2c['m_pBuf'][2] = stops
        # Payload length will be provided later.
        self.i2c['m_pBuf'][3] = 0
        for i in range(data_length):
            self.i2c['m_pBuf'][4+i] = preamble[i]

        self.i2c['m_nDataStart'] = 4 + data_length

    def i2c_transmit(self, data, data_length):
        """Send data along the SCL and SDA lines."""

        self.i2c['m_pBuf'][3] = data_length
        for i in range(data_length):
            self.i2c['m_pBuf'].append(data[i])

        # Reset the memory pointer and transfer the buffer.
        self.fpga.xem.ActivateTriggerIn(
            self.endpoints['MEMSTART'].address, self.endpoints['MEMSTART'].bit_index_low)
        for i in range(data_length + self.i2c['m_nDataStart']):
            # print('(transmit) WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
            mask = 0xff << self.endpoints['WIRE_IN'].bit_index_low
            value = self.i2c['m_pBuf'][i] << self.endpoints['WIRE_IN'].bit_index_low
            self.fpga.xem.SetWireInValue(
                self.endpoints['WIRE_IN'].address, value, mask)
            self.fpga.xem.UpdateWireIns()
            self.fpga.xem.ActivateTriggerIn(
                self.endpoints['MEMWRITE'].address, self.endpoints['MEMWRITE'].bit_index_low)

        # Start I2C transaction
        self.fpga.xem.ActivateTriggerIn(
            self.endpoints['START'].address, self.endpoints['START'].bit_index_low)

        # Wait for transaction to finish
        for i in range(int(I2CController.I2C_MAX_TIMEOUT_MS / 10)):
            self.fpga.xem.UpdateTriggerOuts()
            # change to waiting for True
            if self.fpga.xem.IsTriggered(self.endpoints['DONE'].address, (1 << self.endpoints['DONE'].bit_index_low)):
                return True
            time.sleep(0.01)

        print('Timeout error in transmit')

    def i2c_receive(self, data_length, results='wire'):
        """Take in data from the SCL and SDA lines."""

        self.i2c['m_pBuf'][0] |= 0x80
        self.i2c['m_pBuf'][3] = data_length

        # Reset the memory pointer and transfer the buffer.
        self.fpga.xem.ActivateTriggerIn(
            self.endpoints['MEMSTART'].address, self.endpoints['MEMSTART'].bit_index_low)

        for i in range(self.i2c['m_nDataStart']):
            # print('WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
            # TODO: check this change (LJK)
            mask = 0xff << self.endpoints['WIRE_IN'].bit_index_low
            value = self.i2c['m_pBuf'][i] << self.endpoints['WIRE_IN'].bit_index_low
            self.fpga.xem.SetWireInValue(
                self.endpoints['WIRE_IN'].address, value, mask)
            self.fpga.xem.UpdateWireIns()
            self.fpga.xem.ActivateTriggerIn(
                self.endpoints['MEMWRITE'].address, self.endpoints['MEMWRITE'].bit_index_low)

        # Start I2C transaction
        self.fpga.xem.ActivateTriggerIn(
            self.endpoints['START'].address,
            self.endpoints['START'].bit_index_low)

        # Wait for transaction to finish
        for _ in range(int(I2CController.I2C_MAX_TIMEOUT_MS / 10)):
            self.fpga.xem.UpdateTriggerOuts()
            # change to 1, LJK
            if self.fpga.xem.IsTriggered(self.endpoints['DONE'].address,
                                         (1 << self.endpoints['DONE'].bit_index_low)):
                if results.lower() == 'wire':
                    # Read data: Reset the memory pointer
                    self.fpga.xem.ActivateTriggerIn(
                        self.endpoints['MEMSTART'].address, self.endpoints['MEMSTART'].bit_index_low)
                    data = [None]*data_length
                    for i in range(data_length):
                        self.fpga.xem.UpdateWireOuts()
                        # TODO: check this change (LJK)
                        data_tmp = self.fpga.xem.GetWireOutValue(
                            self.endpoints['WIRE_OUT'].address)
                        mask = 0xff << self.endpoints['WIRE_OUT'].bit_index_low
                        data[i] = (data_tmp & mask) >> self.endpoints['WIRE_OUT'].bit_index_low
                        self.fpga.xem.ActivateTriggerIn(
                            self.endpoints['MEMREAD'].address, self.endpoints['MEMREAD'].bit_index_low)
                    return data
                if results.lower() == 'pipe':
                    # should not be used. OK pipe is not configured.
                    data_read = np.int(np.ceil(data_length*4/16)*16)
                    buf, e = self.read_pipe_out(0xA0 + 0, data_read)
                    # reset FIFO
                    self.fpga.xem.ActivateTriggerIn(
                        self.endpoints['MEMREAD'].address, self.endpoints['MEMREAD'].bit_index_low)
                    return list(buf[0::4])[0:data_length]
            time.sleep(0.01)

        print('Timeout Exception in Rx')

    # def i2c_write8(self, devAddr, regAddr, data_length, data):

    #     preamble = [devAddr & 0xfe, regAddr]
    #     self.i2c_configure(2, 0x00, 0x00, preamble)
    #     return self.i2c_transmit(data, data_length)

    def i2c_write_long(self, devAddr, regAddr, data_length, data):
        """Send a write command with given data to regAddr on devAddr.

        regAddr must be given in a list."""

        preamble = [devAddr & 0xfe] + regAddr  # + data
        self.i2c_configure(len(preamble), 0x00, 1 << len(preamble), preamble)
        return self.i2c_transmit(data, data_length)

    # Sequence is
    # [START] DEV_ADDR(W) REG_ADDR [START] DEV_ADDR(R) VALUE
    # LJK - this command does not execute OK API calls
    # def i2c_read8(self, devAddr, regAddr, data_length):

    #     # for the pressure sensors that only need the slave address and a read bit and then send out 4 bytes.
    #     if regAddr is None:
    #         preamble = [devAddr | 0x01]
    #         self.i2c_configure(1, 0x01, 0x00, preamble)
    #     else:
    #         preamble = [devAddr & 0xfe, regAddr, devAddr | 0x01]
    #         # signature: i2c_configure(data_length, starts (a one for each byte that gets a start), stops, preamble):
    #         self.i2c_configure(3, 0x02, 0x00, preamble)
    #     data = self.i2c_receive(data_length)

    #     return data

    # Sequence is
    # [START] DEV_ADDR(W) REG_ADDR [START] DEV_ADDR(R) VALUE
    # LJK - this command does not execute OK API calls
    def i2c_read_long(self, devAddr, regAddr, data_length):
        """Read data_length bytes from regAddr on devAddr.

        devAddr : 8 bit address (don't set the read bit (LSB) since this is done in this function)
        regAddr:  written to device (this is a list and must be even if length 1)
        data_length : number of bytes expected to receive
        """

        preamble = [devAddr & 0xfe] + regAddr + [devAddr | 0x01]
        # signature: i2c_configure(data_length, starts (a one for each byte that gets a start), stops, preamble):
        start_positions = 0x01 << len(regAddr)
        self.i2c_configure(len(preamble), start_positions, 0x00, preamble)
        data = self.i2c_receive(data_length)

        return data

    def reset_device(self):
        """Reset the I2C controller using an OK TriggerIn."""

        return self.fpga.xem.ActivateTriggerIn(
            self.endpoints['RESET'].address,
            self.endpoints['RESET'].bit_index_low)


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

    Methods
    -------
    configure_pins(data)
        Configure the chip's pins as inputs (1's) or outputs (0's).
    write(data, register_name='OUTPUT', mask=0xffff)
        Write 2 bytes of data to the pins.
    read(register_name="INPUT")
        Read 2 bytes of data from the pins.
    """

    ADDRESS_HEADER=0b0100_0000
    registers = Register.get_chip_registers('TCA9555')

    def __init__(self, fpga, addr_pins, endpoints):
        super().__init__(fpga=fpga, endpoints=endpoints)
        self.addr_pins = addr_pins


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
            read_out = self.read(self.addr_pins)
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
        dev_addr = self.ADDRESS_HEADER | (
            self.addr_pins << 1) | 0b1
        return self.i2c_read_long(dev_addr, [TCA9555.registers[register_name].address], 2)


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

    Methods
    -------
    write(data, word_address=0x00, num_bytes=None)
        Write data into memory at word_address.
    read(word_address=0x00, words_read=1)
        Return words_read words of data from memory at word_address.
    get_serial_number()
        Return the unique 32-serial number stored in memory on the chip.
    get_manufacturer_code()
        Return the chip's manufacturer code.
    get_device_code()
        Return the chip's device code.
    """

    ADDRESS_HEADER=0b10100000
    registers = Register.get_chip_registers('24AA025UID')

    def __init__(self, fpga, addr_pins, endpoints):
        # No endpoints default because I2CDC or I2CDAQ does not make sense as a default either way
        super().__init__(fpga=fpga, endpoints=endpoints)
        self.addr_pins = addr_pins


    def write(self, data, word_address=0x00, num_bytes=None):
        """Write data into memory at word_address."""

        dev_addr = UID_24AA025UID.ADDRESS_HEADER | (self.addr_pins << 1)
        print(f'word_address: {hex(word_address)}\ndata: {hex(data)}\nnum_bytes: {num_bytes}')

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
            recurse_data = data % (0x1 << (8 * (num_bytes - 16)))
            print(f'{data} % {(0x1 << (8 * (num_bytes - 16)))} = {recurse_data}')
            self.write(data=recurse_data, word_address=word_address
                       + 16, num_bytes=num_bytes - 16)
            return True

        # Data is no more than 16 bytes (1 page) and can be written with 1 I2C command.
        self.i2c_write_long(dev_addr, [word_address], num_bytes, list_data)
        return True


    def read(self, word_address=0x00, words_read=1):
        """Return words_read words of data from memory at word_address."""

        # A word is a byte, 8 bits
        dev_addr = UID_24AA025UID.ADDRESS_HEADER | (
            self.addr_pins << 1) | 0b1
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

    Methods
    -------
    write(data, register_name='DAC_DATA')
        Write data to any register on the chip.
    read(register_name='DAC_DATA')
        Return data from any register on the chip.
    write_voltage(voltage)
        Write a voltage output from the DAC.
    enable_internal_reference()
        Enable the DAC's internal reference.
    set_gain(gain)
        Set the DAC's output gain value.
    get_gain()
        Return the DAC's current output gain value.
    config_func(function_name)
        Configure the function generator.
    start_func()
        Start function generation.
    stop_func()
        Stop function generation.
    config_margins(margin_high=None, margin_low=None)
        Configure margin high and low values.
    config_step(step)
        Configure the number of bits to step through.
    config_rate(rate)
        Configure the rate to step through each bit.
    reset()
        Reset the chip using a software reset.
    lock()
        Lock the registers of the device so they cannot be changed.
    unlock()
        Unlock the registers of the device so they can be changed again.
    power_up()
        Power up the DAC output.
    power_down_10k()
        Power down the DAC output to 10K ohms.
    power_down_high_impedance()
        Power down the DAC output to high impedance (default).
    get_id()
        Return the device ID and version ID as one integer.
    """

    ADDRESS_HEADER = 0b10010000
    registers = Register.get_chip_registers('DAC53401')

    #        Address Pins Guide
    # Slave Address   |   A0 Pin
    #           000   |   AGND
    #           001   |   VDD
    #           010   |   SDA
    #           011   |   SCL

    def __init__(self, fpga, addr_pins, endpoints):
        super().__init__(fpga=fpga, endpoints=endpoints)
        self.addr_pins = addr_pins

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

        self.write(voltage, 'DAC_DATA')

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


class SPIController:
    """Class for controllers on the FPGA using SPI protocol.

    Attributes
    ----------
    WB_SET_ADDRESS : int
        Set address command for the Wishbone.
    WB_WRITE : int
        Write command for the Wishbone.
    WB_READ : int
        Read command for the Wishbone.
    WB_CLK_FREQ : int
        Frequency of the clock the Wishbone runs on.
    fpga : FPGA
        FPGA instance this controller uses to communicate.
    endpoints : dict
        Endpoints on the FPGA this controller uses to communicate.
    master_config : int
        Value of the CTRL register in the Wishbone.
    registers : dict
        Name-Register pairs for the internal registers of the Wishbone.

    Methods
    -------
    wb_send_cmd(command)
        Send a command to the Wishbone.
    wb_set_address(address)
        Set the address of the register we interact with in the Wishbone.
    wb_write(data)
        Write up to 30 bytes of data to the currently selected register.
    wb_read()
        Return the data stored in the currently selected register.
    wb_go()
        Initiate a SPI transmission.
    select_slave(slave_address)
        Select a slave device.
    set_divider(divider)
        Set the value of the Wishbone's DIVIDER register.
    set_frequency(frequency)
        Set the frequency of SCL.
    write(data, register=0)
        Write data on the SCL and SDA lines.
    read(register=0)
        Return data from the selected data receive register.
    configure_master_bin(data)
        Set the value of the Wishbone's CTRL register directly.
    configure_master(ASS=0, IE=0, LSB=0, Tx_NEG=0, Rx_NEG=0, CHAR_LEN=0)
        Set the Wishbone's CTRL register using several arguments.
    get_master_configuration()
        Return the current configuration of CTRL register.
    reset_master()
        Reset the Wishbone Master and SPI Core.
    """

    WB_SET_ADDRESS=0x80000000  # These 3 are from the SPI core manual
    WB_WRITE=0x40000000
    WB_READ=0x00000000
    # ACK=0x200000000
    WB_CLK_FREQ=200  # clk_sys = 200 MHz in the top_level_module.v comments

    registers = Register.get_chip_registers('SPI')

    def __init__(self, fpga, endpoints, master_config=registers.get('CTRL').default):
        self.fpga = fpga
        self.master_config = master_config
        self.endpoints = endpoints

    def wb_send_cmd(self, command):
        """Send a command to the Wishbone.

        Sent in 32 bits through the WbSignal_converter Verilog module tos
        reformat to 34 bits.
        """

        print(f'wb_send_cmd: {hex(self.endpoints["WB_IN"].address)}, {hex(command)}')
        self.fpga.set_wire(
            self.endpoints['WB_IN'].address, command, 0xffffffff)
        # DEBUG: temporary for logging DAC80508 test
        # print(f'ActivateTriggerIn(address={hex(self.parameters["WB_CONVERT"].address)}, index={hex(self.parameters["WB_CONVERT"].bit_index_high)}')
        self.fpga.xem.ActivateTriggerIn(
            self.endpoints['WB_CONVERT'].address, self.endpoints['WB_CONVERT'].bit_index_low)  # High and low bit indexes are the same for the trigger because it is 1 bit wide

    def wb_is_acknowledged(self):
        pass
    #     response = self.fpga.read_wire(self.endpoints['OUT'].address)
    #     return response == SPIController.ACK

    def wb_set_address(self, address):
        """Set the address of the register we interact with in the Wishbone."""

        self.wb_send_cmd(
            SPIController.WB_SET_ADDRESS | (address << 2) | 0x1)  # TODO: comment here what the | 0x1 is for when I figure it out
        return self.wb_is_acknowledged()  # TODO: test if acknowledge actually comes back

    def wb_write(self, data):
        """Write up to 30 bytes of data to the currently selected register."""

        self.wb_send_cmd(SPIController.WB_WRITE | data)
        return self.wb_is_acknowledged()  # TODO: test if acknowledge actually comes back

    def wb_read(self):
        """Return the data stored in the currently selected register."""

        self.wb_send_cmd(SPIController.WB_READ)
        return self.fpga.read_wire(self.endpoints['OUT'].address)

    def wb_go(self):
        """Initiate a SPI transmission.

        Initiated by setting the GO_BSY bit of the CTRL register to  1.
        """

        ack = self.wb_set_address(SPIController.registers['CTRL'].address)
        # TODO: fix ack
        # if ack:
        #     if self.debug:
        #         print(f'Set address to "CTRL": SUCCESS')
        # else:
        #     if self.debug:
        #         print(f'Set address to "CTRL": FAIL')
        #     return False

        # Use or so we do not overwrite the CTRL configuration, just the GO_BSY bit
        busy = self.master_config | (
            0x1 << SPIController.registers['GO_BSY'].bit_index_low)
        # add mask or something to not reset entire CTRL register
        ack = self.wb_write(busy)
        # TODO: fix ack
        # if ack:
        #     if self.debug:
        #         print(f'Set GO_BSY bit: SUCCESS')
        # else:
        #     if self.debug:
        #         print(f'Set GO_BSY bit: FAIL')
        #     return False

        return True

    def select_slave(self, slave_address):
        """Selecting a slave device.

        Set the correspoinding bit in the Slave Select register to 1."""

        # Set address to SS register
        self.wb_set_address(SPIController.registers['SS'].address)

        # Write slave address
        # Don't need to mask the write because we only select 1 slave device at a time
        self.wb_write(slave_address)

    def set_divider(self, divider):
        """Set the value of the Wishbone's DIVIDER register."""

        self.wb_set_address(SPIController.registers['DIVIDER'].address)
        self.wb_write(divider)

    def set_frequency(self, frequency):
        """Set the frequency of SCL.

        Set the DIVIDER register of the Wishbone with the corresponding divider
        for the target frequency. Frequency must be given in MHz.
        """

        divider = max(
            round((SPIController.WB_CLK_FREQ) / (frequency * 2)), 1) - 1
        # Make sure divider does not exceed 32 bits
        divider = min(divider, 0xffff_ffff)
        self.set_divider(divider)
        return divider

    def write(self, data, register=0):
        """Write data on the SCL and SDA lines.

        Register should be either 0, 1, 2, or 3.
        """

        # TODO: determine if register argument is really necessary

        # Set address to Tx register
        ack = self.wb_set_address(SPIController.registers['Tx' + str(register)].address)
        # TODO: fix ack
        # if ack:
        #     if self.debug:
        #         print(f'Set address to "Tx{register}": SUCCESS')
        # else:
        #     if self.debug:
        #         print(f'Set address to "Tx{register}": FAIL')
        #     return False

        # Write data
        ack = self.wb_write(data)
        # TODO: fix ack
        # if ack:
        #     if self.debug:
        #         print(f'Data write to "Tx{register}": SUCCESS')
        # else:
        #     if self.debug:
        #         print(f'Data write to "Tx{register}": FAIL')
        #     return False

        # Set GO_BSY bit
        return self.wb_go()

    def read(self, register=0):
        """Return data from the selected data receive register.

        Register should be 0, 1, 2, or 3.
        """

        # Set address to the Rx register Rx0, Rx1, Rx2, or Rx3
        ack = self.wb_set_address(SPIController.registers['Rx' + str(register)].address)

        # TODO: fix ack
        # if ack:
        #     if self.debug:
        #         print(f'Set address to "Rx{register}": SUCCESS')
        # else:
        #     if self.debug:
        #         print(f'Set address to "Rx{register}": FAIL')
        #     return False

        # Read data
        return self.wb_read()

    def configure_master_bin(self, data):
        """Set the value of the Wishbone's CTRL register directly."""

        self.wb_set_address(SPIController.registers['CTRL'].address)
        self.wb_write(data)
        self.master_config = data

    def configure_master(self, ASS=0, IE=0, LSB=0, Tx_NEG=0, Rx_NEG=0, CHAR_LEN=0):
        """Set the Wishbone's CTRL register using several arguments.

        ASS: Automatic Slave Select
        IE: Set interrupt output active after a transfer is finished
        LSB: Send LSB first
        Tx_NEG: Change output signal on falling edge of SCLK
        Rx_NEG: Latch input signal on falling edge of SCLK
        CHAR_LEN: Number of bits transmitted per transfer (up to 64).
        """

        params = {'ASS': ASS, 'IE': IE, 'LSB': LSB,
                  'Tx_NEG': Tx_NEG, 'Rx_NEG': Rx_NEG, 'CHAR_LEN': CHAR_LEN}

        configuration = SPIController.registers['CTRL'].default
        for param in params:
            configuration |= (
                params[param] << SPIController.registers[param].bit_index_low)
        self.configure_master_bin(configuration)

    def get_master_configuration(self):
        """Return the current configuration of CTRL register.

        Includes ASS, IO, LSB, Tx_NEG, Rx_NEG, CHAR_LEN.
        """

        self.wb_set_address(SPIController.registers['CTRL'].address)
        config_data = self.wb_read()
        #TODO: convert to text data to show individual settings
        # return config
        return config_data

    def reset_master(self):
        """Reset the Wishbone Master and SPI Core."""

        self.fpga.xem.ActivateTriggerIn(
            self.endpoints['MASTER_RESET'].address,
            self.endpoints['MASTER_RESET'].bit_index_low)


class DAC80508(SPIController):
    """ Class for SPI DAC chip DAC80508.

    Subclass of the SPIController class. Attributes and methods below are
    differences in this class from I2CController only.

    Attributes
    ----------
    WRITE_OPERATION : int
        SPI data prefix for writing to the DAC.
    READ_OPERATION : int
        SPI data prefix for reading from the DAC.
    registers : dict
        Name-Register pairs for the internal registers of the DAC80508.

    Methods
    -------
    write(register_name, data, mask=0xffff)
        Write to any register on the chip.
    read(register_name)
        Return data from any register on the chip.
    set_config_bin(data, mask=0xffff)
        Set the configuration register with a binary number.
    set_config(ALM_SEL=0, ALM_EN=0, CRC_EN=0, FSDO=0, DSDO=0, REF_PWDWN=0,
               DAC7_PWDWN=0, DAC6_PWDWN=0, DAC5_PWDWN=0, DAC4_PWDWN=0,
               DAC3_PWDWN=0, DAC2_PWDWN=0, DAC1_PWDWN=0, DAC0_PWDWN=0)
        Set the configuration register with multiple arguments.
    get_config(display_values=True)
        Return and print the current configuration register data.
    set_gain(data, mask=0x01ff)
        Set the gain value.
    get_gain()
        Get the gain value.
    get_id(display=True)
        Print the device info and return its ID.
    reset()
        Soft reset the chip.
    """

    WRITE_OPERATION = 0x000000
    READ_OPERATION = 0x800000

    registers = Register.get_chip_registers('DAC80508')

    def __init__(self, fpga, master_config=0x3218, slave_address=0x1, endpoints=None):
        # master_config=0x3218 Sets CHAR_LEN=24, Rx_NEG, ASS, IE
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('DAC80508')
        self.slave_address = slave_address
        super().__init__(fpga=fpga, master_config=master_config, endpoints=endpoints)

    # Method to write to any register on the chip.
    def write(self, register_name, data, mask=0xffff):
        """Write to any register on the chip."""

        # .get instead of [brackets] because .get will return None if the register name is not in the dictionary
        reg = DAC80508.registers.get(register_name)
        if reg == None:
            print(f'{register_name} not in registers')
            return False

        # Get current data
        current_data = self.read(register_name)
        # Create new data from input data, mask, and current data
        new_data = (data & mask) | (current_data & ~mask)

        # 23=0 (write), [22:20]=000 (reserved), [19:16]=A[3:0] (reg address), [15:0]=D[15:0] (data)
        transmission = DAC80508.WRITE_OPERATION + \
            (reg.address << 16) + new_data
        print(f'Transmission = {hex(transmission)}')  # DEBUG
        ack = super().write(transmission)
        if ack:
            print(f'Write {hex(data)} to {register_name}: SUCCESS')
        else:
            print(f'Write {hex(data)} to {register_name}: FAIL')
        return ack

    def read(self, register_name):
        """Return data from any register on the chip."""

        # .get instead of [brackets] because .get will return None if the register name is not in the dictionary
        reg = DAC80508.registers.get(register_name)
        if reg == None:
            print(f'{register_name} not in registers')
            return False

        # Issue read command
        # 23=1 (read), [22:20]=000 (reserved), [19:16]=A[3:0] (reg address), [15:0]=0xXXXX (do not cares)
        transmission = DAC80508.READ_OPERATION | (reg.address << 16)
        super().write(transmission)

        # Read in response
        # 23=1 (echo read), [22:20]=000 (echo reserved), [19:16]=A[3:0] (echo reg address), [15:0]=D[15:0] (data read)
        read_out = super().read()
        data_read = read_out & 0xffff  # Data is only in bottom 16 bits
        return data_read

    def set_config_bin(self, data, mask=0xffff):
        """Set the configuration register with a binary number."""

        # Write new config
        return self.write('CONFIG', data, mask)

    def set_config(self, ALM_SEL=0, ALM_EN=0, CRC_EN=0, FSDO=0, DSDO=0, REF_PWDWN=0, DAC7_PWDWN=0, DAC6_PWDWN=0, DAC5_PWDWN=0, DAC4_PWDWN=0, DAC3_PWDWN=0, DAC2_PWDWN=0, DAC1_PWDWN=0, DAC0_PWDWN=0):
        """Set the configuration register with multiple arguments."""

        params = [ALM_SEL, ALM_EN, CRC_EN, FSDO,
                  DSDO, REF_PWDWN, DAC7_PWDWN, DAC6_PWDWN, DAC5_PWDWN, DAC4_PWDWN, DAC3_PWDWN, DAC2_PWDWN, DAC1_PWDWN, DAC0_PWDWN]
        mask = ''
        for bit in range(params):
            if params[bit] == None:
                mask += '0'
                params[bit] = 0
            else:
                mask += '1'
        mask = int(mask)

        # TODO: is this right?
        bit = 13
        data = 0
        for i in range(len(params)):
            data += params[i]*2**bit
        self.set_config_bin(data, mask)

    def get_config(self, display_values=True):
        """Return and print the current configuration register data."""

        config = self.read('CONFIG')
        if not config:
            print('Get Configuration: FAIL')
            return False
        if display_values:
            for key in ['ALM-SEL', 'ALM-EN', 'CRC-EN', 'FSDO', 'DSDO', 'REF-PWDWN',
                        'DAC7-PWDWN', 'DAC6-PWDWN', 'DAC5-PWDWN', 'DAC3-PWDWN',
                        'DAC3-PWDWN', 'DAC2-PWDWN', 'DAC1-PWDWN', 'DAC0-PWDWN']:
                # High and low bit indexes are the same because it is 1 bit wide
                print(f"{key}: {bool(config & DAC80508.registers.get(key).bit_index_low)}")
        return config

    def set_gain(self, data, mask=0x01ff):
        """Set the gain value."""

        return self.write('GAIN', data, mask)

    def get_gain(self):
        """Get the gain value."""

        return self.read('GAIN')

    def get_id(self, display=True):
        """Print the device info and return its ID."""

        id = self.read('ID')
        print(f'ID = {id} = {bin(id)}')
        if not id:  # Check to see if the read worked
            print('ID could not be read')
            return False
        if display:
            device_id = bin(id >> 2)[2:]  # Only from 2 on to skip the '0b'
            version_id = bin(id & 0b11)[2:]
            resolution = {'000': '16-bit', '001': '14-bit', '010': '12-bit'}
            print(f'Resolution: {resolution.get(device_id[1:4])}')
            channels = {'1000': 8}
            print(f'Channels: {channels.get(device_id[4:8])}')
            reset = {'0': 'reset to zero', '1': 'reset to midscale'}
            print(f'Reset: {reset.get(device_id[8])}')
            print(f'Version ID: {version_id}')
        return id

    def reset(self):
        """Soft reset the chip."""

        ack = self.write('TRIGGER', 0b1010, 0x000f)
        if self.debug:
            if ack:
                print('Reset: SUCCESS')
            else:
                print('Reset: FAIL')
        return ack


class AD5453(SPIController):

    registers = Register.get_chip_registers('AD5453')
    bits=12,
    vref=2.5*2

    def __init__(self, fpga, master_config=0x3010, endpoints=None):

        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('AD5453')

        # master_config=0x3010 Sets CHAR_LEN=16, ASS, IE
        super().__init__(fpga=fpga, master_config=master_config, endpoints=endpoints)
        # Default to clocking data into the shift register on the falling edge of the clock
        self.clk_edge_bits = 0b00

    # Method to set the control bits of the signals we write to use the rising edge of the clock rather than the default falling edge
    # To return to the falling edge, the chip requires a power cycle (turn it off and back on)
    def set_clk_rising_edge(self):
        self.clk_edge_bits = 0b11

    # Method to write 14 bits of data with the option to clock data on the rising edge of the clock rather than the default falling edge of the clock.
    def write(self, data):
        super().write((self.clk_edge_bits << 12) | data)

"""
class ADS7952(SPIController):
    registers = Register.get_chip_registers('ADS7952')

    def __init__(self, fpga, endpoints=Endpoint.get_chip_endpoints('ADS7952'), master_config=0x3010, increment=True):
        # master_config=0x3010 Sets CHAR_LEN=16, ASS, IE
        super().__init__(fpga=fpga, master_config=master_config,
                         endpoints=endpoints, increment=increment)
        self.channel = 0

    def to_voltage(self, a):
        bits = 12
        vref = 2.5*2
        masked = a & 0xfff  # 12 bit ADC
        v = masked/(2**bits - 1)*vref
        chan = (a & 0xf000) >> 12
        return v, chan

    # Method to set the operating mode of the chip. mode=0 -> manual, mode=1 -> Auto 1, mode=2 -> Auto 2
    def set_mode(self, mode):
        # [15:12] = 0b0001 Manual
        # [15:12] = 0b0010 Auto 1
        # [15:12] = 0b0011 Auto 2
        # [15:12] = 0b0000 Continue previous mode
        pass  # TODO: write method

    # Method to set the input range. range_bit=0 -> 0-Vref, or range_bit=1 -> 0-2*Vref
    def set_input_range(self, range_bit):
        # range_bit goes in the 16th bit of the Data In
        pass  # TODO: write method

    # Method to power down the device
    def power_down(self):
        # Set bit 5 = 1 to power down after the 16th SCLK falling edge
        pass  # TODO: write method

    # Method to select the output SDO. output_bit=0 -> current channel address and value, or output_bit=1 -> GPIO pins
    def set_output(self, output_bit):
        pass  # TODO: write method

    # Method to configure the GPIO program registers
    def set_gpio(self, data):
        pass  # TODO: write method

    # Method to read the desired channel
    def read_channel(self, channel):
        pass  # TODO: write method

    # Method to read the channel determined by the channel attribute
    def read(self):
        return self.read_channel(self.channel)

    # Method to set up the chip for use
    def setup(self):
        pass  # TODO: figure out what needs to be set up, if anything
"""


class ADCDATA():
    def __init__(self):
        pass

    def deswizzle(self, buf):
        d = np.frombuffer(buf, dtype=np.uint8).astype(np.uint32)
        if self.num_bits == 16:
            d1 = d[0::4] + (d[1::4] << 8)  # TODO: check the byte ordering
            d2 = d[2::4] + (d[3::4] << 8)
        elif self.num_bits == 18:
            # TODO: check 18-bit data conversion
            d2 = (d[3::4] << 8) + d[1::4] + ((d[0::4] << 16) & 0x03)

        c = np.empty((d1.size + d2.size,), dtype=d1.dtype)
        c[0::2] = d1
        c[1::2] = d2

        return c

    def convert_twos(self, d):
        return twos_comp(d, self.num_bits)

    def convert_data(self, buf):
        """
        deswizle and convert the twos complement representation
        """
        return self.convert_twos(self.deswizzle(buf))


    # TODO: test composite ADC function that enables, reads, converts and plots
    # TODO: incorporate/connect QT graphing (UIscript.py)
    def read(self, twos_comp_conv=True):
        # s, e = self.fpga.read_pipe_out(self.eps['AD796x_POUT_OFFSET'] + self.chan)
        s, e = self.fpga.read_pipe_out(self.endpoints['PIPE_OUT'].address)
        if twos_comp_conv:
            data = self.convert_data(s)
        else:
            data = self.deswizzle(s)
        return data

    def stream_mult(self, swps=4, twos_comp_conv=True):
        cnt = 0
        st = bytearray(np.asarray(np.ones(0, np.uint8)))
        self.fpga.xem.UpdateTriggerOuts()

        while cnt < swps:
            # check the FIFO half-full flag
            if (self.fpga.xem.IsTriggered(self.endpoints['FIFO_HALFFULL'].address,
                                          self.endpoints['FIFO_HALFFULL'].bit_index_low)):
                s, e = self.fpga.read_pipe_out(self.endpoints['PIPE_OUT'].address)
                st += s
                cnt = cnt + 1
                print(cnt)
            self.fpga.xem.UpdateTriggerOuts()
        if twos_comp_conv:
            data = self.convert_data(st)
        else:
            data = self.deswizzle(st)
        return data

# Class for the ADS8686 ADC chip.
class ADS8686(SPIController, ADCDATA):
    registers = Register.get_chip_registers('ADS8686')
    msg_w = 0x8000
    range = {10:  0b00,
             2.5: 0b01,
             5:   0b10}
    lpf_khz = {39:  0b00,
               15:  0b01,
               376: 0b10}

    def __init__(self, fpga, master_config=0x3610, endpoints=None):
        # master_config=0x3610 Sets CHAR_LEN=16, ASS (auto SlaveSelect),
        # IE (interrupt enable), Tx/Rx Negative Edge
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('ADS8686')
        super().__init__(fpga=fpga, master_config=master_config, endpoints=endpoints)
        self.ranges = [5]*16  # voltage ranges of all 16 channels
        self.num_bits = 16

    def write(self, msg, reg_name):
        reg = self.registers[reg_name].address << 9
        return super().write(reg | ADS8686.msg_w | msg)

    def read(self, reg_name):
        reg = self.registers[reg_name].address << 9
        super().write(reg)
        return super().read()

    # Method to read a desired channel on the chip
    def read_channel(self, channel):
        pass  # TODO: write method

    # Method to set up the chip
    def setup(self):  # TODO -- defaults to modify the SPI setup
        self.configure_master(self.master_config)
        self.set_frequency(5)
        self.select_slave(1)

    def set_range(self, vals):
        """ if a single value then all channels are given that value
        if a list of length 16 then each channel gets a separate range
        vals must be 10, 5, or 2.5
        """
        if not isinstance(vals, list):
            vals = [vals]*16
        if len(vals) != 16:
            print('Value must be a single number of list of length 16')
        self.ranges = vals

        towrite = 0
        regs = ['rangeA1', 'rangeA2', 'rangeB1', 'rangeB2']
        for idx, val in enumerate(vals):
            towrite += ADS8686.range[val] << ((idx % 4)*2)
            if idx % 4 == 3:
                print('Writing 0x{:x} to reg {}'.format(towrite, regs[idx//4]))
                self.write(towrite, regs[idx//4])
                towrite = 0

    def reg_to_voltage(self, reg_val, chan_num=0):
        """ Calculates the channels voltage from the register value
        using the stored gain range

        reg_val: list of ints or int
        """
        #  TODO: setup for sequence of channels
        val = twos_comp(reg_val, 16)  # 16-bit channel readings
        lsb = (self.ranges[chan_num]*2)/2**16
        return val*lsb

    def write_reg_bridge(self, clk_div=1000):
        """ setup the clk divider and spi_controller to continuously regAddr
        ADC data
        """
        # Configures the clock divider to determine the CONVST frequency
        self.fpga.xem.WriteRegister(self.endpoints['REGBRIDGE_OFFSET'].address + 0x0,
                                          clk_div)  # (1/200e6)*1000 = 5 us period
        # now load the sequence of wishbone commands that will be sent to the SPI converter
        self.fpga.xem.WriteRegister(self.endpoints['REGBRIDGE_OFFSET'].address + 0x1,
                                          0x8000_0001)  # Tx data register

        self.fpga.xem.WriteRegister(self.endpoints['REGBRIDGE_OFFSET'].address + 0x2,
                                          0x4000_0000)  # 0x0000 loaded into the Tx register -- for NOP

        self.fpga.xem.WriteRegister(self.endpoints['REGBRIDGE_OFFSET'].address + 0x3,
                                          0x8000_0041)  #

        self.fpga.xem.WriteRegister(self.endpoints['REGBRIDGE_OFFSET'].address + 0x4,
                                          0x4000_3710)  #
        # reset the clk divider
        self.fpga.send_trig(self.endpoints['CLK_DIV_RESET'])
        self.set_fpga_mode()  # lower the control bit for host vs. FPGA driven
                              # so the FPGA takes control of sending SPI

    def set_lpf(self, lpf):
        if lpf not in ADS8686.lpf_khz.keys():
            print('Error in ADS8686 LPF setup.')
            print('   Skipping ADS8686 LPF setup')
            print('   Frequency options are: {}'.format(list(ADS8686.lpf_khz.keys())))
            print('-'*40)
        else:
            self.write(ADS8686.lpf_khz[lpf], 'lpf')  # 376 khZ

    def setup_sequencer(self, range=5, lpf=376):
        base_creg = 0x0000  # default value
        self.write(base_creg, 'config')

        # set channels to be the fixed digital code
        # channel B = 0x5555; channel A = 0xAAAA
        #  this is over-written by sequencer anyways
        self.write((0xb | (0xb << 4)), 'chan_sel')

        # set the range of all channels to +/-5V
        self.set_range(range)  # sets all channels to +/-5V
        self.set_lpf(lpf)

        # setup the sequencer
        # sequence0: fixed values and then continue
        #   8 SSREN; 7-4 CHSEL_B; 3-0 CHSEL_A
        backto_first_stack = 0x100  # SSREN is bit 8

        self.write((0xb | (0xb << 4)), 'seq0')   # fixed pattern 0xaaaa on CHA; 0x5555 on CHB
        self.write((0x8 | (0x8 << 4)), 'seq1')   # AVDD
        self.write((0x9 | (0x9 << 4)), 'seq2')   # ALDO
        # CH0 and cycle back to seq0
        self.write(((0x0 | 0x0 << 4) | backto_first_stack), 'seq3')

        # enable the sequencer
        self.write(base_creg | 0x20, 'config')

    def set_host_mode(self):
        """ Configure SPI controller to be host driven """
        self.fpga.set_wire_bit(self.endpoints['HOST_FPGA_BIT'].address,
                               self.endpoints['HOST_FPGA_BIT'].bit_index_low)

    def set_fpga_mode(self):
        """ Configure SPI controller to be host driven """
        self.fpga.clear_wire_bit(self.endpoints['HOST_FPGA_BIT'].address,
                                 self.endpoints['HOST_FPGA_BIT'].bit_index_low)

    def hw_reset(self, val=True):
        #  ADS8686 active low hardware reset
        if val:
            self.fpga.clear_wire_bit(self.endpoints['RESET'].address,
                                     self.endpoints['RESET'].bit_index_low)

        elif not val:
            self.fpga.set_wire_bit(self.endpoints['RESET'].address,
                                   self.endpoints['RESET'].bit_index_low)


# Class for the AD7961 Fast ADC. Does not use SPI or I2C (uses LVDS).
class AD7961(ADCDATA):
    """An interface to the AD7961 ADC
    Passed the FPGA object
    Allows for multiple channels
    read status flags (FIFO full, empty, count and PLL)
    configures FPGA internal resets
    configures chip specific and global enables
    Formats data returned from the wire out
    """

    # the AD7961 does not have internal registers -- just OK endpoints

    def __init__(self, fpga, chan=0, endpoints=None):
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('AD7961')
        self.fpga = fpga
        self.endpoints = endpoints
        self.chan = chan  # starts at 0
        self.name = 'AD7961'
        self.num_bits = 16  # for AD7961 bits=18 for AD7960

        # self.eps = {'AD796x_POUT_OFFSET': 0xA1,
        #             'ADC_PLL_LOCKED_STATUS_WIRE_OUT': 0x21,
        #             'GENERAL_RST_VALID_TRIG_IN_ADDR': 0x40,
        #             'TI40_PLL_RST': 0x03,
        #             'TI40_ADC_RST': 19,
        #             'TI40_ADC_FIFO_RST': 4,
        #             'WI02_A_EN0': 1,
        #             'WI02_A_EN': 15}

    def get_status(self):
        """ Get AD796x status:
        pll lock, FIFO full, half-full, and empty

        Returns: dictionary of status
        """
        status = self.get_fifo_status()
        pll_lock = self.get_pll_status()
        status['pll_lock'] = pll_lock
        for k in status:
            print('{} status of {} = {}'.format(self.name,
                                                k, status[k]))
        return status

    def get_pll_status(self):
        return self.fpga.read_wire_bit(self.endpoints['PLL_LOCKED'].address,
                                       self.endpoints['PLL_LOCKED'].bit_index_low)

    def get_fifo_status(self):
        flags = ['FULL', 'HALFFULL', 'EMPTY']
        fifo_status = {}
        self.fpga.xem.UpdateTriggerOuts()
        for k in flags:
            fifo_status[k] = self.fpga.xem.IsTriggered(self.endpoints['FIFO_{}'.format(k)].address,
                                                       self.endpoints['FIFO_{}'.format(k)].bit_index_low)
        return fifo_status

    """
    Enable pins:
    0000 - power down
    1001 - enabled with ref buffer on; 28 MHZ
    0100 - test patterns on LVDS
    1101 - enabled with ref buffer on; 9 MHZ
    Note that EN[3]=1 enables the VCM output buffer.
    """

    def power_down_adc(self):
        # power down single channel of the ADC
        # fails if the global enables are 010 for LVDS test patterns
        # don't
        self.set_enables(0b0, global_enables=False)

    def test_pattern(self):
        # enable PRBS test pattern on the LVDS interface
        self.set_enables(0x0100)

    def power_up_adc(self, bw='28M'):
        if bw == '28M':
            self.set_enables(0x1001)
        elif bw == '9M':
            self.set_enables(0x1101)
        else:
            print('incorrect input sampling bandwidth for {}:Channel{}'.format(self.name,
                                                                        self.chan))

    def power_down_all(self):
        self.set_enables(0b0000)  # TODO: should I return anything here?

    def reset_pll(self):
        return self.fpga.xem.ActivateTriggerIn(self.endpoints['PLL_RESET'].address,
                                               self.endpoints['PLL_RESET'].bit_index_low)

    def reset_fifo(self):
        """resets the FIFO for the ADC data
            one per channel"""
        return self.fpga.xem.ActivateTriggerIn(self.endpoints['FIFO_RESET'].address,
                                               self.endpoints['FIFO_RESET'].bit_index_low)

    def reset_trig(self):
        """resets the FPGA controller for the ADC
            one per channel
            uses the Opal Kelly Trigger"""
        return self.fpga.xem.ActivateTriggerIn(self.endpoints['RESET'].address,
                                               self.endpoints['RESET'].bit_index_low)

    def reset_wire(self, value):
        """sets the value of the wire to reset the FPGA controller for the ADC
            value = 1 is reset
            value = 0 releases reset
            uses the Opal Kelly WireIn (the trigger can't hold the reset)
        """
        if value == 1:
            self.fpga.set_wire_bit(self.endpoints['WIRE_RESET'].address,
                                   self.endpoints['WIRE_RESET'].bit_index_low)
        if value == 0:
            self.fpga.clear_wire_bit(self.endpoints['WIRE_RESET'].address,
                                     self.endpoints['WIRE_RESET'].bit_index_low)

    def power_down_fpga(self):
        """power down the FPGA controller through wirein"""
        # TODO: add functionality (wirein bit) to the FPGA
        #       this would reduce FPGA power consumption
        self.reset_wire(0)

    def set_enables(self, value=0b0000, global_enables=True):
        # will always set the EN0 specific to this channel (LSB in values)
        # optionally also modify the global enables (all channels)

        mask = gen_mask(self.endpoints['ENABLE'].bit_index_low)
        if global_enables:
            # global enables (connect to all AD7961); create a list of bit position
            gl_mask = [x+self.endpoints['GLOBAL_ENABLE'].bit_index_low
                       for x in range(self.endpoints['GLOBAL_ENABLE_LEN'].bit_index_low)]
            # or global mask with the signal channel EN0 mask
            mask = gen_mask(gl_mask) | mask
        # setup the values
        # value = (self.eps['WI02_A_EN0'] + self.chan)
        value_chan = (value & 0b0001) << (self.endpoints['ENABLE'].bit_index_low)
        if global_enables:
            #  globabl enables are the 3 MSBs
            val_global = (value & 0b1110) << (self.endpoints['GLOBAL_ENABLE'].bit_index_low - 1)  # minus 1 since
            print('Global value = 0x{:0x}'.format(val_global))
            value = value_chan | val_global

        print('Enables setting value = 0x{:0x} with mask = = 0x{:0x}'.format(value, mask))
        self.fpga.set_wire(self.endpoints['ENABLE'].address, value, mask=mask)

    def setup(self, reset_pll=False):
        """
        0) put ADC controller into reset
        1) optionally reset the ADC PLL and wait for lock
            (only need to reset PLL on first channel)
        2) power up adc
        3) release ADC controller reset
        4) reset fifo
        5) check and return status (PLL and fifo)
        """
        self.reset_wire(1)
        if reset_pll:
            # reset PLL
            self.reset_pll()
            pll_cnt = 0
            while not self.get_pll_status():
                time.sleep(0.01)
                pll_cnt += 1
                if pll_cnt > 20:
                    print('PLL lock timeout')
                    return -1
        # enable ADC
        self.power_up_adc()
        # now that PLL is locked and ADC is ready
        # release the reset of the ADC controller
        # self.reset_trig()
        self.reset_wire(0)  # releases the reset
        # reset FIFO
        self.reset_fifo()
        status = self.get_status()
        # TODO: the FIFO is guaranteed to overflow
        return status


def disp_device(dev, reg=True):

    print('Displaying endpoints')
    for k in dev.endpoints:
        print(k + ': ' + str(dev.endpoints[k]))

    print('-'*40)
    if reg:
        print('Displaying registers')
        try:
            for r in dev.registers:
                print(r + ': ' + str(dev.registers[r]))
        except:
            pass
