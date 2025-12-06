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
from datetime import datetime
import json
import os
from pathlib import Path
import warnings

import toml

from pyedb import Edb
from pyedb.configuration.cfg_data import CfgData
from pyedb.misc.decorators import execution_timer


def set_padstack_definition(pdef, pdef_obj):
    if pdef.hole_parameters:
        pdef_obj.set_hole_parameters(pdef.hole_parameters)
    if pdef.hole_range:
        pdef_obj.hole_range = pdef.hole_range
    if pdef.hole_plating_thickness:
        pdef_obj.hole_plating_thickness = pdef.hole_plating_thickness
    if pdef.material:
        pdef_obj.material = pdef.material
    if pdef.pad_parameters:
        pdef_obj.set_pad_parameters(pdef.pad_parameters)
    if pdef.solder_ball_parameters:
        pdef_obj.set_solder_parameters(pdef.solder_ball_parameters)


def set_padstack_instance(inst, inst_obj):
    inst_obj.is_pin = inst.is_pin
    if inst.name is not None:
        inst_obj.aedt_name = inst.name
    if inst.net_name is not None:
        inst_obj.net_name = inst_obj._pedb.nets.find_or_create_net(inst.net_name).name
    if inst.layer_range is not None:
        inst_obj.start_layer = inst.layer_range[0]
    if inst.layer_range is not None:
        inst_obj.stop_layer = inst.layer_range[1]
    if inst.backdrill_parameters:
        inst_obj.backdrill_parameters = inst.backdrill_parameters.model_dump(exclude_none=True)
    if inst.solder_ball_layer:
        inst_obj._edb_object.SetSolderBallLayer(inst_obj._pedb.stackup[inst.solder_ball_layer]._edb_object)

    hole_override_enabled, hole_override_diam = inst_obj._edb_object.GetHoleOverrideValue()
    hole_override_enabled = inst.hole_override_enabled if inst.hole_override_enabled else hole_override_enabled
    hole_override_diam = inst.hole_override_diameter if inst.hole_override_diameter else hole_override_diam
    inst_obj._edb_object.SetHoleOverride(hole_override_enabled, inst_obj._pedb.edb_value(hole_override_diam))


class Configuration:
    """Enables export and import of a JSON configuration file that can be applied to a new or existing design."""

    def __init__(self, pedb: Edb):
        self._pedb = pedb

        self._components = self._pedb.components.instances
        self.data = {}
        self._s_parameter_library = ""
        self._spice_model_library = ""
        self.cfg_data = CfgData(self._pedb)

    def __apply_with_logging(self, label: str, func):
        start = datetime.now()
        func()
        self._pedb.logger.info(f"{label} finished. Time lapse {datetime.now() - start}")

    def load(self, config_file, append=True, apply_file=False, output_file=None, open_at_the_end=True):
        """Import configuration settings from a configure file.

        Parameters
        ----------
        config_file : str, dict
            Full path to configure file in JSON or TOML format. Dictionary is also supported.
        append : bool, optional
            Whether if the new file will append to existing properties or the properties will be cleared before import.
            Default is ``True`` to keep stored properties
        apply_file : bool, optional
            Whether to apply the file after the load or not. Default is ``False``.
        output_file : str, optional
            Full path to the new aedb folder where the configured project will be saved.
        open_at_the_end : bool, optional
            Whether to keep the new generated file opened at the end. Default is ``True``.

        Returns
        -------
        dict
            Config dictionary.
        """
        if isinstance(config_file, dict):
            data = config_file
        else:
            config_file = str(config_file)
            if os.path.isfile(config_file):
                with open(config_file, "r") as f:
                    if config_file.endswith(".json"):
                        data = json.load(f)
                    elif config_file.endswith(".toml"):
                        data = toml.load(f)
            else:  # pragma: no cover
                raise RuntimeError(f"File {config_file} does not exist.")

        if not append:  # pragma: no cover
            self.data = {}
        for k, v in data.items():
            if k in self.data:
                if isinstance(v, list):
                    self.data[k].extend(v)
                elif isinstance(v, dict):  # pragma: no cover
                    self.data[k].update(v)
                else:  # pragma: no cover
                    self.data[k] = v
            else:
                self.data[k] = v

        self.cfg_data = CfgData(self._pedb, **self.data)

        if apply_file:
            original_file = self._pedb.edbpath
            if output_file:
                self._pedb.save_edb_as(output_file)
            self.run()
            if output_file and not open_at_the_end:
                self._pedb.save_edb()
                self._pedb.close_edb()
                self._pedb.edbpath = original_file
                self._pedb.open_edb()
        return self.cfg_data

    def run(self, **kwargs):
        """Apply configuration settings to the current design"""
        if kwargs.get("fix_padstack_def"):
            warnings.warn("fix_padstack_def is deprecated.", DeprecationWarning)

        self.apply_variables()

        if self.cfg_data.general:
            self.cfg_data.general.apply()

        self.apply_boundaries()

        if self.cfg_data.nets:
            self.__apply_with_logging("Updating nets", self.cfg_data.nets.apply)

        self.__apply_with_logging("Updating components", self.cfg_data.components.apply)
        self.__apply_with_logging("Creating pin groups", self.cfg_data.pin_groups.apply)
        self.__apply_with_logging("Placing sources", self.cfg_data.sources.apply)

        self.__apply_with_logging("Applying materials", self.apply_materials)
        self.__apply_with_logging("Updating stackup", self.apply_stackup)

        self.apply_padstacks()

        self.__apply_with_logging("Applying S-parameters", self.cfg_data.s_parameters.apply)

        for spice_model in self.cfg_data.spice_models:
            self.__apply_with_logging(f"Assigning Spice model {spice_model}", spice_model.apply)

        self.__apply_with_logging("Applying package definitions", self.cfg_data.package_definitions.apply)
        self.__apply_with_logging("Applying modeler", self.apply_modeler)
        self.__apply_with_logging("Placing ports", self.cfg_data.ports.apply)
        self.apply_terminals()
        self.__apply_with_logging("Placing probes", self.cfg_data.probes.apply)
        self.apply_operations()
        self.cfg_data.setups.apply()

        return True

    def apply_boundaries(self):
        boundaries = self.cfg_data.boundaries
        info = self._pedb.hfss.hfss_extent_info

        # Simple direct-assign attributes:
        attr_map = [
            "use_open_region",
            "open_region_type",
            "is_pml_visible",
            "operating_freq",
            "radiation_level",
            "dielectric_extent_type",
            "honor_user_dielectric",
            "extent_type",
            "truncate_air_box_at_ground",
            "base_polygon",
            "dielectric_base_polygon",
            "sync_air_box_vertical_extent",
        ]

        for b_attr in attr_map:
            if not hasattr(info, b_attr) or not hasattr(boundaries, b_attr):
                self._pedb.logger.error(f"Attribute {b_attr} not found")
                raise AttributeError(f"Attribute {b_attr} not found")
            value = getattr(boundaries, b_attr, None)
            if value is not None:
                setattr(info, b_attr, value)

        # Attributes requiring specific setter functions
        if boundaries.dielectric_extent_size:
            info.set_dielectric_extent(**boundaries.dielectric_extent_size.model_dump())

        if boundaries.air_box_horizontal_extent:
            info.set_air_box_horizontal_extent(**boundaries.air_box_horizontal_extent.model_dump())

        if boundaries.air_box_positive_vertical_extent:
            info.set_air_box_positive_vertical_extent(**boundaries.air_box_positive_vertical_extent.model_dump())

        if boundaries.air_box_negative_vertical_extent:
            info.set_air_box_negative_vertical_extent(**boundaries.air_box_negative_vertical_extent.model_dump())

    def get_boundaries(self):
        boundaries = self.cfg_data.boundaries
        edb_hfss_extent_info = self._pedb.hfss.hfss_extent_info

        boundaries.use_open_region = edb_hfss_extent_info.use_open_region
        boundaries.open_region_type = edb_hfss_extent_info.open_region_type
        boundaries.is_pml_visible = edb_hfss_extent_info.is_pml_visible
        boundaries.operating_freq = edb_hfss_extent_info.operating_freq
        boundaries.radiation_level = edb_hfss_extent_info.radiation_level
        boundaries.dielectric_extent_type = edb_hfss_extent_info.dielectric_extent_type
        size, is_multiple = edb_hfss_extent_info.get_dielectric_extent()
        boundaries.dielectric_extent_size = {"size": size, "is_multiple": is_multiple}
        boundaries.honor_user_dielectric = edb_hfss_extent_info.honor_user_dielectric
        boundaries.extent_type = edb_hfss_extent_info.extent_type
        boundaries.truncate_air_box_at_ground = edb_hfss_extent_info.truncate_air_box_at_ground
        size, is_multiple = edb_hfss_extent_info.get_air_box_horizontal_extent()
        boundaries.air_box_horizontal_extent = {"size": size, "is_multiple": is_multiple}
        size, is_multiple = edb_hfss_extent_info.get_air_box_positive_vertical_extent()
        boundaries.air_box_positive_vertical_extent = {"size": size, "is_multiple": is_multiple}
        size, is_multiple = edb_hfss_extent_info.get_air_box_negative_vertical_extent()
        boundaries.air_box_negative_vertical_extent = {"size": size, "is_multiple": is_multiple}
        boundaries.base_polygon = edb_hfss_extent_info.base_polygon
        boundaries.dielectric_base_polygon = edb_hfss_extent_info.dielectric_base_polygon
        boundaries.sync_air_box_vertical_extent = edb_hfss_extent_info.sync_air_box_vertical_extent

    def apply_modeler(self):
        modeler = self.cfg_data.modeler
        if modeler.traces:
            for t in modeler.traces:
                if t.path:
                    obj = self._pedb.modeler.create_trace(
                        path_list=t.path,
                        layer_name=t.layer,
                        net_name=t.net_name,
                        width=t.width,
                        start_cap_style=t.start_cap_style,
                        end_cap_style=t.end_cap_style,
                        corner_style=t.corner_style,
                    )
                    obj.aedt_name = t.name
                else:
                    obj = self._pedb.modeler.create_trace(
                        path_list=[t.incremental_path[0]],
                        layer_name=t.layer,
                        net_name=t.net_name,
                        width=t.width,
                        start_cap_style=t.start_cap_style,
                        end_cap_style=t.end_cap_style,
                        corner_style=t.corner_style,
                    )
                    obj.aedt_name = t.name
                    for x, y in t.incremental_path[1:]:
                        obj.add_point(x, y, True)

        if modeler.padstack_defs:
            for p in modeler.padstack_defs:
                pdata = self._pedb._edb.Definition.PadstackDefData.Create()
                pdef = self._pedb._edb.Definition.PadstackDef.Create(self._pedb.active_db, p.name)
                pdef.SetData(pdata)
                pdef = self._pedb.pedb_class.database.edb_data.padstacks_data.EDBPadstack(pdef, self._pedb.padstacks)
                set_padstack_definition(p, pdef)

        if modeler.padstack_instances:
            for p in modeler.padstack_instances:
                p_inst = self._pedb.padstacks.place(
                    via_name=p.name,
                    net_name=p.net_name,
                    position=p.position,
                    definition_name=p.definition,
                    rotation=p.rotation if p.rotation is not None else 0,
                )
                set_padstack_instance(p, p_inst)

        if modeler.planes:
            for p in modeler.planes:
                if p.type == "rectangle":
                    obj = self._pedb.modeler.create_rectangle(
                        layer_name=p.layer,
                        net_name=p.net_name,
                        lower_left_point=p.lower_left_point,
                        upper_right_point=p.upper_right_point,
                        corner_radius=p.corner_radius,
                        rotation=p.rotation,
                    )
                    obj.aedt_name = p.name
                elif p.type == "polygon":
                    obj = self._pedb.modeler.create_polygon(
                        main_shape=p.points, layer_name=p.layer, net_name=p.net_name
                    )
                    obj.aedt_name = p.name
                elif p.type == "circle":
                    obj = self._pedb.modeler.create_circle(
                        layer_name=p.layer,
                        net_name=p.net_name,
                        x=p.position[0],
                        y=p.position[1],
                        radius=p.radius,
                    )
                    obj.aedt_name = p.name
                else:
                    raise RuntimeError(f"Plane type {p.type} not supported")

                for v in p.voids:
                    for i in self._pedb.layout.primitives:
                        if i.aedt_name == v:
                            self._pedb.modeler.add_void(obj, i)

        if modeler.components:
            for c in modeler.components:
                obj = self._pedb.components.create(
                    c.pins,
                    component_name=c.reference_designator,
                    placement_layer=c.placement_layer,
                    component_part_name=c.definition,
                )
                c.pyedb_obj = obj
                c.set_parameters_to_edb()

        if len([i for i in modeler.primitives_to_delete.values() if len(i) > 0]):
            primitives = self._pedb.layout.find_primitive(**modeler.primitives_to_delete)
            for i in primitives:
                i.delete()

    def apply_variables(self):
        """Set variables into database."""
        inst = self.cfg_data.variables
        for i in inst.variables:
            if i.name.startswith("$"):
                self._pedb.add_project_variable(i.name, i.value, i.description)
            else:
                self._pedb.add_design_variable(i.name, i.value, description=i.description)

    def get_variables(self):
        """Retrieve variables from database."""
        self.cfg_data.variables.variables = []
        for name, obj in self._pedb.design_variables.items():
            self.cfg_data.variables.add_variable(name, obj.value_string, obj.description)
        for name, obj in self._pedb.project_variables.items():
            self.cfg_data.variables.add_variable(name, obj.value_string, obj.description)

    def apply_materials(self):
        """Apply material settings to the current design"""
        cfg_stackup = self.cfg_data.stackup
        if len(cfg_stackup.materials):
            materials_in_db = {i.lower(): i for i, _ in self._pedb.materials.materials.items()}
            for mat_in_cfg in cfg_stackup.materials:
                if mat_in_cfg.name.lower() in materials_in_db:
                    self._pedb.materials.delete_material(materials_in_db[mat_in_cfg.name.lower()])

                attrs = mat_in_cfg.model_dump(exclude_none=True)
                mat = self._pedb.materials.add_material(**attrs)

                for i in attrs.get("thermal_modifiers", []):
                    mat.set_thermal_modifier(**i.to_dict())

    def get_materials(self):
        """Retrieve materials from the current design.

        Parameters
        ----------
        append: bool, optional
            If `True`, append materials to the current material list.
        """

        self.cfg_data.stackup.materials = []
        for name, mat in self._pedb.materials.materials.items():
            self.cfg_data.stackup.add_material(**mat.to_dict())

    def apply_stackup(self):
        layers = self.cfg_data.stackup.layers
        input_signal_layers = [i for i in layers if i.type.lower() == "signal"]
        if len(input_signal_layers) == 0:
            return
        else:  # Create materials with default properties used in stackup but not defined
            materials = [m.name for m in self.cfg_data.stackup.materials]
            for i in self.cfg_data.stackup.layers:
                if i.type == "signal":
                    if i.material not in materials:
                        self.cfg_data.stackup.add_material(
                            name=i.material, **self._pedb.materials.default_conductor_property_values
                        )

                    if i.fill_material not in materials:
                        self.cfg_data.stackup.add_material(
                            name=i.material, **self._pedb.materials.default_dielectric_property_values
                        )

                elif i.type == "dielectric":
                    if i.material not in materials:
                        self.cfg_data.stackup.add_material(
                            name=i.material, **self._pedb.materials.default_dielectric_property_values
                        )

        if len(self._pedb.stackup.signal_layers) == 0:
            self.__create_stackup()
        elif not len(input_signal_layers) == len(self._pedb.stackup.signal_layers):
            raise Exception(f"Input signal layer count do not match.")
        else:
            self.__update_stackup()

    def __create_stackup(self):
        layers_ = list()
        layers_.extend(self.cfg_data.stackup.layers)
        for l_attrs in layers_:
            attrs = l_attrs.model_dump(exclude_none=True)
            self._pedb.stackup.add_layer_bottom(**attrs)

    def __update_stackup(self):
        """Apply layer settings to the current design"""

        # After import stackup, padstacks lose their definitions. They need to be fixed after loading stackup
        # step 1, archive padstack definitions
        temp_pdef_data = {}
        for pdef_name, pdef in self._pedb.padstacks.definitions.items():
            pdef_edb_object = pdef._padstack_def_data
            temp_pdef_data[pdef_name] = pdef_edb_object
        # step 2, archive padstack instance layer map
        temp_p_inst_layer_map = {}
        for p_inst in self._pedb.layout.padstack_instances:
            temp_p_inst_layer_map[p_inst.id] = p_inst._edb_object.GetLayerMap()

        # ----------------------------------------------------------------------
        # Apply stackup
        layers = list()
        layers.extend(self.cfg_data.stackup.layers)

        removal_list = []
        lc_signal_layers = []
        for name, obj in self._pedb.stackup.all_layers.items():
            if obj.type == "dielectric":
                removal_list.append(name)
            elif obj.type == "signal":
                lc_signal_layers.append(obj.id)
        for l in removal_list:
            self._pedb.stackup.remove_layer(l)

        # update all signal layers
        id_name = {i[0]: i[1] for i in self._pedb.stackup.layers_by_id}
        signal_idx = 0
        for l in layers:
            if l.type == "signal":
                layer_id = lc_signal_layers[signal_idx]
                layer_name = id_name[layer_id]
                attrs = l.model_dump(exclude_none=True)
                self._pedb.stackup.layers[layer_name].update(**attrs)
                signal_idx = signal_idx + 1

        # add all dielectric layers. Dielectric layers must be added last. Otherwise,
        # dielectric layer will occupy signal and document layer id.
        l = layers.pop(0)
        if l.type == "signal":
            prev_layer_clone = self._pedb.stackup.layers[l.name]
        else:
            attrs = l.model_dump(exclude_none=True)
            prev_layer_clone = self._pedb.stackup.add_layer_top(**attrs)
        for idx, l in enumerate(layers):
            if l.type == "dielectric":
                attrs = l.model_dump(exclude_none=True)
                prev_layer_clone = self._pedb.stackup.add_layer_below(base_layer_name=prev_layer_clone.name, **attrs)
            elif l.type == "signal":
                prev_layer_clone = self._pedb.stackup.layers[l.name]

        # ----------------------------------------------------------------------
        # restore padstack definitions
        for pdef_name, pdef_data in temp_pdef_data.items():
            pdef = self._pedb.padstacks.definitions[pdef_name]
            pdef._padstack_def_data = pdef_data
        # restore padstack instance layer map
        for p_inst in self._pedb.layout.padstack_instances:
            p_inst._edb_object.SetLayerMap(temp_p_inst_layer_map[p_inst.id])

    def get_stackup(self):
        self.cfg_data.stackup.layers = []
        for name, obj in self._pedb.stackup.all_layers.items():
            self.cfg_data.stackup.add_layer_at_bottom(**obj.properties)

    def get_padstacks(self):
        padstacks = self.cfg_data.padstacks
        padstacks.clean()

        for name, obj in self._pedb.padstacks.definitions.items():
            if name.lower() == "symbol":
                continue
            padstacks.add_padstack_definition(
                name=obj.name,
                hole_plating_thickness=obj.hole_plating_thickness,
                material=obj.material,
                hole_range=obj.hole_range,
                pad_parameters=obj.get_pad_parameters(),
                hole_parameters=obj.get_hole_parameters(),
                solder_ball_parameters=obj.get_solder_parameters(),
            )

        for obj in self._pedb.layout.padstack_instances:
            _, position, rotation = obj._edb_object.GetPositionAndRotationValue()
            hole_override_enabled, hole_override_diameter = obj._edb_object.GetHoleOverrideValue()
            padstacks.add_padstack_instance(
                name=obj.aedt_name,
                is_pin=obj.is_pin,
                definition=obj.padstack_definition,
                backdrill_parameters=obj.backdrill_parameters,
                position=[position.X.ToString(), position.Y.ToString()],
                rotation=rotation.ToString(),
                eid=obj.id,
                hole_override_enabled=hole_override_enabled,
                hole_override_diameter=hole_override_diameter.ToString(),
                solder_ball_layer=obj._edb_object.GetSolderBallLayer().GetName(),
                layer_range=[obj.start_layer, obj.stop_layer],
            )

    @execution_timer("Applying padstack definitions and instances")
    def apply_padstacks(self):
        padstacks = self.cfg_data.padstacks

        for pdef in padstacks.definitions:
            pdef_obj = self._pedb.padstacks.definitions[pdef.name]
            set_padstack_definition(pdef, pdef_obj)

        for inst in padstacks.instances:
            inst_obj = self._pedb.padstacks.instances_by_name[inst.name]
            set_padstack_instance(inst, inst_obj)

    def get_data_from_db(self, **kwargs):
        """Get configuration data from layout.

        Parameters
        ----------
        stackup

        Returns
        -------

        """
        self._pedb.logger.info("Getting data from layout database.")

        self.get_materials()

        data = {}
        if kwargs.get("general", False):
            data["general"] = self.cfg_data.general.get_data_from_db()
        if kwargs.get("variables", False):
            self.get_variables()
            data.update(self.cfg_data.variables.model_dump(exclude_none=True))
        if kwargs.get("stackup", False):
            self.get_stackup()
            data["stackup"] = self.cfg_data.stackup.model_dump(exclude_none=True)
        if kwargs.get("package_definitions", False):
            data["package_definitions"] = self.cfg_data.package_definitions.get_data_from_db()
        if kwargs.get("setups", False):
            setups = self.cfg_data.setups
            setups.retrieve_parameters_from_edb()
            data["setups"] = setups.to_dict()
        if kwargs.get("terminals", False):
            self.get_terminals()
            data.update(self.cfg_data.terminals.model_dump(exclude_none=True))
        if kwargs.get("sources", False):
            data["sources"] = self.cfg_data.sources.get_data_from_db()
        if kwargs.get("ports", False):
            data["ports"] = self.cfg_data.ports.get_data_from_db()
        if kwargs.get("components", False) or kwargs.get("s_parameters", False):
            self.cfg_data.components.retrieve_parameters_from_edb()
            components = []
            for i in self.cfg_data.components.components:
                if i.type == "io":
                    components.append(i.get_attributes())
                components.append(i.get_attributes())

            if kwargs.get("components", False):
                data["components"] = components
            elif kwargs.get("s_parameters", False):
                data["s_parameters"] = self.cfg_data.s_parameters.get_data_from_db(components)
        if kwargs.get("nets", False):
            data["nets"] = self.cfg_data.nets.get_data_from_db()
        if kwargs.get("pin_groups", False):
            data["pin_groups"] = self.cfg_data.pin_groups.get_data_from_db()
        if kwargs.get("operations", False):
            self.get_operations()
            data["operations"] = self.cfg_data.operations.model_dump()
        if kwargs.get("padstacks", False):
            self.get_padstacks()
            data["padstacks"] = self.cfg_data.padstacks.model_dump(exclude_none=True)

        if kwargs.get("boundaries", False):
            self.get_boundaries()
            data["boundaries"] = self.cfg_data.boundaries.model_dump(exclude_none=True)
        return data

    @execution_timer("Applying operations")
    def apply_operations(self):
        """Apply operations to the current design."""
        op_cutout = self.cfg_data.operations.cutout
        if op_cutout:
            cutout_params = op_cutout.model_dump()
            auto_identify_nets = cutout_params.pop("auto_identify_nets")
            if auto_identify_nets["enabled"]:
                reference_list = cutout_params.get("reference_list", [])
                if auto_identify_nets:
                    self._pedb.nets.generate_extended_nets(
                        auto_identify_nets["resistor_below"],
                        auto_identify_nets["inductor_below"],
                        auto_identify_nets["capacitor_above"],
                        auto_identify_nets.get("exception_list", []),
                    )
                    signal_nets = []
                    for i in self._pedb.terminals.values():
                        if i.net_name in reference_list:
                            continue

                        extended_net = i.net.extended_net
                        if extended_net:
                            temp = [i2 for i2 in extended_net.nets.keys() if i2 not in reference_list]
                            temp = [i2 for i2 in temp if i2 not in signal_nets]
                            signal_nets.extend(temp)
                        else:
                            signal_nets.append(i.net_name)

                    cutout_params["signal_list"] = signal_nets
            polygon_points = self._pedb.cutout(**cutout_params)
            if "pyedb_cutout" not in self._pedb.stackup.all_layers:
                self._pedb.stackup.add_document_layer(name="pyedb_cutout")
                self._pedb.modeler.create_polygon(polygon_points, layer_name="pyedb_cutout", net_name="pyedb_cutout")

    def get_operations(self):
        if "pyedb_cutout" not in self._pedb.stackup.all_layers:
            return

        polygons = self._pedb.layout.find_primitive(layer_name="pyedb_cutout")
        if polygons:
            poly = polygons[0]
            custom_extent = poly.polygon_data.points
            net_names = []
            for name, obj in self._pedb.nets.nets.items():
                if obj.primitives:
                    if obj.primitives[0].layer.name == "pyedb_cutout":
                        continue
                    else:
                        net_names.append(name)
            reference_list = []
            signal_list = net_names

            self.cfg_data.operations.add_cutout(
                custom_extent=custom_extent,
                reference_list=reference_list,
                signal_list=signal_list,
            )

    @execution_timer("Placing terminals")
    def apply_terminals(self):
        terminals_dict = {}
        bungle_terminals = []
        edge_terminals = {}
        for cfg_terminal in self.cfg_data.terminals.terminals:
            if cfg_terminal.terminal_type == "padstack_instance":
                terminal = self._pedb.source_excitation.create_padstack_instance_terminal(
                    name=cfg_terminal.name,
                    padstack_instance_id=cfg_terminal.padstack_instance_id,
                    padstack_instance_name=cfg_terminal.padstack_instance,
                )

            elif cfg_terminal.terminal_type == "pin_group":
                terminal = self._pedb.source_excitation.create_pin_group_terminal(
                    name=cfg_terminal.name,
                    pin_group=cfg_terminal.pin_group,
                )
            elif cfg_terminal.terminal_type == "point":
                terminal = self._pedb.source_excitation.create_point_terminal(
                    name=cfg_terminal.name,
                    net=cfg_terminal.net,
                    x=cfg_terminal.x,
                    y=cfg_terminal.y,
                    layer=cfg_terminal.layer,
                )
            elif cfg_terminal.terminal_type == "edge":
                terminal = self._pedb.source_excitation.create_edge_terminal(
                    primitive_name=cfg_terminal.primitive,
                    x=cfg_terminal.point_on_edge_x,
                    y=cfg_terminal.point_on_edge_y,
                    name=cfg_terminal.name,
                )

                terminal.horizontal_extent_factor = cfg_terminal.horizontal_extent_factor
                terminal.vertical_extent_factor = cfg_terminal.vertical_extent_factor
                terminal.pec_launch_width = cfg_terminal.pec_launch_width
                terminal.do_renormalize = True
                edge_terminals[cfg_terminal.name] = terminal
            elif cfg_terminal.terminal_type == "bundle":
                bungle_terminals.append(cfg_terminal)
                continue
            else:
                self._pedb.logger.warning(f"Terminal type {cfg_terminal.terminal_type} not supported.")
                continue

            terminal.impedance = cfg_terminal.impedance
            terminal.is_circuit_port = cfg_terminal.is_circuit_port
            terminal.boundary_type = cfg_terminal.boundary_type
            terminal.source_amplitude = cfg_terminal.amplitude
            terminal.source_phase = cfg_terminal.phase
            terminal.terminal_to_ground = cfg_terminal.terminal_to_ground

            terminals_dict[cfg_terminal.name] = cfg_terminal, terminal

        for _, obj in terminals_dict.items():
            cfg, obj = obj
            if cfg.reference_terminal:
                obj.reference_terminal = terminals_dict[cfg.reference_terminal][1]

        for i in bungle_terminals:
            self._pedb.source_excitation.create_bundle_terminal(terminals=i.terminals, name=i.name)

    @execution_timer("Retrieving terminal information")
    def get_terminals(self):
        manager = self.cfg_data.terminals
        manager.terminals = []
        for i in self._pedb.terminals.values():
            if i.terminal_type == "PadstackInstanceTerminal":
                manager.add_padstack_instance_terminal(
                    padstack_instance=i.padstack_instance.aedt_name,
                    padstack_instance_id=i.padstack_instance.id,
                    name=i.name,
                    impedance=i.impedance,
                    is_circuit_port=i.is_circuit_port,
                    boundary_type=i.boundary_type,
                    amplitude=i.source_amplitude,
                    phase=i.source_phase,
                    terminal_to_ground=i.terminal_to_ground,
                    reference_terminal=i.reference_terminal.name if i.reference_terminal else None,
                    hfss_type=i.hfss_type if i.hfss_type else "Wave",
                )
            elif i.terminal_type == "PinGroupTerminal":
                manager.add_pin_group_terminal(
                    pin_group=i.pin_group().name,
                    name=i.name,
                    impedance=i.impedance,
                    boundary_type=i.boundary_type,
                    reference_terminal=i.reference_terminal.name if i.reference_terminal else None,
                    amplitude=i.source_amplitude,
                    phase=i.source_phase,
                    terminal_to_ground=i.terminal_to_ground,
                )
            elif i.terminal_type == "PointTerminal":
                manager.add_point_terminal(
                    x=i.location[0],
                    y=i.location[1],
                    layer=i.layer.name,
                    name=i.name,
                    impedance=i.impedance,
                    boundary_type=i.boundary_type,
                    reference_terminal=i.reference_terminal.name if i.reference_terminal else None,
                    amplitude=i.source_amplitude,
                    phase=i.source_phase,
                    terminal_to_ground=i.terminal_to_ground,
                    net=i.net_name,
                )
            elif i.terminal_type == "EdgeTerminal":
                pass
            elif i.terminal_type == "BundleTerminal":
                pass
            else:  # pragma: no cover
                raise RuntimeError(f"Terminal type {i.terminal_type} not supported.")

    def export(
        self,
        file_path,
        stackup=True,
        package_definitions=False,
        setups=True,
        sources=True,
        ports=True,
        nets=True,
        pin_groups=True,
        operations=True,
        components=True,
        boundaries=True,
        s_parameters=True,
        padstacks=True,
        general=True,
        variables=True,
        terminals=False,
    ):
        """Export the configuration data from layout to a file.

        Parameters
        ----------
        file_path : str, Path
            File path to export the configuration data.
        stackup : bool
            Whether to export stackup or not.
        package_definitions : bool
            Whether to export package definitions or not.
        setups : bool
            Whether to export setups or not.
        sources : bool
            Whether to export sources or not. Alternative to terminals.
        ports : bool
            Whether to export ports or not. Alternative to terminals.
        nets : bool
            Whether to export nets.
        pin_groups : bool
            Whether to export pin groups.
        operations : bool
            Whether to export operations.
        components : bool
            Whether to export component.
        boundaries : bool
            Whether to export boundaries.
        s_parameters : bool
            Whether to export s_parameters.
        padstacks : bool
            Whether to export padstacks.
        general : bool
            Whether to export general information.
        variables : bool
            Whether to export variable.
        terminals : bool
            Whether to export terminals. Alternative to ports and sources.
        Returns
        -------
        bool
        """
        data = self.get_data_from_db(
            stackup=stackup,
            package_definitions=package_definitions,
            setups=setups,
            sources=sources,
            ports=ports,
            nets=nets,
            pin_groups=pin_groups,
            operations=operations,
            components=components,
            boundaries=boundaries,
            s_parameters=s_parameters,
            padstacks=padstacks,
            general=general,
            variables=variables,
            terminals=terminals,
        )

        file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        file_path = file_path.with_suffix(".json") if file_path.suffix == "" else file_path

        for comp in data["components"]:
            for key, value in comp.items():
                try:
                    json.dumps(value)
                    print(f"Key '{key}' is serializable.")
                except TypeError as e:
                    print(f"Key '{key}' failed: {e}")

        with open(file_path, "w") as f:
            if file_path.suffix == ".json":
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                toml.dump(data, f)
        return True if os.path.isfile(file_path) else False
