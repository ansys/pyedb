src.pyedb.dotnet.database.sim_setup_data.io.siwave
==================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.io.siwave


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.io.siwave.SettingsBase
   src.pyedb.dotnet.database.sim_setup_data.io.siwave.AdvancedSettings
   src.pyedb.dotnet.database.sim_setup_data.io.siwave.DCSettings
   src.pyedb.dotnet.database.sim_setup_data.io.siwave.DCAdvancedSettings


Module Contents
---------------

.. py:class:: SettingsBase(parent)

   Bases: :py:obj:`object`


   Provide base settings.


   .. py:property:: sim_setup_info

      EDB internal simulation setup object.



   .. py:method:: get_configurations()

      Get all attributes.

      Returns
      -------
      dict



   .. py:method:: restore_default()


.. py:class:: AdvancedSettings(parent)

   Bases: :py:obj:`SettingsBase`


   Provide base settings.


   .. py:attribute:: defaults


   .. py:attribute:: si_defaults


   .. py:attribute:: pi_defaults


   .. py:method:: set_si_slider(value)


   .. py:method:: set_pi_slider(value)


   .. py:property:: include_inter_plane_coupling

      Whether to turn on InterPlane Coupling.
      The setter will also enable custom settings.

      Returns
      -------
      bool
          ``True`` if interplane coupling is used, ``False`` otherwise.



   .. py:property:: xtalk_threshold

      XTalk threshold.
      The setter enables custom settings.

      Returns
      -------
      str



   .. py:property:: min_void_area

      Minimum void area to include.

      Returns
      -------
      bool



   .. py:property:: min_pad_area_to_mesh

      Minimum void pad area to mesh to include.

      Returns
      -------
      bool



   .. py:property:: min_plane_area_to_mesh

      Minimum plane area to mesh to include.

      Returns
      -------
      bool



   .. py:property:: snap_length_threshold

      Snapping length threshold.

      Returns
      -------
      str



   .. py:property:: return_current_distribution

      Whether to enable the return current distribution.
      This option is used to accurately model the change of the characteristic impedance
      of transmission lines caused by a discontinuous ground plane. Instead of injecting
      the return current of a trace into a single point on the ground plane,
      the return current for a high impedance trace is spread out.
      The trace return current is not distributed when all traces attached to a node
      have a characteristic impedance less than 75 ohms or if the difference between
      two connected traces is less than 25 ohms.

      Returns
      -------
      bool
          ``True`` if return current distribution is used, ``False`` otherwise.



   .. py:property:: ignore_non_functional_pads

      Exclude non-functional pads.

      Returns
      -------
      bool
          `True`` if functional pads have to be ignored, ``False`` otherwise.



   .. py:property:: include_coplane_coupling

      Whether to enable coupling between traces and adjacent plane edges.
      This option provides a model for crosstalk between signal lines and planes.
      Plane edges couple to traces when they are parallel.
      Traces and coplanar edges that are oblique to each other do not overlap
      and cannot be considered for coupling.


      Returns
      -------
      bool
          ``True`` if coplane coupling is used, ``False`` otherwise.



   .. py:property:: include_fringe_coupling

      Whether to include the effect of fringe field coupling between stacked cavities.


      Returns
      -------
      bool
          ``True`` if fringe coupling is used, ``False`` otherwise.



   .. py:property:: include_split_plane_coupling

      Whether to account for coupling between adjacent parallel plane edges.
      Primarily, two different cases are being considered:
      - Plane edges that form a split.
      - Plane edges that form a narrow trace-like plane.
      The former leads to crosstalk between adjacent planes for which
      a specific coupling model is applied. For the latter, fringing effects
      are considered to model accurately the propagation characteristics
      of trace-like cavities. Further, the coupling between narrow planes is
      also modeled by enabling this feature.

      Returns
      -------
      bool
          ``True`` if split plane coupling is used, ``False`` otherwise.



   .. py:property:: include_infinite_ground

      Whether to Include a ground plane to serve as a voltage reference for traces and planes
      if they are not defined in the layout.

      Returns
      -------
      bool
          ``True`` if infinite ground is used, ``False`` otherwise.



   .. py:property:: include_trace_coupling

      Whether to model coupling between adjacent traces.
      Coupling is considered for parallel and almost parallel trace segments.

      Returns
      -------
      bool
          ``True`` if trace coupling is used, ``False`` otherwise.



   .. py:property:: include_vi_sources

      Whether to include the effect of parasitic elements from voltage and
      current sources.

      Returns
      -------
      bool
          ``True`` if vi sources is used, ``False`` otherwise.



   .. py:property:: infinite_ground_location

      Elevation of the infinite unconnected ground plane placed under the design.

      Returns
      -------
      str



   .. py:property:: max_coupled_lines

      Maximum number of coupled lines to build the new coupled transmission line model.

      Returns
      -------
      int



   .. py:property:: mesh_automatic

      Whether to automatically pick a suitable mesh refinement frequency,
      depending on drawing size, number of modes, and/or maximum sweep
      frequency.

      Returns
      -------
      bool
          ``True`` if automatic mesh is used, ``False`` otherwise.



   .. py:property:: perform_erc

      Whether to perform an electrical rule check while generating the solver input.
      In some designs, the same net may be divided into multiple nets with separate names.
      These nets are connected at a "star" point. To simulate these nets, the error checking
      for DC shorts must be turned off. All overlapping nets are then internally united
      during simulation.

      Returns
      -------
      bool
          ``True`` if perform erc is used, ``False`` otherwise.



   .. py:property:: mesh_frequency

      Mesh size based on the effective wavelength at the specified frequency.

      Returns
      -------
      str



.. py:class:: DCSettings(parent)

   Bases: :py:obj:`SettingsBase`


   Provide base settings.


   .. py:attribute:: defaults


   .. py:attribute:: dc_defaults


   .. py:property:: compute_inductance

      Whether to compute Inductance.

      Returns
      -------
      bool
          ``True`` if inductances will be computed, ``False`` otherwise.



   .. py:property:: contact_radius

      Circuit element contact radius.

      Returns
      -------
      str



   .. py:property:: dc_slider_position

      DC simulation accuracy level slider position. This property only change slider position.
      Options:
      0- ``optimal speed``
      1- ``balanced``
      2- ``optimal accuracy``.



   .. py:property:: use_dc_custom_settings

      Whether to use DC custom settings.
      This setting is automatically enabled by other properties when needed.

      Returns
      -------
      bool
          ``True`` if custom dc settings are used, ``False`` otherwise.



   .. py:property:: plot_jv

      Plot current and voltage distributions.

      Returns
      -------
      bool
          ``True`` if plot JV is used, ``False`` otherwise.



.. py:class:: DCAdvancedSettings(parent)

   Bases: :py:obj:`SettingsBase`


   Provide base settings.


   .. py:attribute:: defaults


   .. py:attribute:: dc_defaults


   .. py:method:: set_dc_slider(value)


   .. py:property:: dc_min_void_area_to_mesh

      DC minimum area below which voids are ignored.

      Returns
      -------
      float



   .. py:property:: dc_min_plane_area_to_mesh

      Minimum area below which geometry is ignored.

      Returns
      -------
      float



   .. py:property:: energy_error

      Energy error.

      Returns
      -------
      float



   .. py:property:: max_init_mesh_edge_length

      Initial mesh maximum edge length.

      Returns
      -------
      float



   .. py:property:: max_num_pass

      Maximum number of passes.

      deprecated: Use `max_num_passes` instead.

      Returns
      -------
      int



   .. py:property:: max_num_passes

      Maximum number of passes.

      Returns
      -------
      int



   .. py:property:: min_num_pass

      Minimum number of passes.

      deprecated: Use `min_num_passes` instead.

      Returns
      -------
      int



   .. py:property:: min_num_passes

      Minimum number of passes.

      Returns
      -------
      int



   .. py:property:: mesh_bondwires

      Mesh bondwires.

      Returns
      -------
      bool



   .. py:property:: mesh_vias

      Mesh vias.

      Returns
      -------
      bool



   .. py:property:: num_bondwire_sides

      Number of bondwire sides.

      deprecated: Use `num_bw_sides` instead.

      Returns
      -------
      int



   .. py:property:: num_bw_sides

      Number of bondwire sides.

      Returns
      -------
      int



   .. py:property:: num_via_sides

      Number of via sides.

      Returns
      -------
      int



   .. py:property:: percent_local_refinement

      Percentage of local refinement.

      Returns
      -------
      float



   .. py:property:: perform_adaptive_refinement

      Whether to perform adaptive mesh refinement.

      Returns
      -------
      bool
          ``True`` if adaptive refinement is used, ``False`` otherwise.



   .. py:property:: refine_bondwires

      Whether to refine mesh along bondwires.

      deprecated: Use `refine_bws` instead.

      Returns
      -------
      bool
          ``True`` if refine bondwires is used, ``False`` otherwise.



   .. py:property:: refine_bws

      Whether to refine mesh along bondwires.

      Returns
      -------
      bool
          ``True`` if refine bondwires is used, ``False`` otherwise.



   .. py:property:: refine_vias

      Whether to refine mesh along vias.

      Returns
      -------
      bool
          ``True`` if via refinement is used, ``False`` otherwise.




