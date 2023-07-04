"""Create a Protocol from a CSV.

Protocol -> Sweeps -> Epochs
"""

import matplotlib.pyplot as plt
from core import Protocol, Sequence

protocol = Protocol.create_from_csv(filepath='protocol.csv', num_sweeps=5)
protocol.preview()
sequence = Sequence(protocols=protocol)

protocol2 = Protocol.create_from_csv(filepath='protocol2.csv', num_sweeps=12)
protocol2.preview()


plt.show()


