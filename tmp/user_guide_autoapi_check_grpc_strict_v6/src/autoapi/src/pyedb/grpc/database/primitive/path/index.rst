src.pyedb.grpc.database.primitive.path
======================================

.. py:module:: src.pyedb.grpc.database.primitive.path


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.path.mapping


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.path.Path


Module Contents
---------------

.. py:data:: mapping

.. py:class:: Path(pedb, core=None)

   Bases: :py:obj:`pyedb.grpc.database.primitive.primitive.Primitive`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", version="2026.1", grpc=True)
   >>> edb_prim = edb.layout.primitives[0]


   .. py:property:: width
      :type: float


      Path width.

      Returns
      -------
      float
          Path width or None.



   .. py:property:: length
      :type: float


      Path length in meters.

      Returns
      -------
      float
          Path length in meters.



   .. py:method:: create(layout, layer: Union[str, pyedb.grpc.database.layers.layer.Layer] = None, net: Union[str, pyedb.grpc.database.net.net.Net] = None, width: float = 0.0001, end_cap1: Union[str, ansys.edb.core.primitive.path.PathEndCapType] = 'flat', end_cap2: Union[str, ansys.edb.core.primitive.path.PathEndCapType] = 'flat', corner_style: Union[str, ansys.edb.core.primitive.path.PathCornerType] = 'sharp', points: Union[list, ansys.edb.core.geometry.polygon_data.PolygonData] = None)
      :classmethod:


      Create a path in the specified layout, layer, and net with the given parameters.

      Parameters
      ----------
      layout : Layout, optional
          The layout in which the path will be created. If not provided, the active layout of the `pedb` instance
          will be used.
      layer : Union[str, Layer], optional
          The layer in which the path will be created. This parameter is required and must be specified.
      net : Union[str, Net], optional
          The net to which the path will belong. If not provided, the path will not be associated with a net.
      width : float, optional
          The width of the path in meters. The default value is `100e-6`.
      end_cap1 : str, optional
          The style of the first end cap. Options are `"flat"`, `"round"`, `"extended"`, and `"clipped"`.
          The default value is `"flat"`.
      end_cap2 : str, optional
          The style of the second end cap. Options are `"flat"`, `"round"`, `"extended"`, and `"clipped"`.
          The default value is `"flat"`.
      corner_style : str, optional
          The style of the path corners. Options are `"sharp"`, `"round"`, and `"mitter"`.
          The default value is `"sharp"`.
      points : Union[list, GrpcPolygonData], optional
          The points defining the path. This can be a list of points or an instance of `GrpcPolygonData`.
          This parameter is required and must be specified.

      Returns
      -------
      :class:`Path <pyedb.grpc.database.primitive.path.Path>`
          The created path object.

      Raises
      ------
      ValueError
          If the `points` parameter is not provided.

      Notes
      -----
      - If `points` is provided as a list, it will be converted to a `GrpcPolygonData` object.
      - The created path is added to the modeler primitives of the `pedb` instance.




   .. py:method:: add_point(x, y, incremental=True) -> bool

      Add a point at the end of the path.

      Parameters
      ----------
      x: str, int, float
          X coordinate.
      y: str, in, float
          Y coordinate.
      incremental: bool
          Add point incrementally. If True, coordinates of the added point is incremental to the last point.
          The default value is ``True``.

      Returns
      -------
      bool



   .. py:method:: clone()

      Clone a primitive object with keeping same definition and location.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: create_edge_port(name, position='End', port_type='Wave', reference_layer=None, horizontal_extent_factor=5, vertical_extent_factor=3, pec_launch_width='0.01mm')

      Parameters
      ----------
      name : str
          Name of the port.
      position : str, optional
          Position of the port. The default is ``"End"``, in which case the port is created at the end of the trace.
          Options are ``"Start"`` and ``"End"``.
      port_type : str, optional
          Type of the port. The default is ``"Wave"``, in which case a wave port is created. Options are ``"Wave"``
           and ``"Gap"``.
      reference_layer : str, optional
          Name of the references layer. The default is ``None``. Only available for gap port.
      horizontal_extent_factor : int, optional
          Horizontal extent factor of the wave port. The default is ``5``.
      vertical_extent_factor : int, optional
          Vertical extent factor of the wave port. The default is ``3``.
      pec_launch_width : float, str, optional
          Perfect electrical conductor width of the wave port. The default is ``"0.01mm"``.

      Returns
      -------
          :class:`GapPort <pyedb.grpc.database.ports.port.GapPort>`

      Examples
      --------
      >>> edbapp = pyedb.dotnet.Edb("myproject.aedb")
      >>> sig = appedb.modeler.create_trace([[0, 0], ["9mm", 0]], "TOP", "1mm", "SIG", "Flat", "Flat")
      >>> sig.create_edge_port("pcb_port", "end", "Wave", None, 8, 8)




   .. py:method:: create_via_fence(distance, gap, padstack_name, net_name='GND')

      Create via fences on both sides of the trace.

      Parameters
      ----------
      distance: str, float
          Distance between via fence and trace center line.
      gap: str, float
          Gap between vias.
      padstack_name: str
          Name of the via padstack.
      net_name: str, optional
          Name of the net.




   .. py:property:: center_line
      :type: list[list[float]]


      Path center line

      Returns
      -------
      List[float]




   .. py:method:: get_center_line() -> list[list[float]]

      Retrieve center line points list.

      Returns
      -------
      List[List[float, float]].




   .. py:property:: corner_style
      :type: str


      Path's corner style as string.

      Returns
      -------
      str
          Values supported for the setter `"round"`, `"mitter"`, `"sharp"`




   .. py:property:: end_cap1
      :type: str


      Path's start style as string.

      Returns
      -------
      str
          Values supported for the setter `"flat"`, `"round"`, `"extended"`




   .. py:property:: end_cap2
      :type: str


      Path's end style as string.

      Returns
      -------
      str
          Values supported for the setter `"flat"`, `"round"`, `"extended"`




   .. py:method:: move(vector)

      Move the path by a given vector.

      Parameters
      ----------
      vector: list, tuple
          A list or tuple of two floats representing the x and y components of the movement vector.




