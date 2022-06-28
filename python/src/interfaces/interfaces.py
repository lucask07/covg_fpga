"""Module to configure OpalKelly XEM7310 FPGA to communicate with peripherals.

Use Registers for peripherals' internal registers and Endpoints for Opal Kelly Endpoints on the FPGA. 

June 2022

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu
"""

import pandas as pd
import os
import sys
from interfaces.utils import gen_mask
import copy
import yaml

home_dir = os.path.join(os.path.expanduser('~'), '.packagename')
with open(os.path.join(home_dir, 'config.yaml'), 'r') as file:
    configs = yaml.safe_load(file)

# TODO: make sure this path works for Windows, Mac, and Linux: https://docs.opalkelly.com/fpsdk/frontpanel-api/programming-languages/
if sys.platform == 'win32':
    sys.path.append(os.path.join(configs['frontpanel_path'], 'API/Python/3.7/x64')) # Add path to ok.py to PATH for import
    dll_dir = os.path.join(configs['frontpanel_path'], 'API/lib/x64')
    os.add_dll_directory(dll_dir)   # Make DLL (okFrontPanel.dll) available
    os.environ.setdefault('PATH', '')
    os.environ['PATH'] += os.pathsep + dll_dir
elif sys.platform == 'darwin':
    sys.path.append(os.path.join(configs['frontpanel_path'], 'API/Python3/')) # Add _ok.so to PATH for import
import ok


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
    def get_chip_registers(sheet, workbook_path=configs['registers_path']):
        """Return a dictionary of Registers from a page in an Excel spreadsheet."""

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

    MAX_WIDTH = configs['endpoint_max_width']  # Maximum bit width of an Endpoint. Used to wrap Endpoints to the next address when incrementing
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
    def update_endpoints_from_defines(ep_defines_path=configs['ep_defines_path']):
        """Store and return a dictionary of Endpoints for each chip in ep_defines.v.

        Returns -1 if there is a naming collision in ep_defines.v
        """

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

            endpoint = Endpoint(address=address, bit_index_low=bit,
                                bit_width=bit_width, gen_bit=gen_bit, gen_address=gen_address)

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
        list_eps = [(ep.address, none_to_neg_1.get(
            ep.bit_index_low, ep.bit_index_low)) for ep in top_level_eps]
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

    @staticmethod
    def advance_endpoints(endpoints_dict, advance_num=1):
        """
        Advances Endpoints in a dict in place by advance_num. Checks each
        Endpoint's gen_bit and gen_address attributes to see whether to
        increment the bit or the address or both.

        Example usage:
            endpoints=Endpoint.advance_endpoints(Endpoint.get_chip_endpoints('I2CDAQ'),1)

        Parameters
        ----------
        endpoints_dict : dict of Endpoints
            The dict of Endpoints to advance by advance_num.
        advance_num : int
            How much to advance the Endpoints by.

        Returns
        -------
        dict : the same dict of Endpoints given in endpoints_dict, now advanced
        """

        for key in endpoints_dict:
            endpoint = endpoints_dict[key]
            if endpoint.gen_bit:
                endpoint.bit_index_low += (endpoint.bit_width * advance_num)
                if endpoint.bit_index_low > Endpoint.MAX_WIDTH:
                    # Endpoint does not fit, wrap to next address
                    endpoint.address += 1
                    endpoint.bit_index_low %= Endpoint.MAX_WIDTH
                endpoint.bit_index_high = endpoint.bit_index_low + endpoint.bit_width
                if endpoint.bit_index_high > Endpoint.MAX_WIDTH:
                    # Endpoint split across two addresses -> move to next address, start at bit 0
                    endpoint.address += 1
                    endpoint.bit_index_low = 0
                    endpoint.bit_index_high = endpoint.bit_index_low + endpoint.bit_width
            if endpoint.gen_address:
                endpoint.address += advance_num
        return endpoints_dict

# Class for the FPGA itself. Handles FPGA configuration, setting wire values,
# and other FPGA specific functions.


class FPGA:
    """Class for the Opal Kelly FPGA itself.
    Derived from OpalKelly Python examples.

    Attributes
    ----------
    bitfile : str
        Path to the bitfile to load on the FPGA.
    xem : ok.okCFrontPanel
        Opal Kelly API connection to the FPGA.
    device_info : ok.okTDeviceInfo
        General information about the FPGA.
    """


    def __init__(self, bitfile='default', debug=False):
        if bitfile == 'default':
            # Use bitfile from config.yaml fpga_bitfile_path
            self.bitfile = configs['fpga_bitfile_path']
        else:
            self.bitfile = bitfile
        self.debug = debug


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

    def read_trig(self, ep_bit):
        """Read an OK TriggerOut Endpoint.
        
        Parameters
        ----------
        ep_bit : Endpoint
            The endpoint containing the bit_index_low and address of the
            TriggerOut to read.

        Returns
        -------
        bool
            Whether the TriggerOut has been triggered.
        """

        self.xem.UpdateTriggerOuts()
        return self.xem.IsTriggered(ep_bit.address, (1 << ep_bit.bit_index_low))

    def read_ep(self, ep_bit):
        """Return the error code after reading an OK WireOut Endpoint."""
        self.xem.UpdateWireOuts()
        read_out = self.xem.GetWireOutValue(ep_bit.address)
        return read_out

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

    def set_ep_simultaneous(self, address, bit_list, val_list):
        """ set multiple values to the wire of a single endpoint"""
        value = 0
        mask = 0
        for bit, val in zip(bit_list, val_list):
            value = value | (val << bit)
            mask = mask | (1 << bit)
        if self.debug:
            print(
                f'Simultaneous wire write (address={hex(address)},value={hex(value)},mask={hex(mask)})')

        return self.set_wire(address, value=value, mask=mask)


    def read_wire_bit(self, address, bit):
        """Read a single bit in a OpalKelly wire in."""
        value = self.read_wire(address)
        return (value & (1 << bit)) >> bit


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
