src.pyedb.configuration.cfg_s_parameter_models
==============================================

.. py:module:: src.pyedb.configuration.cfg_s_parameter_models


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_s_parameter_models.CfgSParameterModel
   src.pyedb.configuration.cfg_s_parameter_models.CfgSParameters


Module Contents
---------------

.. py:class:: CfgSParameterModel(**kwargs)

   .. py:attribute:: name


   .. py:attribute:: component_definition


   .. py:attribute:: file_path


   .. py:attribute:: apply_to_all


   .. py:attribute:: components


   .. py:attribute:: reference_net


   .. py:attribute:: reference_net_per_component


   .. py:attribute:: pin_order


.. py:class:: CfgSParameters(pedb, data, path_lib=None)

   .. py:method:: apply()


   .. py:method:: get_data_from_db(cfg_components)


   .. py:attribute:: path_libraries
      :value: None



   .. py:attribute:: s_parameters_models


