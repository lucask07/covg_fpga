"""Stack the separate Sweeps data as separate Matplotlib lines."""

import numpy as np
import os
from pyripherals.utils import read_h5, to_voltage
from pyripherals.core import FPGA
from pyripherals.peripherals.DDR3 import DDR3
from core import Protocol

f = FPGA()
f.init_device()
ddr = DDR3(fpga=f, data_version='TIMESTAMPS')

file_name = '20220630-114826.h5'
data_dir = ''   # Path to the h5 file

_, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))
adc_data, timestamp, dac_data, ads, reading_error = ddr.data_to_names(chan_data)

# Voltage data in mV
voltage_data = np.array(to_voltage(adc_data[0], num_bits=16, voltage_range=10, use_twos_comp=True)) * 1e3
# Resistor value in kOhms
res = 33
# Current data in uA?
current_data = voltage_data / res

protocol_file = 'protocol.csv'
protocol_dir = ''   # Path to the protocol CSV
protocol = Protocol.create_from_csv(filepath=os.path.join(protocol_dir, protocol_file), num_sweeps=5)
sweep_length = len(protocol.sweeps[0].data())   # Number of data points in one sweep

# Use current_data and sweep_length to stack the sweeps on top of one another in the plot
