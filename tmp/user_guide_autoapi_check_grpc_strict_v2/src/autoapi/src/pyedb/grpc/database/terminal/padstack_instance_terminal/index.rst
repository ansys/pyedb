src.pyedb.grpc.database.terminal.padstack_instance_terminal
===========================================================

.. py:module:: src.pyedb.grpc.database.terminal.padstack_instance_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal


Module Contents
---------------

.. py:class:: PadstackInstanceTerminal(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.terminal.terminal.Terminal`


   Manages bundle terminal properties.


   .. py:method:: create(layout, name, padstack_instance, layer, is_ref=False, net=None) -> PadstackInstanceTerminal
      :classmethod:


      Create a padstack instance terminal.
      Parameters
      ----------
      layout : :class: <``Layout` pyedb.grpc.database.layout.layout.Layout>
          Layout object associated with the terminal.
      name : str
          Terminal name.
      padstack_instance : PadstackInstance
          Padstack instance object.
      layer : str
          Layer name.
      is_ref : bool, optional
          Whether the terminal is a reference terminal. Default is False.
      Returns
      -------
      PadstackInstanceTerminal
          Padstack instance terminal object.



   .. py:property:: is_reference_terminal
      :type: bool


      Check if the terminal is a reference terminal.

      Returns
      -------
      bool
          True if the terminal is a reference terminal, False otherwise.



   .. py:property:: id
      :type: int


      Terminal ID.

      Returns
      -------
      int
          Terminal ID.



   .. py:property:: edb_uid
      :type: int


      Terminal EDB UID.

      Returns
      -------
      int
          Terminal EDB UID.



   .. py:property:: net
      :type: pyedb.grpc.database.net.net.Net


      Net.

      Returns
      -------
      :class:`Net <pyedb.grpc.database.net.net.Net>`
          Terminal net.



   .. py:property:: position
      :type: tuple[float, float]


      Terminal position.

      Returns
      -------
      Position [x,y] : [float, float]



   .. py:property:: padstack_instance
      :type: pyedb.grpc.database.primitive.padstack_instance.PadstackInstance



   .. py:property:: component
      :type: pyedb.grpc.database.hierarchy.component.Component



   .. py:property:: location
      :type: tuple[float, float]


      Terminal position.

      Returns
      -------
      Position [x,y] : [float, float]



