.. _endpoint-definitions-guide:

Endpoint Definitions Guide
========================================================

The endpoint definitions Verilog file, often shortened to “ep_defines.v,” defines Opal Kelly FrontPanel endpoint addresses and bits as Verilog parameters. These parameters can then be used when instantiating controllers in Verilog as well as over USB from a host using Python. For the host to use the endpoint information, it must be written according to the guide.

The lines in ep_defines.v are split into two categories: addresses and bit indices.

.. _ep-defines-guide-addresses:

Addresses
------------------------------

Address definitions store the address and bit width of the endpoint. The general structure is as follows.

.. code-block:: verilog

    `define {CHIPNAME}_{ENDPOINT_NAME}{_GEN_ADDR} 8’h{ADDRESS} // bit_width={BIT_WIDTH }

Each piece of this definition is explained below.

.. code-block:: verilog

    `define: The macro used to declare a parameter in Verilog

CHIPNAME: the name of the chip this endpoint belongs to. This is the chip the endpoint will be found under when using the :py:meth:`~interfaces.interfaces.Endpoint.get_chip_endpoints` method. This name MUST NOT have any underscores in it because pypanel uses the first underscore in this line to separate the chip name from the endpoint name.

ENDPOINT_NAME: the name of the endpoint. This will be the dictionary key paired with the Endpoint object holding the data defined on this line. Underscores are allowed in this name.

_GEN_ADDR: an optional phrase added after the endpoint name that tells pypanel to increment this endpoint’s address when :py:meth:`~interfaces.interfaces.Endpoint.advance_endpoints` is called on a group containing this endpoint.

8’h: declaration of an 8 bit hexadecimal value before the address. If your address is more than 8 bits, change the 8 to that value. Ex. 16 bit address would be 16’h.

ADDRESS: the hexadecimal address value for this endpoint. This is the value the parameter will hold in the Verilog.

//: start of the comment part of this line. The Verilog parameter only holds the address, but the pypanel Endpoint object will also hold the bit_width, which is defined in the comment.

bit_width=: the prefix for defining the bit width for pypanel.

BIT_WIDTH: the decimal value of the bit width of the endpoint.

.. _ep-defines-guide-bit-indices:

Bit Indices
------------------------------

Bit index definitions store the bit, associated address, and bit width of the endpoint. The general structure is as follows.

.. code-block:: verilog

    `define {CHIPNAME}_{ENDPOINT_NAME}{_GEN_BIT} {BIT} // addr={ADDRESS} bit_width={BIT_WIDTH}

Each piece of this definition is explained below.

.. code-block:: verilog

    `define: The macro used to declare a parameter in Verilog

CHIPNAME: the name of the chip this endpoint belongs to. This is the chip the endpoint will be found under when using the :py:meth:`~interfaces.interfaces.Endpoint.get_chip_endpoints` method. This name MUST NOT have any underscores in it because pypanel uses the first underscore in this line to separate the chip name from the endpoint name.

ENDPOINT_NAME: the name of the endpoint. This will be the dictionary key paired with the Endpoint object holding the data defined on this line. Underscores are allowed in this name.

_GEN_BIT: an optional phrase added after the endpoint name that tells pypanel to increment this endpoint’s lower bit index by its bit width when :py:meth:`~interfaces.interfaces.Endpoint.advance_endpoints` is called on a group containing this endpoint.

BIT: the decimal lower bit index for this endpoint. This is the value the parameter will hold in the Verilog.

//: start of the comment part of this line. The Verilog parameter only holds the address, but the pypanel Endpoint object will also hold the bit_width, which is defined in the comment.

addr=: the prefix for defining the associated address for pypanel.

ADDRESS: the address associated with the bit index for this endpoint. While the Verilog parameter will only store the bit defined in this line, the pypanel Endpoint object will also store the address and bit width defined in the comment. The address can either be a hexadecimal address value with prefix “0x” or the group and endpoint name of an address endpoint (see :ref:`ep-defines-guide-addresses` section). Ex. 0x04 or GP_WIRE_IN.

bit_width=: the prefix for defining the bit width for pypanel.

BIT_WIDTH: the decimal value of the bit width of the endpoint. If the _GEN_BIT suffix is added, then pypanel will add this value to the lower bit index of the endpoint when incrementing a group containing this endpoint.

File
------------------------------

Using the above formats, enter the endpoints each on separate lines in a Verilog file. The order of the endpoints does not matter. Endpoints can have the same name if they have different chip names. For example, “GP_WIRE_IN” and “MEM_WIRE_IN” both have the endpoint name “WIRE_IN” but have different chip names “GP” and “MEM,” which is allowed. Because pypanel uses comments to extract extra information about the endpoints, any other comments must be put on their own line, which pypanel will ignore.

Alternatively, enter the information in an Excel spreadsheet copy of this `template <https://github.com/lucask07/covg_fpga/blob/daq_v2/examples/ep_defines_sheet_template.xlsx>`_. Each row should be a different endpoint. Each column is explained below. Check the “Generated Line” column for any possible errors, then use the :py:meth:`~interfaces.interfaces.Endpoint.excel_to_defines` method to create a Verilog file from the spreadsheet. For reference, here is an `example spreadsheet <https://github.com/lucask07/covg_fpga/blob/daq_v2/examples/ep_defines_sheet_example.xlsx>`_ and an example of the `Verilog file <https://github.com/lucask07/covg_fpga/blob/daq_v2/examples/ep_defines_example.v>`_ generated from it.

Chip Name: CHIPNAME (see :ref:`ep-defines-guide-bit-indices` section) from above.

- Note: recall that the chip name in each endpoint definition line MUST NOT have underscores

Endpoint Name: ENDPOINT_NAME (see :ref:`ep-defines-guide-bit-indices` section) from above.

Address (hex): ADDRESS (see :ref:`ep-defines-guide-bit-indices` section) from above.

Bit: BIT (see :ref:`ep-defines-guide-bit-indices` section) from above. Leave empty if defining an endpoint holding an address only.

Bit Width: BIT_WIDTH (see :ref:`ep-defines-guide-bit-indices` section) from above

GEN_BIT: _GEN_BIT (see :ref:`ep-defines-guide-bit-indices` section) from above. Enter True or False.

GEN_ADDR: _GEN_ADDR (see :ref:`ep-defines-guide-bit-indices` section) from above. Enter True or False.

Generated Name: automatically generated chip name with endpoint name. Since this is the name the “Address (hex)” column needs when referencing another endpoint, referencing this cell allows you to have any future name changes to the address endpoint reflected in the “Address (hex)” column of any endpoint referencing it.

Generated Line: the line that will be written for this endpoint in the endpoint definitions Verilog file when :py:meth:`~interfaces.interfaces.Endpoint.excel_to_defines` is called.

Usage
------------------------------

Once your endpoint definitions file is complete, you can include the parameters you just named in your Verilog containing the Opal Kelly Endpoints themselves by adding the line below to that file. Replace “ep_defines.v” with whatever you named your endpoint definitions file.

.. code-block:: verilog

    `include “ep_defines.v”

To retrieve the endpoints through pypanel, use the :py:meth:`~interfaces.interfaces.Endpoint.get_chip_endpoints` method.
