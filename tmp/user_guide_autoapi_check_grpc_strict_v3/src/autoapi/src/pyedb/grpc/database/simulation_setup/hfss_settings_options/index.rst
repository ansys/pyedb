src.pyedb.grpc.database.simulation_setup.hfss_settings_options
==============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_settings_options


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_settings_options.HFSSSettingsOptions


Module Contents
---------------

.. py:class:: HFSSSettingsOptions(parent)

   PyEDB-core HFSS settings options class.


   .. py:attribute:: core


   .. py:property:: do_lambda_refine
      :type: bool


      Flag to enable/disable lambda refinement.

      Returns
      -------
      bool
          True if lambda refinement is enabled, False otherwise.




   .. py:property:: enhanced_low_frequency_accuracy
      :type: bool


      Flag to enable/disable enhanced low frequency accuracy.

      Returns
      -------
      bool
          True if enhanced low frequency accuracy is enabled, False otherwise.




   .. py:property:: lambda_target
      :type: float


      Lambda target value.

      Returns
      -------
      float
          Lambda target value.




   .. py:property:: max_refinement_per_pass
      :type: int


      Maximum refinement per pass.

      Returns
      -------
      int
          Maximum refinement per pass.




   .. py:property:: mesh_size_factor
      :type: float


      Mesh size factor.

      Returns
      -------
      float
          Mesh size factor.




   .. py:property:: min_converged_passes
      :type: int


      Minimum converged passes.

      Returns
      -------
      int
          Minimum converged passes.




   .. py:property:: min_passes
      :type: int


      Minimum passes.

      Returns
      -------
      int
          Minimum passes.




   .. py:property:: order_basis
      :type: str


      Order basis name.

      Returns
      -------
      str
          Order basis name.




   .. py:property:: relative_residual
      :type: float


      Relative residual value that the HFSS iterative solver is to use.

      Returns
      -------
      float
          Relative residual value.




   .. py:property:: solver_type


   .. py:property:: use_default_lambda_value
      :type: bool


      Flag to indicate whether to use the default lambda value.

      Returns
      -------
      bool
          True if using the default lambda value, False otherwise.




   .. py:property:: use_max_refinement
      :type: float


      Flag to indicate whether to use maximum refinement.

      Returns
      -------
      bool
          True if using maximum refinement, False otherwise.




   .. py:property:: use_shell_elements
      :type: bool


      Flag to indicate whether to use shell elements.

      Returns
      -------
      bool
          True if using shell elements, False otherwise.




