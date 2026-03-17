src.pyedb.dotnet.database.edb_data.primitives_data
==================================================

.. py:module:: src.pyedb.dotnet.database.edb_data.primitives_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.primitives_data.EdbRectangle
   src.pyedb.dotnet.database.edb_data.primitives_data.EdbCircle
   src.pyedb.dotnet.database.edb_data.primitives_data.EdbPolygon
   src.pyedb.dotnet.database.edb_data.primitives_data.EdbText
   src.pyedb.dotnet.database.edb_data.primitives_data.EdbBondwire
   src.pyedb.dotnet.database.edb_data.primitives_data.EDBArcs


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.primitives_data.cast


Module Contents
---------------

.. py:function:: cast(raw_primitive, core_app)

   Cast the primitive object to correct concrete type.

   Returns
   -------
   Primitive


.. py:class:: EdbRectangle(raw_primitive, core_app)

   Bases: :py:obj:`pyedb.dotnet.database.cell.primitive.primitive.Primitive`, :py:obj:`pyedb.dotnet.database.dotnet.primitive.RectangleDotNet`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_prim = edb.modeler.primitives[0]
   >>> edb_prim.is_void  # Class Property
   >>> edb_prim.IsVoid()  # EDB Object Property


.. py:class:: EdbCircle(raw_primitive, core_app)

   Bases: :py:obj:`pyedb.dotnet.database.cell.primitive.primitive.Primitive`, :py:obj:`pyedb.dotnet.database.dotnet.primitive.CircleDotNet`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_prim = edb.modeler.primitives[0]
   >>> edb_prim.is_void  # Class Property
   >>> edb_prim.IsVoid()  # EDB Object Property


.. py:class:: EdbPolygon(raw_primitive, core_app)

   Bases: :py:obj:`pyedb.dotnet.database.cell.primitive.primitive.Primitive`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_prim = edb.modeler.primitives[0]
   >>> edb_prim.is_void  # Class Property
   >>> edb_prim.IsVoid()  # EDB Object Property


   .. py:method:: clone()

      Clone a primitive object with keeping same definition and location.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:property:: has_self_intersections

      Check if Polygon has self intersections.

      Returns
      -------
      bool



   .. py:method:: fix_self_intersections()

      Remove self intersections if they exists.

      Returns
      -------
      list
          All new polygons created from the removal operation.



   .. py:method:: duplicate_across_layers(layers)

      Duplicate across layer a primitive object.

      Parameters:

      layers: list
          list of str, with layer names

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: move(vector)

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



   .. py:method:: rotate(angle, center=None)

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

      Examples
      --------
      >>> edbapp = ansys.aedt.core.Edb("myproject.aedb")
      >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
      >>> for polygon in top_layer_polygon:
      >>>     polygon.rotate(angle=45)



   .. py:method:: move_layer(layer)

      Move polygon to given layer.

      Parameters
      ----------
      layer : str
          layer name.

      Returns
      -------
      bool
         ``True`` when successful, ``False`` when failed.



   .. py:method:: in_polygon(point_data, include_partial=True)

      Check if padstack Instance is in given polygon data.

      Parameters
      ----------
      point_data : PointData Object or list of float
      include_partial : bool, optional
          Whether to include partial intersecting instances. The default is ``True``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:property:: polygon_data

      :class:`pyedb.dotnet.database.dotnet.database.PolygonDataDotNet`: Outer contour of the Polygon object.



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



.. py:class:: EdbText(raw_primitive, core_app)

   Bases: :py:obj:`pyedb.dotnet.database.cell.primitive.primitive.Primitive`, :py:obj:`pyedb.dotnet.database.dotnet.primitive.TextDotNet`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_prim = edb.modeler.primitives[0]
   >>> edb_prim.is_void  # Class Property
   >>> edb_prim.IsVoid()  # EDB Object Property


.. py:class:: EdbBondwire(raw_primitive, core_app)

   Bases: :py:obj:`pyedb.dotnet.database.cell.primitive.primitive.Primitive`, :py:obj:`pyedb.dotnet.database.dotnet.primitive.BondwireDotNet`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> edb_prim = edb.modeler.primitives[0]
   >>> edb_prim.is_void  # Class Property
   >>> edb_prim.IsVoid()  # EDB Object Property


.. py:class:: EDBArcs(app, arc)

   Bases: :py:obj:`object`


   Manages EDB Arc Data functionalities.
   It Inherits EDB primitives arcs properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb(myedb, edbversion="2021.2")
   >>> prim_arcs = edb.modeler.primitives[0].arcs
   >>> prim_arcs.center  # arc center
   >>> prim_arcs.points  # arc point list
   >>> prim_arcs.mid_point  # arc mid point


   .. py:attribute:: arc_object


   .. py:property:: start

      Get the coordinates of the starting point.

      Returns
      -------
      list
          List containing the X and Y coordinates of the starting point.


      Examples
      --------
      >>> appedb = Edb(fpath, edbversion="2024.2")
      >>> start_coordinate = appedb.nets["V1P0_S0"].primitives[0].arcs[0].start
      >>> print(start_coordinate)
      [x_value, y_value]



   .. py:property:: end

      Get the coordinates of the ending point.

      Returns
      -------
      list
          List containing the X and Y coordinates of the ending point.

      Examples
      --------
      >>> appedb = Edb(fpath, edbversion="2024.2")
      >>> end_coordinate = appedb.nets["V1P0_S0"].primitives[0].arcs[0].end



   .. py:property:: height

      Get the height of the arc.

      Returns
      -------
      float
          Height of the arc.


      Examples
      --------
      >>> appedb = Edb(fpath, edbversion="2024.2")
      >>> arc_height = appedb.nets["V1P0_S0"].primitives[0].arcs[0].height



   .. py:property:: center

      Arc center.

      Returns
      -------
      list



   .. py:property:: length

      Arc length.

      Returns
      -------
      float



   .. py:property:: mid_point

      Arc mid point.

      Returns
      -------
      float



   .. py:property:: radius

      Arc radius.

      Returns
      -------
      float



   .. py:property:: is_segment

      Either if it is a straight segment or not.

      Returns
      -------
      bool



   .. py:property:: is_point

      Either if it is a point or not.

      Returns
      -------
      bool



   .. py:property:: is_ccw

      Test whether arc is counter clockwise.

      Returns
      -------
      bool



   .. py:property:: points_raw

      Return a list of Edb points.

      Returns
      -------
      list
          Edb Points.



   .. py:property:: points

      Return the list of points with arcs converted to segments.

      Parameters
      ----------
      arc_segments : int
          Number of facets to convert an arc. Default is `6`.

      Returns
      -------
      list, list
          x and y list of points.



