import numpy as np

def rev_lookup(dd, val):
    key = next(key for key, value in dd.items() if value == val)
    return key 

def bin(s):
    return str(s) if s<=1 else bin(s>>1) + str(s&1)

def test_bit(int_type, offset):
    mask = 1 << offset
    return ((int_type & mask) >> offset)

def gen_mask(bit_pos):

    if not hasattr(bit_pos, '__iter__'):
        bit_pos = [bit_pos]

    mask = sum([(1 << b) for b in bit_pos])
    return mask 

def twos_comp(val, bits):
    """compute the 2's complement of int value val
        handle an array (list or numpy)
    """

    def twos_comp_scalar(val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is

    if hasattr(val, "__len__"):
        tmp_arr = np.array([])
        for v in val:
            tmp_arr = np.append(tmp_arr, twos_comp_scalar(v,bits))
        return tmp_arr
    else:
        return twos_comp_scalar(val, bits)

