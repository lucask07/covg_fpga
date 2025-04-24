"""
This program contains the function to call everytime when users add new instruments configuration to yaml file
"""
import instrbuilder
from instrbuilder import instrument_opening

def add_instrument():
    """
    Call this whenever users need to add any instrument
    """
    _usb, _not_in_cfg = instrument_opening.detect_instruments()
    # cfg = instrument_opening.user_input(not_in_cfg[0])  # requires User input

    # instrument_opening.append_to_yaml(cfg)

