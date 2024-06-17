"""
June 2024

Lucas Koerner, koerner.lucas@stthomas.edu
Analyze measured transfer functions to determine resistances and capacitances 

A square-wave with a current amplitude is used for static resistance
A sinusoid at varying frequencies is measured to fit to a transfer function and derive an RC circuit 

"""

from math import ceil
import os
import sys
from time import sleep
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
import logging as log

from analysis.calibration_analysis import read_cal_data, two_elec_vs_freq, r_from_square, meas_transfer_func, elec_r_cc, vclamp_tf
from calibration.cal_fits import cc_cap
from datastream.datastream import h5_to_datastreams 

# fit square wave 
from calibration.cal_fits import soft_sq_wave
from scipy.optimize import curve_fit
# for publication figures 
from analysis.utils import my_savefig, fig_size, fig_dir # also configures matplotlib defautls 

PLT = True
capture_date = '20240529' # calibration for voltage clamp gain 
if sys.platform == 'darwin':
    data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/{}/'.format(capture_date)
elif sys.platform == 'win32':
    data_dir = 'C:/Users/koer2434/Documents/covg/data/clamp/{}/'.format(capture_date)

att = 13
filename = f'20240529-155148Re1_100katt_{att}dB.h5'
datastreams = h5_to_datastreams (data_dir, filename)
filename = f'20240529-155148Re1_100katt_{att}dBstepinfo.npz'
data_sq = read_cal_data(data_dir=data_dir, filename=filename)

fig, ax = plt.subplots(figsize=fig_size)
gain = 60
for n in ['V1', 'I', 'V1s']:
    if n == 'V1':
        scale = 10**(-13/20)*gain
    elif n == 'V1s':
        scale = gain
    else:
        scale = 1
    data = datastreams[n].data/datastreams[n].conversion_factor # convert to ADS8686 codes since we are trying to determine various gains!
    t =  datastreams[n].create_time()
    ax.plot(t, data, label=n)
ax.legend()

amplitude = {}
colors = ['tab:blue', 'tab:orange', 'tab:green']
for net, clr in zip(['V1', 'I', 'V1s'], colors):
    freq = 83
    t = datastreams[net].create_time()
    y = datastreams[net].data/datastreams[net].conversion_factor
    sq_wave_amp_guess = np.max(y) - np.min(y)
    # soft square wave:  soft_sq_wave(t, f, a, h, phi, s=1):
    yfit, pcov, infodict, mesg, ier = curve_fit(soft_sq_wave, t, y , 
                                                p0=(freq, sq_wave_amp_guess, 0, 0, 0), full_output=True) # freq, amp, offset, phase, smoothing factor 
    print(f'Amplitude of {net} = {yfit[1]} at frequency of {yfit[0]}')
    amplitude[net] = yfit[1]
    ax.plot(t, soft_sq_wave(t, *yfit), linestyle='--', color=clr)

vsense_gain = amplitude['V1s']/amplitude['I']
vsense_att = amplitude['V1s']/amplitude['V1']

print(f'Vsense gain {vsense_gain}')
print(f'Attenuation {20*np.log10(vsense_att)} dB')

## Now the voltage clamp 
capture_date = '20240606' # TF for voltage 
# Example filename: 'imp_all_steps_chirp_floatdut_20240605-060437_vclamp'
date = '20240605-101911'
# date = '20240606-104506'
date = '20240606-105854'

if sys.platform == 'darwin':
    data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/{}/'.format(capture_date)
elif sys.platform == 'win32':
    data_dir = 'C:/Users/koer2434/Documents/covg/data/clamp/{}/'.format(capture_date)

tf_type = 'vclamp'
file_extra = '_vclamp'
filename = f'imp_all_steps_chirp_floatdut_{date}{file_extra}.npz'

print('--'*40)

data = read_cal_data(data_dir=data_dir, filename=filename)

for k in data:
    try:
        data[k]['v1'] = data[k]['v1']/vsense_gain # calibration is  
    except:
        print(f'{k} gain adjust failed')
        pass

# data is divided into 2 sections need only the second half
ks = list(data.keys())
# with the DUT grounded using the bath clamp 
freqs = np.array([])
y1s = []
y2s = []
ts = [] # the ts should be the same for the reference but duplicate just in case

# with the DUT floating 
freqs_ref = np.array([])
y1s_ref =[]
y2s_ref =[]
ts_ref = [] # the ts_ref should be the same for the reference but duplicate just in case

for k in ks:
    if ( (data[k]['src'] == 'v') and (data[k]['bath_clamp']['P2_CAL_CTRL']==1) and (data[k]['voltage_clamp']['DAC_SEL']=='drive_CAL2') and (data[k]['voltage_clamp']['ADC_SEL']=='CAL_SIG2')):
        print(k)
        freqs = np.append(freqs, data[k]['freq'])
        y1s.append(data[k]['volt'])
        y2s.append(data[k]['v1'])
        ts.append(data[k]['t'])

for k in ks:
    if ( (data[k]['src'] == 'v') and (data[k]['bath_clamp']['P2_CAL_CTRL']==0) and (data[k]['voltage_clamp']['DAC_SEL']=='drive_CAL2') and (data[k]['voltage_clamp']['ADC_SEL']=='CAL_SIG2')):
        print(k)
        freqs_ref = np.append(freqs_ref, data[k]['freq'])
        y1s_ref.append(data[k]['volt'])
        y2s_ref.append(data[k]['v1'])
        ts_ref.append(data[k]['t'])

# amp and dac_amp are output just to check for saturation
freq_m, gain, phase, amp, dac_amp = meas_transfer_func(freqs, ts, data=y2s, dac_wave=y1s)
freq_m_ref, gain_ref, phase_ref, amp_ref, dac_amp_ref = meas_transfer_func(freqs_ref, ts_ref, data=y2s_ref, dac_wave=y1s_ref)
# normalize the DUT grounded gain 
gain = gain/gain_ref

fig,ax = plt.subplots(figsize=fig_size)
ax.loglog(freq_m, gain, marker='o', linestyle='none', label='data')

# two_elec_vs_freq processes the transfer function measurements in a way that is specific to the bath clamp 
# component_fits_vclamp, fit_notes_vclamp, components_vclamp = two_elec_vs_freq(data, tf_type, rtotal=predicted_res, PLT=True, knowns=knowns)

# check the json log file to ensure the knowns match the board configuration -- e.g., that CC is disconnected so that rcc is very large 
# now process this data -- need to generalize the knowns and parameters 

freq_limit_forfit = None
if freq_limit_forfit is not None:
    f_idx = freq_m < freq_limit_forfit
else:
    f_idx = freq_m > 0 # all frequencies

#knowns = {'r3': components['r1'], 'r4': components['r2'], 'cc': cc_cap, 'rcc': components['r3'], 'r5': 200e3}

# try making Rs a fit parameter since it can capture increases due to the MUXs, etc. 
knowns = {'r3': 3.32e3, 'r4': 5e3, 'cc': cc_cap, 'rcc': 1e12, 'rleak': 4.7e6}

component_fits, f, model_eval, meas_data = elec_r_cc(freq_m[f_idx], 
                                        (gain[f_idx], phase[f_idx]),
                                        tf_type = tf_type, knowns=knowns)

ax.loglog(f, model_eval, linestyle='--', label='fit')
ax.set_xlabel('f [Hz]')
ax.set_ylabel('$|H_v|\,[dB]$')

# evaluate the Transfer function with known values for comparison
amp_2 = []
for fi in freq_m:
    a, p = vclamp_tf(fi, cm=33e-9, r5=100e3, **(knowns))
    amp_2.append(a)

cm = component_fits[0].params['cm'].value*1e9
cm_err = component_fits[0].params['cm'].stderr*1e9

ri = component_fits[0].params['r1'].value/1e3
ri_err = component_fits[0].params['r1'].stderr/1e3

# ax.loglog(freq_m, amp_2, marker='.', label='my-eval')
# ax.legend()
ax.text(0.05, 0.4, f'$C_m = {cm:3.1f} \pm {cm_err:3.1f}\: nF$', transform=ax.transAxes)
ax.text(0.05, 0.3, f'$R_I = {ri:3.1f} \pm {ri_err:3.1f}\: k \Omega$', transform=ax.transAxes)
ax.legend()
my_savefig(fig, os.path.join(fig_dir, 'calibration'), 'calibration_vclamp_tf')