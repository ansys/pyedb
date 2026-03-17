net
===

.. py:module:: net


Classes
-------

.. autoapisummary::

   net.SingleEndedNet


Module Contents
---------------

.. py:class:: SingleEndedNet

   Single ended net class handler.

   This class manages the configuration for single-ended nets including
   impedance, thresholds, and driver/termination parameters.

   Examples
   --------
   >>> from pyedb.misc.siw_feature_config.xtalk_scan.net import SingleEndedNet
   >>> net = SingleEndedNet()
   >>> net.name = "DDR_DQ0"
   >>> net.nominal_impedance = 50.0
   >>> net.warning_threshold = 45.0
   >>> net.violation_threshold = 40.0
   >>> net.driver_rise_time = "100ps"
   >>> net.voltage = 1.2



   .. py:attribute:: name
      :type:  str | None
      :value: None



   .. py:attribute:: nominal_impedance
      :type:  float | None
      :value: None



   .. py:attribute:: warning_threshold
      :type:  float | None
      :value: None



   .. py:attribute:: violation_threshold
      :type:  float | None
      :value: None



   .. py:attribute:: fext_warning_threshold
      :type:  float | None
      :value: None



   .. py:attribute:: fext_violation_threshold
      :type:  float | None
      :value: None



   .. py:attribute:: next_warning_threshold
      :type:  float | None
      :value: None



   .. py:attribute:: next_violation_threshold
      :type:  float | None
      :value: None



   .. py:attribute:: driver_rise_time
      :type:  str | float | None
      :value: None



   .. py:attribute:: voltage
      :type:  float | None
      :value: None



   .. py:attribute:: driver_impedance
      :type:  float | None
      :value: None



   .. py:attribute:: termination_impedance
      :type:  float | None
      :value: None



   .. py:method:: extend_xml(parent) -> None

      Write XML object section.

      Parameters
      ----------
      parent : xml.etree.ElementTree.Element
          Parent XML element to extend.




