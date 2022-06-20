Installation
=================================

Quick Start
--------------
1. Install with pip (see :ref:`installation_pip` section)

To use an FPGA and peripherals:


2. Download `FrontPanel <https://pins.opalkelly.com/downloads>`_ from OpalKelly (see :ref:`installation_fpga` section)

3. Download `Registers.xlsx <https://github.com/lucask07/covg_fpga/blob/daq_v2/python/Registers.xlsx>`_ and add unsupported peripherals (see :ref:`installation_peripherals` section)

4. Create config.yaml with :py:meth:`interfaces.utils.create_yaml` and edit (see :ref:`installation_yaml` section)


.. _installation_pip:

pip
-----------

PACKAGE_NAME can be installed using pip.

.. code-block:: console

    pip install PACKAGE_NAME

.. _installation_fpga:

FPGA
------------
To use the FPGA class with an Opal Kelly FrontPanel-supported device, you will also need to download the `FrontPanel SDK <https://pins.opalkelly.com/downloads>`_ from Opal Kelly.
You will also need to update the config.yaml file. See the :ref:`installation_yaml` section and example.

.. _installation_peripherals:

Peripherals
--------------------
To use peripherals, you will need FrontPanel (see :ref:`installation_fpga` section) as well as the `Registers.xlsx <https://github.com/lucask07/covg_fpga/blob/daq_v2/python/Registers.xlsx>`_ spreadsheet with register information for all supported peripherals, available on the `GitHub <https://github.com/lucask07/covg_fpga>`_.
Update the config.yaml file with the path to `Registers.xlsx <https://github.com/lucask07/covg_fpga/blob/daq_v2/python/Registers.xlsx>`_ (see :ref:`installation_yaml` section).
If you are using a peripheral not currently supported by PACKAGE_NAME, see the :ref:`New Peripheral Guide <new_peripheral_guide>`.

.. _installation_yaml:

YAML Configuration
-----------------------
PACKAGE_NAME uses a config.yaml file to customize paths to needed files and other user-configurable options.
To start, install the package (see :ref:`installation_pip` section), and open a Python shell. You can then
import :py:meth:`interfaces.utils.create_yaml` and run it like below.

.. code-block:: python

    >>> from interfaces.utils import create_yaml
    >>> create_yaml()
    YAML created at C:/Users/username/.PACKAGE_NAME

From there, you can configure the options available by editing the config.yaml file created at the path given
after running :py:meth:`interfaces.utils.create_yaml`. An example YAML is shown below.

.. code-block:: yaml

    endpoint_max_width: 32
    ep_defines_path: C:/Users/username/my_project/ep_defines.v
    fpga_bitfile_path: C:/Users/username/my_project/top_level_module.bit
    frontpanel_path: C:/Program Files/Opal Kelly/FrontPanelUSB
    registers_path: C:/Users/username/my_project/Registers.xlsx