"""Module containing general functions useful to interfaces.

August 2021

Lucas Koerner, koer2434@stthomas.edu
Abe Stroschein, ajstroschein@stthomas.edu
"""

import numpy as np
import datetime

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


def to_voltage(data, num_bits, voltage_range, use_twos_comp=False):
    """Convert the binary read data into a float voltage.

    We use the bit-width of the data and the voltage range of the channel
    to determine the voltage per bit. Then we multiply the binary data by
    that voltage for the total voltage.

    Arguments
    ---------
    data : int or list(int)
        The method will return the converted version of either.
    voltage_range : int
        The total voltage range used for the data.
    use_twos_comp : bool
        True if the given data is in two's complement form, False otherwise.
    """

    if type(data) is list:
        # If the data is given in a list, we can use our int version of
        # the method on every element in the list.
        return [to_voltage(data=x, voltage_range=voltage_range) for x in data]
    elif type(data) is int:
        # Determine the voltage represented by a single bit
        bit_voltage = voltage_range / (2 ** num_bits)
        if use_twos_comp:
            return twos_comp(val=data, bits=num_bits) * bit_voltage
        else:
            return data * bit_voltage
    else:
        print(
            f'ERROR: wrong data type in to_voltage: type(data) = {type(data)} Expected int')
        return None


def from_voltage(voltage, num_bits, voltage_range, with_negatives=False):
    """Convert the float/int voltage into binary data.

    We use the bit-width and voltage range to determine the voltage per bit.
    Then we divide the voltage by the bit-voltage and round to an integer to
    find the binary data representation.

    Arguments
    ---------
    voltage : int or list(int)
        The method will return the converted version of either.
    voltage_range : int
        The total voltage range used for the voltage.
    with_negatives : bool
        True to convert the voltage with full negative at 0x0, zero at half
        scale, and full positive at full scale, False otherwise.
    """

    if type(voltage) is list:
        # If the voltage is given in a list, we can use our int version of
        # the method on every element in the list.
        return [from_voltage(voltage=x, voltage_range=voltage_range) for x in voltage]
    elif type(voltage) is int or type(voltage) is float:
        # Determine the voltage represented by a single bit
        if with_negatives:
            if voltage < -(voltage_range / 2):
                print(f'WARNING: Voltage {voltage} out of range [{-voltage_range / 2}-{voltage_range / 2}]. Truncating...')
                data = 0x0
            elif voltage > (voltage_range / 2):
                print(f'WARNING: Voltage {voltage} out of range [{-voltage_range / 2}, {voltage_range / 2}]. Truncating...')
                data = 2 ** num_bits - 1
            else:
                bit_voltage = voltage_range / (2 ** num_bits)
                data = round(voltage / bit_voltage)
                data = 2 ** (num_bits - 1) - 1 + data
        elif voltage < 0:
            print(f'WARNING: negative numbers not included in range [0, {voltage_range}]. Use with_negatives=True. Truncating...')
            data = 0x0
        elif voltage > voltage_range:
            print(f'WARNING: voltage {voltage} outside range [0, {voltage_range}]. Truncating...')
            data = 2 ** num_bits - 1
        else:
            bit_voltage = voltage_range / (2 ** num_bits)
            data = round(voltage / bit_voltage)

        return data
    else:
        print(
            f'ERROR: wrong voltage type in from_voltage: type(voltage) = {type(voltage)} Expected float or int')
        return None


def get_timestamp():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
