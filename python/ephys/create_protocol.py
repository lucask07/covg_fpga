"""Create a Protocol from a CSV.

Protocol -> Sweeps -> Epochs
"""

import pandas as pd
import matplotlib.pyplot as plt
from core import Epoch, Sweep, Protocol

df = pd.read_csv(filepath_or_buffer='protocol.csv')
df.fillna(0)
print(df)


epochs = []
first_column = True
for col in df:
    if first_column:
        first_column = False
        continue

    column = df[col]
    type, sample_rate, first_level, delta_level, first_duration, delta_duration = column
    if type=='Off':
        continue

    e = Epoch(first_level=int(first_level), delta_level=int(delta_level), first_duration=int(first_duration),
              delta_duration=int(delta_duration), type=type.capitalize(), sample_rate=sample_rate.capitalize())
    epochs.append(e)

sweep = Sweep(epochs=epochs)
protocol = Protocol(sweep=sweep, num_sweeps=5)
protocol_data = protocol.data()

# Plot Protocol over time
fig, ax = plt.subplots()
ax.plot(protocol_data)
plt.show()

protocol.preview()