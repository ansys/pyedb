.. _create_hfss_setup_example:

Set up an HFSS simulation
=========================

This page shows how to set up an HFSS simulation.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # Ansys release version
    ansys_version = "2024.2"

    # download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # load EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2024.2")

    # create HFSS simulation setup
    setup1 = edbapp.create_hfss_setup("setup1")

    # set solution as single frequenvcy
    setup1.set_solution_single_frequency()

    # set multi-frequencies solution
    setup1.set_solution_multi_frequencies()

    # set broadband solution
    setup1.set_solution_broadband(low_frequency="1GHz", high_frequency="10GHz")

    # enable low-frequency accuracy
    setup1.hfss_solver_settings.enhanced_low_freq_accuracy = True

    # set solution basis order
    setup1.hfss_solver_settings.order_basis = "first"

    # set relative residual
    setup1.hfss_solver_settings.relative_residual = 0.0002

    # enable shell elements usage
    setup1.hfss_solver_settings.use_shell_elements = True

    # retrieve HFSS solver settings
    hfss_solver_settings = edbapp.setups["setup1"].hfss_solver_settings

    # add adaptive settings
    setup1.adaptive_settings.add_adaptive_frequency_data("5GHz", 8, "0.01")

    # add broadband adaptive settings
    setup1.adaptive_settings.adapt_type = "kBroadband"

    # specify maximum number of adaptive passes
    setup1.adaptive_settings.max_refine_per_pass = 20

    # specify minimum number of adaptive passes
    setup1.adaptive_settings.min_passes = 2

    # enable save fields
    setup1.adaptive_settings.save_fields = True

    # enable save radiate fields only
    setup1.adaptive_settings.save_rad_field_only = True

    # enable defeature based on absolute length
    setup1.defeature_settings.defeature_abs_length = "1um"

    # enable defeature based on aspect ratio
    setup1.defeature_settings.defeature_ratio = 1e-5

    # set healing options
    setup1.defeature_settings.healing_option = 0

    # set model type
    setup1.defeature_settings.model_type = 1

    # enable removal of floating geometries
    setup1.defeature_settings.remove_floating_geometry = True

    # void defeaturing criteria
    setup1.defeature_settings.small_void_area = 0.1

    # enable polygon union
    setup1.defeature_settings.union_polygons = False

    #  enable defeaturing
    setup1.defeature_settings.use_defeature = False

    # enable absolute length defeaturing
    setup1.defeature_settings.use_defeature_abs_length = True

    via_settings = setup1.via_settings
    via_settings.via_density = 1
    via_settings.via_material = "pec"
    via_settings.via_num_sides = 8
    via_settings.via_style = "kNum25DViaStyle"

    # specify advanced mesh settings
    advanced_mesh_settings = setup1.advanced_mesh_settings
    advanced_mesh_settings.layer_snap_tol = "1e-6"
    advanced_mesh_settings.mesh_display_attributes = "#0000001"
    advanced_mesh_settings.replace_3d_triangles = False

    # specify curve approximation settings
    curve_approx_settings = setup1.curve_approx_settings
    curve_approx_settings.arc_angle = "15deg"
    curve_approx_settings.arc_to_chord_error = "0.1"
    curve_approx_settings.max_arc_points = 12
    curve_approx_settings.start_azimuth = "1"
    curve_approx_settings.use_arc_to_chord_error = True

    # specify DC settings
    dcr_settings = setup1.dcr_settings
    dcr_settings.conduction_max_passes = 11
    dcr_settings.conduction_min_converged_passes = 2
    dcr_settings.conduction_min_passes = 2
    dcr_settings.conduction_per_error = 2.0
    dcr_settings.conduction_per_refine = 33.0

    # specify port settings
    hfss_port_settings = setup1.hfss_port_settings
    hfss_port_settings.max_delta_z0 = 0.5
    hfss_port_settings.max_triangles_wave_port = 1000
    hfss_port_settings.min_triangles_wave_port = 200
    hfss_port_settings.set_triangles_wave_port = True

    # add frequency sweep
    setup1.add_frequency_sweep(
        "sweep1",
        frequency_sweep=[
            ["linear count", "0", "1kHz", 1],
            ["log scale", "1kHz", "0.1GHz", 10],
            ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ],
    )
    sweep1 = setup1.frequency_sweeps["sweep1"]
    sweep1.adaptive_sampling = True

    # change setup name
    edbapp.setups["setup1"].name = "setup1a"

    # add length-based mesh operation
    mop = edbapp.setups["setup1a"].add_length_mesh_operation(
        {"GND": ["1_Top", "16_Bottom"]}, "m1"
    )
    mop.name = "m2"
    mop.max_elements = 2000
    mop.restrict_max_elements = False
    mop.restrict_length = False
    mop.max_length = "2mm"

    # add skin-depth mesh operation
    mop = edbapp.setups["setup1a"].add_skin_depth_mesh_operation(
        {"GND": ["1_Top", "16_Bottom"]}
    )
    mop.skin_depth = "5um"
    mop.surface_triangle_length = "2mm"
    mop.number_of_layer_elements = "3"
    edbapp.save()
    edbapp.close()

.. image:: ../../resources/create_hfss_setup.png
  :width: 400
  :alt: Define HFSS setup
