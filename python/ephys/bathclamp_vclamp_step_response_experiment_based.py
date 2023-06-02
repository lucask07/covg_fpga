"""Recreate bathclamp_vclamp_step_response.py using the Experiment class.

We want to make use of the Experiment class so the resuting script is easier
to follow and fewer lines.
------------------------------------------------------------------------------
This script attempts to replicate Figure 4 on the biophysical poster. This
consists of measuring the membrane current (Im) with the AD7961 after
supplying a step voltage of 0-50mV by the AD5453.
The system uses two Daughtercards with:
 1) the bath clamp - has a non-zero CMD voltage measures Im 
 2) the voltage clamp - zero CMD voltage, goal is to hold capacitor plate at
    ground 

January 2023

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

from core import Protocol, Experiment
import matplotlib.pyplot as plt
import os
import numpy as np

import sys
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
from datastream.datastream import rawh5_to_datastreams

data_dir = os.path.join(os.path.expanduser('~'), 'ephys_data')

dc_mapping = {'bath': 0, 'clamp': 1}
feedback_resistors = [2.1]
capacitors = [0, 47, 247]
bath_res = [33, 100, 332]  # Clamp.configs['ADG_RES_dict'].keys()

# DEBUGGING
# feedback_resistors = feedback_resistors[-1:]
# capacitors = capacitors[-1:]
# bath_res = bath_res[-1:]

# Set up Experiment
setup_yaml_path = 'bathclamp_vclamp_step_response_setup.yaml'
cmd_protocol_path = 'bathclamp_vclamp_step_response_cmd.csv'
protocol = Protocol.create_from_csv(filepath=cmd_protocol_path, num_sweeps=1)
protocol.preview()
experiment = Experiment(protocol, setup_file_path=setup_yaml_path)
experiment.setup()

# Loop through different resistor, capacitor values
file_names = []
for fb_res in feedback_resistors:
    for cap in capacitors:
        for b_res in bath_res:
            config_updates = {
                'CCOMP': cap,
                'RF1': fb_res,
                'ADG_RES': b_res
            }
            file_name = ('-'.join([str(fb_res), str(cap), str(b_res)])).replace('.', '_') + '.h5'
            file_names.append(file_name)
            experiment.experiment_setup.daq_ports[dc_mapping['bath']]['clamp_configs'].update(config_updates)
            experiment.configure_clamps()
            experiment.record(clamp_num=dc_mapping['bath'], file_name=file_name, plot=False)    # TODO: update record to use Datastreams
            # input('Pausing...')

# Plot data
for file_name in file_names:
    # Plot using datastreams
    datastreams, log_info = rawh5_to_datastreams(
        data_dir=data_dir,
        infile=file_name,
        data_to_names=experiment.daq.ddr.data_to_names,
        daq=experiment.daq,
        phys_connections=experiment.create_phys_connections(),
        outfile=None
    )
    fig, ax = plt.subplots(2, 1)
    fig.suptitle('ADS data')
    # AMP OUT : observing (buffered/amplified) electrode P1 -- represents Vmembrane
    datastreams['P1'].plot(ax[0], {'marker': '.'})
    # CAL ADC : observing electrode P2 (configured by CAL_SIG2)
    datastreams['P2'].plot(ax[1], {'marker': '.'})

    fig, ax = plt.subplots()
    fig.suptitle('Overlay P1 and CMD')
    datastreams['P1'].plot(ax, {'marker': '.'})
    # TODO: use physical connections to allow for setting CMD0 in terms of physical units
    datastreams['CMD0'].plot(ax, {'marker': '.'})

    # estimate Im
    Cm = 33e-9
    fig, ax = plt.subplots()
    fig.suptitle('Overlay Meas. Im and Im estimate')
    datastreams['Im'].plot(ax, {'marker': '.', 'label': 'Meas. Im'})
    t = datastreams['P1'].create_time()
    t = datastreams['P2'].create_time()
    dt = t[1] - t[0]
    p1_diff = np.diff(datastreams['P1'].data)/dt
    p1_diff = np.zeros(t.shape)[:-1]
    ax.plot(t[:-1]*1e6, -Cm*p1_diff)
plt.show()

# Plot the different setups
fig, ax = plt.subplots()
phys_connections = experiment.create_phys_connections()
for file_name in file_names:
    datastreams, log_info = rawh5_to_datastreams(
        data_dir=data_dir,
        infile=file_name,
        data_to_names=experiment.daq.ddr.data_to_names,
        daq=experiment.daq,
        phys_connections=phys_connections,
        outfile=None
    )

    datastreams['Im'].plot(ax, {'marker': '.', 'label': file_name})
# Zoom to one protocol length
# Plot is in microseconds, protocol duration in milliseconds
ax.set_xlim([0, protocol.duration() * 1e3])
ax.legend(loc='upper right')
plt.show()