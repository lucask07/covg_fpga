"""
This code tests DDR reading and writing. 
Works in a mode with two DDR input buffers and two DDR output buffers. 

Does not require specific hardware (though we reference "hardware" to create the data buffers)
Checks timestamps, constant values, data buffered in and then buffered out 

Data loaded into DDR for playback (port 1):
Data buffered into and then read from DDR (port 2):

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

from interfaces.boards import Daq
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
import logging
from interfaces.interfaces import (
    FPGA,
    AD5453,
    Endpoint,
    DAC80508,
    AD7961,
    disp_device,
    DDR3,
    advance_endpoints_bynum,
    TCA9555,
)
from interfaces.boards import Daq, Clamp
from interfaces.utils import twos_comp, from_voltage
import os
import sys
from time import sleep
import datetime
import time
import atexit
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
import h5py
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from analysis.adc_data import read_plot, read_h5, peak_area, get_impulse, im_conv, idx_timerange
from analysis.utils import calc_fft

# constants 
FS = 5e6  # sampling frequency 
dac80508_offset = 0x8000

# The interfaces.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == "covg_fpga":
        interfaces_path = os.path.join(covg_fpga_path, "python")
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(interfaces_path)

eps = Endpoint.endpoints_from_defines

data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    print('Linux directory not configured... Error')
    pass
elif sys.platform == "darwin":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')
    pass
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')

today = datetime.datetime.today()
data_dir = data_dir_covg.format(
    today.year, today.month, today.day
)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# alternative for Python<3.9
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler("AD7961_test.log", "w", "utf-8")
root_logger.addHandler(handler)


# Initialize FPGA
f = FPGA(
    bitfile=os.path.join(
        covg_fpga_path,
        "fpga_XEM7310",
        "fpga_XEM7310.runs",
        "impl_1",
        "top_level_module.bit",
    )
)
f.init_device()
sleep(2)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)
ad7961s = daq.ADC
ad7961s[0].reset_wire(1)


# --------  Initialize fast ADCs  --------
for chan in [0,1,2,3]:
    ad7961s[chan].power_up_adc()  # standard sampling

ad7961s[0].reset_wire(0)
time.sleep(1)

for chan in [0,1,2,3]:
    ad7961s[chan].reset_fifo()

# fast DACs
for i in [0,1,2,3,4,5]:
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="set")
    daq.DAC[i].set_data_mux("DDR")
    daq.DAC[i].write_filter_coeffs()

# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x8)
    daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
    daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

ddr = DDR3(f, data_version='TIMESTAMPS')

def ddr_write_setup():
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()
    ad7961s[0].reset_trig()

def ddr_write_finish():
     # reenable both DACs
    ddr.set_dac_read()  # enable DAC playback and ADC reading
    ddr.set_adc_write()

FAST_DAC_FREQ = 7e3
for i in range(7):
    ddr.data_arrays[i], fdac_freq = ddr.make_sine_wave(0x800, FAST_DAC_FREQ,
                                        offset=0x1000)

# ---------- configure "slow" DAC DAC80508
sdac_amp_volt = 1
target_freq_sdac = 12000.0
sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

# Data for the 2 DAC80508 "Slow DACs"
sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq_sdac, offset=dac80508_offset)

# Specify output channel for DAC80508
sdac_1_out_chan = 5
sdac_2_out_chan = 5

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

ddr_write_setup()
g_buf = ddr.write_channels()
ddr_write_finish()

REPEAT = True
if REPEAT:  # to repeat data capture without rewriting the DAC data
    ddr.clear_adc_read()
    ddr.clear_adc_write()

    ddr.reset_fifo(name='ADC_IN')
    ddr.reset_fifo(name='ADC_TRANSFER')
    ddr.reset_mig_interface()

    ddr.set_adc_write()
    time.sleep(0.01)

file_name = 'test'
idx = 0
# saves data to a file; returns to teh workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats = 8,
                          blk_multiples=40) # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file 
adc_data, timestamp, dac_data, ads = ddr.data_to_names(chan_data)

# Shorter data sequence, just one of the repeats
# adc_data, timestamp, read_check, dac_data, ads = ddr.data_to_names(chan_data_one_repeat)

crop_start = 0 # placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

# DACs 
for dac_ch in range(4):
    fig,ax=plt.subplots()
    y = dac_data[dac_ch][crop_start:]
    lbl = f'Ch{dac_ch}'
    ax.plot(y, marker = '+', label = lbl)
    ax.legend()
    ax.set_title('Fast DAC data')
    ax.set_xlabel('Sample #')
