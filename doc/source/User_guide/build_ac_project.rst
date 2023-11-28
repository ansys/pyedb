Create SYZ project (SimulationConfiguration)
===========================================
This section describes how to create SYZ simulation setup for Siwave using SimulationConfiguration class.

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb_core.edb import EdbLegacy
    from pyedb.generic.constants import SolverType

    # Ansys release version
    ansys_version = "2023.2"

    #download and copy the layout file from examples
    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file('edb/Powerboard_SiC_MOSFET.tgz', destination=temp_folder)

    # loading EDB
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    simconfig = edbapp.new_simulation_configuration()
    simconfig.solver_type = SolverType.SiwaveSYZ
    simconfig.mesh_freq = "40.25GHz"
    edbapp.build_simulation_project(simconfig)
    edbapp.close()