src.pyedb.generic.settings
==========================

.. py:module:: src.pyedb.generic.settings


Attributes
----------

.. autoapisummary::

   src.pyedb.generic.settings.settings


Classes
-------

.. autoapisummary::

   src.pyedb.generic.settings.Settings


Module Contents
---------------

.. py:class:: Settings

   Bases: :py:obj:`object`


   Manages all PyEDB environment variables and global settings.


   .. py:attribute:: CURRENT_STABLE_AEDT_VERSION
      :value: 2025.2



   .. py:attribute:: INSTALLED_VERSIONS
      :value: None



   .. py:attribute:: INSTALLED_STUDENT_VERSIONS
      :value: None



   .. py:attribute:: INSTALLED_CLIENT_VERSIONS
      :value: None



   .. py:attribute:: LATEST_VERSION
      :value: None



   .. py:attribute:: LATEST_STUDENT_VERSION
      :value: None



   .. py:attribute:: specified_version
      :value: None



   .. py:attribute:: is_student_version
      :value: False



   .. py:attribute:: remote_rpc_session
      :value: False



   .. py:attribute:: pyedb_server_path
      :value: ''



   .. py:attribute:: formatter
      :value: None



   .. py:attribute:: time_tick


   .. py:property:: retry_n_times_time_interval

      Time interval between the retries by the ``_retry_n_times`` method.



   .. py:attribute:: logger
      :value: None



   .. py:attribute:: log_file
      :value: None



   .. py:property:: is_grpc

      Whether Edb is launched using grpc or not.

      Returns
      -------
      bool



   .. py:property:: edb_environment_variables

      Environment variables that are set before launching a new AEDT session,
      including those that enable the beta features.



   .. py:property:: aedt_version

      AEDT version in the form ``"2023.x"``. In AEDT 2022 R2 and later,
      evaluating a bounding box by exporting a SAT file is disabled.



   .. py:property:: global_log_file_size

      Global PyEDB log file size in MB. The default value is ``10``.



   .. py:property:: enable_global_log_file

      Flag for enabling and disabling the global PyEDB log file located in the global temp folder.
      The default is ``True``.



   .. py:property:: enable_local_log_file

      Flag for enabling and disabling the local PyEDB log file located
      in the ``projectname.pyedb`` project folder. The default is ``True``.



   .. py:property:: global_log_file_name

      Global PyEDB log file path. The default is ``pyedb_username.log``.



   .. py:property:: enable_debug_methods_argument_logger

      Flag for whether to write out the method's arguments in the debug logger.
      The default is ``False``.



   .. py:property:: enable_error_handler

      Flag for enabling and disabling the internal PyEDB error handling.



   .. py:property:: enable_file_logs

      Flag for enabling and disabling the logging to a file.



   .. py:property:: enable_logger

      Flag for enabling and disabling the logging overall.



   .. py:property:: logger_file_path

      PyEDB log file path.



   .. py:property:: logger_formatter

      Message format of the log entries.
      The default is ``'%(asctime)s:%(destination)s:%(extra)s%(levelname)-8s:%(message)s'``



   .. py:property:: logger_datefmt

      Date format of the log entries.
      The default is ``'%Y/%m/%d %H.%M.%S'``



   .. py:property:: enable_debug_edb_logger

      Flag for enabling and disabling the logger for any EDB API methods.



   .. py:property:: enable_debug_internal_methods_logger

      Flag for enabling and disabling the logging for internal methods.
      This setting is useful for debug purposes.



   .. py:property:: enable_debug_logger

      Flag for enabling and disabling the debug level logger.



   .. py:property:: enable_screen_logs

      Flag for enabling and disabling the logging to STDOUT.



   .. py:property:: edb_dll_path

      Optional path for the EDB DLL file.



   .. py:property:: aedt_installation_path


.. py:data:: settings

