src.pyedb.grpc.database.geometry.arc_data
=========================================

.. py:module:: src.pyedb.grpc.database.geometry.arc_data


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.geometry.arc_data.ArcData


Module Contents
---------------

.. py:class:: ArcData(core)

   Class managing ArcData.


   .. py:attribute:: core


   .. py:property:: height
      :type: float


      Arc data height.

      Returns
      -------
      float
          Height value.




   .. py:property:: direction
      :type: str


      Arc data direction.

      Returns
      -------
      str
          Direction value.




   .. py:property:: center
      :type: list[float]


      Arc data center.

      Returns
      -------
      [float, float]
          [x value, y value]




   .. py:property:: start
      :type: list[float]


      Arc data start point.

      Returns
      -------
      [float, float]
          [x value, y value]




   .. py:property:: end
      :type: list[float]


      Arc data end point.

      Returns
      -------
      [float, float]
          [x value, y value]




   .. py:property:: midpoint
      :type: list[float]


      Arc data mid point.

      Returns
      -------
      [float, float]
          [x value, y value]




   .. py:property:: points
      :type: list[list[float]]


      Arc data points.

      Returns
      -------
      [[float, float]]
          [[x value, y value]]




   .. py:method:: is_segment() -> bool

      Check if arc data is a segment.

      Returns
      -------
      bool
          True if arc data is a segment, false otherwise.




   .. py:property:: length
      :type: list[float]


      Arc data length.

      Returns
      -------
      float
          Length value.




   .. py:method:: is_point()

      Check if arc data is a point.

      Returns
      -------
      bool
          True if arc data is a point, false otherwise.




   .. py:method:: is_ccw()

      Check if arc data is counter-clockwise.

      Returns
      -------
      bool
          True if arc data is counter-clockwise, false otherwise.




