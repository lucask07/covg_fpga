"""Classes for electrophysiology.

Abe Stroschein, ajstroschein@stthomas.edu
"""

from typing import List, Dict
import copy
import time
import numpy as np
import matplotlib.pyplot as plt
import atexit
from pyripherals.core import FPGA, Endpoint
from pyripherals.utils import from_voltage
from pyripherals.peripherals.DDR3 import DDR3
from ..instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from ..boards import Daq, Clamp

# Variables
f = FPGA()
f.init_device()
ddr = DDR3(fpga=f)

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
        """Calculate the actual duration of the Epoch.
        
        We will aim for the sum of the Epochs' first_duration values, but the actual duration may change slightly due to DDR constraints.
        
        Returns
        -------
        duration : float
            The actual duration of the Epoch in ms.
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
            print(f'WARNING: Sweep data too long for DDR. {len(data) * ddr.parameters["update_period"] * 1e3} ms > max {Protocol.MAX_TIME * 1e3} ms')
        return data

    def duration(self):
        """Calculate the actual duration of the Epoch.
        
        We will aim for the sum of the Epochs' first_duration values, but the actual duration may change slightly due to DDR constraints.
        
        Returns
        -------
        duration : float
            The actual duration of the Epoch in ms.
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
        for i in range(len(self.sweeps)):
            data = self.sweeps[i].data()
            if i == 0:
                final_t = len(data) * ddr.parameters["update_period"] * 1e3   # Final time in milliseconds
                t = np.arange(0, final_t, ddr.parameters["update_period"] * 1e3)
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
    """

    def __init__(self):

        # Initialize FPGA
        self.endpoints = Endpoint.update_endpoints_from_defines()
        self.fpga = FPGA()
        self.daq = Daq(self.fpga)
        self.clamps = [Clamp(f, dc_num=dc_num) for dc_num in range(4)]
        self.gpio = Daq.GPIO(self.fpga)
        self.pwr = Daq.Power(self.fpga)
        self.pwr.all_off()  # disable all power enables
        self.dc_pwr = []

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
        f.init_device()
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
        pwr_off(self.dc_pwr)

    def record(self):
        """Send out Sequence and record data back."""

        pass
