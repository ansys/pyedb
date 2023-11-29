EDB manager
===========
An AEDB database is a folder that contains the database representing any part of a PCB.
It can be opened and edited using the ``Edb`` class.

.. image:: ../Resources/3dlayout_1.png
  :width: 800
  :alt: HFSS 3D Layout is the tool used to visualize EDB content.



.. autosummary::
   :toctree: _autosummary

   pyedb.legacy.edb
   pyedb.legacy.edb_core.edb_data.variables.Variable
   pyedb.legacy.edb_core.edb_data.edbvalue.EdbValue


.. code:: python

    from pyedb.legacy.edb import EdbLegacy
    # this call returns the Edb class initialized on 2023 R1
    edb = EdbLegacy(myedb, edbversion="2023.1")

    ...


EDB modules
~~~~~~~~~~~
This section lists the core EDB modules for reading and writing information
to AEDB files.


.. currentmodule:: pyedb.legacy.edb_core

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   hfss.EdbHfss
   siwave.EdbSiwave
   materials.Materials



.. currentmodule:: pyedb.legacy.edb_core.edb_data.edbvalue

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   EdbValue


.. code:: python

    from from pyedb.legacy.edb_core.edb import Edb
    edb = Edb(myedb, edbversion="2023.1")

    # this call returns the EdbHfss Class
    comp = edb.hfss

    # this call returns the Components Class
    comp = edb.components

    # this call returns the EdbSiwave Class
    comp = edb.siwave

    # this call returns the EdbPadstacks Class
    comp = edb.padstacks

    # this call returns the Stackup Class
    comp = edb.stackup

    # this call returns the Materials Class
    comp = edb.materials

    # this call returns the EdbNets Class
    comp = edb.nets

    ...
