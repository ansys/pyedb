src.pyedb.grpc.database.primitive.polygon
=========================================

.. py:module:: src.pyedb.grpc.database.primitive.polygon


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.polygon.Polygon


Module Contents
---------------

.. py:class:: Polygon(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.primitive.primitive.Primitive`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", version="2026.1", grpc=True)
   >>> edb_prim = edb.layout.primitives[0]


   .. py:attribute:: core


   .. py:property:: layer
      :type: pyedb.grpc.database.layers.layer.Layer


      Layer of the polygon.

      Returns
      -------
      :class:`Layer <pyedb.edb.database.layers.layer.Layer>`
          Layer object.




   .. py:property:: type
      :type: str


      Primitive type.

      Return
      ------
      str
          Polygon type.




   .. py:property:: has_self_intersections
      :type: bool


      Check if Polygon has self intersections.

      Returns
      -------
      bool



   .. py:method:: create(layout: pyedb.grpc.database.layout.layout.Layout, layer: Union[str, pyedb.grpc.database.layers.layer.Layer], net: Union[str, pyedb.grpc.database.net.net.Net] = None, polygon_data=None)
      :classmethod:


      Create a polygon in the specified layout, layer, and net using the provided polygon data.

      Parameters
      ----------
      layout : Layout
          The layout in which the polygon will be created. If not provided, the active layout of the `pedb`
          instance will be used.
      layer : Union[str, Layer]
          The layer in which the polygon will be created. This parameter is required and must be specified.
      net : Union[str, Net], optional
          The net to which the polygon will belong. If not provided, the polygon will not be associated with a
          net.
      polygon_data : list or GrpcPolygonData, optional
          The data defining the polygon. This can be a list of points or an instance of `GrpcPolygonData`.
          This parameter is required and must be specified.

      Returns
      -------
      :class:`Polygon <ansys.edb.core.primitive.polygon.Polygon>`
          The created polygon object.

      Raises
      ------
      ValueError
          If the `layer` parameter is not provided.
      ValueError
          If the `polygon_data` parameter is not provided.

      Notes
      -----
      - If `polygon_data` is provided as a list, it will be converted to a `GrpcPolygonData` object.
      - The created polygon is added to the modeler primitives of the `pedb` instance.




   .. py:method:: fix_self_intersections() -> list[Polygon]

      Remove self intersections if they exist.

      Returns
      -------
      List[:class:`Polygon <ansys.edb.core.primitive.polygon.Polygon>`]
          All new polygons created from the removal operation.




   .. py:method:: clone()

      Duplicate polygon.

      Returns
      -------
      :class:`Polygon <ansys.edb.core.primitive.polygon.Polygon>`
          Cloned polygon.




   .. py:method:: duplicate_across_layers(layers) -> bool

      Duplicate across layer a primitive object.

      Parameters:

      layers: list
          list of str, with layer names

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
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
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

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
      >>> for polygon in top_layer_polygon:
      >>>     polygon.rotate(angle=45)



   .. py:method:: move_layer(layer) -> bool

      Move polygon to given layer.

      Parameters
      ----------
      layer : str
          layer name.

      Returns
      -------
      bool
         ``True`` when successful, ``False`` when failed.



   .. py:method:: in_polygon(point_data, include_partial=True) -> bool

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



   .. py:method:: add_void(polygon)

      Add a void to current primitive.

      Parameters
      ----------
      point_list : list or :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`             or point list in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.

      Returns
      -------
      bool
          ``True`` if successful, either  ``False``.



