import ok
import sys
import string
import time
import numpy as np

I2C_TRIGIN = 0x50
I2C_TRIGOUT = 0x70
I2C_CONFIG_REG = 0x00
I2C_WIREIN_DATA = 0x01
I2C_REP_REG = 0x03
I2C_WIREOUT_DATA = 0x20

I2C_SHUF_CH0 = 4 # for configuring CH0 (or reading from it all the time)
I2C_SHUF_CH1 = 5 # for configuring CH1 (or reading from it all the time)
I2C_SHUF_ON = 3 # for multiple reads

I2C_TRIGIN_GO = 0
I2C_TRIGIN_MEM_RESET = 1
I2C_TRIGIN_MEM_WRITE = 2
I2C_TRIGIN_MEM_READ = 3
I2C_TRIGOUT_DONE = 0
I2C_TRIGOUT_MULT_DONE = 1
I2C_TRIGOUT_FIFO_HALF = 2
I2C_MAX_TIMEOUT_MS = 5000

PIPE_RESULTS = True
WIRE_RESULTS = False

class FPGA():
    def __init__(self, bitfile = '../SPI_Master/top_level_module.bit'):
        self.bitfile = bitfile
        self.i2c = {'m_pBuf': [], 'm_nDataStart': 7}
        return

    def init_device(self):
        # Open the first device we find.
        self.xem = ok.okCFrontPanel()
        if (self.xem.NoError != self.xem.OpenBySerial("")):
            print ("A device could not be opened.  Is one connected?")
            return(False)

        # Get some general information about the device.
        self.devInfo = ok.okTDeviceInfo()
        if (self.xem.NoError != self.xem.GetDeviceInfo(self.devInfo)):
            print ("Unable to retrieve device information.")
            return(False)
        print("         Product: " + self.devInfo.productName)
        print("Firmware version: %d.%d" % (self.devInfo.deviceMajorVersion, self.devInfo.deviceMinorVersion))
        print("   Serial Number: %s" % self.devInfo.serialNumber)
        print("       Device ID: %s" % self.devInfo.deviceID)

        self.xem.LoadDefaultPLLConfiguration()

        # Download the configuration file.
        if (self.xem.NoError != self.xem.ConfigureFPGA(self.bitfile)):
            print ("FPGA configuration failed.")
            return(False)
        else:
            print('Loaded bit-file: {}'.format(self.bitfile))

        # Check for FrontPanel support in the FPGA configuration.
        if (False == self.xem.IsFrontPanelEnabled()):
            print ("FrontPanel support is not available.")
            return(False)

        self.pll = ok.okCPLL22150()

        print ("FrontPanel support is available.")
        return self

    def read_pipe_out(self, addr_offset = 0, data_len = 1024):

        buf = bytearray(np.asarray(np.ones(data_len), np.uint8))
        e = self.xem.ReadFromPipeOut(0xA0 + addr_offset, buf)

        if (e < 0):
            print('Error code {}'.format(e))
        return buf, e

    def set_wire(self, address, value, mask=0xFFFF):
        self.xem.SetWireInValue(address, value, mask)
        self.xem.UpdateWireIns()

    def set_wire_bit(self, address, bit):
        return self.xem.set_wire(address, value=1 << bit, mask=1 << bit)

    def clear_wire_bit(self, address, bit):
        return self.xem.set_wire(address, value=0, mask=1 << bit)



    def reset_device(self):
        self.xem.SetWireInValue(0x10, 0xff, 0x03)
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(0x10, 0x00, 0x03)
        self.xem.UpdateWireIns()

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
        self.i2c['m_pBuf'][3] = 0        # Payload length will be provided later.
        for i in range(data_length):
            self.i2c['m_pBuf'][4+i] = preamble[i]

        self.i2c['m_nDataStart'] = 4 + data_length

    def i2c_transmit(self, data, data_length):

        self.i2c['m_pBuf'][3] = data_length
        for i in range(data_length):
            self.i2c['m_pBuf'].append(data[i])

        # Reset the memory pointer and transfer the buffer.
        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)
        for i in range(data_length + self.i2c['m_nDataStart']):
            # print('(transmit) WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
            self.xem.SetWireInValue(I2C_WIREIN_DATA, self.i2c['m_pBuf'][i], 0x00ff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_WRITE)

        # Start I2C transaction
        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_GO)

        # Wait for transaction to finish
        for i in range( int(I2C_MAX_TIMEOUT_MS / 10)):
            self.xem.UpdateTriggerOuts()
            if self.xem.IsTriggered(I2C_TRIGOUT, (1 << I2C_TRIGOUT_DONE)): # change to waiting for True
                return True
            time.sleep(0.01)

        print('Timeout error in transmit')

    def i2c_receive(self, data_length):

        self.i2c['m_pBuf'][0] |= 0x80
        self.i2c['m_pBuf'][3] = data_length

        # Reset the memory pointer and transfer the buffer.
        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)

        for i in range(self.i2c['m_nDataStart']):
            # print('WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
            self.xem.SetWireInValue(I2C_WIREIN_DATA, self.i2c['m_pBuf'][i], 0x00ff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_WRITE)

        # Start I2C transaction
        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_GO)

        # Wait for transaction to finish
        for _ in range(int(I2C_MAX_TIMEOUT_MS/10)):
            self.xem.UpdateTriggerOuts()
            if self.xem.IsTriggered(I2C_TRIGOUT, (1<<I2C_TRIGOUT_DONE)): # change to 1, LJK
                if WIRE_RESULTS:
                    # Read data: Reset the memory pointer
                    self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)
                    data = [None]*data_length
                    for i in range(data_length):
                        self.xem.UpdateWireOuts()
                        data[i] = self.xem.GetWireOutValue(I2C_WIREOUT_DATA)
                        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_READ)
                    return data
                if PIPE_RESULTS:
                    data_read = np.int(np.ceil(data_length*4/16)*16)
                    buf, e = self.read_pipe_out(0, data_read)
                    # reset FIFO
                    self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_READ)
                    return list(buf[0::4])[0:data_length]
            time.sleep(0.01)

        print('Timeout Excpetion in Rx')

    def i2c_write8(self, devAddr, regAddr, data_length, data):

        preamble = [devAddr & 0xfe, regAddr]
        self.i2c_configure(2, 0x00, 0x00, preamble)
        return self.i2c_transmit(data, data_length)

    def i2c_write_long(self, devAddr, regAddr, data_length, data):

        print('i2c write long')
        preamble = [devAddr & 0xfe] + regAddr + data
        self.i2c_configure(len(preamble), 0x00, 1<<len(preamble), preamble)
        return self.i2c_transmit(data, data_length)

    # Sequence is
    # [START] DEV_ADDR(W) REG_ADDR [START] DEV_ADDR(R) VALUE
    # LJK - this command does not execute OK API calls
    def i2c_read8(self, devAddr, regAddr, data_length):

        if regAddr is None: # for the pressure sensors that only need the slave address and a read bit and then send out 4 bytes.
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


    def reread_i2c(self, data_length):
        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)
        data = [None]*data_length
        for i in range(data_length):
            self.xem.UpdateWireOuts()
            data[i] = self.xem.GetWireOutValue(I2C_WIREOUT_DATA)
            self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_READ)
        return data

    def rep_rate(self, val):
        # off of the 48 MHz ok interface clock -- changed to 100 MHz system clock
        self.xem.SetWireInValue(I2C_REP_REG, val, 0xFFFFFFFF)
        self.xem.UpdateWireIns()

    def one_shot(self, yes_no = 1, CHAN = 0):
        if CHAN == 0:
            val = (yes_no << 2) + (1 << I2C_SHUF_CH0)
            mask = 0x0004 + (1<<I2C_SHUF_CH0)

        elif CHAN == 1:
            val = (yes_no << 2) + (1 << I2C_SHUF_CH1)
            mask = 0x0004 + (1<<I2C_SHUF_CH1)

        self.xem.SetWireInValue(I2C_CONFIG_REG, val, mask)
        self.xem.UpdateWireIns()

    def num_repeats(self, val):
        self.xem.SetWireInValue(I2C_CONFIG_REG, val << 16, 0xffff0000)
        self.xem.UpdateWireIns()

    def i2c_read_mult(self, num, devAddr, regAddr, data_length):
        self.one_shot(0)
        self.num_repeats(num-1)
        self.xem.UpdateWireIns()
        return self.i2c_receive_mult(num, devAddr, regAddr, data_length)

    def i2c_write_mult(self, num, devAddrs, regAddr, data_length, data):

        self.one_shot(0)
        self.num_repeats(num-1) # for two slave devices num should always be 2
        self.xem.UpdateWireIns()

        # HW time write to two different slaves

        for idx, devAddr in enumerate(devAddrs):
            preamble = [devAddr & 0xfe, regAddr]
            # signature: i2c_configure(data_length, starts, stops, preamble):
            self.i2c_configure(2, 0x00, 0x00, preamble)

            # copied from i2c.transmit
            self.i2c['m_pBuf'][3] = data_length
            for i in range(data_length):
                self.i2c['m_pBuf'].append(data[i])

            # setup the command buffer that we need
            if idx == 0:
                self.xem.SetWireInValue(I2C_CONFIG_REG, 1 << (I2C_SHUF_CH0), 1 << (I2C_SHUF_CH0))
                self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_CH1), 1 << (I2C_SHUF_CH1))
            elif idx == 1:
                self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_CH0), 1 << (I2C_SHUF_CH0))
                self.xem.SetWireInValue(I2C_CONFIG_REG, 1 << (I2C_SHUF_CH1), 1 << (I2C_SHUF_CH1))

            self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_ON), 1 << (I2C_SHUF_ON))
            self.xem.UpdateWireIns()

            # Reset the memory pointer and transfer the buffer.
            self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)
            for i in range(data_length + self.i2c['m_nDataStart']):
                # print('(transmit) WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
                self.xem.SetWireInValue(I2C_WIREIN_DATA, self.i2c['m_pBuf'][i], 0x00ff)
                self.xem.UpdateWireIns()
                self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_WRITE)

        for idx, devAddr in enumerate(devAddrs):
            self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_CH0+idx), 1 << (I2C_SHUF_CH0+idx))
            self.xem.UpdateWireIns()
        self.xem.SetWireInValue(I2C_CONFIG_REG, 1 << (I2C_SHUF_ON), 1 << (I2C_SHUF_ON))
        self.xem.UpdateWireIns()

        # Start I2C transaction
        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_GO)


    def i2c_receive_mult(self, num, devAddrs, regAddr, data_length):

        for idx, devAddr in enumerate(devAddrs):
            preamble = [devAddr & 0xfe, regAddr, devAddr | 0x01]

            # signature: i2c_configure(data_length, starts, stops, preamble):
            self.i2c_configure(3, 0x02, 0x00, preamble)
            self.i2c['m_pBuf'][0] |= 0x80
            self.i2c['m_pBuf'][3] = data_length

            # setup the command buffer that we need
            if idx == 0:
                self.xem.SetWireInValue(I2C_CONFIG_REG, 1 << (I2C_SHUF_CH0), 1 << (I2C_SHUF_CH0))
                self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_CH1), 1 << (I2C_SHUF_CH1))
            elif idx == 1:
                self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_CH0), 1 << (I2C_SHUF_CH0))
                self.xem.SetWireInValue(I2C_CONFIG_REG, 1 << (I2C_SHUF_CH1), 1 << (I2C_SHUF_CH1))

            self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_ON), 1 << (I2C_SHUF_ON))
            self.xem.UpdateWireIns()

            # Reset the memory pointer and transfer the buffer.
            self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)
            for i in range(self.i2c['m_nDataStart']):
                print('WireIn Value = {}'.format(self.i2c['m_pBuf'][i]))
                self.xem.SetWireInValue(I2C_WIREIN_DATA, self.i2c['m_pBuf'][i], 0x00ff)
                self.xem.UpdateWireIns()
                self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_WRITE)

        for idx, devAddr in enumerate(devAddrs):
            self.xem.SetWireInValue(I2C_CONFIG_REG, 0 << (I2C_SHUF_CH0+idx), 1 << (I2C_SHUF_CH0+idx))
            self.xem.UpdateWireIns()
        self.xem.SetWireInValue(I2C_CONFIG_REG, 1 << (I2C_SHUF_ON), 1 << (I2C_SHUF_ON))
        self.xem.UpdateWireIns()

        # Start I2C transaction
        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_GO)

        if WIRE_RESULTS:
            # Wait for num transaction to finish
            data_arr = []
            for n in range(num):
                if (n % 20) == 0:
                    print('read number {}'.format(n))
                for _ in range(int(I2C_MAX_TIMEOUT_MS/5)):
                    self.xem.UpdateTriggerOuts()
                    if self.xem.IsTriggered(I2C_TRIGOUT, (1<<I2C_TRIGOUT_DONE)): # change to 1, LJK
                        # Reset the memory pointer and then read data
                        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)
                        data = [None]*data_length
                        for i in range(data_length):
                            self.xem.UpdateWireOuts()
                            data[i] = self.xem.GetWireOutValue(I2C_WIREOUT_DATA)
                            self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_READ)
                        # print('got a read back')
                        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_RESET)
                        data_arr.append(data)
                        break
                    time.sleep(0.00001)
            return data_arr

        self.xem.UpdateTriggerOuts()
        if PIPE_RESULTS:
            half_fifo_depth = 2048
            # if num*data_length < 2048 don't need to check the FIFO half-full trigger
            if (num*data_length) <= half_fifo_depth:
                for _ in range(num*100):
                    self.xem.UpdateTriggerOuts()
                    if self.xem.IsTriggered(I2C_TRIGOUT, (1<<I2C_TRIGOUT_MULT_DONE)):
                        data_read = np.int(np.ceil(data_length*num*4/16)*16)
                        print('Will read {} bytes from pipes'.format(data_read))
                        buf, e = self.read_pipe_out(0, data_read)
                        print('Length of byte array {}'.format(len(buf)))
                        # reset FIFO
                        self.xem.ActivateTriggerIn(I2C_TRIGIN, I2C_TRIGIN_MEM_READ)
                        break
                    time.sleep(0.001)
                return np.reshape(list(buf[0::4]), (num, data_length))
            if (num*data_length) > half_fifo_depth:
                buf_t = bytearray()
                data_to_read = num*data_length
                for _ in range(num*100):
                    self.xem.UpdateTriggerOuts()
                    if self.xem.IsTriggered(I2C_TRIGOUT, (1<<I2C_TRIGOUT_FIFO_HALF)):
                        data_read = half_fifo_depth*4
                        print('FIFO half trigger. Data read {}'.format(data_read))
                        buf, e = self.read_pipe_out(0, data_read)
                        buf_t = buf_t + buf
                        data_to_read -= half_fifo_depth
                        # merge multiple buffers
                    if self.xem.IsTriggered(I2C_TRIGOUT, (1<<I2C_TRIGOUT_MULT_DONE)):
                        data_read = (data_to_read)*4 # get what's left
                        print('Mult done. Data read {}'.format(data_read))
                        buf, e = self.read_pipe_out(0, data_read)
                        buf_t = buf_t + buf
                        break
                    time.sleep(0.001)
                return np.reshape(list(buf_t[0::4]), (num, data_length))
