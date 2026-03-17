src.pyedb.dotnet.database.cell.terminal.pingroup_terminal
=========================================================

.. py:module:: src.pyedb.dotnet.database.cell.terminal.pingroup_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal


Module Contents
---------------

.. py:class:: PinGroupTerminal(pedb, edb_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.terminal.Terminal`


   Manages pin group terminal properties.


   .. py:method:: create(name, net_name, pin_group_name, is_ref=False)

      Create a pin group terminal.

      Parameters
      ----------
      name : str
          Name of the terminal.
      net_name : str
          Name of the net.
      pin_group_name : str,
          Name of the pin group.
      is_ref : bool, optional
          Whether it is a reference terminal. The default is ``False``.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`



   .. py:property:: pin_group

      Gets the pin group the terminal refers to.



