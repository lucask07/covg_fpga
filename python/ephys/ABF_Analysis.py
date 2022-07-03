import pyabf
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog

#plt.ion()

UseGui = True
#Notify user to open abf file
if UseGui:
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    abf = pyabf.ABF(file_path)
else:
    abf = pyabf.ABF('LeakSubtraction.abf')

fig, (ax1, ax2)  = plt.subplots(2, sharex = 'col', sharey=False)

#0.07 - 0.15
print(abf.sweepY)
#print(np.where(np.logical_and(abf.sweepY>=0.07, abf.sweepY<=0.15)))
for sweepNumber in abf.sweepList:
    abf.setSweep(sweepNumber)
    ax1.plot(abf.sweepX, abf.sweepY)
    ax2.plot(abf.sweepX, abf.sweepC)
    print("Sweep " + str(sweepNumber) + " current average is " + str(np.average(abf.sweepY[594:610])))
    print("with a standard deviation of " + str(np.std(abf.sweepY[594:610])))

#plt.xlim(0.05, 0.16)
#plt.ylim(-5, 8)
plt.show()