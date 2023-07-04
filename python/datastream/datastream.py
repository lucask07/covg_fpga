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
import copy
import datetime
import h5py
import json
import numpy as np
from scipy import signal
from pyripherals.utils import to_voltage, from_voltage, create_filter_coefficients
from analysis.adc_data import read_h5, separate_ads_sequence
from filters.filter_tools import butter_lowpass_filter
from control.matlab import stepinfo
sys.path.append('C:\\Users\\koer2434\\Documents\\covg\\my_pyabf\\pyABF\\src\\')
from pyabf.abfWriter import writeABF1 
from pyabf.tools.covg import interleave_np

FS = 5e6
FS_ADS = 1e6 
SYS_CLK = 5e-9 # period (1/200 MHz)

class Datastream():

    def __init__(self, data, sample_rate, units=None, name = None, net=None, t0 = 0, conv_factor = None):
        self.data = data # 100% require that this data is in correct physical units
                         # such that all conversions have been completed
        self.sample_rate = sample_rate
        self.name = name # a name related assigned to the DAQ board / specific converter channel 
        self.net = net   # a name of the net related to the DUT and electrode connections  
        self.units = units
        self.initial_time = t0
        self.conversion_factor = conv_factor # describes how to get back to DDR codes 

    def create_time(self):
        return np.arange(len(self.data))*(1/self.sample_rate) + self.initial_time

    def plot(self, ax, kwargs={}):

        t = self.create_time()
        invert = kwargs.pop('invert', 1)
        if 'fc' in kwargs:
            fs = 1/(t[1] - t[0])
            fc = kwargs.pop('fc', None) # default None should never happen
            data = invert*butter_lowpass_filter(self.data, fc, fs, order=kwargs.pop('order', 5))
        elif 'decimate' in kwargs:
            factors = kwargs.pop('decimate', None) # default None should never happen
            new_ds = self.decimate(factors)
            data = invert*new_ds.data 
            t = new_ds.create_time()
        else:
            data = invert*self.data

        l = ax.plot(t*1e6, data, **kwargs)
        # TODO: allow for scaling of time to present in milliseconds or seconds. Fixed at us
        ax.set_xlabel('time [$\mu$s]')
        if self.net is not None:
            ax.set_ylabel(f'{self.net} [{self.units}]')
        else:
            ax.set_ylabel(f'{self.name} [{self.units}]')
        return l

    def update_lines(self, line, kwargs={}):
        t = self.create_time()
        invert = kwargs.pop('invert', 1)
        if 'fc' in kwargs:
            fs = 1/(t[1] - t[0])
            fc = kwargs.pop('fc', None) # default None should never happen
            data = invert*butter_lowpass_filter(self.data, fc, fs, order=kwargs.pop('order', 5))
        elif 'decimate' in kwargs:
            factors = kwargs.pop('decimate', None) # default None should never happen
            new_ds = self.decimate(factors)
            data = invert*new_ds.data 
            t = new_ds.create_time()
        else:
            data = invert*self.data

        line.set_xdata(t*1e6)
        line.set_ydata(data)


    def get_impulse(self, t0=6553.6e-6, tl_tr=(-150e-6, 200e-6), fc=None):
        """ get the impulse of a trace produced by a step function by calculating the derivative
        """
        t = self.create_time()
        tlow = t0 + tl_tr[0]
        thigh = t0 + tl_tr[1]
        idx = ((t>=tlow) & (t<=thigh))
        t = t[idx]
        y = self.data[idx]

        if fc is not None:
            y = butter_lowpass_filter(y, cutoff=fc, fs=FS, order=5)

        #  the Wiener deconvolution adds noise to the denominator so that the result doesn't explode.
        # imp_resp_w = wiener_deconvolution(y, step_func)[:(len(y)-len(step_func) + 1)]
        # imp_resp_w = wiener_deconvolution(y, step_func)[:(248)]

        # An FFT-based deconvolution of a step response is fraught since the step response has a
        #  low information FFT. Large at f=0 and then constant at all other frequencies.
        #  seems better to simply take the derivative ... this gives the impulse response
        imp_resp_d = np.gradient(y, t[1]-t[0])
        return imp_resp_d, t, t0

    def decimate(self, factors = [10,10,10]):

        d_out = copy.deepcopy(self)

        total_factor = 1        
        for f in factors:
            d_out.data = signal.decimate(d_out.data, f)
            total_factor = total_factor*f
        d_out.sample_rate = d_out.sample_rate/total_factor

        return d_out
    
    def stepinfo_range(self, time_range):
        """
        get step info using the control systems toolbox stepinfo function
        specify a time range [in seconds] 
        """
        t = self.create_time()
        idx = (t>=time_range[0]) & (t<=time_range[1])
        if sum(idx) == 0:
            print('Error time range of {time_range} is not part of datastream')
            return None

        y = self.data[idx]
        t = t[idx]
        try:
            si = stepinfo(y, t)
        except:
            si = None

        return si

class Datastreams(dict):

    def __init__(self):
        self.set_time()

    def set_time(self):
        self.time = datetime.datetime.now().isoformat()

    def add_log_info(self, log_dict):
        for k in log_dict:
            setattr(self, k, log_dict[k])

    def to_h5(self, directory, filename, log_info):
        # write datastreams to a file 
        # filename must include the directory 
        full_file = os.path.join(directory, filename)
        with h5py.File(full_file, 'w') as f:
            grp = f.create_group('metadata') # TODO
            for dk in self:
                d_stream = copy.deepcopy(self[dk])
                dataset = f.create_dataset(d_stream.net, data=d_stream.data) # net must be a string 
                dstream_attrs = d_stream.__dict__
                dstream_attrs.pop('data', None)
                # get attributes from the datastream and set these attributes to the dataset 
                dataset.attrs.update(dstream_attrs)
                dataset.attrs.update(log_info) # should log_info itself be a dictionary key?
            
            grp.attrs['json'] = json.dumps(self.__dict__, default=vars)

    def get_log_info(self):
        """ 
        extract log info from datastreams and placed into a dict
        removes the data array (consumes the most disk space)
        but keeps the other info
        """
        log_dict = {}
        for dk in self:
            d_stream = copy.deepcopy(self[dk])
            dstream_attrs = d_stream.__dict__
            dstream_attrs.pop('data', None)
            # get attributes from the datastream and set these attributes to the dataset 
            log_dict.update(dstream_attrs)

        return log_dict

    def equalize_sampling(self, names):
        # first find the sampling rates 
        ds_new = copy.deepcopy(self)
        srs = []
        for n in names:
            srs.append(int(self[n].sample_rate))
        srs = np.array(srs)
        gcd = np.gcd.reduce(srs)  # TODO this doesn't work if the sampling rate is 1e6/3 (or similar)

        for n in names:
            sr = self[n].sample_rate
            if int(sr) == gcd:
                pass
            else:
                dec_factor = int(sr/gcd)
                print(f'Decimating {n} by {dec_factor}')

                if dec_factor > 10:
                    for num_try in [10,8,5,4,3,2]:
                        if dec_factor / num_try % 0:
                            factors = [num_try, dec_factor/num_try]
                            break
                else:
                    factors = [dec_factor]

                ds_new[n] = self[n].decimate(factors)

        return ds_new
    
    def append(self, append_ds):
        # append two datastreams in place  
        def check_same(ds1, ds2):
            # confirm that important properties are consistent
            all_same = True

            if ds1.sample_rate != ds2.sample_rate:
                all_same = False
            if ds1.conversion_factor != ds2.conversion_factor:
                all_same = False
            return all_same

        for n in self:
            if check_same(self[n], append_ds[n]):
                self[n].data = np.append(self[n].data, append_ds[n].data)
            else:
                print('error')
                break
        
    def crop(self, to_length):
        """
            reduce the length of a datastream useful when dividing into sweeps 

        Parameters
        ----------
        to_length : int
            final length after crop
        """
        for n in self:
            try:
                self[n].data = self[n].data[0:(to_length)]
            except:
                print(f'Error! Datastream length of {len(self[n].data)} cannot be cropped to length of {to_length}')

    def to_sweeps(self, num_sweeps):

        sweeps = [] # a list of datastreams 
        for i in range(num_sweeps):
            sweeps.append(copy.deepcopy(self))
        for n in self:
            split_data = np.split(self[n].data, num_sweeps) 
            for i in range(num_sweeps):
                sweeps[i][n].data = split_data[i]

        return sweeps        

    def to_clampfit(self, data_dir, filename, 
                    names_pclamp, dac_len, dac_sample_rate, sweeps=1):
        """
        names_pclamp: list (must include CMD0)
        
        """        
        ds_equal = self.equalize_sampling(names=names_pclamp)
        downsample_factor = int(dac_sample_rate/ds_equal['CMD0'].sample_rate)        
        ds_equal.crop(int(dac_len/downsample_factor))

        t = ds_equal['CMD0'].create_time()

        data_list = []
        units = []
        # if the current is in Amps the 16-bit precision makes it all zero 
        for n in names_pclamp:
            data_list.append(np.reshape(ds_equal[n].data, (1,-1)))
            units.append(ds_equal[n].units)
        x_write = interleave_np(data_list)
        x_write = np.reshape(x_write, (sweeps, -1))
        num_channels = len(names_pclamp)
        # the sample-rate is assumed to be divided among all ADC channels
        # so if we are sampling in parallel increase the sample rate by the number of channels
        writeABF1(x_write, os.path.join(data_dir, filename), 1/(t[1]-t[0])*num_channels, 
                units=units, nADCNumChannels=num_channels, FLOAT=True, names_input=names_pclamp)



def h5_to_datastreams(directory, filename):

    full_file = os.path.join(directory, filename)

    datastreams = Datastreams()
    with h5py.File(full_file, "r") as file:
        for dk in file.keys():
            if dk == 'metadata':
                t2 = json.loads(file[dk].attrs['json'])
                datastreams.add_log_info(t2)
            else:
                try:
                    ds = Datastream(file[dk][:],  # must use [:] to create a copy of the data so that the h5 file doesn't need to stay open
                                sample_rate=file[dk].attrs['sample_rate'], 
                                units=file[dk].attrs['units'], 
                                name=file[dk].attrs['name'], 
                                net=file[dk].attrs['net'], 
                                t0=file[dk].attrs['initial_time'])

                    datastreams[ds.net] = ds
                except:
                    print(f'skipping h5 key {dk}')

    return datastreams



def rawh5_to_datastreams(data_dir, infile, data_to_names, daq, phys_connections, outfile = None, out_log_info={}):
    """
    parameters: 
        data_dir: directory for both input and output files 
        infile: name of input file (needs .h5 suffix)
        data_to_names: this is a method of the DDR, pass this in to complete
        daq: the DAQ board object (to get info such as sequencer_setup)
        phys_connection: dictionary of PhysicalConnections 
        outfile: name of output h5 file 

    returns: 
        datastreams 

    """
    # to get the deswizzled data of all repeats need to read the file
    _, chan_data = read_h5(data_dir, file_name=infile, chan_list=np.arange(8))

    # Long data sequence -- entire file
    adc_data, timestamp, dac_data, ads_data_tmp, ads_seq_cnt, read_errors = data_to_names(chan_data)
    ads_separate_data = extract_ads_data(ads_data_tmp, ads_seq_cnt, daq.ADC_gp.sequencer_setup)
    log_info = {'timestamp_step': timestamp[1]-timestamp[0],
                'timestamp_span': 5e-9*(timestamp[-1] - timestamp[0]),
                'read_errors': read_errors}

    datastreams = data_to_datastreams(adc_data, ads_separate_data, dac_data, phys_connections, log_info)

    if outfile is not None:
        datastreams.to_h5(data_dir, outfile, {**log_info, **out_log_info}) # merge the two dictionaries of log info

    return datastreams, log_info  


def data_to_datastreams(adc_data, ads_separate_data, dac_data, phys_connections, log_info): 
    # TODO: only store adc_data that is connected -- create a "datastream h5"

    seq_len = len(ads_separate_data['A'])
    datastreams = Datastreams()

    # for each physical connection, create a datastream instance, add to h5  
    for pc_name in phys_connections:
        pc = phys_connections[pc_name]
        if pc.converter == 'AD7961':
            data = np.array(to_voltage(adc_data[pc_name], num_bits=pc.bits, voltage_range=pc.conv_factor, use_twos_comp=True))
            sample_rate = FS
        elif pc.converter == 'ADS8686' and (int(pc_name[1]) in ads_separate_data[pc_name[0]].keys()): # need to check that this converter was in the sequencer
            sample_rate = FS_ADS/seq_len
            data = np.array(to_voltage(ads_separate_data[pc_name[0]][int(pc_name[1])], 
                                       num_bits=pc.bits, voltage_range=pc.conv_factor, use_twos_comp=False))
        elif pc.converter == 'AD5453': 
            sample_rate = FS/2
            data_name = int(pc_name.replace('D',''))
            data = np.array(to_voltage(dac_data[data_name], 
                                       num_bits=pc.bits, voltage_range=pc.conv_factor, use_twos_comp=False))
            data = data - to_voltage(2**(pc.bits-1), 
                                     num_bits=pc.bits, voltage_range=pc.conv_factor, use_twos_comp=False)

        else:
            continue # don't add to datastream dictionary 
        ds = Datastream(data, sample_rate, units=pc.units, name=pc_name, net=pc.net, t0=0, conv_factor=pc.conv_factor/2**pc.bits)

        if pc.net is not None:
            datastreams[pc.net] = ds         
        else:
            datastreams[pc_name] = ds 
    conv_factor = phys_connections['D1'].conv_factor
    ds = Datastream(to_voltage(dac_data[4], num_bits=16, voltage_range=2**16, use_twos_comp=True), 1e6, units='DAC', name='OBSV', net='OBSV', t0=0, conv_factor=1)
    datastreams['OBSV'] = ds
    ds = Datastream(to_voltage(dac_data[5], num_bits=16, voltage_range=2**16, use_twos_comp=True), 1e6, units='DAC', name='OBSV_CH1', net='OBSV_CH1', t0=0, conv_factor=1)
    datastreams['OBSV_CH1'] = ds
    ds = Datastream(to_voltage(dac_data[6], num_bits=16, voltage_range=2**16, use_twos_comp=True), 1e6, units='DAC', name='PI_ERR', net='PI_ERR', t0=0, conv_factor=1)
    datastreams['PI_ERR'] = ds
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

    def __init__(self, name, conv_factor, converter, bits, units, net=None):
        self.name = name 
        self.conv_factor = conv_factor # DN to physical units 
        self.converter = converter # name of the converter (eg AD7961)
        self.bits = bits 
        self.units = units 
        self.net = net

# Need physical system connectivity dictionary 

# I channels 0 - 3, node, conversion, factor 

def create_sys_connections(dc_config_dicts, daq_brd, ephys_sys=None, system='daq_v2', calibration=False, inamp_gain_correct=None):

    # build up the connectivity to ADCs  
    
    # dc_config_dicts are dictionaries of the daughercard connectivity that are returned by configure_clamp
    # daq_brd is the daq object 
    # ephys_sys class EphysSystem from electrodes.py describes the particular system 
    # system: str the type of daq board. Only supported is daq_v2
    # calibration: bool if True removes specific net names like P2 from CAL_ADC since it will change based on relay settings 
    # inamp_gain_correct: function to correct the gain of the inamp 

    ads = daq_brd.ADC_gp
    connections = {}
    
    if system == 'daq_v2':
        ad7961_fs = 4.096*2 
        # ADC data 
        # 1) AD7961 - dictionary key is an integer [0, 3]
        for dc_config in dc_config_dicts:
            RF = dc_config_dicts[dc_config]['ADG_RES']*1e3 # all resistor values are in kilo-Ohms
            inamp_gain = dc_config_dicts[dc_config]['gain']
            if inamp_gain_correct is not None: #TODO make this a list for each daughtercard?
                inamp_gain = inamp_gain_correct(inamp_gain)
            diff_buffer_gain = 499/(1500+120) # daughter-card differential buffer (resistor values). Gain is less than x1
            conv_factor = -ad7961_fs/inamp_gain/RF/diff_buffer_gain # add negative sign so an increase in the cell voltage is positive current

            if ephys_sys is not None:
                dc_type = ephys_sys.dc_mapping[dc_config] 
                net = ephys_sys.daughtercard_to_net[dc_type]['AD7961']
            else:
                net = None

            pc = PhysicalConnection(f'{dc_config}', 
                                  conv_factor, 
                                  converter='AD7961',
                                  bits = 16, 
                                  units='A',
                                  net=net)
            connections[int(dc_config)] = pc


        # 2) ADS8686
        ads_map = daq_brd.parameters["ads_map"]
        for dc_config in dc_config_dicts:
            for amp_net in ['AMP_OUT', 'CAL_ADC']:
                if amp_net == 'AMP_OUT':
                    try:
                        v_sense_gain = dc_config_dicts[dc_config]['VSENSE']
                        gain = v_sense_gain*11
                    except:
                        gain = 11*(1+dc_config_dicts[dc_config]['RF1']/3.01)  # the AMP_OUT buffer has a gain of x11, the P1 buffer has a gain of 1+RF/3.01  [both resistors are in kOhms]
                else:
                    gain = 1
                if ads_map[dc_config][amp_net][0] == 'A':
                    ads_chan = 0
                else:
                    ads_chan = 8
                ads_chan += int(ads_map[dc_config][amp_net][1]) # channel goes from 0 - 15 for the voltage range 
                conv_factor = ads.ranges[ads_chan]*2/gain # ads.current_voltage_range is a len 16 list
                con_name = f'{ads_map[dc_config][amp_net][0]}{ads_map[dc_config][amp_net][1]}' # example 'A0' or 'B2'
                if ephys_sys is not None:
                    dc_type = ephys_sys.dc_mapping[dc_config]
                    if calibration and (amp_net=='CAL_ADC'):
                        net = 'CAL_ADC'
                    else:
                        net = ephys_sys.daughtercard_to_net[dc_type][amp_net]
                else:
                    net = None
                pc = PhysicalConnection(f'{net}_{dc_config}', 
                                        conv_factor, 
                                        converter='ADS8686',
                                        bits=16, 
                                        units='V',
                                        net=net)
                connections[con_name] = pc

        # P1 is the voltage that is actually at the membrane electrode (divided by gain of feedback amplifier)
        
        # CMD is the target membrane voltage with a closed-loop configuration
        # 3) DAC data -- AD5453, does not depend on daughtercard config, unsigned 
        for ch in range(4):
            net = daq_brd.parameters['fast_dac_map'][ch] 
            gain = daq_brd.current_dac_gain[ch] # +/-
            if gain > 99: # must by mV -- convert to volts
                gain = gain/1000
            if 'CMD' in net:
                gain = gain/(1 + dc_config_dicts[dc_config]['RF1']/3.01)/10 # TODO x10 is a property of the clamp board, can we have a parameter for this? 
            con_name = f'D{ch}'
            pc = PhysicalConnection(con_name, 
                                    gain*2,  # this is more accurately the full-scale range on the positive side
                                    converter='AD5453',
                                    bits=14, 
                                    units='V',
                                    net=net)
            connections[con_name] = pc
        
        return connections
    else:
        print(f'The system of {system} is not supported by create_sys_connections')

        return None
