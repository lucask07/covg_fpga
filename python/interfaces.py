"""
Python script for configuring OpalKelly XEM7310 
and use it as an I2C controller.

Much of the Python is no longer used as the FPGA code is simpler than previously. 
Functions no longer in use include SHUF (shuffling) and multiple and/or timed reads. 

May 2021

Lucas Koerner, koer2434@stthomas.edu

"""
import ok
import time
import numpy as np
import pandas as pd
import os

# Class for registers to be used within chips and the SPI core. Contains the register's hex address, default value, bit index, and bit width.
class Register():
    spreadsheet_path = os.getcwd()
    for i in range(15): # The Registers spreadsheet is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
        if os.path.basename(spreadsheet_path) == 'covg_fpga':
            spreadsheet_path = os.path.join(spreadsheet_path, 'Registers.xlsx')
            break
        else:
            spreadsheet_path = os.path.dirname(spreadsheet_path) # If we aren't in covg_fpga, move up a folder and check again
        

    def __init__(self, address, default, bit_width, bit_index_high, bit_index_low):
        self.address        = address
        self.default        = default
        self.bit_index_high = bit_index_high
        self.bit_index_low  = bit_index_low
        self.bit_width      = bit_width

    @classmethod
    def dict_from_excel(cls, sheet, workbook=spreadsheet_path):
        reg_dict = {}
        sheet_data = pd.read_excel(workbook, sheet)
        for row in range(len(sheet_data)):
            row_data = sheet_data.iloc[row]
            reg_dict[row_data['Name']] = Register(
                address        = int(row_data['Hex Address'], 16),
                default        = int(row_data['Default Value'], 16),
                bit_width      = int(row_data['Bit Width']),
                bit_index_high = (None if row_data['Bit Index (High)'] == 'None' else int(row_data['Bit Index (High)'])),  # Bit Index of None means the register takes up the whole endpoint
                bit_index_low  = (None if row_data['Bit Index (Low)'] == 'None' else int(row_data['Bit Index (Low)'])))
        return reg_dict

# Class for the FPGA itself. Handles FPGA configuration, setting wire values, and other FPGA specific functions.
class FPGA():
    def __init__(self, bitfile='../starter.runs/impl_1/First.bit'): # TODO: change to complete bitfile when Verilog is combined

        self.bitfile = bitfile
        self.i2c = {'m_pBuf': [], 'm_nDataStart': 7}
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

        self.pll = ok.okCPLL22150()

        print("FrontPanel support is available.")
        return self

    def read_pipe_out(self, addr_offset=0, data_len=1024):

        buf = bytearray(np.asarray(np.ones(data_len), np.uint8))
        e = self.xem.ReadFromPipeOut(0xA0 + addr_offset, buf)

        if (e < 0):
            print('Error code {}'.format(e))
        return buf, e

    def set_wire(self, address, value, mask=0xFFFF):
        self.xem.SetWireInValue(address, value, mask)
        self.xem.UpdateWireIns()

    def read_wire(self, address):
        self.xem.UpdateWireOuts()
        return self.xem.GetWireOutValue(address)

    def infile(self, infile, outfile):
        # RAM test
        fileIn = open(infile, "rb")
        fileOut = open(outfile, "wb")

        # Reset the RAM address pointer.
        self.xem.ActivateTriggerIn(0x41, 0)

        while fileIn:
            buf = bytearray(fileIn.read(2048))

            got = len(buf)
            if (got == 0):
                break

            if (got < 2048):
                buf += b"\x00"*(2048-got)

            # Write a block of data.
            self.xem.ActivateTriggerIn(0x41, 0)
            self.xem.WriteToPipeIn(0x80, buf)

            # Perform DES on the block.
            self.xem.ActivateTriggerIn(0x40, 0)

            # Wait for the TriggerOut indicating DONE.
            for i in range(100):
                self.xem.UpdateTriggerOuts()
                if (self.xem.IsTriggered(0x60, 1)):
                    break

            self.xem.ReadFromPipeOut(0xa0, buf)
            fileOut.write(buf)

        fileIn.close()
        fileOut.close()

    def get_pll_freq(self):
        f = self.pll.GetOutputFrequency(0)
        print('Pll f = {} [MHz]'.format(f))
        return f

    def read_sensors(self):
        '''
        https://opalkelly.com/examples/device-sensors-api/#tab-python
        '''
        sensors = self.xem.GetDeviceSensors()

        # Retrieve individual sensors using index values
        for s in sensors:
            print('Sensor name = {}; value = {}'.format(s.name,
                                                        s.value))

        return sensors

# Class for controllers on the FPGA using I2C protocol. Handles configuration, reading, writing, and reset.
# Requires First.bit file for FPGA.
class I2CController():
    DEFAULT_PARAMETERS = dict(
        # addresses for the OpalKelly interfaces (ins and outs)
        I2C_TRIGIN_GO        = 0,
        I2C_TRIGIN_MEM_RESET = 1,
        I2C_TRIGIN_MEM_WRITE = 2,
        I2C_TRIGIN_MEM_READ  = 3,
        I2C_TRIGOUT_DONE     = 0,
        I2C_MAX_TIMEOUT_MS   = 5000,

        PIPE_RESULTS=False,
        WIRE_RESULTS=True
    )

    # Add the registers from the Excel file to the parameters
    reg_dict = Register.dict_from_excel('I2C')
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
        self.fpga.xem.ActivateTriggerIn(self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_RESET'])
        for i in range(data_length + self.i2c['m_nDataStart']):
            # print('(transmit) WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
            self.fpga.xem.SetWireInValue(
                self.parameters['I2C_WIREIN_DATA'].address, self.i2c['m_pBuf'][i], 0x00ff)
            self.fpga.xem.UpdateWireIns()
            self.fpga.xem.ActivateTriggerIn(self.parameters['I2C_TRIGIN'].address, self.parameters['I2C_TRIGIN_MEM_WRITE'])

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

        print('Timeout Excpetion in Rx')

    def i2c_write8(self, devAddr, regAddr, data_length, data):

        preamble = [devAddr & 0xfe, regAddr]
        self.i2c_configure(2, 0x00, 0x00, preamble)
        return self.i2c_transmit(data, data_length)

    def i2c_write_long(self, devAddr, regAddr, data_length, data):

        print('i2c write long')
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
class IOExpanderController(I2CController):
    DEFAULT_PARAMETERS = dict(I2CController.DEFAULT_PARAMETERS)
    DEFAULT_PARAMETERS.update(dict(
        ADDRESS_HEADER=0b01000000
        ))

    # Add the registers from the Excel file to the parameters
    reg_dict = Register.dict_from_excel('IOExpander')
    DEFAULT_PARAMETERS.update(reg_dict)

    def __init__(self, fpga, parameters=DEFAULT_PARAMETERS):
        super().__init__(fpga, parameters)

    # Method to configure the pins as inputs (1's) or outputs (0's)
    def configure_pins(self, addr_pins, data):
        # Inputs = 1
        # Outputs = 0
        dev_addr = self.parameters['ADDRESS_HEADER'] + (addr_pins*2)
        self.i2c_write_long(
            dev_addr, [self.parameters['SLAVE_CONFIG_REG'].address], 2, data)

    # Method to write 2 bytes of data to the pins.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 0100 and Write bit automatically
    def write(self, addr_pins, data, mask=0xffff):
        dev_addr = self.parameters['ADDRESS_HEADER'] + (addr_pins*2)

        # Compare with current data to mask unchanged values
        if mask == 0xffff:
            new_data = data
        else:
            current_data = self.read(addr_pins)
            new_data = (data & mask) | (current_data & ~mask)

        self.i2c_write_long(
            dev_addr, [self.parameters['SLAVE_OUTPUT_REG'].address], 2, new_data)


    # Method to read 2 bytes of data from the pins.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 0100 and Read bit automatically
    def read(self, addr_pins):
        dev_addr = self.parameters['ADDRESS_HEADER'] + (addr_pins*2) + 0b1
        return self.i2c_read_long(dev_addr, [self.parameters['SLAVE_INPUT_REG'].address], 2)

# Class for the ID chip 24AA025UID extending the I2CController class. Handles reading and writing.
class IDChipController(I2CController):
    DEFAULT_PARAMETERS = I2CController.DEFAULT_PARAMETERS.update(dict(
        ADDRESS_HEADER = 10100000
    ))
    def __init__(self, fpga, parameters):
        super().__init__(fpga, parameters)

    # Method to write up to 8 bytes of data to a given word address within the chip.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 1010 and Write bit automatically
    def write(self, addr_pins, data, word_address=0x00):
        dev_addr = self.parameters['ADDRESS_HEADER'] + (addr_pins*2)
        # Determine the byte length of the data
        shifted_data = data
        number_of_bytes = 0
        while shifted_data != 0:
            number_of_bytes += 1
            shifted_data >>= 8
        self.i2c_write_long(dev_addr, [word_address], number_of_bytes, data)

    # Method to read 1 byte of data from a given word address within the chip.
    # We only need to be given the { A2 A1 A0 } pin values for the device, we can add the 0100 and Read bit automatically
    def read(self, addr_pins, word_address=0x00):
        dev_addr = self.parameters['ADDRESS_HEADER'] + (addr_pins*2) + 0b1
        return self.i2c_read_long(dev_addr, [word_address], 1)

# Class for controllers on the FPGA using SPI protocol. Handles reading, writing, slave select, and configuration of the control register.
# Requires top_level_module.bit file for FPGA.
class SPIController():
    DEFAULT_PARAMETERS = dict(
        WB_SET_ADDRESS = 0x80000000, # These 3 are from the SPI core manual
        WB_WRITE       = 0x40000000,
        WB_READ        = 0x00000000,
        ACK            = 0x200000000,

        CTRL_BITS      = dict(
            ASS      = 0b10000000000000,
            IE       = 0b01000000000000,
            LSB      = 0b00100000000000,
            Tx_NEG   = 0b00010000000000,
            Rx_NEG   = 0b00001000000000,
            CHAR_LEN = 0b00000001111111
        )
    )

    # Add the registers from the Excel file to the parameters
    reg_dict = Register.dict_from_excel('SPI')
    DEFAULT_PARAMETERS.update(reg_dict)

    WB_1_PARAMETERS = dict(DEFAULT_PARAMETERS)
    reg_dict_WB_1 = Register.dict_from_excel('SPI_WB_1')
    WB_1_PARAMETERS.update(reg_dict_WB_1)

    WB_2_PARAMETERS = dict(DEFAULT_PARAMETERS)
    reg_dict_WB_2 = Register.dict_from_excel('SPI_WB_2')
    WB_2_PARAMETERS.update(reg_dict_WB_2)

    def __init__(self, fpga, parameters=WB_1_PARAMETERS, debug=False):
        self.fpga = fpga
        self.parameters = parameters
        self.debug = debug # Turning on debug will show more output

    # Method to send a command to the Wishbone. Sent in 32 bits through the WbSignal_converter Verilog module to reformat to 34 bits.
    def wb_send_cmd(self, command):
        self.fpga.set_wire(
            self.parameters['WB_IN'].address, command, 0xffffffff)
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['TRIGGER_BIT'].address, self.parameters['TRIGGER_BIT'].bit_index_high)  # High and low bit indexes are the same for the trigger because it is 1 bit wide

    def wb_is_acknowledged(self):
        response = self.fpga.read_wire(self.parameters['WB_OUT'].address)
        if response == self.parameters['ACK']:
            acknowledged = True
        else:
            acknowledged = False
        return acknowledged

    # Method to send a Wishbone command setting the address of the register we interact with.
    def wb_set_address(self, address):
        self.wb_send_cmd(
            self.parameters['WB_SET_ADDRESS'] | address)
        return self.wb_is_acknowledged() # TODO: test if acknowledge actually comes back

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
        self.wb_set_address(self.parameters['CTRL'].address)
        self.wb_write(0x00000100)

    # Method to write a slave_address to the SS register, selecting that slave device.
    def select_slave(self, slave_address):
        # Set address to SS register
        self.wb_set_address(self.parameters['SS'].address)

        # Write slave address
        self.wb_write(slave_address) # Don't need to mask the write because we only select 1 slave device at a time

    # Method to set the DIVIDER register.
    def set_divider(self, divider):
        self.wb_set_address(self.parameters['DIVIDER'].address)
        self.wb_write(divider)

    # Method to set the DIVIDER register according to the input target frequency
    def set_frequency(self, frequency):
        divider = round((2*self.parameters['WB_CLK'])/frequency) - 1
        self.set_divider(divider)
        return divider

    # Method to write up to 30 bits of data to register Tx0, Tx1, Tx2, or Tx3
    def write(self, data, register=0): # register should be 0, 1, 2, or 3
        # Set address to Tx register
        ack = self.wb_set_address(self.parameters['Tx'+str(register)].address)
        if ack:
            if self.debug:
                print(f'Set address to "Tx{register}": SUCCESS')
        else:
            if self.debug:
                print(f'Set address to "Tx{register}": FAIL')
            return False

        # Write data
        ack = self.wb_write(data)
        if ack:
            if self.debug:
                print(f'Data write to "Tx{register}": SUCCESS')
        else:
            if self.debug:
                print(f'Data write to "Tx{register}": FAIL')
            return False

        # Set address to CTRL register
        ack = self.wb_set_address(self.parameters['CTRL'].address)
        if ack:
            if self.debug:
                print(f'Set address to "CTRL": SUCCESS')
        else:
            if self.debug:
                print(f'Set address to "CTRL": FAIL')
            return False

        # Set GO_BSY bit
        self.wb_go()
        return True

    # Method to read data from register 
    def read(self, register=0):
        # Set address to the Rx register Rx0, Rx1, Rx2, or Rx3
        ack = self.wb_set_address(self.parameters['Rx'+str(register)].address)

        if ack:
            if self.debug:
                print(f'Set address to "Rx{register}": SUCCESS')
        else:
            if self.debug:
                print(f'Set address to "Rx{register}": FAIL')
            return False

        # Read data
        return self.wb_read()

    # Method to set the CTRL register using binary
    def configure_master_bin(self, data, mask=0xffff):
        self.wb_set_address(self.parameters['CTRL'].address)
        self.fpga.set_wire(self.parameters['WB_IN'].address, data, mask)
        self.fpga.xem.ActivateTriggerIn(
            self.parameters['TRIGGER_BIT'].address, self.parameters['TRIGGER_BIT'].bit_index_high)  # High and low bit indexes are the same for the trigger because it is 1 bit wide
        response = self.fpga.read_wire(self.parameters['WB_OUT'].address)
        if response == self.parameters['ACK']:
            ack = True
        else:
            ack = False
        print(f'Acknowledged: {ack}')

    # Method to set the CTRL register using several arguments
    def configure_master(self, ASS=None, IE=None, LSB=None, Tx_NEG=None, Rx_NEG=None, CHAR_LEN=None):
        params = [ASS, IE, LSB, Tx_NEG, Rx_NEG, CHAR_LEN]
        mask = ''
        for bit in range(len(params)-1):
            if params[bit] == None:
                mask += '0'
                params[bit] = 0
            else:
                mask += '1'
        mask += '0' # Reserved bit
        if CHAR_LEN == None: # CHAR_LEN is 7 bits rather than 1, so its portion of the mask goes outside the loop
            mask += '0000000'
        else:
            mask += '1111111'
        mask = int(mask, 2)

        configuration = 0x00000000 + params[0] * \
            2**(13) + params[1]*2**(12) + params[2]*2**(11) + \
            params[3]*2**(10) + params[4]*2**(9) + params[5]
        self.configure_bin(configuration, mask)

    # Method to get the current configuration of the non-reserved CTRL register bits in a dictionary
    # Includes ASS, IO, LSB, Tx_NEG, Rx_NEG, CHAR_LEN
    def get_master_configuration(self):
        config = {}
        self.wb_set_address(self.parameters['CTRL'].address)
        config_data = self.wb_read()
        for bit in self.parameters['CTRL_BITS']:
            config[bit] = bool(self.parameters['CTRL_BITS'][bit] & config_data)
        return config

# Class for DAC80508 chip extending SPIController. Handles read, write, configuration, gain configuration, id, and reset.
class GeneralDACController(SPIController):
    DEFAULT_PARAMETERS = dict(SPIController.WB_1_PARAMETERS)
    DEFAULT_PARAMETERS.update(dict(
        WRITE_OPERATION = 0x000000,
        READ_OPERATION = 0x800000
    ))

    # Get registers from spreadsheet
    reg_dict = Register.dict_from_excel('DAC80508')
    config_dict = Register.dict_from_excel('DAC80508_CONFIG')
    DEFAULT_PARAMETERS.update(reg_dict)
    DEFAULT_PARAMETERS.update(dict(CONFIG_DICT = config_dict))
    
    def __init__(self, fpga, slave_address=0x5, parameters=DEFAULT_PARAMETERS, debug=False):
        self.slave_address = slave_address
        super().__init__(fpga, parameters, debug)

    # Method to write to any register on the chip.
    def write(self, register_name, data, mask=0xffff):
        reg = self.parameters.get(register_name) # .get instead of [brackets] because .get will return None if the register name is not in the dictionary
        if reg == None:
            print('Register not in parameters')
            return False

        self.select_slave(self.slave_address)
        
        # Get current data
        current_data = self.read(register_name)
        # Create new data from input data, mask, and current data
        new_data = (data & mask) | (current_data & ~mask)
        
        # 23=0 (write), [22:20]=000 (reserved), [19:16]=A[3:0] (reg address), [15:0]=D[15:0] (data) 
        transmission = self.parameters['WRITE_OPERATION'] + \
            reg.address*2**15 + new_data
        ack = super().write(transmission)
        if ack:
            print(f'Write {hex(data)} to {register_name}: SUCCESS')
        else:
            print(f'Write {hex(data)} to {register_name}: FAIL')
        return ack


    # Method to read from any register on the chip.
    def read(self, register_name):
        reg = self.parameters.get(register_name) # .get instead of [brackets] because .get will return None if the register name is not in the dictionary
        if reg == None:
            print(f'"{register_name}" not in parameters')
            return False

        self.select_slave(self.slave_address)
        # Issue read command
        # 23=1 (read), [22:20]=000 (reserved), [19:16]=A[3:0] (reg address), [15:0]=0xXXXX (do not cares)
        transmission = self.parameters['READ_OPERATION'] + \
            reg.address*2**15
        super().write(transmission)

        # Read in response
        # 23=1 (echo read), [22:20]=000 (echo reserved), [19:16]=A[3:0] (echo reg address), [15:0]=D[15:0] (data read)
        read_out = super().read()
        data_read = read_out & 0xffff # Data is only in bottom 16 bits
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
                print(f"{key}: {bool(config & self.parameters['CONFIG_DICT'][key].bit_index_high)}") # High and low bit indexes are the same because it is 1 bit wide
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
        if not id: # Check to see if the read worked
            print('ID could not be read')
            return False
        if display:
            device_id = bin(id >> 2)[2:] # Only from 2 on to skip the '0b'
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

if __name__ == '__main__':
    f = FPGA()
    f.init_device()  # load the bitstream to the FPGA and initialize
    io_expander = IOExpanderController(fpga=f)

    ######## I2C setup ################
    i2c_addr = '0100000'  # slave address of the device
    dev_addr = int(i2c_addr, 2) << 1

    ######## toggle LEDs (using a mask) #########
    f.set_wire(0x00, value=0x0000, mask=0xff00)
    time.sleep(3)
    f.set_wire(0x00, value=0xff00, mask=0xff00)
    time.sleep(3)

    io_expander.reset_device()

    # Set outputs
    io_expander.configure_pins(dev_addr, [0x00, 0x00])

    # Write to outputs
    io_expander.write(dev_addr, [0xaa, 0xaa])

    # Set inputs
    io_expander.configure_pins(dev_addr, [0xff, 0xff])

    # Read from inputs
    print(io_expander.read(dev_addr))
