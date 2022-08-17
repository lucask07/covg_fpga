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
import pandas as pd
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3
# from pyripherals.utils import calc_impedance, from_voltage, to_voltage, read_h5
from pyripherals.utils import from_voltage, to_voltage, read_h5
import scipy
from scipy.signal.windows import hann
from scipy.fft import rfftfreq
from scipy.fft import rfft
from scipy import signal
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def calc_impedance(v_in, v_out, resistance):
    """Calculate the impedance of an unknown component.
    
    It is assumed the voltage source is connect in series with both the resistor and the unknown component.
    Arguments
    ---------
    v_in : list(int or float)
        The sinusoidal voltage source in the circuit.
    v_out : list(int or float)
        The output voltage across the unknown component.
    resistance : int or float
        The resistance of the resistor in the circuit in Ohms.
    Returns
    -------
    numpy.ndarray : the array of impedances calculated.
    """

    current = np.subtract(v_in, v_out) / resistance

    window = hann(len(v_out), sym=False)
    w_v_out = window * v_out
    w_current = window * current

    impedance_calc = np.divide(rfft(w_v_out), rfft(w_current))
    
    return impedance_calc



# USER SET CONSTANTS
RESISTANCE = 9.831e3  # Resistance of the known resistance in Ohms
FREQUENCY = 10000     # Desired frequency of the output sine wave in Hertz
AMPLITUDE = 0.5     # Desired amplitude of the output sine wave in Volts
BITFILE_PATH = 'default'    # Path to top_level_module.bit. Leave as default if configured in config.yaml
DATA_DIR = os.path.join(os.path.expanduser('~'), '.pyripherals/data/{}{:02d}{:02d}')  # Folder where data will be saved
PLOT = False        # True to create a graph of ADS8686 readings, False otherwise

# Other constants
DAC80508_OFFSET = 0x8000                # DAC80508 voltage offset code for keeping sine wave positive
ADS8686_UPDATE_PERIOD = 1e-6            # Time (seconds) between ADS8686 voltage reads
DAC80508_OUT_CHAN = 7                   # DAC80508 sine wave output channel
ADS8686_A_CHAN = 7                      # ADS8686 input from side A reading DAC80508 output voltage
ADS8686_B_CHAN = 3                      # ADS8686 input from side B reading unknown impedance voltage

input_side = 'A'
output_side = 'B'

# configure Matplotlib
matplotlib.use("Qt5agg")  # or "Qt5agg" depending on you version of Qt
plt.ion()

#data_dir = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/pyripherals/data/20220722/"
data_dir = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/pyripherals/data/202207{}/"
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


# file_name = 'impedance_analyzer_500mV_64repeats_15khZ_1nF'
# file_name = 'impedance_analyzer_500mV_64repeats_3khZ'
# file_name = 'impedance_analyzer_15k_900pF_v2'  # this is actually captured at 20 kHz
file_name_base = 'impedance_analyzer_{}k_900pF'  # this is actually captured at 20 kHz

results = {}
for n in ['f', 'calc_real', 'calc_imag', 'real', 'imag', 'real_err', 'imag_err']:
    results[n] = np.array([])

# ('25', 10000, True), ('25', 15000, True), ('25', 20000, True),
for data_dir_day, FREQUENCY, FIX_PHASE_SHIFT in [
                                             ('26', 10000, False), ('26', 15000, False), ('26', 20000, False)]:

    data_dir = data_dir.format(data_dir_day)
    file_name = file_name_base.format(FREQUENCY//1000)

    r1 = 9.831e3
    r2 = 9.866e3 
    c = 0.8845e-9
    # c = 0.310e-6

    f = FPGA()
    f.init_device()
    ddr = DDR3(fpga=f, data_version='TIMESTAMPS')

    zp = r2 - 1j/(c*2*np.pi*FREQUENCY)
    print('-'*60)
    print(f'projected unknown impedance {zp} Ohms')
    print(f'Phasor Notation Impedance: {np.abs(zp)}\N{ANGLE}{np.angle(zp, deg=True)}\N{DEGREE SIGN}')
    
    results['calc_real'] = np.append(results['calc_real'], np.real(zp))
    results['calc_imag'] = np.append(results['calc_imag'], np.imag(zp))

    # Change gain and reference divider for DAC80508 to get maximum precision
    # Check (AMPLITUDE * 2) because we will shift all values up since DAC80508 cannot output negative values
    if (AMPLITUDE * 2) <= 1.25:
        gain = 1
        divide_reference = True
        voltage_range = 1.25
    elif (AMPLITUDE * 2) <= 2.5:
        # *2 and /2 is recommended instead of *1 and /1
        gain = 2
        divide_reference = True
        voltage_range = 2.5
    elif (AMPLITUDE * 2) <= 5:
        gain = 2
        divide_reference = False
        voltage_range = 5
    else:
        print(f'WARNING: cannot use AMPLITUDE {AMPLITUDE}V, limiting to maximum 2.5V')
    amplitude_code = from_voltage(voltage=AMPLITUDE, num_bits=16, voltage_range=voltage_range, with_negatives=False)
    v_in_code, actual_freq = ddr.make_sine_wave(amplitude=amplitude_code, frequency=FREQUENCY, offset=DAC80508_OFFSET, actual_frequency=True)


    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(
        0) + '.h5', chan_list=np.arange(8))
    # Long data sequence -- entire file
    adc_data, timestamp, dac_data, ads, ads_seq_cnt, read_errors = ddr.data_to_names(chan_data)

    data_stream = ads
    # We discard the first few points because we want the component to reach steady state.
    initial_cutoff = 5000
    v_in_code = data_stream[input_side][initial_cutoff:]
    v_out_code = data_stream[output_side][initial_cutoff:]


    # --- Calculate impedance across frequencies ---
    # Convert back to voltage
    v_in_voltage = to_voltage(data=np.array(v_in_code, dtype=int), num_bits=16, voltage_range=10, use_twos_comp=True)
    v_out_voltage = to_voltage(data=np.array(v_out_code, dtype=int), num_bits=16, voltage_range=10, use_twos_comp=True)

    if FIX_PHASE_SHIFT:
        v_in_voltage = v_in_voltage[1:]
        v_out_voltage = v_out_voltage[0:-1]

    impedance_arr = calc_impedance(v_in=v_in_voltage, v_out=v_out_voltage, resistance=RESISTANCE)

    # --- Set up x frequencies ---
    x_freq = rfftfreq(len(v_in_voltage), ADS8686_UPDATE_PERIOD)

    # --- Find nearest x frequency to input frequency ---
    distances_from_actual = [abs(x - actual_freq) for x in x_freq]
    desired_index = distances_from_actual.index(min(distances_from_actual))
    frequency_found = x_freq[desired_index]

    # --- Print impedance at that frequency ---
    z = impedance_arr[desired_index]
    print('Single Frequency FFT method -----------------')
    print(f'Impedance of {z} Ohms found at {frequency_found} Hz')
    print(f'Phasor Notation Impedance: {np.abs(z)}\N{ANGLE}{np.angle(z, deg=True)}\N{DEGREE SIGN}')

    plt.ion()
    fig, ax = plt.subplots()
    t = np.arange(0,len(v_in_voltage))*1e-6
    ax.plot(t*1e3, v_in_voltage, marker='o', color='k', label='$V_{in}$')
    ax.plot(t*1e3, v_out_voltage, marker='*', color='g', linestyle='--', label='$V_{mid}$')
    ax.set_ylabel('V')
    ax.set_xlabel('t [ms]')
    ax.set_xlim([3,3.2])
    ax.legend()

    # read in schematic and add to figure 
    schematic_file = '/Users/koer2434/My Drive/UST/research/covg/manuscripts/ians_eit_modification/impedance_circuit.png'
    arr_image = plt.imread(schematic_file, format='png')

    axins2 = inset_axes(ax, width="100%", height="100%", loc='upper left',
                       bbox_to_anchor=(0.5,1-0.45,.5,.4), bbox_transform=ax.transAxes)
    axins2.imshow(arr_image)
    axins2.set_xticks([])
    axins2.set_yticks([])

    my_savefig(fig, 'vin_vout_impedance_{}kHz'.format(FREQUENCY//1000))

    fig2, ax2 = plt.subplots(2,1)

    in_fft = rfft(v_in_voltage)
    ax2[0].semilogy(x_freq, np.abs(in_fft))
    ax2[0].semilogy(x_freq[desired_index], np.abs(in_fft)[desired_index], marker='o')

    ax2[1].plot(x_freq, np.angle(in_fft))
    ax2[1].plot(x_freq[desired_index], np.angle(in_fft)[desired_index], marker='o')

    print('-'*60)

    print(f'VIN: FFT Magnitude and phase of {np.abs(in_fft)[desired_index]}; {np.angle(in_fft)[desired_index]}')

    fig2, ax2 = plt.subplots(2,1)

    in_fft = rfft(v_out_voltage)
    ax2[0].semilogy(x_freq, np.abs(in_fft))
    ax2[0].semilogy(x_freq[desired_index], np.abs(in_fft)[desired_index], marker='o')

    ax2[1].plot(x_freq, np.angle(in_fft))
    ax2[1].plot(x_freq[desired_index], np.angle(in_fft)[desired_index], marker='o')

    print(f'VOUT: FFT Magnitude and phase of {np.abs(in_fft)[desired_index]}; {np.angle(in_fft)[desired_index]}')
    print('-'*60)

    # Using correlation to extract the phase difference gives a resolution limited to bin size 
    correlation = signal.correlate(v_in_voltage, v_out_voltage, mode="full")
    lags = signal.correlation_lags(v_in_voltage.size, v_out_voltage.size, mode="full")
    lag = lags[np.argmax(correlation)]

    def sinusoid_fit(t, A, w, p, c):
        return A * np.sin(w*t + p) + c

    def fit_sinusoid(v):
        PLT = False
        t = np.arange(0, len(v))*ADS8686_UPDATE_PERIOD
        mean_val = np.mean(v)
        amp = np.std(v)*np.sqrt(2)

        popt, pcov = scipy.optimize.curve_fit(sinusoid_fit, t, v, p0=[amp, FREQUENCY*2*np.pi, mean_val, 0])
        A, w, p, c = popt
        fitfunc = lambda t: A * np.sin(w*t + p) + c

        if PLT:
            plt.figure()
            plt.plot(t, v)
            plt.plot(t, sinusoid_fit(t,A,w,p,c), 'r')

        return A, w, p, c


    A1, w1, p1, c1 = fit_sinusoid( (v_in_voltage-v_out_voltage)/RESISTANCE)
    A2, w2, p2, c2 = fit_sinusoid(v_out_voltage)
    A3, w3, p3, c3 = fit_sinusoid(v_in_voltage)

    print(f'Sinusoid fit method -------------')
    imp_mag = A2/A1 
    imp_angle = p2 - p1 

    z2 = imp_mag*(np.cos(imp_angle) + 1j*np.sin(imp_angle)) 

    print(f'Impedance of {z2} Ohms')
    print(f'Phasor Notation Impedance: {np.abs(z2)}\N{ANGLE}{np.angle(z2, deg=True)}\N{DEGREE SIGN}')

    results['f'] = np.append(results['f'], FREQUENCY)
    results['real'] = np.append(results['real'], np.real(z2))
    results['imag'] = np.append(results['imag'], np.imag(z2))

    results['real_err'] = np.append(results['real_err'], (np.real(z2) - np.real(zp))/np.real(zp)*100)
    results['imag_err'] = np.append(results['imag_err'], (np.imag(z2) - np.imag(zp))/np.imag(zp)*100)

    print(f'Vin/Vout = {A3/A2}')
    print(f'Vin to Vout phase = {p3-p2} [rads] {(p3-p2)*360/(2*np.pi)}')

df = pd.DataFrame.from_dict(results)
df.to_csv(os.path.join(figure_dir, 'impedance_results.csv'))