"""Classes for electrophysiology.

Abe Stroschein, ajstroschein@stthomas.edu
"""

from typing import List, Dict
import os
import sys
import copy
import time
import numpy as np
import matplotlib.pyplot as plt
import atexit
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
from boards import Daq, Clamp

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

    def data(self):
        """Create and return the data for the Epoch.
        
        Returns
        -------
        data : np.ndarray
            The voltage data points for the Epoch in V.
        """

        data = self.first_level * np.ones(shape=int(np.ceil(self.first_duration * 1e-3 / ddr.parameters['update_period'])), dtype=np.int16)
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


    def data(self):
        """Create and return the data for the Sweep.
        
        Returns
        -------
        data : np.ndarray
            The voltage data points for the Sweep in V.
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

    def data(self):
        """Create and return the data for the Protocol.
        
        Returns
        -------
        data : np.ndarray
            The voltage data for the Protocol in V.
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

    def data(self):
        """Create and return the data for the Sequence.
        
        Returns
        -------
        data : np.ndarray
            The voltage data for the Sequence in V.
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

        # --------  Enable fast ADCs  --------
        for chan in [0, 1, 2, 3]:
            self.daq.ADC[chan].power_up_adc()  # standard sampling
        time.sleep(0.1)
        self.daq.ADC[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
        time.sleep(1)

        # TODO: are the TCA pins already configured in Clamp.configure_clamp()?
        self.daq.TCA[0].configure_pins([0, 0])
        self.daq.TCA[1].configure_pins([0, 0])

        # fast DAC channels setup
        for i in range(6):
            self.daq.DAC[i].set_ctrl_reg(self.daq.DAC[i].master_config)
            self.daq.DAC[i].set_spi_sclk_divide()
            self.daq.DAC[i].filter_select(operation="clear")
            self.daq.DAC[i].write(int(0))
            self.daq.DAC[i].set_data_mux("DDR")
            self.daq.DAC[i].change_filter_coeff(target="passthru")
            self.daq.DAC[i].write_filter_coeffs()
            self.daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

    def close(self):
        """Close opened devices from setup."""

        self.pwr.all_off()
        pwr_off([pwr for pwr in self.dc_pwr if pwr is not None])
        self.fpga.xem.Close()

    def write_sequence(self, clamp_num):
        """Write the Sequence for this Experiment. 
        
        Write to the CMD channel of the specified Clamp board.
        
        Parameters
        ----------
        clamp_num : int or List[int]
            Which Clamp to write to (0, 1, 2, or 3).
        """

        if type(clamp_num) is int:
            clamp_nums = [clamp_num]
        elif type(clamp_num) is list:
            clamp_nums = clamp_num
        else:
            raise TypeError('write_sequence parameter clamp_num must be int or list of ints.')

        dac_offset = 0x2000
        target_len = len(self.daq.ddr.data_arrays[0])

        # Create data
        for clamp_num in clamp_nums:
            cmd_ch = clamp_num * 2 + 1
            cc_ch = clamp_num * 2
            # Multiply data by 1e-3 because it is given in mV, need in V
            # Pad with zeros to make correct size
            cmd_signal = self.sequence.data() * 1e-3
            cmd_signal = np.pad(cmd_signal, (0, target_len - len(cmd_signal)), 'constant')
            cmd_signal = [float(x) for x in cmd_signal]
            # TODO: determine voltage_range for AD5453
            cmd_signal = from_voltage(voltage=cmd_signal, num_bits=14, voltage_range=5, with_negatives=True)
            cc_signal = np.ones(len(cmd_signal)) * dac_offset
            self.daq.ddr.data_arrays[cmd_ch] = cmd_signal
            self.daq.ddr.data_arrays[cc_ch] = cc_signal

        # Write channels to the DDR
        self.daq.ddr.write_setup()
        block_pipe_return, speed_MBs = self.daq.ddr.write_channels(set_ddr_read=False)
        self.daq.ddr.reset_mig_interface()
        self.daq.ddr.write_finish()

    def read_response(self, clamp_num):
        """Return the incoming data from the Daq board.
        
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
        self.daq.ddr.repeat_setup()
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
