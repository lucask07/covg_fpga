.. _register-index-guide:

Register Index Guide
========================================================

The register index holds the name, address, lower bit index, upper bit index, and bit width of registers so they can be read in by pypanel and stored in a Register object. Here is a `template <https://github.com/lucask07/covg_fpga/blob/daq_v2/examples/register_index_template.xlsx>`_ for the register index. Start with the template and follow the example below.

For this example, our peripheral/chip is called GUIDE and has 4 internal registers: WRITE_IN, READ_OUT, CONFIG, and ID.

1. Enter the chip name
------------------------------

The name of the chip is used to access this sheet of registers as a group. Our chip is GUIDE, so replace the sheet title CHIP with GUIDE.

- Note: any valid Excel sheet name is allowed for CHIP, but a one word uppercase name is recommended so it can match the chip name in the endpoints definitions Verilog file (see :ref:`endpoint definitions guide <endpoint-definitions-guide>`), which cannot contain underscores.

2. Enter register name
------------------------------

Names are used to access each register within a group on a sheet. We will start with WRITE_IN. In the first open row (row 2) enter WRITE_IN in the “Name” column. Do not change the column labels.

- Note: any valid Excel string is allowed for register names
- Note: since the chip name is already available in the sheet name, adding the chip name to register names is redundant
- Note: the column labels must remain as given. This allows other columns with similar names introduced for whatever reason to be ignored.

3. Enter hex address and default value
--------------------------------------

The address and default value for the register should be taken from the chip’s datasheet and entered in hexadecimal. WRITE_IN is located at address 0x00 with default value 0x0000. Enter these values in the “Hex Address” and “Default Value” columns.

- Note: the extra zeros are for readability only. (0x00 == 0x0)
- Note: the “0x” prefix on hexadecimal values is for readability only, it is recommended, but not required (0x10 == 10­). The “Hex Address” and “Default Value” columns MUST be given as hexadecimal values.
    
    16
    
4. Enter bit width, upper bit index, and lower index
----------------------------------------------------

The bit width, upper index, and lower index should be taken from the chip’s datasheet and entered in decimal. WRITE_IN has the following values concerning bit indices. Enter these values in their corresponding columns.

    Bit Width: 16

    Bit Index (High): 15

    Bit Index (Low): 0

- Note: these values MUST be entered in decimal

5. Repeat for remaining registers
---------------------------------

Repeat steps 2-5 for any remaining registers. Values for the remaining registers in this example are listed below.

    READ_OUT

        Hex Address: 0x01

        Default Value: 0xffff

        Bit Width: 16

        Bit Index (High): 15

        Bit Index (Low): 0

    CONFIG

        Hex Address: 0x02

        Default Value: 0x31A0

        Bit Width: 8

        Bit Index (High):15

        Bit Index (Low): 8

    ID

        Hex Address: 0x02

        Default Value: 0x44

        Bit Width: 8

        Bit Index (High): 7

        Bit Index (Low): 0

- Note: the order of the registers does not matter

6. Repeat for remaining chips
------------------------------

Repeat steps 1-5 for any remaining chips in your project. Be sure to create a new sheet for each chip. Example values are listed below.

    CHIP: MEMORY

        DATA

            Hex Address: 0x0

            Default Value: 0x000

            Bit Width: 10

            Bit Index (High): 9

            Bit Index (Low): 0

        ID

            Hex Address: 0x0

            Default Value: 0x3f

            Bit Width: 6

            Bit Index (High): 15

            Bit Index (Low): 10

Here is the `completed register index <https://github.com/lucask07/covg_fpga/blob/daq_v2/examples/register_index_guide_completed_example.xlsx>`_ for this example. You can read the registers into pypanel using the :py:meth:`~interfaces.interfaces.Register.get_chip_registers` method.

