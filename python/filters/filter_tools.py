"""
Filters: low-pass, high-pass, delays

"""
import numpy as np
from numpy.fft import fft, ifftshift, ifft
from numpy import exp, pi, arange, zeros_like, isreal
from scipy import signal
from scipy.interpolate import interp1d


def delayseq_interp(x, delay_sec: float, fs: int):
    """ Delay 1D signal using shift and linear interpolation (no FFT)
        must assume the signal is periodic

    Arguments
    ---------
    x (numpy.ndarray): input 1-D signal
    delay_sec (float): amount to shift signal [seconds]
    fs (float): sampling frequency [Hz]

    Returns
    -------
    (numpy.ndarray) time-shifted signal
    """
    resolution_increase = 20

    assert x.ndim == 1, "only 1-D signals for now"

    t = np.linspace(0, len(x)*(1/fs), len(x))
    f1 = interp1d(t, x, kind='linear')

    # higher resolution signal and time
    tnew = np.linspace(0, len(x)*(1/fs), len(x)*resolution_increase)
    xnew = f1(tnew)

    # determine how much to shift by (in high res samples)
    delay_samples = delay_sec * fs * resolution_increase
    delay_int = -int(delay_samples)  # the algorithm shifts negative delays later in time ... need  to correct

    if delay_int > 0: # append to the end
        xnew = np.concatenate( (xnew, xnew[0:delay_int]) )
        xshift = xnew[delay_int:]
    if delay_int < 0: # append to the start
        xnew = np.concatenate((xnew[delay_int:-1], xnew) )
        xshift = xnew[0:delay_int]
    if delay_int == 0:
        xshift = xnew

    xs = xshift[resolution_increase//2::resolution_increase]

    return xs


def nextpow2(n: int) -> int:
    """
    determine the closest power of two going up
    e.g. 3 returns 4 and
         14 returns 16
    notes: bit_length() is a Python built-in

    Arguments
    ---------
    n: integer to find the closest (larger) power of 2

    Returns
    -------
    integer
    """
    return 2 ** (int(n) - 1).bit_length()


def butter_highpass(cutoff, fs, order=5):
    """ create a Butterworth high pass filter and return the filter coefficients.
    see: https://stackoverflow.com/questions/39032325/python-high-pass-filter

    Arguments
    ---------
    cutoff (float): cutoff frequency [same units as fs]
    fs (float): the sampling frequency [same units as cutoff]
    order (int): filter order (default=5)

    Returns
    -------
    (ndarray) IIR filter numerator coefficients
    (ndarray) IIR filter denominator coefficients
    """

    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    """ Filter data using a Butterworth highpass

    Arguments
    ---------
    data (ndarray): input data to filter as array
    cutoff (float): cutoff frequency [same units as fs]
    fs (float): the sampling frequency [same units as cutoff]
    order (int): filter order (default=5)

    Returns
    -------
    (ndarray) filtered data as array
    """

    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def butter_lowpass(cutoff, fs, order=5):
    """ create a Butterworth low pass filter and return the filter coefficients.
    see: https://stackoverflow.com/questions/39032325/python-high-pass-filter

    Arguments
    ---------
    cutoff (float): cutoff frequency [same units as fs]
    fs (float): the sampling frequency [same units as cutoff]
    order (int): filter order (default=5)

    Returns
    -------
    (ndarray) IIR filter numerator coefficients
    (ndarray) IIR filter denominator coefficients
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    # print(f'Butter: {b}, {a}. Normal cutoff = {normal_cutoff}')
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    """ Filter data using a Butterworth highpass

    Arguments
    ---------
    data (ndarray): input data to filter as array
    cutoff (float): cutoff frequency [same units as fs]
    fs (float): the sampling frequency [same units as cutoff]
    order (int): filter order (default=5)

    Returns
    -------
    (ndarray) filtered data as array
    """
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y
