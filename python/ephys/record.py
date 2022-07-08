"""Write a Protocol and record the data back from the cell in an updating graph."""

import matplotlib.pyplot as plt
from core import Protocol, Experiment

protocol = Protocol.create_from_csv(filepath='protocol.csv', num_sweeps=5)
# protocol.preview()

# Pause to show user preview
plt.show()

# Run experiment
clamp_nums = [0, 1]
experiment = Experiment(protocol)
experiment.setup()

cap = 47
fb_res = 2.1
res = 3000
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

t, data = experiment.record(clamp_num=clamp_nums, inject_current=True, low_scaling_factor=0, cutoff=-10, high_scaling_factor=10)
experiment.close()
