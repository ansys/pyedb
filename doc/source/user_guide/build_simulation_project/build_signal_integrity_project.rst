.. _build_si_project_example:

Build a signal integrity project
================================

This page shows how to build an signal integrity project.

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

    sim_setup = edbapp.new_simulation_configuration()
    sim_setup.signal_nets = [
        "DDR4_A0",
        "DDR4_A1",
        "DDR4_A2",
        "DDR4_A3",
        "DDR4_A4",
        "DDR4_A5",
    ]
    sim_setup.power_nets = ["GND"]
    sim_setup.do_cutout_subdesign = True
    sim_setup.components = ["U1", "U15"]
    sim_setup.use_default_coax_port_radial_extension = False
    sim_setup.cutout_subdesign_expansion = 0.001
    sim_setup.start_freq = 0
    sim_setup.stop_freq = 20e9
    sim_setup.step_freq = 10e6
    edbapp.build_simulation_project(sim_setup)
    edbapp.close()

.. image:: ../../resources/build_signal_integrity_user_guide.png
  :width: 800
  :alt: Built signal integrity project
