src.pyedb.grpc.database.utility.heat_sink
=========================================

.. py:module:: src.pyedb.grpc.database.utility.heat_sink


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.heat_sink.HeatSink


Module Contents
---------------

.. py:class:: HeatSink(pedb, core)

   Heatsink model description.

   Parameters
   ----------
   pedb : :class:`Edb < pyedb.grpc.edb.Edb>`
       Inherited object.


   .. py:property:: fin_base_height
      :type: float


      The base elevation of the fins.

      Returns
      -------
      float
          Height value.



   .. py:property:: fin_height
      :type: float


      Fin height.

      Returns
      -------
      float
          Fin height value.




   .. py:property:: fin_orientation
      :type: str


      Fin orientation.

      Returns
      -------
      str
          Fin orientation.



   .. py:property:: fin_spacing
      :type: float


      Fin spacing.

      Returns
      -------
      float
          Fin spacing value.




   .. py:property:: fin_thickness
      :type: float


      Fin thickness.

      Returns
      -------
      float
          Fin thickness value.




