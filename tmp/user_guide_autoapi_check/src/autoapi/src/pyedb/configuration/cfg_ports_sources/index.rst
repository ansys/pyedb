src.pyedb.configuration.cfg_ports_sources
=========================================

.. py:module:: src.pyedb.configuration.cfg_ports_sources


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_ports_sources.CfgTerminalInfo
   src.pyedb.configuration.cfg_ports_sources.CfgCoordinateTerminalInfo
   src.pyedb.configuration.cfg_ports_sources.CfgNearestPinTerminalInfo
   src.pyedb.configuration.cfg_ports_sources.CfgSources
   src.pyedb.configuration.cfg_ports_sources.CfgPorts
   src.pyedb.configuration.cfg_ports_sources.CfgProbes
   src.pyedb.configuration.cfg_ports_sources.CfgCircuitElement
   src.pyedb.configuration.cfg_ports_sources.CfgPort
   src.pyedb.configuration.cfg_ports_sources.CfgSource
   src.pyedb.configuration.cfg_ports_sources.CfgProbe
   src.pyedb.configuration.cfg_ports_sources.CfgEdgePort
   src.pyedb.configuration.cfg_ports_sources.CfgDiffWavePort


Module Contents
---------------

.. py:class:: CfgTerminalInfo(pedb, **kwargs)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBase`


   .. py:attribute:: CFG_TERMINAL_TYPES
      :value: ['pin', 'net', 'pin_group', 'nearest_pin', 'coordinates']



   .. py:method:: update_contact_radius(radius)


   .. py:attribute:: value


   .. py:attribute:: reference_designator


   .. py:attribute:: contact_type


   .. py:attribute:: contact_radius


   .. py:attribute:: num_of_contact


   .. py:attribute:: contact_expansion


   .. py:method:: export_properties()


.. py:class:: CfgCoordinateTerminalInfo(pedb, **kwargs)

   Bases: :py:obj:`CfgTerminalInfo`


   .. py:attribute:: layer


   .. py:attribute:: point_x


   .. py:attribute:: point_y


   .. py:attribute:: net


   .. py:method:: export_properties()


.. py:class:: CfgNearestPinTerminalInfo(pedb, **kwargs)

   Bases: :py:obj:`CfgTerminalInfo`


   .. py:attribute:: reference_net


   .. py:attribute:: search_radius


   .. py:method:: export_properties()


.. py:class:: CfgSources(pedb, sources_data)

   .. py:method:: get_pin_group_name(src)


   .. py:attribute:: sources


   .. py:method:: apply()


   .. py:method:: get_data_from_db()


   .. py:method:: export_properties()


.. py:class:: CfgPorts(pedb, ports_data)

   .. py:method:: get_pin_group(port)


   .. py:attribute:: ports
      :value: []



   .. py:method:: apply()


   .. py:method:: get_data_from_db()


   .. py:method:: export_properties()


.. py:class:: CfgProbes(pedb, data)

   .. py:attribute:: probes


   .. py:method:: apply()


.. py:class:: CfgCircuitElement(pedb, **kwargs)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBase`


   .. py:attribute:: name


   .. py:attribute:: type


   .. py:attribute:: impedance


   .. py:attribute:: reference_designator


   .. py:attribute:: distributed


   .. py:method:: create_terminals()

      Create step 1. Collect positive and negative terminals.



.. py:class:: CfgPort(pedb, **kwargs)

   Bases: :py:obj:`CfgCircuitElement`


   Manage port.


   .. py:attribute:: CFG_PORT_TYPE


   .. py:method:: set_parameters_to_edb()

      Create port.



   .. py:method:: export_properties()


.. py:class:: CfgSource(pedb, **kwargs)

   Bases: :py:obj:`CfgCircuitElement`


   .. py:attribute:: CFG_SOURCE_TYPE


   .. py:attribute:: magnitude


   .. py:method:: set_parameters_to_edb()

      Create sources.



   .. py:method:: export_properties()


.. py:class:: CfgProbe(pedb, **kwargs)

   Bases: :py:obj:`CfgCircuitElement`


   .. py:method:: set_parameters_to_edb()


.. py:class:: CfgEdgePort(pedb, **kwargs)

   .. py:method:: set_parameters_to_edb()


   .. py:method:: export_properties()


   .. py:attribute:: name


   .. py:attribute:: type


   .. py:attribute:: primitive_name


   .. py:attribute:: point_on_edge


   .. py:attribute:: horizontal_extent_factor


   .. py:attribute:: vertical_extent_factor


   .. py:attribute:: pec_launch_width


.. py:class:: CfgDiffWavePort(pedb, **kwargs)

   .. py:attribute:: name


   .. py:attribute:: type


   .. py:attribute:: horizontal_extent_factor


   .. py:attribute:: vertical_extent_factor


   .. py:attribute:: pec_launch_width


   .. py:attribute:: positive_port


   .. py:attribute:: negative_port


   .. py:method:: set_parameters_to_edb()


