src.pyedb.grpc.database.primitive.circle
========================================

.. py:module:: src.pyedb.grpc.database.primitive.circle


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.circle.Circle


Module Contents
---------------

.. py:class:: Circle(pedb, core=None)

   Bases: :py:obj:`pyedb.grpc.database.primitive.primitive.Primitive`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", version="2026.1", grpc=True)
   >>> edb_prim = edb.layout.primitives[0]


   .. py:method:: create(layout, layer: Union[str, pyedb.grpc.database.layers.layer.Layer] = None, net: Union[str, pyedb.grpc.database.net.net.Net, None] = None, center_x: float = None, center_y: float = None, radius: float = 0.0)
      :classmethod:



   .. py:method:: get_parameters() -> tuple[float, float, float]

      Returns parameters.

      Returns
      -------
      tuple[
          :class:`.Value`,
          :class:`.Value`,
          :class:`.Value`
      ]

          Returns a tuple in this format:

          **(center_x, center_y, radius)**

          **center_x** : X value of center point.

          **center_y** : Y value of center point.

          **radius** : Radius value of the circle.





   .. py:method:: set_parameters(center_x, center_y, radius)

      Set parameters.

      Parameters
      ----------
      center_x : float
          Center x value.
      center_y : float
          Center y value
      radius : float
          Circle radius.




