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

def infer_ccwave(run_date = '20240403', run_time = '161720', 
                 cmd_wave=None, DEBUG_PLOTS = False): 

    # TODO: may need the capability to input an alternative CC impulse response 
    # TODO: allow for unexpected lengths of the cmd_wave waveform 

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
