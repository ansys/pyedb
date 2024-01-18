Export EDB to Maxwell
=====================
This section describes how to export EDB to Maxwell:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    # define export options
    options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
    edbapp.write_export3d_option_config_file(temp_folder, options_config)

    # export to Maxwell with given net list
    edbapp.export_maxwell(
        temp_folder, net_list=["ANALOG_A0", "ANALOG_A1", "ANALOG_A2"], hidden=True
    )
    edbapp.close()
