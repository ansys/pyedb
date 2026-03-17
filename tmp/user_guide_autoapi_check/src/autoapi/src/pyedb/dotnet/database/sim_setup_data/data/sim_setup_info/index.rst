src.pyedb.dotnet.database.sim_setup_data.data.sim_setup_info
============================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.data.sim_setup_info


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.data.sim_setup_info.SimSetupInfo


Module Contents
---------------

.. py:class:: SimSetupInfo(pedb, sim_setup, edb_object=None, setup_type: str = None, name: str = None)

   .. py:attribute:: core
      :value: None



   .. py:attribute:: sim_setup


   .. py:property:: name


   .. py:property:: position


   .. py:property:: sim_setup_type

      "kHFSS": self._pedb.simsetupdata.HFSSSimulationSettings,
      "kPEM": None,
      "kSIwave": self._pedb.simsetupdata.SIwave.SIWSimulationSettings,
      "kLNA": None,
      "kTransient": None,
      "kQEye": None,
      "kVEye": None,
      "kAMI": None,
      "kAnalysisOption": None,
      "kSIwaveDCIR": self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings,
      "kSIwaveEMI": None,
      "kHFSSPI": self._pedb.simsetupdata.HFSSPISimulationSettings,
      "kDDRwizard": None,
      "kQ3D": None,
      "kNumSetupTypes": None,



   .. py:property:: simulation_settings


   .. py:property:: sweep_data_list


   .. py:method:: add_sweep_data(sweep_data)


