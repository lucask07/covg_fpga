"""Module containing general functions useful to interfaces.

August 2021

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu
"""

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


def reverse_bits(number, bit_width=8):
    """Return an integer with the reversed bits of the input number."""
    
    reversed_number = 0
    for i in range(bit_width):
        reversed_number <<= 1
        reversed_number |= number & 0b1
        number >>= 1
    return reversed_number


def count_bytes(num):
    """Count the number of bytes in a number."""

    bytes = 0
    if (num == 0):  # if the number equals 0
        return 1
    while (num != 0):  # bit shift 8 bits (byte)
        num >>= 8
        bytes += 1
    return bytes


def int_to_list(integer, num_bytes=None):
    """Convert an integer into a list of integers 1 byte long.
    
    The MSB will be at index 0 in the list.
    """

    list_int = []

    while integer != 0:
        # Take the least significant byte and append it to the list, then shift the integer right 1 byte.
        byte = integer % 2**(8)
        list_int.append(byte)
        integer >>= 8

    # In case integer began at 0.
    if len(list_int) == 0:
        list_int.append(0)

    if num_bytes is not None:
        # User entered a number of bytes
        # Check if the integer fits into the given number of bytes
        if num_bytes < len(list_int):
            return False
        else:
            # Fill the list with 0 for remaining bytes
            for i in range(num_bytes - len(list_int)):
                # Can append to the end because the list will be reversed in the return
                list_int.append(0)

    return list_int[::-1]
