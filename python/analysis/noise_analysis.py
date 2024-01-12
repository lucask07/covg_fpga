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
from analysis.noise_analysis_tools import plot_psd_integrated_noise

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
data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20231210'
GND = True
dagan = pyabf.ABF(r'C:\Users\koer2434\OneDrive - University of St. Thomas\UST\research\covg\fpga_and_measurements\data_sharing\dagan_data\Richmond Data\Steps\0.1 Gain 10mV Steps.abf')


dagan_data = {}
sweep_num = 4
# sweeps 0: 0mV, 1: 10mV, ... ,4: 40 mV
#figd,axd=plt.subplots(2,1 , figsize=(4,3))
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

rtia = 100
ccomp = 47

figs = []
axs = []
for i in range(8):
    fig, ax=plt.subplots()
    figs.append(fig)
    axs.append(ax)

in_amp = 2
ccomp = 47

filtered_current = {}

for rtia in [10, 33, 100, 332]:
    if GND and rtia==100:
        data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20231211'
    else:
        data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20231210'

    if rtia == 10:
        filename = 'datastreams_noise_10res_20231210-204802_1.h5'
    elif rtia == 33:
        filename = 'datastreams_noise_33res_20231210-204835_1.h5' 
    elif rtia == 100:
        if GND:
            filename = 'datastreams_noise_vclampgnd_100res_20231211-082711_1.h5' # lights on
            filename = 'datastreams_noise_vclampgnd_100res_20231211-083347_1.h5' # lights off
            # filename = 'datastreams_noise_vclampgnd_100res_20231211-083707_1.h5' # lights on 
            filename = 'datastreams_noise_vclampgnd_100res_20231211-160622_1.h5' # removed guard capacitor and resistor
        else:
            filename = 'datastreams_noise_100res_20231210-204316_1.h5' 
    elif rtia == 332:
        filename = 'datastreams_noise_332res_20231210-204923_1.h5' 
    datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, in_amp))
   
    # noise analysis, ensure away from a peak 
    t_start = 0.1
    t_stop = 5

    t = datastreams['Im'].create_time()
    idx = (t > t_start) & (t < t_stop)
    y = datastreams['Im'].data[idx]
    fs = datastreams['Im'].sample_rate

    plot_psd_integrated_noise([axs[3], axs[4]], y, fs, datastreams)

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

    if rtia == 100:
        fig,ax = plt.subplots()
        fig2,ax2=plt.subplots()
        ax2.plot(datastreams['P1'].create_time(), datastreams['P1'].data)
    # filter and find a section in time away from a step to determine noise 
    for fc in [1e6, 500e3, 200e3, 100e3, 50e3, 30e3, 10e3, 3e3]:
        y_filt, fs = filter_ds(datastreams['Im'], fc, idx)
        # crop y_fliter to prevent transients 
        y_filt = y_filt[100:]
        print(f'Filtering: {fc}')
        filtered_current[fc] = {'data': y_filt, 'fs':fs}
        print(f'Noise of {np.std(y_filt)} with cutoff of {fc}')

        if rtia == 100:
            f, im_pd = calc_psd(y_filt, fs, nperseg=1024*8, scaling='spectrum')
            ax.loglog(f, np.sqrt(im_pd)*1e9, marker='*', label=f'R={rtia} k$\Omega$, $f_c$={fc}')
            ax.set_ylabel('I/$\sqrt{Hz}$ [nA]')
            ax.set_xlabel('f [Hz]')
    ax.legend()

    filt_t = np.linspace(0, len(y_filt)-1,len(y_filt))*1/fs
    axs[5].plot(filt_t, y_filt, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}', marker='.')
    axs[5].set_xlabel('t')

    f, im_pd = calc_psd(y_filt, fs, nperseg=1024)
    axs[6].loglog(f, im_pd, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}', marker='.')
    axs[6].set_xlabel('f [Hz]')

    for i in range(8):
        axs[i].legend()


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