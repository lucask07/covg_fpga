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
    """ compute the 2's complement of int value val
        handle an array (list or numpy)
    """

    # converts a val into 2's comp
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

def two2dec(num): # input the num we want to convert
    ''' Converts a 2's comp number to its dec. equivalent // two2dec fx
    found from stack overflow: https://stackoverflow.com/questions/1604464/twos-complement-in-python '''
    num = str(num) # temporarily change to a string so we can use indexing to find the weight of each bit's value on the whole
    if num[0] == '1': # if we have a negative number
        return -1 * (int(''.join('1' if x == '0' else '0' for x in num), 2) + 1) # find the equvalent of the negative number by evaluating the weight of each bit and concatenate w/negative 1
    else:
        return int(num, 2) # if pos, just turn into an int