'''A Script to convert any ABF to its used protocol and collect the other important recording setting'''
from os import truncate
from pickle import TRUE
import pandas as pd
import pyabf
import tkinter as tk
from tkinter import filedialog

UseGui = True
#Notify user to open abf file
if UseGui:
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    abf = pyabf.ABF(file_path)
else:
    abf = pyabf.ABF('LeakSubtraction.abf')

#iterate through epochs in abf and append data
initialEpoch = 'A'
epochColumn = ['A']
epochlist = []
for i in range(len(abf._epochPerDacSection.nEpochNum)):
    type = ''
    if abf._epochPerDacSection.nEpochType[i] == 1:
        type = 'Step'
    elif abf._epochPerDacSection.nEpochType[i] == 2:
        type = 'Ramp'
    else:
        type ='Off'
    temp_epochlist = [type, abf._epochPerDacSection.fEpochInitLevel[i], 
                 abf._epochPerDacSection.fEpochLevelInc[i], abf._epochPerDacSection.lEpochInitDuration[i] / 10, 
                 abf._epochPerDacSection.lEpochDurationInc[i]]
    epochlist.append(temp_epochlist)

#Convert array to Dataframe and transpose
df = pd.DataFrame(epochlist)
tdf = df.T

# create index and rows
tdf.index = ['Type', 'First level (mV)', 'Delta level (mV)', 'First Duration (ms)', 'Delta Duration (ms)']
for i in range(len(abf._epochPerDacSection.nEpochNum) - 1):
    epochColumn.append(chr(ord(initialEpoch) + 1))

#convert Dataframe to CSV file
tdf.columns = [epochColumn]
tdf.to_csv("Protocol.csv")
print (tdf)

'''Collecting other important recording settings usually booleans'''
class ProtocolSettings:

    def isLeakSubtractionOn():
        if abf._dacSection.nLeakSubtractType[0]:
            return True
        return False

    def getDACHoldingLevel():
        return abf._dacSection.fDACHoldingLevel[0]

    def getDataRate():
        return abf.dataRate