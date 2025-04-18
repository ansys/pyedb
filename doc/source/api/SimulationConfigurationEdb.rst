Simulation configuration
========================
These classes are the containers of simulation configuration constructors for the EDB.


.. currentmodule:: pyedb.dotnet.database.edb_data.simulation_configuration

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SimulationConfiguration
   SimulationConfigurationDc
   SimulationConfigurationAc
   SimulationConfigurationBatch



.. code:: python

    from pyedb import Edb

    edbapp = Edb(myedb, edbversion="2023.1")

    sim_setup = edbapp.new_simulation_configuration()
    sim_setup.solver_type = sim_setup.SOLVER_TYPE.SiwaveSYZ
    sim_setup.batch_solve_settings.cutout_subdesign_expansion = 0.01
    sim_setup.batch_solve_settings.do_cutout_subdesign = True
    sim_setup.use_default_cutout = False
    sim_setup.batch_solve_settings.signal_nets = [
        "PCIE0_RX0_P",
        "PCIE0_RX0_N",
        "PCIE0_TX0_P_C",
        "PCIE0_TX0_N_C",
        "PCIE0_TX0_P",
        "PCIE0_TX0_N",
    ]
    sim_setup.batch_solve_settings.components = ["U2A5", "J2L1"]
    sim_setup.batch_solve_settings.power_nets = ["GND"]
    sim_setup.ac_settings.start_freq = "100Hz"
    sim_setup.ac_settings.stop_freq = "6GHz"
    sim_setup.ac_settings.step_freq = "10MHz"

    sim_setup.export_json(os.path.join(project_path, "configuration.json"))
    edbapp.build_simulation_project(sim_setup)

    ...
