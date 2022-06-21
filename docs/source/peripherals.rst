peripherals
======================

The :py:mod:`peripherals` subpackage contains a few base controllers and several specific controllers for different peripherals. The base controllers are used to reduce code repetition as many peripherals use common communication methods. Specific peripheral classes that use these communication methods are derived from the more general base classes.

Base Controllers
--------------------------
.. automodule:: interfaces.peripherals.I2CController
    :members:

.. automodule:: interfaces.peripherals.SPIController
    :members:

.. automodule:: interfaces.peripherals.SPIFifoDriven
    :members:

Extends I2CController
--------------------------
.. automodule:: interfaces.peripherals.TCA9555
    :members:

.. automodule:: interfaces.peripherals.UID_24AA025UID
    :members:

.. automodule:: interfaces.peripherals.DAC53401
    :members:

.. automodule:: interfaces.peripherals.TMF8801
    :members:


Extends SPIController
--------------------------
.. automodule:: interfaces.peripherals.ADS8686
    :members:


Extends SPIFifoDriven
--------------------------
.. automodule:: interfaces.peripherals.DAC80508
    :members:

.. automodule:: interfaces.peripherals.AD5453
    :members:


Miscellaneous
---------------
.. automodule:: interfaces.peripherals.DDR3
    :members:

.. automodule:: interfaces.peripherals.AD7961
    :members:

.. automodule:: interfaces.peripherals.ADCDATA
    :members:

