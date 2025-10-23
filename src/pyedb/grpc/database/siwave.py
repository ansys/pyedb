# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from typing import Any, Dict, Optional, Union
import warnings

from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.simulation_setup.simulation_setup import (
    Distribution as GrpcDistribution,
    FrequencyData as GrpcFrequencyData,
    SweepData as GrpcSweepData,
)

from pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup import (
    SIWaveCPASimulationSetup,
)
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

    def __init__(self, p_edb) -> None:
        self._pedb = p_edb

    @property
    def _edb(self) -> Any:
        """EDB object."""
        return self._pedb

    @property
    def _logger(self) -> Any:
        """Logger object."""
        return self._pedb.logger

    @property
    def _active_layout(self) -> Any:
        """Active layout."""
        return self._pedb.active_layout

    @property
    def _layout(self) -> Any:
        """Active layout."""
        return self._pedb.layout

    @property
    def _cell(self) -> Any:
        """Active cell."""
        return self._pedb.active_cell

    @property
    def _db(self) -> Any:
        """Active database."""
        return self._pedb.active_db

    @property
    def excitations(self) -> Dict[str, Any]:
        """Excitation sources in the layout.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> excitations = edbapp.siwave.excitations
        """
        return self._pedb.excitations

    @property
    def sources(self) -> Dict[str, Any]:
        """All sources in the layout.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> sources = edbapp.siwave.sources
        """
        return self._pedb.sources

    @property
    def probes(self) -> Dict[str, Any]:
        """All probes in the layout.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> probes = edbapp.siwave.probes
        """
        return self._pedb.probes

    @property
    def pin_groups(self) -> Dict[str, Any]:
        """All layout pin groups.

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
        """
        _pingroups = {}
        for el in self._pedb.layout.pin_groups:
            _pingroups[el.name] = el
        return _pingroups

    def _create_terminal_on_pins(self, source):
        """Create a terminal on pins.

        .. deprecated:: pyedb 0.28.0
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
        """Create a resistor boundary between two given pins.

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
        """
        warnings.warn(
            "`create_resistor_on_pin` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_resistor_on_pin` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_resistor_on_pin(pos_pin, neg_pin, rvalue, resistor_name)

    def _check_gnd(self, component_name):
        """Check ground reference.

        .. deprecated:: pyedb 0.28.0
            Use :func:`pyedb.grpc.core.excitations._check_gnd` instead.
        """
        warnings.warn(
            "`_check_gnd` is deprecated and is now located here `pyedb.grpc.core.excitations._check_gnd` instead.",
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
        """Create a circuit port on a net.

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
        """Create a voltage source on a net.

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
        """Create a current source on a net.

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
        """Create a DC terminal.

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
        """
        warnings.warn(
            "`create_dc_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_dc_terminal` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_dc_terminal(component_name, net_name, source_name)

    def create_exec_file(
        self,
        add_dc: bool = False,
        add_ac: bool = False,
        add_syz: bool = False,
        export_touchstone: bool = False,
        touchstone_file_path: str = "",
    ) -> bool:
        """Create an executable file.

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
        bool
            ``True`` if file was created, ``False`` otherwise.

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

        return file_name

    def add_cpa_analysis(self, name=None, siwave_cpa_setup_class=None):
        if not name:
            from pyedb.generic.general_methods import generate_unique_name

            if not siwave_cpa_setup_class:
                name = generate_unique_name("cpa_setup")
            else:
                name = siwave_cpa_setup_class.name
        cpa_setup = SIWaveCPASimulationSetup(self._pedb, name=name, siwave_cpa_setup_class=siwave_cpa_setup_class)
        return cpa_setup

    def add_siwave_syz_analysis(
        self,
        accuracy_level: int = 1,
        distribution: str = "linear",
        start_freq: Union[str, float] = 1,
        stop_freq: Union[str, float] = 1e9,
        step_freq: Union[str, float, int] = 1e6,
        discrete_sweep: bool = False,
    ) -> Any:
        """Add a SIwave AC analysis to EDB.

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

    def add_siwave_dc_analysis(self, name: Optional[str] = None) -> Any:
        """Add a Siwave DC analysis in EDB.

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

        .. deprecated:: pyedb 0.28.0
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
        """Create physical RLC component.

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
        """
        warnings.warn(
            "`create_pin_group` is deprecated and is now located here "
            "`pyedb.grpc.core.components.create_pin_group` instead.",
            DeprecationWarning,
        )
        return self._pedb.components.create_pin_group(reference_designator, pin_numbers, group_name)

    def create_pin_group_on_net(self, reference_designator, net_name, group_name=None):
        """Create pin group on component by net name.

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

    def create_impedance_crosstalk_scan(self, scan_type: str = "impedance") -> "SiwaveScanConfig":
        """Create Siwave crosstalk scan object.

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
        """
        return SiwaveScanConfig(self._pedb, scan_type)

    @property
    def icepak_use_minimal_comp_defaults(self) -> bool:
        """Icepak default setting.

        If ``True``, only resistors are active in Icepak simulation and power dissipation
        is calculated from DC results.
        """
        return self._pedb.active_cell.get_product_property(GrpcProductIdType.SIWAVE, 422).value

    @icepak_use_minimal_comp_defaults.setter
    def icepak_use_minimal_comp_defaults(self, value):
        value = "True" if bool(value) else ""
        self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, 422, value)

    @property
    def icepak_component_file(self) -> str:
        """Icepak component file path."""
        return self._pedb.active_cell.get_product_property(GrpcProductIdType.SIWAVE, 420).value

    @icepak_component_file.setter
    def icepak_component_file(self, value):
        self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, 420, value)
