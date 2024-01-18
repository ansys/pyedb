Settings all anti-pads value
============================
This shows how to set all anti-pads value to fixed one.

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.dotnet import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # Ansys release version
    ansys_version = "2023.2"

    # download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # loading EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    # settings all anti-pads value to zero
    edbapp.padstacks.set_all_antipad_value(0.0)
    edbapp.close()