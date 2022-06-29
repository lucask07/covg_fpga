"""Write a Protocol and read back the data from the cell."""

import matplotlib.pyplot as plt
from core import Protocol, Experiment

protocol = Protocol.create_from_csv(filepath='protocol.csv', num_sweeps=5)
protocol.preview()

# Pause to show user preview
plt.show()

# Run experiment
clamp_nums = [0, 1]
experiment = Experiment(protocol)
experiment.setup()
experiment.write_sequence(clamp_num=clamp_nums)
# time and data will be in milliseconds and millivolts
time, data = experiment.read_response(clamp_num=clamp_nums)
experiment.close()

# Plot data
fig, ax = plt.subplots(1, 2)
for clamp_num in clamp_nums:
    ax[clamp_num].plot(time, data[0])
    ax[clamp_num].set_xlabel('Time [ms]')
    ax[clamp_num].set_xlabel('Current [uA]')
    ax[clamp_num].set_title('Current Response')
plt.show()
