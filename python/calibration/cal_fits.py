"""Fitting functions and calculations to extract impedance from 
square wave and sine-wave stimulus 

Oct 2022

Lucas Koerner, koer2434@stthomas.edu
"""
import functools
import os
import logging as log
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from analysis.utils import calc_fft, fft_maxs
from lmfit import minimize, Parameters, report_fit
import pdb
from analysis.utils import my_savefig, fig_size, fig_dir  # also configures matplotlib defautls
fig_dir = os.path.join(fig_dir, 'calibration')

# Useful lmfit example
# https://stackoverflow.com/questions/20339234/python-and-lmfit-how-to-fit-multiple-datasets-with-shared-parameters?noredirect=1&lq=1

plt.ion()

cc_cap = 4.491e-9 # measured with LCR 
c1 = cc_cap

def soft_sq_wave(t, f, a, h, phi, s=1):
    """
    Generate a softened square wave (sigmoid edges).

    Parameters
    ----------
    t : array-like
        Time array.
    f : float
        Frequency in Hz.
    a : float
        Amplitude.
    h : float
        DC offset.
    phi : float
        Phase offset in radians.
    s : float, optional
        Softness parameter (default 1).

    Returns
    -------
    ndarray
        Soft square wave signal.
    """
    # a square-wave that does not have infinitely fast edges. 
    return h + a * np.tanh(s * np.cos(2 * np.pi * f * t + phi))


def sine_wave(t, f, a, h, phi):
    """
    Generate a sine wave.

    Parameters
    ----------
    t : array-like
        Time array.
    f : float
        Frequency in Hz.
    a : float
        Amplitude.
    h : float
        DC offset.
    phi : float
        Phase offset in radians.

    Returns
    -------
    ndarray
        Sine wave signal.
    """
    return h + a * np.sin(2 * np.pi * f * t + phi)


def sine_wave_nodc(t, f, a, phi):
    """
    Generate a sine wave with no DC offset.

    Parameters
    ----------
    t : array-like
        Time array.
    f : float
        Frequency in Hz.
    a : float
        Amplitude.
    phi : float
        Phase offset in radians.

    Returns
    -------
    ndarray
        Sine wave signal.
    """
    return a * np.sin(2 * np.pi * f * t + phi)


def exponential_rise(t, a, k, c):
    """
    Generate an exponential rise signal.

    Parameters
    ----------
    t : array-like
        Time array.
    a : float
        Amplitude.
    k : float
        Exponential rate.
    c : float
        DC offset.

    Returns
    -------
    ndarray
        Exponential rise signal.
    """
    return a * (np.exp(k * t)) + c


def fit_sine(t, y, freq, freq_eps=1e-3):
    """
    Fit a sine wave to data using curve_fit.

    Parameters
    ----------
    t : array-like
        Time array.
    y : array-like
        Data to fit.
    freq : float
        Expected frequency.
    freq_eps : float, optional
        Allowed relative error in frequency (default 1e-3).

    Returns
    -------
    tuple
        Fit parameters and covariance.
    """
    # linear least squares fit to a sinusoid often has problems
    # better to use an FFT to extract amplitude and phase
    y = y - np.mean(y)
    a_guess = np.sqrt(2) * np.std(y)
    yfit = curve_fit(sine_wave_nodc, t, y,
                     p0=(freq, a_guess, 0),
                     bounds=((freq * (1 - freq_eps), a_guess * (0.8), -np.pi),
                             (freq * (1 + freq_eps), a_guess * 1.2, np.pi)))
    return yfit


def fit_sine_fft(t, y, method='quad_interpolate'):
    """
    Fit a sine wave to data using FFT for amplitude and phase extraction.

    Parameters
    ----------
    t : array-like
        Time array.
    y : array-like
        Data to fit.
    method : str, optional
        FFT peak extraction method (default 'quad_interpolate').

    Returns
    -------
    max_freq : float
        Frequency with maximum amplitude.
    amp : float
        Amplitude at max_freq.
    phase : float
        Phase at max_freq.
    """
    dc_level = np.mean(y)
    freq, max_freq, amp, phase = fft_maxs(y - dc_level, 1 / (t[1] - t[0]),
                                          method=method, plot=False, window='hann')

    return max_freq, amp, phase
    # return freq, max_freq, amp, phase


def tf(name):
    """
    Create a transfer function with selected parameters fixed.

    Parameters
    ----------
    name : str
        Name of the transfer function type.

    Returns
    -------
    function
        Partial transfer function with fixed parameters.
    """
    # create a transfer function from calc_tf that only uses 
    #   a subset of the parameters. 
    #   functools.partial generates a new function that has constant parameters
    #   no longer as inputs 
    if name == 'no_dut':
        # ignore c1, just use c2 
        return functools.partial(calc_tf, rs=np.inf, c2=1e-15, r5=np.inf, r6=np.inf)
    if name == 'vclamp_cm':
        pass


def vclamp_tf(f, cm, rleak, r5=100e3, r3=3.32e3, r4=5e3, cc=cc_cap, rcc=6.8e3):
    """
    Transfer function for voltage clamp calibration measurements.

    Parameters
    ----------
    f : float or array-like
        Frequency in Hz.
    cm : float
        Membrane capacitance.
    rleak : float
        Leak resistance.
    r5, r3, r4, cc, rcc : float, optional
        Circuit parameters.

    Returns
    -------
    amp : float or ndarray
        Gain (magnitude).
    phase : float or ndarray
        Phase (radians).
    """
    #  this is for voltage clamp calibration measurements
    # TODO: will need to solve for rleak 
    # Confirmed with the LTSpice result: clamp_electrodes.raw 

    # r5=100e3, r3=3.32e3, r4=5e3, cc=cc_cap, rcc=6.8e3
    # r5 is equivalent to COVG ri 
    # r3, r4, rcc can be inputs 

    rbot = par(r3, r4)
    rs = 1e3 # TODO: potentially solve for this in the future

    w = f * 2 * np.pi
    cc_rc = -1j * (1 / (w * cc)) + rcc
    num = par(-1j * (1 / (w * cm)), rleak) + rs + par(rbot, cc_rc)
    a = num / (num + r5)

    return np.abs(a), np.angle(a)


def lpf_tf(f, r5, cm):
    """
    Low-pass filter transfer function.

    Parameters
    ----------
    f : float or array-like
        Frequency in Hz.
    r5 : float
        Resistance.
    cm : float
        Capacitance.

    Returns
    -------
    amp : float or ndarray
        Gain (magnitude).
    phase : float or ndarray
        Phase (radians).
    """
    # Test lowpass filter transfer function 
    #  verify transfer function calculation match LTSpice
    w = f * 2 * np.pi
    num = -1j * (1 / (w * cm))
    a = num / (num + r5)

    return np.abs(a), np.angle(a)


def calc_tf(f, r1, r2, r3, c1, rs, c2, r5, r6):
    """
    General transfer function for the bath clamp with CC held at small signal ground.

    Parameters
    ----------
    f : float or array-like
        Frequency in Hz.
    r1, r2, r3 : float
        Resistances.
    c1, c2 : float
        Capacitances.
    rs, r5, r6 : float
        Additional resistances.

    Returns
    -------
    amp : float or ndarray
        Gain (magnitude).
    phase : float or ndarray
        Phase (radians).
    """
    # General transfer function for the bath clamp with CC held at small signal ground 
    # 
    #  variables match reference designators in schematic LTSpice bath_electrodes.asc 
    #  f: frequency
    #  r1: drive on (i.e., force)
    #  r2: sensing resistor so does not contribute to transfer function
    #  r3: CC electrode resistance 
    #  c1: CC capacitance 
    #  TODO: Implement transfer dependence of rs, c2, r5, r6. Assumption is that they are not connected 
    w = f * 2 * np.pi
    num = r3 - 1j * (1 / (w * c1))
    a = num / (num + r1)
    # see NB#2 pg116
    #  (s*r3*c1 + 1) / (s*(r3+r1)*c1 + 1)

    return np.abs(a), np.angle(a)


def elec_r_cc(f, tf_amp_phase, tf_type='elec_r_cc', rtotal=None, knowns={}):
    """
    Fit electrode resistance and capacitance from measured transfer function data.

    Parameters
    ----------
    f : array-like
        Frequencies tested.
    tf_amp_phase : tuple
        Measured gain (array) and phase (array).
    tf_type : str
        Transfer function type ('elec_r_cc', 'vclamp', 'vclamp_bound').
    rtotal : float, optional
        Known total resistance (for vclamp_bound).
    knowns : dict, optional
        Known circuit parameters.

    Returns
    -------
    tuple
        (fit results, frequency array, model evaluation, measured data)
    """
    def tf_eval(params, f, tf_type, knowns):

        if tf_type == 'elec_r_cc':
            tf_nodut = tf('no_dut')
            tf_test = functools.partial(tf_nodut, c1=c1)
        elif (tf_type == 'vclamp') or (tf_type == 'vclamp_bound'):
            # print('vclamp knowns')
            # print(knowns)
            tf_test = functools.partial(vclamp_tf, **(knowns)) 
            # tf_test = vclamp_tf

        if tf_type == 'elec_r_cc':
            r1 = params['r1'].value
            r2 = params['r2'].value
            r3 = params['r3'].value

            return tf_test(f, r1, r2, r3)

        elif tf_type == 'vclamp':            
            try:
                knowns['r5'] > 0
                cm = params['cm'].value
                return tf_test(f, cm)            
            except:
                r1 = params['r1'].value # r1 is a typo here, actually solving for r5
                cm = params['cm'].value 
                # print('Solving Vclamp for CM and r1')
                return tf_test(f, cm, r1)

        # TODO: not implemented once functools reduction of vclamp_tf was done 
        elif tf_type == 'vclamp_bound':  # since we measure rtotal using a current source: solve for r2 as rtotal-r1
            r1 = params['r1'].value
            cm = params['cm'].value
            rtotal = params['rtotal'].value
            if rtotal is None:
                log.error('rtotal is None. For voltage clamp bound fit need an rtotal input.')
                raise ValueError('rtotal cannot be None in vclamp_bnd')

            return tf_test(f, rtotal - r1, cm)

    def residuals(params, f_arr, data, tf_type, knowns):
        # calculate the difference between the data (gain, phase) and the
        #  evaluated impedance
        ap_tot = np.array([])
        for tft in tf_type:
            amp, phase = tf_eval(params, f_arr, tft, knowns)
            ap = np.vstack([amp, phase])
            ap_tot = np.append(ap_tot, ap)

        diff = ap_tot.ravel() - data.ravel()  # TODO: is this aligning mangitude and phase correctly?
        # The only change required is to use view instead of abs.
        # so that gain and phase both contribute to the fit
        return diff.flatten()

    def residuals_magnitude(params, f_arr, data, tf_type, knowns):
        # calculate the difference between the data (magnitude) and the
        #  evaluated impedance

        ap_tot = np.array([])
        for tft in tf_type:
            amp, phase = tf_eval(params, f_arr, tft, knowns) # evaluate a transfer function of type tft 
            ap_tot = np.append(ap_tot, amp)
        # pdb.set_trace()

        diff = np.abs(ap_tot) - data

        return diff.flatten()

    if type(tf_type) is not list:
        tf_type = [tf_type]

    if tf_type[0] == 'elec_r_cc': # bath clamp board 
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
    # lmfit: minimize
    # TODO: Plot the tf_phase 0 vs the f --> confident in the stats: f - x, tf_amp_phase[0] - y
    result = minimize(residuals_magnitude, fit_params, args=(f, tf_amp_phase[0], tf_type, knowns))
    report_fit(result)

    data_split = np.split(tf_amp_phase[0], len(tf_type))

    # Plot measured transfer functions and fits -- plotting data is returned to the calling function
    for tft_idx, tft in enumerate(tf_type):
        model_eval = tf_eval(result.params, f, tft, knowns)
        #ax.semilogx(f, 20 * np.log10(np.abs(model_eval[0])), label=f'Drive {elec} (fit)', linestyle=next(linesty))
        #ax.semilogx(f, 20 * np.log10(data_split[tft_idx]), label=f'Drive {elec} (meas.)', 
        #    marker=next(markers), linestyle='none')

    # also try with amplitude and phase, don't expect to work as well
    amp = tf_amp_phase[0]
    phase = tf_amp_phase[1]
    result2 = minimize(residuals, fit_params, args=(f, np.vstack([amp, phase]), tf_type, knowns))
    # report_fit(result2)

    return (result, result2), f, model_eval[0], data_split[tft_idx]  # result ignores phase, result 2 considers phase


# use known rtotal: 1 TF is r1; the other is rtotal-r1

def par(z1, z2):
    """
    Calculate the parallel combination of two impedances.

    Parameters
    ----------
    z1 : float or complex
        First impedance.
    z2 : float or complex
        Second impedance.

    Returns
    -------
    float or complex
        Parallel impedance.
    """
    # parallel combination of two impedances
    return 1 / (1 / z1 + 1 / z2)


if __name__ == '__main__':
    # various tests of calibration fits
    t = np.linspace(0, 10e-3, 1000000)
    phi = 0.8
    h = 2.2
    a = 1
    f = 1e3
    y = h + a * np.cos(2 * np.pi * f * t + phi)

    plt.plot(t, y)

    # yfit = fit_sine(y,y,freq=f)
    # plt.plot(t, sine_wave_nodc(t, *yfit[0]) + h)

    plt.plot(t, sine_wave(t, f, amp, dc_level, phase))

    plt.figure()
    calc_fft(y, 1 / (t[1] - t[0]), plot=True, WINDOW='hann')

    tf_nodut = tf('no_dut')
    f_arr = np.logspace(3, 5, 40)
    tf_nodut_v = np.vectorize(tf_nodut)
    a, p = tf_nodut_v(f_arr, 3.3e3, 5e3, 6.8e3, cc_cap)

    fig, ax = plt.subplots()
    ax.semilogx(f_arr, 20 * np.log10(a))
    ax.semilogx(f_arr, np.degrees(p))


    # to curve fit: gain, phase at f1, gain,phase at f2, gain,phase at f3.
    #  Solve for r1, r4, cc
    #  however cc capacitance is a known-constant (bound?)

    def ap_eval(params, f_arr):
        r1 = params['r1'].value
        r2 = params['r2'].value
        r3 = params['r3'].value
        cc = cc_cap

        a, p = tf_nodut_v(f_arr, r1, r2, r3, cc)
        return a, p


    def residuals(params, f_arr, data):
        # calculate the difference between the data (gain, phase) and the
        #  evaluated impedance
        a, p = ap_eval(params, f_arr)
        ap = np.vstack([a, p])

        diff = ap - data
        # The only change required is to use view instead of abs.
        # so that gain and phase both contribute to the fit
        return diff.flatten()


    fit_params = Parameters()
    fit_params.add('r1', value=5e3, min=100, max=15e3)
    fit_params.add('r2', value=5e3, min=100, max=15e3)
    fit_params.add('r3', value=5e3, min=100, max=15e3)

    data = np.vstack([a, p])

    # run the global fit to all the data sets
    result = minimize(residuals, fit_params, args=(f_arr, data))
    report_fit(result)

    af, pf = ap_eval(result.params, f_arr)
    ax.semilogx(f_arr, 20 * np.log10(af), linestyle='--')
    ax.semilogx(f_arr, np.degrees(pf), linestyle='--')

    f_arr = np.logspace(1, 5, 40)
    # def vclamp_tf(f, cm, r5=100e3, r3=3.32e3, r4=5e3, cc=cc_cap, rcc=6.8e3)
    tf = np.vectorize(vclamp_tf)
    a, p = tf(f_arr, 33e-9, 100e3, 3.3e3, 5e3, cc_cap, 6.8e3)

    fig, ax = plt.subplots()
    ax.semilogx(f_arr, 20 * np.log10(a))
    # ax.semilogx(f_arr, np.degrees(p))
