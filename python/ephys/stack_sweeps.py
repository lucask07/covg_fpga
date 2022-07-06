"""Stack the separate Sweeps data as separate Matplotlib lines."""

from inspect import currentframe
from re import X
import numpy as np
import os
import matplotlib.pyplot  as plt
import pandas as pd
import axon_text as atf
from pyripherals.utils import read_h5, to_voltage
from pyripherals.core import FPGA
from pyripherals.peripherals.DDR3 import DDR3
from core import Protocol

f = FPGA()
f.init_device()
ddr = DDR3(fpga=f, data_version='TIMESTAMPS')

file_name = '20220630-155747.h5'
data_dir = 'C:/Users/shog4177\Desktop/h5 file/'   # Path to the h5 file

_, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))
adc_data, timestamp, dac_data, ads, reading_error = ddr.data_to_names(chan_data)

print(len(adc_data[0]))
print(len(dac_data[1]))

# Voltage data in mV
voltage_data = np.array(to_voltage(adc_data[0], num_bits=16, voltage_range=10, use_twos_comp=True)) * 1e3
Voltage_data_reduced = voltage_data[0::2]
#Command voltage
Cmd_voltage_data = np.array(to_voltage(dac_data[1], num_bits=16, voltage_range=5, use_twos_comp=False))

# Resistor value in kOhms
res = 33
# Current data in uA?
current_data = voltage_data / res
current_data_reduced = Voltage_data_reduced / res
#plt.ion()

#numpy x axis

protocol_file = 'protocol.csv'
protocol_dir = ''   # Path to the protocol CSV
protocol = Protocol.create_from_csv(filepath=os.path.join(protocol_dir, protocol_file), num_sweeps=5)
sweep_length = len(protocol.sweeps[0].data()) * 2   # Number of data points in one sweep

#find portions of array 6000 - 30000 = Range without artifacts
#print(np.where(np.logical_and(_>=0.0012, _<=0.006)))

#plot graph
plt.title('Current plot')
plt.xlabel('Time (in units)')
plt.ylabel('Current (uA)')
previousSweep = 0
initialBaseline = 6000
incrementalBaseline = 30000
sweep_pos = sweep_length
xOffset = 0
incrementalColumn = 0
ATFfile = np.array([])
# Dac_ADC_DF = []
# df2 = pd.DataFrame(Dac_ADC_DF)
# df2.insert(0, column = "Trace #1 (μA)", value = current_data_reduced)
# df2.insert(1, column= "Trace #1 (vm)", value = Cmd_voltage_data)
# df2.to_csv("Simple.csv", index = False)

for i in range(len(protocol.sweeps)):
    #Plot time vs current in sweep length range
    sweep = current_data[previousSweep:sweep_pos]
    ATFFile = np.append(ATFfile, sweep)
    Cmd_Sweep = Cmd_voltage_data[previousSweep:sweep_pos]
    xAxis = _[previousSweep:sweep_pos]
    plt.plot(xAxis + xOffset, sweep)
    ##increment upper and lower sweep bounds by sweep length
    ## offset the next graph by sweep length (sweeplength = _[35000] in this example)
    #print ("Sweep length " + str(sweep_pos))
    sweep_pos += sweep_length
    #print ("previous sweep " + str(previousSweep))
    previousSweep += sweep_length
    xOffset -= _[sweep_length]
    print("Iavg for sweep " + str(i + 1) + " is " + str(np.average(current_data[initialBaseline:incrementalBaseline])))
    print("Standard deviation for sweep " + str(i + 1) + " is " +  str(np.std(current_data[initialBaseline:incrementalBaseline])))
    print("Current command voltage " + str(i + 1) + " is " +  str(np.average(Cmd_voltage_data[previousSweep:sweep_pos])))
    #35000 extrapolated from 0.007 offset to set sweep. 65000 from 35000+incrementalBaseline(30000)
    initialBaseline += 35000
    incrementalBaseline += 65000
    #df.insert(incrementalColumn, column = "Trace #" + str(incrementalColumn + 1) + " (μA)", value  = sweep)
    #df.insert(incrementalColumn, column = "Trace #" + str(incrementalColumn + 1) + " (vm)", value = Cmd_Sweep)
    incrementalColumn += 1

#df.insert(0, column = "Time (ms)", value = xAxis)

print(ATFfile)
#atf.write(out_file='copy.atf', out_atf=current_data)
#df.to_csv("Testfile.csv", index = False)

print(len(Voltage_data_reduced))
print(len(Cmd_voltage_data))

plt.xlim(0, 0.007)

fig, (ax1, ax2)  = plt.subplots(2, sharex = 'col', sharey=False)
ax1.plot(current_data_reduced)
ax2.plot(Cmd_voltage_data)


#[0::2]
plt.show()

# Use current_data and sweep_length to stack the sweeps on top of one another in the plot
