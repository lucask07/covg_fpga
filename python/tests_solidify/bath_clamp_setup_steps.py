import sys
import openpyxl
import json
from setup_paths import *

from instrbuilder.instrument_opening import open_by_name
from bathclamp_vclamp_utils import *

"""
excel_cfg_file = sys.argv[1]
workbook = openpyxl.load_workbook(excel_cfg_file)
content = workbook.active

key_map = dict()
for i, row in enumerate(content.iter_rows(min_col=1, max_col=1, values_only=True)):
    key_map[row[0]] = i
    """

# ------------- vsense2 and quiet_dacs ------------------
VSENSE2 = True # content['B'+str(key_map['VSENSE2'])] # True
QUIET_DACS = False # content['B'+str(key_map['QUIET_DACS'])] # False
DAQ_V = "2.1"
# ------------- ephys system name -------------
EPHYS_SYS_NAME = 'Dagan_guard' # content['B'+str(key_map['EPHYS_SYS_NAME'])] # 'Dagan_guard'
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
CLAMP = 2
GUARD = 1
VSENSE = 3
# ------------- power instrument & setup -----------
POWER_SETUP = '3dual'
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

# Load json #############
with open("system_setup.json") as f:
    data = json.load(f)

for key, value in data.items():
    globals()[key] = value
#########################

osc = open_by_name('msox_scope')

# ----- chose negatives version -----------

NEG = (16.5 if DAQ_V == '2.1' else 15.0)

class DeviceSetUp:
    def __init__(self, allfour=False):
        self.instrument = BathclampVclampStepResponse(set_vsense2=VSENSE2, 
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
        self.instrument.set_sample_params(DAC_FS=DAC_FS, FS=FS, SAMPLE_PERIOD=1/FS, ADS_FS=ADS_FS)
        self.instrument.setup_power(pwr_setup=POWER_SETUP, neg=NEG)

        self.fpga_board = FPGAInterface(experiment_class=self.instrument, dc_mapping=dict(bath=BATH, guard=GUARD, clamp=CLAMP, vclamp=VSENSE))
        self.fpga_board.turn_on_power_supply(LIST_POWERS)
        # Config debug muxs
        self.fpga_board.config_spi_debug_mux(spi_debug=SPI_DEBUG, ads_misc=ADS_MISC)
        self.fpga_board.organize_clamp_board(allfour=allfour)
        # configure the ADS8686
        self.fpga_board.configure_ads8686(ads_voltage_range=ADS8686_VOLTAGE_RANGE, 
                                    lpf=ADS8686_LPF, 
                                    ads_sequencer_setup=ADS8686_SEQUENCER_SETUP)
        self.fpga_board.fast_dac_chan_setup(dac_range=dac_range)
        self.fpga_board.quiet_unused_dacs(UNUSED_DACS)
        self.fpga_board.enable_fast_adcs(FAST_AD7961_CHANNELS)

        # set all fast-DAC DDR data to midscale
        self.fpga_board.set_cmd_cc(dc_nums=FAST_AD7961_CHANNELS, cmd_val=0x0, cc_scale=0, cc_delay=0, fc=None,
                step_len=16384, cc_val=None, cc_pickle_num=None)


def device_setup(allfour=False) -> DeviceSetUp:
    return DeviceSetUp(allfour=allfour)


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
