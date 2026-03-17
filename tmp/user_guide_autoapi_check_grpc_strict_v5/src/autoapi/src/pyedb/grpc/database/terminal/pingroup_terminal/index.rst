src.pyedb.grpc.database.terminal.pingroup_terminal
==================================================

.. py:module:: src.pyedb.grpc.database.terminal.pingroup_terminal


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.pingroup_terminal.boundary_type_mapping


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.pingroup_terminal.PinGroupTerminal


Module Contents
---------------

.. py:data:: boundary_type_mapping

.. py:class:: PinGroupTerminal(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.terminal.terminal.Terminal`


   Manages pin group terminal properties.


   .. py:property:: net
      :type: pyedb.grpc.database.net.net.Net


      Terminal net.

      Returns
      -------
      :class:`Net <pyedb.grpc.database.net.net.Net>`
          Terminal Net object.




   .. py:property:: pin_group
      :type: pyedb.grpc.database.hierarchy.pingroup.PinGroup


      Pingroup.

      Returns
      -------
      :class:`PinGroup <pyedb.grpc.database.hierarchy.pingroup.PinGroup>`
          Terminal pingroup.




   .. py:property:: is_reference_terminal
      :type: bool


      Check if the terminal is a reference terminal.

      Returns
      -------
      bool
          True if the terminal is a reference terminal, False otherwise.




   .. py:method:: create(layout, name, pin_group, net=None, is_ref=False) -> PinGroupTerminal
      :classmethod:


      Create a pin group terminal.
      Parameters
      ----------
      layout : :class:`.Layout`
          Layout to create the pin group terminal in.
      name : :obj:`str`
          Name of the pin group terminal.
      pin_group : :class:`.PinGroup`
          Pin group.
      net : :class:`.Net` or :obj:`str`, optional
          Net.
      is_ref : :obj:`bool`, default: False
          Whether the pin group terminal is a reference terminal.
      Returns
      -------
      PinGroupTerminal



