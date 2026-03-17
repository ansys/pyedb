src.pyedb.dotnet.database.source_excitations
============================================

.. py:module:: src.pyedb.dotnet.database.source_excitations


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.source_excitations.SourceExcitation


Module Contents
---------------

.. py:class:: SourceExcitation(pedb)

   Manage sources and excitations.


   .. py:method:: get_edge_from_port(port)


   .. py:method:: create_circuit_port_on_pin(pos_pin, neg_pin, impedance=50, port_name=None)

      Create a circuit port on a pin.

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

      Returns
      -------
      str
          Port Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")



   .. py:method:: create_voltage_source_on_pin(pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source.

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

      Parameters
      ----------
      pos_pin : Object
          Positive pin.
      neg_pin : Object
          Negative pin.
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

      Create a Resistor boundary between two given pins..

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
          Name of the resistor.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_resistor_on_pin(pins[0], pins[1], 50, "res_name")



   .. py:method:: create_circuit_port_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, impedance_value=50, port_name='')

      Create a circuit port on a NET.

      It groups all pins belonging to the specified net and then applies the port on PinGroups.

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
          Name of the negative net name. The default is ``None`` which will look for GND Nets.
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



   .. py:method:: create_voltage_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source.

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
          Name of the negative net name. The default is ``None`` which will look for GND Nets.
      voltage_value : float, optional
          Value for the voltage. The default is ``3.3``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          The name of the source.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edb.excitation_manager.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")



   .. py:method:: create_current_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, current_value=0.1, phase_value=0, source_name='')

      Create a current source.

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
          Name of the negative net name. The default is ``None`` which will look for GND Nets.
      current_value : float, optional
          Value for the current. The default is ``0.1``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          The name of the source.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edb.excitation_manager.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")



   .. py:method:: create_coax_port_on_component(ref_des_list, net_list, delete_existing_terminal=False)

      Create a coaxial port on a component or component list on a net or net list.
         The name of the new coaxial port is automatically assigned.

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




   .. py:method:: create_bundle_wave_port(primitives_id, points_on_edge, port_name=None, horizontal_extent_factor=5, vertical_extent_factor=3, pec_launch_width='0.01mm')

      Create a bundle wave port.

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



   .. py:method:: create_differential_wave_port(positive_primitive_id, positive_points_on_edge, negative_primitive_id, negative_points_on_edge, port_name=None, horizontal_extent_factor=5, vertical_extent_factor=3, pec_launch_width='0.01mm')

      Create a differential wave port.

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



   .. py:method:: create_hfss_ports_on_padstack(pinpos, portname=None)

      Create an HFSS port on a padstack.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.excitation_manager.create_edge_port` instead.

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



   .. py:method:: create_port_between_pin_and_layer(component_name=None, pins_name=None, layer_name=None, reference_net=None, impedance=50.0)

      Create circuit port between pin and a reference layer.

      Parameters
      ----------
      component_name : str
          Component name. The default is ``None``.
      pins_name : str
          Pin name or list of pin names. The default is ``None``.
      layer_name : str
          Layer name. The default is ``None``.
      reference_net : str
          Reference net name. The default is ``None``.
      impedance : float, optional
          Port impedance. The default is ``50.0`` in ohms.

      Returns
      -------
      PadstackInstanceTerminal
          Created terminal.




   .. py:method:: create_padstack_instance_terminal(name='', padstack_instance_id=None, padstack_instance_name=None)


   .. py:method:: create_pin_group_terminal(pin_group)


   .. py:method:: create_terminal_from_pin_group(pin_group, name='')


   .. py:method:: create_point_terminal(x, y, layer, net, name='')


   .. py:method:: create_edge_terminal(primitive_name, x, y, name='')


   .. py:method:: create_bundle_terminal(terminals, name='')


   .. py:method:: create_edge_port(location, primitive_name, name, impedance=50, is_wave_port=True, horizontal_extent_factor=1, vertical_extent_factor=1, pec_launch_width=0.0001) -> pyedb.dotnet.database.edb_data.ports.WavePort

      Create an edge port on a primitive specific location.

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



   .. py:method:: create_rlc_boundary_on_pins(positive_pin=None, negative_pin=None, rvalue=0.0, lvalue=0.0, cvalue=0.0)

      Create hfss rlc boundary on pins.

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




   .. py:method:: create_circuit_port_on_pin_group(pos_pin_group_name, neg_pin_group_name, impedance=50, name=None)

      Create a port between two pin groups.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      impedance : int, float, optional
          Impedance of the port. Default is ``50``.
      name : str, optional
          Port name.

      Returns
      -------
      bool




   .. py:method:: create_current_source_on_pin_group(pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None)

      Create current source between two pin groups.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      magnitude : int, float, optional
          Magnitude of the source.
      phase : int, float, optional
          Phase of the source

      Returns
      -------
      bool




   .. py:property:: pin_groups

      All Layout Pin groups.

      Returns
      -------
      list
          List of all layout pin groups.



   .. py:method:: create_voltage_source_on_pin_group(pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None, impedance=0.001)

      Create voltage source between two pin groups.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      magnitude : int, float, optional
          Magnitude of the source.
      phase : int, float, optional
          Phase of the source

      Returns
      -------
      bool




   .. py:method:: create_voltage_probe_on_pin_group(probe_name, pos_pin_group_name, neg_pin_group_name, impedance=1000000)

      Create voltage probe between two pin groups.

      Parameters
      ----------
      probe_name : str
          Name of the probe.
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      impedance : int, float, optional
          Phase of the source.

      Returns
      -------
      bool




   .. py:method:: create_port_on_component(component, net_list, port_type=SourceType.CoaxPort, do_pingroup=True, reference_net='gnd', port_name=None, solder_balls_height=None, solder_balls_size=None, solder_balls_mid_size=None, extend_reference_pins_outside_component=False)

      Create ports on a component.

      Parameters
      ----------
      component : str or  self._pedb.component
          EDB component or str component name.
      net_list : str or list of string.
          List of nets where ports must be created on the component.
          If the net is not part of the component, this parameter is skipped.
      port_type : SourceType enumerator, CoaxPort or CircuitPort
          Type of port to create. ``CoaxPort`` generates solder balls.
          ``CircuitPort`` generates circuit ports on pins belonging to the net list.
      do_pingroup : bool
          True activate pingroup during port creation (only used with combination of CircPort),
          False will take the closest reference pin and generate one port per signal pin.
      refnet : string or list of string.
          list of the reference net.
      port_name : str
          Port name for overwriting the default port-naming convention,
          which is ``[component][net][pin]``. The port name must be unique.
          If a port with the specified name already exists, the
          default naming convention is used so that port creation does
          not fail.
      solder_balls_height : float, optional
          Solder balls height used for the component. When provided default value is overwritten and must be
          provided in meter.
      solder_balls_size : float, optional
          Solder balls diameter. When provided auto evaluation based on padstack size will be disabled.
      solder_balls_mid_size : float, optional
          Solder balls mid-diameter. When provided if value is different than solder balls size, spheroid shape will
          be switched.
      extend_reference_pins_outside_component : bool
          When no reference pins are found on the component extend the pins search with taking the closest one. If
          `do_pingroup` is `True` will be set to `False`. Default value is `False`.

      Returns
      -------
      double, bool
          Salder ball height vale, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> net_list = ["M_DQ<1>", "M_DQ<2>", "M_DQ<3>", "M_DQ<4>", "M_DQ<5>"]
      >>> edbapp.components.create_port_on_component(cmp="U2A5", net_list=net_list,
      >>> port_type=SourceType.CoaxPort, do_pingroup=False, refnet="GND")




   .. py:method:: create_pingroup_from_pins(pins, group_name=None)

      Create a pin group on a component.

      Parameters
      ----------
      pins : list
          List of EDB pins.
      group_name : str, optional
          Name for the group. The default is ``None``, in which case
          a default name is assigned as follows: ``[component Name] [NetName]``.

      Returns
      -------
      tuple
          The tuple is structured as: (bool, pingroup).

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.create_pingroup_from_pins(gndpinlist, "MyGNDPingroup")




   .. py:method:: create_port_on_pins(refdes, pins, reference_pins, impedance=50.0, port_name=None, pec_boundary=False, pingroup_on_single_pin=False)

      Create circuit port between pins and reference ones.

      Parameters
      ----------
      refdes : Component reference designator
          str or EDBComponent object.
      pins : pin specifier(s) or instance(s) where the port terminal is to be created. Single pin name or a list of
      several can be provided. If several pins are provided a pin group will be created. Pin specifiers can be the
      global EDB object ID or padstack instance name or pin name on component with refdes ``refdes``. Pin instances
      can be provided as ``EDBPadstackInstance`` objects.
      For instance for the pin called ``Pin1`` located on component with refdes ``U1``: ``U1-Pin1``, ``Pin1`` with
      ``refdes=U1``, the pin's global EDB object ID, or the ``EDBPadstackInstance`` corresponding to the pin can be
      provided.
          Union[int, str, EDBPadstackInstance], List[Union[int, str, EDBPadstackInstance]]
      reference_pins : reference pin specifier(s) or instance(s) for the port reference terminal. Allowed values are
      the same as for the ``pins`` parameter.
          Union[int, str, EDBPadstackInstance], List[Union[int, str, EDBPadstackInstance]]
      impedance : Port impedance
          str, float
      port_name : str, optional
          Port name. The default is ``None``, in which case a name is automatically assigned.
      pec_boundary : bool, optional
      Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
      a perfect short is created between the pin and impedance is ignored. This
      parameter is only supported on a port created between two pins, such as
      when there is no pin group.
      pingroup_on_single_pin : bool
          If ``True`` force using pingroup definition on single pin to have the port created at the pad center. If
          ``False`` the port is created at the pad edge. Default value is ``False``.

      Returns
      -------
      EDB terminal created, or False if failed to create.

      Example:
      >>> from pyedb import Edb
      >>> edb = Edb(path_to_edb_file)
      >>> pin = "AJ6"
      >>> ref_pins = ["AM7", "AM4"]
      Or to take all reference pins
      >>> ref_pins = [pin for pin in list(edb.components["U2A5"].pins.values()) if pin.net_name == "GND"]
      >>> edb.components.create_port_on_pins(refdes="U2A5", pins=pin, reference_pins=ref_pins)
      >>> edb.save()
      >>> edb.close()



   .. py:method:: create_port(terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, ref_terminal=None, is_circuit_port=False, name=None) -> pyedb.dotnet.database.edb_data.ports.CircuitPort | pyedb.dotnet.database.edb_data.ports.BundleWavePort | pyedb.dotnet.database.edb_data.ports.WavePort | pyedb.dotnet.database.edb_data.ports.CoaxPort | pyedb.dotnet.database.edb_data.ports.GapPort

      Create a port.

      Parameters
      ----------
      terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          Positive terminal of the port.
      ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          optional
          Negative terminal of the port.
      is_circuit_port : bool, optional
          Whether it is a circuit port. The default is ``False``.
      name: str, optional
          Name of the created port. The default is None, a random name is generated.
      Returns
      -------
      list: [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
          :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,].



   .. py:method:: create_voltage_probe(terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, ref_terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal) -> pyedb.dotnet.database.cell.terminal.terminal.Terminal

      Create a voltage probe.

      Parameters
      ----------
      terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          Positive terminal of the port.
      ref_terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          Negative terminal of the probe.

      Returns
      -------
      pyedb.dotnet.database.edb_data.terminals.Terminal



   .. py:method:: create_voltage_source(terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, ref_terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal) -> pyedb.dotnet.database.cell.terminal.terminal.Terminal

      Create a voltage source.

      Parameters
      ----------
      terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
          Positive terminal of the port.
      ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
          Negative terminal of the source.

      Returns
      -------
      class:`legacy.database.edb_data.ports.ExcitationSources`



   .. py:method:: create_current_source(terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, ref_terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal) -> pyedb.dotnet.database.cell.terminal.terminal.Terminal

      Create a current source.

      Parameters
      ----------
      terminal : :class:`legacy.database.edb_data.terminals.EdgeTerminal`,
          :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`legacy.database.edb_data.terminals.PointTerminal`,
          :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
          Positive terminal of the port.
      ref_terminal : class:`legacy.database.edb_data.terminals.EdgeTerminal`,
          :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`legacy.database.edb_data.terminals.PointTerminal`,
          :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
          Negative terminal of the source.

      Returns
      -------
      :class:`legacy.edb_core.edb_data.ports.ExcitationSources`



   .. py:method:: get_point_terminal(name, net_name, location, layer) -> pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal

      Place a voltage probe between two points.

      Parameters
      ----------
      name : str,
          Name of the terminal.
      net_name : str
          Name of the net.
      location : list
          Location of the terminal.
      layer : str,
          Layer of the terminal.

      Returns
      -------
      :class:`legacy.edb_core.edb_data.terminals.PointTerminal`



