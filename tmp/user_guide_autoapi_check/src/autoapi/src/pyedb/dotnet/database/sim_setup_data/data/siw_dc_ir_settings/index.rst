src.pyedb.dotnet.database.sim_setup_data.data.siw_dc_ir_settings
================================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.data.siw_dc_ir_settings


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.data.siw_dc_ir_settings.SiwaveDCIRSettings


Module Contents
---------------

.. py:class:: SiwaveDCIRSettings(parent)

   Class for DC IR settings.


   .. py:property:: export_dc_thermal_data

      Export DC Thermal Data.

      Returns
      -------
          bool
          ``True`` when activated, ``False`` deactivated.



   .. py:property:: import_thermal_data

      Import Thermal Data.

      Returns
      -------
          bool
          ``True`` when activated, ``False`` deactivated.



   .. py:property:: dc_report_show_active_devices

      DC Report Show Active Devices.

      Returns
      -------
          bool
          ``True`` when activated, ``False`` deactivated.



   .. py:property:: per_pin_use_pin_format

      Per Pin Use Pin Format.

      Returns
      -------
          bool
          ``True`` when activated, ``False`` deactivated.



   .. py:property:: use_loop_res_for_per_pin

      Use loop Res Per Pin.

      Returns
      -------
          bool
          ``True`` when activated, ``False`` deactivated.



   .. py:property:: dc_report_config_file

      DC Report Config File.

      Returns
      -------
          str
          path to the DC report configuration file.



   .. py:property:: full_dc_report_path

      Full DC Report Path.

      Returns
      -------
          str
          full path to the DC report file.



   .. py:property:: icepak_temp_file

      Icepack Temp File.

      Returns
      -------
          str
          path to the temp Icepak file.



   .. py:property:: icepak_temp_file_path

      Icepak Temp File Path.

      Returns
      -------
          str
          path for the Icepak temp file.



   .. py:property:: per_pin_res_path

      Per Pin Res Path.

      Returns
      -------
          str
          path for per pin res.



   .. py:property:: via_report_path

      Via Report Path.

      Returns
      -------
          str
          path for the Via Report.



   .. py:property:: source_terms_to_ground

      A dictionary of SourceName, NodeToGround pairs,
      where NodeToGround is one of 0 (unspecified), 1 (negative), 2 (positive).


      Returns
      -------
          dict <str, int>
              str: source name,
              int: node to ground pairs, 0 (unspecified), 1 (negative), 2 (positive) .



