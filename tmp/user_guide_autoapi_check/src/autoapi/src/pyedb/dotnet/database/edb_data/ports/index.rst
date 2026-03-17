src.pyedb.dotnet.database.edb_data.ports
========================================

.. py:module:: src.pyedb.dotnet.database.edb_data.ports


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.ports.GapPort
   src.pyedb.dotnet.database.edb_data.ports.CircuitPort
   src.pyedb.dotnet.database.edb_data.ports.WavePort
   src.pyedb.dotnet.database.edb_data.ports.ExcitationSources
   src.pyedb.dotnet.database.edb_data.ports.BundleWavePort
   src.pyedb.dotnet.database.edb_data.ports.CoaxPort


Module Contents
---------------

.. py:class:: GapPort(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal`


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

      Whether renormalize is active.



   .. py:property:: renormalize_z0

      Renormalize Z0 value (real, imag).



   .. py:property:: renormalization_impedance


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

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal`


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


.. py:class:: ExcitationSources(pedb, edb_terminal)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.terminal.Terminal`


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



.. py:class:: BundleWavePort(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.bundle_terminal.BundleTerminal`


   Manages bundle wave port properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.BundleTerminal
       BundleTerminal instance from EDB.



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



.. py:class:: CoaxPort(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal`


   Manages bundle wave port properties.

   Parameters
   ----------
   pedb : pyedb.edb.Edb
       EDB object from the ``Edblib`` library.
   edb_object : Ansys.Ansoft.Edb.Cell.Terminal.PadstackInstanceTerminal
       PadstackInstanceTerminal instance from EDB.



   .. py:property:: radial_extent_factor

      Radial extent factor.



