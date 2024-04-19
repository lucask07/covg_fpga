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
import os
os.environ['KMP_DUPLICATE_LIB_OK']="TRUE" # this is a workaround for an issue once pytorch was installed 
import sys
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

from torch_cubic_spline_grids import CubicBSplineGrid1d
from analysis.cc_calibration import main as main_cc_cal
from analysis.cc_calibration import main as load_datastreams
from datastream.datastream import h5_to_datastreams

plt.ion()

if sys.platform == 'darwin':
    data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/'
    fig_dir = '/Users/koer2434/My Drive/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/cc'
elif sys.platform == 'win32':
    data_dir = r'C:/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/'
    fig_dir = r'C:/Users/Public/Documents/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/cc/'


def prepare_training(subdir='c:\\Users\\koer2434\\Documents\\covg\\data\\clamp\\20240417\\',
                    cmd_file='cmd_impulse_20240417-163357_rtia10_ccomp47.h5',
                    cc_file='cc_impulse_20240417-163357_rtia10_ccomp47.h5', MAKE_PLTS=False):
    
    # impulse is an Impulse object with .values (units of A/s = uA/us; values does not account for the DAC value used to measure)
    #  and with .step_pkpk (units of V)
    #  Here for training I am using:
    #    impulse_cc_torch = impulse['CC0'].values[impulse_idx_torch]/impulse['CC0'].step_pkpk # units of A/(V*s)
    #    im_torch = ds['CMD0']['Im'].data[im_idx_imp]/impulse['CMD0'].step_pkpk # A/V

    # directory and file names of captured data 
    impulse, cc_im, im_torch, impulse_cc_torch, configs_main = main_cc_cal(subdir=subdir, 
            cmd_file=cmd_file, 
            cc_file=cc_file, 
            MAKE_PLTS=MAKE_PLTS)

    # determine lengths 
    if len(im_torch)%2 == 1:
        im_torch=im_torch[0:-1]
    l1 = len(im_torch)
    l2 = 1200 # beyond this the CC waveform will be forced to 0 or 1. Spans 240 us
    x = torch.linspace(0, 1, l2)
    x = torch.cat((torch.zeros(int((l1-l2)/2)), x, torch.ones(int((l1-l2)/2))), 0).float()

    # normalize the target and the impulse to 1 
    NORMALIZE = True
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
    configs['x'] = x 
    configs['normalize'] = NORMALIZE
    configs['subdir'] = subdir
    configs['cmd_file'] = cmd_file
    configs['cc_file'] = cc_file

    for c in ['cmd_val', 'cc_val', 'cc_conv_factor', 'cmd_conv_factor']:
        configs[c] = configs_main[c] # conversion factor is in V / DAC

    # load the datastreams so that the log information is available
    ds = {}
    ds['CMD0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cmd_file)
    ds['CC0'] = h5_to_datastreams(os.path.join(data_dir, subdir), cc_file)

    # from the datastream have access to ds['CMD0'].dc_configs['0']['ADG_RES']
    configs['adg_r'] = ds['CMD0'].dc_configs['0']['ADG_RES']
    configs['ccomp'] = ds['CMD0'].dc_configs['0']['CCOMP']

    if NORMALIZE:
        target = target/torch.max(target)
        impulse_train = impulse_cc/torch.max(impulse_cc)

    return x, target, impulse_train, configs

def train_net(x, target, impulse_train, configs, EPOCHS = 200):

    configs['N_CONTROL_POINTS'] = 50
    configs['MAX_EPOCHS'] = EPOCHS
    configs['learning_rate'] = 1e-3
    configs['stopping_loss'] = 9.8e-6
    configs['EPOCH_BATCH'] = 100    

    decay = 1 # decay for coloring a plot vs. Epochs 
    results = {}
    results['epoch'] = []
    results['output'] = []
    results['step_wave'] = []
    results['loss'] = []

    # Optimizers specified in the torch.optim package
    loss_fn = torch.nn.MSELoss()
    grid_1d = CubicBSplineGrid1d(resolution=configs['N_CONTROL_POINTS'])
    optimiser = torch.optim.Adam(grid_1d.parameters(), lr=configs['learning_rate'])

    step_wave = grid_1d(x).squeeze()
    before_training = F.convolve(step_wave, impulse_train, mode='same')
    results['before_training'] = before_training
    results['nocancel_loss'] = loss_fn(torch.zeros(len(before_training)), target)
    print('No cancel loss = {}'.format(results['nocancel_loss']))
    results['initial_loss'] = loss_fn(before_training, target)
    print('Initial loss = {}'.format(results['initial_loss']))

    def train_one_epoch(epoch_index, tb_writer, impulse_train=None):
        running_loss = 0.
        last_loss = 0.

        for i in range(configs['EPOCH_BATCH']):
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
                tb_x = epoch_index*configs['EPOCH_BATCH'] + i + 1
                tb_writer.add_scalar('Loss/train', last_loss, tb_x)
                #tb_writer.add_hparams()
                running_loss = 0.
                results['epoch'].append(epoch_number)
                results['output'].append(prediction)
                results['step_wave'].append(step_wave)
                results['loss'].append(last_loss)
    
        return last_loss
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results['timestamp'] = timestamp

    model_filename =  configs['cmd_file'].replace('cmd_impulse_','').replace('.h5','')
    output_dir = os.path.join(configs['subdir'], f'runs/cubic_spline_tuner_{model_filename}')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    writer = SummaryWriter(output_dir)

    fig, ax = plt.subplots()
    fig.suptitle('Training progress')
    training_loss = []
    for epoch_number in range(EPOCHS):
        print('EPOCH (cubic spline) {}:'.format(epoch_number + 1))
        avg_loss = train_one_epoch(epoch_number, writer, impulse_train=impulse_train)
        print('Average loss: {}'.format(avg_loss))
        training_loss.append(avg_loss)
        if avg_loss < configs['stopping_loss']:
            print(f'Breaking at EPOCH = {epoch_number} at loss of {avg_loss}')
            break
        # plot
        if epoch_number % 10 == 0:
            decay *= 0.99
            # ax.scatter(x, grid_1d.data, color='blue', alpha=1 - decay) # cool plotting technique! 
            y = grid_1d(x).squeeze()
            ax.plot(y.detach(), alpha=1-decay, color='blue')

    for name, param in grid_1d.named_parameters():
        if param.requires_grad:
            print('{} = {}'.format(name, param.data))

    step_wave = grid_1d(x).squeeze()
    after_training = F.convolve(step_wave, impulse_train, mode='same')

    # Save the pytorch model and the results and configs 
    torch.save(grid_1d.state_dict(), os.path.join(output_dir, 'model.pt'))
    with open(os.path.join(output_dir, 'results.pkl'), 'wb') as handle:
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(os.path.join(output_dir, 'configs.pkl'), 'wb') as handle:
        pickle.dump(configs, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    writer.close()

    return grid_1d, before_training, after_training, training_loss, results, output_dir


def main(subdir, cmd_file, cc_file, MAKE_PLTS=False, MAX_EPOCHS=40):

    x, target, impulse_train, configs = prepare_training(subdir, cmd_file, cc_file, MAKE_PLTS)

    fig1,ax1 = plt.subplots()
    ax1.plot(target.detach().numpy(), label='Im target')
    fig1.suptitle('Normalized Im current for training')

    # train the network
    grid_1d, before_training, after_training, training_loss, results, output_dir = train_net(x, 
                                                                                    target, 
                                                                                    impulse_train=impulse_train,
                                                                                    configs=configs,
                                                                                    EPOCHS = MAX_EPOCHS)
    ax1.plot((after_training/torch.max(after_training)).detach().numpy(), label='Trained')
    ax1.legend()

    fig,ax=plt.subplots()
    step_wave = grid_1d(x).squeeze()
    prediction = F.convolve(step_wave, impulse_train, mode='same')
    ax.plot(prediction.detach().numpy())
    fig.suptitle('Trained Icc current')

    # normalizing the target value (max-target [A]) decreases the learned CC_wave
    # normalizing the impulse response [A/(V*s)] increases the learned CC_wave  -- need the DAC/mV conversion factor 
    scale_factor = (1/configs['max_impulse']/configs['max_target'])*configs['cmd_val']*configs['cc_conv_factor'] # *(configs['cmd_val']/configs['cc_val'])
    scale_factor = scale_factor.detach().numpy()
    print(f'Scale factor {scale_factor}')

    fig,ax=plt.subplots()
    ax.plot(step_wave.detach().numpy()*scale_factor)
    fig.suptitle('Step wave')

    return before_training, after_training, training_loss, results, output_dir

if __name__ == '__main__':
    #subdir='c:\\Users\\koer2434\\Documents\\covg\\data\\clamp\\20240417\\'
    #cmd_file='cmd_impulse_20240417-163357_rtia10_ccomp47.h5'
    #cc_file='cc_impulse_20240417-163357_rtia10_ccomp47.h5'
    #MAKE_PLTS=False
    main()
