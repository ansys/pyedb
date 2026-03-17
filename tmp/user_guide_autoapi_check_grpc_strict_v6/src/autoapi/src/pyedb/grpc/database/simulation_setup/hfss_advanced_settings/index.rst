src.pyedb.grpc.database.simulation_setup.hfss_advanced_settings
===============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_advanced_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_advanced_settings.HFSSAdvancedSettings


Module Contents
---------------

.. py:class:: HFSSAdvancedSettings(parent)

   .. py:attribute:: core


   .. py:property:: defeature_abs_length
      :type: str


      Absolute length used as tolerance when defeaturing polygons.

      .. deprecated:: 0.77.3
          Use :attr:`defeature_absolute_length` instead.




   .. py:property:: defeature_absolute_length
      :type: str


      Absolute length used as tolerance when defeaturing polygons.

      Returns
      -------
      str
          Length value.




   .. py:property:: defeature_ratio
      :type: float


      Extent ratio used as tolerance when defeaturing polygons.

      Returns
      -------
      float
          Ratio value.




   .. py:property:: healing_option
      :type: int


      Enable/disable healing of mis-aligned points and edges.

      Returns
      -------
      int
          Healing option value.




   .. py:property:: ic_mode_auto_resolution
      :type: bool


      Flag indicating if model resolution is automatically calculated for IC designs..

      Returns
      -------
      bool
          True if IC mode auto resolution is enabled, False otherwise.




   .. py:property:: mesh_for_via_plating
      :type: bool


      Flag indicating if meshing for via plating is enabled.

      Returns
      -------
      bool
          True if meshing for via plating is enabled, False otherwise.




   .. py:property:: model_type
      :type: str


      HFSS model type.

      Returns
      -------
      str
          Model type name.




   .. py:property:: via_density
      :type: float


      Density of vias.

      .. deprecated:: 0.77.3
          Use :attr:`num_via_density` instead.




   .. py:property:: num_via_density
      :type: float


      Spacing between vias.

      Returns
      -------
      int
          Spacing value.




   .. py:property:: via_num_sides
      :type: int


      Number of sides a via is considered to have.

      .. deprecated:: 0.77.3
          Use :attr:`num_via_sides` instead.




   .. py:property:: num_via_sides
      :type: int


      Number of sides a via is considered to have.

      Returns
      -------
      int
          Number of via sides value.




   .. py:property:: remove_floating_geometry
      :type: bool


      Flag indicating if a geometry not connected to any other geometry is removed.

      Returns
      -------
      bool
          True if floating geometry is removed, False otherwise.




   .. py:property:: small_void_area
      :type: float


      Voids with an area smaller than this value are ignored during simulation.

      Returns
      -------
      float
          Small void area value.




   .. py:property:: union_polygons
      :type: bool


      Flag indicating if polygons are unioned.

      Returns
      -------
      bool
          True if polygons are unioned, False otherwise.




   .. py:property:: use_defeature
      :type: bool


      Flag indicating if defeaturing is used.

      Returns
      -------
      bool
          True if defeaturing is used, False otherwise.




   .. py:property:: use_defeature_abs_length
      :type: bool


      Flag indicating if absolute length defeaturing is used.

      .. deprecated:: 0.77.3
          Use :attr:`use_defeature_absolute_length` instead.




   .. py:property:: use_defeature_absolute_length
      :type: bool


      Flag indicating if absolute length or extent ratio is used when defeaturing polygons.

      Returns
      -------
      bool
          True if absolute length defeaturing is used, False otherwise.




   .. py:property:: via_material
      :type: str


      Default via material.

      Returns
      -------
      str
          Via material name.




   .. py:property:: via_style
      :type: str


      Via style.

      .. deprecated:: 0.77.3
          Use :attr:`via_model_type` instead.




   .. py:property:: via_model_type
      :type: str


      Via model type.

      Returns
      -------
      str
          Via model type name.




