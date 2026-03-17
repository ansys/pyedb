src.pyedb.siwave_core.icepak
============================

.. py:module:: src.pyedb.siwave_core.icepak


Classes
-------

.. autoapisummary::

   src.pyedb.siwave_core.icepak.Icepak


Module Contents
---------------

.. py:class:: Icepak(psiw)

   SIwave Icepak.


   .. py:method:: run(name: str, dc_simulation_name: str) -> bool

      Run Icepak analysis.

      Parameters
      ----------
      name : str,
          Name of the Icepak simulation.
      dc_simulation_name: str
          Name of the dc simulation.

      Returns
      -------




   .. py:method:: set_meshing_detail(mesh_level: int = 0) -> bool

      Sets the meshing detail level for Icepak simulations.

      Parameters
      ----------
      mesh_level : int, optional
          Meshing level.

      Returns
      -------




   .. py:method:: set_board_outline_fidelity(fidelity: int = 2) -> bool

      Specifies the minimum edge length when modifying the board outline for export to Icepak. This
      minimum edge length is used when indiscretion arcs into a series of straight lines and when
      simplifying the outline to remove very small edges.

      Parameters
      ----------
      fidelity : int, float, optional
          Fidelity level in mm.

      Returns
      -------




   .. py:method:: set_thermal_environment(convection: bool = True, force_air: bool = True, top_or_ambient_temperature: int | float = 22, top_or_overall_flow_direction: str = '+X', top_or_overall_flow_speed: int | float = 2, bottom_temperature: int | float = 22, bottom_flow_direction: str = '+X', bottom_flow_speed: int | float = 2, gravity_vector_x: int | float = 0, gravity_vector_y: int | float = 0, gravity_vector_z: int | float = 9.8) -> bool

      Sets the thermal environment settings to use for Icepak simulations.

      Parameters
      ----------
      convection : bool, optional
      force_air : bool, optional
      top_or_ambient_temperature: int, float, optional
          Temperature above PCB in degrees Celsius.
      top_or_overall_flow_direction : str, optional
          Flow direction above PCB.
      top_or_overall_flow_speed : int, float, optional
          Flow speed above PCB.
      bottom_temperature : int, float, optional
          Temperature below PCB in degrees Celsius.
      bottom_flow_direction : str, optional
          Flow direction below PCB.
      bottom_flow_speed : int, float, optional
          Flow speed below PCB.
      gravity_vector_x : int, float, optional
          Gravity vector x for natural convection.
      gravity_vector_y : int, float, optional
          Gravity vector y for natural convection.
      gravity_vector_z : int, float, optional
          Gravity vector z for natural convection.

      Returns
      -------




   .. py:method:: export_report(simulation_name: str, file_path: str | pathlib.Path) -> bool

      Export Icepak simulation report to a file.

      Parameters
      ----------
      simulation_name : str
          Name of the Icepak simulation.
      file_path : str, Path
          Path to the report file.

      Returns
      -------




