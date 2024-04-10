.. _set_all_antipads_value_example:

Edit a padstack definition
==========================

This page shows how to edit a padstack definition, setting all anti-pad values to a fixed value.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # Ansys release version
    ansys_version = "2024.1"

    # download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # load EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2024.1")

    # sets all anti-pads value to zero
    edbapp.padstacks.set_all_antipad_value(0.0)
    edbapp.close()