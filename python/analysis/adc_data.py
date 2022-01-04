import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import h5py
import matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()
from filters.filter_tools import butter_lowpass_filter

DATA_DIR = '/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp_test/20220104'
file_name = 'out_clamp_tests_jan4_2.h5'
SAMPLE_RATE = 1 / 5e6

def read_plot(file_name, chan_list=[0]):
    # Post processing: read in h5 data and plot -- this seems to be what drags iPython to a crawl
    data_name = os.path.join(DATA_DIR, file_name)
    fig, ax = plt.subplots()
    with h5py.File(data_name, "r") as file:
        list(file.keys())  # this returns adc
        dset = file["adc"]
        t = np.arange(len(dset[0, :])) * SAMPLE_RATE
        # chan_list = range(4)
        for i in chan_list:
            ax.plot(t, dset[i, :], label=f"Ch: {i}", marker=".")
        ax.legend()
        ax.set_xlabel("Time")
        ax.set_ylabel("DN")
        del dset


def read_h5(file_name, chan_list=[0]):
    # Post processing: read in h5 data and plot -- this seems to be what drags iPython to a crawl
    data_name = os.path.join(DATA_DIR, file_name)
    adc_data = {}
    with h5py.File(data_name, "r") as file:
        list(file.keys())  # this returns adc
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

t, adc = read_h5('out_clamp_tests_jan4_6.h5')
filt_data = butter_lowpass_filter(adc[0], 1e6, 5e6, order=5)
ax = plot_adc(t, filt_data)
filt_data = butter_lowpass_filter(adc[0], 20e3, 5e6, order=5)
plot_adc(t, filt_data)
