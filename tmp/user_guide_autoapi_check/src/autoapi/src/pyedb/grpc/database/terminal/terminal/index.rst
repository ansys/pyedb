src.pyedb.grpc.database.terminal.terminal
=========================================

.. py:module:: src.pyedb.grpc.database.terminal.terminal


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.terminal.Terminal


Module Contents
---------------

.. py:class:: Terminal(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.inner.conn_obj.ConnObj`


   Represents a layout object.


   .. py:attribute:: core


   .. py:property:: net

      Terminal net.

      Returns
      -------
      :class:`Net <pyedb.grpc.database.net.net.Net>`
          Terminal Net object.




   .. py:property:: port_post_processing_prop


   .. py:property:: horizontal_extent_factor
      :type: float


      Horizontal extent factor.

      Returns
      -------
      float
          Extent value.



   .. py:property:: vertical_extent_factor
      :type: float


      Vertical extent factor.

      Returns
      -------
      float
          Vertical extent value.




   .. py:property:: pec_launch_width
      :type: float


      Launch width for the printed electronic component (PEC).

      Returns
      -------
      float
          Pec launch width value.



   .. py:property:: reference_layer

      Get layer of the terminal.



   .. py:property:: hfss_type
      :type: str


      HFSS port type.



   .. py:property:: do_renormalize
      :type: bool


      Determine whether port renormalization is enabled.

      Returns
      -------
      bool




   .. py:property:: renormalization_impedance
      :type: float


      Get the renormalization impedance value.

      Returns
      -------
      float




   .. py:property:: net_name
      :type: str


      Net name.

      Returns
      -------
      str : name of the net.



   .. py:property:: terminal_type
      :type: str | None


      Terminal Type. Accepted values for setter: `"edge"`, `"point"`, `"terminal_instance"`,
      `"padstack_instance"`, `"bundle_terminal"`, `"pin_group"`.

      Returns
      -------
      str



   .. py:property:: boundary_type
      :type: str


      Boundary type.

      Returns
      -------
      str
          port, pec, rlc, current_source, voltage_source, nexxim_ground, nexxim_pPort, dc_terminal, voltage_probe.



   .. py:property:: source_amplitude
      :type: float


      Source amplitude.

      Returns
      -------
      float : amplitude value.



   .. py:property:: source_phase
      :type: float


      Source phase.

      Returns
      -------
      float : phase value.



   .. py:property:: is_port
      :type: bool


      Whether it is a port.

      Returns
      -------
      bool




   .. py:property:: is_current_source
      :type: bool


      Whether it is a current source.

      Returns
      -------
      bool




   .. py:property:: is_voltage_source
      :type: bool


      Whether it is a voltage source.

      Returns
      -------
      bool




   .. py:property:: impedance
      :type: float


      Impedance of the port.

      Returns
      -------
      float : impedance value.




   .. py:property:: reference_object
      :type: any


      This returns the object assigned as reference. It can be a primitive or a padstack instance.


      Returns
      -------
      :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>` or
      :class:`Primitive <pyedb.grpc.database.primitive.primitives.Primitive>`



   .. py:property:: reference_net_name
      :type: str


      Net name to which reference_object belongs.

      Returns
      -------
      str : net name.




   .. py:method:: get_padstack_terminal_reference_pin(gnd_net_name_preference=None) -> pyedb.grpc.database.primitive.padstack_instance.PadstackInstance

      Get a list of pad stacks instances and serves Coax wave ports,
      pingroup terminals, PadEdge terminals.

      Parameters
      ----------
      gnd_net_name_preference : str, optional
          Preferred reference net name.

      Returns
      -------
      :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`



   .. py:method:: get_pin_group_terminal_reference_pin(gnd_net_name_preference=None) -> pyedb.grpc.database.primitive.padstack_instance.PadstackInstance

      Return a list of pins and serves terminals connected to pingroups.

      Parameters
      ----------
      gnd_net_name_preference : str, optional
          Preferred reference net name.

      Returns
      -------
      :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`



   .. py:method:: get_edge_terminal_reference_primitive() -> any

      Check and return a primitive instance that serves Edge ports,
      wave-ports and coupled-edge ports that are directly connected to primitives.

      Returns
      -------
      :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`



   .. py:method:: get_point_terminal_reference_primitive() -> pyedb.grpc.database.primitive.primitive.Primitive

      Find and return the primitive reference for the point terminal or the padstack instance.

      Returns
      -------
      Primitive or PadstackInstance
          The primitive reference for the point terminal or the padstack instance.
          Returns an instance of :class:`PadstackInstance
          <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
          or :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`.



   .. py:method:: get_pad_edge_terminal_reference_pin(gnd_net_name_preference=None) -> pyedb.grpc.database.primitive.padstack_instance.PadstackInstance

      Get the closest pin padstack instances and serves any edge terminal connected to a pad.

      Parameters
      ----------
      gnd_net_name_preference : str, optional
          Preferred reference net name. Optianal, default is `None` which will auto compute the gnd name.

      Returns
      -------
      :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`



   .. py:property:: magnitude
      :type: float


      Get the magnitude of the source.

      Returns
      -------
      float : source magnitude.



   .. py:property:: phase
      :type: float


      Get the phase of the source.

      Returns
      -------
      float : source phase.




   .. py:property:: terminal_to_ground


   .. py:property:: reference_terminal

      Return reference terminal.

      Returns
      -------
      PadstackInstanceTerminal
          Reference terminal object.



   .. py:property:: name

      Terminal name.



   .. py:property:: is_circuit_port
      :type: bool


      Whether the terminal is a circuit port.

      Returns
      -------
      bool




   .. py:property:: is_circuit
      :type: bool


      Check if the terminal is a circuit terminal.

      .. deprecated:: 0.70.0
          The `is_circuit` property is deprecated. Please use `is_circuit_port` instead.

      Returns
      -------
      bool
          True if the terminal is a circuit terminal, False otherwise.



