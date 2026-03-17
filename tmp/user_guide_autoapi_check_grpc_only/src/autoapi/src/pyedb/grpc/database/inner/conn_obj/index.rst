src.pyedb.grpc.database.inner.conn_obj
======================================

.. py:module:: src.pyedb.grpc.database.inner.conn_obj


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.inner.conn_obj.ConnObj


Module Contents
---------------

.. py:class:: ConnObj(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.inner.layout_obj.LayoutObj`


   Represents a layout object.


   .. py:method:: get_em_properties() -> pyedb.generic.product_property.EMProperties

      Get EM properties.



   .. py:method:: set_em_properties(em_properties: pyedb.generic.product_property.EMProperties)


   .. py:property:: dcir_equipotential_region
      :type: bool


      Get DCIR equipotential region property of a primitive or a padstack instance.



