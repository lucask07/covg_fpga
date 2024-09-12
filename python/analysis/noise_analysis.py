"""
Noise Analysis of COVG data from model cell (h5, datastream-based)
Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import scipy.signal as signal 
from scipy.integrate import cumulative_trapezoid
import itertools 

from filters.filter_tools import bessel_lowpass_filter, butter_lowpass_filter
from datastream.datastream import h5_to_datastreams 
from analysis.adc_data import find_peak, calc_psd
from analysis.utils import my_savefig, fig_size # also configures matplotlib defautls 

# configure Matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()

# setup data directory
data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    print('linux directory not yet configured')
elif sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp/"
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/clamp/')

figure_dir = '/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/figures/step/'

if sys.platform == "darwin":
    figure_dir_paper = '/Users/koer2434/My Drive/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/step/'
elif sys.platform == "win32":
    figure_dir_paper = r'C:/Users/Public/Documents/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/step/'

fig_names = {}
SAVE_FIG = False

def filter_fc(y, fs, fc, REMOVE_DC = True):

    if REMOVE_DC:
        y = y - np.mean(y)
    while(fs/fc > 20):
        y = signal.decimate(y, 10)
        fs = fs/10
    else: 
        y = y
        fs = fs

    y_filt = bessel_lowpass_filter(y, cutoff=fc, fs=fs, order=5)
    filt_t = np.linspace(0, len(y_filt)-1,len(y_filt))*1/fs

    return y_filt, filt_t


data_dir_end = r'20240621a'
#data_dir_end = r'20240906'
#data_dir_end = r'20240910a'
data_dir_end = r'20240910'
data_dir_end = r'20240911'
data_dir_end = r'20240912'


data_dir = os.path.join(data_dir_covg, data_dir_end)

filename = 'initial_startup_{}rf_{}ccomp.h5'
filename = 'step_rtia{}_ccomp{}_cmd{}.h5'

time_range = [-50, 250] # [us] before and after peak; datastream plotting uses units of us; for step_info will expand to 400 us for slow rtia values 

# clamp board configuration 
rtia = 33 # kilo-ohms 
ccomp = 47 # pF 
in_amp_arr = 2 # gain of instrumentation amplifier 
cmd = 719

def noise_analysis(datastreams, rtia, ccomp, in_amp, t0_us, t0_us_stop, res, PLT=True):
    # noise analysis, ensure away from a peak 
    # results for noise analysis, plot noise spectrum, integrated noise, RMS noise vs. fc (return a results dictionary), total length of measurement 
    # inputs: datastreams, rtia, inamp,  

    t_start = t0_us/1e6 + 2e-3  # 2 ms 
    t_stop = t0_us_stop/1e6 - 2e-3 # 2 ms 
    print(f'Noise analysis from {t_start} to {t_stop} for a total length of {t_stop-t_start}')

    t = datastreams['Im'].create_time()
    idx = (t > t_start) & (t < t_stop)
    y = datastreams['Im'].data[idx]
    fs = datastreams['Im'].sample_rate

    f, im_pd = calc_psd(y, fs, nperseg=1024*8, scaling='spectrum')
    if PLT:
        fig, ax = plt.subplots(figsize=fig_size)
        ax.loglog(f, np.sqrt(im_pd)*1e9, marker='o', color='k')
        ax.set_ylabel('I/$\sqrt{Hz}$ [nA]')
        ax.set_xlabel('f [Hz]')

        fig, ax = plt.subplots(figsize=fig_size)
        ax.loglog(f, np.cumsum(im_pd*1e9**2), marker='o', color='k')
        ax.set_ylabel('Int. noise [nA$^2$]')
        ax.set_xlabel('f [Hz]')
        my_savefig(fig, figure_dir_paper, f'integrated_noise_psd_rtia{rtia}_CComp{ccomp}_inamp{in_amp}')

    print(f'RTIA = {rtia}; CComp = {ccomp}')
    for fc in [1e6, 500e3, 200e3, 100e3, 50e3, 30e3, 10e3, 3e3]:
        fs = datastreams['Im'].sample_rate
        y = datastreams['Im'].data[idx]
        y_filt, filt_t = filter_fc(y, fs, fc, REMOVE_DC = True)

        # append results 
        dc_num = next(key for key, value in datastreams.dc_mapping.items() if value == 'bath')
        in_amp = datastreams.dc_configs[dc_num]['gain']
        rtia = datastreams.dc_configs[dc_num]['ADG_RES']
        ccomp = datastreams.dc_configs[dc_num]['CCOMP']
        res['rtia'].append(rtia)
        res['ccomp'].append(ccomp)
        res['in_amp'].append(in_amp)
        res['fc'].append(fc)
        res['im_std'].append(np.std(y_filt))

    return res 

# 2x1 subplot for manuscript 
fs = fig_size 
# increase height to support 2x1 
fs = (fig_size[0], fig_size[1]*1.2) # was 1.8
fig_m, ax_m = plt.subplots(figsize = fs, nrows=2, ncols=1)

# find all cmd_vals by inspecting the directory 
import glob 
fs = glob.glob(data_dir + "/step*.h5")
cmd_vals = []
for f in fs:
    head, tail = os.path.split(f)
    cmd_vals.append(int(tail.split('.h5')[0].split('cmd')[1]))
cmd_vals = np.unique(np.asarray(cmd_vals))

# find the peak once so that this doesn't break with CMD = 0 
rtia = 33
ccomp = 47 
cmd = 719
datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, cmd))
# append results 
dc_num = next(key for key, value in datastreams.dc_mapping.items() if value == 'bath')
in_amp = datastreams.dc_configs[dc_num]['gain']
rtia = datastreams.dc_configs[dc_num]['ADG_RES']
ccomp = datastreams.dc_configs[dc_num]['CCOMP']

pos_pks = find_peak(datastreams['CMD0'].create_time(), np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)
neg_pks = find_peak(datastreams['CMD0'].create_time(), -np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)

print(pos_pks)
print(neg_pks)

# Need to find the peaks with a large command value and then reuse
try:
    t0_us = pos_pks[0][0]*1e6
except: # if no peak is found use the logfile information in datastreams
    print('Could not find a positive peak')
    t0_us = datastreams.ddr_step_peak*1e6
try:
    t0_us_stop = neg_pks[0][0]*1e6
except:
    print('Could not find a negative peak')
    t0_us_stop = datastreams.ddr_step_peak*1e6*2

noise_res = {'rtia':[], 'ccomp':[], 'in_amp':[], 'fc':[], 'im_std':[]}

# make PSD and integrated noise plots for 
# RTIA = 33k, ccomp = 47 
# RTIA = 100k, ccomp = 47 
# RTIA = 333k, ccomp = 4700 
# RTIA = 1M, ccomp = 4700 

fig1,ax1=plt.subplots(figsize=(fig_size[0], fig_size[1]*0.8))
fig2,ax2=plt.subplots(figsize=(fig_size[0], fig_size[1]*0.8))
fig3,ax3=plt.subplots(figsize=(fig_size[0], fig_size[1]*0.8))

PLT_SPECTRA = False
for in_amp in [in_amp_arr]: # not used in most experiments
    for ccomp in [47, 4700]:
        speed = 'fast' if ccomp==47 else 'slow' 
        for rtia in [33, 100, 332, 1000]:
#        for rtia in [33]:
            for cmd in [0, 719]:
                datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, cmd))
                if cmd==0:
                    # confirm daughter card configuration 
                    # find socket of bath clamp 
                    dc_num = next(key for key, value in datastreams.dc_mapping.items() if value == 'bath')
                    inamp_gain = datastreams.dc_configs[dc_num]['gain']
                    rf = datastreams.dc_configs[dc_num]['ADG_RES']
                    ccomp = datastreams.dc_configs[dc_num]['CCOMP']
                    # Im conversion factor 
                    im_cf = datastreams['Im'].conversion_factor 
                    print(f'bath daughter card. InAmp = {inamp_gain}; Rf = {rf}; ccomp = {ccomp}; Im conversion factor = {im_cf}')

                    # run noise analysis -- since cmd == 0 can use the whole trace 
                    t = datastreams['Im'].create_time()*1e6
                    print(f'Noise analysis loop: t0 {t0_us}, max time {np.max(t)}')
                    noise_res = noise_analysis(datastreams, rtia, ccomp, in_amp, t0_us, np.max(t), noise_res, PLT=False)

                    if PLT_SPECTRA:
                        t = datastreams['Im'].create_time()
                        idx = (t > t0_us/1e6) & (t < np.max(t)) # start at the first detected peak just so that the signal has time to settle.
                        y = datastreams['Im'].data[idx]
                        fs = datastreams['Im'].sample_rate
                        ax3.plot(t[idx], y) 

                        f, im_pdensity = calc_psd(y, fs, nperseg=1024*8, scaling='density') # was spectrum, density is the default has units of V^2/Hz
                        f, im_spectrum = calc_psd(y, fs, nperseg=1024*8, scaling='spectrum') # was spectrum, density is the default has units of V^2/Hz

                        if ( ((rtia==33) & (ccomp==47)) | ((rtia==100) & (ccomp==47)) | ((rtia==332) & (ccomp==4700)) | ((rtia==1000) & (ccomp==4700))):
                            ax1.loglog(f, np.sqrt(im_pdensity)*1e9, marker='.', label=f'{rtia} k$\Omega$, {speed}')
                            # note only **2 for the nA conversion factor 
                            # https://docs.scipy.org/doc/scipy/tutorial/signal.html#tutorial-spectralanalysis
                            ax2.loglog(f, np.sqrt(np.cumsum(im_spectrum*1e9**2)), marker='.', label=f'{rtia} k$\Omega$, {speed}')
if PLT_SPECTRA:
    ax1.set_ylabel('I/$\sqrt{Hz}$ [nA]')
    ax1.set_xlabel('f [Hz]')
    ax1.set_xlim([400, 2.5e6])
    ax1.legend()
    my_savefig(fig1, figure_dir_paper, f'noise_psd')

    ax2.set_ylabel('Integrated noise [nA]')
    ax2.set_xlabel('f [Hz]')
    ax2.set_xlim([400, 2.5e6])
    ax2.set_ylim([0.2, 3e2])
    ax2.legend()
    my_savefig(fig2, figure_dir_paper, f'integrated_noise')

    ax3.set_ylabel('Im')
    ax3.set_xlabel('t [s]')
    ax3.legend()
    my_savefig(fig3, figure_dir_paper, f'noise_time_trace')

# pandas dataframe to summarize results
df_noise = pd.DataFrame(noise_res)
df_noise.to_csv(os.path.join(figure_dir_paper, f'noise_summary_{data_dir_end}_inamp{in_amp}.csv'), index=False)
# print noise results 
print('--'*40)
print('Noise summary')
ccomp = 47
for rtia in [33, 100, 332, 1000]:
    for fc in np.unique(df_noise['fc']):
        condition = (df_noise.rtia==rtia) & (df_noise.ccomp==ccomp) & (df_noise.fc == fc)
        print(f'rtia={rtia}, fc={fc}: {df_noise[condition]["im_std"]*1e9}')

ccomp = 47
condition = (df_noise.ccomp==ccomp) & ((df_noise.fc == 3000) | (df_noise.fc == 10000) | (df_noise.fc == 100000))
print(df_noise[condition])
print('--'*100)
ccomp = 4700
condition = (df_noise.ccomp==ccomp) & ((df_noise.fc == 3000) | (df_noise.fc == 10000) | (df_noise.fc == 100000))
print(df_noise[condition])