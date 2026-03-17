src.pyedb.dotnet.database.modeler
=================================

.. py:module:: src.pyedb.dotnet.database.modeler

.. autoapi-nested-parse::

   This module contains these classes: `EdbLayout` and `Shape`.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.modeler.Modeler


Module Contents
---------------

.. py:class:: Modeler(p_edb)

   Bases: :py:obj:`object`


   Manages EDB methods for primitives management accessible from `Edb.modeler` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_layout = edbapp.modeler


   .. py:property:: primitives

      Primitives.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          List of primitives.



   .. py:method:: parametrize_polygon(polygon, selection_polygon, offset_name='offsetx', origin=None)

      Parametrize pieces of a polygon based on another polygon.

      Parameters
      ----------
      polygon :
          Name of the polygon.
      selection_polygon :
          Polygon to use as a filter.
      offset_name : str, optional
          Name of the offset to create.  The default is ``"offsetx"``.
      origin : list, optional
          List of the X and Y origins, which impacts the vector
          computation and is needed to determine expansion direction.
          The default is ``None``, in which case the vector is
          computed from the polygon's center.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: create_trace(path_list, layer_name, width=1, net_name='', start_cap_style='Round', end_cap_style='Round', corner_style='Round')

      Create a trace based on a list of points.

      Parameters
      ----------
      path_list : list
          List of points.
      layer_name : str
          Name of the layer on which to create the path.
      width : float, optional
          Width of the path. The default is ``1``.
      net_name : str, optional
          Name of the net. The default is ``""``.
      start_cap_style : str, optional
          Style of the cap at its start. Options are ``"Round"``,
          ``"Extended",`` and ``"Flat"``. The default is
          ``"Round"``.
      end_cap_style : str, optional
          Style of the cap at its end. Options are ``"Round"``,
          ``"Extended",`` and ``"Flat"``. The default is
          ``"Round"``.
      corner_style : str, optional
          Style of the corner. Options are ``"Round"``,
          ``"Sharp"`` and ``"Mitered"``. The default is ``"Round"``.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`



   .. py:method:: create_polygon(points=None, layer_name='', voids=[], net_name='')

      Create a polygon based on a list of points and voids.

      Parameters
      ----------
      points : list of points or PolygonData or ``modeler.Shape``
          Shape or point lists of the main object. Point list can be in the format of `[[x1,y1], [x2,y2],..,[xn,yn]]`.
          Each point can be:
          - [x, y] coordinate
          - [x, y, height] for an arc with specific height (between previous point and actual point)
          - [x, y, rotation, xc, yc] for an arc given a point, rotation and center.
      layer_name : str
          Name of the layer on which to create the polygon.
      voids : list, optional
          List of shape objects for voids or points that creates the shapes. The default is``[]``.
      net_name : str, optional
          Name of the net. The default is ``""``.


      Returns
      -------
      bool, :class:`dotnet.database.edb_data.primitives.Primitive`
          Polygon when successful, ``False`` when failed.



   .. py:method:: create_rectangle(layer_name, net_name='', lower_left_point='', upper_right_point='', center_point='', width='', height='', representation_type='LowerLeftUpperRight', corner_radius='0mm', rotation='0deg')

      Create rectangle.

      Parameters
      ----------
      layer_name : str
          Name of the layer on which to create the rectangle.
      net_name : str
          Name of the net. The default is ``""``.
      lower_left_point : list
          Lower left point when ``representation_type="LowerLeftUpperRight"``. The default is ``""``.
      upper_right_point : list
          Upper right point when ``representation_type="LowerLeftUpperRight"``. The default is ``""``.
      center_point : list
          Center point when ``representation_type="CenterWidthHeight"``. The default is ``""``.
      width : str
          Width of the rectangle when ``representation_type="CenterWidthHeight"``. The default is ``""``.
      height : str
          Height of the rectangle when ``representation_type="CenterWidthHeight"``. The default is ``""``.
      representation_type : str, optional
          Type of the rectangle representation. The default is ``LowerLeftUpperRight``. Options are
          ``"LowerLeftUpperRight"`` and ``"CenterWidthHeight"``.
      corner_radius : str, optional
          Radius of the rectangle corner. The default is ``"0mm"``.
      rotation : str, optional
          Rotation of the rectangle. The default is ``"0deg"``.

      Returns
      -------
       :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Rectangle when successful, ``False`` when failed.



   .. py:method:: create_circle(layer_name, x, y, radius, net_name='')

      Create a circle on a specified layer.

      Parameters
      ----------
      layer_name : str
          Name of the layer.
      x : float
          Position on the X axis.
      y : float
          Position on the Y axis.
      radius : float
          Radius of the circle.
      net_name : str, optional
          Name of the net. The default is ``None``, in which case the
          default name is assigned.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          Objects of the circle created when successful.



   .. py:method:: delete_primitives(net_names)

      Delete primitives by net names.

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

      >>> Edb.modeler.delete_primitives(net_names=["GND"])



   .. py:method:: fix_circle_void_for_clipping()

      Fix issues when circle void are clipped due to a bug in EDB.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when no changes were applied.



   .. py:method:: add_void(shape, void_shape)

      Add a void into a shape.

      Parameters
      ----------
      shape : Polygon
          Shape of the main object.
      void_shape : list, Path
          Shape of the voids.



   .. py:method:: shape_to_polygon_data(shape)

      Convert a shape to polygon data.

      Parameters
      ----------
      shape : :class:`pyedb.dotnet.database.modeler.Modeler.Shape`
          Type of the shape to convert. Options are ``"rectangle"`` and ``"polygon"``.



   .. py:class:: Shape(type='unknown', pointA=None, pointB=None, centerPoint=None, radius=None, points=None, properties={})

      Bases: :py:obj:`object`


      Shape class.

      Parameters
      ----------
      type : str, optional
          Type of the shape. Options are ``"circle"``, ``"rectangle"``, and ``"polygon"``.
          The default is ``"unknown``.
      pointA : optional
          Lower-left corner when ``type="rectangle"``. The default is ``None``.
      pointB : optional
          Upper-right corner when ``type="rectangle"``. The default is ``None``.
      centerPoint : optional
          Center point when ``type="circle"``. The default is ``None``.
      radius : optional
          Radius when ``type="circle"``. The default is ``None``.
      points : list, optional
          List of points when ``type="polygon"``. The default is ``None``.
      properties : dict, optional
          Dictionary of properties associated with the shape. The default is ``{}``.


      .. py:attribute:: type
         :value: 'unknown'



      .. py:attribute:: pointA
         :value: None



      .. py:attribute:: pointB
         :value: None



      .. py:attribute:: centerPoint
         :value: None



      .. py:attribute:: radius
         :value: None



      .. py:attribute:: points
         :value: None



      .. py:attribute:: properties



   .. py:method:: parametrize_trace_width(nets_name, layers_name=None, parameter_name='trace_width', variable_value=None)

      Parametrize a Trace on specific layer or all stackup.

      Parameters
      ----------
      nets_name : str, list
          name of the net or list of nets to parametrize.
      layers_name : str, optional
          name of the layer or list of layers to which the net to parametrize has to be included.
      parameter_name : str, optional
          name of the parameter to create.
      variable_value : str, float, optional
          value with units of parameter to create.
          If None, the first trace width of Net will be used as parameter value.

      Returns
      -------
      bool



   .. py:method:: unite_polygons_on_layer(layer_name=None, delete_padstack_gemometries=False, net_names_list=None)

      Try to unite all Polygons on specified layer.

      Parameters
      ----------
      layer_name : str, optional
          Name of layer name to unite objects on. The default is ``None``, in which case all layers are taken.
      delete_padstack_gemometries : bool, optional
          Whether to delete all padstack geometries. The default is ``False``.
      net_names_list : list[str] : optional
          Net names list filter. The default is ``[]``, in which case all nets are taken.

      Returns
      -------
      bool
          ``True`` is successful.



   .. py:method:: defeature_polygon(poly, tolerance=0.001)

      Defeature the polygon based on the maximum surface deviation criteria.

      Parameters
      ----------
      maximum_surface_deviation : float
      poly : Edb Polygon primitive
          Polygon to defeature.
      tolerance : float, optional
          Maximum tolerance criteria. The default is ``0.001``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: get_layout_statistics(evaluate_area=False, net_list=False) -> pyedb.dotnet.database.edb_data.utilities.EDBStatistics

      Return EDBStatistics object from a layout.

      Parameters
      ----------

      evaluate_area : optional bool
          When True evaluates the layout metal surface, can take time-consuming,
          avoid using this option on large design.
      net_list: optional bool
          list of net names to evaluate area for, if None all nets will be evaluated.
      Returns
      -------

      EDBStatistics object.




   .. py:method:: create_bondwire(definition_name, placement_layer, width, material, start_layer_name, start_x, start_y, end_layer_name, end_x, end_y, net, bondwire_type='jedec4', start_cell_instance_name=None)

      Create a bondwire object.

      Parameters
      ----------
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
      start_layer_name : str
          Name of start layer.
      start_x : :class:`Value <ansys.edb.utility.Value>`
          X value of start point.
      start_y : :class:`Value <ansys.edb.utility.Value>`
          Y value of start point.
      end_layer_name : str
          Name of end layer.
      end_x : :class:`Value <ansys.edb.utility.Value>`
          X value of end point.
      end_y : :class:`Value <ansys.edb.utility.Value>`
          Y value of end point.
      net : str or :class:`Net <ansys.edb.net.Net>` or None
          Net of the Bondwire.
      start_cell_instance_name : None
          Added for grpc compatibility.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.primitive.BondwireDotNet`
          Bondwire object created.



   .. py:method:: create_pin_group(name: str, pins_by_id=None, pins_by_aedt_name=None, pins_by_name=None)

      Create a PinGroup.

      Parameters
      ----------
      name : str
          Name of the PinGroup.
      pins_by_id : list[int] or None
          List of pins by ID.
      pins_by_aedt_name : list[str] or None
          List of pins by AEDT name.
      pins_by_name : list[str] or None
          List of pins by name.



   .. py:property:: db

      Db object.



   .. py:property:: layers

      Dictionary of layers.

      Returns
      -------
      dict
          Dictionary of layers.



   .. py:method:: get_primitive(primitive_id)

      Retrieve primitive from give id.

      Parameters
      ----------
      primitive_id : int
          Primitive id.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          List of primitives.



   .. py:property:: polygons_by_layer

      Primitives with layer names as keys.

      Returns
      -------
      dict
          Dictionary of primitives with layer names as keys.



   .. py:property:: primitives_by_net

      Primitives with net names as keys.

      Returns
      -------
      dict
          Dictionary of primitives with nat names as keys.



   .. py:property:: primitives_by_layer

      Primitives with layer names as keys.

      Returns
      -------
      dict
          Dictionary of primitives with layer names as keys.



   .. py:property:: rectangles

      Rectangles.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          List of rectangles.




   .. py:property:: circles

      Circles.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          List of circles.




   .. py:property:: paths

      Paths.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          List of paths.



   .. py:property:: polygons

      Polygons.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          List of polygons.



   .. py:method:: get_polygons_by_layer(layer_name, net_list=None)

      Retrieve polygons by a layer.

      Parameters
      ----------
      layer_name : str
          Name of the layer.
      net_list : list, optional
          List of net names.

      Returns
      -------
      list
          List of primitive objects.



   .. py:method:: get_primitive_by_layer_and_point(point=None, layer=None, nets=None)

      Return primitive given coordinate point [x, y], layer name and nets.

      Parameters
      ----------
      point : list
          Coordinate [x, y]

      layer : list or str, optional
          list of layer name or layer name applied on filter.

      nets : list or str, optional
          list of net name or single net name applied on filter

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.Primitive`
          List of primitives, polygons, paths and rectangles.



   .. py:method:: get_polygon_bounding_box(polygon)

      Retrieve a polygon bounding box.

      Parameters
      ----------
      polygon :
          Name of the polygon.

      Returns
      -------
      list
          List of bounding box coordinates in the format ``[-x, -y, +x, +y]``.

      Examples
      --------
      >>> poly = database.modeler.get_polygons_by_layer("GND")
      >>> bounding = database.modeler.get_polygon_bounding_box(poly[0])



   .. py:method:: get_polygon_points(polygon)

      Retrieve polygon points.

      .. note::
         For arcs, one point is returned.

      Parameters
      ----------
      polygon :
          class: `dotnet.database.edb_data.primitives_data.Primitive`

      Returns
      -------
      list
          List of tuples. Each tuple provides x, y point coordinate. If the length of two consecutives tuples
           from the list equals 2, a segment is defined. The first tuple defines the starting point while the second
           tuple the ending one. If the length of one tuple equals one, that means a polyline is defined and the value
           is giving the arc height. Therefore to polyline is defined as starting point for the tuple
           before in the list, the current one the arc height and the tuple after the polyline ending point.

      Examples
      --------

      >>> poly = database.modeler.get_polygons_by_layer("GND")
      >>> points = database.modeler.get_polygon_points(poly[0])




   .. py:method:: get_primitives(net_name=None, layer_name=None, prim_type=None, is_void=False)

      Get primitives by conditions.

      Parameters
      ----------
      net_name : str, optional
          Set filter on net_name. Default is ``None``.
      layer_name : str, optional
          Set filter on layer_name. Default is ``None``.
      prim_type :  str, optional
          Set filter on primitive type. Default is ``None``.
      is_void : bool
          Set filter on is_void. Default is '``False'``
      Returns
      -------
      list
          List of filtered primitives



   .. py:method:: clear_cache()
      :staticmethod:


      Force reload of all primitives and reset indexes.



