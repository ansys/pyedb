.. _create_ac_setup_example:

Create AC simulation setup
==========================
This section describes how to create AC simulation setup for Siwave.

.. autosummary::
   :toctree: _autosummary

.. code:: python




    from pyedb.legacy.edb import EdbLegacy
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
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    # create AC simulation setup
    setup1 = edbapp.create_siwave_syz_setup("AC1")
    setup1.advanced_settings.restore_default()

    # get configuration defaults settings
    settings = edbapp.setups["AC1"].get_configurations()
    for k, v in setup1.advanced_settings.defaults.items():
        if k in ["min_plane_area_to_mesh"]:
            continue
        settings["advanced_settings"][k] == v

    # SI settings
    for p in [0, 1, 2]:
        setup1.set_si_slider(p)
        settings = edbapp.setups["AC1"].get_configurations()
        for k, v in setup1.advanced_settings.si_defaults.items():
            settings["advanced_settings"][k] == v[p]

    # PI settings
    for p in [0, 1, 2]:
        setup1.set_pi_slider(p)
        settings = edbapp.setups["AC1"].get_configurations()
        for k, v in setup1.advanced_settings.pi_defaults.items():
            settings["advanced_settings"][k] == v[p]

    # add frequency sweep
    sweep = setup1.add_frequency_sweep(
        "sweep1",
        frequency_sweep=[
            ["linear count", "0", "1kHz", 1],
            ["log scale", "1kHz", "0.1GHz", 10],
            ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ],
    )

    # settings sweep options
    sweep.adaptive_sampling = True
    sweep.adv_dc_extrapolation = True
    sweep.compute_dc_point = True
    sweep.auto_s_mat_only_solve = False
    sweep.enforce_causality = True
    sweep.enforce_dc_and_causality = True
    sweep.enforce_passivity = False
    sweep.freq_sweep_type = "kDiscreteSweep"
    sweep.interpolation_use_full_basis = False
    sweep.interpolation_use_port_impedance = False
    sweep.interpolation_use_prop_const = False
    sweep.max_solutions = 200
    sweep.min_freq_s_mat_only_solve = "2MHz"
    sweep.min_solved_freq = "1Hz"
    sweep.passivity_tolerance = 0.0002
    sweep.relative_s_error = 0.004
    sweep.save_fields = True
    sweep.save_rad_fields_only = True
    sweep.use_q3d_for_dc = True