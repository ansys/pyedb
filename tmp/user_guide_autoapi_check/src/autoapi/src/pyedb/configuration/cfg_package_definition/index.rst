src.pyedb.configuration.cfg_package_definition
==============================================

.. py:module:: src.pyedb.configuration.cfg_package_definition


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_package_definition.CfgPackage
   src.pyedb.configuration.cfg_package_definition.CfgHeatSink
   src.pyedb.configuration.cfg_package_definition.CfgPackageDefinitions


Module Contents
---------------

.. py:class:: CfgPackage(**kwargs)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBase`


   Configuration package class.


   .. py:attribute:: protected_attributes
      :value: ['apply_to_all', 'components', 'extent_bounding_box', 'component_definition']



   .. py:attribute:: name


   .. py:attribute:: component_definition


   .. py:attribute:: maximum_power


   .. py:attribute:: thermal_conductivity


   .. py:attribute:: theta_jb


   .. py:attribute:: theta_jc


   .. py:attribute:: height


   .. py:attribute:: apply_to_all


   .. py:attribute:: components


   .. py:attribute:: extent_bounding_box


   .. py:property:: heatsink


.. py:class:: CfgHeatSink(**kwargs)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBase`


   Configuration heat sink class.


   .. py:attribute:: fin_base_height


   .. py:attribute:: fin_height


   .. py:attribute:: fin_orientation


   .. py:attribute:: fin_spacing


   .. py:attribute:: fin_thickness


.. py:class:: CfgPackageDefinitions(pedb, data)

   .. py:method:: get_parameter_from_edb()


   .. py:method:: set_parameter_to_edb()


   .. py:attribute:: packages


   .. py:method:: apply()


   .. py:method:: get_data_from_db()


