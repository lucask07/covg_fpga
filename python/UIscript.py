from interfaces.interfaces import AD7961, ADS8686
from PyQt5 import QtWidgets, QtCore
from scipy import signal
import pyqtgraph as pg
from interfaces.interfaces import FPGA
import numpy as np
import threading
import datetime
import platform
import time
import json
import h5py
import sys
import os

#File locations determined by the user, bitfile can be changed
save_hdf5         = 'C:/Users/nalo1/Downloads/HDF5'
save_json         = 'C:/Users/nalo1/Downloads/Metadata'
bitfile_used      = 'counterfile.bit'

#Times and dates are set at the start of the experiment
start_time        = time.time()
now               = datetime.datetime.now()
current_time      = now.strftime("%H_%M_%S")
pipe_addr         = 0x80
data_set          = []
clock_divs        = []
clock_divider     = []
user_scaling      = []
notes             = []
adc_list          = []
SAMPLE_SIZE       = (524288)
BLOCK_SIZE        = (16384)

#makes the dataset scalable, needs to be called by main
def create_dataset():
    for x in range (len(adc_list)):
        data_set.append([])
        clock_divs.append(10)
        clock_divider.append(0)
        user_scaling.append(1)

#Initialize the FPGA for calls to "f"
def config():
    f = FPGA(bitfile = bitfile_used)
    if (False == f.init_device()):
        print("Configuration failed")
    return f

#returns a dictionary of metadata for JSON file creation
def get_meta_data():
    meta_dict = {
        "Time"                  : (str)(current_time),
        "Date"                  : "{:%d, %b %Y}".format(datetime.date.today()),
        "Firmware version"      : f.xem.GetDeviceMajorVersion(),
        "Product"               : f.xem.GetBoardModel(),
        "Product Serial Number" : f.xem.GetSerialNumber(),
        "Device ID"             : f.xem.GetDeviceID(),
        "OS"                    : platform.system(),
        "OS Version"            : platform.version(),
        "Notes"                 : notes
    }
    return meta_dict

#Called by mainthread to create a graphing window for each ADC listed
def main_loop():
    if (f.xem.NoError != f.xem.OpenBySerial("")):
            print ("You can't run the software if no device is detected")
            return(False)
    else:
        app= QtWidgets.QApplication(sys.argv)
        obj_list = []
        for x in range(len(adc_list)):
            if (adc_list[x].used):
                obj = MainWindow(chan=adc_list[x].number)
                obj.show()
                obj_list.append(obj)

        app.exec_()

#graphing window class, called by each object instantiation
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self,chan,*args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.chan=chan
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.x = list(range(100))  # 100 time points
        self.y = [0 for _ in range(100)]  # 100 data points
        self.graphWidget.setBackground('w')
        self.setWindowTitle("Channel " + (str)(self.chan))
        self.setGeometry((500*self.chan), 50, 500, 300)
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        #closing the graph window(with the drop down menu)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    #Called by each mainwindow object by QTimer()
    def update_plot_data(self):
        if (adc_list[self.chan].used):
            #d = adc_list[self.chan].chip.read(f)
            d=5
            time_of_read = f.get_time()
            data_set[self.chan].append([d, time_of_read])
            #d = signal.decimate(d, adc_list[self.chan].downsample_factor)
            global clock_divider
            global user_scaling
            clock_divider[self.chan]+=1
            if (clock_divider[self.chan]==clock_divs[self.chan]):
                clock_divider[self.chan]=0
                self.x = self.x[1:]  # Remove the first y element.
                a=(self.x[-1]+1)
                self.x.append(a)
                self.y = self.y[1:]  # Remove the first
                self.y = np.append(self.y, np.mean(d)*user_scaling[self.chan])
                self.data_line.setData(self.x, self.y)
     
#Given a buffer and DDR address, writes to SDRAM
def writeSDRAM(g_buf, address):
    #Reset FIFOs
    f.set_wire(0x30, 4)
    f.set_wire(0x03, 0)
    f.set_wire(0x03, 2)

    r = f.xem.WriteToBlockPipeIn( epAddr= address, blockSize= BLOCK_SIZE,
                                      data= g_buf[0:(len(g_buf))])
    if (r>0):
        print("Write was a success")
    else:
        print ("Write was a failure")
    #below sets the HDL into read mode
    f.set_wire(0x03, 4)
    f.set_wire(0x03, 0)
    f.set_wire(0x03, 1)

#Given the amplitude and period, returns an array to be plotted 
def make_sin_wave(amplitude_shift):
    time_axis = np.arange (0, np.pi*2 , (1/SAMPLE_SIZE*2*np.pi) )
    amplitude = (amplitude_shift*1000*np.sin(time_axis))
    for x in range (len(amplitude)):
        amplitude[x] = amplitude[x]+(10000)
    for x in range (len(amplitude)):
        amplitude[x] = (int)(amplitude[x]/20000*16384)
    amplitude = amplitude.astype(np.int32)
    byteamp = bytearray(amplitude)
    return byteamp

#Given a single 14-bit value, writes full data set at that DAC value
def make_flat_voltage(input_voltage):
    amplitude = np.arange (0, np.pi*2 , (1/SAMPLE_SIZE*2*np.pi) )
    for x in range (len(amplitude)):
        amplitude[x] = input_voltage
    amplitude = amplitude.astype(np.int32)
    byteamp = bytearray(amplitude)
    return byteamp

#Creates both an HDF5 file with data, and JSON with metadata
def filemaker():
    hdf5_name = os.path.join(save_hdf5,"OPAMPDATA" + (str)(current_time)+ ".hdf5")
    hf  = h5py.File(hdf5_name, 'w')
    for x in adc_list:
        hf.create_dataset((str)((str)(x)+ "dataset"), data=data_set[x.number])
    hf.close()

    data = get_meta_data()
    json_name = os.path.join(save_json,'metadata' + (str) (current_time) + ".json")
    with open (json_name, 'w') as outfile:
        json.dump(data, outfile)

#Object creation for each chip, look at interfaces.py for more reference
class DisplayChip:
    def __init__(self, chip, number,  used, downsample_factor):
        self.chip = chip
        self.number = number
        self.used = used
        self.downsample_factor = downsample_factor

'''
This block will contain the writable commands, useful to the UI
'''

#Writes a single flat voltage to the DDR3
def write_flat_voltage(voltage):
    writeSDRAM(make_flat_voltage(voltage), pipe_addr)
    note = ("Flat voltage of voltage ", voltage, " written to the DDR3")
    add_note(note)
    
#Writes a single period of a sin wave to the DDR3
def write_sin_wave(voltage):
    writeSDRAM(make_sin_wave(voltage), pipe_addr)
    note = ("Sin wave of voltage ", voltage, " written to the DDR3")
    add_note(note)

#Used at any time to update the HDF5 file with the data collected
def save_data():
    print("Saving data...")
    filemaker()
    print ("Data saved to: ", save_hdf5)
    note = ("Data saved at time: ", (str)(current_time) )

#Used to change the SPI clockedge 
def change_clock():
    f.xem.WriteRegister(0x80000010, 0x00003410)
    f.xem.ActivateTriggerIn(0x40, 8)
    print("Clocking edge changed")
    add_note("SPI clockedge changed")

#Changes the scaling of the outputs
def change_scaling(scaling, channel):
    global user_scaling
    user_scaling[channel] = scaling
    note = ("Scaling of channel ", channel, " changed to ", scaling)
    add_note(note)

#Given the graphing channel, pick which channel to stop pulling data and graphing from 
def stop_ADC(channel):
    adc_list[channel].used = False
    note = ("Channel ", channel, " stopped")
    add_note(note)

#Given a paused ADC channel, it will resume the graphing and data retention
def resume_ADC(channel):
    adc_list[channel].used = True
    note = ("Channel ", channel, " resumed")
    add_note(note)

#Given two integer values, will chnage the update speed of the graph for a specific channel
def change_update_speed(factor, channel):
    clock_divs[channel] = factor
    global clock_divider
    clock_divider[channel] =0
    note = ("Update speed of channel ", channel, " changed to ", factor)
    add_note(note)

#Given a factor and a channel, change the downsampling of the graphing window
def downsample_change(factor, channel):
    adc_list[channel].downsample_factor = factor
    note = ("Chanel ", channel, " changed to downsample factor ", factor)
    add_note(note)

#Given a factor, downsample all of the channels to that value
def all_factors(factor):
    for x in adc_list:
        x.downsample_factor= factor
    note = ("All factors changed to ", factor)
    add_note(note)

#Given a string, it will append it to the notes eventually dumped into the JSON file
def add_note(note):
    notes.append(note)

#Given a value, changes the channel of the given chip
def chan_select(display_chip, channel):
    if hasattr(display_chip.chip, 'channel'):
        display_chip.chip.channel = channel
        note =("Chip ", (str)(display_chip), " changed to channel ", channel)
        add_note(note)
    else:
        print(display_chip, "has no attribute channel")

    
'''
End of command block, main loop to start thread and set wire ins
'''

if __name__ == "__main__":
    f=config()

    ad7961            = DisplayChip(AD7961(f),  0, False,  1)
    ads8686           = DisplayChip(ADS8686(f), 1, True,   1)
    adc_list          = [ad7961, ads8686]
    for x in adc_list:
        if(x.used):
            x.chip.setup()
    create_dataset()
    GRAPHING_THREAD = threading.Thread(target=main_loop)
    GRAPHING_THREAD.start()

    #Wait for the configuration
    time.sleep(3)

    #Set the HDL indexing value, and HDL sampling rate
    factor = (int)(SAMPLE_SIZE/8)
    f.set_wire(0x04, factor)
    f.set_wire(0x02, 0x0000A000, 0x0003FF00 )
