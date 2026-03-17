src.pyedb.grpc.database.modeler
===============================

.. py:module:: src.pyedb.grpc.database.modeler

.. autoapi-nested-parse::

   This module contains these classes: `EdbLayout` and `Shape`.



Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.modeler.Modeler


Functions
---------

.. autoapisummary::

   src.pyedb.grpc.database.modeler.normalize_pairs


Module Contents
---------------

.. py:function:: normalize_pairs(points: Iterable[float]) -> List[List[float]]

   Convert any reasonable point description into [[x1, y1], [x2, y2], …]


.. py:class:: Modeler(p_edb)

   Bases: :py:obj:`object`


   Manages EDB methods for primitives management accessible from `Edb.modeler`.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_layout = edbapp.modeler


   .. py:method:: clear_cache()

      Force reload of all primitives and reset indexes.



   .. py:property:: primitives

      Primitives.

      .. deprecated:: 0.70.0
              Use :attr:`edb.layout.primitives` instead.

      Returns
      -------
      list of :class:`pyedb.grpc.database.primitives.Primitive`
          List of primitives.



   .. py:property:: primitives_by_layer


   .. py:method:: get_primitive(primitive_id: int, edb_uid=True) -> Optional[pyedb.grpc.database.primitive.primitive.Primitive]

      Retrieve primitive by ID.

      Parameters
      ----------
      primitive_id : int
          Primitive ID.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive` or bool
          Primitive object if found, False otherwise.



   .. py:property:: polygons_by_layer
      :type: Dict[str, List[pyedb.grpc.database.primitive.primitive.Primitive]]


      Primitives organized by layer names.

      Returns
      -------
      dict
          Dictionary where keys are layer names and values are lists of polygons.



   .. py:property:: rectangles
      :type: List[Union[pyedb.grpc.database.primitive.rectangle.Rectangle, pyedb.grpc.database.primitive.primitive.Primitive]]


      All rectangle primitives.

      Returns
      -------
      list
          List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Rectangle` objects.



   .. py:property:: circles
      :type: List[Union[pyedb.grpc.database.primitive.circle.Circle, pyedb.grpc.database.primitive.primitive.Primitive]]


      All circle primitives.

      Returns
      -------
      list
          List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Circle` objects.



   .. py:property:: paths
      :type: List[Union[pyedb.grpc.database.primitive.path.Path, pyedb.grpc.database.primitive.primitive.Primitive]]


      All path primitives.

      Returns
      -------
      list
          List of :class:`pyedb.dotnet.database.edb_data.primitives_data.Path` objects.



   .. py:property:: polygons
      :type: List[Union[pyedb.grpc.database.primitive.polygon.Polygon, pyedb.grpc.database.primitive.primitive.Primitive]]


      All polygon primitives.

      Returns
      -------
      list
          List of :class:`pyedb.grpc.database.primitive.polygon.Polygon` objects.



   .. py:method:: get_polygons_by_layer(layer_name: str, net_list: Optional[List[str]] = None) -> List[pyedb.grpc.database.primitive.primitive.Primitive]

      Retrieve polygons by layer.

      Parameters
      ----------
      layer_name : str
          Layer name.
      net_list : list, optional
          List of net names to filter by.

      Returns
      -------
      list
          List of polygon objects.



   .. py:method:: get_primitive_by_layer_and_point(point: Optional[List[float]] = None, layer: Optional[Union[str, List[str]]] = None, nets: Optional[Union[str, List[str]]] = None) -> List[pyedb.grpc.database.primitive.primitive.Primitive]

      Get primitive at specified point on layer.

      Parameters
      ----------
      point : list, optional
          [x, y] coordinate point.
      layer : str or list, optional
          Layer name(s) to filter by.
      nets : str or list, optional
          Net name(s) to filter by.

      Returns
      -------
      list
          List of primitive objects at the point.

      Raises
      ------
      ValueError
          If point is invalid.



   .. py:method:: get_polygon_bounding_box(polygon: pyedb.grpc.database.primitive.primitive.Primitive) -> List[float]

      Get bounding box of polygon.

      Parameters
      ----------
      polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Polygon primitive.

      Returns
      -------
      list
          Bounding box coordinates [min_x, min_y, max_x, max_y].



   .. py:method:: get_polygon_points(polygon) -> List[List[float]]

      Get points defining a polygon.

      Parameters
      ----------
      polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Polygon primitive.

      Returns
      -------
      list
          List of point coordinates.



   .. py:method:: parametrize_polygon(polygon, selection_polygon, offset_name='offsetx', origin=None) -> bool

      Parametrize polygon points based on another polygon.

      Parameters
      ----------
      polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Polygon to parametrize.
      selection_polygon : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Polygon used for selection.
      offset_name : str, optional
          Name of offset parameter.
      origin : list, optional
          [x, y] origin point for vector calculation.

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: create_trace(path_list: Union[Iterable[float], ansys.edb.core.geometry.polygon_data.PolygonData], layer_name: str, width: float = 1, net_name: str = '', start_cap_style: str = 'Round', end_cap_style: str = 'Round', corner_style: str = 'Round') -> Optional[pyedb.grpc.database.primitive.primitive.Primitive]

      Create trace path.

      Parameters
      ----------
      path_list : Iterable
          List of points [x,y] or [[x, y], ...]
          or [(x, y)...].
      layer_name : str
          Layer name.
      width : float, optional
          Trace width.
      net_name : str, optional
          Associated net name.
      start_cap_style : str, optional
          Start cap style ("Round", "Extended", "Flat").
      end_cap_style : str, optional
          End cap style ("Round", "Extended", "Flat").
      corner_style : str, optional
          Corner style ("Round", "Sharp", "Mitered").

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Path` or bool
          Path object if created, False otherwise.



   .. py:method:: create_polygon(points: Union[List[List[float]], ansys.edb.core.geometry.polygon_data.PolygonData], layer_name: str, voids: Optional[List[Any]] = [], net_name: str = '') -> Union[Optional[pyedb.grpc.database.primitive.primitive.Primitive], bool]

      Create polygon primitive.

      Parameters
      ----------
      points : list or :class:`ansys.edb.core.geometry.polygon_data.PolygonData`
          Polygon points or PolygonData object.
      layer_name : str
          Layer name.
      voids : list, optional
          List of void shapes or points.
      net_name : str, optional
          Associated net name.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Polygon` or bool
          Polygon object if created, False otherwise.



   .. py:method:: create_rectangle(layer_name: str, net_name: str = '', lower_left_point: str = '', upper_right_point: str = '', center_point: str = '', width: Union[str, float] = '', height: Union[str, float] = '', representation_type: str = 'lower_left_upper_right', corner_radius: str = '0mm', rotation: str = '0deg') -> Optional[pyedb.grpc.database.primitive.primitive.Primitive]

      Create rectangle primitive.

      Parameters
      ----------
      layer_name : str
          Layer name.
      net_name : str, optional
          Associated net name.
      lower_left_point : list, optional
          [x,y] lower left point.
      upper_right_point : list, optional
          [x,y] upper right point.
      center_point : list, optional
          [x,y] center point.
      width : str or float, optional
          Rectangle width.
      height : str or float, optional
          Rectangle height.
      representation_type : str, optional
          "lower_left_upper_right" or "center_width_height".
      corner_radius : str, optional
          Corner radius with units.
      rotation : str, optional
          Rotation angle with units.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Rectangle` or bool
          Rectangle object if created, False otherwise.



   .. py:method:: create_circle(layer_name: str, x: Union[float, str], y: Union[float, str], radius: Union[float, str], net_name: str = '') -> Optional[pyedb.grpc.database.primitive.primitive.Primitive]

      Create circle primitive.

      Parameters
      ----------
      layer_name : str
          Layer name.
      x : float
          Center x-coordinate.
      y : float
          Center y-coordinate.
      radius : float
          Circle radius.
      net_name : str, optional
          Associated net name.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Circle` or bool
          Circle object if created, False otherwise.



   .. py:method:: delete_primitives(net_names: Union[str, List[str]]) -> bool

      Delete primitives by net name(s).

      Parameters
      ----------
      net_names : str or list
          Net name(s).

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: get_primitives(net_name: Optional[str] = None, layer_name: Optional[str] = None, prim_type: Optional[str] = None, is_void: bool = False) -> List[pyedb.grpc.database.primitive.primitive.Primitive]

      Get primitives with filtering.

      Parameters
      ----------
      net_name : str, optional
          Net name filter.
      layer_name : str, optional
          Layer name filter.
      prim_type : str, optional
          Primitive type filter.
      is_void : bool, optional
          Void primitive filter.

      Returns
      -------
      list
          List of filtered primitives.



   .. py:method:: fix_circle_void_for_clipping() -> bool

      Fix circle void clipping issues.

      Returns
      -------
      bool
          True if changes made, False otherwise.



   .. py:method:: parametrize_trace_width(nets_name: Union[str, List[str]], layers_name: Optional[Union[str, List[str]]] = None, parameter_name: str = 'trace_width', variable_value: Optional[Union[float, str]] = None) -> bool

      Parametrize trace width.

      Parameters
      ----------
      nets_name : str or list
          Net name(s).
      layers_name : str or list, optional
          Layer name(s) filter.
      parameter_name : str, optional
          Parameter name prefix.
      variable_value : float or str, optional
          Initial parameter value.

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: unite_polygons_on_layer(layer_name: Optional[Union[str, List[str]]] = None, delete_padstack_gemometries: bool = False, net_names_list: Optional[List[str]] = None) -> bool

      Unite polygons on layer.

      Parameters
      ----------
      layer_name : str or list, optional
          Layer name(s) to process.
      delete_padstack_gemometries : bool, optional
          Whether to delete padstack geometries.
      net_names_list : list, optional
          Net names filter.

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: defeature_polygon(poly: pyedb.grpc.database.primitive.polygon.Polygon, tolerance: float = 0.001) -> bool

      Defeature polygon.

      Parameters
      ----------
      poly : :class:`pyedb.dotnet.database.edb_data.primitives_data.Polygon`
          Polygon to defeature.
      tolerance : float, optional
          Maximum surface deviation tolerance.

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: get_layout_statistics(evaluate_area: bool = False, net_list: Optional[List[str]] = None) -> pyedb.grpc.database.utility.layout_statistics.LayoutStatistics

      Get layout statistics.

      Parameters
      ----------
      evaluate_area : bool, optional
          Whether to compute metal area statistics.
      net_list : list, optional
          Net list for area computation.

      Returns
      -------
      :class:`LayoutStatistics`
          Layout statistics object.



   .. py:method:: create_bondwire(definition_name: str, placement_layer: str, width: Union[float, str], material: str, start_layer_name: str, start_x: Union[float, str], start_y: Union[float, str], end_layer_name: str, end_x: Union[float, str], end_y: Union[float, str], net: str, start_cell_instance_name: Optional[str] = None, end_cell_instance_name: Optional[str] = None, bondwire_type: str = 'jedec4') -> pyedb.grpc.database.primitive.bondwire.Bondwire

      Create bondwire.

      Parameters
      ----------
      definition_name : str
          Bondwire definition name.
      placement_layer : str
          Placement layer name.
      width : float or str
          Bondwire width.
      material : str
          Material name.
      start_layer_name : str
          Start layer name.
      start_x : float or str
          Start x-coordinate.
      start_y : float or str
          Start y-coordinate.
      end_layer_name : str
          End layer name.
      end_x : float or str
          End x-coordinate.
      end_y : float or str
          End y-coordinate.
      net : str
          Associated net name.
      start_cell_instance_name : str, optional
          Start cell instance name.
      end_cell_instance_name : str, optional
          End cell instance name.
      bondwire_type : str, optional
          Bondwire type ("jedec4", "jedec5", "apd").

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Bondwire` or bool
          Bondwire object if created, False otherwise.



   .. py:method:: create_pin_group(name: str, pins_by_id: Optional[List[int]] = None, pins_by_aedt_name: Optional[List[str]] = None, pins_by_name: Optional[List[str]] = None) -> bool

      Create pin group.

      Parameters
      ----------
      name : str
          Pin group name.
      pins_by_id : list, optional
          List of pin IDs.
      pins_by_aedt_name : list, optional
          List of pin AEDT names.
      pins_by_name : list, optional
          List of pin names.

      Returns
      -------
      :class:`pyedb.dotnet.database.siwave.pin_group.PinGroup` or bool
          PinGroup object if created, False otherwise.



   .. py:method:: add_void(shape: pyedb.grpc.database.primitive.primitive.Primitive, void_shape: Union[pyedb.grpc.database.primitive.primitive.Primitive, List[pyedb.grpc.database.primitive.primitive.Primitive]]) -> bool
      :staticmethod:


      Add void to shape.

      Parameters
      ----------
      shape : :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Main shape.
      void_shape : list or :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Void shape(s).

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: insert_layout_instance_on_layer(cell_name: str, placement_layer: str, rotation: Union[float, str] = 0, x: Union[float, str] = 0, y: Union[float, str] = 0, place_on_bottom: bool = False, local_origin_x: Optional[Union[float, str]] = 0, local_origin_y: Optional[Union[float, str]] = 0) -> Any

      Insert a layout instance into the active layout.

      Parameters
      ----------
      cell_name: str
          Name of the layout to insert.
      placement_layer: str
          Placement Layer.
      scaling : float
          Scale parameter.
      rotation : float or str
          Rotation angle, specified counter-clockwise in radians.
      mirror : bool
          Mirror about Y-axis.
      x : float or str
          X offset.
      y : float or str
          Y offset.
      place_on_bottom : bool
          Whether to place the layout instance on the bottom of the layer.
      local_origin_x: float or str
          Local origin X coordinate.
      local_origin_y: float or str
          Local origin Y coordinate.



   .. py:method:: insert_layout_instance_placement_3d(cell_name: Union[str, pyedb.grpc.database.primitive.path.Path], x: Union[float, str] = 0.0, y: Union[float, str] = 0.0, z: Union[float, str] = 0.0, rotation_x: Union[float, str] = 0.0, rotation_y: Union[float, str] = 0.0, rotation_z: Union[float, str] = 0.0, local_origin_x: Union[float, str] = 0.0, local_origin_y: Union[float, str] = 0.0, local_origin_z: Union[float, str] = 0.0) -> Any

      Insert a 3D component placement into the active layout.

      Parameters
      ----------
      cell_name: str
          Name of the layout to insert.
      x: float or str
          X coordinate.
      y: float or str
          Y coordinate.
      z: float or str
          Z coordinate.
      rotation_x: float or str
          Rotation angle around X-axis, specified counter-clockwise in radians.
      rotation_y: float or str
          Rotation angle around Y-axis, specified counter-clockwise in radians.
      rotation_z: float or str
          Rotation angle around Z-axis, specified counter-clockwise in radians.
      local_origin_x: float or str
          Local origin X coordinate.
      local_origin_y: float or str
          Local origin Y coordinate.
      local_origin_z: float or str
          Local origin Z coordinate.



   .. py:method:: insert_3d_component_placement_3d(a3dcomp_path: Union[str, pyedb.grpc.database.primitive.path.Path], x: Union[float, str] = 0.0, y: Union[float, str] = 0.0, z: Union[float, str] = 0.0, rotation_x: Union[float, str] = 0.0, rotation_y: Union[float, str] = 0.0, rotation_z: Union[float, str] = 0.0, local_origin_x: Union[float, str] = 0.0, local_origin_y: Union[float, str] = 0.0, local_origin_z: Union[float, str] = 0.0) -> Any

      Insert a 3D component placement into the active layout.

      Parameters
      ----------
      a3dcomp_path: str or Path
          File path to the 3D component.
      x: float or str
          X coordinate.
      y: float or str
          Y coordinate.
      z: float or str
          Z coordinate.
      rotation_x: float or str
          Rotation angle around X-axis, specified counter-clockwise in radians.
      rotation_y: float or str
          Rotation angle around Y-axis, specified counter-clockwise in radians.
      rotation_z: float or str
          Rotation angle around Z-axis, specified counter-clockwise in radians.
      local_origin_x: float or str
          Local origin X coordinate.
      local_origin_y: float or str
          Local origin Y coordinate.
      local_origin_z: float or str
          Local origin Z coordinate.



   .. py:method:: insert_3d_component_on_layer(a3dcomp_path: Union[str, pyedb.grpc.database.primitive.path.Path], placement_layer: str, rotation: Union[float, str] = 0, x: Union[float, str] = 0, y: Union[float, str] = 0, place_on_bottom: bool = False, local_origin_x: Optional[Union[float, str]] = 0, local_origin_y: Optional[Union[float, str]] = 0, local_origin_z: Optional[Union[float, str]] = 0) -> Any

      Insert a layout instance into the active layout.

      Parameters
      ----------
      a3dcomp_path: str or Path
          File path to the 3D component.
      placement_layer: str
          Placement Layer.
      rotation : float or str
          Rotation angle, specified counter-clockwise in radians.
      x : float or str
          X offset.
      y : float or str
          Y offset.
      place_on_bottom : bool
          Whether to place the layout instance on the bottom of the layer.
      local_origin_x: float or str
          Local origin X coordinate.
      local_origin_y: float or str
          Local origin Y coordinate.
      local_origin_z: float or str
          Local origin Z coordinate.



