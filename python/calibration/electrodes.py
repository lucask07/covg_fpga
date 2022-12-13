"""Module physical electrodes and their connections 

This module organizes electrode properties and calibrations 

Oct 2022

Lucas Koerner, koer2434@stthomas.edu
"""

class Electrode:
    """Class for an electrode.

    Attributes
    ----------
    name : str (for now use names in the Dagan COVG manual)
    dc_num : int (number of daughtercard)
    dc_pin : str [one of 'P2', 'P1', 'CC']
    nominal : dict {'res': , 'offset':}
    measured : dict {'res': , 'offset':}

    Methods
    -------


    """

    def __init__(self, name, dc_num, dc_pin,
                 nominal={'res': None, 'offset': 0},
                 measured={'res': None, 'offset': None}):
        # dc_num is the daughter card channel number since there are 0-3 channels

        self.name = name
        self.dc_num = dc_num
        if dc_pin not in ['P2', 'P1', 'CC']:
            print(f'Warning. Daughter-card pin {dc_pin} of electrode {name} is non-standard')
        self.dc_pin = dc_pin
        self.nominal = nominal
        self.measured = measured
        if dc_pin == 'CC':
            self.ac_coupled = True
        else:
            self.ac_coupled = False

    def __repr__(self):
        return str(vars(self))


class Dut:

    # The electrical properties of the device under test 
    #  (cell membrane)

    def __init__(self, 
                 nominal={'r': 4.7e6, 'c': 33e-9, 'i_leak': 0},
                 measured={'r': None, 'c': None, 'i_leak': None},
                 name=None):


class System: 
    
    def __init__(self, system='Dagan_no_guard'):

        self.electrodes = []
        self.system = system  # nickname of system configuration 
        self.dc_mapping = {'bath': 0, 'clamp': 1}

        if self.system == 'Dagan_no_guard':
            # voltage clamp board 
            e = Electrode(name='I', dc_num=1, dc_pin='P2',
                      nominal={'res':100e3, 'offset':0})
            self.electrodes.append(e)

            e = Electrode(name='V2', dc_num=1, dc_pin='P1',
                      nominal={'res':200e3, 'offset':0})
            self.electrodes.append(e)

            # bath clamp board 
            e = Electrode(name='P1', dc_num=0, dc_pin='P1',
                      nominal={'res':5e3, 'offset':0})
            self.electrodes.append(e)

            e = Electrode(name='P2', dc_num=0, dc_pin='P2',
                      nominal={'res':5e3, 'offset':0})
            self.electrodes.append(e)

            e = Electrode(name='CC', dc_num=0, dc_pin='CC',
                          nominal={'res':6.8e3, 'offset':0})
            self.electrodes.append(e)


    def find_item(self, key, value):
        return next((i for i, item in enumerate(self.electrodes) if getattr(item,key) == value), None)

    def find_name(self, value):
        return self.find_item('name', value) 