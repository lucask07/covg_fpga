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
SAMPLE_PERIOD = 1 / 5e6
FS = 5e6
ADC_CROP = 64

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
        t = np.arange(len(dset[0, :])) * SAMPLE_PERIOD
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
    span = int(200e-6/SAMPLE_PERIOD)
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


def get_impulse(data_dir, filename, t_offset_idx=ADC_CROP, t0=6400e-6, tl_tr=(-150e-6, 200e-6),fc=None):
    """ get the impulse of an Im trace by calculating the derivative
    """
    t, adc_data = read_h5(data_dir, filename + '.h5', chan_list=[0])
    t=t[ADC_CROP:]
    adc_data[0]=adc_data[0][ADC_CROP:]

    SAT_VAL = 30000
    if any(np.abs(adc_data[0]) > SAT_VAL):
        print(f'warning {filename} impulse is over {SAT_VAL}')

    idx_signal = idx_timerange(t, t0 + tl_tr[0], t0 + tl_tr[1])
    y = adc_data[0][idx_signal]

    if fc is not None:
        y = butter_lowpass_filter(y, cutoff=fc, fs=FS, order=5)

    #  the Wiener deconvolution adds noise to the denominator so that the result doesn't explode.
    # imp_resp_w = wiener_deconvolution(y, step_func)[:(len(y)-len(step_func) + 1)]
    # imp_resp_w = wiener_deconvolution(y, step_func)[:(248)]

    # An FFT-based deconvolution of a step response is fraught since the step response has a
    #  low information FFT. Large at f=0 and then constant at all other frequencies.
    #  seems better to simply take the derivative ... this gives the impulse response
    imp_resp_d = np.gradient(y, t[1]-t[0])
    return imp_resp_d, t[idx_signal], t0


def im_conv(x, cmd_impulse, cmd_step, cc_impulse, cc_step, adjust_func):
    """ convolve the impulse function with a step function after adjusting the step function
    that is applied to the cc impulse function
    return the sum of the absolute value of the current
    """
    cc_step_adj = adjust_func(x, cc_step)  # adjust_step, adjust_step2
    return np.sum(np.abs(np.convolve(cmd_impulse, cmd_step, mode='valid') + np.convolve(cc_impulse, cc_step_adj, mode='valid')))
