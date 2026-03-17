src.pyedb.grpc.database.simulation_setup.raptor_x_advanced_settings
===================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.raptor_x_advanced_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.raptor_x_advanced_settings.RaptorXAdvancedSettings


Module Contents
---------------

.. py:class:: RaptorXAdvancedSettings(pedb, core: ansys.edb.core.simulation_setup.raptor_x_simulation_settings.RaptorXAdvancedSettings)

   Raptor X advanced settings class.


   .. py:attribute:: core


   .. py:property:: advanced_options
      :type: dict[str, list[str]]


      Get advanced options as a dictionary.



   .. py:property:: auto_removal_sliver_poly
      :type: float


      Automatic sliver polygon removal tolerance.



   .. py:property:: cell_per_wave_length

      Number of cells that fit under each wavelength.

      .. deprecated:: 0.70.0
            Use :attr:`cells_per_wavelength` instead.



   .. py:property:: cells_per_wavelength
      :type: int


      Number of cells that fit under each wavelength.

      Returns
      -------
      int
          Number of cells per wavelength.



   .. py:property:: edge_mesh
      :type: float


      Thickness and width of the exterior conductor filament.



   .. py:property:: eliminate_slit_per_hole

      Threshold for strain or thermal relief slits and hole polygon areas.

      .. deprecated:: 0.70.0
            Use :attr:`eliminate_slit_per_holes` instead.



   .. py:property:: eliminate_slit_per_holes
      :type: float


      Threshold for strain or thermal relief slits and hole polygon areas.



   .. py:property:: mesh_frequency
      :type: float


      Frequency at which the mesh is generated.



   .. py:property:: net_settings_options
      :type: dict[str, list[str]]


      Get net settings options as a dictionary.



   .. py:property:: override_shrink_fac

      Override shrink factor for polygon edges.

      .. deprecated:: 0.70.0
            Use :attr:`override_shrink_factor` instead.



   .. py:property:: override_shrink_factor
      :type: float


      Override shrink factor for polygon edges.



   .. py:property:: plane_projection_factor
      :type: float


      Plane projection factor for reducing the mesh complexity of large metal planes.



   .. py:property:: use_accelerate_via_extraction
      :type: bool


      Flag indicating if neighboring vias are simplified/merged.



   .. py:property:: use_auto_removal_sliver_poly
      :type: bool


      Flag indicating if slight misaligned overlapping polygons are to be automatically aligned.



   .. py:property:: use_cells_per_wavelength
      :type: bool


      Flag indicating if cells per wavelength are used.



   .. py:property:: use_edge_mesh
      :type: bool


      Flag indicating if edge mesh is used.



   .. py:property:: use_eliminate_slit_per_holes
      :type: bool


      Flag indicating if elimination of slits and holes is used.



   .. py:property:: use_enable_advanced_cap_effects
      :type: bool


      Flag indicating if capacitance-related effects such as conformal dielectrics are applied.



   .. py:property:: use_enable_etch_transform
      :type: bool


      Flag indicating if layout is "pre-distorted" based on foundry rules.



   .. py:property:: defuse_enable_hybrid_extraction
      :type: bool


      Flag indicating if the modeler is to split the layout into two parts in an attempt to decrease
      the complexity.



   .. py:property:: use_enable_substrate_network_extraction
      :type: bool


      Flag indicating if modeling of substrate coupling effects is enabled using equivalent distributed RC
      networks.



   .. py:property:: use_extract_floating_metals_dummy
      :type: bool


      Flag indicating if floating metals are modeled as dummy fills.



   .. py:property:: use_extract_floating_metals_floating
      :type: bool


      Flag indicating if floating metals are modeled as floating nets.



   .. py:property:: use_lde
      :type: bool


      Flag indicating if variations in resistivity are taken into account.



   .. py:property:: use_mesh_frequency
      :type: bool


      Flag indicating if mesh frequency is used.



   .. py:property:: use_override_shrink_fac

      Flag indicating if override shrink factor is used.

      .. deprecated:: 0.70.0
            Use :attr:`use_override_shrink_factor` instead.



   .. py:property:: use_override_shrink_factor
      :type: bool


      Flag indicating if override shrink factor is used.



   .. py:property:: use_plane_projection_factor
      :type: bool


      Flag indicating if plane projection factor is used.



   .. py:property:: use_relaxed_z_axis
      :type: bool


      Flag indicating if simplified meshing is used along the z axis.



