Verilog and Python for the COVG project.



## Acknowledgements 

### The FPGA code is dervied from many open-source contributions. 

* The I2C controller is from OpalKelly [OpalKelly I2CController](https://github.com/opalkelly-opensource/design-resources/tree/main/HDLComponents/I2CController) (MIT License).

* The AD7961 controller is from Analog Devices and is free to use / redistribute as long as its used with Analog Devices parts (which must be the case since it does not work if connected to other parts). The Verilog is available within the [EVAL-AD7960 evaluation kit software](https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/eval-ad7960.html#eb-overview)

* The [SPI Controller](http://www.opencores.org/projects/spi/) is from OpenCores.org and is authored by Simon Srot (GPL 2.1 or later license). 

* The wishbone master is written by Dan Gisselquist, Gisselquist Technology LLC. (LGPL, v3) 

* The DDR user interface (ddr_test.v) started with the OpalKelly DDR example provided in the FrontPanel example RAMTester and was significantly modified to support two ports.

### The Python code relies on wonderful open source packages such as:

* Matplotlib 
* numpy
* pandas

### (Approximate) FPGA Block Diagram 
![Block diagram](docs/block_diagram/fpga_block_diagram.pdf)
