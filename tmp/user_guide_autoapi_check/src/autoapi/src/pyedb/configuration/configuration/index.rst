src.pyedb.configuration.configuration
=====================================

.. py:module:: src.pyedb.configuration.configuration


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.configuration.Configuration


Functions
---------

.. autoapisummary::

   src.pyedb.configuration.configuration.set_padstack_definition
   src.pyedb.configuration.configuration.set_padstack_instance


Module Contents
---------------

.. py:function:: set_padstack_definition(pdef, pdef_obj)

.. py:function:: set_padstack_instance(inst, inst_obj)

.. py:class:: Configuration(pedb: pyedb.Edb)

   Enables export and import of a JSON configuration file that can be applied to a new or existing design.


   .. py:attribute:: data


   .. py:attribute:: cfg_data


   .. py:method:: load(config_file, append=True, apply_file=False, output_file=None, open_at_the_end=True)

      Import configuration settings from a configure file.

      Parameters
      ----------
      config_file : str, dict
          Full path to configure file in JSON or TOML format. Dictionary is also supported.
      append : bool, optional
          Whether if the new file will append to existing properties or the properties will be cleared before import.
          Default is ``True`` to keep stored properties
      apply_file : bool, optional
          Whether to apply the file after the load or not. Default is ``False``.
      output_file : str, optional
          Full path to the new aedb folder where the configured project will be saved.
      open_at_the_end : bool, optional
          Whether to keep the new generated file opened at the end. Default is ``True``.

      Returns
      -------
      dict
          Config dictionary.



   .. py:method:: run(**kwargs)

      Apply configuration settings to the current design



   .. py:method:: apply_setups()


   .. py:method:: get_setups()


   .. py:method:: apply_boundaries()


   .. py:method:: get_boundaries()


   .. py:method:: apply_modeler()


   .. py:method:: apply_variables()

      Set variables into database.



   .. py:method:: get_variables()

      Retrieve variables from database.



   .. py:method:: apply_materials()

      Apply material settings to the current design



   .. py:method:: get_materials()

      Retrieve materials from the current design.



   .. py:method:: apply_stackup()


   .. py:method:: get_stackup()


   .. py:method:: get_padstacks()


   .. py:method:: apply_padstacks()


   .. py:method:: get_data_from_db(**kwargs)

      Get configuration data from layout.

      Returns
      -------




   .. py:method:: apply_operations()

      Apply operations to the current design.



   .. py:method:: get_operations()


   .. py:method:: apply_terminals()


   .. py:method:: get_terminals()


   .. py:method:: export(file_path, stackup=True, package_definitions=False, setups=True, sources=True, ports=True, nets=True, pin_groups=True, operations=True, components=True, boundaries=True, s_parameters=True, padstacks=True, general=True, variables=True, terminals=False)

      Export the configuration data from layout to a file.

      Parameters
      ----------
      file_path : str, Path
          File path to export the configuration data.
      stackup : bool
          Whether to export stackup or not.
      package_definitions : bool
          Whether to export package definitions or not.
      setups : bool
          Whether to export setups or not.
      sources : bool
          Whether to export sources or not. Alternative to terminals.
      ports : bool
          Whether to export ports or not. Alternative to terminals.
      nets : bool
          Whether to export nets.
      pin_groups : bool
          Whether to export pin groups.
      operations : bool
          Whether to export operations.
      components : bool
          Whether to export component.
      boundaries : bool
          Whether to export boundaries.
      s_parameters : bool
          Whether to export s_parameters.
      padstacks : bool
          Whether to export padstacks.
      general : bool
          Whether to export general information.
      variables : bool
          Whether to export variable.
      terminals : bool
          Whether to export terminals. Alternative to ports and sources.
      Returns
      -------
      bool



