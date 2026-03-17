src.pyedb.dotnet.database.net_class
===================================

.. py:module:: src.pyedb.dotnet.database.net_class


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.net_class.EdbCommon
   src.pyedb.dotnet.database.net_class.EdbNetClasses
   src.pyedb.dotnet.database.net_class.EdbExtendedNets
   src.pyedb.dotnet.database.net_class.EdbDifferentialPairs


Module Contents
---------------

.. py:class:: EdbCommon(pedb)

.. py:class:: EdbNetClasses(p_edb)

   Bases: :py:obj:`EdbCommon`, :py:obj:`object`


   Manages EDB methods for managing nets accessible from the ``Edb.net_classes`` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_nets = edbapp.net_classes


   .. py:property:: items

      Extended nets.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`]
          Dictionary of extended nets.



   .. py:method:: create(name: str, net: str | list) -> pyedb.dotnet.database.edb_data.nets_data.EDBNetClassData

      Create a new net class.

      Parameters
      ----------
      name : str
          Name of the net class.
      net : str, list
         Name of the nets to be added into this net class.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetClassData`



.. py:class:: EdbExtendedNets(p_edb)

   Bases: :py:obj:`EdbCommon`, :py:obj:`object`


   Manages EDB methods for managing nets accessible from the ``Edb.extended_nets`` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_nets = edbapp.extended_nets


   .. py:property:: items

      Extended nets.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetsData`]
          Dictionary of extended nets.



   .. py:method:: create(name: str, net: str | list) -> pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetData

      Create a new Extended net.

      Parameters
      ----------
      name : str
          Name of the extended net.
      net : str, list
         Name of the nets to be added into this extended net.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetsData`



   .. py:method:: auto_identify_signal(resistor_below: int | float = 10, inductor_below: int | float = 1, capacitor_above: int | float = 1e-09, exception_list: list = None) -> list

      Get extended signal net and associated components.

      Parameters
      ----------
      resistor_below : int, float, optional
          Threshold for the resistor value. Search the extended net across resistors that
          have a value lower than the threshold.
      inductor_below : int, float, optional
          Threshold for the inductor value. Search the extended net across inductances
          that have a value lower than the threshold.
      capacitor_above : int, float, optional
          Threshold for the capacitor value. Search the extended net across capacitors
          that have a value higher than the threshold.
      exception_list : list, optional
          List of components to bypass when performing threshold checks. Components
          in the list are considered as serial components. The default is ``None``.

      Returns
      -------
      list
          List of all extended nets.

      Examples
      --------
      >>> from pyedb import Edb
      >>> app = Edb()
      >>> app.extended_nets.auto_identify_signal()



   .. py:method:: auto_identify_power(resistor_below: int | float = 10, inductor_below: int | float = 1, capacitor_above: int | float = 1, exception_list: list = None) -> list

      Get all extended power nets and their associated components.

      Parameters
      ----------
      resistor_below : int, float, optional
          Threshold for the resistor value. Search the extended net across resistors that
          have a value lower than the threshold.
      inductor_below : int, float, optional
          Threshold for the inductor value. Search the extended net across inductances that
          have a value lower than the threshold.
      capacitor_above : int, float, optional
          Threshold for the capacitor value. Search the extended net across capacitors that
          have a value higher than the threshold.
      exception_list : list, optional
          List of components to bypass when performing threshold checks. Components
          in the list are considered as serial components. The default is ``None``.

      Returns
      -------
      list
          List of all extended nets and their associated components.

      Examples
      --------
      >>> from pyedb import Edb
      >>> app = Edb()
      >>> app.extended_nets.auto_identify_power()



   .. py:method:: clean()

      Remove all extended nets.



.. py:class:: EdbDifferentialPairs(p_edb)

   Bases: :py:obj:`EdbCommon`, :py:obj:`object`


   Manages EDB methods for managing nets accessible from the ``Edb.differential_pairs`` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_nets = edbapp.differential_pairs.items
   >>> edb_nets = edbapp.differential_pairs["DQ4"]


   .. py:property:: items

      Extended nets.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`]
          Dictionary of extended nets.



   .. py:method:: create(name: str, net_p: str, net_n: str) -> pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData

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



   .. py:method:: auto_identify(positive_differentiator='_P', negative_differentiator='_N')

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
      >>> edbapp = Edb("myaedbfolder", edbversion="2023.1")
      >>> edb_nets = edbapp.differential_pairs.auto_identify()



