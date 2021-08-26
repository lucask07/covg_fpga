from os import write
import matplotlib.pyplot as plot
from fpga import FPGA
import numpy as np
import struct
import time
import csv
import ok
import timeit

BLOCK_SIZE  = (16384)
WRITE_SIZE  = (8*1024*1024)
READ_SIZE   = (8*1024*1024)
g_nMemSize  = (8*1024*1024)
sample_size = (524288)
MB_SIZE     = 2.09

#Given the amplitude and period, returns an array to be plotted 
def make_sin_wave(amplitude_shift, frequency_shift=16):
    time_axis = np.arange (0, np.pi*2 , (1/sample_size*2*np.pi) )
    amplitude = (amplitude_shift*1000*np.sin(time_axis))
    y = len(amplitude)
    for x in range (y):
        amplitude[x]= amplitude[x]+(10000)
    for x in range (y):
        amplitude[x]= (int)(amplitude[x]/20000*16384)
    for x in range(y):
        amplitude[x] = amplitude[x]+5000
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

#given a buffer, it writes a bytearray to the DDR3
def writeSDRAM(g_buf):

    #Reset FIFOs
    f.set_wire(0x03, 0x0004)
    f.set_wire(0x03, 0x0000)
    f.set_wire(0x03, 0x0002)
    #for i in range ((int)(len(g_buf)/WRITE_SIZE)):
    r = f.xem.WriteToBlockPipeIn( epAddr= 0x80, blockSize= BLOCK_SIZE,
                                      data= g_buf[0:(len(g_buf))])

    #below sets the HDL into read mode
    f.xem.UpdateWireOuts()
    f.set_wire(0x03, 0x0004)
    f.set_wire(0x03, 0x0000)
    f.set_wire(0x03, 0x0001)

#reads to an empty array passed to the function
def readSDRAM():
    amplitude = np.zeros((sample_size,), dtype=int)
    pass_buf = bytearray(amplitude)
    #Reset FIFOs
    #below sets the HDL into read mode
    f.xem.UpdateWireOuts()
    f.set_wire(0x03, 0x0004)
    f.set_wire(0x03, 0x0000)
    f.set_wire(0x03, 0x0001)

    for i in range ((int)(g_nMemSize/WRITE_SIZE)):
        g = f.xem.ReadFromBlockPipeOut( epAddr= 0xA0, blockSize= BLOCK_SIZE,
                                      data= pass_buf)

def infile_func(self, infile, outfile):
    # RAM test
    fileIn = open(infile, "rb")
    fileOut = open(outfile, "wb")

    # Reset the RAM address pointer.
    self.xem.ActivateTriggerIn(0x41, 0)

    while fileIn:
        buf = bytearray(fileIn.read(2048))

        got = len(buf)
        if (got == 0):
            break

        if (got < 2048):
            buf += b"\x00"*(2048-got)

        # Write a block of data.
        f.xem.ActivateTriggerIn(0x41, 0)
        f.xem.WriteToPipeIn(0x80, buf)

        # Perform DES on the block.
        f.xem.ActivateTriggerIn(0x40, 0)

        # Wait for the TriggerOut indicating DONE.
        for i in range(100):
            f.xem.UpdateTriggerOuts()
            if (f.xem.IsTriggered(0x60, 1)):
                break

        f.xem.ReadFromPipeOut(0xa0, buf[0:1])
        fileOut.write(buf[0:1])

    fileIn.close()
    fileOut.close()

def test_infile(configured_fpga, text):
    with open('infile.txt', 'w') as infile:
        infile.write(text)

    infile_func(f, 'infile.txt', 'outfile.txt')

    with open('outfile.txt', 'r') as outfile:
        output = outfile.read()

    if text == output.split('\x00')[0]:
        print("The write/read test was a success")
    else:
        print("The write/read test didnt work")

#given an amplitude and a period, it will write a waveform to the DDR3
def write_sin_wave (a):
    time_axis, g_buf_init = make_sin_wave(a)
    pass_buf = bytearray(g_buf_init)
    d = writeSDRAM(pass_buf)
    return d

if __name__ == "__main__":

    f = FPGA(bitfile = 'Speedtest.bit')
    if (False == f.init_device()):
        raise SystemExit
    #Wait for the configuration
    time.sleep(3)
    factor = (int)(sample_size/8)
    f.set_wire(0x04, factor)
    f.set_wire(0x02, 0x0000A000, 0x0003FF00 )
  
    Header        = ["Read/Write", "Test Number"]
    write_speed   = ["Write", 1]
    write_speed2  = ["Write", 2]
    write_speed3  = ["Write", 3]
    read_speed    = ["Read", 1]
    read_speed2   = ["Read", 2]
    read_speed3   = ["Read", 3]
    average_write = ["Average write", 1]
    average_read  = ["Average read", 1]
    test_infile(f, 'a')
    a, b = make_sin_wave(3)
    before = time.time()
    for x in range (6):
        BLOCK_SIZE = (512*(2**(x)))
        Header.append(BLOCK_SIZE)
        write_speed.append((int)(MB_SIZE//((timeit.timeit('writeSDRAM(b)', globals=globals(), number =20))/20)))
        read_speed.append((int)(MB_SIZE//((timeit.timeit('readSDRAM()', globals=globals(), number =20))/20)))
        write_speed2.append((int)(MB_SIZE//((timeit.timeit('writeSDRAM(b)', globals=globals(), number =20))/20)))
        read_speed2.append((int)(MB_SIZE//((timeit.timeit('readSDRAM()', globals=globals(), number =20))/20)))
        write_speed3.append((int)(MB_SIZE//((timeit.timeit('writeSDRAM(b)', globals=globals(), number =20))/20)))
        read_speed3.append((int)(MB_SIZE//((timeit.timeit('readSDRAM()', globals=globals(), number =20))/20)))
    after = time.time()
    for x in range (6):
        y = (int)(((int)(read_speed[x+2])+(int)(read_speed2[x+2])+(int)(read_speed3[x+2]))/3)
        average_read.append(y)
        b = (int)(((int)(write_speed[x+2])+(int)(write_speed2[x+2])+(int)(write_speed3[x+2]))/3)
        average_write.append(b)
    elapsed = (after-before)
    Average_speed = 0
    for x in range(6):
        Average_speed = (Average_speed + (int)(average_read[x+1]))
    for x in range (6):
        Average_speed = (Average_speed + (int)(average_write[x+1]))
    Average_speed/=12
    Transfer_time = (1504/Average_speed)
    divisor = (Transfer_time-elapsed)
    end_percentage = (divisor/(elapsed))
    print("Percentage of transfer spent in downtime: ", (int)(end_percentage*100), "%")

    with open('Speedtest.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)


        writer.writerow(Header)
        writer.writerow(read_speed)
        writer.writerow(read_speed2)
        writer.writerow(read_speed3)
        writer.writerow(write_speed)
        writer.writerow(write_speed2)
        writer.writerow(write_speed3)
        writer.writerow(average_read)
        writer.writerow(average_write)


