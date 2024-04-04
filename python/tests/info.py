import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from analysis.adc_data import *
from scipy.fft import fft, fftfreq
from scipy import signal
from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams

data_dir0 = "C:\\Users\\gagn7324\\Documents\\covg\\data\\clamp\\bathclamp_vclamp_step_response_tests\\LightsOffClosedBox\\"
data_dir1 = "C:\\Users\\gagn7324\\Documents\\covg\\data\\clamp\\bathclamp_vclamp_step_response_tests\\LightsOnClosedBox\\"
data_dir2 = "C:\\Users\\gagn7324\\Documents\\covg\\data\\clamp\\bathclamp_vclamp_step_response_tests\\LightsOnOpenBox\\"
data_dir3 = "C:\\Users\\gagn7324\\Documents\\covg\\data\\clamp\\20240103"
file_name0123 = "test"


datastreams = h5_to_datastreams(data_dir3, file_name0123)

"""
Keys: 'CC0', 'CC1', 'CMD0', 'CMD1', 'I', 'Im', 'Itop', 'OBSV', 'OBSV_CH1', 'P1', 'PI_ERR', 'V1', 'metadata'
"""

def fastFourierPlot(dictionary):
    sampleRate = datastreams[dictionary].sample_rate
    N = datastreams[dictionary].data.size #number of data points
    T = 1 / sampleRate #spacing
    data = datastreams[dictionary].data 
    
    plt.subplots()
    fftData = fft(data) #fast fourier transform
    xf = fftfreq(N, T)[:N//2] #makes all x values on plot
    plt.semilogx(xf, np.abs(fftData[0:N//2])) #plots positive freq on log scale
    plt.suptitle("Fast Fourier Transform")
    
    plt.subplots()
    f, Pxx_den = signal.welch(data, sampleRate, nperseg=4096) #reduces varience in data
    plt.semilogx(f, Pxx_den) #plotted on log scale
    plt.suptitle("Power Density of Fourier Transform")
    
def signaltonoise(dictionary, axis=0, ddof=0):
    a = np.asanyarray(datastreams[dictionary].data)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return 20*np.log10(abs(np.where(sd == 0, 0, m/sd)))
    
# Finds noise over level part of signal
def noiseLevelFinder(dictionary, timeRange):
    t = datastreams[dictionary].create_time()
    idx = (t>=timeRange[0]) & (t<=timeRange[1])
    y = datastreams[dictionary].data[idx]
    array = np.asanyarray(y)
    std = np.std(array)
    noise = 20 * np.log10(std)
    return noise

# The two data sets I care about, Im and CMD0
plotKey = "Im"
# Im saturates at 82.8 microamps which is -34.64 dB
ImSignal = -34.64
ImNoise = noiseLevelFinder(plotKey, [0.001, 0.025])
print(f"{plotKey} has {round(ImSignal,1)}dB of signal")
print(f"{plotKey} has {round(ImNoise,1)}dB of noise")
print(f"Signal-to-noise ratio is {ImSignal/ImNoise}")
plt.plot(datastreams[plotKey].create_time(), datastreams[plotKey].data)
plt.suptitle(plotKey)

#fastFourierPlot(plotKey)
