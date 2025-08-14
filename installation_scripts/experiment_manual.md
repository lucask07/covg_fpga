# Experiment Manual
<!-- Start from page 45-46 -->
## Hardware setup
One improvement that has been made to this software is the ability to power on and configure the hardware device separately from running multiple experiments on the very same hardware configuration, which is where the `HardwareSetUp` class comes in handy. This class provides various functionalities and methods to serve various purposes in FPGA-hardware configuration. For more details, visit `covg_fpga/python/tests_solidify/bathclamp_vclamp_utils.py`. Note that the `HardwareSetUp` class supports [method chaining](https://www.geeksforgeeks.org/python/method-chaining-in-python/), meaning users do not need to refer to this class's object variable repeatedly. The script in `covg_fpga/python/tests_solidify/bath_clamp_setup_steps.py` provides an example of how to make use of method chaining from the `HardwareSetup` class and also serves as the default hardware configuration, so if there are no extreme cases that demand a different set up procedure, such a default set-up has been enough for later experiments. Here is how to execute the default hardware set-up in the Ipython terminal once it is in `covg_fpga/python/tests_solidify` directory:

```py
>> from bath_clamp_setup_steps import *
>> hardware = device_setup(allfour=True)
```
Depending on if there is a need to power the voltage sense daughtercard, `allfour` can be set accordingly. Notice that in the same directory, the `system_setup.json` contains essential parameters for hardware set-up process and will be treated as constants across the experiments, so users should modify those parameters according to their needs before powering the hardware using scripts.

For later experiments, that `hardware` reference will be registered as an argument for the functions representing those experiments. Users can refer to the section [Bath/Guard Headstage](#bathguard-headstage).

After all, the most important thing to know if the system has been successfully set up is the reports of four HDMI sockets. Check the output where it goes:

```
------------Clamp 0 Init-----------
TCA_0 register: OUTPUT FAILED
    (read_out) None != (default) 255
------------Clamp 1 Init-----------
TCA_0 register: OUTPUT FAILED
    (read_out) None != (default) 255
------------Clamp 2 Init-----------
TCA_0 register: POLARITY FAILED
    (read_out) 255 != (default) 0
------------Clamp 3 Init-----------
TCA_0 register: POLARITY FAILED
    (read_out) 255 != (default) 0
```
Pay attention to the `(read_out)` code. If it is anything else besides 255 or `None`, the boards have been correctly initialized. If it is either code 255 (board detectable, but failed to gain relay controls), or `None` (board not detectable), it likely appears that the DAQ board is not correctly functional. One way to inspect the DAQ board in this scenario is to measure the $I^2C$ traffic individually for each HDMI socket. __The example given above shows that all sockets have failed__.

## Headstage
### Bath/Guard Headstage
Notice the P1, P2, CC, GS1, and GS2 ports on the bathclamp. In the model cell there are 5 corresponding ports to those 5 on the bathclamp, with the first consecutive two for GS1 and GS2 (symmetrical, meaning they can interchange) and the remaining consecutive three for P1, P2, and CC. Of the latter, the middle one is colored red reserved for P2, so connect accordingly. P1's port is the one outermost, so the remaining one is for CC.

#### Experiment execution
Once the working directory has been moved to `covg_fpga/python/tests_solidify`, run the headstage calibration script with the command:

```py
>> from bath_clamp_headstage import Headstage, experiment
>> # Note that earlier on I said the `hardware` object would be registered as an argument 
>> # into the experiments' functions. Here is one representative example!
>> headstage = experiment(hardware, <vsense_lowergain>, <vsense_uppergain>)
```
with `<vsense_lowergain>` and `<vsense_uppergain>` are two gain values for the voltage sense's TCA, whose details can be found in the `Vsense2` class in the `covg_fpga/python/boards.py` file.

However, if users want to go ahead and execute the calibration right away without first having to power and configure the hardware, they can refer to this wrapper operation instead:

```py
>> from try_out_vsense_gains import headstage_experiment
>> # Note that this function also returns a `Headstage` object!
>> headstage = headstage_experiment(<lowergain_clamp>, <uppergain_clamp>)
```
Now, this new lightweight operation does provide one advantage ahead of configuring hardware and experimenting separately: It will automatically clean all `.h5` files resulting after the current calibration experiment which take up a lot of hard disk memory resources and if it ran out, the `experiment()` function would raise a `PermissionError`. Thus, in case users want to keep those `.h5` files for later exploitation, they can use the former two-step operation (but please make sure to clean up `.h5` files when they are not in use), or else they are advised to use the latter straight to a fault operation that also takes care of memory resources.

The `headstage` variable is the reference to the object of class `Headstage` that stores the history of the current calibration procedure. Three dictionaries of interests are `Headstage.EXPERIMENTS`, `Headstage.RELAYS_DAQS`, and `Headstage.FIT_RESULTS`, which bundles all logs and traces throughout the calibration as a whole, stores the history of the relays states for all active daughtercards for every subexperiment, and stores fit statistics reports, respectively. Talking about subexperiments, there are four in total, including **_Bath's resistance measurement, Bath's transfer function fitting, Clamp's resistance measurement, and finally Clamp's transfer function fitting_**, in order of occurrence throughout the calibration process. These four will be four keys of all those three dictionaries.

#### Post-calibration inspection
After this calibration script runs, users are encouraged to try inspecting these three logging dictionaries by typing these lines into the current working IPython terminal:

```py
>> headstage.EXPERIMENTS
>> headstage.RELAYS_DAQS
>> headstage.FIT_RESULTS
```
However, if storing these dictionaries as history logging files is desired, the `Headstage` class also provides a method named `Headstage.save_log(logtype= Literal["all", "fit_notes", "relays_DAQs"], filename = None)`, which can be invoked in the current working IPython terminal as:

```py
>> # If desire to save all bundled information about the last calibration experiment
>> headstage.save_log("all") # OR
>> headstage.save_log("all", filename="calibration.json") # if want to custom file name, but its extension must be .json
>>
>> # If desire to save the relays states for all daughtercards
>> headstage.save_log("relays_DAQs") # OR
>> headstage.save_log("relays_DAQs", filename="relay_calibration.json") # custom file name, must end with .json
>>
>> # If desire to save general fit statistics for all four subexperiments
>> headstage.save_log("fit_notes") # OR
>> headstage.save_log("fit_notes", filename="fitstats_cal.json") # custom file name, must end with .json
```
All those are going to export a logging `.json` file to the current working directory.

One simplification compared to the traditional calibration script is there will be no active Matplotlib's plots during and after the calibration experiment! That is because a large number of active plots will make any new plot harder to be allocated into Matplotlib's UI memory resources, and also likely lead to memory leakage. Hence, all those plots instead have been moved to a directory, named `~/Documents/covg/manuscripts/covg_methods/digital_amp_manuscript/overleaf/figures/bathclamp_headstage`, which has also been organized according to four temporal phases of the calibration experiment, making figure inspection more convenient. Also, note that at the end of the calibration experiment, the output log also tells users where to inspect those plots:

```
# CODE OUTPUT GOES HERE
```
Inspecting those figures only takes about less than 3 seconds to know if the system has been set up as expected, that is, if all the measured data points (represented as dots in the plots) are snuggly fitted onto the predicted lines (represented as lines, please look at the legends as they provide a pretty clear guide). One thing that can be inferred from the **fit notes** for the transfer function fits, though, is if the Chi-squared values are low enough ($< 0.05$ is OKAY).

#### Advanced Data Exploration & Inspection
Although the Resistance Measurement has not provided any advanced tool tip yet besides plots, the Transfer Function Fits for both bath and clamp do produce three datasets (2 for bath, another for clamp) that list measured and predicted value at each controlled frequency. They also inform about the two values (`DAC` and `DAC Wave`) whose ratio is the actual measured Amplitude value for each frequency against the predicted Amplitude. Such datasets are `.xlsx` files and can be found at the `~/Documents/covg/fpga_and_measurements/daq_v2/data` directory. __Nevertheless, such data exportions for the Resistance Measurements should be the main focus for future codebase maintainers to develop!__

It is also critical to know if the data pipelines in the DAC and TCA for all daughtercards are smooth and not disrupted at any cost. In other words, what was written to those should also be what they will read out. For example, the `Headstage` class also provides a `Vsense2` member, allowing users to directly access and change its DAC and TCA writes for subsequent read tests:
```py
>> headstage.vsense.DAC.write(122)
>> headstage.vsense.DAC.read()
[Out 1]: (122, 0)
>>
>> # This allows for setting the gain values for TCA
>> headstage.vsense.set_gain(31, 31)
>> headstage.vsense.TCA.read()
[Out 2]: [0, 0]
```
For that purpose, the `ReadTest` class (visit `python/tests_solidify/DAC_TCA_reads_test.py`) assists the DAC and TCA read tests with a more informative logging output. Some essential functionalities include:
* `add_board(board : Optional[Union[Daq, Clamp]], name=None, allow_DAC_write=False, allow_TCA_write=False, TCA_write=0b000, DAC_write=0b000)`: 
    Adding one more daughtercard (bath/guard/clamp/vsense) to the testing system, with an optional custom name. If changing the writes to TCA or DAC before adding to the testing system is desired, set `allow_DAC_write` to `True` or `allow_TCA_write` to `True` and then set the writes accordingly. Otherwise, ignore the latter 4 arguments.
* `get_log()`:
    This method is straightforward, just call it, all information about DAC/TCA reads for every daughtercard will be parsed and logged in an organized manner to the program's output!

For example, the `HardwareSetup` object (stored in the `hardware` variable) has a `clamps` list of all active daughtercards (instance of `Clamp` class, visit `covg_fpga/python/boards.py`). However, it is crucial to be informed about at which index each daughtercard is stored. Fortunately, the `hardware.dc_mapping` dictionary stores the map of those daughtercards to their corresonding indices in the `clamps` list, as illustrated in this code snippet below. Then users can add them one by one, change the writes as necessary, to the testing system:

```py
>> from DAC_TCA_reads_test import ReadTest
>> # Note that voltage sense daughtercard will have the `vclamp` shorthand!
>> hardware.dc_mapping
[Out 1]: bidict({'bath': 0, 'guard': 1, 'vclamp': 2, 'clamp': 3})
>> bath = hardware.clamps[hardware.dc_mapping['bath']]
>> guard = hardware.clamps[hardware.dc_mapping['guard']]
>> clamp = hardware.clamps[hardware.dc_mapping['clamp']]
>> vclamp = hardware.clamps[hardware.dc_mapping['vclamp']]
>> # Now add them accordingly to the ReadTest object. Note that, 
>> # this example will change the writes, but if the purpose is merely 
>> # inspecting the reads for all daughtercards' TCA & DAC, changing such 
>> # writes is not necessary.
>> read_test = ReadTest()
>> read_test.add_board(board=bath, name="Bath", allow_DAC_write=True, allow_TCA_write=True, TCA_write=122, DAC_write=100)
>> read_test.add_board(board=guard, name="Guard", allow_DAC_write=True, allow_TCA_write=True, TCA_write=122, DAC_write=100)
>> read_test.add_board(board=clamp, name="Clamp", allow_DAC_write=True, allow_TCA_write=True, TCA_write=122, DAC_write=100)
>> read_test.add_board(board=vclamp, name="Voltage clamp", allow_DAC_write=True, allow_TCA_write=True, TCA_write=122, DAC_write=100)
>> # The reads reported by `get_log()` in theory must be the same as what has been written.
>> read_test.get_log()
[Out 2]: # ADD CODE OUTPUT HERE
```
Keep in mind that whatever has been written to the DAC and TCA must be read out as the exact same messages. Otherwise, if the reads are 255 or different from the writes, it indicates that the data pipelines in the daughtercard examined are not working properly.

#### Notes
In conclusion, check out the documentation of the `HardwareSetup`, `Headstage`, and `ReadTest` classes, together with the ones in the `bathclamp_vclamp_utils.py` and `try_out_vsense_gains.py` files for more details!

**_After these steps and there is nothing deviates from the above requirements, your system setup has been ready for cut-open procedure!_**

### Bath clamp & Voltage clamp step responses

### Future maintenance & development
1. Fix up the clamp's transfer function fit cause it has by now not been OKAY!
2. Add datasets for the results of Resistance Measurements for both Bath and Clamp.
3. Refactor the code for bath and clamp step responses. Then, finish up the section describing the [bath & clamp step responses procedure](#bath-clamp--voltage-clamp-step-responses).
4. Consider [argparse](https://realpython.com/command-line-interfaces-python-argparse/), from which an API can be made so that users can call out and execute these experiments with Shell command lines, which will then communicate with the API to execute python scripts, then the output will be brought back to the API and then handed to the Shell terminal to output. This will make the scripting process more convenient to the end users!
