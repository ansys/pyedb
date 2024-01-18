.. _load_edb_example:

Loading layout
==============
Although an entire layout can be built from scratch with PyEDB most of the time the first step is
loading an existing aedb file. This section is showing how to load an EDB and start manipulating
objects.

.. autosummary::
   :toctree: _autosummary

.. code:: python


    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

.. image:: ../../resources/starting_load_edb.png
  :width: 600
  :alt: Loading first EDB

