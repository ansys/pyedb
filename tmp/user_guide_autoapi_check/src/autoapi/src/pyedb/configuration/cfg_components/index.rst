src.pyedb.configuration.cfg_components
======================================

.. py:module:: src.pyedb.configuration.cfg_components


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_components.CfgComponent
   src.pyedb.configuration.cfg_components.CfgComponents


Module Contents
---------------

.. py:class:: CfgComponent(_pedb, pedb_object, **kwargs)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBase`


   .. py:method:: retrieve_model_properties_from_edb()


   .. py:method:: set_parameters_to_edb()


   .. py:method:: retrieve_parameters_from_edb()


   .. py:attribute:: pyedb_obj


   .. py:attribute:: enabled


   .. py:attribute:: reference_designator


   .. py:attribute:: definition


   .. py:attribute:: type


   .. py:attribute:: placement_layer


   .. py:attribute:: pins


   .. py:attribute:: port_properties


   .. py:attribute:: solder_ball_properties


   .. py:attribute:: ic_die_properties


   .. py:attribute:: pin_pair_model


   .. py:attribute:: spice_model


   .. py:attribute:: s_parameter_model


   .. py:attribute:: netlist_model


.. py:class:: CfgComponents(pedb, components_data)

   .. py:attribute:: components
      :value: []



   .. py:method:: clean()


   .. py:method:: apply()


   .. py:method:: retrieve_parameters_from_edb()


