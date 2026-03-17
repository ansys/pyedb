src.pyedb.dotnet.database.hfss
==============================

.. py:module:: src.pyedb.dotnet.database.hfss

.. autoapi-nested-parse::

   This module contains the ``EdbHfss`` class.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.hfss.EdbHfss


Module Contents
---------------

.. py:class:: EdbHfss(p_edb)

   Bases: :py:obj:`object`


   Manages EDB method to configure Hfss setup accessible from `Edb.hfss` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder")
   >>> edb_hfss = edb_3dedbapp.hfss


   .. py:property:: hfss_extent_info

      HFSS extent information.



   .. py:property:: excitations
      :type: Dict[str, Union[pyedb.dotnet.database.edb_data.ports.BundleWavePort, pyedb.dotnet.database.edb_data.ports.GapPort, pyedb.dotnet.database.edb_data.ports.CircuitPort, pyedb.dotnet.database.edb_data.ports.CoaxPort, pyedb.dotnet.database.edb_data.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CircuitPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CoaxPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.BundleWavePort`]]




   .. py:property:: ports
      :type: Dict[str, Union[pyedb.dotnet.database.edb_data.ports.BundleWavePort, pyedb.dotnet.database.edb_data.ports.GapPort, pyedb.dotnet.database.edb_data.ports.CircuitPort, pyedb.dotnet.database.edb_data.ports.CoaxPort, pyedb.dotnet.database.edb_data.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CircuitPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CoaxPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.BundleWavePort`]]




   .. py:property:: sources
      :type: Dict[str, pyedb.dotnet.database.edb_data.ports.ExcitationSources]


      Get all sources.



   .. py:property:: probes
      :type: Dict[str, Union[pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal, pyedb.dotnet.database.cell.terminal.bundle_terminal.BundleTerminal, pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal, pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal]]


      Get all probes.



   .. py:method:: get_trace_width_for_traces_with_ports()

      Retrieve the trace width for traces with ports.

      Returns
      -------<
      dict
          Dictionary of trace width data.



   .. py:method:: create_circuit_port_on_pin(pos_pin, neg_pin, impedance=50, port_name=None)

      Create Circuit Port on Pin.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_circuit_port_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Edb Pin
      neg_pin : Object
          Edb Pin
      impedance : float
          Port Impedance
      port_name : str, optional
          Port Name

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")

      Returns
      -------
      str
          Port Name.




   .. py:method:: create_voltage_source_on_pin(pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_voltage_source_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive Pin.
      neg_pin : Object
          Negative Pin.
      voltage_value : float, optional
          Value for the voltage. The default is ``3.3``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          Source Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_voltage_source_on_pin(pins[0], pins[1], 50, "source_name")



   .. py:method:: create_current_source_on_pin(pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name='')

      Create a current source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_current_source_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive Pin.
      neg_pin : Object
          Negative Pin.
      current_value : float, optional
          Value for the current. The default is ``0.1``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          Source Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_current_source_on_pin(pins[0], pins[1], 50, "source_name")



   .. py:method:: create_resistor_on_pin(pos_pin, neg_pin, rvalue=1, resistor_name='')

      Create a Resistor boundary between two given pins.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_resistor_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive Pin.
      neg_pin : Object
          Negative Pin.
      rvalue : float, optional
          Resistance value. The default is ``1``.
      resistor_name : str, optional
          Name of the resistor. The default is ``""``.

      Returns
      -------
      str
          Name of the Resistor.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_resistor_on_pin(pins[0], pins[1], 50, "res_name")



   .. py:method:: create_circuit_port_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name='GND', impedance_value=50, port_name='')

      Create a circuit port on a NET.
      It groups all pins belonging to the specified net and then applies the port on PinGroups.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_circuit_port_on_net` instead.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. The default is ``None``, in which case the name of
          the positive net is assigned.
      negative_net_name : str, optional
          Name of the negative net name. The default is ``"GND"``.
      impedance_value : float, optional
          Port impedance value. The default is ``50``.
      port_name : str, optional
          Name of the port. The default is ``""``.

      Returns
      -------
      str
          The name of the port.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.excitation_manager.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")



   .. py:method:: create_voltage_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name='GND', voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_voltage_source_on_net` instead.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. The default is ``None``, in which case the name of
          the positive net is assigned.
      negative_net_name : str, optional
          Name of the negative net. The default is ``"GND"``.
      voltage_value : float, optional
          Value for the voltage. The default is ``3.3``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          Source Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edb.excitation_manager.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")



   .. py:method:: create_current_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name='GND', current_value=0.1, phase_value=0, source_name='')

      Create a current source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_current_source_on_net` instead.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. The default is ``None``, in which case the name of
          the positive net is assigned.
      negative_net_name : str, optional
          Name of the negative net. The default is ``"GND"``.
      current_value : float, optional
          Value for the current. The default is ``0.1``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          Source Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edb.excitation_manager.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")



   .. py:method:: create_coax_port_on_component(ref_des_list, net_list, delete_existing_terminal=False)

      Create a coaxial port on a component or component list on a net or net list.
         The name of the new coaxial port is automatically assigned.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_coax_port_on_component` instead.

      Parameters
      ----------
      ref_des_list : list, str
          List of one or more reference designators.

      net_list : list, str
          List of one or more nets.

      delete_existing_terminal : bool
          Only active with grpc version. This argument is added only to ensure compatibility between DotNet and grpc.


      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: create_differential_wave_port(positive_primitive_id, positive_points_on_edge, negative_primitive_id, negative_points_on_edge, port_name=None, horizontal_extent_factor=5, vertical_extent_factor=3, pec_launch_width='0.01mm')

      Create a differential wave port.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_differential_wave_port` instead.

      Parameters
      ----------
      positive_primitive_id : int, EDBPrimitives
          Primitive ID of the positive terminal.
      positive_points_on_edge : list
          Coordinate of the point to define the edge terminal.
          The point must be close to the target edge but not on the two
          ends of the edge.
      negative_primitive_id : int, EDBPrimitives
          Primitive ID of the negative terminal.
      negative_points_on_edge : list
          Coordinate of the point to define the edge terminal.
          The point must be close to the target edge but not on the two
          ends of the edge.
      port_name : str, optional
          Name of the port. The default is ``None``.
      horizontal_extent_factor : int, float, optional
          Horizontal extent factor. The default value is ``5``.
      vertical_extent_factor : int, float, optional
          Vertical extent factor. The default value is ``3``.
      pec_launch_width : str, optional
          Launch Width of PEC. The default value is ``"0.01mm"``.

      Returns
      -------
      tuple
          The tuple contains: (port_name, pyedb.dotnet.database.edb_data.sources.ExcitationDifferential).

      Examples
      --------
      >>> edb.excitation_manager.create_differential_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])



   .. py:method:: create_bundle_wave_port(primitives_id, points_on_edge, port_name=None, horizontal_extent_factor=5, vertical_extent_factor=3, pec_launch_width='0.01mm')

      Create a bundle wave port.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_bundle_wave_port` instead.

      Parameters
      ----------
      primitives_id : list
          Primitive ID of the positive terminal.
      points_on_edge : list
          Coordinate of the point to define the edge terminal.
          The point must be close to the target edge but not on the two
          ends of the edge.
      port_name : str, optional
          Name of the port. The default is ``None``.
      horizontal_extent_factor : int, float, optional
          Horizontal extent factor. The default value is ``5``.
      vertical_extent_factor : int, float, optional
          Vertical extent factor. The default value is ``3``.
      pec_launch_width : str, optional
          Launch Width of PEC. The default value is ``"0.01mm"``.

      Returns
      -------
      tuple
          The tuple contains: (port_name, pyedb.egacy.database.edb_data.sources.ExcitationDifferential).

      Examples
      --------
      >>> edb.excitation_manager.create_bundle_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])



   .. py:method:: create_hfss_ports_on_padstack(pinpos, portname=None)

      Create an HFSS port on a padstack.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_hfss_ports_on_padstack` instead.

      Parameters
      ----------
      pinpos :
          Position of the pin.

      portname : str, optional
           Name of the port. The default is ``None``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: create_edge_port(location, primitive_name, name, impedance=50, is_wave_port=True, horizontal_extent_factor=1, vertical_extent_factor=1, pec_launch_width=0.0001) -> pyedb.dotnet.database.edb_data.ports.WavePort

      Create an edge port on a primitive specific location.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitations.create_edge_port` instead.

      Parameters
      ----------
      location : list
          Port location.
      primitive_name : str
          Name of primitive.
      name : str
          Port name.
      impedance : float, optional
          Impedance.
      is_wave_port : bool, optional
          Whether if it is a wave port or gap port.
      horizontal_extent_factor : float, optional
          Horizontal extent factor for wave ports.
      vertical_extent_factor  : float, optional
          Vertical extent factor for wave ports.
      pec_launch_width : float, optional
          Pec launcher width for wave ports.




   .. py:method:: create_edge_port_on_polygon(polygon=None, reference_polygon=None, terminal_point=None, reference_point=None, reference_layer=None, port_name=None, port_impedance=50.0, force_circuit_port=False)

      Create lumped port between two edges from two different polygons. Can also create a vertical port when
      the reference layer name is only provided. When a port is created between two edge from two polygons which don't
      belong to the same layer, a circuit port will be automatically created instead of lumped. To enforce the circuit
      port instead of lumped,use the boolean force_circuit_port.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_edge_port_on_polygon` instead.

      Parameters
      ----------
      polygon : The EDB polygon object used to assign the port.
          Edb.Cell.Primitive.Polygon object.

      reference_polygon : The EDB polygon object used to define the port reference.
          Edb.Cell.Primitive.Polygon object.

      terminal_point : The coordinate of the point to define the edge terminal of the port. This point must be
      located on the edge of the polygon where the port has to be placed. For instance taking the middle point
      of an edge is a good practice but any point of the edge should be valid. Taking a corner might cause unwanted
      port location.
          list[float, float] with values provided in meter.

      reference_point : same as terminal_point but used for defining the reference location on the edge.
          list[float, float] with values provided in meter.

      reference_layer : Name used to define port reference for vertical ports.
          str the layer name.

      port_name : Name of the port.
          str.

      port_impedance : port impedance value. Default value is 50 Ohms.
          float, impedance value.

      force_circuit_port ; used to force circuit port creation instead of lumped. Works for vertical and coplanar
      ports.

      Examples
      --------

      >>> edb_path = path_to_edb
      >>> edb = Edb(edb_path)
      >>> poly_list = [poly for poly in list(edb.layout.primitives) if poly.GetPrimitiveType() == 2]
      >>> port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
      >>> ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]
      >>> port_location = [-65e-3, -13e-3]
      >>> ref_location = [-63e-3, -13e-3]
      >>> edb.excitation_manager.create_edge_port_on_polygon(polygon=port_poly, reference_polygon=ref_poly,
      >>> terminal_point=port_location, reference_point=ref_location)




   .. py:method:: create_wave_port(prim_id, point_on_edge, port_name=None, impedance=50, horizontal_extent_factor=5, vertical_extent_factor=3, pec_launch_width='0.01mm')

      Create a wave port.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_wave_port` instead.

      Parameters
      ----------
      prim_id : int, Primitive
          Primitive ID.
      point_on_edge : list
          Coordinate of the point to define the edge terminal.
          The point must be on the target edge but not on the two
          ends of the edge.
      port_name : str, optional
          Name of the port. The default is ``None``.
      impedance : int, float, optional
          Impedance of the port. The default value is ``50``.
      horizontal_extent_factor : int, float, optional
          Horizontal extent factor. The default value is ``5``.
      vertical_extent_factor : int, float, optional
          Vertical extent factor. The default value is ``3``.
      pec_launch_width : str, optional
          Launch Width of PEC. The default value is ``"0.01mm"``.

      Returns
      -------
      tuple
          The tuple contains: (Port name, pyedb.dotnet.database.edb_data.sources.Excitation).

      Examples
      --------
      >>> edb.excitation_manager.create_wave_port(0, ["-50mm", "-0mm"])



   .. py:method:: create_edge_port_vertical(prim_id, point_on_edge, port_name=None, impedance=50, reference_layer=None, hfss_type='Gap', horizontal_extent_factor=5, vertical_extent_factor=3, pec_launch_width='0.01mm')

      Create a vertical edge port.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_edge_port_vertical` instead.

      Parameters
      ----------
      prim_id : int
          Primitive ID.
      point_on_edge : list
          Coordinate of the point to define the edge terminal.
          The point must be on the target edge but not on the two
          ends of the edge.
      port_name : str, optional
          Name of the port. The default is ``None``.
      impedance : int, float, optional
          Impedance of the port. The default value is ``50``.
      reference_layer : str, optional
          Reference layer of the port. The default is ``None``.
      hfss_type : str, optional
          Type of the port. The default value is ``"Gap"``. Options are ``"Gap"``, ``"Wave"``.
      horizontal_extent_factor : int, float, optional
          Horizontal extent factor. The default value is ``5``.
      vertical_extent_factor : int, float, optional
          Vertical extent factor. The default value is ``3``.
      radial_extent_factor : int, float, optional
          Radial extent factor. The default value is ``0``.
      pec_launch_width : str, optional
          Launch Width of PEC. The default value is ``"0.01mm"``.

      Returns
      -------
      str
          Port name.



   .. py:method:: create_edge_port_horizontal(prim_id, point_on_edge, ref_prim_id=None, point_on_ref_edge=None, port_name=None, impedance=50, layer_alignment='Upper')

      Create a horizontal edge port.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_edge_port_horizontal` instead.

      Parameters
      ----------
      prim_id : int
          Primitive ID.
      point_on_edge : list
          Coordinate of the point to define the edge terminal.
          The point must be on the target edge but not on the two
          ends of the edge.
      ref_prim_id : int, optional
          Reference primitive ID. The default is ``None``.
      point_on_ref_edge : list, optional
          Coordinate of the point to define the reference edge
          terminal. The point must be on the target edge but not
          on the two ends of the edge. The default is ``None``.
      port_name : str, optional
          Name of the port. The default is ``None``.
      impedance : int, float, optional
          Impedance of the port. The default value is ``50``.
      layer_alignment : str, optional
          Layer alignment. The default value is ``Upper``. Options are ``"Upper"``, ``"Lower"``.

      Returns
      -------
      str
          Name of the port.



   .. py:method:: create_lumped_port_on_net(nets=None, reference_layer=None, return_points_only=False, digit_resolution=6, at_bounding_box=True)

      Create an edge port on nets. This command looks for traces and polygons on the
      nets and tries to assign vertical lumped port.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_lumped_port_on_net` instead.

      Parameters
      ----------
      nets : list, optional
          List of nets, str or Edb net.

      reference_layer : str, Edb layer.
           Name or Edb layer object.

      return_points_only : bool, optional
          Use this boolean when you want to return only the points from the edges and not creating ports. Default
          value is ``False``.

      digit_resolution : int, optional
          The number of digits carried for the edge location accuracy. The default value is ``6``.

      at_bounding_box : bool
          When ``True`` will keep the edges from traces at the layout bounding box location. This is recommended when
           a cutout has been performed before and lumped ports have to be created on ending traces. Default value is
           ``True``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: create_vertical_circuit_port_on_clipped_traces(nets=None, reference_net=None, user_defined_extent=None)

      Create an edge port on clipped signal traces.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_vertical_circuit_port_on_clipped_traces` instead.

      Parameters
      ----------
      nets : list, optional
          String of one net or EDB net or a list of multiple nets or EDB nets.

      reference_net : str, Edb net.
           Name or EDB reference net.

      user_defined_extent : [x, y], EDB PolygonData
          Use this point list or PolygonData object to check if ports are at this polygon border.

      Returns
      -------
      [[str]]
          Nested list of str, with net name as first value, X value for point at border, Y value for point at border,
          and terminal name.



   .. py:method:: get_layout_bounding_box(layout=None, digit_resolution=6)

      Evaluate the layout bounding box.

      Parameters
      ----------
      layout :
          Edb layout.

      digit_resolution : int, optional
          Digit Resolution. The default value is ``6``.

      Returns
      -------
      list
          [lower left corner X, lower left corner, upper right corner X, upper right corner Y].



   .. py:method:: add_setup(name=None)

      Adding method for grpc compatibility



   .. py:method:: get_ports_number()

      Return the total number of excitation ports in a layout.

      Parameters
      ----------
      None

      Returns
      -------
      int
         Number of ports.




   .. py:method:: create_rlc_boundary_on_pins(positive_pin=None, negative_pin=None, rvalue=0.0, lvalue=0.0, cvalue=0.0)

      Create hfss rlc boundary on pins.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_rlc_boundary_on_pins` instead.

      Parameters
      ----------
      positive_pin : Positive pin.
          Edb.Cell.Primitive.PadstackInstance

      negative_pin : Negative pin.
          Edb.Cell.Primitive.PadstackInstance

      rvalue : Resistance value

      lvalue : Inductance value

      cvalue . Capacitance value.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: generate_auto_hfss_regions()

      Generate auto HFSS regions.

      This method automatically identifies areas for use as HFSS regions in SIwave simulations.



