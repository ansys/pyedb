src.pyedb.dotnet.database.utilities.heatsink
============================================

.. py:module:: src.pyedb.dotnet.database.utilities.heatsink


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.utilities.heatsink.HeatSink


Module Contents
---------------

.. py:class:: HeatSink(pedb, edb_object=None)

   Heatsink model description.

   Parameters
   ----------
   pedb : :class:`pyedb.dotnet.edb.Edb`
       Inherited object.
   edb_object : :class:`Ansys.Ansoft.Edb.Utility.HeatSink`,


   .. py:property:: fin_base_height
      :type: float


      The base elevation of the fins.

      Returns
      -------
          float



   .. py:property:: fin_height
      :type: float


      The fin height.

      Returns
      -------
          float



   .. py:property:: fin_orientation
      :type: str


      The fin orientation.

      Returns
      -------
          str, can be either x_oriented", "y_oriented" or "other_oriented"



   .. py:property:: fin_spacing
      :type: float


      The fin spacing.

      Returns
      -------
          float



   .. py:property:: fin_thickness
      :type: float


      The fin thickness.

      Returns
      -------
          float



