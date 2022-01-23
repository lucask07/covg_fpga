"""

General analysis of COVG ADC data (h5 files)
Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os
import sys
import glob
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy.signal import find_peaks, find_peaks_cwt
import pandas as pd
from filters.filter_tools import butter_lowpass_filter

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
SAMPLE_RATE = 1 / 5e6
FS = 5e6


def read_plot(data_dir, file_name, chan_list=[0], filter_bw=None, ax=None,
              clr='b', lbl=None, scaling = 1):
    """ Read in h5 data, plot, and return the axes handle, time and adc_data
        for the channels in input list

    Arguments
    ---------
    data_dir (string): directory of h5 file
    file_name (string): file name (must include extension)
    chan_list (list of ints): adc channels to return
    filter_bw (float): bandwidth of a low-pass filter
    ax (axis handle): axes handle to plot to if None creates new figure (default None)
    clr (string): color of the plot markers
    lbl (string): custom label for the plot if None uses channel and filter bandwidth
    scaling (float): scaling of ADC data in nA/DN. If not 1 labels plots with nA
                     (defaults to 1 and then labels y-axis with DN)

    Returns
    -------
    (axes object) matplotlib axes object
    (numpy.ndarray) time
    (dicionary of numpy.ndarrays) adc data
    """

    # if filter_bw is not a list make it a list
    if not hasattr(filter_bw, '__iter__'):
        filter_bw = [filter_bw]
    # create a new figure
    if ax == None:
        fig, ax = plt.subplots(figsize=(12,8))

    t, adc_data = read_h5(data_dir, file_name, chan_list)

    for ch in chan_list:
        for f_bw in filter_bw:
            if f_bw is not None:
                filt_data = butter_lowpass_filter(adc_data[ch], f_bw, FS, order=5)
                if lbl is None:
                    lbl = f"Ch: {ch}; fc = {int(f_bw/1000)} kHz"
            else:
                filt_data = adc_data[ch]
                if lbl is None:
                    lbl = f"Ch: {ch}"
            ax.plot(t*1e6, filt_data*scaling, label=lbl, marker=".", color=clr)
        ax.set_xlabel("Time [$\mu$s]")
        if scaling == 1:
            ax.set_ylabel("DN")
        else:
            ax.set_ylabel('Im [nA]')
    return ax, t, adc_data


def read_h5(data_dir, file_name, chan_list=[0]):
    """ Read in h5 data and return the time and adc_data for the channels in
        input list

    Arguments
    ---------
    data_dir (string): directory of h5 file
    file_name (string): file name (must include extension)
    chan_list (list of ints): adc channels to return

    Returns
    -------
    (numpy.ndarray) time
    (dicionary of numpy.ndarrays) adc data
    """

    data_name = os.path.join(data_dir, file_name)
    adc_data = {}
    with h5py.File(data_name, "r") as file:
        dset = file["adc"]
        t = np.arange(len(dset[0, :])) * SAMPLE_RATE
        for ch in chan_list:
            adc_data[ch] = dset[ch, :]
    return t, adc_data


def plot_adc(t, data, ax=None):
    """ basic plotting of ADC data

    Arguments
    ---------
    t (ndarray): time [in seconds]
    data (ndarray): ADC data [in DN]
    ax (axes object): Matplotlib axes (defaults to None and then creates a new figure)

    Returns
    -------
    (axes object) matplotlib axes object
    """

    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(t, data, marker=".")
    ax.legend()
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("DN")

    return ax


def find_peak_cwt(t, data, peak_width=40):
    """ Use scipy.signal find_peaks_cwt continuous wavelet transform
        TODO: many input parameters that are not understood

    Arguments
    ---------
    t (ndarray): time [in seconds]
    data (ndarray): ADC data [in DN]
    ax (axes object): Matplotlib axes (defaults to None and then creates a new figure)

    Returns
    -------
    (ndarray) time of the found peaks
    (ndarray) index of the found peaks
    """

    loc_idx = find_peaks_cwt(data, peak_width, min_snr=20)
    if loc_idx is None:
        return None, None
    for pk in loc_idx:
        print(f'Found peak at {t[pk]}')
        return t[loc_idx], loc_idx

def find_peak(t, data, th=100, height=100, distance=1000):
    """ Use scipy.signal find_peaks
        TODO: many input parameters that are not understood

    Arguments
    ---------
    t (ndarray): time [in seconds]
    data (ndarray): ADC data [in DN]
    ax (axes object): Matplotlib axes (defaults to None and then creates a new figure)

    Returns
    -------
    (ndarray) time of the found peaks
    (ndarray) index of the found peaks
    """

    results = find_peaks(data, threshold=th, height=height, distance=distance)
    loc_idx = results[0]
    if loc_idx is None:
        return None, None, None
    for pk in loc_idx:
        print(f'Found peak at {t[pk]}')
        return t[loc_idx], loc_idx, results


def peak_area(t, data, th=5, distance=10000):
    """ Calculate the area of peak(s) in a Waveform
        and return the average

    Arguments
    ---------
    t (ndarray): time [in seconds]
    data (ndarray): ADC data
    th (float): threshold for finding a peak
    distance (float): required distance between peaks

    Returns
    -------
    (float) average peak area
    (int) number of found peaks
    """

    t_peaks, idx_pk, results = find_peak(t, data, th=th, distance=distance)
    # distance of 10000 corresponds to 2 ms at 5 MSPS
    # integrate over a span of the peaks
    span = int(200e-6/SAMPLE_RATE)
    peak_area = np.array([])
    for ix in idx_pk:
        peak_area = np.append(peak_area, np.sum(np.abs(data[(ix-span):(ix+span)])))
    print(f'Found {len(idx_pk)} peaks')
    return np.mean(peak_area), len(idx_pk)


def idx_timerange(t, tlow, thigh):
    """ Get indices for a range of time
        inclusive from tlow to thigh

    Arguments
    ---------
    t (ndarray): time
    tlow (float): low time range
    thigh (float): high time range

    Returns
    -------
    (ndarray) indices (True, False) for whether within range
    """
    idx = ((t>=tlow) & (t<=thigh))
    print(f'Found {np.sum(idx)} points between times of {tlow*1e3} ms and {thigh*1e3} ms')
    print(f'From idx {np.where(idx)[0][0]} to {np.where(idx)[0][-1]}')
    return idx


if __name__ == '__main__':

    analysis_type =['summary_stats']
    filename = 'cc_swp4'
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

        # load CSV summary as Pandas dataframe
        csv_summary = glob.glob(os.path.join(data_dir, f'{filename}_*.csv'))[0]
        output = pd.read_csv(csv_summary)


        # use 7e5 as lowest peak area without acquisition issue
        min_peakarea_ok = 7e4
        idx = output.peak_area > min_peakarea_ok

        # plot trace with minimum peak area
        min_pa = output[idx].peak_area.min()
        min_row = output[output.peak_area == min_pa]
        ax, adc_data, t = read_plot(data_dir, min_row.filename.item() + '.h5', chan_list=[0], filter_bw=None, ax=None, clr='b')
        ax.set_title('Minimum peak area')

        max_pa = output[idx].peak_area.max()
        max_row = output[output.peak_area == max_pa]
        ax, adc_data, t = read_plot(data_dir, max_row.filename.item() + '.h5', chan_list=[0], filter_bw=None, ax=None, clr='b')
        ax.set_title('Maximum peak area')

        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        def find_closest_row(target_dict):

            idx = output['peak_area'] > min_peakarea_ok
            print(f'Length of index = {np.sum(idx)}')

            for k in target_dict:
                unq = np.unique(output[idx][k])
                c = find_nearest(unq, target_dict[k])
                idx = idx & (output[k] == c)
                print(f'Length of index = {np.sum(idx)}')
            return idx

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

    if 'trace_comparison' in analysis_type:
        colors = iter(plt.cm.rainbow(np.linspace(0, 1, np.sum(idx))))
        fn = output[idx].filename
        cc_scale = output[idx].cc_scale
        ax, adc_data, t = read_plot(data_dir, fn.iloc[0] + '.h5', chan_list=[0], filter_bw=None, ax=None, clr=next(colors), lbl='cc = {:.2f}'.format(cc_scale.iloc[0]))
        for f, cc_s in zip(fn[1:], cc_scale[1:]):
            ax, adc_data, t = read_plot(data_dir, f + '.h5', chan_list=[0], filter_bw=None, ax=ax, clr=next(colors), lbl='cc = {:.2f}'.format(cc_s),
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
        ax, adc_data, t = read_plot(data_dir, fn.iloc[0] + '.h5', chan_list=[0], filter_bw=None, ax=None, clr=next(colors), lbl='cc = {:.2f}'.format(cc_delay.iloc[0]))
        for f, cc_s in zip(fn[1:], cc_delay[1:]):
            ax, adc_data, t = read_plot(data_dir, f + '.h5', chan_list=[0], filter_bw=None, ax=ax, clr=next(colors), lbl='delay = {:.2f}'.format(cc_s*1e6),
            scaling = 4)
        ax.legend()
        ax.set_xlim([1400, 3000])
        plt.savefig(os.path.join(data_dir, 'fig_vary_ccdelay'))


    # read in all h5 in data_dir and determine peak-area
    if 'plot_all_im' in analysis_type:
        # ax, adc_data, t = read_plot(os.path.join(data_dir, f'cc_swp_{i}.h5'), filter_bw=[None])
        h5_files = glob.glob(os.path.join(data_dir, '*.h5'))
        pa_arr = np.array([])
        for hf in h5_files:
            t, adc_data = read_h5(data_dir, hf.split('/')[-1], chan_list=[0])
            pa, num_found = peak_area(t, adc_data[0])
            pa_arr = np.append(pa_arr, pa)
