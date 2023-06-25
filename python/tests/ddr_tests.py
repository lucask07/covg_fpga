import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3

f = FPGA()
f.init_device()

ddr = DDR3(f)

frequencies = np.array([40, 200, 10e3])

# if you would like to avoid reading out too much data its possible to use smaller periods and then only readout 
# the first bits of the last frequency
chan_data, freq, indices = ddr.make_chirp(amplitude=100, frequencies=frequencies, periods=np.array([60,60,60]), 
                   offset=1000)

len_first_f = 60*frequencies[0]/DDR3.UPDATE_PERIOD
print(len_first_f)
plt.plot(chan_data)
