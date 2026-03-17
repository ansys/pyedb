pins
====

.. py:module:: pins


Classes
-------

.. autoapisummary::

   pins.DriverPin
   pins.ReceiverPin


Module Contents
---------------

.. py:class:: DriverPin

   Driver pin class handler.

   Examples
   --------
   >>> from pyedb.misc.siw_feature_config.xtalk_scan.pins import DriverPin
   >>> pin = DriverPin()
   >>> pin.name = "A1"
   >>> pin.ref_des = "U1"
   >>> pin.driver_rise_time = "50ps"
   >>> pin.voltage = 1.8
   >>> pin.driver_impedance = 40.0



   .. py:attribute:: name
      :type:  str | None
      :value: None



   .. py:attribute:: ref_des
      :type:  str | None
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



   .. py:method:: extend_xml(parent) -> None

      Write object to XML section.

      Parameters
      ----------
      parent : xml.etree.ElementTree.Element
          Parent XML element to extend.




.. py:class:: ReceiverPin

   Receiver pin class handler.

   Examples
   --------
   >>> from pyedb.misc.siw_feature_config.xtalk_scan.pins import ReceiverPin
   >>> pin = ReceiverPin()
   >>> pin.name = "B1"
   >>> pin.ref_des = "U2"
   >>> pin.receiver_impedance = 75.0



   .. py:attribute:: name
      :type:  str | None
      :value: None



   .. py:attribute:: ref_des
      :type:  str | None
      :value: None



   .. py:attribute:: receiver_impedance
      :type:  float | None
      :value: None



   .. py:method:: extend_xml(parent) -> None

      Write object to XML section.

      Parameters
      ----------
      parent : xml.etree.ElementTree.Element
          Parent XML element to extend.




