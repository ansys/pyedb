src.pyedb.grpc.database.terminal.edge_terminal
==============================================

.. py:module:: src.pyedb.grpc.database.terminal.edge_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal


Module Contents
---------------

.. py:class:: EdgeTerminal(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.terminal.terminal.Terminal`


   Represents a layout object.


   .. py:method:: create(layout, name, edge, net, is_ref=False)
      :classmethod:


      Create an edge terminal.

      Parameters
      ----------
      layout : :class:`pyedb.grpc.database.layout.layout.Layout`
          Layout object.
      name : str
          Terminal name.
      edge : :class:`.Edge`
          Edge object.
      net : :class:`.Net` or str, optional
          Net object or net name. If None, the terminal will not be assigned to any net.
      is_ref : bool, optional
          Whether the terminal is a reference terminal. Default is False.

      Returns
      -------
      :class:`EdgeTerminal <pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal>`
          Edge terminal object.



   .. py:property:: component

      Component.

      Returns
      -------
      Component object.
          :class:`Component <pyedb.grpc.database.component.Component>`.



   .. py:property:: is_circuit_port
      :type: bool


      Is circuit port.

      Returns
      -------
      bool : circuit port.



   .. py:property:: port_post_processing_prop

      Port post-processing property.



   .. py:property:: is_wave_port
      :type: bool



   .. py:property:: is_reference_terminal
      :type: bool


      Added for dotnet compatibility

      Returns
      -------
      bool



   .. py:method:: set_product_solver_option(product_id, solver_name, option)

      Set product solver option.



   .. py:method:: couple_ports(port) -> pyedb.grpc.database.terminal.bundle_terminal.BundleTerminal

      Create a bundle wave port.

      Parameters
      ----------
      port : :class:`Waveport <pyedb.grpc.database.ports.ports.WavePort>`,
      :class:`GapPOrt <pyedb.grpc.database.ports.ports.GapPort>`, list, optional
          Ports to be added.

      Returns
      -------
      :class:`BundleWavePort <pyedb.grpc.database.ports.ports.BundleWavePort>`



