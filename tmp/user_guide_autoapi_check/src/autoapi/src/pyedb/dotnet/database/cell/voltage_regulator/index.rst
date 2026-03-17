src.pyedb.dotnet.database.cell.voltage_regulator
================================================

.. py:module:: src.pyedb.dotnet.database.cell.voltage_regulator


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.voltage_regulator.VoltageRegulator


Module Contents
---------------

.. py:class:: VoltageRegulator(pedb, edb_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.cell.connectable.Connectable`


   Class managing EDB voltage regulator.


   .. py:property:: load_regulator_current
      :type: float


      Get load regulator current value.

      Returns
      -------
      float
          Load regulator current.



   .. py:property:: load_regulation_percent
      :type: float


      Get load regulation percent value.

      Returns
      -------
      float
          Load regulation percentage.



   .. py:property:: negative_remote_sense_pin
      :type: pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance


      Get negative remote sense pin.

      Returns
      -------
      EDBPadstackInstance
          Negative remote sense pin instance.



   .. py:property:: positive_remote_sense_pin
      :type: pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance


      Get positive remote sense pin.

      Returns
      -------
      EDBPadstackInstance
          Positive remote sense pin instance.



   .. py:property:: voltage
      :type: float


      Get voltage value.

      Returns
      -------
      float
          Voltage of the regulator.



   .. py:property:: is_active
      :type: bool


      Check if voltage regulator is active.

      Returns
      -------
      bool
          True if active, False otherwise.



