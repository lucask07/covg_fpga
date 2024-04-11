"""
Apr 2024 
Lucas Koerner, koerner.lucas@stthomas.edu

Load a trained CC network model and pass a CMD waveform through it to determine CC waveform 

"""
import os
import sys
from time import sleep
import datetime
import time
import os 
import pickle
import numpy as np
import matplotlib.pyplot as plt
import torch

from analysis.audiotorch_cc import Net
from torch_cubic_spline_grids import CubicBSplineGrid1d


def infer_ccwave_spline(run_date = '20240408', 
                 run_time = '193723', 
                 cmd_wave=None, DEBUG_PLOTS = False):

    # load a trained spline model and then create a CC wave

    torch_dir = 'runs/cubic_spline_tuner_{}_{}'.format(run_date, run_time)
    model_name = 'model.pt' 

    net = Net().to(device='cpu', dtype=torch.float64)

    # also load the configuration file 
    with open(os.path.join(torch_dir, 'configs.pkl'), 'rb') as f:
        configs = pickle.load(f)
    with open(os.path.join(torch_dir, 'results.pkl'), 'rb') as f:
        results = pickle.load(f)

    grid_1d = CubicBSplineGrid1d(resolution=configs['N_CONTROL_POINTS'])
    grid_1d.load_state_dict(torch.load(os.path.join(torch_dir, model_name)))

    # now generate the cc_wave 
    if cmd_wave is None:
        cmd_wave = configs['x']

    cc_wave = grid_1d(cmd_wave).squeeze()
    # do not need to evaluate the convolution with the impulse response
    # after_training = F.convolve(step_wave, impulse_train, mode='same')

    if DEBUG_PLOTS:
        fig,ax=plt.subplots()
        ax.plot(cc_wave.cpu().detach().numpy())

    return cc_wave, configs, results

def cat_cc_wave(edge_pts, cc_wave, amplitude=None, midpt=0x0200): 
    """
    at edge pts splice in cc waves 

    Parameters 
    edge pts: np.array (1 if rising edge, -1 is falling edge), total length of cc_wave 
    cc_wave: 
    amplitude: 
    midpt: DAC level -- integer 
    
    Returns: 

    """
    if (amplitude % 2) == 1:
        amplitude = amplitude + 1
    half_amp = int(amplitude/2)

    l = len(edge_pts)
    l_cc = len(cc_wave)
    l_cc_half = int(l_cc/2)

    rising_edge = np.where(edge_pts==1)[0]
    falling_edge = np.where(edge_pts==-1)[0]
    all_edges = np.hstack( (rising_edge, falling_edge))
    all_edges = np.sort(all_edges)

    # if rising edge is first 
    if rising_edge[0] < falling_edge[0]:     
        cc_wave_full = np.ones(l)*midpt - half_amp
    else:
        cc_wave_full = np.ones(l)*midpt + half_amp

    for e in all_edges:
        if edge_pts[e] == 1:
            cc_wave_full[e- l_cc_half : e+l_cc_half] = (cc_wave)*(amplitude) + midpt - half_amp
            cc_wave_full[e+l_cc_half:] = midpt + half_amp
        elif edge_pts[e] == -1:
            cc_wave_full[e- l_cc_half : e+l_cc_half] = -(cc_wave)*(amplitude) + midpt + half_amp
            cc_wave_full[e+l_cc_half:] = midpt - half_amp
    return cc_wave_full


def infer_ccwave_filter(run_date = '20240403', run_time = '161720', 
                 cmd_wave=None, DEBUG_PLOTS = False): 

    torch_dir = 'runs/filter_tuner_{}_{}'.format(run_date, run_time)
    model_name = 'model.pt' 

    net = Net().to(device='cpu', dtype=torch.float64)
    net.load_state_dict(torch.load(os.path.join(torch_dir, model_name)))
    net.eval()

    # load the configuraton pickle file 
    with open(os.path.join(torch_dir, 'config.pkl'), 'rb') as input_file:
        configs = pickle.load(input_file)

    if cmd_wave is None:
        cmd_wave = np.zeros((len(configs['impulse_train'])))
        cmd_wave[int(len(configs['impulse_train'])/2):] = 1

    # want to determine this without convolving with the impulse response
    cc_wave = net(torch.from_numpy(cmd_wave))
    cc_im = net(torch.from_numpy(cmd_wave), imp=torch.from_numpy(configs['impulse_train']))

    if DEBUG_PLOTS:
        fig,ax=plt.subplots()
        ax.plot(cc_wave.cpu().detach().numpy())

        fig,ax=plt.subplots()
        ax.plot(cc_im.cpu().detach().numpy())

    return cc_wave.cpu().detach().numpy(), cc_im.cpu().detach().numpy(), configs 
