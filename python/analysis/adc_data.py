import os
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
import h5py
import matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()
from filters.filter_tools import butter_lowpass_filter
from scipy.signal import find_peaks, find_peaks_cwt

data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    pass
elif sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp_test/{}{:02d}{:02d}"
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/{}{:02d}{:02d}')

data_dir = data_dir_covg.format(2022, 1, 10)
SAMPLE_RATE = 1 / 5e6
FS = 5e6

def read_plot(file_name, chan_list=[0], filter_bw=None, ax=None, clr='b'):
    
    if not hasattr(filter_bw, '__iter__'):
        filter_bw = [filter_bw]
    # Post processing: read in h5 data and plot -- this seems to be what drags iPython to a crawl
    data_name = os.path.join(data_dir, file_name)
    if ax == None:
        fig, ax = plt.subplots()

    t, adc_data = read_h5(data_name, chan_list)

    for ch in chan_list:
        for f_bw in filter_bw:
            if f_bw is not None:
                filt_data = butter_lowpass_filter(adc_data[ch], f_bw, FS, order=5)
                lbl = f"Ch: {ch}; fc = {int(f_bw/1000)} kHz"
            else:
                filt_data = adc_data[ch]
                lbl = f"Ch: {ch}"
            ax.plot(t*1e6, filt_data, label=lbl, marker=".", color=clr)
        ax.legend()
        ax.set_xlabel("Time [$\mu$s]")
        ax.set_ylabel("DN")
    return ax, adc_data, t


def read_h5(file_name, chan_list=[0]):
    # Post processing: read in h5 data and plot -- this seems to be what drags iPython to a crawl
    data_name = os.path.join(data_dir, file_name)
    adc_data = {}
    with h5py.File(data_name, "r") as file:
        dset = file["adc"]
        t = np.arange(len(dset[0, :])) * SAMPLE_RATE
        for ch in chan_list:
            adc_data[ch] = dset[ch, :]
    return t, adc_data


def plot_adc(t, data, ax=None):

    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(t, data, marker=".")
    ax.legend()
    ax.set_xlabel("Time")
    ax.set_ylabel("DN")

    return ax

def find_peak_cwt(t, data, peak_width=40):

    loc_idx = find_peaks_cwt(data, peak_width, min_snr=20)
    if loc_idx is None:
        return None, None
    for pk in loc_idx:
        print(f'Found peak at {t[pk]}')
        return t[loc_idx], loc_idx

def find_peak(t, data, th=100, height=100,distance=1000):

    results = find_peaks(data, threshold=th, height=height, distance=distance)
    loc_idx = results[0]
    if loc_idx is None:
        return None, None, None
    for pk in loc_idx:
        print(f'Found peak at {t[pk]}')
        return t[loc_idx], loc_idx, results


def peak_area(t, data, th=5, distance=10000):

    t_peaks, idx_pk, results = find_peak(t, data, th=5, distance=10000) # 2 ms
    # integrate over a span of the peaks
    span = int(200e-6/SAMPLE_RATE)
    peak_area = np.array([])
    for ix in idx_pk:
        peak_area = np.append(peak_area, np.sum(np.abs(data[(ix-span):(ix+span)])))
    print(f'Found {len(idx_pk)} peaks')
    return np.mean(peak_area), len(idx_pk)

if __name__ == '__main__':
    t, adc = read_h5(file_name, [0,1])
    ax = plot_adc(t, adc[1])
    filt_data = butter_lowpass_filter(adc[0], 1e6, 5e6, order=5)
    ax = plot_adc(t, filt_data)
    filt_data = butter_lowpass_filter(adc[0], 20e3, 5e6, order=5)
    plot_adc(t, filt_data)



    import time
    for i in range(24):
        read_plot(os.path.join(data_dir, f'cc_swp_neg_{i}.h5'), filter_bw=[None])
        plt.show()
        plt.pause(0.01)
        time.sleep(2)
        plt.close('all')

    i = 0
    # ax, adc_data, t = read_plot(os.path.join(data_dir, f'cc_swp_{i}.h5'), filter_bw=[None])

    t, adc_data = read_h5(os.path.join(data_dir, f'cc_swp_{i}.h5'), chan_list=[0])
    pa, num_found = peak_area(t, adc_data[0])
