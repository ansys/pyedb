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
from datetime import datetime
import json
import os
from pathlib import Path
import warnings

import toml

from pyedb import Edb
from pyedb.configuration.cfg_data import CfgData


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

        # Configure boundary settings
        if self.cfg_data.boundaries:
            self.__apply_with_logging("Updating boundaries", self.cfg_data.boundaries.apply)

        if self.cfg_data.nets:
            self.__apply_with_logging("Updating nets", self.cfg_data.nets.apply)

        self.__apply_with_logging("Updating components", self.cfg_data.components.apply)
        self.__apply_with_logging("Creating pin groups", self.cfg_data.pin_groups.apply)
        self.__apply_with_logging("Placing sources", self.cfg_data.sources.apply)
        self.__apply_with_logging("Creating setups", self.cfg_data.setups.apply)

        self.__apply_with_logging("Applying materials", self.apply_materials)
        self.__apply_with_logging("Updating stackup", self.apply_stackup)

        if self.cfg_data.padstacks:
            self.__apply_with_logging("Applying padstacks", self.cfg_data.padstacks.apply)

        self.__apply_with_logging("Applying S-parameters", self.cfg_data.s_parameters.apply)

        for spice_model in self.cfg_data.spice_models:
            self.__apply_with_logging(f"Assigning Spice model {spice_model}", spice_model.apply)

        self.__apply_with_logging("Applying package definitions", self.cfg_data.package_definitions.apply)
        self.__apply_with_logging("Applying modeler", self.apply_modeler)
        self.__apply_with_logging("Placing ports", self.cfg_data.ports.apply)
        self.__apply_with_logging("Placing probes", self.cfg_data.probes.apply)
        self.__apply_with_logging("Applying operations", self.cfg_data.operations.apply)

        return True

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
                p.pyedb_obj = pdef
                p.api.set_parameters_to_edb()

        if modeler.padstack_instances:
            for p in modeler.padstack_instances:
                p_inst = self._pedb.padstacks.place(
                    via_name=p.name,
                    net_name=p.net_name,
                    position=p.position,
                    definition_name=p.definition,
                    rotation=p.rotation if p.rotation is not None else 0,
                )
                p.pyedb_obj = p_inst
                p.api.set_parameters_to_edb()

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
                c.api.set_parameters_to_edb()

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

    def get_data_from_db(self, **kwargs):
        """Get configuration data from layout.

        Parameters
        ----------
        stackup

        Returns
        -------

        """
        self._pedb.logger.info("Getting data from layout database.")
        self.get_variables()
        self.get_materials()
        self.get_stackup()

        data = {}
        if kwargs.get("general", False):
            data["general"] = self.cfg_data.general.get_data_from_db()
        if kwargs.get("variables", False):
            data["variables"] = self.cfg_data.variables.model_dump(exclude_none=True)
        if kwargs.get("stackup", False):
            data["stackup"] = self.cfg_data.stackup.model_dump(exclude_none=True)
        if kwargs.get("package_definitions", False):
            data["package_definitions"] = self.cfg_data.package_definitions.get_data_from_db()
        if kwargs.get("setups", False):
            setups = self.cfg_data.setups
            setups.retrieve_parameters_from_edb()
            data["setups"] = setups.to_dict()
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
            data["operations"] = self.cfg_data.operations.get_data_from_db()
        if kwargs.get("padstacks", False):
            self.cfg_data.padstacks.retrieve_parameters_from_edb()
            definitions = []
            for i in self.cfg_data.padstacks.definitions:
                definitions.append(i.get_attributes())
            instances = []
            for i in self.cfg_data.padstacks.instances:
                instances.append(i.get_attributes())
            data["padstacks"] = dict()
            data["padstacks"]["definitions"] = definitions
            data["padstacks"]["instances"] = instances

        if kwargs.get("boundaries", False):
            data["boundaries"] = self.cfg_data.boundaries.get_data_from_db()

        return data

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
            Whether to export sources or not.
        ports : bool
            Whether to export ports or not.
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
