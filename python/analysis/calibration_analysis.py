"""

Oct 2022

Lucas Koerner, koerner.lucas@stthomas.edu
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

from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5, separate_ads_sequence
from analysis.utils import calc_fft, phase_by_xcorr
from filters.filter_tools import butter_lowpass_filter, delayseq_interp

from calibration.cal_fits import fit_sine_fft, soft_sq_wave, sine_wave, elec_r_cc, vclamp_tf
from scipy.optimize import curve_fit

PLT = True

file_extra = '_vclamp'
chop_idx = 6
full_scale_current = 0.8e-6 # full-scale current is 0.8 uA 
dac_resolution = 16 # in bits 
freq_limit_forfit = 1.5e3

tf_type = 'vclamp'
# tf_type = 'elec_r_cc'

def read_cal_data(data_dir, file_extra, tf_type):

	if tf_type == 'elec_r_cc':
		data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/20221102/'
		data_dir = 'C/Users/koer2434/Documents/covg/data/clamp/20221102/'
		file_extra = ''
	elif tf_type == 'vclamp':
		data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/20221102/'
		data_dir = 'C/Users/koer2434/Documents/covg/data/clamp/20221102/'
		data_dir = r'C:/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/20221102/'
		file_extra = '_vclamp'


	data = np.load(os.path.join(data_dir, f'imp_all_steps{file_extra}.npy.npz'), allow_pickle=True)
	# 0-d arrays can be indexed using the empty tuple:
	# https://stackoverflow.com/questions/8361561/recover-dict-from-0-d-numpy-array
	data = data['arr_0'][()]

	return data

def r_from_square(r_total_guess, data, PLT=False):
	# analyze square wave signal for the predicted resistance 
	for data_key in data:
		d = data[data_key]
		
		try: # removed the 'dac_wave' and replaced with 'amp' to reduce disk usage 
			amp_dac = np.max(d['dac_wave']) - np.min(d['dac_wave']) 
			dac_wave = True
		except: 
			amp_dac = d['amp']  # in uA
			dac_wave = False

		if d['shape'] == 'SQ':
			t = d['t'][chop_idx:]
			y = d['volt'][chop_idx:] # if I chop at an arbitrary point there will be a phase shift that varies with frequency
			freq = d['freq']
			if dac_wave:
				current_amp = (full_scale_current/2**dac_resolution*amp_dac*2)
				sq_wave_amp_guess = r_total_guess * current_amp
				print(f'Square wave amp guess {sq_wave_amp_guess}')
			else:
				current_amp = (amp_dac*1e-6)
				sq_wave_amp_guess = r_total_guess * current_amp
				print(f'Square wave amp guess {sq_wave_amp_guess}')
		
			yfit, pcov, infodict, mesg, ier = curve_fit(soft_sq_wave, t,y , p0=(freq, 0.016, 0, 0, 0), full_output=True) # freq, amp, offset, phase, smoothing factor 
							#bounds = ([0,0,-15,0,0], [10e6, np.inf, 15, 2*np.pi, np.inf]))  # bounds cause problems. Not sure why
			predicted_res = yfit[1]/current_amp
			print(f'Predicted resistance {predicted_res}')
			if PLT:
				plt.figure(data_key)
				plt.plot(t*1e6,y, marker='.')
				plt.plot(t*1e6, soft_sq_wave(t, *yfit[0]))
				
	return predicted_res, pcov, mesg


def two_elec_vs_freq(data, PLT=False):
	fit_results = {}
	component_fits = {}

	# analyze two different electrode configurations at each frequency 
	# 1 is a reference and calculate 
	ref_e_config = []
	freq_arr_fixed = np.unique([data[data_key]['freq'] for data_key in data])
	chop_idx = 200

	for (drive_elec, meas_adc) in [('drive_CAL1', 'CAL_SIG1'), ('drive_CAL2', 'CAL_SIG2')]:
		fit_results[drive_elec] = {}
		for k in ['freq', 'gain', 'phase', 'e_config']:
			fit_results[drive_elec][k] = np.array([])

		freq_arr = freq_arr_fixed
		for data_key in data:
			d = data[data_key]
			if d['freq'] in freq_arr and d['shape'] == 'SINE' and d['bath_clamp']['ADC_SEL']==meas_adc and d['bath_clamp']['DAC_SEL']==drive_elec: # CAL_SIG1 is the reference 
				freq = d['freq']
				# find the companion 
				key_pair = [data_key_pair for data_key_pair in data if ((data[data_key_pair]['freq'] == freq) and (data[data_key_pair]['bath_clamp']['DAC_SEL'] == drive_elec) and (data_key_pair != data_key))][0]  
				# so we don't process this group again remove the frequency from the array
				freq_arr = freq_arr[freq_arr != freq]
				print(f'Found pair of keys {data_key} and {key_pair} at frequency of {freq} with drive electrode {drive_elec}')
				t = d['t'][chop_idx:]
				y = d['volt'][chop_idx:] # if chopped at an arbitrary point there will be a phase shift that varies with frequency if compared to an ideal sine
				y_pair = data[key_pair]['volt'][chop_idx:]

				log.info(f'---- Freq = {freq}')
		#            for method in ['quad_interpolate', 'single_bin']:
				for method in ['quad_interpolate']:
					max_freq, amp, phase = fit_sine_fft(t, y, method=method)
					xcorr_phase, sample_lag, n_period_float, amp_ratio = phase_by_xcorr(freq, t, y, 
														dac_wave=y_pair, debug_plots=False)
					log.info(f'Amp. of sine from fft: {amp:.2f}. Phase: {np.degrees(phase):.2f}, {np.degrees(xcorr_phase):.2f}  at freq of {max_freq} [Hz] vclamp of {d["vclamp"]}') 
					log.info(f'Sample lag of {sample_lag}. With {n_period_float} samples in a period')

				fit_results[drive_elec]['freq'] = np.append(fit_results[drive_elec]['freq'], max_freq)
				fit_results[drive_elec]['gain'] = np.append(fit_results[drive_elec]['gain'], amp_ratio)
				fit_results[drive_elec]['phase'] = np.append(fit_results[drive_elec]['phase'], xcorr_phase)

		if PLT:
			fig, ax = plt.subplots(2,1)
			if drive_elec == 'drive_CAL1':
				clr = 'b'
			elif drive_elec == 'drive_CAL2':
				clr = 'r'
			ax[0].semilogx(fit_results[drive_elec]['freq'], 20*np.log10(fit_results[drive_elec]['gain']), 
				marker='*', color=clr)
			ph = -np.degrees(fit_results[drive_elec]['phase'])
			ax[1].semilogx(fit_results[drive_elec]['freq'], ph, 
				marker='*', color=clr)

		f_idx = fit_results[drive_elec]['freq'] < freq_limit_forfit
		component_fits[drive_elec] = elec_r_cc(fit_results[drive_elec]['freq'][f_idx], 
											   (fit_results[drive_elec]['gain'][f_idx], fit_results[drive_elec]['phase'][f_idx]),
											  tf_type = tf_type)

	print('-'*60)
	print('constrained by total resistance')
	f_fit_short = fit_results['drive_CAL1']['freq'][f_idx]
	f_fit = np.hstack((fit_results['drive_CAL1']['freq'][f_idx], fit_results['drive_CAL2']['freq'][f_idx]))
	g_fit = np.hstack((fit_results['drive_CAL1']['gain'][f_idx], fit_results['drive_CAL2']['gain'][f_idx]))
	p_fit = np.hstack((fit_results['drive_CAL1']['phase'][f_idx], fit_results['drive_CAL2']['phase'][f_idx]))

	TEST_TF = False # to test if the fits match the transfer functions override the experimental data 
	if TEST_TF:
		a1,p1 = vclamp_tf(f_fit_short, r5=200e3, cm=33e-9)
		a2,p2 = vclamp_tf(f_fit_short, r5=300e3-200e3, cm=33e-9)

		g_fit = np.hstack((a1,a2))
		p_fit = np.hstack((p1,p2))

	component_fits[drive_elec] = elec_r_cc(f_fit_short, (g_fit, p_fit), 
										   tf_type = ['vclamp', 'vclamp_bound'])

	# TODO: use frequency data to estimate Rs individual

	idx = 0 # this is the fit to just magnitude 
	# idx = 1 # fit to magnitude and phase 

	components = {}
	if tf_type == 'elec_r_cc':
		components['r1'] = component_fits['drive_CAL1'][idx].params['r1'].value
		components['r2'] = component_fits['drive_CAL2'][idx].params['r1'].value
		components['r3'] = np.average([component_fits['drive_CAL1'][idx].params['r3'].value, 
						component_fits['drive_CAL2'][idx].params['r3'].value])
		components['cm'] = np.average([component_fits['drive_CAL1'][idx].params['cm'].value, component_fits['drive_CAL2'][idx].params['cm'].value])

	if tf_type == 'vclamp':
		components['r1'] = component_fits['drive_CAL1'][idx].params['r1'].value
		components['r2'] = component_fits['drive_CAL2'][idx].params['r1'].value
		components['cm'] = np.average([component_fits['drive_CAL1'][idx].params['cm'].value, component_fits['drive_CAL2'][idx].params['cm'].value])

	fit_notes = {'success': component_fits['drive_CAL1'][idx].success,
			  'chisqr': component_fits['drive_CAL1'][idx].chisqr,
			  'message': component_fits['drive_CAL1'][idx].message}


	return component_fits, fit_notes, components

if file_extra == '_vclamp':
    r_total_guess = 300e3
else:
    r_total_guess = 5e3 + 3.32e3
	
data = read_cal_data(data_dir=None, file_extra=None, tf_type=tf_type)
predicted_res, pcov, fit_mesg = r_from_square(r_total_guess, data)
component_fits, fit_notes, components = two_elec_vs_freq(data, PLT=False)