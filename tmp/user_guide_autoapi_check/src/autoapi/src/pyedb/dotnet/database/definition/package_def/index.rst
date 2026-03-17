src.pyedb.dotnet.database.definition.package_def
================================================

.. py:module:: src.pyedb.dotnet.database.definition.package_def


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.definition.package_def.PackageDef


Module Contents
---------------

.. py:class:: PackageDef(pedb, edb_object=None, name=None, component_part_name=None, extent_bounding_box=None)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.obj_base.ObjBase`


   Manages EDB functionalities for package definitions.

   Parameters
   ----------
   pedb : :class:`pyedb.edb`
       Edb object.
   edb_object : object
   Edb PackageDef Object
       component_part_name : str, optional
       Part name of the component.
   extent_bounding_box : list, optional
       Bounding box defines the shape of the package. For example, [[0, 0], ["2mm", "2mm"]].



   .. py:method:: delete()

      Delete a package definition object from the database.



   .. py:property:: exterior_boundary

      Get the exterior boundary of a package definition.



   .. py:property:: maximum_power

      Maximum power of the package.



   .. py:property:: thermal_conductivity

      Adding this property for compatibility with grpc.



   .. py:property:: therm_cond

      Thermal conductivity of the package.

      ..deprecated:: 0.48.0
         Use: func:`thermal_conductivity` property instead.



   .. py:property:: theta_jb

      Theta Junction-to-Board of the package.



   .. py:property:: theta_jc

      Theta Junction-to-Case of the package.



   .. py:property:: height

      Height of the package.



   .. py:method:: set_heatsink(fin_base_height, fin_height, fin_orientation, fin_spacing, fin_thickness)


   .. py:property:: heat_sink

      Component heatsink.



