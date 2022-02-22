import numpy as np
import scipy.fftpack

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


def calc_fft(data, FS, plot=True):
    # Number of samplepoints
    N = len(data)

    yf = np.fft.fft(data)

    freq = np.fft.fftfreq(N, d=1/FS)

    if plot:
        fig, ax = plt.subplots()
        ax.loglog(freq[:N//2], 2.0/N * np.abs(yf[:N//2]))
        ax.set_xlabel('f [Hz]')
        ax.set_ylabel('|A|')
