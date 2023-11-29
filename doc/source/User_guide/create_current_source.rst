Create circuit ports on component
=================================
This section describes how to create current and voltage sources:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file('edb/ANSYS-HSD_V1.aedb', destination=temp_folder)
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    # create simple current source on component U1 between net USB3_D_N and GND
    edbapp.siwave.create_current_source_on_net("U1", "USB3_D_N", "U1", "GND", 0.1, 0) != ""

    # retrieve pins from component U1
    pins = edbapp.components.get_pin_from_component("U1")

    # create current source on specific pins
    edbapp.siwave.create_current_source_on_pin(pins[301], pins[10], 0.1, 0, "I22")

    # creating pin group on net GND from component U1
    edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd")

    # creating pin group on specific pins
    edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vrm_pos")

    # creating current source on pin group
    edbapp.siwave.create_current_source_on_pin_group(pos_pin_group_name="vrm_pos", neg_pin_group_name="gnd",
                                name="vrm_current_source")

    #  creating voltage source
    edbapp.siwave.create_pin_group(
            reference_designator="U1", pin_numbers=["R23", "P23"], group_name="sink_pos"
        )
    edbapp.siwave.create_voltage_source_on_pin_group("sink_pos", "gnd", name="vrm_voltage_source")

    # creating voltage probe
    edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vp_pos")
    edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["R23", "P23"], group_name="vp_neg")
    dbapp.siwave.create_voltage_probe_on_pin_group("vprobe", "vp_pos", "vp_neg")
    edbapp.probes["vprobe"]
    edbapp.siwave.place_voltage_probe(
            "vprobe_2", "1V0", ["112mm", "24mm"], "1_Top", "GND", ["112mm", "27mm"], "Inner1(GND1)"
        )

    # retrieving voltage probes
    vprobe_2 = edbapp.probes["vprobe_2"]
    ref_term = vprobe_2.ref_terminal
    ref_term.location = [0, 0]
    ref_term.layer
    ref_term.layer = "1_Top"
