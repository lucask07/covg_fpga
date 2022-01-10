"""
delays signal (non-integer delays) using FFT frequency-dependent phase shift

delayseq from here: https://github.com/space-physics/piradar/blob/main/piradar/delayseq.py
with Apache2.0 license
TODO: understand impacts of this licence

"""
from numpy.fft import fft, ifftshift, ifft
from numpy import exp, pi, arange, zeros_like, isreal
from scipy import signal

def delayseq(x, delay_sec: float, fs: int):
    """
    x: input 1-D signal
    delay_sec: amount to shift signal [seconds]
    fs: sampling frequency [Hz]
    xs: time-shifted signal
    """

    assert x.ndim == 1, "only 1-D signals for now"

    delay_samples = delay_sec * fs
    delay_int = round(delay_samples)

    nfft = nextpow2(x.size + delay_int)

    fbins = 2 * pi * ifftshift((arange(nfft) - nfft // 2)) / nfft

    X = fft(x, nfft)
    Xs = ifft(X * exp(-1j * delay_samples * fbins))

    if isreal(x[0]):
        Xs = Xs.real

    xs = zeros_like(x)
    xs[delay_int:] = Xs[delay_int : x.size]

    return xs


def nextpow2(n: int) -> int:
    return 2 ** (int(n) - 1).bit_length()

# https://stackoverflow.com/questions/39032325/python-high-pass-filter
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y
