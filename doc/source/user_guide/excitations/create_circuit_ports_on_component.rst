.. _create_circuit_port_on_component_example:

Create a circuit port
=====================

This page shows how to retrieve pins and create a circuit port on a component.

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.2")

    edbapp.siwave.create_circuit_port_on_net("U1", "1V0", "U1", "GND", 50, "test")
    edbapp.components.get_pin_from_component("U1")

    # create pin groups
    edbapp.siwave.create_pin_group_on_net("U1", "1V0", "PG_V1P0_S0")
    # create port on pin group
    edbapp.siwave.create_circuit_port_on_pin_group(
        "PG_V1P0_S0", "PinGroup_2", impedance=50, name="test_port"
    )
    # rename port with property setter
    edbapp.excitations["test_port"].name = "test_rename"
    # retrieve port
    created_port = (port for port in list(edbapp.excitations) if port == "test_rename")
    edbapp.save_edb()
    edbapp.close_edb()


.. image:: ../../resources/create_circuit_ports_on_component.png
    :width: 800
    :alt: Circuit port created on a component