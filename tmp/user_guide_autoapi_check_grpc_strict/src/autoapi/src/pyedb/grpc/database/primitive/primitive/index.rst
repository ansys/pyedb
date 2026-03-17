src.pyedb.grpc.database.primitive.primitive
===========================================

.. py:module:: src.pyedb.grpc.database.primitive.primitive


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.primitive.layer_type_mapping


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.primitive.Primitive


Module Contents
---------------

.. py:data:: layer_type_mapping

.. py:class:: Primitive(pedb, core)

   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", version="2026.1", grpc=True)
   >>> edb_prim = edb.layout.primitives[0]


   .. py:attribute:: core


   .. py:property:: type
      :type: str


      Type of the primitive.

      Expected output is among ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

      Returns
      -------
      str



   .. py:property:: layout

      Layout object.

      Returns
      -------
      :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`




   .. py:property:: polygon_data

      Polygon data.

      Returns
      -------
      :class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`




   .. py:property:: object_instance

      Layout object instance.

      Returns
      -------
      :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`




   .. py:property:: net_name
      :type: str | None


      Net name.

      Returns
      -------
      str
          Net name.




   .. py:property:: layer_name
      :type: str


      Layer name.

      Returns
      -------
      str
          Layer name.



   .. py:property:: voids
      :type: list[Any]


      Primitive voids.

      Returns
      -------
      List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`




   .. py:property:: has_voids
      :type: bool


      Check if primitive has voids.

      Returns
      -------
      bool



   .. py:property:: is_negative
      :type: bool


      Check if primitive is negative.

      Returns
      -------
      bool



   .. py:property:: is_parameterized
      :type: bool


      Check if any primitive is parameterized.

      Returns
      -------
      bool
          True if any primitive is parameterized, False otherwise.



   .. py:property:: is_zone_primitive
      :type: bool


      Check if primitive is a zone primitive.

      Returns
      -------
      bool
          True if primitive is a zone primitive, False otherwise.



   .. py:property:: can_be_zone_primitive
      :type: bool


      Check if primitive can be a zone primitive.

      Returns
      -------
      bool
          True if primitive can be a zone primitive, False otherwise.



   .. py:property:: aedt_name
      :type: str


      Name to be visualized in AEDT.

      Returns
      -------
      str
          Name.



   .. py:method:: get_connected_objects() -> list[Any]

      Get connected objects.

      Returns
      -------
      List[:class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`]




   .. py:method:: area(include_voids=True) -> float

      Return the total area.

      Parameters
      ----------
      include_voids : bool, optional
          Either if the voids have to be included in computation.
          The default value is ``True``.

      Returns
      -------
      float
          Area value.



   .. py:property:: center
      :type: tuple[float, float]


      Return the primitive bounding box center coordinate.

      Returns
      -------
      List[float, float]
          [x, y]




   .. py:method:: get_connected_object_id_set() -> list[int]

      Produce a list of all geometries physically connected to a given layout object.

      Returns
      -------
      List[int]
          Found connected objects IDs with Layout object.



   .. py:property:: bbox
      :type: list[float]


      Return the primitive bounding box points. Lower left corner, upper right corner.

      Returns
      -------
      List[float, float, float, float]
          [lower_left x, lower_left y, upper right x, upper right y]




   .. py:method:: convert_to_polygon() -> pyedb.grpc.database.primitive.polygon.Polygon

      Convert path to polygon.

      Returns
      -------
      :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
          Polygon when successful, ``False`` when failed.




   .. py:method:: intersection_type(primitive) -> int

      Get intersection type between actual primitive and another primitive or polygon data.

      Parameters
      ----------
      primitive : :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>>` or `PolygonData`

      Returns
      -------
      int
          Intersection type:
          0 - objects do not intersect,
          1 - this object fully inside other (no common contour points),
          2 - other object fully inside this,
          3 - common contour points,
          4 - undefined intersection.



   .. py:method:: is_intersecting(primitive) -> bool

      Check if actual primitive and another primitive or polygon data intesects.

      Parameters
      ----------
      primitive : :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>>` or `PolygonData`

      Returns
      -------
      bool



   .. py:method:: get_closest_point(point) -> list[float]

      Get the closest point of the primitive to the input data.

      Parameters
      ----------
      point : list of float or PointData

      Returns
      -------
      List[float, float]
          [x, y].




   .. py:property:: arcs

      Get the Primitive Arc Data.

      Returns
      -------
      :class:`ArcData <ansys.edb.core.geometry.arc_data.ArcData>`



   .. py:property:: longest_arc
      :type: float


      Longest arc.

      Returns
      -------
      float
          Arc length.



   .. py:method:: rotate(angle, center=None) -> bool

      Rotate polygon around a center point by an angle.

      Parameters
      ----------
      angle : float
          Value of the rotation angle in degree.
      center : List of float or str [x,y], optional
          If None rotation is done from polygon center.

      Returns
      -------
      bool
         ``True`` when successful, ``False`` when failed.



   .. py:method:: move(vector) -> bool

      Move polygon along a vector.

      Parameters
      ----------
      vector : List of float or str [x,y].

      Returns
      -------
      bool
         ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> edbapp = ansys.aedt.core.Edb("myproject.aedb")
      >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
      >>> for polygon in top_layer_polygon:
      >>>     polygon.move(vector=["2mm", "100um"])



   .. py:method:: scale(factor, center=None) -> bool

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



   .. py:method:: subtract(primitives) -> list[Any]

      Subtract active primitive with one or more primitives.

      Parameters
      ----------
      primitives : :class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`
       or: List[:class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`]
       or: class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

      Returns
      -------
      List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`]
          List of Primitive objects.




   .. py:method:: intersect(primitives) -> list[Any]

      Intersect active primitive with one or more primitives.

      Parameters
      ----------
       primitives :class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`
       or: List[:class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`]
       or: class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

      Returns
      -------
      List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`]
          List of Primitive objects.




   .. py:method:: unite(primitives) -> list[Any]

      Unite active primitive with one or more primitives.

      Parameters
      ----------
       primitives : :class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`
       or: List[:class:`Primitives <pyedb.grpc.database.primitive.primitive.Primitive>`]
       or: class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

      Returns
      -------
      List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`]
          List of Primitive objects.




   .. py:method:: get_closest_arc_midpoint(point) -> list[float]

      Get the closest arc midpoint of the primitive to the input data.

      Parameters
      ----------
      point : List[float] or List[:class:`PointData <ansys.edb.core.geometry.point_data.PointData>`]

      Returns
      -------
      LIst[float, float]
          [x, y].



   .. py:property:: shortest_arc
      :type: float


      Longest arc.

      Returns
      -------
      float
          Arc length.



   .. py:method:: add_void(point_list) -> bool

      Add a void to current primitive.

      Parameters
      ----------
      point_list : list or :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`             or point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.

      Returns
      -------
      bool
          ``True`` if successful, either  ``False``.



   .. py:method:: points(arc_segments=6) -> tuple[list[float], list[float]] | None

      Return the list of points with arcs converted to segments.

      Parameters
      ----------
      arc_segments : int
          Number of facets to convert an arc. Default is `6`.

      Returns
      -------
      tuple(float, float)
          (X, Y).



   .. py:method:: points_raw()

      Return a list of Edb points.

      Returns
      -------
      List[:class:`PointData <ansys.edb.core.geometry.point_data.PointData>`]




   .. py:property:: id
      :type: int


      Primitive ID. This is the same as edb_uid, long Int.

      Returns
      -------
      int
          Primitive ID.



   .. py:property:: edb_uid
      :type: int


      Primitive EDB UID. This is the same as id, long Int.

      Returns
      -------
      int
          Primitive EDB UID.



   .. py:property:: primitive_type
      :type: str


      Primitive type.

      Returns
      -------
      str
          Primitive type, such as "circle", "rectangle", "polygon", "path" or "bondwire".



   .. py:property:: net
      :type: pyedb.grpc.database.net.net.Net



   .. py:property:: is_void

      Check if the primitive is a void.

      Returns
      -------
      bool
          ``True`` if the primitive is a void, ``False`` otherwise.



   .. py:property:: is_null

      Check if the primitive is null.

      Returns
      -------
      bool
          ``True`` if the primitive is null, ``False`` otherwise.



   .. py:property:: layer

      Get the layer object of the primitive.

      Returns
      -------
      :class:`Layer <pyedb.grpc.database.stackup.layer.Layer>`
          Layer object.



   .. py:method:: expand(offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001) -> list[Any]

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

      Return
      ------
      List:[:class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`]




   .. py:method:: plot(plot_net=False, show=True, save_plot=None)

      Plot the current polygon on matplotlib.

      Parameters
      ----------
      plot_net : bool, optional
          Whether if plot the entire net or only the selected polygon. Default is ``False``.
      show : bool, optional
          Whether if show the plot or not. Default is ``True``.
      save_plot : str, optional
          Save the plot path.

      Returns
      -------
      (ax, fig)
          Matplotlib ax and figures.



   .. py:method:: delete()

      Delete the primitive.



