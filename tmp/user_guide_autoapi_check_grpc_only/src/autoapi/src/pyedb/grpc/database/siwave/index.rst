src.pyedb.grpc.database.siwave
==============================

.. py:module:: src.pyedb.grpc.database.siwave

.. autoapi-nested-parse::

   This module contains these classes: ``CircuitPort``, ``CurrentSource``, ``EdbSiwave``,
   ``PinGroup``, ``ResistorSource``, ``Source``, ``SourceType``, and ``VoltageSource``.



Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.siwave.Siwave


Module Contents
---------------

.. py:class:: Siwave(p_edb)

   Bases: :py:obj:`object`


   Manages EDB methods related to Siwave Setup accessible from `Edb.siwave` property.

   Parameters
   ----------
   edb_class : :class:`pyedb.edb.Edb`
       Inherited parent object.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_siwave = edbapp.siwave


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
      :type: Dict[str, Any]


      All sources in the layout.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> sources = edbapp.siwave.sources



   .. py:property:: probes
      :type: Dict[str, Any]


      All probes in the layout.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> probes = edbapp.siwave.probes



   .. py:property:: pin_groups
      :type: Dict[str, Any]


      All layout pin groups.

      Returns
      -------
      dict
          Dictionary of pin groups with names as keys and pin group objects as values.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> pin_groups = edbapp.siwave.pin_groups
      >>> for name, group in pin_groups.items():
      ...     print(f"Pin group {name} has {len(group.pins)} pins")



   .. py:method:: create_circuit_port_on_pin(pos_pin, neg_pin, impedance=50, port_name=None)

      Create a circuit port on a pin.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Edb Pin
      neg_pin : Object
          Edb Pin
      impedance : float, optional
          Port Impedance. Default is ``50``.
      port_name : str, optional
          Port Name

      Returns
      -------
      str
          Port Name.



   .. py:method:: create_port_between_pin_and_layer(component_name=None, pins_name=None, layer_name=None, reference_net=None, impedance=50.0)

      Create circuit port between pin and a reference layer.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_port_between_pin_and_layer` instead.

      Parameters
      ----------
      component_name : str
          Component name.
      pins_name : str
          Pin name or list of pin names.
      layer_name : str
          Layer name.
      reference_net : str
          Reference net name.
      impedance : float, optional
          Port impedance. Default is ``50.0`` ohms.

      Returns
      -------
      PadstackInstanceTerminal
          Created terminal.



   .. py:method:: create_voltage_source_on_pin(pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive Pin.
      neg_pin : Object
          Negative Pin.
      voltage_value : float, optional
          Value for the voltage. Default is ``3.3``.
      phase_value : optional
          Value for the phase. Default is ``0``.
      source_name : str, optional
          Name of the source. Default is ``""``.

      Returns
      -------
      str
          Source Name.



   .. py:method:: create_current_source_on_pin(pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name='')

      Create a current source.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_current_source_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive pin.
      neg_pin : Object
          Negative pin.
      current_value : float, optional
          Value for the current. Default is ``0.1``.
      phase_value : optional
          Value for the phase. Default is ``0``.
      source_name : str, optional
          Name of the source. Default is ``""``.

      Returns
      -------
      str
          Source Name.



   .. py:method:: create_resistor_on_pin(pos_pin, neg_pin, rvalue=1, resistor_name='')

      Create a resistor boundary between two given pins.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_resistor_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive Pin.
      neg_pin : Object
          Negative Pin.
      rvalue : float, optional
          Resistance value. Default is ``1``.
      resistor_name : str, optional
          Name of the resistor. Default is ``""``.

      Returns
      -------
      str
          Name of the resistor.



   .. py:method:: create_circuit_port_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, impedance_value=50, port_name='')

      Create a circuit port on a net.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_net` instead.

      Groups all pins belonging to the specified net and applies the port on PinGroups.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. Default is ``None``.
      negative_net_name : str, optional
          Name of the negative net name. Default is ``None`` (searches for GND nets).
      impedance_value : float, optional
          Port impedance value. Default is ``50``.
      port_name : str, optional
          Name of the port. Default is ``""``.

      Returns
      -------
      str
          The name of the port.



   .. py:method:: create_voltage_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source on a net.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_net` instead.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. Default is ``None``.
      negative_net_name : str, optional
          Name of the negative net name. Default is ``None`` (searches for GND nets).
      voltage_value : float, optional
          Value for the voltage. Default is ``3.3``.
      phase_value : optional
          Value for the phase. Default is ``0``.
      source_name : str, optional
          Name of the source. Default is ``""``.

      Returns
      -------
      str
          The name of the source.



   .. py:method:: create_current_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, current_value=0.1, phase_value=0, source_name='')

      Create a current source on a net.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_current_source_on_net` instead.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. Default is ``None``.
      negative_net_name : str, optional
          Name of the negative net name. Default is ``None`` (searches for GND nets).
      current_value : float, optional
          Value for the current. Default is ``0.1``.
      phase_value : optional
          Value for the phase. Default is ``0``.
      source_name : str, optional
          Name of the source. Default is ``""``.

      Returns
      -------
      str
          The name of the source.



   .. py:method:: create_dc_terminal(component_name, net_name, source_name='')

      Create a DC terminal.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_dc_terminal` instead.

      Parameters
      ----------
      component_name : str
          Name of the positive component.
      net_name : str
          Name of the positive net.
      source_name : str, optional
          Name of the source. Default is ``""``.

      Returns
      -------
      str
          The name of the source.



   .. py:method:: create_exec_file(add_dc: bool = False, add_ac: bool = False, add_syz: bool = False, export_touchstone: bool = False, touchstone_file_path: str = '') -> str

      Create an executable file.

      Parameters
      ----------
      add_dc : bool, optional
          Whether to add the DC option in the EXE file. Default is ``False``.
      add_ac : bool, optional
          Whether to add the AC option in the EXE file. Default is ``False``.
      add_syz : bool, optional
          Whether to add the SYZ option in the EXE file. Default is ``False``.
      export_touchstone : bool, optional
          Add the Touchstone file export option in the EXE file. Default is ``False``.
      touchstone_file_path : str, optional
          File path for the Touchstone file. Default is ``""``. When no path is
          specified and ``export_touchstone=True``, the project path is used.

      Returns
      -------
      str
          Path to the created exec file.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> # Create exec file with AC and SYZ options
      >>> success = edbapp.siwave.create_exec_file(add_ac=True, add_syz=True)
      >>> # Create exec file with Touchstone export
      >>> success = edbapp.siwave.create_exec_file(
      ...     add_ac=True, export_touchstone=True, touchstone_file_path="C:/temp/my_touchstone.s2p"
      ... )



   .. py:method:: add_cpa_analysis(name=None, siwave_cpa_setup_class=None)

      Add a SIwave CPA analysis to EDB.

      .. deprecated:: pyedb 0.77.3
          Use :func:`pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup.SiwaveCPASimulationSetup.create`
          instead.




   .. py:method:: add_siwave_syz_analysis(accuracy_level: int = 1, distribution: str = 'linear', start_freq: Union[str, float] = 1, stop_freq: Union[str, float] = 1000000000.0, step_freq: Union[str, float, int] = 1000000.0, discrete_sweep: bool = False) -> pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup

      Add a SIwave AC analysis to EDB.

      Parameters
      ----------
      accuracy_level : int, optional
         Level of accuracy of SI slider. Default is ``1``.
      distribution : str, optional
          Type of the sweep. Default is ``"linear"``. Options are:
          - ``"linear"``
          - ``"linear_count"``
          - ``"decade_count"``
          - ``"octave_count"``
          - ``"exponential"``
      start_freq : str, float, optional
          Starting frequency. Default is ``1``.
      stop_freq : str, float, optional
          Stopping frequency. Default is ``1e9``.
      step_freq : str, float, int, optional
          Frequency step. Default is ``1e6``. Used for ``"decade_count"``, ``"linear_count"``, ``"octave_count"``
          distribution. Must be integer in that case.
      discrete_sweep : bool, optional
          Whether the sweep is discrete. Default is ``False``.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`
          Setup object class.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
      >>> # Add SYZ analysis with linear sweep from 1kHz to 10GHz
      >>> setup = edbapp.siwave.add_siwave_syz_analysis(start_freq=1e3, stop_freq=10e9, distribution="linear")
      >>> # Add SYZ analysis with decade sweep
      >>> setup = edbapp.siwave.add_siwave_syz_analysis(
      ...     start_freq=1e3,
      ...     stop_freq=10e9,
      ...     distribution="decade_count",
      ...     step_freq=10,  # 10 points per decade
      ... )



   .. py:method:: add_siwave_dc_analysis(name: Optional[str] = None) -> Any

      Add a Siwave DC analysis in EDB.

      .. note::
         Source Reference to Ground settings works only from 2021.2

      Parameters
      ----------
      name : str, optional
          Setup name.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveDCSimulationSetup`
          Setup object class.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("pathtoaedb", edbversion="2021.2")
      >>> edb.siwave.add_siwave_ac_analysis()
      >>> edb.siwave.add_siwave_dc_analysis2("my_setup")



   .. py:method:: create_pin_group_terminal(source)

      Create a pin group terminal.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_pin_group_terminal` instead.

      Parameters
      ----------
      source : VoltageSource, CircuitPort, CurrentSource, DCTerminal or ResistorSource
          Name of the source.




   .. py:method:: create_rlc_component(pins, component_name='', r_value=1.0, c_value=1e-09, l_value=1e-09, is_parallel=False)

      Create physical RLC component.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.components.create_rlc_component` instead.

      Parameters
      ----------
      pins : list[Edb.Cell.Primitive.PadstackInstance]
           List of EDB pins.
      component_name : str
          Component name.
      r_value : float
          Resistor value.
      c_value : float
          Capacitance value.
      l_value : float
          Inductor value.
      is_parallel : bool
          Use parallel model when ``True``, series when ``False``.

      Returns
      -------
      :class:`pyedb.dotnet.database.components.Components`
          Created EDB component.



   .. py:method:: create_pin_group(reference_designator, pin_numbers, group_name=None)

      Create pin group on the component.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.components.create_pin_group` instead.

      Parameters
      ----------
      reference_designator : str
          References designator of the component.
      pin_numbers : int, str, list
          List of pin names.
      group_name : str, optional
          Name of the pin group.

      Returns
      -------
      PinGroup
          Pin group object.



   .. py:method:: create_pin_group_on_net(reference_designator, net_name, group_name=None)

      Create pin group on component by net name.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.components.create_pin_group_on_net` instead.

      Parameters
      ----------
      reference_designator : str
          References designator of the component.
      net_name : str
          Name of the net.
      group_name : str, optional
          Name of the pin group.

      Returns
      -------
      PinGroup
          Pin group object.



   .. py:method:: create_current_source_on_pin_group(pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None)

      Create current source between two pin groups.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_current_source_on_pin_group` instead.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      magnitude : int, float, optional
          Magnitude of the source. Default is ``1``.
      phase : int, float, optional
          Phase of the source. Default is ``0``.
      name : str, optional
          Source name.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` otherwise.



   .. py:method:: create_voltage_source_on_pin_group(pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None, impedance=0.001)

      Create voltage source between two pin groups.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_pin_group` instead.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      magnitude : int, float, optional
          Magnitude of the source. Default is ``1``.
      phase : int, float, optional
          Phase of the source. Default is ``0``.
      name : str, optional
          Source name.
      impedance : float, optional
          Source impedance. Default is ``0.001``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` otherwise.



   .. py:method:: create_voltage_probe_on_pin_group(probe_name, pos_pin_group_name, neg_pin_group_name, impedance=1000000.0)

      Create voltage probe between two pin groups.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_voltage_probe_on_pin_group` instead.

      Parameters
      ----------
      probe_name : str
          Name of the probe.
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      impedance : int, float, optional
          Probe impedance. Default is ``1e6``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` otherwise.



   .. py:method:: create_circuit_port_on_pin_group(pos_pin_group_name, neg_pin_group_name, impedance=50, name=None)

      Create a port between two pin groups.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_pin_group` instead.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      impedance : int, float, optional
          Impedance of the port. Default is ``50``.
      name : str, optional
          Port name.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` otherwise.



   .. py:method:: place_voltage_probe(name, positive_net_name, positive_location, positive_layer, negative_net_name, negative_location, negative_layer)

      Place a voltage probe between two points.

      .. deprecated:: pyedb 0.28.0
          Use :func:`pyedb.grpc.core.excitations.place_voltage_probe` instead.

      Parameters
      ----------
      name : str
          Name of the probe.
      positive_net_name : str
          Name of the positive net.
      positive_location : list
          Location of the positive terminal.
      positive_layer : str
          Layer of the positive terminal.
      negative_net_name : str
          Name of the negative net.
      negative_location : list
          Location of the negative terminal.
      negative_layer : str
          Layer of the negative terminal.



   .. py:method:: create_impedance_crosstalk_scan(scan_type: str = 'impedance') -> pyedb.misc.siw_feature_config.xtalk_scan.scan_config.SiwaveScanConfig

      Create Siwave crosstalk scan object.

      Parameters
      ----------
      scan_type : str, optional
          Scan type to be analyzed. Options are:
          - ``"impedance"`` for frequency impedance scan
          - ``"frequency_xtalk"`` for frequency domain crosstalk
          - ``"time_xtalk"`` for time domain crosstalk
          Default is ``"impedance"``.

      Returns
      -------
      SiwaveScanConfig
          Scan configuration object.



   .. py:property:: icepak_use_minimal_comp_defaults
      :type: bool


      Icepak default setting.

      If ``True``, only resistors are active in Icepak simulation and power dissipation
      is calculated from DC results.



   .. py:property:: icepak_component_file
      :type: str


      Icepak component file path.



