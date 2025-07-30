'''
Use gradient descent to optimize biquad filters for tuning of CC filters for the COVG project
Use biquads as these filters can be directly implemented onto an FPGA 

Lucas Koerner 
2024/2/27 

requires the nightly build of torchaudio:
pip install --pre torchaudio -f https://download.pytorch.org/whl/nightly/torch_nightly.html 

General biquad filters are described here:
https://pytorch.org/audio/main/generated/torchaudio.functional.biquad.html

Low-pass filter biquad 
https://pytorch.org/audio/main/generated/torchaudio.functional.lowpass_biquad.html?highlight=lowpass_biquad#torchaudio.functional.lowpass_biquad

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

plt.ion()

# training example 
# https://pytorch.org/tutorials/beginner/introyt/trainingyt.html

# TODO: create a more general filter structure that:
# 3) cascades filters for multi-order (and/or adjusts Q) 
# 4) adds phase shift or delay -- indexing isn't differentiable so instead use all_pass (iir) or lfilter 

SAMPLE_RATE = 5e6 # 1 ms is 16 samples 

class FilterParams(torch.nn.Module):
    # this doesn't work since the parameters are not part of the NN and are not optimized
    def __init__(
        self,
        fc,
        Q,
        gain
    ):
        super().__init__()
        self.fc = fc
        self.Q = Q 
        self.gain = gain 

    def print_params(self):
        print(self.__dict__)


class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.sample_rate = SAMPLE_RATE 

        self.filts = []

        self.fc0 = torch.nn.Parameter(torch.tensor((50000.0), requires_grad=True)) # cutoff frequency 
        self.gain0 = torch.nn.Parameter(torch.tensor((1.0), requires_grad=True)) # amplitude 
        self.Q0 = torch.nn.Parameter(torch.tensor((0.707), requires_grad=True)) # Q 

        self.fc1 = torch.nn.Parameter(torch.tensor((100000.0), requires_grad=True)) # cutoff frequency 
        self.gain1 = torch.nn.Parameter(torch.tensor((1.0), requires_grad=True)) # amplitude 
        self.Q1 = torch.nn.Parameter(torch.tensor((0.707), requires_grad=True)) # Q 

        # allpass 
        self.fc2 = torch.nn.Parameter(torch.tensor((100000.0), requires_grad=True)) # cutoff frequency 
        self.gain2 = torch.nn.Parameter(torch.tensor((1.0), requires_grad=True)) # amplitude 
        self.Q2 = torch.nn.Parameter(torch.tensor((0.707), requires_grad=True)) # Q 

        self.fc3 = torch.nn.Parameter(torch.tensor((100000.0), requires_grad=True)) # cutoff frequency 
        self.gain3 = torch.nn.Parameter(torch.tensor((0.10), requires_grad=True)) # amplitude 
        self.Q3 = torch.nn.Parameter(torch.tensor((0.707), requires_grad=True)) # Q 

        # allpass 
        # self.fc4 = torch.nn.Parameter(torch.tensor((6000.0), requires_grad=True)) # cutoff frequency 
        # self.gain4 = torch.nn.Parameter(torch.tensor((0.1), requires_grad=True)) # amplitude 
        # self.Q4 = torch.nn.Parameter(torch.tensor((0.707), requires_grad=True)) # Q 

        # # lowpass after second all pass  
        # self.fc5 = torch.nn.Parameter(torch.tensor((50000.0), requires_grad=True)) # cutoff frequency 
        # self.gain5 = torch.nn.Parameter(torch.tensor((-1.0), requires_grad=True)) # amplitude 
        # self.Q5 = torch.nn.Parameter(torch.tensor((0.707), requires_grad=True)) # Q 

    def forward(self, x, imp=None):
        sig1 = F.lowpass_biquad(x, sample_rate=self.sample_rate, 
                                cutoff_freq=self.fc0, Q=self.Q0)*self.gain0
        
        sig3 = F.lowpass_biquad(x, sample_rate=self.sample_rate,   
                                cutoff_freq=self.fc3, Q=self.Q3)*self.gain3

        sig2 = F.highpass_biquad(x, sample_rate=self.sample_rate,   
                                cutoff_freq=self.fc1, Q=self.Q1)*self.gain1

        # this addition caused problems with NaNs after about 15 Epochs 
        # sig4 = F.allpass_biquad(x, sample_rate=self.sample_rate,   
        #                         central_freq=self.fc4, Q=self.Q4)*self.gain4
        # sig5 = F.lowpass_biquad(sig4, sample_rate=self.sample_rate,   
        #                         cutoff_freq=self.fc5, Q=self.Q5)*self.gain5

        sig = F.allpass_biquad(sig1 + sig2 + sig3, sample_rate=self.sample_rate, 
                                central_freq=self.fc2, Q=self.Q2)*self.gain2
        # sig = sig + sig5
        sig = sig


        # TODO: convolve with an impulse response here 
        if imp is not None:
            sig = F.convolve(sig, imp, mode='same')

        return sig 



def train_net(step_wave, target_wave, EPOCHS = 200, imp=None):

    results = {}
    results['epoch'] = []
    results['output'] = []
    results['loss'] = []

    # Optimizers specified in the torch.optim package
    loss_fn = torch.nn.MSELoss()
    net = Net().to(device='cpu', dtype=torch.float64)
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-3)
    before_training = net(step_wave, imp=imp)
    results['before_training'] = before_training
    sig_len = len(before_training)
    results['initial_loss'] = loss_fn(before_training, target_wave[0:sig_len])
    print('Initial loss = {}'.format(results['initial_loss']))

    def train_one_epoch(epoch_index, tb_writer, imp=None):
        running_loss = 0.
        last_loss = 0.

        # Here, we use enumerate(training_loader) instead of
        # iter(training_loader) so that we can track the batch
        # index and do some intra-epoch reporting
        EPOCH_BATCH = 1000    

        # Zero your gradients for every batch!

        for i in range(EPOCH_BATCH):
            optimizer.zero_grad()
            # Make predictions for this batch
            outputs = net(step_wave, imp=imp)
            sig_len = len(outputs)

            # Compute the loss and its gradients
            loss = loss_fn(outputs, target_wave[0:sig_len])
            loss.backward(retain_graph=True) 
            torch.nn.utils.clip_grad_norm_(net.parameters(), 2)
            # Adjust learning weights
            optimizer.step()

            # Gather data and report
            running_loss += loss.item()
            if i % 1000 == 999:
                last_loss = running_loss / 1000 # loss per batch
                print('  batch {} loss: {}'.format(i + 1, last_loss))
                tb_x = epoch_index*EPOCH_BATCH + i + 1
                tb_writer.add_scalar('Loss/train', last_loss, tb_x)
                #tb_writer.add_hparams()
                running_loss = 0.
                results['epoch'].append(epoch_number)
                results['output'].append(outputs)
                results['loss'].append(last_loss)
    
        return last_loss

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = 'runs/filter_tuner_{}'.format(timestamp)
    writer = SummaryWriter(output_dir)

    training_loss = []
    for epoch_number in range(EPOCHS):
        print('EPOCH {}:'.format(epoch_number + 1))
        net.train(True)
        avg_loss = train_one_epoch(epoch_number, writer, imp=imp)
        print('Average loss: {}'.format(avg_loss))
        training_loss.append(avg_loss)
        if avg_loss < 1e-5:
            break

    for name, param in net.named_parameters():
        if param.requires_grad:
            print('{} = {}'.format(name, param.data))

    after_training = net(step_wave, imp=imp)

    torch.save(net.state_dict(), os.path.join(output_dir, 'model.pt'))
    with open(os.path.join(output_dir, 'results.pkl'), 'wb') as handle:
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return net, before_training, after_training, training_loss, results, output_dir

if __name__ == '__main__':

    SIG_LEN = 100
    STEP_IDX = 20
    step_wave = torch.ones(SIG_LEN, dtype=torch.float64, device='cpu', requires_grad=True)
    step_wave_ref = copy.deepcopy(step_wave)
    with torch.no_grad():
        step_wave_ref[0:STEP_IDX + 12] = 0  # this delay is not entirely reproducible by linear biquad filters 
        step_wave[0:STEP_IDX] = 0

    target_fc = 700
    target_q = 0.707
    target_gain = 0.8

    filt_step_ideal = F.lowpass_biquad(step_wave_ref, sample_rate=16000, 
                                    cutoff_freq=target_fc, Q=target_q)*target_gain
    target_fc = 500
    target_q = 0.707 
    target_gain = 0.2

    x2 = F.highpass_biquad(step_wave_ref, sample_rate=16000, 
                                    cutoff_freq=target_fc, Q=target_q)*target_gain
    filt_step_ideal = filt_step_ideal + x2 

    plt.plot(filt_step_ideal.cpu().detach().numpy(), 'g', marker='o', label='target')

    net, before_training, after_training,training_loss, results, _ = train_net(step_wave, filt_step_ideal, EPOCHS = 20, imp=None)
    plt.plot(before_training.cpu().detach().numpy(), 'm', marker='o', label='before training')
    plt.show()
    plt.plot(after_training.cpu().detach().numpy(), 'b', marker='x', label='after training')
    plt.legend()