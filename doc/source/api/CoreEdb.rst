EDB manager
===========
An AEDB database is a folder that contains the database representing any part of a PCB.
It can be opened and edited using the ``Edb`` class.

.. image:: ../resources/3dlayout_1.png
  :width: 800
  :alt: HFSS 3D Layout is the tool used to visualize EDB content.


.. currentmodule:: pyedb.dotnet
.. autosummary::
   :toctree: _autosummary

   edb.Edb


.. code:: python

    from pyedb import Edb

    # this call returns the Edb class initialized on 2024R2
    edb = Edb(myedb, edbversion="2024.2")

    ...


EDB modules
~~~~~~~~~~~
This section lists the core EDB modules for reading and writing information
to AEDB files.


.. currentmodule:: pyedb.dotnet.database

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   components.Components
   hfss.EdbHfss
   layout_validation.LayoutValidation
   materials.Materials
   modeler.Modeler
   nets.EdbNets
   edb_data.padstacks_data.EDBPadstack
   siwave.EdbSiwave
   stackup.Stackup



.. code:: python

    from pyedb import Edb

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
