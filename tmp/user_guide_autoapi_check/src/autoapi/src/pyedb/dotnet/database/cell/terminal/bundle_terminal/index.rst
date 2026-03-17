src.pyedb.dotnet.database.cell.terminal.bundle_terminal
=======================================================

.. py:module:: src.pyedb.dotnet.database.cell.terminal.bundle_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.terminal.bundle_terminal.BundleTerminal


Module Contents
---------------

.. py:class:: BundleTerminal(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.terminal.Terminal`


   Manages bundle terminal properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.BundleTerminal
       BundleTerminal instance from EDB.


   .. py:property:: terminals

      Get terminals belonging to this excitation.



   .. py:method:: decouple()

      Ungroup a bundle of terminals.



   .. py:method:: create(pedb, name, terminals)
      :classmethod:



