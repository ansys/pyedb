src.pyedb.dotnet.database.utilities.siwave_simulation_setup
===========================================================

.. py:module:: src.pyedb.dotnet.database.utilities.siwave_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.utilities.siwave_simulation_setup.DeprecatedSettings
   src.pyedb.dotnet.database.utilities.siwave_simulation_setup.SIwaveSimulationSetup
   src.pyedb.dotnet.database.utilities.siwave_simulation_setup.SiwaveDCSimulationSetup
   src.pyedb.dotnet.database.utilities.siwave_simulation_setup.SIWaveGeneralSettings
   src.pyedb.dotnet.database.utilities.siwave_simulation_setup.Settings


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.utilities.siwave_simulation_setup.clone_edb_sim_setup_info


Module Contents
---------------

.. py:function:: clone_edb_sim_setup_info(source, target)

.. py:class:: DeprecatedSettings

   .. py:property:: dc_report_config_file
      :type: str


      Path to the DC report configuration file.



   .. py:property:: dc_report_show_active_devices
      :type: bool


      Flag to show active devices in the DC report.



   .. py:property:: enabled
      :type: bool


      Flag indicating if the setup is enabled.



   .. py:property:: export_dc_thermal_data
      :type: bool


      Flag to export DC thermal data.



   .. py:property:: full_dc_report_path
      :type: str


      Full path to the DC report.



   .. py:property:: icepak_temp_file_path
      :type: str


      Path to the Icepak temporary file.



   .. py:property:: icepak_temp_file

      Icepak temporary file name.



   .. py:property:: import_thermal_data
      :type: bool


      Flag to import thermal data.



   .. py:property:: per_pin_res_path

      Path to the per-pin resistance data.



   .. py:property:: s_parameter
      :type: pyedb.dotnet.database.sim_setup_data.data.siwave.SIwaveSParameterSettings


      S-parameter settings.



   .. py:property:: source_terms_to_ground
      :type: dict[str, int]


      Dictionary of grounded terminals.

      Returns
      -------
      Dictionary
          {str, int}, keys is source name, value int 0 unspecified, 1 negative node, 2 positive one.




   .. py:property:: use_loop_res_for_per_pin

      Flag to use loop resistance for per-pin calculations.



   .. py:property:: per_pin_use_pin_format

      Flag to use pin format for per-pin calculations.
      .. deprecated:: 0.68.2
          Use :property:`settings.dc.per_pin_use_pin_format` property instead.




   .. py:property:: via_report_path
      :type: str


      Path to the via report.



   .. py:method:: add_source_terminal_to_ground(source_name, terminal=0)

      Add a source terminal to ground.

      Parameters
      ----------
      source_name : str,
          Source name.
      terminal : int, optional
          Terminal to assign. Options are:

           - 0=Unspecified
           - 1=Negative node
           - 2=Positive none

      Returns
      -------
      bool




.. py:class:: SIwaveSimulationSetup(pedb, edb_object=None, name: str = None)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.simulation_setup.SimulationSetup`


   Manages EDB methods for SIwave simulation setup.


   .. py:method:: create(name=None)

      Create a SIwave SYZ setup.

      Returns
      -------
      :class:`SiwaveDCSimulationSetup`



   .. py:method:: get_configurations()

      Get SIwave SYZ simulation settings.

      Returns
      -------
      dict
          Dictionary of SIwave SYZ simulation settings.



   .. py:property:: settings

      Get the settings interface for SIwave DC simulation.

      Returns
      -------
      SIWaveSimulationSettings
          An instance of the Settings class providing access to SIwave DC simulation settings.



   .. py:property:: advanced_settings

      SIwave advanced settings.



   .. py:property:: sim_setup_info

      Overrides the default sim_setup_info object.



   .. py:property:: get_sim_setup_info

      Get simulation information from the setup.



   .. py:method:: set_si_slider(value)

      Set SIwave SI simulation accuracy level.

      Options are:
      - ``0``: Optimal speed;
      - ``1``:  Balanced;
      - ``2``: Optimal accuracy```.



   .. py:property:: pi_slider_position

      PI solider position. Values are from ``1`` to ``3``.



   .. py:property:: pi_slider_pos


   .. py:property:: si_slider_position

      SI slider position. Values are from ``1`` to ``3``.



   .. py:property:: use_custom_settings

      Custom settings to use.

      Returns
      -------
      bool



   .. py:property:: use_si_settings

      Whether to use SI Settings.

      Returns
      -------
      bool



   .. py:method:: add_sweep(name: str = None, frequency_set: list = None, sweep_type: str = 'interpolation', **kwargs)

      Add frequency sweep.

      Parameters
      ----------
      name : str, optional
          Name of the frequency sweep. The default is ``None``.
      frequency_set : list, optional
          List of frequency points. The default is ``None``.
      sweep_type : str, optional
          Sweep type. The default is ``"interpolation"``. Options are ``"discrete"``,"discrete"``.
      Returns
      -------

      Examples
      --------
      >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
      >>> setup1.add_sweep(name="sw1", frequency_set=["linear count", "1MHz", "100MHz", 10])



   .. py:property:: sweeps

      List of frequency sweeps.



   .. py:property:: dc_settings

      SIwave DC setting.



   .. py:property:: dc_advanced_settings

      Siwave DC advanced settings.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`



.. py:class:: SiwaveDCSimulationSetup(pedb, edb_object=None, name: str = None)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.simulation_setup.SimulationSetup`


   Manages EDB methods for SIwave DC simulation setup.


   .. py:method:: create(name=None)

      Create a SIwave DCIR setup.

      Returns
      -------
      :class:`SiwaveDCSimulationSetup`



   .. py:property:: sim_setup_info

      Overrides the default sim_setup_info object.



   .. py:property:: get_sim_setup_info

      Get simulation information from the setup.



   .. py:property:: settings

      Get the settings interface for SIwave DC simulation.

      Returns
      -------
      Settings
          An instance of the Settings class providing access to SIwave DC simulation settings.



   .. py:property:: dc_ir_settings

      DC IR settings.
      ..deprecated:: 0.68.2

      use :property:`settings.dc_ir` property instead.




   .. py:method:: get_configurations()

      Get SIwave DC simulation settings.

      Returns
      -------
      dict
          Dictionary of SIwave DC simulation settings.



   .. py:method:: set_dc_slider(value)

      Set DC simulation accuracy level.

      Options are:

      - ``0``: Optimal speed
      - ``1``: Balanced
      - ``2``: Optimal accuracy



   .. py:property:: dc_settings

      SIwave DC setting.

      deprecated:: 0.57.0
            Use :property:`settings` property instead.




   .. py:property:: dc_advanced_settings

      Siwave DC advanced settings.

      .. deprecated :: 0.57.0
              Use :property:`settings` property instead.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveDCAdvancedSettings`



.. py:class:: SIWaveGeneralSettings(parent)

   Class to manage global settings for the Siwave simulation setup module.
   Added to be compliant with ansys-edbe-core settings structure.


.. py:class:: Settings(parent: SIwaveSimulationSetup)

   Bases: :py:obj:`DeprecatedSettings`


   Class to reflect the same structure as gRPC.


   .. py:property:: advanced


   .. py:property:: dc


   .. py:property:: dc_ir


   .. py:property:: dc_advanced


   .. py:property:: general


