src.pyedb.grpc.database.simulation_setup.hfss_pi_general_settings
=================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_pi_general_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_pi_general_settings.HFSSPIGeneralSettings


Module Contents
---------------

.. py:class:: HFSSPIGeneralSettings(pedb, core: ansys.edb.core.simulation_setup.hfss_pi_simulation_settings.HFSSPIGeneralSettings)

   PyEDB HFSS PI general settings class.


   .. py:attribute:: core


   .. py:property:: mesh_region_name
      :type: str


      Mesh region name.

      Returns
      -------
      str
          Mesh region name.



   .. py:property:: model_type
      :type: str


      Model type.

      Returns
      -------
      str
          Model type, possible values are "pcb", "rdl", and "package".



   .. py:property:: use_auto_mesh_region
      :type: bool


      Flag indicating if auto mesh regions are used.

      Returns
      -------
      bool
          True if auto mesh region is used, False otherwise.



   .. py:property:: use_mesh_region
      :type: bool


      Flag indicating if mesh region is used.

      Returns
      -------
      bool
          True if mesh region is used, False otherwise.



