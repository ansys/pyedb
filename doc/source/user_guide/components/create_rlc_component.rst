.. _create_rlc_component_example:

Create an RLC component between pins
====================================

This page shows how to create an RLC component between pins:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # download and open EDB project
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.2")

    # retrieving pins from component U1 and net 1V0
    pins = edbapp.components.get_pin_from_component("U1", "1V0")

    # retrieving reference pins from component U1 and net GND
    ref_pins = edbapp.components.get_pin_from_component("U1", "GND")

    # create RLC network between 2 pins
    edbapp.components.create(
        [pins[0], ref_pins[0]], "test_0rlc", r_value=1.67, l_value=1e-13, c_value=1e-11
    )
    edbapp.save_edb()
    edbapp.close_edb()


.. image:: ../../resources/create_rlc_boundary_on_pin.png
  :width: 800
  :alt: Create RLC boundary