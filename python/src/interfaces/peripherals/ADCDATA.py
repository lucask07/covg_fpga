from ..interfaces import Endpoint
from ..utils import twos_comp
import numpy as np
import time


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
        print('ADC stream multiple')
        cnt = 0
        st = bytearray(np.asarray(np.ones(0, np.uint8)))
        self.fpga.xem.UpdateTriggerOuts()

        start_time = time.time()
        timeout_time = 1*swps  # seconds
        timeout_flg = (time.time() < (start_time + timeout_time))

        while ((cnt < swps) and timeout_flg):
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
            timeout_flg = (time.time() < (start_time + timeout_time))
        if not timeout_flg:
            print('ADC stream_mult timed out')
            return -1
        if twos_comp_conv:
            data = self.convert_data(st)
        else:
            data = self.deswizzle(st)
        return data
