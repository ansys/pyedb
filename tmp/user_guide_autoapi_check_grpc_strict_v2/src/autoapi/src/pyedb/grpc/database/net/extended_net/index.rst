src.pyedb.grpc.database.net.extended_net
========================================

.. py:module:: src.pyedb.grpc.database.net.extended_net


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.net.extended_net.ExtendedNets
   src.pyedb.grpc.database.net.extended_net.ExtendedNet


Module Contents
---------------

.. py:class:: ExtendedNets(pedb)

   .. py:property:: items
      :type: dict[str, ExtendedNet]


      Extended nets.

      Returns
      -------
      Dict[str, :class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
          Dictionary of extended nets.



   .. py:method:: create(name, net)

      Create a new Extended net.

      Parameters
      ----------
      name : str
          Name of the extended net.
      net : str, list
         Name of the nets to be added into this extended net.

      Returns
      -------
      :class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`
          Created ExtendedNet object.



   .. py:method:: auto_identify_signal(resistor_below: int | float = 10, inductor_below: int | float = 1, capacitor_above: int | float = 1e-09, exception_list: list = None) -> list[ExtendedNet]

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
      List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
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
      List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
          List of all extended nets and their associated components.

      Examples
      --------
      >>> from pyedb import Edb
      >>> app = Edb()
      >>> app.extended_nets.auto_identify_power()



   .. py:method:: generate_extended_nets(resistor_below: int | float = 10, inductor_below: int | float = 1, capacitor_above: int | float = 1, exception_list: list = None, include_signal: bool = True, include_power: bool = True) -> list[ExtendedNet]

      Get extended net and associated components.

      Parameters
      ----------
      resistor_below : int, float, optional
          Threshold of resistor value. Search extended net across resistors which has value lower than the threshold.
      inductor_below : int, float, optional
          Threshold of inductor value. Search extended net across inductances which has value lower than the
          threshold.
      capacitor_above : int, float, optional
          Threshold of capacitor value. Search extended net across capacitors which has value higher than the
          threshold.
      exception_list : list, optional
          List of components to bypass when performing threshold checks. Components
          in the list are considered as serial components. The default is ``None``.
      include_signal : str, optional
          Whether to generate extended signal nets. The default is ``True``.
      include_power : str, optional
          Whether to generate extended power nets. The default is ``True``.

      Returns
      -------
      List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
          List of all extended nets.

      Examples
      --------
      >>> from pyedb import Edb
      >>> app = Edb()
      >>> app.nets.get_extended_nets()



.. py:class:: ExtendedNet(pedb, edb_object)

   Manages EDB functionalities for a primitives.
   It Inherits EDB Object properties.


   .. py:attribute:: core


   .. py:method:: create(layout, name)
      :classmethod:


      Create a extended net.

      Parameters
      ----------
      layout : :class: <``Layout` pyedb.grpc.database.layout.layout.Layout>
          Layout object associated with the extended net.
      name : str
          Name of the extended net.

      Returns
      -------
      ExtendedNet
          Extended net object.



   .. py:property:: name

      Extended net name.

      Returns
      -------
      str
          Extended net name.



   .. py:property:: nets
      :type: dict[str, pyedb.grpc.database.net.net.Net]


      Nets dictionary.

      Returns
      -------
      Dict[str, :class:`Net <pyedb.grpc.database.net.net.Net>`]
          Dict[net name, Net object].



   .. py:property:: components
      :type: dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Dictionary of components.

      Returns
      -------
      Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
          Dict[net name, Component object].



   .. py:property:: rlc
      :type: dict[str, any]


      Dictionary of RLC components.

      Returns
      -------
      Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
          Dict[net name, Component object].



   .. py:property:: serial_rlc
      :type: dict[str, any]


      Dictionary of serial RLC components.

      Returns
      -------
      Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
          Dict[net name, Component object].




   .. py:property:: shunt_rlc
      :type: dict[str, any]


      Dictionary of shunt RLC components.

      Returns
      -------
      Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
          Dict[net name, Component object].




