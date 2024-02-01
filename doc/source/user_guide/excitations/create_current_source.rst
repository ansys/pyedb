.. _create_current_source_example:

Create current and voltage sources
==================================

This page shows how to create current and voltage sources on a component.

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    # create simple current source on ``U1`` component between ``USB3_D_N`` and ``GND`` nets
    edbapp.siwave.create_current_source_on_net("U1", "USB3_D_N", "U1", "GND", 0.1, 0) != ""

    # retrieve pins from ``U1`` component
    pins = edbapp.components.get_pin_from_component("U1")

    # create current source on specific pins
    edbapp.siwave.create_current_source_on_pin(pins[301], pins[10], 0.1, 0, "I22")

    # create pin group on ``GND`` net from ``U1`` component
    edbapp.siwave.create_pin_group_on_net(
        reference_designator="U1", net_name="GND", group_name="gnd"
    )

    # creat pin group on specific pins
    edbapp.siwave.create_pin_group(
        reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vrm_pos"
    )

    # create current source on pin group
    edbapp.siwave.create_current_source_on_pin_group(
        pos_pin_group_name="vrm_pos", neg_pin_group_name="gnd", name="vrm_current_source"
    )

    #  create voltage source
    edbapp.siwave.create_pin_group(
        reference_designator="U1", pin_numbers=["R23", "P23"], group_name="sink_pos"
    )
    edbapp.siwave.create_voltage_source_on_pin_group(
        "sink_pos", "gnd", name="vrm_voltage_source"
    )

    # create voltage probe
    edbapp.siwave.create_pin_group(
        reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vp_pos"
    )
    edbapp.siwave.create_pin_group(
        reference_designator="U1", pin_numbers=["R23", "P23"], group_name="vp_neg"
    )
    edbapp.siwave.create_voltage_probe_on_pin_group("vprobe", "vp_pos", "vp_neg")
    edbapp.save_edb()
    edbapp.close_edb()


.. image:: ../../Resources/create_sources_and_probes.png
..   :width: 800
..   :alt: Current and voltage sources created on a component
