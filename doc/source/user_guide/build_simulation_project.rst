************************
Build simulation project
************************

Clipping layout
===============

Because most of the time only a specific part of a layout must be simulated, clipping the design
needs to be performed to reduce computer resources and speed up simulation. Here is an example showing
how to clip a design based on nets selection.

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
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # loading EDB
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    # selecting signal nets to evaluate the extent for clipping the layout
    signal_nets = [
        "DDR4_DQ0",
        "DDR4_DQ1",
        "DDR4_DQ2",
        "DDR4_DQ3",
        "DDR4_DQ4",
        "DDR4_DQ5",
        "DDR4_DQ6",
        "DDR4_DQ7",
    ]
    # at least one reference net must be included. Reference nets are included in the design but clipped.
    reference_nets = ["GND"]
    # defining the expansion factor. The value gives the distance for evaluating the cutout extent. Here we define a cutout
    expansion = 0.01  # 1cm in this case
    # processing cutout
    edbapp.cutout(
        signal_list=signal_nets, reference_list=reference_nets, expansion_size=expansion
    )
    # save and close project
    edbapp.save_edb()
    edbapp.close_edb()

.. image:: ../../Resources/clipped_layout.png
  :width: 800
  :alt: Layout clipping

Create SYZ project (SimulationConfiguration)
============================================

Here is an example of how to create a SYZ simulation setup for Siwave using SimulationConfiguration class.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb.legacy.edb_core.edb import EdbLegacy
    from pyedb.generic.constants import SolverType
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

    simconfig = edbapp.new_simulation_configuration()
    simconfig.solver_type = SolverType.SiwaveSYZ
    simconfig.mesh_freq = "40.25GHz"
    edbapp.build_simulation_project(simconfig)
    edbapp.close()

Create coaxial port on component
================================

Now, if you want to create a HFSS coaxial port on a component, here is a simple example.

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
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # loading EDB
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

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

