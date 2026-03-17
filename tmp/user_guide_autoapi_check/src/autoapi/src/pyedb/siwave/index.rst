src.pyedb.siwave
================

.. py:module:: src.pyedb.siwave

.. autoapi-nested-parse::

   This module contains the ``Siwave`` class.

   The ``Siwave`` module can be initialized as standalone before launching an app or
   automatically initialized by an app to the latest installed AEDT version.



Classes
-------

.. autoapisummary::

   src.pyedb.siwave.Siwave


Functions
---------

.. autoapisummary::

   src.pyedb.siwave.wait_export_file
   src.pyedb.siwave.wait_export_folder
   src.pyedb.siwave.parser_file_path


Module Contents
---------------

.. py:function:: wait_export_file(flag, file_path, time_sleep=0.5)

.. py:function:: wait_export_folder(flag, folder_path, time_sleep=0.5)

.. py:function:: parser_file_path(file_path)

.. py:class:: Siwave(specified_version=None)

   Bases: :py:obj:`object`


   Initializes SIwave based on the inputs provided and manages SIwave release and closing.

   Parameters
   ----------
   specified_version : str, int, float, optional
       Version of AEDT to use. The default is ``None``, in which case
       the active setup is used or the latest installed version is used.



   .. py:property:: version


   .. py:property:: version_keys

      Version keys for AEDT.



   .. py:property:: current_version

      Current version of AEDT.



   .. py:property:: project_name

      Project name.

      Returns
      -------
      str
          Name of the project.




   .. py:property:: project_path

      Project path.

      Returns
      -------
      str
          Full absolute path for the project.




   .. py:property:: project_file

      Project file.

      Returns
      -------
      str
          Full absolute path and name for the project file.




   .. py:property:: lock_file

      Lock file.

      Returns
      -------
      str
          Full absolute path and name for the project lock file.




   .. py:property:: results_directory

      Results directory.

      Returns
      -------
      str
          Full absolute path to the ``aedtresults`` directory.



   .. py:property:: src_dir

      Source directory.

      Returns
      -------
      str
          Full absolute path to the ``python`` directory.



   .. py:property:: pyaedt_dir

      PyAEDT directory.

      Returns
      -------
      str
          Full absolute path to the ``pyaedt`` directory.



   .. py:property:: oproject

      Project.



   .. py:property:: icepak


   .. py:method:: open_project(proj_path=None)

      Open a project.

      Parameters
      ----------
      proj_path : str, optional
          Full path to the project. The default is ``None``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:property:: file_dir
      :type: str


      Directory path of the open project.



   .. py:property:: file_path
      :type: str


      Path of the open project file.



   .. py:method:: save_project(projectpath=None, projectName=None)

      Save the project.

      Parameters
      ----------
      proj_path : str, optional
          Full path to the project. The default is ``None``.
      projectName : str, optional
           Name of the project. The default is ``None``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: save(file_path: Optional[Union[str, pathlib.Path]])

      Save the project.

      Parameters
      ----------
      file_path : str, optional
          Full path to the project. The default is ``None``.



   .. py:method:: close_project(save_project=False)

      Close the project.

      Parameters
      ----------
      save_project : bool, optional
          Whether to save the current project before closing it. The default is ``False``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: quit_application()

      Quit the application.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: export_element_data(simulation_name, file_path, data_type='Vias')

      Export element data.

      Parameters
      ----------
      simulation_name : str
          Name of the setup.
      file_path : str
          Path to the exported report.
      data_type : str, optional
          Type of the data. The default is ``"Vias"``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: export_siwave_report(simulation_name, file_path, bkground_color='White')

      Export the Siwave report.

      Parameters
      ----------
      simulation_name : str
          Name of the setup.
      file_path : str
          Path to the exported report.
      bkground_color : str, optional
          Color of the report's background. The default is ``"White"``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: export_dc_simulation_report(simulation_name, file_path, background_color='White')

      Export the Siwave DC simulation report.

      Parameters
      ----------
      simulation_name : str
          Name of the setup.
      file_path : str
          Path to the exported report.
      background_color : str, optional
          Color of the report's background. The default is ``"White"``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: run_dc_simulation(export_dc_power_data_to_icepak=False)

      Run DC simulation.



   .. py:method:: export_icepak_project(file_path, dc_simulation_name)

      Exports an Icepak project for standalone use.

      Parameters
      ----------
      file_path : str,
          Path of the Icepak project.
      dc_simulation_name : str
          Name of the DC simulation.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: run_icepak_simulation(icepak_simulation_name, dc_simulation_name)

      Runs an Icepak simulation.

      Parameters
      ----------
      icepak_simulation_name : str
          Name of the Icepak simulation.
      dc_simulation_name : str
          Name of the DC simulation.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: export_edb(file_path: str)

      Export the layout as EDB.

      Parameters
      ----------
      file_path : str
          Path to the EDB.

      Returns
      -------
      bool



   .. py:method:: import_edb(file_path: str)

      Import layout from EDB.

      Parameters
      ----------
      file_path : Str
          Path to the EDB file.
      Returns
      -------
      bool



   .. py:method:: load_configuration(file_path: str)

      Load configuration settings from a configure file.Import

      Parameters
      ----------
      file_path : str
          Path to the configuration file.



   .. py:method:: export_configuration(file_path: str, fix_padstack_names: bool = False)

      Export layout information into a configuration file.

      Parameters
      ----------
      file_path : str
          Path to the configuration file.
      fix_padstack_names : bool
          Name all the padstacks in edb.



