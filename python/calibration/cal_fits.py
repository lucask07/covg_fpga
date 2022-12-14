"""Fitting functions and calculations to extract impedance from 
square wave and sine-wave stimulus 

Oct 2022

Lucas Koerner, koer2434@stthomas.edu
"""
import functools
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from analysis.utils import calc_fft, fft_maxs
from lmfit import minimize, Parameters, report_fit
import pdb
# Useful lmfit example 
# https://stackoverflow.com/questions/20339234/python-and-lmfit-how-to-fit-multiple-datasets-with-shared-parameters?noredirect=1&lq=1

plt.ion()

def soft_sq_wave(t, f, a, h, phi, s=1):
    # a square-wave that does not have infinitely fast edges. 
    return h + a * np.tanh( s * np.cos( 2 * np.pi *f * t + phi ) )

def sine_wave(t, f, a, h, phi ):
    return h + a * np.sin( 2 * np.pi *f * t + phi )

def sine_wave_nodc(t, f, a, phi ):
    return a * np.sin( 2 * np.pi *f * t + phi )


def exponential_rise(t, a, k, c):
    return a * (np.exp(k * t)) + c


def fit_sine(t,y,freq,freq_eps=1e-3):
    # linear least squares fit to a sinusoid often has problems
    # better to use an FFT to extract amplitude and phase

    y = y - np.mean(y)
    a_guess = np.sqrt(2)*np.std(y)
    yfit = curve_fit(sine_wave_nodc, t, y, 
                    p0=(freq, a_guess, 0),
                    bounds=((freq*(1-freq_eps), a_guess*(0.8), -np.pi),
                            (freq*(1+freq_eps), a_guess*1.2, np.pi)) )
    return yfit 

def fit_sine_fft(t, y, method='quad_interpolate'):

    dc_level = np.mean(y)
    freq, max_freq, amp, phase = fft_maxs(y - dc_level, 1/(t[1]-t[0]), 
    									  method=method, plot=False, window='hann')

    return max_freq, amp, phase 


def tf(name): 
    # create a transfer function from calc_tf that only uses 
    #   a subset of the parameters. 
    #   functools.partial generates a new function that has constant parameters
    #   no longer as inputs 
    if name=='no_dut':
        # ignore c1, just use c2 
        return functools.partial(calc_tf,rs=np.inf,c2=1e-15,r5=np.inf,r6=np.inf) 
    if name=='vclamp_cm':
    	pass

def vclamp_tf(f,r5,cm):

    #  this is for voltage clamp calibration measurements
    r3 = 3.32e3
    r4 = 5e3 

    cc = 4.7e-9 # 4.7e-9
    rcc = 6.8e3  # 6.8e3
    rbot = par(r3,r4)

    rs = 1e3

    w = f*2*np.pi
    cc_rc = -1j*(1/(w*cc)) + rcc
    num = -1j*(1/(w*cm)) + rs + par(rbot, cc_rc)
    a = num/(num + r5)

    return np.abs(a), np.angle(a)

def lpf_tf(f,r5,cm):

    #  verify transfer function calculation match LTSpice
    w = f*2*np.pi
    num = -1j*(1/(w*cm))
    a = num/(num + r5)

    return np.abs(a), np.angle(a)


def calc_tf(f,r1,r2,r3,c1,rs,c2,r5,r6):
    #  variables match reference designators in schematic LTSpice bath_electrodes.asc 
    #  TODO: expand transfer to include rs, c2. 
    #   
    #  Will need a Rbot for the bottom plate resistance
    w = f*2*np.pi
    num = r3 - 1j*(1/(w*c1)) 
    a = num/(num + r1)

    return np.abs(a), np.angle(a)

def elec_r_cc(f, tf_amp_phase, tf_type='elec_r_cc', rtotal=None):
	
	def tf_eval(params, f, tf_type):
		if tf_type == 'elec_r_cc':
			tf_nodut = tf('no_dut')
			c1 = 4.7e-9 # on the daughter-card 
			tf_test = functools.partial(tf_nodut, c1=c1)
		elif (tf_type == 'vclamp') or (tf_type == 'vclamp_bound'):
			tf_test = vclamp_tf

		if tf_type == 'elec_r_cc':
			r1 = params['r1'].value
			r2 = params['r2'].value
			r3 = params['r3'].value

			return tf_test(f,r1,r2,r3)

		elif tf_type == 'vclamp':
			r1 = params['r1'].value
			cm = params['cm'].value

			return tf_test(f,r1,cm)

		elif tf_type == 'vclamp_bound': # since we measure rtotal using a current source: solve for r2 as rtotal-r1 			
			r1 = params['r1'].value
			cm = params['cm'].value
			rtotal = params['rtotal'].value 
			if rtotal is None:
				log.error('rtotal is None. For voltage clamp bound fit need an rtotal input.')
				raise ValueError('rtotal cannot be None in vclamp_bnd')

			return tf_test(f, rtotal - r1, cm)


	def residuals(params, f_arr, data, tf_type):
		# calculate the difference between the data (gain, phase) and the 
		#  evaluated impedance
		ap_tot = np.array([])
		for tft in tf_type:
			amp,phase = tf_eval(params, f_arr, tft)
			ap = np.vstack([amp, phase])
			ap_tot = np.append(ap_tot, ap)

		diff = ap_tot.ravel() - data.ravel() # TODO: is this aligning mangitude and phase correctly?
		# The only change required is to use view instead of abs.
		# so that gain and phase both contribute to the fit
		return diff.flatten()

	def residuals_magnitude(params, f_arr, data, tf_type):
		# calculate the difference between the data (magnitude) and the 
		#  evaluated impedance

		ap_tot = np.array([])
		for tft in tf_type:
			amp, phase = tf_eval(params, f_arr, tft)
			ap_tot = np.append(ap_tot, amp)
			#pdb.set_trace()

		diff = np.abs(ap_tot) - data

		return diff.flatten()

	if type(tf_type) is not list:
		tf_type = [tf_type]
	
	if tf_type[0] == 'elec_r_cc':
		fit_params = Parameters()
		fit_params.add('r1', value=5e3, min=100, max=15e3)
		fit_params.add('r2', value=5e3, min=100, max=15e3)
		fit_params.add('r3', value=5e3, min=100, max=15e3)

	elif tf_type[0] == 'vclamp':
		fit_params = Parameters()
		fit_params.add('r1', value=100e3, min=50e3, max=1e6)
		fit_params.add('cm', value=33e-9, min=20e-9, max=60e-9)
		fit_params.add('rtotal', value=rtotal, vary=False)

	# run the global fit to all the data sets
	result = minimize(residuals_magnitude, fit_params, args=(f, tf_amp_phase[0], tf_type))
	report_fit(result)

	data_split = np.split(tf_amp_phase[0], len(tf_type))
	fig, ax = plt.subplots()
	for tft_idx, tft in enumerate(tf_type):
		model_eval = tf_eval(result.params, f, tft)
		ax.semilogx(f, 20*np.log10(np.abs(model_eval[0])), label='model_eval')
		ax.semilogx(f, 20*np.log10(data_split[tft_idx]), label='data', marker='*', linestyle='none')

	ax.set_xlabel('f [Hz]')
	fig.legend()

	# also try with amplitude and phase, don't expect to work as well
	amp = tf_amp_phase[0]
	phase = tf_amp_phase[1]

	result2 = minimize(residuals, fit_params, args=(f, np.vstack([amp,phase]), tf_type))
	# report_fit(result2)

	return result, result2 # result ignores phase, result 2 considers phase

# use known rtotal: 1 TF is r1; the other is rtotal-r1 

def par(z1,z2):
    # parallel combination of two impedances
    return 1/(1/z1 + 1/z2)

if __name__ == '__main__':

	# various tests of calibration fits 
	t = np.linspace(0, 10e-3, 1000000)
	phi = 0.8
	h = 2.2 
	a = 1
	f = 1e3
	y = h + a*np.cos(2*np.pi*f*t+phi)

	plt.plot(t,y)

	# yfit = fit_sine(y,y,freq=f)
	# plt.plot(t, sine_wave_nodc(t, *yfit[0]) + h)

	plt.plot(t, sine_wave(t,f, amp, dc_level, phase))

	plt.figure()
	calc_fft(y, 1/(t[1]-t[0]), plot=True, WINDOW='hann')

	tf_nodut = tf('no_dut')
	f_arr = np.logspace(3,5,40)
	tf_nodut_v = np.vectorize(tf_nodut)
	a,p=tf_nodut_v(f_arr,3.3e3,5e3,6.8e3,4.7e-9)

	fig,ax=plt.subplots()
	ax.semilogx(f_arr, 20*np.log10(a))
	ax.semilogx(f_arr, np.degrees(p))

	# to curve fit: gain, phase at f1, gain,phase at f2, gain,phase at f3. 
	#  Solve for r1, r4, cc
	#  however cc is a known-constant (bound?)

	def ap_eval(params, f_arr):
		r1 = params['r1'].value
		r2 = params['r2'].value
		r3 = params['r3'].value
		cc = 4.7e-9

		a,p=tf_nodut_v(f_arr,r1,r2,r3,cc)
		return a,p

	def residuals(params, f_arr, data):
		# calculate the difference between the data (gain, phase) and the 
		#  evaluated impedance
		a,p = ap_eval(params, f_arr)
		ap = np.vstack([a,p])

		diff = ap - data
		# The only change required is to use view instead of abs.
		# so that gain and phase both contribute to the fit
		return diff.flatten()

	fit_params = Parameters()
	fit_params.add('r1', value=5e3, min=100, max=15e3)
	fit_params.add('r2', value=5e3, min=100, max=15e3)
	fit_params.add('r3', value=5e3, min=100, max=15e3)

	data = np.vstack([a,p])

	# run the global fit to all the data sets
	result = minimize(residuals, fit_params, args=(f_arr, data))
	report_fit(result)

	af,pf = ap_eval(result.params, f_arr)
	ax.semilogx(f_arr, 20*np.log10(af),linestyle='--')
	ax.semilogx(f_arr, np.degrees(pf),linestyle='--')
