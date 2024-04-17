"""
Oct 2022
edits Feb 2024 
Lucas Koerner, koerner.lucas@stthomas.edu
"""
import os
os.environ['KMP_DUPLICATE_LIB_OK']="TRUE" # this is a workaround for an issue once pytorch was installed 

import sys
from time import sleep
import datetime
import time
import os 
import pickle
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

from analysis.audiotorch_cc import train_net 
import torch

def wiener_deconvolution(signal, kernel, lambd, fs = None):
    '''
    Deconvolve kernel from signal 
    Parameters: 

        signal: 
        kernel: len(kernel) < len(signal)
        lambd: SNR 

    returns 
    1d array of length of signal 
    '''

    if fs is not None:
        freq_res = fs/len(signal)
        print('Wiener Deconv freq res = {}'.format(freq_res))

    # left zero pad the filtering kernel response since we know that the kernel should be exactly zero
    #  before the signal arrives (causal system)
    kernel = np.hstack((np.zeros(len(signal) - len(kernel)), kernel)) # zero pad the kernel to same length
    H = fft(kernel)/len(kernel)
    F_sig = fft(signal)/len(signal)
    deconvolved = np.real(ifft(np.conj(H)*F_sig)/(H*np.conj(H) + lambd**2))
    return deconvolved


class ImpulseResponse():

    def __init__(self, values, ts, t0, tl_tr, step_pkpk):
        self.values = values
        self.ts = ts
        self.t0 = t0
        self.tl = tl_tr[0]
        self.tr = tl_tr[1]
        self.step_pkpk = step_pkpk

    def create_time(self):
        return np.linspace(self.tl + self.t0, (len(self.values) - 1)*self.ts + self.tl + self.t0, len(self.values))

def cc_waveform(ds, l=0.0035, fc=20e3, vstep=None, win_len=None):

    # creates a CC waveform from two datastream measurements 
    # of the step response of both the CMD and CC terminals

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
    t_imp = {}
    for imp_on in ['CMD0', 'CC0']:
        step_idx = pos_pks[1][0]
        t0 = ds[imp_on][imp_on].create_time()[step_idx]
        # get_impulse calculates the gradient after a Butterworth filter 
        #   default filter order was 5, but this shows considerable ringing in the CC impulse response 
        #   add 50 us to each side to avoid edge effects in the impulse response
        #   symmetric about t0 so that the convolution of a step and the impulse is centered at 0

        # length of impulse is 4501 ~ 900e-6/200e-9
        tl = -450/1e6
        tr = 450/1e6
        # the units from get impulse are Amps/seconds = uA/us 
        impulse_tmp, t_imp[imp_on], t0 = ds[imp_on]['Im'].get_impulse(t0=t0, tl_tr=(tl, tr),
                                                                  fc=500e3, order=1)
        impulse[imp_on] = ImpulseResponse(impulse_tmp, ts=t_imp[imp_on][1]-t_imp[imp_on][0], 
                                          t0=t0, tl_tr=(tl,tr), 
                                          step_pkpk=np.max(np.diff(ds[imp_on][imp_on].data)))
        print('Time zero for impulse: {}'.format(t0))

    # span just the current peak 
    tl_tr = (-10e-6, 1000e-6) # steps are separated by more the 20 ms 
    t0 = pos_pks[0][0]
    tlow = t0 + tl_tr[0]
    thigh = t0 + tl_tr[1]
    t = ds['CMD0']['Im'].create_time()
    im_idx = ((t>=tlow) & (t<=thigh))
    t = (t[im_idx] - t0)*1e6

    im_deconv = ds['CMD0']['Im'].data[im_idx]
    impulse_idx = ((t_imp['CMD0']>=tlow) & (t_imp['CMD0']<=thigh))
    impulse_deconv = impulse['CMD0'].values[impulse_idx] 

    # generate waveform for cc that should cancel using Wiener deconvolution 
    impulse_deconv = impulse['CC0'].values[impulse_idx]  # 600 us at 5 MSPS
    impulse_deconv = impulse_deconv - np.mean(impulse_deconv)
    cc_wave = wiener_deconvolution(-(im_deconv), impulse_deconv, lambd=l, fs=5e6)  # im_deconv is Im for deconvolution

    fs = 1/impulse['CC0'].ts

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html
    lpf_fs = fc 
    order = 3
    b,a = signal.butter(order, [lpf_fs], fs=fs, btype='lowpass')    
    # forward and backward filter for zero phase is preferred over a causal filter 
    filtered_cc_wave = signal.filtfilt(b,a,cc_wave, padlen=300) # TODO: why 300? 
    # window this signal so that it starts and ends at zero 

    if win_len is None:
        win = signal.windows.hann(len(filtered_cc_wave))
    else:
        # this doesn't work, would need to pad this to match length of filtered_cc_wave 
        win = signal.windows.hann(win_len)
    if vstep is None:
        vstep = np.max(filtered_cc_wave) - np.min(filtered_cc_wave) # TODO: Qtot: better way to find this?? 
    step2 = np.zeros(len(filtered_cc_wave)) -vstep/2
    step2[0:int(len(filtered_cc_wave)/2)] = vstep/2
    windowed_filtered_cc_wave  = win*filtered_cc_wave + (1-win)*step2

    return windowed_filtered_cc_wave, filtered_cc_wave, cc_wave, impulse, pos_pks

"""
analyze data captured
"""
if sys.platform == 'darwin':
    data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/'
    fig_dir = '/Users/koer2434/My Drive/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/cc'
elif sys.platform == 'win32':
    data_dir = r'C:/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/'
    fig_dir = r'C:/Users/Public/Documents/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/cc/'

subdir = 'clamp/20240223/'
cc_file = 'clamptest1_quietdacsFalse_rtia33_ccomp47_inamp2_cmdval0_ccval512.h5'
cmd_file = 'clamptest1_quietdacsFalse_rtia33_ccomp47_inamp2_cmdval512_ccval0.h5'

subdir = 'c:\\Users\\koer2434\\Documents\\covg\\data\\clamp\\20240412\\'
subdir = 'c:\\Users\\koer2434\\Documents\\covg\\data\\clamp\\20240413\\'

cc_file = 'cc_impulse.h5'
cmd_file = 'cmd_impulse.h5'

ds = {}
ds['CMD0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cmd_file)
ds['CC0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cc_file)

windowed_filtered_cc_wave, filtered_cc_wave1, cc_wave1, impulse_c1, pos_pks = cc_waveform(ds, l=0.0035, 
    fc=200e3, vstep=7e-5)
windowed_filtered_cc_wave, filtered_cc_wave1, cc_wave1, impulse_c1, pos_pks = cc_waveform(ds, l=1e-6, fc=200e3)

fig,ax=plt.subplots()
ax.plot(windowed_filtered_cc_wave)
ax.plot(filtered_cc_wave1)
ax.plot(cc_wave1)


def main():
    ds = {}
    ds['CMD0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cmd_file)
    ds['CC0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cc_file)

    configs = {}
    configs['cmd_val'] = ds['CMD0'].cmd_val
    configs['cc_val'] = ds['CC0'].cc_val
    configs['cmd_conv_factor'] = ds['CMD0']['CMD0'].conversion_factor
    configs['cc_conv_factor'] = ds['CC0']['CC0'].conversion_factor

    windowed_filtered_cc_wave, filtered_cc_wave1, cc_wave1, impulse, pos_pks = cc_waveform(ds, l=0.0035, fc=20e3)

    # find peaks 
    fig,ax = plt.subplots(figsize=fig_size)
    ds['CMD0']['CMD0'].plot(ax, {'label':'CMD'})
    ds['CC0']['CC0'].plot(ax, {'label':'CC'})
    ax.legend()
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$V$')
    # step response of CMD and CC as a sanity check 
    my_savefig(fig, fig_dir, 'step_response')

    # span for figures 
    span_left = -50 # in us 
    span_right = 400 # in us 
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

    # the CC impulse needs zero mean to ensure Qtot=0 with an impulse
    fig,ax = plt.subplots(figsize=fig_size)
    ax.plot((impulse['CMD0'].create_time())*1e6, impulse['CMD0'].values)
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$h \; [\mu A/ (mV \cdot \mu s)]$') 

    # plot the impulse response 
    fig,ax = plt.subplots(nrows=2, ncols=1, figsize=fig_size)
    t = impulse['CMD0'].create_time()*1e6 - peak_time
    idx = (t > span_left) & (t < span_right)
    # .values have units of Amps
    # .step_pkpk has units of Volts 
    ax[0].plot(t[idx], impulse['CMD0'].values[idx]/(impulse['CMD0'].step_pkpk*1e3), label='$h_{CMD}$') # marker='+'
    t = impulse['CC0'].create_time()*1e6 - peak_time
    idx = (t > span_left) & (t < span_right)
    ax[1].plot(t[idx], impulse['CC0'].values[idx]/(impulse['CC0'].step_pkpk*1e3), label='$h_{CC}$', color='tab:orange') #  marker='.', 
    ax[0].legend()
    ax[1].legend()
    ax[0].set_xlabel('time [$\mu$s]')
    ax[1].set_xlabel('time [$\mu$s]')
    ax[0].set_ylabel('$h \; [\mu A/(mV \cdot \mu s)]$') 
    ax[1].set_ylabel('$h \; [\mu A/(mV \cdot \mu s)]$') 
    ax[1].set_xlim([-20, 50]) 
    my_savefig(fig, fig_dir, 'impulse_response')

    # create a step function and convolve impulse and step
    # this is a sanity check to ensure the impulse response is working as anticipated
    t = ds['CMD0']['Im'].create_time()
    t0 = impulse['CMD0'].t0
    t_idx = (t>(t0-1000e-6)) & (t<(t0+1000e-6)) # needs to have a length longer than t_imp so that 'valid' convolution works 
    step_t = t[t_idx]
    step_func = np.zeros(len(step_t))
    step_func[step_t>t0] = 1
    step_t = step_t - t0

    # get time from the input signal 
    # full: N+M-1  - everywhere 
    # same: max(N,M) 
    # valid: max(M,N) - min(M,N) + 1 -- overlap completely  

    # TODO: since the sample rate is 5 MHz need to divide 
    # plot the convolution of the impulse function and a step function 
    fig,ax=plt.subplots(figsize=fig_size)
    print(f'Length of step_t {len(step_t)}; length of impulse {len(impulse["CMD0"].values)}')
    ax.plot(step_t*1e6, np.convolve(impulse['CMD0'].values, step_func, 'same')*200e-9/1e-6, label='CMD') # step_t*1e6, 
    ax.plot(step_t*1e6, np.convolve(impulse['CC0'].values, step_func, 'same')*200e-9/1e-6, label='CC') # step_t*1e6, 
    ax.legend()
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$I_m \; [\mu A]$')
    ax.set_xlim([span_left, span_right])
    fig.suptitle('Impulse * step')
    my_savefig(fig, fig_dir, 'convolution')

    # Guide to using deconvolve
    # https://stackoverflow.com/questions/40615034/understanding-scipy-deconvolve
    # 1) the filter should be shorter than the signal
    # 2) the filter should be such that it's much bigger then zero everywhere

    # https://dsp.stackexchange.com/questions/78319/approximating-inverse-of-unstable-difference-of-gaussians-filter/78325#78325

    im_cmd_conv = np.convolve(impulse['CMD0'].values, step_func) # step function has a sampling rate of 5 MHz (T = 200 ns)
    peak_imp = np.argmax(impulse['CC0'].values)

    # span just the current peak 
    tl_tr = (-10e-6, 1000e-6) # steps are separated by more the 20 ms 
    t0 = pos_pks[0][0]
    t = ds['CMD0']['Im'].create_time()
    tlow = t0 + tl_tr[0]
    thigh = t0 + tl_tr[1]
    im_idx = ((t>=tlow) & (t<=thigh))
    t = (t[im_idx] - t0)*1e6

    im_deconv = ds['CMD0']['Im'].data[im_idx]
    impulse_idx = ((impulse['CMD0'].create_time()>=tlow) & (impulse['CMD0'].create_time()<=thigh))
    impulse_deconv = impulse['CMD0'].values[impulse_idx] 

    # For pytorch want the impulse and data to be centered (i.e. t=0 is in the middle)
    tlow_imp = t0 + impulse['CMD0'].tl
    thigh_imp = t0 + impulse['CMD0'].tr
    t_torch_impulse = ds['CMD0']['Im'].create_time()
    im_idx_imp = ((t_torch_impulse>=tlow_imp) & (t_torch_impulse<=thigh_imp))
    impulse_idx_torch = ((impulse['CMD0'].create_time()>=tlow_imp) & (impulse['CMD0'].create_time()<=thigh_imp))
    impulse_cc_torch = impulse['CC0'].values[impulse_idx_torch]/impulse['CC0'].step_pkpk # units of A/(V*s)
    im_torch = ds['CMD0']['Im'].data[im_idx_imp]/impulse['CMD0'].step_pkpk # A/V

    fig,ax = plt.subplots(figsize=fig_size, nrows=4)
    ax[0].plot(im_deconv*1e6, 'b', label='Meas:Im')
    ax[1].plot(impulse_deconv, 'r', label='h_{CMD}')
    ax[2].plot(im_cmd_conv, 'm', label='h_{CMD}*step')
    fig.suptitle('Sanity check of Im and $h_{CMD}$. Panel 3 shows deconv of CC')

    # Use Im and the CMD impulse function to tune the wiener filter SNR parameter 
    print('Length of signal {} and length of filter/impulse response {}'.format(len(im_deconv), len(impulse_deconv)))
    colors = itertools.cycle(['b', 'g', 'm', 'r'])
    noise_levels = [0.001, 0.002, 0.0035, 0.005, 0.01, 0.02] # in units of uA
    cmd_waves = {}
    for l in noise_levels:
        # the deconvolution is wiener_deconvolution(signal, impulse) --> the output length matches the signal
        cmd_waves[l] = wiener_deconvolution(im_deconv, impulse_deconv, lambd=l*1e-3)
        print(f'In deconvolve. Noise level of {l}; Peak impulse value {np.max(impulse_deconv)}')
        print(f'Sum of cmd_waves l: {l} {np.sum(cmd_waves[l])}')
        ax[3].plot(t, np.real(cmd_waves[l]), next(colors), label='deconv(CMD)@{}'.format(l))
    for i in range(4):
        ax[i].legend()

    fig,ax = plt.subplots(figsize=fig_size)
    colors = itertools.cycle(['b', 'g', 'm', 'r'])
    fig1, ax1=plt.subplots(figsize=fig_size) # plot the cmd_waves
    for l in noise_levels:
        conv = np.convolve(impulse_deconv, cmd_waves[l], 'same') # impulse response, input CMD waveform
        pedestal_conv = np.mean(conv[:-99:-1])
        ax.plot(t, (conv-pedestal_conv), color=next(colors), label='$h_{CMD}$'+':{}'.format(l))
        print(f'Sum of cmd_waves l: {l} {np.sum(cmd_waves[l])}')
        ax1.plot(cmd_waves[l], color=next(colors), label=f'{l}')
    # the step response cannot extract dc offset. So remove on our own. 
    pedestal_im = np.mean(im_deconv[:-99:-1])
    ax.plot(t, (im_deconv - pedestal_im)*1e6, 'k', label='Im') # im_deconv is a subset of the Im measurement 
    ax.legend()
    ax.set_xlabel('time [$\mu$s]')
    ax.set_ylabel('$I_m \; [\mu A]$')
    ax.set_xlim([span_left, span_right])
    fig.suptitle('$h_{CMD} * V_{CMD}$')
    my_savefig(fig, fig_dir, 'CMD_deconv_vs_SNR')

    fig1.suptitle('$V_{CMD} vs. l$')
    ax1.legend()

    # repeat but now generate waveform for cc that should cancel 
    cc_waves = {}
    l = 0.0035*0.0035 # best choice of noise for the Weiner filter 
    impulse_deconv = impulse['CC0'].values[impulse_idx]  # 600 us at 5 MSPS
    cc_waves[l] = wiener_deconvolution(im_deconv, impulse_deconv, lambd=l)  # im_deconv is Im for deconvolution

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
    fs = 1/impulse['CC0'].ts
    
    #for fc in [200e3]:
    fig1,ax1 = plt.subplots(figsize=fig_size, nrows=3)
    for fc in [50e3, 100e3, 200e3, 500e3]:
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html
        order = 3
        b,a = signal.butter(order, [fc], fs=fs, btype='lowpass')    
        # forward and backward filter for zero phase is preferred over a causal filter 
        filtered_cc_wave[fc] = signal.filtfilt(b,a,cc_waves[l], padlen=300)
        # window this signal so that it starts and ends at zero 
        win = signal.windows.hann(len(filtered_cc_wave[fc]))
        peak = np.max(filtered_cc_wave[fc]) - np.min(filtered_cc_wave[fc])
        step2 = -np.ones(len(filtered_cc_wave[fc]))*peak/2
        step2[0:int(len(filtered_cc_wave[fc])/2)] = peak/2
        filtered_cc_wave[fc] = win*filtered_cc_wave[fc] + (1-win)*step2
        
        ax.plot(filtered_cc_wave[fc], label='{} Hz'.format(fc))

        cc_im = np.convolve(impulse_deconv, filtered_cc_wave[fc], mode='valid')
        print('Sum and Average of CC Im: {}, {}'.format(np.sum(cc_im), np.average(cc_im)))
        stop_idx = len(cc_im)
        t = np.linspace(0, impulse['CC0'].ts*(stop_idx-1),  num=stop_idx)*1e6
        # TODO: understand if the 
        ax1[0].plot(t, (cc_im)*1e6, 'tab:blue', label='$h_{CC}*CC_{wave}$')
        ax1[1].plot(t, (im_deconv[:stop_idx])*1e6, label='CMD')
        # TODO: take care of pedestals 
        ax1[2].plot(t, (cc_im + im_deconv[:stop_idx])*1e6, label=f'CMD+CC@{fc} Hz')

    for i in range(3):
        ax1[i].legend()
        ax1[i].set_ylabel('$I_m \; [\mu A]$')
    ax1[2].set_xlabel('time [$\mu$s]')
    ax.legend()
    fig.suptitle('Filtered $V_{CC}(t)$')

    def pad_ends(x, target_len):
        if len(x)>= target_len:
            return x

        half_len = int((target_len - len(x))/2)
        x = np.concatenate((np.ones(half_len)*x[0], x), axis=0)
        x = np.concatenate( (x, np.ones(half_len)*x[-1]), axis=0)
        return x 

    windowed_filtered_cc_wave = pad_ends(windowed_filtered_cc_wave, 10000)
    filtered_cc_wave1 = pad_ends(filtered_cc_wave1, 10000)
    fig,ax = plt.subplots(figsize=fig_size)
    ax.plot(windowed_filtered_cc_wave, label='Windowed')
    ax.plot(filtered_cc_wave1, label='not windowed')

    # compare the Im_CC with a windowed cc_wave and a non-windowed cc_wave (returns to 0)
    cc_im1 = np.convolve(impulse_deconv, windowed_filtered_cc_wave, mode='same')
    cc_im2 = np.convolve(impulse_deconv, filtered_cc_wave1, mode='same')
    fig,ax = plt.subplots(figsize=fig_size)
    ax.plot(cc_im1, label='windowed')
    print(f'Sum of cc_im1 {np.sum(cc_im1)}')
    ax.plot(cc_im2, label='filt_cc_wave')
    print(f'Sum of cc_im2 {np.sum(cc_im2)}')
    fig.suptitle('$I_{mCC} = h_{CC}*V_{CC}$')
    ax.legend()

    # impulse: 
    return impulse, cc_im, im_torch, impulse_cc_torch, configs


if __name__ == '__main__':
    impulse, cc_im, im_torch, impulse_cc_torch, configs = main()

TRAIN = False
if TRAIN:
    # impulse, cc_im, im_torch, impulse_cc_torch = main()
    # remove pedestal from the membrane current 
    im_torch_nopedestal = im_torch - np.mean(im_torch[0:50]) #TODO: generalize 

    from scipy.signal import decimate
    # TODO: need to crop and/or decimate to make training faster 
    decimate_factor = 4
    if decimate_factor > 1:
        target_signal = torch.from_numpy(decimate(im_torch_nopedestal, decimate_factor).copy())
        impulse_train = decimate(impulse_cc_torch, decimate_factor).copy()
    else:
        # use the audiotorch filter 
        target_signal = torch.from_numpy(im_torch)

    step_func = np.zeros(len(target_signal))
    mid_pt = int(len(step_func)/2)
    step_func[int(len(step_func)/2):] = 1
    step_wave = torch.from_numpy(step_func)

    # normalize 
    NORMALIZE = True
    MAX_EPOCHS = 10
    configs = {}
    configs['max_target'] = torch.max(target_signal)
    configs['max_impulse'] = np.max(impulse_train)

    if NORMALIZE:
        target_signal = target_signal/torch.max(target_signal)
        impulse_train = impulse_train/np.max(impulse_train)
    configs['target_signal'] = target_signal
    configs['impulse_train'] = impulse_train
    configs['normalize'] = NORMALIZE
    configs['max_epohcs'] = MAX_EPOCHS

    from analysis.audiotorch_cc import Net 
    net_test = Net().to(device='cpu', dtype=torch.float64)

    fig,ax=plt.subplots()
    ax.plot(step_wave.cpu().detach().numpy(), 'r', label='step')
    ax.plot(target_signal.cpu().detach().numpy(), 'b', label='target')
    ax.plot(impulse_train, 'g', label='impulse')
    out = net_test(step_wave, imp=torch.from_numpy(impulse_train))
    ax.plot(out.cpu().detach().numpy(), 'k', label='first pass')
    ax.legend()

    net, before_training, after_training, train_loss, results, output_dir = train_net(step_wave, 
                                                            target_signal, 
                                                            EPOCHS = MAX_EPOCHS, imp=torch.from_numpy(impulse_train))

    fig,ax = plt.subplots(figsize=fig_size)

    network_time = np.arange(len(before_training.cpu().detach().numpy() - mid_pt))*(200e-9*decimate_factor)
    ax.plot(before_training.cpu().detach().numpy(), 'r', label='before')
    ax.plot(target_signal.cpu().detach().numpy(), 'b', label='target')
    #ax.plot(after_training.cpu().detach().numpy(), 'g', label='trained')
    ax.plot(results['output'][-1].cpu().detach().numpy(), 'g', label='trained')
    ax.legend()

    fig,ax = plt.subplots(figsize=fig_size)
    for e in results['epoch']:
        ax.plot(results['output'][e].cpu().detach().numpy(), label=''.format(e))
    ax.legend()

    configs['decimate_factor'] = decimate_factor
    configs['target'] = target_signal.cpu().detach().numpy()
    configs['before_training'] = before_training.cpu().detach().numpy()
    configs['network'] = 'No extra delay'
    configs['learning_rate'] = 1e-3

    with open(os.path.join(output_dir, 'config.pkl'), 'wb') as handle:
        pickle.dump(configs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # load data and analyze results vs. EPOCHS 
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    epoch_list = np.asarray([0, 2, 4, 40, 80, 160, 399])
    epoch_list = epoch_list[epoch_list<=MAX_EPOCHS]
    plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.viridis(np.linspace(0,1,len(epoch_list))))
    fig,ax = plt.subplots(figsize=fig_size)
    # make Loss vs. epoch a small inset 
    network_time = (np.arange(len(results['output'][0])) - mid_pt)*(200e-9*decimate_factor)

    ax.plot(network_time*1e6, 
        (target_signal.cpu().detach().numpy())*(configs['max_target'].cpu().detach().numpy()*1e6), 'k--', label='Ref.')

    for ep in epoch_list:
        ax.plot(network_time*1e6, 
            (results['output'][ep].cpu().detach().numpy())*(configs['max_target'].cpu().detach().numpy()*1e6), label='{}'.format(ep))
    ax.set_xlim([-20, 400])
    ax.set_ylabel('$I_m \; [\mu A]$')
    ax.set_xlabel('time [$\mu$s]')

    axins2 = inset_axes(ax, width="100%", height="100%", 
                        bbox_to_anchor=(.45, .6, .3, .3),
                        bbox_transform=ax.transAxes)

    axins2.loglog(np.asarray(results['epoch'])+1, results['loss'], marker='.', color='b')
    axins2.set_ylabel('Loss')
    axins2.yaxis.set_tick_params(labelleft=False)
    axins2.set_yticks([], minor=True)
    axins2.set_xlabel('Epoch')

    ax.legend()
    my_savefig(fig, fig_dir, 'cc_cancellation_training_results')


## ---------- NOTES --------------

# These deconvolution methods do not work well because of noise
# cmd_wave, remainder = signal.deconvolve( np.hstack((im_deconv*1e6, np.zeros((1000)))), 
#                                          np.hstack((impulse_deconv,np.zeros((1000)))))

# N = 2**(np.ceil(np.log2(len(im_deconv) + len(impulse_deconv))))
# cmd_wave = ifft(fft(im_deconv*1e6, int(N)) / fft(impulse_deconv, int(N)))
