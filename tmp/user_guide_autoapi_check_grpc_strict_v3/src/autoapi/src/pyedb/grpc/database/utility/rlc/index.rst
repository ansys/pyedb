src.pyedb.grpc.database.utility.rlc
===================================

.. py:module:: src.pyedb.grpc.database.utility.rlc


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.rlc.Rlc


Module Contents
---------------

.. py:class:: Rlc(pedb, core)

   Bases: :py:obj:`ansys.edb.core.utility.rlc.Rlc`


   Represents an RLC.

   Attributes
   ----------
   r : :term:`ValueLike`, default: 0
       Resistance value. This parameter is only used if
       ``r_enabled=True``.
   r_enabled : bool, default: ``False``
       Whether resistance is enabled.
   l : :term:`ValueLike`, default: 0
       Inductance value. This parameter is only used if
       ``c-l_enabled=True``.
   l_enabled : bool, default: ``False``
       Whether inductance is enabled.
   c : :term:`ValueLike`, default: 0
       Capacitance value. This parameter is only used if
       ``c_enabled=True``.
   c_enabled : bool, default: ``False``
       Whether capacitance is enabled.
   is_parallel : bool, default: ``True``
       Whether the r, l, and c elements are in parallel. If ``False``, these
       elements are in series.


   .. py:property:: r
      :type: float


      R value.

      Returns
      -------
      float
          Resistor value.




   .. py:property:: l
      :type: float


      L value.

      Returns
      -------
      float
          Inductor value.




   .. py:property:: c
      :type: float


      C value.

      Returns
      -------
      float
          Capacitor value.




