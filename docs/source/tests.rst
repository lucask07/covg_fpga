Tests
=================

PACKAGE_NAME uses `pytest <https://docs.pytest.org/en/7.1.x/>`_ for its tests. pytest can be installed with pip.

.. code-block:: python

    >>> pip install pytest

All tests are available in the `tests folder on the GitHub <https://github.com/lucask07/covg_fpga/tree/daq_v2/python/tests>`_
All automated and working tests can be run with the "usable" marker.

.. code-block:: python

    >>> py -m pytest -m usable

More specific marks are available for different setups. Simply replace "usable" with one of the following markers in the command above.

* no_fpga: use if you do not have an FPGA connected

* fpga_only: use if you have an FPGA connected

* usable: all working automated tests; may require FPGA and connected peripherals 
