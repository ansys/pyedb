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


from pyedb.generic.constants import NodeType, SourceType
from pyedb.grpc.database.hierarchy.pingroup import PinGroup


class Node(object):
    """Provides for handling nodes for Siwave sources."""

    def __init__(self):
        self._component = None
        self._net = None
        self._node_type = NodeType.Positive
        self._name = ""

    @property
    def component(self) -> str:
        """Component name containing the node."""
        return self._component

    @component.setter
    def component(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._component = value

    @property
    def net(self):  # pragma: no cover
        """Net of the node."""
        return self._net

    @net.setter
    def net(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._net = value

    @property
    def node_type(self):  # pragma: no cover
        """Type of the node."""
        return self._node_type

    @node_type.setter
    def node_type(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._node_type = value

    @property
    def name(self):  # pragma: no cover
        """Name of the node."""
        return self._name

    @name.setter
    def name(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._name = value

    def _json_format(self):  # pragma: no cover
        dict_out = {}
        for k, v in self.__dict__.items():
            dict_out[k[1:]] = v
        return dict_out

    def _read_json(self, node_dict):  # pragma: no cover
        for k, v in node_dict.items():
            self.__setattr__(k, v)


class Source(object):
    """Provides for handling Siwave sources."""

    def __init__(self, pedb):
        self._pedb = pedb
        self._name = ""
        self._source_type = SourceType.Vsource
        self._positive_node = PinGroup(self._pedb)
        self._negative_node = PinGroup(self._pedb)
        self._amplitude = 1.0
        self._phase = 0.0
        self._impedance = 1.0
        self._r = 1.0
        self._l = 0.0
        self._c = 0.0
        self._create_physical_resistor = True
        self._positive_node.node_type = int(NodeType.Positive)
        self._positive_node.name = "pos_term"
        self._negative_node.node_type = int(NodeType.Negative)
        self._negative_node.name = "neg_term"

    @property
    def name(self):  # pragma: no cover
        """Source name."""
        return self._name

    @name.setter
    def name(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._name = value

    @property
    def source_type(self):  # pragma: no cover
        """Source type."""
        return self._source_type

    @source_type.setter
    def source_type(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._source_type = value
            if value == 3:
                self._impedance = 1e-6
            if value == 4:
                self._impedance = 5e7
            if value == 5:
                self._r = 1.0
                self._l = 0.0
                self._c = 0.0

    @property
    def positive_node(self):  # pragma: no cover
        """Positive node of the source."""
        return self._positive_node

    @positive_node.setter
    def positive_node(self, value):  # pragma: no cover
        if isinstance(value, (Node, PinGroup)):
            self._positive_node = value

    @property
    def negative_node(self):  # pragma: no cover
        """Negative node of the source."""
        return self._negative_node

    @negative_node.setter
    def negative_node(self, value):  # pragma: no cover
        if isinstance(value, (Node, PinGroup)):
            self._negative_node = value
            #

    @property
    def amplitude(self):  # pragma: no cover
        """Amplitude value of the source. Either amperes for current source or volts for
        voltage source."""
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):  # pragma: no cover
        if isinstance(float(value), float):
            self._amplitude = value

    @property
    def phase(self):  # pragma: no cover
        """Phase of the source."""
        return self._phase

    @phase.setter
    def phase(self, value):  # pragma: no cover
        if isinstance(float(value), float):
            self._phase = value

    @property
    def impedance(self):  # pragma: no cover
        """Impedance values of the source."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):  # pragma: no cover
        if isinstance(float(value), float):
            self._impedance = value

    @property
    def r_value(self):
        return self._r

    @r_value.setter
    def r_value(self, value):
        if isinstance(float(value), float):
            self._r = value

    @property
    def l_value(self):
        return self._l

    @l_value.setter
    def l_value(self, value):
        if isinstance(float(value), float):
            self._l = value

    @property
    def c_value(self):
        return self._c

    @c_value.setter
    def c_value(self, value):
        if isinstance(float(value), float):
            self._c = value

    @property
    def create_physical_resistor(self):
        return self._create_physical_resistor

    @create_physical_resistor.setter
    def create_physical_resistor(self, value):
        if isinstance(value, bool):
            self._create_physical_resistor = value

    def _json_format(self):  # pragma: no cover
        dict_out = {}
        for k, v in self.__dict__.items():
            if k == "_positive_node" or k == "_negative_node":
                nodes = v._json_format()
                dict_out[k[1:]] = nodes
            else:
                dict_out[k[1:]] = v
        return dict_out

    def _read_json(self, source_dict):  # pragma: no cover
        for k, v in source_dict.items():
            if k == "positive_node":
                self.positive_node._read_json(v)
            elif k == "negative_node":
                self.negative_node._read_json(v)
            else:
                self.__setattr__(k, v)


class CircuitPort(Source):
    """Manages a circuit port."""

    def __init__(self, pedb, impedance="50"):
        self._impedance = impedance
        super().__init__(self)
        self._source_type = SourceType.CircPort

    @property
    def impedance(self):
        """Impedance."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):
        self._impedance = value

    @property
    def get_type(self):
        """Get type."""
        return self._source_type


class VoltageSource(Source):
    """Manages a voltage source."""

    def __init__(self):
        super(VoltageSource, self).__init__()
        self._magnitude = "1V"
        self._phase = "0Deg"
        self._impedance = "0.05"
        self._source_type = SourceType.Vsource

    @property
    def magnitude(self):
        """Magnitude."""
        return self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value

    @property
    def phase(self):
        """Phase."""
        return self._phase

    @phase.setter
    def phase(self, value):
        self._phase = value

    @property
    def impedance(self):
        """Impedance."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):
        self._impedance = value

    @property
    def source_type(self):
        """Source type."""
        return self._source_type


class CurrentSource(Source):
    """Manages a current source."""

    def __init__(self):
        super(CurrentSource, self).__init__()
        self._magnitude = "0.1A"
        self._phase = "0Deg"
        self._impedance = "1e7"
        self._source_type = SourceType.Isource

    @property
    def magnitude(self):
        """Magnitude."""
        return self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value

    @property
    def phase(self):
        """Phase."""
        return self._phase

    @phase.setter
    def phase(self, value):
        self._phase = value

    @property
    def impedance(self):
        """Impedance."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):
        self._impedance = value

    @property
    def source_type(self):
        """Source type."""
        return self._source_type


class DCTerminal(Source):
    """Manages a dc terminal source."""

    def __init__(self):
        super(DCTerminal, self).__init__()

        self._source_type = SourceType.DcTerminal

    @property
    def source_type(self):
        """Source type."""
        return self._source_type


class ResistorSource(Source):
    """Manages a resistor source."""

    def __init__(self):
        super(ResistorSource, self).__init__()
        self._rvalue = "50"
        self._source_type = SourceType.Rlc

    @property
    def rvalue(self):
        """Resistance value."""
        return self._rvalue

    @rvalue.setter
    def rvalue(self, value):
        self._rvalue = value

    @property
    def source_type(self):
        """Source type."""
        return self._source_type
