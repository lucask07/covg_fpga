Verilog and Python for a general purpose data acquisition system using an OpalKelly FPGA as the main controller. The Python is designed to be a general purpose approach to interface with multiple peripheral components that contain register maps. 


## Quick Start

1. Install with pip

```
pip install PACKAGE_NAME
```

To use an FPGA and peripherals:


2. Download [FrontPanel](https://pins.opalkelly.com/downloads) from OpalKelly

3. Download [Registers.xlsx](https://github.com/lucask07/covg_fpga/blob/daq_v2/python/Registers.xlsx) from the GitHub

4. Create config.yaml with create_yaml and edit fields as needed

```python
>>> from interfaces.utils import create_yaml
>>> create_yaml()
YAML created at C:/Users/username/.PACKAGE_NAME
```

See [Installation Guide]() for more information.


## Acknowledgements 
This work is partially supported by National Institutes of Health (NIH) R15 grant R15NS116907 to PI L. J. Koerner.

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


## OpalKelly Module Compatibility. 
We have targeted and tested with the [XEM7310-A75 module](https://opalkelly.com/products/xem7310/) (Xilinx Artix-7). We have not tested but anticipate reasonable portability to other USB 3 OpalKelly modules:

* XEM7310MT
* XEM7320
* XEM7305
* XEM7360

## (Approximate) FPGA Block Diagram 
<p align="center">
<img src="docs/block_diagram/fpga_block_diagram.png" width="700">
