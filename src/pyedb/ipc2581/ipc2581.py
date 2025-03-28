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

import os.path

from pyedb.generic.general_methods import ET
from pyedb.ipc2581.bom.bom import Bom
from pyedb.ipc2581.bom.bom_item import BomItem
from pyedb.ipc2581.content.content import Content
from pyedb.ipc2581.ecad.cad_data.padstack_def import PadstackDef
from pyedb.ipc2581.ecad.ecad import Ecad
from pyedb.ipc2581.history_record import HistoryRecord
from pyedb.ipc2581.logistic_header import LogisticHeader


class Ipc2581(object):
    """Manages the Ipc2581 exporter."""

    def __init__(self, pedb, units):
        self.revision = "C"
        self._pedb = pedb
        self.units = units
        self.content = Content(self)
        self.logistic_header = LogisticHeader()
        self.history_record = HistoryRecord()
        self.bom = Bom(pedb)
        self.ecad = Ecad(self, pedb, units)
        self.file_path = ""
        self.design_name = ""
        self.top_bottom_layers = []

    def load_ipc_model(self):
        self.design_name = self._pedb.cell_names[0]
        self.content.step_ref = self.design_name
        self._pedb.logger.info("Parsing Layers...")
        self.add_layers_info()
        self._pedb.logger.info("Parsing BOM...")
        self.add_bom()
        self._pedb.logger.info("Parsing Padstack Definitions...")
        self.add_pdstack_definition()
        self.add_profile()
        self._pedb.logger.info("Parsing Components...")
        self.add_components()
        self._pedb.logger.info("Parsing Logical Nets...")
        self.add_logical_nets()
        self._pedb.logger.info("Parsing Layout Primitives...")
        self.add_layer_features()
        self._pedb.logger.info("Parsing Drills...")
        self.add_drills()
        self._pedb.logger.info("Parsing EDB Completed!")

    def add_pdstack_definition(self):
        for padstack_name, padstackdef in self._pedb.padstacks.definitions.items():
            padstack_def = PadstackDef()
            padstack_def.name = padstack_name
            padstack_def.padstack_hole_def.name = padstack_name
            if not self._pedb.grpc:
                if padstackdef.hole_properties:
                    padstack_def.padstack_hole_def.diameter = self.from_meter_to_units(
                        padstackdef.hole_properties[0], self.units
                    )
            else:
                padstack_def.padstack_hole_def.diameter = self.from_meter_to_units(
                    padstackdef.hole_diameter, self.units
                )
            for layer, pad in padstackdef.pad_by_layer.items():
                if pad.parameters_values:
                    if pad.geometry_type == 1:
                        primitive_ref = "CIRCLE_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units)
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_circ_dict:
                            self.content.standard_geometries_dict.standard_circ_dict[
                                primitive_ref
                            ] = self.from_meter_to_units(pad.parameters_values[0], self.units)
                    elif pad.geometry_type == 2:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_rect_dict:
                            self.content.standard_geometries_dict.standard_rect_dict[primitive_ref] = [
                                self.from_meter_to_units(pad.parameters_values[0], self.units),
                                self.from_meter_to_units(pad.parameters_values[0], self.units),
                            ]
                    elif pad.geometry_type == 3:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_rect_dict:
                            self.content.standard_geometries_dict.standard_rect_dict[primitive_ref] = [
                                self.from_meter_to_units(pad.parameters_values[0], self.units),
                                self.from_meter_to_units(pad.parameters_values[1], self.units),
                            ]

                    elif pad.geometry_type == 4:
                        primitive_ref = "OVAL_{}_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1], self.units),
                            self.from_meter_to_units(pad.parameters_values[2], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_oval_dict:
                            self.content.standard_geometries_dict.standard_oval_dict[primitive_ref] = [
                                self.from_meter_to_units(pad.parameters_values[0], self.units),
                                self.from_meter_to_units(pad.parameters_values[1], self.units),
                                self.from_meter_to_units(pad.parameters_values[2], self.units),
                            ]
                    else:
                        primitive_ref = "Default"
                    padstack_def.add_padstack_pad_def(layer=layer, pad_use="REGULAR", primitive_ref=primitive_ref)
            for layer, antipad in padstackdef.antipad_by_layer.items():
                if antipad:
                    if antipad.geometry_type == 1:
                        primitive_ref = "CIRCLE_{}".format(
                            self.from_meter_to_units(antipad.parameters_values[0], self.units)
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_circ_dict:
                            self.content.standard_geometries_dict.standard_circ_dict[
                                primitive_ref
                            ] = self.from_meter_to_units(antipad.parameters_values[0], self.units)
                    elif antipad.geometry_type == 2:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(antipad.parameters_values[0], self.units),
                            self.from_meter_to_units(antipad.parameters_values[0], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_rect_dict:
                            self.content.standard_geometries_dict.standard_rect_dict[primitive_ref] = [
                                self.from_meter_to_units(antipad.parameters_values[0], self.units),
                                self.from_meter_to_units(antipad.parameters_values[0], self.units),
                            ]
                    elif antipad.geometry_type == 3:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(antipad.parameters_values[0], self.units),
                            self.from_meter_to_units(antipad.parameters_values[1], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_rect_dict:
                            self.content.standard_geometries_dict.standard_rect_dict[primitive_ref] = [
                                self.from_meter_to_units(antipad.parameters_values[0], self.units),
                                self.from_meter_to_units(antipad.parameters_values[1], self.units),
                            ]
                    elif antipad.geometry_type == 4:
                        primitive_ref = "OVAL_{}_{}_{}".format(
                            self.from_meter_to_units(antipad.parameters_values[0], self.units),
                            self.from_meter_to_units(antipad.parameters_values[1], self.units),
                            self.from_meter_to_units(antipad.parameters_values[2], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_oval_dict:
                            self.content.standard_geometries_dict.standard_oval_dict[primitive_ref] = [
                                self.from_meter_to_units(antipad.parameters_values[0], self.units),
                                self.from_meter_to_units(antipad.parameters_values[1], self.units),
                                self.from_meter_to_units(antipad.parameters_values[2], self.units),
                            ]
                    else:
                        primitive_ref = "Default"
                    padstack_def.add_padstack_pad_def(layer=layer, pad_use="ANTIPAD", primitive_ref=primitive_ref)
            for layer, thermalpad in padstackdef.thermalpad_by_layer.items():
                if thermalpad:
                    if thermalpad.geometry_type == 1:
                        primitive_ref = "CIRCLE_{}".format(
                            self.from_meter_to_units(thermalpad.parameters_values[0], self.units)
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_circ_dict:
                            self.content.standard_geometries_dict[primitive_ref] = self.from_meter_to_units(
                                thermalpad.parameters_values[0], self.units
                            )
                    elif thermalpad.geometry_type == 2:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                            self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_rect_dict:
                            self.content.standard_geometries_dict.standard_rect_dict[primitive_ref] = [
                                self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                                self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                            ]
                    elif thermalpad.geometry_type == 3:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                            self.from_meter_to_units(thermalpad.parameters_values[1], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_rect_dict:
                            self.content.standard_geometries_dict.standard_rect_dict[primitive_ref] = [
                                self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                                self.from_meter_to_units(thermalpad.parameters_values[1], self.units),
                            ]
                    elif thermalpad.geometry_type == 4:
                        primitive_ref = "OVAL_{}_{}_{}".format(
                            self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                            self.from_meter_to_units(thermalpad.parameters_values[1], self.units),
                            self.from_meter_to_units(thermalpad.parameters_values[2], self.units),
                        )
                        if not primitive_ref in self.content.standard_geometries_dict.standard_oval_dict:
                            self.content.standard_geometries_dict.standard_oval_dict[primitive_ref] = [
                                self.from_meter_to_units(thermalpad.parameters_values[0], self.units),
                                self.from_meter_to_units(thermalpad.parameters_values[1], self.units),
                                self.from_meter_to_units(thermalpad.parameters_values[2], self.units),
                            ]
                    else:
                        primitive_ref = "Default"
                    padstack_def.add_padstack_pad_def(layer=layer, pad_use="THERMAL", primitive_ref=primitive_ref)
            if not padstack_def.name in self.ecad.cad_data.cad_data_step.padstack_defs:
                self.ecad.cad_data.cad_data_step.padstack_defs[padstack_def.name] = padstack_def

    def add_bom(self):
        # Bom
        for part_name, components in self._pedb.components.components_by_partname.items():
            bom_item = BomItem()
            bom_item.part_name = part_name
            bom_item.quantity = len(components)
            bom_item.pin_count = components[0].numpins
            bom_item.category = "ELECTRICAL"
            bom_item.charactistics.device_type = components[0].type
            bom_item.charactistics.category = "ELECTRICAL"
            bom_item.charactistics.component_class = "DISCRETE"
            if components[0].type == "Resistor":
                bom_item.charactistics.value = components[0].res_value
            elif components[0].type == "Capacitor":
                bom_item.charactistics.value = components[0].cap_value
            elif components[0].type == "Inductor":
                bom_item.charactistics.value = components[0].ind_value
            for cmp in components:
                bom_item.add_refdes(
                    component_name=cmp.refdes, placement_layer=cmp.placement_layer, package_def="", populate=True
                )
            self.bom.bom_items.append(bom_item)

    def add_layers_info(self):
        if not self._pedb.grpc:
            self.design_name = self._pedb.layout.cell.GetName()
        else:
            self.design_name = self._pedb.layout.cell.name
        self.ecad.design_name = self.design_name
        self.ecad.cad_header.units = self.units
        self.ecad.cad_data.stackup.total_thickness = self.from_meter_to_units(
            self._pedb.stackup.get_layout_thickness(), self.units
        )
        self.ecad.cad_data.stackup.stackup_group.thickness = self.ecad.cad_data.stackup.total_thickness
        self.layers_name = list(self._pedb.stackup.signal_layers.keys())
        self.top_bottom_layers = [self.layers_name[0], self.layers_name[-1]]
        sequence = 0
        for layer_name in list(self._pedb.stackup.layers.keys()):
            sequence += 1
            self.content.add_layer_ref(layer_name)
            layer_color = self._pedb.stackup.layers[layer_name].color
            self.content.dict_colors.add_color(
                "{}".format(layer_name), str(layer_color[0]), str(layer_color[1]), str(layer_color[2])
            )
            # Ecad layers
            layer_type = "CONDUCTOR"
            conductivity = 5e6
            permitivity = 1
            loss_tg = 0
            embedded = "NOT_EMBEDDED"
            # try:
            material_name = self._pedb.stackup.layers[layer_name].material
            material = self._pedb.materials[material_name]
            material_type = "CONDUCTOR"
            if self._pedb.stackup.layers[layer_name].type == "dielectric":
                layer_type = "DIELPREG"
                material_type = "DIELECTRIC"
                permitivity = material.permittivity
                loss_tg = material.loss_tangent
                conductivity = 0
            if layer_type == "CONDUCTOR":
                conductivity = material.conductivity
            self.ecad.cad_header.add_spec(
                name=layer_name,
                material=material_name,
                layer_type=material_type,
                conductivity=str(conductivity),
                dielectric_constant=str(permitivity),
                loss_tg=str(loss_tg),
                embedded=embedded,
            )
            layer_position = "INTERNAL"
            if layer_name == self.top_bottom_layers[0]:
                layer_position = "TOP"
            if layer_name == self.top_bottom_layers[1]:
                layer_position = "BOTTOM"
            self.ecad.cad_data.add_layer(
                layer_name=layer_name, layer_function=layer_type, layer_side=layer_position, polarity="POSITIVE"
            )
            layer_thickness_with_units = self.from_meter_to_units(
                self._pedb.stackup.layers[layer_name].thickness, self.units
            )
            self.ecad.cad_data.stackup.stackup_group.add_stackup_layer(
                layer_name=layer_name, thickness=layer_thickness_with_units, sequence=str(sequence)
            )
            # except:
            #    pass
        self.ecad.cad_data.add_layer(layer_name="Drill", layer_function="DRILL", layer_side="ALL", polarity="POSITIVE")
        self.content.add_layer_ref("Drill")
        self.content.dict_colors.add_color("{}".format("Drill"), "255", "255", "255")

    def add_components(self):
        for item in self._pedb.components.instances.values():
            self.ecad.cad_data.cad_data_step.add_component(item)

    def add_logical_nets(self):
        nets = [i for i in self._pedb.nets.nets.values()]
        for net in nets:
            self.ecad.cad_data.cad_data_step.add_logical_net(net)

    def add_profile(self):
        profile = self._pedb.modeler.primitives_by_layer.get("Outline")
        if profile is None:
            self._pedb.logger.warning("Layer 'Outline' not found.")
        else:
            profile = self._pedb.modeler.primitives_by_layer["Outline"]
            for prim in profile:
                self.ecad.cad_data.cad_data_step.add_profile(prim)

    def add_layer_features(self):
        layers = {i: j for i, j in self._pedb.stackup.layers.items()}
        padstack_instances = list(self._pedb.padstacks.instances.values())
        padstack_defs = {i: k for i, k in self._pedb.padstacks.definitions.items()}
        polys = {i: j for i, j in self._pedb.modeler.primitives_by_layer.items()}
        for layer_name, layer in layers.items():
            self.ecad.cad_data.cad_data_step.add_layer_feature(layer, polys[layer_name])
        self.ecad.cad_data.cad_data_step.add_padstack_instances(padstack_instances, padstack_defs)

    def add_drills(self):
        via_list = [
            obj for obj in list(self._pedb.padstacks.instances.values()) if not obj.start_layer == obj.stop_layer
        ]
        l1 = len(list(self._pedb.stackup.signal_layers.keys()))

        self.ecad.cad_data.cad_data_step.add_drill_layer_feature(via_list, "DRILL_1-{}".format(l1))

    def from_meter_to_units(self, value, units):
        if value:
            if isinstance(value, str):
                value = float(value)
            if isinstance(value, list):
                returned_list = []
                for val in value:
                    if isinstance(val, str):
                        val = float(val)
                    if units.lower() == "mm":
                        returned_list.append(round(val * 1000, 4))
                    if units.lower() == "um":
                        returned_list.append(round(val * 1e6, 4))
                    if units.lower() == "mils":
                        returned_list.append(round(val * 39370.079, 4))
                    if units.lower() == "inch":
                        returned_list.append(round(val * 39.370079, 4))
                    if units.lower() == "cm":
                        returned_list.append(round(val * 100, 4))
                return returned_list
            else:
                if units.lower() == "millimeter":
                    return round(value * 1000, 4)
                if units.lower() == "micrometer":
                    return round(value * 1e6, 4)
                if units.lower() == "mils":
                    return round(value * 39370.079, 4)
                if units.lower() == "inch":
                    return round(value * 39.370079, 4)
                if units.lower() == "centimeter":
                    return round(value * 100, 4)

    def write_xml(self):
        if self.file_path:
            ipc = ET.Element("IPC-2581")
            ipc.set("revision", self.revision)
            ipc.set("xmlns", "http://webstds.ipc.org/2581")
            ipc.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            ipc.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
            self.content.write_wml(ipc)
            self.logistic_header.write_xml(ipc)
            self.history_record.write_xml(ipc)
            self.bom.write_xml(ipc)
            self.ecad.write_xml(ipc)
            try:
                ET.indent(ipc)
            except AttributeError:
                pass
            tree = ET.ElementTree(ipc)
            tree.write(self.file_path)
            return True if os.path.exists(self.file_path) else False
