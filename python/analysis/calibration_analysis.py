"""
Oct 2022

Lucas Koerner, koerner.lucas@stthomas.edu
Analyze impedance analyzer spectrum to determine resistances and capacitances 

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
import logging
import itertools
import json 
import pandas as pd

from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5, separate_ads_sequence
from analysis.utils import calc_fft, phase_by_xcorr
from filters.filter_tools import butter_lowpass_filter, delayseq_interp

from calibration.cal_fits import fit_sine_fft, soft_sq_wave, sine_wave, elec_r_cc, vclamp_tf
from scipy.optimize import curve_fit
from analysis.utils import my_savefig, fig_size, fig_dir, data_dir, my_savedata  # also configures matplotlib defautls
fig_dir = os.path.join(fig_dir, 'calibration')
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

PLT = True

chop_idx = 200 # remove elements before this to allow voltage to settle after changing frequency 

full_scale_current = 0.8e-6 # full-scale current is 0.8 uA 
dac_resolution = 16 # in bits 
freq_limit_forfit = 1.5e3

log = logging.getLogger('Calibration')
log.setLevel(logging.FATAL)
log.setLevel(logging.INFO)
log.setLevel(logging.DEBUG)


def read_cal_data(data_dir, filename):

    data = np.load(os.path.join(data_dir, filename), allow_pickle=True)
    # 0-d arrays can be indexed using the empty tuple:
    # https://stackoverflow.com/questions/8361561/recover-dict-from-0-d-numpy-array
    data = data['arr_0'][()]

    return data

def r_from_square(r_total_guess, data, PLT=False, name='', ANNOTATE=False):
    # analyze square wave signal for the predicted resistance 

    # name: names the figure that is saved 

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
            else:
                current_amp = (amp_dac*1e-6)
                sq_wave_amp_guess = r_total_guess * current_amp
            log.debug(f'Square wave amp guess: {sq_wave_amp_guess}. DAC wave = {dac_wave}')
        
            # use tanh to allow for dull edges 
            # soft_sq_wave: h + a * np.tanh(s * np.cos(2 * np.pi * f * t + phi))
            # fit with scipy.optimize.curve_fit, no bounds so uses the method lm: Levenberg-Marquardt as implemented in MINPACK
            # minimizes sum of squared residuals
            # pcov: estimated approx covariance of popt -> 1 standard deviation errors = np.sqrt(np.diag(pcov))
            yfit, pcov, infodict, mesg, ier = curve_fit(soft_sq_wave, t,y , p0=(freq, sq_wave_amp_guess, 0, 0, 0), full_output=True) # freq, amp, offset, phase, smoothing factor 
                            #bounds = ([0,0,-15,0,0], [10e6, np.inf, 15, 2*np.pi, np.inf]))  # bounds cause problems. Not sure why
            predicted_res = yfit[1]/current_amp
            log.info(f'Current amplitude {current_amp}')
            log.info(f'Predicted resistance {predicted_res}')

            if PLT:
                fig, ax = plt.subplots(figsize=fig_size)
                ax.plot(t*1e3, y*1e3, marker='.', label='meas.', linestyle='none')
                ax.plot(t*1e3, soft_sq_wave(t, *yfit)*1e3, label='fit')
                ax.set_ylabel('[mV]')
                ax.set_xlabel('time [ms]')
                if ANNOTATE:
                    ax.text(0.3, 0.4, f'$R_{{p1}} + R_{{p2}} = {predicted_res/1e3:2.2f}\, k\Omega$', bbox=dict(facecolor='white', pad=3), transform=ax.transAxes)
                # ax.legend()
                my_savefig(fig, fig_dir, f'resistance_cal_square_wave{name}')
                
    return predicted_res, pcov, mesg


def meas_transfer_func(freqs, ts, data, dac_wave):
    # freqs: array of frequency. one y1 array and one y2 array for each frequency 
    # t: the time array from the y data 
    # y1s : array of arrays 
    # y2s : array of arrays 

    # summary arrays that are the output of this function
    freq_m = np.array([])
    gain = np.array([])
    phase_arr = np.array([])

    amp_arr = np.array([])
    dac_amp_arr = np.array([])

    for idx, freq in enumerate(freqs):

        t = ts[idx][chop_idx:]
        t = t - t[0] # configure the time to start at 0 for compatibility with chirp measurements
        y1 = data[idx][chop_idx:] # if chopped at an arbitrary point there will be a phase shift that varies with frequency if compared to an ideal sine
        y2 = dac_wave[idx][chop_idx:] 

        max_freq, amp, phase = fit_sine_fft(t, y1, method='quad_interpolate') # cnly used for finding the frequency 
        xcorr_phase, sample_lag, n_period_float, amp_ratio, amp, dac_amp = phase_by_xcorr(freq, t, y1, 
                                                                            dac_wave=y2, debug_plots=False)
        log.info(f'Amp. of sine from fft: {amp:.2f}. Phase: {np.degrees(phase):.2f}, {np.degrees(xcorr_phase):.2f}  at freq of {max_freq} [Hz]') 
        log.info(f'Sample lag of {sample_lag}. With {n_period_float} samples in a period')

        freq_m = np.append(freq_m, max_freq)
        gain = np.append(gain, amp_ratio)
        phase_arr = np.append(phase_arr, xcorr_phase)

        amp_arr = np.append(amp_arr, amp)
        dac_amp_arr = np.append(dac_amp_arr, dac_amp)

    return freq_m, gain, phase_arr, amp_arr, dac_amp_arr

def two_elec_vs_freq(data, tf_type, rtotal=None, freq_limit_forfit=None, PLT=False, knowns={}, name='', ANNOTATE=False):
    '''
    Analyze sine-wave data that alternates between driving electrode 1 and then driving electrode 2
    DUT (cell capacitance is expected to be connected)
    This compares amplitudes of the two different swap configurations -- in both cases uses the 'volt' measurement not the 'v1'

        Only works for the bath clamp; the vclamp needs to use the v1 measurements since only one electrode can be driven
    
        name : names the figures that are saved 
    '''
    fit_results = {}
    component_fits = {}

    # analyze two different electrode configurations at each frequency 
    # 1 is a reference and calculate 
    freq_arr_fixed = np.unique([data[data_key]['freq'] for data_key in data])
    # Plot measured transfer functions and fits  
    fig_tf, ax_tf = plt.subplots(figsize=fig_size)
    electrodes = itertools.cycle(['P1', 'P2'])
    markers = itertools.cycle(['*', 'o'])
    linesty = itertools.cycle(['-', '--'])

    # loop through two different configurations 
    vclamp_iter = 0
    for (drive_elec, meas_adc) in [('drive_CAL1', 'CAL_SIG1'), ('drive_CAL2', 'CAL_SIG2')]:
        fit_results[drive_elec] = {}
        for k in ['freq', 'gain', 'phase', 'e_config']:
            fit_results[drive_elec][k] = np.array([])

        freq_arr = freq_arr_fixed
        for data_key in data:
            d = data[data_key]
            # Determine if the test is on bath_clamp or voltage_clamp:
            test_type = None
            if tf_type == "elec_r_cc":
                test_type = "bath_clamp"
            elif tf_type == "vclamp":
                test_type = "voltage_clamp"
            ##### end #######
            # print(f"~~~~ Testing {test_type} ~~~~")
            if d['freq'] in freq_arr and d['shape'] == 'SINE' and d[test_type]['ADC_SEL']==meas_adc and d[test_type]['DAC_SEL']==drive_elec: # CAL_SIG1 is the reference 
                freq = d['freq']
                # find the companion 
                key_pair = [data_key_pair for data_key_pair in data if ((data[data_key_pair]['freq'] == freq) and (data[data_key_pair][test_type]['DAC_SEL'] == drive_elec) and (data_key_pair != data_key))][0]  
                # so we don't process this group again remove the frequency from the array
                freq_arr = freq_arr[freq_arr != freq]
                log.debug(f'Found pair of keys {data_key} and {key_pair} at frequency of {freq} with drive electrode {drive_elec}')
                t = d['t'][chop_idx:]
                t = t - t[0] # configure the time to start at 0 for compatibility with chirp measurements
                y = d['volt'][chop_idx:] # if chopped at an arbitrary point there will be a phase shift that varies with frequency if compared to an ideal sine
                y_pair = data[key_pair]['volt'][chop_idx:]

                log.debug(f'---- Freq = {freq}')
        #            for method in ['quad_interpolate', 'single_bin']: # methods to find the maximum fourier amplitude and frequency 
                for method in ['quad_interpolate']:
                    max_freq, amp, phase = fit_sine_fft(t, y, method=method) # cnly used for finding the frequency 
                    xcorr_phase, sample_lag, n_period_float, amp_ratio, amp, dac_amp = phase_by_xcorr(freq, t, y_pair, 
                                                                                        dac_wave=y, debug_plots=False)
                    log.info(f'Amp. of sine from fft: {amp:.2f}. Phase: {np.degrees(phase):.2f}, {np.degrees(xcorr_phase):.2f}  at freq of {max_freq} [Hz]') 
                    log.info(f'Sample lag of {sample_lag}. With {n_period_float} samples in a period')

                fit_results[drive_elec]['freq'] = np.append(fit_results[drive_elec]['freq'], max_freq)
                fit_results[drive_elec]['gain'] = np.append(fit_results[drive_elec]['gain'], amp_ratio)
                # TODO: Uncomment this line below when debugging process is finished
                # print("flagged!")
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
            fig.canvas.draw()
            fig.canvas.flush_events()

        if freq_limit_forfit is not None:
            f_idx = fit_results[drive_elec]['freq'] < freq_limit_forfit
        else:
            f_idx = fit_results[drive_elec]['freq'] > 0 # all frequencies
        # TODO: Uncomment this line below when debugging process is finished
        # print(fit_results[drive_elec]['gain'][f_idx])
        if test_type == "bath_clamp" or vclamp_iter > 0:
            component_fits[drive_elec], f, model_eval, meas_data = elec_r_cc(fit_results[drive_elec]['freq'][f_idx], 
                                                (fit_results[drive_elec]['gain'][f_idx], fit_results[drive_elec]['phase'][f_idx]),
                                                tf_type = tf_type, knowns=knowns)
            data_csv : dict = dict(f=f, meas_data=meas_data, model_eval=model_eval)
            data_csv_dir = os.path.join(data_dir, f"bathguard_headstage_{test_type}_{drive_elec}_regression_data.csv")
            my_savedata(data_csv_dir, **data_csv)
            elec = next(electrodes) 
            labels = {'P1': '$R_{p1}$', 'P2': '$R_{p2}$'} 
        
            ax_tf.semilogx(f, 20 * np.log10(meas_data), label=f'{labels[elec]} meas.', 
                marker=next(markers), linestyle='none')
            ax_tf.semilogx(f, 20 * np.log10(np.abs(model_eval)), label=f'{labels[elec]} fit', 
                        linestyle=next(linesty))
            fig_tf.canvas.draw()
            fig_tf.canvas.flush_events()
        if test_type == "voltage_clamp":
            vclamp_iter += 1

    ax_tf.set_ylabel('$|H_c| \; [dB]$')
    ax_tf.set_xlabel('f [Hz]')
    ax_tf.legend(loc='lower left') # to avoid conflict with the annotations
    # save later once we have the fit results annotated
    # Since we don't do anything about drive_cal1 and cal_sig1 for voltage_clamp, we should black this out
    if tf_type != 'vclamp':
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

    # fitting to determine the component values 
    if tf_type == 'vclamp':
        #knowns = {'r1': , 'r2': , 'c3': , 'r3': }
        #r3=knowns['r1'], r4=knowns['r2'], cc=knowns['c3'], rcc=knowns['r3']

        # component_fits[drive_elec], f, model_eval, meas_data = elec_r_cc(f_fit_short, (g_fit, p_fit), 
        #                                        tf_type = ['vclamp', 'vclamp_bound'], rtotal=rtotal, knowns=knowns)
        f_fit = np.hstack((fit_results['drive_CAL2']['freq'][f_idx]))
        g_fit = np.hstack((fit_results['drive_CAL2']['gain'][f_idx]))
        # normalize the gain to be 1 at lowest frequencies 
        # g_fit = g_fit/g_fit[0]
        p_fit = np.hstack((fit_results['drive_CAL2']['phase'][f_idx]))
        # TODO: is it even worth it to refit vclamp when CAL_SIG1 and drive_CAL1 never exist for vclamp??
        # component_fits[drive_elec], f, model_eval, meas_data = elec_r_cc(f_fit_short, (g_fit, p_fit), 
        #                                        tf_type = ['vclamp'], rtotal=rtotal, knowns=knowns)
        component_fits[drive_elec], f, model_eval, meas_data = elec_r_cc(f_fit, (g_fit, p_fit), 
                                                tf_type = ['vclamp'], rtotal=rtotal, knowns=knowns)
    # TODO: use frequency data to estimate Rs individual

    idx = 0 # this selects the fit to just magnitude which shows better results 
    # idx = 1 # fit to magnitude and phase 

    components = {}
    if tf_type == 'elec_r_cc':  # this is the bath clamp and can extract the resistance of the CC electrode as well as P1/P2 
        components['r1'] = component_fits['drive_CAL1'][idx].params['r1'].value
        components['r2'] = component_fits['drive_CAL2'][idx].params['r1'].value
        # CC resistance is the average of the two fits 
        components['r3'] = np.average([component_fits['drive_CAL1'][idx].params['r3'].value, 
                        component_fits['drive_CAL2'][idx].params['r3'].value])

    if tf_type == 'vclamp':  
        # TODO: can only drive on one configuration (CAL2). Don't use both and don't average Cm 
        # TODO: there is no CAL_SIG1 or drive_CAL1 for vclamp!
        # components['r1'] = component_fits['drive_CAL1'][idx].params['r1'].value # ignore this value 
        components['r2'] = component_fits['drive_CAL2'][idx].params['r1'].value # TODO: use this value; should be RI   
        # components['cm'] = np.average([component_fits['drive_CAL1'][idx].params['cm'].value, component_fits['drive_CAL2'][idx].params['cm'].value])
        components['cm'] = np.average([component_fits['drive_CAL2'][idx].params['cm'].value])

    if ANNOTATE:
        ax_tf.text(0.65, 0.9, f'$R_{{p1}} = {components["r1"]/1e3:2.2f} \, k\Omega$', bbox=dict(facecolor='white', edgecolor='white', pad=3), transform=ax_tf.transAxes)
        ax_tf.text(0.65, 0.8, f'$R_{{p2}} = {components["r2"]/1e3:2.2f} \, k\Omega$', bbox=dict(facecolor='white', edgecolor='white', pad=3), transform=ax_tf.transAxes)
        # TODO: There is no r3 in vclamp either!
        ax_tf.text(0.65, 0.7, f'$R_{{cc}} = {components["r3"]/1e3:2.2f} \, k\Omega$', bbox=dict(facecolor='white', edgecolor='white', pad=3), transform=ax_tf.transAxes)

    my_savefig(fig_tf, fig_dir, f'transfer_function_fit_{tf_type}{name}')

    component_fits_key = 'drive_CAL1' if tf_type == 'elec_r_cc' else 'drive_CAL2'

    # fit_notes = {'success': component_fits['drive_CAL1'][idx].success,
    #           'chisqr': component_fits['drive_CAL1'][idx].chisqr,
    #           'message': component_fits['drive_CAL1'][idx].message}
    fit_notes = {'success': component_fits[component_fits_key][idx].success,
               'chisqr': component_fits[component_fits_key][idx].chisqr,
               'message': component_fits[component_fits_key][idx].message}

    return component_fits, fit_notes, components


def total_res_iso_res(data_dir, filename, r_total_guess, tf_type, PLT=False):
    '''
    reads a numpy .npz file and then determines resistance from a square wave fits 
    '''
    # TODO: where is the `knowns`??
    data = read_cal_data(data_dir=data_dir, filename=filename)
    predicted_res, pcov, res_fit_mesg = r_from_square(r_total_guess, data, PLT=PLT)  # get resistance from a square wave 
    
    shapes = [data[d]['shape'] for d in data]
    if shapes.count('SINE') > 1:
        component_fits, fit_notes, components = two_elec_vs_freq(data, tf_type, rtotal=predicted_res, PLT=PLT)
    else:
        # this is correct syntax 
        component_fits = fit_notes = components = None
        
    return predicted_res, res_fit_mesg, component_fits, fit_notes, components

def main():
    """
    analyze data already captured. Only supports the bath clamp. Use calibration_analysis_vclamp_tf.py 
    """
    tf_type = 'elec_r_cc'  # bath clamp using the CC capacitor as a load 

    if tf_type == 'elec_r_cc':
        if sys.platform == 'darwin':
            data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp/20240606/'
        elif sys.platform == 'win32':
            data_dir = r'C:/Users/koer2434/OneDrive - University of St. Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp/20240606/'
        file_extra = ''

    board_1_rp1 = [3310.9, 4974.9,  7309, 10008] # in Excel file model_cell_groundtruth.xlsx 
    board_2_rp1 = [3312.1, 4986.5,  7310.8, 10004.9] # in Excel file model_cell_groundtruth.xlsx 
    names = ['3p3k', '5k', '7p3k', '10k']
    board_1_rp2 = 4999.2
    board_2_rp2 = 4986.7
    res = {'set': [], 'rp1_fit': [], 'rp2_fit': [], 'multimeter_rp2': [board_2_rp2]*4, 
           'multimeter_rp1': board_1_rp1, 'perc_err_rp1':[],
           'total_res': [], 'total_res_gt': [], 'total_res_perc_err': []}

    for date in ['20240606-110644', '20240606-111113', '20240606-111317', '20240606-111439']:
        # the JSON file is incorrect for 20240606-111113 -- should be 5k 
        json_file = f'setup_info{date}.json'
        filename = f'imp_all_steps_chirp_{date}_bath.npz'
        with open(os.path.join(data_dir, json_file)) as f:
            d_meta = json.load(f)
        print(d_meta.keys())
        
        res['set'].append(d_meta['rpcj1'])
        r_total_guess = 5e3 + 5e3
            
        data = read_cal_data(data_dir=data_dir, filename=filename)
        predicted_res, pcov, res_fit_mesg = r_from_square(r_total_guess, data, PLT=PLT, name=names[len(res['rp1_fit'])], ANNOTATE=True)  # get resistance from a square wave 
        component_fits, fit_notes, components = two_elec_vs_freq(data, tf_type, rtotal=predicted_res, PLT=False, name=names[len(res['rp1_fit'])], ANNOTATE=True)
        res['rp1_fit'].append(component_fits['drive_CAL1'][0].params['r1'].value)
        res['rp2_fit'].append(component_fits['drive_CAL2'][0].params['r1'].value)
        res['perc_err_rp1'].append( (res['rp1_fit'][-1] - res['multimeter_rp1'][len(res['rp1_fit'])-1])/res['multimeter_rp1'][len(res['rp1_fit'])-1]*100)
        res['total_res'].append(predicted_res)
        res['total_res_gt'].append(res['multimeter_rp1'][len(res['rp1_fit'])-1] + res['multimeter_rp2'][len(res['rp1_fit'])-1])
        res['total_res_perc_err'].append( (res['total_res'][-1] - res['total_res_gt'][-1])/res['total_res_gt'][-1]*100)

    df = pd.DataFrame(res)
    df.to_csv(os.path.join(fig_dir, 'bath_cal_summary_stats.csv'))
    return predicted_res, res_fit_mesg, component_fits, fit_notes, components, data, res

if __name__ == "__main__":
    predicted_res, res_fit_mesg, component_fits, fit_notes, components, data, res = main()