src.pyedb.dotnet.database.padstack
==================================

.. py:module:: src.pyedb.dotnet.database.padstack

.. autoapi-nested-parse::

   This module contains the `EdbPadstacks` class.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.padstack.EdbPadstacks


Module Contents
---------------

.. py:class:: EdbPadstacks(p_edb)

   Bases: :py:obj:`object`


   Manages EDB methods for nets management accessible from `Edb.padstacks` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_padstacks = edbapp.padstacks


   .. py:property:: db

      Db object.



   .. py:method:: int_to_pad_type(val=0)

      Convert an integer to an EDB.PadGeometryType.

      Parameters
      ----------
      val : int

      Returns
      -------
      object
          EDB.PadType enumerator value.



   .. py:method:: int_to_geometry_type(val=0)

      Convert an integer to an EDB.PadGeometryType.

      Parameters
      ----------
      val : int

      Returns
      -------
      object
          EDB.PadGeometryType enumerator value.



   .. py:property:: definitions

      Padstack definitions.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.padstacks_data.EdbPadstack`]
          List of definitions via padstack definitions.




   .. py:property:: instances
      :type: Dict[int, pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance]


      Dictionary  of all padstack instances (vias and pins).

      Returns
      -------
      dict[int, :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`]
          List of padstack instances.




   .. py:property:: instances_by_name

      Dictionary  of all padstack instances (vias and pins) by name.

      Returns
      -------
      dict[str, :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`]
          List of padstack instances.




   .. py:method:: find_instance_by_id(value: int)

      Find a padstack instance by database id.

      Parameters
      ----------
      value : int



   .. py:property:: pins

      Dictionary  of all pins instances (belonging to component).

      Returns
      -------
      dic[str, :class:`dotnet.database.edb_data.definitions.EDBPadstackInstance`]
          Dictionary of EDBPadstackInstance Components.


      Examples
      --------
      >>> edbapp = dotnet.Edb("myproject.aedb")
      >>> pin_net_name = edbapp.pins[424968329].netname



   .. py:property:: vias

      Dictionary  of all vias instances not belonging to component.

      Returns
      -------
      list[:class:`dotnet.database.edb_data.definitions.EDBPadstackInstance`]
          Dictionary of EDBPadstackInstance Components.


      Examples
      --------
      >>> edbapp = dotnet.Edb("myproject.aedb")
      >>> pin_net_name = edbapp.pins[424968329].netname



   .. py:property:: pingroups

      All Layout Pin groups.

      Returns
      -------
      list
          List of all layout pin groups.



   .. py:property:: pad_type

      Return a PadType Enumerator.



   .. py:method:: create_circular_padstack(padstackname=None, holediam='300um', paddiam='400um', antipaddiam='600um', startlayer=None, endlayer=None)

      Create a circular padstack.

      Parameters
      ----------
      padstackname : str, optional
          Name of the padstack. The default is ``None``.
      holediam : str, optional
          Diameter of the hole with units. The default is ``"300um"``.
      paddiam : str, optional
          Diameter of the pad with units. The default is ``"400um"``.
      antipaddiam : str, optional
          Diameter of the antipad with units. The default is ``"600um"``.
      startlayer : str, optional
          Starting layer. The default is ``None``, in which case the top
          is the starting layer.
      endlayer : str, optional
          Ending layer. The default is ``None``, in which case the bottom
          is the ending layer.

      Returns
      -------
      str
          Name of the padstack if the operation is successful.



   .. py:method:: create_dielectric_filled_backdrills(layer: str, diameter: Union[float, str], material: str, permittivity: float, padstack_instances: Optional[List[pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance]] = None, padstack_definition: Optional[Union[str, List[str]]] = None, dielectric_loss_tangent: Optional[float] = None, nets: Optional[Union[str, List[str]]] = None) -> bool

      Create dielectric-filled back-drills for through-hole vias.

      Back-drilling (a.k.a. controlled-depth drilling) is used to remove the
      unused via stub that acts as an unterminated transmission-line segment,
      thereby improving signal-integrity at high frequencies.  This routine
      goes one step further: after the stub is removed the resulting cylindrical
      cavity is **completely filled** with a user-specified dielectric.  The
      fill material restores mechanical rigidity, prevents solder-wicking, and
      keeps the original via’s electrical characteristics intact on the
      remaining, still-plated, portion.

      Selection criteria
      ------------------
      A via is processed only when **all** of the following are true:

      1. It is a through-hole structure (spans at least three metal layers).
      2. It includes the requested ``layer`` somewhere in its layer span.
      3. It belongs to one of the supplied ``padstack_definition`` names
         (or to *any* definition if the argument is omitted).
      4. It is attached to one of the supplied ``nets`` (or to *any* net if
         the argument is omitted).

      Geometry that is created
      ------------------------
      For every qualified via the routine

      * Generates a new pad-stack definition named ``<original_name>_BD``.
        The definition is drilled from the **bottom-most signal layer** up to
        and **including** ``layer``, uses the exact ``diameter`` supplied, and
        is plated at 100 %.
      * Places an additional pad-stack instance on top of the original via,
        thereby filling the newly drilled cavity with the requested
        ``material``.
      * Leaves the original via untouched—only its unused stub is removed.

      The back-drill is **not** subtracted from anti-pads or plane clearances;
      the filling material is assumed to be electrically invisible at the
      frequencies of interest.

      Parameters
      ----------
      layer : :class:`str`
          Signal layer name up to which the back-drill is performed (inclusive).
          The drill always starts on the bottom-most signal layer of the stack-up.
      diameter : :class:`float` or :class:`str`
          Finished hole diameter for the back-drill.  A numeric value is
          interpreted in the database length unit; a string such as
          ``"0.3mm"`` is evaluated with units.
      material : :class:`str`
          Name of the dielectric material that fills the drilled cavity.  If the
          material does not yet exist in the central material library it is
          created on the fly.
      permittivity : :class:`float`
          Relative permittivity :math:`\varepsilon_{\mathrm{r}}` used when the
          material has to be created.  Must be positive.
      padstack_instances : :class:`list` [:class:`PadstackInstance` ], optional
          Explicit list of via instances to process.  When provided,
          ``padstack_definition`` and ``nets`` are ignored for filtering.
      padstack_definition : :class:`str` or :class:`list` [:class:`str` ], optional
          Pad-stack definition(s) to process.  If omitted, **all** through-hole
          definitions are considered.
      dielectric_loss_tangent : :class:`float`, optional
          Loss tangent :math:`\tan\delta` used when the material has to be
          created.  Defaults to ``0.0``.
      nets : :class:`str` or :class:`list` [:class:`str` ], optional
          Net name(s) used to filter vias.  If omitted, vias belonging to
          **any** net are processed.

      Returns
      -------
      :class:`bool`
          ``True`` when at least one back-drill was successfully created.
          ``False`` if no suitable via was found or any error occurred.

      Raises
      ------
      ValueError
          If ``material`` is empty or if ``permittivity`` is non-positive when a
          new material must be created.

      Notes
      -----
      * The routine is safe to call repeatedly: existing back-drills are **not**
        duplicated because the ``*_BD`` definition name is deterministic.
      * The original via keeps its pad-stack definition and net assignment; only
        its unused stub is removed.
      * The back-drill is **not** subtracted from anti-pads or plane clearances;
        the filling material is assumed to be electrically invisible at the
        frequencies of interest.

      Examples
      --------
      Create back-drills on all vias belonging to two specific pad-stack
      definitions and two DDR4 nets:

      >>> edb.padstacks.create_dielectric_filled_backdrills(
      ...     layer="L3",
      ...     diameter="0.25mm",
      ...     material="EPON_827",
      ...     permittivity=3.8,
      ...     dielectric_loss_tangent=0.015,
      ...     padstack_definition=["VIA_10MIL", "VIA_16MIL"],
      ...     nets=["DDR4_DQ0", "DDR4_DQ1"],
      ... )
      True



   .. py:method:: delete_padstack_instances(net_names)

      Delete padstack instances by net names.

      Parameters
      ----------
      net_names : str, list
          Names of the nets to delete.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> Edb.padstacks.delete_padstack_instances(net_names=["GND"])



   .. py:method:: set_solderball(padstackInst, sballLayer_name, isTopPlaced=True, ballDiam=0.0001)

      Set solderball for the given PadstackInstance.

      Parameters
      ----------
      padstackInst : Edb.Cell.Primitive.PadstackInstance or int
          Padstack instance id or object.
      sballLayer_name : str,
          Name of the layer where the solder ball is placed. No default values.
      isTopPlaced : bool, optional.
          Bollean triggering is the solder ball is placed on Top or Bottom of the layer stackup.
      ballDiam : double, optional,
          Solder ball diameter value.

      Returns
      -------
      bool




   .. py:method:: create_coax_port(padstackinstance, use_dot_separator=True, name=None)

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




   .. py:method:: get_pinlist_from_component_and_net(refdes=None, netname=None)

      Retrieve pins given a component's reference designator and net name.

      Parameters
      ----------
      refdes : str, optional
          Reference designator of the component. The default is ``None``.
      netname : str optional
          Name of the net. The default is ``None``.

      Returns
      -------
      dict
          Dictionary of pins if the operation is successful.
          ``False`` is returned if the net does not belong to the component.




   .. py:method:: get_pad_parameters(pin, layername, pad_type=0)

      Get Padstack Parameters from Pin or Padstack Definition.

      Parameters
      ----------
      pin : Edb.definition.PadstackDef or Edb.definition.PadstackInstance
          Pin or PadstackDef on which get values.
      layername : str
          Layer on which get properties.
      pad_type : int
          Pad Type.

      Returns
      -------
      tuple
          Tuple of (GeometryType, ParameterList, OffsetX, OffsetY, Rot).



   .. py:method:: set_all_antipad_value(value)

      Set all anti-pads from all pad-stack definition to the given value.

      Parameters
      ----------
      value : float, str
          Anti-pad value.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` if an anti-pad value fails to be assigned.



   .. py:method:: check_and_fix_via_plating(minimum_value_to_replace=0.0, default_plating_ratio=0.2)

      Check for minimum via plating ration value, values found below the minimum one are replaced by default
      plating ratio.

      Parameters
      ----------
      minimum_value_to_replace : float
          Plating ratio that is below or equal to this value is to be replaced
          with the value specified for the next parameter. Default value ``0.0``.
      default_plating_ratio : float
          Default value to use for plating ratio. The default value is ``0.2``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` if an anti-pad value fails to be assigned.



   .. py:method:: get_via_instance_from_net(net_list=None)

      Get the list for EDB vias from a net name list.

      Parameters
      ----------
      net_list : str or list
          The list of the net name to be used for filtering vias. If no net is provided the command will
          return an all vias list.

      Returns
      -------
      list of Edb.Cell.Primitive.PadstackInstance
          List of EDB vias.



   .. py:method:: create(padstackname=None, holediam='300um', paddiam='400um', antipaddiam='600um', pad_shape='Circle', antipad_shape='Circle', x_size='600um', y_size='600um', corner_radius='300um', offset_x='0.0', offset_y='0.0', rotation='0.0', has_hole=True, pad_offset_x='0.0', pad_offset_y='0.0', pad_rotation='0.0', pad_polygon=None, antipad_polygon=None, polygon_hole=None, start_layer=None, stop_layer=None, add_default_layer=False, anti_pad_x_size='600um', anti_pad_y_size='600um', hole_range='upper_pad_to_lower_pad')

      Create a padstack.

      Parameters
      ----------
      padstackname : str, optional
          Name of the padstack. The default is ``None``.
      holediam : str, optional
          Diameter of the hole with units. The default is ``"300um"``.
      paddiam : str, optional
          Diameter of the pad with units, used with ``"Circle"`` shape. The default is ``"400um"``.
      antipaddiam : str, optional
          Diameter of the antipad with units. The default is ``"600um"``.
      pad_shape : str, optional
          Shape of the pad. The default is ``"Circle``. Options are ``"Circle"``, ``"Rectangle"`` and ``"Polygon"``.
      antipad_shape : str, optional
          Shape of the antipad. The default is ``"Circle"``. Options are ``"Circle"`` ``"Rectangle"`` and
          ``"Bullet"``.
      x_size : str, optional
          Only applicable to bullet and rectangle shape. The default is ``"600um"``.
      y_size : str, optional
          Only applicable to bullet and rectangle shape. The default is ``"600um"``.
      corner_radius :
          Only applicable to bullet shape. The default is ``"300um"``.
      offset_x : str, optional
          X offset of antipad. The default is ``"0.0"``.
      offset_y : str, optional
          Y offset of antipad. The default is ``"0.0"``.
      rotation : str, optional
          rotation of antipad. The default is ``"0.0"``.
      has_hole : bool, optional
          Whether this padstack has a hole.
      pad_offset_x : str, optional
          Padstack offset in X direction.
      pad_offset_y : str, optional
          Padstack offset in Y direction.
      pad_rotation : str, optional
          Padstack rotation.
      start_layer : str, optional
          Start layer of the padstack definition.
      stop_layer : str, optional
          Stop layer of the padstack definition.
      add_default_layer : bool, optional
          Add ``"Default"`` to padstack definition. Default is ``False``.
      anti_pad_x_size : str, optional
          Only applicable to bullet and rectangle shape. The default is ``"600um"``.
      anti_pad_y_size : str, optional
          Only applicable to bullet and rectangle shape. The default is ``"600um"``.
      hole_range : str, optional
          Define the padstack hole range. Arguments supported, ``"through"``, ``"begin_on_upper_pad"``,
          ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``.

      Returns
      -------
      str
          Name of the padstack if the operation is successful.



   .. py:method:: duplicate(target_padstack_name, new_padstack_name='')

      Duplicate a padstack.

      Parameters
      ----------
      target_padstack_name : str
          Name of the padstack to be duplicated.
      new_padstack_name : str, optional
          Name of the new padstack.

      Returns
      -------
      str
          Name of the new padstack.



   .. py:method:: place(position: list, definition_name: str | pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstack, net_name: str = '', via_name: str = '', rotation: float = 0.0, fromlayer: str = None, tolayer: str = None, solderlayer: str = None, is_pin: bool = False)

      Place a via.

      Parameters
      ----------
      position : list
          List of float values for the [x,y] positions where the via is to be placed.
      definition_name : str
          Name of the padstack definition.
      net_name : str, optional
          Name of the net. The default is ``""``.
      via_name : str, optional
          The default is ``""``.
      rotation : float, str, optional
          Rotation of the padstack in degrees. The default
          is ``0``.
      fromlayer :
          The default is ``None``.
      tolayer :
          The default is ``None``.
      solderlayer :
          The default is ``None``.
      is_pin : bool, optional
          Whether if the padstack is a pin or not. Default is `False`.

      Returns
      -------
      :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`



   .. py:method:: remove_pads_from_padstack(padstack_name, layer_name=None)

      Remove the Pad from a padstack on a specific layer by setting it as a 0 thickness circle.

      Parameters
      ----------
      padstack_name : str
          padstack name
      layer_name : str, optional
          Layer name on which remove the PadParameters. If None, all layers will be taken.

      Returns
      -------
      bool
          ``True`` if successful.



   .. py:method:: set_pad_property(padstack_name, layer_name=None, pad_shape='Circle', pad_params=0, pad_x_offset=0, pad_y_offset=0, pad_rotation=0, antipad_shape='Circle', antipad_params=0, antipad_x_offset=0, antipad_y_offset=0, antipad_rotation=0)

      Set pad and antipad properties of the padstack.

      Parameters
      ----------
      padstack_name : str
          Name of the padstack.
      layer_name : str, optional
          Name of the layer. If None, all layers will be taken.
      pad_shape : str, optional
          Shape of the pad. The default is ``"Circle"``. Options are ``"Circle"``,  ``"Square"``, ``"Rectangle"``,
          ``"Oval"`` and ``"Bullet"``.
      pad_params : str, optional
          Dimension of the pad. The default is ``"0"``.
      pad_x_offset : str, optional
          X offset of the pad. The default is ``"0"``.
      pad_y_offset : str, optional
          Y offset of the pad. The default is ``"0"``.
      pad_rotation : str, optional
          Rotation of the pad. The default is ``"0"``.
      antipad_shape : str, optional
          Shape of the antipad. The default is ``"0"``.
      antipad_params : str, optional
          Dimension of the antipad. The default is ``"0"``.
      antipad_x_offset : str, optional
          X offset of the antipad. The default is ``"0"``.
      antipad_y_offset : str, optional
          Y offset of the antipad. The default is ``"0"``.
      antipad_rotation : str, optional
          Rotation of the antipad. The default is ``"0"``.

      Returns
      -------
      bool
          ``True`` if successful.



   .. py:method:: get_instances(name=None, pid=None, definition_name=None, net_name=None, component_reference_designator=None, component_pin=None)

      Get padstack instances by conditions.

      Parameters
      ----------
      name : str, optional
          Name of the padstack.
      pid : int, optional
          Id of the padstack.
      definition_name : str, list, optional
          Name of the padstack definition.
      net_name : str, optional
          The net name to be used for filtering padstack instances.
      component_pin: str, optional
          Pin Number of the component.
      Returns
      -------
      list
          List of :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`.



   .. py:method:: get_padstack_instance_by_net_name(net_name)

      Get a list of padstack instances by net name.

      Parameters
      ----------
      net_name : str
          The net name to be used for filtering padstack instances.

      Returns
      -------
      list
          List of :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`.



   .. py:method:: get_reference_pins(positive_pin, reference_net='gnd', search_radius=0.005, max_limit=0, component_only=True, pinlist_position=None)

      Search for reference pins using given criteria.

      Parameters
      ----------
      positive_pin : EDBPadstackInstance
          Pin used for evaluating the distance on the reference pins found.
      reference_net : str, optional
          Reference net. The default is ``"gnd"``.
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
      >>> reference_pins = edbapp.padstacks.get_reference_pins(positive_pin=pin, reference_net="GND",
      >>> search_radius=5e-3, max_limit=0, component_only=True)



   .. py:method:: get_padstack_instances_rtree_index(nets=None)

      Returns padstack instances Rtree index.

      Parameters
      ----------
      nets : str or list, optional
          net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.

      Returns
      -------
      Rtree index object.




   .. py:method:: get_padstack_instances_id_intersecting_polygon(points, nets=None, padstack_instances_index=None)

      Returns the list of padstack instances ID intersecting a given bounding box and nets.

      Parameters
      ----------
      bounding_box : tuple or list.
          bounding box, [x1, y1, x2, y2]
      nets : str or list, optional
          net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.
      padstack_instances_index : optional, Rtree object.
          Can be provided optionally to prevent computing padstack instances Rtree index again.

      Returns
      -------
      List of padstack instances ID intersecting the bounding box.



   .. py:method:: get_padstack_instances_intersecting_bounding_box(bounding_box, nets=None, padstack_instances_index=None)

      Returns the list of padstack instances ID intersecting a given bounding box and nets.

      Parameters
      ----------
      bounding_box : tuple or list.
          bounding box, [x1, y1, x2, y2]
      nets : str or list, optional
          net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.
      padstack_instances_index : optional, Rtree object.
          Can be provided optionally to prevent computing padstack instances Rtree index again.

      Returns
      -------
      List of padstack instances ID intersecting the bounding box.



   .. py:method:: merge_via(contour_boxes, net_filter=None, start_layer=None, stop_layer=None)

      Evaluate padstack instances included on the provided point list and replace all by single instance.

      Parameters
      ----------
      contour_boxes : List[List[List[float, float]]]
          Nested list of polygon with points [x,y].
      net_filter : optional
          List[str: net_name] apply a net filter, nets included in the filter are excluded from the via merge.
      start_layer : optional, str
          Padstack instance start layer, if `None` the top layer is selected.
      stop_layer : optional, str
          Padstack instance stop layer, if `None` the bottom layer is selected.

      Return
      ------
      List[str], list of created padstack instances ID.




   .. py:method:: merge_via_along_lines(net_name='GND', distance_threshold=0.005, minimum_via_number=6, selected_angles=None, padstack_instances_id=None)

      Replace padstack instances along lines into a single polygon.

      Detect all padstack instances that are placed along lines and replace them by a single polygon based one
      forming a wall shape. This method is designed to simplify meshing on via fence usually added to shield RF traces
      on PCB.

      Parameters
      ----------
      net_name : str
          Net name used for detected padstack instances. Default value is ``"GND"``.

      distance_threshold : float, None, optional
          If two points in a line are separated by a distance larger than `distance_threshold`,
          the line is divided in two parts. Default is ``5e-3`` (5mm), in which case the control is not performed.

      minimum_via_number : int, optional
          The minimum number of points that a line must contain. Default is ``6``.

      selected_angles : list[int, float]
          Specify angle in degrees to detected, for instance [0, 180] is only detecting horizontal and vertical lines.
          Other values can be assigned like 45 degrees. When `None` is provided all lines are detected. Default value
          is `None`.
      padstack_instances_id : List[int]
       List of padstack instances ID's to include. If `None`, the algorithm will scan all padstack instances belonging
       to the specified net. Default value is `None`.


      Returns
      -------
      bool
          List[int], list of created padstack instances id.




   .. py:method:: reduce_via_in_bounding_box(bounding_box, x_samples, y_samples, nets=None)

      reduce the number of vias intersecting bounding box and nets by x and y samples.

      Parameters
      ----------
      bounding_box : tuple or list.
          bounding box, [x1, y1, x2, y2]
      x_samples : int
      y_samples : int
      nets : str or list, optional
          net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.

      Returns
      -------
      bool
          ``True`` when succeeded ``False`` when failed. <



   .. py:method:: dbscan(padstack: Dict[int, List[float]], max_distance: float = 0.001, min_samples: int = 5) -> Dict[int, List[str]]
      :staticmethod:


      density based spatial clustering for padstack instances

      Parameters
      ----------
      padstack : dict.
          padstack id: [x, y]

      max_distance: float
          maximum distance between two points to be included in one cluster

      min_samples: int
          minimum number of points that a cluster must have

      Returns
      -------
      dict
          clusters {cluster label: [padstack ids]} <



   .. py:method:: reduce_via_by_density(padstacks: List[int], cell_size_x: float = 0.001, cell_size_y: float = 0.001, delete: bool = False) -> tuple[List[int], List[List[List[float]]]]

      Reduce the number of vias by density. Keep only one via which is closest to the center of the cell. The cells
      are automatically populated based on the input vias.

      Parameters
      ----------
      padstacks: List[int]
          List of padstack ids to be reduced.

      cell_size_x : float
          Width of each grid cell (default is 1e-3).

      cell_size_y : float
          Height of each grid cell (default is 1e-3).

      delete: bool
          If True, delete vias that are not kept (default is False).

      Returns
      -------
      List[int]
          IDs of vias kept after reduction.

      List[List[float]]
          coordinates for grid lines (for plotting).




