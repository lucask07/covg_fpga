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
import scipy.integrate as integrate 
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
data_dir_base = os.path.expanduser('~')
if sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp/{}{:02d}{:02d}"
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/{}{:02d}{:02d}')

fig_dir = "/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/figures/figures2/"

# data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20230619'
data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20230630'
data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20230701'
# comparison with Dagan data from Richmond 
data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20231204'
#data_dir = r'C:\Users\koer2434\Documents\digital_covg\data\clamp\20231211'

#filename = 'datastreams2_output_quietdacs_rtia{}_ccomp{}.h5' # 3 uses RF1 = 30
filename = 'noisetest9_quietdacs_rtia{}_ccomp{}.h5'
filename = 'clamptest1_rtia{}_ccomp{}.h5'
filename = 'clamptest8_quietdacsFalse_rtia{}_ccomp{}.h5'
filename = 'clamptest1_quietdacsFalse_rtia{}_ccomp{}_inamp{}.h5'
filename = 'datastreams_output_20231204-161527_30.h5' # rtia = 100 kOhm 
#filename = 'datastreams_output_protocols20231211-163006_30.h5' # rtia = 100 kOhm 

dagan = pyabf.ABF(r'C:\Users\koer2434\OneDrive - University of St. Thomas\UST\research\covg\fpga_and_measurements\data_sharing\dagan_data\Richmond Data\Steps\0.1 Gain 10mV Steps.abf')

dagan_data = {}
sweep_num = 4
# sweeps 0: 0mV, 1: 10mV, ... ,4: 40 mV
figd,axd=plt.subplots( 2,1 , figsize=(4,3))
# membrane current 
dagan.setSweep(sweepNumber=sweep_num, channel=0)
dagan_data['time'] = dagan.sweepX
dagan_data['im'] = dagan.sweepY
dagan_data['CMD'] = dagan.sweepC # only non-zero for channel 0 

# membrange voltage 
dagan.setSweep(sweepNumber=sweep_num, channel=1)
dagan_data['vm'] = dagan.sweepY
dagan_data['sample_rate'] = dagan.dataRate
dagan_data['peak_time'] = 52.83e-3 

time_range = [-50, 400] # [us] before and after peak; datastream plotting uses units of us
t = (dagan_data['time']-dagan_data['peak_time'])*1e6
idx = (t > time_range[0]) & (t < time_range[1])

axd[0].plot(t[idx], dagan_data['im'][idx]/1e3)
axd[1].plot(t[idx], dagan_data['vm'][idx])

for i in range(2):
    axd[i].set_xlim([time_range[0], time_range[1]])

rtia = 100
ccomp = 47
in_amp = 2

figs = []
axs = []
for i in range(8):
    fig, ax=plt.subplots()
    figs.append(fig)
    axs.append(ax)

filtered_current = {}

for rtia in [100]:
    datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, in_amp))
    pos_pks = find_peak(datastreams['CMD0'].create_time(), np.diff(datastreams['CMD0'].data), th=0.2e-3, height=0.8e-3, distance=100)
    neg_pks = find_peak(datastreams['CMD0'].create_time(), -np.diff(datastreams['CMD0'].data), th=0.2e-3, height=0.8e-3, distance=100)

    print(pos_pks)
    print(neg_pks)

    try:
        t0_us = pos_pks[0][0]*1e6
    except: # if no peak is found use the logfile information in datastreams. Might not be in the log-file 
        t0_us = datastreams.ddr_step_peak*1e6
    try:
        t0_us_stop = neg_pks[0][0]*1e6
    except:
        t0_us_stop = datastreams.ddr_step_peak*1e6*2

    # plot current Im 
    t = datastreams['Im'].create_time()*1e6 - t0_us
    idx = (t > time_range[0]) & (t < time_range[1])
    y = datastreams['Im'].data[idx]
    y = y - np.average(y[-100:]) # remove steady-state current 

    axs[0].plot(t[idx], y/np.sum(y), label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
    axs[0].set_xlim(time_range)
    axs[0].set_xlabel('t [$\mu$s]')
    axs[0].set_ylabel('I (a.u.)')

    axs[7].plot(t[idx], y*1e6, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
    axs[7].set_xlim(time_range)
    axs[7].set_xlabel('t [$\mu$s]')
    axs[7].set_ylabel('I (uA)')

    axs[1].plot(t[idx], np.cumsum(y)/np.sum(y), label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
    axs[1].set_xlim(time_range)
    axs[1].set_xlabel('t [$\mu$s]')
    axs[1].set_ylabel('Q (a.u.)')

    # plot P1 voltage 
    t = datastreams['P1'].create_time()*1e6 - t0_us
    idx = (t > time_range[0]) & (t < time_range[1])
    y = datastreams['P1'].data[idx]
    y_ss = np.average(y[-100:])

    axs[2].plot(t[idx], y/y_ss, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
    axs[2].set_xlim(time_range)
    axs[2].set_xlim(time_range)
    axs[2].set_xlabel('t [$\mu$s]')
    axs[2].set_ylabel('P1')

    # noise analysis, ensure away from a peak 
    t_start = t0_us/1e6 + 1e-3 
    t_stop = t0_us_stop/1e6 - 1e-3 

    t = datastreams['Im'].create_time()
    idx = (t > t_start) & (t < t_stop)
    y = datastreams['Im'].data[idx]
    fs = datastreams['Im'].sample_rate

    f, im_pd = calc_psd(y, fs, nperseg=1024*8, scaling='spectrum')

    axs[3].loglog(f, np.sqrt(im_pd)*1e9, marker='*', label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
    axs[3].set_ylabel('I/$\sqrt{Hz}$ [nA]')
    axs[3].set_xlabel('f [Hz]')

    axs[4].loglog(f, np.cumsum(im_pd*1e9**2), marker='*', label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
    axs[4].set_ylabel('Integrated noise [nA$^2$]')
    axs[4].set_xlabel('f [Hz]')

    print(f'RTIA = {rtia}; CComp = {ccomp}')

    def filter_ds(ds, fc):
        fs = ds.sample_rate
        y = ds.data 
        y_len = len(y)
        while(fs/fc > 20):
            y = signal.decimate(y, 10)
            fs = fs/10
        else: 
            y = y
            fs = fs
        y_filt = butter_lowpass_filter(y, cutoff=fc, fs=fs, order=5)
        dec_factor = y_len/len(y_filt)
        return y_filt, fs, dec_factor

    def get_timeidx(data, fs, time_range, t0=0):
        '''
        data: array of data (to determine the length )
        fs : sampling frequency 
        time_range is a 2 element list in us 
        t0: is an offset in us 

        returns:
        idx 
        time array in us 
        '''
        t = np.arange(len(data))*1/fs*1e6 - t0
        idx = (t > time_range[0]) & (t < time_range[1])   
 
        return idx, t 

    # filter and find a section in time away from a step to determine noise 
    fig_noise,ax_noise=plt.subplots()
    for fc in [1e6, 500e3, 200e3, 100e3, 50e3, 30e3, 10e3, 3e3]:
        y_filt, fs, dec_factor = filter_ds(datastreams['Im'], fc)
        print(f'Filtering: {fc}')
        filtered_current[fc] = {'data': y_filt, 'fs':fs}
        idx_noise, t_noise = get_timeidx(y_filt, filtered_current[fc]['fs'], [60000, 180000], t0_us)
        ax_noise.plot(t_noise[idx_noise], y_filt[idx_noise])
        print(f'Noise of {np.std(y_filt[idx_noise])} with cutoff of {fc}')

    filt_t = np.linspace(0, len(y_filt)-1,len(y_filt))*1/fs
    axs[5].plot(filt_t, y_filt, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}', marker='.')
    axs[5].set_xlabel('t')

    f, im_pd = calc_psd(y_filt, fs, nperseg=1024)
    axs[6].loglog(f, im_pd, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}', marker='.')
    axs[6].set_xlabel('f [Hz]')

    for i in range(8):
        axs[i].legend()

# plot current Im 
fig,ax = plt.subplots(2,1)
t0_us = pos_pks[0][3]*1e6 # 40 mV 

for fc in [30e3]:
    data = filtered_current[fc]['data']
    idx, t = get_timeidx(data, filtered_current[fc]['fs'], time_range, t0_us)
    ax[0].plot(t[idx], data[idx])
    axd[0].plot(t[idx], data[idx]*1e6/10)

fig,ax = plt.subplots(3,1, figsize=(3.5,8))

# get integrated charge and compare to Dagan to check scaling 
# find quiet region by offseting by 5000 us 
idx_quiet, tq = get_timeidx(data, filtered_current[fc]['fs'], [5000+time_range[0], 5000+time_range[1]], t0_us)
# remove DC offset and do a cumulative integral 
qc_digital = integrate.cumtrapz(data[idx]-np.mean(data[idx_quiet]), dx=1/filtered_current[fc]['fs'], initial=0)
ax[0].plot(t[idx], data[idx], label='digital')
y_filt, fs, dec_factor = filter_ds(datastreams['P1'], fc)
idx_p1, t_p1 = get_timeidx(datastreams['P1'].data, datastreams['P1'].sample_rate, [time_range[0], time_range[1]], t0_us)
ax[1].plot(t_p1[idx_p1], y_filt[idx_p1], label='digital:P1')
ax[2].plot(t[idx], qc_digital*1e9, label='digital')
# don't need to filter the command signal 
data = datastreams['CMD0'].data
idx, t = get_timeidx(data, datastreams['CMD0'].sample_rate, time_range, t0_us)
ax[1].plot(t[idx], data[idx], label='digital:CMD')

idx, t = get_timeidx(dagan_data['im'], dagan_data['sample_rate'], [time_range[0], time_range[1]], dagan_data['peak_time']*1e6)
idx_quiet, tq = get_timeidx(dagan_data['im'], dagan_data['sample_rate'], [5000+time_range[0], 5000+time_range[1]], dagan_data['peak_time']*1e6)
qc_dagan = integrate.cumtrapz(dagan_data['im'][idx]-np.mean(dagan_data['im'][idx_quiet]), dx=1/dagan_data['sample_rate'], initial=0)
ax[0].plot(t[idx], dagan_data['im'][idx]/1e6/60, label='dagan')
ax[1].plot(t[idx], dagan_data['vm'][idx]/1000, label='dagan:Vm')
ax[1].plot(t[idx], dagan_data['CMD'][idx]/1000, label='dagan:CMD')
ax[2].plot(t[idx], qc_dagan/1e6/60*1e9, label='dagan')

ax[2].set_xlabel('$t \; [\mu s]$')
ax[0].set_ylabel('$I_m$ [A]')
ax[1].set_ylabel('$V_m$ [V]')
ax[2].set_ylabel('$Q_t$ [nC]')

for i in range(2):
    ax[i].legend()
plt.tight_layout()

plt.savefig(os.path.join(fig_dir, 'three_step.pdf'))