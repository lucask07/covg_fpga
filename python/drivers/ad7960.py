import sys
from fpga import FPGA
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle as pkl 
from drivers.utils import rev_lookup, bin, test_bit, twos_comp, gen_mask

'''
TODO: why am I overriding the built-in bin in utils? 

'''
plt.ion()

from collections import namedtuple
ep = namedtuple('ep', 'addr bits type')
adc_reset = ep(0x01, [8,9,10,11], 'wi')  # note this is active low 
adc_en0 =   ep(0x01, [12,13,14,15], 'wi')
adc_en2 =   ep(0x01, 16, 'wi')
adc_pll_reset =  ep(0x01, 17, 'wi')
adc_fifo_reset = ep(0x01, [18,19,20,21], 'wi')

# wire outs for status 
adc_pll_lock =   ep(0x20, 8, 'wo')
adc_fifo_full =  ep(0x20, 9, 'wo')
adc_fifo_empty = ep(0x20, 10, 'wo')
pipe_out_rd_cnt = ep(0x20, [i+11 for i in range(10)], 'wo') # 10 bits 
ls_en = ep(0x20, 21, 'wo') # 10 bits 

# triggers out 
adc_pipe_rd_trig = ep(0x70, [3,4,5,6], 'to')

# pipeout (bits are meaningless)
# may change to array of addresses for each channel? 
adc_pipe = ep(0xA1, [i for i in range(32)], 'po') 

adc_chan = 0

def set_bit(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, mask, mask) # set
    f.xem.UpdateWireIns()

def clear_bit(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask) # clear
    f.xem.UpdateWireIns()

def toggle_low(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask) # toggle low 
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(ep_bit.addr, mask, mask)   # back high 
    f.xem.UpdateWireIns()

def toggle_high(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])
    f.xem.SetWireInValue(ep_bit.addr, mask, mask) # toggle high 
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask)   # back low 
    f.xem.UpdateWireIns()

def get_status(fpga):

    ''' 
    adc_pll_lock =   ep(0x20, 8, 'wo')
    adc_fifo_full =  ep(0x20, 9, 'wo')
    adc_fifo_empty = ep(0x20, 10, 'wo')
    pipe_out_rd_cnt = ep(0x20, [i+11 for i in range(10)], 'wo') # 10 bits 
    '''
    fpga.xem.UpdateWireOuts()
    a = fpga.xem.GetWireOutValue(adc_pll_lock.addr) 
    for s,n in [(adc_pll_lock, 'pll_lock'), 
                (adc_fifo_full, 'fifo_full'),
                (adc_fifo_empty, 'fifo_empty')]:
        v = test_bit(a, s.bits)
        print('Status {} = {} \n --------- \n'.format(n, v))

    fifo_cnt = (a >> pipe_out_rd_cnt.bits[0]) &  2**(len(pipe_out_rd_cnt.bits)-1)
    print('Data count in ADC FIFO = {}'.format(fifo_cnt))
    return a

def convert_data(buf):
    bits = 16 # for AD7961 bits=18 for AD7960
    d = np.frombuffer(buf, dtype=np.uint8).astype(np.uint32)
    if bits == 16:
        d2 = d[0::4] + (d[1::4] << 8)
    elif bits == 18:
        # not sure of this 
        d2 = (d[3::4]<<8) + d[1::4] + ((d[0::4]<<16) & 0x03)
        # d2 = (d[3::4]<<8) + d[1::4] + ((d[0::4]<<16) & 0x03)

    d_twos = twos_comp(d2, bits)
    return d_twos


def setup(fpga, enable_bits=13, pipe_offset = 1):
    # fpga.reset()
    fpga.reset_adc()
    fpga.adc_enable(enable_bits)
    time.sleep(0.02)
    fpga.adc_active()
    time.sleep(0.01)
    st = fpga.get_status()
    if not(test_bit(st, 2 + 8*pipe_offset)):
        print('ADC pipe out is full \n We can read data')
        # b,cnt = adc.ReadPipeOut(pipe_offset) 
        # d = np.frombuffer(d, dtype=np.uint32)
        # d_twos = twos_comp(d, 18)        

    # return d, d_twos, st
    return st

# test composite ADC function that enables, reads, converts and plots 
def adc_plot(fpga):
    s,e = fpga.read_pipe_out(addr_offset = 1)
    d = convert_data(s)
    plt.plot(d)
    plt.show()
    return d,s,e

def adc_stream_mult(adc, swps = 4):
    
    cnt = 0
    st = bytearray(np.asarray(np.ones(0, np.uint8)))  
    fpga.xem.UpdateTriggerOuts()
    
    while cnt<swps:
        if (fpga.xem.IsTriggered(0x60, 0x01)):
            s,e = adc.read_pipe_out()
            st += s 
            cnt = cnt + 1
            print(cnt)
        fpga.xem.UpdateTriggerOuts()

    d = convert_data(st)
    plt.plot(d)
    plt.show()
    return d


if __name__ == "__main__":
    print ('---FPGA ADC and DAC Controller---')
    f = FPGA()
    if (False == f.init_device()):
        raise SystemExit
    f.one_shot(1)

    # reset PLL 
    toggle_high(adc_pll_reset)
    clear_bit(adc_reset, adc_chan = adc_chan)
    # reset FIFO
    toggle_high(adc_fifo_reset)
    # enable ADC
    set_bit(adc_reset, adc_chan = adc_chan)
    set_bit(adc_en0, adc_chan = adc_chan)

    a = get_status(f)
    print(bin(a))
    time.sleep(1)
    a = get_status(f)
    print(bin(a))
    a = get_status(f)
    print(bin(a))


    d,s,e = adc_plot(f)