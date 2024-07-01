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

from pyedb.configuration.cfg_common import CfgBase


class CfgTerminalInfo(CfgBase):
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.type = list(kwargs.keys())[0]
        """self.pin = kwargs.get('pin')
        self.net = kwargs.get('net')
        self.pin_group = kwargs.get('pin_group')
        self.nearest_pin = kwargs.get('nearest_pin')
        self.coordinates = kwargs.get('coordinates')"""
        self.value = kwargs[self.type]

    """@property
    def type(self):
        if self.pin:
            return "pin"
        if self.net:
            return "net"
        if self.nearest_pin:
            return "nearest_pin"
        if self.coordinates:
            return "coordinates"
        if self.pin_group:
            return "pin_group"""


    def export_properties(self):
        return {
            self.type: self.value
        }


class CfgCoordianteTerminalInfo(CfgTerminalInfo):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

        self.layer = self.value["layer"]
        self.point_x = self.value["point"][0]
        self.point_y = self.value["point"][1]
        self.net = self.value["net"]

    def export_properties(self):
        return {
            "layer": self.layer,
            "point_x": self.point_x,
            "point_y": self.point_y,
            "net": self.net
        }


class CfgNearestPinTerminalInfo(CfgTerminalInfo):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)
        self.reference_net = self.value["reference_net"]
        self.search_radius = self.value["search_radius"]

    def export_properties(self):
        return


class CfgSources:
    def __init__(self, pedb, sources_data):
        self._pedb = pedb
        self.sources = [CfgSource(self._pedb, **src) for src in sources_data]

    def apply(self):
        for src in self.sources:
            src.create()


class CfgPorts:
    def __init__(self, pedb, ports_data):
        self._pedb = pedb
        self.ports = [CfgPort(self._pedb, **p) for p in ports_data]

    def apply(self):
        for p in self.ports:
            p.create()


class CfgCircuitElement(CfgBase):

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs.get("name", None)
        self.type = kwargs.get("type", None)
        self.reference_designator = kwargs.get("reference_designator", None)
        self.distributed = kwargs.get("distributed", False)

        pos = kwargs["positive_terminal"]  # {"pin" : "A1"}
        if list(pos.keys())[0] == "coordinates":
            self.positive_terminal_info = CfgCoordianteTerminalInfo(self._pedb, **pos)
        else:
            self.positive_terminal_info = CfgTerminalInfo(self._pedb, **pos)

        neg = kwargs.get("negative_terminal", {})
        if len(neg) == 0:
            self.negative_terminal_info = None
        elif list(neg.keys())[0] == "coordinates":
            self.negative_terminal_info = CfgCoordianteTerminalInfo(self._pedb, **neg)
        elif list(neg.keys())[0] == "nearest_pin":
            self.negative_terminal_info = CfgNearestPinTerminalInfo(self._pedb, **neg)
        else:
            self.negative_terminal_info = CfgTerminalInfo(self._pedb, **neg)

    def _create_terminals(self):
        """Create step 1. Collect positive and negative terminals."""

        pos_type, pos_value = self.positive_terminal_info.type, self.positive_terminal_info.value
        pos_objs = dict()
        pos_coor_terminal = dict()
        if self.type == "coax":
            pins = self._get_pins(pos_type, pos_value)
            pins = {f"{self.name}_{self.reference_designator}": i for _, i in pins.items()}
            pos_objs.update(pins)
        elif pos_type == "coordinates":
            layer = self.positive_terminal_info.layer
            point = [self.positive_terminal_info.point_x, self.positive_terminal_info.point_y]
            net_name = self.positive_terminal_info.net
            pos_coor_terminal[self.name] = self._pedb.get_point_terminal(self.name, net_name, point, layer)
        elif pos_type == "pin_group":
            pos_objs[pos_value] = self._pedb.siwave.pin_groups[pos_value]
        elif not self.distributed:
            # get pins
            pins = self._get_pins(pos_type, pos_value)  # terminal type pin or net
            # create pin group
            pin_group = self._create_pin_group(pins)
            pos_objs.update(pin_group)
        else:
            # get pins
            pins = self._get_pins(pos_type, pos_value)  # terminal type pin or net or pin group
            pos_objs.update(pins)
            self._elem_num = len(pos_objs)

        self.pos_terminals = {i: j.create_terminal(i) for i, j in pos_objs.items()}
        self.pos_terminals.update(pos_coor_terminal)

        self.neg_terminal = None
        if self.negative_terminal_info:
            neg_type, neg_value = self.negative_terminal_info.type, self.negative_terminal_info.value

            if neg_type == "coordinates":
                layer = self.negative_terminal_info.layer
                point = [self.negative_terminal_info.point_x, self.positive_terminal_info.point_y]
                net_name = self.negative_terminal_info.net
                self.neg_terminal = self._pedb.get_point_terminal(self.name + "_ref", net_name, point, layer)
            elif neg_type == "nearest_pin":
                ref_net = neg_value.get("reference_net", "GND")
                search_radius = neg_value.get("search_radius", "5e-3")
                temp = dict()
                for i, j in pos_objs.items():
                    temp[i] = self._pedb.padstacks.get_reference_pins(j, ref_net, search_radius, max_limit=1)[0]
                self.neg_terminal = {
                    i: j.create_terminal(i + "_ref") if not j.terminal else j.terminal for i, j in temp.items()
                }
            else:
                if neg_type == "pin_group":
                    pin_group = {neg_value: self._pedb.siwave.pin_groups[neg_value]}
                else:
                    # Get pins
                    pins = self._get_pins(neg_type, neg_value)  # terminal type pin or net
                    # create pin group
                    pin_group = self._create_pin_group(pins, True)
                self.neg_terminal = [
                    j.create_terminal(i) if not j.terminal else j.terminal for i, j in pin_group.items()
                ][0]

    def export_properties(self):
        elem = {}
        elem.update(self.pos_terminals)  # todo
        elem.update(self.neg_terminal)  # todo
        elem["reference_designator"] = self.reference_designator
        # elem["positive_terminal"] = self.pos_terminals. # todo
        pass

    def _get_pins(self, terminal_type, terminal_value):
        terminal_value = terminal_value if isinstance(terminal_value, list) else [terminal_value]

        def get_pin_obj(pin_name):
            return {pin_name: self._pedb.components.components[self.reference_designator].pins[pin_name]}

        pins = dict()
        if terminal_type == "pin":
            for i in terminal_value:
                pins.update(get_pin_obj(i))
        else:
            if terminal_type == "net":
                temp = self._pedb.components.get_pins(self.reference_designator, terminal_value[0])
            elif terminal_type == "pin_group":
                pin_group = self._pedb.siwave.pin_groups[terminal_value[0]]
                temp = pin_group.pins
            pins.update({f"{self.reference_designator}_{terminal_value[0]}_{i}": j for i, j in temp.items()})
        return pins

    def _create_pin_group(self, pins, is_ref=False):
        if is_ref:
            pg_name = f"pg_{self.name}_{self.reference_designator}_ref"
        else:
            pg_name = f"pg_{self.name}_{self.reference_designator}"
        pin_names = [i.pin_number for i in pins.values()]
        name, temp = self._pedb.siwave.create_pin_group(self.reference_designator, pin_names, pg_name)
        return {name: temp}


class CfgPort(CfgCircuitElement):
    """Manage port."""

    CFG_PORT_TYPE = {"circuit": [str], "coax": [str]}

    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

    def create(self):
        """Create port."""
        self._create_terminals()
        is_circuit_port = True if self.type == "circuit" else False
        circuit_elements = []
        for name, j in self.pos_terminals.items():
            if isinstance(self.neg_terminal, dict):
                elem = self._pedb.create_port(j, self.neg_terminal[name], is_circuit_port)
            else:
                elem = self._pedb.create_port(j, self.neg_terminal, is_circuit_port)
            if not self.distributed:
                elem.name = self.name
            circuit_elements.append(elem)
        return circuit_elements


class CfgSource(CfgCircuitElement):
    CFG_SOURCE_TYPE = {"current": [int, float], "voltage": [int, float]}

    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

        self.magnitude = kwargs.get("magnitude", 0.001)

    def create(self):
        """Create sources."""
        self._create_terminals()
        # is_circuit_port = True if self.type == "circuit" else False
        circuit_elements = []
        method = self._pedb.create_current_source if self.type == "current" else self._pedb.create_voltage_source
        for name, j in self.pos_terminals.items():
            if isinstance(self.neg_terminal, dict):
                elem = method(j, self.neg_terminal[name])
            else:
                elem = method(j, self.neg_terminal)
            if not self.distributed:
                elem.name = self.name
                elem.magnitude = self.magnitude
            else:
                elem.name = f"{self.name}_{elem.name}"
                elem.magnitude = self.magnitude / self._elem_num
            circuit_elements.append(elem)
        return circuit_elements
