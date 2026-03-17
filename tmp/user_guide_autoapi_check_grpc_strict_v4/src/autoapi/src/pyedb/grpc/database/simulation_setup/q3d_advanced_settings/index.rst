src.pyedb.grpc.database.simulation_setup.q3d_advanced_settings
==============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.q3d_advanced_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.q3d_advanced_settings.Q3DAdvancedSettings


Module Contents
---------------

.. py:class:: Q3DAdvancedSettings(pedb, core: ansys.edb.core.simulation_setup.q3d_simulation_settings.Q3DAdvancedSettings)

   Q3D advanced simulation settings.

   Parameters
   ----------
   pedb : :class:`Edb < pyedb.grpc.edb.Edb>`
       Inherited object.


   .. py:attribute:: core


   .. py:property:: defeature_absolute_length
      :type: float


      Absolute length used as tolerance when defeaturing polygons.

      Returns
      -------
      float
          Defeature absolute length value.



   .. py:property:: defeature_ratio
      :type: float


      Extent ratio used as tolerance when defeaturing polygons.

      Returns
      -------
      float
          Defeature ratio value.



   .. py:property:: healing_option
      :type: int


      Healing option.

      Returns
      -------
      int
          Healing option value.



   .. py:property:: ic_mode_auto_resolution
      :type: bool


      Flag indicating if model resolution is automatically calculated for IC designs.

      Returns
      -------
      bool
          IC mode auto resolution value.



   .. py:property:: ic_mode_length
      :type: float


      Model resolution to use when manually setting the model resolution of IC designs.

      Returns
      -------
      float
          IC mode length value.



   .. py:property:: max_passes
      :type: int


      Maximum number of mesh refinement cycles to perform.

      Returns
      -------
      int
          Max passes value.



   .. py:property:: max_refine_per_pass
      :type: float


      How many tetrahedra are added at each iteration of the adaptive refinement process.

      Returns
      -------
      float
          Max refine per pass value.



   .. py:property:: mesh_for_via_plating
      :type: bool


      Flag indicating whether to mesh the via plating.

      Returns
      -------
      bool
          Mesh for via plating value.



   .. py:property:: min_converged_passes
      :type: int


      Minimum number of converged passes before stopping the adaptive refinement process.

      Returns
      -------
      int
          Min converged passes value.



   .. py:property:: min_passes
      :type: int


      Minimum number of mesh refinement cycles to perform.

      Returns
      -------
      int
          Min passes value.



   .. py:property:: num_via_density
      :type: float


      Spacing between vias.

      Returns
      -------
      float
          Num via density value.



   .. py:property:: num_via_sides
      :type: int


      Number of sides to use when meshing vias.

      Returns
      -------
      int
          Num via sides value.



   .. py:property:: percent_error
      :type: float


      Target percent error for adaptive mesh refinement.

      Returns
      -------
      float
          Percent error value.



   .. py:property:: remove_floating_geometry
      :type: bool


      Flag indicating if a geometry not connected to any other geometry is removed.

      Returns
      -------
      bool
          Remove floating geometry value.



   .. py:property:: small_void_area
      :type: float


      Voids with an area smaller than this value are ignored during simulation.

      Returns
      -------
      float
          Small void area value.



   .. py:property:: union_polygons
      :type: bool


      Flag indicating if polygons are united before meshing.

      Returns
      -------
      bool
          Union polygons value.



   .. py:property:: use_defeature
      :type: bool


      Flag indicating if defeaturing is used when meshing.

      Returns
      -------
      bool
          Use defeature value.



   .. py:property:: use_defeature_absolute_length
      :type: bool


      Flag indicating if absolute length or extent ratio is used when defeaturing polygons.

      Returns
      -------
      bool
          Use defeature absolute length value.



   .. py:property:: via_material
      :type: str


      Material used for vias.

      Returns
      -------
      str
          Via material value.



