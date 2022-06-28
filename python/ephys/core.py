"""Classes for electrophysiology."""

from typing import List
import copy
import numpy as np
import matplotlib.pyplot as plt
from pyripherals.core import FPGA
from pyripherals.peripherals.DDR3 import DDR3

f = FPGA()
f.init_device()
ddr = DDR3(fpga=f)

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
        plt.show()
