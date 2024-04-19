'''
Use gradient descent to optimize cubic spline waveform for the CC compensation for the COVG project

Lucas Koerner 
2024/4/6

requires the nightly build of torchaudio:
pip install --pre torchaudio -f https://download.pytorch.org/whl/nightly/torch_nightly.html 
which can be installed with:
pip install git+https://github.com/alisterburt/torch-cubic-spline-grids

TODO: 
1) determine how to force amplitude of wave 
2) configure width of changing edge 
3) translate control points and width to the max "frequency" of the waveform

Notes: 
1) the learned waveform will be at the same frequency as the Im measurement (5 MSPS) and 
   then will need to be downsampled 

'''
import torch
import torchaudio.functional as F
import matplotlib.pyplot as plt
from torchsummary import summary
# PyTorch TensorBoard support
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
import numpy as np
import copy
import pickle
import os

from torch_cubic_spline_grids import CubicBSplineGrid1d
from analysis.cc_calibration import main as main_cc_cal

plt.ion()

SAMPLE_RATE = 5e6 # 1 ms is 16 samples 
N_CONTROL_POINTS = 50 # sets the resolution of the cubic splines 
# some plotting stuff
fig, ax = plt.subplots()
fig1,ax1 = plt.subplots()

impulse, cc_im, im_torch, impulse_cc_torch = main_cc_cal()

# determine lengths 
if len(im_torch)%2 == 1:
    im_torch=im_torch[0:-1]
l1 = len(im_torch)
l2 = 1200 # beyond this the CC waveform will be forced to 0 or 1. Spans 240 us
x = torch.linspace(0, 1, l2)
x = torch.cat((torch.zeros(int((l1-l2)/2)), x, torch.ones(int((l1-l2)/2))), 0).float()

# normalize the target and the impulse to 1 
NORMALIZE = True
MAX_EPOCHS = 80
configs = {}

# remove Im current pedestal 
im_torch = im_torch - np.mean(im_torch[0:200])
target = torch.from_numpy(im_torch.astype(np.float32))
impulse_cc = torch.from_numpy(impulse_cc_torch.astype(np.float32))
configs['max_target'] = torch.max(target)
configs['max_impulse'] = torch.max(impulse_cc)
configs['target'] = target
configs['impulse_cc'] = impulse_cc
configs['l2'] = l2
configs['l1'] = l1
configs['N_CONTROL_POINTS'] = N_CONTROL_POINTS
configs['MAX_EPOCHS'] = MAX_EPOCHS
configs['x'] = x 

if NORMALIZE:
    target = target/torch.max(target)
    impulse_train = impulse_cc/torch.max(impulse_cc)

ax1.plot(im_torch/np.max(im_torch))

def train_net(x, target, imp, EPOCHS = 200):

    decay = 1 # decay for coloring a plot vs. Epochs 
    results = {}
    results['epoch'] = []
    results['output'] = []
    results['step_wave'] = []
    results['loss'] = []

    # Optimizers specified in the torch.optim package
    loss_fn = torch.nn.MSELoss()
    grid_1d = CubicBSplineGrid1d(resolution=N_CONTROL_POINTS)
    optimiser = torch.optim.Adam(grid_1d.parameters(), lr=1e-3)

    step_wave = grid_1d(x).squeeze()
    before_training = F.convolve(step_wave, impulse_train, mode='same')
    results['before_training'] = before_training
    results['initial_loss'] = loss_fn(before_training, target)
    print('Initial loss = {}'.format(results['initial_loss']))

    def train_one_epoch(epoch_index, tb_writer, imp=None):
        running_loss = 0.
        last_loss = 0.

        EPOCH_BATCH = 100    

        for i in range(EPOCH_BATCH):
            # zero gradients and calculate loss between observations and model prediction
            optimiser.zero_grad()
            step_wave = grid_1d(x).squeeze()
            prediction = F.convolve(step_wave, impulse_train, mode='same')
            loss = loss_fn(prediction, target)

            # backpropagate loss and update values at points on grid
            loss.backward(retain_graph=True)
            optimiser.step()

            # Gather data and report
            running_loss += loss.item()
            if i % 100 == 99:
                last_loss = running_loss / 1000 # loss per batch
                print('  batch {} loss: {}'.format(i + 1, last_loss))
                tb_x = epoch_index*EPOCH_BATCH + i + 1
                tb_writer.add_scalar('Loss/train', last_loss, tb_x)
                #tb_writer.add_hparams()
                running_loss = 0.
                results['epoch'].append(epoch_number)
                results['output'].append(prediction)
                results['step_wave'].append(step_wave)
                results['loss'].append(last_loss)
    
        return last_loss
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = 'runs/cubic_spline_tuner_{}'.format(timestamp)
    writer = SummaryWriter(output_dir)

    training_loss = []
    for epoch_number in range(EPOCHS):
        print('EPOCH {}:'.format(epoch_number + 1))
        avg_loss = train_one_epoch(epoch_number, writer, imp=imp)
        print('Average loss: {}'.format(avg_loss))
        training_loss.append(avg_loss)
        if avg_loss < 1e-5:
            break
        # plot
        if epoch_number % 10 == 0:
            decay *= 0.99
            # ax.scatter(x, grid_1d.data, color='blue', alpha=1 - decay) # cool plotting technique! 
            y = grid_1d(x).squeeze()
            ax.plot(y.detach(), alpha=1 - decay, color='blue')

    for name, param in grid_1d.named_parameters():
        if param.requires_grad:
            print('{} = {}'.format(name, param.data))

    step_wave = grid_1d(x).squeeze()
    after_training = F.convolve(step_wave, impulse_train, mode='same')

    torch.save(grid_1d.state_dict(), os.path.join(output_dir, 'model.pt'))
    with open(os.path.join(output_dir, 'results.pkl'), 'wb') as handle:
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(os.path.join(output_dir, 'configs.pkl'), 'wb') as handle:
        pickle.dump(configs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return grid_1d, before_training, after_training, training_loss, results, output_dir


if __name__ == '__main__':

    # train the network
    grid_1d, before_training, after_training, training_loss, results, output_dir = train_net(x, 
                                                                                    target, EPOCHS = MAX_EPOCHS, 
                                                                                    imp=impulse_train)
    ax1.plot((after_training/torch.max(after_training)).detach().numpy())

    fig,ax=plt.subplots()
    step_wave = grid_1d(x).squeeze()
    prediction = F.convolve(step_wave, impulse_train, mode='same')
    ax.plot(prediction.detach().numpy())

    fig,ax=plt.subplots()
    ax.plot(step_wave.detach().numpy())
    fig.suptitle('Step wave')