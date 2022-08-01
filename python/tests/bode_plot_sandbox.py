"""
This code sweeps frequency of a sine wave input to filters so that
a bode plot can be extracted from the .h5 files. 
Works in a mode with two DDR input buffers and two DDR output buffers. 

Data loaded into DDR for playback (port 1):
* AD5453 DAC and DAC80508 

Data buffered into and then read from DDR (port 2):
 * AD7961 @ 5 MSPS
 * output data to DAC AD5453 (allows for filter tests) @ 2.5 MSPS
 * ADS8686 data @ 1 MSPS
 * Timestamp (clock at 200 MHz)

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
Ian Delgadillo Bonequi, delg5279@stthomas.edu
"""

import os
import sys
import logging
from pyripherals.core import FPGA, Endpoint
from pyripherals.peripherals.DDR3 import DDR3
from pyripherals.utils import from_voltage, create_filter_coefficients
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# The boards.py file is located in the covg_fpga folder so we need to find that folder. If it is not above the current directory, the program fails.
covg_fpga_path = os.getcwd()
for i in range(15):
    if os.path.basename(covg_fpga_path) == "covg_fpga":
        boards_path = os.path.join(covg_fpga_path, "python")
        break
    else:
        # If we aren't in covg_fpga, move up a folder and check again
        covg_fpga_path = os.path.dirname(covg_fpga_path)
sys.path.append(boards_path)


from boards import Daq, Clamp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from analysis.adc_data import read_h5
from analysis.utils import calc_fft


# constants 
FS = 5e6  # sampling frequency 
dac80508_offset = 0x8000


eps = Endpoint.endpoints_from_defines

data_dir_base = covg_fpga_path
if sys.platform == "linux" or sys.platform == "linux2":
    print('Linux directory not configured... Error')
    pass
elif sys.platform == "darwin":
    print('MAC directory not configured... Error')
    pass
elif sys.platform == "win32":
    data_dir_covg = os.path.join(data_dir_base, 'covg/data/clamp/{}{:02d}{:02d}')

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


pwr_setup = "3dual"
dc_num = 0  # the Daughter-card channel under test. Order on board from L to R: 1,0,2,3

# -------- power supplies -----------
dc_pwr, dc_pwr2 = open_rigol_supply(setup=pwr_setup)
if pwr_setup == "3dual":
    atexit.register(pwr_off, [dc_pwr])
else:
    atexit.register(pwr_off, [dc_pwr, dc_pwr2])
config_supply(dc_pwr, dc_pwr2, setup=pwr_setup, neg=15)

# turn on the 7V
dc_pwr.set("out_state", "ON", configs={"chan": 1})

if pwr_setup != "3dual":
    # turn on the +/-16.5 V input
    for ch in [1, 2]:
        dc_pwr2.set("out_state", "ON", configs={"chan": ch})
elif pwr_setup == "3dual":
    # turn on the +/-16.5 V input
    for ch in [2, 3]:
        dc_pwr.set("out_state", "ON", configs={"chan": ch})

# ------ oscilloscope -----------------
# osc = open_by_name("msox_scope")

# --------  function generator  --------
fg_freq = 10e3
fg_v = 2
fg = open_by_name("new_function_gen")
fg.set("load", "INF")
fg.set("offset", 2)
fg.set("v", fg_v)
fg.set("freq", fg_freq)
fg.set("output", "ON")

atexit.register(fg.set, "output", "OFF")

# Initialize FPGA
f = FPGA()
f.init_device()
sleep(2)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)
ad7961s = daq.ADC
ads = daq.ADC_gp # ADS8686
ad7961s[0].reset_wire(1)

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

gpio = Daq.GPIO(f)
gpio.fpga.debug = True
# configure the SPI debug MUXs
gpio.spi_debug("dfast1")
gpio.ads_misc("sdoa")  # do not care for this experiment

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
# TODO: could skip Clamp board setup ... but it is another source of ADC data 
clamp = {}
for dc_num in [0]:
    clamp[dc_num] = Clamp(f, dc_num=dc_num)
    clamp[dc_num].init_board()

    # configure the clamp board, settings default to None so that a setting that is not
    # included is masked and stays the same
    # TODO: configure_clamp errors out if not connected

    log_info, config_dict = clamp[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="drive_CAL2",
        CCOMP=47,
        RF1=2.1,  # feedback circuit
        ADG_RES=100,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=0,
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )

# --------  Initialize fast ADCs  --------
for chan in [0,1,2,3]:
    ad7961s[chan].power_up_adc()  # standard sampling

time.sleep(0.1)
ad7961s[0].reset_wire(0)
time.sleep(1)

# configure I/O expanders 
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

filter_coeff_generated = create_filter_coefficients(fc=500e3, output_scale=2**13)

for i in [0]:
        daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
        daq.DAC[i].set_spi_sclk_divide()
        daq.DAC[i].filter_select(operation="set")
        daq.DAC[i].write(int(0))
        daq.DAC[i].set_data_mux("DDR")
        daq.DAC[i].set_data_mux("DDR", filter_data=True)
        daq.DAC[i].filter_sum("clear")
        daq.DAC[i].filter_downsample("clear")
        daq.DAC[i].change_filter_coeff(target="generated", value=filter_coeff_generated)
        daq.DAC[i].write_filter_coeffs()
        daq.set_dac_gain(0, 500)  # 500 mV full-scale

# -------- configure the ADS8686
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(5)
ads.set_lpf(376)
# 4B - clear sine wave set by the Slow DAC
codes = ads.setup_sequencer(chan_list=[('7', '3')])
ads.write_reg_bridge(clk_div=200) # 1 MSPS update rate. Write register for SPI configuration reg. But update rate is controlled by top-level timer
ads.set_fpga_mode()


# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x8)
    daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
    daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
    daq.DAC_gp[dac_gp_ch].set_gain(gain=1, outputs=[4], divide_reference=False)
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

ddr = DDR3(f, data_version='TIMESTAMPS')

def ddr_write_setup():
    ddr.set_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()

def ddr_write_finish():
     # reenable both DACs
    ddr.set_adc_dac_simultaneous()  # enable DAC playback and ADC writing to DDR

start_exp = 2
end_exp = 6
Frequencies = np.logspace(start_exp,end_exp,5)
FAST_DAC_FREQ = np.array([])

for i in range(len(Frequencies)-1):
    for j in range(2,20):
        FAST_DAC_FREQ = np.append(FAST_DAC_FREQ, Frequencies[i]*j*0.5)

FAST_DAC_FREQ = np.append(FAST_DAC_FREQ, 10**end_exp)
print(FAST_DAC_FREQ)

for freq in range(len(FAST_DAC_FREQ)):
    for i in range(7):
        ddr.data_arrays[i], fdac_freq = ddr.make_sine_wave(0x1fff, FAST_DAC_FREQ[freq],
                                            offset=0x2000)

    ddr_write_setup()
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr_write_finish()

    CHAN_UNDER_TEST = 0
    output = pd.DataFrame()
    data = {}
    file_name = 'test' + str(int(FAST_DAC_FREQ[freq])) + 'Hz'
    data['filename'] = file_name
    output = output.append(data, ignore_index=True)

    print(output.head())
    output.to_csv(os.path.join(data_dir, file_name + '.csv'))
    idx = 0

    # saves data to a file; returns to teh workspace the deswizzled DDR data of the last repeat
    chan_data_one_repeat = ddr.save_data(r'..\..\Matlab\data_analysis\BodePlotData', file_name.format(idx) + '.h5', num_repeats = 8,
                            blk_multiples=40) # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(r'..\..\Matlab\data_analysis\BodePlotData', file_name=file_name.format(idx) + '.h5', chan_list=np.arange(8))

    # Long data sequence -- entire file 
    adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data)

    # Shorter data sequence, just one of the repeats
    # adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data_one_repeat)

    t = np.arange(0,len(adc_data[0]))*1/FS

    crop_start = 0 # placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
    print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

    # DACs 
    t_dacs = t[crop_start::2]  # fast DACs are saved every other 5 MSPS tick
    #for dac_ch in range(4):
    for dac_ch in [0]:
        y = dac_data[dac_ch][crop_start:]
        print(f'Min {np.min(y[2:])}, Max {np.max(y)}') # skip the first 2 readings which are 0