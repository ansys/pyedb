src.pyedb.dotnet.database.cell.terminal.terminal
================================================

.. py:module:: src.pyedb.dotnet.database.cell.terminal.terminal


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.terminal.terminal.Terminal


Module Contents
---------------

.. py:class:: Terminal(pedb, edb_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.cell.connectable.Connectable`


   Manages EDB functionalities for a connectable object.


   .. py:property:: hfss_type

      HFSS port type.



   .. py:property:: layer

      Get layer of the terminal.



   .. py:property:: is_circuit_port

      Whether it is a circuit port.



   .. py:property:: do_renormalize

      Determine whether port renormalization is enabled.



   .. py:property:: terminal_type

      Terminal Type.

      Returns
      -------
      int



   .. py:property:: boundary_type

      Boundary type.

      Returns
      -------
      str
          InvalidBoundary, PortBoundary, PecBoundary, RlcBoundary, kCurrentSource, kVoltageSource, kNexximGround,
          kNexximPort, kDcTerminal, kVoltageProbe



   .. py:property:: is_port

      Whether it is a port.



   .. py:property:: is_current_source

      Whether it is a current source.



   .. py:property:: is_voltage_source

      Whether it is a voltage source.



   .. py:property:: impedance

      Impedance of the port.



   .. py:property:: is_reference_terminal

      Whether it is a reference terminal.



   .. py:property:: reference_terminal

      Adding grpc compatibility.



   .. py:property:: ref_terminal

      Get reference terminal.

      .deprecated:: pyedb 0.47.0
      Use: attribute:`reference_terminal` instead.




   .. py:property:: reference_object

      This returns the object assigned as reference. It can be a primitive or a padstack instance.


      Returns
      -------
      :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance` or
      :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`



   .. py:property:: reference_net_name

      Net name to which reference_object belongs.



   .. py:method:: get_padstack_terminal_reference_pin(gnd_net_name_preference=None)

      Get a list of pad stacks instances and serves Coax wave ports,
      pingroup terminals, PadEdge terminals.

      Parameters
      ----------
      gnd_net_name_preference : str, optional
          Preferred reference net name.

      Returns
      -------
      :class:`dotnet.database.edb_data.padstack_data.EDBPadstackInstance`



   .. py:method:: get_pin_group_terminal_reference_pin(gnd_net_name_preference=None)

      Return a list of pins and serves terminals connected to pingroups.

      Parameters
      ----------
      gnd_net_name_preference : str, optional
          Preferred reference net name.

      Returns
      -------
      :class:`dotnet.database.edb_data.padstack_data.EDBPadstackInstance`



   .. py:method:: get_edge_terminal_reference_primitive()

      Check and  return a primitive instance that serves Edge ports,
      wave ports and coupled edge ports that are directly connedted to primitives.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`



   .. py:method:: get_point_terminal_reference_primitive()

      Find and return the primitive reference for the point terminal or the padstack instance.

      Returns
      -------
      :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance` or
      :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`



   .. py:method:: get_pad_edge_terminal_reference_pin(gnd_net_name_preference=None)

      Get the closest pin padstack instances and serves any edge terminal connected to a pad.

      Parameters
      ----------
      gnd_net_name_preference : str, optional
          Preferred reference net name. Optianal, default is `None` which will auto compute the gnd name.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`



   .. py:property:: magnitude

      Get the magnitude of the source.



   .. py:property:: phase

      Get the phase of the source.



   .. py:property:: amplitude

      Property added for grpc compatibility



   .. py:property:: source_amplitude

      Property added for grpc compatibility



   .. py:property:: source_phase

      Property added for grpc compatibility



   .. py:property:: terminal_to_ground


