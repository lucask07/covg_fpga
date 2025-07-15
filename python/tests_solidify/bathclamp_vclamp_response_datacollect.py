import time
import numpy as np
import matplotlib.pyplot as plt

# Defines data_dir_covg and adds the path to boards.py into the sys.path
import setup_paths
from setup_paths import *
from datastream.datastream import h5_to_datastreams
from boards import Clamp

from instrbuilder.instrument_opening import open_by_name
from bathclamp_vclamp_utils import *

DAQ_V = "2.1"
# ------------- vsense2 and quiet_dacs ------------------
VSENSE2 = True
QUIET_DACS = False
# ------------- ephys system name -------------
EPHYS_SYS_NAME = 'Dagan_guard'
# ------------- model cell configuration ------------
NUMBER = 3 # guard
RS = 1e3
RP1 = 5e3
RV1 = 200e3
COUPLING_CAP_C20 = 0
RLEAK = 47e5
# ------------- sample parameters -------------------
DAC_FS = 2.5e6
FS = 5e6
ADS_FS = 1e6
# ------------- board mapping ----------------------
BATH = 0
CLAMP = 3
GUARD = 1
VSENSE = 2
# ------------- power instrument & setup -----------
POWER_SETUP = '3dual'
NEG = 16.5 if DAQ_V == "2.1" else 15
# ------------- list of names to supply powers ---------
LIST_POWERS = ["1V8", "5V", "3V3"]
SPI_DEBUG = 'ads'
ADS_MISC = 'convst'
# ------------- experiment setups
feedback_resistors = [2.1]
capacitors = [47]
bath_res = [10, 100, 332, 1000] # Clamp.configs['ADG_RES_dict'].keys()
bath_res = [100]
in_amp = 2 # 05/02 step response was 2; 05/04 in_amp = 1
dac_range = 5  # 5V full-scale range of the fast DACs 
ADS8686_VOLTAGE_RANGE = 5
ADS8686_LPF = 376
ADS8686_SEQUENCER_SETUP = [('0', '0'), ('1', '1'), ('3', '2')]
# -------------- DC configuration ------------------------
## Clamp
clamp_fb_res = 60 # resistors and cap have changed so this does not correspond to typical bath clamp board  LJK was 3
clamp_res = 1000 # modified board: set to 10 MOhms -> 0 Ohms; 3.32 MOhms -> Open; 1 MOhms -> 50 Ohms (snubber)
clamp_cap = 47
## Bath
bath_fb_res = 60  # this is disconnected and now in unity-gain! 60 is what configures the calibration to be at x1 
bath_adg_r = 33  # Try with 5 different resistors
bath_ccomp = 47
## Guard
guard_fb_res = 60  # this is disconnected and now in unity-gain!
guard_adg_r = 332  # Try with 5 different resistors
guard_ccomp = 4700
# ----------------- Miscellaneous setup --------------------
UNUSED_DACS = [2, 4, 5]
FAST_AD7961_CHANNELS = [0, 1, 2, 3]

# ----------------- Collect data setting --------------------------
MEASURE_CC_IMPULSE = True
MEASURE_CC_CANCELATION = False
METHOD_CC_CANCELATION = 'spline'
osc = open_by_name('msox_scope')

instrument = BathclampVclampStepResponse(set_vsense2=VSENSE2, 
                                         quiet_dacs=QUIET_DACS, 
                                         ephys_system_name=EPHYS_SYS_NAME, 
                                         model_cell_config=dict(number=NUMBER, 
                                                                Rs=RS,
                                                                Rv1=RV1,
                                                                Rp1=RP1, 
                                                                coupling_cap_c20=COUPLING_CAP_C20, 
                                                                Rleak=RLEAK
                                                                )
                                        )
instrument.set_sample_params(DAC_FS=DAC_FS, FS=FS, SAMPLE_PERIOD=1/FS, ADS_FS=ADS_FS)
instrument.setup_power(pwr_setup=POWER_SETUP, neg=NEG)

fpga_board = FPGAInterface(experiment_class=instrument, dc_mapping=dict(bath=BATH, guard=GUARD, clamp=CLAMP, vsense=VSENSE))
fpga_board.turn_on_power_supply(LIST_POWERS)
# Config debug muxs
fpga_board.config_spi_debug_mux(spi_debug=SPI_DEBUG, ads_misc=ADS_MISC)
fpga_board.organize_clamp_board()
# configure the ADS8686
fpga_board.configure_ads8686(ads_voltage_range=ADS8686_VOLTAGE_RANGE, 
                             lpf=ADS8686_LPF, 
                             ads_sequencer_setup=ADS8686_SEQUENCER_SETUP)
fpga_board.fast_dac_chan_setup(dac_range=dac_range)
fpga_board.quiet_unused_dacs(UNUSED_DACS)
fpga_board.enable_fast_adcs(FAST_AD7961_CHANNELS)

# -------- Collect Data -------------
file_name = time.strftime("%Y%m%d-%H%M%S")
datastream_out_fname = 'clamptest1_quietdacs{}_rtia{}_ccomp{}_inamp{}.h5'
idx = 0

# set all fast-DAC DDR data to midscale
fpga_board.set_cmd_cc(fpga_board, dc_nums=FAST_AD7961_CHANNELS, cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
        step_len=16384, cc_val=None, cc_pickle_num=None)

# Set CMD and CC signals - only for the bath clamp
fc_cmd = None
step_len = 16384*8 # 2^17
first_pos_step = step_len/2*1/DAC_FS # in seconds 
cmd_val = 0x0200 # will be overriden by setting in mV below 
cc_val = 0

dc_configs = {}
clamp_fb_res = 60 # resistors and cap have changed so this does not correspond to typical bath clamp board  LJK was 3
clamp_res = 1000 # modified board: set to 10 MOhms -> 0 Ohms; 3.32 MOhms -> Open; 1 MOhms -> 50 Ohms (snubber)
clamp_cap = 47
# to digitize I1 use ADC_SEL = "CAL_SIG2"; P2_CAL_CTRL=1; DAC_SEL="noDrive"
for dc_num in [fpga_board.dc_mapping['clamp']]:
    log_info, config_dict = fpga_board.clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG2", 
        DAC_SEL="noDrive", # must not be drive_CAL2 
        CCOMP=clamp_cap,
        RF1=clamp_fb_res,  # feedback circuit
        ADG_RES=clamp_res,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=1,
        gain=1,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict

fb_res = 60  # this is disconnected and now in unity-gain! 60 is what configures the calibration to be at x1 
# Try with 5 different resistors
adg_r = 33
ccomp = 47
# Choose resistor; setup
for dc_num in [fpga_board.dc_mapping['bath']]:
    log_info, config_dict = fpga_board.clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG2",  # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize P1
        DAC_SEL="noDrive",
        CCOMP=ccomp,
        RF1=fb_res,  # feedback circuit
        ADG_RES=adg_r,
        PClamp_CTRL=0,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=0,
        gain=in_amp,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict

fb_res = 60  # this is disconnected and now in unity-gain! 
# Try with 5 different resistors
adg_r = 332
ccomp = 4700
for dc_num in [fpga_board.dc_mapping['guard']]:
    log_info, config_dict = fpga_board.clamps[dc_num].configure_clamp(
        ADC_SEL="CAL_SIG2",  # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize P1; must also close the corresponding relay. Note that CAL_SIG1 and P1_CAL_CTRL=1 caused oscillations.
        DAC_SEL="noDrive",
        CCOMP=ccomp,
        RF1=fb_res,  # feedback circuit
        ADG_RES=adg_r,
        PClamp_CTRL=1,
        P1_E_CTRL=0,
        P1_CAL_CTRL=0,
        P2_E_CTRL=0,
        P2_CAL_CTRL=0,
        gain=in_amp,  # instrumentation amplifier
        FDBK=1,
        mode="voltage",
        EN_ipump=0,
        RF_1_Out=1,
        addr_pins_1=0b110,
        addr_pins_2=0b000,
    )
    dc_configs[dc_num] = config_dict

vsense, gain1, gain2 = fpga_board.operate_vsense2()
sys_connections = render_sys_connections(dc_configs, fpga_board, instrument)
# Capture data
plt.close('all')
plt.ion()
first_time = True
cmd_mv = 50
cmd_val, actual_v = cmd_mv2dac(cmd_mv, sys_connections, dac_chan='D1')
fpga_board.set_cmd_cc(dc_nums=[fpga_board.dc_mapping['bath'], fpga_board.dc_mapping['guard']], cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=fc_cmd,
        step_len=step_len, cc_val=cc_val, cc_pickle_num=None)

fpga_board.ddr.repeat_setup()  # Get data

datastreams, log_info = capture_data(fpga_board=fpga_board, 
                                     experiment_setup=instrument, 
                                     file_name_raw=file_name, 
                                     data_dir=setup_paths.data_dir, 
                                     dc_configs=dc_configs, idx=0)
first_time, plotmanager1, plotmanager2, figs, datastreams, idx = update_plots(first_time=first_time, datastreams=datastreams, first_pos_step=first_pos_step)
# run twice to remove initial transient 
idx = 1
datastreams = ds_add_log(instrument, datastreams, dc_configs, first_pos_step, cmd_val=cmd_val, 
                         step_len=step_len, cc_val=cc_val, fc_cmd=fc_cmd, 
                         sys_connections=sys_connections)
datastreams.to_h5(setup_paths.data_dir, f"initial_startup_{adg_r}rf_{ccomp}ccomp.h5", log_info)

ds, datastreams, first_time, plotmanager1, plotmanager2, figs, idx = measure_cmd_cc_impulse(fpga_board, experiment_class=instrument, FS=FS, sys_connections=sys_connections, 
                       cmd_cc_scale={'fc_cmd' : fc_cmd, 'step_len' : step_len}, 
                       plot_setting={'idx' : idx, 'first_time' : first_time, 'plotmanager1' : plotmanager1, 'plotmanager2' : plotmanager2, 'figs' : figs}, 
                       ccomp=ccomp, 
                       first_pos_step=first_pos_step, 
                       adgr_ccomp_combination=[(100, 47)], 
                       data_dir=setup_paths.data_dir, 
                       h5_file_name=file_name, 
                       dc_configs=dc_configs, CC_IMPULSE=MEASURE_CC_IMPULSE, 
                       CC_CANCELATION=MEASURE_CC_CANCELATION, 
                       method_cc_cancelation=METHOD_CC_CANCELATION, 
                       plot_cancel=True
                       )
# large parameter sweep 

OSCOPE = False
scope_data = None
components = None
scope_meas = None
if OSCOPE:
    scope_data = {} 
    components = ['CC', 'RTIA', 'CLAMP_TIA', 'CLAMP_RF']
    scope_meas = ['OVER', 'RIS']
    for sm in scope_meas:
        scope_data[sm] = np.array([])
    for c in components:
        scope_data[c] = np.array([])
    osc.set('run_acq')

# extensive sweep
adg_r_arr = [10, 33, 100, 332] # JOB: fft through all of these 
ccomp_arr = [47, 200, 247, 1000, 1247, 4700]

ccomp_arr = [47, 247, 1000, 4700]
ccomp_arr = [47, 4700]
adg_r_arr = [33, 100, 332, 1000]

mv_val_arr = np.concatenate( ([0,5], [50]) )

TO_CLAMPFIT = False

first_time, plotmanager1, plotmanager2, figs, datastreams, idx = large_param_sweep(fpga_board=fpga_board, 
                                                                                   experiment_setup=instrument, 
                                                                                   file_name_before_format=file_name, 
                                                                                   osc=osc, 
                                                                                   data_dir=data_dir, 
                                                                                   dc_configs=dc_configs, 
                                                                                   mv_val_arr=mv_val_arr, 
                                                                                   ccomp_arr=ccomp_arr, 
                                                                                   adg_r_arr=adg_r_arr, 
                                                                                   scope_meas=scope_meas, 
                                                                                   OSCOPE=OSCOPE, 
                                                                                   scope_data=scope_data, 
                                                                                   cmd_cc_scale={'fc_cmd' : fc_cmd, 'step_len' : step_len}, 
                                                                                   plot_setting={'idx' : idx, 'first_time' : first_time, 
                                                                                                 'plotmanager1' : plotmanager1, 
                                                                                                 'plotmanager2' : plotmanager2, 'figs' : figs}, 
                                                                                    cc_val=cc_val, 
                                                                                    clamp_fb_res=clamp_fb_res, 
                                                                                    clamp_res=clamp_res, 
                                                                                    first_pos_step=first_pos_step, 
                                                                                    TO_CLAMPFIT=TO_CLAMPFIT, 
                                                                                    sys_connections=sys_connections)

plot_oscilloscope(OSCOPE=OSCOPE, adg_r_arr=adg_r_arr, scope_data=scope_data)
# p1_diff = plot_im_est(datastreams)

# test writing and reading datastream h5
TST_DATASTREAM_RW = False
if TST_DATASTREAM_RW:
    datastreams2 = h5_to_datastreams(setup_paths.data_dir, 'test.h5')
    # this datastreams has the log info but as a dictionary, not as Python classes
    # if the original objects are needed could use these methods https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object
    for n in datastreams:
        assert (datastreams[n].data == datastreams2[n].data).all(), f'Datastream data with key {n} after writing and reading from file are not equal!'

print('-'*100)
for sig in ['I', 'P1', 'CMD0']:
    sig_name = sig 
    if sig_name == 'I':
        sig_name = 'Vm'
    try:
        si = datastreams[sig].stepinfo_range([first_pos_step-20e-6, first_pos_step+170e-6])
        print(f'{sig} step info: {si}')
        print('-'*100)
    except:
        print(f'Step info failed for signal: {sig}')

if 0:
    # sweep the gain of the voltage clamp; to check on the oscilloscope 
    for rf in Clamp.configs['RF1_dict']:
        dc_configs[1]['RF1'] = rf
        fpga_board.clamps[1].configure_clamp(**dc_configs[1])
        print(f'RF = {rf}')
        input('next?')

dc_configs[0]['ADG_RES'] = 100
dc_configs[0]['CCOMP'] = 47
fpga_board.clamps[0].configure_clamp(**dc_configs[0])
print(f'Configure at known good config to measure on oscope')
