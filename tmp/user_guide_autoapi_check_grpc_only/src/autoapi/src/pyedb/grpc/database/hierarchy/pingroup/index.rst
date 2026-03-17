src.pyedb.grpc.database.hierarchy.pingroup
==========================================

.. py:module:: src.pyedb.grpc.database.hierarchy.pingroup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.hierarchy.pingroup.PinGroup


Module Contents
---------------

.. py:class:: PinGroup(pedb, edb_pin_group=None)

   Manages pin groups.


   .. py:method:: create(layout, name, padstack_instances) -> PinGroup
      :classmethod:


      Create a pin group.

      Parameters
      ----------
      layout : :class:`Layout <ansys.edb.core.layout.layout.Layout>`
          Layout object.
      name : str
          Pin group name.
      padstack_instances : List[:class:
      `PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
          List of padstack instances.

      Returns
      -------
      :class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`
          Pin group object.




   .. py:property:: name

      Pin group name.

      Returns
      -------
      str
          Pin group name.




   .. py:property:: component
      :type: pyedb.grpc.database.hierarchy.component.Component


      Component.

      Return
      ------
      :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`
          Pin group component.



   .. py:property:: is_null
      :type: bool


      Check if pin group is null.

      Returns
      -------
      bool
          ``True`` if pin group is null, ``False`` otherwise.




   .. py:property:: pins
      :type: dict[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      Pin group pins.

      Returns
      -------
      Dict[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`].



   .. py:property:: net
      :type: pyedb.grpc.database.net.net.Net


      Net.

      Returns
      -------
      :class:`Net <ansys.edb.core.net.net.Net>`.



   .. py:property:: net_name
      :type: str


      Net name.

      Returns
      -------
      str
          Net name.




   .. py:property:: terminal
      :type: Union[pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal, None]


      Terminal.



   .. py:method:: unique_name(layout, base_name: str) -> str
      :staticmethod:


      Generate unique name.

      Parameters
      ----------
      layout : :class:`Layout <pyedb.edb.layout.layout.Layout>`
          Layout object.
      base_name : str
          Base name.

      Returns
      -------
      str
          Unique name.




   .. py:method:: create_terminal(name=None) -> pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal

      Create a terminal.

      Parameters
      ----------
      name : str, optional
          Name of the terminal.

      Returns
      -------
      :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
          Pin group terminal.




   .. py:method:: create_current_source_terminal(magnitude=1.0, phase=0, impedance=1000000.0) -> pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal

      Create current source terminal.

      Parameters
      ----------
      magnitude : float or int, optional
          Source magnitude, default value ``1.0``.
      phase : float or int, optional
          Source phase, default value ``0.0``.
      impedance : float, optional
          Source impedance, default value ``1e6``.

      Returns
      -------
      :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
          Pin group terminal.




   .. py:method:: create_voltage_source_terminal(magnitude=1, phase=0, impedance=0.001) -> pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal

      Create voltage source terminal.

      Parameters
      ----------
      magnitude : float or int, optional
          Source magnitude, default value ``1.0``.
      phase : float or int, optional
          Source phase, default value ``0.0``.
      impedance : float, optional
          Source impedance, default value ``1e-3``.

      Returns
      -------
      :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
          Pin group terminal.




   .. py:method:: create_voltage_probe_terminal(impedance=1000000.0) -> pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal

      Create voltage probe terminal.

      Parameters
      ----------
      impedance : float, optional
          Probe impedance, default value ``1e6``.

      Returns
      -------
      :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
          Pin group terminal.




   .. py:method:: create_port_terminal(impedance=50) -> pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal

      Create port terminal.

      Parameters
      ----------
      impedance : float, optional
          Port impedance, default value ``50``.

      Returns
      -------
      :class:`PinGroupTerminal <pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal>`.
          Pin group terminal.




   .. py:method:: delete()

      Delete active pin group.

      Returns
      -------
      bool




