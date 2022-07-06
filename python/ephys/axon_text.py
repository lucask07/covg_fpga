"""
Axon Text File (ATF) format module
Copyright (C) 2019 Christian Rickert <rc.email@icloud.com>
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNBESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
Version 1.0
"""

# imports
import warnings
import numpy as np


# functions

def read(in_file='atf'):
    """ read an atf file into a numpy array """
    try:
        with open(in_file, 'r') as in_data:
            full_record = []  # python list
            for _ in range(0, 2):
                full_record.append(in_data.readline().strip().split())  # first and second record
            full_record.append([in_data.readline().strip() for line in range(0, int(full_record[1][0]))])  # optional record
            full_record.append([in_data.readline().strip().split('\t')])  # title record
            full_record.append(np.genfromtxt(in_data, dtype='str', delimiter='\t', autostrip=True))  # data record, or: dtype='float'
    except FileNotFoundError:
        print("Error! File not found.")
        read_result = None
        raise
    else:
        read_result = np.array(full_record)  # ndarray.shape == (5,)
    return read_result

def write(out_file='atf', out_atf=np.zeros((5,))):
    """ write a numpy array into an atf file """
    try:
        with open(out_file, 'w') as out_data:
            for array in out_atf[0:2]:  # first and second record
                for element in array[0:-1]:
                    out_data.write(str(element) + '\t')
                out_data.write(str(array[-1] + '\n'))
            for array in out_atf[2]:  # optional record
                out_data.write(str(array) + '\n')
            for array in out_atf[3]:  # title record
                for element in array[0:-1]:
                    out_data.write(str(element) + '\t')
                out_data.write(str(array[-1]) + '\n')
            np.savetxt(out_data, np.stack(out_atf[4]), fmt='%s', delimiter='\t')  # or: dtype='%.7f'
    except PermissionError:
        print("Error! No file permission.")
        write_result = None
        raise
    else:
        write_result = 0  # success
    return write_result

def merge(in_atf_1=np.zeros((5,)), in_atf_2=np.zeros((5,))):
    """ merge two numpy arrays into one numpy array """
    title_columns_1 = str(len(in_atf_1[3][0]))
    title_columns_2 = str(len(in_atf_2[3][0]))
    _, data_columns_1 = in_atf_1[4].shape  # rows, columns
    _, data_columns_2 = in_atf_2[4].shape
    if title_columns_1 != title_columns_2 or data_columns_1 != data_columns_2:
        warnings.warn("Warning! Incompatible arrays.")
        merge_result = None
    else:
        optional_record = in_atf_1[2] + in_atf_2[2]
        comment_rows = str(len(optional_record) + 1)
        merge_record = []
        merge_record.append(["ATF", "1.0"])  # first record
        merge_record.append([comment_rows, title_columns_1])  # second record
        merge_record.append(optional_record)  # optional record
        merge_record.append(in_atf_1[3] + in_atf_2[3])  # title record
        merge_record.append(np.concatenate((in_atf_1[4], in_atf_2[4])))
        merge_result = np.array(merge_record)
    return merge_result

if __name__ == "__main__":  # stand-alone execution
    pass
    