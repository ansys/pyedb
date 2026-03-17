src.pyedb.grpc.database.geometry.polygon_data
=============================================

.. py:module:: src.pyedb.grpc.database.geometry.polygon_data


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.geometry.polygon_data.PolygonData


Module Contents
---------------

.. py:class:: PolygonData(core=None, create_from_points=None, create_from_circle=None, create_from_rectangle=None, create_from_bounding_box=None, **kwargs)

   Class managing Polygon Data.


   .. py:property:: bounding_box
      :type: tuple[tuple[float, float], tuple[float, float]]


      Bounding box.

      Returns
      -------
      tuple[tuple[float, float], tuple[float, float]]
          Tuple of coordinates for the component's bounding box, with the list of
          coordinates in this order: (X lower left corner, Y lower left corner),
          (X upper right corner, Y upper right corner).



   .. py:method:: bounding_circle() -> tuple[tuple[float, float], float]

      Get the bounding circle of the polygon.

      Returns
      -------
      Tuple[Tuple[float, float], float]
          Center point (x, y) and radius of the bounding circle.



   .. py:property:: arcs
      :type: list[pyedb.grpc.database.geometry.arc_data.ArcData]


      Get the Primitive Arc Data.

      Returns
      -------
      List[:class:`ArcData <pyedb.grpc.database.geometry.arc_data.ArcData>`]



   .. py:property:: is_closed
      :type: bool


      Check if polygon is closed.

      Returns
      -------
      bool



   .. py:method:: is_inside(point: tuple[float, float]) -> bool

      Check if polygon is inside.

      Returns
      -------
      bool



   .. py:property:: sense
      :type: ansys.edb.core.geometry.polygon_data.PolygonSenseType


      Get the polygon sense type.

      Returns
      -------
      :class: `PolygonSenseType <ansys.edb.core.geometry.polygon_data.PolygonSenseType>`



   .. py:property:: holes

      Get all holes in polygon.

      Returns
      -------
      list[:class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`]



   .. py:property:: points
      :type: list[tuple[float, float]]


      Get all points in polygon.

      Returns
      -------
      list[tuple[float, float]]



   .. py:property:: points_raw

      Get all points in polygon.

      Returns
      -------
      list[:class:`PointData <pyedb.grpc.database.geometry.point_data.PointData>`]



   .. py:property:: arc_data

      Get all arc data in polygon.

      Returns
      -------
      list[:class:`ArcData <pyedb.grpc.database.geometry.arc_data.ArcData>`]



   .. py:method:: create_from_points(points, closed=True)
      :classmethod:



   .. py:method:: create_from_bounding_box(points) -> ansys.edb.core.geometry.polygon_data.PolygonData
      :classmethod:


      Create PolygonData from point list.

      Returns
      -------
      :class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`




   .. py:method:: has_self_intersections(tolerance=1e-12) -> bool

      Check if the polygon has self-intersections.

      Parameters
      ----------
      tolerance : float, optional
          Tolerance in meters.

      Returns
      -------
      bool
          True if the polygon has self-intersections, False otherwise.




   .. py:method:: expand(offset=0.001, tolerance=1e-12, round_corners=True, maximum_corner_extension=0.001) -> bool

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

      Returns
      -------
      bool




   .. py:method:: unite(polygons)

      Create union of polygons.

      Parameters
      ----------
      polygons : list[:class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`]
          List of PolygonData objects to unite with the current polygon.

      Returns
      -------
      bool



   .. py:method:: area()

      Get area of polygon.

      Returns
      -------
      float



   .. py:method:: intersection_type(polygon_data)

      Get intersection type of polygon.

      Returns
      -------
      :class: `PolygonIntersectionType <ansys.edb.core.geometry.polygon_data.PolygonIntersectionType>`
      Returned value can be one of the following:
          - 0 : No Intersection
          - 1 : Current Polygon Inside Other
          - 2: Other polygon Inside Current
          - 3: Common intersection
          - 4: undifined intersection



   .. py:method:: without_arcs() -> PolygonData

      Get a copy of the polygon without arcs.

      Returns
      -------
      :class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`



