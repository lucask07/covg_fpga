"""
Oct 2022
edits Feb 2024 
Lucas Koerner, koerner.lucas@stthomas.edu
"""
import os
import sys
from time import sleep
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

import itertools
plt.ion()
from scipy.optimize import minimize, basinhopping
from scipy.signal import convolve
from scipy import signal
from scipy.fftpack import fft, ifft

from analysis.clamp_data import adjust_step2, adjust_step3
from analysis.adc_data import im_conv, find_peak
from datastream.datastream import h5_to_datastreams
from filters.filter_tools import butter_lowpass_filter, butter_highpass_filter
from analysis.utils import my_savefig, fig_size # also configures matplotlib defautls 

def wiener_deconvolution(signal, kernel, lambd):
    '''
    Deconvolve kernel from signal 
    Parameters: 

        signal: 
        kernel: len(kernel) < len(signal)
        lambd: SNR 

    returns 
    1d array of length of signal 
    '''

    # left zero pad the filtering kernel response since we know that the kernel should be exactly zero
    #  before the signal arrives (causal system)
    kernel = np.hstack((np.zeros(len(signal) - len(kernel)), kernel)) # zero pad the kernel to same length
    H = fft(kernel)/len(kernel)
    F_sig = fft(signal)/len(signal)
    deconvolved = np.real(ifft(F_sig*np.conj(H)/(H*np.conj(H) + lambd**2)))
    return deconvolved


class ImpulseResponse():

    def __init__(self, values, ts, t0):
        self.values = values
        self.ts = ts
        self.t0 = t0

    def create_time(self):
        return np.linspace(-self.t0, (len(self.values) - 1)*self.ts-self.t0, len(self.values))

def cc_waveform(ds, l=0.0035, fc=20e3):

    # ds: dictionary with keys CMD0, CC0 
    # l: noise parameter for Wiener deconvolution 
    # fc: cutoff frequency [Hz] for low-pass filtering of CC waveform 

    # TODO: add a way to crop/pad to reduce/expand the extent of the CC waveform 

    # find peaks 
    pos_pks = find_peak(ds['CMD0']['CMD0'].create_time(), 
        np.diff(ds['CMD0']['CMD0'].data), 
        th=0.5e-3, height=2e-3, distance=100)

    # get impulse response of both 
    impulse = {}
    impulse_c = {}
    t_imp = {}
    for imp_on in ['CMD0', 'CC0']:
        step_idx = pos_pks[1][0]
        t0 = ds[imp_on][imp_on].create_time()[step_idx]
        # get_impulse calculates the gradient after a Butterworth filter 
        #   default filter order was 5, but this shows considerable ringing in the CC impulse response 
        #   add 50 us to each side to avoid edge effects in the impulse response
        #   symmetric about t0 so that the convolution of a step and the impulse is centered at 0
        tl = -450/1e6
        tr = 450/1e6
        impulse[imp_on], t_imp[imp_on], t0 = ds[imp_on]['Im'].get_impulse(t0=t0, tl_tr=(tl, tr),
                                                                  fc=500e3, order=1)
        impulse_c[imp_on] = ImpulseResponse(impulse[imp_on], ts=t_imp[imp_on][1]-t_imp[imp_on][0], t0=tr)
        print(t0)

    # span just the current peak 
    tl_tr = (-10e-6, 1000e-6) # steps are separated by more the 20 ms 
    t0 = pos_pks[0][0]
    t = ds['CMD0']['Im'].create_time()
    tlow = t0 + tl_tr[0]
    thigh = t0 + tl_tr[1]
    im_idx = ((t>=tlow) & (t<=thigh))
    t = (t[im_idx] - t0)*1e6

    im_deconv = ds['CMD0']['Im'].data[im_idx]
    impulse_idx = ((t_imp['CMD0']>=tlow) & (t_imp['CMD0']<=thigh))
    impulse_deconv = impulse['CMD0'][impulse_idx] 

    # generate waveform for cc that should cancel 
    impulse_deconv = impulse['CC0'][impulse_idx]  # 600 us at 5 MSPS
    cc_wave = wiener_deconvolution(-(im_deconv), impulse_deconv, lambd=l)  # im_deconv is Im for deconvolution

    fs = 1/impulse_c['CC0'].ts

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html
    lpf_fs = fc 
    order = 3
    b,a = signal.butter(order, [lpf_fs], fs=fs, btype='lowpass')    
    # forward and backward filter for zero phase is preferred over a causal filter 
    filtered_cc_wave = signal.filtfilt(b,a,cc_wave, padlen=300)
    # window this signal so that it starts and ends at zero 
    win = signal.windows.hann(len(filtered_cc_wave))
    peak = np.max(filtered_cc_wave) - np.min(filtered_cc_wave) # TODO: Qtot: better way to find this?? 
    step2 = -np.ones(len(filtered_cc_wave))*peak/2
    step2[0:int(len(filtered_cc_wave)/2)] = peak/2
    filtered_cc_wave  = win*filtered_cc_wave + (1-win)*step2

    return filtered_cc_wave, cc_wave, impulse_c


"""
analyze data captured
"""
if sys.platform == 'darwin':
    data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/'
    fig_dir = '/Users/koer2434/My Drive/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/figures/cc'
elif sys.platform == 'win32':
    data_dir = r'C:/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/'

subdir = 'clamp/20240223/'
cc_file = 'clamptest1_quietdacsFalse_rtia33_ccomp47_inamp2_cmdval0_ccval512.h5'
cmd_file = 'clamptest1_quietdacsFalse_rtia33_ccomp47_inamp2_cmdval512_ccval0.h5'


if __name__ == '__main__':

    ds = {}
    ds['CMD0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cmd_file)
    ds['CC0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cc_file)

    filtered_cc_wave1, cc_wave1, impulse_c1 = cc_waveform(ds, l=0.0035, fc=20e3)

    # find peaks 
    fig,ax = plt.subplots(figsize=fig_size)
    ds['CMD0']['CMD0'].plot(ax, {'label':'CMD'})
    ds['CC0']['CC0'].plot(ax, {'label':'CC'})
    ax.legend()
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$V$')
    # step response of CMD and CC as a sanity check 
    my_savefig(fig, fig_dir, 'step_response')

    pos_pks = find_peak(ds['CMD0']['CMD0'].create_time(), 
        np.diff(ds['CMD0']['CMD0'].data), 
        th=1e-3, height=10e-3, distance=100)

    neg_pks = find_peak(ds['CMD0']['CMD0'].create_time(), 
        -np.diff(ds['CMD0']['CMD0'].data), 
        th=1e-3, height=10e-3, distance=100)
    # assume CC and CMD peaks are at the same time 

    # span for figures 
    span_left = -50
    span_right = 400
    peak_time = pos_pks[0][0]*1e6

    # current step response: zoom in to first positive peak 
    fig,ax = plt.subplots(figsize=fig_size)
    t = ds['CMD0']['Im'].create_time()*1e6-peak_time
    idx = (t > span_left) & (t < span_right)
    ax.plot(t[idx], ds['CMD0']['Im'].data[idx]*1e6, label='CMD')
    t = ds['CC0']['Im'].create_time()*1e6-peak_time
    idx = (t > span_left) & (t < span_right)
    ax.plot(t[idx], ds['CC0']['Im'].data[idx]*1e6, label='CC')
    ax.legend()
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$I_m \; [\mu A]$')
    ax.set_xlim([span_left, span_right])
    my_savefig(fig, fig_dir, 'Im_step_response')


    impulse = {}
    impulse_c = {}
    t_imp = {}
    for imp_on in ['CMD0', 'CC0']:
        step_idx = pos_pks[1][0]
        t0 = ds[imp_on][imp_on].create_time()[step_idx]
        # get_impulse calculates the gradient after a Butterworth filter 
        #   default filter order was 5, but this shows considerable ringing in the CC impulse response 
        #   add 50 us to each side to avoid edge effects in the impulse response
        #   symmetric about t0 so that the convolution of a step and the impulse is centered at 0
        tl = -450/1e6
        tr = 450/1e6
        impulse[imp_on], t_imp[imp_on], t0 = ds[imp_on]['Im'].get_impulse(t0=t0, tl_tr=(tl, tr),
                                                                  fc=500e3, order=1)
        impulse_c[imp_on] = ImpulseResponse(impulse[imp_on], ts=t_imp[imp_on][1]-t_imp[imp_on][0], t0=tr)
        print(t0)

    fig,ax = plt.subplots(figsize=fig_size)
    ax.plot((impulse_c['CMD0'].create_time())*1e6, impulse_c['CMD0'].values)
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$h \; [\mu A/\mu s]$') 

    # plot the impulse response 
    fig,ax = plt.subplots(nrows=2, ncols=1, figsize=fig_size)
    t = t_imp['CMD0']*1e6 - peak_time
    idx = (t > span_left) & (t < span_right)
    ax[0].plot(t[idx], impulse['CMD0'][idx], label='CMD') # marker='+'
    t = t_imp['CC0']*1e6 - peak_time
    idx = (t > span_left) & (t < span_right)
    ax[1].plot(t[idx], impulse['CC0'][idx], label='CC', color='tab:orange') #  marker='.', 
    ax[0].legend()
    ax[1].legend()
    ax[0].set_xlabel('time [$\mu$s]')
    ax[1].set_xlabel('time [$\mu$s]')
    ax[0].set_ylabel('$h \; [\mu A/\mu s]$') 
    ax[1].set_ylabel('$h \; [\mu A/\mu s]$') 
    ax[1].set_xlim([-20, 50]) 
    my_savefig(fig, fig_dir, 'impulse_response')


    # create a step function and convolve impulse and step
    # this is a sanity check to ensure the impulse response is working as anticipated
    t = ds[imp_on]['Im'].create_time()
    t_idx = (t>(t0-1000e-6)) & (t<(t0+1000e-6)) # needs to have a length longer than t_imp so that 'valid' convolution works 
    step_t = t[t_idx]
    step_func = np.zeros(len(step_t))
    step_func[step_t>t0] = 1
    step_t = step_t - t0

    # get time from the input signal 

    # full: N+M-1  - everywhere 
    # same: max(N,M) 
    # valid: max(M,N) - min(M,N) + 1 -- overlap completely  

    fig,ax=plt.subplots(figsize=fig_size)
    ax.plot(step_t*1e6, np.convolve(impulse['CMD0'], step_func, 'same'), label='CMD') # step_t*1e6, 
    ax.plot(step_t*1e6, np.convolve(impulse['CC0'], step_func, 'same'), label='CC') # step_t*1e6, 
    ax.legend()
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$I_m \; [\mu A]$')
    ax.set_xlim([span_left, span_right])
    my_savefig(fig, fig_dir, 'convolution')

    # Guide to using deconvolve
    # https://stackoverflow.com/questions/40615034/understanding-scipy-deconvolve
    # 1) the filter should be shorter than the signal
    # 2) the filter should be such that it's much bigger then zero everywhere

    # https://dsp.stackexchange.com/questions/78319/approximating-inverse-of-unstable-difference-of-gaussians-filter/78325#78325

    im_cmd_conv = np.convolve(impulse['CMD0'], step_func) # step function has a sampling rate of 5 MHz (T = 200 ns)
    peak_imp = np.argmax(impulse['CC0'])

    # span just the current peak 
    tl_tr = (-10e-6, 1000e-6) # steps are separated by more the 20 ms 
    t0 = pos_pks[0]
    t = ds['CMD0']['Im'].create_time()
    tlow = t0 + tl_tr[0]
    thigh = t0 + tl_tr[1]
    im_idx = ((t>=tlow) & (t<=thigh))
    t = (t[im_idx] - t0)*1e6

    im_deconv = ds['CMD0']['Im'].data[im_idx]
    impulse_idx = ((t_imp['CMD0']>=tlow) & (t_imp['CMD0']<=thigh))
    impulse_deconv = impulse['CMD0'][impulse_idx] 

    fig,ax = plt.subplots(figsize=fig_size, nrows=4)
    ax[0].plot(im_deconv*1e6, 'b', label='Meas:Im')
    ax[0].legend()
    ax[1].plot(impulse_deconv, 'r', label='h_{CMD}')
    ax[1].legend()
    ax[2].plot(im_cmd_conv, 'm', label='h_{CMD}*step')

    print('Length of signal {} and length of filter/impulse response {}'.format(len(im_deconv), len(impulse_deconv)))
    colors = itertools.cycle(['b', 'g', 'm', 'r'])
    noise_levels = [0.002, 0.0035, 0.005, 0.01, 0.02] # in units of uA
    cmd_waves = {}
    for l in noise_levels:
        # the deconvolution is wiener_deconvolution(signal, impulse) --> the output length matches the signal
        cmd_waves[l] = wiener_deconvolution(im_deconv, impulse_deconv, lambd=l*1e-6)
        ax[3].plot(t, np.real(cmd_waves[l]), next(colors), label='deconv(CMD)@{}'.format(l))
    ax[3].legend()

    fig,ax = plt.subplots(figsize=fig_size)
    colors = itertools.cycle(['b', 'g', 'm', 'r'])
    for l in noise_levels:
        conv = np.convolve(impulse_deconv, cmd_waves[l], 'same') # impulse response, input CMD waveform
        pedestal_conv = np.mean(conv[:-99:-1])
        ax.plot(t, (conv-pedestal_conv), next(colors), label='$h_{CMD}$'+':{}'.format(l))

    # the step response cannot extract dc offset. So remove on our own. 
    pedestal_im = np.mean(im_deconv[:-99:-1])
    ax.plot(t, (im_deconv - pedestal_im)*1e6, 'k', label='Im') # im_deconv is a subset of the Im measurement 
    ax.legend()
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$I_m \; [\mu A]$')
    ax.set_xlim([span_left, span_right])
    my_savefig(fig, fig_dir, 'CMD_deconv_vs_SNR')

    # repeat but now generate waveform for cc that should cancel 
    cc_waves = {}
    l = 0.0035 # best choice of noise for the Weiner filter 
    impulse_deconv = impulse['CC0'][impulse_idx]  # 600 us at 5 MSPS
    cc_waves[l] = wiener_deconvolution(-(im_deconv), impulse_deconv, lambd=l)  # im_deconv is Im for deconvolution

    # plot the CC waveform 
    fig,ax = plt.subplots(figsize=fig_size)
    ax.plot(cc_waves[l]) # TODO: how to time align 
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$V$')
    # ax.set_xlim([span_left, span_right])
    my_savefig(fig, fig_dir, 'CC_waveform_cancelation')

    # TODO: 
    # 1) bandpass filter the CC waveform -- done. 
    # 2) time alignment of CMD and CC 
    # 3) loss metric 

    filtered_cc_wave = {} 
    fig,ax = plt.subplots(figsize=fig_size)
    ax.plot(cc_waves[l], label='Full BW')
    fs = 1/impulse_c['CC0'].ts
    for fc in [200e3]:
    #for fc in [50e3, 100e3, 200e3, 500e3]:
        #TODO: consider filtfilt 
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html

        lpf_fs = fc 
        hpf_fs = 2000 # high pass filter cutoff 
        order = 3
        # b,a = signal.butter(order, [hpf_fs, lpf_fs], fs=fs, btype='bandpass')
        b,a = signal.butter(order, [lpf_fs], fs=fs, btype='lowpass')    
        # forward and backward filter for zero phase is preferred over a causal filter 
        filtered_cc_wave[fc] = signal.filtfilt(b,a,cc_waves[l], padlen=300)
        # window this signal so that it starts and ends at zero 
        win = signal.windows.hann(len(filtered_cc_wave[fc]))
        peak = np.max(filtered_cc_wave[fc]) - np.min(filtered_cc_wave[fc])
        step2 = -np.ones(len(filtered_cc_wave[fc]))*peak/2
        step2[0:int(len(filtered_cc_wave[fc])/2)] = peak/2
        filtered_cc_wave[fc] = win*filtered_cc_wave[fc] + (1-win)*step2
        
        #filtered_cc_wave[fc] = butter_lowpass_filter(cc_waves[l], fc, fs, order=1)
        #filtered_cc_wave[fc] = butter_highpass_filter(filtered_cc_wave[fc], 500, fs, order=1)
        ax.plot(filtered_cc_wave[fc], label='{} Hz'.format(fc))

        fig1,ax1 = plt.subplots(figsize=fig_size, nrows=3)
        cc_im = np.convolve(impulse_deconv, filtered_cc_wave[fc], mode='valid')
        stop_idx = len(cc_im)
        t = np.linspace(0, impulse_c['CC0'].ts*(stop_idx-1),  num=stop_idx)*1e6
        # cc_im = np.hstack( (cc_im, np.zeros( (len(im_deconv) - len(cc_im
        ax1[0].plot(t, (cc_im)*1e6, 'tab:blue', label='$h_{CC} \ast CC_{wave}$')
        # ax[0].plot( (cc_waves[l]), 'tab:red', label='$CC_{wave}$')
        ax1[1].plot(t, (im_deconv[:stop_idx])*1e6, label='CMD')
        # TODO: take care of pedestals 
        ax1[2].plot(t, (cc_im + im_deconv[:stop_idx])*1e6, label=f'CMD+CC@{fc} Hz')

        for i in range(3):
            ax1[i].legend()
            ax1[i].set_ylabel('$I_m \; [\mu A]$')
        ax1[2].set_xlabel('time [$\mu$s]')

    ax.legend()


# TODO: consider setting a support so that non-zero CC only lasts for x us (50 us)
# my_savefig(fig, fig_dir, 'cc_cancellation')

## ---------- NOTES --------------

# These deconvolution methods do not work well because of noise
# cmd_wave, remainder = signal.deconvolve( np.hstack((im_deconv*1e6, np.zeros((1000)))), 
#                                          np.hstack((impulse_deconv,np.zeros((1000)))))

# N = 2**(np.ceil(np.log2(len(im_deconv) + len(impulse_deconv))))
# cmd_wave = ifft(fft(im_deconv*1e6, int(N)) / fft(impulse_deconv, int(N)))