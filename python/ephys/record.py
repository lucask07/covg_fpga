"""Write a Protocol and record the data back from the cell in an updating graph."""

import matplotlib.pyplot as plt
from pyripherals.utils import read_h5, to_voltage
import os
import numpy as np
from core import Protocol, Experiment

protocol = Protocol.create_from_csv(filepath='protocol.csv', num_sweeps=14)
protocol.preview()

# Pause to show user preview
plt.show(block=True)

# Set up Experiment
setup_yaml_path = 'bathclamp_vclamp_step_response_setup.yaml'
cmd_protocol_path = 'bathclamp_vclamp_step_response_cmd.csv'
# Run experiment
clamp_nums = [1]
experiment = Experiment(protocol, setup_file_path=setup_yaml_path)
experiment.setup()

cap = 47
fb_res = 2.1
res = 332
for clamp_num in clamp_nums:
    log_info, config_dict = experiment.clamps[clamp_num].configure_clamp(
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

# For scaling factors, keep in mind our current injection range is only ~ [-0.8, 0.8] uA
data_dir, file_name = experiment.record(clamp_num=clamp_nums, filter_current=500, inject_current=True, low_scaling_factor=0, cutoff=50, high_scaling_factor=0.8/100)
# experiment.close()

_, chan_data = read_h5(data_dir, file_name=file_name, chan_list=np.arange(8))

adc_data, timestamp, dac_data, ads, ads_seq_cnt, reading_error = experiment.daq.ddr.data_to_names(chan_data)

t = np.arange(len(adc_data[0]))
plt.plot(t, to_voltage(adc_data[1], 16, 10, True) / res)
# plt.show()

import os, sys
sys.path.append(os.path.join(os.getcwd().split('covg_fpga')[0], 'covg_fpga/python'))
from analysis.adc_data import separate_ads_sequence
ads_sequencer_setup = [('1', '1'), ('2', '2')]
ads_voltage_range = 5

ads_data_v = {}
for letter in ['A', 'B']:
    ads_data_v[letter] = np.array(to_voltage(ads[letter], num_bits=16, voltage_range=ads_voltage_range, use_twos_comp=False))

total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
total_seq_cnt[::2] = ads_seq_cnt[0]
total_seq_cnt[1::2] = ads_seq_cnt[1]

ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data_v, total_seq_cnt, slider_value=4)
t_ads = np.linspace(0, len(adc_data[0]), len(ads_separate_data['A'][1]))
plt.plot(t_ads, ads_separate_data['A'][2], label="['A'][2]")
plt.show()

print('ADDR_DAC_WR:', experiment.daq.ddr.fpga.read_wire(experiment.daq.ddr.endpoints['ADDR_DAC_WR'].address))
print('ADDR_DAC_RD:', experiment.daq.ddr.fpga.read_wire(experiment.daq.ddr.endpoints['ADDR_DAC_RD'].address))
print('ADDR_ADC_WR:', experiment.daq.ddr.fpga.read_wire(experiment.daq.ddr.endpoints['ADDR_ADC_WR'].address))
print('ADDR_ADC_RD:', experiment.daq.ddr.fpga.read_wire(experiment.daq.ddr.endpoints['ADDR_ADC_RD'].address))
