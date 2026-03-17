src.pyedb.dotnet.database.utilities.hfss_simulation_setup
=========================================================

.. py:module:: src.pyedb.dotnet.database.utilities.hfss_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.utilities.hfss_simulation_setup.HfssSimulationSetup
   src.pyedb.dotnet.database.utilities.hfss_simulation_setup.HFSSPISimulationSetup


Module Contents
---------------

.. py:class:: HfssSimulationSetup(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.simulation_setup.SimulationSetup`


   Manages EDB methods for HFSS simulation setup.


   .. py:class:: Settings(sim_setup)

      HFSS simulation setup settings container.



   .. py:method:: create(pedb, name)
      :classmethod:



   .. py:property:: solver_slider_type

      Solver slider type.
      Options are:
      1 - ``Fast``.
      2 - ``Medium``.
      3 - ``Accurate``.

      Returns
      -------
      int



   .. py:property:: is_auto_setup

      Flag indicating if automatic setup is enabled.



   .. py:property:: hfss_solver_settings

      Manages EDB methods for HFSS solver settings.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.HfssSolverSettings`




   .. py:property:: adaptive_settings

      Adaptive Settings Class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.AdaptiveSettings`




   .. py:property:: defeature_settings

      Defeature settings Class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.DefeatureSettings`




   .. py:property:: via_settings

      Via settings Class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.ViaSettings`




   .. py:property:: advanced_mesh_settings

      Advanced mesh settings Class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.AdvancedMeshSettings`




   .. py:property:: curve_approx_settings

      Curve approximation settings Class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.CurveApproxSettings`




   .. py:property:: dcr_settings

      Dcr settings Class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.DcrSettings`




   .. py:property:: hfss_port_settings

      HFSS port settings Class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.hfss_simulation_setup_data.HfssPortSettings`




   .. py:property:: mesh_operations

      Mesh operations settings Class.

      Returns
      -------
      List of :class:`dotnet.database.edb_data.hfss_simulation_setup_data.MeshOperation`




   .. py:method:: add_length_mesh_operation(net_layer_list, name=None, max_elements=1000, max_length='1mm', restrict_elements=True, restrict_length=True, refine_inside=False, mesh_region=None)

      Add a mesh operation to the setup.

      Parameters
      ----------
      net_layer_list : dict
          Dictionary containing nets and layers on which enable Mesh operation. Example ``{"A0_N": ["TOP", "PWR"]}``.
      name : str, optional
          Mesh operation name.
      max_elements : int, optional
          Maximum number of elements. Default is ``1000``.
      max_length : str, optional
          Maximum length of elements. Default is ``1mm``.
      restrict_elements : bool, optional
          Whether to restrict number of elements. Default is ``True``.
      restrict_length : bool, optional
          Whether to restrict length of elements. Default is ``True``.
      mesh_region : str, optional
          Mesh region name.
      refine_inside : bool, optional
          Whether to refine inside or not.  Default is ``False``.

      Returns
      -------
      :class:`dotnet.database.edb_data.hfss_simulation_setup_data.LengthMeshOperation`



   .. py:method:: add_skin_depth_mesh_operation(net_layer_list, name=None, max_elements=1000, skin_depth='1um', restrict_elements=True, surface_triangle_length='1mm', number_of_layers=2, refine_inside=False, mesh_region=None)

      Add a mesh operation to the setup.

      Parameters
      ----------
      net_layer_list : dict
          Dictionary containing nets and layers on which enable Mesh operation. Example ``{"A0_N": ["TOP", "PWR"]}``.
      name : str, optional
          Mesh operation name.
      max_elements : int, optional
          Maximum number of elements. Default is ``1000``.
      skin_depth : str, optional
          Skin Depth. Default is ``1um``.
      restrict_elements : bool, optional
          Whether to restrict number of elements. Default is ``True``.
      surface_triangle_length : bool, optional
          Surface Triangle length. Default is ``1mm``.
      number_of_layers : int, str, optional
          Number of layers. Default is ``2``.
      mesh_region : str, optional
          Mesh region name.
      refine_inside : bool, optional
          Whether to refine inside or not.  Default is ``False``.

      Returns
      -------
      :class:`dotnet.database.edb_data.hfss_simulation_setup_data.LengthMeshOperation`



   .. py:method:: set_solution_single_frequency(frequency='5Ghz', max_num_passes=10, max_delta_s=0.02)

      Set single-frequency solution.

      Parameters
      ----------
      frequency : str, float, optional
          Adaptive frequency. The default is ``5GHz``.
      max_num_passes : int, optional
          Maximum number of passes. The default is ``10``.
      max_delta_s : float, optional
          Maximum delta S. The default is ``0.02``.

      Returns
      -------
      bool




   .. py:method:: set_solution_multi_frequencies(frequencies=('5Ghz', '10Ghz'), max_num_passes=10, max_delta_s='0.02')

      Set multi-frequency solution.

      Parameters
      ----------
      frequencies : list, tuple, optional
          List or tuple of adaptive frequencies. The default is ``5GHz``.
      max_num_passes : int, optional
          Maximum number of passes. Default is ``10``.
      max_delta_s : float, optional
          Maximum delta S. The default is ``0.02``.

      Returns
      -------
      bool




   .. py:method:: set_solution_broadband(low_frequency='5Ghz', high_frequency='10Ghz', max_num_passes=10, max_delta_s='0.02')

      Set broadband solution.

      Parameters
      ----------
      low_frequency : str, float, optional
          Low frequency. The default is ``5GHz``.
      high_frequency : str, float, optional
          High frequency. The default is ``10GHz``.
      max_num_passes : int, optional
          Maximum number of passes. The default is ``10``.
      max_delta_s : float, optional
          Maximum Delta S. Default is ``0.02``.

      Returns
      -------
      bool



   .. py:method:: auto_mesh_operation(trace_ratio_seeding: float = 3, signal_via_side_number: int = 12, power_ground_via_side_number: int = 6) -> bool

      Automatically create and apply a length-based mesh operation for all nets in the design.

      The method inspects every signal net, determines the smallest trace width, and
      seeds a :class:`LengthMeshOperation` whose maximum element length is
      ``smallest_width * trace_ratio_seeding``. Signal vias (padstack instances) are
      configured with the requested number of polygon sides, while power/ground vias
      are updated through the global ``num_via_sides`` advanced setting.

      Parameters
      ----------
      trace_ratio_seeding : float, optional
          Ratio used to compute the maximum allowed element length from the
          smallest trace width found in the design.  The resulting length is
          ``min_width * trace_ratio_seeding``.  Defaults to ``3``.
      signal_via_side_number : int, optional
          Number of sides (i.e. faceting resolution) assigned to **signal**
          padstack instances that belong to the nets being meshed.
          Defaults to ``12``.
      power_ground_via_side_number : int, optional
          Number of sides assigned to **power/ground** vias via the global
          ``advanced.num_via_sides`` setting.  Defaults to ``6``.

      Returns
      -------
      bool

      Raises
      ------
      ValueError
          If the design contains no terminals, making mesh seeding impossible.

      Notes
      -----
      * Only primitives of type ``"path"`` are considered when determining the
        smallest trace width.
      * Every ``(net, layer, sheet)`` tuple required by the mesher is
        automatically populated; sheet are explicitly marked as ``False``.
      * Existing contents of :attr:`mesh_operations` are **replaced** by the
        single new operation.

      Examples
      --------
      >>> setup = edbapp.setups["my_setup"]
      >>> setup.auto_mesh_operation(trace_ratio_seeding=4, signal_vias_side_number=16)
      >>> setup.mesh_operations[0].max_length
      '2.5um'



.. py:class:: HFSSPISimulationSetup(pedb, edb_object=None, name: str = None)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.simulation_setup.SimulationSetup`


   Manages EDB methods for HFSSPI simulation setup.


   .. py:method:: create(edb, name) -> HFSSPISimulationSetup
      :classmethod:


      Create a new HFSSPI simulation setup.

      Parameters
      ----------
      edb : Edb
          An EDB instance.
      name : str
          Name of the simulation setup.

      Returns
      -------
      HFSSPISimulationSetup
          The created HFSSPI simulation setup object.



