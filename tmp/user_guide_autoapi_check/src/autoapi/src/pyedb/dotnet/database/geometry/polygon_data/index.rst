src.pyedb.dotnet.database.geometry.polygon_data
===============================================

.. py:module:: src.pyedb.dotnet.database.geometry.polygon_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.geometry.polygon_data.PolygonData


Module Contents
---------------

.. py:class:: PolygonData(pedb: pyedb.dotnet.edb.Edb, edb_object: Any | None = None, create_from_points: Any | None = None, create_from_bounding_box: Any | None = None, **kwargs)

   Polygon Data.


   .. py:property:: bounding_box
      :type: list[float]


      Bounding box.

      Returns
      -------
      List[float]
          List of coordinates for the component's bounding box, with the list of
          coordinates in this order: [X lower left corner, Y lower left corner,
          X upper right corner, Y upper right corner].



   .. py:property:: arcs
      :type: list[pyedb.dotnet.database.edb_data.primitives_data.EDBArcs]


      Get the Primitive Arc Data.



   .. py:property:: points
      :type: list[tuple[float, float]]


      Get all points in polygon.

      Returns
      -------
      list[tuple[float, float]]



   .. py:property:: points_without_arcs
      :type: list[tuple[float, float]]


      Get all points in polygon without arcs.



   .. py:method:: create_from_points(points: list[tuple[float, float]], closed: bool = True) -> Any

      Create a polygon from a list of points.



   .. py:property:: area
      :type: float


      Get the area of the polygon.



   .. py:method:: create_from_bounding_box(points: list[Any]) -> Any

      Create a polygon from a bounding box defined by two corner points.



   .. py:method:: expand(offset: float = 0.001, tolerance: float = 1e-12, round_corners: bool = True, maximum_corner_extension: float = 0.001) -> bool

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



   .. py:method:: create_from_arcs(arcs: list[Any], flag: bool) -> PolygonData

      Edb Dotnet Api Database `Edb.Geometry.CreateFromArcs`.

      Parameters
      ----------
      arcs : list or `Edb.Geometry.ArcData`
          List of ArcData.
      flag : bool



   .. py:method:: is_inside(x: str | float | list[Any], y: str | float | None = None) -> bool

      Determines whether a point is inside the polygon.



   .. py:method:: point_in_polygon(x: str | float | list[Any], y: str | float | None = None) -> bool

      Determines whether a point is inside the polygon.

      ..deprecated:: 0.48.0
         Use: func:`is_inside` instead.



   .. py:method:: get_point(index: int) -> pyedb.dotnet.database.geometry.point_data.PointData

      Gets the point at the index as a PointData object.



   .. py:method:: set_point(index: int, point_data: pyedb.dotnet.database.geometry.point_data.PointData) -> None

      Sets the point at the index from a PointData object.



