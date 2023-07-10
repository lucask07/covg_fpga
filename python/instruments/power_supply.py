import numpy as np
from instrbuilder.instrument_opening import open_by_name
from pyripherals.utils import get_timestamp

def open_rigol_supply(setup=None):
    # set up DC power supply
    # name within the configuration file (config.yaml)

    if setup=='3dual':  # new power supply that can handle all three voltages
        dc_pwr = open_by_name(name='rigol_3dual')  # Ch1=7V, Ch2=16.5V, Ch3=-16.5V
        return dc_pwr, None
    elif setup=='boland_lab':
        dc_pwr = open_by_name(name='rigol_boland')  # Ch1=-15V, Ch2=16.5V, Ch3=5.3V
        return dc_pwr, None
    else:
        dc_pwr = open_by_name(name='rigol_pwr1')  # 7V in
        dc_pwr2 = open_by_name(name='rigol_ps2')  # +/-16.5V
        return dc_pwr, dc_pwr2


def init_current_meas_dict():
    current_meas = {}
    for ch in range(1, 4):
        # create dictionary for each channel
        current_meas['ch{}'.format(ch)] = {}
        for n in ['val', 'timestamp']:
            current_meas['ch{}'.format(ch)][n] = np.array([])
        # create a list
        current_meas['ch{}'.format(ch)]['description'] = []
    return current_meas


def log_dc_pwr(dc_pwr, dc_pwr2, data, desc='none', config=None):
    """ measure current from CH1 and  CH1,CH2 of two PWR supplies channels and
        update into dictionary with timestamp (ms)
    """
    if config == '3dual' or config == 'boland_lab':
        # first supply
        for ch in [1, 2, 3]:
            data['ch{}'.format(ch)]['val'] = np.append(data['ch{}'.format(ch)]['val'],
                                            dc_pwr.get('meas_i', configs={'chan': ch}))
            data['ch{}'.format(ch)]['timestamp'] = np.append(data['ch{}'.format(ch)]['timestamp'], get_timestamp())
            data['ch{}'.format(ch)]['description'].append(desc)

    else:
        # first supply
        for ch in [1]:
            data['ch{}'.format(ch)]['val'] = np.append(data['ch{}'.format(ch)]['val'],
                                            dc_pwr.get('meas_i', configs={'chan': ch}))
            data['ch{}'.format(ch)]['timestamp'] = np.append(data['ch{}'.format(ch)]['timestamp'], get_timestamp())
            data['ch{}'.format(ch)]['description'].append(desc)
        # second supply
        for ch in [1, 2]:
            data['ch{}'.format(ch)]['val'] = np.append(data['ch{}'.format(ch)]['val'],
                                            dc_pwr2.get('meas_i', configs={'chan': ch}))
            data['ch{}'.format(ch)]['timestamp'] = np.append(data['ch{}'.format(ch)]['timestamp'], get_timestamp())
            data['ch{}'.format(ch)]['description'].append(desc)


def pwr_off(dc_pwrs):
    '''
    dc_pwrs: is a list of power supplies to turn off
    '''
    for dc_pwr in dc_pwrs:
        for ch in [1, 2, 3]:
            dc_pwr.set('out_state', 'OFF', configs={'chan': ch})


def config_supply(dc_pwr, dc_pwr2, setup=None, neg=16.5):

    if setup == '3dual':  # 3 channel capable supply
        # Channel 2, 3 setup (for +/-15V)
        for ch in [2, 3]:
            dc_pwr.set('i', 0.70, configs={'chan': ch})
            if ch == 3:
                dc_pwr.set('v', neg, configs={'chan': ch})
            else:
                dc_pwr.set('v', 16.5, configs={'chan': ch})
            dc_pwr.set('ovp', 16.7, configs={'chan': ch})
            dc_pwr.set('ocp', 0.70, configs={'chan': ch})
            dc_pwr.set('i', 0.60, configs={'chan': ch}) # for calibration testing. Increase due to relay current
        # Channel 1 on supply1 for Vin
        dc_pwr.set('i', 0.70, configs={'chan': 1}) # for calibration testing. Increase due to relay current
        dc_pwr.set('v', 7, configs={'chan': 1})
        dc_pwr.set('ovp', 7.2, configs={'chan': 1})
        dc_pwr.set('ocp', 0.75, configs={'chan': 1})

    elif setup == 'boland_lab':  # 3 channel capable supply
        # Channel 2, 3 setup (for +/-15V)
        for ch in [1, 2]:
            dc_pwr.set('i', 0.70, configs={'chan': ch})
            if ch == 1:
                dc_pwr.set('v', neg, configs={'chan': ch})
            else:
                dc_pwr.set('v', 16.5, configs={'chan': ch})
            dc_pwr.set('ovp', 16.7, configs={'chan': ch})
            dc_pwr.set('ocp', 0.70, configs={'chan': ch})
            dc_pwr.set('i', 0.60, configs={'chan': ch}) # for calibration testing. Increase due to relay current
        # Channel 1 on supply1 for Vin
        dc_pwr.set('i', 0.70, configs={'chan': 3}) # for calibration testing. Increase due to relay current
        dc_pwr.set('v', 5.3, configs={'chan': 3})
        dc_pwr.set('ovp', 5.5, configs={'chan': 3})
        dc_pwr.set('ocp', 0.7, configs={'chan': 3})

    else:
        # Channel 1 and 2 setup
        for ch in [1, 2]:
            dc_pwr2.set('i', 0.39, configs={'chan': ch})
            dc_pwr2.set('v', 16.5, configs={'chan': ch})
            dc_pwr2.set('ovp', 16.7, configs={'chan': ch})
            dc_pwr2.set('ocp', 0.400, configs={'chan': ch})

        # Channel 1 on supply1 for Vin
        dc_pwr.set('i', 0.55, configs={'chan': 1})
        dc_pwr.set('v', 7, configs={'chan': 1})
        dc_pwr.set('ovp', 7.2, configs={'chan': 1})
        dc_pwr.set('ocp', 0.75, configs={'chan': 1})
