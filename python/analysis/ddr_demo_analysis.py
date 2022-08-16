"""
General analysis of COVG ADC data (h5 files)
Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3
# from pyripherals.utils import calc_impedance, from_voltage, to_voltage, read_h5
from pyripherals.utils import from_voltage, to_voltage, read_h5
import scipy
from scipy.signal.windows import hann
from scipy.fft import rfftfreq
from scipy.fft import rfft
from scipy import signal
from analysis.adc_data import separate_ads_sequence
from analysis.utils import calc_fft
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

"""
Connectivity:
 * Daughtercard position 0 to clamp board (v2) + model cell
 * Daughtercard position 1 to 2nd clamp board (v2) + model cell
 * Position 2: empty
 * Position 3 daughter card with just differential buffer connected to function generator (note this is showing as adc channel 2)

Daughtercard 0: 
* GP_ADC_0: pin 9 --> CAL_ADC
* GP_ADC_1: pin 19 --> AMP_OUT
* DAC1_CAL0: pin 3 --> CAL_DAC

Daughtercard 1:
* GP_ADC_8: pin 9 --> CAL_ADC
* GP_ADC_2: pin 19 --> AMP_OUT
* DAC1_CAL1: pin 3 --> CAL_DAC
"""

# configure Matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()

data_dir = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/ddr_demo/20220725/"
file_name = 'test'
figure_dir = "/Users/koer2434/My Drive/UST/research/covg/manuscripts/ians_eit_modification/figures/"
SAVE_FIGS = True

# make directories if needed 
for d in [figure_dir, data_dir]:
    if not os.path.exists(d):
        os.makedirs(d)

def my_savefig(fig, figname):
    fig.tight_layout()
    if SAVE_FIGS:
        for e in ['.png', '.pdf']: # use pdf rather than eps to support transparency
            fig.savefig(os.path.join(figure_dir,
                                     figname + e))



ads_voltage_range = 5
ads_sequencer_setup = [('1', '0')]

# constants 
FS = 5e6  # sampling frequency 
dac80508_offset = 0x8000
FS_ADS = 1e6

FAST_DAC_FREQ = 7000
target_freq_sdac = 12000.0
fg_freq = 160e3

f = FPGA()
f.init_device()
ddr = DDR3(fpga=f, data_version='TIMESTAMPS')

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(
    0) + '.h5', chan_list=np.arange(8))
# Long data sequence -- entire file
adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = ddr.data_to_names(chan_data, old=True)

############### extract the ADS data just for the last run and plot as a demonstration ############
ads_data_v = {}
for letter in ['A', 'B']:
    # ADS8686 is a bipolar converter and the twos_complement is already done in the ddr method data_to_names
    ads_data_v[letter] = np.array(to_voltage(
        ads_data_tmp[letter], num_bits=16, voltage_range=ads_voltage_range*2, use_twos_comp=False))

total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
total_seq_cnt[::2] = ads_seq_cnt[0]
total_seq_cnt[1::2] = ads_seq_cnt[1]
ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)
#########

# ----- Check frequency of results ----------
def check_fft(t, y, predicted_freq, WINDOW='none'):
    ffreq, famp, max_freq, fig, ax = calc_fft(y, 1/(t[1]-t[0]), plot=True, WINDOW=WINDOW)
    print(f'Frequency of maximum amplitude {max_freq} [Hz]')
    print(f'Predicted frequency: {predicted_freq}')
    rms = np.std(y)
    print(f'RMS amplitude: {rms}, peak amplitude: {rms*1.414}')
    print('-'*40)
    return ffreq, famp, max_freq, fig, ax

wtype = 'hann'

t = np.arange(0,len(adc_data[0]))*1/FS
crop_start = 0 # placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

# DACs 
t_dacs = t[crop_start::2]  # fast DACs are saved every other 5 MSPS tick

for dac_ch in range(4):
    fig,ax=plt.subplots()
    y = dac_data[dac_ch][crop_start:]
    lbl = f'Ch{dac_ch}'
    ax.plot(t_dacs*1e6, y, marker = '+', label = lbl)
    print(f'Min {np.min(y[2:])}, Max {np.max(y)}') # skip the first 2 readings which are 0
    ax.legend()
    ax.set_title('Fast DAC data')
    ax.set_xlabel('s [us]')


# fast ADC. AD7961
adc_data_v = {}
for ch in range(4):
    # this gives -4.096 to 4.095875 
    adc_data_v[ch] = to_voltage(adc_data[ch], num_bits=16, voltage_range=4.096*2, use_twos_comp=True)
    fig,ax=plt.subplots()
    lbl = f'Ch{ch}'
    ax.plot(t*1e6, adc_data_v[ch], marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Fast ADC data')
    ax.set_xlabel('s [us]')

# ADS8686 
fig,ax=plt.subplots()
for chan, ch_idx in [('A',1), ('B',0)]:
    y = ads_separate_data[chan][int(ch_idx)]
    t_ads = np.arange(0,len(y))*(1/FS_ADS)*len(ads_sequencer_setup)
    ax.plot(t_ads*1e6, y, marker = '+', label = f'ADS: {chan}')
    # check ADS8686
    print('FFT of ADS8686')
    ffreq, famp, max_freq, fig, ax = check_fft(t_ads, y, target_freq_sdac, WINDOW=wtype)

ax.legend()
ax.set_xlabel('s [us]')
ax.set_title('ADS8686 data')

# check AD7961 channel 0. Frequency from clamp board
print('FFT of AD7961 channel 0')
ffreq, famp, max_freq, fig, ax = check_fft(t, adc_data_v[0], FAST_DAC_FREQ, WINDOW=wtype)

# check AD7961 channel 2. Frequency from function generator 
print('FFT of AD7961 channel 2')
print(f'Time length is {np.min(t)} to {np.max(t)}')
ffreq, famp, max_freq, fig, ax = check_fft(t, adc_data_v[2], fg_freq, WINDOW=wtype)

# the function generator amplitude is 2 V 
ax.set_ylabel('V')
ax.set_xlim([1e3, 2.5e6])
yl = ax.get_ylim()
ax.set_ylim([yl[0], 0.4])

print('Amplitude of FFT and sine-wave')

sdev = np.std(adc_data_v[2])
print(f'Standard deviation: {sdev}')
print(f'Amplitude: {np.sqrt(2)*sdev}')

x0, y0, width, height = 0.2, 0.2, 0.7, 0.7
axins2 = inset_axes(ax, width="100%", height="100%", loc='upper left',
                   bbox_to_anchor=(0.125,1-0.35,.3,.3), bbox_transform=ax.transAxes)

axins2.plot(t*1e6, adc_data_v[2], color='k')
axins2.set_xlabel('t [$\mu$s]')
axins2.set_ylabel('V')
axins2.set_xlim([1000, 1050])
print(f'Fast ADC Max: {np.max(adc_data_v[2])}, Min: {np.min(adc_data_v[2])}, Avg: {np.mean(adc_data_v[2])} ')

ax.annotate(
# Label and coordinate
'f=160 kHz', xy=(165e3, 0.01), xytext=(300e3, 0.05) ,
horizontalalignment="center",color='m',
# Custom arrow
arrowprops=dict(arrowstyle='->',lw=1, color='m'))

my_savefig(fig, 'adc_fft_demo')

fast_dac_amp = 0x400 # 0x040
dac_offset = 0x2000
step_len = 8000

#for i in range(6):
    #ddr.data_arrays[i], fdac_freq = ddr.make_sine_wave(fast_dac_amp, FAST_DAC_FREQ,
    #                                    offset=0x1000)

# CMD voltage for Daughter card 0,1
ddr.data_arrays[1] = ddr.make_step(low=dac_offset - int(fast_dac_amp),
                                               high=dac_offset + int(fast_dac_amp),
                                               length=step_len)  # 1.6 ms between edges

if 0: # use Daughtercard 1 just for GP DAC to GP ADC via the calibration line 
    ddr.data_arrays[3] = ddr.make_step(low=dac_offset - int(fast_dac_amp),
                                                   high=dac_offset + int(fast_dac_amp),
                                                   length=step_len)  # 1.6 ms between edges

# ---------- configure "slow" DAC DAC80508
SLOW_DAC = True
if SLOW_DAC:
    sdac_amp_volt = 1 # 1
    target_freq_sdac = 12000.0
    sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

    # Data for the 2 DAC80508 "Slow DACs"
    sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq_sdac, offset=dac80508_offset)

    # Specify output channel for DAC80508
    sdac_1_out_chan = 1
    sdac_2_out_chan = 0

    # Clear bits in the FDAC DDR stream that store the slow DAC channel
    for i in range(6):
        ddr.data_arrays[i] = np.bitwise_and(ddr.data_arrays[i], 0x3fff)

    # Load data into DDR
    # Set channel bits
    ddr.data_arrays[0] = np.bitwise_or(ddr.data_arrays[0], (sdac_1_out_chan & 0b110) << 13)
    ddr.data_arrays[1] = np.bitwise_or(ddr.data_arrays[1], (sdac_1_out_chan & 0b001) << 14)
    ddr.data_arrays[2] = np.bitwise_or(ddr.data_arrays[2], (sdac_2_out_chan & 0b110) << 13)
    ddr.data_arrays[3] = np.bitwise_or(ddr.data_arrays[3], (sdac_2_out_chan & 0b001) << 14)

    # load slow DAC sine-wave in DDR channels 7 and 8 
    for i in range(2):
        ddr.data_arrays[i + 6] = sdac_sine


fig,ax = plt.subplots(2,1)

# daughter-card 1. GP DAC data and ADS ADC measured data 
ads_data = ads_separate_data['B'][0]
dac_data = ddr.data_arrays[6][0:len(t_dacs)]

vref = 2.5
vrange = 5
bipolar_amp_gain = (15e3/10e3 + 15e3/30.1e3 + 15e3/15e3)
dac_data_v = to_voltage(dac_data, num_bits=16, voltage_range=vrange, use_twos_comp=False)
# TODO: why this /2? 
dac_data_v = dac_data_v*bipolar_amp_gain/2 - vref*1.5
ax[0].plot(t_dacs*1e3, dac_data_v, 'k', marker='*', label='DAC')
ax[0].plot(t_ads*1e3, ads_data, 'g', linestyle='--', marker='o', label='ADC')
ax[0].set_xlim([4.2, 4.6])
ax[0].grid(True)
ax[0].set_xlabel('t [ms]')
ax[0].set_ylabel('V')
ax[0].legend()
# ADC is phased delayed by about 4 us, which seems reasonable given the settling time of the DAC

# daughter-card 0. Fast DAC data and ADC measured data 
ads_data = ads_separate_data['A'][1]
dac_data = np.bitwise_and(ddr.data_arrays[1][0:len(t_dacs)], 0x3fff)
dac_data_v = to_voltage(dac_data, num_bits=14, voltage_range=5, use_twos_comp=False)
dac_data_offset = to_voltage(dac_offset, num_bits=14, voltage_range=5, use_twos_comp=False)
dac_data_v = dac_data_v - dac_data_offset

dac_data_scale = 1/10
lns1 = ax[1].plot(t_dacs*1e3, 1e3*(dac_data_v)*dac_data_scale, 'k', marker='.', label='DAC')
lns2 = ax[1].plot(t_ads*1e3, 1e3*ads_data/(1 + 2.152/3.01), 'm', linestyle='-.', marker='o', label='$V_{P1}$')
ax[1].set_xlim([4.78, 4.90])
ax[1].set_xlabel('t [ms]')
ax[1].set_ylabel('V [mV]')
ax[1].set_ylim([-60, 60])
ax2 = ax[1].twinx()
rf = 100e3 
diff_buf = 499/(1500+120)
lns3 = ax2.plot(t*1e3, -1e6*adc_data_v[0]/diff_buf/rf, 'r', linestyle='--', marker='*', label='$I_m$')
ax2.set_ylabel('$I [\mu$A]')
ax2.yaxis.label.set_color('red') 
ax2.set_ylim([-2,80])

print('Check value of current ---------------------')
Qint = 70e-6*0.5*70e-6 # estimate with a triangle
Qint_calc = 33e-9*70e-3 # C*V = Q 
print(f'Integrated charge: {Qint}, calculated charge: {Qint_calc}')


lns = lns1+lns2+lns3
labs = [l.get_label() for l in lns]
ax[1].legend(lns, labs, loc=5)
ax[1].grid(True)

my_savefig(fig, 'adc_vm_demo')