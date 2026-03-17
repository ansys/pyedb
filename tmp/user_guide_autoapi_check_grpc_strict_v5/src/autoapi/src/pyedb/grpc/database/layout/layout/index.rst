src.pyedb.grpc.database.layout.layout
=====================================

.. py:module:: src.pyedb.grpc.database.layout.layout

.. autoapi-nested-parse::

   This module contains these classes: `EdbLayout` and `Shape`.



Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.layout.layout.Layout


Module Contents
---------------

.. py:class:: Layout(pedb, core: ansys.edb.core.layout.layout.Layout)

   Manage Layout class.


   .. py:attribute:: core


   .. py:property:: layout_instance
      :type: Any



   .. py:property:: primitives
      :type: list[pyedb.grpc.database.primitive.primitive.Primitive]



   .. py:property:: terminals
      :type: list[pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal | pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal | pyedb.grpc.database.terminal.bundle_terminal.BundleTerminal | pyedb.grpc.database.terminal.point_terminal.PointTerminal]


      Get terminals belonging to active layout.

      Returns
      -------
      Terminal dictionary : Dict[str, :class:`Terminal <pyedb.grpc.database.terminal.Terminal>`]
          Dictionary of terminals.



   .. py:property:: nets
      :type: list[pyedb.grpc.database.net.net.Net]


      Nets.

      Returns
      -------
      List[:class:`Net <pyedb.grpc.database.net.net.Net>`]
          List of Net.



   .. py:property:: bondwires
      :type: list[pyedb.grpc.database.primitive.bondwire.Bondwire]


      Bondwires.

      Returns
      -------
      list [:class:`pyedb.grpc.database.primitive.primitive.Primitive`]:
          List of bondwires.



   .. py:property:: groups
      :type: list[pyedb.grpc.database.hierarchy.component.Component]


      Groups

      Returns
      -------
      List[:class:`Group <pyedb.grpc.database.hierarch.component.Component>`].
          List of Component.




   .. py:property:: pin_groups
      :type: list[pyedb.grpc.database.hierarchy.pingroup.PinGroup]


      Pin groups.

      Returns
      -------
      List[:class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`]
          List of PinGroup.




   .. py:property:: net_classes
      :type: list[pyedb.grpc.database.net.net_class.NetClass]


      Net classes.

      Returns
      -------
      List[:class:`NetClass <pyedb.grpc.database.net.net_class.NetClass>`]
          List of NetClass.




   .. py:property:: extended_nets
      :type: list[pyedb.grpc.database.net.extended_net.ExtendedNet]


      Extended nets.

      Returns
      -------
      List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
          List of extended nets.



   .. py:property:: differential_pairs
      :type: list[pyedb.grpc.database.net.differential_pair.DifferentialPair]


      Differential pairs.

      Returns
      -------
      List[:class:`DifferentialPair <pyedb.grpc.database.net.differential_pair.DifferentialPair>`
          List of DifferentialPair.




   .. py:property:: padstack_instances
      :type: list[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      Get all padstack instances in a list.



   .. py:property:: voltage_regulators
      :type: list[pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator]


      Voltage regulators.

      List[:class:`VoltageRegulator <pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator>`.
          List of VoltageRegulator.




   .. py:method:: find_primitive(layer_name: Union[str, list] = None, name: Union[str, list] = None, net_name: Union[str, list] = None) -> list[any]

      Find a primitive objects by layer name.
      Parameters
      ----------
      layer_name : str, list
      layer_name : str, list, optional
          Name of the layer.
      name : str, list, optional
          Name of the primitive.
      net_name : str, list, optional
          Name of the primitive.
      Returns
      -------
      List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive`].
          List of Primitive.



   .. py:method:: find_padstack_instances(aedt_name: Union[str, List[str]] = None, component_name: Union[str, List[str]] = None, component_pin_name: Union[str, List[str]] = None, net_name: Union[str, List[str]] = None, instance_id: Union[int, List[int]] = None) -> List

      Finds padstack instances matching the specified criteria.

      This method filters the available padstack instances based on specified attributes such as
      `aedt_name`, `component_name`, `component_pin_name`, `net_name`, or `instance_id`. Criteria
      can be passed as individual values or as a list of values. If no padstack instances match
      the criteria, an error is raised.

      Parameters
      ----------
      aedt_name : Union[str, List[str]], optional
          Name(s) of the AEDT padstack instance(s) to filter.
      component_name : Union[str, List[str]], optional
          Name(s) of the component(s) to filter padstack instances by.
      component_pin_name : Union[str, List[str]], optional
          Name(s) of the component pin(s) to filter padstack instances by.
      net_name : Union[str, List[str]], optional
          Name(s) of the net(s) to filter padstack instances by.
      instance_id : Union[int, List[int]], optional
          ID(s) of the padstack instance(s) to filter.

      Returns
      -------
      List
          A list of padstack instances matching the specified criteria.



