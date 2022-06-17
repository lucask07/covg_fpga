from ..interfaces import Endpoint
from ..utils import gen_mask
import copy


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
        'DDR_norepeat': 3,  # does not send an update if the DDR data is the same. Reduces digital switching noise on the SPI bus
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
            Endpoint.advance_endpoints(shared_chip_eps, number_of_chips)
        else:
            # Increment custom dictionary
            Endpoint.advance_endpoints(endpoints, number_of_chips)

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

        self.fpga.xem.WriteRegister(
            self.endpoints['REGBRIDGE_OFFSET'].bit_index_low, reg_value)

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
        self.fpga.xem.WriteRegister(
            self.endpoints['REGBRIDGE_OFFSET'].bit_index_low + 1, divide_value)

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
