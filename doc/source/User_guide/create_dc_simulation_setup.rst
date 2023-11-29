Create DC simulation setup (SimulationConfiguration)
====================================================
This section describes how to create DC simulation setup for Siwave using SimulationConfiguration class.

.. autosummary::
   :toctree: _autosummary

.. code:: python


    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads
    from pyedb.generic.constants import SolverType

    # Ansys release version
    ansys_version = "2023.2"

    #download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file('edb/Powerboard_SiC_MOSFET.tgz', destination=temp_folder)

    # loading EDB
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    # create a new simulatiom setup object
    sim_setup = edbapp.new_simulation_configuration()

    # disabling cutout
    sim_setup.do_cutout_subdesign = False

    # selectin solver type
    sim_setup.solver_type = SolverType.SiwaveDC

    # adding volatge source
    sim_setup.add_voltage_source(
            positive_node_component="Q3",
            positive_node_net="SOURCE_HBA_PHASEA",
            negative_node_component="Q3",
            negative_node_net="HV_DC+")

    # adding current source
    sim_setup.add_current_source(
            name="I25",
            positive_node_component="Q5",
            positive_node_net="SOURCE_HBB_PHASEB",
            negative_node_component="Q5",
            negative_node_net="HV_DC+")

    # defining out put files
    sim_setup.open_edb_after_build = False
    sim_setup.batch_solve_settings.output_aedb = os.path.join(self.local_scratch.path, "build.aedb")
    original_path = edbapp.edbpath

    # specifying multi-threaded cutout
    sim_setup.batch_solve_settings.use_pyaedt_cutout = True
    sim_setup.open_edb_after_build = True

    # build simulation project
    sim_setup.build_simulation_project()
    edb.close()