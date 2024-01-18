.. _create_rlc_component_example:

Create RLC boundary between pins
================================
This section shows how to create RLC component with EDB:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # download and open EDB project
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    # retrieving pins from component U1 and net 1V0
    pins = edbapp.components.get_pin_from_component("U1", "1V0")

    # retrieving reference pins from component U1 and net GND
    ref_pins = edbapp.components.get_pin_from_component("U1", "GND")

    # create RLC network between 2 pins
    edbapp.components.create(
        [pins[0], ref_pins[0]], "test_0rlc", r_value=1.67, l_value=1e-13, c_value=1e-11
    )
    edbapp.close()