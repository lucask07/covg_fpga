.. _new_peripheral_guide:

New Peripheral Guide
===========================

Adding a new peripheral is a great way to contribute. The steps below will guide you through the process. For more information on community contributions, see the `contributions guide <https://github.com/lucask07/covg_fpga/blob/daq_v2/CONTRIBUTING.md>`_.

Before You Begin
----------------
To get set up, first `create a new issue <https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue>`_ for the peripheral you want to add. Include the name, a short description, and a link to the datasheet. To avoidi duplicates, check if there are any open issues with the same peripheral before creating a new issue. With this done, `fork the repo <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_ and begin working on your addition. Be sure to keep your branch up to date with the main branch of the repository.

Registers
---------
The first step is to add your peripheral to the `main registers spreadsheet <https://github.com/lucask07/covg_fpga/blob/daq_v2/python/Registers.xlsx>`_. Add a new page to the spreadsheet with the name of your peripheral and fill in the information for its internal registers. For more information, see the :ref:`register index guide <register-index-guide>`.

Interfaces
----------
Add a class for your peripheral to the :py:mod:`~interfaces.interfaces` module. If your peripheral uses an I2C or SPI interface, you may consider extending the :py:class:`~interfaces.interfaces.I2CController`, :py:class:`~interfaces.interfaces.SPIController`, or :py:class:`~interfaces.interfaces.SPIFifoDriven` class. Your class should include a :py:meth:`create_chips` method for creating several instances of the new peripheral at once. Write and read commands are commonly useful methods that, if applicable, should be included, but remaining functionality will likely be specific to your peripheral. Add what will be useful.

Sandbox/Test File
-----------------
Once your peripheral is functional, create an example script or test file to show its use. Any test files should be written using `pytest <https://docs.pytest.org/en/7.1.x/contents.html>`_.

Documentation
-------------
The last requirement of your addition is documentation. Please add class and method docstrings to your code in `numpy format <https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard>`_. See the :py:class:`~interfaces.interfaces.DAC80508` class for an example. Please also add a docstring to your exampe/test file explaining what it does. 

Pull Request
------------
With the above steps complete, `create a pull request <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_, linking the issue you created, for your peripheral. Be sure to watch your pull request for any comments on questions or additions that may be needed.
