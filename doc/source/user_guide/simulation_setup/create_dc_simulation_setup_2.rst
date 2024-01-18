Create DC simulation setup
==========================
This section describes how to create DC simulation setup for Siwave.

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
    targetfile = downloads.download_file(
        "edb/Powerboard_SiC_MOSFET.tgz", destination=temp_folder
    )

    # loading EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    setup1 = edbapp.create_siwave_dc_setup("DC1")
    setup1.dc_settings.restore_default()
    setup1.dc_advanced_settings.restore_default()

    settings = edbapp.setups["DC1"].get_configurations()
    for k, v in setup1.dc_settings.defaults.items():
        if k in ["compute_inductance", "plot_jv"]:
            continue
        settings["dc_settings"][k] == v

    for k, v in setup1.dc_advanced_settings.defaults.items():
        settings["dc_advanced_settings"][k] == v

    for p in [0, 1, 2]:
        setup1.set_dc_slider(p)
        settings = edbapp.setups["DC1"].get_configurations()
        for k, v in setup1.dc_settings.dc_defaults.items():
            assert settings["dc_settings"][k] == v[p]
        for k, v in setup1.dc_advanced_settings.dc_defaults.items():
            assert settings["dc_advanced_settings"][k] == v[p]
