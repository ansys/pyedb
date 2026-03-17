src.pyedb.dotnet.database.sim_setup_data.data.settings
======================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.data.settings


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.data.settings.AdaptiveSettings
   src.pyedb.dotnet.database.sim_setup_data.data.settings.DefeatureSettings
   src.pyedb.dotnet.database.sim_setup_data.data.settings.AdvancedMeshSettings
   src.pyedb.dotnet.database.sim_setup_data.data.settings.ViaSettings
   src.pyedb.dotnet.database.sim_setup_data.data.settings.CurveApproxSettings
   src.pyedb.dotnet.database.sim_setup_data.data.settings.DcrSettings
   src.pyedb.dotnet.database.sim_setup_data.data.settings.HfssPortSettings
   src.pyedb.dotnet.database.sim_setup_data.data.settings.HfssSolverSettings


Module Contents
---------------

.. py:class:: AdaptiveSettings(parent)

   Bases: :py:obj:`object`


   Manages EDB methods for adaptive settings.


   .. py:property:: adaptive_settings

      Adaptive EDB settings.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.AdaptiveSettings`



   .. py:property:: adaptive_frequency_data_list

      List of all adaptive frequency data.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.AdaptiveFrequencyData`



   .. py:method:: clean_adaptive_frequency_data_list()

      Clean all adaptive frequency data from the list.



   .. py:property:: adapt_type

      Adaptive type.
      Options:
      1- ``kSingle``.
      2- ``kMultiFrequencies``.
      3- ``kBroadband``.
      4- ``kNumAdaptTypes``.

      Returns
      -------
      str



   .. py:property:: basic

      Whether if turn on basic adaptive.

      Returns
      -------
          ``True`` if basic adaptive is used, ``False`` otherwise.



   .. py:property:: do_adaptive

      Whether if adaptive mesh is on.

      Returns
      -------
      bool
          ``True`` if adaptive is used, ``False`` otherwise.




   .. py:property:: max_refinement

      Maximum number of mesh elements to be added per pass.

      Returns
      -------
      int



   .. py:property:: max_refine_per_pass

      Maximum number of mesh elementat that can be added during an adaptive pass.

      Returns
      -------
      int



   .. py:property:: min_passes

      Minimum number of passes.

      Returns
      -------
      int



   .. py:property:: min_converged_passes

      Minimum number of converged passes.

      Returns
      -------
          int



   .. py:property:: save_fields

      Whether to turn on save fields.

      Returns
      -------
      bool
          ``True`` if save fields is used, ``False`` otherwise.



   .. py:property:: save_rad_field_only

      Flag indicating if the saving of only radiated fields is turned on.

      Returns
      -------
      bool
          ``True`` if save radiated field only is used, ``False`` otherwise.




   .. py:property:: use_convergence_matrix

      Whether to turn on the convergence matrix.

      Returns
      -------
      bool
          ``True`` if convergence matrix is used, ``False`` otherwise.




   .. py:property:: use_max_refinement

      Whether to turn on maximum refinement.

      Returns
      -------
      bool
          ``True`` if maximum refinement is used, ``False`` otherwise.



   .. py:method:: add_adaptive_frequency_data(frequency=0, max_num_passes=10, max_delta_s=0.02)

      Add a setup for frequency data.

      Parameters
      ----------
      frequency : str, float
          Frequency with units or float frequency (in Hz).
      max_num_passes : int, optional
          Maximum number of passes. The default is ``10``.
      max_delta_s : float, optional
          Maximum delta S. The default is ``0.02``.

      Returns
      -------
      bool
          ``True`` if method is successful, ``False`` otherwise.



   .. py:method:: add_broadband_adaptive_frequency_data(low_frequency=0, high_frequency=10000000000.0, max_num_passes=10, max_delta_s=0.02)

      Add a setup for frequency data.

      Parameters
      ----------
      low_frequency : str, float
          Frequency with units or float frequency (in Hz).
      high_frequency : str, float
          Frequency with units or float frequency (in Hz).
      max_num_passes : int, optional
          Maximum number of passes. The default is ``10``.
      max_delta_s : float, optional
          Maximum delta S. The default is ``0.02``.

      Returns
      -------
      bool
          ``True`` if method is successful, ``False`` otherwise.



   .. py:method:: add_multi_frequency_adaptive_setup(freq_list, max_num_passes=10, max_delta_s=0.02)

      Add a setup for frequency data.

      Parameters
      ----------
      low_frequency : str, float
          Frequency with units or float frequency (in Hz).
      high_frequency : str, float
          Frequency with units or float frequency (in Hz).
      max_num_passes : int, optional
          Maximum number of passes. The default is ``10``.
      max_delta_s : float, optional
          Maximum delta S. The default is ``0.02``.

      Returns
      -------
      bool
          ``True`` if method is successful, ``False`` otherwise.



.. py:class:: DefeatureSettings(parent)

   Bases: :py:obj:`object`


   Manages EDB methods for defeature settings.


   .. py:property:: defeature_abs_length

      Absolute length for polygon defeaturing.

      Returns
      -------
      str



   .. py:property:: defeature_ratio

      Defeature ratio.

      Returns
      -------
      float



   .. py:property:: healing_option

      Whether to turn on healing of mis-aligned points and edges.
      Options are:
      0- Turn off.
      1- Turn on.

      Returns
      -------
      int



   .. py:property:: model_type

      Model type.
      Options:
      0- General.
      1- IC.

      Returns
      -------
      int



   .. py:property:: remove_floating_geometry

      Whether to remove floating geometries.

      Returns
      -------
      bool
          ``True`` if floating geometry removal is used, ``False`` otherwise.



   .. py:property:: small_void_area

      Small voids to remove area.

      Returns
      -------
      float



   .. py:property:: union_polygons

      Whether to turn on the union of polygons before meshing.

      Returns
      -------
      bool
          ``True`` if union polygons is used, ``False`` otherwise.



   .. py:property:: use_defeature

      Whether to turn on the defeature.

      Returns
      -------
      bool
          ``True`` if defeature is used, ``False`` otherwise.



   .. py:property:: use_defeature_abs_length

      Whether to turn on the defeature absolute length.

      Returns
      -------
      bool
          ``True`` if defeature absolute length is used, ``False`` otherwise.




.. py:class:: AdvancedMeshSettings(parent)

   Bases: :py:obj:`object`


   Manages EDB methods for advanced mesh settings.


   .. py:property:: layer_snap_tol

      Layer snap tolerance. Attempt to align independent stackups in the mesher.

      Returns
      -------
      str




   .. py:property:: mesh_display_attributes

      Mesh display attributes. Set color for mesh display (i.e. ``"#000000"``).

      Returns
      -------
      str



   .. py:property:: replace_3d_triangles

      Whether to turn on replace 3D triangles.

      Returns
      -------
      bool
          ``True`` if replace 3D triangles is used, ``False`` otherwise.




.. py:class:: ViaSettings(parent)

   Bases: :py:obj:`object`


   Manages EDB methods for via settings.


   .. py:property:: via_density

      Via density.

      Returns
      -------
      float



   .. py:property:: via_mesh_plating

      Via mesh plating.

      Returns
      -------
      bool



   .. py:property:: via_material

      Via material.

      Returns
      -------
      str



   .. py:property:: via_num_sides

      Via number of sides.

      Returns
      -------
      int



   .. py:property:: via_style

      Via style.
      Options:
      1- ``k25DViaWirebond``.
      2- ``k25DViaRibbon``.
      3- ``k25DViaMesh``.
      4- ``k25DViaField``.
      5- ``kNum25DViaStyle``.

      Returns
      -------
      str



.. py:class:: CurveApproxSettings(parent)

   Bases: :py:obj:`object`


   Manages EDB methods for curve approximate settings.


   .. py:property:: arc_angle

      Step-size to be used for arc faceting.

      Returns
      -------
      str



   .. py:property:: arc_to_chord_error

      Maximum tolerated error between straight edge (chord) and faceted arc.

      Returns
      -------
      str



   .. py:property:: max_arc_points

      Maximum number of mesh points for arc segments.

      Returns
      -------
      int



   .. py:property:: start_azimuth

      Azimuth angle for first mesh point of the arc.

      Returns
      -------
      str



   .. py:property:: use_arc_to_chord_error

      Whether to turn on the arc-to-chord error setting for arc faceting.

      Returns
      -------
          ``True`` if arc-to-chord error is used, ``False`` otherwise.



.. py:class:: DcrSettings(parent)

   Bases: :py:obj:`object`


   Manages EDB methods for DCR settings.


   .. py:property:: conduction_max_passes

      Conduction maximum number of passes.

      Returns
      -------
      int



   .. py:property:: conduction_min_converged_passes

      Conduction minimum number of converged passes.

      Returns
      -------
      int



   .. py:property:: conduction_min_passes

      Conduction minimum number of passes.

      Returns
      -------
      int



   .. py:property:: conduction_per_error

      WConduction error percentage.

      Returns
      -------
      float



   .. py:property:: conduction_per_refine

      Conduction refinement.

      Returns
      -------
      float



.. py:class:: HfssPortSettings(parent)

   Bases: :py:obj:`object`


   Manages EDB methods for HFSS port settings.


   .. py:property:: max_delta_z0

      Maximum change to Z0 in successive passes.

      Returns
      -------
      float



   .. py:property:: max_triangles_wave_port

      Maximum number of triangles allowed for wave ports.

      Returns
      -------
      int



   .. py:property:: min_triangles_wave_port

      Minimum number of triangles allowed for wave ports.

      Returns
      -------
      int



   .. py:property:: enable_set_triangles_wave_port

      Whether to enable setting of minimum and maximum mesh limits for wave ports.

      Returns
      -------
      bool
          ``True`` if triangles wave port  is used, ``False`` otherwise.



.. py:class:: HfssSolverSettings(sim_setup)

   Bases: :py:obj:`object`


   Manages EDB methods for HFSS solver settings.


   .. py:property:: enhanced_low_freq_accuracy

      Whether to enable legacy low-frequency sampling.

      .. deprecated:: pyedb 0.54.0
          Use :func:`enhanced_low_frequency_accuracy` instead.

      Returns
      -------
      bool
          ``True`` if low frequency accuracy is used, ``False`` otherwise.



   .. py:property:: enhanced_low_frequency_accuracy

      Whether to enable legacy low-frequency sampling.

      Returns
      -------
      bool
          ``True`` if low frequency accuracy is used, ``False`` otherwise.



   .. py:property:: order_basis

      Order of the basic functions for HFSS.
      - 0=Zero.
      - 1=1st order.
      - 2=2nd order.
      - 3=Mixed.

      Returns
      -------
      int
          Integer value according to the description.



   .. py:property:: relative_residual

      Residual for use by the iterative solver.

      Returns
      -------
      float



   .. py:property:: solver_type

      Get solver type to use (Direct/Iterative/Auto) for HFSS.
      Options:
      1- ``kAutoSolver``.
      2- ``kDirectSolver``.
      3- ``kIterativeSolver``.
      4- ``kNumSolverTypes``.

      Returns
      -------
      str



   .. py:property:: use_shell_elements

      Whether to enable use of shell elements.

      Returns
      -------
      bool
          ``True`` if shall elements are used, ``False`` otherwise.



