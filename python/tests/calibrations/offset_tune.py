from array import array


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
lowestVal = closestValue - 0.03
for i in range (5):
    valueArray = np.append(valueArray, lowestVal)
    lowestVal += 0.01

for v_value in valueArray:
    dc_num = 0
    clamps[dc_num].DAC.write(data=from_voltage(voltage=v_value, num_bits=10, voltage_range=5, with_negatives=False))
    
