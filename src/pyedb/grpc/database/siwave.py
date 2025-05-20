# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module contains these classes: ``CircuitPort``, ``CurrentSource``, ``EdbSiwave``,
``PinGroup``, ``ResistorSource``, ``Source``, ``SourceType``, and ``VoltageSource``.
"""
import os
import warnings

from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.simulation_setup.simulation_setup import (
    Distribution as GrpcDistribution,
)
from ansys.edb.core.simulation_setup.simulation_setup import (
    FrequencyData as GrpcFrequencyData,
)
from ansys.edb.core.simulation_setup.simulation_setup import SweepData as GrpcSweepData

from pyedb.misc.siw_feature_config.xtalk_scan.scan_config import SiwaveScanConfig


class Siwave(object):
    """Manages EDB methods related to Siwave Setup accessible from `Edb.siwave` property.

    Parameters
    ----------
    edb_class : :class:`pyedb.edb.Edb`
        Inherited parent object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_siwave = edbapp.siwave
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def _edb(self):
        """EDB."""
        return self._pedb

    @property
    def _logger(self):
        """EDB."""
        return self._pedb.logger

    @property
    def _active_layout(self):
        """Active layout."""
        return self._pedb.active_layout

    @property
    def _layout(self):
        """Active layout."""
        return self._pedb.layout

    @property
    def _cell(self):
        """Cell."""
        return self._pedb.active_cell

    @property
    def _db(self):
        """ """
        return self._pedb.active_db

    @property
    def excitations(self):
        """Get all excitations."""
        return self._pedb.excitations

    @property
    def sources(self):
        """Get all sources."""
        return self._pedb.sources

    @property
    def probes(self):
        """Get all probes."""
        return self._pedb.probes

    @property
    def pin_groups(self):
        """All Layout Pin groups.

        Returns
        -------
        list
            List of all layout pin groups.
        """
        _pingroups = {}
        for el in self._pedb.layout.pin_groups:
            _pingroups[el.name] = el
        return _pingroups

    def _create_terminal_on_pins(self, source):
        """Create a terminal on pins.
        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations._create_terminal_on_pins` instead.

        Parameters
        ----------
        source : VoltageSource, CircuitPort, CurrentSource or ResistorSource
            Name of the source.

        """
        warnings.warn(
            "`_create_terminal_on_pins` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations._create_terminal_on_pins` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation._create_terminal_on_pins(source)

    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create a circuit port on a pin.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_pin` instead.

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
        """
        warnings.warn(
            "`create_circuit_port_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_circuit_port_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_circuit_port_on_pin(pos_pin, neg_pin, impedance, port_name)

    def create_port_between_pin_and_layer(
        self, component_name=None, pins_name=None, layer_name=None, reference_net=None, impedance=50.0
    ):
        """Create circuit port between pin and a reference layer.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_port_between_pin_and_layer` instead.

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
        """
        warnings.warn(
            "`create_port_between_pin_and_layer` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_port_between_pin_and_layer` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_port_between_pin_and_layer(
            component_name, pins_name, layer_name, reference_net, impedance
        )

    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """Create a voltage source.
        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_pin` instead.

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
        """

        warnings.warn(
            "`create_voltage_source_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_voltage_source_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_voltage_source_on_pin(
            pos_pin, neg_pin, voltage_value, phase_value, source_name
        )

    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_current_source_on_pin` instead.

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
        """
        warnings.warn(
            "`create_current_source_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_current_source_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_current_source_on_pin(
            pos_pin, neg_pin, current_value, phase_value, source_name
        )

    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a Resistor boundary between two given pins.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_resistor_on_pin` instead.

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
        """
        warnings.warn(
            "`create_resistor_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_resistor_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_resistor_on_pin(pos_pin, neg_pin, rvalue, resistor_name)

    def _check_gnd(self, component_name):
        """
        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations._check_gnd` instead.

        """
        warnings.warn(
            "`_check_gnd` is deprecated and is now located here " "`pyedb.grpc.core.excitations._check_gnd` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation._check_gnd(component_name)

    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        impedance_value=50,
        port_name="",
    ):
        """Create a circuit port on a NET.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_circuit_port_on_net` instead.

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

        """
        warnings.warn(
            "`create_circuit_port_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.source_excitation.create_circuit_port_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_circuit_port_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            impedance_value,
            port_name,
        )

    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        voltage_value=3.3,
        phase_value=0,
        source_name="",
    ):
        """Create a voltage source.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_voltage_source_on_net` instead.

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

        """
        warnings.warn(
            "`create_voltage_source_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_voltage_source_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_voltage_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            voltage_value,
            phase_value,
            source_name,
        )

    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        current_value=0.1,
        phase_value=0,
        source_name="",
    ):
        """Create a current source.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_current_source_on_net` instead.

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
        """
        warnings.warn(
            "`create_current_source_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_current_source_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_current_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            current_value,
            phase_value,
            source_name,
        )

    def create_dc_terminal(
        self,
        component_name,
        net_name,
        source_name="",
    ):
        """Create a dc terminal.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_dc_terminal` instead.

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
        """
        warnings.warn(
            "`create_dc_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_dc_terminal` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_dc_terminal(component_name, net_name, source_name)

    def create_exec_file(
        self, add_dc=False, add_ac=False, add_syz=False, export_touchstone=False, touchstone_file_path=""
    ):
        """Create an executable file.

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
        """
        workdir = os.path.dirname(self._pedb.edbpath)
        file_name = os.path.join(workdir, os.path.splitext(os.path.basename(self._pedb.edbpath))[0] + ".exec")
        if os.path.isfile(file_name):
            os.remove(file_name)
        with open(file_name, "w") as f:
            if add_ac:
                f.write("ExecAcSim\n")
            if add_dc:
                f.write("ExecDcSim\n")
            if add_syz:
                f.write("ExecSyzSim\n")
            if export_touchstone:
                if touchstone_file_path:  # pragma no cover
                    f.write('ExportTouchstone "{}"\n'.format(touchstone_file_path))
                else:  # pragma no cover
                    touchstone_file_path = os.path.join(
                        workdir, os.path.splitext(os.path.basename(self._pedb.edbpath))[0] + "_touchstone"
                    )
                    f.write('ExportTouchstone "{}"\n'.format(touchstone_file_path))
            f.write("SaveSiw\n")

        return True if os.path.exists(file_name) else False

    def add_siwave_syz_analysis(
        self,
        accuracy_level=1,
        distribution="linear",
        start_freq=1,
        stop_freq=1e9,
        step_freq=1e6,
        discrete_sweep=False,
    ):
        """Add a SIwave AC analysis to EDB.

        Parameters
        ----------
        accuracy_level : int, optional
           Level of accuracy of SI slider. The default is ``1``.
        distribution : str, optional
            Type of the sweep. The default is `"linear"`. Options are:
            - `"linear"`
            - `"linear_count"`
            - `"decade_count"`
            - `"octave_count"`
            - `"exponential"`
        start_freq : str, float, optional
            Starting frequency. The default is ``1``.
        stop_freq : str, float, optional
            Stopping frequency. The default is ``1e9``.
        step_freq : str, float, int, optional
            Frequency step. The default is ``1e6``. or used for `"decade_count"`, "linear_count"`, "octave_count"`
            distribution. Must be integer in that case.
        discrete_sweep : bool, optional
            Whether the sweep is discrete. The default is ``False``.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`
            Setup object class.
        """
        setup = self._pedb.create_siwave_syz_setup()
        start_freq = self._pedb.number_with_units(start_freq, "Hz")
        stop_freq = self._pedb.number_with_units(stop_freq, "Hz")
        setup.settings.general.si_slider_pos = accuracy_level
        if distribution.lower() == "linear":
            distribution = "LIN"
        elif distribution.lower() == "linear_count":
            distribution = "LINC"
        elif distribution.lower() == "exponential":
            distribution = "ESTP"
        elif distribution.lower() == "decade_count":
            distribution = "DEC"
        elif distribution.lower() == "octave_count":
            distribution = "OCT"
        else:
            distribution = "LIN"
        sweep_name = f"sweep_{len(setup.sweep_data) + 1}"
        sweep_data = [
            GrpcSweepData(
                name=sweep_name,
                frequency_data=GrpcFrequencyData(
                    distribution=GrpcDistribution[distribution], start_f=start_freq, end_f=stop_freq, step=step_freq
                ),
            )
        ]
        if discrete_sweep:
            sweep_data[0].type = sweep_data[0].type.DISCRETE_SWEEP
        for sweep in setup.sweep_data:
            sweep_data.append(sweep)
        setup.sweep_data = sweep_data
        self.create_exec_file(add_ac=True)
        return setup

    def add_siwave_dc_analysis(self, name=None):
        """Add a Siwave DC analysis in EDB.

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

        """
        setup = self._pedb.create_siwave_dc_setup(name)
        self.create_exec_file(add_dc=True)
        return setup

    def create_pin_group_terminal(self, source):
        """Create a pin group terminal.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_pin_group_terminal` instead.

        Parameters
        ----------
        source : VoltageSource, CircuitPort, CurrentSource, DCTerminal or ResistorSource
            Name of the source.

        """
        warnings.warn(
            "`create_pin_group_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_pin_group_terminal` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_pin_group_terminal(source)

    def create_rlc_component(
        self,
        pins,
        component_name="",
        r_value=1.0,
        c_value=1e-9,
        l_value=1e-9,
        is_parallel=False,
    ):
        """Create physical Rlc component.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.components.create_pin_group_terminal` instead.

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

        """
        warnings.warn(
            "`create_rlc_component` is deprecated and is now located here "
            "`pyedb.grpc.core.components.create_rlc_component` instead.",
            DeprecationWarning,
        )
        return self._pedb.components.create(
            pins,
            component_name=component_name,
            is_rlc=True,
            r_value=r_value,
            c_value=c_value,
            l_value=l_value,
            is_parallel=is_parallel,
        )  # pragma no cover

    def create_pin_group(self, reference_designator, pin_numbers, group_name=None):
        """Create pin group on the component.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.components.create_pin_group_terminal` instead.

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
        """
        warnings.warn(
            "`create_pin_group` is deprecated and is now located here "
            "`pyedb.grpc.core.components.create_pin_group` instead.",
            DeprecationWarning,
        )
        return self._pedb.components.create_pin_group(reference_designator, pin_numbers, group_name)

    def create_pin_group_on_net(self, reference_designator, net_name, group_name=None):
        """Create pin group on component by net name.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.components.create_pin_group_terminal` instead.

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
        """
        warnings.warn(
            "`create_pin_group_on_net` is deprecated and is now located here "
            "`pyedb.grpc.core.components.create_pin_group_on_net` instead.",
            DeprecationWarning,
        )
        return self._pedb.components.create_pin_group_on_net(reference_designator, net_name, group_name)

    def create_current_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None
    ):
        """Create current source between two pin groups.

        .deprecated:: pyedb 0.28.0
        Use: func:`pyedb.grpc.core.excitations.create_current_source_on_pin_group`
        instead.

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
        name : str, optional
            source name.

        Returns
        -------
        bool

        """
        warnings.warn(
            "`create_current_source_on_pin_group` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_current_source_on_pin_group` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_current_source_on_pin_group(
            pos_pin_group_name, neg_pin_group_name, magnitude, phase, name
        )

    def create_voltage_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None, impedance=0.001
    ):
        """Create voltage source between two pin groups.

        .deprecated:: pyedb 0.28.0
        Use: func:`pyedb.grpc.core.excitations.create_voltage_source_on_pin_group`
        instead.

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

        """
        warnings.warn(
            "`create_voltage_source_on_pin_group` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_voltage_source_on_pin_group` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_voltage_source_on_pin_group(
            pos_pin_group_name, neg_pin_group_name, magnitude, phase, name, impedance
        )

    def create_voltage_probe_on_pin_group(self, probe_name, pos_pin_group_name, neg_pin_group_name, impedance=1e6):
        """Create voltage probe between two pin groups.

        .deprecated:: pyedb 0.28.0
        Use: func:`pyedb.grpc.core.excitations.create_voltage_probe_on_pin_group`
        instead.

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

        """

        warnings.warn(
            "`create_voltage_probe_on_pin_group` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_voltage_probe_on_pin_group` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_voltage_probe_on_pin_group(
            probe_name, pos_pin_group_name, neg_pin_group_name, impedance=impedance
        )

    def create_circuit_port_on_pin_group(self, pos_pin_group_name, neg_pin_group_name, impedance=50, name=None):
        """Create a port between two pin groups.

        .deprecated:: pyedb 0.28.0
        Use: func:`pyedb.grpc.core.excitations.create_circuit_port_on_pin_group`
        instead.

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

        """
        warnings.warn(
            "`create_circuit_port_on_pin_group` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_circuit_port_on_pin_group` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_circuit_port_on_pin_group(
            pos_pin_group_name, neg_pin_group_name, impedance, name
        )

    def place_voltage_probe(
        self,
        name,
        positive_net_name,
        positive_location,
        positive_layer,
        negative_net_name,
        negative_location,
        negative_layer,
    ):
        """Place a voltage probe between two points.

        .deprecated:: pyedb 0.28.0
        Use: func:`pyedb.grpc.core.excitations.place_voltage_probe`
        instead.

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
        """
        warnings.warn(
            "`place_voltage_probe` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.place_voltage_probe` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.place_voltage_probe(
            name,
            positive_net_name,
            positive_location,
            positive_layer,
            negative_net_name,
            negative_location,
            negative_layer,
        )

    # def create_vrm_module(
    #     self,
    #     name=None,
    #     is_active=True,
    #     voltage="3V",
    #     positive_sensor_pin=None,
    #     negative_sensor_pin=None,
    #     load_regulation_current="1A",
    #     load_regulation_percent=0.1,
    # ):
    #     """Create a voltage regulator module.
    #
    #     Parameters
    #     ----------
    #     name : str
    #         Name of the voltage regulator.
    #     is_active : bool optional
    #         Set the voltage regulator active or not. Default value is ``True``.
    #     voltage ; str, float
    #         Set the voltage value.
    #     positive_sensor_pin : int, .class pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance
    #         defining the positive sensor pin.
    #     negative_sensor_pin : int, .class pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance
    #         defining the negative sensor pin.
    #     load_regulation_current : str or float
    #         definition the load regulation current value.
    #     load_regulation_percent : float
    #         definition the load regulation percent value.
    #     """
    #     from pyedb.grpc.database.voltage_regulator import VoltageRegulator
    #
    #     voltage = self._pedb.edb_value(voltage)
    #     load_regulation_current = self._pedb.edb_value(load_regulation_current)
    #     load_regulation_percent = self._pedb.edb_value(load_regulation_percent)
    #     edb_vrm = self._edb_object = self._pedb._edb.Cell.VoltageRegulator.Create(
    #         self._pedb.active_layout, name, is_active, voltage, load_regulation_current, load_regulation_percent
    #     )
    #     vrm = VoltageRegulator(self._pedb, edb_vrm)
    #     if positive_sensor_pin:
    #         vrm.positive_remote_sense_pin = positive_sensor_pin
    #     if negative_sensor_pin:
    #         vrm.negative_remote_sense_pin = negative_sensor_pin
    #     return vrm

    @property
    def icepak_use_minimal_comp_defaults(self):
        """Icepak default setting. If "True", only resistor are active in Icepak simulation.
        The power dissipation of the resistors are calculated from DC results.
        """
        return self._pedb.active_cell.get_product_property(GrpcProductIdType.SIWAVE, 422).value

    def create_impedance_crosstalk_scan(self, scan_type="impedance"):
        """Create Siwave crosstalk scan object

        Parameters
        ----------
        scan_type : str
            Scan type to be analyzed. 3 options are available, ``impedance`` for frequency impedance scan,
            ``frequency_xtalk`` for frequency domain crosstalk and ``time_xtalk`` for time domain crosstalk.
            Default value is ``frequency``.

        """
        return SiwaveScanConfig(self._pedb, scan_type)

    @icepak_use_minimal_comp_defaults.setter
    def icepak_use_minimal_comp_defaults(self, value):
        value = "True" if bool(value) else ""
        self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, 422, value)

    @property
    def icepak_component_file(self):
        """Icepak component file path."""
        return self._pedb.active_cell.get_product_property(GrpcProductIdType.SIWAVE, 420).value
        return value

    @icepak_component_file.setter
    def icepak_component_file(self, value):
        self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, 420, value)
