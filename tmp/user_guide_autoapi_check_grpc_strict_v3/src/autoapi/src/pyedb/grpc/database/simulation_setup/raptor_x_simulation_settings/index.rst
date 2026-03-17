src.pyedb.grpc.database.simulation_setup.raptor_x_simulation_settings
=====================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.raptor_x_simulation_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.raptor_x_simulation_settings.RaptorXSimulationSettings


Module Contents
---------------

.. py:class:: RaptorXSimulationSettings(pedb, core: ansys.edb.core.simulation_setup.raptor_x_simulation_setup.RaptorXSimulationSettings)

   Raptor X simulation settings class.


   .. py:attribute:: core


   .. py:property:: advanced_settings
      :type: pyedb.grpc.database.simulation_setup.raptor_x_advanced_settings.RaptorXAdvancedSettings


      Advanced settings class.

      .. deprecated:: 0.70.0
              Use :attr:`advanced` instead.

      Returns
      -------
      :class:`RaptorXAdvancedSettings <pyedb.grpc.database.simulation_setup.
      raptor_x_advanced_settings.RaptorXAdvancedSettings>`




   .. py:property:: advanced
      :type: pyedb.grpc.database.simulation_setup.raptor_x_advanced_settings.RaptorXAdvancedSettings


      Advanced class.

      Returns
      -------
      :class:`RaptorXAdvancedSettings <pyedb.grpc.database.simulation_setup.
      raptor_x_advanced_settings.RaptorXAdvancedSettings>`




   .. py:property:: general_settings
      :type: pyedb.grpc.database.simulation_setup.raptor_x_general_settings.RaptorXGeneralSettings


      General settings class.

      Returns
      -------
      :class:`RaptorXGeneralSettings <pyedb.grpc.database.simulation_setup.
      raptor_x_general_settings.RaptorXGeneralSettings>`




   .. py:property:: general
      :type: pyedb.grpc.database.simulation_setup.raptor_x_general_settings.RaptorXGeneralSettings


      General settings class.

      Returns
      -------
      :class:`RaptorXGeneralSettings <pyedb.grpc.database.simulation_setup.
      raptor_x_general_settings.RaptorXGeneralSettings>`




   .. py:property:: enabled
      :type: bool


      Enabled flag.

      Returns
      -------
      bool
          Enabled flag.




