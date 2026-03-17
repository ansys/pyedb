src.pyedb.grpc.database.primitive.padstack_instance
===================================================

.. py:module:: src.pyedb.grpc.database.primitive.padstack_instance


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.padstack_instance.PadstackInstance


Module Contents
---------------

.. py:class:: PadstackInstance(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.inner.conn_obj.ConnObj`


   Manages EDB functionalities for a padstack.

   Parameters
   ----------
   :class:`PadstackInstance <pyedb.grpc.dataybase.primitive.PadstackInstance>`
       PadstackInstance object.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", version="2026.1")
   >>> edb_padstack_instance = edb.padstacks.instances[0]


   .. py:attribute:: core


   .. py:method:: create(layout, padstack_definition: str, net: Union[pyedb.grpc.database.net.net.Net, str], position_x: float, position_y: float, rotation: float, top_layer: str | pyedb.grpc.database.layers.stackup_layer.StackupLayer, bottom_layer: str | pyedb.grpc.database.layers.stackup_layer.StackupLayer, name: str = None, solder_ball_layer: pyedb.grpc.database.layers.stackup_layer.StackupLayer = None, layer_map: str = 'two_way') -> PadstackInstance
      :classmethod:


      Create a padstack instance.

      Parameters
      ----------
      layout : :class:`Layout <py
          edb.grpc.database.layout.layout.Layout>`
          Layout object.
      net : :class:`Net <pyedb.grpc.database.net.net.Net>` or str
          Net object or net name.
      padstack_definition : str
          Padstack definition name.
      position_x : float
          X position.
      position_y : float
          Y position.
      rotation : float
          Rotation.
      top_layer : str, :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`
          Top layer.
      bottom_layer : str, :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`
          Bottom layer.
      name : str, optional
          Padstack instance name. The default is ``None``, in which case a name is automatically assigned.
      solder_ball_layer : :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`, optional
          Solder ball layer. The default is ``None``.
      layer_map : str, optional
          Layer map type. The default is ``"two_way"``. Options are ``"forward"``, ``"backward"``.

      Returns
      -------
      :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
          PadstackInstance object.



   .. py:property:: layer_map


   .. py:property:: solderball_layer


   .. py:method:: get_hole_overrides()


   .. py:method:: set_hole_overrides(enabled, diameter)


   .. py:property:: backdrill_parameters


   .. py:property:: is_pin

      Property added for backward compatibility with earlier versions of pyEDB.



   .. py:property:: net

      Net.

      Returns
      -------
      :class:`Net <pyedb.grpc.database.net.net.Net>`
          Net object.



   .. py:property:: layout

      Layout.

      Returns
      -------
      :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`
          Layout object.



   .. py:property:: definition
      :type: pyedb.grpc.database.definition.padstack_def.PadstackDef


      Padstack definition.

      Returns
      -------
      :class:`PadstackDef`<pyedb.grpc.database.definition.padstack_def.PadstackDef>`



   .. py:property:: padstack_definition
      :type: str


      Padstack definition name.

      Returns
      -------
      str
          Padstack definition name.




   .. py:property:: terminal
      :type: pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal


      PadstackInstanceTerminal.

      Returns
      -------
      :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
      PadstackInstanceTerminal>`
          PadstackInstanceTerminal object.



   .. py:property:: side_number

      Return the number of sides meshed of the padstack instance.
      Returns
      -------
      int
          Number of sides meshed of the padstack instance.



   .. py:method:: delete()

      Delete the padstack instance.



   .. py:method:: set_backdrill_top(drill_depth, drill_diameter, offset=0.0)

      Set backdrill from top.

      .deprecated:: 0.55.0
      Use :method:`set_back_drill_by_depth` instead.

      Parameters
      ----------
      drill_depth : str
          Name of the drill to layer.
      drill_diameter : float, str
          Diameter of backdrill size.
      offset : str, optional.
          offset with respect to the layer to drill to.

      Returns
      -------
      bool
          True if success, False otherwise.



   .. py:method:: set_backdrill_bottom(drill_depth, drill_diameter, offset=0.0)

      Set backdrill from bottom.

      .deprecated: 0.55.0
      Use: method:`set_back_drill_by_depth` instead.

      Parameters
      ----------
      drill_depth : str
          Name of the drill to layer.
      drill_diameter : float, str
          Diameter of backdrill size.
      offset : str, optional.
          offset with respect to the layer to drill to.

      Returns
      -------
      bool
          True if success, False otherwise.



   .. py:method:: create_terminal(name=None) -> pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal

      Create a padstack instance terminal.

      Returns
      -------
      :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
      PadstackInstanceTerminal>`
          PadstackInstanceTerminal object.




   .. py:method:: get_terminal(create_new_terminal=True) -> pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal

      Returns padstack instance terminal.

      Parameters
      ----------
      create_new_terminal : bool, optional
          If terminal instance is not created,
          and value is ``True``, a new PadstackInstanceTerminal is created.

      Returns
      -------
      :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
      PadstackInstanceTerminal>`
          PadstackInstanceTerminal object.




   .. py:method:: create_coax_port(name=None, radial_extent_factor=0)

      Create a coax port.

      Parameters
      ----------
      name : str, optional.
          Port name, the default is ``None``, in which case a name is automatically assigned.
      radial_extent_factor : int, float, optional
          Radial extent of coaxial port.

      Returns
      -------
      :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
          Port terminal.



   .. py:method:: create_port(name=None, reference=None, is_circuit_port=False)

      Create a port on the padstack instance.

      Parameters
      ----------
      name : str, optional
          Name of the port. The default is ``None``, in which case a name is automatically assigned.
      reference : reference net or pingroup  optional
          Negative terminal of the port.
      is_circuit_port : bool, optional
          Whether it is a circuit port.

      Returns
      -------
      :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
          Port terminal.



   .. py:property:: object_instance

      Layout object instance.

      Returns
      -------
      :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance import.LayoutObjInstance>`




   .. py:property:: bounding_box
      :type: list[float]


      Padstack instance bounding box.
      Because this method is slow, the bounding box is stored in a variable and reused.

      Returns
      -------
      list of float



   .. py:method:: in_polygon(polygon_data, include_partial=True, arbitrary_extent_value=0.0003) -> bool

      Check if padstack Instance is in given polygon data.

      Parameters
      ----------
      polygon_data : PolygonData Object
      include_partial : bool, optional
          Whether to include partial intersecting instances. The default is ``True``.
      simple_check : bool, optional
          Whether to perform a single check based on the padstack center or check the padstack bounding box.
      arbitrary_extent_value : float, optional
          When ``include_partial`` is ``True``, an arbitrary value is used to create a bounding box for the padstack
          instance to check for intersection and save computation time during the cutout. The default is ``300e-6``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



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

      Returns
      -------
      List[str]
          List of layer names.




   .. py:property:: id

      Padstack instance ID.



   .. py:property:: edb_uid

      Padstack instance EDB UID.



   .. py:property:: net_name
      :type: str


      Net name.

      Returns
      -------
      str
          Name of the net.



   .. py:property:: layout_object_instance

      Layout object instance.

      Returns
      -------
      :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`




   .. py:property:: component

      Component.

      Returns
      -------
      :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`




   .. py:property:: position
      :type: list[float]


      Padstack instance position.

      Returns
      -------
      list[float, float]
          List of ``[x, y]`` coordinates for the padstack instance position.



   .. py:property:: rotation
      :type: float


      Padstack instance rotation.

      Returns
      -------
      float
          Rotatation value for the padstack instance.



   .. py:property:: position_and_rotation
      :type: list[float]


      Padstack instance position.

      Returns
      -------
      list
          List of ``[x, y,r]`` coordinates for the padstack instance position and rotation.



   .. py:property:: name
      :type: str


      Padstack Instance Name.

      Returns
      -------
      str
          If it is a pin, the syntax will be like in AEDT ComponentName-PinName.




   .. py:property:: backdrill_type
      :type: str


      Backdrill type.


      Returns
      -------
      str
          Backdrill type.




   .. py:property:: backdrill_top
      :type: bool



   .. py:property:: backdrill_bottom
      :type: bool


      Check is backdrill is starting at bottom.


      Returns
      -------
      bool




   .. py:property:: backdrill_diameter


   .. py:property:: backdrill_layer


   .. py:property:: backdrill_offset


   .. py:property:: padstack_def

      Padstack definition.

      Returns
      -------
      :class:`PadstackDef`<pyedb.grpc.database.definition.padstack_def.PadstackDef>`



   .. py:property:: metal_volume
      :type: float


      Metal volume of the via hole instance in cubic units (m3). Metal plating ratio is accounted.

      Returns
      -------
      float
          Metal volume of the via hole instance.




   .. py:property:: component_pin
      :type: str


      Component pin.

      Returns
      -------
      str
          Component pin name.




   .. py:property:: aedt_name
      :type: str


      Retrieve the pin name that is shown in AEDT.

      .. note::
         To obtain the EDB core pin name, use `pin.name`.

      Returns
      -------
      str
          Name of the pin in AEDT.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.padstacks.instances[111].get_aedt_pin_name()




   .. py:method:: split() -> list

      Split padstack instance into multiple instances. The new instances only connect adjacent layers.



   .. py:method:: get_layer_range() -> tuple[str, str]

      Get the layer range of the padstack instance.

      Returns
      -------
      tuple
          Tuple of (start_layer_name, stop_layer_name).



   .. py:method:: convert_hole_to_conical_shape(angle=75)

      Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

      Parameters
      ----------
      angle : float, optional
          Angle of laser penetration in degrees. The angle defines the lowest hole diameter with this formula:
          HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
          The default is ``75``.
          The lowest hole is ``0.75*HoleDepth/HoleDiam``.

      Returns
      -------



   .. py:method:: get_backdrill_type(from_bottom=True)

      Return backdrill type
      Parameters
      ----------
      from_bottom : bool, optional
          default value is `True.`

      Return
      ------
      str
          Back drill type, `"layer_drill"`,`"depth_drill"`, `"no_drill"`.




   .. py:method:: get_back_drill_by_depth(from_bottom: bool, include_fill_material: Literal[False] = False) -> tuple[pyedb.grpc.database.utility.value.Value, pyedb.grpc.database.utility.value.Value]
                  get_back_drill_by_depth(from_bottom: bool, include_fill_material: Literal[True]) -> tuple[pyedb.grpc.database.utility.value.Value, pyedb.grpc.database.utility.value.Value, str]

      Get the back drill type by depth.

      Parameters
      ----------
      from_bottom : bool
          Whether to get the back drill type from the bottom.
      include_fill_material : bool, optional
          Input flag to obtain fill material as well as other parameters.
          If false, the return tuple does not include fill material and is backward compatible with previous versions.
      Returns
      -------
      tuple of (.Value, .Value, str)
          Tuple containing:

          - **drill_depth** : Drilling depth, may not align with layer.
          - **diameter** : Drilling diameter.
          - **fill_material** : Fill material name (empty string if no fill),
            only included when ``include_fill_material`` is True.




   .. py:method:: set_back_drill_by_depth(drill_depth, diameter, from_bottom=True, fill_material='')

      Set back drill by depth.

      Parameters
      ----------
      drill_depth : str, float
          drill depth value
      diameter : str, float
          drill diameter
      from_bottom : bool, optional
          Default value is `True`.
      fill_material : str, optional



   .. py:method:: get_back_drill_by_layer(from_bottom: bool, include_fill_material: Literal[False] = False) -> tuple[str, pyedb.grpc.database.utility.value.Value, pyedb.grpc.database.utility.value.Value]
                  get_back_drill_by_layer(from_bottom: bool, include_fill_material: Literal[True]) -> tuple[str, pyedb.grpc.database.utility.value.Value, pyedb.grpc.database.utility.value.Value, str]

      Get the back drill type by the layer.

      Parameters
      ----------
      from_bottom : bool
          Whether to get the back drill type from the bottom.
      include_fill_material : bool, optional
          Input flag to obtain fill material as well as other parameters.
          If false, the return tuple does not include fill material and is backward compatible with previous versions.
      Returns
      -------
      tuple of (.Layer, .Value, .Value, str)
          Returns a tuple in this format:

          **(drill_to_layer, offset, diameter, fill_material)**

          - **drill_to_layer** : Layer drills to. If drill from top, drill stops at the upper elevation of the layer.
                                 If from bottom, drill stops at the lower elevation of the layer.
          - **offset** : Layer offset (or depth if layer is empty).
          - **diameter** : Drilling diameter.
          - **fill_material** : Fill material name (empty string if no fill).
                                Returned only when include_fill_material is true.




   .. py:method:: set_back_drill_by_layer(drill_to_layer, diameter, offset, from_bottom=True, fill_material='')

      Set back drill layer.

      Parameters
      ----------
      drill_to_layer : str
          Layer to drill to.
      offset : str, float
          Offset value
      diameter : str, float
          Drill diameter
      from_bottom : bool, optional
          Default value is `True`
      fill_material : str, optional
          Fill material name



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



   .. py:method:: in_voids(net_name=None, layer_name=None) -> list[any]

      Check if this padstack instance is in any void.

      Parameters
      ----------
      net_name : str
          Net name of the voids to be checked. Default is ``None``.
      layer_name : str
          Layer name of the voids to be checked. Default is ``None``.

      Returns
      -------
      List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
          List of the voids that include this padstack instance.



   .. py:property:: pingroups

      Pin groups that the pin belongs to.

      Returns
      -------
      List[:class:`PinGroup <ansys.edb.core.hierarchy.pin_group>`]
          List of pin groups that the pin belongs to.



   .. py:property:: placement_layer

      Placement layer name.

      Returns
      -------
      str
          Name of the placement layer.



   .. py:property:: layer

      Placement layer object.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
         Placement layer.



   .. py:property:: lower_elevation
      :type: float


      Lower elevation of the placement layer.

      Returns
      -------
      float
          Lower elavation of the placement layer.



   .. py:property:: upper_elevation
      :type: float


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



   .. py:method:: create_rectangle_in_pad(layer_name, return_points=False, partition_max_order=16)

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
      bool, List, :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`
          Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> edb_layout = edbapp.modeler
      >>> list_of_padstack_instances = list(edbapp.padstacks.instances.values())
      >>> padstack_inst = list_of_padstack_instances[0]
      >>> padstack_inst.create_rectangle_in_pad("TOP")



   .. py:method:: get_reference_pins(reference_net='GND', search_radius=0.005, max_limit=0, component_only=True, pinlist_position=None) -> list[any]

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
      List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]

      Examples
      --------
      >>> edbapp = Edb("target_path")
      >>> pin = edbapp.components.instances["J5"].pins["19"]
      >>> reference_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=0,
      >>> component_only=True)



   .. py:method:: get_connected_objects()

      Get connected objects.

      Returns
      -------
      List[:class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`]



   .. py:method:: set_dcir_equipotential_advanced(contact_radius=None, layer_name=None)

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



