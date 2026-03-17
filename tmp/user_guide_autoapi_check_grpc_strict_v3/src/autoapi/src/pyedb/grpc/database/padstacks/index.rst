src.pyedb.grpc.database.padstacks
=================================

.. py:module:: src.pyedb.grpc.database.padstacks

.. autoapi-nested-parse::

   This module contains the `EdbPadstacks` class.



Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.padstacks.GEOMETRY_MAP
   src.pyedb.grpc.database.padstacks.PAD_TYPE_MAP


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.padstacks.Padstacks


Module Contents
---------------

.. py:data:: GEOMETRY_MAP

.. py:data:: PAD_TYPE_MAP

.. py:class:: Padstacks(p_edb: Any)

   Bases: :py:obj:`object`


   Manages EDB methods for padstacks accessible from `Edb.padstacks` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2024.2")
   >>> edb_padstacks = edbapp.padstacks


   .. py:method:: clear_instances_cache()

      Clear the cached padstack instances.



   .. py:property:: db
      :type: Any


      Db object.



   .. py:method:: int_to_pad_type(val=0) -> ansys.edb.core.definition.padstack_def_data.PadType
      :staticmethod:


      Convert an integer to an EDB.PadGeometryType.

      Parameters
      ----------
      val : int

      Returns
      -------
      object
          EDB.PadType enumerator value.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> pad_type = edb.padstacks.int_to_pad_type(0)  # Returns REGULAR_PAD
      >>> pad_type2 = edb.padstacks.int_to_pad_type(1)  # Returns ANTI_PAD



   .. py:method:: int_to_geometry_type(val: int = 0) -> ansys.edb.core.definition.padstack_def_data.PadGeometryType
      :staticmethod:


      Convert an integer to an EDB.PadGeometryType.

      Parameters
      ----------
      val : int

      Returns
      -------
      object
          EDB.PadGeometryType enumerator value.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> geom_type = edb.padstacks.int_to_geometry_type(1)  # Returns CIRCLE
      >>> geom_type2 = edb.padstacks.int_to_geometry_type(2)  # Returns SQUARE



   .. py:property:: definitions
      :type: Dict[str, pyedb.grpc.database.definition.padstack_def.PadstackDef]


      Padstack definitions.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.definition.padstack_def.PadstackDef`]
          Dictionary of padstack definitions with definition names as keys.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> all_definitions = edb.padstacks.definitions
      >>> for name, definition in all_definitions.items():
      ...     print(f"Padstack: {name}")



   .. py:property:: instances
      :type: Dict[int, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      All padstack instances (vias and pins) in the layout.

      Returns
      -------
      dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          Dictionary of padstack instances with database IDs as keys.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> all_instances = edb.padstacks.instances
      >>> for inst_id, instance in all_instances.items():
      ...     print(f"Instance {inst_id}: {instance.name}")



   .. py:property:: instances_by_net
      :type: Dict[Any, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]



   .. py:property:: instances_by_name
      :type: Dict[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      All padstack instances (vias and pins) indexed by name.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          Dictionary of padstack instances with names as keys.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> named_instances = edb.padstacks.instances_by_name
      >>> for name, instance in named_instances.items():
      ...     print(f"Instance named {name}")



   .. py:method:: find_instance_by_id(value: int) -> Optional[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]

      Find a padstack instance by database ID.

      Parameters
      ----------
      value : int
          Database ID of the padstack instance.

      Returns
      -------
      :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance` or None
          Padstack instance if found, otherwise ``None``.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> via = edb.padstacks.find_instance_by_id(123)
      >>> if via:
      ...     print(f"Found via: {via.name}")



   .. py:property:: pins
      :type: Dict[int, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      All pin instances belonging to components.

      Returns
      -------
      dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          Dictionary of pin instances with database IDs as keys.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> all_pins = edb.padstacks.pins
      >>> for pin_id, pin in all_pins.items():
      ...     print(f"Pin {pin_id} belongs to {pin.component.refdes}")



   .. py:property:: vias
      :type: Dict[int, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      All via instances not belonging to components.

      Returns
      -------
      dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          Dictionary of via instances with database IDs as keys.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> all_vias = edb.padstacks.vias
      >>> for via_id, via in all_vias.items():
      ...     print(f"Via {via_id} on net {via.net_name}")



   .. py:property:: pingroups
      :type: List[Any]


      All Layout Pin groups.

      . deprecated:: pyedb 0.28.0
      Use :func:`pyedb.grpc.core.layout.pin_groups` instead.

      Returns
      -------
      list
          List of all layout pin groups.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> groups = edb.padstacks._layout.pin_groups  # New way



   .. py:property:: pad_type
      :type: ansys.edb.core.definition.padstack_def_data.PadType


      Return a PadType Enumerator.



   .. py:method:: create_dielectric_filled_backdrills(layer: str, diameter: Union[float, str], material: str, permittivity: float, padstack_instances: Optional[List[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]] = None, padstack_definition: Optional[Union[str, List[str]]] = None, dielectric_loss_tangent: Optional[float] = None, nets: Optional[Union[str, List[str]]] = None) -> bool

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

      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
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



   .. py:method:: create_circular_padstack(padstackname: Optional[str] = None, holediam: str = '300um', paddiam: str = '400um', antipaddiam: str = '600um', startlayer: Optional[str] = None, endlayer: Optional[str] = None) -> str

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> via_name = edb.padstacks.create_circular_padstack(
      ...     padstackname="VIA1", holediam="200um", paddiam="400um", antipaddiam="600um"
      ... )



   .. py:method:: delete_batch_instances(instances_to_delete)


   .. py:method:: delete_padstack_instances(net_names: Union[str, List[str]]) -> bool

      Delete padstack instances by net names.

      Parameters
      ----------
      net_names : str, list
          Names of the nets whose padstack instances should be deleted.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> success = edb.padstacks.delete_padstack_instances("GND")



   .. py:method:: set_solderball(padstack_instance, solder_ball_layer, top_placed=True, solder_ball_diameter=0.0001)

      Set solderball for the given PadstackInstance.

      Parameters
      ----------
      padstack_instance : Edb.Cell.Primitive.PadstackInstance or int
          Padstack instance id or object.
      solder_ball_layer : str,
          Name of the layer where the solder ball is placed. No default values.
      top_placed : bool, optional.
          Boolean triggering is the solder ball is placed on Top or Bottom of the layer stackup.
      solder_ball_diameter : double, optional,
          Solder ball diameter value.

      Returns
      -------
      bool




   .. py:method:: create_coax_port(padstackinstance, use_dot_separator=True, name=None)

      Create HFSS 3Dlayout coaxial lumped port on a pastack
      Requires to have solder ball defined before calling this method.

      . deprecated:: pyedb 0.28.0
      Use :func:`pyedb.grpc.core.excitations.create_source_on_component` instead.

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




   .. py:method:: get_pin_from_component_and_net(refdes: Optional[str] = None, netname: Optional[str] = None) -> List[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]

      Retrieve pins by component reference designator and net name.

      Parameters
      ----------
      refdes : str, optional
          Component reference designator.
      netname : str, optional
          Net name.

      Returns
      -------
      list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          List of matching pin instances.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> pins = edb.padstacks.get_pin_from_component_and_net(refdes="U1", netname="VCC")
      >>> pins2 = edb.padstacks.get_pin_from_component_and_net(netname="GND")  # All GND pins



   .. py:method:: get_pinlist_from_component_and_net(refdes=None, netname=None)

      Retrieve pins given a component's reference designator and net name.

      . deprecated:: pyedb 0.28.0
      Use :func:`get_pin_from_component_and_net` instead.

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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> pins = edb.padstacks.get_pin_from_component_and_net(refdes="U1", netname="CLK")  # New way



   .. py:method:: get_pad_parameters(pin: pyedb.grpc.database.primitive.padstack_instance.PadstackInstance, layername: str, pad_type: str = 'regular_pad') -> Tuple[str, Union[List[float], List[List[float]]], float, float, float]

      Get pad parameters for a pin on a specific layer.

      Parameters
      ----------
      pin : :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
          Padstack instance.
      layername : str
          Layer name.
      pad_type : str, optional
          Pad type ("regular_pad", "anti_pad", "thermal_pad"). Default is ``"regular_pad"``.

      Returns
      -------
      tuple
          (geometry_type, parameters, offset_x, offset_y, rotation) where:
          - geometry_type : str
          - parameters : list[float] or list[list[float]]
          - offset_x : float
          - offset_y : float
          - rotation : float

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> via = edb.padstacks.instances[123]
      >>> geom_type, params, x, y, rot = edb.padstacks.get_pad_parameters(via, "TOP", "regular_pad")



   .. py:method:: set_all_antipad_value(value: Union[float, str]) -> bool

      Set anti-pad value for all padstack definitions.

      Parameters
      ----------
      value : float or str
          Anti-pad value with units (e.g., "0.2mm").

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> success = edb.padstacks.set_all_antipad_value("0.3mm")



   .. py:method:: check_and_fix_via_plating(minimum_value_to_replace: float = 0.0, default_plating_ratio: float = 0.2) -> bool

      Check and fix via plating ratios below a minimum value.

      Parameters
      ----------
      minimum_value_to_replace : float, optional
          Minimum plating ratio threshold. Default is ``0.0``.
      default_plating_ratio : float, optional
          Default plating ratio to apply. Default is ``0.2``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> success = edb.padstacks.check_and_fix_via_plating(minimum_value_to_replace=0.1)



   .. py:method:: get_via_instance_from_net(net_list: Optional[Union[str, List[str]]] = None) -> List[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]

      Get via instances by net names.

      Parameters
      ----------
      net_list : str or list, optional
          Net name(s) for filtering. Returns all vias if ``None``.

      Returns
      -------
      list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          List of via instances.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_design.edb")
      >>> vias = edb.padstacks.get_via_instance_from_net(["GND", "PWR"])



   .. py:method:: layers_between(layers, start_layer=None, stop_layer=None)

      Return the sub-list of *layers* that lies between *start_layer*
      (inclusive) and *stop_layer* (inclusive).  Works no matter which
      of the two is nearer the top of the stack.



   .. py:method:: create(padstackname: Optional[str] = None, holediam: str = '300um', paddiam: str = '400um', antipaddiam: str = '600um', pad_shape: str = 'Circle', antipad_shape: str = 'Circle', x_size: str = '600um', y_size: str = '600um', corner_radius: str = '300um', offset_x: str = '0.0', offset_y: str = '0.0', rotation: str = '0.0', has_hole: bool = True, pad_offset_x: str = '0.0', pad_offset_y: str = '0.0', pad_rotation: str = '0.0', pad_polygon: Optional[Any] = None, antipad_polygon: Optional[Any] = None, polygon_hole: Optional[Any] = None, start_layer: Optional[str] = None, stop_layer: Optional[str] = None, add_default_layer: bool = False, anti_pad_x_size: str = '600um', anti_pad_y_size: str = '600um', hole_range: str = 'upper_pad_to_lower_pad')

      Create a padstack definition.

      Parameters
      ----------
      padstackname : str, optional
          Name of the padstack definition.
      holediam : str, optional
          Hole diameter with units. Default is ``"300um"``.
      paddiam : str, optional
          Pad diameter with units. Default is ``"400um"``.
      antipaddiam : str, optional
          Anti-pad diameter with units. Default is ``"600um"``.
      pad_shape : str, optional
          Pad geometry type ("Circle", "Rectangle", "Polygon"). Default is ``"Circle"``.
      antipad_shape : str, optional
          Anti-pad geometry type ("Circle", "Rectangle", "Bullet", "Polygon"). Default is ``"Circle"``.
      x_size : str, optional
          X-size for rectangular/bullet shapes. Default is ``"600um"``.
      y_size : str, optional
          Y-size for rectangular/bullet shapes. Default is ``"600um"``.
      corner_radius : str, optional
          Corner radius for bullet shapes. Default is ``"300um"``.
      offset_x : str, optional
          X-offset for anti-pad. Default is ``"0.0"``.
      offset_y : str, optional
          Y-offset for anti-pad. Default is ``"0.0"``.
      rotation : str, optional
          Rotation for anti-pad in degrees. Default is ``"0.0"``.
      has_hole : bool, optional
          Whether the padstack has a hole. Default is ``True``.
      pad_offset_x : str, optional
          X-offset for pad. Default is ``"0.0"``.
      pad_offset_y : str, optional
          Y-offset for pad. Default is ``"0.0"``.
      pad_rotation : str, optional
          Rotation for pad in degrees. Default is ``"0.0"``.
      pad_polygon : list or :class:`ansys.edb.core.geometry.PolygonData`, optional
          Polygon points for custom pad shape.
      antipad_polygon : list or :class:`ansys.edb.core.geometry.PolygonData`, optional
          Polygon points for custom anti-pad shape.
      polygon_hole : list or :class:`ansys.edb.core.geometry.PolygonData`, optional
          Polygon points for custom hole shape.
      start_layer : str, optional
          Starting layer name.
      stop_layer : str, optional
          Ending layer name.
      add_default_layer : bool, optional
          Whether to add "Default" layer. Default is ``False``.
      anti_pad_x_size : str, optional
          Anti-pad X-size. Default is ``"600um"``.
      anti_pad_y_size : str, optional
          Anti-pad Y-size. Default is ``"600um"``.
      hole_range : str, optional
          Hole range type ("through", "begin_on_upper_pad", "end_on_lower_pad", "upper_pad_to_lower_pad").
          Default is ``"upper_pad_to_lower_pad"``.

      Returns
      -------
      str
          Name of the created padstack definition.



   .. py:method:: duplicate(target_padstack_name: str, new_padstack_name: str = '') -> str

      Duplicate a padstack definition.

      Parameters
      ----------
      target_padstack_name : str
          Name of the padstack definition to duplicate.
      new_padstack_name : str, optional
          Name for the new padstack definition.

      Returns
      -------
      str
          Name of the new padstack definition.



   .. py:method:: place(position: List[float], definition_name: str | pyedb.grpc.database.definition.padstack_def.PadstackDef, net_name: str = '', via_name: str = '', rotation: float = 0.0, from_layer: Optional[str] = None, to_layer: Optional[str] = None, solder_ball_layer: Optional[str] = None, is_pin: bool = False, layer_map: str = 'two_way') -> pyedb.grpc.database.primitive.padstack_instance.PadstackInstance

      Place a padstack instance.

      Parameters
      ----------
      position : list[float, float]
          [x, y] position for placement.
      definition_name : str or :class:`PadstackDef`
          Padstack definition name.
      net_name : str, optional
          Net name. Default is ``""``.
      via_name : str, optional
          Instance name. Default is ``""``.
      rotation : float, optional
          Rotation in degrees. Default is ``0.0``.
      from_layer : str, optional
          Starting layer name.
      to_layer : str, optional
          Ending layer name.
      solder_ball_layer : str, optional
          Solder ball layer name.
      is_pin : bool, optional
          Whether the instance is a pin. Default is ``False``.
      layer_map : str, optional
          Layer mapping information. Valid input is ``"two_way"``, ``"backward"``, or ``"forward"``.
          Default is ``two_way``.

      Returns
      -------
      :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance` or bool
          Created padstack instance or ``False`` if failed.



   .. py:method:: remove_pads_from_padstack(padstack_name: str, layer_name: Optional[str] = None)

      Remove pads from a padstack definition on specified layers.

      Parameters
      ----------
      padstack_name : str
          Padstack definition name.
      layer_name : str or list, optional
          Layer name(s). Applies to all layers if ``None``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: set_pad_property(padstack_name: str, layer_name: Optional[str] = None, pad_shape: str = 'Circle', pad_params: Union[float, List[float]] = 0, pad_x_offset: float = 0, pad_y_offset: float = 0, pad_rotation: float = 0, antipad_shape: str = 'Circle', antipad_params: Union[float, List[float]] = 0, antipad_x_offset: float = 0, antipad_y_offset: float = 0, antipad_rotation: float = 0)

      Set pad and anti-pad properties for a padstack definition.

      Parameters
      ----------
      padstack_name : str
          Padstack definition name.
      layer_name : str or list, optional
          Layer name(s). Applies to all layers if ``None``.
      pad_shape : str, optional
          Pad geometry type ("Circle", "Square", "Rectangle", "Oval", "Bullet"). Default is ``"Circle"``.
      pad_params : float or list, optional
          Pad dimension(s). Default is ``0``.
      pad_x_offset : float, optional
          Pad X-offset. Default is ``0``.
      pad_y_offset : float, optional
          Pad Y-offset. Default is ``0``.
      pad_rotation : float, optional
          Pad rotation in degrees. Default is ``0``.
      antipad_shape : str, optional
          Anti-pad geometry type ("Circle", "Square", "Rectangle", "Oval", "Bullet"). Default is ``"Circle"``.
      antipad_params : float or list, optional
          Anti-pad dimension(s). Default is ``0``.
      antipad_x_offset : float, optional
          Anti-pad X-offset. Default is ``0``.
      antipad_y_offset : float, optional
          Anti-pad Y-offset. Default is ``0``.
      antipad_rotation : float, optional
          Anti-pad rotation in degrees. Default is ``0``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: get_instances(name: Optional[str] = None, pid: Optional[int] = None, definition_name: Optional[str] = None, net_name: Optional[Union[str, List[str]]] = None, component_reference_designator: Optional[str] = None, component_pin: Optional[str] = None) -> List[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]

      Get padstack instances by search criteria.

      Parameters
      ----------
      name : str, optional
          Instance name.
      pid : int, optional
          Database ID.
      definition_name : str or list, optional
          Padstack definition name(s).
      net_name : str or list, optional
          Net name(s).
      component_reference_designator : str or list, optional
          Component reference designator(s).
      component_pin : str or list, optional
          Component pin number(s).

      Returns
      -------
      list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          List of matching padstack instances.



   .. py:method:: get_reference_pins(positive_pin: Union[int, str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance], reference_net: str = 'gnd', search_radius: float = 0.005, max_limit: int = 0, component_only: bool = True, pinlist_position: dict = None) -> List[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]

      Find reference pins near a specified pin.

      Parameters
      ----------
      positive_pin : :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
          Target pin.
      reference_net : str, optional
          Reference net name. Default is ``"gnd"``.
      search_radius : float, optional
          Search radius in meters. Default is ``5e-3`` (5 mm).
      max_limit : int, optional
          Maximum number of pins to return. Default is ``0`` (no limit).
      component_only : bool, optional
          Whether to search only in component pins. Default is ``True``.

      Returns
      -------
      list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
          List of reference pins.



   .. py:method:: get_padstack_instances_rtree_index(nets: Optional[Union[str, List[str]]] = None) -> rtree.index.Index

      Returns padstack instances Rtree index.

      Parameters
      ----------
      nets : str or list, optional
          net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.

      Returns
      -------
      Rtree index object.




   .. py:method:: get_padstack_instances_id_intersecting_polygon(points: List[Tuple[float, float]], nets: Optional[Union[str, List[str]]] = None, padstack_instances_index: Optional[Dict[int, Tuple[float, float]]] = None) -> List[int]

      Returns the list of padstack instances ID intersecting a given bounding box and nets.

      Parameters
      ----------
      points : tuple or list.
          bounding box, [x1, y1, x2, y2]
      nets : str or list, optional
          net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.
      padstack_instances_index : optional, Rtree object.
          Can be provided optionally to prevent computing padstack instances Rtree index again.

      Returns
      -------
      List[int]
          List of padstack instances ID intersecting the bounding box.



   .. py:method:: get_padstack_instances_intersecting_bounding_box(bounding_box: List[float], nets: Optional[Union[str, List[str]]] = None, padstack_instances_index: Optional[rtree.index.Index] = None) -> List[int]

      Returns the list of padstack instances ID intersecting a given bounding box and nets.
      Parameters
      ----------
      bounding_box : tuple or list.
          bounding box, [x1, y1, x2, y2]
      nets : str or list, optional
          net name of list of nets name applying filtering on pad-stack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.
      padstack_instances_index : optional, Rtree object.
          Can be provided optionally to prevent computing padstack instances Rtree index again.
      Returns
      -------
      List of padstack instances ID intersecting the bounding box.



   .. py:method:: merge_via_along_lines(net_name: str = 'GND', distance_threshold: float = 0.005, minimum_via_number: int = 6, selected_angles: Optional[List[float]] = None, padstack_instances_id: Optional[List[int]] = None) -> List[str]

      Replace padstack instances along lines into a single polygon.

      Detect all pad-stack instances that are placed along lines and replace them by a single polygon based one
      forming a wall shape. This method is designed to simplify meshing on via fence usually added to shield RF traces
      on PCB.

      Parameters
      ----------
      net_name : str
          Net name used for detected pad-stack instances. Default value is ``"GND"``.

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
          List of pad-stack instances ID's to include. If `None`, the algorithm will scan all pad-stack
          instances belonging to the specified net. Default value is `None`.

      Returns
      -------
      List[int], list of created pad-stack instances id.




   .. py:method:: merge_via(contour_boxes: List[List[float]], net_filter: Optional[Union[str, List[str]]] = None, start_layer: Optional[str] = None, stop_layer: Optional[str] = None) -> List[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]

      Evaluate pad-stack instances included on the provided point list and replace all by single instance.

      Parameters
      ----------
      contour_boxes : List[List[List[float, float]]]
          Nested list of polygon with points [x,y].
      net_filter : optional
          List[str: net_name] apply a net filter, nets included in the filter are excluded from the via merge.
      start_layer : optional, str
          Pad-stack instance start layer, if `None` the top layer is selected.
      stop_layer : optional, str
          Pad-stack instance stop layer, if `None` the bottom layer is selected.

      Return
      ------
      List[str], list of created pad-stack instances ID.




   .. py:method:: reduce_via_in_bounding_box(bounding_box: List[float], x_samples: int, y_samples: int, nets: Optional[Union[str, List[str]]] = None) -> bool

      reduce the number of vias intersecting bounding box and nets by x and y samples.

      Parameters
      ----------
      bounding_box : tuple or list.
          bounding box, [x1, y1, x2, y2]
      x_samples : int
      y_samples : int
      nets : str or list, optional
          net name of list of nets name applying filtering on pad-stack instances selection. If ``None`` is provided
          all instances are included in the index. Default value is ``None``.

      Returns
      -------
      bool
          ``True`` when succeeded ``False`` when failed.



   .. py:method:: dbscan(padstack: Dict[int, List[float]], max_distance: float = 0.001, min_samples: int = 5) -> Dict[int, List[int]]
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




