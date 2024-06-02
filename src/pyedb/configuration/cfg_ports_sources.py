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

from pyedb.generic.general_methods import pyedb_function_handler


class CfgCircuitElement:
    @property
    def pedb(self):
        """Edb."""
        return self._pdata._pedb

    @pyedb_function_handler
    def __init__(self, pdata, **kwargs):
        self._pdata = pdata
        self._data = kwargs
        self.name = kwargs.get("name", None)
        self.type = kwargs.get("type", None)
        self.reference_designator = kwargs.get("reference_designator", None)
        self.distributed = kwargs.get("distributed", False)
        self.pos_term_info = kwargs.get("positive_terminal", None)  # {"pin" : "A1"}
        self.neg_term_info = kwargs.get("negative_terminal", None)

    @pyedb_function_handler
    def _create_terminals(self):
        """Create step 1. Collect positive and negative terminals."""
        pos_term_info = self.pos_term_info
        if pos_term_info:
            pos_type, pos_value = [[i, j] for i, j in pos_term_info.items()][0]
            pos_objs = dict()
            if self.type == "coax":
                pins = self._get_pins(pos_type, pos_value)
                pins = {f"{self.name}_{self.reference_designator}": i for _, i in pins.items()}
                pos_objs.update(pins)
            elif pos_type == "pin_group":
                pos_objs[pos_value] = self.pedb.siwave.pin_groups[pos_value]
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

        neg_term_info = self.neg_term_info
        self.neg_terminal = None
        if neg_term_info:
            neg_type, neg_value = [[i, j] for i, j in neg_term_info.items()][0]
            if neg_type == "nearest_pin":
                ref_net = neg_value.get("reference_net", "GND")
                search_radius = neg_value.get("search_radius", "5e-3")
                temp = dict()
                for i, j in pos_objs.items():
                    temp[i] = self._pdata._pedb.padstacks.get_reference_pins(j, ref_net, search_radius, max_limit=1)[0]
                self.neg_terminal = {
                    i: j.create_terminal(i + "_ref") if not j.terminal else j.terminal for i, j in temp.items()
                }
            else:
                if neg_type == "pin_group":
                    pin_group = {neg_value: self.pedb.siwave.pin_groups[neg_value]}
                else:
                    # Get pins
                    pins = self._get_pins(neg_type, neg_value)  # terminal type pin or net
                    # create pin group
                    pin_group = self._create_pin_group(pins, True)
                self.neg_terminal = [
                    j.create_terminal(i) if not j.terminal else j.terminal for i, j in pin_group.items()
                ][0]

    @pyedb_function_handler
    def _get_pins(self, terminal_type, terminal_value):
        terminal_value = terminal_value if isinstance(terminal_value, list) else [terminal_value]

        def get_pin_obj(pin_name):
            return {pin_name: self._pdata.edb_comps[self.reference_designator].pins[pin_name]}

        pins = dict()
        if terminal_type == "pin":
            for i in terminal_value:
                pins.update(get_pin_obj(i))
        else:
            if terminal_type == "net":
                temp = self._pdata._pedb.components.get_pins(self.reference_designator, terminal_value[0])
            elif terminal_type == "pin_group":
                pin_group = self.pedb.siwave.pin_groups[terminal_value[0]]
                temp = pin_group.pins
            pins.update({f"{self.reference_designator}_{terminal_value[0]}_{i}": j for i, j in temp.items()})
        return pins

    @pyedb_function_handler
    def _create_pin_group(self, pins, is_ref=False):
        if is_ref:
            pg_name = f"pg_{self.name}_{self.reference_designator}_ref"
        else:
            pg_name = f"pg_{self.name}_{self.reference_designator}"
        pin_names = [i.pin_number for i in pins.values()]
        name, temp = self._pdata._pedb.siwave.create_pin_group(self.reference_designator, pin_names, pg_name)
        return {name: temp}


class CfgPort(CfgCircuitElement):
    """Manage port."""

    CFG_PORT_TYPE = {"circuit": [str], "coax": [str]}

    @pyedb_function_handler
    def __init__(self, pdata, **kwargs):
        super().__init__(pdata, **kwargs)

    @pyedb_function_handler
    def create(self):
        """Create port."""
        self._create_terminals()
        is_circuit_port = True if self.type == "circuit" else False
        circuit_elements = []
        for name, j in self.pos_terminals.items():
            if isinstance(self.neg_terminal, dict):
                elem = self.pedb.create_port(j, self.neg_terminal[name], is_circuit_port)
            else:
                elem = self.pedb.create_port(j, self.neg_terminal, is_circuit_port)
            if not self.distributed:
                elem.name = self.name
            circuit_elements.append(elem)
        return circuit_elements


class CfgSources(CfgCircuitElement):
    CFG_SOURCE_TYPE = {"current": [int, float], "voltage": [int, float]}

    @pyedb_function_handler
    def __init__(self, pdata, **kwargs):
        super().__init__(pdata, **kwargs)

        self.magnitude = kwargs.get("magnitude", 0.001)

    @pyedb_function_handler
    def create(self):
        """Create sources."""
        self._create_terminals()
        is_circuit_port = True if self.type == "circuit" else False
        circuit_elements = []
        method = self.pedb.create_current_source if self.type == "current" else self.pedb.create_voltage_source
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
