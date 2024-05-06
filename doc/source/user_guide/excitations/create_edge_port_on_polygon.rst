.. _create_edge_port_on_polygon_example:

Create an edge port
===================

This page shows how to create an edge port on a polygon and trace.

.. autosummary::
   :toctree: _autosummary

.. code:: python


    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # Ansys release version
    ansys_version = "2024.1"

    # download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/edb_edge_ports.aedb", destination=temp_folder)

    # load EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2024.1")

    # retrieve polygon list
    poly_list = [
        poly for poly in edbapp.layout.primitives if int(poly.GetPrimitiveType()) == 2
    ]

    # select specific polygons
    port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
    ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]

    #  define port location
    port_location = [-65e-3, -13e-3]
    ref_location = [-63e-3, -13e-3]

    # create edge port
    edbapp.hfss.create_edge_port_on_polygon(
        polygon=port_poly,
        reference_polygon=ref_poly,
        terminal_point=port_location,
        reference_point=ref_location,
    )

    # select specific polygon
    port_poly = [poly for poly in poly_list if poly.GetId() == 23][0]
    ref_poly = [poly for poly in poly_list if poly.GetId() == 22][0]

    # define port location
    port_location = [-65e-3, -10e-3]
    ref_location = [-65e-3, -10e-3]

    # create port on polygon
    edbapp.hfss.create_edge_port_on_polygon(
        polygon=port_poly,
        reference_polygon=ref_poly,
        terminal_point=port_location,
        reference_point=ref_location,
    )

    # select polygon
    port_poly = [poly for poly in poly_list if poly.GetId() == 25][0]

    # define port location
    port_location = [-65e-3, -7e-3]

    # create edge port with defining reference layer
    edbapp.hfss.create_edge_port_on_polygon(
        polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
    )

    # create trace
    sig = edbapp.modeler.create_trace(
        [["-55mm", "-10mm"], ["-29mm", "-10mm"]], "TOP", "1mm", "SIG", "Flat", "Flat"
    )

    # create wave port at the end of the trace
    sig.create_edge_port("pcb_port_1", "end", "Wave", None, 8, 8)

    # create gap port at the beginning of the trace
    sig.create_edge_port("pcb_port_2", "start", "gap")

    # retrieve existing port
    gap_port = edbapp.ports["pcb_port_2"]

    # rename port
    gap_port.name = "gap_port"

    # change gap to circuit port
    gap_port.is_circuit_port = True

    edbapp.save_edb()
    edbapp.close_edb()

.. image:: ../../Resources/create_edge_port_on_polygon_and_trace.png
..   :width: 800
..   :alt: Edge port created on a polygon and trace