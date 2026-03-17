src.pyedb.grpc.database.simulation_setups
=========================================

.. py:module:: src.pyedb.grpc.database.simulation_setups


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setups.SimulationSetups


Module Contents
---------------

.. py:class:: SimulationSetups(pedb)

   Simulation setups container class.


   .. py:property:: hfss
      :type: dict[str, pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup]


      HFSS simulation setups.

      Returns
      -------
      List[:class:`HFSSSimulationSetup <pyedb.grpc.database.simulation_setup.
      hfss_simulation_setup.HFSSSimulationSetup>`]



   .. py:property:: siwave
      :type: dict[str, pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup]


      SIWave simulation setups.

      Returns
      -------
      List[:class:`SIWaveSimulationSetup <pyedb.grpc.database.simulation_setup.
      siwave_simulation_setup.SIWaveSimulationSetup>`]



   .. py:property:: siwave_dcir
      :type: dict[str, pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup]


      SIWave DCIR simulation setups.

      Returns
      -------
      List[:class:`SIWaveDCIRSimulationSetup <pyedb.grpc.database.simulation_setup.
      siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup>`]



   .. py:property:: siwave_cpa
      :type: dict[str, pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup.SIWaveCPASimulationSetup]


      SIWave CPA simulation setups.

      Returns
      -------
      List[:class:`SIWaveCPASimulationSetup <pyedb.grpc.database.simulation_setup.
      siwave_cpa_simulation_setup.SIWaveCPASimulationSetup>`]



   .. py:property:: raptor_x
      :type: dict[str, pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup.RaptorXSimulationSetup]


      RaptorX simulation setups.

      Returns
      -------
      List[:class:`RaptorXSimulationSetup <pyedb.grpc.database.simulation_setup.
      raptor_x_simulation_setup.RaptorXSimulationSetup>`]



   .. py:property:: q3d
      :type: dict[str, pyedb.grpc.database.simulation_setup.q3d_simulation_setup.Q3DSimulationSetup]


      Q3D simulation setups.

      Returns
      -------
      List[:class:`Q3DSimulationSetup <pyedb.grpc.database.simulation_setup.
      q3d_simulation_setup.Q3DSimulationSetup>`]



   .. py:property:: hfss_pi
      :type: dict[str, pyedb.dotnet.database.utilities.hfss_simulation_setup.HFSSPISimulationSetup]


      HFSS PI simulation setups.

      Returns
      -------
      List[:class:`HFSSPISimulationSetup <pyedb.grpc.database.simulation_setup.
      hfss_pi_simulation_setup.HFSSPISimulationSetup>`]



   .. py:property:: setups
      :type: dict[str, pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup | pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup | pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup | pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup.SIWaveCPASimulationSetup | pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup.RaptorXSimulationSetup | pyedb.grpc.database.simulation_setup.q3d_simulation_setup.Q3DSimulationSetup | pyedb.dotnet.database.utilities.hfss_simulation_setup.HFSSPISimulationSetup]


      All simulation setups.

      Returns
      -------
      dict[str:setup name, :class:`SimulationSetup <pyedb.grpc.database.simulation_setup.
      simulation_setup.SimulationSetup>`]



   .. py:method:: create(name=None, solver='hfss') -> pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetup | None

      Add analysis setup.

      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).
      solver : str, optional
          Simulation setup type ("hfss", "siwave", "siwave_dcir", "raptor_x", "q3d", "hfss_pi").

      Returns
      -------



   .. py:method:: create_hfss_setup(name=None, distribution='linear', start_freq: float = None, stop_freq: float = None, step_freq: float = None, discrete_sweep=False, sweep_name: str = 'frequency_sweep', **kwargs) -> pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup

      Add HFSS analysis setup.

      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).
      distribution : str, optional
          Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
      start_freq : float, str, optional
          Starting frequency (Hz).
      stop_freq : float, str, optional
          Stopping frequency (Hz).
      step_freq : float, str, int, optional
      Frequency step (Hz) or count depending on distribution.
      discrete_sweep : bool, optional
          Use discrete sweep.
      sweep_name : str, optional
          Name of the frequency sweep.

      Returns
      -------
      HfssSimulationSetup
          Created setup object.



   .. py:method:: create_hfss_pi_setup(name=None, distribution='linear', start_freq: float = None, stop_freq: float = None, step_freq: float = None, discrete_sweep=False, sweep_name: str = 'frequency_sweep', **kwargs) -> pyedb.dotnet.database.utilities.hfss_simulation_setup.HFSSPISimulationSetup

      Add HFSS analysis setup.

      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).
      distribution : str, optional
          Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
      start_freq : float, str, optional
          Starting frequency (Hz).
      stop_freq : float, str, optional
          Stopping frequency (Hz).
      step_freq : float, str, int, optional
      Frequency step (Hz) or count depending on distribution.
      discrete_sweep : bool, optional
          Use discrete sweep.
      sweep_name : str, optional
          Name of the frequency sweep.

      Returns
      -------
      HfssSimulationSetup
          Created setup object.



   .. py:method:: create_siwave_setup(name=None, distribution='linear', start_freq: float = None, stop_freq: float = None, step_freq: float = None, discrete_sweep=False, sweep_name: str = 'frequency_sweep', **kwargs) -> pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup

      Add SIWave analysis setup.

      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).
      distribution : str, optional
          Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
      start_freq : float, str, optional
          Starting frequency (Hz).
      stop_freq : float, str, optional
          Stopping frequency (Hz).
      step_freq : float, str, int, optional
          Frequency step (Hz) or count depending on distribution.
      discrete_sweep : bool, optional
          Use discrete sweep.
      sweep_name : str, optional
          Name of the frequency sweep.

      Returns
      -------
      SIWaveSimulationSetup
          Created setup object.



   .. py:method:: create_siwave_dcir_setup(name=None, **kwargs) -> pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup

      Add SIWave DCIR analysis setup.

      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).

      Returns
      -------
      SIWaveDCIRSimulationSetup
          Created setup object.



   .. py:method:: create_siwave_cpa_setup(name=None, siwave_cpa_config=None, **kwargs) -> pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup.SIWaveCPASimulationSetup

      Add SIWave CPA analysis setup.

      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).

      Returns
      -------
      SIWaveCPASimulationSetup
          Created setup object.



   .. py:method:: create_raptor_x_setup(name=None, distribution='linear', start_freq: float = None, stop_freq: float = None, step_freq: float = None, discrete_sweep=False, sweep_name: str = 'frequency_sweep', **kwargs) -> pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup.RaptorXSimulationSetup

      Add RaptorX analysis setup
      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).
      distribution : str, optional
          Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
      start_freq : float, str, optional
          Starting frequency (Hz).
      stop_freq : float, str, optional
          Stopping frequency (Hz).
      step_freq : float, str, int, optional
          Frequency step (Hz) or count depending on distribution.
      discrete_sweep : bool, optional
          Use discrete sweep.
      sweep_name : str, optional
          Name of the frequency sweep.
      Returns
      -------
      RaptorXSimulationSetup
          Created setup object.



   .. py:method:: create_q3d_setup(name=None, distribution='linear', start_freq: float = None, stop_freq: float = None, step_freq: float = None, discrete_sweep=False, sweep_name: str = 'frequency_sweep', **kwargs) -> pyedb.grpc.database.simulation_setup.q3d_simulation_setup.Q3DSimulationSetup

      Add Q3D analysis setup
      Parameters
      ----------
      name : str, optional
          Setup name (auto-generated if None).
      distribution : str, optional
          Sweep distribution type ("linear", "linear_count", "decade_count", "octave_count", "exponential").
      start_freq : float, str, optional
          Starting frequency (Hz).
      stop_freq : float, str, optional
          Stopping frequency (Hz).
      step_freq : float, str, int, optional
          Frequency step (Hz) or count depending on distribution.
      discrete_sweep : bool, optional
          Use discrete sweep.
      sweep_name : str, optional
          Name of the frequency sweep.
      Returns
      -------
      Q3DSimulationSetup
          Created setup object.



