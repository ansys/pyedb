src.pyedb.dotnet.database.cell.primitive.primitive
==================================================

.. py:module:: src.pyedb.dotnet.database.cell.primitive.primitive


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.primitive.primitive.Primitive


Module Contents
---------------

.. py:class:: Primitive(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.connectable.Connectable`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_prim = edb.modeler.primitives[0]
   >>> edb_prim.is_void  # Class Property
   >>> edb_prim.IsVoid()  # EDB Object Property


   .. py:attribute:: primitive_object


   .. py:property:: type

      Return the type of the primitive.

      Expected output is among ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

      Returns
      -------
      str



   .. py:property:: primitive_type

      Return the type of the primitive.

      Expected output is among ``"circle"``, ``"rectangle"``,``"polygon"``,``"path"`` or ``"bondwire"``.

      Returns
      -------
      str



   .. py:property:: layer

      Get the primitive edb layer object.



   .. py:property:: layer_name

      Get the primitive layer name.

      Returns
      -------
      str



   .. py:property:: is_void

      Either if the primitive is a void or not.

      Returns
      -------
      bool



   .. py:method:: area(include_voids=True)

      Return the total area.

      Parameters
      ----------
      include_voids : bool, optional
          Either if the voids have to be included in computation.
          The default value is ``True``.

      Returns
      -------
      float



   .. py:property:: is_negative

      Determine whether this primitive is negative.

      Returns
      -------
      bool
          True if it is negative, False otherwise.



   .. py:property:: center

      Return the primitive bounding box center coordinate.

      Returns
      -------
      list
          [x, y]




   .. py:method:: is_arc(point)

      Either if a point is an arc or not.

      Returns
      -------
      bool



   .. py:property:: bbox

      Return the primitive bounding box points. Lower left corner, upper right corner.

      Returns
      -------
      list
          [lower_left x, lower_left y, upper right x, upper right y]




   .. py:method:: convert_to_polygon()

      Convert path to polygon.

      Returns
      -------
      bool, :class:`dotnet.database.edb_data.primitives.EDBPrimitives`
          Polygon when successful, ``False`` when failed.




   .. py:method:: intersection_type(primitive)

      Get intersection type between actual primitive and another primitive or polygon data.

      Parameters
      ----------
      primitive : :class:`pyaeedt.database.edb_data.primitives_data.EDBPrimitives` or `PolygonData`

      Returns
      -------
      int
          Intersection type:
          0 - objects do not intersect,
          1 - this object fully inside other (no common contour points),
          2 - other object fully inside this,
          3 - common contour points,
          4 - undefined intersection.



   .. py:method:: is_intersecting(primitive)

      Check if actual primitive and another primitive or polygon data intesects.

      Parameters
      ----------
      primitive : :class:`pyaeedt.database.edb_data.primitives_data.EDBPrimitives` or `PolygonData`

      Returns
      -------
      bool



   .. py:method:: get_closest_point(point)

      Get the closest point of the primitive to the input data.

      Parameters
      ----------
      point : list of float or PointData

      Returns
      -------
      list of float



   .. py:property:: arcs

      Get the Primitive Arc Data.



   .. py:property:: longest_arc

      Get the longest arc.



   .. py:method:: subtract(primitives)

      Subtract active primitive with one or more primitives.

      Parameters
      ----------
      primitives : :class:`dotnet.database.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

      Returns
      -------
      List of :class:`dotnet.database.edb_data.EDBPrimitives`



   .. py:method:: intersect(primitives)

      Intersect active primitive with one or more primitives.

      Parameters
      ----------
      primitives : :class:`dotnet.database.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

      Returns
      -------
      List of :class:`dotnet.database.edb_data.EDBPrimitives`



   .. py:method:: unite(primitives)

      Unite active primitive with one or more primitives.

      Parameters
      ----------
      primitives : :class:`dotnet.database.edb_data.EDBPrimitives` or EDB PolygonData or EDB Primitive or list

      Returns
      -------
      List of :class:`dotnet.database.edb_data.EDBPrimitives`



   .. py:method:: get_closest_arc_midpoint(point)

      Get the closest arc midpoint of the primitive to the input data.

      Parameters
      ----------
      point : list of float or PointData

      Returns
      -------
      list of float



   .. py:property:: voids

      :obj:`list` of :class:`Primitive <ansys.edb.primitive.Primitive>`: List of void        primitive objects inside the primitive.

      Read-Only.



   .. py:property:: shortest_arc

      Get the longest arc.



   .. py:property:: aedt_name

      Name to be visualized in AEDT.

      Returns
      -------
      str
          Name.



   .. py:property:: polygon_data

      :class:`pyedb.dotnet.database.dotnet.database.PolygonDataDotNet`: Outer contour of the Polygon object.



   .. py:method:: add_void(point_list)

      Add a void to current primitive.

      Parameters
      ----------
      point_list : list or :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`             or EDB Primitive Object. Point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.

      Returns
      -------
      bool
          ``True`` if successful, either  ``False``.



   .. py:property:: api_class


   .. py:method:: set_hfss_prop(material, solve_inside)

      Set HFSS properties.

      Parameters
      ----------
      material : str
          Material property name to be set.
      solve_inside : bool
          Whether to do solve inside.



   .. py:property:: has_voids

      :obj:`bool`: If a primitive has voids inside.

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



