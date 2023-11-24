Loading layout
==============
Although an entire layout can be built from scratch with PyEDB most of the time the first step is
loading an existing aedb file. This section is showing how to load an EDB and start manipulating
objects.



.. code:: python


    from pyedb.legacy.edb_core.edb import EdbLegacy

    edb_file = pyedb.layout_examples.ANSYS-HSD_V1.aedb
    edb = EdbLegacy(edbversion="2024.1", edbpath=edb_file)


.. image:: ../Resources/starting_load_edb.png
  :width: 600
  :alt: Loading first EDB

