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
import yaml
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
from datastream.datastream import PhysicalConnection

# Constants
FS = 5e6
ADS_FS = 1e6
CMAP_NAME = 'plasma'

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

        return int(np.ceil(self.first_duration * 1e-3 / DDR3.UPDATE_PERIOD))

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

        duration = int(np.ceil(self.first_duration * 1e-3 /
                       DDR3.UPDATE_PERIOD)) * DDR3.UPDATE_PERIOD * 1e3
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

    MAX_TIME = DDR3.SAMPLE_SIZE * DDR3.UPDATE_PERIOD  # In seconds

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
        if len(data) > DDR3.SAMPLE_SIZE:
            print(f'WARNING: Sweep data too long for DDR. {len(data) * DDR3.UPDATE_PERIOD * 1e3} ms > max {Sweep.MAX_TIME * 1e3} ms')
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

    MAX_TIME = DDR3.SAMPLE_SIZE * DDR3.UPDATE_PERIOD  # In seconds

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
        if len(data) > DDR3.SAMPLE_SIZE:
            print(f'WARNING: Protocol data too long for DDR. {len(data) * DDR3.UPDATE_PERIOD * 1e3} ms > max {Protocol.MAX_TIME * 1e3} ms')
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

        cmap = plt.get_cmap(CMAP_NAME)
        fig, ax = plt.subplots()
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Voltage (mV)')
        ax.set_title('Protocol Preview')
        for i in range(len(self.sweeps)):
            data = self.sweeps[i].data()
            if i == 0:
                # final_t = len(data) * DDR3.UPDATE_PERIOD * 1e3   # Final time in milliseconds
                # t = np.arange(0, final_t, DDR3.UPDATE_PERIOD * 1e3)
                t = np.linspace(0, len(data) - 1, len(data)) * DDR3.UPDATE_PERIOD * 1e3
            ax.plot(t, data, color=cmap(1.*i / len(self.sweeps)), label=i + 1)   # Number sweeps on plot starting at 1
        ax.legend(loc='upper right')
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

    MAX_TIME = DDR3.SAMPLE_SIZE * DDR3.UPDATE_PERIOD  # In seconds

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
        if len(data) > DDR3.SAMPLE_SIZE:
            print(f'WARNING: Sequence data too long for DDR. {len(data) * DDR3.UPDATE_PERIOD * 1e3} ms > max {Sequence.MAX_TIME * 1e3} ms')
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


class ExperimentSetup:
    """Contains information from YAML setup file.
    
    This includes how daughtercards are connected to DAQ ports and which pins of which daughtercards are used for what in an experiment.
    
    Attributes
    ----------
    daq_ports : List[Dict[str : Electrode]]
        The setup connection structure: DAQ port number, daughtercard pins, Electrode
    electrodes : List[Electrode]
        A list of all Electrodes in the setup. This is used to help access Electrodes by their name. To avoid confusion, it is recommended to use the ExperimentSetup.get_electrode_by_name method rather than accessing this dictionary directly.
    daq_peripherals : Dict[str: Dict[str: any]]
        Configuration information for DAQ chips such as the ADS8686 (ADC_GP).
    """

    def __init__(self, yaml_dict):
        """Create ExperimentSetup object.
        
        Meant to be used after loading a YAML setup file with yaml.safe_load(file).
        
        Parameters
        ----------
        yaml_dict : dict
            Dictionary of YAML setup file after yaml.safe_load(file).
        """

        self.electrodes = []

        # Accessing the ports explicitly in case other numbered attributes are added later.
        self.daq_ports = [None] * 4
        for i in range(4):
            # Copy everything
            try:
                self.daq_ports[i] = yaml_dict['daq'][i]
            except KeyError:
                self.daq_ports[i] = {}
                continue

            # Now create Electrodes and replace the innermost dictionaries with Electrodes
            # TODO: need to understand which parts of the dictionaries should be replaced with Electrodes first

            # TODO: append to electrodes list as we go

        self.daq_peripherals = {}
        for k in yaml_dict['daq']:
            # Skip ports, already did that above
            if k in [0, 1, 2, 3]:
                continue
            else:
                self.daq_peripherals[k] = yaml_dict['daq'][k]

    @staticmethod
    def from_yaml(file_path: str):
        """Create an ExperimentSetup from a YAML file.
        
        Parameters
        ----------
        file_path : str
            Path to the setup YAML file.

        Returns
        -------
        ExperimentSetup : the loaded setup.
        """

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f'ExperimentSetup file {os.path.abspath(file_path)} not found.')

        with open(file_path, 'r') as file:
            yaml_dict = yaml.safe_load(file)

        return ExperimentSetup(yaml_dict)

    def to_yaml(self, file_path: str, overwrite: bool = False):
        """Store the information in ExperimentSetup in a YAML file.
        
        Parameters
        ----------
        file_path : str
            Path to the save the setup YAML file at.
        overwrite : bool
            Whether to overwrite an existing YAML file at the path given.
            
        Returns
        -------
        str : absolute path to the saved YAML file.
        """
        
        abs_path = os.path.abspath(file_path)
        directory = os.path.dirname(abs_path)

        # Create directory if it does not exist
        if not os.path.isdir(directory):
            print('Directory does not exist. Creating directory...')
            os.makedirs(directory)

        # Overwrite an existing file if allowed
        if os.path.isfile(abs_path):
            if overwrite:
                print(f'File already exists at {abs_path}, overwriting...')
            else:
                raise FileExistsError(f'File already exists at {abs_path}. Use overwrite=True to overwrite it.')

        # Save setup data to the file
        d = {
            'daq': {
                0: self.daq_ports[0],
                1: self.daq_ports[1],
                2: self.daq_ports[2],
                3: self.daq_ports[3],
            }
        }
        d['daq'].update(self.daq_peripherals)
        with open(abs_path, 'w') as file:
            yaml.safe_dump(d, file)

        return abs_path

    def get_electrode_by_name(self, name: str):
        """Get an Electrode instance from setup by name.
        
        Parameters
        ----------
        name : str
            The name of the Electrode.
        
        Returns
        -------
        Electrode : the Electrode with that name. None if the Electrode is not in self.electrodes list.
        """


class Experiment:
    """Holds all objects needed for an Experiment.
    
    Attributes
    ----------
    sequence : Sequence
        The Sequence to be run in this Experiment.
    setup_file_path : str
        Path to the setup YAML file.
    experiment_setup : ExperimentSetup
        ExperimentSetup instance containing information about connections for the experiment.
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

    def __init__(self, sequence: Sequence or Protocol, setup_file_path: str = None, autoload_setup: bool = True):

        # Initialize FPGA
        self.endpoints = Endpoint.update_endpoints_from_defines()
        self.fpga = FPGA()
        # TODO: is there any way we can wait to fpga.init_device() until setup?
        self.fpga.init_device()
        self.daq = Daq(self.fpga)
        self.daq.ddr.data_version = 'TIMESTAMPS'
        self.clamps = [Clamp(fpga=self.fpga, dc_num=dc_num) for dc_num in range(4)]
        self.gpio = Daq.GPIO(self.fpga)
        self.pwr = Daq.Power(self.fpga)
        self.pwr.all_off()  # disable all power enables
        self.dc_pwr = []
        if type(sequence) is Protocol:
            self.sequence = Sequence(protocols=sequence)
        else:
            self.sequence = sequence
        self.setup_file_path = setup_file_path
        if self.setup_file_path is not None and autoload_setup:
            self.load_setup()
        else:
            self.experiment_setup = ExperimentSetup({})

    def load_setup(self, file_path: str = None):
        """Load setup from a YAML file.
        
        Parameters
        ----------
        file_path : str
            Path to the setup YAML file. Defaults to None in which case Experiment.setup_yaml_path is used instead.

        Returns
        -------
        ExperimentSetup : the loaded setup.
        """

        if file_path is None:
            file_path = self.setup_file_path
        self.experiment_setup = ExperimentSetup.from_yaml(file_path)

        return self.experiment_setup

    def create_phys_connections(self):
        """Return a dictionary of PhysicalConnections based on the current setup.
        
        Returns
        -------
        dict : int or str to PhysicalConnections pairs
        """

        phys_connections = {}

        ad7961_fs = 4.096*2
        # ADC data
        # 1) AD7961 - dictionary key is an integer [0, 3]
        for dc_num in range(4):
            dc = self.experiment_setup.daq_ports[dc_num]
            # Skip any daughtercards not defined in setup YAML
            if dc == {}:
                continue
            else:
                RF = dc['clamp_configs']['ADG_RES'] * \
                    1e3  # all resistor values are in kilo-Ohms
                inamp_gain = dc['clamp_configs']['gain']
                # daughter-card differential buffer (resistor values). Gain is less than x1
                diff_buffer_gain = 499/(1500+120)
                conv_factor = ad7961_fs/inamp_gain/RF/diff_buffer_gain

                net = dc['AD7961']['name']
                pc = PhysicalConnection(f'{dc_num}',
                                        conv_factor,
                                        converter='AD7961',
                                        bits=16,
                                        units='A',
                                        net=net)
            phys_connections[int(dc_num)] = pc

        # 2) ADS8686
        ads_map = self.daq.parameters["ads_map"]
        for dc_num in range(4):
            dc = self.experiment_setup.daq_ports[dc_num]
            # Skip any daughtercards not defined in setup YAML
            if dc == {}:
                continue
            else:
                for amp_net in ['AMP_OUT', 'CAL_ADC']:
                    if amp_net == 'AMP_OUT':
                        # the AMP_OUT buffer has a gain of x11, the P1 buffer has a gain of 1+RF/3.01  [both resistors are in kOhms]
                        gain = 11*(1+dc['clamp_configs']['RF1']/3.01)
                    else:
                        gain = 1
                    if ads_map[dc_num][amp_net][0] == 'A':
                        ads_chan = 0
                    else:
                        ads_chan = 8
                    # channel goes from 0 - 15 for the voltage range
                    ads_chan += int(ads_map[dc_num][amp_net][1])
                    # ads.current_voltage_range is a len 16 list
                    conv_factor = self.daq.ADC_gp.ranges[ads_chan]*2/gain
                    # example 'A0' or 'B2'
                    con_name = f'{ads_map[dc_num][amp_net][0]}{ads_map[dc_num][amp_net][1]}'

                    net = dc[amp_net]['name']
                    pc = PhysicalConnection(f'{net}_{dc_num}',
                                            conv_factor,
                                            converter='ADS8686',
                                            bits=16,
                                            units='V',
                                            net=net)
                    phys_connections[con_name] = pc

        # P1 is the voltage that is actually at the membrane electrode (divided by gain of feedback amplifier)

        # CMD is the target membrane voltage with a closed-loop configuration
        # 3) DAC data -- AD5453, does not depend on daughtercard config, unsigned
        for dc_num in range(4):
            dc = self.experiment_setup.daq_ports[dc_num]
            # Skip any daughtercards not defined in setup YAML
            if dc == {}:
                continue
            else:
                net = self.daq.parameters['fast_dac_map'][dc_num]
                gain = self.daq.current_dac_gain[dc_num]  # +/-
                if gain > 99:  # must by mV -- convert to volts
                    gain = gain/1000
                if 'CMD' in net:
                    # TODO x10 is a property of the clamp board, can we have a parameter for this?
                    gain = gain/(1 + dc['clamp_configs']['RF1']/3.01)/10
                con_name = f'D{dc_num}'
                pc = PhysicalConnection(con_name,
                                        gain*2,  # this is more accurately the full-scale range
                                        converter='AD5453',
                                        bits=14,
                                        units='V',
                                        net=net)
            phys_connections[con_name] = pc

        return phys_connections

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
        # self.fpga.init_device()   # Currently being done in __init__
        time.sleep(2)
        self.fpga.send_trig(self.endpoints["GP"]["SYSTEM_RESET"])  # system reset
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
        self.daq.ADC_gp.hw_reset(val=False)
        self.daq.ADC_gp.set_host_mode()
        self.daq.ADC_gp.setup()
        self.daq.ADC_gp.set_range(self.experiment_setup.daq_peripherals['ADS8686']['voltage_range'])
        self.daq.ADC_gp.set_lpf(39)
        codes = self.daq.ADC_gp.setup_sequencer(chan_list=self.experiment_setup.daq_peripherals['ADS8686']['sequencer_setup'])
        self.daq.ADC_gp.write_reg_bridge(clk_div=200) # 1 MSPS rate (do not use default value of 1000 which is 200 ksps)
        self.daq.ADC_gp.set_fpga_mode()

        # TODO: are the TCA pins already configured in Clamp.configure_clamp()?
        self.daq.TCA[0].configure_pins([0, 0])
        self.daq.TCA[1].configure_pins([0, 0])

        # fast DAC channels setup
        holding_voltage_code = (from_voltage(voltage=holding_voltage, num_bits=14, voltage_range=5, with_negatives=True) + dac_offset) & 0x3FFF
        for i in range(6):
            self.daq.DAC[i].set_ctrl_reg(self.daq.DAC[i].master_config)
            self.daq.DAC[i].set_spi_sclk_divide()
            self.daq.DAC[i].filter_select(operation="clear")
            self.daq.DAC[i].write(holding_voltage_code)
            self.daq.DAC[i].change_filter_coeff(target="passthru")
            self.daq.DAC[i].write_filter_coeffs()
            self.daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

        # --------  Enable fast ADCs  --------
        for chan in [0, 1, 2, 3]:
            self.daq.ADC[chan].power_up_adc()  # standard sampling
        self.daq.ADC[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
        self.daq.ADC[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset

    def configure_clamps(self, clamps: list = [0, 1, 2, 3]):
        """Configure the clamps (daughtercards) as defined in the self.setup attribute.
        
        To change the configuration of the clamps, change the values in self.setup and run this method again.

        Parameters
        ----------
        clamps : List[int]
            A list of which clamps to configure. Defaults to [0, 1, 2, 3] to configure all clamps.
        
        Returns
        -------
        List[Dict] : the configuration parameters just set for each daughtercard. DC 0 at index 0, DC 1 at index 1, etc.
        """

        config_list = [{}] * 4

        for dc_num in clamps:
            dc = self.experiment_setup.daq_ports[dc_num]
            # Skip any daughtercard (clamp) with no specified configuration
            if dc is None or dc.get('clamp_configs') is None:
                continue

            configs = dc['clamp_configs']
            # Configure any daughtercard with a specified configuration
            # We use .get() instead of [] to access dict here so we get None instead of a KeyError
            # This way, any parameter not specified in the 'clamp_configs' dict will be left as the default Clamp.configure_clamp() argument for that parameter.
            _, config_list[dc_num] = self.clamps[dc_num].configure_clamp(
                ADC_SEL     = configs.get('ADC_SEL'),
                DAC_SEL     = configs.get('DAC_SEL'),
                CCOMP       = configs.get('CCOMP'),
                RF1         = configs.get('RF1'),
                ADG_RES     = configs.get('ADG_RES'),
                PClamp_CTRL = configs.get('PClamp_CTRL'),
                P1_E_CTRL   = configs.get('P1_E_CTRL'),
                P1_CAL_CTRL = configs.get('P1_CAL_CTRL'),
                P2_E_CTRL   = configs.get('P2_E_CTRL'),
                P2_CAL_CTRL = configs.get('P2_CAL_CTRL'),
                gain        = configs.get('gain'),
                FDBK        = configs.get('FDBK'),
                mode        = configs.get('mode'),
                EN_ipump    = configs.get('EN_ipump'),
                RF_1_Out    = configs.get('RF_1_Out'),
                addr_pins_1 = configs.get('addr_pins_1'),
                addr_pins_2 = configs.get('addr_pins_2'),
            )

        return config_list

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
            # Pad with zeros to make correct size. TODO: make constant_values the holding voltage for the Protocol. For now, assuming the Protocol begins at the holding voltage and use its first value.
            cmd_voltage = np.pad(cmd_voltage, (0, target_len - len(cmd_voltage)), 'constant', constant_values=cmd_voltage[0])
            # TODO: determine voltage_range for AD5453
            cmd_signal = np.array(from_voltage(voltage=cmd_voltage, num_bits=14, voltage_range=5, with_negatives=True), dtype=np.uint16) + dac_offset
            cc_signal = np.ones(len(cmd_signal), dtype=np.uint16) * dac_offset
            self.daq.ddr.data_arrays[cmd_ch] = cmd_signal
            self.daq.ddr.data_arrays[cc_ch] = cc_signal

            # Write channels to the DDR
            self.daq.DAC[cmd_ch].write(int(self.daq.ddr.data_arrays[cmd_ch][0]) & 0x3FFF)    # Write first output code from host to make smooth transition
            self.daq.DAC[cc_ch].write(int(self.daq.ddr.data_arrays[cc_ch][0]) & 0x3FFF)    # Write first output code from host to make smooth transition

        # Create injected current data
        if inject_current:
            # sequence_data in V, cutoff in mV, scaling factors in uA/mv, current needs to be in nA
            current = np.where(
                sequence_data < cutoff * 1e-3,
                sequence_data * 1e3 * low_scaling_factor * 1e3,
                sequence_data * 1e3 * high_scaling_factor * 1e3
            )
            self.inject_current(current=current, write_ddr=False)


        self.daq.ddr.write_setup()
        block_pipe_return, speed_MBs = self.daq.ddr.write_channels(set_ddr_read=False)
        # self.daq.DAC[cmd_ch].write(int(self.daq.ddr.data_arrays[cmd_ch][0]) & 0x3FFF)    # Write first output code from host to make smooth transition
        # self.daq.DAC[cc_ch].write(int(self.daq.ddr.data_arrays[cc_ch][0]) & 0x3FFF)    # Write first output code from host to make smooth transition
        self.daq.ddr.reset_mig_interface()
        self.daq.ddr.reset_fifo('ALL')
        # self.daq.ddr.write_finish()
        # DEBUG
        bits = [self.daq.ddr.endpoints['ADC_WRITE_ENABLE'].bit_index_low,
                self.daq.ddr.endpoints['DAC_READ_ENABLE'].bit_index_low]
        self.daq.ddr.fpga.set_ep_simultaneous(self.daq.ddr.endpoints['ADC_WRITE_ENABLE'].address, bits, [1, 1])
        for i in range(6):
            self.daq.DAC[i].set_data_mux("DDR")

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
            data will still be in the self.daq.ddr.data_arrays variable and will be
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

    def record(self, clamp_num, file_name=None, filter_current=None, inject_current=False, low_scaling_factor=0, cutoff=-10, high_scaling_factor=1/7, plot=True):
        """Send out Sequence and display updating graph.
        
        We read back the data by Sweep so we can update the graph in pieces,
        with each new Sweep being overlaid in a new color. We have the option
        to send out an injected current on pins 16, 18 of J11 on the DAQ board
        as well.

        Parameters
        ----------
        clamp_num : int or List[int]
            Which Clamp to write to (0, 1, 2, or 3).
        file_name : str
            The h5 file name for the data which will be stored in ~/ephys_data/file_name. If left as None, the current date will be used.
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
        plot : bool
            Whether to plot membrane voltage and current data as it comes in.
        
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
        sequence_length = self.write_sequence(clamp_num=clamp_nums, inject_current=inject_current, low_scaling_factor=low_scaling_factor, cutoff=cutoff, high_scaling_factor=high_scaling_factor)

        # Split Sequence into Sweeps. Write full sequence but read each Sweep individually
        sweeps = np.concatenate([p.sweeps for p in self.sequence.protocols])

        data_dir = os.path.join(os.path.expanduser('~'), 'ephys_data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # Assign file name according to the date if None is given
        if file_name is None:
            file_name = time.strftime("%Y%m%d-%H%M%S.h5")

        if not plot:
            # Time it takes from starting the fast DACs on DDR mode through stopping them without a time.sleep() delay
            natural_delay = 0.23539209365844727
            time.sleep(max(0, self.sequence.duration() * 1e-3 - natural_delay))
            blk_multiples = 40
            # total bytes from save data = 2048 * num_repeats * blk_multiples
            # 128 bits per read point -> 16 bytes per read point
            # Need 2*len(sweep) points read to read the same amount of time since ADC 2 times faster than DAC (5 MSPS vs. 2.5 MSPS)
            # num_repeats = 2*len(sweep) * 16 / 2048 / blk_multiples --> simplifies to the below
            total_sweep_len = sum([len(sweep) for sweep in sweeps])
            num_repeats = np.ceil(total_sweep_len / 64 / blk_multiples)
            # Get data
            # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
            chan_data = self.daq.ddr.save_data(data_dir, file_name, num_repeats=num_repeats,
                                               blk_multiples=blk_multiples, append=True)  # blk multiples multiple of 10
            return data_dir, file_name

        start = time.time()

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
        current_offset = [None] * 4
        fig_x, ax_x = plt.subplots()
        fig_x.suptitle('dac_data')
        time.sleep(max(0, self.sequence.duration() * 1e-3 - natural_delay))
        bits = [self.daq.ddr.endpoints['ADC_WRITE_ENABLE'].bit_index_low,
                self.daq.ddr.endpoints['DAC_READ_ENABLE'].bit_index_low]
        self.daq.ddr.fpga.set_ep_simultaneous(self.daq.ddr.endpoints['ADC_WRITE_ENABLE'].address, bits, [0, 0])
        self.daq.ddr.fpga.set_wire_bit(self.daq.ddr.endpoints['ADC_TRANSFER_ENABLE'].address, self.daq.ddr.endpoints['ADC_TRANSFER_ENABLE'].bit_index_low)
        end = time.time()
        print(f'Time between starting DAC data and stopping DAC data and ADC write = {end - start}')
        cmap = plt.get_cmap(CMAP_NAME)
        for sweep_num in range(len(sweeps)):
            color = cmap(1.*sweep_num / len(sweeps))

            # time.sleep(0.050)
            sweep = sweeps[sweep_num]
            # Only need len of leftover_adc_data from one clamp board's data, so we just take the first
            blk_multiples = 40
            # total bytes from save data = 2048 * num_repeats * blk_multiples
            # 128 bits per read point -> 16 bytes per read point
            # Need 2*len(sweep) points read to read the same amount of time since ADC 2 times faster than DAC (5 MSPS vs. 2.5 MSPS)
            # num_repeats = 2*len(sweep) * 16 / 2048 / blk_multiples --> simplifies to the below
            num_repeats = np.ceil(len(sweep) / 64 / blk_multiples)
            # Get data
            # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
            chan_data = self.daq.ddr.save_data(data_dir, file_name, num_repeats=num_repeats,
                                                blk_multiples=blk_multiples, append=True)  # blk multiples multiple of 10
            chan_data = chan_data.astype(int)

            # to get the deswizzled data of all repeats need to read the file
            # _t, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))
            adc_cutoff_len = len(sweep) * 2
            ads_cutoff_len = int(adc_cutoff_len // (FS / ADS_FS) / len(self.experiment_setup.daq_peripherals['ADS8686']['sequencer_setup']))

            adc_data, timestamp, dac_data, ads, ads_seq_cnt, reading_error = self.daq.ddr.data_to_names(chan_data, self.daq.ddr.fpga.bitfile_version)
            if reading_error:
                print(f'{timestamp[0]}:{timestamp[-1]} - Error in DDR read')
            
            ax_x.plot(dac_data[1], color=color)
            plt.show()

            # Resize data array for new data, append new data
            # chan_data_arr = np.ones((data.shape[0], chan_data[0].shape[0]), dtype=data.dtype)
            # for i in chan_data.keys():
            #     chan_data_arr[i] = chan_data[i]
            # data = np.concatenate((data, chan_data_arr), axis=1)

            ############### extract the ADS data ############
            ads_data_v = {}
            for letter in ['A', 'B']:
                ads_data_v[letter] = np.array(to_voltage(
                    ads[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

            total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
            total_seq_cnt[::2] = ads_seq_cnt[0]
            total_seq_cnt[1::2] = ads_seq_cnt[1]
            ads_separate_data = separate_ads_sequence(self.experiment_setup.daq_peripherals['ADS8686']['sequencer_setup'], ads_data_v, total_seq_cnt, slider_value=4)

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
                    current_offset[clamp_num] = np.mean(current_data[first_index:last_index])
                current_data = current_data - current_offset[clamp_num]

                if filter_current is not None:
                    # Should filter the current data using a LPF with given cutoff frequency in Hz
                    current_data = butter_lowpass_filter(data=current_data, cutoff=filter_current, fs=ADS_FS)

                # Create time in milliseconds
                t = np.arange(0, len(current_data))*1/FS * 1e3

                # Multiply by 1e3 to put in mV units
                vm = combined_ads_data[:ads_cutoff_len] * 1e3 / 1.7

                t_ads = np.arange(len(vm))*1/(ADS_FS / len(self.experiment_setup.daq_peripherals['ADS8686']['sequencer_setup'])) * 1e3
                # Because we recalculate the length of data to read each sweep,
                # the current_data in later sweeps may be a different length
                # than initial sweeps, so we cut off time with current to
                # prevent plotting ValueErrors due to shape differences.
                axes[0][clamp_nums.index(clamp_num)].plot(t, current_data, label=f'Sweep {sweep_num + 1}', color=color)
                axes[1][clamp_nums.index(clamp_num)].plot(t_ads, vm, label=f'Sweep {sweep_num + 1}', color=color)
            # Add legend to last plot
            axes[1][-1].legend(loc='lower right')
            fig.canvas.draw()
            fig.canvas.flush_events()

        fig.suptitle('Experiment Recording')
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Save full data
        # print('Saving recorded data')
        full_data_name = os.path.join(data_dir, file_name)
        # with h5py.File(full_data_name, "w") as file:
        #     data_set = file.create_dataset("adc", data=data)
        print(f'DDR data saved at {full_data_name}')
        plt.ioff()
        plt.show()

        return data_dir, file_name


    def write_sine(self, clamp_num, amplitude=1, frequency=1e3):
        """Write a continuous sine wave to the DDR.

        The sine wave will come as the CMD signal. The CC signal will remain
        at the dac_offset value of 0x1E00.
        
        Parameters
        ----------
        clamp_num : int or List[int]
            Which Clamp to write to (0, 1, 2, or 3).
        amplitude : float
            The amplitude (peak to peak) of the sine wave in Volts.
        frequency : float
            The frequency of the sine wave in Hertz. In order to make the sine
            wave continuous, the real frequency may different.

        Returns
        -------
        real_freq : float
            The actual frequency used for the sine wave in Hertz. This may be
            different from the input frequency to ensure the sine wave is
            continuous.
        """

        if type(clamp_num) is int:
            clamp_nums = [clamp_num]
        elif type(clamp_num) is list:
            clamp_nums = clamp_num
        else:
            raise TypeError('write_sequence parameter clamp_num must be int or list of ints.')

        dac_offset = 0x1E00
        fb_res = 2.1
        offset_adjust_k = 1 + fb_res / 3    # fb_res is already in kOhms, so 3 instead of 3e3

        # In addition to the offset adjust amplifier, the CMD signal is
        # attennuated 10x from the DAQ board to the daughtercard so we
        # have to multiply our signal by 10 to get it back to what we want
        # cmd_voltage = amplitude * offset_adjust_k * 10
        cmd_voltage = 1 * offset_adjust_k * 10
        cmd_bin = from_voltage(voltage=cmd_voltage, num_bits=14,
                                voltage_range=5, with_negatives=True)
        cmd_signal, real_freq = self.daq.ddr.make_sine_wave(amplitude=cmd_bin, frequency=frequency, offset=dac_offset, actual_frequency=True)
        cc_signal = np.ones(len(cmd_signal), dtype=np.uint16) * dac_offset

        for clamp_num in clamp_nums:
            cmd_ch = clamp_num * 2 + 1
            cc_ch = clamp_num * 2

            self.daq.ddr.data_arrays[cmd_ch] = cmd_signal
            self.daq.ddr.data_arrays[cc_ch] = cc_signal
        
        self.daq.ddr.write_setup()
        block_pipe_return, speed_MBs = self.daq.ddr.write_channels(set_ddr_read=False)
        # self.daq.DAC[cmd_ch].write(int(self.daq.ddr.data_arrays[cmd_ch][0]) & 0x3FFF)    # Write first output code from host to make smooth transition
        # self.daq.DAC[cc_ch].write(int(self.daq.ddr.data_arrays[cc_ch][0]) & 0x3FFF)    # Write first output code from host to make smooth transition
        self.daq.ddr.reset_mig_interface()
        self.daq.ddr.reset_fifo('ALL')
        self.daq.ddr.write_finish()
        # DEBUG
        # bits = [self.daq.ddr.endpoints['ADC_WRITE_ENABLE'].bit_index_low,
        #         self.daq.ddr.endpoints['DAC_READ_ENABLE'].bit_index_low]
        # self.daq.ddr.fpga.set_ep_simultaneous(self.daq.ddr.endpoints['ADC_WRITE_ENABLE'].address, bits, [1, 1])
        for i in range(6):
            self.daq.DAC[i].set_data_mux("DDR")

        return real_freq

    
    def record_sine(self, clamp_num, amplitude=1, frequency=1e3, save_data=False):
        """Write and read a continuous sine wave with an updating graph.
        
        Parameters
        ----------
        clamp_num : int or List[int]
            Which Clamp to write to (0, 1, 2, or 3).
        amplitude : float
            The amplitude (peak to peak) of the sine wave in Volts.
        frequency : float
            The frequency of the sine wave in Hertz.
        save_data : bool
            Whether to save the data read back in the sine wave. Being continuous, this could become a very large file.

        Returns
        -------
        None
        """

        ads_voltage_range = 5  # need this for to_voltage later
        ads_sequencer_setup = [('1', '1'), ('2', '2')]

        # Make clamp_nums a list
        if type(clamp_num) is int:
            clamp_nums = [clamp_num]
        elif type(clamp_num) is list:
            clamp_nums = clamp_num
        else:
            raise TypeError('record parameter clamp_num must be int or list of ints.')

        data_dir = os.path.join(os.path.expanduser('~'), 'ephys_data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        file_name = time.strftime("%Y%m%d-%H%M%S.h5")

        real_freq = self.write_sine(clamp_num=clamp_nums, amplitude=amplitude, frequency=frequency)

        # Set up plots
        # Graph membrane current on top row, membrane voltage on bottom row,
        # each clamp board gets a different column.
        nrows = 2
        ncols = len(clamp_nums)
        # squeeze=False to always return a 2d array so our accessing can be generalized for 1-4 clamps being used
        plt.ion()
        fig, axes = plt.subplots(
            nrows, ncols, sharex='all', sharey='row', squeeze=False)
        fig.suptitle('Experiment Recording...')
        for col in range(ncols):
            axes[0][col].set_title(f'Clamp {clamp_nums[col]}')
            # Only label bottom since shared axis
            axes[1][col].set_xlabel('Time [ms]')
        # Only label first since shared axis
        axes[0][0].set_ylabel('Membrane Current [\N{GREEK SMALL LETTER MU}A]')
        axes[1][0].set_ylabel('Membrane Voltage [mV]')

        # Stop recording data when the figure is closed
        class EventVariables:
            """Hold variables needed outside event handlers, but set inside event handlers."""
            def __init__(self, experiment):
                self.closed = False
                self.user_cmd = ''
                self.experiment = experiment

            def close(self, event):
                """Stop while loop when figure is closed."""

                self.closed = True

            def on_press(self, event):
                """Handle user input."""

                if event.key == 'enter':
                    # Execute command on enter
                    try:
                        exec(self.user_cmd)
                    except Exception as e:
                        raise e
                    finally:
                        self.user_cmd = ''
                elif event.key == 'shift':
                    # Ignore shift because we do not want that part of the executed command
                    return
                elif event.key == 'backspace':
                    # Allow backspace to remove last character
                    self.user_cmd = self.user_cmd[:-1]
                else:
                    # Keep track of keys pressed to build up the command; display keys pressed for user
                    self.user_cmd += event.key
                    print(event.key, end='')
                    sys.stdout.flush()

                if self.user_cmd == '`1':
                    # Some automatic keypresses prefixed by `
                    for i in range(6):
                        self.experiment.daq.set_dac_gain(i, 2)
                    self.user_cmd = ''
                    return
                elif self.user_cmd == '`2':
                    # Some automatic keypresses prefixed by `
                    for i in range(6):
                        self.experiment.daq.set_dac_gain(i, 5)
                    self.user_cmd = ''
                    return
                elif self.user_cmd == '`3':
                    # Some automatic keypresses prefixed by `
                    for i in range(6):
                        self.experiment.daq.set_dac_gain(i, 15)
                    self.user_cmd = ''
                    return


        event_vars = EventVariables(self)
        fig.canvas.mpl_connect('close_event', event_vars.close)
        fig.canvas.mpl_connect('key_press_event', event_vars.on_press)
        # Clear matplotlib default keyboard shortcuts
        for key in plt.rcParams.keys():
            if 'keymap' in key:
                plt.rcParams[key] = []

        # No leftover data required because we are not doing this in sweeps
        # Instead, we will rewrite the data on the plot

        # Give the FIFO a little time to fill up, then start transferring continuously
        time.sleep(0.100)
        self.daq.ddr.fpga.set_wire_bit(self.daq.ddr.endpoints['ADC_TRANSFER_ENABLE'].address, self.daq.ddr.endpoints['ADC_TRANSFER_ENABLE'].bit_index_low)
        blk_multiples = 40
        num_period = 5
        data_points_per_period = FS / real_freq
        num_repeats = np.ceil(data_points_per_period * num_period / 64 / blk_multiples)

        first_time = True
        current_lines = [None] * 4
        voltage_lines = [None] * 4
        # TODO: turn this into a while loop with a way to get out
        while not event_vars.closed:
            # Start grabbing data, append if save_data, otherwise overwrite each time to save space
            chan_data = self.daq.ddr.save_data(data_dir, file_name, num_repeats=num_repeats,
                                            blk_multiples=blk_multiples, append=save_data)
            chan_data = chan_data.astype(int)
            adc_data, timestamp, dac_data, ads, ads_seq_cnt, reading_error = self.daq.ddr.data_to_names(chan_data, self.daq.ddr.fpga.bitfile_version)
            if reading_error:
                print(f'{timestamp[0]}:{timestamp[-1]} - Error in DDR read')

            for clamp_num in clamp_nums:
                # Multiply by 1e3 to get Voltage data in millivolts
                current_data = (np.array(to_voltage(adc_data[clamp_num], num_bits=16, voltage_range=10, use_twos_comp=True)) * 1e3) / 332 * 1620/500

                # Extract the ADS data
                ads_data_v = {}
                for letter in ['A', 'B']:
                    ads_data_v[letter] = np.array(to_voltage(ads[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

                # get the right length
                total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1]))
                total_seq_cnt[::2] = ads_seq_cnt[0]
                total_seq_cnt[1::2] = ads_seq_cnt[1]
                ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)

                # Create time in milliseconds
                t = np.arange(0, len(current_data))*1/FS * 1e3

                # Multiply by 1e3 to put in mV units
                vm =  ads_separate_data['A'][clamp_num + 1] * 1e3 / 1.7

                t_ads = np.arange(len(vm))*1/(ADS_FS / len(ads_sequencer_setup)) * 1e3
                # Because we recalculate the length of data to read each sweep,
                # the current_data in later sweeps may be a different length
                # than initial sweeps, so we cut off time with current to
                # prevent plotting ValueErrors due to shape differences.
                if first_time:
                    # Plot returns a list of Line objects that we can later use to update data instead of drawing new lines, which is faster
                    current_lines[clamp_num] = axes[0][clamp_nums.index(clamp_num)].plot(t, current_data)[0]
                    voltage_lines[clamp_num] = axes[1][clamp_nums.index(clamp_num)].plot(t_ads, vm)[0]
                else:
                    current_lines[clamp_num].set_xdata(t)
                    current_lines[clamp_num].set_ydata(current_data)
                    voltage_lines[clamp_num].set_xdata(t_ads)
                    voltage_lines[clamp_num].set_ydata(vm)
                fig.canvas.draw()
                fig.canvas.flush_events()
            first_time = False

        fig.suptitle('Experiment Recording')
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Delete data if not save_data
        full_data_name = os.path.join(data_dir, file_name)
        if save_data:
            print(f'DDR data saved at {full_data_name}')
        else:
            os.remove(full_data_name)
            print(f'DDR data cleared from {full_data_name}')
        plt.ioff()
        plt.show()
