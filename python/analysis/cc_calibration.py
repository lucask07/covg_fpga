"""
Oct 2022

Lucas Koerner, koerner.lucas@stthomas.edu

Analyze impedance analyzer spectrum to determine 

"""

import os
import sys
from time import sleep
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
from scipy.optimize import minimize, basinhopping
from analysis.clamp_data import adjust_step2, adjust_step3
from analysis.adc_data import im_conv
from datastream.datastream import h5_to_datastreams

"""
analyze data already captured
"""
if sys.platform == 'darwin':
    data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/cc_impulse/20230104/'
elif sys.platform == 'win32':
    data_dir = r'C:/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/cc_impulse/20230104/'

FS = 5e6
ds = {}
ds['CMD0'] = h5_to_datastreams(data_dir, 'CMD_impulse.h5')
ds['CC0'] = h5_to_datastreams(data_dir, 'CC_impulse.h5')

fig,ax = plt.subplots()
impulse = {}
for imp_on in ['CMD0', 'CC0']:
    step_idx = np.argmax(np.diff(ds[imp_on][imp_on].data) > 0)
    t0 = ds[imp_on][imp_on].create_time()[step_idx]
    impulse[imp_on], t_imp, t0 = ds[imp_on]['Im'].get_impulse(t0=t0)
    print(t0)

ax.plot(t_imp*1e6, -impulse['CMD0']*12, marker='+')
ax.plot(t_imp*1e6, -impulse['CC0'], marker='.')

# create a step function
t = ds[imp_on]['Im'].create_time()
t_idx = (t>(t0-350e-6)) & (t<(t0+400e-6)) # needs to have a length longer than t_imp so that 'valid' convolution works 
pulse_t = t[t_idx]

step_func = np.zeros(len(pulse_t))
step_func[pulse_t>t0] = 1

# runt_idx = np.argmin(step_func>0)

# # bounds for adjust_step2 
# ADJ_STP2 = True
# if ADJ_STP2:
#     bnds = ((-1, 1), (-5e-6, 5e-6),
#             (-1, 1), (2e3, 2.45e6), (-5e-6, 5e-6),
#             (-1, 1), (2e3, 2.45e6),(-5e-6, 5e-6),
#             (-1, 1), (2e3, 2.45e6), (-5e-6, 5e-6),
#             (-0.3, 0.3), (runt_idx-50, runt_idx+50), (runt_idx-20, runt_idx+80))

#     out_min = minimize(im_conv, x0=[-0.16, 0e-6,
#                                     -0.16, 100e3, 0e-6,
#                                     -0.05,100e3, 0e-6,
#                                     0.1, 100e3, 0e-6,
#                                     0.02, runt_idx, runt_idx+20],
#                         args=(impulse['CMD0'], step_func, impulse['CC0'], step_func, adjust_step2), bounds=bnds, method='L-BFGS-B')
#     new_cc_step2 = adjust_step2(out_min['x'], step_func)

#     print(out_min['x'])
#     fig,ax = plt.subplots()
#     ax.plot(new_cc_step2, marker='.')


# ADJ_STP3 = True
# if ADJ_STP3:
#     bnds = ((-10, 10), (-5e-6, 5e-6),
#             (-10, 10), (-5e-6, 5e-6),
#             (2e3, 1e6),
#             (2e3, 1e6))

#     out_min = minimize(im_conv, x0=[-0.16, 0e-6,
#                                     0.4, 0e-6,
#                                     100e3,
#                                     100e3], 
#                         args=(impulse['CMD0'], step_func, impulse['CC0'], step_func, adjust_step3), bounds=bnds, method='L-BFGS-B')
#     new_cc_step = adjust_step3(out_min['x'], step_func)

#     print(out_min['x'])
#     fig,ax = plt.subplots()
#     ax.plot(new_cc_step, marker='.')

SHGO = False
from scipy.optimize import shgo
if SHGO:
    bnds = ((-10, 10), (-2e-6, 5e-6),
            (-10, 10), (-2e-6, 5e-6),
            (5e3, 500e3),
            (5e3, 500e3))

    out_min3 = shgo(im_conv, bounds=bnds,
                        args=(impulse['CMD0'], step_func, impulse['CC0'], step_func, adjust_step3), 
                        minimizer_kwargs={'method':'SLSQP'}, iters=4, sampling_method='sobol')
    new_cc_step3 = adjust_step3(out_min3['x'], step_func)

    print(out_min3['x'])
    fig,ax = plt.subplots()
    ax.plot(new_cc_step3, marker='.')

BASIN = True
if BASIN:
    class RandomDisplacementBounds(object):
        """random displacement with bounds"""
        def __init__(self, bnds, stepsize=0.05):
            self.bnds = bnds
            self.bnds_range = [(b[1] - b[0]) for b in bnds]
            self.xcenter = [(b[1] - b[0])/2 + b[0] for b in bnds]
            self.stepsize = stepsize

        def __call__(self, x):
            """take a random step but ensure the new position is within the bounds"""
            xnew = np.array([])
            for idx,xs in enumerate(x):
                xtmp = xs + np.random.uniform(-self.bnds_range[idx]/2, self.bnds_range[idx]/2) # omit shape for a single scalar 
                xnew = np.append(xnew, np.clip(xtmp, self.bnds[idx][0], self.bnds[idx][1]))
            return xnew

    x0 = [-0.11, 0e-6,
          -0.1, 5e-6, 
          -0.1, 15e-6, 
          -0.1, 30e-6, 
           100e3, 10e3, 10e3]
    bnds = ((-0.2, -0.05), (0e-6, 4e-6),  # direct 
            (-1, 1), (5e-6, 50e-6),
            (-1, 1), (5e-6, 100e-6),
            (-1, 1), (0e-6, 50e-6),
            (50e3, 500e3),
            (1e3, 500e3),
            (1e3, 1e6))
    # define the new step taking routine and pass it to basinhopping
    take_step = RandomDisplacementBounds(bnds)

    minimizer_kwargs = { "method": "L-BFGS-B","bounds":bnds,"args": (impulse['CMD0'], step_func, impulse['CC0'], 
        step_func, adjust_step3)}

    out_min4 = basinhopping(im_conv, x0=x0,
                        minimizer_kwargs=minimizer_kwargs, take_step=take_step, niter=1000)
    new_cc_step4 = adjust_step3(out_min4['x'], step_func)

    print(out_min4['x'])
    fig,ax = plt.subplots()
    ax.plot(new_cc_step4, marker='.')

FS = 5e6
fig, ax = plt.subplots(3,1)
ax[0].plot(t[t_idx]*1e6, -ds['CMD0']['Im'].data[t_idx])
ax[0].set_xlim([t0*1e6-150, t0*1e6+200])
cmd_conv = np.convolve(impulse['CMD0'], step_func, mode='valid')
ax[1].plot(np.arange(len(cmd_conv))*1/FS*1e6, cmd_conv, label='Im via conv.')
ax[1].legend()
baseline_conv = np.sum(np.abs(np.convolve(impulse['CMD0'], step_func, mode='valid')))
print(f'Baseline, without CC, function evaluation {baseline_conv}')
# ax[2].plot(np.convolve(impulse['CMD0'], step_func, mode='valid') + np.convolve(impulse['CC0'], new_cc_step, mode='valid'), label='BLFS')
# ax[2].plot(np.convolve(impulse['CMD0'], step_func, mode='valid') + np.convolve(impulse['CC0'], new_cc_step3, mode='valid'), label='SHGO')
cmd_p_cc_conv = np.convolve(impulse['CMD0'], step_func, mode='valid') + np.convolve(impulse['CC0'], new_cc_step4, mode='valid')
opt_conv = baseline_conv = np.sum(np.abs(cmd_p_cc_conv))
print(f'With CC, function evaluation {baseline_conv}')
ax[2].plot(np.arange(len(cmd_p_cc_conv))*1/FS*1e6, cmd_p_cc_conv, label='BH')
ax[2].legend()