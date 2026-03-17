src.pyedb.grpc.database.components
==================================

.. py:module:: src.pyedb.grpc.database.components

.. autoapi-nested-parse::

   This module contains the `Components` class.



Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.components.edbapp


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.components.Components


Functions
---------

.. autoapisummary::

   src.pyedb.grpc.database.components.resistor_value_parser


Module Contents
---------------

.. py:data:: edbapp
   :type:  pyedb.grpc.edb.Edb
   :value: None


.. py:function:: resistor_value_parser(r_value) -> float

   Convert a resistor value to float.

   Parameters
   ----------
   r_value : float or str
       Resistor value to convert.

   Returns
   -------
   float
       Converted resistor value.


.. py:class:: Components(p_edb: Any)

   Bases: :py:obj:`object`


   Manages EDB components and related methods accessible from `Edb.components`.

   Parameters
   ----------
   p_edb : :class:`pyedb.grpc.edb.Edb`
       EDB object.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myaedbfolder")
   >>> edb.components


   .. py:property:: instances
      :type: Dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of all component instances in the layout.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of component instances keyed by name.

      Examples
      --------
      >>> edbapp.components.instances



   .. py:property:: definitions
      :type: Dict[str, pyedb.grpc.database.definition.component_def.ComponentDef]


      Dictionary of all component definitions.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.definition.component_def.ComponentDef`]
          Dictionary of component definitions keyed by name.

      Examples
      --------
      >>> edbapp.components.definitions



   .. py:property:: nport_comp_definition
      :type: Dict[str, pyedb.grpc.database.definition.component_def.ComponentDef]


      Dictionary of N-port component definitions.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of N-port component definitions keyed by name.



   .. py:method:: import_definition(file_path) -> bool

      Import component definitions from a JSON file.

      Parameters
      ----------
      file_path : str
          Path to the JSON file.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.import_definition("definitions.json")



   .. py:method:: export_definition(file_path) -> bool

      Export component definitions to a JSON file.

      Parameters
      ----------
      file_path : str
          Path to the output JSON file.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.export_definition("exported_definitions.json")



   .. py:method:: refresh_components() -> bool

      Refresh the component dictionary.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.refresh_components()



   .. py:property:: resistors
      :type: Dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of resistor components.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of resistor components keyed by name.

      Examples
      --------
      >>> edbapp.components.resistors



   .. py:property:: capacitors
      :type: Dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of capacitor components.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of capacitor components keyed by name.

      Examples
      --------
      >>> edbapp.components.capacitors



   .. py:property:: inductors
      :type: Dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of inductor components.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of inductor components keyed by name.

      Examples
      --------
      >>> edbapp.components.inductors



   .. py:property:: ICs
      :type: Dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of integrated circuit components.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of IC components keyed by name.

      Examples
      --------
      >>> edbapp.components.ICs



   .. py:property:: IOs
      :type: Dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of I/O components.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of I/O components keyed by name.

      Examples
      --------
      >>> edbapp.components.IOs



   .. py:property:: Others
      :type: Dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of other components.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
          Dictionary of other components keyed by name.

      Examples
      --------
      >>> edbapp.components.Others



   .. py:property:: components_by_partname
      :type: Dict[str, List[pyedb.grpc.database.hierarchy.component.Component]]


      Dictionary of components grouped by part name.

      Returns
      -------
      dict[str, list[:class:`pyedb.grpc.database.hierarchy.component.Component`]]
          Dictionary of components lists keyed by part name.

      Examples
      --------
      >>> edbapp.components.components_by_partname



   .. py:method:: get_component_by_name(name) -> pyedb.grpc.database.hierarchy.component.Component

      Retrieve a component by name.

      Parameters
      ----------
      name : str
          Name of the component.

      Returns
      -------
      :class:`pyedb.grpc.database.hierarchy.component.Component`
          Component instance.

      Examples
      --------
      >>> comp = edbapp.components.get_component_by_name("R1")



   .. py:method:: get_pin_from_component(component: Union[str, pyedb.grpc.database.hierarchy.component.Component], net_name: Optional[Union[str, List[str]]] = None, pin_name: Optional[str] = None) -> List[Any]

      Get pins from a component with optional filtering.

      Parameters
      ----------
      component : str or :class:`pyedb.grpc.database.hierarchy.component.Component`
          Component name or instance.
      net_name : str or list[str], optional
          Net name(s) to filter by.
      pin_name : str, optional
          Pin name to filter by.

      Returns
      -------
      list[:class:`pyedb.grpc.database.padstacks.PadstackInstance`]
          List of pin instances.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_aedb")
      >>> edb.components.get_pin_from_component("R1", net_name="GND")



   .. py:method:: get_components_from_nets(netlist=None) -> list[str]

      Get components connected to specified nets.

      Parameters
      ----------
      netlist : str or list[str], optional
          Net name(s) to filter by.

      Returns
      -------
      list[str]
          List of component names.

      Examples
      --------
      >>> comps = edbapp.components.get_components_from_nets(["GND", "VCC"])



   .. py:method:: get_component_placement_vector(mounted_component: pyedb.grpc.database.hierarchy.component.Component, hosting_component: pyedb.grpc.database.hierarchy.component.Component, mounted_component_pin1: str, mounted_component_pin2: str, hosting_component_pin1: str, hosting_component_pin2: str, flipped: bool = False) -> Tuple[bool, List[float], float, float]

      Get placement vector between two components.

      Parameters
      ----------
      mounted_component : :class:`pyedb.grpc.database.hierarchy.component.Component`
          Mounted component.
      hosting_component : :class:`pyedb.grpc.database.hierarchy.component.Component`
          Hosting component.
      mounted_component_pin1 : str
          Pin name on mounted component.
      mounted_component_pin2 : str
          Pin name on mounted component.
      hosting_component_pin1 : str
          Pin name on hosting component.
      hosting_component_pin2 : str
          Pin name on hosting component.
      flipped : bool, optional
          Whether the component is flipped.

      Returns
      -------
      tuple
          (success, vector, rotation, solder_ball_height)

      Examples
      --------
      >>> success, vec, rot, height = edbapp.components.get_component_placement_vector(...)



   .. py:method:: get_solder_ball_height(cmp: Union[str, pyedb.grpc.database.hierarchy.component.Component]) -> float

      Get solder ball height of a component.

      Parameters
      ----------
      cmp : str or :class:`pyedb.grpc.database.hierarchy.component.Component`
          Component name or instance.

      Returns
      -------
      float
          Solder ball height in meters.

      Examples
      --------
      >>> height = edbapp.components.get_solder_ball_height("U1")



   .. py:method:: get_vendor_libraries() -> pyedb.component_libraries.ansys_components.ComponentLib

      Get vendor component libraries.

      Returns
      -------
      :class:`pyedb.component_libraries.ansys_components.ComponentLib`
          Component library object.

      Examples
      --------
      >>> lib = edbapp.components.get_vendor_libraries()



   .. py:method:: create(pins: List[Any], component_name: Optional[str] = None, placement_layer: Optional[str] = None, component_part_name: Optional[str] = None, is_rlc: bool = False, r_value: Optional[float] = None, c_value: Optional[float] = None, l_value: Optional[float] = None, is_parallel: bool = False) -> Union[pyedb.grpc.database.hierarchy.component.Component, bool]

      Create a new component.

      Parameters
      ----------
      pins : list[:class:`pyedb.grpc.database.padstacks.PadstackInstance`]
          List of pins.
      component_name : str, optional
          Component name.
      placement_layer : str, optional
          Placement layer name.
      component_part_name : str, optional
          Part name.
      is_rlc : bool, optional
          Whether the component is RLC.
      r_value : float, optional
          Resistance value.
      c_value : float, optional
          Capacitance value.
      l_value : float, optional
          Inductance value.
      is_parallel : bool, optional
          Whether RLC is parallel.

      Returns
      -------
      :class:`pyedb.grpc.database.hierarchy.component.Component` or bool
          New component instance if successful, False otherwise.

      Examples
      --------
      >>> new_comp = edbapp.components.create(pins, "R1")



   .. py:method:: set_component_model(componentname: str, model_type: str = 'Spice', modelpath: Optional[str] = None, modelname: Optional[str] = None) -> bool

      Set component model.

      Parameters
      ----------
      componentname : str
          Component name.
      model_type : str, optional
          Model type ("Spice" or "Touchstone").
      modelpath : str, optional
          Model file path.
      modelname : str, optional
          Model name.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.set_component_model("U1", "Spice", "path/to/model.sp")



   .. py:method:: create_pingroup_from_pins(pins: List[Any], group_name: Optional[str] = None) -> Union[pyedb.grpc.database.hierarchy.pingroup.PinGroup, bool]

      Create pin group from pins.

      Parameters
      ----------
      pins : list[:class:`pyedb.grpc.database.padstacks.PadstackInstance`]
          List of pins.
      group_name : str, optional
          Group name.

      Returns
      -------
      :class:`pyedb.grpc.database.hierarchy.pingroup.PinGroup` or bool
          Pin group instance if successful, False otherwise.

      Examples
      --------
      >>> pingroup = edbapp.components.create_pingroup_from_pins(pins, "GND_pins")



   .. py:method:: delete_single_pin_rlc(deactivate_only: bool = False) -> List[str]

      Delete or deactivate single-pin RLC components.

      Parameters
      ----------
      deactivate_only : bool, optional
          Whether to only deactivate instead of deleting.

      Returns
      -------
      list[str]
          List of affected components.

      Examples
      --------
      >>> deleted = edbapp.components.delete_single_pin_rlc()



   .. py:method:: delete(component_name: str) -> bool

      Delete a component.

      Parameters
      ----------
      component_name : str
          Component name.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.delete("R1")



   .. py:method:: disable_rlc_component(component_name: str) -> bool

      Disable RLC component.

      Parameters
      ----------
      component_name : str
          Component name.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.disable_rlc_component("R1")



   .. py:method:: set_solder_ball(component: Union[str, pyedb.grpc.database.hierarchy.component.Component] = '', sball_diam: Optional[float] = None, sball_height: Optional[float] = None, shape: str = 'Cylinder', sball_mid_diam: Optional[float] = None, chip_orientation: str = 'chip_down', auto_reference_size: bool = True, reference_size_x: float = 0, reference_size_y: float = 0, reference_height: float = 0) -> bool

      Set solder ball properties for a component.

      Parameters
      ----------
      component : str or :class:`pyedb.grpc.database.hierarchy.component.Component`, optional
          Component name or instance.
      sball_diam : float, optional
          Solder ball diameter.
      sball_height : float, optional
          Solder ball height.
      shape : str, optional
          Solder ball shape ("Cylinder" or "Spheroid").
      sball_mid_diam : float, optional
          Solder ball mid diameter.
      chip_orientation : str, optional
          Chip orientation ("chip_down" or "chip_up").
      auto_reference_size : bool, optional
          Use auto reference size.
      reference_size_x : float, optional
          Reference size X.
      reference_size_y : float, optional
          Reference size Y.
      reference_height : float, optional
          Reference height.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.set_solder_ball("U1", sball_diam=0.5e-3)



   .. py:method:: set_component_rlc(componentname: str, res_value: Optional[float] = None, ind_value: Optional[float] = None, cap_value: Optional[float] = None, isparallel: bool = False) -> bool

      Set RLC values for a component.

      Parameters
      ----------
      componentname : str
          Component name.
      res_value : float, optional
          Resistance value.
      ind_value : float, optional
          Inductance value.
      cap_value : float, optional
          Capacitance value.
      isparallel : bool, optional
          Whether RLC is parallel.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.set_component_rlc("R1", res_value=50)



   .. py:method:: update_rlc_from_bom(bom_file: str, delimiter: str = ';', valuefield: str = 'Func des', comptype: str = 'Prod name', refdes: str = 'Pos / Place') -> bool

      Update RLC values from BOM file.

      Parameters
      ----------
      bom_file : str
          BOM file path.
      delimiter : str, optional
          Delimiter character.
      valuefield : str, optional
          Value field name.
      comptype : str, optional
          Component type field name.
      refdes : str, optional
          Reference designator field name.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.update_rlc_from_bom("bom.csv")



   .. py:method:: import_bom(bom_file: str, delimiter: str = ',', refdes_col: int = 0, part_name_col: int = 1, comp_type_col: int = 2, value_col: int = 3) -> bool

      Import BOM file.

      Parameters
      ----------
      bom_file : str
          BOM file path.
      delimiter : str, optional
          Delimiter character.
      refdes_col : int, optional
          Reference designator column index.
      part_name_col : int, optional
          Part name column index.
      comp_type_col : int, optional
          Component type column index.
      value_col : int, optional
          Value column index.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.import_bom("bom.csv")



   .. py:method:: export_bom(bom_file: str, delimiter: str = ',') -> bool

      Export BOM file.

      Parameters
      ----------
      bom_file : str
          Output file path.
      delimiter : str, optional
          Delimiter character.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.export_bom("exported_bom.csv")



   .. py:method:: find_by_reference_designator(reference_designator: str) -> pyedb.grpc.database.hierarchy.component.Component

      Find component by reference designator.

      Parameters
      ----------
      reference_designator : str
          Reference designator.

      Returns
      -------
      :class:`pyedb.grpc.database.hierarchy.component.Component`
          Component instance.

      Examples
      --------
      >>> comp = edbapp.components.find_by_reference_designator("R1")



   .. py:method:: get_aedt_pin_name(pin: Any) -> str

      Get AEDT pin name.

      Parameters
      ----------
      pin : :class:`pyedb.grpc.database.padstacks.PadstackInstance`
          Pin instance.

      Returns
      -------
      str
          AEDT pin name.

      Examples
      --------
      >>> name = edbapp.components.get_aedt_pin_name(pin)



   .. py:method:: get_pins(reference_designator: str, net_name: Optional[str] = None, pin_name: Optional[str] = None) -> Dict[str, Any]

      Get pins of a component.

      Parameters
      ----------
      reference_designator : str
          Reference designator.
      net_name : str, optional
          Net name filter.
      pin_name : str, optional
          Pin name filter.

      Returns
      -------
      dict
          Dictionary of pins.

      Examples
      --------
      >>> pins = edbapp.components.get_pins("U1", net_name="GND")



   .. py:method:: get_pin_position(pin: Any) -> List[float]

      Get pin position.

      Parameters
      ----------
      pin : :class:`pyedb.grpc.database.padstacks.PadstackInstance`
          Pin instance.

      Returns
      -------
      list[float]
          [x, y] position in meters.

      Examples
      --------
      >>> pos = edbapp.components.get_pin_position(pin)



   .. py:method:: get_pins_name_from_net(net_name: str, pin_list: Optional[List[Any]] = None) -> List[str]

      Get pin names from net.

      Parameters
      ----------
      net_name : str
          Net name.
      pin_list : list, optional
          List of pins to search.

      Returns
      -------
      list[str]
          List of pin names.

      Examples
      --------
      >>> pins = edbapp.components.get_pins_name_from_net("GND")



   .. py:method:: get_nets_from_pin_list(pins: List[Any]) -> List[str]

      Get nets from pin list.

      Parameters
      ----------
      pins : list
          List of pins.

      Returns
      -------
      list[str]
          List of net names.

      Examples
      --------
      >>> nets = edbapp.components.get_nets_from_pin_list(pins)



   .. py:method:: get_component_net_connection_info(refdes: str) -> Dict[str, List[str]]

      Get net connection info for a component.

      Parameters
      ----------
      refdes : str
          Reference designator.

      Returns
      -------
      dict
          Dictionary with refdes, pin_name, and net_name.

      Examples
      --------
      >>> info = edbapp.components.get_component_net_connection_info("U1")



   .. py:method:: get_rats() -> List[Dict[str, List[str]]]

      Get RATS (Reference Designator, Pin, Net) information.

      Returns
      -------
      list[dict]
          List of dictionaries with refdes, pin_name, and net_name.

      Examples
      --------
      >>> rats = edbapp.components.get_rats()



   .. py:method:: get_through_resistor_list(threshold: float = 1) -> List[str]

      Get through resistors below threshold.

      Parameters
      ----------
      threshold : float, optional
          Resistance threshold.

      Returns
      -------
      list[str]
          List of component names.

      Examples
      --------
      >>> resistors = edbapp.components.get_through_resistor_list(1)



   .. py:method:: short_component_pins(component_name: str, pins_to_short: Optional[List[str]] = None, width: float = 0.001) -> bool

      Short component pins with traces.

      Parameters
      ----------
      component_name : str
          Component name.
      pins_to_short : list[str], optional
          List of pin names to short.
      width : float, optional
          Trace width.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> edbapp.components.short_component_pins("J4A2", ["G4", "9", "3"])



   .. py:method:: create_pin_group(reference_designator: str, pin_numbers: Union[str, List[str]], group_name: Optional[str] = None) -> Union[Tuple[str, pyedb.grpc.database.hierarchy.pingroup.PinGroup], bool]

      Create pin group on a component.

      Parameters
      ----------
      reference_designator : str
          Reference designator.
      pin_numbers : list[str]
          List of pin names.
      group_name : str, optional
          Group name.

      Returns
      -------
      tuple[str, :class:`pyedb.grpc.database.hierarchy.pingroup.PinGroup`] or bool
          (group_name, PinGroup) if successful, False otherwise.

      Examples
      --------
      >>> name, group = edbapp.components.create_pin_group("U1", ["1", "2"])



   .. py:method:: create_pin_group_on_net(reference_designator: str, net_name: str, group_name: Optional[str] = None) -> Union[pyedb.grpc.database.hierarchy.pingroup.PinGroup, Tuple[str, pyedb.grpc.database.hierarchy.pingroup.PinGroup], bool]

      Create pin group by net name.

      Parameters
      ----------
      reference_designator : str
          Reference designator.
      net_name : str
          Net name.
      group_name : str, optional
          Group name.

      Returns
      -------
      :class:`pyedb.grpc.database.hierarchy.pingroup.PinGroup`
          Pin group instance.

      Examples
      --------
      >>> group = edbapp.components.create_pin_group_on_net("U1", "GND")



   .. py:method:: deactivate_rlc_component(component: Optional[str] = None, create_circuit_port: bool = False, pec_boundary: bool = False) -> bool

      Deactivate RLC component with a possibility to convert it to a circuit port.

      Parameters
      ----------
      component : str
          Reference designator of the RLC component.

      create_circuit_port : bool, optional
          Whether to replace the deactivated RLC component with a circuit port. The default
          is ``False``.
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
      >>> edb_file = r"C:\my_edb_file.aedb"
      >>> edb = Edb(edb_file)
      >>> for cmp in list(edb.components.instances.keys()):
      >>>     edb.components.deactivate_rlc_component(component=cmp, create_circuit_port=False)
      >>> edb.save()
      >>> edb.close()



   .. py:method:: add_port_on_rlc_component(component: Optional[Union[str, pyedb.grpc.database.hierarchy.component.Component]] = None, circuit_ports: bool = True, pec_boundary: bool = False) -> bool

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
      >>> edb.source_excitations.add_port_on_rlc_component("R1")



   .. py:method:: replace_rlc_by_gap_boundaries(component: Optional[Union[str, pyedb.grpc.database.hierarchy.component.Component]] = None) -> bool

      Replace RLC component by RLC gap boundaries. These boundary types are compatible with 3D modeler export.
      Only 2 pins RLC components are supported in this command.

      Parameters
      ----------
      component : str
          Reference designator of the RLC component.

      Returns
      -------
      bool
      ``True`` when succeed, ``False`` if it failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("edb_file")
      >>>  for refdes, cmp in edb.components.capacitors.items():
      >>>     edb.components.replace_rlc_by_gap_boundaries(refdes)
      >>> edb.save()
      >>> edb.close()



   .. py:method:: add_rlc_boundary(component: Optional[Union[str, pyedb.grpc.database.hierarchy.component.Component]] = None, circuit_type: bool = True) -> bool

      Add RLC gap boundary on component and replace it with a circuit port.
      The circuit port supports only 2-pin components.

      . deprecated:: pyedb 0.28.0
      Use :func:`pyedb.grpc.core.excitations.add_rlc_boundary` instead.

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



