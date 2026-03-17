src.pyedb.dotnet.database.cell.hierarchy.pin_pair_model
=======================================================

.. py:module:: src.pyedb.dotnet.database.cell.hierarchy.pin_pair_model


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.hierarchy.pin_pair_model.PinPair


Module Contents
---------------

.. py:class:: PinPair(component, edb_pin_pair)

   Bases: :py:obj:`object`


   .. py:property:: first_pin


   .. py:property:: second_pin


   .. py:property:: is_parallel


   .. py:property:: rlc_enable


   .. py:property:: resistance


   .. py:property:: inductance


   .. py:property:: capacitance


   .. py:property:: rlc_values


   .. py:method:: add_pin_pair(r: float | None = None, l: float | None = None, c: float | None = None, r_enabled: bool | None = None, l_enabled: bool | None = None, c_enabled: bool | None = None, first_pin: str | None = None, second_pin: str | None = None, is_parallel: bool = False)

      Add a pin pair definition.

      Parameters
      ----------
      r: float | None
      l: float | None
      c: float | None
      r_enabled: bool
      l_enabled: bool
      c_enabled: bool
      first_pin: str
      second_pin: str
      is_parallel: bool

      Returns
      -------




