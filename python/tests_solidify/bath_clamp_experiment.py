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
hardware = None
if __name__ == '__main__' and hardware is None:
    hardware : HardwareSetup = device_setup()

if __name__ == '__main__':
    dc_configs = {}
    # self.clamp_fb_res = 60 # resistors and cap have changed so this does not correspond to typical bath clamp board  LJK was 3
    # self.clamp_res = 1000 # modified board: set to 10 MOhms -> 0 Ohms; 3.32 MOhms -> Open; 1 MOhms -> 50 Ohms (snubber)
    # self.clamp_cap = 47
    # to digitize I1 use ADC_SEL = "CAL_SIG2"; P2_CAL_CTRL=1; DAC_SEL="noDrive"
    for dc_num in [hardware.dc_mapping['clamp']]:
        log_info, config_dict = hardware.clamps[dc_num].configure_clamp(
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

    # self.fb_res = 60  # this is disconnected and now in unity-gain! 60 is what configures the calibration to be at x1 
    # Try with 5 different resistors
    # self.adg_r = 33
    # self.ccomp = 47
    # Choose resistor; setup
    for dc_num in [hardware.dc_mapping['bath']]:
        log_info, config_dict = hardware.clamps[dc_num].configure_clamp(
            ADC_SEL="CAL_SIG2",  # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize P1
            DAC_SEL="noDrive",
            CCOMP=bath_ccomp,
            RF1=bath_fb_res,  # feedback circuit
            ADG_RES=bath_adg_r,
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

    # self.fb_res = 60  # this is disconnected and now in unity-gain! 
    # Try with 5 different resistors
    # self.adg_r = 332
    # self.ccomp = 4700
    for dc_num in [hardware.dc_mapping['guard']]:
        log_info, config_dict = hardware.clamps[dc_num].configure_clamp(
            ADC_SEL="CAL_SIG2",  # CAL_SIG2 to digitize P2 or CAL_SIG1 to digitize P1; must also close the corresponding relay. Note that CAL_SIG1 and P1_CAL_CTRL=1 caused oscillations.
            DAC_SEL="noDrive",
            CCOMP=guard_ccomp,
            RF1=guard_fb_res,  # feedback circuit
            ADG_RES=guard_adg_r,
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
    
    vsense, gain1, gain2 = hardware.operate_vsense2()
    
    sys_connections = render_sys_connections(
        dc_configs, hardware
    )

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
    cmd_val, actual_v = cmd_mv2dac(cmd_mv, sys_connections, dac_chan='D1')
    hardware.set_cmd_cc(dc_nums=[hardware.dc_mapping['bath'], 
                        hardware.dc_mapping['guard']], 
                        cmd_val=cmd_val, cc_scale=0, cc_delay=0, fc=fc_cmd,
            step_len=step_len, cc_val=cc_val, cc_pickle_num=None)

    hardware.ddr.repeat_setup()  # Get data

    datastreams, log_info = capture_data(hardware=hardware, 
                                        file_name_raw=file_name, 
                                        data_dir=setup_paths.data_dir, 
                                        dc_configs=dc_configs, idx=0)
    first_time, plotmanager1, plotmanager2, figs, datastreams, idx = update_plots(first_time=first_time, datastreams=datastreams, first_pos_step=first_pos_step)
    # run twice to remove initial transient 
    idx = 1
    datastreams = ds_add_log(hardware, datastreams, dc_configs, first_pos_step, cmd_val=cmd_val, 
                            step_len=step_len, cc_val=cc_val, fc_cmd=fc_cmd, 
                            sys_connections=sys_connections)
    datastreams.to_h5(setup_paths.data_dir, f"initial_startup_{guard_adg_r}rf_{guard_ccomp}ccomp.h5", log_info)

    ds, datastreams, first_time, plotmanager1, plotmanager2, figs, idx = measure_cmd_cc_impulse(
                        hardware, 
                        FS=FS, 
                        sys_connections=sys_connections, 
                        cmd_cc_scale={'fc_cmd' : fc_cmd, 'step_len' : step_len}, 
                        plot_setting={'idx' : idx, 'first_time' : first_time, 'plotmanager1' : plotmanager1, 'plotmanager2' : plotmanager2, 'figs' : figs}, 
                        ccomp=guard_ccomp, 
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

    first_time, plotmanager1, plotmanager2, figs, datastreams, idx = large_param_sweep(
        hardware=hardware, 
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
        plot_setting={
            'idx' : idx, 'first_time' : first_time, 
            'plotmanager1' : plotmanager1, 
            'plotmanager2' : plotmanager2, 'figs' : figs}, 
        cc_val=cc_val, 
        clamp_fb_res=clamp_fb_res, 
        clamp_res=clamp_res, 
        first_pos_step=first_pos_step, 
        TO_CLAMPFIT=TO_CLAMPFIT, 
        sys_connections=sys_connections
    )

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
            hardware.clamps[1].configure_clamp(**dc_configs[1])
            print(f'RF = {rf}')
            input('next?')

    dc_configs[0]['ADG_RES'] = 100
    dc_configs[0]['CCOMP'] = 47
    hardware.clamps[0].configure_clamp(**dc_configs[0])
    print(f'Configure at known good config to measure on oscope')
