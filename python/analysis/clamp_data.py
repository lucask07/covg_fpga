"""
General analysis of COVG ADC data (h5 files)
Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import glob
from scipy.signal import deconvolve, convolve, resample, decimate, resample_poly
import pandas as pd
from filters.filter_tools import butter_lowpass_filter
from analysis.adc_data import *
from analysis.utils import find_nearest, find_closest_row
from calibration.signal_chain import dn_per_nA
from scipy.optimize import curve_fit
from scipy.integrate import trapezoid
from scipy.special import erfinv, erf
from numpy.fft import fft, ifft, ifftshift

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

data_dir = data_dir_covg.format(2022, 1, 16)
FS = 5e6

# TODO: fig_dir
# TODO: summary tables
# TODO: description of various data-sets
# TODO: should the dir and file be set with the analysis type?
# TODO: demonstrate RF adjustment -- label with nA
# TODO: determine total integrated charge
# TODO: search for optimal cc settings

# analysis_type =['summary_stats', 'rf_swp']
analysis_type =['deconvolve']

# analysis examples

if 'im_noise' in analysis_type:
    file_name = 'cc_swp_0.h5'
    t, adc = read_h5(data_dir_covg.format(2022, 1, 7), file_name, [0,1])
    ax = plot_adc(t, adc[0])
    filt_data = butter_lowpass_filter(adc[0], 1e6, 5e6, order=5)
    ax = plot_adc(t, filt_data)
    filt_data = butter_lowpass_filter(adc[0], 20e3, 5e6, order=5)
    plot_adc(t, filt_data)

if 'im_movie' in analysis_type:
    import time
    for i in range(24):
        read_plot(data_dir, f'cc_swp_{i}.h5', filter_bw=[None])
        plt.show()
        plt.pause(0.01)
        time.sleep(2)
        plt.close('all')

if 'summary_stats' in analysis_type:
    filename = 'cc_swp4'
    # load CSV summary as Pandas dataframe
    csv_summary = glob.glob(os.path.join(data_dir, f'{filename}_*.csv'))[0]
    output = pd.read_csv(csv_summary)

    # use 7e5 as lowest peak area without acquisition issue
    min_peakarea_ok = 7e5
    idx = output.peak_area > min_peakarea_ok

    # plot trace with minimum peak area
    min_pa = output[idx].peak_area.min()
    min_row = output[output.peak_area == min_pa]
    ax, t, adc_data = read_plot(data_dir, min_row.filename.item() + '.h5', chan_list=[0], filter_bw=None, ax=None, clr='b')
    ax.set_title('Minimum peak area')

    max_pa = output[idx].peak_area.max()
    max_row = output[output.peak_area == max_pa]
    ax, t, adc_data = read_plot(data_dir, max_row.filename.item() + '.h5', chan_list=[0], filter_bw=None, ax=None, clr='b')
    ax.set_title('Maximum peak area')



    def plot_one_vs(x_var='cc_scale', x_var_label='CC scaling', leg_var='cc_delay',
                    other_var='cc_fc', y_var='peak_area'):
        # vary cc_scale at constant delay and fc
        # y-axis: peak_area
        # x-axis: cc_scale
        # legend: cc_delay
        # other: cc_fc at midpoint
        scaling = 4e-3

        idx = output['peak_area'] > min_peakarea_ok
        leg_var_unq = np.unique(output[leg_var])
        leg_var_unq_mid = leg_var_unq[len(leg_var_unq)//2]

        min_row = output[output.peak_area == min_pa]
        other_var_val = min_row[other_var].item()
        print(f'Found {other_var} value of {other_var_val} at minimum row')

        idx_other = idx & (output[other_var] == other_var_val)
        colors = iter(plt.cm.rainbow(np.linspace(0, 1, len(leg_var_unq))))
        fig, ax = plt.subplots()
        for leg_var_val in leg_var_unq:
            idx_subset = idx_other & (output[leg_var] == leg_var_val)
            lbl = leg_var + ' = {:0.2g}'.format(leg_var_val)
            ax.plot(output[idx_subset][x_var], output[idx_subset][y_var]*scaling,
                    marker='*', linestyle='None', color=next(colors), label=lbl)  # uC

        ax.set_ylabel('Area of |Im| $\mu$C')
        ax.set_xlabel(f'{x_var_label}')
        ax.legend()
        plt.savefig(os.path.join(data_dir, f'fig_{y_var}_vs_{x_var}'))

    plot_one_vs(x_var='cc_delay', x_var_label='CC delay', leg_var='cc_fc',
                other_var='cc_scale', y_var='peak_area')


if 'trace_comparison' in analysis_type:
    colors = iter(plt.cm.rainbow(np.linspace(0, 1, np.sum(idx))))
    fn = output[idx].filename
    cc_scale = output[idx].cc_scale
    ax, t, adc_data  = read_plot(data_dir, fn.iloc[0] + '.h5', chan_list=[0], filter_bw=None, ax=None, clr=next(colors), lbl='cc = {:.2f}'.format(cc_scale.iloc[0]))
    for f, cc_s in zip(fn[1:], cc_scale[1:]):
        ax, t, adc_data  = read_plot(data_dir, f + '.h5', chan_list=[0], filter_bw=None, ax=ax, clr=next(colors), lbl='cc = {:.2f}'.format(cc_s),
        scaling = 4)
    ax.legend()
    ax.set_xlim([1400, 3000])
    plt.savefig(os.path.join(data_dir, 'fig_vary_ccscale'))

    # vary delay at constant fc and scale
    idx = output.peak_area > 7e5
    cc_scale = np.unique(output.cc_scale)
    cc_scale_mid = cc_scale[3]
    # ('cc_scale', min_row.cc_scale.item())
    for col in [('cc_scale', cc_scale_mid), ('cc_fc', min_row.cc_fc.item())]:
        idx = idx & (output[col[0]] == col[1])

    fig, ax = plt.subplots()
    ax.plot(output[idx].cc_delay, output[idx].peak_area*4e-3, marker='*')  # uC
    ax.set_ylabel('Area of |Im| $\mu$C')
    ax.set_xlabel('CC delay')
    plt.savefig(os.path.join(data_dir, 'fig_area_vs_ccdelay'))

    colors = iter(plt.cm.rainbow(np.linspace(0, 1, np.sum(idx))))
    fn = output[idx].filename
    cc_delay = output[idx].cc_delay
    ax, t, adc_data  = read_plot(data_dir, fn.iloc[0] + '.h5', chan_list=[0], filter_bw=None, ax=None, clr=next(colors), lbl='cc = {:.2f}'.format(cc_delay.iloc[0]))
    for f, cc_s in zip(fn[1:], cc_delay[1:]):
        ax, t, adc_data  = read_plot(data_dir, f + '.h5', chan_list=[0], filter_bw=None, ax=ax, clr=next(colors), lbl='delay = {:.2f}'.format(cc_s*1e6),
        scaling = 4)
    ax.legend()
    ax.set_xlim([1400, 3000])
    plt.savefig(os.path.join(data_dir, 'fig_vary_ccdelay'))

if 'rf_swp' in analysis_type:
    data_dir = data_dir_covg.format(2022, 1, 16)
    filename = 'rf_swp3'
    csv_summary = glob.glob(os.path.join(data_dir, f'{filename}_*.csv'))[0]
    output = pd.read_csv(csv_summary)

    h5_files = glob.glob(os.path.join(data_dir, f'{filename}_*.h5'))
    pa_arr = np.array([])
    for hf in h5_files:
        ax, t, adc_data = read_plot(data_dir, hf.split('/')[-1], chan_list=[0])
        plt.pause(1)
        plt.close('all')
        pa, num_found = peak_area(t, adc_data[0])
        pa_arr = np.append(pa_arr, pa)

    # alternatively, use the dataframe to find the files to plot
    for ccomp in [47, 4747]:
        for cc_scale in [0, -0.33]:
            fig, ax = plt.subplots()
            if ccomp < 1000:
                rf_test = 3000
                idx = (output.ccomp == ccomp) & (output.cc_scale == cc_scale) & (output.rf < rf_test)
            else:
                rf_test = 100000 # all rfs
                idx = (output.ccomp == ccomp) & (output.cc_scale == cc_scale) & (output.rf < rf_test)
            clrs = iter(plt.cm.rainbow(np.linspace(0, 1, np.sum(idx))))
            for idx, r in output.iterrows():
                t, adc_data = read_h5(data_dir, r.filename + '.h5', chan_list=[0])
                if (r.ccomp == ccomp) and (r.cc_scale == cc_scale) and (r.rf < rf_test):
                    ax, t, adc_data = read_plot(data_dir, r.filename + '.h5', chan_list=[0],
                                                ax=ax, clr=next(clrs))

    DEBUG_FIT_PLOT = False
    im_df = pd.DataFrame()
    im_data = {}
    noise_time = [2500e-6, 2900e-6]
    peak_time = [3200e-6, 3400e-6]
    for idx, r in output.iterrows():
        t, adc_data = read_h5(data_dir, r.filename + '.h5', chan_list=[0])
        t=t[64:]
        adc_data[0]=adc_data[0][64:]
            # calculate peak rise-time, peak fall-time (time-constant), integrated charge, noise [full BW and 3 kHz], undershoot
        im_data['rf'] = r.rf
        im_data['ccomp'] = r.ccomp
        im_data['cc_scale'] = r.cc_scale
        idx_noise = idx_timerange(t, noise_time[0], noise_time[1])
        im_data['noise_nofilt'] = np.std(adc_data[0][idx_noise]/dn_per_nA(r.rf*1e3))
        im_data['noise_3k_filt']  = np.std(butter_lowpass_filter(adc_data[0][idx_noise]/dn_per_nA(r.rf*1e3), cutoff=3e3, fs=FS, order=5))
        im_data['filename'] = r.filename

        y = adc_data[0]
        t_peaks, idx_pk, results = find_peak(t, y, th=5, distance=10000)
        print(t_peaks)
        t_nearest = find_nearest(t_peaks, peak_time[0])
        idx_decay = idx_timerange(t, t_nearest, t_nearest+120e-6)
        y = adc_data[0][idx_decay]/dn_per_nA(r.rf*1e3)
        # idx_decay = idx_timerange(t, peak_time[0], peak_time[1])
        # tau, amp = np.polyfit(t[idx_decay], np.log(y), 1, w=np.sqrt(y))
        exp_fits, err = curve_fit(lambda t,a,tau: a*np.exp(-t/tau),
                                  t[idx_decay]-t[idx_decay][0], y,
                                  p0=[10000, 1e3*33e-9])
        im_data['tau'] = exp_fits[1]
        im_data['amp'] = exp_fits[0]
        im_data['peak_time'] = t_nearest
        # integrate around the peak for total charge
        idx_integrate = idx_timerange(t, t_nearest-120e-6, t_nearest+120e-6)
        y = adc_data[0][idx_integrate]/dn_per_nA(r.rf*1e3)
        im_data['integrated_charge_nC'] = trapezoid(y, t[idx_integrate])

        if DEBUG_FIT_PLOT:
            fig, ax = plt.subplots()
            ax.plot(t[idx_decay]-t[idx_decay][0],  y, color='b')
            ax.plot(t[idx_decay]-t[idx_decay][0],  exp_fits[0]*np.exp( -(t[idx_decay]-t[idx_decay][0])/exp_fits[1]), color='r')
            print(im_data)
            input()
            plt.close('all')

        im_df = im_df.append(im_data, ignore_index=True)


if 'deconvolve' in analysis_type:

    def wiener_deconvolution(signal, kernel, lambd=1e-3):
        """Applies Wiener deconvolution to find true observation from signal and filter

        The function can be also used to estimate filter from true signal and observation
        """
        # zero pad the kernel to same length
        kernel = np.hstack((kernel, np.zeros(len(signal) - len(kernel))))
        H = fft(kernel)
        deconvolved = np.real(ifft(fft(signal)*np.conj(H)/(H*np.conj(H) + lambd**2)))
        return deconvolved

    data_dir = data_dir_covg.format(2022, 1, 16)
    filename = 'rf_swp3_{}'
    data_dir = data_dir_covg.format(2022, 1, 19)
    filename = 'step_swp_{}'
    t_offset_idx = 64
    t_offset = 64*200e-9

    # try with 20 and 21 which is Rf = 100 k and Ccomp = 47 pF
    num = 21

    def get_impulse(num):

        t, adc_data = read_h5(data_dir, filename.format(num) + '.h5', chan_list=[0])
        t=t[t_offset_idx:]
        adc_data[0]=adc_data[0][t_offset_idx:]

        # make step function at t0
        t0 = 3200e-6*2
        idx_signal = idx_timerange(t, t0-150e-6, t0 + 200e-6)
        y = adc_data[0][idx_signal]
        while y[0]==0:
            y = y[1:]

        # step function is not necessary but could be used for plotting convolution
        idx_step = idx_timerange(t, t0-350e-6, t0 + 400e-6)
        t_conv = t[idx_step]
        step_func = np.ones(len(t_conv)) # can't have 0s in the filter function
        step_func[t_conv < t0] = 0
        step_func = butter_lowpass_filter(step_func, cutoff=1e6, fs=FS, order=5)
        # The length of the deconvolution output is: len(signal) - len(filter) + 1
        # imp_resp, remainder = deconvolve(step_func, y)
        y = butter_lowpass_filter(y, cutoff=1e6, fs=FS, order=5)

        #  the Wiener deconvolution adds noise to the denominator so that the result doesn't explode.
        # imp_resp_w = wiener_deconvolution(y, step_func)[:(len(y)-len(step_func) + 1)]
        # imp_resp_w = wiener_deconvolution(y, step_func)[:(248)]

        # An FFT-based deconvolution of a step response is fraught since the step response has a
        #  low information FFT. Large at f=0 and then constant at all other frequencies.
        #  seems better to simply take the derivative ... this gives the impulse response
        imp_resp_d = np.gradient(y, t[1]-t[0])
        return imp_resp_d, step_func

    alpha_cmd, step_func = get_impulse(20)
    beta_cc, _ = get_impulse(21)

    fig, ax = plt.subplots()

    # deconvolution is messy -- optimize the step_func that is convolved with beta_cc
    ax.plot(np.convolve(alpha_cmd, step_func, mode='valid') + np.convolve(beta_cc, step_func, mode='valid'))


    fig, ax = plt.subplots()
    ax.plot(y)
    ax.plot(step_func)

    # fig, ax = plt.subplots()
    # ax.plot(imp_resp_w)

    fig, ax = plt.subplots()
    ax.plot(imp_resp_d)

    im_conv = np.convolve(step_func, imp_resp_d, mode='valid')
    fig, ax = plt.subplots()
    ax.plot(im_conv)


# read in all h5 in data_dir and determine peak-area
if 'plot_all_im' in analysis_type:
    # ax, adc_data, t = read_plot(os.path.join(data_dir, f'cc_swp_{i}.h5'), filter_bw=[None])
    h5_files = glob.glob(os.path.join(data_dir, '*.h5'))
    pa_arr = np.array([])
    for hf in h5_files:
        t, adc_data = read_h5(data_dir, hf.split('/')[-1], chan_list=[0])
        pa, num_found = peak_area(t, adc_data[0])
        pa_arr = np.append(pa_arr, pa)
