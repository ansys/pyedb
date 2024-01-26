.. _quick_code:

Quick code
==========

You can view or download a PyEDB cheat sheet, which is a one-page reference
providing syntax rules and commands for using the PyEDB API:

- `View <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.png>`_ the PyEDB API cheat sheet.
- `Download <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf>`_ the PyEDB API cheat sheet.

Example
-------

This example shows how to use PyEDB to load an existing AEDB file into memory:

.. code:: python
  
    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

Example workflow
----------------

Here’s a brief example of how PyEDB works:

Connect to EDB from a Python IDE
---------------------------------
PyEDB works both inside AEDT and as a standalone app.
PyEDB also provides advanced error management. Usage examples follow.

Explicit PyEDB declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # Start EDB

    from pyedb.dotnet.edb import Edb

    edb_file = pyedb.layout_examples.ANSYS - HSD_V1.aedb
    edb = Edb(edbversion="2023.2", edbpath=edb_file)


Variables
~~~~~~~~~

.. code:: python

    from pyedb.dotnet.edb import Edb

    edb_file = pyedb.layout_examples.ANSYS - HSD_V1.aedb
    edb = Edb(edbversion="2023.2", edbpath=edb_file)
    edb["dim"] = "1mm"  # design variable
    edb["$dim"] = "1mm"  # project variable
