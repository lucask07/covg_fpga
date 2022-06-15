"""This script attempts to replicate Figure 4 on the biophysical poster. This
consists of measuring the membrane current (Im) with the AD7961 after
supplying a step voltage of 0-50mV by the AD5453. This is repeated for
feedback resistors of 10K, 33K, 100K, 332K, and 3000K. The membrane current
(Im) is graphed against time with all of these responses together.

Biophysical poster: https://uofstthomasmn.sharepoint.com/:b:/r/sites/COVGsummer2022/Shared%20Documents/biophysical_2022_poster_covg_v1.pdf?csf=1&web=1&e=gbUPQi

June 2022

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

from analysis.clamp_data import adjust_step2
from analysis.adc_data import read_h5
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from interfaces.utils import to_voltage, from_voltage
from interfaces.interfaces import (
    FPGA,
    Endpoint,
    DDR3,
)
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from interfaces.boards import Daq, Clamp


def ddr_write_setup(dc_num):
    ddr.set_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()
    ad7961s[dc_num].reset_trig()  # TODO: what does this do?


def ddr_write_finish():
    # reenable both DACs
    ddr.set_adc_dac_simultaneous()  # enable DAC playback and ADC writing to DDR


def get_cc_optimize(nums):

    data_dir_base = os.path.expanduser('~')
    data_dir_covg = os.path.join(
        data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')
    data_dir = data_dir_covg.format(2022, 1, 19)

    #for nums in ([20,21], [30,31], [14,15], [40,41]):
    with open(os.path.join(data_dir, 'basin_hop_cc_nums{}.pickle'.format(nums[0])), 'rb') as fp:
        out = pkl.load(fp)
    return out


def set_cmd_cc(dc_num, cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None):

    dac_offset = 0x2000
    cmd_ch = dc_num * 2 + 1
    cc_ch = dc_num * 2

    ddr.data_arrays[cmd_ch] = ddr.make_step(
        low=dac_offset - int(cmd_val), high=dac_offset + int(cmd_val), length=step_len)  # 1.6 ms between edges

    # create the cc using multiple methods
    if cc_pickle_num is not None:
        cc_impulse_scale = -2600/7424
        out = get_cc_optimize(cc_pickle_num)
        cc_wave = adjust_step2(
            out['x'], ddr.data_arrays[cmd_ch].astype(np.int32) - dac_offset)
        cc_wave = cc_wave * cc_impulse_scale
        cc_wave = cc_wave + dac_offset
        if cc_delay != 0:
            # 2.5e6 is the sampling rate
            cc_wave = delayseq_interp(cc_wave, cc_delay, 2.5e6)
        ddr.data_arrays[cc_ch] = cc_wave.astype(np.uint16)

    elif cc_val is None:  # get the cc signal from scaling the cmd signal
        if fc is not None:
            ddr.data_arrays[cc_ch] = butter_lowpass_filter(
                ddr.data_arrays[cmd_ch] - dac_offset, cutoff=fc, fs=2.5e6, order=1)*cc_scale + dac_offset
        else:
            ddr.data_arrays[cc_ch] = (
                ddr.data_arrays[cmd_ch] - dac_offset)*cc_scale + dac_offset
        if cc_delay != 0:
            ddr.data_arrays[cc_ch] = delayseq_interp(
                ddr.data_arrays[cc_ch], cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    else:  # needed so that the cmd signal can be zero with a non-zero cc signal
        ddr.data_arrays[cc_ch] = ddr.make_step(low=dac_offset - int(cc_val),
                                               high=dac_offset + int(cc_val),
                                               length=step_len)  # 1.6 ms between edges
        if fc is not None:
            ddr.data_arrays[cc_ch] = butter_lowpass_filter(
                ddr.data_arrays[cc_ch], cutoff=fc, fs=2.5e6, order=1)
        if cc_delay != 0:
            ddr.data_arrays[cc_ch] = delayseq_interp(
                ddr.data_arrays[cc_ch], cc_delay, 2.5e6)  # 2.5e6 is the sampling rate

    # write channels to the DDR
    ddr_write_setup(dc_num=dc_num)
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr_write_finish()

FS = 5e6
SAMPLE_PERIOD = 1/FS
DC_NUMS = [0, 1]  # list of the Daughter-card channels under test. Order on board from L to R: 1,0,2,3

feedback_resistors = [2.1]                  # list of RF1 values; use None to get all options
capacitors = [47, 200, 1000, 4700]          # list of CCOMP values; use None to get all options

eps = Endpoint.endpoints_from_defines
pwr_setup = "3dual"

# TODO: at data directories like this to a config file
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
ddr = DDR3(f, data_version='TIMESTAMPS')
ad7961s = daq.ADC
for dc_num in DC_NUMS:
    ad7961s[dc_num].reset_wire(1)

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

# configure the SPI debug MUXs
gpio = Daq.GPIO(f)
gpio.spi_debug("dfast1")
gpio.ads_misc("sdoa")  # do not care for this experiment

# ------- COPIED FROM clamp_sandbox.py FOR CLAMP V1 BUG FIX -------
# # configure clamp board Utility pin to be the offset voltage for the feedback
# # at this point the slow DA Ccan be set by the host
# for i in range(2):
#     # Reset the Wishbone controller and SPI core
#     # daq.DAC_gp[i].reset_master()
#     daq.DAC_gp[i].set_ctrl_reg(daq.DAC_gp[i].master_config)
#     daq.DAC_gp[i].set_spi_sclk_divide()
#     daq.DAC_gp[i].filter_select(operation="clear")
#     daq.DAC_gp[i].set_data_mux("host")
#     # daq.DAC_gp[i].set_gain(gain=1, divide_reference=False) #TODO: check default values
#     daq.DAC_gp[i].set_config_bin(0x00)
#     print('Outputs powered on')

# #DAC1_BP_OUT4, J11 pin #11 -- connected to utility pin to daughter card -- offset voltage
# # clamp board TP1
# # 0.6125 V, which approx centers P1 and P2
# daq.DAC_gp[0].write_voltage(1.457, 4)
# #DAC1_BP_OUT5, J11 pin #13 -- connected to utility pin to daughter card -- offset voltage
# # clamp board TP1
# # 0.6125 V, which approx centers P1 and P2 -- for DC #2
# daq.DAC_gp[0].write_voltage(1.457, 5)
# # for the 3.3 V "supply voltage" to the op-amp
# daq.DAC_gp[1].write_voltage(2.36, 7)
# ------- END COPIED FROM clamp_sandbox.py FOR CLAMP V1 BUG FIX -------

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamps = [None] * 4
for dc_num in DC_NUMS:
    clamp = Clamp(f, dc_num=dc_num)
    print(f'Clamp {dc_num} Init'.center(35, '-'))
    clamp.init_board()
    clamp.DAC.write(data=from_voltage(voltage=0.9940/1.6662, num_bits=10, voltage_range=5, with_negatives=False))
    clamps[dc_num] = clamp

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling

for dc_num in DC_NUMS:
    ad7961s[dc_num].reset_wire(0)
time.sleep(1)

daq.TCA[0].configure_pins([0, 0])
daq.TCA[1].configure_pins([0, 0])

# fast DAC channels setup
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

# saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                     blk_multiples=40)  # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(
    idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file
adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data)
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

# Time in seconds
t = np.arange(0, len(chan_data[0]))*1/FS

for dc_num in DC_NUMS:
    clamp = clamps[dc_num]

    # Try with different capacitors
    if feedback_resistors is None:
        feedback_resistors = [x for x in clamp.configs['RF1_dict'].keys() if type(x) == int or type(x) == float] # RF1 Resistor values in kilo-ohms for Offset Adjust amplifier
        feedback_resistors.sort()
    if capacitors is None:
        capacitors = [x for x in clamp.configs['CCOMP_dict'] if type(x) == int or type(x) == np.int32]  # CCOMP Capacitor values in pF
        capacitors.sort()
    voltage_data = dict(clamp.configs['ADG_RES_dict'])    # Rf Resistor values in kilo-ohms for Figure 4 graph
    for key in voltage_data:
        voltage_data[key] = []  # Lists to hold voltage data at each resistor value

    for fb_res in feedback_resistors:
        rows = ceil(len(capacitors)**(1/2))
        fig, axes = plt.subplots(rows, rows)
        fig.suptitle(f'DC{dc_num} Current response to CMD step voltage (RF1={fb_res})')
        for i in range(len(capacitors)):
            cap = capacitors[i]
            current_ax = axes[i // rows][i % rows]
            current_ax.set_title(f'CCOMP={cap}pF')
            current_ax.set_xlabel('Time (\N{GREEK SMALL LETTER MU}s)')
            current_ax.set_ylabel('Current (\N{GREEK SMALL LETTER MU}A)')

            # Try with 5 different resistors
            for res in [x for x in voltage_data.keys() if type(x) == int]:
                # Choose resistor; setup
                log_info, config_dict = clamp.configure_clamp(
                    ADC_SEL="CAL_SIG1",
                    DAC_SEL="drive_CAL2",
                    CCOMP=cap,
                    RF1=fb_res,  # feedback circuit
                    ADG_RES=res,
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

                # Set CMD and CC signals
                set_cmd_cc(dc_num=dc_num, cmd_val=0x400, cc_scale=0, cc_delay=0, fc=None,
                        step_len=16384, cc_val=None, cc_pickle_num=None)

                # Get data
                # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
                chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                                    blk_multiples=40)  # blk multiples multiple of 10

                # to get the deswizzled data of all repeats need to read the file
                _, chan_data = read_h5(data_dir, file_name=file_name.format(
                    idx) + '.h5', chan_list=np.arange(8))

                # Store voltage in list; plot
                voltage_data[res] = to_voltage(chan_data[dc_num], num_bits=16, voltage_range=10, use_twos_comp=True)

                # Plot current (uA) against time (us) -> uA because resistor values are in kilo-ohms, we multiply current by 1e3
                current_ax.plot(t * 1e6, [(v / res) * 1e3 for v in voltage_data[res]], label=str(res) + 'k\N{GREEK CAPITAL LETTER OMEGA}')
            # Zoom in on the data
            current_ax.set_xlim(6550, 6800)
            current_ax.set_ylim(-10, 40)
            
            # Set up the legend after the first subplot so there are no repeat labels from following subplots
            if i == 0:
                fig.legend(loc='lower right')
