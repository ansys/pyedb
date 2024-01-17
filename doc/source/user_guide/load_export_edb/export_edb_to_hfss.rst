.. _export_edb_to_hfss_example:

Export EDB to HFSS
==================
This section describes how to export EDB to HFSS:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    # define export options
    options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
    edbapp.write_export3d_option_config_file(temp_folder, options_config)

    # export to HFSS
    edbapp.export_hfss(temp_folder)
    edbapp.close()
