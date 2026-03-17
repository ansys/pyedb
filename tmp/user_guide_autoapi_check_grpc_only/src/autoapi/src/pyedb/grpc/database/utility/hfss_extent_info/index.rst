src.pyedb.grpc.database.utility.hfss_extent_info
================================================

.. py:module:: src.pyedb.grpc.database.utility.hfss_extent_info


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.hfss_extent_info.HfssExtentInfo


Module Contents
---------------

.. py:class:: HfssExtentInfo(pedb)

   Manages EDB functionalities for HFSS extent information.

   Parameters
   ----------
   pedb : :class:`pyedb.grpc.edb.Edb`
       Inherited EDB object.


   .. py:attribute:: core


   .. py:attribute:: extent_type_mapping


   .. py:attribute:: hfss_extent_type


   .. py:method:: get_air_box_horizontal_extent() -> (float, bool)

      Size of horizontal extent for the air box.

      Returns
      -------
      float
          Air box horizontal extent value.



   .. py:method:: set_air_box_horizontal_extent(size: float, is_multiple: bool = True)


   .. py:method:: get_air_box_positive_vertical_extent() -> (float, bool)

      Negative vertical extent for the air box.

      Returns
      -------
      float
          Air box positive vertical extent value.




   .. py:method:: set_air_box_positive_vertical_extent(size: float, is_multiple: bool)


   .. py:method:: get_air_box_negative_vertical_extent() -> (float, bool)

      Negative vertical extent for the airbox.

      Returns
      -------
      float
          Air box negative vertical extent value.




   .. py:method:: set_air_box_negative_vertical_extent(size: float, is_multiple: bool = True)


   .. py:property:: base_polygon
      :type: any


      Base polygon.

      Returns
      -------
      :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`



   .. py:property:: dielectric_base_polygon
      :type: any


      Dielectric base polygon.

      Returns
      -------
      :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`



   .. py:method:: get_dielectric_extent() -> (float, bool)

      Dielectric extent size.

      Returns
      -------
      float
          Dielectric extent size value.



   .. py:method:: set_dielectric_extent(size: float, is_multiple: bool = True)


   .. py:property:: dielectric_extent_type
      :type: str


      Dielectric extent type.

      Returns
      -------
      str
          Dielectric extent type.




   .. py:property:: extent_type
      :type: str


      Extent type.

      Returns
      -------
      str
          Extent type.



   .. py:property:: honor_user_dielectric
      :type: bool


      Honor user dielectric.

      Returns
      -------
      bool



   .. py:property:: is_pml_visible
      :type: bool


      Whether visibility of the PML is enabled.

      Returns
      -------
      bool




   .. py:property:: open_region_type
      :type: str


      Open region type.

      Returns
      -------
      str
          Open region type.



   .. py:property:: operating_freq
      :type: float


      PML Operating frequency.

      Returns
      -------
      float
          Operating frequency value.




   .. py:property:: radiation_level
      :type: float


      PML Radiation level to calculate the thickness of boundary.

      Returns
      -------
      float
          Boundary thickness value.




   .. py:property:: sync_air_box_vertical_extent
      :type: bool


      Vertical extent of the sync air box.

      Returns
      -------
      bool
          Synchronise vertical extent.




   .. py:property:: truncate_air_box_at_ground
      :type: bool


      Truncate air box at ground.

      Returns
      -------
      bool
          Truncate air box at ground.




   .. py:property:: use_open_region
      :type: bool


      Whether using an open region is enabled.

      Returns
      -------
      bool
          Use open region.




   .. py:property:: use_xy_data_extent_for_vertical_expansion
      :type: bool


      Whether using the xy data extent for vertical expansion is enabled.

      Returns
      -------
      bool
          USe x y data extent for vertical expansion.




   .. py:method:: load_config(config)

      Load HFSS extent configuration.

      Parameters
      ----------
      config: dict
          Parameters of the HFSS extent information.



   .. py:method:: export_config()

      Export HFSS extent information.

      Returns
      -------
      dict
          Parameters of the HFSS extent information.



