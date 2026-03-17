src.pyedb.grpc.database.definition.package_def
==============================================

.. py:module:: src.pyedb.grpc.database.definition.package_def


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definition.package_def.PackageDef


Module Contents
---------------

.. py:class:: PackageDef(pedb, core=None, name=None, component_part_name=None, extent_bounding_box=None)

   Manages EDB package definitions.

   Parameters
   ----------
   pedb : :class:`Pedb <pyedb.grpc.database.general.Pedb>`
       Pedb object.
   core : :class:`CorePackageDef <ansys.edb.core.definition.package_def.PackageDef>`, optional
       Core package definition object. If not provided, a new package definition will be created using the provided
       name.
   name : str, optional
       Name of the package definition. Required if core is not provided.
   component_part_name : str, optional
       Name of the component part to infer the package definition bounding box. Required if extent_bounding_box is
       not provided.
   extent_bounding_box : list, optional
       Bounding box to define the package definition extent. Format: [[y_min, x_min], [y_max, x_max]]. Required if
       component_part_name is not provided.



   .. py:property:: name
      :type: str



   .. py:property:: exterior_boundary
      :type: ansys.edb.core.geometry.polygon_data.PolygonData


      Get the exterior boundary of a package definition.

      Returns
      -------
      :class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`




   .. py:property:: maximum_power
      :type: float


      Maximum power of the package.

      Returns
      -------
      float
          maximum power value.



   .. py:property:: thermal_conductivity
      :type: float


      Thermal conductivity of the package.

      Returns
      -------
      float
          Thermal conductivity value.




   .. py:property:: theta_jb
      :type: float


      Theta Junction-to-Board of the package.

      Returns
      -------
      float
          Theta jb value.



   .. py:property:: theta_jc
      :type: float


      Theta Junction-to-Case of the package.

      Returns
      -------
      float
          Theta jc value.



   .. py:property:: height
      :type: float


      Height of the package.

      Returns
      -------
      float
          Height value.



   .. py:property:: heat_sink
      :type: HeatSink | None


      Package heat sink.

      Returns
      -------
      :class:`HeatSink <pyedb.grpc.database.utility.heat_sink.HeatSink>`
          HeatSink object.



   .. py:method:: create(edb, name: str) -> PackageDef
      :staticmethod:


      Create a package definition.

      Parameters
      ----------
      edb : :class:`Edb <pyedb.grpc.edb.Edb>`
          Edb object.
      name: str
          Name of the package definition.

      Returns
      -------
      :class:`PackageDef <pyedb.grpc.database.definition.package_def.PackageDef>`
          PackageDef object.



   .. py:method:: set_heatsink(fin_base_height, fin_height, fin_orientation, fin_spacing, fin_thickness) -> pyedb.grpc.database.utility.heat_sink.HeatSink

      Set Heat sink.
      Parameters
      ----------
      fin_base_height : str, float
          Fin base height.
      fin_height : str, float
          Fin height.
      fin_orientation : str
          Fin orientation. Supported values, `x_oriented`, `y_oriented`.
      fin_spacing : str, float
          Fin spacing.
      fin_thickness : str, float
          Fin thickness.



