src.pyedb.dotnet.database.edb_data.hfss_extent_info
===================================================

.. py:module:: src.pyedb.dotnet.database.edb_data.hfss_extent_info


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.hfss_extent_info.HfssExtentInfo


Module Contents
---------------

.. py:class:: HfssExtentInfo(pedb)

   Manages EDB functionalities for HFSS extent information.

   Parameters
   ----------
   pedb : :class:`pyedb.edb.Edb`
       Inherited EDB object.


   .. py:property:: air_box_horizontal_extent_enabled

      Whether horizontal extent is enabled for the airbox.



   .. py:property:: air_box_horizontal_extent

      Size of horizontal extent for the air box.

      Returns:
      dotnet.database.edb_data.edbvalue.EdbValue



   .. py:method:: set_air_box_horizontal_extent(size: float, is_multiple: bool = True)


   .. py:method:: get_air_box_horizontal_extent()


   .. py:property:: air_box_positive_vertical_extent_enabled

      Whether positive vertical extent is enabled for the air box.



   .. py:property:: air_box_positive_vertical_extent

      Negative vertical extent for the air box.



   .. py:method:: set_air_box_positive_vertical_extent(size: float, is_multiple: bool = True)


   .. py:method:: get_air_box_positive_vertical_extent()


   .. py:property:: air_box_negative_vertical_extent_enabled

      Whether negative vertical extent is enabled for the air box.



   .. py:property:: air_box_negative_vertical_extent

      Negative vertical extent for the airbox.



   .. py:method:: set_air_box_negative_vertical_extent(size: float, is_multiple: bool = True)


   .. py:method:: get_air_box_negative_vertical_extent()


   .. py:property:: base_polygon

      Base polygon.

      Returns
      -------
      :class:`dotnet.database.edb_data.primitives_data.EDBPrimitive`



   .. py:property:: dielectric_base_polygon

      Dielectric base polygon.

      Returns
      -------
      :class:`dotnet.database.edb_data.primitives_data.EDBPrimitive`



   .. py:property:: dielectric_extent_size_enabled

      Whether dielectric extent size is enabled.



   .. py:property:: dielectric_extent_size

      Dielectric extent size.



   .. py:method:: set_dielectric_extent(size: float, is_multiple: bool = True)


   .. py:method:: get_dielectric_extent()


   .. py:property:: dielectric_extent_type

      Dielectric extent type.



   .. py:property:: extent_type

      Extent type.



   .. py:property:: honor_user_dielectric

      Honor user dielectric.



   .. py:property:: is_pml_visible

      Whether visibility of the PML is enabled.



   .. py:property:: open_region_type

      Open region type.



   .. py:property:: operating_freq

      PML Operating frequency.

      Returns
      -------
      pyedb.dotnet.database.edb_data.edbvalue.EdbValue



   .. py:property:: radiation_level

      PML Radiation level to calculate the thickness of boundary.



   .. py:property:: pml_radiation_factor

      PML Radiation level to calculate the thickness of boundary.



   .. py:property:: sync_air_box_vertical_extent

      Vertical extent of the sync air box.



   .. py:property:: truncate_air_box_at_ground

      Truncate air box at ground.



   .. py:property:: use_open_region

      Whether using an open region is enabled.



   .. py:property:: use_xy_data_extent_for_vertical_expansion

      Whether using the xy data extent for vertical expansion is enabled.



   .. py:method:: load_config(config)

      Load HFSS extent configuration.

      Parameters
      ----------
      config: dict
          Parameters of the HFSS extent information.



   .. py:method:: export_config()

      Export HFSS extent information.

      Returns:
      dict
          Parameters of the HFSS extent information.



