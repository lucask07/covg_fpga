"""

Analysis of COVG data from model cell (h5, datastream-based)
Step response similar to Dagan CA-1B data from Dr. Gil Toombes

Plot:
1) I
2) Q 

Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import scipy.signal as signal 
from filters.filter_tools import butter_lowpass_filter
from datastream.datastream import h5_to_datastreams 
from analysis.adc_data import find_peak, calc_psd

sys.path.append('C:\\Users\\koer2434\\Documents\\covg\\my_pyabf\\pyABF\\src\\')
import pyabf 
from pyabf.tools.covg import interleave_np

# configure Matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()


def get_clamp_config(datastreams):
    # awkward dictionary reverse lookup 
    clamp_num = list(datastreams.dc_mapping.keys())[list(datastreams.dc_mapping.values()).index('bath')]
    rtia = datastreams.dc_configs[clamp_num]['ADG_RES']
    ccomp = datastreams.dc_configs[clamp_num]['CCOMP']
    in_amp = datastreams.dc_configs[clamp_num]['gain']

    return rtia, ccomp, in_amp

def plot_psd_integrated_noise(axs, y, fs, datastreams=None, color='b', label='', sig_type='I'):

    if axs is None:
        fig,axs = plt.sublots((2,1))
    else:
        fig = None

    # TODO: get 
    if datastreams is None:
        rtia = ''
        ccomp = ''
        in_amp = ''
    else:
        rtia, ccomp, in_amp = get_clamp_config(datastreams)

    if sig_type == 'I':
        scale = 1e9 # nA 
        ylabels = ['I/$\sqrt{Hz}$ [nA]', 'Integrated noise [nA RMS]']
    else:
        scale = 1e6
        ylabels = ['V/$\sqrt{Hz}$ [$\mu$V]', 'Integrated noise [$\mu$V RMS]']

    f, im_pd = calc_psd(y, fs, nperseg=1024*8, scaling='spectrum')


    label = f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp} ' + label

    axs[0].loglog(f, np.sqrt(im_pd)*scale, marker='*', label=label, color=color)
    axs[0].set_ylabel(ylabels[0])
    axs[0].set_xlabel('f [Hz]')

    axs[1].loglog(f, np.sqrt(np.cumsum(im_pd*scale**2)), marker='*', label=label, color=color)
    axs[1].set_ylabel(ylabels[1])
    axs[1].set_xlabel('f [Hz]')

    print(f'RTIA = {rtia}; CComp = {ccomp}')

    return fig 


def filter_ds(ds, fc, idx=None):
    fs = ds.sample_rate
    if idx is None:
        y = ds.data 
    else:
        y = ds.data[idx]
    while(fs/fc > 20):
        y = signal.decimate(y, 10)
        fs = fs/10
    else: 
        y = y
        fs = fs
    y_filt = butter_lowpass_filter(y, cutoff=fc, fs=fs, order=5)
    return y_filt, fs 

def get_timeidx(data, fs, time_range, t0=0):
    '''
    data: array of data (to determine the length )
    fs : sampling frequency 
    time_range is a 2 element list in us 
    t0: is an offset in us 
    '''
    t = np.arange(len(data))*1/fs*1e6 - t0
    idx = (t > time_range[0]) & (t < time_range[1])   

    return idx, t 

def plot_timedomain(datastreams, signals=['Im', 'P1', 'CMD0']):

    fig,ax = plt.subplots((len(signals), 1))

    for i, s in enumerate(signals):
        ax[i].plot(datastreams[s].create_time(), datastreams[s].data)

    return fig


def filt_sig(datastreams, idx, fc_arr=[1e6, 500e3, 200e3, 100e3, 50e3, 30e3, 10e3, 3e3], signal = 'Im'):
    # filter and find a section in time away from a step to determine noise 
    # idx: index to crop the input signal 
    filtered_data = {}

    for fc in fc_arr:
        y_filt, fs = filter_ds(datastreams[signal], fc, idx)
        # crop y_fliter to prevent transients from the filter itself.
        y_filt = y_filt[100:]
        filtered_data[fc] = {'data': y_filt, 'fs':fs, 'noise': np.std(y_filt)}
        print(f'Noise of {filtered_data[fc]["noise"]} with cutoff of {fc}')

    return filtered_data


def print_experiment_metadata(datastreams):

    for k in datastreams.experiment_info:
        print(f'{k}: {datastreams.experiment_info[k]}')


def create_time(y, fs):
    # alternative method to generate a time trace 
    t = np.linspace(0, len(y)-1,len(y))*1/fs

    return t 


if 0:
    # test with a sine-wave, do I get the correct RMS amplitude from integrated power spectrum?
    fig_t, ax_t = plt.subplots()

    fs = 5e6
    f = 1e3
    amp = 1
    N = 10000000
    t = np.arange(N)*(1/fs)
    y = amp*np.sin(2*np.pi*t*f)
    f, im_pd = calc_psd(y, fs, nperseg=1024*1024, scaling='spectrum')

    ax_t.loglog(f, np.sqrt(im_pd), marker='*')
    ax_t.set_ylabel('V/$\sqrt{Hz}$ [V]')
    ax_t.set_xlabel('f [Hz]')

    fig_t, ax_t = plt.subplots()

    ax_t.loglog(f, np.cumsum(im_pd), marker='*')
    ax_t.set_ylabel('Integrated noise [$V^2$]')
    ax_t.set_xlabel('f [Hz]')