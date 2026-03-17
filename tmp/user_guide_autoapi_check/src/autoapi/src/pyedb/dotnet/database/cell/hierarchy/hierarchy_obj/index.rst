src.pyedb.dotnet.database.cell.hierarchy.hierarchy_obj
======================================================

.. py:module:: src.pyedb.dotnet.database.cell.hierarchy.hierarchy_obj


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.hierarchy.hierarchy_obj.HierarchyObj
   src.pyedb.dotnet.database.cell.hierarchy.hierarchy_obj.Group


Module Contents
---------------

.. py:class:: HierarchyObj(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.connectable.Connectable`


   Manages EDB functionalities for a connectable object.


   .. py:property:: component_def
      :type: str


      Return the name of the component definition.

      Returns
      -------
      str
          Name of the component definition.



   .. py:property:: location
      :type: List[float] | None


      Return XY coordinates if available.

      Returns
      -------
      list[float] or None
          [x, y] if available, else None.



.. py:class:: Group(pedb, edb_object)

   Bases: :py:obj:`HierarchyObj`


   Manages EDB functionalities for a connectable object.


   .. py:method:: ungroup(recursive=False) -> bool

      Dissolve a group.

      Parameters
      ----------
      recursive : bool, optional
          If True, all subgroups will also be dissolved.




