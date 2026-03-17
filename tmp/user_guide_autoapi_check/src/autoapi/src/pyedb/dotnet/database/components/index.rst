src.pyedb.dotnet.database.components
====================================

.. py:module:: src.pyedb.dotnet.database.components

.. autoapi-nested-parse::

   This module contains the `Components` class.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.components.Components


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.components.resistor_value_parser


Module Contents
---------------

.. py:function:: resistor_value_parser(RValue: str | float) -> float

   Convert a resistor value.

   Parameters
   ----------
   RValue : str | float
       Resistor value.

   Returns
   -------
   float
       Resistor value.



.. py:class:: Components(p_edb)

   Bases: :py:obj:`object`


   Manages EDB components and related method accessible from `Edb.components` property.

   Parameters
   ----------
   edb_class : :class:`pyedb.dotnet.edb.Edb`

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder")
   >>> edbapp.components


   .. py:property:: instances

      All Cell components objects.

      Returns
      -------
      Dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
          Default dictionary for the EDB component.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.instances




   .. py:property:: definitions

      Retrieve component definition list.

      Returns
      -------
      dict of :class:`EDBComponentDef`



   .. py:property:: nport_comp_definition

      Retrieve Nport component definition list.



   .. py:method:: import_definition(file_path: pathlib.Path) -> bool

      Import component definition from json file.

      Parameters
      ----------
      file_path : Path
          File path of json file.



   .. py:method:: export_definition(file_path: pathlib.Path) -> str

      Export component definitions to json file.

      Parameters
      ----------
      file_path : Path
          File path of json file.

      Returns
      -------




   .. py:method:: refresh_components() -> bool

      Refresh the component dictionary.



   .. py:property:: resistors
      :type: dict[str, dict]


      Resistors.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
          Dictionary of resistors.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.resistors



   .. py:property:: capacitors
      :type: dict[str, dict]


      Capacitors.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
          Dictionary of capacitors.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.capacitors



   .. py:property:: inductors
      :type: dict[str, dict]


      Inductors.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
          Dictionary of inductors.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.inductors




   .. py:property:: ICs
      :type: dict[str, dict]


      Integrated circuits.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
          Dictionary of integrated circuits.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.ICs




   .. py:property:: IOs
      :type: dict[str, dict]


      Circuit inupts and outputs.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
          Dictionary of circuit inputs and outputs.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.IOs




   .. py:property:: Others
      :type: dict[str, dict]


      Other core components.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
          Dictionary of other core components.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.others




   .. py:property:: components_by_partname
      :type: dict


      Components by part name.

      Returns
      -------
      dict
          Dictionary of components by part name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.components_by_partname




   .. py:method:: get_component_by_name(name) -> bool

      Retrieve a component by name.

      Parameters
      ----------
      name : str
          Name of the component.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: get_components_from_nets(netlist=None) -> list

      Retrieve components from a net list.

      Parameters
      ----------
      netlist : str, optional
          Name of the net list. The default is ``None``.

      Returns
      -------
      list
          List of components that belong to the signal nets.




   .. py:method:: get_component_placement_vector(mounted_component, hosting_component, mounted_component_pin1, mounted_component_pin2, hosting_component_pin1, hosting_component_pin2, flipped=False) -> tuple

      Get the placement vector between 2 components.

      Parameters
      ----------
      mounted_component : `edb.cell.hierarchy._hierarchy.Component`
          Mounted component name.
      hosting_component : `edb.cell.hierarchy._hierarchy.Component`
          Hosting component name.
      mounted_component_pin1 : str
          Mounted component Pin 1 name.
      mounted_component_pin2 : str
          Mounted component Pin 2 name.
      hosting_component_pin1 : str
          Hosted component Pin 1 name.
      hosting_component_pin2 : str
          Hosted component Pin 2 name.
      flipped : bool, optional
          Either if the mounted component will be flipped or not.

      Returns
      -------
      tuple
          Tuple of Vector offset, rotation and solder height.

      Examples
      --------
      >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
      >>> hosting_cmp = edb1.components.get_component_by_name("U100")
      >>> mounted_cmp = edb2.components.get_component_by_name("BGA")
      >>> vector, rotation, solder_ball_height = edb1.components.get_component_placement_vector(
      ...     mounted_component=mounted_cmp,
      ...     hosting_component=hosting_cmp,
      ...     mounted_component_pin1="A12",
      ...     mounted_component_pin2="A14",
      ...     hosting_component_pin1="A12",
      ...     hosting_component_pin2="A14",
      ... )



   .. py:method:: get_solder_ball_height(cmp) -> float | bool

      Get component solder ball height.

      Parameters
      ----------
      cmp : str or  self._pedb.component
          EDB component or str component name.

      Returns
      -------
      double, bool
          Salder ball height vale, ``False`` when failed.




   .. py:method:: get_vendor_libraries() -> dict[str, dict[str, dict[str]]]

      Retrieve all capacitors and inductors libraries from ANSYS installation (used by Siwave).

      Returns
      -------
      ComponentLib object contains nested dictionaries to navigate through [component type][vendors][series]
      :class: `pyedb.component_libraries.ansys_components.ComponentPart`

      Examples
      --------
      >>> edbapp = Edb()
      >>> comp_lib = edbapp.components.get_vendor_libraries()
      >>> network = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].s_parameters
      >>> network.write_touchstone(os.path.join(edbapp.directory, "test_export.s2p"))




   .. py:method:: create_source_on_component(sources=None) -> bool

      Create voltage, current source, or resistor on component.

      Parameters
      ----------
      sources : list[SourceBuilder] or SourceBuilder
          List of ``edb_data.sources.SourceBuilder`` objects.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: create_port_on_pins(refdes, pins, reference_pins, impedance=50.0, port_name=None, pec_boundary=False, pingroup_on_single_pin=False)


   .. py:method:: create_port_on_component(component, net_list, port_type=SourceType.CoaxPort, do_pingroup=True, reference_net='gnd', port_name=None, solder_balls_height=None, solder_balls_size=None, solder_balls_mid_size=None, extend_reference_pins_outside_component=False) -> float | bool

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
      >>> edbapp.components.create_port_on_component(component="U2A5", net_list=net_list,
      >>> port_type=SourceType.CoaxPort, do_pingroup=False, reference_net="GND")




   .. py:method:: replace_rlc_by_gap_boundaries(component=None)

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
      >>> edb = Edb(edb_file)
      >>>  for refdes, cmp in edb.components.capacitors.items():
      >>>     edb.components.replace_rlc_by_gap_boundaries(refdes)
      >>> edb.save_edb()
      >>> edb.close_edb()



   .. py:method:: deactivate_rlc_component(component=None, create_circuit_port=False, pec_boundary=False)

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
      >>> edb.save_edb()
      >>> edb.close_edb()



   .. py:method:: add_port_on_rlc_component(component=None, circuit_ports=True, pec_boundary=False)

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



   .. py:method:: add_rlc_boundary(component=None, circuit_type=True)

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



   .. py:method:: create_rlc_component(pins, component_name='', r_value=None, c_value=None, l_value=None, is_parallel=False)

      Create physical Rlc component.

      Parameters
      ----------
      pins : list
           List of EDB pins, length must be 2, since only 2 pins component are currently supported.
           It can be an `dotnet.database.edb_data.padstacks_data.EDBPadstackInstance` object or
           an Edb Padstack Instance object.
      component_name : str
          Component definition name.
      r_value : float
          Resistor value.
      c_value : float
          Capacitance value.
      l_value : float
          Inductor value.
      is_parallel : bool
          Using parallel model when ``True``, series when ``False``.

      Returns
      -------
      Component
          Created EDB component.




   .. py:method:: create(pins, component_name=None, placement_layer=None, component_part_name=None, is_rlc=False, r_value=None, c_value=None, l_value=None, is_parallel=False)

      Create a component from pins.

      Parameters
      ----------
      pins : list
          List of EDB core pins.
      component_name : str
          Name of the reference designator for the component.
      placement_layer : str, optional
          Name of the layer used for placing the component.
      component_part_name : str, optional
          Part name of the component.
      is_rlc : bool, optional
          Whether if the new component will be an RLC or not.
      r_value : float
          Resistor value.
      c_value : float
          Capacitance value.
      l_value : float
          Inductor value.
      is_parallel : bool
          Using parallel model when ``True``, series when ``False``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> pins = edbapp.components.get_pin_from_component("A1")
      >>> edbapp.components.create(pins, "A1New")




   .. py:method:: set_component_model(componentname, model_type='Spice', modelpath=None, modelname=None)

      Assign a Spice or Touchstone model to a component.

      Parameters
      ----------
      componentname : str
          Name of the component.
      model_type : str, optional
          Type of the model. Options are ``"Spice"`` and
          ``"Touchstone"``.  The default is ``"Spice"``.
      modelpath : str, optional
          Full path to the model file. The default is ``None``.
      modelname : str, optional
          Name of the model. The default is ``None``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.set_component_model(
      ...     "A1", model_type="Spice", modelpath="pathtospfile", modelname="spicemodelname"
      ... )




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




   .. py:method:: delete_single_pin_rlc(deactivate_only: bool = False) -> list

      Delete all RLC components with a single pin.
      Single pin component model type will be reverted to ``"RLC"``.

      Parameters
      ----------
      deactivate_only : bool, optional
          Whether to only deactivate RLC components with a single point rather than
          delete them. The default is ``False``, in which case they are deleted.

      Returns
      -------
      list
          List of deleted RLC components.


      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> list_of_deleted_rlcs = edbapp.components.delete_single_pin_rlc()
      >>> print(list_of_deleted_rlcs)




   .. py:method:: delete(component_name)

      Delete a component.

      Parameters
      ----------
      component_name : str
          Name of the component.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.delete("A1")




   .. py:method:: disable_rlc_component(component_name)

      Disable a RLC component.

      Parameters
      ----------
      component_name : str
          Name of the RLC component.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.disable_rlc_component("A1")




   .. py:method:: set_solder_ball(component='', sball_diam=None, sball_height=None, shape='Cylinder', sball_mid_diam=None, chip_orientation='chip_down', auto_reference_size=True, reference_size_x=0, reference_size_y=0, reference_height=0)

      Set cylindrical solder balls on a given component.

      Parameters
      ----------
      component : str or EDB component, optional
          Name of the discrete component.
      sball_diam  : str, float, optional
          Diameter of the solder ball.
      sball_height : str, float, optional
          Height of the solder ball.
      shape : str, optional
          Shape of solder ball. Options are ``"Cylinder"``,
          ``"Spheroid"``. The default is ``"Cylinder"``.
      sball_mid_diam : str, float, optional
          Mid diameter of the solder ball.
      chip_orientation : str, optional
          Give the chip orientation, ``"chip_down"`` or ``"chip_up"``. Default is ``"chip_down"``. Only applicable on
          IC model.
      auto_reference_size : bool, optional
          Whether to automatically set reference size.
      reference_size_x : int, str, float, optional
          X size of the reference. Applicable when auto_reference_size is False.
      reference_size_y : int, str, float, optional
          Y size of the reference. Applicable when auto_reference_size is False.
      reference_height : int, str, float, optional
          Height of the reference. Applicable when auto_reference_size is False.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.set_solder_ball("A1")




   .. py:method:: set_component_rlc(componentname, res_value=None, ind_value=None, cap_value=None, isparallel=False)

      Update values for an RLC component.

      Parameters
      ----------
      componentname :
          Name of the RLC component.
      res_value : float, optional
          Resistance value. The default is ``None``.
      ind_value : float, optional
          Inductor value.  The default is ``None``.
      cap_value : float optional
          Capacitor value.  The default is ``None``.
      isparallel : bool, optional
          Whether the RLC component is parallel. The default is ``False``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.set_component_rlc("R1", res_value=50, ind_value=1e-9, cap_value=1e-12, isparallel=False)




   .. py:method:: update_rlc_from_bom(bom_file, delimiter=';', valuefield='Func des', comptype='Prod name', refdes='Pos / Place')

      Update the EDC core component values (RLCs) with values coming from a BOM file.

      Parameters
      ----------
      bom_file : str
          Full path to the BOM file, which is a delimited text file.
          Header values needed inside the BOM reader must
          be explicitly set if different from the defaults.
      delimiter : str, optional
          Value to use for the delimiter. The default is ``";"``.
      valuefield : str, optional
          Field header containing the value of the component. The default is ``"Func des"``.
          The value for this parameter must being with the value of the component
          followed by a space and then the rest of the value. For example, ``"22pF"``.
      comptype : str, optional
          Field header containing the type of component. The default is ``"Prod name"``. For
          example, you might enter ``"Inductor"``.
      refdes : str, optional
          Field header containing the reference designator of the component. The default is
          ``"Pos / Place"``. For example, you might enter ``"C100"``.

      Returns
      -------
      bool
          ``True`` if the file contains the header and it is correctly parsed. ``True`` is
          returned even if no values are assigned.




   .. py:method:: import_bom(bom_file, delimiter=',', refdes_col=0, part_name_col=1, comp_type_col=2, value_col=3)

      Load external BOM file.

      Parameters
      ----------
      bom_file : str
          Full path to the BOM file, which is a delimited text file.
      delimiter : str, optional
          Value to use for the delimiter. The default is ``","``.
      refdes_col : int, optional
          Column index of reference designator. The default is ``"0"``.
      part_name_col : int, optional
           Column index of part name. The default is ``"1"``. Set to ``None`` if
           the column does not exist.
      comp_type_col : int, optional
          Column index of component type. The default is ``"2"``.
      value_col : int, optional
          Column index of value. The default is ``"3"``. Set to ``None``
          if the column does not exist.

      Returns
      -------
      bool



   .. py:method:: export_bom(bom_file, delimiter=',')

      Export Bom file from layout.

      Parameters
      ----------
      bom_file : str
          Full path to the BOM file, which is a delimited text file.
      delimiter : str, optional
          Value to use for the delimiter. The default is ``","``.



   .. py:method:: find_by_reference_designator(reference_designator)

      Find a component.

      Parameters
      ----------
      reference_designator : str
          Reference designator of the component.



   .. py:method:: get_pin_from_component(component, netName=None, pinName=None, net_name=None, pin_name=None)

      Retrieve the pins of a component.

      Parameters
      ----------
      component : str or EDB component
          Name of the component or the EDB component object.
      netName : str, optional
          Filter on the net name as an alternative to
          ``pinName``. The default is ``None``.
      pinName : str, optional
          Filter on the pin name an alternative to
          ``netName``. The default is ``None``.
      net_name : str, optional
          Filter on the net name as an alternative to
          ``pin_name``. The default is ``None``. This parameter is added to add compatibility with grpc and is
          recommended using it rather than `netName`.
      pin_name : str, optional
          Filter on the pin name an alternative to
          ``netName``. The default is ``None``. This parameter is added to add compatibility with grpc and is
          recommended using it rather than `pinName`.

      Returns
      -------
      list
          List of pins when the component is found or ``[]`` otherwise.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_pin_from_component("R1", refdes)




   .. py:method:: get_aedt_pin_name(pin)

      Retrieve the pin name that is shown in AEDT.

      .. note::
         To obtain the EDB core pin name, use `pin.GetName()`.

      Parameters
      ----------
      pin : str
          Name of the pin in EDB core.

      Returns
      -------
      str
          Name of the pin in AEDT.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_aedt_pin_name(pin)




   .. py:method:: get_pins(reference_designator, net_name=None, pin_name=None)

      Get component pins.

      Parameters
      ----------
      reference_designator : str
          Reference designator of the component.
      net_name : str, optional
          Name of the net.
      pin_name : str, optional
          Name of the pin.

      Returns
      -------




   .. py:method:: get_pin_position(pin)

      Retrieve the pin position in meters.

      Parameters
      ----------
      pin : str
          Name of the pin.

      Returns
      -------
      list
          Pin position as a list of float values in the form ``[x, y]``.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_pin_position(pin)




   .. py:method:: get_pins_name_from_net(net_name, pin_list=None)

      Retrieve pins belonging to a net.

      Parameters
      ----------
      pin_list : list of EDBPadstackInstance, optional
          List of pins to check. The default is ``None``, in which case all pins are checked
      net_name : str
          Name of the net.

      Returns
      -------
      list of str names:
          Pins belonging to the net.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_pins_name_from_net(pin_list, net_name)




   .. py:method:: get_nets_from_pin_list(PinList)

      Retrieve nets with one or more pins.

      Parameters
      ----------
      PinList : list
          List of pins.

      Returns
      -------
      list
          List of nets with one or more pins.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_nets_from_pin_list(pinlist)




   .. py:method:: get_component_net_connection_info(refdes)

      Retrieve net connection information.

      Parameters
      ----------
      refdes :
          Reference designator for the net.

      Returns
      -------
      dict
          Dictionary of the net connection information for the reference designator.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_component_net_connection_info(refdes)




   .. py:method:: get_rats()

      Retrieve a list of dictionaries of the reference designator, pin names, and net names.

      Returns
      -------
      list
          List of dictionaries of the reference designator, pin names,
          and net names.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_rats()




   .. py:method:: get_through_resistor_list(threshold=1)

      Retrieve through resistors.

      Parameters
      ----------
      threshold : int, optional
          Threshold value. The default is ``1``.

      Returns
      -------
      list
          List of through resistors.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.components.get_through_resistor_list()




   .. py:method:: short_component_pins(component_name, pins_to_short=None, width=0.001)

      Short pins of component with a trace.

      Parameters
      ----------
      component_name : str
          Name of the component.
      pins_to_short : list, optional
          List of pins to short. If `None`, all pins will be shorted.
      width : float, optional
          Short Trace width. It will be used in trace computation algorithm

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder")
      >>> edbapp.components.short_component_pins("J4A2", ["G4", "9", "3"])




