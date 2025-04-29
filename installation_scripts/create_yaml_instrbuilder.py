"""
This program tries to create a config yaml for instrbuilder
"""
import instrbuilder
from instrbuilder import instrument_opening

# find location of commands_csv
init_file_loc = instrbuilder.__file__
instrument_cmds = init_file_loc.replace('__init__.py', 'instruments/')
# initiate the yaml file
instrument_opening.init_yaml(csv_dir = instrument_cmds)
