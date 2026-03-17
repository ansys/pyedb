src.pyedb.grpc.database.source_excitations
==========================================

.. py:module:: src.pyedb.grpc.database.source_excitations


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.source_excitations.SourceExcitationInternal
   src.pyedb.grpc.database.source_excitations.SourceExcitation


Module Contents
---------------

.. py:class:: SourceExcitationInternal

.. py:class:: SourceExcitation(pedb)

   Bases: :py:obj:`SourceExcitationInternal`


   Manage sources and excitations.

   Examples
   --------
   >>> # Initialize EDB session
   >>> from pyedb import Edb
   >>> edb = Edb(edbpath="path/to/your/edb")

   >>> # Access SourceExcitation class
   >>> source_excitations = edb.source_excitation

   >>> # 1. create_source_on_component
   >>> # Create voltage source on component pins
   >>> from pyedb.grpc.database.utility.sources import Source, SourceType
   >>> source = Source(
   ...     source_type=SourceType.Vsource,
   ...     name="V1",
   ...     positive_node=("U1", "VCC"),
   ...     negative_node=("U1", "GND"),
   ...     amplitude="1V",
   ...     phase="0deg",
   ...     impedance="50ohm",
   ... )
   >>> source_excitations.create_source_on_component([source])

   >>> # 2. create_port
   >>> # Create port between two terminals
   >>> pos_terminal = edb.terminals["MyTerminal"]
   >>> ref_terminal = edb.terminals["MyRefTerminal"]
   >>> port = source_excitations.create_port(pos_terminal, ref_terminal)

   >>> # 3. create_port_on_pins
   >>> # Create circuit port between component pins
   >>> port_term = source_excitations.create_port_on_pins(
   ...     refdes="U1", pins="Pin1", reference_pins=["GND_Pin1", "GND_Pin2"], impedance=50, port_name="Port1"
   ... )

   >>> # 4. create_port_on_component
   >>> # Create coaxial ports on component nets
   >>> source_excitations.create_port_on_component(
   ...     component="U1", net_list=["PCIe_RX0", "PCIe_RX1"], port_type=SourceType.CoaxPort, reference_net="GND"
   ... )

   >>> # 5. add_port_on_rlc_component
   >>> # Replace RLC component with circuit port
   >>> source_excitations.add_port_on_rlc_component("R1")

   >>> # 6. _create_terminal (Internal method - typically not called directly)

   >>> # 7. _create_pin_group_terminal (Internal method)

   >>> # 8. create_coax_port
   >>> # Create coaxial port on padstack
   >>> pin = edb.components["U1"].pins["Pin1"]
   >>> port_name = source_excitations.create_coax_port(pin)

   >>> # 9. create_circuit_port_on_pin
   >>> # Create circuit port between two pins
   >>> pin1 = edb.components["U1"].pins["Pin1"]
   >>> pin2 = edb.components["U1"].pins["Pin2"]
   >>> port_name = source_excitations.create_circuit_port_on_pin(pin1, pin2, 50, "Port1")

   >>> # 10. create_voltage_source_on_pin
   >>> # Create voltage source between pins
   >>> source_name = source_excitations.create_voltage_source_on_pin(pin1, pin2, 3.3, 0, "V1")

   >>> # 11. create_current_source_on_pin
   >>> # Create current source between pins
   >>> source_name = source_excitations.create_current_source_on_pin(pin1, pin2, 0.1, 0, "I1")

   >>> # 12. create_resistor_on_pin
   >>> # Create resistor between pins
   >>> res_name = source_excitations.create_resistor_on_pin(pin1, pin2, 100, "R1")

   >>> # 13. create_circuit_port_on_net
   >>> # Create port between component nets
   >>> port_name = source_excitations.create_circuit_port_on_net(
   >>> "U1", "SignalNet", "U1", "GND", 50, "Port1"
   >>> )

   >>> # 14. create_voltage_source_on_net
   >>> # Create voltage source between nets
   >>> source_name = source_excitations.create_voltage_source_on_net(
   >>> "U1", "VCC", "U1", "GND", 5.0, 0, "VCC_Source"
   >>> )

   >>> # 15. create_current_source_on_net
   >>> # Create current source between nets
   >>> source_name = source_excitations.create_current_source_on_net(
   >>> "U1", "InputNet", "U1", "GND", 0.02, 0, "InputCurrent"
   >>> )

   >>> # 16. create_coax_port_on_component
   >>> # Create coaxial ports on component
   >>> ports = source_excitations.create_coax_port_on_component(
   ...     ["U1", "U2"], ["PCIe_RX0", "PCIe_TX0"], delete_existing_terminal=True
   ... )

   >>> # 17. create_differential_wave_port
   >>> # Create differential wave port
   >>> pos_prim = edb.modeler.primitives[0]
   >>> neg_prim = edb.modeler.primitives[1]
   >>> port_name, diff_port = source_excitations.create_differential_wave_port(
   ...     pos_prim.id, [0, 0], neg_prim.id, [0, 0.2], "DiffPort"
   ... )

   >>> # 18. create_wave_port
   >>> # Create wave port
   >>> port_name, wave_port = source_excitations.create_wave_port(pos_prim.id, [0, 0], "WavePort")

   >>> # 19. create_bundle_wave_port
   >>> # Create bundle wave port
   >>> port_name, bundle_port = source_excitations.create_bundle_wave_port(
   ...     [pos_prim.id, neg_prim.id], [[0, 0], [0, 0.2]], "BundlePort"
   ... )

   >>> # 20. create_dc_terminal
   >>> # Create DC terminal
   >>> source_excitations.create_dc_terminal("U1", "VCC", "VCC_Terminal")

   >>> # 21. create_voltage_probe
   >>> # Create voltage probe
   >>> probe = source_excitations.create_voltage_probe(term1, term2)

   >>> # 22. place_voltage_probe
   >>> # Place voltage probe between points
   >>> source_excitations.place_voltage_probe(
   ...     "Probe1", "SignalNet", [0, 0], "TopLayer", "GND", [0.1, 0.1], "BottomLayer"
   ... )

   >>> # Save and close EDB
   >>> edb.save()
   >>> edb.close()


   .. py:property:: pin_groups
      :type: Dict[str, Any]


      All layout pin groups.

      Returns
      -------
      dict
          Dictionary of pin groups with names as keys and pin group objects as values.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> pin_groups = edbapp.siwave.pin_groups
      >>> for name, group in pin_groups.items():
      ...     print(f"Pin group {name} has {len(group.pins)} pins")



   .. py:property:: excitations
      :type: Dict[str, Union[pyedb.grpc.database.ports.ports.BundleWavePort, pyedb.grpc.database.ports.ports.GapPort, pyedb.grpc.database.ports.ports.CircuitPort, pyedb.grpc.database.ports.ports.CoaxPort, pyedb.grpc.database.ports.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.grpc.database.ports.ports.ports.GapPort`,
                 :class:`pyedb.grpc.database.ports.ports.ports.WavePort`,
                 :class:`pyedb.grpc.database.ports.ports.CircuitPort`,
                 :class:`pyedb.grpc.database.ports.ports.CoaxPort`,
                 :class:`pyedb.grpc.database.ports.ports.BundleWavePort`]]




   .. py:property:: ports
      :type: Dict[str, Union[pyedb.grpc.database.ports.ports.BundleWavePort, pyedb.grpc.database.ports.ports.GapPort, pyedb.grpc.database.ports.ports.CircuitPort, pyedb.grpc.database.ports.ports.CoaxPort, pyedb.grpc.database.ports.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.grpc.database.ports.ports.ports.GapPort`,
                 :class:`pyedb.grpc.database.ports.ports.ports.WavePort`,
                 :class:`pyedb.grpc.database.ports.ports.CircuitPort`,
                 :class:`pyedb.grpc.database.ports.ports.CoaxPort`,
                 :class:`pyedb.grpc.database.ports.ports.BundleWavePort`]]




   .. py:property:: sources
      :type: Dict[str, Any]


      Get all sources.



   .. py:property:: probes
      :type: Dict[str, Any]


      Get all probes.



   .. py:method:: create_source_on_component(sources: Optional[Union[pyedb.grpc.database.utility.sources.Source, List[pyedb.grpc.database.utility.sources.Source]]] = None) -> bool

      Create voltage, current source, or resistor on component.

      Parameters
      ----------
      sources : list[Source]
          List of ``pyedb.grpc.utility.sources.Source`` objects.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> from pyedb.grpc.database.utility.sources import Source, SourceType
      >>> edb = Edb()
      >>> source = Source(source_type=SourceType.Vsource, amplitude="1V", ...)
      >>> edb.excitation_manager.create_source_on_component([source])



   .. py:method:: create_port(terminal: pyedb.grpc.database.terminal.terminal.Terminal, ref_terminal: Optional[pyedb.grpc.database.terminal.terminal.Terminal] = None, is_circuit_port: bool = False, name: Optional[str] = None) -> Any

      Create a port.

      Parameters
      ----------
      terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          class:`pyedb.grpc.database.terminals.PadstackInstanceTerminal`,
          class:`pyedb.grpc.database.terminals.PointTerminal`,
          class:`pyedb.grpc.database.terminals.PinGroupTerminal`,
          Positive terminal of the port.
      ref_terminal : class:`pyedb.grpc.database.terminals.EdgeTerminal`,
          class:`pyedb.grpc.database.terminals.PadstackInstanceTerminal`,
          class:`pyedb.grpc.database.terminals.PointTerminal`,
          class:`pyedb.grpc.database.terminals.PinGroupTerminal`,
          optional
          Negative terminal of the port.
      is_circuit_port : bool, optional
          Whether it is a circuit port. The default is ``False``.
      name: str, optional
          Name of the created port. The default is None, a random name is generated.
      Returns
      -------
      list: [:class:`GapPort <pyedb.grpc.database.ports.ports.GapPort`>,
          :class:`WavePort <pyedb.grpc.database.ports.ports.WavePort>`].

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> term = edb.terminals["MyTerminal"]
      >>> ref_term = edb.terminals["RefTerminal"]
      >>> port = edb.excitation_manager.create_port(term, ref_term, name="Port1")



   .. py:method:: create_port_on_pins(refdes: Union[str, pyedb.grpc.database.components.Component], pins: Union[int, str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance, List[Union[int, str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]]], reference_pins: Union[int, str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance, List[Union[int, str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]]] = None, impedance: Union[str, float] = '50ohm', port_name: Optional[str] = None, pec_boundary: bool = False, pingroup_on_single_pin: bool = False) -> pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal

      Create circuit port between pins and reference ones.

      Parameters
      ----------
      refdes : Component reference designator
          str or Component object.
      pins : pin specifier(s) or instance(s) where the port terminal is to be created. Single pin name or a list of
      several can be provided. If several pins are provided a pin group will be created. Pin specifiers can be the
      global EDB object ID or padstack instance name or pin name on component with refdes ``refdes``. Pin instances
      can be provided as ``EDBPadstackInstance`` objects.
      For instance for the pin called ``Pin1`` located on component with refdes ``U1``: ``U1-Pin1``, ``Pin1`` with
      ``refdes=U1``, the pin's global EDB object ID, or the ``EDBPadstackInstance`` corresponding to the pin can be
      provided.
          Union[int, str, PadstackInstance], List[Union[int, str, PadstackInstance]]
      reference_pins : reference pin specifier(s) or instance(s) for the port reference terminal. Allowed values are
      the same as for the ``pins`` parameter.
          Union[int, str, PadstackInstance], List[Union[int, str, PadstackInstance]]
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



   .. py:method:: create_port_on_component(component: Union[str, pyedb.grpc.database.components.Component], net_list: Union[str, List[str]], port_type: str = 'coax_port', do_pingroup: Optional[bool] = True, reference_net: Optional[str] = None, port_name: Optional[List[str]] = None, solder_balls_height: Union[float, str] = None, solder_balls_size: Union[float, str] = None, solder_balls_mid_size: Union[float, str] = None, extend_reference_pins_outside_component: Optional[bool] = False) -> List[str]

      Create ports on a component.

      Parameters
      ----------
      component : str or Component
          EDB component or str component name.
      net_list : str or list of string.
          List of nets where ports must be created on the component.
          If the net is not part of the component, this parameter is skipped.
      port_type : str, optional
          Type of port to create. ``coax_port`` generates solder balls.
          ``circuit_port`` generates circuit ports on pins belonging to the net list.
      do_pingroup : bool
          True activate pingroup during port creation (only used with combination of CircPort),
          False will take the closest reference pin and generate one port per signal pin.
      reference_net : string or list of string.
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
      >>> edbapp.excitations.create_port_on_component(cmp="U2A5", net_list=net_list,
      >>> port_type=SourceType.CoaxPort, do_pingroup=False, refnet="GND")




   .. py:method:: add_port_on_rlc_component(component: Optional[Union[str, pyedb.grpc.database.components.Component]] = None, circuit_ports: bool = True, pec_boundary: bool = False) -> bool

      Deactivate RLC component and replace it with a circuit port.
      The circuit port supports only two-pin components.

      Parameters
      ----------
      component : str
          Reference designator of the RLC component.

      circuit_ports : bool
          ``True`` will replace RLC component by circuit ports, ``False`` gap ports compatible with HFSS 3D modeler
          export.

      pec_boundary : bool, optional
          Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
          a perfect short is created between the pin and impedance is ignored. This
          parameter is only supported on a port created between two pins, such as
          when there is no pin group.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.add_port_on_rlc_component("R1")



   .. py:method:: add_rlc_boundary(component: Optional[Union[str, pyedb.grpc.database.components.Component]] = None, circuit_type: bool = True) -> bool

      Add RLC gap boundary on component and replace it with a circuit port.
      The circuit port supports only 2-pin components.

      Parameters
      ----------
      component : str
          Reference designator of the RLC component.
      circuit_type : bool
          When ``True`` circuit type are defined, if ``False`` gap type will be used instead (compatible with HFSS 3D
          modeler). Default value is ``True``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: create_coax_port(padstackinstance: Union[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance, int], use_dot_separator: bool = True, name: Optional[str] = None, create_on_top: bool = True) -> Optional[str]

      Create HFSS 3Dlayout coaxial lumped port on a pastack
      Requires to have solder ball defined before calling this method.

      Parameters
      ----------
      padstackinstance : `Edb.Cell.Primitive.PadstackInstance` or int
          Padstack instance object.
      use_dot_separator : bool, optional
          Whether to use ``.`` as the separator for the naming convention, which
          is ``[component][net][pin]``. The default is ``True``. If ``False``, ``_`` is
          used as the separator instead.
      name : str
          Port name for overwriting the default port-naming convention,
          which is ``[component][net][pin]``. The port name must be unique.
          If a port with the specified name already exists, the
          default naming convention is used so that port creation does
          not fail.

      Returns
      -------
      str
          Terminal name.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> pin = edb.padstacks.instances[0]
      >>> edb.excitation_manager.create_coax_port(pin, name="CoaxPort1")



   .. py:method:: create_circuit_port_on_pin(pos_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], neg_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], impedance: Union[int, float] = 50, port_name: Optional[str] = None) -> Optional[str]

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



   .. py:method:: create_voltage_source_on_pin(pos_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], neg_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], voltage_value: Union[int, float] = 0, phase_value: Union[int, float] = 0, source_name: Optional[str] = None) -> Optional[str]

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
      >>> edb = Edb()
      >>> pin1 = edb.components["U1"].pins["VCC"]
      >>> pin2 = edb.components["U1"].pins["GND"]
      >>> edb.excitation_manager.create_voltage_source_on_pin(pin1, pin2, 3.3, name="VSource1")



   .. py:method:: create_current_source_on_pin(pos_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], neg_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], current_value: Union[int, float] = 0, phase_value: Union[int, float] = 0, source_name: Optional[str] = None) -> Optional[str]

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
      >>> edb = Edb()
      >>> pin1 = edb.components["U1"].pins["IN"]
      >>> pin2 = edb.components["U1"].pins["GND"]
      >>> edb.excitation_manager.create_current_source_on_pin(pin1, pin2, 0.1, name="ISource1")



   .. py:method:: create_resistor_on_pin(pos_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], neg_pin: Union[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], rvalue: Union[int, float] = 1, resistor_name: Optional[str] = '') -> Optional[str]

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
      >>> edb = Edb()
      >>> pin1 = edb.components["U1"].pins["R1_p"]
      >>> pin2 = edb.components["U1"].pins["R1_n"]
      >>> edb.excitation_manager.create_resistor_on_pin(pin1, pin2, 50, "R1")



   .. py:method:: create_circuit_port_on_net(positive_component_name: str, positive_net_name: str, negative_component_name: str = None, negative_net_name: Optional[str] = None, impedance_value: Union[int, float] = 50, port_name: Optional[str] = None) -> Optional[str]

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
      >>> edb = Edb()
      >>> edb.excitation_manager.create_circuit_port_on_net("U1", "VCC", "U1", "GND", 50, "PowerPort")



   .. py:method:: create_voltage_source_on_net(positive_component_name: str, positive_net_name: str, negative_component_name: Optional[str] = None, negative_net_name: Optional[str] = None, voltage_value: Union[int, float] = 0, phase_value: Union[int, float] = 0, source_name: Optional[str] = None) -> Optional[str]

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
      >>> edb = Edb()
      >>> edb.excitation_manager.create_voltage_source_on_net("U1", "VCC", "U1", "GND", 3.3, name="VCC_Source")



   .. py:method:: create_current_source_on_net(positive_component_name: str, positive_net_name: str, negative_component_name: Optional[str] = None, negative_net_name: Optional[str] = None, current_value: Union[int, float] = 0, phase_value: Union[int, float] = 0, source_name: Optional[str] = None) -> Optional[str]

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
      >>> edb = Edb()
      >>> edb.excitation_manager.create_current_source_on_net("U1", "INPUT", "U1", "GND", 0.1, name="InputCurrent")
      "InputCurrent"



   .. py:method:: create_coax_port_on_component(ref_des_list: Union[str, List[str]], net_list: Union[str, List[str]], delete_existing_terminal: bool = False) -> List[str]

      Create a coaxial port on a component or component list on a net or net list.
         The name of the new coaxial port is automatically assigned.

      Parameters
      ----------
      ref_des_list : list, str
          List of one or more reference designators.

      net_list : list, str
          List of one or more nets.

      delete_existing_terminal : bool
          Delete existing terminal with same name if exists.
          Port naming convention is `ref_des`_`pin.net.name`_`pin.name`

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.create_coax_port_on_component(["U1"], ["RF1", "RF2"])



   .. py:method:: check_before_terminal_assignement(connectable: Any, delete_existing_terminal: bool = False) -> bool


   .. py:method:: create_differential_wave_port(positive_primitive_id: Union[int, pyedb.grpc.database.primitive.primitive.Primitive], positive_points_on_edge: List[float], negative_primitive_id: Union[int, pyedb.grpc.database.primitive.primitive.Primitive], negative_points_on_edge: List[float], port_name: Optional[str] = None, horizontal_extent_factor: Union[int, float] = 5, vertical_extent_factor: Union[int, float] = 3, pec_launch_width: str = '0.01mm') -> pyedb.grpc.database.terminal.bundle_terminal.BundleTerminal

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
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> port_name, port = edb.excitation_manager.create_differential_wave_port(0, [0, 0], 1, [0, 0.2])



   .. py:method:: create_wave_port(prim_id: Union[int, pyedb.grpc.database.primitive.primitive.Primitive], point_on_edge: List[float], port_name: Optional[str] = None, impedance: Union[int, float] = 50, horizontal_extent_factor: Union[int, float] = 5, vertical_extent_factor: Union[int, float] = 3, pec_launch_width: str = '0.01mm') -> Tuple[str, pyedb.grpc.database.ports.ports.WavePort]

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
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> port_name, port = edb.excitation_manager.create_wave_port(0, [0, 0])



   .. py:method:: create_edge_port_vertical(prim_id: int, point_on_edge: List[float], port_name: Optional[str] = None, impedance: Union[int, float] = 50, reference_layer: Optional[str] = None, hfss_type: str = 'Gap', horizontal_extent_factor: Union[int, float] = 5, vertical_extent_factor: Union[int, float] = 3, pec_launch_width: str = '0.01mm') -> str

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> term = edb.excitation_manager.create_edge_port_vertical(0, [0, 0], reference_layer="TopLayer")



   .. py:method:: create_edge_port_horizontal(prim_id: Union[int, pyedb.grpc.database.primitive.primitive.Primitive], point_on_edge: List[float], ref_prim_id: Optional[Union[int, pyedb.grpc.database.primitive.primitive.Primitive]] = None, point_on_ref_edge: Optional[List[float]] = None, port_name: Optional[str] = None, impedance: Union[int, float] = 50, layer_alignment: str = 'Upper') -> Optional[pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal]

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.create_edge_port_horizontal(0, [0, 0], 1, [0, 0.1], "EdgePort")



   .. py:method:: create_lumped_port_on_net(nets: Optional[Union[str, List[str]]] = None, reference_layer: Optional[Union[str, pyedb.grpc.database.layers.stackup_layer.StackupLayer]] = None, return_points_only: bool = False, digit_resolution: int = 6, at_bounding_box: bool = True) -> bool

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> points = edb.excitation_manager.create_lumped_port_on_net(["Net1"], return_points_only=True)



   .. py:method:: create_vertical_circuit_port_on_clipped_traces(nets: Optional[Union[str, List[str], pyedb.grpc.database.net.net.Net, List[pyedb.grpc.database.net.net.Net]]] = None, reference_net: Optional[Union[str, pyedb.grpc.database.net.net.Net]] = None, user_defined_extent: Optional[Union[List[float], ansys.edb.core.geometry.polygon_data.PolygonData]] = None) -> Union[List[List[str]], bool]

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> terminals = edb.excitation_manager.create_vertical_circuit_port_on_clipped_traces(["Net1"], "GND")



   .. py:method:: create_bundle_wave_port(primitives_id: List[Union[int, pyedb.grpc.database.primitive.primitive.Primitive]], points_on_edge: List[List[float]], port_name: Optional[str] = None, horizontal_extent_factor: Union[int, float] = 5, vertical_extent_factor: Union[int, float] = 3, pec_launch_width: str = '0.01mm') -> pyedb.grpc.database.ports.ports.BundleWavePort

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
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> port_name, port = edb.excitation_manager.create_bundle_wave_port([0, 1], [[0, 0], [0, 0.2]])



   .. py:method:: create_hfss_ports_on_padstack(pinpos: pyedb.grpc.database.primitive.padstack_instance.PadstackInstance, portname: Optional[str] = None) -> bool

      Create an HFSS port on a padstack.

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> pin = edb.padstacks.instances[0]
      >>> edb.excitation_manager.create_hfss_ports_on_padstack(pin, "Port1")



   .. py:method:: get_ports_number() -> int

      Return the total number of excitation ports in a layout.

      Parameters
      ----------
      None

      Returns
      -------
      int
         Number of ports.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> num_ports = edb.excitation_manager.get_ports_number()



   .. py:method:: get_point_terminal(name: str, net_name: str, location: List[float], layer: str) -> pyedb.grpc.database.terminal.point_terminal.PointTerminal

      Place terminal between two points.

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
      :class:`PointTerminal <pyedb.grpc.database.terminal.point_terminal.PointTerminal>`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> term = edb.excitation_manager.get_point_terminal("Term1", "Net1", [0, 0], "TopLayer")



   .. py:method:: create_rlc_boundary_on_pins(positive_pin: Optional[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance] = None, negative_pin: Optional[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance] = None, rvalue: float = 0.0, lvalue: float = 0.0, cvalue: float = 0.0) -> Union[pyedb.grpc.database.terminal.terminal.Terminal, bool]

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> pin1 = edb.components["U1"].pins["Pin1"]
      >>> pin2 = edb.components["U1"].pins["Pin2"]
      >>> term = edb.excitation_manager.create_rlc_boundary_on_pins(pin1, pin2, rvalue=50)



   .. py:method:: get_edge_from_port(port)


   .. py:method:: create_edge_port(location, primitive_name, name, impedance=50, is_wave_port=True, horizontal_extent_factor=1, vertical_extent_factor=1, pec_launch_width=0.0001)


   .. py:method:: create_edge_port_on_polygon(polygon: Optional[pyedb.grpc.database.primitive.primitive.Primitive] = None, reference_polygon: Optional[pyedb.grpc.database.primitive.primitive.Primitive] = None, terminal_point: Optional[List[float]] = None, reference_point: Optional[List[float]] = None, reference_layer: Optional[Union[str, pyedb.grpc.database.layers.stackup_layer.StackupLayer]] = None, port_name: Optional[str] = None, port_impedance: Union[int, float] = 50.0, force_circuit_port: bool = False) -> Optional[str]

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
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> poly = edb.modeler.primitives[0]
      >>> ref_poly = edb.modeler.primitives[1]
      >>> edb.excitation_manager.create_edge_port_on_polygon(poly, ref_poly, [0, 0], [0.1, 0])



   .. py:method:: create_port_between_pin_and_layer(component_name: Optional[str] = None, pins_name: Optional[Union[str, List[str]]] = None, layer_name: Optional[str] = None, reference_net: Optional[str] = None, impedance: Union[int, float] = 50.0) -> bool

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> terms = edb.excitation_manager.create_port_between_pin_and_layer("U1", "Pin1", "GND", "GND")



   .. py:method:: create_current_source(terminal: Union[pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal, pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal], ref_terminal: Union[pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal, pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal], magnitude: Union[int, float] = 1, phase: Union[int, float] = 0) -> Union[pyedb.grpc.database.terminal.terminal.Terminal, bool]

      Create a current source.

      Parameters
      ----------
      terminal : :class:`EdgeTerminal <pyedb.grpc.database.terminals.EdgeTerminal>`or
          :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminals.PadstackInstanceTerminal>` or
          :class:`PointTerminal <pyedb.grpc.database.terminals.PointTerminal>` or
          :class:`PinGroupTerminal <pyedb.grpc.database.terminals.PinGroupTerminal>`.
              Positive terminal of the source.
      ref_terminal : :class:`EdgeTerminal <pyedb.grpc.database.terminals.EdgeTerminal>` or
          :class:`pyedb.grpc.database.terminals.PadstackInstanceTerminal` or
          :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminals.PointTerminal>` or
          :class:`PinGroupTerminal <pyedb.grpc.database.terminals.PinGroupTerminal>`.
              Negative terminal of the source.
      magnitude : int, float, optional
          Magnitude of the source.
      phase : int, float, optional
          Phase of the source

      Returns
      -------
      :class:`ExcitationSources <legacy.database.edb_data.ports.ExcitationSources>`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.create_current_source_on_pin_group("PG1", "PG2", 0.1, name="ISource1")



   .. py:method:: create_current_source_on_pin_group(pos_pin_group_name: str, neg_pin_group_name: str, magnitude: Union[int, float] = 1, phase: Union[int, float] = 0, name: Optional[str] = None) -> bool

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




   .. py:method:: create_voltage_source(terminal: Union[pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal, pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], ref_terminal: Union[pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal, pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], magnitude: Union[int, float] = 1, phase: Union[int, float] = 0) -> Union[pyedb.grpc.database.terminal.terminal.Terminal, bool]

      Create a voltage source.

      Parameters
      ----------
      name : str, optional
          Voltage source name
      terminal : :class:`EdgeTerminal <pyedb.grpc.database.terminals.EdgeTerminal>`,
          :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminals.PadstackInstanceTerminal>`,
          :class:`PointTerminal <pyedb.grpc.database.terminals.PointTerminal>`,
          :class:`PinGroupTerminal <pyedb.grpc.database.terminals.PinGroupTerminal>`,
          :class:`PadstackInstance <pyedb.grpc.database.padstacks.PadstackInstance>`,
          Positive terminal of the source.
      ref_terminal : :class:`EdgeTerminal <pyedb.grpc.database.terminals.EdgeTerminal>`,
          :class:`pyedb.grpc.database.terminals.PadstackInstanceTerminal`,
          :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminals.PointTerminal>`,
          :class:`PinGroupTerminal <pyedb.grpc.database.terminals.PinGroupTerminal>`,
          :class:`PadstackInstance <pyedb.grpc.database.padstacks.PadstackInstance>`,
          Negative terminal of the source.
      magnitude : int, float, optional
          Magnitude of the source.
      phase : int, float, optional
          Phase of the source

      Returns
      -------
      class:`ExcitationSources <legacy.database.edb_data.ports.ExcitationSources>`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.create_voltage_source("pin1", "pin2", 3.3, name="VSource1")



   .. py:method:: create_voltage_source_on_pin_group(pos_pin_group_name: str, neg_pin_group_name: str, magnitude: Union[int, float] = 1, phase: Union[int, float] = 0, name: Optional[str] = None, impedance: Union[int, float] = 0.001) -> bool

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.create_voltage_probe_on_pin_group("Probe1", "PG1", "PG2")



   .. py:method:: create_voltage_probe(terminal: pyedb.grpc.database.terminal.terminal.Terminal, ref_terminal: pyedb.grpc.database.terminal.terminal.Terminal) -> Union[pyedb.grpc.database.terminal.terminal.Terminal, bool]

      Create a voltage probe.

      Parameters
      ----------
      terminal : :class:`EdgeTerminal <pyedb.grpc.database.terminals.EdgeTerminal>`,
          :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminals.PadstackInstanceTerminal>`,
          :class:`PointTerminal <pyedb.grpc.database.terminals.PointTerminal>`,
          :class:`PinGroupTerminal <pyedb.grpc.database.terminals.PinGroupTerminal>`,
          :class:`PadstackInstance <pyedb.grpc.database.padstacks.PadstackInstance>`,
          Positive terminal of the port.
      ref_terminal : :class:`EdgeTerminal <pyedb.grpc.database.terminals.EdgeTerminal>`,
          :class:`pyedb.grpc.database.terminals.PadstackInstanceTerminal`,
          :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminals.PointTerminal>`,
          :class:`PinGroupTerminal <pyedb.grpc.database.terminals.PinGroupTerminal>`,
          :class:`PadstackInstance <pyedb.grpc.database.padstacks.PadstackInstance>`,
          Negative terminal of the probe.

      Returns
      -------
      :class:`Terminal <pyedb.dotnet.database.edb_data.terminals.Terminal>`



   .. py:method:: create_voltage_probe_on_pin_group(probe_name: str, pos_pin_group_name: str, neg_pin_group_name: str, impedance: Union[int, float] = 1000000) -> bool

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




   .. py:method:: create_dc_terminal(component_name: str, net_name: str, source_name: Optional[str] = None) -> Optional[str]

      Create a dc terminal.

      Parameters
      ----------
      component_name : str
          Name of the positive component.
      net_name : str
          Name of the positive net.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          The name of the source.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.create_dc_terminal("U1", "VCC", "DC_VCC")



   .. py:method:: create_circuit_port_on_pin_group(pos_pin_group_name: str, neg_pin_group_name: str, impedance: Union[int, float] = 50, name: Optional[str] = None) -> bool

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.excitation_manager.create_circuit_port_on_pin_group("PG1", "PG2", 50, "Port1")



   .. py:method:: place_voltage_probe(name: str, positive_net_name: str, positive_location: List[float], positive_layer: str, negative_net_name: str, negative_location: List[float], negative_layer: str) -> pyedb.grpc.database.terminal.terminal.Terminal

      Place a voltage probe between two points.

      Parameters
      ----------
      name : str,
          Name of the probe.
      positive_net_name : str
          Name of the positive net.
      positive_location : list
          Location of the positive terminal.
      positive_layer : str,
          Layer of the positive terminal.
      negative_net_name : str,
          Name of the negative net.
      negative_location : list
          Location of the negative terminal.
      negative_layer : str
          Layer of the negative terminal.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> probe = edb.excitation_manager.place_voltage_probe(
      ...     "Probe1", "Net1", [0, 0], "TopLayer", "GND", [0.1, 0], "TopLayer"
      ... )



   .. py:method:: create_padstack_instance_terminal(name='', padstack_instance_id=None, padstack_instance_name=None)


   .. py:method:: create_point_terminal(x, y, layer, net, name='')


   .. py:method:: create_edge_terminal(primitive_name, x, y, name='')


   .. py:method:: create_bundle_terminal(terminals, name='')


   .. py:method:: create_pin_group_terminal(pin_group)


   .. py:method:: create_terminal_from_pin_group(pin_group, name='')


