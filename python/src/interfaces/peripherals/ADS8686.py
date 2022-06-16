from SPIController import SPIController
from ADCDATA import ADCDATA

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
