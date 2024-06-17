"""
June 2024
Lucas Koerner, koerner.lucas@stthomas.edu
Analyze impedance analyzer spectrum to determine resistances and capacitances 

A square-wave with a current amplitude is used for static resistance
A sinusoid at varying frequencies is measured to fit to a transfer function and derive an RC circuit 

"""

from math import ceil
import os
import sys
from time import sleep
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
import logging as log
import glob 
import scipy.signal as signal 

from filters.filter_tools import butter_lowpass_filter
from datastream.datastream import h5_to_datastreams, rawh5_to_datastreams  

# fit square wave 
# for publication figures 
from analysis.utils import my_savefig, fig_size, fig_dir # also configures matplotlib defautls 

def filter_fc(y, fs, fc, REMOVE_DC = True):

    if REMOVE_DC:
        y = y - np.mean(y)
    while(fs/fc > 20):
        y = signal.decimate(y, 10)
        fs = fs/10
    else: 
        y = y
        fs = fs

    y_filt = butter_lowpass_filter(y, cutoff=fc, fs=fs, order=5)
    filt_t = np.linspace(0, len(y_filt)-1,len(y_filt))*1/fs

    return y_filt, filt_t


PLT = True
capture_date = '20240522' # Vsense step response 
if sys.platform == 'darwin':
    data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/{}/'.format(capture_date)
elif sys.platform == 'win32':
    data_dir = 'C:/Users/koer2434/Documents/covg/data/clamp/{}/'.format(capture_date)

fig, ax = plt.subplots(figsize=fig_size)
fc = 250e3
for re, re_val in zip(['100k', '200k', '475k', '1000k'], [100e3, 200e3, 475e3, 1000e3]): 

    files_found = glob.glob(data_dir + f'/*{re}.h5')
    print(files_found)
    file_name = os.path.split(files_found[0])[1]
    datastreams = h5_to_datastreams(data_dir, file_name)
    t0 = 0.012497
    if re == '100k':
        y = datastreams['I'].data
        t = datastreams['I'].create_time()
        print(f'fs = {1/(t[1]-t[0])/1e3} [kHz]')
        y,t = filter_fc(y, 1/(t[1]-t[0]), fc, REMOVE_DC = False)
        # datastreams['I'].plot(ax, {'label': 'I'})
        ax.plot((t-t0)*1e6, y*1e3, label='I', linestyle='--')
    for n in ['V1']:
        y = datastreams[n].data
        t = datastreams[n].create_time()
        y,t = filter_fc(y, 1/(t[1]-t[0]), fc, REMOVE_DC = False)
        # datastreams['I'].plot(ax, {'label': 'I'})
        lbl = n + ': ' + f'{re.replace("k","")}' + r'$\, k\Omega$'
        print(lbl)
        # ax.plot((t-t0)*1e6, y*1e3, label=lbl)
        ax.plot((t-t0)*1e6, y*1e3, )

        step_info = datastreams['V1'].stepinfo_range([12400e-6, 12600e-6])

        par_cap = step_info['RiseTime']/np.log(9)/(100e3 + re_val)
        step_info['capacitance'] = par_cap

        print(f'Rise-time {step_info["RiseTime"]} and tau {step_info["RiseTime"]/np.log(9)}, capacitance {par_cap}')
        print(f'Rise-time: {step_info["RiseTime"]} with {re}')

    ax.annotate(r'$RC \uparrow $', xytext=(3,-2), xy=(18,-20), arrowprops=dict(arrowstyle='-|>'))

        # datastreams[n].plot(ax, {'label': n})
ax.legend()
ax.set_xlabel('t [$\mu$s]')
ax.set_ylabel('V [mV]')
ax.set_xlim([-30, 30])
my_savefig(fig, os.path.join(fig_dir, 'calibration'), f'calibration_vsense_step_all_rs')
    # TODO: measure with model cell disconnected to remove slow decays, 
    #       fit to determine amplitude 
    #       measure with 2 different attenuators 
    #       check datastreams code to figure out V1 vs V1s -- Vls is from the voltage sense board, V1 is AMP_OUT on the clamp board. Difference is only the attenuation.
    #       confirm that AMP_OUT on the clamp board has x1 gain -- must be since correction for the attenuation is all that's needed to align
fig, ax = plt.subplots(figsize=fig_size)
gain = 60
# for n in ['V1', 'I', 'V1s']:
for n in ['V1', 'I']:

    if n == 'V1':
        scale = 10**(-13/20)*gain
    elif n == 'V1s':
        scale = gain
    else:
        scale = 1
    data = datastreams[n].data/datastreams[n].conversion_factor/scale # convert to ADS8686 codes since we are trying to determine various gains!
    t =  datastreams[n].create_time()
    ax.plot(t, data, label=n)
ax.legend()

my_savefig(fig, os.path.join(fig_dir, 'calibration'), f'calibration_vsense_step_{re}')