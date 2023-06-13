"""
General analysis of COVG ADC data (h5 files)
Lucas Koerner: koerner.lucas@stthomas.edu

"""
import os
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import glob

from datastream.datastream import create_sys_connections, rawh5_to_datastreams, h5_to_datastreams

data_dir = 'C:\\Users\\koer2434\\Documents\\covg\\data\\clamp\\20230612\\'
filename = 'datastreams_output.h5'

sys.path.append('C:\\Users\\koer2434\\Documents\\covg\\my_pyabf\\pyABF\\src\\')
from pyabf.abfWriter import writeABF1 
from pyabf.tools.covg import interleave_np

datastreams = h5_to_datastreams(data_dir, filename)

ds_equal = datastreams.equalize_sampling(names=['Im', 'CMD0', 'V1', 'P1'])

t = ds_equal['Im'].create_time()

names_pclamp = ['Im', 'CMD0', 'V1', 'P1']
# if the current is in Amps the 16-bit precision makes it all zero 
im = np.reshape(ds_equal['Im'].data, (1,-1))*1e6
cmd = np.reshape(ds_equal['CMD0'].data, (1,-1))*1e3
v1 = np.reshape(ds_equal['V1'].data, (1,-1))*1e3
p1 = np.reshape(ds_equal['P1'].data, (1,-1))*1e3

x_write = interleave_np([im, cmd, v1, p1])
writeABF1(x_write, os.path.join(data_dir, 'test_step.abf'), 1/(t[1]-t[0]), 
           units=['uA', 'mV', 'mV', 'mV'], FLOAT = False, nADCNumChannels=4, names_input = names_pclamp)

im = np.reshape(ds_equal['Im'].data, (1,-1))
cmd = np.reshape(ds_equal['CMD0'].data, (1,-1))
v1 = np.reshape(ds_equal['V1'].data, (1,-1))
p1 = np.reshape(ds_equal['P1'].data, (1,-1))
x_write = interleave_np([im, cmd, v1, p1])

writeABF1(x_write, os.path.join(data_dir, 'test_step_float.abf'), 1/(t[1]-t[0]), 
           units=['A', 'V', 'V', 'V'], FLOAT = True, nADCNumChannels=4, names_input = names_pclamp)