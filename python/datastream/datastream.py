"""

Abe Stroschein 
Lucas Koerner: koerner.lucas@stthomas.edu

Organize COVG data to prevent continuous reinvention of the wheel 
This file has some overlap with analysis.adc_data and eventually TODO may merge 

This will create a dictionary of datastreams.

Steps: 
0) configure experiment, DAQ board, and daughter cards - build a dict of configurations with 0,1,2,3 as keys 
1) create_sys_connections using daughter card configuration dictionaries 
2) capture data, store as "RAW h5"
3) run data_to_names and ADS conversions 
4) populate a "datastream h5" with sufficient attr to read into datastreams 
5) build the datastream dictionary 
6) make plots and run analysis off of the datastream dictionary 
7) test that later, in analysis, we can read in the "datastream h5" and know nothing else about the system configuration

"""
import os
import sys
import h5py
import numpy as np
from analysis.adc_data import read_h5, separate_ads_sequence

FS = 5e6
FS_ADS = 1e6 
SYS_CLK = 5e-9 # period (1/200 MHz)

class Datastream():

    def __init__(self, data, sample_rate, units=None, name = None, net=None, t0 = 0):
        self.data = data # 100% require that this data is in correct physical units
                         # such that all conversions have been completed
        self.sample_rate = sample_rate
        self.name = name # a name related assigned to the DAQ board / specific converter channel 
        self.net = net   # a name of the net related to the DUT and electrode connections  
        self.units = units
        self.initial_time = t0

    def create_time(self):
        return np.arange(len(self.data))*self.sample_rate + self.initial_time

    def plot(self, ax):
        ax.plot(self.create_time(), self.data)
        # TODO: allow for scaling of time to present in milliseconds or seconds  
        ax.set_xlabel('time [s]')
        ax.set_ylabel(f'{self.name} [{self.units}]')


def h5_to_datastreams(filename):
    return datastreams, info  


# def datastream_to_h5(datastreams, filename):
    # TODO: this could be a method of a datastreams class 


def rawh5_to_datastreams(data_dir, infile, data_to_names, ads_sequencer_setup, outfile = None):
    """
    parameters: 
        data_dir: directory for both input and output files 
        infile: name of input file (needs .h5 suffix)
        data_to_names: this is a method of the DDR, pass this in to complete
        phys_connection: dictionary of PhysicalConnections 
        outfile: name of output h5 file 

    returns: 
        datastreams 

    """

    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=infile, chan_list=np.arange(8))

    # Long data sequence -- entire file
    adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = data_to_names(chan_data)
    ads_separate_data = extract_ads_data(ads_data, ads_seq_cnt, ads_sequencer_setup)
    log_info = {'timestamp_step': timestamp[1]-timestamp[0],
                'timestamp_span': 5e-9*(timestamp[-1] - timestamp[0]),
                'read_errors': read_errors}

    datastreams = data_to_datastreams(adc_data, ads_data, dac_data, phys_connections, log_info)

    if outfile is not None:
        pass

    return datastreams, log_info  


def data_to_datastreams(adc_data, ads_separate_data, dac_data, phys_connections, log_info): 
    # TODO: only store adc_data that is connected -- create a "datastream h5"

    seq_len = len(ads_separate_data['A'])
    datastreams = {}

    # for each physical connection, create a datastream instance, add to h5  
    for pc_name in phys_connections:
        pc = phys_connections[pc_name]
        if pc.converter == 'AD7961':
            use_twos_comp = True
            data = np.array(to_voltage(adc_data[pc_name], num_bits=pc.bits, voltage_range=pc.conv_factor, use_twos_comp=use_twos_comp))
            sample_rate = FS
        elif pc.converter == 'ADS8686':
            use_twos_comp = False
            sample_rate = FS_ADS/seq_len
            data = np.array(to_voltage(ads_separate_data[pc_name[0]][pc_name[1]], 
                                       num_bits=pc.bits, voltage_range=pc.conv_factor, use_twos_comp=use_twos_comp))

        ds = Datastream(data, sample_rate, units=pc.units, name=pc_name, net=None, t0=0)

        datastreams[pc_name] = ds 

    return datastreams


def extract_ads_data(ads_data, ads_seq_cnt, ads_sequencer_setup):

    """
    Extract different channels from the ADS converter based on the sequencer setup 
    a dict with keys of 'A' and 'B' and values of np.array 
    turns into a dict of keys 'A' and 'B' that are dicts with keys of the channels '0', '1' that were in the sequencer
     """
    total_seq_cnt = np.zeros(len(ads_seq_cnt[0]) + len(ads_seq_cnt[1])) # get the right length
    total_seq_cnt[::2] = ads_seq_cnt[0]
    total_seq_cnt[1::2] = ads_seq_cnt[1]
    ads_separate_data = separate_ads_sequence(ads_sequencer_setup, ads_data, total_seq_cnt, slider_value=4)

    return ads_separate_data 

class PhysicalConnection():

    """
    A physical connection defines how named nets are connected to converters (ADCs or DACs)
    this connection depends upon the DAQ board being used and the conversion factor based on configurable 
    gain settings and the converter connected to. 

    These connections are agnostic to the connections to the DUT (and electrodes)
    """

    def __init__(self, node, conv_factor, converter, units, net=None):
        self.name = name 
        self.conv_factor = conv_factor # DN to physical units 
        self.converter = converter # name of the converter (eg AD7961)
        self.bits = bits 
        self.units = units 
        self.net = net

# Need physical system connectivity dictionary 

# I channels 0 - 3, node, conversion, factor 

def create_sys_connections(dc_config_dicts, daq_brd, ads, system='daq_v2'):

    # build up the connectivity to ADCs  
    # dc_config_dicts are dictionaries of the daughercard connectivity that are returned by configure_clamp
    # TODO: need an update_conv_factor method

    connections = {} 
    
    if system == 'daq_v2':
        ad7961_fs = 4.096*2 
        # ADC data 
        # 1) AD7961 - dictionary key is an integer [0, 3]
        for dc_config in dc_config_dicts:
            RF = dc_config_dicts[dc_config]['ADG_RES']
            inamp_gain = dc_config_dicts[dc_config]['gain']
            conv_factor = ad7961_fs/inamp_gain/RF
            connections[{dc_config}] = PhysicalConnection(f'I{dc_config}', 
                                                              conv_factor, 
                                                              converter='AD7961',
                                                              bits = 16, 
                                                              units='A')

        # 2) ADS8686
        ads_map = daq_brd.parameters["ads_map"]
        for dc_config in dc_config_dicts:
            for net in ['AMP_OUT', 'CAL_OUT']:
            if 'AMP_OUT':
                gain = dc_config_dicts[dc_config]['RF1']
            else:
                gain = 1
            if ads_map[dc_config][0] == 'A':
                ads_chan = 0
            else:
                ads_chan = 8
            ads_chan += int(ads_map[dc_config][1]) # channel goes from 0 - 15 for the voltage range 
            conv_factor = ads.ranges[ads_chan]*2/gain # ads.current_voltage_range is a len 16 list
            con_name = f'{ads_map[dc_config][0]}{ads_map[dc_config][1]}' # example 'A0' or 'B2'
            connections[con_name] = PhysicalConnection(f'{net}_{dc_config}', 
                                                        conv_factor, 
                                                        converter='ADS8686',
                                                        bits=16, 
                                                        units='V')

        # TODO 3) DAC data 

        return connections
    else:
        print(f'The system of {system} is not supported by create_sys_connections')

        return None
