import numpy as np
import scipy.fftpack
import matplotlib.pyplot as plt
from scipy.signal.windows import hann


def find_nearest(array, target):
    """ find value in an array nearest to a target value

    Arguments
    ---------
    array (numpy.ndarray): array of values
    target (float): target value

    Returns
    -------
    (float) value in the array that is closest to target
    """

    array = np.asarray(array)
    idx = (np.abs(array - target)).argmin()
    return array[idx]


def find_closest_row(df, target_dict, prefilter = ('peak_area', 7e5)):

    if prefilter is not None:
        idx = df[prefilter[0]] > prefilter[1]
        print(f'Length of index = {np.sum(idx)}')
    else:
        idx = [True] * len(df.index)

    for k in target_dict:
        unq = np.unique(df[idx][k])
        c = find_nearest(unq, target_dict[k])
        idx = idx & (output[k] == c)
        print(f'Length of index = {np.sum(idx)}')
    return idx


def calc_fft(data, FS, plot=True, WINDOW='hann'):
    # Number of samplepoints
    N = len(data)
    if WINDOW=='hann': # only supported window 
        window = hann(len(data), sym=False)
    else:
        window = np.ones(len(data))

    # ensure window does not change amplitude
    scale = np.mean(window)
    yf = np.fft.fft(data*window/scale)

    freq = np.fft.fftfreq(N, d=1/FS)

    if plot:
        fig, ax = plt.subplots()
        ax.loglog(freq[:N//2], 2.0/N * np.abs(yf[:N//2]), marker='.', color='k')
        ax.set_xlabel('f [Hz]')
        ax.set_ylabel('|A|')
    else:
        fig=None
        ax=None

    # determine maximum frequency bin (outside of DC)
    max_idx = np.argmax(np.abs(yf[1:N//2]))
    max_freq = freq[1:N//2][max_idx]
    return freq, yf, max_freq, fig, ax


def fft_maxs(data, FS, plot=False, window='hann'):
    # to avoid breaking the interface to calc_fft 
    # add this helper function that gets the amplitude and frequency of the maximum 
    #  frequency point

    if np.mean(data)>0.2:
        print('Warning in fft_maxs: in most case it is best to remove the DC \
              value of the signal')

    N = len(data)
    freq, yf, max_freq, fig, ax = calc_fft(data, FS, plot=plot, WINDOW=window)
    max_idx = np.argmax(np.abs(yf[1:N//2]))
    max_amp = 2.0/N * np.abs(yf[1:N//2])[max_idx]
    max_phase = np.angle(yf[1:N//2][max_idx])

    return freq, max_freq, max_amp, max_phase



def get_impulse(data_dir, filename, t_offset_idx, t0=6400e-6):
    """ get the impulse of an Im trace by calculating the derivative
    """
    t, adc_data = read_h5(data_dir, filename.format(num) + '.h5', chan_list=[0])
    t=t[t_offset_idx:]
    adc_data[0]=adc_data[0][t_offset_idx:]

    idx_signal = idx_timerange(t, t0-150e-6, t0 + 200e-6)
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
    return imp_resp_d