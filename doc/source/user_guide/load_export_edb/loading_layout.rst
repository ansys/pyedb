.. _load_edb_example:

Load a layout
=============

Although you can use PyEDB to build an entire layout from scratch, most of the time you
load an layout in an existing AEDB file. This page shows how to load a layout in EDB and
start manipulating objects.

.. autosummary::
   :toctree: _autosummary

.. code:: python


    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.2")

.. image:: ../../resources/starting_load_edb.png
  :width: 600
  :alt: Load layout in EDB

