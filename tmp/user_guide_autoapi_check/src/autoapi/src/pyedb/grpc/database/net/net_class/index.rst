src.pyedb.grpc.database.net.net_class
=====================================

.. py:module:: src.pyedb.grpc.database.net.net_class


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.net.net_class.NetClass


Module Contents
---------------

.. py:class:: NetClass(pedb, core)

   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> myedb = "path_to_your_edb_file.edb"
   >>> edb = Edb(myedb, version="2025.1")
   >>> edb.net_classes


   .. py:attribute:: core


   .. py:property:: name

      Net class name.

      Returns
      -------
      str
          Name of the net class.



   .. py:property:: nets

      Net list.

      Returns
      -------
      List[:class:`Net <pyedb.grpc.database.net.net.Net>`].
          List of Net object.



   .. py:method:: add_net(net)

      Add a net to the net class.

      Returns
      -------
      bool



   .. py:property:: is_null

      Check if the net class is a null net class.

      Returns
      -------
      bool
          ``True`` if the net class is a null net class, ``False`` otherwise.



   .. py:method:: contains_net(net) -> bool

      Determine if a net exists in the net class.

      Parameters
      ----------
      net : str or Net
          The net to check. This can be a string representing the net name or a `Net` object.

      Returns
      -------
      bool
          True if the net exists in the net class, False otherwise.




   .. py:method:: remove_net(net)

      Remove net.

      Returns
      -------
      bool



