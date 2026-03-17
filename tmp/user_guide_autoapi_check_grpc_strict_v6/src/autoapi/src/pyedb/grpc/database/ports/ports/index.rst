src.pyedb.grpc.database.ports.ports
===================================

.. py:module:: src.pyedb.grpc.database.ports.ports


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.ports.ports.GapPort
   src.pyedb.grpc.database.ports.ports.CircuitPort
   src.pyedb.grpc.database.ports.ports.WavePort
   src.pyedb.grpc.database.ports.ports.ExcitationSources
   src.pyedb.grpc.database.ports.ports.BundleWavePort
   src.pyedb.grpc.database.ports.ports.CoaxPort


Module Contents
---------------

.. py:class:: GapPort(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal`


   Manages gap port properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
       Edge terminal instance from EDB.

   Examples
   --------
   This example shows how to access the ``GapPort`` class.
   >>> from pyedb import Edb
   >>> edb = Edb("myaedb.aedb")
   >>> gap_port = edb.ports["gap_port"]


   .. py:property:: renormalize
      :type: bool


      Whether renormalize is active.

      Returns
      -------
      bool



   .. py:property:: deembed
      :type: bool


      Deembed gap port.

      Returns
      -------
      bool




   .. py:property:: renormalize_z0
      :type: tuple[float, float]


      Renormalize Z0 value (real, imag).

      Returns
      -------
      Tuple(float, float)
          (Real value, Imaginary value).



.. py:class:: CircuitPort(pedb, edb_object)

   Bases: :py:obj:`GapPort`


   Manages gap port properties.
   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
       Edge terminal instance from EDB.
   Examples
   --------
   This example shows how to access the ``GapPort`` class.


.. py:class:: WavePort(pedb, edb_terminal)

   Bases: :py:obj:`pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal`


   Manages wave port properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
       Edge terminal instance from EDB.

   Examples
   --------
   This example shows how to access the ``WavePort`` class.

   >>> from pyedb import Edb
   >>> edb = Edb("myaedb.aedb")
   >>> exc = edb.ports


   .. py:property:: deembed
      :type: bool


      Whether deembed is active.

      Returns
      -------
      bool




   .. py:property:: deembed_length
      :type: float


      Deembed Length.

      Returns
      -------
      float
          deembed value.



.. py:class:: ExcitationSources(pedb, edb_terminal)

   Bases: :py:obj:`pyedb.grpc.database.terminal.edge_terminal.EdgeTerminal`


   Manage sources properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       Edb object from Edblib.
   edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
       Edge terminal instance from Edb.



   Examples
   --------
   This example shows how to access this class.
   >>> from pyedb import Edb
   >>> edb = Edb("myaedb.aedb")
   >>> all_sources = edb.sources
   >>> print(all_sources["VSource1"].name)



.. py:class:: BundleWavePort(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.terminal.bundle_terminal.BundleTerminal`


   Manages bundle wave port properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.BundleTerminal
       BundleTerminal instance from EDB.



   .. py:property:: horizontal_extent_factor
      :type: float


      Horizontal extent factor.

      Returns
      -------
      float
          Horizontal extent value.



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
          Width value.



   .. py:property:: deembed
      :type: bool


      Whether deembed is active.

      Returns
      -------
      bool



   .. py:property:: deembed_length
      :type: float


      Deembed Length.

      Returns
      -------
      float
          Length value.



.. py:class:: CoaxPort(pedb, edb_object)

   Bases: :py:obj:`pyedb.grpc.database.terminal.padstack_instance_terminal.PadstackInstanceTerminal`


   Manages bundle wave port properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.PadstackInstanceTerminal
       PadstackInstanceTerminal instance from EDB.



   .. py:property:: radial_extent_factor

      Radial extent factor.

      Returns
      -------
      float
          Radial extent value.



