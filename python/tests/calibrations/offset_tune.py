from array import array
import numpy as np
import matplotlib.pyplot as plt

plt.ioff()

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

amp_out = np.array([])
v_value_array = [0.4, 0.6, 0.8]
for v_value in v_value_array:
    dc_num = 0
    clamps[dc_num].DAC.write(data=from_voltage(voltage=v_value, num_bits=10, voltage_range=5, with_negatives=False))
    amp_out = np.append(amp_out, read_data(False))
    

valueArray = np.array([])    

closestValue = find_nearest(amp_out, value = 0)
result = np.where(amp_out == closestValue)

#print(result[0][0])
voltageValue = v_value_array[result[0][0]]

lowestVal = voltageValue - 0.05
for i in range (5):
    valueArray = np.append(valueArray, lowestVal)
    lowestVal += 0.02

#Resets Round 1
valueList = valueArray.tolist()
amp_out = np.array([])


print(valueList)
for v_value in valueList:
    dc_num = 0
    clamps[dc_num].DAC.write(data=from_voltage(voltage=v_value, num_bits=10, voltage_range=5, with_negatives=False))
    amp_out = np.append(amp_out, read_data(False))

print(amp_out)

#Resets Round 2
closestValue = find_nearest(amp_out, value = 0)
result = np.where(amp_out == closestValue)
print(valueList[result[0][0]])
valueArray = np.array([])

lowestVal = valueList[result[0][0]] - 0.01
for i in range (5):
    valueArray = np.append(valueArray, lowestVal)
    lowestVal += 0.01
print(valueArray)


#Resets Round 3
valueList = valueArray.tolist()
amp_out = np.array([])

for v_value in valueList:
    dc_num = 0
    clamps[dc_num].DAC.write(data=from_voltage(voltage=v_value, num_bits=10, voltage_range=5, with_negatives=False))
    amp_out = np.append(amp_out, read_data(False))

closestValue = find_nearest(amp_out, value = 0)
result = np.where(amp_out == closestValue)
print(valueList[result[0][0]])


#Round 4
valueArray = np.array([])
lowestVal = valueList[result[0][0]] - 0.002
for i in range (5):
    valueArray = np.append(valueArray, lowestVal)
    lowestVal += 0.002
print(valueArray)

valueList = valueArray.tolist()
amp_out = np.array([])

for v_value in valueList:
    dc_num = 0
    clamps[dc_num].DAC.write(data=from_voltage(voltage=v_value, num_bits=10, voltage_range=5, with_negatives=False))
    amp_out = np.append(amp_out, read_data(False))

closestValue = find_nearest(amp_out, value = 0)
result = np.where(amp_out == closestValue)
print(valueList[result[0][0]])

#Round 5
valueArray = np.array([])
lowestVal = valueList[result[0][0]] - 0.0002
for i in range (5):
    valueArray = np.append(valueArray, lowestVal)
    lowestVal += 0.0002
print(valueArray)

valueList = valueArray.tolist()
amp_out = np.array([])

for v_value in valueList:
    dc_num = 0
    clamps[dc_num].DAC.write(data=from_voltage(voltage=v_value, num_bits=10, voltage_range=5, with_negatives=False))
    amp_out = np.append(amp_out, read_data(False))

closestValue = find_nearest(amp_out, value = 0)
result = np.where(amp_out == closestValue)
print(valueList[result[0][0]])