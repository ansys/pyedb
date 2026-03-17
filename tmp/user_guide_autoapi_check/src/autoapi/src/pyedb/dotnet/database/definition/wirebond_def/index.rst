src.pyedb.dotnet.database.definition.wirebond_def
=================================================

.. py:module:: src.pyedb.dotnet.database.definition.wirebond_def


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.definition.wirebond_def.WirebondDef
   src.pyedb.dotnet.database.definition.wirebond_def.Jedec4BondwireDef
   src.pyedb.dotnet.database.definition.wirebond_def.Jedec5BondwireDef
   src.pyedb.dotnet.database.definition.wirebond_def.ApdBondwireDef


Module Contents
---------------

.. py:class:: WirebondDef(edb, edb_object)

   .. py:property:: name


   .. py:method:: delete()


   .. py:property:: height


.. py:class:: Jedec4BondwireDef(pedb, edb_object)

   Bases: :py:obj:`WirebondDef`


   .. py:method:: find_by_name(edb, name: str)
      :classmethod:



   .. py:method:: create(edb, name: str, top_to_die_distance: float = 3e-05)
      :classmethod:



.. py:class:: Jedec5BondwireDef(pedb, edb_object)

   Bases: :py:obj:`WirebondDef`


   .. py:method:: find_by_name(edb, name: str)
      :classmethod:



   .. py:method:: create(edb, name: str, top_to_die_distance: float = 3e-05)
      :classmethod:



.. py:class:: ApdBondwireDef(pedb, edb_object)

   Bases: :py:obj:`WirebondDef`


   .. py:method:: find_by_name(edb, name: str)
      :classmethod:



   .. py:method:: create(edb, name: str, top_to_die_distance: float = 3e-05)
      :classmethod:



