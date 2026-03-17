src.pyedb.grpc.database.terminal.bundle_terminal
================================================

.. py:module:: src.pyedb.grpc.database.terminal.bundle_terminal


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.terminal.bundle_terminal.BundleTerminal


Module Contents
---------------

.. py:class:: BundleTerminal(pedb, core)

   Bases: :py:obj:`pyedb.grpc.database.terminal.terminal.Terminal`


   Manages bundle terminal properties.

   Parameters
   ----------
   pedb : :class:`Edb <pyedb.grpc.edb.Edb>`
       EDB object.
   edb_object : :class:`BundleTerminal <ansys.edb.core.terminal.terminals.BundleTerminal>`
       BundleTerminal instance from EDB.


   .. py:attribute:: core


   .. py:method:: create(pedb, name: str, terminals: list[Union[pyedb.grpc.database.terminal.terminal.Terminal, pyedb.grpc.database.ports.ports.WavePort, str]]) -> BundleTerminal
      :classmethod:


      Create a bundle terminal.

      Parameters
      ----------
      name : str
          Bundle terminal name.
      terminals : list[Union[Terminal, WavePort]]
          List of terminals to bundle.

      Returns
      -------
      BundleTerminal
          The created bundle terminal.



   .. py:property:: is_reference_terminal
      :type: bool


      Check if the bundle terminal is a reference terminal.

      Returns
      -------
      bool



   .. py:method:: decouple() -> bool

      Ungroup a bundle of terminals.

      Returns
      -------
      bool



   .. py:property:: component
      :type: pyedb.grpc.database.hierarchy.component.Component


      Component.

      Returns
      -------
      :class:`Component <pyedb.grpc.database.hierarchy.component.Component`



   .. py:property:: net
      :type: pyedb.grpc.database.net.net.Net


      Returns Net object.

      Returns
      -------
      :class:`Net <pyedb.grpc.database.net.net.Net>`



   .. py:property:: hfss_pi_type
      :type: str


      Returns HFSS PI type.

      Returns
      -------
      str



   .. py:property:: rlc_boundary_parameters
      :type: pyedb.grpc.database.utility.rlc.Rlc


      Returns Rlc parameters

      Returns
      -------
      :class:`Rlc <pyedb.grpc.database.utility.rlc.Rlc>`



   .. py:property:: term_to_ground
      :type: str


      Returns terminal to ground.

      Returns
      -------
      str
          Terminal name.



   .. py:property:: terminals
      :type: list[pyedb.grpc.database.terminal.terminal.Terminal]



