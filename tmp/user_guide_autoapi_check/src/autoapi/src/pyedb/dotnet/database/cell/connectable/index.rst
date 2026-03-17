src.pyedb.dotnet.database.cell.connectable
==========================================

.. py:module:: src.pyedb.dotnet.database.cell.connectable


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.connectable.Connectable


Module Contents
---------------

.. py:class:: Connectable(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.layout_obj.LayoutObj`


   Manages EDB functionalities for a connectable object.


   .. py:property:: net

      Net Object.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetsData`



   .. py:property:: net_name

      Get the primitive layer name.


      Returns
      -------
      str



   .. py:property:: component

      Component connected to this object.

      Returns
      -------
      :class:`dotnet.database.edb_data.nets_data.EDBComponent`



   .. py:property:: component_name

      Get the name of the component connected to this object.



   .. py:method:: get_connected_objects()

      Get connected objects.

      Returns
      -------
      list



   .. py:method:: get_connected_object_id_set()

      Produce a list of all geometries physically connected to a given layout object.

      Returns
      -------
      list
          Found connected objects IDs with Layout object.



   .. py:method:: get_em_properties() -> pyedb.generic.product_property.EMProperties


   .. py:method:: set_em_properties(em_properties: pyedb.generic.product_property.EMProperties)


   .. py:property:: dcir_equipotential_region
      :type: bool


      Get or set whether this primitive or padstack instance has a DCIR equipotential region. If this padstack
      instance has pads on multiple layers, the region is set on top layer.



