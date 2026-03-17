src.pyedb.grpc.database.simulation_setup.hfss_dcr_settings
==========================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_dcr_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings


Module Contents
---------------

.. py:class:: HFSSDCRSettings(parent)

   PyEDB HFSS DC settings class.


   .. py:attribute:: core


   .. py:property:: conduction_max_passes
      :type: int


      Maximum number of conduction adaptive passes.

      ... deprecated:: 0.77.3
      Use :attr:`max_passes <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.max_passes>`
      nstead.



   .. py:property:: max_passes
      :type: int


      Maximum number of conduction adaptive passes.



   .. py:property:: conduction_min_converged_passes
      :type: int


      Minimum number of converged conduction adaptive passes.

      ... deprecated:: 0.77.3
      Use :attr:`min_converged_passes
      <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.min_converged_passes>`
      instead.



   .. py:property:: min_converged_passes
      :type: int


      Minimum number of converged conduction adaptive passes.



   .. py:property:: conduction_min_passes
      :type: int


      Minimum number of conduction adaptive passes.

      ... deprecated:: 0.77.3
      Use :attr:`min_passes <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.min_passes>`
      instead.



   .. py:property:: min_passes
      :type: int


      Minimum number of conduction adaptive passes.



   .. py:property:: conduction_per_error
      :type: float


      Conduction adaptive percent error.

      ... deprecated:: 0.77.3
      Use :attr:`percent_error <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.percent_error>`
      instead.



   .. py:property:: percent_error
      :type: float


      Conduction adaptive percent error.



   .. py:property:: conduction_per_refine
      :type: float


      Conduction adaptive percent refinement per pass.

      ... deprecated:: 0.77.3
      Use :attr:
      `percent_refinement_per_pass
      <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.percent_refinement_per_pass>`
      instead.



   .. py:property:: percent_refinement_per_pass
      :type: float


      Conduction adaptive percent refinement per pass.



