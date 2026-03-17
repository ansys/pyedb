src.pyedb.grpc.database.layout.voltage_regulator
================================================

.. py:module:: src.pyedb.grpc.database.layout.voltage_regulator


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator


Module Contents
---------------

.. py:class:: VoltageRegulator(pedb, core)

   Class managing voltage regulator.


   .. py:attribute:: core


   .. py:property:: component

      Voltage regulator component

      Returns
      -------
      :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`
          Component.



   .. py:property:: load_regulator_current
      :type: float


      Load regulator current value

      Returns
      -------
      float
          Current value.



   .. py:property:: load_regulation_percent
      :type: float


      Retrieve load regulation percent value.

      Returns
      -------
      float
          Percent value.



   .. py:property:: negative_remote_sense_pin
      :type: pyedb.grpc.database.primitive.padstack_instance.PadstackInstance


      Retrieve negative remote sense pin.

      Returns
      -------
      :class:`PadstackInstance pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
          PadstackInstance.



   .. py:property:: positive_remote_sense_pin
      :type: pyedb.grpc.database.primitive.padstack_instance.PadstackInstance


      Retrieve positive remote sense pin.

      Returns
      -------
      :class:`PadstackInstance pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
          PadstackInstance.



   .. py:property:: voltage
      :type: float


      Retrieve voltage value.

      Returns
      -------
      float
          Voltage value.



