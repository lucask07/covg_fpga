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

dc_mapping = {'bath': 0, 'clamp': 1}
feedback_resistors = [2.1]
capacitors = [0, 47, 247]
bath_res = [33, 100, 332]  # Clamp.configs['ADG_RES_dict'].keys()

# Set up Experiment
setup_yaml_path = 'bathclamp_vclamp_step_response_setup.yaml'
cmd_protocol_path = 'bathclamp_vclamp_step_response_cmd.csv'
protocol = Protocol.create_from_csv(filepath=cmd_protocol_path, num_sweeps=1)
protocol.preview()
experiment = Experiment(protocol, setup_file_path=setup_yaml_path)
experiment.setup()
experiment.configure_clamps()
