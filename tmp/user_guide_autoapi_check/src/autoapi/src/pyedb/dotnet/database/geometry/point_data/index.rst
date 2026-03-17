src.pyedb.dotnet.database.geometry.point_data
=============================================

.. py:module:: src.pyedb.dotnet.database.geometry.point_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.geometry.point_data.PointData


Module Contents
---------------

.. py:class:: PointData(pedb: Any, edb_object: Any | None = None)

   Point Data.


   .. py:method:: create_from_x(pedb: Any, x: float) -> PointData
      :classmethod:


      Create a new PointData object.



   .. py:method:: create_from_xy(pedb: Any, x: float, y: float) -> PointData
      :classmethod:


      Create a new PointData object.



   .. py:property:: x
      :type: str


      X value of point.



   .. py:property:: x_evaluated
      :type: float



   .. py:property:: y
      :type: str


      Y value of point.



   .. py:property:: y_evaluated
      :type: float



