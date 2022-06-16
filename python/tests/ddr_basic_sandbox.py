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
from interfaces.interfaces import (
    FPGA,
    AD5453,
    Endpoint,
    DAC80508,
    DDR3,
)
from interfaces.utils import from_voltage
import os
import sys
from time import sleep
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
from analysis.adc_data import read_h5


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
    today.year, today.month, today.day)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

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

daq = Daq(f)

# fast DACs -- only use to set SPI controller data source to DDR and disable filters
for i in [0,1,2,3,4,5]:
    daq.DAC[i].filter_select(operation="clear")
    daq.DAC[i].set_data_mux("DDR")
    #daq.DAC[i].write_filter_coeffs()

# --- Configure for DDR read to DAC80508 ---
for dac_gp_ch in [0, 1]:
    daq.DAC_gp[dac_gp_ch].set_data_mux('DDR')

ddr = DDR3(f, data_version='TIMESTAMPS')

def ddr_write_setup():
    ddr.clear_adcs_connected()
    ddr.clear_dac_read()
    ddr.clear_adc_write()
    ddr.reset_fifo(name='ALL')
    ddr.reset_mig_interface()

def ddr_write_finish():
    ddr.set_adc_dac_simultaneous()  # enable DAC playback and ADC writing to DDR

##### --------- configure data to load into DDR -------------------
FAST_DAC_FREQ = 7e3
for i in range(7):
    ddr.data_arrays[i], fdac_freq = ddr.make_sine_wave(0x800, FAST_DAC_FREQ,
                                        offset=0x1000)

# ---------- configure "slow" DAC DAC80508
sdac_amp_volt = 1
target_freq_sdac = 12000.0
sdac_amp_code = from_voltage(voltage=sdac_amp_volt, num_bits=16, voltage_range=2.5, with_negatives=False)
sdac_sine, sdac_freq = ddr.make_sine_wave(amplitude=sdac_amp_code, frequency=target_freq_sdac, offset=0x8000)

# load slow DAC sine-wave in DDR channels 7 and 8 
for i in range(2):
    ddr.data_arrays[i + 6] = sdac_sine

ddr_write_setup()
block_pipe_return, speed_MBs = ddr.write_channels(set_ddr_read=False)
ddr.reset_mig_interface()  # resets the address pointers for both DDR buffers 
ddr_write_finish()  # simultaneously enables DAC read, ADC write, and ADC read via PipeOut 

## ----------- end writing data to DDR -------------------

def run_test(repeat=False, num_repeats=8, blk_multiples=40, PLT=False, KEEP_DAC_GOING=False):

    if repeat:  # to repeat data capture without rewriting the DAC data
        
        # stop access to the FIFOs so that after reset of the FIFO(s) no new data is added/extracted
        ddr.clear_adc_read()
        ddr.clear_adc_write()
        ddr.clear_dac_read()

        if not KEEP_DAC_GOING:
            ddr.reset_fifo(name='ALL')

        elif KEEP_DAC_GOING:
            # alternatively to keep DAC data running only reset ADC fifos 
            # (but mismatches of DAC written / read will fail)
            ddr.reset_fifo(name='ADC_IN')
            ddr.reset_fifo(name='ADC_TRANSFER')

        ddr.reset_mig_interface()  # self.fpga.send_trig(self.endpoints['UI_RESET'])

        ddr_write_finish()  # note that the MIG interface addresses are driven by the FIFOs so will idle 
                            # until the FIFOs are reenable with ddr_write_finish()
        time.sleep(0.01)

    file_name = 'test'
    idx = 0

    # saves data to a file; returns to the workspace the deswizzled DDR data of the last repeat
    # ddr.save_data calls:   set_adc_read()  # enable data into the ADC reading FIFO
    chan_data_one_repeat = ddr.save_data(data_dir, file_name.format(idx) + '.h5', num_repeats = num_repeats,
                            blk_multiples=blk_multiples) # blk multiples must be a multiple of 10

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=file_name.format(idx) + '.h5', chan_list=np.arange(8))

    # Long data sequence read back entire file 
    adc_data, timestamp, dac_data, ads, reading_error = ddr.data_to_names(chan_data)

    print(f'Timestamp spans {5e-9*(timestamp[-1] - timestamp[0])*1000} [ms]')
    if reading_error:
        print(f'DDR reading error is {reading_error}')
    else:
        print(f'No DDR reading errors \n constant values are correct and timestamps have equal increments')

    # DACs 
    if PLT:
        for dac_ch in range(4):
            fig,ax=plt.subplots()
            y = dac_data[dac_ch]
            lbl = f'Ch{dac_ch}'
            ax.plot(y[1:], marker = '+', label = lbl)
            ax.plot(ddr.data_arrays[dac_ch][0:(len(dac_data[dac_ch])-1)], 
                marker='*', label = 'DDR uploaded')
            ax.legend()
            ax.set_title('Fast DAC data')
            ax.set_xlabel('Sample #')

    total_mismatches = 0
    # compare DAC channels read to DAC channels written 
    for dac_ch in range(4):
        dac_write = ddr.data_arrays[dac_ch][0:(len(dac_data[dac_ch])-1)]
        num_mismatch = np.sum(dac_data[dac_ch][1:] != dac_write)
        total_mismatches += num_mismatch
        print(f'DAC channel {dac_ch} has {num_mismatch} mismatches between read and write')

    if total_mismatches == 0 and (not reading_error):
        test_pass = True
        print('Test passed') 
    else:
        test_pass = False
        print('Test failed') 

    print(f'DDR write speed {speed_MBs} MB/s')
    data_rate = 8*2/0.2e-6/1024**2 # in MB/s 
    print(f'DDR reading kept pace with {data_rate} MB/s')

    return test_pass, total_mismatches, reading_error, speed_MBs

print(f'First run after DDR upload'.center(35, '-'))
run_test(num_repeats = 8, PLT=True)
# TODO: data_to_names - hangs with num_repeats = 80 

# can be rerun again without reloading DDR via
# however output data (DAC) and read data (ADC, DAC readback) will be out of phase unless repeat=True
print(f'Re-run without re-writing the DDR data'.center(35, '-'))
run_test(repeat=True, num_repeats=2, PLT=True)

pasue_time = 10
print(f'Pausing for {pasue_time} seconds'.center(35, '-'))
print(f'Re-run without re-writing the DDR data'.center(35, '-'))
time.sleep(pasue_time)
run_test(repeat=True, num_repeats=2, PLT=True)

print(f'Re-run without re-writing the DDR data and without DAC FIFO reset'.center(35, '-'))
run_test(repeat=True, num_repeats=2, PLT=True, KEEP_DAC_GOING=True)