# Experiment Manual
<!-- Start from page 45-46 -->
## Headstage
### Bath/Guard Headstage
Notice the P1, P2, CC, GS1, and GS2 ports on the bathclamp. In the model cell there are 5 corresponding ports to those 5 on the bathclamp, with the first consecutive two for GS1 and GS2 (symmetrical, meaning they can interchange) and the remaining consecutive three for P1, P2, and CC. Of the latter, the middle one is colored red reserved for P2, so connect accordingly. P1's port is the one outermost, so the remaining one is for CC.

Run the headstage calibration script with the command:

```{sh}
python bathclamp_vclamp_cal.py
```
or if the terminal is having the `IPython` terminal activated, type this instead:

```{python}
%run bathclamp_vclamp_cal.py
```

Then track the output in both the terminal, figures, and dataset generated, which is elaborated below.

#### Terminal
First off, we need to make sure that all of the boards are initialized properly. Check the lines where it goes:

```
------------Clamp 0 Init-----------
Timeout Exception in Rx
TCA_0 register: OUTPUT FAILED
    (read_out) None != (default) 255
Timeout error in transmit
------------Clamp 1 Init-----------
Timeout Exception in Rx
TCA_0 register: OUTPUT FAILED
    (read_out) None != (default) 255
Timeout error in transmit
------------Clamp 2 Init-----------
TCA_0 register: POLARITY FAILED
    (read_out) 255 != (default) 0
------------Clamp 3 Init-----------
TCA_0 register: POLARITY FAILED
    (read_out) 255 != (default) 0
```
Pay attention to the `(read_out)` code. If it is anything else besides 255 or `None`, your boards have been correctly initialized. If it is either code 255 (board detectable, but failed to gain relay controls), or `None` (board not detectable), it likely appears that the DAQ board is not correctly functional. One way to inspect the DAQ board in this scenario is to measure the $I^2C$ traffic individually for each HDMI socket. __The example given above shows that all sockets have failed__.

Second, make sure that the program is not buggy to the point that it produces 4 statistical test results (first two for DAC and ADC 1 and the last two for DAC and ADC 2). Make sure that the Chi-square value is small enough (as close, but not equal, to 0 as possible) and both AIC and BIC are highly negative (around -70 or more).

In the `~\Documents\covg\manuscripts\covg_methods\digital_amp_manuscript\overleaf\figures\calibration` directory, look for the figure file named `transfer_function_fit_elec_r_cc` and `transfer_function_fit_vclamp` (either pdf or png) and ensure that the measured data aligns well with the fitted data. One more thing we can do, though, is to peek into all the excel worksheets in the `~\Documents\covg\fpga_and_measurements\daq_v2\data` directory and ensure that the measured data points match the fitted data points.

After these steps and there is nothing deviates from the above requirements, your system setup has been ready for cut-open procedure!
