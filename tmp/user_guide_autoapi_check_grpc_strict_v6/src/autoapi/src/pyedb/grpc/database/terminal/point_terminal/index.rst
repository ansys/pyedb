src.pyedb.grpc.database.terminal.point_terminal
===============================================

.. py:module:: src.pyedb.grpc.database.terminal.point_terminal


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.point_terminal.mapping_boundary_type


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.point_terminal.PointTerminal


Module Contents
---------------

.. py:data:: mapping_boundary_type

.. py:class:: PointTerminal(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.terminal.terminal.Terminal`


   Manages point terminal properties.


   .. py:method:: create(layout, net, layer, name, point) -> PointTerminal
      :classmethod:


      Create a point terminal.

      Parameters
      ----------
      layout : :class: <``Layout` pyedb.grpc.database.layout.layout.Layout>
          Layout object associated with the terminal.
      net : Net
          :class: `Net` <pyedb.grpc.database.net.net.Net> object associated with the terminal.
      name : str
          Terminal name.
      point : [float, float]
          [x,y] location of the terminal.
      layer : str
          Layer name.
      net : :class: <``Net` pyedb.grpc.database.net.net.Net>, optional
          Net object associated with the terminal. If None, the terminal will be
          associated with the ground net.

      Returns
      -------
      PointTerminal
          Point terminal object.



   .. py:property:: is_reference_terminal
      :type: bool


      Whether the terminal is a reference terminal.

      Returns
      -------
      bool
          True if the terminal is a reference terminal, False otherwise.




   .. py:property:: point
      :type: tuple[float, float]


      Terminal point.

      Returns
      -------
      tuple[float, float]




   .. py:property:: location
      :type: tuple[float, float]


      Terminal position.

      Returns
      -------
      tuple[float, float] : (x,y])




   .. py:property:: reference_layer

      Reference layer of the terminal.

      Returns
      -------
      :class:`Layer <pyedb.grpc.database.layer.layer.Layer>`



   .. py:property:: layer

      Layer that the point terminal is placed on.



