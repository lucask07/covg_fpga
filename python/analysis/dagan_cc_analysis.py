"""
Analysis of COVG data from model cell (h5, datastream-based)
Step response similar to Dagan CA-1B data from Dr. Gil Toombes

Plot:
1) I
2) Q 

Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import scipy.signal as signal 
import scipy.integrate as integrate 
from filters.filter_tools import butter_lowpass_filter
from datastream.datastream import h5_to_datastreams 
from analysis.adc_data import find_peak, calc_psd
from analysis.noise_analysis_tools import plot_psd_integrated_noise, print_experiment_metadata, get_clamp_config, filt_sig


sys.path.append('C:\\Users\\koer2434\\Documents\\covg\\my_pyabf\\pyABF\\src\\')
import pyabf 
from pyabf.tools.covg import interleave_np

# configure Matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()

# setup data directory
data_dir_base = os.path.expanduser('~')
if sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp/{}{:02d}{:02d}"
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/{}{:02d}{:02d}')

fig_dir = "/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/manuscripts/covg_methods/digital_amp_manuscript/figures/figures2/"
dagan_dirs = {}
file_names = {}

dagan_dirs['CC'] = r'C:\Users\koer2434\OneDrive - University of St. Thomas\UST\research\covg\other_clamp_instruments\dagan_ca1b\richmond\Richmond Data\Capacitive Compensation'
# file_names['CC'] = ['0.1 Gain CC.abf']
# gain = 0.1
file_names['CC'] = [ ('1 Gain CC - Attempt 1.abf', 'CC 1'),  ('1 Gain CC - Attempt 2.abf', 'CC 2'), ('1 Gain CC - Attempt 3 (Modest CC).abf', 'CC 3')]
gain = 0.1

dagan_dirs['Rs'] = r'C:\Users\koer2434\OneDrive - University of St. Thomas\UST\research\covg\other_clamp_instruments\dagan_ca1b\richmond\Richmond Data\Series Resistance'
file_names['Rs'] = [('0.1 Gain - Clear Rise.abf', 'Rs Clear'),  ('0.1 Gain - Excessive Rise.abf', 'Rs Exc.'),  ('0.1 Gain - Modest Rise.abf', 'Rs Modest')]

# baseline 
dagan_dirs['Base'] = r'C:\Users\koer2434\OneDrive - University of St. Thomas\UST\research\covg\other_clamp_instruments\dagan_ca1b\richmond\Richmond Data\Steps'
if gain == 0.1:
    file_names['Base'] = [('0.1 Gain 10mV Steps.abf', 'Base')]
else:
    file_names['Base'] = [('1 Gain 10mV Steps.abf', 'Base')]

figd,axd=plt.subplots( 2,1 , figsize=(6,5))

dirs_to_plot = ['CC', 'Base']
dirs_to_plot = ['Rs', 'Base']


for dg_dirs in dirs_to_plot:
    for fname in file_names[dg_dirs]:

        dagan = pyabf.ABF(os.path.join(dagan_dirs[dg_dirs], fname[0]))
        dagan_data = {}
        if gain == 0.1:
            sweep_num = 4
        elif gain == 1:
            sweep_num = 2
        # sweeps 0: 0mV, 1: 10mV, ... ,4: 40 mV
        # membrane current 
        dagan.setSweep(sweepNumber=sweep_num, channel=0)
        dagan_data['time'] = dagan.sweepX
        dagan_data['im'] = dagan.sweepY
        dagan_data['CMD'] = dagan.sweepC # only non-zero for channel 0 

        # membrange voltage 
        dagan.setSweep(sweepNumber=sweep_num, channel=1)
        dagan_data['vm'] = dagan.sweepY
        dagan_data['sample_rate'] = dagan.dataRate
        dagan_data['peak_time'] = 52.83e-3 

        time_range = [-50, 4000] # [us] before and after peak; datastream plotting uses units of us
        t = (dagan_data['time']-dagan_data['peak_time'])*1e6
        idx = (t > time_range[0]) & (t < time_range[1])

        axd[0].plot(t[idx], dagan_data['im'][idx]/60, label=fname[1])
        axd[1].plot(t[idx], dagan_data['vm'][idx])
        # axd[1].plot(t[idx], dagan_data['CMD'][idx])
    
for i in range(2):
    axd[i].set_xlim([time_range[0], time_range[1]])
    axd[i].set_xlabel('$\mu$s')
    if 'CC' in dirs_to_plot:
        axd[i].set_xlim([0, 400])
    else:
        axd[i].set_xlim([0, 800])

axd[0].set_ylabel('$I_m \; [\mu A]$')
axd[1].set_ylabel('$V_m \; [mV]$')

axd[0].legend()
plt.tight_layout()
if 'CC' in dirs_to_plot:
    plt.savefig(os.path.join(fig_dir, f'cc_dagan_{gain}.pdf'))
elif 'RS' in dirs_to_plot:
    plt.savefig(os.path.join(fig_dir, f'rs_dagan_{gain}.pdf'))

# Dagan saturation at 1 mV/nA at a swing of 30 mV 
#   peak current of 12 uA at a step of 20 mV 
#   saturates at 18 uA -- this implies 18 V whereas 12 uA implies 12 V 