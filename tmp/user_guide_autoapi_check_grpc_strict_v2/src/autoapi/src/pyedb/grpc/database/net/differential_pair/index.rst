src.pyedb.grpc.database.net.differential_pair
=============================================

.. py:module:: src.pyedb.grpc.database.net.differential_pair


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.net.differential_pair.DifferentialPairs
   src.pyedb.grpc.database.net.differential_pair.DifferentialPair


Module Contents
---------------

.. py:class:: DifferentialPairs(pedb)

   .. py:property:: items
      :type: dict[str, DifferentialPair]


      Extended nets.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`]
          Dictionary of extended nets.



   .. py:method:: create(name: str, net_p: str, net_n: str) -> DifferentialPair

      Parameters
      ----------
      name : str
          Name of the differential pair.
      net_p : str
          Name of the positive net.
      net_n : str
          Name of the negative net.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`



   .. py:method:: auto_identify(positive_differentiator='_P', negative_differentiator='_N') -> list[str]

      Auto identify differential pairs by naming conversion.

      Parameters
      ----------
      positive_differentiator: str, optional
          Differentiator of the positive net. The default is ``"_P"``.
      negative_differentiator: str, optional
          Differentiator of the negative net. The default is ``"_N"``.

      Returns
      -------
      list
          A list containing identified differential pair names.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2025.2")
      >>> edb_nets = edbapp.differential_pairs.auto_identify()



.. py:class:: DifferentialPair(pedb, edb_object)

   Bases: :py:obj:`ansys.edb.core.net.differential_pair.DifferentialPair`


   Manages EDB functionalities for a primitive.
   It inherits EDB object properties.


   .. py:property:: positive_net
      :type: pyedb.grpc.database.net.net.Net


      Positive Net.



   .. py:property:: negative_net
      :type: pyedb.grpc.database.net.net.Net


      Negative Net.



