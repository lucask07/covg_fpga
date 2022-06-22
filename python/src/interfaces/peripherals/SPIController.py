from ..interfaces import Endpoint, Register
import copy


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
                Endpoint.advance_endpoints(endpoints)
        else:
            for i in range(number_of_chips):
                chips.append(cls(fpga=fpga, endpoints=copy.deepcopy(
                    endpoints), master_config=master_config))
                # Use deepcopy to keep the endpoints for different instances separate
                endpoints = copy.deepcopy(chips[-1].endpoints)
                Endpoint.advance_endpoints(endpoints)

        if endpoints is None:
            # Increment shared endpoints dictionary
            # We need to get the shared endpoints in endpoints_from_defines to
            # increment and we only have the endpoints given to us in the
            # argument.
            shared_full_eps = Endpoint.endpoints_from_defines
            shared_chip_eps = shared_full_eps[
                list(shared_full_eps.keys())[
                    list(shared_full_eps.values()).index(chips[0].endpoints)
                ]
            ]
            Endpoint.advance_endpoints(shared_chip_eps, number_of_chips)
        else:
            # Increment custom dictionary
            Endpoint.advance_endpoints(endpoints, number_of_chips)

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
        """Set the Wishbone's CTRL register using several parameters.

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
