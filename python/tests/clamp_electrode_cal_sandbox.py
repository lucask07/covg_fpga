"""This script demonstrates measurement of the electrode and membrane capacitance
using the calibration functionality (relay) switches of the clamp board 
and the ADC cal output to the ADS8686.

Biophysical poster: https://uofstthomasmn.sharepoint.com/:b:/r/sites/COVGsummer2022/Shared%20Documents/biophysical_2022_poster_covg_v1.pdf?csf=1&web=1&e=gbUPQi

Abe Stroschein, ajstroschein@stthomas.edu
Lucas Koerner, koerner.lucas@stthomas.edu
"""

from math import ceil
import os
import sys
from time import sleep
import datetime
import time
import atexit
from instrbuilder.instrument_opening import open_by_name
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl
import copy
from interfaces.utils import to_voltage, from_voltage
from interfaces.interfaces import FPGA, Endpoint
from interfaces.peripherals.DDR3 import DDR3
from interfaces.peripherals.DAC80508 import DAC80508
from interfaces.peripherals.ADS8686 import ADS8686

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


from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from boards import Daq, Clamp


def ddr_write_setup():
    ddr.set_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.clear_adc_read()    # Stop putting data in outgoing FIFO for Pipe read
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()


def ddr_repeat_setup():
    """Setup for reading new data without writing to the DDR again."""

    # stop access to the FIFOs so that after reset of the FIFO(s) no new data is added/extracted
    ddr.clear_adc_read()
    ddr.clear_adc_write()
    ddr.clear_dac_read()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()  # self.fpga.send_trig(self.endpoints['UI_RESET'])
    # note that the MIG interface addresses are driven by the FIFOs so will idle
    # until the FIFOs are reenable with ddr_write_finish()
    ddr_write_finish()
    time.sleep(0.01)


def ddr_write_finish():
    # reenable both DACs
    ddr.set_adc_dac_simultaneous()  # enable DAC playback and ADC writing to DDR


def make_chirp():
    """Return the DAC signal for calibration excitation .
    
    Parameters
    ----------
    
    Returns
    -------
    np.ndarray: the cal signal data.
    """

    signal = ddr.make_step(low=dac_offset - int(cc_val),
                                           high=dac_offset + int(cc_val),
                                           length=step_len)  # 1.6 ms between edges

    return signal


def ddr_write_dacs(ddr):
    """Write the DAC data to DDR.

    Returns
    -------
    None
    """

    # write channels to the DDR
    ddr_write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr_write_finish()

FS = 5e6
SAMPLE_PERIOD = 1/FS
DC_NUMS = [0, 1, 2, 3]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3

feedback_resistors = [2.1]                  # list of RF1 values; use None to get all options
capacitors = [47, 200, 1000, 4700]          # list of CCOMP values; use None to get all options

eps = Endpoint.endpoints_from_defines
pwr_setup = "3dual"

# TODO: add data directories like this to a config file
data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    pass
elif sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp_test/{}{:02d}{:02d}"
elif sys.platform == "win32":
    if os.path.exists('C:/Users/ajstr/OneDrive - University of St. Thomas/Research Internship/clamp_step_response_data'):
        data_dir_covg = 'C:/Users/ajstr/OneDrive - University of St. Thomas/Research Internship/clamp_step_response_data/{}{:02d}{:02d}'
    else:
        data_dir_covg = os.path.join(data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')

today = datetime.datetime.today()
data_dir = data_dir_covg.format(
    today.year, today.month, today.day
)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


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


# Initialize FPGA
f = FPGA()
f.init_device()
sleep(2)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)
ddr = DDR3(f, data_version='TIMESTAMPS')
ad7961s = daq.ADC
ad7961s[0].reset_wire(1)    # Only actually one WIRE_RESET for all AD7961s

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamps = [None] * 4
for dc_num in DC_NUMS:
    clamp = Clamp(f, dc_num=dc_num)
    print(f'Clamp {dc_num} Init'.center(35, '-'))
    clamp.init_board()
    clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
    clamps[dc_num] = clamp

# ------------- configure ADS8686
ads = daq.ADC_gp # ADS8686
ads.hw_reset(val=False)
ads.set_host_mode()
ads.setup()
ads.set_range(5)
ads.set_lpf(376)

ads_sequence = [('0', '0'), ('1', '1'), ('2','2')]
codes = ads.setup_sequencer(chan_list=ads_sequence)
ads.write_reg_bridge(clk_div=200) # 1 MSPS update rate. Write register for SPI configuration reg. Update rate is controlled by top-level timer
ads.set_fpga_mode()

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling
time.sleep(0.1)
ad7961s[0].reset_wire(0)    # Only actually one WIRE_RESET for all AD7961s
ad7961s[0].reset_trig() # this IS required because it resets the timing generator of the ADS8686. Make sure to configure the ADS8686 before this reset

# DAQ board I/O expanders for DAC gains and others 
daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channels setup -- for calibration these should be zeroed 
for i in range(6):
    daq.DAC[i].set_ctrl_reg(daq.DAC[i].master_config)
    daq.DAC[i].set_spi_sclk_divide()
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].write(int(0))
    daq.DAC[i].set_data_mux("DDR")
    daq.DAC[i].change_filter_coeff(target="passthru")
    daq.DAC[i].write_filter_coeffs()
    daq.set_dac_gain(i, 5)  # 5V to see easier on oscilloscope

# ------ Collect Data --------------
file_name = time.strftime("%Y%m%d-%H%M%S")
idx = 0

# --- Write to the DDR ---
# [0:13]    FDAC_1 [14:15] ADDR SDAC_1
# [16:29]   FDAC_2 [31:32] ADDR SDAC_1 and SDAC_2
# [32:45]   FDAC_3 [46:47] ADDR SDAC_2
# [48:61]   FDAC_4 [62:63] 0's
# [64:77]   FDAC_5 [78:79] 0's
# [80:93]   FDAC_6 [94:95] 0's
# [96:111]  SDAC_1
# [112:127] SDAC_2

sdac_1_out_chan = 0
sdac_2_out_chan = 0  # Do not care
fdac_amp_volt = 1
sdac_amp_volt = 1
target_freq = 1e3

# TODO: figure out what the voltage range should be for fdac, 3.3 is just a guess
fdac_amp_code = from_voltage(voltage=fdac_amp_volt, num_bits=14, voltage_range=3.3, with_negatives=False)
sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)

# Data for the 6 AD5453 "Fast DACs"
fdac_sine, fdac_freq = ddr.make_sine_wave(amplitude=0, frequency=target_freq)

# Data for the 2 DAC80508 "Slow DACs"
dac80508_offset = 0x8000
sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=1e3, offset=dac80508_offset)

# Clear channel bits
fdac_sine = np.bitwise_and(fdac_sine, 0x3fff)

# Load data into DDR
# Set channel bits
ddr.data_arrays[0] = np.bitwise_or(fdac_sine, (sdac_1_out_chan & 0b110) << 13)
ddr.data_arrays[1] = np.bitwise_or(fdac_sine, (sdac_1_out_chan & 0b001) << 14)
ddr.data_arrays[2] = np.bitwise_or(fdac_sine, (sdac_2_out_chan & 0b110) << 13)
ddr.data_arrays[3] = np.bitwise_or(fdac_sine, (sdac_2_out_chan & 0b001) << 14)
for i in range(2):
    ddr.data_arrays[i + 4] = fdac_sine
for i in range(2):
    ddr.data_arrays[i + 6] = sdac_sine

# configure all 4 daughtercards 
for dc_num in DC_NUMS:
    log_info, config_dict = clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="drive_CAL2",
        CCOMP=47,
        RF1=100,  # feedback circuit
        ADG_RES=2.1,  # TODO: Why is this 2.1 and not just 2?
        PClamp_CTRL=0, # keep open (not passive clamp)
        P1_E_CTRL=0, #open 
        P1_CAL_CTRL=1, #close for cal
        P2_E_CTRL=1, #open
        P2_CAL_CTRL=1, #close for cal
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )

# write channels to the DDR
ddr_write_setup()
# clear read, set write, etc. handled within write_channels
block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
ddr.reset_mig_interface()
ddr_write_finish()

for i in range(4):
    ddr_repeat_setup()

    # Get data
    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                        blk_multiples=40)  # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(
        idx) + '.h5', chan_list=np.arange(8))

    adc_data, timestamp, dac_data, ads_data, reading_error = ddr.data_to_names(chan_data)
    print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

len_sz = len(ads_sequence)
fix, ax = plt.subplots(len_sz,1)
for l in range(len_sz):
    ax[l].plot(ads_data['A'][l::len_sz])
