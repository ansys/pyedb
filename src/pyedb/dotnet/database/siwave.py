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
import time

from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.database.edb_data.simulation_configuration import (
    SimulationConfiguration,
    SourceType,
)
from pyedb.dotnet.database.edb_data.sources import (
    CircuitPort,
    CurrentSource,
    DCTerminal,
    ResistorSource,
    VoltageSource,
)
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.utilities.siwave_cpa_simulation_setup import (
    SIWaveCPASimulationSetup,
)
from pyedb.generic.constants import SolverType, SweepType
from pyedb.generic.general_methods import _retry_ntimes, generate_unique_name
from pyedb.misc.siw_feature_config.xtalk_scan.scan_config import SiwaveScanConfig
from pyedb.modeler.geometry_operators import GeometryOperators


class EdbSiwave(object):
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
        return self._pedb.core

    def _get_edb_value(self, value):
        """Get the Edb value."""
        return self._pedb.edb_value(value)

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
    def voltage_regulator_modules(self):
        """Get all voltage regulator modules"""
        return self._pedb.voltage_regulator_modules

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
            _pingroups[el._edb_object.GetName()] = el
        return _pingroups

    def _create_terminal_on_pins(self, source):
        """Create a terminal on pins.

        Parameters
        ----------
        source : VoltageSource, CircuitPort, CurrentSource or ResistorSource
            Name of the source.

        """
        if isinstance(source.positive_node.node_pins, EDBPadstackInstance):
            pos_pin = source.positive_node.node_pins._edb_padstackinstance
        else:
            pos_pin = source.positive_node.node_pins
        if isinstance(source.negative_node.node_pins, EDBPadstackInstance):
            neg_pin = source.negative_node.node_pins._edb_padstackinstance
        else:
            neg_pin = source.negative_node.node_pins

        res, fromLayer_pos, toLayer_pos = pos_pin.GetLayerRange()
        res, fromLayer_neg, toLayer_neg = neg_pin.GetLayerRange()

        pos_pingroup_terminal = _retry_ntimes(
            10,
            self._edb.cell.terminal.PadstackInstanceTerminal.Create,
            self._active_layout,
            pos_pin.GetNet(),
            pos_pin.GetName(),
            pos_pin,
            toLayer_pos,
        )
        time.sleep(0.5)
        neg_pingroup_terminal = _retry_ntimes(
            20,
            self._edb.cell.terminal.PadstackInstanceTerminal.Create,
            self._active_layout,
            neg_pin.GetNet(),
            neg_pin.GetName(),
            neg_pin,
            toLayer_neg,
        )
        if source.source_type in [SourceType.CoaxPort, SourceType.CircPort, SourceType.LumpedPort]:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.PortBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.PortBoundary)
            pos_pingroup_terminal.SetImpedance(self._get_edb_value(source.impedance))
            if source.source_type == SourceType.CircPort:
                pos_pingroup_terminal.SetIsCircuitPort(True)
                neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)
        elif source.source_type == SourceType.Isource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kCurrentSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kCurrentSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._get_edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._get_edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except Exception as e:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.source_type == SourceType.Vsource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kVoltageSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kVoltageSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._get_edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._get_edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.source_type == SourceType.Rlc:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.RlcBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.RlcBoundary)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            pos_pingroup_terminal.SetSourceAmplitude(self._get_edb_value(source.rvalue))
            Rlc = self._edb.utility.utility.Rlc()
            Rlc.CEnabled = False
            Rlc.LEnabled = False
            Rlc.REnabled = True
            Rlc.R = self._get_edb_value(source.rvalue)
            pos_pingroup_terminal.SetRlcBoundaryParameters(Rlc)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)
        else:
            pass
        return pos_pingroup_terminal.GetName()

    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create a circuit port on a pin.

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
        >>> edbapp.siwave.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")
        """
        circuit_port = CircuitPort()
        if not isinstance(pos_pin, EDBPadstackInstance):
            pos_pin = EDBPadstackInstance(pos_pin, self._pedb)
        if not isinstance(neg_pin, EDBPadstackInstance):
            neg_pin = EDBPadstackInstance(neg_pin, self._pedb)
        circuit_port.positive_node.net = pos_pin.net_name
        circuit_port.negative_node.net = neg_pin.net_name
        circuit_port.impedance = impedance

        if not port_name:
            port_name = "Port_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        circuit_port.name = port_name
        circuit_port.positive_node.component_node = pos_pin.component
        circuit_port.positive_node.node_pins = pos_pin
        circuit_port.negative_node.component_node = neg_pin.component
        circuit_port.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(circuit_port)

    def create_port_between_pin_and_layer(
        self, component_name=None, pins_name=None, layer_name=None, reference_net=None, impedance=50.0
    ):
        """Create circuit port between pin and a reference layer.

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
        if not pins_name:
            pins_name = []
        if pins_name:
            if not isinstance(pins_name, list):  # pragma no cover
                pins_name = [pins_name]
            if not reference_net:
                self._logger.info("no reference net provided, searching net {} instead.".format(layer_name))
                reference_net = self._pedb.nets.get_net_by_name(layer_name)
                if not reference_net:  # pragma no cover
                    self._logger.error("reference net {} not found.".format(layer_name))
                    return False
            else:
                if not isinstance(reference_net, self._edb.cell.net.net):  # pragma no cover
                    reference_net = self._pedb.nets.get_net_by_name(reference_net)
                if not reference_net:
                    self._logger.error("Net {} not found".format(reference_net))
                    return False
            for pin_name in pins_name:  # pragma no cover
                pin = [
                    pin
                    for pin in self._pedb.padstacks.get_pinlist_from_component_and_net(component_name)
                    if pin.component_pin == pin_name
                ][0]
                term_name = "{}_{}_{}".format(pin.component.name, pin._edb_object.GetNet().GetName(), pin.component_pin)
                res, start_layer, stop_layer = pin._edb_object.GetLayerRange()
                if res:
                    pin_instance = pin._edb_padstackinstance
                    positive_terminal = self._edb.cell.terminal.PadstackInstanceTerminal.Create(
                        self._active_layout, pin_instance.GetNet(), term_name, pin_instance, start_layer
                    )
                    positive_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.PortBoundary)
                    positive_terminal.SetImpedance(self._edb.utility.value(impedance))
                    positive_terminal.SetIsCircuitPort(True)
                    pos = self._pedb.components.get_pin_position(pin_instance)
                    position = self._edb.geometry.point_data(
                        self._edb.utility.value(pos[0]), self._edb.utility.value(pos[1])
                    )
                    negative_terminal = self._edb.cell.terminal.PointTerminal.Create(
                        self._active_layout,
                        reference_net.net_obj,
                        "{}_ref".format(term_name),
                        position,
                        self._pedb.stackup.signal_layers[layer_name]._edb_layer,
                    )
                    negative_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.PortBoundary)
                    negative_terminal.SetImpedance(self._edb.utility.value(impedance))
                    negative_terminal.SetIsCircuitPort(True)
                    if positive_terminal.SetReferenceTerminal(negative_terminal):
                        self._logger.info("Port {} successfully created".format(term_name))
                        return positive_terminal
            return False

    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """Create a voltage source.

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
        >>> edbapp.siwave.create_voltage_source_on_pin(pins[0], pins[1], 50, "source_name")
        """

        voltage_source = VoltageSource()
        voltage_source.positive_node.net = pos_pin.net_name
        voltage_source.negative_node.net = neg_pin.net_name
        voltage_source.magnitude = voltage_value
        voltage_source.phase = phase_value
        if not source_name:
            source_name = "VSource_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        voltage_source.name = source_name
        voltage_source.positive_node.component_node = pos_pin.component
        voltage_source.positive_node.node_pins = pos_pin
        voltage_source.negative_node.component_node = neg_pin.component
        voltage_source.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(voltage_source)

    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

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
        >>> edbapp.siwave.create_current_source_on_pin(pins[0], pins[1], 50, "source_name")
        """
        current_source = CurrentSource()
        current_source.positive_node.net = pos_pin.net_name
        current_source.negative_node.net = neg_pin.net_name
        current_source.magnitude = current_value
        current_source.phase = phase_value
        if not source_name:
            source_name = "ISource_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        current_source.name = source_name
        current_source.positive_node.component_node = pos_pin.component
        current_source.positive_node.node_pins = pos_pin
        current_source.negative_node.component_node = neg_pin.component
        current_source.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(current_source)

    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a Resistor boundary between two given pins..

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
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.siwave.create_resistor_on_pin(pins[0], pins[1],50,"res_name")
        """
        resistor = ResistorSource()
        resistor.positive_node.net = pos_pin.net_name
        resistor.negative_node.net = neg_pin.net_name
        resistor.rvalue = rvalue
        if not resistor_name:
            resistor_name = "Res_{}_{}_{}_{}".format(
                pos_pin.component.name,
                pos_pin.net_name,
                neg_pin.component.name,
                neg_pin.net_name,
            )
        resistor.name = resistor_name
        resistor.positive_node.component_node = pos_pin.component
        resistor.positive_node.node_pins = pos_pin
        resistor.negative_node.component_node = neg_pin.component
        resistor.negative_node.node_pins = neg_pin
        return self._create_terminal_on_pins(resistor)

    def _check_gnd(self, component_name):
        negative_net_name = None
        if self._pedb.nets.is_net_in_component(component_name, "GND"):
            negative_net_name = "GND"
        elif self._pedb.nets.is_net_in_component(component_name, "PGND"):
            negative_net_name = "PGND"
        elif self._pedb.nets.is_net_in_component(component_name, "AGND"):
            negative_net_name = "AGND"
        elif self._pedb.nets.is_net_in_component(component_name, "DGND"):
            negative_net_name = "DGND"
        if not negative_net_name:
            raise ValueError("No GND, PGND, AGND, DGND found. Please setup the negative net name manually.")
        return negative_net_name

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
        >>> edbapp.siwave.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        circuit_port = CircuitPort()
        circuit_port.positive_node.net = positive_net_name
        circuit_port.negative_node.net = negative_net_name
        circuit_port.impedance = impedance_value
        pos_node_cmp = self._pedb.components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)
        if port_name == "":
            port_name = "Port_{}_{}_{}_{}".format(
                positive_component_name,
                positive_net_name,
                negative_component_name,
                negative_net_name,
            )
        circuit_port.name = port_name
        circuit_port.positive_node.component_node = pos_node_cmp
        circuit_port.positive_node.node_pins = pos_node_pins
        circuit_port.negative_node.component_node = neg_node_cmp
        circuit_port.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(circuit_port)

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
        >>> edb.siwave.create_voltage_source_on_net("U2A5","V1P5_S3","U2A5","GND",3.3,0,"source_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        voltage_source = VoltageSource()
        voltage_source.positive_node.net = positive_net_name
        voltage_source.negative_node.net = negative_net_name
        voltage_source.magnitude = voltage_value
        voltage_source.phase = phase_value
        pos_node_cmp = self._pedb.components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Vsource_{}_{}_{}_{}".format(
                positive_component_name,
                positive_net_name,
                negative_component_name,
                negative_net_name,
            )
        voltage_source.name = source_name
        voltage_source.positive_node.component_node = pos_node_cmp
        voltage_source.positive_node.node_pins = pos_node_pins
        voltage_source.negative_node.component_node = neg_node_cmp
        voltage_source.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(voltage_source)

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
        >>> edb.siwave.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        current_source = CurrentSource()
        current_source.positive_node.net = positive_net_name
        current_source.negative_node.net = negative_net_name
        current_source.magnitude = current_value
        current_source.phase = phase_value
        pos_node_cmp = self._pedb.components.get_component_by_name(positive_component_name)
        neg_node_cmp = self._pedb.components.get_component_by_name(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)

        if source_name == "":
            source_name = "Port_{}_{}_{}_{}".format(
                positive_component_name,
                positive_net_name,
                negative_component_name,
                negative_net_name,
            )
        current_source.name = source_name
        current_source.positive_node.component_node = pos_node_cmp
        current_source.positive_node.node_pins = pos_node_pins
        current_source.negative_node.component_node = neg_node_cmp
        current_source.negative_node.node_pins = neg_node_pins
        return self.create_pin_group_terminal(current_source)

    def create_dc_terminal(
        self,
        component_name,
        net_name,
        source_name="",
    ):
        """Create a dc terminal.

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
        """

        dc_source = DCTerminal()
        dc_source.positive_node.net = net_name
        pos_node_cmp = self._pedb.components.get_component_by_name(component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(component_name, net_name)

        if source_name == "":
            source_name = "DC_{}_{}".format(
                component_name,
                net_name,
            )
        dc_source.name = source_name
        dc_source.positive_node.component_node = pos_node_cmp
        dc_source.positive_node.node_pins = pos_node_pins
        return self.create_pin_group_terminal(dc_source)

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
        name=None,
        accuracy_level=1,
        decade_count=10,
        sweeptype=1,
        start_freq=1,
        stop_freq=1e9,
        step_freq=1e6,
        discrete_sweep=False,
    ):
        """Add a SIwave AC analysis to EDB.

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
        """
        setup = self._pedb.create_siwave_syz_setup(name=name)
        sweep = "linear count"
        if sweeptype == 2:
            sweep = "log scale"
        elif sweeptype == 0:
            sweep = "linear scale"
        start_freq = self._pedb.number_with_units(start_freq, "Hz")
        stop_freq = self._pedb.number_with_units(stop_freq, "Hz")
        third_arg = int(decade_count)
        if sweeptype == 0:
            third_arg = self._pedb.number_with_units(step_freq, "Hz")
        setup.si_slider_position = int(accuracy_level)
        sweep = setup.add_frequency_sweep(
            frequency_sweep=[
                [sweep, start_freq, stop_freq, third_arg],
            ]
        )
        if discrete_sweep:
            sweep.freq_sweep_type = "kDiscreteSweep"

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

        Parameters
        ----------
        source : VoltageSource, CircuitPort, CurrentSource, DCTerminal or ResistorSource
            Name of the source.

        """
        if source.name in [i.name for i in self._layout.terminals]:
            source.name = generate_unique_name(source.name, n=3)
            self._logger.warning("Port already exists with same name. Renaming to {}".format(source.name))
        pos_pin_group = self._pedb.components.create_pingroup_from_pins(source.positive_node.node_pins)
        pos_node_net = self._pedb.nets.get_net_by_name(source.positive_node.net)

        pos_pingroup_term_name = source.name
        pos_pingroup_terminal = _retry_ntimes(
            10,
            self._edb.cell.terminal.PinGroupTerminal.Create,
            self._active_layout,
            pos_node_net.net_obj,
            pos_pingroup_term_name,
            pos_pin_group,
            False,
        )
        time.sleep(0.5)
        if source.negative_node.node_pins:
            neg_pin_group = self._pedb.components.create_pingroup_from_pins(source.negative_node.node_pins)
            neg_node_net = self._pedb.nets.get_net_by_name(source.negative_node.net)
            neg_pingroup_term_name = source.name + "_N"
            neg_pingroup_terminal = _retry_ntimes(
                20,
                self._edb.cell.terminal.PinGroupTerminal.Create,
                self._active_layout,
                neg_node_net.net_obj,
                neg_pingroup_term_name,
                neg_pin_group,
                False,
            )

        if source.source_type in [SourceType.CoaxPort, SourceType.CircPort, SourceType.LumpedPort]:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.PortBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.PortBoundary)
            pos_pingroup_terminal.SetSourceAmplitude(self._get_edb_value(source.impedance))
            if source.source_type == SourceType.CircPort:
                pos_pingroup_terminal.SetIsCircuitPort(True)
                neg_pingroup_terminal.SetIsCircuitPort(True)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.source_type == SourceType.Isource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kCurrentSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kCurrentSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._get_edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._edb.utility.value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except Exception as e:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.source_type == SourceType.Vsource:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kVoltageSource)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kVoltageSource)
            pos_pingroup_terminal.SetSourceAmplitude(self._get_edb_value(source.magnitude))
            pos_pingroup_terminal.SetSourcePhase(self._get_edb_value(source.phase))
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            try:
                pos_pingroup_terminal.SetName(source.name)
            except:
                name = generate_unique_name(source.name)
                pos_pingroup_terminal.SetName(name)
                self._logger.warning("%s already exists. Renaming to %s", source.name, name)

        elif source.source_type == SourceType.Rlc:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.RlcBoundary)
            neg_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.RlcBoundary)
            pos_pingroup_terminal.SetReferenceTerminal(neg_pingroup_terminal)
            pos_pingroup_terminal.SetSourceAmplitude(self._get_edb_value(source.rvalue))
            Rlc = self._edb.utility.utility.Rlc()
            Rlc.CEnabled = False
            Rlc.LEnabled = False
            Rlc.REnabled = True
            Rlc.R = self._get_edb_value(source.rvalue)
            pos_pingroup_terminal.SetRlcBoundaryParameters(Rlc)
        elif source.source_type == SourceType.DcTerminal:
            pos_pingroup_terminal.SetBoundaryType(self._edb.cell.terminal.BoundaryType.kDcTerminal)
        else:
            pass
        return pos_pingroup_terminal.GetName()

    def configure_siw_analysis_setup(self, simulation_setup=None, delete_existing_setup=True):
        """Configure Siwave analysis setup.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):  # pragma: no cover
            return False
        if simulation_setup.solver_type == SolverType.SiwaveSYZ:  # pragma: no cover
            simsetup_info = self._pedb.simsetupdata.SimSetupInfo[self._pedb.simsetupdata.SIwave.SIWSimulationSettings]()
            simsetup_info.Name = simulation_setup.setup_name
            simsetup_info.SimulationSettings.AdvancedSettings.PerformERC = False
            simsetup_info.SimulationSettings.UseCustomSettings = True
            if simulation_setup.mesh_freq:  # pragma: no cover
                if isinstance(simulation_setup.mesh_freq, str):
                    simsetup_info.SimulationSettings.UseCustomSettings = True
                    simsetup_info.SimulationSettings.AdvancedSettings.MeshAutoMatic = False
                    simsetup_info.SimulationSettings.AdvancedSettings.MeshFrequency = simulation_setup.mesh_freq
                else:
                    self._logger.warning("Meshing frequency value must be a string with units")
            if simulation_setup.include_inter_plane_coupling:  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.IncludeInterPlaneCoupling = (
                    simulation_setup.include_inter_plane_coupling
                )
            if abs(simulation_setup.xtalk_threshold):  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.XtalkThreshold = str(simulation_setup.xtalk_threshold)
            if simulation_setup.min_void_area:  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.MinVoidArea = simulation_setup.min_void_area
            if simulation_setup.min_pad_area_to_mesh:  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.MinPadAreaToMesh = (
                    simulation_setup.min_pad_area_to_mesh
                )
            if simulation_setup.min_plane_area_to_mesh:  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.MinPlaneAreaToMesh = (
                    simulation_setup.min_plane_area_to_mesh
                )
            if simulation_setup.snap_length_threshold:  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.SnapLengthThreshold = (
                    simulation_setup.snap_length_threshold
                )
            if simulation_setup.return_current_distribution:  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.ReturnCurrentDistribution = (
                    simulation_setup.return_current_distribution
                )
            if simulation_setup.ignore_non_functional_pads:  # pragma: no cover
                simsetup_info.SimulationSettings.AdvancedSettings.IgnoreNonFunctionalPads = (
                    simulation_setup.ignore_non_functional_pads
                )
            if simulation_setup.min_void_area:  # pragma: no cover
                simsetup_info.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh = simulation_setup.min_void_area
            try:
                if simulation_setup.add_frequency_sweep:
                    self._logger.info("Adding frequency sweep")
                    sweep = self._pedb.simsetupdata.SweepData(simulation_setup.sweep_name)
                    sweep.IsDiscrete = False  # need True for package??
                    sweep.UseQ3DForDC = simulation_setup.use_q3d_for_dc
                    sweep.RelativeSError = simulation_setup.relative_error
                    sweep.InterpUsePortImpedance = False
                    sweep.EnforceCausality = (GeometryOperators.parse_dim_arg(simulation_setup.start_freq) - 0) < 1e-9
                    sweep.EnforcePassivity = simulation_setup.enforce_passivity
                    sweep.PassivityTolerance = simulation_setup.passivity_tolerance
                    sweep.Frequencies.Clear()
                    if simulation_setup.sweep_type == SweepType.LogCount:  # pragma: no cover
                        self._setup_decade_count_sweep(
                            sweep,
                            simulation_setup.start_freq,
                            simulation_setup.stop_freq,
                            simulation_setup.decade_count,
                        )
                    else:
                        sweep.Frequencies = self._pedb.simsetupdata.SweepData.SetFrequencies(
                            simulation_setup.start_freq, simulation_setup.stop_freq, simulation_setup.step_freq
                        )
                    simsetup_info.SweepDataList.Add(sweep)
                else:
                    self._logger.info("Adding frequency sweep disabled")
            except Exception as err:
                self._logger.error("Exception in sweep configuration: {0}.".format(err))
            edb_sim_setup = self._edb.utility.utility.SIWaveSimulationSetup(simsetup_info)
            for setup in self._cell.SimulationSetups:
                self._cell.DeleteSimulationSetup(setup.GetName())
                self._logger.warning("Setup {} has been deleted".format(setup.GetName()))
            return self._cell.AddSimulationSetup(edb_sim_setup)
        if simulation_setup.solver_type == SolverType.SiwaveDC:  # pragma: no cover
            dcir_setup = self._pedb.simsetupdata.SimSetupInfo[
                self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings
            ]()
            dcir_setup.Name = simulation_setup.setup_name
            dcir_setup.SimulationSettings.DCSettings.ComputeInductance = simulation_setup.dc_compute_inductance
            dcir_setup.SimulationSettings.DCSettings.ContactRadius = simulation_setup.dc_contact_radius
            dcir_setup.SimulationSettings.DCSettings.DCSliderPos = simulation_setup.dc_slide_position
            dcir_setup.SimulationSettings.DCSettings.PlotJV = simulation_setup.dc_plot_jv
            dcir_setup.SimulationSettings.DCSettings.UseDCCustomSettings = simulation_setup.dc_use_dc_custom_settings
            dcir_setup.SimulationSettings.DCAdvancedSettings.DcMinPlaneAreaToMesh = (
                simulation_setup.dc_min_plane_area_to_mesh
            )
            dcir_setup.SimulationSettings.DCAdvancedSettings.DcMinVoidAreaToMesh = (
                simulation_setup.dc_min_void_area_to_mesh
            )
            dcir_setup.SimulationSettings.DCAdvancedSettings.EnergyError = simulation_setup.dc_error_energy
            dcir_setup.SimulationSettings.DCAdvancedSettings.MaxInitMeshEdgeLength = (
                simulation_setup.dc_max_init_mesh_edge_length
            )
            dcir_setup.SimulationSettings.DCAdvancedSettings.MaxNumPasses = simulation_setup.dc_max_num_pass
            dcir_setup.SimulationSettings.DCAdvancedSettings.MeshBws = simulation_setup.dc_mesh_bondwires
            dcir_setup.SimulationSettings.DCAdvancedSettings.MeshVias = simulation_setup.dc_mesh_vias
            dcir_setup.SimulationSettings.DCAdvancedSettings.MinNumPasses = simulation_setup.dc_min_num_pass
            dcir_setup.SimulationSettings.DCAdvancedSettings.NumBwSides = simulation_setup.dc_num_bondwire_sides
            dcir_setup.SimulationSettings.DCAdvancedSettings.NumViaSides = simulation_setup.dc_num_via_sides
            dcir_setup.SimulationSettings.DCAdvancedSettings.PercentLocalRefinement = (
                simulation_setup.dc_percent_local_refinement
            )
            dcir_setup.SimulationSettings.DCAdvancedSettings.PerformAdaptiveRefinement = (
                simulation_setup.dc_perform_adaptive_refinement
            )
            dcir_setup.SimulationSettings.DCAdvancedSettings.RefineBws = simulation_setup.dc_refine_bondwires
            dcir_setup.SimulationSettings.DCAdvancedSettings.RefineVias = simulation_setup.dc_refine_vias

            dcir_setup.SimulationSettings.DCIRSettings.DCReportConfigFile = simulation_setup.dc_report_config_file
            dcir_setup.SimulationSettings.DCIRSettings.DCReportShowActiveDevices = (
                simulation_setup.dc_report_show_Active_devices
            )
            dcir_setup.SimulationSettings.DCIRSettings.ExportDCThermalData = simulation_setup.dc_export_thermal_data
            dcir_setup.SimulationSettings.DCIRSettings.FullDCReportPath = simulation_setup.dc_full_report_path
            dcir_setup.SimulationSettings.DCIRSettings.IcepakTempFile = simulation_setup.dc_icepak_temp_file
            dcir_setup.SimulationSettings.DCIRSettings.ImportThermalData = simulation_setup.dc_import_thermal_data
            dcir_setup.SimulationSettings.DCIRSettings.PerPinResPath = simulation_setup.dc_per_pin_res_path
            dcir_setup.SimulationSettings.DCIRSettings.PerPinUsePinFormat = simulation_setup.dc_per_pin_use_pin_format
            dcir_setup.SimulationSettings.DCIRSettings.UseLoopResForPerPin = (
                simulation_setup.dc_use_loop_res_for_per_pin
            )
            dcir_setup.SimulationSettings.DCIRSettings.ViaReportPath = simulation_setup.dc_via_report_path
            dcir_setup.SimulationSettings.DCIRSettings.SourceTermsToGround = simulation_setup.dc_source_terms_to_ground
            dcir_setup.Name = simulation_setup.setup_name
            sim_setup = self._edb.utility.utility.SIWaveDCIRSimulationSetup(dcir_setup)
            for setup in self._cell.SimulationSetups:
                self._cell.DeleteSimulationSetup(setup.GetName())
                self._logger.warning("Setup {} has been delete".format(setup.GetName()))
            return self._cell.AddSimulationSetup(sim_setup)

    def _setup_decade_count_sweep(self, sweep, start_freq, stop_freq, decade_count):
        import math

        start_f = GeometryOperators.parse_dim_arg(start_freq)
        if start_f == 0.0:
            start_f = 10
            self._logger.warning(
                "Decade count sweep does not support a DC value. Defaulting starting frequency to 10Hz."
            )

        stop_f = GeometryOperators.parse_dim_arg(stop_freq)
        decade_cnt = GeometryOperators.parse_dim_arg(decade_count)
        freq = start_f
        sweep.Frequencies.Add(str(freq))
        while freq < stop_f:
            freq = freq * math.pow(10, 1.0 / decade_cnt)
            sweep.Frequencies.Add(str(freq))

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
        if not isinstance(pin_numbers, list):
            pin_numbers = [pin_numbers]
        pin_numbers = [str(p) for p in pin_numbers]
        if group_name is None:
            group_name = self._edb.cell.hierarchy.pin_group.GetUniqueName(self._active_layout)
        comp = self._pedb.components.instances[reference_designator]
        pins = [pin.pin for name, pin in comp.pins.items() if name in pin_numbers]
        edb_pingroup = self._edb.cell.hierarchy.pin_group.Create(
            self._active_layout, group_name, convert_py_list_to_net_list(pins)
        )

        if edb_pingroup.IsNull():  # pragma: no cover
            raise RuntimeError(f"Failed to create pin group {group_name}.")
        else:
            names = [i for i in pins if i.GetNet().GetName()]
            edb_pingroup.SetNet(names[0].GetNet())
            return group_name, self.pin_groups[group_name]

    def create_pin_group_on_net(self, reference_designator, net_name, group_name=None):
        """Create pin group on component by net name.

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
        pins = self._pedb.components.get_pin_from_component(reference_designator, net_name)
        pin_names = [p.GetName() for p in pins]
        return self.create_pin_group(reference_designator, pin_names, group_name)

    def create_current_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None
    ):
        """Create current source between two pin groups.

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
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_current_source_terminal(magnitude, phase)
        if name:
            pos_terminal.SetName(name)
        else:
            name = generate_unique_name("isource")
            pos_terminal.SetName(name)
        neg_pin_group_name = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group_name.create_current_source_terminal()
        neg_terminal.SetName(name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return True

    def create_voltage_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None, impedance=0.001
    ):
        """Create voltage source between two pin groups.

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
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_voltage_source_terminal(magnitude, phase, impedance)
        if name:
            pos_terminal.SetName(name)
        else:
            name = generate_unique_name("vsource")
            pos_terminal.SetName(name)
        neg_pin_group_name = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group_name.create_voltage_source_terminal(magnitude, phase)
        neg_terminal.SetName(name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return True

    def create_voltage_probe_on_pin_group(self, probe_name, pos_pin_group_name, neg_pin_group_name, impedance=1000000):
        """Create voltage probe between two pin groups.

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
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_voltage_probe_terminal(impedance)
        if probe_name:
            pos_terminal.SetName(probe_name)
        else:
            probe_name = generate_unique_name("vprobe")
            pos_terminal.SetName(probe_name)
        neg_pin_group = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group.create_voltage_probe_terminal()
        neg_terminal.SetName(probe_name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return not pos_terminal.IsNull()

    def create_circuit_port_on_pin_group(self, pos_pin_group_name, neg_pin_group_name, impedance=50, name=None):
        """Create a port between two pin groups.

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
        pos_pin_group = self.pin_groups[pos_pin_group_name]
        pos_terminal = pos_pin_group.create_port_terminal(impedance)
        if name:  # pragma: no cover
            pos_terminal.SetName(name)
        else:
            name = generate_unique_name("port")
            pos_terminal.SetName(name)
        neg_pin_group = self.pin_groups[neg_pin_group_name]
        neg_terminal = neg_pin_group.create_port_terminal(impedance)
        neg_terminal.SetName(name + "_ref")
        pos_terminal.SetReferenceTerminal(neg_terminal)
        return True

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
        p_terminal = self._pedb.get_point_terminal(name, positive_net_name, positive_location, positive_layer)
        n_terminal = self._pedb.get_point_terminal(name + "_ref", negative_net_name, negative_location, negative_layer)
        return self._pedb.create_voltage_probe(p_terminal, n_terminal)

    def create_vrm_module(
        self,
        name=None,
        is_active=True,
        voltage="3V",
        positive_sensor_pin=None,
        negative_sensor_pin=None,
        load_regulation_current="1A",
        load_regulation_percent=0.1,
    ):
        """Create a voltage regulator module.

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
        """
        from pyedb.dotnet.database.cell.voltage_regulator import VoltageRegulator

        voltage = self._pedb.edb_value(voltage)
        load_regulation_current = self._pedb.edb_value(load_regulation_current)
        load_regulation_percent = self._pedb.edb_value(load_regulation_percent)
        edb_vrm = self._edb_object = self._pedb._edb.Cell.VoltageRegulator.Create(
            self._pedb.active_layout, name, is_active, voltage, load_regulation_current, load_regulation_percent
        )
        vrm = VoltageRegulator(self._pedb, edb_vrm)
        if positive_sensor_pin:
            vrm.positive_remote_sense_pin = positive_sensor_pin
        if negative_sensor_pin:
            vrm.negative_remote_sense_pin = negative_sensor_pin
        return vrm

    @property
    def icepak_use_minimal_comp_defaults(self):
        """Icepak default setting. If "True", only resistor are active in Icepak simulation.
        The power dissipation of the resistors are calculated from DC results.
        """
        siwave_id = self._pedb.core.ProductId.SIWave
        cell = self._pedb.active_cell._active_cell
        _, value = cell.GetProductProperty(siwave_id, 422, "")
        return bool(value)

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

    def add_cpa_analysis(self, name=None, siwave_cpa_setup_class=None):
        if not name:
            from pyedb.generic.general_methods import generate_unique_name

            if not siwave_cpa_setup_class:
                name = generate_unique_name("cpa_setup")
            else:
                name = siwave_cpa_setup_class.name
        cpa_setup = SIWaveCPASimulationSetup(self._pedb, name=name, siwave_cpa_setup_class=siwave_cpa_setup_class)
        return cpa_setup

    @icepak_use_minimal_comp_defaults.setter
    def icepak_use_minimal_comp_defaults(self, value):
        value = "True" if bool(value) else ""
        siwave_id = self._pedb.core.ProductId.SIWave
        cell = self._pedb.active_cell._active_cell
        cell.SetProductProperty(siwave_id, 422, value)

    @property
    def icepak_component_file(self):
        """Icepak component file path."""
        siwave_id = self._pedb.core.ProductId.SIWave
        cell = self._pedb.active_cell._active_cell
        _, value = cell.GetProductProperty(siwave_id, 420, "")
        return value

    @icepak_component_file.setter
    def icepak_component_file(self, value):
        siwave_id = self._pedb.core.ProductId.SIWave
        cell = self._pedb.active_cell._active_cell
        cell.SetProductProperty(siwave_id, 420, value)
