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
import struct
import time
from interfaces.utils import gen_mask, twos_comp, test_bit, int_to_list, from_voltage, to_voltage
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
    """

    def __init__(self, address, default, bit_index_high, bit_index_low, bit_width):
        self.address = address
        self.default = default
        self.bit_index_high = bit_index_high
        self.bit_index_low = bit_index_low
        self.bit_width = bit_width

    def __str__(self):
        return f'{hex(self.address)}[{self.bit_index_low}:{self.bit_index_high}]'

    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        else:
            return False

    @staticmethod
    def get_chip_registers(sheet, workbook_path=None):
        """Return a dictionary of Registers from a page in an Excel spreadsheet."""

        if workbook_path == None:
            workbook_path = os.getcwd()
            # The Registers spreadsheet is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
            for i in range(15):
                if os.path.basename(workbook_path) == 'covg_fpga':
                    workbook_path = os.path.join(
                        workbook_path, 'python', 'Registers.xlsx')
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
        Class attribute. Dictionary of each group of endpoints paired with inner dictionaries
        of endpoint names to Endpoint objects, starts empty.
    I2CDAQ_level_shifted : dict
        Class attribute. Dictionary of Endpoints for the level shifted I2CDAQ bus.
    I2CDAQ_QW : dict
        Class attribute. Dictionary of Endpoints for QW 3.3V I2CDAQ bus.
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
    """

    endpoints_from_defines = dict()
    I2CDAQ_level_shifted = dict()
    I2CDAQ_QW = dict()

    def __init__(self, address, bit_index_low, bit_width, gen_bit, gen_address):
        self.address = address
        self.bit_index_low = bit_index_low
        # Endpoints that are only containing addresses will be generated from ep_defines.v with bit_index_low = None
        if bit_index_low == None:
            self.bit_index_high = None
        else:
            self.bit_index_high = bit_index_low + bit_width
        self.bit_width = bit_width
        self.gen_bit = gen_bit
        self.gen_address = gen_address

    def __str__(self):
        str_rep = '0x{:0x}[{}:{}]'.format(
            self.address, self.bit_index_low, self.bit_index_high)
        return str_rep

    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        else:
            return False

    @staticmethod
    def update_endpoints_from_defines(ep_defines_path=None):
        """Store and return a dictionary of Endpoints for each chip in ep_defines.v.

        Returns -1 if there is a naming collision in ep_defines.v
        """

        # Find ep_defines.v path
        if ep_defines_path == None:
            ep_defines_path = os.getcwd()
            # The Registers spreadsheet is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
            for i in range(15):
                if os.path.basename(ep_defines_path) == 'covg_fpga':
                    ep_defines_path = os.path.join(
                        ep_defines_path, 'fpga_XEM7310', 'fpga_XEM7310.srcs', 'sources_1', 'ep_defines.v')
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

            # Address, bit, and bit_width
            if "8'h" in pieces[2]:
                # Definition holds an address, take that value
                address = int(pieces[2][3:], base=16)
                bit = None
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
                    address_name_no_gen = address_name.split(
                        '_GEN', maxsplit=1)[0]
                    address = address_name_no_gen
                bit = int(pieces[2])
                bit_width = int(pieces[5].split('=')[1])

            endpoint = Endpoint(address=address, bit_index_low=bit, bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)

            # Put defined endpoint in endpoints_from_defines dictionary
            if Endpoint.endpoints_from_defines.get(class_name) is None:
                # Class doesn't exist yet in the dictionary
                Endpoint.endpoints_from_defines[class_name] = {
                    ep_name: endpoint}
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
                    class_name, ep_name = endpoint.address.split(
                        '_', maxsplit=1)
                    referenced_group = Endpoint.endpoints_from_defines.get(
                        class_name)
                    if referenced_group is None:
                        print(
                            f'{group_name}[{endpoint_name}]: Referenced group "{class_name}" not found.')
                        continue
                    referenced_endpoint = referenced_group.get(ep_name)
                    if referenced_endpoint is None:
                        print(
                            f'{group_name}[{endpoint_name}]: Referenced endpoint "{class_name}_{ep_name}" not found.')
                        continue
                    endpoint.address = referenced_endpoint.address

        # At this point the dictionary should be built
        # Check for naming collisions (2+ names sharing same address or bit within address)
        # Collect all top level endpoints
        top_level_eps = [
            x for x in Endpoint.endpoints_from_defines.values() if type(x) == Endpoint]
        # Collect all endpoints in dictionaries
        lower_level_eps = []
        for eps in [d.values() for d in Endpoint.endpoints_from_defines.values() if type(d) == dict]:
            lower_level_eps += list(eps)
        none_to_neg_1 = {None: -1}
        # Make tuples of (address, bit) from each list, then concatenate the lists
        # The none_to_neg_1.get() translates None values of bit_index_low to -1 for sorting later
        list_eps = [(ep.address, none_to_neg_1.get(ep.bit_index_low, ep.bit_index_low)) for ep in top_level_eps]
        list_len = len(list_eps)
        set_len = len(set(list_eps))  # A set removes duplicates

        if list_len != set_len:
            # There may be duplicates. May not, because different groups can have endpoints of the same name.
            print('Checking for naming collisions in ep_defines.v ...')

            # Search through to find duplicates
            # Copy the list to keep order in the original
            sorted_list_eps = list(list_eps)
            sorted_list_eps.sort()  # Put duplicates next to one another in new list
            top_level_names = [x for x in Endpoint.endpoints_from_defines.keys() if type(
                Endpoint.endpoints_from_defines[x]) == Endpoint]
            lower_level_names = []
            for sub_dicts in [x for x in Endpoint.endpoints_from_defines.values() if type(x) == dict]:
                lower_level_names += list(sub_dicts.keys())
            list_names = top_level_names + lower_level_names

            collision = False  # Keep track of whether there was a collision for return value
            for ep_index in range(len(sorted_list_eps) - 1):
                ep = sorted_list_eps[ep_index]
                next_ep = sorted_list_eps[ep_index + 1]
                name = list_names[list_eps.index(sorted_list_eps[ep_index])]
                next_name = list_names[list_eps.index(
                    sorted_list_eps[ep_index])]
                if (ep == next_ep) and (name != next_name):
                    # Need different names because otherwise they are from different groups and do not actually conflict

                    # The name part of this uses a list of names created in the same order as the original list_eps (list_names)
                    # then finds the index of the current endpoint in list_eps and uses that to find the corresponding
                    # name in list_names
                    print(
                        f'Collision found at address={ep[0]} bit={ep[1]}: {name} with {next_name}')
                    collision = True
            if collision:
                return -1
            else:
                print('No collisions found.')

        # If the list and set match length, no duplicates
        return Endpoint.endpoints_from_defines

    @staticmethod
    def get_chip_endpoints(chip_name):
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

    @staticmethod
    def increment_endpoints(endpoints_dict, in_place=True):
        """Increment all Endpoints in endpoints_dict.

        Use each Endpoint's gen_bit and gen_addr values to determine whether to
        increment bits and addresses, respectively.

        Parameters
        ----------
        endpoints_dict : dict
            The dict of Endpoints to increment.
        in_place : bool
            If True, the dictionary given will be changed. Otherwise, a copy
            of the dictionary will be made.
        """

        if not in_place:
            # Make a copy
            endpoints_dict = copy.deepcopy(endpoints_dict)

        for key in endpoints_dict:
            endpoint = endpoints_dict[key]
            if endpoint.gen_bit and endpoint.gen_address:
                # Increment the bit by the endpoint's bit_width and if it would
                # go outside the address's width, increment the address
                # TODO: do we want to wrap around the bits on the same address, -> can change address on each bit individually
                # or shift all bits when one moves to the next address? -> each bit needs to know if other bits fit on the current address as well
                pass
            elif endpoint.gen_bit:
                # Increment the bit by the bit_width
                endpoint.bit_index_low += endpoint.bit_width
                endpoint.bit_index_high = endpoint.bit_index_low + endpoint.bit_width
            elif endpoint.gen_address:
                # Increment the address by 1
                endpoint.address += 1

        return endpoints_dict

    @staticmethod
    def excel_to_defines(excel_path, defines_path, sheet=0):
        """Convert an Excel spreadsheet of endpoint definitions to Verilog.

        Parameters
        ----------
        excel_path : str
            The path to the Excel spreadsheet to convert.
        defines_path : str
            The path to the Verilog file to create.
        sheet : int or str
            Optional. The int index of the sheet to read from the Excel
            spreadsheet, or the str sheet name.

        Returns
        -------
        str : the text written to the Verilog file.
        """

        sheet_data = pd.read_excel(excel_path, sheet)
        text = '\n'.join(sheet_data['Generated Line'])
        with open(defines_path, 'w') as file:
            file.write(text)
        return text


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
            endpoint.bit_index_low = (
                endpoint.bit_index_low + (endpoint.bit_width*num))
            endpoint.bit_index_high = endpoint.bit_index_low + endpoint.bit_width
        if endpoint.gen_address:
            print(f'gen address bit_width: {endpoint.bit_width}')
            endpoint.address += 1
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
    """

    # TODO: change to complete bitfile when Verilog is combined
    def __init__(self, bitfile=os.path.join('..', '..', 'fpga_test.bit'),
                 debug=False):

        self.bitfile = bitfile
        self.debug = debug
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
        print("       USB Speed  %d" % self.device_info.usbSpeed)

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
        # print('read_pipe_out:', addr, buf)

        if (e < 0):
            print('Error code {}'.format(e))
        return buf, e

    def set_wire(self, address, value, mask=0xFFFFFFFF):
        """Return the error code after setting an OK WireIn value."""
        if self.debug:
            print(
                f'set_wire(address={hex(address)}, value={hex(value)}, mask={hex(mask)})')
        error_code = self.xem.SetWireInValue(address, value, mask)
        self.xem.UpdateWireIns()
        return error_code

    def read_wire(self, address):
        """Return the read data after reading an OK WireOut."""

        self.xem.UpdateWireOuts()
        return self.xem.GetWireOutValue(address)

    def set_endpoint(self, ep_bit):
        """Set all bits in an Endpoint high."""

        mask = gen_mask(
            list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        if self.debug:
            print(
                f'set_endpoint(address={hex(ep_bit.address)}, value={hex(mask)}, mask={hex(mask)})')
        self.xem.SetWireInValue(ep_bit.address, mask, mask)  # set
        self.xem.UpdateWireIns()

    def clear_endpoint(self, ep_bit):
        """Set all bits in an Endpoint low."""

        mask = gen_mask(
            list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        if self.debug:
            print(
                f'clear_endpoint(address={hex(ep_bit.address)}, value={hex(0)}, mask={hex(mask)})')
        self.xem.SetWireInValue(ep_bit.address, 0x0000, mask)  # clear
        self.xem.UpdateWireIns()

    def toggle_low(self, ep_bit):
        """Toggle all bits in an Endpoint low then back to high."""

        mask = gen_mask(
            list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        self.xem.SetWireInValue(
            ep_bit.address, 0x0000, mask)  # toggle low
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(ep_bit.address, mask, mask)   # back high
        self.xem.UpdateWireIns()

    def toggle_high(self, ep_bit):
        """Toggle all bits in an Endpoint high then back to low."""

        mask = gen_mask(
            list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        self.xem.SetWireInValue(ep_bit.address, mask, mask)  # toggle high
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(ep_bit.address, 0x0000, mask)   # back low
        self.xem.UpdateWireIns()

    def send_trig(self, ep_bit):
        """Return the error code after activating an OK TriggerIn Endpoint.

        Expects a single bit, not yet implement for multiple bits and will only
        activate the LSB if the Endpoint containts multiple bits.
        """

        # print(f'send_trig(address={hex(ep_bit.address)},bit={ep_bit.bit_index_low})')
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

        if self.debug:
            print(
                f'set_wire_bit(address={hex(address)},value={hex(1 << bit)},mask={hex(1 << bit)})')
        return self.set_wire(address, value=1 << bit, mask=1 << bit)

    def clear_wire_bit(self, address, bit):
        """Clear a single bit to 0 in a OpalKelly wire in."""
        if self.debug:
            print(
                f'clear_wire_bit(address={hex(address)},value={hex(1 << bit)},mask={hex(1 << bit)})')

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
    """

    I2C_MAX_TIMEOUT_MS = 50

    def __init__(self, fpga, addr_pins, endpoints, i2c={'m_pBuf': [], 'm_nDataStart': 7}):
        self.i2c = i2c
        self.fpga = fpga
        self.addr_pins = addr_pins
        self.endpoints = endpoints

    @classmethod
    def create_chips(cls, fpga, addr_pins, endpoints):
        """Instantiate a number of new I2C chips.

        The FPGA and endpoints will be the same for all instantiated chips.

        Parameters
        ----------
        fpga : FPGA
            The fpga instance for the chip to connect with.
        addr_pins : list
            The list of addr_pins assigned to the new chips.

        Returns
        -------
        list
            A list of the newly instantiated chips in the same order addr_pins was given in.
        """

        return [cls(fpga=fpga, addr_pins=addr, endpoints=endpoints) for addr in addr_pins]


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
            mask = 0xff << self.endpoints['IN'].bit_index_low
            value = self.i2c['m_pBuf'][i] << self.endpoints['IN'].bit_index_low
            self.fpga.xem.SetWireInValue(
                self.endpoints['IN'].address, value, mask)
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
            mask = 0xff << self.endpoints['IN'].bit_index_low
            value = self.i2c['m_pBuf'][i] << self.endpoints['IN'].bit_index_low
            self.fpga.xem.SetWireInValue(
                self.endpoints['IN'].address, value, mask)
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
                            self.endpoints['OUT'].address)
                        mask = 0xff << self.endpoints['OUT'].bit_index_low
                        data[i] = (
                            data_tmp & mask) >> self.endpoints['OUT'].bit_index_low
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

        Parameters
        ----------
        devAddr : int
            8 bit address (don't set the read bit (LSB) since this is done in this function)
        regAddr : int
            Written to device (this is a list and must be even if length 1)
        data_length : int
            Number of bytes expected to receive
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

        voltage_data = from_voltage(voltage=voltage, num_bits=10, voltage_range=5, with_negatives=False)

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
    """

    WB_SET_ADDRESS = 0x80000000  # These 3 are from the SPI core manual
    WB_WRITE = 0x40000000
    WB_READ = 0x00000000
    # ACK=0x200000000
    WB_CLK_FREQ = 200  # clk_sys = 200 MHz in the top_level_module.v comments

    registers = Register.get_chip_registers('SPI')

    def __init__(self, fpga, endpoints, master_config=registers.get('CTRL').default):
        self.fpga = fpga
        self.master_config = master_config
        self.endpoints = endpoints

    @classmethod
    def create_chips(cls, fpga, number_of_chips, endpoints=None, master_config=None):
        """Instantiate a number of new chips.

        The number must be an integer greater than zero. The endpoints between
        each instance will be incremented. If the endpoints argument is left
        as None, then we will use copies of the endpoints_from_defines
        dictionary for the endpoints for each instance, and update that
        original dictionary when we increment the endpoints. This way, the
        endpoints there are ready for another instantiation if needed.
        """

        if type(number_of_chips) is not int or number_of_chips <= 0:
            print('number_of_chips must be an integer greater than 0')
            return False

        chips = []
        if master_config is None:
            # Use class default for master_config
            for i in range(number_of_chips):
                chips.append(cls(fpga=fpga, endpoints=endpoints))
                # Use deepcopy to keep the endpoints for different instances separate
                endpoints = copy.deepcopy(chips[-1].endpoints)
                Endpoint.increment_endpoints(endpoints)
        else:
            for i in range(number_of_chips):
                chips.append(cls(fpga=fpga, endpoints=copy.deepcopy(
                    endpoints), master_config=master_config))
                # Use deepcopy to keep the endpoints for different instances separate
                endpoints = copy.deepcopy(chips[-1].endpoints)
                Endpoint.increment_endpoints(endpoints)

        if endpoints is None:
            # Increment shared endpoints dictionary
            # TODO: is there a better way to do this?
            # We need to get the shared endpoints in endpoints_from_defines to
            # increment and we only have the endpoints given to us in the
            # argument.
            shared_full_eps = Endpoint.endpoints_from_defines
            shared_chip_eps = shared_full_eps[
                list(shared_full_eps.keys())[
                    list(shared_full_eps.values()).index(chips[0].endpoints)
                    ]
                ]
            for i in range(number_of_chips):
                Endpoint.increment_endpoints(shared_chip_eps)
        else:
            # Increment custom dictionary
            Endpoint.increment_endpoints(endpoints)

        return chips

    def wb_send_cmd(self, command):
        """Send a command to the Wishbone.

        Sent in 32 bits through the WbSignal_converter Verilog module tos
        reformat to 34 bits.
        """

        # print(f'wb_send_cmd: {hex(self.endpoints["WB_IN"].address)}, {hex(command)}')
        self.fpga.set_wire(
            self.endpoints['WB_IN'].address, command, 0xffffffff)
        # DEBUG: temporary for logging DAC80508 test
        # print(f'ActivateTriggerIn(address={hex(self.parameters["WB_CONVERT"].address)}, index={hex(self.parameters["WB_CONVERT"].bit_index_high)}')

        # allows for optional debug prints
        self.fpga.send_trig(self.endpoints['WB_CONVERT'])
        #self.fpga.xem.ActivateTriggerIn(
        #    self.endpoints['WB_CONVERT'].address, self.endpoints['WB_CONVERT'].bit_index_low)  # High and low bit indexes are the same for the trigger because it is 1 bit wide

    def wb_is_ack(self):
        """Check if the Wishbone sent back a write acknowledge."""

        pass
    #     response = self.fpga.read_wire(self.endpoints['OUT'].address)
    #     return response == SPIController.ACK

    def wb_set_address(self, address):
        """Set the address of the register we interact with in the Wishbone."""

        self.wb_send_cmd(
            SPIController.WB_SET_ADDRESS | (address << 2) | 0x1)  # TODO: comment here what the | 0x1 is for when I figure it out
        return self.wb_is_ack()  # TODO: test if acknowledge actually comes back

    def wb_write(self, data):
        """Write up to 30 bytes of data to the currently selected register."""

        self.wb_send_cmd(SPIController.WB_WRITE | data)
        return self.wb_is_ack()  # TODO: test if acknowledge actually comes back

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
        """Set the frequency of SPI SCLK.

        Set the DIVIDER register of the Wishbone with the corresponding divider
        for the target frequency. Frequency must be given in MHz.
        """

        divider = max(
            round((SPIController.WB_CLK_FREQ) / (frequency * 2)), 1) - 1
        # Make sure divider does not exceed 32 bits
        divider = min(divider, 0xffff_ffff)
        # print('Set frequency. Divider value = {}'.format(divider))
        self.set_divider(divider)
        return divider

    def write(self, data, register=0):
        """Write data on the SPI lines.

        Register should be either 0, 1, 2, or 3.
        """

        # Set address to Tx register
        ack = self.wb_set_address(
            SPIController.registers['Tx' + str(register)].address)
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
        ack = self.wb_set_address(
            SPIController.registers['Rx' + str(register)].address)

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

        Parameters
        ----------
        ASS : bool or int
            Automatic Slave Select
        IE : bool or int
            Set interrupt output active after a transfer is finished
        LSB : bool or int
            Send LSB first
        Tx_NEG : bool or int
            Change output signal on falling edge of SCLK
        Rx_NEG : bool or int
            Latch input signal on falling edge of SCLK
        CHAR_LEN : bool or int
            Number of bits transmitted per transfer (up to 64).
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

    def set_host_mode(self):
        """ Configure SPI controller to be host driven."""

        self.fpga.set_wire_bit(self.endpoints['HOST_FPGA'].address,
                               self.endpoints['HOST_FPGA'].bit_index_low)

    def set_fpga_mode(self):
        """ Configure SPI controller to be host driven."""

        self.fpga.clear_wire_bit(self.endpoints['HOST_FPGA'].address,
                                 self.endpoints['HOST_FPGA'].bit_index_low)


class SPIFifoDriven():
    """Class for SPI controllers on the FPGA driven by a FIFO.

    Attributes
    ----------
    default_data_mux : dict
        Class attribute. Default data_mux dictionary.
    fpga : FPGA
        FPGA instance this controller uses to communicate.
    endpoints : dict
        Endpoints on the FPGA this controller uses to communicate.
    master_config : int
        Value of the CTRL register in the Wishbone.
    data_mux: dict
        Name to select value dictionary for source data MUX.
    current_data_mux : str
        Name of the current MUX data source.
    """

    default_data_mux = {
        'DDR': 0,
        'host': 1,
        'ads8686_chA': 2,
        'ads8686_chB': 3,
        'ad7961_ch0': 4,
        'ad7961_ch1': 5,
        'ad7961_ch2': 6,
        'ad7961_ch3': 7,
    }

    def __init__(self, fpga, endpoints, master_config, data_mux=default_data_mux):
        self.fpga = fpga
        self.endpoints = endpoints
        self.master_config = master_config
        self.data_mux = data_mux
        # Start with host to minimize unintentional commands from other sources on startup
        self.current_data_mux = None
        if self.set_data_mux('host') == -1:
            # 'host' was not in data_mux dict
            print("WARNING: no 'host' in data_mux dict")

    @classmethod
    def create_chips(cls, fpga, number_of_chips, endpoints=None, master_config=None):
        """Instantiate a number of new chips.

        The number must be an integer greater than zero. The endpoints between
        each instance will be incremented. If the endpoints argument is left
        as None, then we will use copies of the endpoints_from_defines
        dictionary for the endpoints for each instance, and update that
        original dictionary when we increment the endpoints. This way, the
        endpoints there are ready for another instantiation if needed.
        """

        if type(number_of_chips) is not int or number_of_chips <= 0:
            print('number_of_chips must be an integer greater than 0')
            return False

        chips = []
        if master_config is None:
            # Use class default for master_config
            for i in range(number_of_chips):
                chips.append(cls(fpga=fpga, endpoints=endpoints))
                # Use deepcopy to keep the endpoints for different instances separate
                endpoints = copy.deepcopy(chips[-1].endpoints)
                Endpoint.increment_endpoints(endpoints)
        else:
            for i in range(number_of_chips):
                chips.append(cls(fpga=fpga, endpoints=copy.deepcopy(
                    endpoints), master_config=master_config))
                # Use deepcopy to keep the endpoints for different instances separate
                endpoints = copy.deepcopy(chips[-1].endpoints)
                Endpoint.increment_endpoints(endpoints)

        if endpoints is None:
            # Increment shared endpoints dictionary
            # TODO: is there a better way to do this?
            # We need to get the shared endpoints in endpoints_from_defines to
            # increment and we only have the endpoints given to us in the
            # argument.
            shared_full_eps = Endpoint.endpoints_from_defines
            shared_chip_eps = shared_full_eps[
                list(shared_full_eps.keys())[
                    list(shared_full_eps.values()).index(chips[0].endpoints)
                ]
            ]
            for i in range(number_of_chips):
                Endpoint.increment_endpoints(shared_chip_eps)
        else:
            # Increment custom dictionary
            Endpoint.increment_endpoints(endpoints)

        return chips

    def filter_select(self, operation='set'):
        """Set whether SPI data comes from filter ('set') or direct ('clear')

        Direct comes from the spi_fifo_driven data.
        """

        if operation == 'set':
            self.fpga.set_wire_bit(self.endpoints['FILTER_SEL'].address,
                                   self.endpoints['FILTER_SEL'].bit_index_low)
        elif operation == 'clear':
            self.fpga.clear_wire_bit(self.endpoints['FILTER_SEL'].address,
                                     self.endpoints['FILTER_SEL'].bit_index_low)
        else:
            print(f'Incorrect operation: {operation} for filter select \n')

    def set_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        mask = gen_mask(range(self.endpoints['DATA_SEL'].bit_index_low,
                              self.endpoints['DATA_SEL'].bit_index_high))
        data = (self.data_mux[source]
                << self.endpoints['DATA_SEL'].bit_index_low)
        self.fpga.set_wire(self.endpoints['DATA_SEL'].address, data,
                           mask=mask)
        self.current_data_mux = source

    def set_clk_divider(self, divide_value):
        """Set clock divider to configure rate of SPI updates.

        Tupdate = Tclk * divide_value
        """
        mask = gen_mask(range(self.endpoints['PERIOD_ENABLE'].bit_index_low,
                              self.endpoints['PERIOD_ENABLE'].bit_index_high))

        self.fpga.set_wire(self.endpoints['PERIOD_ENABLE'].address,
                           divide_value << self.endpoints['PERIOD_ENABLE'].bit_index_low,
                           mask)

        # resets the SPI state machine
        self.fpga.xem.ActivateTriggerIn(self.endpoints['REG_TRIG'].address,
                                        self.endpoints['REG_TRIG'].bit_index_low)

    def set_ctrl_reg(self, reg_value):
        """Configures the SPI Wishbone control register over the registerBridge.

        HDL default is ctrlValue = 16'h3010 (initialized in the HDL)
        """

        self.fpga.xem.WriteRegister(self.endpoints['REGBRIDGE_OFFSET'].bit_index_low, reg_value)

        # resets the SPI state machine -- needed since these registers are only
        #   programmed at startup of the state machine
        self.fpga.xem.ActivateTriggerIn(self.endpoints['REG_TRIG'].address,
                                        self.endpoints['REG_TRIG'].bit_index_low)

    def set_spi_sclk_divide(self, divide_value=0x01):
        """Configures the SPI Wishbone clock divider register over the registerBridge.

        HDL default is 8'h13 (initialized in the HDL)
        """

        sys_clk = 200  # in MHz
        print('SCLK predicted frequency {:.2f} [MHz]'.format(
            sys_clk/(divide_value+1)))
        self.fpga.xem.WriteRegister(self.endpoints['REGBRIDGE_OFFSET'].bit_index_low + 1, divide_value)

        # resets the SPI state machine -- needed since these WishBone
        #   registers are only programmed at startup of the state machine
        self.fpga.xem.ActivateTriggerIn(self.endpoints['REG_TRIG'].address,
                                        self.endpoints['REG_TRIG'].bit_index_low)

    def write(self, data):
        """Host write 24 bits of data to the chip over SPI."""

        if self.current_data_mux != 'host':
            self.set_data_mux('host')
        self.fpga.set_wire(self.endpoints['HOST_WIRE_IN'].address, data)
        self.fpga.xem.ActivateTriggerIn(self.endpoints['HOST_TRIG'].address,
                                        self.endpoints['HOST_TRIG'].bit_index_low)


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

    WRITE_OPERATION = 0x000000
    READ_OPERATION = 0x800000

    registers = Register.get_chip_registers('DAC80508')

    def __init__(self, fpga, master_config=0x3218, endpoints=None, data_mux=SPIFifoDriven.default_data_mux):
        # master_config=0x3218 Sets CHAR_LEN=24, Rx_NEG, ASS, IE
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('DAC80508')
        super().__init__(fpga=fpga, master_config=master_config, endpoints=endpoints, data_mux=data_mux)
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
        """Set the gain and reference divider.

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


class AD5453(SPIFifoDriven):
    # TODO: add class docstring

    bits = 12,
    vref = 2.5*2

    def __init__(self, fpga, master_config=0x3010, endpoints=None, data_mux=SPIFifoDriven.default_data_mux):

        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('AD5453')

        # master_config=0x3010 Sets CHAR_LEN=16, ASS, IE
        super().__init__(fpga=fpga, master_config=master_config,
                         endpoints=endpoints, data_mux=data_mux)
        # Default to clocking data into the shift register on the falling edge of the clock
        self.clk_edge_bits = 0b00

        self.filter_coeff = {0: 0x009e1586,
                             1: 0x20000000,
                             2: 0x40000000,
                             3: 0x20000000,
                             4: 0xbce3be9a,
                             5: 0x12f3f6b0,
                             8: 0x7fffffff,
                             9: 0x20000000,
                             10: 0x40000000,
                             11: 0x20000000,
                             12: 0xab762783,
                             13: 0x287ecada,
                             7: 0x7fffffff}

        self.filter_offset = 4
        self.filter_len = np.max(
            list(self.filter_coeff.keys())) - np.min(list(self.filter_coeff.keys()))
        self.current_data_mux = None
        self.set_data_mux('host')

    def set_clk_rising_edge(self):
        """Set the signals we write to use the rising edge of the clock.

        Default is falling edge. To return to the falling edge, the chip
        requires a power cycle (turn it off and back on).
        """

        self.clk_edge_bits = 0b11

    def set_ctrl_reg(self, reg_value=0x3010):
        """Configures the SPI Wishbone control register over the registerBridge.

        reg_value=0x3010 sets CHAR_LEN=16, ASS, IE
        """

        super().set_ctrl_reg(reg_value=reg_value)

    def write_filter_coeffs(self):
        # TODO: add method docstring

        # TODO is this correct? and how to parameterize?
        for i in np.arange(self.filter_offset, 1 + self.filter_offset + self.filter_len):
            if (i-self.filter_offset) in self.filter_coeff:
                addr = int(
                    self.endpoints['REGBRIDGE_OFFSET'].bit_index_low + i)
                val = int(self.filter_coeff[i-self.filter_offset])
                # TODO: ian has first addr of 0x19, second as 0x1a
                print(
                    'Write filter addr=0x{:02X}  value=0x{:02X}'.format(addr, val))
                self.fpga.xem.WriteRegister(addr, val)

    def write_filter_coeffs_simultaneous(self):
        # TODO: add method docstring

        # https://opalkelly.com/examples/setting-and-getting-multiple-registers/#tab-python
        loop_thru = np.arange(self.filter_offset, 1
                              + self.filter_offset + self.filter_len)
        regs = ok.okTRegisterEntries((len(loop_thru)))

        for i in loop_thru:  # TODO is this correct? and how to parameterize?
            if (i-self.filter_offset) in self.filter_coeff:
                addr = int(
                    self.endpoints['REGBRIDGE_OFFSET'].bit_index_low + i)
                val = int(self.filter_coeff[i-self.filter_offset])
                idx = int(i-self.filter_offset)
                regs[idx].address = addr
                regs[idx].data = val
                # TODO: ian has first addr of 0x19, second as 0x1a
                print(
                    'Write filter addr=0x{:02X}  value=0x{:02X}'.format(addr, val))
        self.fpga.xem.WriteRegisters(regs)

    def read_coeff_debug(self):
        """
        Read two wire outs for coefficients a3 section1, scale 3
        debug wires available for filters 0, 1
        """

        debug_coeff_0 = self.fpga.read_wire(
            self.endpoints[f'COEFF_DEBUG_0'].address)
        debug_coeff_1 = self.fpga.read_wire(
            self.endpoints[f'COEFF_DEBUG_1'].address)
        debug_coeff_2 = self.fpga.read_wire(
            self.endpoints[f'COEFF_DEBUG_2'].address)
        debug_coeff_3 = self.fpga.read_wire(
            self.endpoints[f'COEFF_DEBUG_3'].address)

        print(f'Read Coefficients:')
        print('    0:', debug_coeff_0)
        print('    1:', debug_coeff_1)
        print('    2:', debug_coeff_2)
        print('    3:', debug_coeff_3)
        return debug_coeff_0, debug_coeff_1, debug_coeff_2, debug_coeff_3

    def change_filter_coeff(self, target, value=None):
        # TODO: add method docstring

        if (target == 'passthru') or (target == 'passthrough'):
            self.filter_coeff = {0: 0x7fff_ffff,   # changed for about unity gain
                                 1: 0x20000000,
                                 2: 0,
                                 3: 0,
                                 4: 0,
                                 5: 0,
                                 8: 0x7fffffff,
                                 9: 0x20000000,
                                 10: 0,
                                 11: 0,
                                 12: 0,
                                 13: 0,
                                 7: 0x7fffffff,
                                 6: 0}
        elif target == '100kHz':
            self.filter_coeff = {0: 0x0000_6f84,
                                 1: 0x20000000,
                                 2: 0x40000000,
                                 3: 0x20000000,
                                 4: 0x8e301ca0,
                                 5: 0x32b7759a,
                                 8: 0x7fffffff,
                                 9: 0x20000000,
                                 10: 0x40000000,
                                 11: 0x20000000,
                                 12: 0x86d2475f,
                                 13: 0x3a2447ec,
                                 7: 0x7fffffff}
        elif target == '500kHz':
            self.filter_coeff = {0: 0x009e1586,
                                 1: 0x20000000,
                                 2: 0x40000000,
                                 3: 0x20000000,
                                 4: 0xbce3be9a,
                                 5: 0x12f3f6b0,
                                 8: 0x7fffffff,
                                 9: 0x20000000,
                                 10: 0x40000000,
                                 11: 0x20000000,
                                 12: 0xab762783,
                                 13: 0x287ecada,
                                 7: 0x7fffffff}


class ADCDATA():
    # TODO: add class docstring

    def __init__(self):
        pass

    def deswizzle(self, buf):
        # TODO: add method docstring

        d = np.frombuffer(buf, dtype=np.uint8).astype(np.uint32)
        if self.num_bits == 16:
            d1 = d[0::4] + (d[1::4] << 8)  # TODO: check the byte ordering
            # TODO: is breaking this up necessary? looks like it
            d2 = d[2::4] + (d[3::4] << 8)
        elif self.num_bits == 18:
            # TODO: check 18-bit data conversion
            d2 = (d[3::4] << 8) + d[1::4] + ((d[0::4] << 16) & 0x03)

        if self.name == 'AD7961':
            c = np.empty((d1.size + d2.size,), dtype=d1.dtype)
            # see Xilinx FIFO guide PG057 pg 115, memory fills up from left to right (MSB to LSB)
            c[0::2] = d2
            c[1::2] = d1
        elif self.name == 'ADS8686':
            c = {'A': np.array([]),
                 'B': np.array([])}
            c['A'] = d1
            c['B'] = d2
        return c

    def convert_twos(self, d):
        """Convert data to integer two's complement representation."""

        return twos_comp(d, self.num_bits)

    def convert_data(self, buf):
        """Deswizle and convert the twos complement representation."""

        return self.convert_twos(self.deswizzle(buf))

    # TODO: test composite ADC function that enables, reads, converts and plots
    # TODO: incorporate/connect QT graphing (UIscript.py)
    def read(self, twos_comp_conv=True):
        # TODO: add method docstring

        s, e = self.fpga.read_pipe_out(self.endpoints['PIPE_OUT'].address)
        if twos_comp_conv:
            data = self.convert_data(s)
        else:
            data = self.deswizzle(s)
        return data

    def stream_mult(self, swps=4, twos_comp_conv=True, data_len=1024):
        # TODO: add method docstring

        cnt = 0
        st = bytearray(np.asarray(np.ones(0, np.uint8)))
        self.fpga.xem.UpdateTriggerOuts()

        while cnt < swps:
            # check the FIFO half-full flag
            if (self.fpga.xem.IsTriggered(self.endpoints['FIFO_HALFFULL'].address,
                                          self.endpoints['FIFO_HALFFULL'].bit_index_low)):
                s, e = self.fpga.read_pipe_out(self.endpoints['PIPE_OUT'].address,
                                               data_len)
                st += s
                cnt = cnt + 1
                if self.fpga.debug:
                    print(cnt)
            self.fpga.xem.UpdateTriggerOuts()
        if twos_comp_conv:
            data = self.convert_data(st)
        else:
            data = self.deswizzle(st)
        return data


# Class for the ADS8686 ADC chip.
class ADS8686(SPIController, ADCDATA):
    # TODO: add class docstring

    registers = Register.get_chip_registers('ADS8686')
    msg_w = 0x8000
    range = {10:  0b00,
             2.5: 0b01,
             5:   0b10}
    lpf_khz = {39:  0b00,
               15:  0b01,
               376: 0b10}

    def __init__(self, fpga, master_config=0x3010, endpoints=None):
        # master_config=0x3010 Sets CHAR_LEN=16, ASS (auto SlaveSelect),
        # IE (interrupt enable), Tx/Rx Pos. Edge  TODO: why was this changed??
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('ADS8686')
        super().__init__(fpga=fpga, master_config=master_config, endpoints=endpoints)
        self.ranges = [5]*16  # voltage ranges of all 16 channels
        self.num_bits = 16
        self.name = 'ADS8686'

    def write(self, msg, reg_name):
        """Write to an internal register on the chip."""

        reg = self.registers[reg_name].address << 9
        return super().write(reg | ADS8686.msg_w | msg)

    def read(self, reg_name):
        """Read from an internal register on the chip."""

        reg = self.registers[reg_name].address << 9
        super().write(reg)
        return super().read()

    def read_channel(self, channel):
        """Read a desired channel on the chip."""

        pass  # TODO: write method

    def read_last(self):
        """Return the last value read by the ADS8686.

        This reads a wire_out rather than a pipe_out so we get 1 data point
        rather than many.
        """

        data = self.fpga.read_wire(self.endpoints['OUT'].address)
        buf = int.to_bytes(data, 4, byteorder='little')
        return self.deswizzle(buf)

    def setup(self):
        """Perform basic setup for default chip use."""

        # TODO -- defaults to modify the SPI setup
        self.set_host_mode()  # required for the SPI configuration to work
        self.configure_master_bin(self.master_config)  # configures directly
        # self.set_frequency(5)
        self.set_divider(3)  # TODO: check on scope: 200/(3+1)=50 MHz
        self.select_slave(1)

    def set_range(self, vals):
        """Set the voltage range of all channels.

        If vals is a single value then all channels are given that value.
        If vals is a list of length 16 then each channel gets a separate range
        vals must be 10, 5, or 2.5. These represent +/-10, +/-5, and +/-2.5 V.
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
                if self.fpga.debug:
                    print('Writing 0x{:x} to reg {}'.format(
                        towrite, regs[idx//4]))
                self.write(towrite, regs[idx//4])
                towrite = 0

    def reg_to_voltage(self, reg_val, chan_num=0):
        """Calculates the channel's voltage from the register value.

        Uses the stored gain range. reg_val can be list of ints or int
        """
        #  TODO: setup for sequence of channels
        val = twos_comp(reg_val, 16)  # 16-bit channel readings
        lsb = (self.ranges[chan_num]*2)/2**16
        return val*lsb

    def write_reg_bridge(self, clk_div=1000):
        """Set clk divider and spi_controller to continuously read ADC data."""

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
                                    0x4000_3110)  #
        # reset the clk divider
        self.fpga.send_trig(self.endpoints['CLK_DIV_RESET'])
        self.set_fpga_mode()  # lower the control bit for host vs. FPGA driven
        # so the FPGA takes control of sending SPI

    def set_lpf(self, lpf):
        # TODO: add method docstring

        if lpf not in ADS8686.lpf_khz.keys():
            print('Error in ADS8686 LPF setup.')
            print('   Skipping ADS8686 LPF setup')
            print('   Frequency options are: {}'.format(
                list(ADS8686.lpf_khz.keys())))
            print('-'*40)
        else:
            self.write(ADS8686.lpf_khz[lpf], 'lpf')  # 376 khZ

    def setup_sequencer(self, chan_list=[('FIXED', 'FIXED'), ('0', 'FIXED')], voltage_range=5, lpf=376):
        """Start the sequencer looping through the given channels.

        Parameters
        ----------
        chan_list : list
            Ordered list of channel pairs (A, B) to loop through. Options below.
                [0-7]
                AVDD
                ALDO
                FIXED (0xAAAA, 0x5555)
        voltage_range : int
            Voltage range of the channels, positive and negative.
        lpf : int
            Low pass frequency in kHz.
        """
        named_chans = {
            'AVDD': 0b1000,
            'ALDO': 0b1001,
            'FIXED': 0b1011,
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
        }
        codes = []
        for chan in chan_list:
            code = 0
            for i in range(len(chan)):
                code_piece = named_chans.get(chan[i])
                if code_piece is None:
                    print(f'ERROR: name not recognized: {chan}')
                    code = named_chans.get('FIXED') + \
                        (named_chans.get('FIXED') << 4)
                    break
                else:
                    # B side shifted 4 bits left, A side at 0
                    code += code_piece << (4 * i)
            codes.append(code)

        # Room for 32 codes, any more after that are not included
        if len(codes) > 32:
            print(
                f'WARNING: too many channels. Using first 32/{len(codes)} channels')
            codes = codes[:32]
        base_creg = 0x0000  # default value
        self.write(base_creg, 'config')
        # set channels to be the fixed digital code
        # channel B = 0x5555; channel A = 0xAAAA
        #  this is over-written by sequencer anyways
        # TODO: if this is over-written anyways, do we need it?
        self.write((0xb | (0xb << 4)), 'chan_sel')
        # set the range of all channels to +/-5V
        self.set_range(voltage_range)  # sets all channels to +/-5V
        self.set_lpf(lpf)
        # setup the sequencer
        # sequence0: fixed values and then continue
        #   8 SSREN; 7-4 CHSEL_B; 3-0 CHSEL_A
        backto_first_stack = 0x100  # SSREN is bit 8

        # Write all but the last code, which is done separately
        for i in range(len(codes) - 1):
            code = codes[i]
            self.write(code, 'seq' + str(i))
        # Write last code with loop back: use (len(codes) - 1) since i is not set if len(codes)==1
        self.write((codes[-1] | backto_first_stack),
                   'seq' + str(len(codes) - 1))
        # enable the sequencer
        self.write(base_creg | 0x20, 'config')
        return codes

    def hw_reset(self, val=True):
        """Trigger ADS8686 active low hardware reset."""

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
    # TODO: add Attributes to docstring

    # the AD7961 does not have internal registers -- just OK endpoints

    def __init__(self, fpga, endpoints=None):
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('AD7961')
        self.fpga = fpga
        self.endpoints = endpoints
        self.name = 'AD7961'
        self.num_bits = 16  # for AD7961 bits=18 for AD7960

    @staticmethod
    def create_chips(fpga, number_of_chips, endpoints=None):
        """Instantiate a given number of new chips.

        We increment the endpoints between each instantiation as well. The
        number must be greater than 0. If the endpoints argument is left
        as None, then we will use copies of the endpoints_from_defines
        dictionary for the endpoints for each instance, and update that
        original dictionary when we increment the endpoints. This way, the
        endpoints there are ready for another instantiation if needed.
        """

        if type(number_of_chips) is not int or number_of_chips <= 0:
            print('number_of_chips must be an integer greater than 0')
            return False

        if endpoints is None:
            endpoints = Endpoint.endpoints_from_defines.get('AD7961')

        chips = []
        for i in range(number_of_chips):
            # Use deepcopy here to keep the endpoints for different instances separate
            chips.append(AD7961(fpga=fpga, endpoints=copy.deepcopy(endpoints)))
            Endpoint.increment_endpoints(endpoints)
        return chips

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
        """Get status of the phase locked loop."""

        return self.fpga.read_wire_bit(self.endpoints['PLL_LOCKED'].address,
                                       self.endpoints['PLL_LOCKED'].bit_index_low)

    def get_timing_pll_status(self):
        """Get status of the timing of the phase locked loop."""

        return self.fpga.read_wire_bit(self.endpoints['TIMING_PLL_LOCKED'].address,
                                       self.endpoints['TIMING_PLL_LOCKED'].bit_index_low)

    def get_fifo_status(self):
        """Get fullness status of the FIFO."""

        flags = ['FULL', 'HALFFULL', 'EMPTY']
        fifo_status = {}
        self.fpga.xem.UpdateTriggerOuts()
        for k in flags:
            fifo_status[k] = self.fpga.xem.IsTriggered(self.endpoints['FIFO_{}'.format(k)].address,
                                                       self.endpoints['FIFO_{}'.format(k)].bit_index_low)
        return fifo_status

    # Enable pins:
    # 0000 - power down
    # 1001 - enabled with ref buffer on; 28 MHZ
    # 0100 - test patterns on LVDS
    # 1101 - enabled with ref buffer on; 9 MHZ
    # Note that EN[3]=1 enables the VCM output buffer.

    def power_down_adc(self):
        """Power down single channel of the ADC.

        Fails if the global enables are 010 for LVDS test patterns
        """

        self.set_enables(0b0, global_enables=False)

    def test_pattern(self):
        """Enable PRBS test pattern on the LVDS interface."""

        self.set_enables(value=0b0100)

    def power_up_adc(self, bw='28M'):
        # TODO: add method docstring
        # TODO: explain what bw should be in docstring

        if bw == '28M':
            self.set_enables(0b1001)
        elif bw == '9M':
            self.set_enables(0b1101)
        else:
            print(f'incorrect input sampling bandwidth for {self.name}')

    def power_down_all(self):
        """Power down all channels of the ADC."""

        self.set_enables(0b0000)  # TODO: return anything here?

    def reset_pll(self):
        """Reset the phase locked loop."""

        return self.fpga.xem.ActivateTriggerIn(self.endpoints['PLL_RESET'].address,
                                               self.endpoints['PLL_RESET'].bit_index_low)

    def reset_fifo(self):
        """Reset the FIFO for the ADC data.

        One per channel.
        """

        return self.fpga.xem.ActivateTriggerIn(self.endpoints['FIFO_RESET'].address,
                                               self.endpoints['FIFO_RESET'].bit_index_low)

    def reset_trig(self):
        """Reset the FPGA controller for the ADC.

        One per channel. Uses the Opal Kelly Trigger
        """

        return self.fpga.xem.ActivateTriggerIn(self.endpoints['RESET'].address,
                                               self.endpoints['RESET'].bit_index_low)

    def reset_wire(self, value):
        """Set the value of the wire to reset the FPGA controller for the ADC.

        Uses the Opal Kelly WireIn (the trigger can't hold the reset).

        Parameters
        -----------
        value : int
            value = 1 is reset
            value = 0 releases reset
        """

        if value == 1:
            self.fpga.set_wire_bit(self.endpoints['WIRE_RESET'].address,
                                   self.endpoints['WIRE_RESET'].bit_index_low)
        if value == 0:
            self.fpga.clear_wire_bit(self.endpoints['WIRE_RESET'].address,
                                     self.endpoints['WIRE_RESET'].bit_index_low)

    def power_down_fpga(self):
        """Power down the FPGA controller through WireIn."""

        # TODO: add functionality (wirein bit) to the FPGA
        #       this would reduce FPGA power consumption
        self.reset_wire(0)

    def set_enables(self, value=0b0000, global_enables=True):
        """Set the EN0 specific to this channel (LSB in values).

        Optionally also modify the global enables (all channels).
        """

        mask = gen_mask(self.endpoints['ENABLE'].bit_index_low)
        if global_enables:
            # global enables (connect to all AD7961); create a list of bit position
            gl_mask = [x+self.endpoints['GLOBAL_ENABLE'].bit_index_low
                       for x in range(self.endpoints['GLOBAL_ENABLE_LEN'].bit_index_low)]
            # or global mask with the signal channel EN0 mask
            mask = gen_mask(gl_mask) | mask

        # setup the values
        value_chan = (value & 0b0001) << (
            self.endpoints['ENABLE'].bit_index_low)
        if global_enables:
            #  globabl enables are the 3 MSBs
            val_global = (value & 0b1110) << (
                self.endpoints['GLOBAL_ENABLE'].bit_index_low - 1)
            # minus 1 since already left shifted by 1
            print('Global value = 0x{:0x}'.format(val_global))
            value = value_chan | val_global

        print('Enables setting value = 0x{:0x} with mask = = 0x{:0x}'.format(
            value, mask))
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


class DDR3():
    """DDR is striped in groups of 16 bits to 8 channels  (128 bits)
    Out of the DDR FIFO
    Input write is 256 bits wide.

    Output read bus is 128 bits wide.
    Supports up to 8 channels at 16 bits each.

    Into the DDR:
    FIFO Write side 32 bits (PipeIn), Read side is 256 bits
    Write: W31-W0:     t0: W31-W0 [MSB]; W63-W32, ... W255-W224

    Out of the DDR:
    FIFO Write: W255 - W0 : t0 W255 - W128, t1: W127 - W0
    so:
    channel 0: 128    + 15:128, W15-W0
    channel 1: 128+16 + 15:144, 16*1 + 15: 16

    The DDR is divided into 2 buffers. Each buffer has an incoming and outgoing FIFO.

    1st buffer:
        * function generator like data that provides a data-stream to the DACs
        * write from the host when WRITE_ENABLE is set
        * read to the DACs when READ_ENABLE is set

    2nd buffer:
        * buffering for ADC data.
        * ADC data writes to the DDR when READ_ENABLE is set
        * ADC data in DDR can be read to the host when READ_FG_ENABLE is set

    Expected sequence of operations:
        1) At startup write pattern for DACs using write_channels()
        2) set_read() # starts DAC data output to DACs via SPI and ADC data captured into DDR
        3) set_adc_read() # allows host to read PipeOut as PipeOut is continuously filled if emptied

    DDR configuration bits:
        * WRITE_ENABLE
        * READ_ENABLE
        * READ_FG_ENABLE
    """
    # TODO: add Attributes to docstring

    def __init__(self, fpga, endpoints=None):
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('DDR3')
        self.fpga = fpga
        self.endpoints = endpoints
        self.parameters = {'BLOCK_SIZE': 2048, # 1/2 the incoming FIFO depth in bytes (size of the BlockPipeIn)
                           'sample_size': 65536,  # per channel
                           # number of channels that the DDR is striped between (for DACs)
                           'channels': 8,
                           'update_period': 400e-9,  # 2.5 MHz -- requires SCLK ~ 50 MHZ
                           'port1_index': 0x7f_ff_f8}

        # the index is the DDR address that the circular buffer stops at.
        # need to write all the way up to this stoping point otherwise the SPI output will glitch
        self.parameters['sample_size'] = int(
            (self.parameters['port1_index'] + 8)/2)

        self.data_arrays = []
        for i in range(self.parameters['channels']):
            self.data_arrays.append(np.zeros(
                self.parameters['sample_size']).astype(np.uint16))

        self.clear_adc_debug()

    def set_adc_debug(self):
        """Set the ADC debug bit.

        That bit multiplexes a counter to ADC channel 0 and bits 47:0 of the
        DAC data to ADC channels 1,2,3.

        Not supported in all versions of the FPGA design.
        """

        self.fpga.set_wire_bit(self.endpoints['ADC_DEBUG'].address,
                               self.endpoints['ADC_DEBUG'].bit_index_low)

    def clear_adc_debug(self):
        """Clear the ADC debug bit.

        DDR ADC data will be from the ADC.
        """
        self.fpga.clear_wire_bit(self.endpoints['ADC_DEBUG'].address,
                                 self.endpoints['ADC_DEBUG'].bit_index_low)

    def make_flat_voltage(self, amplitude):
        """Return a constant unit16 array of value amplitude.

        Array length based on the sample_size parameter. The conversion from
        float or int voltage to int digital (binary) code should take place
        BEFORE this function.

        Parameters
        ----------
        amplitude: int
            Digital (binary) value of the flat voltage

        Returns
        -------
            numpy.ndarray (for DDR data array)
        """

        amplitude = np.ones(self.parameters['sample_size'])*amplitude
        amplitude = amplitude.astype(np.uint16)
        return amplitude

    def closest_frequency(self, freq):
        """Determine closest frequency so the waveform evenly divides into the length of the DDR3

        Parameters
        ----------
        freq : float
            Desired frequency

        Returns
        -------
        float : The closest possible frequency
        """

        samples_per_period = (1/freq) / self.parameters['update_period']

        if samples_per_period <= 2:
            print('Frequency is too high for the DDR update rate')
            return None
        total_periods = self.parameters['sample_size']/samples_per_period
        # round and recalculate frequency
        round_total_periods = np.round(total_periods)
        round_samples_per_period = self.parameters['sample_size'] / \
            round_total_periods
        new_frequency = 1 / \
            (self.parameters['update_period'] * round_samples_per_period)

        return new_frequency

    def make_sine_wave(self, amplitude, frequency,
                       offset=0x2000, actual_frequency=True):
        """Return a sine-wave array for writing to DDR.

        The conversion from float or int voltage to int digital (binary) code
        should take place BEFORE this function.

        Parameters
        ----------
        amplitude : int
            Digital (binary) value of the sine wave.
        frequency : float
            Desired frequency in Hz.
        offset : int
            Digital (binary) value offset.
        actual_frequency : bool
            Decide whether closest frequency that fits an integer number of periods is used.

        Returns
        -------
        numpy.ndarray, float : for DDR data array, actual frequeny used
        """

        if (amplitude) > offset:
            print('Error: amplitude in sine-wave is too large')
            return -1
        if actual_frequency:
            frequency = self.closest_frequency(frequency)

        t = np.arange(0, self.parameters['update_period']*self.parameters['sample_size'],
                      self.parameters['update_period'])
        # print('length of time axis after creation ', len(t))
        ddr_seq = (amplitude)*np.sin(t*frequency*2*np.pi) + offset
        if any(ddr_seq < 0) or any(ddr_seq > (2**16-1)):
            print('Error: Uint16 overflow in make sine wave')
            return -1
        ddr_seq = ddr_seq.astype(np.uint16)
        return ddr_seq, frequency

    def make_ramp(self, start, stop, step, actual_length=True):
        """Create a ramp signal to write to the DDR.

        The conversion from float or int voltage to int digital (binary) code
        should take place BEFORE this function.

        Parameters
        ----------
        start : int
            Digital (binary) value to start the ramp at
        stop : int
            Digital (binary) value to stop the ramp at
        step : int
            Digital (binary) code to step by

        Returns
        -------
        numpy.ndarray : for DDR data array
        """

        # change the stop value for integer number of cycles
        ramp_seq = np.arange(start, stop, step)
        len_ramp_seq = len(ramp_seq)
        if actual_length:
            length = int(
                self.parameters['sample_size']/np.round(self.parameters['sample_size']/len_ramp_seq))
            stop = start + length*step
            ramp_seq = np.arange(start, stop, step)
        num_tiles = self.parameters['sample_size']//len(ramp_seq)
        extras = self.parameters['sample_size'] % len(ramp_seq)
        ddr_seq = np.tile(ramp_seq, num_tiles)
        ddr_seq = np.hstack((ddr_seq, ramp_seq[0:extras]))
        ddr_seq = ddr_seq.astype(np.uint16)
        return ddr_seq

    def make_step(self, low, high, length, actual_length=True, duty=50):
        """Return a step signal (square wave) to write to the DDR.

        The conversion from float or int voltage to int digital (binary) code
        should take place BEFORE this function.

        Parameters
        ----------
        low : int
            Digital (binary) code for the low value of the step.
        high : int
            Digital (binary) code for the high value of the step.
        length : TODO add type for length
            TODO add description for length
        actual_length : bool
            TODO add description for actual_length
        duty : int or float
            Duty cycle percentage. Enter as a percentage [0.0, 100.0].

        Returns
        -------
        numpy.ndarray : for DDR data array
        """

        if actual_length:
            length = int(
                self.parameters['sample_size']/np.round(self.parameters['sample_size']/length))
        l_first = int(length/100*duty)
        l_end = int(length/100*(100-duty))
        ramp_seq = np.concatenate((np.ones(l_first)*low, np.ones(l_end)*high))
        num_tiles = self.parameters['sample_size']//len(ramp_seq)
        extras = self.parameters['sample_size'] % len(ramp_seq)
        ddr_seq = np.tile(ramp_seq, num_tiles)
        ddr_seq = np.hstack((ddr_seq, ramp_seq[0:extras]))
        ddr_seq = ddr_seq.astype(np.uint16)
        return ddr_seq

    def write_channels(self, set_ddr_read=True):
        """Write the channels as striped data to the DDR."""

        data = np.zeros(
            int(len(self.data_arrays[0])*self.parameters['channels']))
        data = data.astype(np.uint16)

        for i in range(self.parameters['channels']):
            if i % 2 == 0:  # extra order swap on the 32 bit wide pipe
                data[(7-i - 1)::8] = self.data_arrays[i]
            else:
                data[(7-i + 1)::8] = self.data_arrays[i]

        print('Length of data = {}'.format(len(data)))
        return self.write(bytearray(data), set_ddr_read=set_ddr_read)

    def write(self, buf, set_ddr_read=True):
        """Write a bytearray to the DDR3.

        Parameters
        ----------
        buf : bytearray
            bytearray to write to the DDR

        Returns
        -------
            int, float : length of the buffer written to the DDR
                         (or error code if unsuccessful), speed of the write in MB/s
        """

        print('Length of buffer being written to DDR [bytes]: ', len(buf))
        # Reset FIFOs
        self.clear_read()
        self.reset_fifo()
        self.set_write()

        print('Writing to DDR...')
        time1 = time.time()
        block_pipe_return = self.fpga.xem.WriteToBlockPipeIn(epAddr=self.endpoints['BLOCK_PIPE_IN'].address,
                                                             blockSize=self.parameters['BLOCK_SIZE'],
                                                             data=buf)
        print(f'The length of the DDR write was {block_pipe_return}')

        time2 = time.time()
        time3 = (time2-time1)
        speed_MBs = (int)(block_pipe_return/1024/1024/time3)
        print(f'The speed of the write was {speed_MBs} MB/s')

        # below prepares the HDL into read mode
        self.clear_write()
        self.reset_fifo()
        if set_ddr_read:
            self.set_read()
        return block_pipe_return, speed_MBs

    def reset_fifo(self):
        """Reset both FIFOs and DDR Mig and DDR address pointers."""

        # TODO: convert to trigger, split resets? This is synchronized on the FPGA
        # TODO: important! the rst_ddr_ui is not connected on the FPGA

        self.fpga.set_wire_bit(self.endpoints['RESET'].address,
                               self.endpoints['RESET'].bit_index_low)
        self.fpga.clear_wire_bit(self.endpoints['RESET'].address,
                                 self.endpoints['RESET'].bit_index_low)

    def fifo_status(self):
        """Check the empty, full, and count status of the DDR interfacing FIFOs

        Returns
        -------
        dict : dictionary of fifo status ('EMPTY', 'FULL', 'ADC_DATA_COUNT')
            for 'IN', 'OUT', and channels 1, 2
        """
        wire_status = self.fpga.read_wire(
            self.endpoints['INIT_CALIB_COMPLETE'].address)
        fifo_status = {}
        for fe in ['EMPTY', 'FULL']:
            for num in [1, 2]:
                for inout in ['IN', 'OUT']:
                    ep_name = '{}{}_{}'.format(inout, num, fe)
                    bit_pos = self.endpoints[ep_name].bit_index_low
                    val = test_bit(wire_status, bit_pos)
                    fifo_status[ep_name] = val
                    print('{} = {}'.format(ep_name, val))

        ep_name = 'ADC_DATA_COUNT'
        cnt_bit_low = self.endpoints[ep_name].bit_index_low
        cnt_bit_width = self.endpoints[ep_name].bit_width
        cnt_msk = gen_mask(np.arange(cnt_bit_low, cnt_bit_width))
        fifo_status[ep_name] = (wire_status & cnt_msk) >> cnt_bit_low
        print('{} = {}'.format(ep_name, val))

        # self.print_fifo_status(fifo_status)
        return fifo_status

    def print_fifo_status(self, fifo_status):
        """Print the FIFO status dictionary.

        Parameters
        ----------
        fifo_status : dict
            Dictionary of fifo status.
        """

        for k in fifo_status:
            print('{} = {}'.format(k, fifo_status[k]))

    def set_read(self):
        """Set DDR / FIFOs to read.
           Enables DDR data going to the DACs and ADC data into DDR
        """

        self.fpga.set_wire_bit(self.endpoints['READ_ENABLE'].address,
                               self.endpoints['READ_ENABLE'].bit_index_low)

    def clear_read(self):
        """Clear DDR / FIFOs to read.
            Stops DDR data from going to the DACs and ADC data into DDR
        """

        self.fpga.clear_wire_bit(self.endpoints['READ_ENABLE'].address,
                                 self.endpoints['READ_ENABLE'].bit_index_low)

    def set_write(self):
        """Set DDR / FIFOs to write data into DDR via Pipe.
        """

        self.fpga.set_wire_bit(self.endpoints['WRITE_ENABLE'].address,
                               self.endpoints['WRITE_ENABLE'].bit_index_low)

    def clear_write(self):
        """Clear DDR / FIFOs to write data into DDR via Pipe.
        """

        self.fpga.clear_wire_bit(self.endpoints['WRITE_ENABLE'].address,
                                 self.endpoints['WRITE_ENABLE'].bit_index_low)

    def set_adc_read(self):
        """Set DDR / FIFOs to read DDR data from the ADCs out via a PipeOut.
        """
        # TODO: change this name to ADC_READ_ENABLE and modify names in FPGA
        self.fpga.set_wire_bit(self.endpoints['FG_READ_ENABLE'].address,
                               self.endpoints['FG_READ_ENABLE'].bit_index_low)

    def clear_adc_read(self):
        """Clear DDR / FIFOs to read DDR data from the ADCs out via a PipeOut.
        """

        self.fpga.clear_wire_bit(self.endpoints['FG_READ_ENABLE'].address,
                                 self.endpoints['FG_READ_ENABLE'].bit_index_low)

    def adc_single(self):
        """Set ADC read address to the ADC write address.

        Emulates an immediate "trigger" of an oscilloscope.
        """

        self.fpga.set_wire_bit(self.endpoints['ADC_ADDR_SET'].address,
                                 self.endpoints['ADC_ADDR_SET'].bit_index_low)
        self.fpga.send_trig(self.endpoints['ADC_ADDR_RESET'])


    def read_adc(self, sample_size=None, source='ADC', DEBUG_PRINT=False):
        """Read ADC data.

        Parameters
        ----------
        sample_size : int
            Length of read in bytes. If none uses DDR parameter 'sample_size.'
        source : str
            FIFO output buffer to read. Either 'ADC' or 'FG'. 'FG' just reads
            back what is written for DACs (as function generator) so not so
            useful.

        Returns
        -------
        byearray, int : The data read as a bytearray, The count (or error code)
        read from the OpalKelly interface
        """

        if sample_size is None:
            data = np.zeros((self.parameters['sample_size'],), dtype=int)
            data_buf = bytearray(data)
        else:
            data_buf = bytearray(sample_size)

        # Block size must be a power of two from 16 to 16384
        # will automatically perform multiple transfers to complete the full LENGTH
        # the length must be an integer multiple of 16 for USB3.0
        # and the length must be an Integer multiple of Block Size
        # see https://docs.opalkelly.com/fpsdk/frontpanel-api/ section 3.3.1

        block_size = self.parameters['BLOCK_SIZE']
        # check block size
        if block_size % 16 != 0:
            print('Error in read adc. Block size is not a multiple of 16')
            return -1, -1
        if block_size > 16384:
            print('Error in read adc. Block size is greater than 16384')
            return -2, -2

        if source == 'ADC':
            read_cnt = self.fpga.xem.ReadFromBlockPipeOut(epAddr=self.endpoints['BLOCK_PIPE_OUT'].address,
                                                          blockSize=block_size,
                                                          data=data_buf)

        elif source == 'FG':  # TODO: test, don't expect this to work
            read_cnt = self.fpga.xem.ReadFromBlockPipeOut(epAddr=self.endpoints['BLOCK_PIPE_OUT_FG'].address,
                                                          blockSize=block_size,
                                                          data=data_buf)
        else:
            print('incorrect source in read_adc')
            return -11, -11

        if DEBUG_PRINT:
            print(
                f'The length [num of bytes] of the BlockPipeOut read is: {read_cnt}')
        return data_buf, read_cnt

    def set_index(self, factor, factor2=None):
        """
        No longer used. Index (the DDR address that wraps-around to 0)
        is fixed to improve timing performance.
        """
        print('Set index is no longer used. Index is fixed to: {}'.format(
            self.parameters['port1_index']))


# TODO: should there be a 'device' or similar class that all controllers are subclasses of?
def disp_device(dev, reg=True):
    """Display endpoints and registers for a chip.

    Parameters
    ----------
    dev : I2CController or SPIController or SPIFifoDriven or AD7961
        Chip instance to display information for.
    reg : bool
        Whether to display registers.
    """

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
