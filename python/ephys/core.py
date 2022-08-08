"""Classes for electrophysiology.

Abe Stroschein, ajstroschein@stthomas.edu
"""

from typing import List
import os
import sys
import copy
import time
import numpy as np
import matplotlib.pyplot as plt
import atexit
import h5py
from pyripherals.core import FPGA, Endpoint
from pyripherals.utils import to_voltage, from_voltage, read_h5
from pyripherals.peripherals.DDR3 import DDR3

# The boards.py file and instruments folder are located in the covg_fpga/python folder. If covg_fpga is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == "covg_fpga":
        boards_path = os.path.join(covg_fpga_path, "python")
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(boards_path)

from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from analysis.adc_data import separate_ads_sequence
from boards import Daq, Clamp
from filters.filter_tools import butter_lowpass_filter

# Constants
FS = 5e6
ADS_FS = 1e6

# Variables
f = FPGA()
f.init_device()
ddr = DDR3(fpga=f)
f.xem.Close()

# Classes

class Epoch:
    """One division of time in a CMD signal.
    
    Attributes
    ----------
    first_level : int
        The first voltage in mV.
    delta_level : int
        How much to add to first_level in mV each time the Sweep containing this Epoch is repeated in a Protocol.
    first_duration : int
        The first time duration in ms.
    delta_level : int
        How much to add to first_duration in ms each time the Sweep containing this Epoch is repeated in a Protocol.
    type : str
        How to change the voltage during the Epoch.
    sample_rate : str
        ???
    """

    def __init__(self, first_level, delta_level, first_duration, delta_duration, type='Step', sample_rate='Fast'):
        self.first_level = first_level
        self.delta_level = delta_level
        self.first_duration = first_duration
        self.delta_duration = delta_duration
        self.type = type
        self.sample_rate = sample_rate

    def __len__(self):
        """Return the length of the Epoch data np.ndarray of np.uint16
        
        Returns
        -------
        len : int
            Length of the Epoch data np.ndarray of np.uint16.
        """

        return int(np.ceil(self.first_duration * 1e-3 / ddr.parameters['update_period']))

    def data(self):
        """Create and return the data for the Epoch.
        
        Returns
        -------
        data : np.ndarray
            The voltage data points for the Epoch in mV.
        """

        data = self.first_level * np.ones(shape=len(self), dtype=float)
        return data

    def duration(self):
        """Calculate the actual duration of the Epoch.
        
        We will aim for first_duration, but the actual duration may change slightly due to DDR constraints.
        
        Returns
        -------
        duration : float
            The actual duration of the Epoch in ms.
        """

        duration = int(np.ceil(self.first_duration * 1e-3 / ddr.parameters['update_period'])) * ddr.parameters["update_period"] * 1e3
        return duration


class Sweep:
    """One set of Epochs. Can be repeated in a Protocol.
    
    Attributes
    ----------
    epochs : List[Epoch]
        The Epochs to include in the Sweep.
    duration : float
        The duration of the Sweep in ms.
    """

    MAX_TIME = ddr.parameters['sample_size'] * ddr.parameters['update_period']

    def __init__(self, epochs: List[Epoch]):
        self.epochs = epochs

    def __len__(self):
        """Return the length of the Sweep data np.ndarray of np.uint16
        
        Returns
        -------
        len : int
            Length of the Sweep data np.ndarray of np.uint16.
        """

        return sum([len(e) for e in self.epochs])

    def data(self):
        """Create and return the data for the Sweep.
        
        Returns
        -------
        data : np.ndarray
            The voltage data points for the Sweep in mV.
        """

        data = np.concatenate([e.data() for e in self.epochs])
        if len(data) > ddr.parameters['sample_size']:
            print(f'WARNING: Sweep data too long for DDR. {len(data) * ddr.parameters["update_period"] * 1e3} ms > max {Sweep.MAX_TIME * 1e3} ms')
        return data

    def duration(self):
        """Calculate the actual duration of the Sweep.

        Calculated as sum of durations of Epochs.
        
        Returns
        -------
        duration : float
            The actual duration of the Sweep in ms.
        """
        duration = sum([e.duration() for e in self.epochs])
        return duration


class Protocol:
    """One CMD signal to send out.
    
    Attributes
    ----------
    sweep : Sweep
        The first sweep to repeat throughout the Protocol.
    num_sweeps : int
        How many sweeps to repeat.
    duration : float
        The duration of the Protocol in ms.
    """

    MAX_TIME = ddr.parameters['sample_size'] * ddr.parameters['update_period']

    def __init__(self, sweep: Sweep, num_sweeps):
        self.sweeps = [sweep]
        for i in range(1, num_sweeps):
            next_sweep = copy.deepcopy(sweep)
            for j in range(len(next_sweep.epochs)):
                epoch = next_sweep.epochs[j]
                epoch.first_level = self.sweeps[i - 1].epochs[j].first_level + epoch.delta_level
                epoch.first_duration = self.sweeps[i - 1].epochs[j].first_duration + epoch.delta_duration
                next_sweep.epochs[j] = epoch
            self.sweeps.append(next_sweep)

    def __len__(self):
        """Return the length of the Protocol data np.ndarray of np.uint16
        
        Returns
        -------
        len : int
            Length of the Protocol data np.ndarray of np.uint16.
        """

        return sum([len(s) for s in self.sweeps])

    def data(self):
        """Create and return the data for the Protocol.
        
        Returns
        -------
        data : np.ndarray
            The voltage data for the Protocol in mV.
        """

        data = np.concatenate([s.data() for s in self.sweeps])
        if len(data) > ddr.parameters['sample_size']:
            print(f'WARNING: Protocol data too long for DDR. {len(data) * ddr.parameters["update_period"] * 1e3} ms > max {Protocol.MAX_TIME * 1e3} ms')
        return data

    def duration(self):
        """Calculate the actual duration of the Protocol.
        
        Calculated from the sum of durations of each Sweep.

        Returns
        -------
        duration : float
            The actual duration of the Protocol in ms.
        """

        duration = sum([s.duration() for s in self.sweeps])
        return duration

    def preview(self):
        """Plot a preview of the Protocol with different sweeps stacked on top of one another.

        To show the plot, use matplotlib.pyplot.show.
        
        Returns
        -------
        ax : matplotlib.axes._subplots.AxesSubplot
        """

        fig, ax = plt.subplots()
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Voltage (mV)')
        ax.set_title('Protocol Preview')
        for i in range(len(self.sweeps)):
            data = self.sweeps[i].data()
            if i == 0:
                # final_t = len(data) * ddr.parameters["update_period"] * 1e3   # Final time in milliseconds
                # t = np.arange(0, final_t, ddr.parameters["update_period"] * 1e3)
                t = np.linspace(0, len(data) - 1, len(data)) * ddr.parameters['update_period'] * 1e3
            ax.plot(t, data, label=i)
        ax.legend()
        return ax

    @staticmethod
    def create_from_csv(filepath, num_sweeps):
        """Create a Protocol from a CSV.
        
        Parameters
        ----------
        filepath : str, path object or file-like object
            The path to the CSV.
        num_sweeps : int
            The number of sweeps to include.
        
        Returns
        -------
        protocol : Protocol
            The Protocol generated from the CSV with the given number of sweeps.
        """

        import pandas as pd

        df = pd.read_csv(filepath_or_buffer=filepath)
        df = df.iloc[:, 1:]    # Skip labels column
        df.fillna(0)

        epochs = []
        for col in df:
            column = df[col]
            type, sample_rate, first_level, delta_level, first_duration, delta_duration = column
            if type == 'Off':
                # No entry, skip
                continue

            e = Epoch(first_level=int(first_level), delta_level=int(delta_level), first_duration=int(first_duration),
                    delta_duration=int(delta_duration), type=type.capitalize(), sample_rate=sample_rate.capitalize())
            epochs.append(e)
        sweep = Sweep(epochs=epochs)
        protocol = Protocol(sweep=sweep, num_sweeps=num_sweeps)
        return protocol


class Sequence:
    """A sequence of Protocols.
    
    Attributes
    ----------
    protocols : List[Protocol]
        List of all contained Protocols.
    """

    MAX_TIME = ddr.parameters['sample_size'] * ddr.parameters['update_period']

    def __init__(self, protocols: Protocol or List[Protocol]):
        if type(protocols) is Protocol:
            self.protocols = [protocols]
        else:
            self.protocols = protocols

    def __len__(self):
        """Return the length of the Sequence data np.ndarray of np.uint16
        
        Returns
        -------
        len : int
            Length of the Sequence data np.ndarray of np.uint16.
        """

        return sum([len(p) for p in self.protocols])

    def data(self):
        """Create and return the data for the Sequence.
        
        Returns
        -------
        data : np.ndarray
            The voltage data for the Sequence in mV.
        """

        data = np.concatenate([p.data() for p in self.protocols])
        if len(data) > ddr.parameters['sample_size']:
            print(f'WARNING: Sequence data too long for DDR. {len(data) * ddr.parameters["update_period"] * 1e3} ms > max {Sequence.MAX_TIME * 1e3} ms')
        return data

    def duration(self):
        """Calculate the actual duration of the Sequence.
        
        Calculated from the sum of the durations of each Protocol.

        Returns
        -------
        duration : float
            The actual duration of the Sequence in ms.
        """

        return sum([p.duration() for p in self.protocols])


class Experiment:
    """Holds all objects needed for an Experiment.
    
    Attributes
    ----------
    endpoints : Dict[str, Endpoint]
        All Endpoints used in the experiment.
    fpga : FPGA
        The FPGA instance connected to the Daq board.
    daq : Daq
        The Daq instance conneced to the Clamp boards.
    clamps : List[Clamp]
        List of Clamp instances available on the Daq board. These can be connected to cells.
    gpio : Daq.GPIO
        GPIO pins on Daq board.
    pwr : Daq.POWER
        Power for Daq board.
    dc_pwr : ???
        The power supply instances powering the Daq board.
    sequence : Sequence
        The Sequence to be run in this Experiment.
    """

    def __init__(self, sequence: Sequence or Protocol):

        # Initialize FPGA
        self.endpoints = Endpoint.update_endpoints_from_defines()
        self.fpga = FPGA()
        # TODO: is there any way we can wait to fpga.init_device() until setup?
        self.fpga.init_device()
        self.daq = Daq(self.fpga)
        self.daq.ddr.parameters['data_version'] = 'TIMESTAMPS'
        self.clamps = [Clamp(fpga=self.fpga, dc_num=dc_num) for dc_num in range(4)]
        self.gpio = Daq.GPIO(self.fpga)
        self.pwr = Daq.Power(self.fpga)
        self.pwr.all_off()  # disable all power enables
        self.dc_pwr = []
        if type(sequence) is Protocol:
            self.sequence = Sequence(protocols=sequence)
        else:
            self.sequence = sequence

    def setup(self):
        """Setup necessary for reading and writing data with a connection to a model cell."""

        dac_offset = 0x1E00

        # TODO: either get this from the first Protocol in the Sequence, or
        # as an Experiment attribute
        # Epoch first_level given in mV, convert to V
        holding_voltage = self.sequence.protocols[0].sweeps[0].epochs[0].first_level * 1e-3

        # Set up power supplies
        pwr_setup = "3dual"
        self.dc_pwr = open_rigol_supply(setup=pwr_setup)
        if pwr_setup == "3dual":
            atexit.register(pwr_off, [self.dc_pwr[0]])
        else:
            atexit.register(pwr_off, [self.dc_pwr])
        config_supply(self.dc_pwr[0], self.dc_pwr[1], setup=pwr_setup, neg=15)

        # Turn on power supplies
        self.dc_pwr[0].set("out_state", "ON", configs={"chan": 1})  # turn on the 7V
        if pwr_setup != "3dual":
            # turn on the +/-16.5 V input
            for ch in [1, 2]:
                self.dc_pwr[1].set("out_state", "ON", configs={"chan": ch})
        elif pwr_setup == "3dual":
            # turn on the +/-16.5 V input
            for ch in [2, 3]:
                self.dc_pwr[0].set("out_state", "ON", configs={"chan": ch})

        # Initialize the FPGA
        # f.init_device()   # Currently being done in __init__
        time.sleep(2)
        f.send_trig(self.endpoints["GP"]["SYSTEM_RESET"])  # system reset
        self.daq.ADC[0].reset_wire(1)    # Only actually one WIRE_RESET for all AD7961s

        # power supply turn on via FPGA enables
        for name in ["1V8", "5V", "3V3"]:
            self.pwr.supply_on(name)
            time.sleep(0.05)

        # configure the SPI debug MUXs
        self.gpio.spi_debug("dfast1")
        self.gpio.ads_misc("sdoa")  # do not care for this experiment

        # instantiate the Clamp board providing a daughter card number (from 0 to 3)
        for dc_num in range(len(self.clamps)):
            print(f'Clamp {dc_num} Init'.center(35, '-'))
            self.clamps[dc_num].init_board()
            self.clamps[dc_num].DAC.write(data=from_voltage(voltage=0.9940/1.6662,
                            num_bits=10, voltage_range=5, with_negatives=False))


        # -------- configure the ADS8686
        ads_voltage_range = 5  # need this for to_voltage later 
        self.daq.ADC_gp.hw_reset(val=False)
        self.daq.ADC_gp.set_host_mode()
        self.daq.ADC_gp.setup()
        self.daq.ADC_gp.set_range(ads_voltage_range) # TODO: make an self.daq.ADC_gp.current_voltage_range a property of the ADS so we always know it
        self.daq.ADC_gp.set_lpf(376)
        ads_sequencer_setup = [('1', '1'), ('2', '2')]
        codes = self.daq.ADC_gp.setup_sequencer(chan_list=ads_sequencer_setup)
        self.daq.ADC_gp.write_reg_bridge(clk_div=200) # 1 MSPS rate (do not use default value of 1000 which is 200 ksps)
        self.daq.ADC_gp.set_fpga_mode()

        # TODO: are the TCA pins already configured in Clamp.configure_clamp()?
        self.daq.TCA[0].configure_pins([0, 0])
        self.daq.TCA[1].configure_pins([0, 0])

        # fast DAC channels setup
        for i in range(6):
            self.daq.DAC[i].set_ctrl_reg(self.daq.DAC[i].master_config)
            self.daq.DAC[i].set_spi_sclk_divide()
            self.daq.DAC[i].filter_select(operation="clear")
            self.daq.DAC[i].write(from_voltage(voltage=holding_voltage, num_bits=14, voltage_range=5, with_negatives=True) + dac_offset)
            # self.daq.DAC[i].set_data_mux("DDR")
            self.daq.DAC[i].change_filter_coeff(target="passthru")
            self.daq.DAC[i].write_filter_coeffs()
            self.daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

        # --------  Enable fast ADCs  --------
        for chan in [0, 1, 2, 3]:
            self.daq.ADC[chan].power_up_adc()  # standard sampling
        self.daq.ADC[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
        self.daq.ADC[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset

    def close(self):
        """Close opened devices from setup."""

        self.pwr.all_off()
        pwr_off([pwr for pwr in self.dc_pwr if pwr is not None])
        self.fpga.xem.Close()

    def write_sequence(self, clamp_num, inject_current=False, low_scaling_factor=0, cutoff=-10, high_scaling_factor=1/7):
        """Write the Sequence for this Experiment. 
        
        Write to the CMD channel of the specified Clamp board with the option
        to write a corresponding injected current to pins 16, 18 of J11 on the
        DAQ board.
        
        Parameters
        ----------
        clamp_num : int or List[int]
            Which Clamp to write to (0, 1, 2, or 3).
        inject_current : bool
            Whether to include a corresponding injected current.
        low_scaling_factor : float
            The scaling factor (uA/mV) for current when the CMD voltage is
            less than the cutoff.
            current = voltage * low_scaling_factor  * 1e3.
        cutoff : float
            The voltage in millivolts at which to switch from the
            low_scaling_factor to the high_scaling_factor for the injected
            current.
        high_scaling_factor : float
            The scaling factor (uA/mV) for current when the CMD voltage is
            greater than or equal to the cutoff.
            current = voltage * high_scaling_factor  * 1e3.

        Returns
        -------
        sequence_len : int
            Length of the Sequence data np.ndarray of np.uint16.
        """

        if type(clamp_num) is int:
            clamp_nums = [clamp_num]
        elif type(clamp_num) is list:
            clamp_nums = clamp_num
        else:
            raise TypeError('write_sequence parameter clamp_num must be int or list of ints.')

        # Offset adjust gain k is multiply by 3k/feedback resistor. To counteract this we multiply by feedback resistor/3k
        fb_res = 2.1
        offset_adjust_k = 1 + fb_res / 3    # fb_res is already in kOhms, so 3 instead of 3e3
        dac_offset = 0x1E00
        target_len = len(self.daq.ddr.data_arrays[0])

        # Create data
        # Multiply data by 1e-3 because sequence data is given in mV, need in V for from_voltage conversion
        sequence_data = self.sequence.data() * 1e-3
        sequence_len = len(sequence_data)
        for clamp_num in clamp_nums:
            cmd_ch = clamp_num * 2 + 1
            cc_ch = clamp_num * 2

            # In addition to the offset adjust amplifier, the CMD signal is
            # attennuated 10x from the DAQ board to the daughtercard so we
            # have to multiply our signal by 10 to get it back to what we want
            cmd_voltage = sequence_data * offset_adjust_k * 10
            # Pad with zeros to make correct size
            cmd_voltage = np.pad(cmd_voltage, (0, target_len - len(cmd_voltage)), 'constant', constant_values=0)
            # TODO: determine voltage_range for AD5453
            cmd_signal = np.array(from_voltage(voltage=cmd_voltage, num_bits=14, voltage_range=5, with_negatives=True), dtype=np.uint16) + dac_offset
            cc_signal = np.ones(len(cmd_signal), dtype=np.uint16) * dac_offset
            self.daq.ddr.data_arrays[cmd_ch] = cmd_signal
            self.daq.ddr.data_arrays[cc_ch] = cc_signal

        # Create injected current data
        if inject_current:
            # sequence_data in V, cutoff in mV, scaling factors in uA/mv, current needs to be in nA
            current = np.where(
                sequence_data < cutoff * 1e-3,
                sequence_data * 1e3 * low_scaling_factor * 1e3,
                sequence_data * 1e3 * high_scaling_factor * 1e3
            )
            self.inject_current(current=current, write_ddr=False)

        # Write channels to the DDR
        self.daq.ddr.write_setup()
        block_pipe_return, speed_MBs = self.daq.ddr.write_channels(set_ddr_read=False)
        for i in range(6):
            self.daq.DAC[i].set_data_mux("DDR")
        time.sleep(0.2) # Let Vm stabalize
        self.daq.ddr.reset_mig_interface()
        self.daq.ddr.write_finish()

        return sequence_len

    def inject_current(self, current, write_ddr=False):
        """Write current data to a DAC80508 controlling a current pump.

        This function expects that the Experiment has already been setup with
        Experiment.setup(). The current will be written to DAC2_CAL0 and
        DAC2_CAL1 (Pins 16 and 18 on J11 on the DAQ board).
        
        Parameters
        ----------
        current : np.ndarray
            The current data in nanoamps (nA).
        write_ddr : bool
            Whether to write to the DDR after creating the data. If False, the
            data will still be in the ddr.data_arrays variable and will be
            written next time the DDR is written.
        """

        # DAC80508 output to bipolar amplifier to Howland current pump
        # Bipolar Amplifier: OUT = 3*IN – 3/2*VREF
        # Howland Current Pump: IOUT = VIN/4.7e6
        # DAC gain of x1 makes bipolar output symmetric about zero
        v_ref = 2.5
        max_current = ((3*2.5 - (3/2)*(v_ref)) / 4.7e6)
        min_current = ((3*0 - (3/2)*(v_ref)) / 4.7e6)
        current_range = max_current - min_current
        lsb_range = 0xffff - 0x0000
        amps_per_lsb = current_range / (lsb_range + 1)
        def amps_to_lsb(amp_data, limit=True):
            if type(amp_data) is np.ndarray:
                lsb_data = ((amp_data - min_current) / amps_per_lsb).astype(int)
                if limit:
                    # Limit values to [0x0000, 0xFFFF] range
                    lsb_data = np.where(lsb_data > 0xFFFF, 0xFFFF, lsb_data)
                    lsb_data = np.where(lsb_data < 0x0000, 0x0000, lsb_data)
            elif type(amp_data) is float or type(amp_data) is int:
                lsb_data = int((amp_data - min_current) / amps_per_lsb)
                if limit:
                    if lsb_data > 0xFFFF:
                        lsb_data = 0xFFFF
                    elif lsb_data < 0x0000:
                        lsb_data = 0x0000
            else:
                raise TypeError(f'amps_to_lsb expected amp_data of type np.ndarray or float or int. Got {type(amp_data)}.')
            return lsb_data
            
        sdac_1_out_chan = 7  # Do not care for this experiment -- able to connect DAC1_OUT7 to the scope. Have voltage mirror current
        sdac_2_out_chan = 0  # Howland current source -- connecting to DAC2_CAL0

        for i in range(2):
            # self.daq.set_isel(port=i+1, channels=None)
            # Reset the Wishbone controller and SPI core
            self.daq.DAC_gp[i].set_ctrl_reg(self.daq.DAC_gp[i].master_config)
            self.daq.DAC_gp[i].set_spi_sclk_divide()
            self.daq.DAC_gp[i].filter_select(operation="clear")
            self.daq.DAC_gp[i].set_data_mux("host")
            self.daq.DAC_gp[i].set_config_bin(0x00)
            print('Outputs powered on')

        # Use DAC2_CAL0 as a current source driven by the DDR
        # DAC2_CAL1 is available as a repeat of the same current.
        self.daq.set_isel(port=2, channels=[0, 1])
        # -3.5 V to 3.5 V out from the bipolar amplifier with gain of x1. ~ [-0.8, 0.8] uA
        # Howland current pump gain is Vin*1/4.7e6
        self.daq.DAC_gp[1].set_gain(1, outputs=[0, 1])

        self.daq.DAC_gp[0].set_data_mux("DDR")
        self.daq.DAC_gp[1].set_data_mux("DDR")

        # Clear channel bits
        for i in range(4):
            self.daq.ddr.data_arrays[i] = np.bitwise_and(self.daq.ddr.data_arrays[i], 0x3fff)
        
        # Set channel bits for the General purpose DAC
        self.daq.ddr.data_arrays[0] = np.bitwise_or(self.daq.ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
        self.daq.ddr.data_arrays[1] = np.bitwise_or(self.daq.ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
        self.daq.ddr.data_arrays[2] = np.bitwise_or(self.daq.ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
        self.daq.ddr.data_arrays[3] = np.bitwise_or(self.daq.ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

        # Set current data with offset
        target_len = len(self.daq.ddr.data_arrays[6])
        # For current output to be bidirectional, our range gets shifted down
        # to the halfway point being zero. Add half to everything before
        # converting so we use the right binary codes.
        # Add half scale nA to split our [-0.8, 0.8] uA == [-800, 800] nA range
        current_data = amps_to_lsb(current * 1e-9)  # Current given in nA, convert to A before converting to binary
        offset = 0x8000
        self.daq.ddr.data_arrays[6] = np.pad(current_data, (0, target_len - len(current_data)), mode='constant', constant_values=offset)
        self.daq.ddr.data_arrays[7] = self.daq.ddr.data_arrays[6]

        if write_ddr:
            # Write channels to the DDR
            self.daq.ddr.write_setup()
            block_pipe_return, speed_MBs = self.daq.ddr.write_channels(set_ddr_read=False)
            self.daq.ddr.reset_mig_interface()
            self.daq.ddr.write_finish()
            for i in range(6):
                self.daq.DAC[i].set_data_mux("DDR")

    def read_response(self, clamp_num):
        """Return the incoming data from the Daq board.

        Read the full sequence with one call to DDR3.save_data.
        
        Parameters
        ----------
        clamp_num : int or List[int]
            Which Clamp to write to (0, 1, 2, or 3).
        
        Returns
        -------
        time, data : np.ndarray, np.ndarray
            Time and Voltage data in ms and mV.
        """

        if type(clamp_num) is int:
            clamp_nums = [clamp_num]
        elif type(clamp_num) is list:
            clamp_nums = clamp_num
        else:
            raise TypeError('write_sequence parameter clamp_num must be int or list of ints.')

        data_dir = os.path.join(os.path.expanduser('~'), 'ephys_data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        file_name = time.strftime("%Y%m%d-%H%M%S.h5")

        # Get data
        # num_repeats=8 gets a 8.19000000000051 ms timestamp span. Adjust to get full sequence reading.
        num_repeats = np.ceil(self.sequence.duration() / 8.191 * 8)
        # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
        chan_data_one_repeat = self.daq.ddr.save_data(data_dir, file_name, num_repeats=num_repeats,
                                            blk_multiples=40)  # blk multiples multiple of 10

        # to get the deswizzled data of all repeats need to read the file
        _, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))

        adc_data, timestamp, dac_data, ads, ads_seq_cnt, reading_error = self.daq.ddr.data_to_names(chan_data)
        t = timestamp * 5e-6 # 5e-9 * 1000 for milliseconds
        print(f'Timestamp spans {t[-1] - t[0]} [ms]')

        data = {}
        for clamp_num in clamp_nums:
            # Multiply by 1e3 to get Voltage data in millivolts
            data[clamp_num] = np.array(to_voltage(adc_data[clamp_num], num_bits=16, voltage_range=10, use_twos_comp=True)) * 1e3

        return t, data

    def record(self, clamp_num, filter_current=None, inject_current=False, low_scaling_factor=0, cutoff=-10, high_scaling_factor=1/7):
        """Send out Sequence and display updating graph.
        
        We read back the data by Sweep so we can update the graph in pieces,
        with each new Sweep being overlaid in a new color. We have the option
        to send out an injected current on pins 16, 18 of J11 on the DAQ board
        as well.

        Parameters
        ----------
        clamp_num : int or List[int]
            Which Clamp to write to (0, 1, 2, or 3).
        filter_current : float or None
            The cutoff frequency in Hertz for a Low Pass Filter (LPF) to
            apply to the current data. None to apply no filter. Defaults to
            None.
        inject_current : bool
            Whether to include a corresponding injected current.
        low_scaling_factor : float
            The scaling factor (uA/mV) for current when the CMD voltage is
            less than the cutoff.
            current = voltage * low_scaling_factor  * 1e3.
        cutoff : float
            The voltage in millivolts at which to switch from the
            low_scaling_factor to the high_scaling_factor for the injected
            current.
        high_scaling_factor : float
            The scaling factor (uA/mV) for current when the CMD voltage is
            greater than or equal to the cutoff.
            current = voltage * low_scaling_factor  * 1e3.
        
        Returns
        -------
        time, data : np.ndarray, np.ndarray
            Time and Voltage data in ms and mV.
        """

        if type(clamp_num) is int:
            clamp_nums = [clamp_num]
        elif type(clamp_num) is list:
            clamp_nums = clamp_num
        else:
            raise TypeError('record parameter clamp_num must be int or list of ints.')

        ads_voltage_range = 5
        ads_sequencer_setup = [('1', '1'), ('2', '2')]
        sequence_length = self.write_sequence(clamp_num=clamp_nums, inject_current=inject_current, low_scaling_factor=low_scaling_factor, cutoff=cutoff, high_scaling_factor=high_scaling_factor)

        # Split Sequence into Sweeps. Write full sequence but read each Sweep individually
        sweeps = np.concatenate([p.sweeps for p in self.sequence.protocols])

        # Hold data from h5 from each sweep so we can write all at the end
        data = np.array([[] for i in range(self.daq.ddr.parameters['adc_channels'])], dtype=int)

        data_dir = os.path.join(os.path.expanduser('~'), 'ephys_data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        file_name = time.strftime("%Y%m%d-%H%M%S.h5")

        # Graph membrane current on top row, membrane voltage on bottom row,
        # each clamp board gets a different column.
        nrows = 2
        ncols = len(clamp_nums)
        # squeeze=False to always return a 2d array so our accessing can be generalized for 1-4 clamps being used
        plt.ion()
        fig, axes = plt.subplots(nrows, ncols, sharex='all', sharey='row', squeeze=False)
        fig.suptitle('Experiment Recording...')
        for col in range(ncols):
            axes[0][col].set_title(f'Clamp {clamp_nums[col]}')
            # Only label bottom since shared axis
            axes[1][col].set_xlabel('Time [ms]')
        # Only label first since shared axis
        axes[0][0].set_ylabel('Membrane Current [\N{GREEK SMALL LETTER MU}A]')
        axes[1][0].set_ylabel('Membrane Voltage [mV]')

        # 4 possible clamps
        leftover_adc_data = [np.array([], dtype=int) for i in range(4)]
        leftover_ads_data = [np.array([]) for i in range(4)]
        current_offset = []
        for sweep_num in range(len(sweeps)):
            sweep = sweeps[sweep_num]
            # Only need len of leftover_adc_data from one clamp board's data, so we just take the first
            blk_multiples = 40
            num_repeats = np.ceil(len(sweep) / 64 / blk_multiples)
            # num_repeats = np.ceil((len(sweep) - len(leftover_adc_data[clamp_nums[0]])) / 64 / blk_multiples)
            # Get data
            # TODO: determine num_repeats to read in exactly one Sweep given that Sweep's length
            # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
            chan_data_one_repeat = self.daq.ddr.save_data(data_dir, file_name, num_repeats=num_repeats,
                                                blk_multiples=blk_multiples)  # blk multiples multiple of 10

            # to get the deswizzled data of all repeats need to read the file
            _t, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))
            adc_cutoff_len = len(sweep) * 2
            ads_cutoff_len = int(adc_cutoff_len // (FS / ADS_FS) / len(ads_sequencer_setup))

            adc_data, timestamp, dac_data, ads, ads_seq_cnt, reading_error = self.daq.ddr.data_to_names(chan_data)
            if reading_error:
                print(f'{timestamp[0]}:{timestamp[-1]} - Error in DDR read')

            # Resize data array for new data, append new data
            chan_data_arr = np.ones((data.shape[0], chan_data[0].shape[0]), dtype=data.dtype)
            for i in chan_data.keys():
                chan_data_arr[i] = chan_data[i]
            data = np.concatenate((data, chan_data_arr), axis=1)

            ############### extract the ADS data ############
            ads_data_v = {}
            for letter in ['A', 'B']:
                ads_data_v[letter] = np.array(to_voltage(
                    ads[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

            total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
            total_seq_cnt[::2] = ads_seq_cnt[0]
            total_seq_cnt[1::2] = ads_seq_cnt[1]
            ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)

            for clamp_num in clamp_nums:
                # Need leftover_adc_data to keep track of any data not part of the current sweep that came with the last read of data.
                # That leftover_adc_data contains data for the next sweep, so we keep it around.
                # use dtype=int so to_voltage function works
                combined_adc_data = np.concatenate([leftover_adc_data[clamp_num], adc_data[clamp_num]], dtype=int)
                leftover_adc_data[clamp_num] = combined_adc_data[adc_cutoff_len:]
                combined_ads_data = np.concatenate([leftover_ads_data[clamp_num], ads_separate_data['A'][clamp_num + 1]])
                leftover_ads_data[clamp_num] = combined_ads_data[ads_cutoff_len:]
                # Multiply by 1e3 to get Voltage data in millivolts
                current_data = (np.array(to_voltage(combined_adc_data[:adc_cutoff_len], num_bits=16, voltage_range=10, use_twos_comp=True)) * 1e3) / 332 * 1620/500

                # Apply offset current on graph to adjust output current readings to 0
                if sweep_num == 0:
                    # Only calculate offset on first sweep, then apply to all data
                    first_index = int(0.1 * len(sweep.epochs[0]))
                    last_index = int(0.9 * len(sweep.epochs[0]))
                    current_offset.append(np.mean(current_data[first_index:last_index]))
                current_data = current_data - current_offset[clamp_num]

                if filter_current is not None:
                    # Should filter the current data using a LPF with given cutoff frequency in Hz
                    current_data = butter_lowpass_filter(data=current_data, cutoff=filter_current, fs=ADS_FS)

                # Create time in milliseconds
                t = np.arange(0, len(current_data))*1/FS * 1e3

                # Multiply by 1e3 to put in mV units
                vm = combined_ads_data[:ads_cutoff_len] * 1e3 / 1.7

                t_ads = np.arange(len(vm))*1/(ADS_FS / len(ads_sequencer_setup)) * 1e3
                # Because we recalculate the length of data to read each sweep,
                # the current_data in later sweeps may be a different length
                # than initial sweeps, so we cut off time with current to
                # prevent plotting ValueErrors due to shape differences.
                axes[0][clamp_nums.index(clamp_num)].plot(t, current_data, label=f'Sweep {sweep_num + 1}')
                axes[1][clamp_nums.index(clamp_num)].plot(t_ads, vm, label=f'Sweep {sweep_num + 1}')
            # Add legend to last plot
            axes[1][-1].legend(loc='lower right')
            fig.canvas.draw()
            fig.canvas.flush_events()

        fig.suptitle('Experiment Recording')
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Save full data
        print('Saving recorded data')
        full_data_name = os.path.join(data_dir, file_name)
        with h5py.File(full_data_name, "w") as file:
            data_set = file.create_dataset("adc", data=data)
        print(f'DDR data saved at {full_data_name}')
        plt.ioff()
        plt.show()

        return data_dir, file_name
