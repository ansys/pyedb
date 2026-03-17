src.pyedb.grpc.database.simulation_setup.siwave_dcir_settings
=============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_dcir_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_dcir_settings.SIWaveDCIRSettings


Module Contents
---------------

.. py:class:: SIWaveDCIRSettings(pedb, core)

   .. py:attribute:: core


   .. py:property:: advanced


   .. py:property:: dc


   .. py:property:: dc_settings
      :type: pyedb.grpc.database.simulation_setup.siwave_dc_settings.SIWaveDCSettings


      Setup dc settings.



   .. py:property:: dc_advanced


   .. py:property:: general


   .. py:property:: s_parameter


   .. py:property:: dc_report_config_file
      :type: str


      DC report configuration file path.

      Returns
      -------
      str:
          file path.



   .. py:property:: dc_report_show_active_devices
      :type: bool


      Whether to show active devices in the DC report.

      Returns
      -------
      bool:
          True if active devices are shown, False otherwise.



   .. py:property:: enabled

      Whether the DC IR simulation is enabled.

      Returns
      -------
      bool:
          True if enabled, False otherwise.



   .. py:property:: export_dc_thermal_data
      :type: bool


      Whether to export DC thermal data.

      Returns
      -------
      bool:
          True if DC thermal data is exported, False otherwise.



   .. py:property:: full_dc_report_path
      :type: str


      Full DC report path.

      Returns
      -------
      str:
          file path.



   .. py:property:: icepak_temp_file
      :type: str


      Icepak temperature file path.

      Returns
      -------
      str:
          file path.



   .. py:property:: import_thermal_data
      :type: bool


      Whether to import thermal data.

      Returns
      -------
      bool:
          True if thermal data is imported, False otherwise.



   .. py:property:: per_pin_res_path
      :type: str


      Per-pin resistance file path.

      Returns
      -------
      str:
          file path.



   .. py:property:: per_pin_use_pin_format
      :type: bool


      Whether to use pin format for per-pin resistance.

      Returns
      -------
      bool:
          True if pin format is used, False otherwise.



   .. py:property:: source_terms_to_ground
      :type: dict[str, int]


      Source terms to ground mapping.

      Returns
      -------
      dict[str, int]:
          Mapping of source terms to ground.



   .. py:property:: use_loop_res_for_per_pin
      :type: bool


      Whether to use loop resistance for per-pin resistance.

      Returns
      -------
      bool:
          True if loop resistance is used for per-pin resistance, False otherwise.



   .. py:property:: via_report_path
      :type: str


      Via report file path.

      Returns
      -------
      str:
          file path.



