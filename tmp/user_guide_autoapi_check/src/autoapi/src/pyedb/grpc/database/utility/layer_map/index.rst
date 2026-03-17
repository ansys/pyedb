src.pyedb.grpc.database.utility.layer_map
=========================================

.. py:module:: src.pyedb.grpc.database.utility.layer_map


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.layer_map.LayerMap


Module Contents
---------------

.. py:class:: LayerMap(core)

   .. py:attribute:: core


   .. py:method:: create(direction: str = 'two_way') -> LayerMap
      :classmethod:


      Create a layer map.

      Parameters
      ----------
      direction : str, optional
          Direction of the layer map. Options are "two_way", "forward", and "backward". Default is "two_way".

      Returns
      -------
      LayerMap
          Layer map object.



   .. py:property:: id

      Get the layer map ID.

      Returns
      -------
      int
          Layer map ID.



   .. py:property:: is_null
      :type: bool


      Check if the layer map is null.

      Returns
      -------
      bool
          True if the layer map is null, False otherwise.



   .. py:method:: clear()

      Clear the layer map.



   .. py:method:: get_mapping_backward(layer_id: int) -> int

      Get the backward mapping for a given layer ID.

      Parameters
      ----------
      layer_id : int
          Layer ID to get the backward mapping for.

      Returns
      -------
      int
          Mapped layer ID.



   .. py:method:: get_mapping_forward(layer_id: int) -> int

      Get the forward mapping for a given layer ID.

      Parameters
      ----------
      layer_id : int
          Layer ID to get the forward mapping for.

      Returns
      -------
      int
          Mapped layer ID.



   .. py:method:: set_mapping(layer_id_from: int, layer_id_to: int)

      Set the mapping from one layer ID to another.

      Parameters
      ----------
      layer_id_from : int
          Layer ID to map from.
      layer_id_to : int
          Layer ID to map to.



