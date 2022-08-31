"""Write and read a continuous sine wave with an updating graph."""

from core import Protocol, Experiment


# Run experiment
clamp_nums = [1]
protocol = Protocol.create_from_csv(filepath='protocol.csv', num_sweeps=14)
experiment = Experiment(protocol)
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

experiment.record_sine(clamp_num=clamp_nums, amplitude=1, frequency=1e3, save_data=False)
