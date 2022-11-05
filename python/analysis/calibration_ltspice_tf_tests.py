"""

Oct 2022

Lucas Koerner, koerner.lucas@stthomas.edu
"""

import os
import sys
from time import sleep
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

import ltspice # for comparison to simulations 

from calibration.cal_fits import elec_r_cc, vclamp_tf, lpf_tf

file = '/Users/koer2434/My Drive/UST/research/covg/simulations/covg_circuit_sims/theory/calibrations/clamp_electrodes.raw'

l = ltspice.Ltspice(file)
l.parse()
f = l.get_frequency()
vout = l.get_data('V(OUT)')

a,p = vclamp_tf(f, r5=100e3, cm=33e-9)

fig, ax = plt.subplots()
ax.semilogx(f, np.abs(vout), label='LTSpice')
ax.semilogx(f, a, label='TF')
fig.legend()