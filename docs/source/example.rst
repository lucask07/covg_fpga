Example
============

One example of using PACKAGE_NAME is an impedance analyzer which calculates the impedance of an unknown
component. For this example you will need an Opal Kelly XEM7310 FPGA connected to your computer as well as a
`DAC80508 <https://www.ti.com/product/DAC80508>`_ and `ADS8686 <https://www.ti.com/product/ADS8686S>`_
connected to the FPGA. The pin connections between the FPGA and these peripherals are as follows:

DAC80508

* SDI - L3

* SDO - K3

ADS8686

* SDI - P2

* SDOA - N5

* SDOB - N2

Also download the `top_level_module.bit <https://github.com/lucask07/covg_fpga/blob/daq_v2/fpga_XEM7310/fpga_XEM7310.runs/impl_1/top_level_module.bit>`_
bitfile and `impedance_analyzer.py <https://github.com/lucask07/covg_fpga/blob/daq_v2/examples/impedance_analyzer.py>`_
file from the GitHub. Change the BITFILE_PATH constant in impedance_analyzer.py to the path of
top_level_module.bit on your computer. Read through the documentation included in impedance_analyzer.py
to understand the other constants you can change as well as the setup of the circuit. You can then run
impedance_analyzer.py.

This will send a test voltage across the unknown impedance with the DDR3 and the DAC80508 and read it back
using the DDR3 and the ADS8686. With the known resistor's value, the current is calculated to be used with
the read voltage to calculate the impedance.