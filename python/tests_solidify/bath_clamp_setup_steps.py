import sys
import openpyxl
import json
from setup_paths import *

from instrbuilder.instrument_opening import open_by_name
from bathclamp_vclamp_utils import *
# ------------- vsense2 and quiet_dacs ------------------
VSENSE2 = 0 # True # content['B'+str(key_map['VSENSE2'])] # True
QUIET_DACS = 0 # False # content['B'+str(key_map['QUIET_DACS'])] # False
DAQ_V = 0 # "2.1"
# ------------- ephys system name -------------
EPHYS_SYS_NAME = 0 # 'Dagan_guard' # content['B'+str(key_map['EPHYS_SYS_NAME'])] # 'Dagan_guard'
# ------------- model cell configuration ------------
NUMBER = 0 # 3 # guard
RS = 0 # 1e3
RP1 = 0 # 5e3
RV1 = 0 # 200e3
COUPLING_CAP_C20 = 0 # 0
RLEAK = 0 # 47e5
# ------------- sample parameters -------------------
DAC_FS = 0 # 2.5e6
FS = 0 # 5e6
ADS_FS = 0 # 1e6
# ------------- board mapping ----------------------
BATH = 0 # 0
CLAMP = 0 # 2
GUARD = 0 # 1
VSENSE = 0 # 3
# ------------- power instrument & setup -----------
POWER_SETUP = 0 # '3dual'
# ------------- list of names to supply powers ---------
LIST_POWERS = 0 # ["1V8", "5V", "3V3"]
SPI_DEBUG = 0 # 'ads'
ADS_MISC = 0 # 'convst'
# ------------- experiment setups
feedback_resistors = 0 # [2.1]
capacitors = 0 # [47]
bath_res = 0 # [10, 100, 332, 1000] # Clamp.configs['ADG_RES_dict'].keys()
bath_res = 0 # [100]
in_amp = 0 # 2 # 05/02 step response was 2; 05/04 in_amp = 0 # 1
dac_range = 0 # 5  # 5V full-scale range of the fast DACs 
ADS8686_VOLTAGE_RANGE = 0 # 5
ADS8686_LPF = 0 # 376
ADS8686_SEQUENCER_SETUP = 0 # [('0', '0'), ('1', '1'), ('3', '2')]
# -------------- DC configuration ------------------------
## Clamp
clamp_fb_res = 0 # 60 # resistors and cap have changed so this does not correspond to typical bath clamp board  LJK was 3
clamp_res = 0 # 1000 # modified board: set to 10 MOhms -> 0 Ohms; 3.32 MOhms -> Open; 1 MOhms -> 50 Ohms (snubber)
clamp_cap = 0 # 47
## Bath
bath_fb_res = 0 # 60  # this is disconnected and now in unity-gain! 60 is what configures the calibration to be at x1 
bath_adg_r = 0 # 33  # Try with 5 different resistors
bath_ccomp = 0 # 47
## Guard
guard_fb_res = 0 # 60  # this is disconnected and now in unity-gain!
guard_adg_r = 0 # 332  # Try with 5 different resistors
guard_ccomp = 0 # 4700
# ----------------- Miscellaneous setup --------------------
UNUSED_DACS = 0 # [2, 4, 5]
FAST_AD7961_CHANNELS = 0 # [0, 1, 2, 3]

# ----------------- Collect data setting --------------------------
MEASURE_CC_IMPULSE = 0 # True
MEASURE_CC_CANCELATION = 0 # False
METHOD_CC_CANCELATION = 0 # 'spline'

# Load json #############
with open("system_setup.json") as f:
    data = json.load(f)

for key, value in data.items():
    globals()[key] = value
#########################

osc = open_by_name('msox_scope')

# ----- chose negatives version -----------

NEG = (16.5 if DAQ_V == '2.1' else 15.0)

def device_setup(allfour=False) -> HardwareSetup:
    """
    Setup the hardware configuration for the experiment.
    Parameters
    ----------
    allfour : bool
        If True, sets up all four channels of the hardware.
    Returns
    -------
    hardware : HardwareSetup
        Configured hardware setup for the experiment.
    """
    return (
        HardwareSetup(
            set_vsense2=VSENSE2, 
            quiet_dacs=QUIET_DACS, 
            ephys_system_name=EPHYS_SYS_NAME, 
            model_cell_config=dict(
                number=NUMBER, 
                Rs=RS,
                Rv1=RV1,
                Rp1=RP1, 
                coupling_cap_c20=COUPLING_CAP_C20, 
                Rleak=RLEAK
            )
        )
        .set_sample_params(DAC_FS=DAC_FS, FS=FS, SAMPLE_PERIOD=1/FS, ADS_FS=ADS_FS)
        .setup_power(pwr_setup=POWER_SETUP, neg=NEG)
        .fpga_interface(dc_mapping=dict(bath=BATH, guard=GUARD, clamp=CLAMP, vclamp=VSENSE))
        .turn_on_power_supply(LIST_POWERS)
        # Config debug muxs
        .config_spi_debug_mux(spi_debug=SPI_DEBUG, ads_misc=ADS_MISC)
        .organize_clamp_board(allfour=allfour)
        # configure the ADS8686
        .configure_ads8686(ads_voltage_range=ADS8686_VOLTAGE_RANGE, 
                                    lpf=ADS8686_LPF, 
                                    ads_sequencer_setup=ADS8686_SEQUENCER_SETUP)
        .fast_dac_chan_setup(dac_range=dac_range)
        .quiet_unused_dacs(UNUSED_DACS)
        .enable_fast_adcs(FAST_AD7961_CHANNELS)

        # set all fast-DAC DDR data to midscale
        .set_cmd_cc(dc_nums=FAST_AD7961_CHANNELS, cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
                step_len=16384, cc_val=None, cc_pickle_num=None)
    )

__all__ = ['VSENSE2', 'QUIET_DACS', 'EPHYS_SYS_NAME', 'NUMBER', 'RS', 'RP1', 'RV1',
    'COUPLING_CAP_C20', 'RLEAK', 'DAC_FS', 'FS', 'ADS_FS', 'BATH', 'CLAMP',
    'GUARD', 'VSENSE', 'POWER_SETUP', 'NEG', 'LIST_POWERS', 'SPI_DEBUG',
    'ADS_MISC', 'feedback_resistors', 'capacitors', 'bath_res', 'in_amp',
    'dac_range', 'ADS8686_VOLTAGE_RANGE', 'ADS8686_LPF', 'ADS8686_SEQUENCER_SETUP',
    'clamp_fb_res', 'clamp_res', 'clamp_cap', 'bath_fb_res', 'bath_adg_r',
    'bath_ccomp', 'guard_fb_res', 'guard_adg_r', 'guard_ccomp', 'UNUSED_DACS',
    'FAST_AD7961_CHANNELS', 'MEASURE_CC_IMPULSE', 'MEASURE_CC_CANCELATION',
    'METHOD_CC_CANCELATION', 'osc', 'device_setup'
]
