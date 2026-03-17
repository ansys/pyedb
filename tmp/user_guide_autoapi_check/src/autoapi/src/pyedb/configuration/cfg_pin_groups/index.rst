src.pyedb.configuration.cfg_pin_groups
======================================

.. py:module:: src.pyedb.configuration.cfg_pin_groups


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_pin_groups.CfgPinGroups
   src.pyedb.configuration.cfg_pin_groups.CfgPinGroup


Module Contents
---------------

.. py:class:: CfgPinGroups(pedb, pingroup_data)

   Manage configuration pin group class.


   .. py:method:: set_pingroup_to_edb()


   .. py:method:: get_data_from_edb()


   .. py:attribute:: pin_groups


   .. py:method:: apply()


   .. py:method:: get_data_from_db()


   .. py:method:: export_properties()


.. py:class:: CfgPinGroup(pedb, **kwargs)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBase`


   .. py:method:: create()


   .. py:attribute:: name


   .. py:attribute:: reference_designator


   .. py:attribute:: pins


   .. py:attribute:: net


   .. py:method:: export_properties()


