src.pyedb.dotnet.database.simulation_setups
===========================================

.. py:module:: src.pyedb.dotnet.database.simulation_setups


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.simulation_setups.SimulationSetups


Module Contents
---------------

.. py:class:: SimulationSetups(pedb)

   Simulation setups container class.


   .. py:method:: create(name=None, solver='hfss')

      Add analysis setup.

      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).
      solver : str, optional
          Simulation setup type ("hfss", "siwave", "siwave_dcir", "raptor_x", "q3d").



   .. py:method:: create_hfss_setup(name: str = None, distribution='linear', start_freq: float = None, stop_freq: float = None, freq_step: float = None, discrete_sweep=False, sweep_name: str = 'frequency_sweep') -> pyedb.dotnet.database.utilities.hfss_simulation_setup.HfssSimulationSetup

      Create an HFSS simulation setup from a template.

      Parameters
      ----------
      name : str, optional
          Setup name.

      Returns
      -------
      :class:`legacy.database.edb_data.hfss_simulation_setup_data.HfssSimulationSetup`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb()
      >>> setup1 = edbapp.create_hfss_setup("setup1")
      >>> setup1.hfss_port_settings.max_delta_z0 = 0.5



   .. py:method:: create_hfss_pi_setup(name=None)

      Create an HFSS PI simulation setup from a template.

      Parameters
      ----------
      name : str, optional
          Setup name.

      Returns
      -------
      :class:`legacy.database.edb_data.hfss_pi_simulation_setup_data.HFSSPISimulationSetup when succeeded, ``False``
      when failed.




   .. py:method:: create_raptor_x_setup(name=None)

      Create an RaptorX simulation setup from a template.

      Parameters
      ----------
      name : str, optional
          Setup name.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data.RaptorXSimulationSetup`




   .. py:method:: create_siwave_dcir_setup(name=None, **kwargs)

      Create a setup from a template.

      Parameters
      ----------
      name : str, optional
          Setup name.

      Returns
      -------
      :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb()
      >>> setup1 = edbapp.create_siwave_dc_setup("setup1")
      >>> setup1.mesh_bondwires = True




   .. py:method:: create_siwave_setup(name=None, **kwargs)

      Create a setup from a template.

      Parameters
      ----------
      name : str, optional
          Setup name.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb()
      >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
      >>> setup1.add_frequency_sweep(
      ...     frequency_sweep=[
      ...         ["linear count", "0", "1kHz", 1],
      ...         ["log scale", "1kHz", "0.1GHz", 10],
      ...         ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
      ...     ]
      ... )



