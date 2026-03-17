src.pyedb.grpc.database.simulation_setup.hfss_solver_settings
=============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_solver_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_solver_settings.HFSSSolverSettings


Module Contents
---------------

.. py:class:: HFSSSolverSettings(parent)

   HFSS solver settings class.


   .. py:attribute:: core


   .. py:property:: enable_intra_plane_coupling
      :type: bool


      Flag indicating if intra-plane coupling of power/ground nets is enabled to enhance accuracy..



   .. py:property:: max_delta_z0
      :type: float


      Maximum percent change in characteristic impedance of ports between adaptive passes.



   .. py:property:: max_triangles_wave_port
      :type: int


      Maximum number of triangles to use for meshing wave-ports.



   .. py:property:: max_triangles_for_wave_port
      :type: int


      Maximum number of triangles to use for meshing wave-ports.



   .. py:property:: min_triangles_wave_port
      :type: int


      Minimum number of triangles to use for meshing wave-ports.



   .. py:property:: min_triangles_for_wave_port
      :type: int


      Minimum number of triangles to use for meshing wave-ports.



   .. py:property:: enable_set_triangles_wave_port
      :type: bool


      Flag indicating if the minimum and maximum triangle values for wave-ports are used.



   .. py:property:: set_triangles_for_wave_port
      :type: bool


      Flag indicating ifthe minimum and maximum triangle values for wave-ports are used.



   .. py:property:: thin_dielectric_layer_threshold
      :type: float


      Value below which dielectric layers are merged with adjacent dielectric layers.



   .. py:property:: thin_signal_layer_threshold
      :type: float


      Value below which signal layers are merged with adjacent signal layers.



