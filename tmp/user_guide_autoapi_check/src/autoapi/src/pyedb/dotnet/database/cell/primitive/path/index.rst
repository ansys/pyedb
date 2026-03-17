src.pyedb.dotnet.database.cell.primitive.path
=============================================

.. py:module:: src.pyedb.dotnet.database.cell.primitive.path


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.primitive.path.Path


Module Contents
---------------

.. py:class:: Path(pedb, edb_object=None)

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


   .. py:property:: width

      Path width.

      Returns
      -------
      float
          Path width or None.



   .. py:method:: get_end_cap_style()

      Get path end cap styles.

      Returns
      -------
      tuple[
          :class:`PathEndCapType`,
          :class:`PathEndCapType`
      ]

          Returns a tuple of the following format:

          **(end_cap1, end_cap2)**

          **end_cap1** : End cap style of path start end cap.

          **end_cap2** : End cap style of path end  cap.



   .. py:method:: set_end_cap_style(end_cap1, end_cap2)

      Set path end cap styles.

      Parameters
      ----------
      end_cap1: :class:`PathEndCapType`
          End cap style of path start end cap.
      end_cap2: :class:`PathEndCapType`
          End cap style of path end cap.



   .. py:property:: length

      Path length in meters.

      Returns
      -------
      float
          Path length in meters.



   .. py:method:: add_point(x, y, incremental=False)

      Add a point at the end of the path.

      Parameters
      ----------
      x: str, int, float
          X coordinate.
      y: str, in, float
          Y coordinate.
      incremental: bool
          Add point incrementally. If True, coordinates of the added point is incremental to the last point.
          The default value is ``False``.

      Returns
      -------
      bool



   .. py:method:: get_center_line(to_string=False)

      Get the center line of the trace.

      Parameters
      ----------
      to_string : bool, optional
          Type of return. The default is ``"False"``.

      Returns
      -------
      list




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
          :class:`dotnet.database.edb_data.sources.ExcitationPorts`

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

      Returns
      -------



   .. py:property:: center_line

      :class:`PolygonData <ansys.edb.geometry.PolygonData>`: Center line for this Path.



   .. py:method:: get_center_line_polygon_data()

      Gets center lines of the path as a PolygonData object.



   .. py:method:: set_center_line_polygon_data(polygon_data)

      Sets center lines of the path from a PolygonData object.



   .. py:property:: corner_style

      :class:`PathCornerType`: Path's corner style.



