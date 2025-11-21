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

import numpy as np

from pyedb.configuration.cfg_common import CfgBase
from pyedb.dotnet.database.cell.primitive.primitive import Primitive
from pyedb.dotnet.database.edb_data.ports import WavePort
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.point_data import PointData


class CfgTerminalInfo(CfgBase):
    CFG_TERMINAL_TYPES = ["pin", "net", "pin_group", "nearest_pin", "coordinates"]

    def update_contact_radius(self, radius):
        self.contact_radius = self._pedb.edb_value(radius).ToDouble()

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb

        if kwargs.get("padstack"):
            self.type = "padstack"
        elif "pin" in kwargs:
            self.type = "pin"
        elif "net" in kwargs:
            self.type = "net"
        elif "pin_group" in kwargs:
            self.type = "pin_group"
        elif "nearest_pin" in kwargs:
            self.type = "nearest_pin"
        elif "coordinates" in kwargs:
            self.type = "coordinates"
        else:  # pragma no cover
            raise RuntimeError
        self.value = kwargs[self.type]
        self.reference_designator = kwargs.get("reference_designator")

        self.contact_type = kwargs.get("contact_type", "default")  # options are full, center, quad, inline
        contact_radius = "0.1mm" if kwargs.get("contact_radius") is None else kwargs.get("contact_radius")

        self.contact_radius = self._pedb.value(contact_radius)
        self.num_of_contact = kwargs.get("num_of_contact", 4)
        self.contact_expansion = kwargs.get("contact_expansion", 1)

    def export_properties(self):
        return {self.type: self.value}


class CfgCoordinateTerminalInfo(CfgTerminalInfo):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

        self.layer = self.value["layer"]
        self.point_x = self.value["point"][0]
        self.point_y = self.value["point"][1]
        self.net = self.value["net"]

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
    def get_pin_group_name(self, src):
        return src._edb_object.GetPinGroup().GetName()

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
                pg = self._pedb.siwave.pin_groups[self.get_pin_group_name(src)]
                pos_term_info = {"pin_group": pg.name}
            elif src.terminal_type == "PadstackInstanceTerminal":
                refdes = src.component.refdes if src.component else ""
                pos_term_info = {"padstack": src.padstack_instance.aedt_name}

            neg_term = self._pedb.terminals[src.ref_terminal.name]
            if neg_term.terminal_type == "PinGroupTerminal":
                pg = self._pedb.siwave.pin_groups[self.get_pin_group_name(neg_term)]
                neg_term_info = {"pin_group": pg.name}
            elif neg_term.terminal_type == "PadstackInstanceTerminal":
                neg_term_info = {"padstack": neg_term.padstack_instance.aedt_name}

            cfg_src = CfgSource(
                self._pedb,
                name=name,
                type=src_type,
                impedance=src.impedance,
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
    def get_pin_group(self, port):
        return self._pedb.siwave.pin_groups[port._edb_object.GetPinGroup().GetName()]

    def _get_edge_port_from_edb(self, p, port_type):
        _, primitive, point = p._edb_object.GetEdges()[0].GetParameters()

        primitive = Primitive(self._pedb, primitive)
        point = PointData(self._pedb, point)

        cfg_port = CfgEdgePort(
            self._pedb,
            name=p.name,
            type=port_type,
            primitive_name=primitive.aedt_name,
            point_on_edge=[point._edb_object.X.ToString(), point._edb_object.Y.ToString()],
            horizontal_extent_factor=p.horizontal_extent_factor,
            vertical_extent_factor=p.vertical_extent_factor,
            pec_launch_width=p.pec_launch_width,
        )
        return cfg_port

    def __init__(self, pedb, ports_data):
        self._pedb = pedb
        self.ports = []
        for p in ports_data:
            if p["type"] == "wave_port":
                self.ports.append(CfgEdgePort(self._pedb, **p))
            elif p["type"] == "gap_port":
                self.ports.append(CfgEdgePort(self._pedb, **p))
            elif p["type"] == "diff_wave_port":
                self.ports.append(CfgDiffWavePort(self._pedb, **p))
            elif p["type"] in ["coax", "circuit"]:
                self.ports.append(CfgPort(self._pedb, **p))
            else:
                raise ValueError("Unknown port type")

    def apply(self):
        for p in self.ports:
            p.set_parameters_to_edb()

    def get_data_from_db(self):
        self.ports = []
        ports = {name: t for name, t in self._pedb.terminals.items() if not t.is_reference_terminal}
        ports = {name: t for name, t in ports.items() if t.is_port}

        for _, p in ports.items():
            if not p.ref_terminal:
                if p.terminal_type == "PadstackInstanceTerminal":
                    port_type = "coax"
                elif p.terminal_type == "PinGroupTerminal":
                    port_type = "circuit"
                elif p.terminal_type == "EdgeTerminal":
                    port_type = "wave_port" if p.hfss_type == "Wave" else "gap_port"
                else:
                    raise ValueError("Unknown terminal type")
            else:
                port_type = "circuit"

            if p.terminal_type == "PinGroupTerminal":
                refdes = ""
                pg = self.get_pin_group(p)
                pos_term_info = {"pin_group": pg.name}
            elif p.terminal_type == "PadstackInstanceTerminal":
                refdes = p.component.refdes if p.component else ""
                pos_term_info = {"padstack": p.padstack_instance.aedt_name}
            elif p.terminal_type == "PointTerminal":
                refdes = ""
                pos_term_info = {"coordinates": {"layer": p.layer.name, "point": p.location, "net": p.net.name}}

            if port_type == "circuit":
                neg_term = self._pedb.terminals[p.ref_terminal.name]
                if neg_term.terminal_type == "PinGroupTerminal":
                    pg = self.get_pin_group(neg_term)
                    # pg = self._pedb.siwave.pin_groups[neg_term._edb_object.GetPinGroup().GetName()]
                    neg_term_info = {"pin_group": pg.name}
                elif neg_term.terminal_type == "PadstackInstanceTerminal":
                    neg_term_info = {"padstack": neg_term.padstack_instance.aedt_name}
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
                    impedance=p.impedance,
                    reference_designator=refdes,
                    positive_terminal=pos_term_info,
                    negative_terminal=neg_term_info,
                )
            elif port_type == "coax":
                cfg_port = CfgPort(
                    self._pedb,
                    name=p.name,
                    type=port_type,
                    impedance=p.impedance,
                    reference_designator=refdes,
                    positive_terminal=pos_term_info,
                )
            else:
                cfg_port = self._get_edge_port_from_edb(p, port_type)
            self.ports.append(cfg_port)
        return self.export_properties()

    def export_properties(self):
        ports = []
        for p in self.ports:
            ports.append(p.export_properties())
        return ports


class CfgProbes:
    def __init__(self, pedb, data):
        self._pedb = pedb
        self.probes = [CfgProbe(self._pedb, **probe) for probe in data]

    def apply(self):
        for probe in self.probes:
            probe.set_parameters_to_edb()


class CfgCircuitElement(CfgBase):
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs["name"]
        self.type = kwargs["type"]
        self.impedance = kwargs.get("impedance", None)
        self.reference_designator = kwargs.get("reference_designator", None)
        self.distributed = kwargs.get("distributed", False)
        self._elem_num = 1

        pos = kwargs["positive_terminal"]  # {"pin" : "A1"}
        if list(pos.keys())[0] == "coordinates":
            self.positive_terminal_info = CfgCoordinateTerminalInfo(self._pedb, **pos)
        else:
            self.positive_terminal_info = CfgTerminalInfo(self._pedb, **pos)
            if not self.positive_terminal_info.reference_designator:
                self.positive_terminal_info.reference_designator = self.reference_designator

        neg = kwargs.get("negative_terminal", {})
        if len(neg) == 0:
            self.negative_terminal_info = None
        elif list(neg.keys())[0] == "coordinates":
            self.negative_terminal_info = CfgCoordinateTerminalInfo(self._pedb, **neg)
        elif list(neg.keys())[0] == "nearest_pin":
            self.negative_terminal_info = CfgNearestPinTerminalInfo(self._pedb, **neg)
        else:
            self.negative_terminal_info = CfgTerminalInfo(self._pedb, **neg)
            if not self.negative_terminal_info.reference_designator:
                self.negative_terminal_info.reference_designator = self.positive_terminal_info.reference_designator

    def create_terminals(self):
        """Create step 1. Collect positive and negative terminals."""

        # Collect all positive terminals
        pos_type, pos_value = self.positive_terminal_info.type, self.positive_terminal_info.value
        pos_objs = dict()
        pos_coor_terminal = dict()
        if self.type == "coax":
            pins = self._get_pins(pos_type, pos_value, self.positive_terminal_info.reference_designator)
            if len(pins) < 2:
                pins = {f"{self.name}": i for _, i in pins.items()}
            else:
                pins = {f"{self.name}_{name}": i for name, i in pins.items()}
                self.distributed = True
            pos_objs.update(pins)
        elif pos_type == "coordinates":
            layer = self.positive_terminal_info.layer
            point = [self.positive_terminal_info.point_x, self.positive_terminal_info.point_y]
            net_name = self.positive_terminal_info.net
            if net_name not in self._pedb.nets:
                self._pedb.nets.find_or_create_net(net_name)
            pos_coor_terminal[self.name] = self._pedb.get_point_terminal(self.name, net_name, point, layer)

        elif pos_type == "padstack":
            flag = False
            for pds in self._pedb.layout.padstack_instances:
                if pds.aedt_name == pos_value:
                    pos_objs.update({pos_value: pds})
                    flag = True
                    break
            if flag is False:
                raise ValueError(f"Padstack instance {pos_value} does not exist")
        elif pos_type == "pin":
            pins = {
                pos_value: self._pedb.components.instances[self.positive_terminal_info.reference_designator].pins[
                    pos_value
                ]
            }
            if self.positive_terminal_info.contact_type in ["quad", "inline"]:
                for _, pin in pins.items():
                    contact_type = self.positive_terminal_info.contact_type
                    radius = self.positive_terminal_info.contact_radius
                    num_of_contact = self.positive_terminal_info.num_of_contact
                    contact_expansion = self.positive_terminal_info.contact_expansion

                    virtual_pins = self._create_virtual_pins_on_pin(
                        pin, contact_type, radius, num_of_contact, contact_expansion
                    )
                    pos_objs.update(virtual_pins)
                    self._elem_num = len(pos_objs)
            else:
                pos_objs.update(pins)
        elif pos_type == "pin_group":
            if self.distributed:
                pins = self._get_pins(pos_type, pos_value, self.positive_terminal_info.reference_designator)
                pos_objs.update(pins)
                self._elem_num = len(pos_objs)
            elif self.positive_terminal_info.contact_type in ["quad", "inline"]:
                pins = self._get_pins(pos_type, pos_value, self.positive_terminal_info.reference_designator)
                for _, pin in pins.items():
                    contact_type = self.positive_terminal_info.contact_type
                    radius = self.positive_terminal_info.contact_radius
                    num_of_contact = self.positive_terminal_info.num_of_contact
                    contact_expansion = self.positive_terminal_info.contact_expansion

                    virtual_pins = self._create_virtual_pins_on_pin(
                        pin, contact_type, radius, num_of_contact, contact_expansion
                    )
                    pos_objs.update(virtual_pins)
                    self._elem_num = len(pos_objs)
            else:
                pos_objs[pos_value] = self._pedb.siwave.pin_groups[pos_value]
        elif pos_type == "net":
            pins = self._get_pins(pos_type, pos_value, self.positive_terminal_info.reference_designator)
            if self.distributed:
                pos_objs.update(pins)
                self._elem_num = len(pos_objs)
            elif self.positive_terminal_info.contact_type in ["quad", "inline"]:
                for _, pin in pins.items():
                    contact_type = self.positive_terminal_info.contact_type
                    radius = self.positive_terminal_info.contact_radius
                    num_of_contact = self.positive_terminal_info.num_of_contact
                    contact_expansion = self.positive_terminal_info.contact_expansion

                    virtual_pins = self._create_virtual_pins_on_pin(
                        pin, contact_type, radius, num_of_contact, contact_expansion
                    )
                    pos_objs.update(virtual_pins)
                    self._elem_num = len(pos_objs)
            else:
                # create pin group
                neg_obj = self._create_pin_group(pins, self.positive_terminal_info.reference_designator)
                pos_objs.update(neg_obj)
        else:
            raise Exception(f"Wrong positive terminal type {pos_type}.")

        self.pos_terminals = {i: j.create_terminal(i) for i, j in pos_objs.items()}
        self.pos_terminals.update(pos_coor_terminal)

        # Collect all negative terminals
        self.neg_terminal = None
        if self.negative_terminal_info:
            neg_type, neg_value = self.negative_terminal_info.type, self.negative_terminal_info.value

            if neg_type == "coordinates":
                layer = self.negative_terminal_info.layer
                point = [self.negative_terminal_info.point_x, self.negative_terminal_info.point_y]
                net_name = self.negative_terminal_info.net
                if net_name not in self._pedb.nets:
                    self._pedb.nets.find_or_create_net(net_name)
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
                    pins = self._get_pins(
                        neg_type, neg_value, self.negative_terminal_info.reference_designator
                    )  # terminal type pin or net
                    # create pin group
                    neg_obj = self._create_pin_group(pins, self.negative_terminal_info.reference_designator, True)
                elif neg_type == "padstack":
                    for pds in self._pedb.layout.padstack_instances:
                        if pds.aedt_name == neg_value:
                            neg_obj = {neg_value: pds}
                            break
                elif neg_type == "pin":
                    terminal_name = f"{self.negative_terminal_info.reference_designator}_{neg_value}"
                    neg_obj = {
                        terminal_name: self._pedb.components.instances[
                            self.negative_terminal_info.reference_designator
                        ].pins[neg_value]
                    }
                else:
                    raise Exception(f"Wrong negative terminal type {neg_type}.")
                neg_term = [j.create_terminal(i) if not j.terminal else j.terminal for i, j in neg_obj.items()][0]
                self.neg_terminal = neg_term

    def _get_pins(self, terminal_type, terminal_value, reference_designator):
        terminal_value = terminal_value if isinstance(terminal_value, list) else [terminal_value]

        def get_pin_obj(pin_name):
            return {pin_name: self._pedb.components.instances[reference_designator].pins[pin_name]}

        pins = dict()
        if terminal_type == "pin":
            for i in terminal_value:
                pins.update(get_pin_obj(i))
        elif terminal_type == "padstack":
            for i in self._pedb.layout.find_padstack_instances(aedt_name=terminal_value):
                pins[i.component_pin] = i
        else:
            if terminal_type == "net":
                temp = self._pedb.components.get_pins(reference_designator, terminal_value[0])
            elif terminal_type == "pin_group":
                pin_group = self._pedb.siwave.pin_groups[terminal_value[0]]
                temp = pin_group.pins
            else:
                temp = {}
            pins.update({f"{reference_designator}_{terminal_value[0]}_{i}": j for i, j in temp.items()})
        return pins

    def _create_virtual_pins_on_pin(self, pin, contact_type, radius, num_of_contact=4, expansion=1):
        component = pin.component
        placement_layer = component.placement_layer
        pos_x, pos_y = pin.position
        comp_rotation = self._pedb.edb_value(component.rotation).ToDouble() % 3.141592653589793

        pad = pin.definition.pad_by_layer[placement_layer]
        if pad.shape.lower() in ["rectangle", "oval"]:
            width, height = pad.parameters_values[0:2]
        elif pad.shape.lower() == "nogeometry":
            polygon_data = pad.polygon_data
            if polygon_data:
                p1, p2 = polygon_data.bounding_box
                width = p2[0] - p1[0]
                height = p2[1] - p1[1]
            else:
                raise AttributeError(f"Unsupported pad shape {pad.shape.lower()}")
        else:  # pragma no cover
            raise AttributeError(f"Unsupported pad shape {pad.shape.lower()}")

        width = width * expansion
        height = height * expansion

        positions = []
        if contact_type.lower() == "inline":
            if width > height:
                offset = (width - radius * 2) / (num_of_contact - 1)
            else:
                offset = (height - radius * 2) / (num_of_contact - 1)

            start_pos = (num_of_contact - 1) / 2
            offset = [offset * i for i in np.arange(start_pos * -1, start_pos + 1)]

            if (width > height and comp_rotation == 0) or (width < height and comp_rotation != 0):
                positions.extend(list(zip(offset, [0] * num_of_contact)))
            else:
                positions.extend(list(zip([0] * num_of_contact, offset)))
        else:  # quad
            x_offset = width / 2 - radius if comp_rotation == 0 else height / 2 - radius
            y_offset = height / 2 - radius if comp_rotation == 0 else width / 2 - radius

            for x, y in [[1, 1], [-1, 1], [1, -1], [-1, -1]]:
                positions.append([x_offset * x, y_offset * y])

        pdef_name = f"{self.name}_{pin.pin_number}"
        self._pedb.padstacks.create(padstackname=pdef_name, has_hole=False, paddiam=radius * 2, antipaddiam=0)
        instances = {}
        for idx, xy in enumerate(positions):
            x = xy[0] + pos_x
            y = xy[1] + pos_y
            pin_name = f"{pdef_name}_{idx}"
            p_inst = self._pedb.padstacks.place(
                position=[x, y],
                definition_name=pdef_name,
                net_name=pin.net_name,
                via_name=pin_name,
                fromlayer=placement_layer,
                tolayer=placement_layer,
                is_pin=True,
            )
            instances[pin_name] = p_inst
        self._pedb.components.create(
            pins=list(instances.values()),
        )
        return instances

    def _create_pin_group(self, pins, reference_designator, is_ref=False):
        if is_ref:
            pg_name = f"pg_{self.name}_{reference_designator}_ref"
        else:
            pg_name = f"pg_{self.name}_{reference_designator}"
        pin_names = [i.component_pin for i in pins.values()]
        name, temp = self._pedb.siwave.create_pin_group(reference_designator, pin_names, pg_name)
        return {name: temp}


class CfgPort(CfgCircuitElement):
    """Manage port."""

    CFG_PORT_TYPE = {"circuit": [str], "coax": [str]}

    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

    def set_parameters_to_edb(self):
        """Create port."""
        self.create_terminals()
        is_circuit_port = True if self.type == "circuit" else False
        circuit_elements = []
        for name, j in self.pos_terminals.items():
            if isinstance(self.neg_terminal, dict):
                elem = self._pedb.create_port(j, self.neg_terminal[name], is_circuit_port)
            else:
                elem = self._pedb.create_port(j, self.neg_terminal, is_circuit_port)
            elem.impedance = self.impedance if self.impedance else self._pedb.edb_value(50)
            if not self.distributed:
                elem.name = self.name
            circuit_elements.append(elem)
        return circuit_elements

    def export_properties(self):
        data = {
            "name": self.name,
            "type": self.type,
            "impedance": self.impedance,
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

    def set_parameters_to_edb(self):
        """Create sources."""
        self.create_terminals()
        # is_circuit_port = True if self.type == "circuit" else False
        circuit_elements = []
        create_xxx_source = (
            self._pedb.create_current_source if self.type == "current" else self._pedb.create_voltage_source
        )
        for name, j in self.pos_terminals.items():
            if isinstance(self.neg_terminal, dict):
                elem = create_xxx_source(j, self.neg_terminal[name])
            else:
                elem = create_xxx_source(j, self.neg_terminal)

            if self.impedance:
                elem.impedance = self.impedance
            else:
                elem.impedance = 5e7 if self.type == "current" else 1e-6

            if self._elem_num == 1:
                elem.name = self.name
                elem.magnitude = self.magnitude
            else:
                elem.name = name
                elem.magnitude = self.magnitude / self._elem_num
            elem = self._pedb.terminals[elem.name]
            circuit_elements.append(elem)

        for terminal in circuit_elements:
            # Get reference terminal
            terms = [terminal, terminal.ref_terminal] if terminal.ref_terminal else [terminal]
            for t in terms:
                if not t.is_reference_terminal:
                    radius = self.positive_terminal_info.contact_radius
                    contact_type = self.positive_terminal_info.contact_type
                else:
                    radius = self.negative_terminal_info.contact_radius
                    contact_type = self.negative_terminal_info.contact_type
                if t.terminal_type == "PointTerminal":
                    temp = [i for i in self._pedb.layout.terminals if i.name == t.name][0]
                    prim = self._pedb.modeler.create_circle(
                        temp.layer.name, temp.location[0], temp.location[1], radius, temp.net_name
                    )
                    prim.dcir_equipotential_region = True
                    continue
                elif contact_type.lower() == "default":
                    continue
                elif t.terminal_type == "PadstackInstanceTerminal":
                    if contact_type.lower() in ["full", "quad", "inline"]:
                        t.padstack_instance._set_equipotential()
                    elif contact_type.lower() == "center":
                        t.padstack_instance._set_equipotential(contact_radius=radius)
                elif t.terminal_type == "PinGroupTerminal":
                    name = t._edb_object.GetPinGroup().GetName()
                    pg = self._pedb.siwave.pin_groups[name]
                    pads = [i for _, i in pg.pins.items()]
                    for i in pads:
                        if contact_type.lower() in ["full", "quad", "inline"]:
                            i._set_equipotential()
                        elif contact_type.lower() == "center":
                            i._set_equipotential(contact_radius=radius)
                        elif t.is_reference_terminal:
                            continue
                else:
                    raise AttributeError("Unsupported terminal type.")

        return circuit_elements

    def export_properties(self):
        return {
            "name": self.name,
            "reference_designator": self.reference_designator,
            "type": self.type,
            "impedance": self.impedance,
            "magnitude": self.magnitude,
            "positive_terminal": self.positive_terminal_info.export_properties(),
            "negative_terminal": self.negative_terminal_info.export_properties(),
        }


class CfgProbe(CfgCircuitElement):
    def set_parameters_to_edb(self):
        self.create_terminals()
        circuit_elements = []
        for name, j in self.pos_terminals.items():
            if isinstance(self.neg_terminal, dict):
                elem = self._pedb.create_voltage_probe(j, self.neg_terminal[name])
            else:
                elem = self._pedb.create_voltage_probe(j, self.neg_terminal)
            elem.name = self.name
            circuit_elements.append(elem)
        return circuit_elements

    def __init__(self, pedb, **kwargs):
        kwargs["type"] = "probe"
        super().__init__(pedb, **kwargs)


class CfgEdgePort:
    def set_parameters_to_edb(self):
        point_on_edge = PointData.create_from_xy(self._pedb, x=self.point_on_edge[0], y=self.point_on_edge[1])
        primitive = self._pedb.layout.primitives_by_aedt_name[self.primitive_name]
        pos_edge = self._pedb.core.Cell.Terminal.PrimitiveEdge.Create(primitive._edb_object, point_on_edge._edb_object)
        pos_edge = convert_py_list_to_net_list(pos_edge, self._pedb.core.Cell.Terminal.Edge)
        edge_term = self._pedb.core.Cell.Terminal.EdgeTerminal.Create(
            primitive._edb_object.GetLayout(),
            primitive._edb_object.GetNet(),
            self.name,
            pos_edge,
            isRef=False,
        )
        edge_term.SetImpedance(self._pedb.edb_value(50))
        wave_port = WavePort(self._pedb, edge_term)
        wave_port.horizontal_extent_factor = self.horizontal_extent_factor
        wave_port.vertical_extent_factor = self.vertical_extent_factor
        wave_port.pec_launch_width = self.pec_launch_width
        if self.type == "wave_port":
            wave_port.hfss_type = "Wave"
        else:
            wave_port.hfss_type = "Gap"
        wave_port.do_renormalize = True
        return wave_port

    def export_properties(self):
        return {
            "name": self.name,
            "type": self.type,
            "primitive_name": self.primitive_name,
            "point_on_edge": self.point_on_edge,
            "horizontal_extent_factor": self.horizontal_extent_factor,
            "vertical_extent_factor": self.vertical_extent_factor,
            "pec_launch_width": self.pec_launch_width,
        }

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs["name"]
        self.type = kwargs["type"]
        self.primitive_name = kwargs["primitive_name"]
        self.point_on_edge = kwargs["point_on_edge"]
        self.horizontal_extent_factor = kwargs.get("horizontal_extent_factor", 5)
        self.vertical_extent_factor = kwargs.get("vertical_extent_factor", 3)
        self.pec_launch_width = kwargs.get("pec_launch_width", "0.01mm")


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
        self.positive_port = CfgEdgePort(
            self._pedb,
            horizontal_extent_factor=self.horizontal_extent_factor,
            vertical_extent_factor=self.vertical_extent_factor,
            pec_launch_width=self.pec_launch_width,
            **kwargs["positive_terminal"],
        )
        kwargs["negative_terminal"]["type"] = "wave_port"
        kwargs["negative_terminal"]["name"] = self.name + ":T2"
        self.negative_port = CfgEdgePort(
            self._pedb,
            horizontal_extent_factor=self.horizontal_extent_factor,
            vertical_extent_factor=self.vertical_extent_factor,
            pec_launch_width=self.pec_launch_width,
            **kwargs["negative_terminal"],
        )

    def set_parameters_to_edb(self):
        pos_term = self.positive_port.set_parameters_to_edb()
        neg_term = self.negative_port.set_parameters_to_edb()
        edb_list = convert_py_list_to_net_list(
            [pos_term._edb_object, neg_term._edb_object], self._pedb.core.Cell.Terminal.Terminal
        )
        _edb_boundle_terminal = self._pedb.core.Cell.Terminal.BundleTerminal.Create(edb_list)
        _edb_boundle_terminal.SetName(self.name)
        pos, neg = list(_edb_boundle_terminal.GetTerminals())
        pos.SetName(self.name + ":T1")
        neg.SetName(self.name + ":T2")
