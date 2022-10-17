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

def fit_sine_fft(t, y):

    dc_level = np.mean(y)
    freq, max_freq, amp, phase = fft_maxs(y - dc_level, 1/(t[1]-t[0]), plot=False, window='hann')

    return max_freq, amp, phase 


def tf(name): 
    # create a transfer function from calc_tf that only uses 
    #   a subset of the parameters. 
    #   functools.partial generates a new function that has constant parameters
    #   no longer as inputs 
    if name=='nodut':
        # ignore c1, just use c2 
        return functools.partial(calc_tf,rs=np.inf,c1=1e-15) 


def calc_tf(f,r1,r2,r3,c2,rs,c1):
    # TODO: expand the include rs, c1. 
    #  Will need a Rbot for the bottom plate resistance
    w = f*2*np.pi
    num = r3 - 1j*(1/(w*c2)) 
    a = num/(num + r1)

    return np.abs(a), np.angle(a)

def par(z1,z2):
    # parallel combination of two impedances
    return 1/(1/z1+1/z2)


if __name__ == '__main__':
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

	tf_nodut = tf('nodut')
	f_arr = np.logspace(3,5,40)
	tf_nodut_v = np.vectorize(tf_nodut)
	a,p=tf_nodut_v(f_arr,3.3e3,5e3,6.8e3,4.7e-9)

	fig,ax=plt.subplots()
	ax.semilogx(f_arr, 20*np.log10(a))
	ax.semilogx(f_arr, np.degrees(p))


	# to curve fit: gain, phase at f1, gain,phase at f2, gain,phase at f3. 
	#  Solve for r1, r4, cc
	#  however cc is a known-constant (bound?)

	from lmfit import minimize, Parameters, report_fit
	# Useful lmfit example 
	# https://stackoverflow.com/questions/20339234/python-and-lmfit-how-to-fit-multiple-datasets-with-shared-parameters?noredirect=1&lq=1

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
