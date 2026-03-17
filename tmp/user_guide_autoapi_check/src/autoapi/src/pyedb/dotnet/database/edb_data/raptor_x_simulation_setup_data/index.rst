src.pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data
=================================================================

.. py:module:: src.pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data.RaptorXSimulationSetup
   src.pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data.RaptorXSimulationSettings
   src.pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data.RaptorXGeneralSettings
   src.pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data.RaptorXSimulationAdvancedSettings


Module Contents
---------------

.. py:class:: RaptorXSimulationSetup(pedb, edb_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.simulation_setup.SimulationSetup`


   Manages EDB methods for RaptorX simulation setup.


   .. py:attribute:: logger


   .. py:method:: create(pedb, name)
      :classmethod:



   .. py:property:: setup_type

      Type of the setup.



   .. py:property:: settings

      Get the settings interface for SIwave DC simulation.

      Returns
      -------
      SIWaveSimulationSettings
          An instance of the Settings class providing access to SIwave DC simulation settings.



   .. py:property:: position

      Position in the setup list.



   .. py:method:: add_frequency_sweep(name=None, frequency_sweep=None)

      Add frequency sweep.

      Parameters
      ----------
      name : str, optional
          Name of the frequency sweep.
      frequency_sweep : list, optional
          List of frequency points.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.simulation_setup.EdbFrequencySweep`

      Examples
      --------
      >>> setup1 = edbapp.create_hfss_setup("setup1")
      >>> setup1.add_frequency_sweep(
      ...     frequency_sweep=[
      ...         ["linear count", "0", "1kHz", 1],
      ...         ["log scale", "1kHz", "0.1GHz", 10],
      ...         ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
      ...     ]
      ... )



.. py:class:: RaptorXSimulationSettings(parent)

   Bases: :py:obj:`object`


   .. py:attribute:: logger


   .. py:property:: general_settings


   .. py:property:: general


   .. py:property:: advanced_settings


   .. py:property:: advanced


   .. py:property:: enabled


.. py:class:: RaptorXGeneralSettings(edb_setup_info, parent)

   Bases: :py:obj:`object`


   .. py:attribute:: logger


   .. py:property:: global_temperature

      The simulation temperature. Units: C



   .. py:property:: max_frequency


.. py:class:: RaptorXSimulationAdvancedSettings(edb_setup_info, pedb)

   Bases: :py:obj:`object`


   .. py:attribute:: logger


   .. py:property:: auto_removal_sliver_poly


   .. py:property:: cell_per_wave_length

      This setting describes the number of cells that fit under each wavelength. The wavelength is
      calculated according to the Max Frequency or the Mesh Frequency, unless specified by user through
      this setting. E.g. Setting Cells/Wavelength to 20 means that an object will be divided into 10 cells
      if its width or length is 1/2 wavelengths.
      Units: unitless.



   .. py:property:: edge_mesh

      This option controls both, the thickness and the width of the exterior conductor filament.
      When specified, it prevails over the Mesh Frequency or Max Frequency during mesh calculation.
      Example: "0.8um".



   .. py:property:: eliminate_slit_per_hole

      This is a setting that internally simplifies layouts with strain relief or thermal relief slits and
      holes. It will examine each hole separately against the whole polygon it belongs to.
      If the area of the hole is below the threshold defined in this setting, then the hole will be filled.
      Units: unitless.



   .. py:property:: mesh_frequency

      User can override the default meshing applied by setting a custom frequency for mesh generation.
      Example: "1GHz".



   .. py:property:: net_settings_options

      A list of Name, Value pairs that stores advanced option.



   .. py:property:: override_shrink_fac

      Set the shrink factor explicitly, that is, review what-if scenarios of migrating to half-node
      technologies.
      Units: unitless.



   .. py:property:: plane_projection_factor

      To eliminate unnecessary mesh complexity of "large" metal planes and improve overall extraction time,
      user can define the mesh of certain planes using a combination of the Plane Projection Factor and
      settings of the Nets Advanced Options.
      Units: unitless.



   .. py:property:: use_accelerate_via_extraction

      Setting this option will simplify/merge neighboring vias before sending the layout for processing
      to the mesh engine and to the EM engine.



   .. py:property:: use_auto_removal_sliver_poly

      Setting this option simplifies layouts by aligning slightly misaligned overlapping polygons.



   .. py:property:: use_cells_per_wavelength

      This setting describes the number of cells that fit under each wavelength. The wavelength is calculated
      according to the Max Frequency or the Mesh Frequency, unless specified by user through this setting.



   .. py:property:: use_edge_mesh

      This option controls both, the thickness and the width of the exterior conductor filament.
      When checked, it prevails over the Mesh Frequency or Max Frequency during mesh calculation.



   .. py:property:: use_eliminate_slit_per_holes

      This is a setting that internally simplifies layouts with strain relief or thermal relief slits and
      holes.



   .. py:property:: use_enable_advanced_cap_effects

      Applies all the capacitance related effects such as Conformal Dielectrics, Loading Effect,
      Dielectric Damage.



   .. py:property:: use_enable_etch_transform

      Pre-distorts the layout based on the foundry rules, applying the conductor's bias (positive/negative –
      deflation/inflation) at the conductor edges due to unavoidable optical effects in the manufacturing process.



   .. py:property:: use_enable_hybrid_extraction

      This setting allows the modelling engine to separate the layout into two parts in an attempt to
      decrease the complexity of EM modelling.



   .. py:property:: use_enable_substrate_network_extraction

      This setting models substrate coupling effects using an equivalent distributed RC network.



   .. py:property:: use_extract_floating_metals_dummy

      Enables modeling of floating metals as dummy fills. Captures the effect of dummy fill by extracting
      the effective capacitance between any pairs of metal segments in the design, in the presence of each
      individual dummy metal islands. This setting cannot be used with UseExtractFloatingMetalsFloating.



   .. py:property:: use_extract_floating_metals_floating

      Enables modeling of floating metals as floating nets. Floating metal are grouped into a single entity
      and treated as an independent net. This setting cannot be used with UseExtractFloatingMetalsDummy.



   .. py:property:: use_lde

      Takes into account the variation of resistivity as a function of a conductor’s drawn width and spacing to
      its neighbors or as a function of its local density, due to dishing, slotting, cladding thickness, and so
      on.



   .. py:property:: use_mesh_frequency

      User can override the default meshing applied by the mesh engine by checking this option and setting a
      custom frequency for mesh generation.



   .. py:property:: use_override_shrink_fac

      Set the shrink factor explicitly, that is, review what-if scenarios of migrating to half-node
      technologies.



   .. py:property:: use_plane_projection_factor

      To eliminate unnecessary mesh complexity of "large" metal planes and improve overall
      extraction time, user can define the mesh of certain planes using a combination of the Plane Projection
      Factor and settings of the Nets Advanced Options.



   .. py:property:: use_relaxed_z_axis

      Enabling this option provides a simplified mesh along the z-axis.



