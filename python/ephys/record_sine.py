"""Write and read a continuous sine wave with an updating graph."""

from core import Protocol, Experiment


# Run experiment
setup_yaml_path = 'record_sine.yaml'

clamp_nums = [0]
protocol = Protocol.create_from_csv(filepath='protocol.csv', num_sweeps=14)
experiment = Experiment(protocol, setup_file_path=setup_yaml_path)
experiment.setup()
experiment.configure_clamps()

experiment.record_sine(clamp_num=clamp_nums, amplitude=1, frequency=1e3, save_data=False)
