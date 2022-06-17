from ..interfaces import Endpoint
from ..utils import gen_mask
from .ADCDATA import ADCDATA
import copy
import time

class AD7961(ADCDATA):
    """An interface to the AD7961 ADC
    Passed the FPGA object
    Allows for multiple channels
    read status flags (FIFO full, empty, count and PLL)
    configures FPGA internal resets
    configures chip specific and global enables
    Formats data returned from the wire out
    """
    # TODO: add Attributes to docstring

    # the AD7961 does not have internal registers -- just OK endpoints

    def __init__(self, fpga, endpoints=None):
        if endpoints is None:
            endpoints = Endpoint.get_chip_endpoints('AD7961')
        self.fpga = fpga
        self.endpoints = endpoints
        self.name = 'AD7961'
        self.num_bits = 16  # for AD7961 bits=18 for AD7960

    @staticmethod
    def create_chips(fpga, number_of_chips, endpoints=None):
        """Instantiate a given number of new chips.

        We increment the endpoints between each instantiation as well. The
        number must be greater than 0. If the endpoints argument is left
        as None, then we will use copies of the endpoints_from_defines
        dictionary for the endpoints for each instance, and update that
        original dictionary when we increment the endpoints. This way, the
        endpoints there are ready for another instantiation if needed.
        """

        if type(number_of_chips) is not int or number_of_chips <= 0:
            print('number_of_chips must be an integer greater than 0')
            return False

        if endpoints is None:
            endpoints = Endpoint.endpoints_from_defines.get('AD7961')

        chips = []
        for i in range(number_of_chips):
            # Use deepcopy here to keep the endpoints for different instances separate
            chips.append(AD7961(fpga=fpga, endpoints=copy.deepcopy(endpoints)))
            Endpoint.advance_endpoints(endpoints)
        return chips

    def get_status(self):
        """ Get AD796x status:
        pll lock, FIFO full, half-full, and empty

        Returns: dictionary of status
        """
        status = self.get_fifo_status()
        pll_lock = self.get_pll_status()
        status['pll_lock'] = pll_lock
        for k in status:
            print('{} status of {} = {}'.format(self.name,
                                                k, status[k]))
        return status

    def get_pll_status(self):
        """Get status of the phase locked loop."""

        return self.fpga.read_wire_bit(self.endpoints['PLL_LOCKED'].address,
                                       self.endpoints['PLL_LOCKED'].bit_index_low)

    def get_timing_pll_status(self):
        """Get status of the timing of the phase locked loop."""

        return self.fpga.read_wire_bit(self.endpoints['TIMING_PLL_LOCKED'].address,
                                       self.endpoints['TIMING_PLL_LOCKED'].bit_index_low)

    def get_fifo_status(self):
        """Get fullness status of the FIFO."""

        flags = ['FULL', 'HALFFULL', 'EMPTY']
        fifo_status = {}
        self.fpga.xem.UpdateTriggerOuts()
        for k in flags:
            fifo_status[k] = self.fpga.xem.IsTriggered(self.endpoints['FIFO_{}'.format(k)].address,
                                                       self.endpoints['FIFO_{}'.format(k)].bit_index_low)
        return fifo_status

    # Enable pins:
    # 0000 - power down
    # 1001 - enabled with ref buffer on; 28 MHZ
    # 0100 - test patterns on LVDS
    # 1101 - enabled with ref buffer on; 9 MHZ
    # Note that EN[3]=1 enables the VCM output buffer.

    def power_down_adc(self):
        """Power down single channel of the ADC.

        Fails if the global enables are 010 for LVDS test patterns
        """

        self.set_enables(0b0, global_enables=False)

    def test_pattern(self):
        """Enable PRBS test pattern on the LVDS interface."""

        self.set_enables(value=0b0100)

    def power_up_adc(self, bw='28M'):
        # TODO: add method docstring
        # TODO: explain what bw should be in docstring

        if bw == '28M':
            self.set_enables(0b1001)
        elif bw == '9M':
            self.set_enables(0b1101)
        else:
            print(f'incorrect input sampling bandwidth for {self.name}')

    def power_down_all(self):
        """Power down all channels of the ADC."""

        self.set_enables(0b0000)  # TODO: return anything here?

    def reset_pll(self):
        """Reset the phase locked loop."""

        return self.fpga.xem.ActivateTriggerIn(self.endpoints['PLL_RESET'].address,
                                               self.endpoints['PLL_RESET'].bit_index_low)

    def reset_trig(self):
        """Reset the FPGA controller for the ADC.
        
        Common to synchronize timing (resets ad7961_timing module AND the
        ads8686 timing) 
        """

        return self.fpga.xem.ActivateTriggerIn(self.endpoints['RESET'].address,
                                               self.endpoints['RESET'].bit_index_low)

    def reset_wire(self, value):
        """Set the value of the wire to reset the FPGA controller for the ADC.

        Uses the Opal Kelly WireIn (the trigger can't hold the reset).

        Parameters
        -----------
        value : int
            value = 1 is reset
            value = 0 releases reset
        """

        if value == 1:
            self.fpga.set_wire_bit(self.endpoints['WIRE_RESET'].address,
                                   self.endpoints['WIRE_RESET'].bit_index_low)
        if value == 0:
            self.fpga.clear_wire_bit(self.endpoints['WIRE_RESET'].address,
                                     self.endpoints['WIRE_RESET'].bit_index_low)

    def power_down_fpga(self):
        """Power down the FPGA controller through WireIn."""

        # TODO: add functionality (wirein bit) to the FPGA
        #       this would reduce FPGA power consumption
        self.reset_wire(0)

    def set_enables(self, value=0b0000, global_enables=True):
        """Set the EN0 specific to this channel (LSB in values).

        Optionally also modify the global enables (all channels).
        """

        mask = gen_mask(self.endpoints['ENABLE'].bit_index_low)
        if global_enables:
            # global enables (connect to all AD7961); create a list of bit position
            gl_mask = [x+self.endpoints['GLOBAL_ENABLE'].bit_index_low
                       for x in range(self.endpoints['GLOBAL_ENABLE_LEN'].bit_index_low)]
            # or global mask with the signal channel EN0 mask
            mask = gen_mask(gl_mask) | mask

        # setup the values
        value_chan = (value & 0b0001) << (
            self.endpoints['ENABLE'].bit_index_low)
        if global_enables:
            #  globabl enables are the 3 MSBs
            val_global = (value & 0b1110) << (
                self.endpoints['GLOBAL_ENABLE'].bit_index_low - 1)
            # minus 1 since already left shifted by 1
            print('Global value = 0x{:0x}'.format(val_global))
            value = value_chan | val_global

        print('Enables setting value = 0x{:0x} with mask = = 0x{:0x}'.format(
            value, mask))
        self.fpga.set_wire(self.endpoints['ENABLE'].address, value, mask=mask)

    def setup(self, reset_pll=False):
        """
        0) put ADC controller into reset
        1) optionally reset the ADC PLL and wait for lock
            (only need to reset PLL on first channel)
        2) power up adc
        3) release ADC controller reset
        4) reset fifo
        5) check and return status (PLL and fifo)
        """
        self.reset_wire(1)
        if reset_pll:
            # reset PLL
            self.reset_pll()
            pll_cnt = 0
            while not self.get_pll_status():
                time.sleep(0.01)
                pll_cnt += 1
                if pll_cnt > 20:
                    print('PLL lock timeout')
                    return -1
        # enable ADC
        self.power_up_adc()
        # now that PLL is locked and ADC is ready
        # release the reset of the ADC controller
        # self.reset_trig()
        self.reset_wire(0)  # releases the reset
        # reset FIFO
        self.reset_fifo()
        status = self.get_status()
        # TODO: the FIFO is guaranteed to overflow
        return status
