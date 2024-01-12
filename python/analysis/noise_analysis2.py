"""

Analysis of COVG data from model cell (h5, datastream-based)
Determine noise and the noise power spectrum 

2023/12/22

Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import scipy.signal as signal 
import glob 
import pandas as pd
from filters.filter_tools import butter_lowpass_filter
from datastream.datastream import h5_to_datastreams 
from analysis.adc_data import find_peak, calc_psd
from analysis.noise_analysis_tools import plot_psd_integrated_noise, print_experiment_metadata, get_clamp_config, filt_sig


sys.path.append('C:\\Users\\koer2434\\Documents\\covg\\my_pyabf\\pyABF\\src\\')
import pyabf 
from pyabf.tools.covg import interleave_np

# configure Matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()

# setup data directory
data_dir_base = 'C:\\Users\\koer2434\\Documents\\digital_covg\\data\\clamp\\'

# directory for output figures 
fig_dir = "/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/figures/figures2/"
fig, axs = plt.subplots(2,1)

fig_p1, axs_p1 = plt.subplots(2,1)


# open all files in the noise_sweep directory and get the r,c,i configuration 
meta = {'res': [], 'ccomp': [], 'in_amp': [], 'filename': []}

data_dir = os.path.join(data_dir_base, '20231221\\noise_sweep')
fs = glob.glob(data_dir + '\\*.h5')

for f in fs:
    datastreams = h5_to_datastreams(os.path.dirname(f), os.path.basename(f))

    try:
        r,c,i = get_clamp_config(datastreams)
        meta['res'].append(r)
        meta['ccomp'].append(c)
        meta['in_amp'].append(i)
        meta['filename'].append(f)
    except:
        pass

df = pd.DataFrame(meta)

idx = (df['res'] == 100) & (df['ccomp'] == 47) & (df['in_amp'] == 10)
filename = os.path.basename(df['filename'][idx].values[0])
print(filename)

for data_folder, filename, color, lbl in zip(['20231219', '20231221\\noise_sweep'], 
                                        ['20231219-191720_1.h5', filename],
                                        ['blue', 'red'], ['offset adj DAC', 'no offset DAC']):

    datastreams = h5_to_datastreams(os.path.join(data_dir_base, data_folder), filename)

    r,c,i = get_clamp_config(datastreams)
    print_experiment_metadata(datastreams)
    # noise analysis, ensure away from a peak 
    t_start = 0.1
    t_stop = 5

    t = datastreams['Im'].create_time()
    idx = (t > t_start) & (t < t_stop)
    print('-'*80)
    filtered_data = filt_sig(datastreams, idx, 
            fc_arr=[1e6, 500e3, 200e3, 100e3, 50e3, 30e3, 10e3, 3e3], 
            signal = 'Im')

    # Plot PSD integrated noise 
    y = datastreams['Im'].data[idx]
    fs = datastreams['Im'].sample_rate
    plot_psd_integrated_noise([axs[0], axs[1]], y, fs, datastreams, color=color, label=lbl)
    axs[0].legend()


    t = datastreams['P1'].create_time()
    idx = (t > t_start) & (t < t_stop)
    print('-'*80)
    filtered_data = filt_sig(datastreams, idx, 
            fc_arr=[125e3, 100e3, 50e3, 30e3, 10e3, 3e3], 
            signal = 'P1')

    # Plot PSD integrated noise 
    y = datastreams['P1'].data[idx]
    if lbl == 'no offset DAC': # the conversion factor for P1 was not yet correct for the unity gain buffer (was probably calculated as 1.7)
        increase_scale = 1.7 # need to check the scaling with the new modification 
        y = y*increase_scale
    fs = datastreams['P1'].sample_rate
    plot_psd_integrated_noise([axs_p1[0], axs_p1[1]], y, fs, datastreams, color=color, label=lbl, sig_type='V')
    axs_p1[0].legend()