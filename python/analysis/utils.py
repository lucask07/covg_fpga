import os
import numpy as np
import scipy.fftpack
import matplotlib.pyplot as plt
from scipy.signal.windows import hann
from scipy.signal import correlate, correlation_lags


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

def phase_by_xcorr(freq, t, data, dac_wave=None, debug_plots=False):
    # determine the phase of a sinusoid at a given frequency
    VERBOSE = False 
    # remove mean of data 
    fs = 1/(t[1]-t[0])
    data = data - np.mean(data)
    amp = np.sqrt(2)*np.std(data)

    if dac_wave is None:
        ideal_sine = amp*np.sin(2*np.pi*freq*t)
        amp_ratio = amp
    else:
        dac_wave = dac_wave - np.mean(dac_wave)
        amp_ratio = np.sqrt(2)*np.std(dac_wave)/amp
        ideal_sine = amp*dac_wave/np.max(dac_wave)
    
    n_period = int(np.ceil(fs/freq))
    n_period_float = fs/freq
    # TODO: limit to 20 periods so that small frequency errors don't cause problems 
    data_range = n_period*20
    xc = correlate(ideal_sine[:n_period], data[:data_range], mode='same')
    lags = correlation_lags(len(ideal_sine[:n_period]), 
                            len(data[:data_range]), mode='same')

    if debug_plots and VERBOSE:
        print(f'Sampling freq. {fs}')
        plt.figure()
        plt.plot(t, ideal_sine, linestyle = '--', label='ideal sine', marker='.')
        plt.plot(t, data, 'k', label='data', marker='.')

    angle = (t * freq * 2 * np.pi) % (2*np.pi)
    # index of 1 period 
    if debug_plots:
        fig, ax = plt.subplots(2,1)
        ax[0].plot(ideal_sine[:n_period])
        ax[0].plot(data)
        ax[1].plot(lags, xc)
        ax[1].plot(lags, angle[0:len(lags)]*100)

    maxa_idx = np.argmax(xc[:int(n_period/2)])
    lag = lags[maxa_idx] % n_period_float
    maxangle = (lag * (2*np.pi)/n_period_float) % (2*np.pi)

    if debug_plots:
        print(f'Max xcorr index {maxa_idx} search up to {int(n_period/2)}')
        print(f'phase shift (radians): {maxangle}, (degrees) {np.degrees(maxangle)} ')
        print(f'Amplitude ratio: {amp_ratio}, {20*np.log10(amp_ratio)} ')

        if dac_wave is None:
            ideal_sine_shift = amp*np.sin(2*np.pi*freq*t + maxangle)
            t_shift = t
        else:
            print(f'Shifting reference input by lag of {lag}')
            if int(lag)>0:
                ideal_sine_shift = ideal_sine[int(lag):]
                t_shift = t[:-int(lag)]
            else:
                ideal_sine_shift = ideal_sine
                t_shift = t 

        plt.figure()
        plt.plot(t, data, 'k', label='data')
        plt.plot(t, ideal_sine, linestyle = '--', label='ideal sine')
        plt.plot(t_shift, ideal_sine_shift, 'r', marker='.', label='shifted_sine')
        plt.title('after phase shift by xcorr')
        plt.legend()

    return maxangle, lag, n_period_float, amp_ratio


def fft_maxs(data, FS, method='quad_interpolate', 
             plot=False, window='hann'):
    # to avoid breaking the interface to calc_fft 
    # add this helper function that gets the amplitude and frequency of the maximum 
    #  frequency point

    if np.mean(data)>0.2:
        print('Warning in fft_maxs: in most case it is best to remove the DC \
              value of the signal')

    N = len(data)
    freq, yf, max_freq, fig, ax = calc_fft(data, FS, plot=plot, WINDOW=window)
    
    if method == 'single_bin':
        max_idx = np.argmax(np.abs(yf[1:N//2]))
        max_amp = 2.0/N * np.abs(yf[1:N//2])[max_idx]
        max_phase = np.angle(yf[1:N//2][max_idx])
    if method == 'quad_interpolate': #https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html
        max_idx = np.argmax(np.abs(yf[1:N//2]))
        beta = np.abs(yf[1:N//2])[max_idx]
        alpha = np.abs(yf[1:N//2])[max_idx-1]
        gamma = np.abs(yf[1:N//2])[max_idx+1]

        p = 1/2*(alpha-gamma)/(alpha - 2*beta + gamma)
        max_freq = max_freq + p*(freq[1] - freq[0])
        max_amp = 2.0/N * (beta - 1/4*(alpha-gamma)*p)
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


def my_savefig(fig, figure_dir, figname):
    """ 
    save a figure given a handle and directory
    Params: 
        fig: matplotlib handle
        figure_dir: directory 
        figname: desired output name 

    Returns:
        None
    """
    fig.tight_layout()
    for e in ['.png', '.pdf']: # use pdf rather than eps to support transparency
        fig.savefig(os.path.join(figure_dir,
                                 figname + e))