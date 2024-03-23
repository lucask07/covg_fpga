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
from analysis.utils import my_savefig

# configure Matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()

# setup data directory
data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    print('linux directory not yet configured')
elif sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp/{}{:02d}{:02d}"
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/{}{:02d}{:02d}')

figure_dir = '/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/figures/'
fig_names = {}


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
    print(f'Noise of {np.std(y_filt[50:-50])} with cutoff of {fc}')

    filt_t = np.linspace(0, len(y_filt)-1,len(y_filt))*1/fs

    return y_filt, filt_t


# data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20230619'
# data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20230630'
# data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20230701'
data_dir = r'C:\Users\koer2434\Documents\covg\data\clamp\20230704'


#filename = 'datastreams2_output_quietdacs_rtia{}_ccomp{}.h5' # 3 uses RF1 = 30
filename = 'noisetest9_quietdacs_rtia{}_ccomp{}.h5'
filename = 'clamptest1_rtia{}_ccomp{}.h5'
filename = 'clamptest8_quietdacsFalse_rtia{}_ccomp{}.h5'
filename = 'clamptest1_quietdacsFalse_rtia{}_ccomp{}_inamp{}.h5'


time_range = [-50, 400] # [us] before and after peak; datastream plotting uses units of us

rtia = 100
ccomp = 47
in_amp_arr = 2

figs = []
axs = []
N = 10
for i in range(N):
    fig, ax=plt.subplots()
    figs.append(fig)
    axs.append(ax)

for in_amp in [in_amp_arr]:
    for ccomp in [47]:
#        for rtia in [33, 100, 332, 1000, 3000, 10000]:
        #for rtia in [100]:
        for rtia in [100]:
            datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, in_amp))
            pos_pks = find_peak(datastreams['CMD0'].create_time(), np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)
            neg_pks = find_peak(datastreams['CMD0'].create_time(), -np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)

            print(pos_pks)
            print(neg_pks)

            try:
                t0_us = pos_pks[0][0]*1e6
            except: # if no peak is found use the logfile information in datastreams
                t0_us = datastreams.ddr_step_peak*1e6
            try:
                t0_us_stop = neg_pks[0][0]*1e6
            except:
                t0_us_stop = datastreams.ddr_step_peak*1e6*2

            # plot current Im 
            t = datastreams['Im'].create_time()*1e6 - t0_us
            fs = datastreams['Im'].sample_rate
            idx = (t > time_range[0]) & (t < time_range[1])
            y = datastreams['Im'].data[idx]
            y = y - np.average(y[-100:]) # remove steady-state current 

            fc = 100e3
            if fc is not None:
                y, t = filter_fc(y, fs, fc, REMOVE_DC = False)
                t = t*1e6
            else:
                t = t[idx]

            axs[0].plot(t, y/np.sum(y), label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[0].set_xlim(time_range)
            axs[0].set_xlabel('t [$\mu$s]')
            axs[0].set_ylabel('I (a.u.)')
            fig_names[0] = 'Istep_arbitrary_units_fc{}'.format(fc)

            axs[7].plot(t, y*1e6, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[7].set_xlim(time_range)
            axs[7].set_xlabel('t [$\mu$s]')
            axs[7].set_ylabel('I (uA)')
            fig_names[7] = 'Istep_uA_units_fc{}'.format(fc)


            axs[1].plot(t, np.cumsum(y)/np.sum(y), label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[1].set_xlim(time_range)
            axs[1].set_xlabel('t [$\mu$s]')
            axs[1].set_ylabel('Q (a.u.)')
            fig_names[1] = 'Istep_Q_arbitrary_units_fc{}'.format(fc)


            #dt_tmp = datastreams['Im'].create_time() # in second 
            #dt = dt_tmp[1] - dt_tmp[0]
            dt = (t[1] - t[0])/1e6 # use filtered time in seconds 
            axs[8].plot(t, (np.cumsum(y*dt))*1e9, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[8].set_xlim(time_range)
            axs[8].set_xlabel('t [$\mu$s]')
            axs[8].set_ylabel('Q (nC)')
            fig_names[8] = 'Istep_Q_nC_units_fc{}'.format(fc)


            # plot P1 voltage 
            t = datastreams['P1'].create_time()*1e6 - t0_us
            idx = (t > time_range[0]) & (t < time_range[1])
            y = datastreams['P1'].data[idx]
            y_ss = np.average(y[-100:])
            t_cmd = datastreams['CMD0'].create_time()*1e6 - t0_us
            idx_cmd = (t_cmd > time_range[0]) & (t_cmd < time_range[1])
            y_cmd = datastreams['CMD0'].data[idx_cmd]

            axs[2].plot(t[idx], y/y_ss, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[2].set_xlim(time_range)
            axs[2].set_xlabel('t [$\mu$s]')
            axs[2].set_ylabel('P1')

            axs[9].plot(t[idx], y*1e3, label=f'P1: R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[9].plot(t_cmd[idx_cmd], y_cmd*1e3, label=f'CMD: R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[9].set_xlim(time_range)
            axs[9].set_xlabel('t [$\mu$s]')
            axs[9].set_ylabel('[mV]')
            axs[9].legend()
            fig_names[9] = 'CMDstep_mV_units'

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
            fig_names[3] = 'noise_spectrum'.format(fc)


            axs[4].loglog(f, np.cumsum(im_pd*1e9**2), marker='*', label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[4].set_ylabel('Integrated noise [nA$^2$]')
            axs[4].set_xlabel('f [Hz]')
            fig_names[4] = 'intergrated_noise_spectrum'.format(fc)


            print(f'RTIA = {rtia}; CComp = {ccomp}')
            for fc in [1e6, 500e3, 200e3, 100e3, 50e3, 30e3, 10e3, 3e3]:
                fs = datastreams['Im'].sample_rate
                y = datastreams['Im'].data[idx]
                y_filt, filt_t = filter_fc(y, fs, fc, REMOVE_DC = True)

            axs[5].plot(filt_t, y_filt, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}', marker='.')
            axs[5].set_xlabel('t')

            f, im_pd = calc_psd(y_filt, fs, nperseg=1024)
            axs[6].loglog(f, im_pd, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}', marker='.')
            axs[6].set_xlabel('f [Hz]')

    for i in range(N):
        axs[i].legend()

    for i in range(N):
        try:
            my_savefig(figs[i], figure_dir, fig_names[i])
        except:
            pass



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