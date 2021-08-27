"""Module for configuring OpalKelly XEM7310
and use it as an I2C controller, SPI controller, and Serial LVDS controller.

Much of the Python is no longer used as the FPGA code is simpler than previously.
Functions no longer in use include SHUF (shuffling) and multiple and/or timed reads.

August 2021

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu
"""

import ok
import numpy as np
import pandas as pd
import os
import sys
import time
from collections import namedtuple
from interfaces.utils import gen_mask, twos_comp, test_bit, int_to_list


Register = namedtuple('Register', 'address, default, bit_index_high, bit_index_low, bit_width')

def registers_from_excel(sheet, workbook_path=None):
    """Return a dictionary of Registers from an page in an Excel spreadsheet."""

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

Endpoint = namedtuple('Endpoint', 'address, bit_index_high, bit_index_low, bit_width')

def endpoints_from_defines(chip_name, ep_defines_path):
    """Return a dictionary of Endpoints for a chip in ep_defines.v."""
    pass

# Class for the FPGA itself. Handles FPGA configuration, setting wire values, and other FPGA specific functions.
class FPGA:
    # TODO: change to complete bitfile when Verilog is combined
    def __init__(self, bitfile=os.path.join('..', '..', 'fpga_test.bit')):

        self.bitfile = bitfile
        self.i2c = {'m_pBuf': [], 'm_nDataStart': 7}
        # self.pll = ok.PLL22150()
        # I don't know why, but uncommenting this makes things fail
        return

    def init_device(self):
        # Open the first device we find.
        self.xem = ok.okCFrontPanel()
        if (self.xem.NoError != self.xem.OpenBySerial("")):
            print("A device could not be opened.  Is one connected?")
            return(False)

        # Get some general information about the device.
        self.devInfo = ok.okTDeviceInfo()
        if (self.xem.NoError != self.xem.GetDeviceInfo(self.devInfo)):
            print("Unable to retrieve device information.")
            return(False)
        print("         Product: " + self.devInfo.productName)
        print("Firmware version: %d.%d" %
              (self.devInfo.deviceMajorVersion, self.devInfo.deviceMinorVersion))
        print("   Serial Number: %s" % self.devInfo.serialNumber)
        print("       Device ID: %s" % self.devInfo.deviceID)

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

    def read_pipe_out(self, addr_offset=0, data_len=1024):
        buf = bytearray(np.asarray(np.ones(data_len), np.uint8))
        e = self.xem.ReadFromPipeOut(0xA0 + addr_offset, buf)
        print('read_pipe_out:', addr_offset, buf)

        if (e < 0):
            print('Error code {}'.format(e))
        return buf, e

    def set_wire(self, address, value, mask=0xFFFF):
        # DEBUG: temporary for logging DAC80508 test
        # print(f'set_wire(address={hex(address)}, value={hex(value)}, mask={hex(mask)}')
        error_code = self.xem.SetWireInValue(address, value, mask)
        self.xem.UpdateWireIns()
        return error_code

    def read_wire(self, address):
        self.xem.UpdateWireOuts()
        return self.xem.GetWireOutValue(address)

    def set_bit(self, ep_bit, adc_chan=None):
        if adc_chan is None:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        else:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1))[adc_chan])
        self.xem.SetWireInValue(ep_bit.address, mask, mask)  # set
        self.xem.UpdateWireIns()

    def clear_bit(self, ep_bit, adc_chan=None):
        if adc_chan is None:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1)))
        else:
            mask = gen_mask(
                list(range(ep_bit.bit_index_low, ep_bit.bit_index_high + 1))[adc_chan])
        self.xem.SetWireInValue(ep_bit.address, 0x0000, mask)  # clear
        self.xem.UpdateWireIns()

    def toggle_low(self, ep_bit, adc_chan=None):
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
        '''
            expects a single bit, not yet implement for list of bits
        '''
        return self.xem.ActivateTriggerIn(ep_bit.address, ep_bit.bit_index_low)

    def read_ep(self, ep_bit):
        self.xem.UpdateWireOuts()
        read_out = self.xem.GetWireOutValue(ep_bit.address)
        return read_out

    def get_pll_freq(self, output):
        f = self.pll.GetOutputFrequency(output)
        print('Pll f = {} [MHz]'.format(f))
        return f
    
    def get_time(self):
        self.send_trig(Endpoint(0x40, 10, 10, 1))
        low_end = self.read_wire(0x25)
        high_end = self.read_wire(0x26)
        total_time =  (high_end<<32| low_end)
        total_time/=200000000
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
                if result is False: # Need is because False == 0 is True
                    continue
                print('Appending...')
                # Not an error, add to list
                pipe_ins.append(hex(ep))

        # PipeOuts (Includes Block-Throttled) [0xA0:0xBF] return -2 if the endpoint is not there
        print('Gathering PipeOuts...')
        pipe_outs = []
        # for offset in range(0x00, 0x1f + 1):
        for offset in range(32):
            # buf, result = self.read_pipe_out(addr_offset=addr_offset, data_len=16)
            buf, result = self.read_pipe_out(offset, 16)
            print(offset, buf, result)
            if result == None:
                self.set_wire(0, 0) # Intermediate step to get the FPGA to do some sort of "reset"
                continue
            elif result >= 0:
                if result is False: # Need is because False == 0 is True
                    continue
                print('Appending...')
                # Not an error, add to list
                pipe_outs.append(hex(offset + 0xa0))

        available_endpoints = [pipe_ins, pipe_outs]
        return available_endpoints


# Class for controllers on the FPGA using I2C protocol. Handles configuration, reading, writing, and reset.
# Requires First.bit file for FPGA.
class I2CController:
    DEFAULT_PARAMETERS = dict(
        # addresses for the OpalKelly interfaces (ins and outs)
        I2C_TRIGIN_GO=0,
        I2C_TRIGIN_MEM_RESET=1,
        I2C_TRIGIN_MEM_WRITE=2,
        I2C_TRIGIN_MEM_READ=3,
        I2C_TRIGOUT_DONE=0,
        I2C_MAX_TIMEOUT_MS=5000,

        PIPE_RESULTS=False,
        WIRE_RESULTS=True
    )

    # Add the registers from the Excel file to the parameters
    reg_dict = registers_from_excel('I2C')
    DEFAULT_PARAMETERS.update(reg_dict)

    def __init__(self, fpga, parameters=DEFAULT_PARAMETERS, i2c={'m_pBuf': [], 'm_nDataStart': 7}):
        self.i2c = i2c
        self.fpga = fpga
        self.parameters = parameters

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

        self.i2c['m_pBuf'][3] = data_length
        for i in range(data_length):
            self.i2c['m_pBuf'].append(data[i])

        # Reset the memory pointer and transfer the buffer.
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_RESET'])
        for i in range(data_length + self.i2c['m_nDataStart']):
            # print('(transmit) WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
            self.fpga.xem.SetWireInValue(
                self.parameters['I2C_WIREIN_DATA'].address, self.i2c['m_pBuf'][i], 0x00ff)
            self.fpga.xem.UpdateWireIns()
            self.fpga.xem.ActivateTriggerIn(
                self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_WRITE'])

        # Start I2C transaction
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_GO'])

        # Wait for transaction to finish
        for i in range(int(self.parameters['I2C_MAX_TIMEOUT_MS'] / 10)):
            self.fpga.xem.UpdateTriggerOuts()
            # change to waiting for True
            if self.fpga.xem.IsTriggered(self.parameters['I2C_TRIGOUT'].address, (1 << self.parameters['I2C_TRIGOUT_DONE'])):
                return True
            time.sleep(0.01)

        print('Timeout error in transmit')

    def i2c_receive(self, data_length):

        self.i2c['m_pBuf'][0] |= 0x80
        self.i2c['m_pBuf'][3] = data_length

        # Reset the memory pointer and transfer the buffer.
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_RESET'])

        for i in range(self.i2c['m_nDataStart']):
            # print('WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
            self.fpga.xem.SetWireInValue(
                self.parameters['I2C_WIREIN_DATA'].address, self.i2c['m_pBuf'][i], 0x00ff)
            self.fpga.xem.UpdateWireIns()
            self.fpga.xem.ActivateTriggerIn(
                self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_WRITE'])

        # Start I2C transaction
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_GO'])

        # Wait for transaction to finish
        for _ in range(int(self.parameters['I2C_MAX_TIMEOUT_MS']/10)):
            self.fpga.xem.UpdateTriggerOuts()
            # change to 1, LJK
            if self.fpga.xem.IsTriggered(self.parameters['I2C_TRIGOUT'].address, (1 << self.parameters['I2C_TRIGOUT_DONE'])):
                if self.parameters['WIRE_RESULTS']:
                    # Read data: Reset the memory pointer
                    self.fpga.xem.ActivateTriggerIn(
                        self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_RESET'])
                    data = [None]*data_length
                    for i in range(data_length):
                        self.fpga.xem.UpdateWireOuts()
                        data[i] = self.fpga.xem.GetWireOutValue(
                            self.parameters['I2C_WIREOUT_DATA'].address)
                        self.fpga.xem.ActivateTriggerIn(
                            self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_READ'])
                    return data
                if self.parameters['PIPE_RESULTS']:
                    data_read = np.int(np.ceil(data_length*4/16)*16)
                    buf, e = self.read_pipe_out(0, data_read)
                    # reset FIFO
                    self.fpga.xem.ActivateTriggerIn(
                        self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_READ'])
                    return list(buf[0::4])[0:data_length]
            time.sleep(0.01)

        print('Timeout Exception in Rx')

    def i2c_write8(self, devAddr, regAddr, data_length, data):

        preamble = [devAddr & 0xfe, regAddr]
        self.i2c_configure(2, 0x00, 0x00, preamble)
        return self.i2c_transmit(data, data_length)

    def i2c_write_long(self, devAddr, regAddr, data_length, data):

        preamble = [devAddr & 0xfe] + regAddr  # + data
        self.i2c_configure(len(preamble), 0x00, 1 << len(preamble), preamble)
        return self.i2c_transmit(data, data_length)

    # Sequence is
    # [START] DEV_ADDR(W) REG_ADDR [START] DEV_ADDR(R) VALUE
    # LJK - this command does not execute OK API calls
    def i2c_read8(self, devAddr, regAddr, data_length):

        # for the pressure sensors that only need the slave address and a read bit and then send out 4 bytes.
        if regAddr is None:
            preamble = [devAddr | 0x01]
            self.i2c_configure(1, 0x01, 0x00, preamble)
        else:
            preamble = [devAddr & 0xfe, regAddr, devAddr | 0x01]
            # signature: i2c_configure(data_length, starts (a one for each byte that gets a start), stops, preamble):
            self.i2c_configure(3, 0x02, 0x00, preamble)
        data = self.i2c_receive(data_length)

        return data

    # Sequence is
    # [START] DEV_ADDR(W) REG_ADDR [START] DEV_ADDR(R) VALUE
    # LJK - this command does not execute OK API calls
    def i2c_read_long(self, devAddr, regAddr, data_length):
        '''
        devAddr : 8 bit address (don't set the read bit (LSB) since this is done in this function)
        regAddr:  written to device (this is a list and must be even if length 1)
        data_length : number of bytes expected to receive

        '''
        preamble = [devAddr & 0xfe] + regAddr + [devAddr | 0x01]
        # signature: i2c_configure(data_length, starts (a one for each byte that gets a start), stops, preamble):
        start_positions = 0x01 << len(regAddr)
        self.i2c_configure(len(preamble), start_positions, 0x00, preamble)
        data = self.i2c_receive(data_length)

        return data

    def reset_device(self):
        self.fpga.xem.SetWireInValue(
            self.parameters['I2C_CONFIG_REG'].address, 0x01, 0x01)
        self.fpga.xem.UpdateWireIns()
        self.fpga.xem.SetWireInValue(
            self.parameters['I2C_CONFIG_REG'].address, 0x00, 0x01)
        self.fpga.xem.UpdateWireIns()

# Class for the I/O Expander TCA9555 extending the I2CController class. Handles pin configuration as inputs/outputs, reading, and writing.
class TCA9555(I2CController):
    DEFAULT_PARAMETERS = dict(I2CController.DEFAULT_PARAMETERS)
    DEFAULT_PARAMETERS.update(dict(
        ADDRESS_HEADER=0b01000000
    ))

    # Add the registers from the Excel file to the parameters
    reg_dict = registers_from_excel('TCA9555')
    DEFAULT_PARAMETERS.update(reg_dict)

    def __init__(self, fpga, addr_pins, parameters=DEFAULT_PARAMETERS):
        super().__init__(fpga, parameters)
        self.addr_pins = addr_pins

    # Method to configure the pins as inputs (1's) or outputs (0's)
    def configure_pins(self, data):
        # Inputs = 1
        # Outputs = 0
        dev_addr = self.parameters['ADDRESS_HEADER'] + (self.addr_pins << 1)
        self.i2c_write_long(
            dev_addr, [self.parameters['CONFIG'].address], 2, data)

    # Method to write 2 bytes of data to the pins.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 0100 and Write bit automatically
    def write(self, data, register_name='OUTPUT', mask=0xffff):
        dev_addr = self.parameters['ADDRESS_HEADER'] | (self.addr_pins << 1)

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
            dev_addr, [self.parameters[register_name].address], 2, list_data)

    # Method to read 2 bytes of data from the pins.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 0100 and Read bit automatically

    def read(self, register_name='INPUT'):
        dev_addr = self.parameters['ADDRESS_HEADER'] | (self.addr_pins << 1) | 0b1
        return self.i2c_read_long(dev_addr, [self.parameters[register_name].address], 2)

# Class for the ID chip 24AA025UID extending the I2CController class. Handles reading and writing.
class UID_24AA025UID(I2CController):
    DEFAULT_PARAMETERS = dict(I2CController.DEFAULT_PARAMETERS)
    DEFAULT_PARAMETERS.update(dict(
        ADDRESS_HEADER=0b10100000
    ))
    reg_dict = registers_from_excel('24AA025UID')
    DEFAULT_PARAMETERS.update(reg_dict)

    def __init__(self, fpga, addr_pins, parameters=DEFAULT_PARAMETERS):
        super().__init__(fpga, parameters)
        self.addr_pins = addr_pins

    # Method to write up to 8 bytes of data to a given word address within the chip.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 1010 and Write bit automatically
    def write(self, data, word_address=0x00, num_bytes=None):
        dev_addr = self.parameters['ADDRESS_HEADER'] | (self.addr_pins << 1)
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
            self.i2c_write_long(devAddr=dev_addr, regAddr=[word_address], data_length=16, data=list_data[:16])
            # We can recursively call this function instead of looping through multiple times.
            recurse_data = data % (0x1 << (8 * (num_bytes - 16)))
            print(f'{data} % {(0x1 << (8 * (num_bytes - 16)))} = {recurse_data}')
            self.write(data=recurse_data, word_address=word_address + 16, num_bytes=num_bytes - 16)
            return True

        # Data is no more than 16 bytes (1 page) and can be written with 1 I2C command.
        self.i2c_write_long(dev_addr, [word_address], num_bytes, list_data)
        return True

    # Method to read data from a given word address within the chip.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 1010 and Read bit automatically.
    def read(self, word_address=0x00, words_read=1):
        # A word is a byte, 8 bits
        dev_addr = self.parameters['ADDRESS_HEADER'] | (self.addr_pins << 1) | 0b1
        return self.i2c_read_long(dev_addr, [word_address], words_read)

    # Method to get the manufactured 32-bit serial number for the chip. This is different for every chip.
    def get_serial_number(self):
        serial_list = self.read(word_address=self.parameters['SERIAL_NUMBER'].address, words_read=4)
        serial_number = 0
        for byte in serial_list:
            serial_number <<= 8
            serial_number |= byte
            
        return serial_number

    # Method to get the manufacturer code. Should be 0x29.
    def get_manufacturer_code(self):
        return self.read(word_address=self.parameters['MANUFACTURER_CODE'].address)[0]

    # Method to get the device code. Should be 0x41.
    def get_device_code(self):
        return self.read(word_address=self.parameters['DEVICE_CODE'].address)[0]

# Class for the I2C DAC chip DAC53401. Handles reading, writing, and configuration. This is a child class of the parent I2CController class.
class DAC53401(I2CController):
    DEFAULT_PARAMETERS = dict(I2CController.DEFAULT_PARAMETERS)
    reg_dict = registers_from_excel('DAC53401')
    DEFAULT_PARAMETERS.update(reg_dict)
    DEFAULT_PARAMETERS['ADDRESS_HEADER'] = 0b10010000

    #        Address Pins Guide
    # Slave Address   |   A0 Pin
    #           000   |   AGND
    #           001   |   VDD
    #           010   |   SDA
    #           011   |   SCL

    def __init__(self, fpga, addr_pins, parameters=DEFAULT_PARAMETERS):
        super().__init__(fpga, parameters)
        self.addr_pins = addr_pins

    # Method to write to any register on the chip.
    def write(self, data, register_name='DAC_DATA'):
        dev_addr = self.parameters['ADDRESS_HEADER'] | (self.addr_pins << 1)
        register = self.parameters[register_name]
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

    # Method to read from any register on the chip.
    def read(self, register_name='DAC_DATA'):
        dev_addr = self.parameters['ADDRESS_HEADER'] | (self.addr_pins << 1)
        register = self.parameters[register_name]
        byte_number = register.bit_index_high // 8 # Ex. 16-bit register: | Byte 1 [15:8] | Byte 0 [7:0] |
        number_of_bytes = 2 - byte_number # 16-bit register = 2 bytes, i2c_read_long starts at the MSB so we read 2 bytes to get Byte 0
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
        desired_data = (read_back_data &
                        desired_bits) >> register.bit_index_low

        return desired_data

    # Method to write a voltage output from the DAC.
    def write_voltage(self, voltage):
        self.write(voltage, 'DAC_DATA')

    # Method to enable the internal reference. Necessary to set the gain value.
    def enable_internal_reference(self):
        self.write(0x1, 'REF_EN')

    # Method to set the gain value. Gain can be set to 1.5x, 2x, 3x, or 4x the internal reference. Internal reference must be enabled.
    def set_gain(self, gain):
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

    # Method to get the gain value.
    def get_gain(self):
        gain_dict = {
            0b00: 1.5,
            0b01: 2,
            0b10: 3,
            0b11: 4
        }

        gain_code = self.read('DAC_SPAN')
        return gain_dict.get(gain_code)

    # Method to configure the function generator.
    def config_func(self, function_name):
        func_dict = {
            # Generates a Triangle wave between MARGIN_HIGH code to MARGIN_LOW code with slope defined by SLEW_RATE.
            'triangle': 0b00,
            # Generates a Saw-Tooth wave between MARGIN_HIGH code to MARGIN_LOW code with slope defined by SLEW_RATE and immeidate falling edge.
            'sawtooth_falling': 0b01,
            # Generates a Saw-Tooth wave between MARGIN_HIGH code to MARGIN_LOW code with slope defined by SLEW_RATE and immeidate rising edge.
            'sawtooth_rising': 0b10,
            # Generates a Square wave between MARGIN_HIGH code to MARGIN_LOW code with pulse high and low period defined by defined by SLEW_RATE.
            'square': 0b11
        }

        func_code = func_dict.get(function_name.lower())
        if func_code == None:
            print('Invalid function name')
            return False
        self.write(func_code, 'FUNC_CONFIG')

    # Method to start function generation. The waveform generated is based on the FUNC_CONFIG and MARGIN_LOW, MARGIN_HIGH registers.
    # Waveform configured through config_func() and config_margins() functions.
    def start_func(self):
        self.write(0b1, 'START_FUNC_GEN')

    # Method to stop function generation.
    def stop_func(self):
        self.write(0b0, 'START_FUNC_GEN')

    # Method to configure the margins.
    def config_margins(self, margin_high=None, margin_low=None):
        if margin_high != None:
            self.write(margin_high, 'MARGIN_HIGH')

        if margin_low != None:
            self.write(margin_low, 'MARGIN_LOW')

    # Method to configure the number of bits to step through.
    def config_step(self, step):
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

    # Method to configuer the rate to step through each bit.
    def config_rate(self, rate):
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

    # Method to reset the device using a software reset.
    def reset(self):
        self.write(0b1010, 'SW_RESET')

    # Method to lock the registers of the device.
    def lock(self):
        self.write(0b1, 'DEVICE_LOCK')

    # Method to unlock the registers of the device.
    def unlock(self):
        self.write(0b0101, 'DEVICE_UNLOCK_CODE')

    # Method to power up the DAC.
    def power_up(self):
        self.write(0b00, 'DAC_PDN')

    # Method to power down the DAC to 10K.
    def power_down_10k(self):
        self.write(0b01, 'DAC_PDN')

    # Method to power down the DAC to high impedance (default).
    def power_down_high_impedance(self):
        self.write(0b10, 'DAC_PDN')

    # Method to get the DEVICE_ID and the VERSION_ID of the chip
    def get_id(self):
        device_id = self.read('DEVICE_ID')
        version_id = self.read('VERSION_ID')
        return (device_id << self.parameters['DEVICE_ID'].bit_index_low) | (version_id << self.parameters['VERSION_ID'].bit_index_low)


# Class for controllers on the FPGA using SPI protocol. Handles reading, writing, slave select, and configuration of the control register.
# Requires top_level_module.bit file for FPGA.
class SPIController:
    DEFAULT_PARAMETERS = dict(
        WB_SET_ADDRESS = 0x80000000,  # These 3 are from the SPI core manual
        WB_WRITE       = 0x40000000,
        WB_READ        = 0x00000000,
        ACK            = 0x200000000,
        WB_CLK_FREQ    = 200, # clk_sys = 200 MHz in the top_level_module.v comments
    )

    # Add the registers from the Excel file to the parameters
    reg_dict = registers_from_excel('SPI')
    DEFAULT_PARAMETERS.update(reg_dict)

    WB_1_PARAMETERS = dict(DEFAULT_PARAMETERS)
    reg_dict_WB_1 = registers_from_excel('SPI_WB_1')
    WB_1_PARAMETERS.update(reg_dict_WB_1)

    WB_2_PARAMETERS = dict(DEFAULT_PARAMETERS)
    reg_dict_WB_2 = registers_from_excel('SPI_WB_2')
    WB_2_PARAMETERS.update(reg_dict_WB_2)

    def __init__(self, fpga, master_config=DEFAULT_PARAMETERS.get('CTRL').default, parameters=DEFAULT_PARAMETERS, debug=False):
        self.fpga = fpga
        self.parameters = parameters
        self.debug = debug  # Turning on debug will show more output
        self.master_config = master_config

    # Method to send a command to the Wishbone. Sent in 32 bits through the WbSignal_converter Verilog module to reformat to 34 bits.
    def wb_send_cmd(self, command):
        print(
            f'wb_send_cmd: {hex(self.parameters["WB_IN"].address)}, {hex(command)}')
        self.fpga.set_wire(
            self.parameters['WB_IN'].address, command, 0xffffffff)
        # DEBUG: temporary for logging DAC80508 test
        # print(f'ActivateTriggerIn(address={hex(self.parameters["WB_CONVERT_TRIGGER"].address)}, index={hex(self.parameters["WB_CONVERT_TRIGGER"].bit_index_high)}')
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['WB_CONVERT_TRIGGER'].address, self.parameters['WB_CONVERT_TRIGGER'].bit_index_high)  # High and low bit indexes are the same for the trigger because it is 1 bit wide

    def wb_is_acknowledged(self):
        response = self.fpga.read_wire(self.parameters['WB_OUT'].address)
        return response == self.parameters['ACK']

    # Method to send a Wishbone command setting the address of the register we interact with.
    def wb_set_address(self, address):
        self.wb_send_cmd(
            self.parameters['WB_SET_ADDRESS'] | (address << 2) | 0x1)  # TODO: comment here what the | 0x1 is for when I figure it out
        return self.wb_is_acknowledged()  # TODO: test if acknowledge actually comes back

    # Method to write up to 30 bytes of data to the currently selected register.
    def wb_write(self, data):
        self.wb_send_cmd(self.parameters['WB_WRITE'] | data)
        return self.wb_is_acknowledged()  # TODO: test if acknowledge actually comes back

    # Method to read the data from the current register
    def wb_read(self):
        self.wb_send_cmd(self.parameters['WB_READ'])
        return self.fpga.read_wire(self.parameters['WB_OUT'].address)

    # Method to set the GO_BSY bit of the CTRL register to logic 1, initiating a SPI transmission.
    def wb_go(self):
        ack = self.wb_set_address(self.parameters['CTRL'].address)
        # TODO: fix ack
        # if ack:
        #     if self.debug:
        #         print(f'Set address to "CTRL": SUCCESS')
        # else:
        #     if self.debug:
        #         print(f'Set address to "CTRL": FAIL')
        #     return False

        busy = self.master_config | (0x1 << self.parameters['GO_BSY'].bit_index_low) # Use or so we do not overwrite the CTRL configuration, just the GO_BSY bit
        ack = self.wb_write(busy) # add mask or something to not reset entire CTRL register
        # TODO: fix ack
        # if ack:
        #     if self.debug:
        #         print(f'Set GO_BSY bit: SUCCESS')
        # else:
        #     if self.debug:
        #         print(f'Set GO_BSY bit: FAIL')
        #     return False

        return True

    # Method to write a slave_address to the SS register, selecting that slave device.
    def select_slave(self, slave_address):
        # Set address to SS register
        self.wb_set_address(self.parameters['SS'].address)

        # Write slave address
        # Don't need to mask the write because we only select 1 slave device at a time
        self.wb_write(slave_address)

    # Method to set the DIVIDER register.
    def set_divider(self, divider):
        self.wb_set_address(self.parameters['DIVIDER'].address)
        self.wb_write(divider)

    # Method to set the DIVIDER register according to the input target frequency in MHz
    def set_frequency(self, frequency):
        divider = max(round((self.parameters['WB_CLK_FREQ'])/(frequency * 2)), 1) - 1
        divider = min(divider, 0xffff_ffff) # Make sure divider does not exceed 32 bits
        self.set_divider(divider)
        return divider

    # Method to write up to 30 bits of data to register Tx0, Tx1, Tx2, or Tx3
    def write(self, data, register=0):  # register should be 0, 1, 2, or 3
        # Set address to Tx register
        ack = self.wb_set_address(self.parameters['Tx'+str(register)].address)
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

    # Method to read data from register
    def read(self, register=0):
        # Set address to the Rx register Rx0, Rx1, Rx2, or Rx3
        ack = self.wb_set_address(self.parameters['Rx'+str(register)].address)

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

    # Method to set the CTRL register using binary
    def configure_master_bin(self, data):
        self.wb_set_address(self.parameters['CTRL'].address)
        self.wb_write(data)
        self.master_config = data

    # Method to set the CTRL register using several arguments
    def configure_master(self, ASS=0, IE=0, LSB=0, Tx_NEG=0, Rx_NEG=0, CHAR_LEN=0):
        params = {'ASS': ASS, 'IE': IE, 'LSB': LSB, 'Tx_NEG': Tx_NEG, 'Rx_NEG': Rx_NEG, 'CHAR_LEN': CHAR_LEN}

        configuration = self.parameters['CTRL'].default
        for param in params:
            configuration |= (params[param] << self.parameters[param].bit_index_low)
        self.configure_master_bin(configuration)

    # Method to get the current configuration of the non-reserved CTRL register bits in a dictionary
    # Includes ASS, IO, LSB, Tx_NEG, Rx_NEG, CHAR_LEN
    def get_master_configuration(self):
        self.wb_set_address(self.parameters['CTRL'].address)
        config_data = self.wb_read()
        #TODO: convert to text data to show individual settings
        # return config
        return config_data

    # Method to reset the Wishbone Master and SPI Core
    def reset_master(self):
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['MASTER_RESET'].address, self.parameters['MASTER_RESET'].bit_index_low)

# Class for DAC80508 chip extending SPIController. Handles read, write, configuration, gain configuration, id, and reset.
class DAC80508(SPIController):
    DEFAULT_PARAMETERS = dict(SPIController.DEFAULT_PARAMETERS)
    DEFAULT_PARAMETERS.update(dict(
        WRITE_OPERATION=0x000000,
        READ_OPERATION=0x800000
    ))

    # Get registers from spreadsheet
    reg_dict = registers_from_excel('DAC80508')
    config_dict = registers_from_excel('DAC80508_CONFIG')
    DEFAULT_PARAMETERS.update(reg_dict)
    DEFAULT_PARAMETERS.update(dict(CONFIG_DICT=config_dict))

    def __init__(self, fpga, master_config=0x3218, slave_address=0x1, chip_number=0, parameters=DEFAULT_PARAMETERS, debug=False):
        # master_config=0x3218 Sets CHAR_LEN=24, Rx_NEG, ASS, IE
        self.slave_address = slave_address
        super().__init__(fpga, master_config, parameters, debug)
        self.parameters['WB_IN'] = self.parameters['WB_IN_' + str(chip_number)]
        self.parameters['WB_OUT'] = self.parameters['WB_OUT_' +
                                                    str(chip_number)]
        self.parameters['WB_CONVERT_TRIGGER'] = self.parameters['WB_CONVERT_TRIGGER_' +
                                                                str(chip_number)]

    # Method to write to any register on the chip.
    def write(self, register_name, data, mask=0xffff):
        # .get instead of [brackets] because .get will return None if the register name is not in the dictionary
        reg = self.parameters.get(register_name)
        if reg == None:
            print('Register not in parameters')
            return False

        # self.select_slave(self.slave_address)

        # Get current data
        current_data = self.read(register_name)
        # Create new data from input data, mask, and current data
        new_data = (data & mask) | (current_data & ~mask)

        # 23=0 (write), [22:20]=000 (reserved), [19:16]=A[3:0] (reg address), [15:0]=D[15:0] (data)
        transmission = self.parameters['WRITE_OPERATION'] + \
            (reg.address << 16) + new_data
        print(f'Transmission = {hex(transmission)}')  # DEBUG
        ack = super().write(transmission)
        if ack:
            print(f'Write {hex(data)} to {register_name}: SUCCESS')
        else:
            print(f'Write {hex(data)} to {register_name}: FAIL')
        return ack

    # Method to read from any register on the chip.

    def read(self, register_name):
        # .get instead of [brackets] because .get will return None if the register name is not in the dictionary
        reg = self.parameters.get(register_name)
        if reg == None:
            print(f'"{register_name}" not in parameters')
            return False

        self.select_slave(self.slave_address)
        # Issue read command
        # 23=1 (read), [22:20]=000 (reserved), [19:16]=A[3:0] (reg address), [15:0]=0xXXXX (do not cares)
        transmission = self.parameters['READ_OPERATION'] | (reg.address << 16)
        super().write(transmission)

        # Read in response
        # 23=1 (echo read), [22:20]=000 (echo reserved), [19:16]=A[3:0] (echo reg address), [15:0]=D[15:0] (data read)
        read_out = super().read()
        data_read = read_out & 0xffff  # Data is only in bottom 16 bits
        return data_read

    # Method to set the configuration register with a binary number.
    def set_config_bin(self, data, mask=0xffff):
        # Write new config
        return self.write('CONFIG', data, mask)

    # Method to set the configuration register with multiple arguments.
    def set_config(self, ALM_SEL=0, ALM_EN=0, CRC_EN=0, FSDO=0, DSDO=0, REF_PWDWN=0, DAC7_PWDWN=0, DAC6_PWDWN=0, DAC5_PWDWN=0, DAC4_PWDWN=0, DAC3_PWDWN=0, DAC2_PWDWN=0, DAC1_PWDWN=0, DAC0_PWDWN=0, ):
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

    # Method to read the current configuration register data.
    def get_config(self, display_values=True):
        config = self.read('CONFIG')
        if not config:
            print('Get Configuration: FAIL')
            return False
        if display_values:
            for key in self.parameters['CONFIG_DICT']:
                # High and low bit indexes are the same because it is 1 bit wide
                print(
                    f"{key}: {bool(config & self.parameters['CONFIG_DICT'][key].bit_index_high)}")
        return config

    # Method to set the gain value.
    def set_gain(self, data, mask=0x01ff):
        return self.write('GAIN', data, mask)

    # Method to get the gain value.
    def get_gain(self):
        return self.read('GAIN')

    # Method to get the device info from its ID.
    def get_id(self, display=True):
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

    # Method to soft reset the chip.
    def reset(self):
        ack = self.write('TRIGGER', 0b1010, 0x000f)
        if self.debug:
            if ack:
                print('Reset: SUCCESS')
            else:
                print('Reset: FAIL')
        return ack


class AD5453(SPIController):
    DEFAULT_PARAMETERS = dict(SPIController.DEFAULT_PARAMETERS)
    DEFAULT_PARAMETERS.update(registers_from_excel('AD5453'))
    DEFAULT_PARAMETERS.update(dict(
        bits = 12,
        vref = 2.5*2
    ))

    def __init__(self, fpga, master_config=0x3010, parameters=DEFAULT_PARAMETERS, debug=False):
        # master_config=0x3010 Sets CHAR_LEN=16, ASS, IE
        super().__init__(fpga, master_config=master_config, parameters=parameters, debug=debug)
        self.clk_edge_bits = 0b00 # Default to clocking data into the shift register on the falling edge of the clock

    def send_val(self, to_send):
        # now send SPI command
        # to_send a 14 bit word (1/2 scale is 1ffff)
        value = self.parameters['WB_WRITE'] | to_send

        for val in [self.parameters['WB_SET_ADDRESS'] | 0x1, value,  # Tx register, data to send
                    self.parameters['WB_SET_ADDRESS'] | 0x40 | 0x1, self.master_config | (1 << 8)]:  # Control register - GO (bit 8)
            self.fpga.set_wire(self.parameters['control'].address, val, mask=0xffffffff)
            self.fpga.send_trig(self.parameters['valid'])

    # Method to set the control bits of the signals we write to use the rising edge of the clock rather than the default falling edge
    # To return to the falling edge, the chip requires a power cycle (turn it off and back on)
    def set_clk_rising_edge(self):
        self.clk_edge_bits = 0b11

    # Method to write 14 bits of data with the option to clock data on the rising edge of the clock rather than the default falling edge of the clock.
    def write(self, data):
        super().write(self.clk_edge_bits | data)


class ADS7952(SPIController):
    DEFAULT_PARAMETERS = dict(SPIController.DEFAULT_PARAMETERS)
    DEFAULT_PARAMETERS.update(registers_from_excel('ADS7952'))

    def __init__(self, fpga, master_config=0x3010, parameters=DEFAULT_PARAMETERS, debug=False):
        # master_config=0x3010 Sets CHAR_LEN=16, ASS, IE
        super().__init__(fpga, master_config=master_config, parameters=parameters, debug=debug)
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
        pass # TODO: write method

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
        pass #TODO: figure out what needs to be set up, if anything


# Class for the ADS8686 ADC chip.
class ADS8686(SPIController):
    DEFAULT_PARAMETERS = dict(SPIController.DEFAULT_PARAMETERS)
    DEFAULT_PARAMETERS.update(registers_from_excel('ADS8686'))

    def __init__(self, fpga, master_config=0x3010, parameters=DEFAULT_PARAMETERS, debug=False):
        # master_config=0x3010 Sets CHAR_LEN=16, ASS, IE
        super().__init__(fpga, master_config=master_config, parameters=parameters, debug=debug)
        self.channel = 0

    # Method to read a desired channel on the chip
    def read_channel(self, channel):
        pass # TODO: write method

    # Method to read from the current set channel on the chip
    def read(self):
        self.read_channel(self.channel)

    # Method to set up the chip
    def setup(self):
        pass # TODO: write method


# Class for the AD7961 Fast ADC. Does not use SPI or I2C.
class AD7961:
    DEFAULT_PARAMETERS = {
        'adc_chan' : 0
    }
    DEFAULT_PARAMETERS.update(registers_from_excel('AD7961'))

    def __init__(self, fpga, parameters=DEFAULT_PARAMETERS):
        self.fpga = fpga
        self.parameters = parameters

    def get_status(self, fpga):
        '''
        adc_pll_lock =   ep(0x20, 8, 'wo')
        adc_fifo_full =  ep(0x20, 9, 'wo')
        adc_fifo_empty = ep(0x20, 10, 'wo')
        pipe_out_rd_cnt = ep(0x20, [i+11 for i in range(10)], 'wo') # 10 bits
        '''
        fpga.xem.UpdateWireOuts()
        a = fpga.xem.GetWireOutValue(self.parameters.get('adc_pll_lock').addr)
        for s, n in [(self.parameters.get('adc_pll_lock'), 'pll_lock'),
                    (self.parameters.get('adc_fifo_full'), 'fifo_full'),
                    (self.parameters.get('adc_fifo_empty'), 'fifo_empty')]:
            v = test_bit(a, s.bits)
            print('Status {} = {} \n --------- \n'.format(n, v))

        fifo_cnt = (a >> self.parameters.get('pipe_out_rd_cnt').bits[0]
                    ) & 2**(len(self.parameters.get('pipe_out_rd_cnt').bits)-1)
        print('Data count in ADC FIFO = {}'.format(fifo_cnt))
        return a


    def convert_data(self, buf):
        bits = 16  # for AD7961 bits=18 for AD7960
        d = np.frombuffer(buf, dtype=np.uint8).astype(np.uint32)
        if bits == 16:
            d2 = d[0::4] + (d[1::4] << 8)
        elif bits == 18:
            # not sure of this
            d2 = (d[3::4] << 8) + d[1::4] + ((d[0::4] << 16) & 0x03)
            # d2 = (d[3::4]<<8) + d[1::4] + ((d[0::4]<<16) & 0x03)

        d_twos = twos_comp(d2, bits)
        return d_twos


    def setup(self):
        # reset PLL
        self.fpga.toggle_high(self.parameters.get('adc_pll_reset'))
        self.fpga.clear_bit(self.parameters.get('adc_reset'), adc_chan = self.parameters.get('adc_chan'))
        # reset FIFO
        self.fpga.toggle_high(self.parameters.get('adc_fifo_reset'))
        # enable ADC
        self.fpga.set_bit(self.parameters.get('adc_reset'), adc_chan = self.parameters.get('adc_chan'))
        self.fpga.set_bit(self.parameters.get('adc_en0'), adc_chan = self.parameters.get('adc_chan'))

    # test composite ADC function that enables, reads, converts and plots

    def read(self):
        s, e = self.fpga.read_pipe_out(addr_offset=1)
        data = self.convert_data(s)
        return data

    def adc_stream_mult(self, swps=4):
        cnt = 0
        st = bytearray(np.asarray(np.ones(0, np.uint8)))
        self.fpga.xem.UpdateTriggerOuts()

        while cnt < swps:
            if (self.fpga.xem.IsTriggered(0x60, 0x01)):
                s, e = self.fpga.read_pipe_out()
                st += s
                cnt = cnt + 1
                print(cnt)
            self.fpga.xem.UpdateTriggerOuts()

        data = self.convert_data(st)
        return data
