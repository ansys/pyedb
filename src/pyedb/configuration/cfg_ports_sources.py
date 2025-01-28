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
from pyedb.dotnet.edb_core.edb_data.ports import WavePort
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list
from pyedb.dotnet.edb_core.geometry.point_data import PointData


class CfgTerminalInfo(CfgBase):
    CFG_TERMINAL_TYPES = ["pin", "net", "pin_group", "nearest_pin", "coordinates"]

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.type = list(kwargs.keys())[0]
        self.value = kwargs[self.type]

    def export_properties(self):
        return {self.type: self.value}


class CfgCoordianteTerminalInfo(CfgTerminalInfo):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

        self.layer = self.value["layer"]
        self.point_x = self.value["point"][0]
        self.point_y = self.value["point"][1]
        self.net = self.value["net"]
        self.contact_radius = self.value.get("contact_radius", None)

    def export_properties(self):
        return {"coordinates": {"layer": self.layer, "point": [self.point_x, self.point_y], "net": self.net}}


class CfgNearestPinTerminalInfo(CfgTerminalInfo):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)
        self.reference_net = self.value["reference_net"]
        self.search_radius = self.value["search_radius"]

    def export_properties(self):
        return {"reference_net": self.reference_net, "search_radius": self.search_radius}


class CfgSources:
    def __init__(self, pedb, sources_data):
        self._pedb = pedb
        self.sources = [CfgSource(self._pedb, **src) for src in sources_data]

    def apply(self):
        for src in self.sources:
            src.set_parameters_to_edb()

    def get_data_from_db(self):
        self.sources = []
        sources = {name: t for name, t in self._pedb.terminals.items() if not t.is_reference_terminal}
        sources = {name: t for name, t in sources.items() if t.is_current_source or t.is_voltage_source}

        for _, src in sources.items():
            src_type = "voltage" if "voltage" in src.boundary_type.lower() else "current"
            name = src.name
            magnitude = src.magnitude

            if src.terminal_type == "PinGroupTerminal":
                refdes = ""
                pg = self._pedb.siwave.pin_groups[src._edb_object.GetPinGroup().GetName()]
                pos_term_info = {"pin_group": pg.name}
            elif src.terminal_type == "PadstackInstanceTerminal":
                refdes = src.component.refdes if src.component else ""
                pos_term_info = {"pin": src.padstack_instance.component_pin}

            neg_term = self._pedb.terminals[src.ref_terminal.name]
            if neg_term.terminal_type == "PinGroupTerminal":
                pg = self._pedb.siwave.pin_groups[neg_term._edb_object.GetPinGroup().GetName()]
                neg_term_info = {"pin_group": pg.name}
            elif neg_term.terminal_type == "PadstackInstanceTerminal":
                neg_term_info = {"pin": neg_term.padstack_instance.component_pin}

            cfg_src = CfgSource(
                self._pedb,
                name=name,
                type=src_type,
                magnitude=magnitude,
                reference_designator=refdes,
                positive_terminal=pos_term_info,
                negative_terminal=neg_term_info,
            )
            self.sources.append(cfg_src)
        return self.export_properties()

    def export_properties(self):
        sources = []
        for src in self.sources:
            sources.append(src.export_properties())
        return sources


class CfgPorts:
    def __init__(self, pedb, ports_data):
        self._pedb = pedb

        self.ports = []
        for p in ports_data:
            if p["type"] == "wave_port":
                self.ports.append(CfgWavePort(self._pedb, **p))
            elif p["type"] == "diff_wave_port":
                self.ports.append(CfgDiffWavePort(self._pedb, **p))
            elif p["type"] in ["coax", "circuit"]:
                self.ports.append(CfgPort(self._pedb, **p))
            else:
                raise ValueError("Unknown port type")

    def apply(self):
        edb_primitives = {}
        for i in self._pedb.layout.primitives:
            if i.aedt_name:
                edb_primitives[i.aedt_name] = i
        for p in self.ports:
            if p.type in ["wave_port", "diff_wave_port"]:
                p.set_parameters_to_edb(edb_primitives)
            else:
                p.set_parameters_to_edb()

    def get_data_from_db(self):
        self.ports = []
        ports = {name: t for name, t in self._pedb.terminals.items() if not t.is_reference_terminal}
        ports = {name: t for name, t in ports.items() if t.is_port}

        for _, p in ports.items():
            if not p.ref_terminal:
                port_type = "coax"
            else:
                port_type = "circuit"

            if p.terminal_type == "PinGroupTerminal":
                refdes = ""
                pg = self._pedb.siwave.pin_groups[p._edb_object.GetPinGroup().GetName()]
                pos_term_info = {"pin_group": pg.name}
            elif p.terminal_type == "PadstackInstanceTerminal":
                refdes = p.component.refdes if p.component else ""
                pos_term_info = {"pin": p.padstack_instance.component_pin}
            elif p.terminal_type == "PointTerminal":
                refdes = ""
                pos_term_info = {"coordinates": {"layer": p.layer.name, "point": p.location, "net": p.net.name}}

            if port_type == "circuit":
                neg_term = self._pedb.terminals[p.ref_terminal.name]
                if neg_term.terminal_type == "PinGroupTerminal":
                    pg = self._pedb.siwave.pin_groups[neg_term._edb_object.GetPinGroup().GetName()]
                    neg_term_info = {"pin_group": pg.name}
                elif neg_term.terminal_type == "PadstackInstanceTerminal":
                    neg_term_info = {"pin": neg_term.padstack_instance.component_pin}
                elif neg_term.terminal_type == "PointTerminal":
                    neg_term_info = {
                        "coordinates": {
                            "layer": neg_term.layer.name,
                            "point": neg_term.location,
                            "net": neg_term.net.name,
                        }
                    }

                cfg_port = CfgPort(
                    self._pedb,
                    name=p.name,
                    type=port_type,
                    reference_designator=refdes,
                    positive_terminal=pos_term_info,
                    negative_terminal=neg_term_info,
                )
            else:
                cfg_port = CfgPort(
                    self._pedb,
                    name=p.name,
                    type=port_type,
                    reference_designator=refdes,
                    positive_terminal=pos_term_info,
                )

            self.ports.append(cfg_port)
        return self.export_properties()

    def export_properties(self):
        ports = []
        for p in self.ports:
            ports.append(p.export_properties())
        return ports


class CfgCircuitElement(CfgBase):
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs["name"]
        self.type = kwargs["type"]
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
            if self.positive_terminal_info.contact_radius:
                pos_coor_terminal[self.name].contact_radius = self.positive_terminal_info.contact_radius

        elif pos_type == "pin_group":
            if self.distributed:
                pins = self._get_pins(pos_type, pos_value)
                pos_objs.update(pins)
                self._elem_num = len(pos_objs)
            else:
                pos_objs[pos_value] = self._pedb.siwave.pin_groups[pos_value]
        elif pos_type == "net":
            if self.distributed:
                pins = self._get_pins(pos_type, pos_value)
                pos_objs.update(pins)
                self._elem_num = len(pos_objs)
            else:
                pins = self._get_pins(pos_type, pos_value)
                # create pin group
                neg_obj = self._create_pin_group(pins)
                pos_objs.update(neg_obj)
        elif pos_type == "pin":
            pins = {pos_value: self._pedb.components.instances[self.reference_designator].pins[pos_value]}
            pos_objs.update(pins)
        else:
            raise Exception(f"Wrong positive terminal type {pos_type}.")

        self.pos_terminals = {i: j.create_terminal(i) for i, j in pos_objs.items()}
        self.pos_terminals.update(pos_coor_terminal)

        self.neg_terminal = None
        if self.negative_terminal_info:
            neg_type, neg_value = self.negative_terminal_info.type, self.negative_terminal_info.value

            if neg_type == "coordinates":
                layer = self.negative_terminal_info.layer
                point = [self.negative_terminal_info.point_x, self.negative_terminal_info.point_y]
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
                    neg_obj = {neg_value: self._pedb.siwave.pin_groups[neg_value]}
                elif neg_type == "net":
                    # Get pins
                    pins = self._get_pins(neg_type, neg_value)  # terminal type pin or net
                    # create pin group
                    neg_obj = self._create_pin_group(pins, True)
                elif neg_type == "pin":
                    terminal_name = f"{self.reference_designator}_{neg_value}"
                    neg_obj = {
                        terminal_name: self._pedb.components.instances[self.reference_designator].pins[neg_value]
                    }
                else:
                    raise Exception(f"Wrong negative terminal type {neg_type}.")
                self.neg_terminal = [
                    j.create_terminal(i) if not j.terminal else j.terminal for i, j in neg_obj.items()
                ][0]

    def _get_pins(self, terminal_type, terminal_value):
        terminal_value = terminal_value if isinstance(terminal_value, list) else [terminal_value]

        def get_pin_obj(pin_name):
            return {pin_name: self._pedb.components.instances[self.reference_designator].pins[pin_name]}

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
        pin_names = [i.component_pin for i in pins.values()]
        name, temp = self._pedb.siwave.create_pin_group(self.reference_designator, pin_names, pg_name)
        return {name: temp}


class CfgPort(CfgCircuitElement):
    """Manage port."""

    CFG_PORT_TYPE = {"circuit": [str], "coax": [str]}

    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

    def set_parameters_to_edb(self):
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

    def export_properties(self):
        data = {
            "name": self.name,
            "type": self.type,
            "reference_designator": self.reference_designator,
            "positive_terminal": self.positive_terminal_info.export_properties(),
        }
        if self.negative_terminal_info:
            data.update({"negative_terminal": self.negative_terminal_info.export_properties()})
        return data


class CfgSource(CfgCircuitElement):
    CFG_SOURCE_TYPE = {"current": [int, float], "voltage": [int, float]}

    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

        self.magnitude = kwargs.get("magnitude", 0.001)
        self.equipotential = kwargs.get("equipotential", False)

    def set_parameters_to_edb(self):
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
        for terminal in circuit_elements:
            if self.equipotential:
                terms = [terminal, terminal.ref_terminal] if terminal.ref_terminal else [terminal]
                for t in terms:
                    pads = []
                    if t.terminal_type == "PadstackInstanceTerminal":
                        pads.append(t.reference_object)
                        t._edb_object.dcir_equipotential_region = True
                    elif t.terminal_type == "PinGroupTerminal":
                        name = t._edb_object.GetPinGroup().GetName()
                        pg = self._pedb.siwave.pin_groups[name]
                        pads.extend([i for _, i in pg.pins.items()])
                    elif t.terminal_type == "PointTerminal":
                        temp = [i for i in self._pedb.layout.terminals if i.name == t.name][0]
                        if not temp.is_reference_terminal:
                            radius = self.positive_terminal_info.contact_radius
                        else:
                            radius = self.negative_terminal_info.contact_radius
                        if radius is not None:
                            prim = self._pedb.modeler.create_circle(
                                temp.layer.name, temp.location[0], temp.location[1], radius, temp.net_name
                            )
                            prim.dcir_equipotential_region = True

                    for i in pads:
                        i._set_equipotential()

        return circuit_elements

    def export_properties(self):
        return {
            "name": self.name,
            "reference_designator": self.reference_designator,
            "type": self.type,
            "magnitude": self.magnitude,
            "positive_terminal": self.positive_terminal_info.export_properties(),
            "negative_terminal": self.negative_terminal_info.export_properties(),
        }


class CfgWavePort:
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs["name"]
        self.type = kwargs["type"]
        self.primitive_name = kwargs["primitive_name"]
        self.point_on_edge = kwargs["point_on_edge"]
        self.horizontal_extent_factor = kwargs.get("horizontal_extent_factor", 5)
        self.vertical_extent_factor = kwargs.get("vertical_extent_factor", 3)
        self.pec_launch_width = kwargs.get("pec_launch_width", "0.01mm")

    def set_parameters_to_edb(self, edb_primitives):
        point_on_edge = PointData(self._pedb, x=self.point_on_edge[0], y=self.point_on_edge[1])
        primitive = edb_primitives[self.primitive_name]
        pos_edge = self._pedb.edb_api.cell.terminal.PrimitiveEdge.Create(
            primitive._edb_object, point_on_edge._edb_object
        )
        pos_edge = convert_py_list_to_net_list(pos_edge, self._pedb.edb_api.cell.terminal.Edge)
        edge_term = self._pedb.edb_api.cell.terminal.EdgeTerminal.Create(
            primitive._edb_object.GetLayout(), primitive._edb_object.GetNet(), self.name, pos_edge, isRef=False
        )
        edge_term.SetImpedance(self._pedb.edb_value(50))
        wave_port = WavePort(self._pedb, edge_term)
        wave_port.horizontal_extent_factor = self.horizontal_extent_factor
        wave_port.vertical_extent_factor = self.vertical_extent_factor
        wave_port.pec_launch_width = self.pec_launch_width
        wave_port.hfss_type = "Wave"
        wave_port.do_renormalize = True
        return wave_port


class CfgDiffWavePort:
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs["name"]
        self.type = kwargs["type"]
        self.horizontal_extent_factor = kwargs.get("horizontal_extent_factor", 5)
        self.vertical_extent_factor = kwargs.get("vertical_extent_factor", 3)
        self.pec_launch_width = kwargs.get("pec_launch_width", "0.01mm")

        kwargs["positive_terminal"]["type"] = "wave_port"
        kwargs["positive_terminal"]["name"] = self.name + ":T1"
        self.positive_port = CfgWavePort(
            self._pedb,
            horizontal_extent_factor=self.horizontal_extent_factor,
            vertical_extent_factor=self.vertical_extent_factor,
            pec_launch_width=self.pec_launch_width,
            **kwargs["positive_terminal"],
        )
        kwargs["negative_terminal"]["type"] = "wave_port"
        kwargs["negative_terminal"]["name"] = self.name + ":T2"
        self.negative_port = CfgWavePort(
            self._pedb,
            horizontal_extent_factor=self.horizontal_extent_factor,
            vertical_extent_factor=self.vertical_extent_factor,
            pec_launch_width=self.pec_launch_width,
            **kwargs["negative_terminal"],
        )

    def set_parameters_to_edb(self, edb_primitives):
        pos_term = self.positive_port.set_parameters_to_edb(edb_primitives)
        neg_term = self.negative_port.set_parameters_to_edb(edb_primitives)
        edb_list = convert_py_list_to_net_list(
            [pos_term._edb_object, neg_term._edb_object], self._pedb.edb_api.cell.terminal.Terminal
        )
        _edb_boundle_terminal = self._pedb.edb_api.cell.terminal.BundleTerminal.Create(edb_list)
        _edb_boundle_terminal.SetName(self.name)
        pos, neg = list(_edb_boundle_terminal.GetTerminals())
        pos.SetName(self.name + ":T1")
        neg.SetName(self.name + ":T2")
