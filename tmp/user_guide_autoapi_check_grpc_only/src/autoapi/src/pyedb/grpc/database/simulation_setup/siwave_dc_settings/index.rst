src.pyedb.grpc.database.simulation_setup.siwave_dc_settings
===========================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_dc_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_dc_settings.SIWaveDCSettings


Module Contents
---------------

.. py:class:: SIWaveDCSettings(pedb, core: ansys.edb.core.simulation_setup.siwave_simulation_settings.SIWaveDCSettings)

   .. py:attribute:: core


   .. py:property:: compute_inductance
      :type: bool


      Compute inductance flag.

      Returns
      -------
      bool
          True if compute inductance is enabled, False otherwise.




   .. py:property:: contact_radius
      :type: str


      Contact radius value.

      Returns
      -------
      str
          Contact radius.




   .. py:property:: dc_slider_position
      :type: int


      DC slider position.

      Returns
      -------
      int
          DC slider position.




   .. py:property:: plot_jv
      :type: bool


      Plot JV flag.

      Returns
      -------
      bool
          True if plot JV is enabled, False otherwise.




   .. py:property:: use_dc_custom_settings
      :type: bool


      Use DC custom settings flag.

      Returns
      -------
      bool
          True if DC custom settings are used, False otherwise.




   .. py:property:: export_dc_thermal_data
      :type: bool


      Export DC thermal data flag.

      Returns
      -------
      bool
          True if export DC thermal data is enabled, False otherwise.




   .. py:property:: import_thermal_data
      :type: bool


      Import thermal data flag.

      Returns
      -------
      bool
          True if import thermal data is enabled, False otherwise.




   .. py:property:: dc_report_show_active_devices
      :type: bool


      DC report show active devices flag.

      Returns
      -------
      bool
          True if DC report show active devices is enabled, False otherwise.




   .. py:property:: per_pin_use_pin_format
      :type: bool


      Per pin use pin format flag.

      Returns
      -------
      bool
          True if per pin use pin format is enabled, False otherwise.




   .. py:property:: use_loop_res_for_per_pin
      :type: bool


      Use loop resistance for per pin flag.

      Returns
      -------
      bool
          True if use loop resistance for per pin is enabled, False otherwise.




   .. py:property:: dc_report_config_file
      :type: str


      DC report configuration file.

      Returns
      -------
      str
          DC report configuration file.




   .. py:property:: full_dc_report_path
      :type: str


      Full DC report path.

      Returns
      -------
      str
          Full DC report path.




   .. py:property:: icepak_temp_file
      :type: str


      Icepak temperature file.

      Returns
      -------
      str
          Icepak temperature file.




   .. py:property:: per_pin_res_path
      :type: bool


      Per pin resistance path.

      Returns
      -------
      bool
          True if per pin resistance path is enabled, False otherwise.




   .. py:property:: via_report_path
      :type: str


      Via report path.

      Returns
      -------
      str
          Via report path.




   .. py:property:: source_terms_to_ground
      :type: dict[str, int]


      Source terms to ground mapping.

      Returns
      -------
      dict[str, int]
          Source terms to ground mapping.




