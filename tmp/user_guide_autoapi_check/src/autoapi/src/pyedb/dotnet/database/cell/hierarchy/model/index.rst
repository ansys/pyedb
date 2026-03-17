src.pyedb.dotnet.database.cell.hierarchy.model
==============================================

.. py:module:: src.pyedb.dotnet.database.cell.hierarchy.model


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.hierarchy.model.Model
   src.pyedb.dotnet.database.cell.hierarchy.model.PinPairModel


Module Contents
---------------

.. py:class:: Model(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.obj_base.ObjBase`


   Manages model class.


   .. py:property:: model_type

      Component model type.



.. py:class:: PinPairModel(component, edb_object=None)

   Bases: :py:obj:`Model`


   Manages pin pair model class.


   .. py:attribute:: component


   .. py:property:: pin_pairs

      List of pin pair definitions.



   .. py:method:: delete_pin_pair_rlc(pin_pair)

      Delete a pin pair definition.

      Parameters
      ----------
      pin_pair: Ansys.Ansoft.Edb.Utility.PinPair

      Returns
      -------
      bool



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




