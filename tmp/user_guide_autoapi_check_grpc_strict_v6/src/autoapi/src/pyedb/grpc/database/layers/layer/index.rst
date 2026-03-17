src.pyedb.grpc.database.layers.layer
====================================

.. py:module:: src.pyedb.grpc.database.layers.layer


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.layers.layer.layer_type_mapping


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.layers.layer.Layer


Module Contents
---------------

.. py:data:: layer_type_mapping

.. py:class:: Layer(core=None, name='', layer_type='undefined', **kwargs)

   Manages Layer.


   .. py:attribute:: core
      :value: None



   .. py:method:: create(name, layer_type: str = 'solder_mask') -> Layer
      :classmethod:


      Parameters
      ----------
      name : str
          Layer name
      layer_type : str
          Layer type

      Returns
      -------
      :class: `Layer <pyedb.`



   .. py:property:: id

      Get the layer ID.



   .. py:method:: update(**kwargs)


   .. py:property:: name
      :type: str


      Get the layer name.



   .. py:property:: properties
      :type: dict[str, str]



   .. py:property:: type
      :type: str



   .. py:property:: is_stackup_layer

      Check if the layer is a stackup layer.



