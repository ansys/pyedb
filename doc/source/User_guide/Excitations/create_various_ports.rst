Create coaxial port on component
================================
This section shows a simple example to create HFSS coaxial port on a component.

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

    prim_1_id = [i.id for i in edb.modeler.primitives if i.net_name == "trace_2"][0]
    assert edb.hfss.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")

    prim_2_id = [i.id for i in edb.modeler.primitives if i.net_name == "trace_3"][0]
    assert edb.hfss.create_edge_port_horizontal(
        prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
    )
    assert edb.hfss.get_ports_number() == 2
    port_ver = edb.ports["port_ver"]
    assert not port_ver.is_null
    assert port_ver.hfss_type == "Gap"
    port_hori = edb.ports["port_hori"]
    assert port_hori.ref_terminal

    args = {
        "layer_name": "1_Top",
        "net_name": "SIGP",
        "width": "0.1mm",
        "start_cap_style": "Flat",
        "end_cap_style": "Flat",
    }
    traces = []
    trace_paths = [
        [["-40mm", "-10mm"], ["-30mm", "-10mm"]],
        [["-40mm", "-10.2mm"], ["-30mm", "-10.2mm"]],
        [["-40mm", "-10.4mm"], ["-30mm", "-10.4mm"]],
    ]
    for p in trace_paths:
        t = edb.modeler.create_trace(path_list=p, **args)
        traces.append(t)

    assert edb.hfss.create_wave_port(traces[0].id, trace_paths[0][0], "wave_port")
    wave_port = edb.ports["wave_port"]
    wave_port.horizontal_extent_factor = 10
    wave_port.vertical_extent_factor = 10
    assert wave_port.horizontal_extent_factor == 10
    assert wave_port.vertical_extent_factor == 10
    wave_port.radial_extent_factor = 1
    assert wave_port.radial_extent_factor == 1
    assert wave_port.pec_launch_width
    assert not wave_port.deembed
    assert wave_port.deembed_length == 0.0
    assert wave_port.do_renormalize
    wave_port.do_renormalize = False
    assert not wave_port.do_renormalize
    assert edb.hfss.create_differential_wave_port(
        traces[0].id,
        trace_paths[0][0],
        traces[1].id,
        trace_paths[1][0],
        horizontal_extent_factor=8,
        port_name="df_port",
    )
    assert edb.ports["df_port"]
    p, n = edb.ports["df_port"].terminals
    assert edb.ports["df_port"].decouple()
    p.couple_ports(n)

    traces_id = [i.id for i in traces]
    paths = [i[1] for i in trace_paths]
    _, df_port = edb.hfss.create_bundle_wave_port(traces_id, paths)
    assert df_port.name
    assert df_port.terminals
    df_port.horizontal_extent_factor = 10
    df_port.vertical_extent_factor = 10
    df_port.deembed = True
    df_port.deembed_length = "1mm"
    assert df_port.horizontal_extent_factor == 10
    assert df_port.vertical_extent_factor == 10
    assert df_port.deembed
    assert df_port.deembed_length == 1e-3
    edb.close()