src.pyedb.dotnet.database.edb_data.padstacks_data
=================================================

.. py:module:: src.pyedb.dotnet.database.edb_data.padstacks_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.padstacks_data.EDBPadProperties
   src.pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstack
   src.pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance


Module Contents
---------------

.. py:class:: EDBPadProperties(edb_padstack, layer_name, pad_type, p_edb_padstack)

   Bases: :py:obj:`object`


   Manages EDB functionalities for pad properties.

   Parameters
   ----------
   edb_padstack : str
       Inherited AEDT object.
   layer_name : str
       Name of the layer.
   pad_type :
       Type of the pad.


   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", edbversion="2026.1")
   >>> edb_pad_properties = edb.padstacks.definitions["MyPad"].pad_by_layer["TOP"]


   .. py:attribute:: layer_name


   .. py:attribute:: pad_type


   .. py:property:: geometry_type
      :type: int


      Geometry type.

      Returns
      -------
      int
          Type of the geometry.



   .. py:property:: shape
      :type: str


      Get the shape of the pad.

      Returns
      -------
      str
          Shape of the pad.



   .. py:property:: parameters_values
      :type: list[float]


      Parameters.

      Returns
      -------
      list
          List of parameters.



   .. py:property:: parameters_values_string
      :type: list[str]


      Parameters value in string format.

      Returns
      -------
      list
          List of parameters in string format.



   .. py:property:: polygon_data
      :type: pyedb.dotnet.database.geometry.polygon_data.PolygonData


      Parameters.

      Returns
      -------
      PolygonData



   .. py:property:: parameters
      :type: collections.OrderedDict[str, pyedb.dotnet.database.edb_data.edbvalue.EdbValue]


      Get parameters.

      Returns
      -------
      dict



   .. py:property:: offset_x
      :type: str


      Offset for the X axis.

      Returns
      -------
      str
          Offset for the X axis.



   .. py:property:: offset_y
      :type: str


      Offset for the Y axis.

      Returns
      -------
      str
          Offset for the Y axis.



   .. py:property:: rotation
      :type: str


      Rotation.

      Returns
      -------
      str
          Value for the rotation.



   .. py:method:: int_to_pad_type(val=0) -> Any

      Convert an integer to an EDB.PadGeometryType.

      Parameters
      ----------
      val : int

      Returns
      -------
      object
          EDB.PadType enumerator value.



   .. py:method:: int_to_geometry_type(val=0) -> Any

      Convert an integer to an EDB.PadGeometryType.

      Parameters
      ----------
      val : int

      Returns
      -------
      object
          EDB.PadGeometryType enumerator value.



.. py:class:: EDBPadstack(edb_padstack, ppadstack)

   Bases: :py:obj:`object`


   Manages EDB functionalities for a padstack.

   Parameters
   ----------
   edb_padstack :

   ppadstack : str
       Inherited AEDT object.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_padstack = edb.padstacks.definitions["MyPad"]


   .. py:attribute:: PAD_SHAPE_PARAMETERS


   .. py:attribute:: edb_padstack


   .. py:property:: pad_by_layer
      :type: dict[str, EDBPadProperties]


      Regular pad property.



   .. py:property:: antipad_by_layer
      :type: dict[str, EDBPadProperties]


      Anti pad property.



   .. py:property:: thermalpad_by_layer
      :type: dict[str, EDBPadProperties]


      Thermal pad property.



   .. py:property:: data
      :type: Any


      Get padstack definition data.

      Returns
      -------
      PadstackDefData
          Padstack definition data object.



   .. py:property:: instances
      :type: list[Any]


      Definitions Instances.



   .. py:property:: name
      :type: str


      Padstack Definition Name.



   .. py:property:: via_layers
      :type: list[str]


      Layers.

      Returns
      -------
      list
          List of layers.



   .. py:property:: via_start_layer
      :type: str


      Starting layer.

      Returns
      -------
      str
          Name of the starting layer.



   .. py:property:: via_stop_layer
      :type: str


      Stopping layer.

      Returns
      -------
      str
          Name of the stopping layer.



   .. py:property:: hole_params

      Via Hole parameters values.



   .. py:property:: hole_diameter
      :type: float


      Hole diameter.



   .. py:property:: hole_diameter_string
      :type: str


      Hole diameter in string format.



   .. py:property:: hole_properties
      :type: list[float]


      Hole properties.

      Returns
      -------
      list
          List of float values for hole properties.



   .. py:property:: hole_type
      :type: int


      Hole type.

      Returns
      -------
      int
          Type of the hole.



   .. py:property:: hole_offset_x
      :type: str


      Hole offset for the X axis.

      Returns
      -------
      str
          Hole offset value for the X axis.



   .. py:property:: hole_offset_y
      :type: str


      Hole offset for the Y axis.

      Returns
      -------
      str
          Hole offset value for the Y axis.



   .. py:property:: hole_rotation
      :type: str


      Hole rotation.

      Returns
      -------
      str
          Value for the hole rotation.



   .. py:property:: hole_plating_ratio
      :type: float


      Hole plating ratio.

      Returns
      -------
      float
          Percentage for the hole plating.



   .. py:property:: hole_plating_thickness
      :type: float


      Hole plating thickness.

      Returns
      -------
      float
          Thickness of the hole plating if present.



   .. py:property:: hole_finished_size
      :type: float | int


      Finished hole size.

      Returns
      -------
      float
          Finished size of the hole (Total Size + PlatingThickess*2).



   .. py:property:: material
      :type: str


      Hole material.

      Returns
      -------
      str
          Material of the hole.



   .. py:property:: padstack_instances
      :type: dict[str, EDBPadstackInstance]


      Get all the vias that belongs to active Padstack definition.

      Returns
      -------
      dict



   .. py:property:: hole_range
      :type: str


      Get hole range value from padstack definition.

      Returns
      -------
      str
          Possible returned values are ``"through"``, ``"begin_on_upper_pad"``,
          ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"unknown_range"``.



   .. py:method:: convert_to_3d_microvias(convert_only_signal_vias=True, hole_wall_angle=75, delete_padstack_def=True) -> bool

      Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

      Parameters
      ----------
      convert_only_signal_vias : bool, optional
          Either to convert only vias belonging to signal nets or all vias. Defaults is ``True``.
      hole_wall_angle : float, optional
          Angle of laser penetration in degrees. The angle defines the lowest hole diameter with this formula:
          HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
          The default is ``15``.
          The lowest hole is ``0.75*HoleDepth/HoleDiam``.
      delete_padstack_def : bool, optional
          Whether to delete the padstack definition. The default is ``True``.
          If ``False``, the padstack definition is not deleted and the hole size is set to zero.

      Returns
      -------
          ``True`` when successful, ``False`` when failed.



   .. py:method:: split_to_microvias() -> list[EDBPadstackInstance]

      Convert actual padstack definition to multiple microvias definitions.

      Returns
      -------
      List of :class:`pyedb.dotnet.database.padstackEDBPadstack`



   .. py:method:: get_pad_parameters() -> dict[str, list[dict[str, str]]]

      Pad parameters.

      Returns
      -------
      dict
          params = {
          'regular_pad': [
              {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0.1mm', 'offset_y': '0',
              'rotation': '0', 'diameter': '0.5mm'}
          ],
          'anti_pad': [
              {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
              'diameter': '1mm'}
          ],
          'thermal_pad': [
              {'layer_name': '1_Top', 'shape': 'round90', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
              'inner': '1mm', 'channel_width': '0.2mm', 'isolation_gap': '0.3mm'},
          ],
          'hole': [
              {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
               'diameter': '0.1499997mm'},
          ]
      }



   .. py:method:: set_pad_parameters(param)


   .. py:method:: get_hole_parameters()


   .. py:method:: set_hole_parameters(params)


   .. py:method:: get_solder_parameters() -> dict[str, str]

      Solder ball parameters.



   .. py:method:: set_solder_parameters(parameters)


.. py:class:: EDBPadstackInstance(edb_padstackinstance, _pedb)

   Bases: :py:obj:`pyedb.dotnet.database.cell.primitive.primitive.Connectable`


   Manages EDB functionalities for a padstack.

   Parameters
   ----------
   edb_padstackinstance :

   _pedb :
       Inherited AEDT object.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_padstack_instance = edb.padstacks.instances[0]


   .. py:property:: layer_map

      Edb layer map.



   .. py:method:: get_hole_overrides()


   .. py:method:: set_hole_overrides(is_hole_override, hole_override)

      Set the hole overrides of Padstack Instance.

      Parameters
      ----------
      is_hole_override : bool
          If padstack instance is hole override.
      hole_override : :class:`Value <ansys.edb.utility.Value>`
          Hole override diameter of this padstack instance.



   .. py:property:: solderball_layer
      :type: str



   .. py:method:: get_terminal(name=None, create_new_terminal=False) -> PadstackInstanceTerminal | None

      Get PadstackInstanceTerminal object.

      Parameters
      ----------
      name : str, optional
          Name of the terminal. Only applicable when create_new_terminal is True.
      create_new_terminal : bool, optional
          Whether to create a new terminal.

      Returns
      -------
      :class:`database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal`



   .. py:property:: side_number
      :type: int


      Return the number of sides meshed of the padstack instance.
      Returns
      -------
      int
          Number of sides meshed of the padstack instance.



   .. py:property:: terminal
      :type: PadstackInstanceTerminal | None


      Terminal.



   .. py:method:: create_terminal(name=None) -> pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal

      Create a padstack instance terminal



   .. py:method:: create_coax_port(name=None, radial_extent_factor=0) -> pyedb.dotnet.database.edb_data.ports.CoaxPort

      Create a coax port.



   .. py:method:: create_port(name=None, reference=None, is_circuit_port=False) -> pyedb.dotnet.database.edb_data.ports.WavePort

      Create a port on the padstack.

      Parameters
      ----------
      name : str, optional
          Name of the port. The default is ``None``, in which case a name is automatically assigned.
      reference : class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetsData`,             class:`pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`,             class:`pyedb.dotnet.database.edb_data.sources.PinGroup`, optional
          Negative terminal of the port.
      is_circuit_port : bool, optional
          Whether it is a circuit port.



   .. py:method:: set_dcir_equipotential_advanced(contact_radius=None, layer_name=None) -> pyedb.dotnet.database.cell.primitive.primitive.Primitive

      Set DCIR equipotential region on the padstack instance. This method allows to set equipotential region on
      specified layer and specify contact circle size. If contact_radius is not specified, the method will use the
      pad size. If layer_name is not specified, the method will use the start layer of the padstack definition.

      Parameters
      ----------
      contact_radius : float, optional
          Radius of the contact circle. The default is ``None```, in which case the
          method will use the pad size.
      layer_name : str, optional
          Layer name to set the equipotential region. The default is ``None``, in which case the method will use the
          start layer of the padstack definition.



   .. py:property:: object_instance

      Return Ansys.Ansoft.Edb.LayoutInstance.LayoutObjInstance object.



   .. py:property:: bounding_box
      :type: list[list[float]]


      Get bounding box of the padstack instance.
      Because this method is slow, the bounding box is stored in a variable and reused.

      Returns
      -------
      list of float



   .. py:method:: in_polygon(polygon_data, include_partial=True, simple_check=False) -> bool

      Check if padstack Instance is in given polygon data.

      Parameters
      ----------
      polygon_data : PolygonData Object
      include_partial : bool, optional
          Whether to include partial intersecting instances. The default is ``True``.
      simple_check : bool, optional
          Whether to perform a single check based on the padstack center or check the padstack bounding box.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:property:: pin
      :type: EDBPadstackInstance


      EDB padstack object.



   .. py:property:: padstack_definition
      :type: str


      Padstack definition Name.

      Returns
      -------
      str
          Name of the padstack definition.



   .. py:property:: definition
      :type: EDBPadstack


      Padstack definition.

      Returns
      -------
      str
          Name of the padstack definition.



   .. py:property:: backdrill_top
      :type: tuple[str, str, str] | tuple[str, str] | None


      Backdrill layer from top.

      Returns
      -------
      tuple
          Tuple of the layer name, drill diameter, and offset if it exists.



   .. py:method:: set_backdrill_top(drill_depth, drill_diameter, offset=0.0)

      Set backdrill from top.

      Parameters
      ----------
      drill_depth : str
          Name of the drill to layer.
      drill_diameter : float, str
          Diameter of backdrill size.
      offset : float, str
          Offset for the backdrill. The default is ``0.0``. If the value is other than the
          default, the stub does not stop at the layer. In AEDT, this parameter is called
          "Mfg stub length".

      Returns
      -------
      bool
          True if success, False otherwise.



   .. py:property:: backdrill_type
      :type: str


      Adding grpc compatibility. DotNet is supporting only layer drill type with adding stub length.



   .. py:method:: get_back_drill_by_layer() -> tuple[str, float, float] | None


   .. py:property:: backdrill_bottom
      :type: tuple[str, str, str] | tuple[str, str] | None


      Backdrill layer from bottom.

      Returns
      -------
      tuple
          Tuple of the layer name, drill diameter, and drill offset if it exists.



   .. py:property:: backdrill_parameters
      :type: dict[str, dict[str, str]]


      Backdrill parameters by layer.



   .. py:method:: set_back_drill_by_layer(drill_to_layer, diameter, offset, from_bottom=True, fill_material='')

      Method added to bring compatibility with grpc.



   .. py:method:: set_backdrill_bottom(drill_depth, drill_diameter, offset=0.0)

      Set backdrill from bottom.

      Parameters
      ----------
      drill_depth : str
          Name of the drill to layer.
      drill_diameter : float, str
          Diameter of the backdrill size.
      offset : float, str, optional
          Offset for the backdrill. The default is ``0.0``. If the value is other than the
          default, the stub does not stop at the layer. In AEDT, this parameter is called
          "Mfg stub length".

      Returns
      -------
      bool
          True if success, False otherwise.



   .. py:property:: start_layer
      :type: str


      Starting layer.

      Returns
      -------
      str
          Name of the starting layer.



   .. py:property:: stop_layer
      :type: str


      Stopping layer.

      Returns
      -------
      str
          Name of the stopping layer.



   .. py:property:: layer_range_names
      :type: list[str]


      List of all layers to which the padstack instance belongs.



   .. py:property:: is_pin
      :type: bool


      Determines whether this padstack instance is a layout pin.

      Returns
      -------
      bool
          True if this padstack type is a layout pin, False otherwise.



   .. py:property:: position
      :type: list[float]


      Padstack instance position.

      Returns
      -------
      list
          List of ``[x, y]`` coordinates for the padstack instance position.



   .. py:property:: position_and_rotation
      :type: list[float]


      Padstack instance position and rotation.

      Returns
      -------
      list
          List of ``[x, y]`` coordinates for the padstack instance position.



   .. py:property:: rotation
      :type: float


      Padstack instance rotation.

      Returns
      -------
      float
          Rotatation value for the padstack instance.



   .. py:property:: metal_volume
      :type: float


      Metal volume of the via hole instance in cubic units (m3). Metal plating ratio is accounted.

      Returns
      -------
      float
          Metal volume of the via hole instance.




   .. py:property:: pin_number
      :type: str


      Get pin number.



   .. py:property:: component_pin
      :type: str


      Get component pin.



   .. py:property:: aedt_name
      :type: str


      Retrieve the pin name that is shown in AEDT.

      .. note::
         To obtain the EDB core pin name, use `pin.GetName()`.

      Returns
      -------
      str
          Name of the pin in AEDT.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.padstacks.instances[111].get_aedt_pin_name()




   .. py:method:: parametrize_position(prefix=None) -> list[str]

      Parametrize the instance position.

      Parameters
      ----------
      prefix : str, optional
          Prefix for the variable name. Default is ``None``.
          Example `"MyVariableName"` will create 2 Project variables $MyVariableNamesX and $MyVariableNamesY.

      Returns
      -------
      List
          List of variables created.



   .. py:method:: in_voids(net_name=None, layer_name=None) -> list[pyedb.dotnet.database.cell.primitive.primitive.Primitive]

      Check if this padstack instance is in any void.

      Parameters
      ----------
      net_name : str
          Net name of the voids to be checked. Default is ``None``.
      layer_name : str
          Layer name of the voids to be checked. Default is ``None``.

      Returns
      -------
      list
          List of the voids that include this padstack instance.



   .. py:property:: pingroups
      :type: Any


      Pin groups that the pin belongs to.

      Returns
      -------
      list
          List of pin groups that the pin belongs to.



   .. py:property:: placement_layer
      :type: str


      Placement layer.

      Returns
      -------
      str
          Name of the placement layer.



   .. py:property:: lower_elevation
      :type: float | None


      Lower elevation of the placement layer.

      Returns
      -------
      float
          Lower elavation of the placement layer.



   .. py:property:: upper_elevation
      :type: float | None


      Upper elevation of the placement layer.

      Returns
      -------
      float
         Upper elevation of the placement layer.



   .. py:property:: top_bottom_association
      :type: int


      Top/bottom association of the placement layer.

      Returns
      -------
      int
          Top/bottom association of the placement layer.

          * 0 Top associated.
          * 1 No association.
          * 2 Bottom associated.
          * 4 Number of top/bottom association type.
          * -1 Undefined.



   .. py:method:: create_rectangle_in_pad(layer_name, return_points=False, partition_max_order=16) -> list[pyedb.dotnet.database.dotnet.primitive.PrimitiveDotNet] | bool

      Create a rectangle inscribed inside a padstack instance pad.

      The rectangle is fully inscribed in the pad and has the maximum area.
      It is necessary to specify the layer on which the rectangle will be created.

      Parameters
      ----------
      layer_name : str
          Name of the layer on which to create the polygon.
      return_points : bool, optional
          If `True` does not create the rectangle and just returns a list containing the rectangle vertices.
          Default is `False`.
      partition_max_order : float, optional
          Order of the lattice partition used to find the quasi-lattice polygon that approximates ``polygon``.
          Default is ``16``.

      Returns
      -------
      bool, List,  :class:`pyedb.dotnet.database.edb_data.primitives.EDBPrimitives`
          Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> edb_layout = edbapp.modeler
      >>> list_of_padstack_instances = list(edbapp.padstacks.instances.values())
      >>> padstack_inst = list_of_padstack_instances[0]
      >>> padstack_inst.create_rectangle_in_pad("TOP")



   .. py:method:: get_reference_pins(reference_net='GND', search_radius=0.005, max_limit=0, component_only=True, pinlist_position: dict = None) -> list[EDBPadstackInstance]

      Search for reference pins using given criteria.

      Parameters
      ----------
      reference_net : str, optional
          Reference net. The default is ``"GND"``.
      search_radius : float, optional
          Search radius for finding padstack instances. The default is ``5e-3``.
      max_limit : int, optional
          Maximum limit for the padstack instances found. The default is ``0``, in which
          case no limit is applied. The maximum limit value occurs on the nearest
          reference pins from the positive one that is found.
      component_only : bool, optional
          Whether to limit the search to component padstack instances only. The
          default is ``True``. When ``False``, the search is extended to the entire layout.

      Returns
      -------
      list
          List of :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`.

      Examples
      --------
      >>> edbapp = Edb("target_path")
      >>> pin = edbapp.components.instances["J5"].pins["19"]
      >>> reference_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=0,
      >>> component_only=True)



   .. py:method:: split() -> list[EDBPadstackInstance]

      Split padstack instance into multiple instances. The new instances only connect adjacent layers.



   .. py:method:: convert_hole_to_conical_shape(angle=75)

      Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

      Parameters
      ----------
      angle : float, optional
          Angle of laser penetration in degrees. The angle defines the lowest hole diameter with this formula:
          HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
          The default is ``75``.
          The lowest hole is ``0.75*HoleDepth/HoleDiam``.




