Create RLC component
====================
This section shows how to create RLC component with EDB:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # download and open EDB project
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    # retrieving pins from component U1 and net 1V0
    pins = edbapp.components.get_pin_from_component("U1", "1V0")

    # reference pins
    ref_pins = edbapp.components.get_pin_from_component("U1", "GND")

    # creating rlc boundary
    edbapp.hfss.create_rlc_boundary_on_pins(
        pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13
    )

    # close EDB
    edbapp.close()