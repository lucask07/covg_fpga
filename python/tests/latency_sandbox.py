"""
This code uses input on ADC daughtercard 3 from a function generator (square wave)
routed to fast DAC chan0 (CC on daughtercard 0) to measure latency from ADC - DAC 
on the oscilloscope 

Lucas Koerner, koerner.lucas@stthomas.edu
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
    data_dir_covg = os.path.join(data_dir_base, 'covg/data/latency/{}{:02d}{:02d}')

today = datetime.datetime.today()
data_dir = data_dir_covg.format(
    today.year, today.month, today.day
)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

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
fg.set("function", "SQU")

atexit.register(fg.set, "output", "OFF")

# ------ oscilloscope -----------------
osc = open_by_name("msox_scope")
osc.set("chan_label", '"P2"', configs={"chan": 1})
osc.set("chan_label", '"ADC"', configs={"chan": 3})
osc.set("chan_label", '"DAC"', configs={"chan": 4}) # label must be in "" for the scope to accept
osc.comm_handle.write(':DISP:LAB 1')  # turn on the labels
osc.set('chan_display', 0, configs={'chan': 1})
osc.set('chan_display', 0, configs={'chan': 2})

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

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
# TODO: could skip Clamp board setup ... but it is another source of ADC data 
clamp = {}
for dc_num in [0,1]:
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

filter_onoff = 'clear'  
# filter_onoff = 'set'
filter_status = 'passthru' # 'generator'
filter_status = 'generator' # 'generator'

for i in [0]:
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation=filter_onoff)
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("ad7961_ch3")
    daq.DAC[i].set_data_mux("ad7961_ch3", filter_data=True)
    daq.DAC[i].filter_sum("clear")
    daq.DAC[i].filter_downsample("clear")
    
    if filter_status == 'passthru':
        daq.DAC[i].change_filter_coeff(target="passthru")
    else:
        daq.DAC[i].change_filter_coeff(target="generated", value=filter_coeff_generated)

    daq.DAC[i].write_filter_coeffs()

for i in range(6):
    daq.set_dac_gain(i, 500)  # 500 mV full-scale

# -------- configure the ADS8686
ads_voltage_range = 5
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(ads_voltage_range)
ads.set_lpf(376)
ads_sequencer_setup = [('1', '0')]

codes = ads.setup_sequencer(chan_list=ads_sequencer_setup)
ads.write_reg_bridge(clk_div=200) # 1 MSPS update rate. Write register for SPI configuration reg. But update rate is controlled by top-level timer
ads.set_fpga_mode()

# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_spi_sclk_divide(0x2)
    daq.DAC_gp[dac_gp_ch].set_ctrl_reg(0x3218)
    daq.DAC_gp[dac_gp_ch].set_config_bin(0x00)
    daq.DAC_gp[dac_gp_ch].set_data_mux('host')
    # daq.DAC_gp[dac_gp_ch].set_gain(gain=1, outputs=[4], divide_reference=False)
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

daq.set_isel(port=1, channels=None)
daq.set_isel(port=2, channels=None)

ad7961s[0].reset_trig()

# ---- Configure DDR data 
ddr = DDR3(f, data_version='TIMESTAMPS')

SCOPE_SCREENSHOT = True
file_name = 'latency_{}_{}'

if SCOPE_SCREENSHOT:
    time.sleep(10)
    # osc.set('single_acq') - average waveforms so don't use single
    time.sleep(0.10)
    # save a PNG screen-shot to host computer -- would like to check for a trigger first but osc.get('is_running') doesn't seem to work
    osc.set('stop_acq') # in case the trigger didn't work
    t = osc.save_display_data(os.path.join(data_dir, file_name.format(filter_onoff, filter_status)))
    osc.set('run_acq')
