Simulation setups
=================
These classes are the containers of ``setup`` classes in EDB for both HFSS and Siwave.


.. code:: python

    from pyedb.dotnet.edb import Edb

    edb = Edb(myedb, edbversion="2023.1")

    # this call create a setup and returns the object
    setup = edb.create_hfss_setup("my_setup")
    setup.set_solution_single_frequency()
    setup.hfss_solver_settings.enhanced_low_freq_accuracy = True
    setup.hfss_solver_settings.order_basis = "first"

    setup.adaptive_settings.add_adaptive_frequency_data("5GHz", 8, "0.01")
    ...



.. currentmodule:: pyedb.dotnet.edb_core.utilities.simulation_setup

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   simulation_setup.HfssSimulationSetup
   simulation_setup.EdbFrequencySweep
   simulation_setup.DcrSettings
   simulation_setup.CurveApproxSettings
   simulation_setup.AdvancedMeshSettings
   simulation_setup.ViaSettings
   simulation_setup.DefeatureSettings
   simulation_setup.AdaptiveSettings
   simulation_setup.AdaptiveFrequencyData
   simulation_setup.HfssSolverSettings
   simulation_setup.HfssPortSettings
   simulation_setup.MeshOperationLength
   simulation_setup.MeshOperationSkinDepth
