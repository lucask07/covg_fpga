import time
from fpga import FPGA
from drivers.utils import rev_lookup, bin, test_bit, twos_comp

regs = {}
regs['led'] =  {'wire': 0x00, 'lsb': 8, 'length': 7 }  
regs['ls'] =   {'wire': 0x02, 'lsb': 12, 'length': 6 }
regs['gpio'] = {'wire': 0x02, 'lsb': 0, 'length': 12}

def set_gpio(dev, name, val): 
    val = (val << regs[name]['lsb'])
    mask = (2**regs[name]['length'] - 1) << regs[name]['lsb']
    dev.set_wire(regs[name]['wire'], val, mask=mask)

'''
def read_gpio()
    self.xem.SetWireInValue(0x10, 0xff, 0x03)
    self.xem.UpdateWireIns()
'''

if __name__ == "__main__":

    f = FPGA()
    f.init_device()

    for test in ['led', 'gpio', 'ls']:

        # set the GPIOS 
        val = 0x555
        print('In 2 seconds will set the {} to 0x{:X}'.format(test, val))
        time.sleep(2)
        set_gpio(f, test, val)
        val = val >> 1
        print('In 2 seconds will set the {} to 0x{:X}'.format(test, val))
        time.sleep(2)
        set_gpio(f, test, val)
        time.sleep(2)


