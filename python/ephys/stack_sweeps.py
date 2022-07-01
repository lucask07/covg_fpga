"""Stack the separate Sweeps data as separate Matplotlib lines."""

from inspect import currentframe
from re import X
import numpy as np
import os
import matplotlib.pyplot  as plt
from pyripherals.utils import read_h5, to_voltage
from pyripherals.core import FPGA
from pyripherals.peripherals.DDR3 import DDR3
from core import Protocol

f = FPGA()
f.init_device()
ddr = DDR3(fpga=f, data_version='TIMESTAMPS')

file_name = '20220701-114930.h5'
data_dir = 'C:/Users/shog4177\Desktop/h5 file/new h5 abe'   # Path to the h5 file

_, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))
adc_data, timestamp, dac_data, ads, reading_error = ddr.data_to_names(chan_data)

# Voltage data in mV
voltage_data = np.array(to_voltage(adc_data[0], num_bits=16, voltage_range=10, use_twos_comp=True)) * 1e3
# Resistor value in kOhms
res = 33
# Current data in uA?
current_data = voltage_data / res

#numpy x axis

protocol_file = 'protocol.csv'
protocol_dir = ''   # Path to the protocol CSV
protocol = Protocol.create_from_csv(filepath=os.path.join(protocol_dir, protocol_file), num_sweeps=5)
sweep_length = len(protocol.sweeps[0].data()) * 2   # Number of data points in one sweep

#plot graph
plt.title('Current plot')
plt.xlabel('Time (in units)')
plt.ylabel('Current (uA)')
previousSweep = 0
sweep_pos = sweep_length
xOffset = 0
for i in range(len(protocol.sweeps)):
    #Plot time vs current in sweep length range
    sweep = current_data[previousSweep:sweep_pos]
    xAxis = _[previousSweep:sweep_pos]
    plt.plot(xAxis + xOffset, sweep)

    ##increment upper and lower sweep bounds by sweep length
    ## offset the next graph by sweep length (sweeplength = _[35000] in this example)
    print ("Sweep length " + str(sweep_pos))
    sweep_pos += sweep_length
    print ("previous sweep " + str(previousSweep))
    previousSweep += sweep_length
    xOffset -= _[sweep_length]

plt.xlim(0, 0.007)
plt.show()

# Use current_data and sweep_length to stack the sweeps on top of one another in the plot
