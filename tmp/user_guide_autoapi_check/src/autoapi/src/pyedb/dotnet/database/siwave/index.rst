src.pyedb.dotnet.database.siwave
================================

.. py:module:: src.pyedb.dotnet.database.siwave

.. autoapi-nested-parse::

   This module contains these classes: ``CircuitPort``, ``CurrentSource``, ``EdbSiwave``,
   ``PinGroup``, ``ResistorSource``, ``Source``, ``SourceType``, and ``VoltageSource``.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.siwave.EdbSiwave


Module Contents
---------------

.. py:class:: EdbSiwave(p_edb)

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
      :type: Dict[str, Union[pyedb.dotnet.database.edb_data.ports.BundleWavePort, pyedb.dotnet.database.edb_data.ports.GapPort, pyedb.dotnet.database.edb_data.ports.CircuitPort, pyedb.dotnet.database.edb_data.ports.CoaxPort, pyedb.dotnet.database.edb_data.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CircuitPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CoaxPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.BundleWavePort`]]




   .. py:property:: ports
      :type: Dict[str, Union[pyedb.dotnet.database.edb_data.ports.BundleWavePort, pyedb.dotnet.database.edb_data.ports.GapPort, pyedb.dotnet.database.edb_data.ports.CircuitPort, pyedb.dotnet.database.edb_data.ports.CoaxPort, pyedb.dotnet.database.edb_data.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CircuitPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CoaxPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.BundleWavePort`]]




   .. py:property:: sources
      :type: Dict[str, pyedb.dotnet.database.edb_data.ports.ExcitationSources]


      Get all sources.



   .. py:property:: probes
      :type: Dict[str, Union[pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal, pyedb.dotnet.database.cell.terminal.bundle_terminal.BundleTerminal, pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal, pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal]]


      Get all probes.



   .. py:property:: voltage_regulator_modules

      Get all voltage regulator modules



   .. py:property:: pin_groups

      All Layout Pin groups.

      Returns
      -------
      list
          List of all layout pin groups.



   .. py:method:: create_circuit_port_on_pin(pos_pin, neg_pin, impedance=50, port_name=None)

      Create a circuit port on a pin.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_circuit_port_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Edb Pin
      neg_pin : Object
          Edb Pin
      impedance : float
          Port Impedance
      port_name : str, optional
          Port Name

      Returns
      -------
      str
          Port Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")



   .. py:method:: create_port_between_pin_and_layer(component_name=None, pins_name=None, layer_name=None, reference_net=None, impedance=50.0)

      Create circuit port between pin and a reference layer.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_port_between_pin_and_layer` instead.

      Parameters
      ----------
      component_name : str
          Component name. The default is ``None``.
      pins_name : str
          Pin name or list of pin names. The default is ``None``.
      layer_name : str
          Layer name. The default is ``None``.
      reference_net : str
          Reference net name. The default is ``None``.
      impedance : float, optional
          Port impedance. The default is ``50.0`` in ohms.

      Returns
      -------
      PadstackInstanceTerminal
          Created terminal.




   .. py:method:: create_voltage_source_on_pin(pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_voltage_source_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive Pin.
      neg_pin : Object
          Negative Pin.
      voltage_value : float, optional
          Value for the voltage. The default is ``3.3``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          Source Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_voltage_source_on_pin(pins[0], pins[1], 50, "source_name")



   .. py:method:: create_current_source_on_pin(pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name='')

      Create a current source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_current_source_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive pin.
      neg_pin : Object
          Negative pin.
      current_value : float, optional
          Value for the current. The default is ``0.1``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          Source Name.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_current_source_on_pin(pins[0], pins[1], 50, "source_name")



   .. py:method:: create_resistor_on_pin(pos_pin, neg_pin, rvalue=1, resistor_name='')

      Create a Resistor boundary between two given pins..

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_resistor_on_pin` instead.

      Parameters
      ----------
      pos_pin : Object
          Positive Pin.
      neg_pin : Object
          Negative Pin.
      rvalue : float, optional
          Resistance value. The default is ``1``.
      resistor_name : str, optional
          Name of the resistor. The default is ``""``.

      Returns
      -------
      str
          Name of the resistor.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> pins = edbapp.components.get_pin_from_component("U2A5")
      >>> edbapp.excitation_manager.create_resistor_on_pin(pins[0], pins[1], 50, "res_name")



   .. py:method:: create_circuit_port_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, impedance_value=50, port_name='')

      Create a circuit port on a NET.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_circuit_port_on_net` instead.

      It groups all pins belonging to the specified net and then applies the port on PinGroups.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. The default is ``None``, in which case the name of
          the positive net is assigned.
      negative_net_name : str, optional
          Name of the negative net name. The default is ``None`` which will look for GND Nets.
      impedance_value : float, optional
          Port impedance value. The default is ``50``.
      port_name : str, optional
          Name of the port. The default is ``""``.

      Returns
      -------
      str
          The name of the port.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edbapp.excitation_manager.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")



   .. py:method:: create_voltage_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, voltage_value=3.3, phase_value=0, source_name='')

      Create a voltage source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_voltage_source_on_net` instead.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. The default is ``None``, in which case the name of
          the positive net is assigned.
      negative_net_name : str, optional
          Name of the negative net name. The default is ``None`` which will look for GND Nets.
      voltage_value : float, optional
          Value for the voltage. The default is ``3.3``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          The name of the source.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edb.excitation_manager.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")



   .. py:method:: create_current_source_on_net(positive_component_name, positive_net_name, negative_component_name=None, negative_net_name=None, current_value=0.1, phase_value=0, source_name='')

      Create a current source.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_current_source_on_net` instead.

      Parameters
      ----------
      positive_component_name : str
          Name of the positive component.
      positive_net_name : str
          Name of the positive net.
      negative_component_name : str, optional
          Name of the negative component. The default is ``None``, in which case the name of
          the positive net is assigned.
      negative_net_name : str, optional
          Name of the negative net name. The default is ``None`` which will look for GND Nets.
      current_value : float, optional
          Value for the current. The default is ``0.1``.
      phase_value : optional
          Value for the phase. The default is ``0``.
      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          The name of the source.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edb.excitation_manager.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")



   .. py:method:: create_dc_terminal(component_name, net_name, source_name='')

      Create a dc terminal.

      Parameters
      ----------
      component_name : str
          Name of the positive component.
      net_name : str
          Name of the positive net.

      source_name : str, optional
          Name of the source. The default is ``""``.

      Returns
      -------
      str
          The name of the source.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edbapp = Edb("myaedbfolder", "project name", "release version")
      >>> edb.siwave.create_dc_terminal("U2A5", "V1P5_S3", "source_name")



   .. py:method:: create_exec_file(add_dc=False, add_ac=False, add_syz=False, export_touchstone=False, touchstone_file_path='')

      Create an executable file.

      Parameters
      ----------
      add_dc : bool, optional
          Whether to add the DC option in the EXE file. The default is ``False``.
      add_ac : bool, optional
          Whether to add the AC option in the EXE file. The default is
          ``False``.
      add_syz : bool, optional
          Whether to add the SYZ option in the EXE file
      export_touchstone : bool, optional
          Add the Touchstone file export option in the EXE file.
          The default is ``False``.
      touchstone_file_path : str, optional
          File path for the Touchstone file. The default is ``""``.  When no path is
          specified and ``export_touchstone=True``, the path for the project is
          used.



   .. py:method:: add_siwave_syz_analysis(name=None, accuracy_level=1, decade_count=10, sweeptype=1, start_freq=1, stop_freq=1000000000.0, step_freq=1000000.0, discrete_sweep=False)

      Add a SIwave AC analysis to EDB.

      Parameters
      ----------
      name : str optional
          Setup name.
      accuracy_level : int, optional
         Level of accuracy of SI slider. The default is ``1``.
      decade_count : int
          The default is ``10``. The value for this parameter is used for these sweep types:
          linear count and decade count.
          This parameter is alternative to ``step_freq``, which is used for a linear scale sweep.
      sweeptype : int, optional
          Type of the sweep. The default is ``1``. Options are:

          - ``0``: linear count
          - ``1``: linear scale
          - ``2``: loc scale
      start_freq : float, optional
          Starting frequency. The default is ``1``.
      stop_freq : float, optional
          Stopping frequency. The default is ``1e9``.
      step_freq : float, optional
          Frequency size of the step. The default is ``1e6``.
      discrete_sweep : bool, optional
          Whether the sweep is discrete. The default is ``False``.

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`
          Setup object class.



   .. py:method:: add_siwave_dc_analysis(name=None)

      Add a Siwave DC analysis in EDB.

      If a setup is present, it is deleted and replaced with
      actual settings.

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

      Parameters
      ----------
      source : VoltageSource, CircuitPort, CurrentSource, DCTerminal or ResistorSource
          Name of the source.




   .. py:method:: create_rlc_component(pins, component_name='', r_value=1.0, c_value=1e-09, l_value=1e-09, is_parallel=False)

      Create physical Rlc component.

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
          Using parallel model when ``True``, series when ``False``.

      Returns
      -------
      class:`pyedb.dotnet.database.components.Components`
          Created EDB component.




   .. py:method:: create_pin_group(reference_designator, pin_numbers, group_name=None)

      Create pin group on the component.

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



   .. py:method:: create_pin_group_on_net(reference_designator, net_name, group_name=None)

      Create pin group on component by net name.

      Parameters
      ----------
      reference_designator : str
          References designator of the component.
      net_name : str
          Name of the net.
      group_name : str, optional
          Name of the pin group. The default value is ``None``.

      Returns
      -------
      PinGroup



   .. py:method:: create_current_source_on_pin_group(pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None)

      Create current source between two pin groups.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_current_source_on_pin_group` instead.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      magnitude : int, float, optional
          Magnitude of the source.
      phase : int, float, optional
          Phase of the source

      Returns
      -------
      bool




   .. py:method:: create_voltage_source_on_pin_group(pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None, impedance=0.001)

      Create voltage source between two pin groups.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_voltage_source_on_pin_group` instead.

      Parameters
      ----------
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      magnitude : int, float, optional
          Magnitude of the source.
      phase : int, float, optional
          Phase of the source

      Returns
      -------
      bool




   .. py:method:: create_voltage_probe_on_pin_group(probe_name, pos_pin_group_name, neg_pin_group_name, impedance=1000000)

      Create voltage probe between two pin groups.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_voltage_probe_on_pin_group` instead.

      Parameters
      ----------
      probe_name : str
          Name of the probe.
      pos_pin_group_name : str
          Name of the positive pin group.
      neg_pin_group_name : str
          Name of the negative pin group.
      impedance : int, float, optional
          Phase of the source.

      Returns
      -------
      bool




   .. py:method:: create_circuit_port_on_pin_group(pos_pin_group_name, neg_pin_group_name, impedance=50, name=None)

      Create a port between two pin groups.

      .. deprecated:: 0.70.0
          Use :func:`pyedb.grpc.core.excitation_manager.create_circuit_port_on_pin_group` instead.

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




   .. py:method:: place_voltage_probe(name, positive_net_name, positive_location, positive_layer, negative_net_name, negative_location, negative_layer)

      Place a voltage probe between two points.

      Parameters
      ----------
      name : str,
          Name of the probe.
      positive_net_name : str
          Name of the positive net.
      positive_location : list
          Location of the positive terminal.
      positive_layer : str,
          Layer of the positive terminal.
      negative_net_name : str,
          Name of the negative net.
      negative_location : list
          Location of the negative terminal.
      negative_layer : str
          Layer of the negative terminal.



   .. py:method:: create_vrm_module(name=None, is_active=True, voltage='3V', positive_sensor_pin=None, negative_sensor_pin=None, load_regulation_current='1A', load_regulation_percent=0.1)

      Create a voltage regulator module.

      Parameters
      ----------
      name : str
          Name of the voltage regulator.
      is_active : bool optional
          Set the voltage regulator active or not. Default value is ``True``.
      voltage ; str, float
          Set the voltage value.
      positive_sensor_pin : int, .class pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance
          defining the positive sensor pin.
      negative_sensor_pin : int, .class pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance
          defining the negative sensor pin.
      load_regulation_current : str or float
          definition the load regulation current value.
      load_regulation_percent : float
          definition the load regulation percent value.



   .. py:property:: icepak_use_minimal_comp_defaults

      Icepak default setting. If "True", only resistor are active in Icepak simulation.
      The power dissipation of the resistors are calculated from DC results.



   .. py:method:: create_impedance_crosstalk_scan(scan_type='impedance')

      Create Siwave crosstalk scan object

      Parameters
      ----------
      scan_type : str
          Scan type to be analyzed. 3 options are available, ``impedance`` for frequency impedance scan,
          ``frequency_xtalk`` for frequency domain crosstalk and ``time_xtalk`` for time domain crosstalk.
          Default value is ``frequency``.




   .. py:method:: add_cpa_analysis(name=None, siwave_cpa_setup_class=None)


   .. py:property:: icepak_component_file

      Icepak component file path.



