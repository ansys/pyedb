src.pyedb.dotnet.database.utilities.obj_base
============================================

.. py:module:: src.pyedb.dotnet.database.utilities.obj_base


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.utilities.obj_base.SystemObject
   src.pyedb.dotnet.database.utilities.obj_base.BBox
   src.pyedb.dotnet.database.utilities.obj_base.ObjBase


Module Contents
---------------

.. py:class:: SystemObject(pedb: pyedb.dotnet.edb.Edb, edb_object)

   Bases: :py:obj:`object`


   .. py:property:: core


.. py:class:: BBox(pedb, edb_object=None, point_1=None, point_2=None)

   Bounding box.


   .. py:property:: point_1


   .. py:property:: point_2


   .. py:property:: corner_points


.. py:class:: ObjBase(pedb: pyedb.dotnet.edb.Edb, edb_object)

   Bases: :py:obj:`SystemObject`


   Manages EDB functionalities for a base object.


   .. py:property:: is_null

      Flag indicating if this object is null.



   .. py:property:: type

      Type of the edb object.



   .. py:property:: name

      Name of the definition.



