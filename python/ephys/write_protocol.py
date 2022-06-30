"""Write a Protocol and read back the data from the cell."""

import matplotlib.pyplot as plt
from core import Protocol, Experiment

protocol = Protocol.create_from_csv(filepath='protocol.csv', num_sweeps=5)
protocol.preview()

# Pause to show user preview
# plt.show()

# Run experiment
clamp_nums = [0, 1]
experiment = Experiment(protocol)
experiment.setup()

cap = 47
fb_res = 2.1
res = 33
for clamp_num in [0, 1]:
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

experiment.write_sequence(clamp_num=clamp_nums)
# time and data will be in milliseconds and millivolts
t, data = experiment.read_response(clamp_num=clamp_nums)
# experiment.close()

# Plot data
current_data = {}
for key in data:
    # Voltage data in mV, want current data in uA, so multiply by 1e3
    current_data[key] = data[key] / res * 1e3
fig, ax = plt.subplots(1, 2)
for clamp_num in clamp_nums:
    # ax[clamp_num].plot(t, current_data[clamp_num])
    # ax[clamp_num].set_xlabel('Time [ms]')
    ax[clamp_num].plot(current_data[clamp_num])
    ax[clamp_num].set_title('Current Response')
    ax[clamp_num].set_ylabel('Current [\N{GREEK SMALL LETTER MU}A]')
plt.show()
