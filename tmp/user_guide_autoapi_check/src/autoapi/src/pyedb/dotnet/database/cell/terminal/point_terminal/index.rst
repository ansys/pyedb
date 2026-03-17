src.pyedb.dotnet.database.cell.terminal.point_terminal
======================================================

.. py:module:: src.pyedb.dotnet.database.cell.terminal.point_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal


Module Contents
---------------

.. py:class:: PointTerminal(pedb, edb_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.terminal.Terminal`


   Manages point terminal properties.


   .. py:method:: create(name, net, location, layer, is_ref=False)

      Create a point terminal.

      Parameters
      ----------
      name : str
          Name of the terminal.
      net : str
          Name of the net.
      location : list
          Location of the terminal.
      layer : str
          Name of the layer.
      is_ref : bool, optional
          Whether it is a reference terminal.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`



   .. py:property:: layer

      Get layer of the terminal.



   .. py:property:: location

      Location of the terminal.



   .. py:property:: is_reference_terminal
      :type: bool


      Whether the terminal is a reference terminal.

      Returns
      -------
      bool
          True if the terminal is a reference terminal, False otherwise.




