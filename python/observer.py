import numpy as np
from pyripherals.utils import to_voltage, from_voltage, create_filter_coefficients, gen_mask
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3

# Class for Luenberger Observer
class Observer():
    """Class for Luenberger Observer on the FPGA

    Attributes
    ----------
    default_im_data_mux : dict
        Class attribute. Default im_data_mux dictionary.
    default_vcmd_mux : dict
        Class attribute. Default vcmd_data_mux dictionary.
    default_vp1_data_mux : dict
        Class attribute. Default vp1_data_mux dictionary.
    fpga : FPGA
        FPGA instance this controller uses to communicate.
    endpoints : dict
        Endpoints on the FPGA this controller uses to communicate.
    master_config : int
        Value of the CTRL register in the Wishbone.
    im_data_mux: dict
        Name to select value dictionary for source data MUX.
    vcmd_data_mux: dict
        Name to select value dictionary for source data MUX.
    vp1_data_mux: dict
        Name to select value dictionary for source data MUX.
    current_im_data_mux : str
        Name of the current MUX data source.
    current_vcmd_data_mux : str
        Name of the current MUX data source.
    current_vp1_data_mux : str
        Name of the current MUX data source.
    
    """

    default_im_data_mux = {
        'ad7961_ch0': 0,
        'ad7961_ch1': 1,
        'ad7961_ch2': 2,
        'ad7961_ch3': 3,
    }

    default_vcmd_data_mux = {
        'ad5453_ch0': 0,
        'ad5453_ch1': 1,
        'ad5453_ch2': 2,
        'ad5453_ch3': 3,
        'ad5453_ch4': 4,
        'ad5453_ch5': 5,
    }

    default_vp1_data_mux = {
        'ads8686_chA': 0,
        'ads8686_chB': 1,
    }

    default_rdy_data_mux = {
        'sync_im': 0,
        'sync_vp1': 1,
        'sync_vcmd': 2,
    }

    def __init__(self, fpga, endpoints=None, im_data_mux=default_im_data_mux, 
    vcmd_data_mux=default_vcmd_data_mux, vp1_data_mux=default_vp1_data_mux, rdy_data_mux=default_rdy_data_mux):

        self.fpga = fpga
        if endpoints is None:
            self.endpoints = Endpoint.get_chip_endpoints('OBSV')
        #self.endpoints = endpoints
        self.im_data_mux = im_data_mux
        self.vcmd_data_mux = vcmd_data_mux
        self.vp1_data_mux = vp1_data_mux
        self.rdy_data_mux = rdy_data_mux
        # Start with ad7961_ch0 to minimize unintentional commands from other sources on startup
        self.current_im_data_mux = None
        if self.set_im_data_mux('ad7961_ch0') == -1:
            # 'ad7961_ch0' was not in data_mux dict
            print("WARNING: no 'ad7961_ch0' in data_mux dict")
        # Start with ad5453_ch0 to minimize unintentional commands from other sources on startup
        self.current_vcmd_data_mux = None
        if self.set_vcmd_data_mux('ad5453_ch0') == -1:
            # 'ad5453_ch0' was not in data_mux dict
            print("WARNING: no 'ad5453_ch0' in data_mux dict")
        # Start with ads8686_chA to minimize unintentional commands from other sources on startup
        self.current_vp1_data_mux = None
        if self.set_vp1_data_mux('ads8686_chA') == -1:
            # 'ads8686_chA' was not in data_mux dict
            print("WARNING: no 'ads8686_chA' in data_mux dict")

        # Observer coefficients
        self.observer_offset = 0
        self.observer_coeff = {0:0x00000000,
                               1:0x00000000,
                               2:0x00000000,
                               3:0x00000000,
                               4:0x00000000,
                               5:0x00000000,
                               6:0x00000000,
                               7:0x00000000,
                               8:0x00000000,
                               9:0x00000000}
        self.observer_len = np.max(
            list(self.observer_coeff.keys())) - np.min(list(self.observer_coeff.keys()))
    
    def set_im_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.im_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'IM_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.im_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_im_data_mux = source
    
    def set_vcmd_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.vcmd_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'VCMD_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.vcmd_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_vcmd_data_mux = source

    def set_vp1_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.vp1_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'VP1_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.vp1_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_vp1_data_mux = source

    def set_rdy_data_mux(self, source):
        """Configure the MUX that routes data source to the SPI output.

        Parameters
        ----------
        source : str
            See SPIFifoDriven.data_mux dict for options and conversion.
        """

        select_val = self.rdy_data_mux.get(source)
        if select_val is None:
            print(f'Set data mux failed, {source} not available')
            return -1

        endpoint = 'RDY_DATA_SEL'

        mask = gen_mask(range(self.endpoints[endpoint].bit_index_low,
                              self.endpoints[endpoint].bit_index_high))
        data = (self.rdy_data_mux[source]
                << self.endpoints[endpoint].bit_index_low)
        self.fpga.set_wire(self.endpoints[endpoint].address, data,
                           mask=mask)
        self.current_rdy_data_mux = source

    def write_observer_coeffs(self):
        # TODO: add method docstring

        # TODO is this correct? and how to parameterize?
        for i in np.arange(self.observer_offset, 1 + self.observer_offset + self.observer_len):
            if (i-self.observer_offset) in self.observer_coeff:
                addr = int(
                    self.endpoints['REGBRIDGE_OFFSET'].address + i)
                val = int(self.observer_coeff[i-self.observer_offset])
                print(
                    'Write filter addr=0x{:02X}  value=0x{:02X}'.format(addr, val))
                self.fpga.xem.WriteRegister(addr, val)

    def change_observer_coeff(self, value=None):
        self.observer_coeff = value
        self.observer_len = np.max(
            list(self.observer_coeff.keys())) - np.min(list(self.observer_coeff.keys()))
