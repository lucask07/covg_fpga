import time
import numpy as np
import matplotlib.pyplot as plt

# Defines data_dir_covg and adds the path to boards.py into the sys.path
import setup_paths
from setup_paths import *

from bathclamp_vclamp_utils import *
from bath_clamp_setup_steps import *

from datastream.datastream import h5_to_datastreams
from boards import Clamp

## TODO: Add a conditional function here
device_compilation = None
def initialize_devices():
    global device_compilation
    device_compilation = device_setup()

def collect_data():
    # -------- Collect Data -------------
    file_name = time.strftime("%Y%m%d-%H%M%S")
    datastream_out_fname = 'clamptest1_quietdacs{}_rtia{}_ccomp{}_inamp{}.h5'
    idx = 0


    # Set CMD and CC signals - only for the bath clamp
    fc_cmd = None
    step_len = 16384*8 # 2^17
    first_pos_step = step_len/2*1/DAC_FS # in seconds 
    cmd_val = 0x0200 # will be overriden by setting in mV below 
    cc_val = 0

    # Capture data
    plt.close('all')
    first_time = True
    cmd_mv = 50
    cmd_val, actual_v = cmd_mv2dac(cmd_mv, device_compilation.sys_connections, dac_chan='D1')
    set_cmd_cc(fpga_board=device_compilation.fpga_board, dc_nums=[device_compilation.fpga_board.dc_mapping['bath'], 
                                                                device_compilation.fpga_board.dc_mapping['guard']], 
                                                                cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=fc_cmd,
            step_len=step_len, cc_val=cc_val, cc_pickle_num=None)

    device_compilation.fpga_board.ddr.repeat_setup()  # Get data

    datastreams, log_info = capture_data(fpga_board=device_compilation.fpga_board, 
                                        experiment_setup=device_compilation.instrument, 
                                        file_name_raw=file_name, 
                                        data_dir=setup_paths.data_dir, 
                                        dc_configs=device_compilation.dc_configs, idx=0)
    first_time, plotmanager1, plotmanager2, figs, datastreams, idx = update_plots(first_time=first_time, datastreams=datastreams, first_pos_step=first_pos_step)
    # run twice to remove initial transient 
    idx = 1
    datastreams = ds_add_log(device_compilation.instrument, datastreams, device_compilation.dc_configs, first_pos_step, cmd_val=cmd_val, 
                            step_len=step_len, cc_val=cc_val, fc_cmd=fc_cmd, 
                            sys_connections=device_compilation.sys_connections)
    datastreams.to_h5(setup_paths.data_dir, f"initial_startup_{guard_adg_r}rf_{guard_ccomp}ccomp.h5", log_info)

    ds, datastreams, first_time, plotmanager1, plotmanager2, figs, idx = measure_cmd_cc_impulse(device_compilation.fpga_board, 
                        experiment_class=device_compilation.instrument, FS=FS, 
                        sys_connections=device_compilation.sys_connections, 
                        cmd_cc_scale={'fc_cmd' : fc_cmd, 'step_len' : step_len}, 
                        plot_setting={'idx' : idx, 'first_time' : first_time, 'plotmanager1' : plotmanager1, 'plotmanager2' : plotmanager2, 'figs' : figs}, 
                        ccomp=guard_ccomp, 
                        first_pos_step=first_pos_step, 
                        adgr_ccomp_combination=[(100, 47)], 
                        data_dir=setup_paths.data_dir, 
                        h5_file_name=file_name, 
                        dc_configs=device_compilation.dc_configs, CC_IMPULSE=MEASURE_CC_IMPULSE, 
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

    first_time, plotmanager1, plotmanager2, figs, datastreams, idx = large_param_sweep(fpga_board=device_compilation.fpga_board, 
                                                                                    experiment_setup=device_compilation.instrument, 
                                                                                    file_name_before_format=file_name, 
                                                                                    osc=osc, 
                                                                                    data_dir=data_dir, 
                                                                                    dc_configs=device_compilation.dc_configs, 
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
                                                                                        sys_connections=device_compilation.sys_connections)

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
            device_compilation.dc_configs[1]['RF1'] = rf
            device_compilation.fpga_board.clamps[1].configure_clamp(**device_compilation.dc_configs[1])
            print(f'RF = {rf}')
            input('next?')

    device_compilation.dc_configs[0]['ADG_RES'] = 100
    device_compilation.dc_configs[0]['CCOMP'] = 47
    device_compilation.fpga_board.clamps[0].configure_clamp(**device_compilation.dc_configs[0])
    print(f'Configure at known good config to measure on oscope')
