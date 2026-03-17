src.pyedb.dotnet.database.cell.terminal.padstack_instance_terminal
==================================================================

.. py:module:: src.pyedb.dotnet.database.cell.terminal.padstack_instance_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal


Module Contents
---------------

.. py:class:: PadstackInstanceTerminal(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.terminal.Terminal`


   Manages bundle terminal properties.


   .. py:property:: position

      Return terminal position.
      Returns
      -------
      Position [x,y] : [float, float]



   .. py:property:: location

      Location of the padstack instance.



   .. py:method:: create(padstack_instance, name=None, layer=None, is_ref=False)

      Create an edge terminal.

      Parameters
      ----------
      prim_id : int
          Primitive ID.
      point_on_edge : list
          Coordinate of the point to define the edge terminal.
          The point must be on the target edge but not on the two
          ends of the edge.
      terminal_name : str, optional
          Name of the terminal. The default is ``None``, in which case the
          default name is assigned.
      is_ref : bool, optional
          Whether it is a reference terminal. The default is ``False``.

      Returns
      -------
      Edb.Cell.Terminal.EdgeTerminal



   .. py:property:: padstack_instance


   .. py:property:: layer

      Get layer of the terminal.



