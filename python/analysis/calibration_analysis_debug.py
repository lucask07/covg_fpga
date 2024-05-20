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
import logging as log

from analysis.calibration_analysis import read_cal_data, two_elec_vs_freq, r_from_square

PLT = True
tf_type = 'vclamp'
#tf_type = 'elec_r_cc'

capture_date = '20240507'

if tf_type == 'elec_r_cc':
    if sys.platform == 'darwin':
        data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/{}/'.format(capture_date)
    elif sys.platform == 'win32':
        data_dir = 'c/Users/koer2434/Documents/covg/data/clamp/{}/'.format(capture_date)
    file_extra = ''
elif tf_type == 'vclamp':
    if sys.platform == 'darwin':
        data_dir = '/Users/koer2434/Library/CloudStorage/OneDrive-UniversityofSt.Thomas/UST/research/covg/fpga_and_measurements/daq_v2/data/calibrations/{}/'.format(capture_date)
    elif sys.platform == 'win32':
        data_dir = 'C:/Users/koer2434/Documents/covg/data/clamp/20240507/'
        #data_dir = 'c:/Users/koer2434/Documents/covg/data/clamp/{}/'.format(capture_date)
    file_extra = '_vclamp'

filename = f'imp_all_steps_chirp{file_extra}.npz'

if file_extra == '_vclamp': 
    r_total_guess = 300e3 # TODO: replace with the electrode configuration 
else:
    r_total_guess = 5e3 + 3.32e3
    
data = read_cal_data(data_dir=data_dir, filename=filename)
predicted_res, pcov, res_fit_mesg = r_from_square(r_total_guess, data, PLT=PLT)  # get resistance from a square wave 
component_fits, fit_notes, components = two_elec_vs_freq(data, tf_type, rtotal=predicted_res, PLT=True)