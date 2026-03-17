src.pyedb.dotnet.database.cell.terminal.edge_terminal
=====================================================

.. py:module:: src.pyedb.dotnet.database.cell.terminal.edge_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal


Module Contents
---------------

.. py:class:: EdgeTerminal(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.terminal.Terminal`


   Manages EDB functionalities for a connectable object.


   .. py:method:: couple_ports(port)

      Create a bundle wave port.

      Parameters
      ----------
      port : :class:`dotnet.database.ports.WavePort`, :class:`dotnet.database.ports.GapPort`, list, optional
          Ports to be added.

      Returns
      -------
      :class:`dotnet.database.ports.BundleWavePort`




   .. py:property:: horizontal_extent_factor

      Horizontal extent factor.



   .. py:property:: vertical_extent_factor

      Vertical extent factor.



   .. py:property:: pec_launch_width

      Launch width for the printed electronic component (PEC).



   .. py:property:: deembed

      Whether deembed is active.



   .. py:property:: deembed_length

      Deembed Length.



