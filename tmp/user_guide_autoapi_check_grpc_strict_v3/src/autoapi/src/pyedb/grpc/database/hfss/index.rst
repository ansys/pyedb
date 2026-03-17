src.pyedb.grpc.database.hfss
============================

.. py:module:: src.pyedb.grpc.database.hfss

.. autoapi-nested-parse::

   This module contains the ``EdbHfss`` class.



Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.hfss.Hfss


Module Contents
---------------

.. py:class:: Hfss(p_edb)

   Manages EDB methods for HFSS setup configuration.

   Provides access to HFSS-specific operations including:
   - Excitation and port creation
   - Source and probe management
   - Simulation setup configuration
   - Boundary condition creation
   - Layout manipulation for simulation

   Accessed via `Edb.hfss` property.


   .. py:property:: hfss_extent_info
      :type: pyedb.grpc.database.utility.hfss_extent_info.HfssExtentInfo


      HFSS extent information.

      Returns
      -------
      HfssExtentInfo
          Object containing HFSS extent configuration data.



   .. py:property:: excitations
      :type: Dict[str, Union[pyedb.grpc.database.ports.ports.BundleWavePort, pyedb.grpc.database.ports.ports.GapPort, pyedb.grpc.database.ports.ports.CircuitPort, pyedb.grpc.database.ports.ports.CoaxPort, pyedb.grpc.database.ports.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.grpc.database.ports.ports.ports.GapPort`,
                 :class:`pyedb.grpc.database.ports.ports.ports.WavePort`,
                 :class:`pyedb.grpc.database.ports.ports.CircuitPort`,
                 :class:`pyedb.grpc.database.ports.ports.CoaxPort`,
                 :class:`pyedb.grpc.database.ports.ports.BundleWavePort`]]




   .. py:property:: ports
      :type: Dict[str, Union[pyedb.grpc.database.ports.ports.BundleWavePort, pyedb.grpc.database.ports.ports.GapPort, pyedb.grpc.database.ports.ports.CircuitPort, pyedb.grpc.database.ports.ports.CoaxPort, pyedb.grpc.database.ports.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.grpc.database.ports.ports.ports.GapPort`,
                 :class:`pyedb.grpc.database.ports.ports.ports.WavePort`,
                 :class:`pyedb.grpc.database.ports.ports.CircuitPort`,
                 :class:`pyedb.grpc.database.ports.ports.CoaxPort`,
                 :class:`pyedb.grpc.database.ports.ports.BundleWavePort`]]




   .. py:property:: sources

      All source definitions in the layout.

      Returns
      -------
      list
          List of source objects.



   .. py:property:: probes

      All probe definitions in the layout.

      Returns
      -------
      list
          List of probe objects.



   .. py:method:: get_trace_width_for_traces_with_ports()

      Retrieve trace widths for traces with ports.

      Returns
      -------
      dict
          Dictionary mapping net names to smallest trace widths.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_aedb")
      >>> widths = edb.hfss.get_trace_width_for_traces_with_ports()
      >>> for net_name, width in widths.items():
      ...     print(f"Net '{net_name}': Smallest width = {width}")



   .. py:method:: create_edge_port(location, primitive_name, name, impedance=50, is_wave_port=True, horizontal_extent_factor=1, vertical_extent_factor=1, pec_launch_width=0.0001)


   .. py:method:: get_layout_bounding_box(layout=None, digit_resolution=6)

      Calculate layout bounding box.

      Parameters
      ----------
      layout : Edb.Cell.Layout, optional
          Layout object (uses active layout if None).
      digit_resolution : int, optional
          Coordinate rounding precision.

      Returns
      -------
      list
          [min_x, min_y, max_x, max_y] coordinates.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("my_aedb")
      >>> bbox = edb.hfss.get_layout_bounding_box()
      >>> print(f"Layout Bounding Box: {bbox}")
      >>> custom_layout = edb.active_layout
      >>> bbox = edb.hfss.get_layout_bounding_box(custom_layout, 5)



   .. py:method:: add_setup(name=None, distribution='linear', start_freq=None, stop_freq=None, step_freq=None, discrete_sweep=False) -> Optional[pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup]

      .. deprecated pyedb 0.67.0

      Add HFSS analysis setup (deprecated).
      use :func:`create_simulation_setup` instead.




   .. py:method:: generate_auto_hfss_regions()

      Generate auto HFSS regions.

      This method automatically identifies areas for use as HFSS regions in SIwave simulations.



