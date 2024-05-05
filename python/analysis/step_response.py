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
import pandas as pd
import scipy.signal as signal 
from filters.filter_tools import butter_lowpass_filter
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
figure_dir_paper = '/Users/koer2434/My Drive/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/step/'
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
    filt_t = np.linspace(0, len(y_filt)-1,len(y_filt))*1/fs

    return y_filt, filt_t


# data_dir_end = r'20230619'
# data_dir_end = r'20230630'
# data_dir_end = r'20230701'
data_dir_end = r'20230704'
#data_dir_end = r'20240320'
data_dir_end = r'20240502'

data_dir = os.path.join(data_dir_covg, data_dir_end)


#filename = 'datastreams2_output_quietdacs_rtia{}_ccomp{}.h5' # 3 uses RF1 = 30
filename = 'noisetest9_quietdacs_rtia{}_ccomp{}.h5'
filename = 'clamptest1_rtia{}_ccomp{}.h5'
filename = 'clamptest8_quietdacsFalse_rtia{}_ccomp{}.h5'
filename = 'clamptest1_quietdacsFalse_rtia{}_ccomp{}_inamp{}.h5'

# for 05/02
filename = 'step_rtia{}_ccomp{}_cmd{}.h5'

time_range = [-50, 250] # [us] before and after peak; datastream plotting uses units of us; for step_info will expand to 400 us for slow rtia values 

# clamp board configuration 
rtia = 100 # kilo-ohms 
ccomp = 47 # pF 
in_amp_arr = 2 # gain of instrumentation amplifier 
cmd = 705

figs = []
axs = []
N = 10
for i in range(N):
    fig, ax=plt.subplots(figsize = fig_size)
    figs.append(fig)
    axs.append(ax)


# 2x1 subplot for manuscript 
fs = fig_size 
# increase height to support 2x1 
fs = (fig_size[0], fig_size[1]*1.8)
fig_m, ax_m = plt.subplots(figsize = fs, nrows=2, ncols=1)

def i_step_and_q(rtia, ccomp, cmd, fc=100e3):

    in_amp = 2
    if data_dir_end == '20240502':
        datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, cmd))
    else:
        datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, in_amp))

    # plot current Im 
    t = datastreams['Im'].create_time()*1e6 - t0_us
    fs = datastreams['Im'].sample_rate
    idx = (t > time_range[0]) & (t < time_range[1]) # time range is in us around the step
    y = datastreams['Im'].data[idx]
    idx_pedestal = t[idx] < -10
    y = y - np.average(y[idx_pedestal]) # remove steady-state current 

    if fc is not None:
        y, t = filter_fc(y, fs, fc, REMOVE_DC = False)
        t = t*1e6 + time_range[0]
    else:
        t = t[idx]

    # 2x1 subplot for manuscript 
    fs = fig_size 
    # increase height to support 2x1 
    fs = (fig_size[0], fig_size[1]*1.8)
    fig_m, ax_m = plt.subplots(figsize = fs, nrows=2, ncols=1)

    # 2x1 for manuscript 
    lns1 = ax_m[1].plot(t, y*1e6, label='$I_m$')
    ax_m[1].set_xlim(time_range)
    ax_m[1].set_xlabel('t [$\mu$s]')
    ax_m[1].set_ylabel('I [$\mu$A]')

    dt = (t[1] - t[0])/1e6 # use filtered time in seconds 

    ax_right = ax_m[1].twinx()
    lns2 = ax_right.plot(t, (np.cumsum(y*dt))*1e9, label=f'Q', color='tab:orange')
    ax_right.set_xlim(time_range)
    ax_right.set_xlabel('t [$\mu$s]')
    ax_right.set_ylabel('Q [nC]')

    # added these three lines
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax_m[1].legend(lns, labs, loc=5)

    # plot P1 voltage 
    t = datastreams['P1'].create_time()*1e6 - t0_us
    idx = (t > time_range[0]) & (t < time_range[1])
    y = datastreams['P1'].data[idx]
    PLOT_P2 = False # in 05/02 data included P2 datastream; generally distracting so will omit  
    if PLOT_P2: 
        try:
            t2 = datastreams['P2'].create_time()*1e6 - t0_us
            idx2 = (t2 > time_range[0]) & (t2 < time_range[1])
            y2 = datastreams['P2'].data[idx2]
        except:
            PLOT_P2 = False

    y_ss = np.average(y[-100:])
    t_cmd = datastreams['CMD0'].create_time()*1e6 - t0_us
    idx_cmd = (t_cmd > time_range[0]) & (t_cmd < time_range[1])
    y_cmd = datastreams['CMD0'].data[idx_cmd]

    ax_m[0].plot(t[idx], y*1e3, label=f'P1')
    ax_m[0].plot(t_cmd[idx_cmd], y_cmd*1e3, label=f'CMD')
    if PLOT_P2:
        ax_m[0].plot(t[idx], y2*1e3, label=f'P2')

    ax_m[0].set_xlim(time_range)
    ax_m[0].set_xlabel('t [$\mu$s]')
    ax_m[0].set_ylabel('V [mV]')
    ax_m[0].legend(loc=5)

    my_savefig(fig_m, figure_dir, f'voltage_cmd_im_q_rtia{rtia}_ccomp{ccomp}_cmd{cmd}')
    try:
        my_savefig(fig_m, figure_dir_paper, f'voltage_cmd_im_q_rtia{rtia}_ccomp{ccomp}_cmd{cmd}')
    except:
        print('Cannot find directory {}'.format(figure_dir_paper))

    return datastreams 

for in_amp in [in_amp_arr]:
    for ccomp in [47]:
#        for rtia in [33, 100, 332, 1000, 3000, 10000]:
        #for rtia in [100]:
        for rtia in [100]:
            if data_dir_end == '20240502':
                datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, cmd))
            else:
                datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, in_amp))
            pos_pks = find_peak(datastreams['CMD0'].create_time(), np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)
            neg_pks = find_peak(datastreams['CMD0'].create_time(), -np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)

            print(pos_pks)
            print(neg_pks)

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

            # plot current Im 
            t = datastreams['Im'].create_time()*1e6 - t0_us
            fs = datastreams['Im'].sample_rate
            idx = (t > time_range[0]) & (t < time_range[1])
            y = datastreams['Im'].data[idx]
            y = y - np.average(y[-100:]) # remove steady-state current 

            fc = 100e3
            if fc is not None:
                y, t = filter_fc(y, fs, fc, REMOVE_DC = False)
                t = t*1e6 + time_range[0]
            else:
                t = t[idx]

            axs[0].plot(t, y/np.sum(y), label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[0].set_xlim(time_range)
            axs[0].set_xlabel('t [$\mu$s]')
            axs[0].set_ylabel('I [a.u.]')
            fig_names[0] = 'Istep_arbitrary_units_fc{}'.format(fc)

            axs[7].plot(t, y*1e6, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[7].set_xlim(time_range)
            axs[7].set_xlabel('t [$\mu$s]')
            axs[7].set_ylabel('I [uA]')
            fig_names[7] = 'Istep_uA_units_fc{}'.format(fc)

            # 2x1 for manuscript 
            lns1 = ax_m[1].plot(t, y*1e6, label='$I_m$')
            ax_m[1].set_xlim(time_range)
            ax_m[1].set_xlabel('t [$\mu$s]')
            ax_m[1].set_ylabel('I [$\mu$A]')

            axs[1].plot(t, np.cumsum(y)/np.sum(y), label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[1].set_xlim(time_range)
            axs[1].set_xlabel('t [$\mu$s]')
            axs[1].set_ylabel('Q [a.u.]')
            fig_names[1] = 'Istep_Q_arbitrary_units_fc{}'.format(fc)

            dt = (t[1] - t[0])/1e6 # use filtered time in seconds 
            axs[8].plot(t, (np.cumsum(y*dt))*1e9, label=f'R={rtia} k$\Omega$, C={ccomp} pF, InAmp=x{in_amp}')
            axs[8].set_xlim(time_range)
            axs[8].set_xlabel('t [$\mu$s]')
            axs[8].set_ylabel('Q [nC]')
            fig_names[8] = 'Istep_Q_nC_units_fc{}'.format(fc)

            ax_right = ax_m[1].twinx()
            lns2 = ax_right.plot(t, (np.cumsum(y*dt))*1e9, label=f'Q', color='tab:orange')
            ax_right.set_xlim(time_range)
            ax_right.set_xlabel('t [$\mu$s]')
            ax_right.set_ylabel('Q [nC]')

            # added these three lines
            lns = lns1+lns2
            labs = [l.get_label() for l in lns]
            ax_m[1].legend(lns, labs, loc=5)

            # plot P1 voltage 
            t = datastreams['P1'].create_time()*1e6 - t0_us
            idx = (t > time_range[0]) & (t < time_range[1])
            y = datastreams['P1'].data[idx]
            PLOT_P2 = False # in 05/02 data included P2 datastream; generally distracting so will omit  
            if PLOT_P2: 
                try:
                    t2 = datastreams['P2'].create_time()*1e6 - t0_us
                    idx2 = (t2 > time_range[0]) & (t2 < time_range[1])
                    y2 = datastreams['P2'].data[idx2]
                except:
                    PLOT_P2 = False

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
            axs[9].set_ylabel('V [mV]')
            axs[9].legend()
            fig_names[9] = 'CMDstep_mV_units'

            ax_m[0].plot(t[idx], y*1e3, label=f'P1')
            ax_m[0].plot(t_cmd[idx_cmd], y_cmd*1e3, label=f'CMD')
            if PLOT_P2:
                ax_m[0].plot(t[idx], y2*1e3, label=f'P2')

            ax_m[0].set_xlim(time_range)
            ax_m[0].set_xlabel('t [$\mu$s]')
            ax_m[0].set_ylabel('V [mV]')
            ax_m[0].legend(loc=5)            

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
    my_savefig(fig_m, figure_dir, 'voltage_cmd_im_q')
    try:
        my_savefig(fig_m, figure_dir_paper, 'voltage_cmd_im_q')
    except:
        print('Cannot find directory {}'.format(figure_dir_paper))


res = {}
for k in ['cmd_v', 'cmd', 'rtia', 'ccomp', 'Qt', 'Ipk', 'tr_p1', 'os_p1', 
          'tr_im', 'us_im', 'settle_p1', 'peak_time_im', 'peak_p1', 'ss_p1']:
    res[k] = []

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
cmd = 705
if data_dir_end == '20240502':
    datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, cmd))
else:
    datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, in_amp))

pos_pks = find_peak(datastreams['CMD0'].create_time(), np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)
neg_pks = find_peak(datastreams['CMD0'].create_time(), -np.diff(datastreams['CMD0'].data), th=0.2e-3, height=1e-3, distance=100)

print(pos_pks)
print(neg_pks)

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

for in_amp in [in_amp_arr]:
    for ccomp in [47, 4700]:
        for rtia in [33, 100, 332, 1000]:
#        for rtia in [33]:
            for cmd in cmd_vals:
                if data_dir_end == '20240502':
                    datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, cmd))
                else:
                    datastreams = h5_to_datastreams(data_dir, filename.format(rtia, ccomp, in_amp))

                res['cmd'].append(cmd)
                res['ccomp'].append(ccomp)
                res['rtia'].append(rtia)
                
                # Analyze current Im 
                t = datastreams['Im'].create_time()*1e6 - t0_us
                fs = datastreams['Im'].sample_rate
                idx = (t > time_range[0]) & (t < time_range[1])
                y = datastreams['Im'].data[idx]
                y = y - np.average(y[-100:]) # remove steady-state current 

                fc = 100e3
                if fc is not None:
                    y, t = filter_fc(y, fs, fc, REMOVE_DC = False)
                    t = t*1e6 + time_range[0]
                else:
                    t = t[idx]

                res['Ipk'].append(np.max(y))
                dt = (t[1] - t[0])/1e6 # use filtered time in seconds 
                q = (np.cumsum(y*dt))*1e9
                res['Qt'].append(q[-1])

                t = datastreams['CMD0'].create_time()*1e6 - t0_us
                idx = (t > time_range[0]) & (t < time_range[1])
                y = datastreams['CMD0'].data[idx]
                res['cmd_v'].append(y[-1] - y[0])

                if rtia >= 332:
                    fc = 10e3 # filter for stepinfo processing so that setting time (within 2%) is accurate
                else:
                    fc = 100e3

                # need to extend to step response processing to 550 us for the 332 and 1000 rtia.
                si1 = datastreams['P1'].stepinfo_range([ (time_range[0] + t0_us)*1e-6, (time_range[1] + 300 + t0_us)*1e-6], fc=fc)
                res['tr_p1'].append(si1['RiseTime'])
                res['settle_p1'].append(si1['SettlingTime'] - t0_us/1.0e6) # finds absolute settling time in us
                res['os_p1'].append(si1['Overshoot'])
                res['peak_p1'].append(si1['Peak'])
                res['ss_p1'].append(si1['SteadyStateValue'])

                si2 = datastreams['Im'].stepinfo_range([(time_range[0] + t0_us)*1e-6, (time_range[1] + 300 + t0_us)*1e-6], fc=fc)
                res['tr_im'].append(si2['RiseTime'])
                res['us_im'].append(si2['Undershoot'])
                res['peak_time_im'].append(si2['PeakTime'] - t0_us*1e-6)

df = pd.DataFrame(res)
df.to_csv(os.path.join(figure_dir, f'step_response_summary_{data_dir_end}_inamp{in_amp}.csv'), index=False)
# TODO: just one ccomp based on stability 
# TODO: convert to CMD value
for ccomp in [47, 4700]:
    fig, ax=plt.subplots(figsize = fig_size)
    for rtia in [33, 100, 332, 1000]:
        condition = (df.rtia==rtia) & (df.ccomp==ccomp)
        ax.plot(df[condition]['cmd_v']*1000, df[condition]['Qt'], marker='o', linestyle='none', label=f'{rtia} k$\Omega$')

    ax.set_xlabel('$\Delta V_m$ [mV]')
    ax.set_ylabel('Q [nC]')
    ax.legend()
    my_savefig(fig, figure_dir, f'charge_linearity_ccomp{ccomp}')

res2 = {'ccomp': [], 'rtia': [], 'peak_i': [], 'max_v_wo_sat': []} 
for ccomp in [47, 4700]:
    fig, ax=plt.subplots(figsize = fig_size)
    for rtia in [33, 100, 332, 1000]:
        condition = (df.rtia==rtia) & (df.ccomp==ccomp)
        ax.plot(df[condition]['cmd_v']*1000, df[condition]['Ipk']*1e6, marker='o', linestyle='none', label=f'{rtia} k$\Omega$')

        peak_i = np.max(df[condition]['Ipk'])
        # idx = df[condition]['Ipk'] < 0.90*peak_i # doesn't work because ipk turns over at very high Vcmd 
        idx = df[condition]['Ipk'] > 0.90*peak_i # find smallest Vcmd within 90% of peak; fails at Rtia = 100 kOhm  
        max_v = np.min(df[condition]['cmd_v'][idx])
        res2['ccomp'].append(ccomp)
        res2['rtia'].append(rtia)
        res2['peak_i'].append(peak_i)
        res2['max_v_wo_sat'].append(max_v)

    ax.set_xlabel('$\Delta V_m$ [mV]')
    ax.set_ylabel('$I_{pk}$ [$\mu$A]')
    ax.legend()
    my_savefig(fig, figure_dir, f'peak_current_ccomp{ccomp}')

df_sum = pd.DataFrame(res2)
df_sum.to_csv(os.path.join(figure_dir, f'step_response_total_summary_{data_dir_end}_inamp{in_amp}.csv'), index=False)

# given these 2 dataframes export to Latex table 

# cmd_val of 705 is 80 mV; 88 is 10 mV -- using 10 mV to avoid saturation 
# Condition to select rows
condition = ((df['cmd'] == 705) & ((df['rtia'] == 33) | (df['rtia'] == 100))) | ((df['cmd'] == 88) & ((df['rtia'] == 332) | (df['rtia'] == 1000)))               
dfs = df[condition]
# plot the step response for each of the selections 
# Higher rtia will look noisier because of considerably smaller CMD step (and subsequent scaling)
for index, row in dfs.iterrows():
    rtia = int(row['rtia'])
    if rtia >= 332:
        fc = 33e3 # filter for stepinfo processing so that setting time (within 2%) is accurate
    else:
        fc = 100e3

    i_step_and_q(rtia = rtia, ccomp=int(row['ccomp']), cmd=int(row['cmd']), fc=fc)
# need to extend to step response processing to 400 us for the 332 and 1000 rtia.

# remove 33 and ccomp = 4700 since unstable 
row_to_drop = dfs[ (dfs['rtia'] == 33 ) & (dfs['ccomp']==4700) ].index[0]
dfs = dfs.drop(row_to_drop)

# select a subset of columns and reorder 
# dfs = dfs[['rtia', 'ccomp', 'tr_p1', 'os_p1', 'settle_p1', 'tr_im', 'us_im', 'peak_time_im']]
dfs = dfs[['rtia', 'ccomp', 'tr_p1', 'os_p1', 'settle_p1', 'peak_time_im']]

# Convert ccomp to fast and slow 
# Define a custom function to convert values
def convert_speed(value):
    if value == 47:
        return 'fast'
    elif value == 4700:
        return 'slow'
    else:
        return 'other'

dfs['ccomp'] = df['ccomp'].apply(convert_speed)

# multiply by 1e6 to convert to us 
for v in ['tr_p1', 'settle_p1', 'peak_time_im']:
    dfs[v] = dfs[v]*1e6

# rename columns 
dfs.columns = ['R_{F} [k\Omega]', 'Speed', 't_r', 'OS \%', 't_s', 'I_m t_{pk}']

# Default formatter function
def default_formatter(x):
    return "{:.1f}".format(x)

formatter = {
    'R_{F} [k\Omega]': '{}'.format,  # Format RF as int
    'Speed': '{}'.format,
    't_r': '{:.1f}'.format,   # Format tr with 1 decimal place
    't_r i_m': '{:.1f}'.format   # Format tr with 1 decimal place
}

formatters = {col: formatter.get(col, default_formatter) for col in dfs.columns}
latex_table = dfs.to_latex(index=False, formatters=formatters)
print(latex_table)

print(---)

print(df_sum) # print the second table to get the saturation voltages 

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
