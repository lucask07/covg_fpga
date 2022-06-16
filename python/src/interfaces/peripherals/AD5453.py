from SPIFifoDriven import SPIFifoDriven


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
