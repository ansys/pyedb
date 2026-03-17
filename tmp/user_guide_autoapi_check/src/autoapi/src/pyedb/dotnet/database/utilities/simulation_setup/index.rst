src.pyedb.dotnet.database.utilities.simulation_setup
====================================================

.. py:module:: src.pyedb.dotnet.database.utilities.simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.utilities.simulation_setup.SimulationSetupType
   src.pyedb.dotnet.database.utilities.simulation_setup.AdaptiveType
   src.pyedb.dotnet.database.utilities.simulation_setup.SimulationSetup


Module Contents
---------------

.. py:class:: SimulationSetupType(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Create a collection of name/value pairs.

   Example enumeration:

   >>> class Color(Enum):
   ...     RED = 1
   ...     BLUE = 2
   ...     GREEN = 3

   Access them by:

   - attribute access::

   >>> Color.RED
   <Color.RED: 1>

   - value lookup:

   >>> Color(1)
   <Color.RED: 1>

   - name lookup:

   >>> Color['RED']
   <Color.RED: 1>

   Enumerations can be iterated over, and know how many members they have:

   >>> len(Color)
   3

   >>> list(Color)
   [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]

   Methods can be added to enumerations, and members can have their own
   attributes -- see the documentation for details.


   .. py:attribute:: kHFSS
      :value: 'hfss'



   .. py:attribute:: hfss
      :value: 'hfss'



   .. py:attribute:: kPEM
      :value: None



   .. py:attribute:: kSIwave
      :value: 'siwave_ac'



   .. py:attribute:: siwave
      :value: 'siwave_ac'



   .. py:attribute:: kLNA
      :value: 'lna'



   .. py:attribute:: kTransient
      :value: 'transient'



   .. py:attribute:: kQEye
      :value: 'quick_eye'



   .. py:attribute:: kVEye
      :value: 'verif_eye'



   .. py:attribute:: kAMI
      :value: 'ami'



   .. py:attribute:: kAnalysisOption
      :value: 'analysis_option'



   .. py:attribute:: kSIwaveDCIR
      :value: 'siwave_dc'



   .. py:attribute:: siwave_dc
      :value: 'siwave_dc'



   .. py:attribute:: kSIwaveEMI
      :value: 'siwave_emi'



   .. py:attribute:: kHFSSPI
      :value: 'hfss_pi'



   .. py:attribute:: kDDRwizard
      :value: 'ddrwizard'



   .. py:attribute:: kQ3D
      :value: 'q3d'



   .. py:attribute:: unknown
      :value: 'unknown'



.. py:class:: AdaptiveType

   Bases: :py:obj:`object`


.. py:class:: SimulationSetup(pedb, edb_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.obj_base.SystemObject`


   Provide base simulation setup.

   Parameters
   ----------
   pedb : :class:`pyedb.dotnet.edb.Edb`
       Inherited object.
   edb_object : :class:`Ansys.Ansoft.Edb.Utility.SIWaveSimulationSetup`,
   :class:`Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings`,
   :class:`Ansys.Ansoft.Edb.Utility.HFSSSimulationSettings`
       EDB object.


   .. py:property:: sim_setup_info


   .. py:method:: set_sim_setup_info(sim_setup_info: pyedb.dotnet.database.sim_setup_data.data.sim_setup_info.SimSetupInfo)


   .. py:property:: is_null

      Adding this property for compatibility with grpc.



   .. py:method:: get_simulation_settings()


   .. py:method:: set_simulation_settings(sim_settings: dict)


   .. py:property:: type


   .. py:property:: mesh_operations


   .. py:property:: enabled


   .. py:property:: name

      Name of the setup.



   .. py:property:: position

      Position in the setup list.



   .. py:property:: setup_type

      Type of the setup.



   .. py:property:: frequency_sweeps


   .. py:property:: sweeps

      List of frequency sweeps.



   .. py:property:: sweep_data

      Adding property for compatibility with grpc.



   .. py:method:: add_sweep(name: str = None, distribution: str = None, start_freq: str = None, stop_freq: str = None, step=None, frequency_set: list = None, discrete=False, **kwargs)

      Add frequency sweep.

      Parameters
      ----------
      name : str, optional
          Name of the frequency sweep. The default is ``None``.
      distribution : str, optional
          Added for grpc compatibility.
      start_freq : str, optional
          Added for rpc compatibility.
      stop_freq : str, optional
          Added for grpc compatibility.
      step : optional
          Added for grpc compatibility.
      frequency_set : list, optional
          List of frequency points. The default is ``None``.
      sweep_type : str, optional
          Sweep type. The default is ``"interpolation"``. Options are ``"discrete"``,"discrete"``.
      Returns
      -------

      Examples
      --------
      >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
      >>> setup1.add_sweep(name="sw1", frequency_set=["linear count", "1MHz", "100MHz", 10])



   .. py:method:: delete()

      Delete current simulation setup.



   .. py:method:: delete_frequency_sweep(sweep_data)

      Delete a frequency sweep.

      Parameters
      ----------
          sweep_data : EdbFrequencySweep.



   .. py:method:: add_frequency_sweep(name=None, frequency_sweep=None)

      Add frequency sweep.

      Parameters
      ----------
      name : str, optional
          Name of the frequency sweep. The default is ``None``.
      frequency_sweep : list, optional
          List of frequency points. The default is ``None``.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.simulation_setup_data.EdbFrequencySweep`

      Examples
      --------
      >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
      >>> setup1.add_frequency_sweep(
      ...     frequency_sweep=[
      ...         ["linear count", "0", "1kHz", 1],
      ...         ["log scale", "1kHz", "0.1GHz", 10],
      ...         ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
      ...     ]
      ... )



   .. py:property:: settings
      :abstractmethod:


      Get the settings interface for SIwave DC simulation.

      Returns
      -------
      SIWaveSimulationSettings
          An instance of the Settings class providing access to SIwave DC simulation settings.



