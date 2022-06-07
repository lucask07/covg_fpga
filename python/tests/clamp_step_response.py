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

from analysis.clamp_data import adjust_step2, adjust_step, adjust_step_delay, adjust_step_scale
from analysis.adc_data import read_plot, read_h5, peak_area, get_impulse, im_conv, idx_timerange
from filters.filter_tools import butter_lowpass_filter, delayseq_interp
from interfaces.utils import to_voltage, from_voltage, twos_comp
from interfaces.interfaces import (
    FPGA,
    Endpoint,
    DDR3,
)
from instruments.power_supply import open_rigol_supply, pwr_off, config_supply
from interfaces.boards import Daq, Clamp


def ddr_write_setup():
    ddr.set_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()
    ad7961s[1].reset_trig()  # TODO: what does this do?


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


def set_cmd_cc(cmd_val=0x1d00, cc_scale=0.351, cc_delay=0, fc=4.8e3, step_len=8000,
               cc_val=None, cc_pickle_num=None):

    dac_offset = 0x2000
    cmd_ch = 3
    cc_ch = 2

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
    ddr_write_setup()
    # clear read, set write, etc. handled within write_channels
    block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
    ddr.reset_mig_interface()
    ddr_write_finish()

FS = 5e6
SAMPLE_PERIOD = 1/FS
DC_NUM = 1  # the Daughter-card channel under test. Order on board from L to R: 1,0,2,3
eps = Endpoint.endpoints_from_defines
pwr_setup = "3dual"


data_dir_base = os.path.expanduser('~')
if sys.platform == "linux" or sys.platform == "linux2":
    pass
elif sys.platform == "darwin":
    data_dir_covg = "/Users/koer2434/My Drive/UST/research/covg/fpga_and_measurements/daq_v2/data/clamp_test/{}{:02d}{:02d}"
elif sys.platform == "win32":
    data_dir_covg = os.path.join(
        data_dir_base, 'Documents/covg/data/clamp/{}{:02d}{:02d}')

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

# ------ oscilloscope -----------------
if 0:
    osc = open_by_name("msox_scope")
    osc.set("chan_label", '"P2"', configs={"chan": 1})
    osc.set("chan_label", '"CC"', configs={"chan": 3})
    # label must be in "" for the scope to accept
    osc.set("chan_label", '"Vm"', configs={"chan": 4})
    osc.comm_handle.write(':DISP:LAB 1')  # turn on the labels
    osc.set('chan_display', 0, configs={'chan': 2})


# Initialize FPGA
f = FPGA(
    bitfile=os.path.join(
        covg_fpga_path,
        "fpga_XEM7310",
        "fpga_XEM7310.runs",
        "impl_1",
        "top_level_module.bit",
    ), debug=False
)
f.init_device()
sleep(2)
f.send_trig(eps["GP"]["SYSTEM_RESET"])  # system reset

pwr = Daq.Power(f)
pwr.all_off()  # disable all power enables

daq = Daq(f)
ad7961s = daq.ADC
ad7961s[1].reset_wire(1)

# power supply turn on via FPGA enables
for name in ["1V8", "5V", "3V3"]:
    pwr.supply_on(name)
    sleep(0.05)

gpio = Daq.GPIO(f)
# configure the SPI debug MUXs
gpio.spi_debug("dfast1")
gpio.ads_misc("sdoa")  # do not care for this experiment

# instantiate the Clamp board providing a daughter card number (from 0 to 3)
clamp = Clamp(f, dc_num=DC_NUM)
clamp.init_board()

# configure the clamp board, settings default to None so that a setting that is not
# included is masked and stays the same
log_info, config_dict = clamp.configure_clamp(
    ADC_SEL="CAL_SIG1",
    DAC_SEL="drive_CAL2",
    CCOMP=47,
    RF1=2.2,  # feedback circuit
    # RF1=2.1,  # feedback circuit
    ADG_RES=10,
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

# --------  Enable fast ADCs  --------
for chan in [0, 1, 2, 3]:
    ad7961s[chan].power_up_adc()  # standard sampling

ad7961s[1].reset_wire(0)
time.sleep(1)

# TODO: is this needed?
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
    daq.set_dac_gain(i, 5)  # 500 mV full-scale

# # TODO: do we need this for this experiment?
# # configure clamp board Utility pin to be the offset voltage for the feedback
# # at this point the slow DAC can be set by the host
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

# # TODO: how much of this do we need?
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

cmd_dac = daq.DAC[1]  # DAC channel 0 is connected to dc clamp ch 0 CMD signal
cc = daq.DAC[0]

ddr = DDR3(f, data_version='TIMESTAMPS')

# for i in range(len(ddr.data_arrays)):
#     ddr.data_arrays[i] = ddr.make_step(0, 0xFFFF, len(ddr.data_arrays[i]))
# # write channels to the DDR
# ddr_write_setup()
# # clear read, set write, etc. handled within write_channels
# block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
# ddr.reset_mig_interface()
# ddr_write_finish()

# ddr.data_arrays[3] = ddr.make_step(0x2000 - 0x800, 0x2000 + 0x800,
#                                    length=2048)
# ddr.data_arrays[2] = ddr.make_step(0x2000 - 0x800, 0x2000 + 0x800,
#                                    length=2048)

set_cmd_cc(cmd_val=0xff00, cc_scale=0, cc_delay=0, fc=None,
           step_len=16384, cc_val=None, cc_pickle_num=None)
# set_cmd_cc(cmd_val=from_voltage(0.05, 16, 5), cc_scale=0, cc_delay=0, fc=None,
#            step_len=16384, cc_val=None, cc_pickle_num=None)

#CHAN_UNDER_TEST = 0
#output = pd.DataFrame()
#data = {}
file_name = 'test'
#data['filename'] = file_name
#output = output.append(data, ignore_index=True)

#print(output.head())
#output.to_csv(os.path.join(data_dir, file_name + '.csv'))

idx = 0

REPEAT = False
if REPEAT:  # to repeat data capture without rewriting the DAC data
    ddr.clear_adc_read()
    ddr.clear_adc_write()

    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()

    ddr_write_finish()
    time.sleep(0.01)

# saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                     blk_multiples=40)  # blk multiples multiple of 10

# to get the deswizzled data of all repeats need to read the file
_, chan_data = read_h5(data_dir, file_name=file_name.format(
    idx) + '.h5', chan_list=np.arange(8))

# Long data sequence -- entire file
adc_data, timestamp, dac_data, ads, read_errors = ddr.data_to_names(chan_data)

# Shorter data sequence, just one of the repeats
# adc_data, timestamp, read_check, dac_data, ads = ddr.data_to_names(chan_data_one_repeat)

t = np.arange(0, len(adc_data[0]))*1/FS

# placeholder in case the first bits of DDR data are unrealiable. Doesn't seem to be the case.
crop_start = 0
print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')

# fig, axes = plt.subplots(2, 4)
# # fast ADC. AD7961
# for ch in range(4):
#     y = adc_data[ch][crop_start:]
#     lbl = f'Ch{ch}'
#     axes[0][ch].plot(t*1e6, y, marker='.', label=lbl)
#     axes[0][ch].legend()
#     axes[0][ch].set_title('Fast ADC data')
#     axes[0][ch].set_xlabel('s [us]')

# # DACs
# t_dacs = t[crop_start::2]  # fast DACs are saved every other 5 MSPS tick
# for dac_ch in range(4):
#     y = dac_data[dac_ch][crop_start:]
#     lbl = f'Ch{dac_ch}'
#     axes[1][dac_ch].plot(t_dacs*1e6, y, marker='.', label=lbl)
#     axes[1][dac_ch].legend()
#     axes[1][dac_ch].set_title(f'Fast DAC data {dac_ch}')
#     axes[1][dac_ch].set_xlabel('s [us]')

# fig2, ax2 = plt.subplots(2, 4)
# for ch in range(8):
#     y = ddr.data_arrays[ch]
#     ax2[ch // 4][ch % 4].plot(y)
#     ax2[ch // 4][ch % 4].set_title(f'DDR ch{ch}')

# # Convert to voltage?
# adc_converted = to_voltage(chan_data[1][crop_start:], num_bits=16, voltage_range=10, use_twos_comp=True)
# adc_converted2 = to_voltage(adc_data[0][crop_start:], num_bits=16, voltage_range=10, use_twos_comp=True)
# fig3, ax3 = plt.subplots()
# ax3.plot(t[crop_start:] * 1e6, adc_converted, c='b', label='chan_data')
# ax3.plot(t[crop_start:] * 1e6, adc_converted2, c='r', label='adc_data')
# ax3.set_title('Converted ADC data (AD7961)')
# ax3.set_xlabel('Time [us]')
# ax3.set_ylabel('Voltage [V]')
# ax3.legend()

# Convert to voltage?
adc_converted = to_voltage(chan_data[1][crop_start:], num_bits=16, voltage_range=10, use_twos_comp=True)
fig3, ax3 = plt.subplots()
ax3.plot(t[crop_start:] * 1e6, adc_converted, c='b', label='chan_data')
ax3.set_title('Converted ADC data (AD7961)')
ax3.set_xlabel('Time [us]')
ax3.set_ylabel('Voltage [V]')
ax3.legend()

# Try with 5 different resistors
voltage_data = {10: [], 33: [], 100: [], 332: [], 3000: []}    # Rf Resistor values for Figure 4 graph
main_fig, main_ax = plt.subplots()
main_ax.set_title('Voltage response to CMD step voltage')
for res in voltage_data.keys():
    # Choose resistor
    log_info, config_dict = clamp.configure_clamp(
        ADC_SEL="CAL_SIG1",
        DAC_SEL="drive_CAL2",
        CCOMP=47,
        RF1=2.2,  # feedback circuit
        # RF1=2.1,  # feedback circuit
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
    set_cmd_cc(cmd_val=0x400, cc_scale=0, cc_delay=0, fc=None,
               step_len=16384, cc_val=None, cc_pickle_num=None)

    # Get data
    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats=8,
                                        blk_multiples=40)  # blk multiples multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(
        idx) + '.h5', chan_list=np.arange(8))

    # Store voltage in list
    voltage_data[res] = to_voltage(chan_data[1][crop_start:], num_bits=16, voltage_range=10, use_twos_comp=True)
    main_ax.plot(voltage_data[res], label=str(res) + 'k\N{GREEK CAPITAL LETTER OMEGA}')
main_ax.legend()

current_fig, current_ax = plt.subplots()
current_ax.set_title('Current response to CMD step voltage')
for res in voltage_data.keys():
    current_ax.plot([v / res for v in voltage_data[res]], label=str(res) + 'k\N{GREEK CAPITAL LETTER OMEGA}')
current_ax.legend()