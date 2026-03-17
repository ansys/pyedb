src.pyedb.grpc.database.simulation_setup.hfss_pi_advanced_settings
==================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_pi_advanced_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_pi_advanced_settings.HFSSPIAdvancedSettings


Module Contents
---------------

.. py:class:: HFSSPIAdvancedSettings(pedb, core: ansys.edb.core.simulation_setup.hfss_pi_simulation_settings.HFSSPIAdvancedSettings)

   HFSS PI simulation advanced settings class.


   .. py:property:: arc_to_chord_error
      :type: float


      Arc to chord error value.

      Returns
      -------
      float
          Arc to chord error value.



   .. py:property:: auto_model_resolution
      :type: bool


      Flag indicating if model resolution is automatically calculated.

      Returns
      -------
      bool
          Auto model resolution value.



   .. py:property:: max_num_arc_points
      :type: int


      Maximum number of points used to approximate arcs.

      Returns
      -------
      int
          Maximum number of arc points.



   .. py:property:: mesh_for_via_plating
      :type: bool


      Flag indicating if meshing for via plating is enabled.

      Returns
      -------
      bool
          Mesh for via plating value.



   .. py:property:: model_resolution_length
      :type: float


      Model resolution to use when manually setting the model resolution.

      Returns
      -------
      float
          Model resolution length value.



   .. py:property:: num_via_sides
      :type: int


      Number of sides a via is considered to have.

      Returns
      -------
      int
          Number of via sides.



   .. py:property:: remove_floating_geometry
      :type: bool


      Flag indicating if a geometry not connected to any other geometry is removed.

      Returns
      -------
      bool
          Remove floating geometry value.



   .. py:property:: small_plane_area
      :type: float


      Planes with an area smaller than this value are ignored during simulation.

      Returns
      -------
      float
          Small plane area value.



   .. py:property:: small_void_area
      :type: float


      Voids with an area smaller than this value are ignored during simulation.

      Returns
      -------
      float
          Small void area value.



   .. py:property:: use_arc_chord_error_approx
      :type: bool


      Flag indicating if arc chord error approximation is used.

      Returns
      -------
      bool
          Use arc to chord error approximation value.



   .. py:property:: via_material
      :type: str


      Default via material.

      Returns
      -------
      str
          Via material name.



   .. py:property:: zero_metal_layer_thickness
      :type: float


      Pwr/Gnd layers with a thickness smaller than this value are simplified during simulation.

      Returns
      -------
      float
          Zero metal layer thickness value.



