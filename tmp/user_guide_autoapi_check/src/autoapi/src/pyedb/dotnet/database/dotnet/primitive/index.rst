src.pyedb.dotnet.database.dotnet.primitive
==========================================

.. py:module:: src.pyedb.dotnet.database.dotnet.primitive

.. autoapi-nested-parse::

   Primitive.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.dotnet.primitive.PrimitiveDotNet
   src.pyedb.dotnet.database.dotnet.primitive.RectangleDotNet
   src.pyedb.dotnet.database.dotnet.primitive.CircleDotNet
   src.pyedb.dotnet.database.dotnet.primitive.TextDotNet
   src.pyedb.dotnet.database.dotnet.primitive.PathDotNet
   src.pyedb.dotnet.database.dotnet.primitive.BondwireDotNet
   src.pyedb.dotnet.database.dotnet.primitive.PadstackInstanceDotNet
   src.pyedb.dotnet.database.dotnet.primitive.BoardBendDef


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.dotnet.primitive.cast


Module Contents
---------------

.. py:function:: cast(api, prim_object)

   Cast the primitive object to correct concrete type.

   Returns
   -------
   PrimitiveDotNet


.. py:class:: PrimitiveDotNet(api, prim_object=None)

   Base class representing primitive objects.


   .. py:attribute:: api


   .. py:attribute:: core


   .. py:attribute:: prim_obj
      :value: None



   .. py:property:: api_class


   .. py:property:: api_object


   .. py:property:: path


   .. py:property:: rectangle


   .. py:property:: circle


   .. py:property:: text


   .. py:property:: bondwire


   .. py:property:: padstack_instance


   .. py:property:: net


   .. py:property:: primitive_type

      :class:`PrimitiveType`: Primitive type of the primitive.

      Read-Only.



   .. py:method:: add_void(point_list)

      Add a void to current primitive.

      Parameters
      ----------
      point_list : list or :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`             or EDB Primitive Object. Point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.

      Returns
      -------
      bool
          ``True`` if successful, either  ``False``.



   .. py:method:: set_hfss_prop(material, solve_inside)

      Set HFSS properties.

      Parameters
      ----------
      material : str
          Material property name to be set.
      solve_inside : bool
          Whether to do solve inside.



   .. py:property:: layer_name
      :type: str


      :str: Layer name that the primitive object is on.



   .. py:property:: layer

      :class:`Layer <ansys.edb.layer.Layer>`: Layer that the primitive object is on.



   .. py:property:: is_negative

      :obj:`bool`: If the primitive is negative.



   .. py:property:: is_void

      :obj:`bool`: If a primitive is a void.



   .. py:property:: has_voids

      :obj:`bool`: If a primitive has voids inside.

      Read-Only.



   .. py:property:: voids

      :obj:`list` of :class:`Primitive <ansys.edb.primitive.Primitive>`: List of void        primitive objects inside the primitive.

      Read-Only.



   .. py:property:: owner

      :class:`Primitive <ansys.edb.primitive.Primitive>`: Owner of the primitive object.

      Read-Only.



   .. py:property:: is_parameterized

      :obj:`bool`: Primitive's parametrization.

      Read-Only.



   .. py:method:: get_hfss_prop()

      Get HFSS properties.

      Returns
      -------
      material : str
          Material property name.
      solve_inside : bool
          If solve inside.



   .. py:method:: remove_hfss_prop()

      Remove HFSS properties.



   .. py:property:: is_zone_primitive

      :obj:`bool`: If primitive object is a zone.

      Read-Only.



   .. py:property:: can_be_zone_primitive

      :obj:`bool`: If a primitive can be a zone.

      Read-Only.



   .. py:method:: make_zone_primitive(zone_id)

      Make primitive a zone primitive with a zone specified by the provided id.

      Parameters
      ----------
      zone_id : int
          Id of zone primitive will use.




   .. py:method:: points(arc_segments=6)

      Return the list of points with arcs converted to segments.

      Parameters
      ----------
      arc_segments : int
          Number of facets to convert an arc. Default is `6`.

      Returns
      -------
      tuple
          The tuple contains 2 lists made of X and Y points coordinates.



   .. py:method:: points_raw()

      Return a list of Edb points.

      Returns
      -------
      list
          Edb Points.



   .. py:method:: expand(offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001)

      Expand the polygon shape by an absolute value in all direction.
      Offset can be negative for negative expansion.

      Parameters
      ----------
      offset : float, optional
          Offset value in meters.
      tolerance : float, optional
          Tolerance in meters.
      round_corners : bool, optional
          Whether to round corners or not.
          If True, use rounded corners in the expansion otherwise use straight edges (can be degenerate).
      maximum_corner_extension : float, optional
          The maximum corner extension (when round corners are not used) at which point the corner is clipped.



   .. py:method:: scale(factor, center=None)

      Scales the polygon relative to a center point by a factor.

      Parameters
      ----------
      factor : float
          Scaling factor.
      center : List of float or str [x,y], optional
          If None scaling is done from polygon center.

      Returns
      -------
      bool
         ``True`` when successful, ``False`` when failed.



.. py:class:: RectangleDotNet(api, prim_obj=None)

   Bases: :py:obj:`PrimitiveDotNet`


   Class representing a rectangle object.


   .. py:method:: create(layout, layer, net, rep_type, param1, param2, param3, param4, corner_rad, rotation)

      Create a rectangle.

      Parameters
      ----------
      layout : :class:`Layout <ansys.edb.layout.Layout>`
          Layout this rectangle will be in.
      layer : str or :class:`Layer <ansys.edb.layer.Layer>`
          Layer this rectangle will be on.
      net : str or :class:`Net <ansys.edb.net.Net>` or None
          Net this rectangle will have.
      rep_type : :class:`RectangleRepresentationType`
          Type that defines given parameters meaning.
      param1 : :class:`Value <ansys.edb.utility.Value>`
          X value of lower left point or center point.
      param2 : :class:`Value <ansys.edb.utility.Value>`
          Y value of lower left point or center point.
      param3 : :class:`Value <ansys.edb.utility.Value>`
          X value of upper right point or width.
      param4 : :class:`Value <ansys.edb.utility.Value>`
          Y value of upper right point or height.
      corner_rad : :class:`Value <ansys.edb.utility.Value>`
          Corner radius.
      rotation : :class:`Value <ansys.edb.utility.Value>`
          Rotation.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.primitive.RectangleDotNet`

          Rectangle that was created.



   .. py:method:: get_parameters()

      Get coordinates parameters.

      Returns
      -------
      tuple[
          :class:`RectangleRepresentationType`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`
      ]

          Returns a tuple of the following format:

          **(representation_type, parameter1, parameter2, parameter3, parameter4, corner_radius, rotation)**

          **representation_type** : Type that defines given parameters meaning.

          **parameter1** : X value of lower left point or center point.

          **parameter2** : Y value of lower left point or center point.

          **parameter3** : X value of upper right point or width.

          **parameter4** : Y value of upper right point or height.

          **corner_radius** : Corner radius.

          **rotation** : Rotation.



   .. py:method:: set_parameters(rep_type, param1, param2, param3, param4, corner_rad, rotation)

      Set coordinates parameters.

      Parameters
      ----------
      rep_type : :class:`RectangleRepresentationType`
          Type that defines given parameters meaning.
      param1 : :class:`Value <ansys.edb.utility.Value>`
          X value of lower left point or center point.
      param2 : :class:`Value <ansys.edb.utility.Value>`
          Y value of lower left point or center point.
      param3 : :class:`Value <ansys.edb.utility.Value>`
          X value of upper right point or width.
      param4 : :class:`Value <ansys.edb.utility.Value>`
          Y value of upper right point or height.
      corner_rad : :class:`Value <ansys.edb.utility.Value>`
          Corner radius.
      rotation : :class:`Value <ansys.edb.utility.Value>`
          Rotation.



   .. py:property:: can_be_zone_primitive

      :obj:`bool`: If a rectangle can be a zone.

      Read-Only.



.. py:class:: CircleDotNet(api, prim_obj=None)

   Bases: :py:obj:`PrimitiveDotNet`


   Class representing a circle object.


   .. py:method:: create(layout, layer, net, center_x, center_y, radius)

      Create a circle.

      Parameters
      ----------
      layout: :class:`Layout <ansys.edb.layout.Layout>`
          Layout this circle will be in.
      layer: str or :class:`Layer <ansys.edb.layer.Layer>`
          Layer this circle will be on.
      net: str or :class:`Net <ansys.edb.net.Net>` or None
          Net this circle will have.
      center_x: :class:`Value <ansys.edb.utility.Value>`
          X value of center point.
      center_y: :class:`Value <ansys.edb.utility.Value>`
          Y value of center point.
      radius: :class:`Value <ansys.edb.utility.Value>`
          Radius value of the circle.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.primitive.CircleDotNet`
          Circle object created.



   .. py:method:: get_parameters()

      Get parameters of a circle.

      Returns
      -------
      tuple[
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`
      ]

          Returns a tuple of the following format:

          **(center_x, center_y, radius)**

          **center_x** : X value of center point.

          **center_y** : Y value of center point.

          **radius** : Radius value of the circle.



   .. py:method:: set_parameters(center_x, center_y, radius)

      Set parameters of a circle.

       Parameters
       ----------
      center_x: :class:`Value <ansys.edb.utility.Value>`
          X value of center point.
      center_y: :class:`Value <ansys.edb.utility.Value>`
          Y value of center point.
      radius: :class:`Value <ansys.edb.utility.Value>`
          Radius value of the circle.



   .. py:method:: get_polygon_data()

      :class:`PolygonData <ansys.edb.geometry.PolygonData>`: Polygon data object of the Circle object.



   .. py:method:: can_be_zone_primitive()

      :obj:`bool`: If a circle can be a zone.



   .. py:method:: expand(offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001)

      Expand the polygon shape by an absolute value in all direction.
      Offset can be negative for negative expansion.

      Parameters
      ----------
      offset : float, optional
          Offset value in meters.
      tolerance : float, optional
          Tolerance in meters. Ignored for Circle and Path.
      round_corners : bool, optional
          Whether to round corners or not.
          If True, use rounded corners in the expansion otherwise use straight edges (can be degenerate).
           Ignored for Circle and Path.
      maximum_corner_extension : float, optional
          The maximum corner extension (when round corners are not used) at which point the corner is clipped.
           Ignored for Circle and Path.



.. py:class:: TextDotNet(api, prim_obj=None)

   Bases: :py:obj:`PrimitiveDotNet`


   Class representing a text object.


   .. py:method:: create(layout, layer, center_x, center_y, text)

      Create a text object.

      Parameters
      ----------
      layout: :class:`Layout <ansys.edb.layout.Layout>`
          Layout this text will be in.
      layer: str or Layer
          Layer this text will be on.
      center_x: :class:`Value <ansys.edb.utility.Value>`
          X value of center point.
      center_y: :class:`Value <ansys.edb.utility.Value>`
          Y value of center point.
      text: str
          Text string.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.primitive.TextDotNet`
          The text Object that was created.



   .. py:method:: get_text_data()

      Get the text data of a text.

      Returns
      -------
      tuple[
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          str
      ]
          Returns a tuple of the following format:

          **(center_x, center_y, text)**

          **center_x** : X value of center point.

          **center_y** : Y value of center point.

          **radius** : Text object's String value.



   .. py:method:: set_text_data(center_x, center_y, text)

      Set the text data of a text.

      Parameters
      ----------
      center_x: :class:`Value <ansys.edb.utility.Value>`
          X value of center point.
      center_y: :class:`Value <ansys.edb.utility.Value>`
          Y value of center point.
      text: str
          Text object's String value.



.. py:class:: PathDotNet(api, prim_obj=None)

   Bases: :py:obj:`PrimitiveDotNet`


   Class representing a path object.


   .. py:method:: create(layout, layer, net, width, end_cap1, end_cap2, corner_style, points)

      Create a path.

      Parameters
      ----------
      layout : :class:`Layout <ansys.edb.layout.Layout>`
          Layout this Path will be in.
      layer : str or :class:`Layer <ansys.edb.layer.Layer>`
          Layer this Path will be on.
      net : str or :class:`Net <ansys.edb.net.Net>` or None
          Net this Path will have.
      width: :class:`Value <ansys.edb.utility.Value>`
          Path width.
      end_cap1: :class:`PathEndCapType`
          End cap style of path start end cap.
      end_cap2: :class:`PathEndCapType`
          End cap style of path end end cap.
      corner_style: :class:`PathCornerType`
          Corner style.
      points : :class:`PolygonData <ansys.edb.geometry.PolygonData>` or center line point list.
          Centerline polygonData to set.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.primitive.PathDotNet`
          Path object created.



   .. py:property:: center_line

      :class:`PolygonData <ansys.edb.geometry.PolygonData>`: Center line for this Path.



   .. py:property:: get_clip_info

      Get data used to clip the path.

      Returns
      -------
      tuple[:class:`PolygonData <ansys.edb.geometry.PolygonData>`, bool]

          Returns a tuple of the following format:

          **(clipping_poly, keep_inside)**

          **clipping_poly** : PolygonData used to clip the path.

          **keep_inside** : Indicates whether the part of the path inside the polygon is preserved.



   .. py:property:: corner_style

      :class:`PathCornerType`: Path's corner style.



   .. py:property:: width

      :class:`Value <ansys.edb.utility.Value>`: Path width.



   .. py:property:: miter_ratio

      :class:`Value <ansys.edb.utility.Value>`: Miter ratio.



   .. py:property:: can_be_zone_primitive

      :obj:`bool`: If a path can be a zone.

      Read-Only.



   .. py:method:: expand(offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001)

      Expand the polygon shape by an absolute value in all direction.
      Offset can be negative for negative expansion.

      Parameters
      ----------
      offset : float, optional
          Offset value in meters.
      tolerance : float, optional
          Tolerance in meters. Ignored for Circle and Path.
      round_corners : bool, optional
          Whether to round corners or not.
          If True, use rounded corners in the expansion otherwise use straight edges (can be degenerate).
           Ignored for Circle and Path.
      maximum_corner_extension : float, optional
          The maximum corner extension (when round corners are not used) at which point the corner is clipped.
           Ignored for Circle and Path.



.. py:class:: BondwireDotNet(api, prim_obj=None)

   Bases: :py:obj:`PrimitiveDotNet`


   Class representing a bondwire object.


   .. py:method:: create(layout, bondwire_type, definition_name, placement_layer, width, material, start_context, start_layer_name, start_x, start_y, end_context, end_layer_name, end_x, end_y, net)

      Create a bondwire object.

      Parameters
      ----------
      layout : :class:`Layout <ansys.edb.layout.Layout>`
          Layout this bondwire will be in.
      bondwire_type : :class:`BondwireType`
          Type of bondwire: kAPDBondWire or kJDECBondWire types.
      definition_name : str
          Bondwire definition name.
      placement_layer : str
          Layer name this bondwire will be on.
      width : :class:`Value <ansys.edb.utility.Value>`
          Bondwire width.
      material : str
          Bondwire material name.
      start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          Start context: None means top level.
      start_layer_name : str
          Name of start layer.
      start_x : :class:`Value <ansys.edb.utility.Value>`
          X value of start point.
      start_y : :class:`Value <ansys.edb.utility.Value>`
          Y value of start point.
      end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          End context: None means top level.
      end_layer_name : str
          Name of end layer.
      end_x : :class:`Value <ansys.edb.utility.Value>`
          X value of end point.
      end_y : :class:`Value <ansys.edb.utility.Value>`
          Y value of end point.
      net : str or :class:`Net <ansys.edb.net.Net>` or None
          Net of the Bondwire.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.primitive.BondwireDotNet`
          Bondwire object created.



   .. py:method:: get_material(evaluated=True)

      Get material of the bondwire.

      Parameters
      ----------
      evaluated : bool, optional
          True if an evaluated material name is wanted.

      Returns
      -------
      str
          Material name.



   .. py:method:: set_material(material)

      Set the material of a bondwire.

      Parameters
      ----------
      material : str
          Material name.



   .. py:property:: type

      :class:`BondwireType`: Bondwire-type of a bondwire object.



   .. py:property:: cross_section_type

      :class:`BondwireCrossSectionType`: Bondwire-cross-section-type of a bondwire object.



   .. py:property:: cross_section_height

      :class:`Value <ansys.edb.utility.Value>`: Bondwire-cross-section height of a bondwire object.



   .. py:method:: get_definition_name(evaluated=True)

      Get definition name of a bondwire object.

      Parameters
      ----------
      evaluated : bool, optional
          True if an evaluated (in variable namespace) material name is wanted.

      Returns
      -------
      str
          Bondwire name.



   .. py:method:: set_definition_name(definition_name)

      Set the definition name of a bondwire.

      Parameters
      ----------
      definition_name : str
          Bondwire name to be set.



   .. py:method:: get_traj()

      Get trajectory parameters of a bondwire object.

      Returns
      -------
      tuple[
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`
      ]

          Returns a tuple of the following format:

          **(x1, y1, x2, y2)**

          **x1** : X value of the start point.

          **y1** : Y value of the start point.

          **x1** : X value of the end point.

          **y1** : Y value of the end point.



   .. py:method:: set_traj(x1, y1, x2, y2)

      Set the parameters of the trajectory of a bondwire.

      Parameters
      ----------
      x1 : :class:`Value <ansys.edb.utility.Value>`
          X value of the start point.
      y1 : :class:`Value <ansys.edb.utility.Value>`
          Y value of the start point.
      x2 : :class:`Value <ansys.edb.utility.Value>`
          X value of the end point.
      y2 : :class:`Value <ansys.edb.utility.Value>`
          Y value of the end point.



   .. py:property:: width

      :class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object.



   .. py:method:: get_start_elevation(start_context)

      Get the start elevation layer of a bondwire object.

      Parameters
      ----------
      start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          Start cell context of the bondwire.

      Returns
      -------
      :class:`Layer <ansys.edb.layer.Layer>`
          Start context of the bondwire.



   .. py:method:: set_start_elevation(start_context, layer)

      Set the start elevation of a bondwire.

      Parameters
      ----------
      start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          Start cell context of the bondwire. None means top level.
      layer : str or :class:`Layer <ansys.edb.layer.Layer>`
          Start layer of the bondwire.



   .. py:method:: get_end_elevation(end_context)

      Get the end elevation layer of a bondwire object.

      Parameters
      ----------
      end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          End cell context of the bondwire.

      Returns
      -------
      :class:`Layer <ansys.edb.layer.Layer>`
          End context of the bondwire.



   .. py:method:: set_end_elevation(end_context, layer)

      Set the end elevation of a bondwire.

      Parameters
      ----------
      end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          End cell context of the bondwire. None means top level.
      layer : str or :class:`Layer <ansys.edb.layer.Layer>`
          End layer of the bondwire.



.. py:class:: PadstackInstanceDotNet(api, prim_obj=None)

   Bases: :py:obj:`PrimitiveDotNet`


   Class representing a Padstack Instance object.


   .. py:method:: create(layout, net, name, padstack_def, point, rotation, top_layer, bottom_layer, solder_ball_layer, layer_map)

      Create a PadstackInstance object.

      Parameters
      ----------
      layout : :class:`Layout <ansys.edb.layout.Layout>`
          Layout this padstack instance will be in.
      net : :class:`Net <ansys.edb.net.Net>`
          Net of this padstack instance.
      name : str
          Name of padstack instance.
      padstack_def : PadstackDef
          Padstack definition of this padstack instance.
      rotation : :class:`Value <ansys.edb.utility.Value>`
          Rotation of this padstack instance.
      top_layer : :class:`Layer <ansys.edb.layer.Layer>`
          Top layer of this padstack instance.
      bottom_layer : :class:`Layer <ansys.edb.layer.Layer>`
          Bottom layer of this padstack instance.
      solder_ball_layer : :class:`Layer <ansys.edb.layer.Layer>`
          Solder ball layer of this padstack instance, or None for none.
      layer_map : :class:`LayerMap <ansys.edb.utility.LayerMap>`
          Layer map of this padstack instance. None or empty means do auto-mapping.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.primitive.PadstackInstanceDotNet`
          Padstack instance object created.



   .. py:method:: get_hole_overrides()


   .. py:property:: padstack_def

      :class:`PadstackDef <ansys.edb.definition.padstack_def>`: PadstackDef of a Padstack Instance.



   .. py:property:: name

      :obj:`str`: Name of a Padstack Instance.



   .. py:method:: get_position_and_rotation()

      Get the position and rotation of a Padstack Instance.

      Returns
      -------
      tuple[
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`
      ]

          Returns a tuple of the following format:

          **(x, y, rotation)**

          **x** : X coordinate.

          **y** : Y coordinate.

          **rotation** : Rotation in radians.



   .. py:method:: set_position_and_rotation(x, y, rotation)

      Set the position and rotation of a Padstack Instance.

      Parameters
      ----------
      x : :class:`Value <ansys.edb.utility.Value>`
          x : X coordinate.
      y : :class:`Value <ansys.edb.utility.Value>`
          y : Y coordinate.
      rotation : :class:`Value <ansys.edb.utility.Value>`
          rotation : Rotation in radians.



   .. py:method:: get_layer_range()

      Get the top and bottom layers of a Padstack Instance.

      Returns
      -------
      tuple[
          :class:`Layer <ansys.edb.layer.Layer>`,
          :class:`Layer <ansys.edb.layer.Layer>`
      ]

          Returns a tuple of the following format:

          **(top_layer, bottom_layer)**

          **top_layer** : Top layer of the Padstack instance

          **bottom_layer** : Bottom layer of the Padstack instance



   .. py:method:: set_layer_range(top_layer, bottom_layer)

      Set the top and bottom layers of a Padstack Instance.

      Parameters
      ----------
      top_layer : :class:`Layer <ansys.edb.layer.Layer>`
          Top layer of the Padstack instance.
      bottom_layer : :class:`Layer <ansys.edb.layer.Layer>`
          Bottom layer of the Padstack instance.



   .. py:property:: solderball_layer

      :class:`Layer <ansys.edb.layer.Layer>`: SolderBall Layer of Padstack Instance.



   .. py:property:: layer_map

      :class:`LayerMap <ansys.edb.utility.LayerMap>`: Layer Map of the Padstack Instance.



   .. py:method:: set_hole_overrides(is_hole_override, hole_override)

      Set the hole overrides of Padstack Instance.

      Parameters
      ----------
      is_hole_override : bool
          If padstack instance is hole override.
      hole_override : :class:`Value <ansys.edb.utility.Value>`
          Hole override diameter of this padstack instance.



   .. py:property:: is_layout_pin

      :obj:`bool`: If padstack instance is layout pin.



   .. py:method:: get_back_drill_type(from_bottom)

      Get the back drill type of Padstack Instance.

      Parameters
      ----------
      from_bottom : bool
          True to get drill type from bottom.

      Returns
      -------
      :class:`BackDrillType`
          Back-Drill Type of padastack instance.



   .. py:method:: get_back_drill_by_layer(from_bottom)

      Get the back drill by layer.

      Parameters
      ----------
      from_bottom : bool
          True to get drill type from bottom.

      Returns
      -------
      tuple[
          bool,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`
      ]

          Returns a tuple of the following format:

          **(drill_to_layer, offset, diameter)**

          **drill_to_layer** : Layer drills to. If drill from top, drill stops at the upper elevation of the layer.            If from bottom, drill stops at the lower elevation of the layer.

          **offset** : Layer offset (or depth if layer is empty).

          **diameter** : Drilling diameter.



   .. py:method:: set_back_drill_by_layer(drill_to_layer, offset, diameter, from_bottom)

      Set the back drill by layer.

      Parameters
      ----------
      drill_to_layer : :class:`Layer <ansys.edb.layer.Layer>`
          Layer drills to. If drill from top, drill stops at the upper elevation of the layer.
          If from bottom, drill stops at the lower elevation of the layer.
      offset : :class:`Value <ansys.edb.utility.Value>`
          Layer offset (or depth if layer is empty).
      diameter : :class:`Value <ansys.edb.utility.Value>`
          Drilling diameter.
      from_bottom : bool
          True to set drill type from bottom.



   .. py:method:: get_back_drill_by_depth(from_bottom)

      Get the back drill by depth.

      Parameters
      ----------
      from_bottom : bool
          True to get drill type from bottom.

      Returns
      -------
      tuple[
          bool,
          :class:`Value <ansys.edb.utility.Value>`
      ]
          Returns a tuple of the following format:

          **(drill_depth, diameter)**

          **drill_depth** : Drilling depth, may not align with layer.

          **diameter** : Drilling diameter.



   .. py:method:: set_back_drill_by_depth(drill_depth, diameter, from_bottom)

      Set the back drill by Depth.

      Parameters
      ----------
      drill_depth : :class:`Value <ansys.edb.utility.Value>`
          Drilling depth, may not align with layer.
      diameter : :class:`Value <ansys.edb.utility.Value>`
          Drilling diameter.
      from_bottom : bool
          True to set drill type from bottom.



   .. py:method:: get_padstack_instance_terminal()

      :class:`TerminalInstance <ansys.edb.terminal.TerminalInstance>`: Padstack Instance's terminal.



   .. py:method:: is_in_pin_group(pin_group)

      Check if Padstack instance is in the Pin Group.

      Parameters
      ----------
      pin_group : :class:`PinGroup <ansys.edb.hierarchy.PinGroup>`
          Pin group to check if padstack instance is in.

      Returns
      -------
      bool
          True if padstack instance is in pin group.



   .. py:property:: pin_groups

      :obj:`list` of :class:`PinGroup <ansys.edb.hierarchy.PinGroup>`: Pin groups of Padstack instance object.

      Read-Only.



.. py:class:: BoardBendDef(api, prim_obj=None)

   Bases: :py:obj:`PrimitiveDotNet`


   Class representing board bending definitions.


   .. py:method:: create(zone_prim, bend_middle, bend_radius, bend_angle)

      Create a board bend definition.

      Parameters
      ----------
      zone_prim : :class:`Primitive <Primitive>`
          Zone primitive this board bend definition exists on.
      bend_middle : :term:`PointDataTuple`
          Tuple containing the starting and ending points of the line that represents the middle of the bend.
      bend_radius : :term:`ValueLike`
          Radius of the bend.
      bend_angle : :term:`ValueLike`
          Angle of the bend.

      Returns
      -------
      BoardBendDef
          BoardBendDef that was created.



   .. py:property:: boundary_primitive

      :class:`Primitive <Primitive>`: Zone primitive the board bend is placed on.

      Read-Only.



   .. py:property:: bend_middle

      :term:`PointDataTuple`: Tuple of the bend middle starting and ending points.



   .. py:property:: radius

      :term:`ValueLike`: Radius of the bend.



   .. py:property:: angle

      :term:`ValueLike`: Angle of the bend.



   .. py:property:: bent_regions

      :obj:`list` of :class:`PolygonData <ansys.edb.geometry.PolygonData>`: Bent region polygons.

          Collection of polygon data representing the areas bent by this bend definition.

      Read-Only.



