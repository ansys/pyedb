.. _create_edge_port_on_polygon_example:

Create edge port on polygon
===========================
This section describes how create edge port on polygon.

.. autosummary::
   :toctree: _autosummary

.. code:: python


    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads


    # Ansys release version
    ansys_version = "2023.2"

    # download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # loading EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    # retrieving polygon list
    poly_list = [
        poly for poly in edbapp.layout.primitives if int(poly.GetPrimitiveType()) == 2
    ]

    # selecting specific polygons
    port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
    ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]

    #  defining port location
    port_location = [-65e-3, -13e-3]
    ref_location = [-63e-3, -13e-3]

    # creating edge port
    edbapp.hfss.create_edge_port_on_polygon(
        polygon=port_poly,
        reference_polygon=ref_poly,
        terminal_point=port_location,
        reference_point=ref_location,
    )

    # selecting specific polygon
    port_poly = [poly for poly in poly_list if poly.GetId() == 23][0]
    ref_poly = [poly for poly in poly_list if poly.GetId() == 22][0]

    # port location
    port_location = [-65e-3, -10e-3]
    ref_location = [-65e-3, -10e-3]

    #  create port on polygon
    edbapp.hfss.create_edge_port_on_polygon(
        polygon=port_poly,
        reference_polygon=ref_poly,
        terminal_point=port_location,
        reference_point=ref_location,
    )

    # selecting polygon
    port_poly = [poly for poly in poly_list if poly.GetId() == 25][0]

    # port location
    port_location = [-65e-3, -7e-3]

    # create edge port with defining reference layer
    edbapp.hfss.create_edge_port_on_polygon(
        polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
    )

    # create trace
    sig = edbapp.modeler.create_trace(
        [[0, 0], ["9mm", 0]], "TOP", "1mm", "SIG", "Flat", "Flat"
    )

    # create wave port a the end of the trace
    sig.create_edge_port("pcb_port_1", "end", "Wave", None, 8, 8)

    # create gap port at the beginning of the trace
    sig.create_edge_port("pcb_port_2", "start", "gap")

    # retrieving existing port
    gap_port = edbapp.ports["pcb_port_2"]

    # renaming port
    gap_port.name = "gap_port"

    # changing gap to circuit port
    gap_port.is_circuit_port = True

    edbapp.close()