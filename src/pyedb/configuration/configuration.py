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

import json
import os
from pathlib import Path

import toml

from pyedb.configuration.cfg_data import CfgData
from pyedb.dotnet.edb_core.definition.package_def import PackageDef
from pyedb.dotnet.edb_core.stackup import LayerCollection
from pyedb.generic.general_methods import pyedb_function_handler


class Configuration:
    """Enables export and import of a JSON configuration file that can be applied to a new or existing design."""

    def __init__(self, pedb):
        self._pedb = pedb
        self._components = self._pedb.components.components
        self.data = {}
        self._s_parameter_library = ""
        self._spice_model_library = ""
        self.cfg_data = CfgData(self._pedb)

    @pyedb_function_handler
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
        elif os.path.isfile(config_file):
            with open(config_file, "r") as f:
                if config_file.endswith(".json"):
                    data = json.load(f)
                elif config_file.endswith(".toml"):
                    data = toml.load(f)
        else:  # pragma: no cover
            return False

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

        self.cfg_data = CfgData(self._pedb, **data)

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

    @pyedb_function_handler()
    def run(self):
        """Apply configuration settings to the current design"""

        # Configure boundary settings
        if self.cfg_data.boundaries:
            self.cfg_data.boundaries.apply()

        # Configure nets
        if self.cfg_data.nets:
            self.cfg_data.nets.apply()

        # Configure components
        if self.cfg_data.components:
            for comp in self.cfg_data.components:
                comp.apply()

        # Configure padstacks
        if self.cfg_data.padstacks:
            self.cfg_data.padstacks.apply()

        # Configure pin groups
        for pin_group in self.cfg_data.pin_groups:
            pin_group.apply()

        # Configure ports
        for port in self.cfg_data.ports:
            port.create()

        # Configure sources
        """if "sources" in self.data:
            self._load_sources()"""
        for source in self.cfg_data.sources:
            source.create()

        # Configure HFSS setup
        for setup in self.cfg_data.setups:
            setup.apply()

        # Configure stackup
        if "stackup" in self.data:
            self._load_stackup()

        # Configure S-parameter
        if "s_parameters" in self.data:
            self._load_s_parameter()

        # Configure SPICE models
        for spice_model in self.cfg_data.spice_models:
            spice_model.apply()

        # Configure package definitions
        if "package_definitions" in self.data:
            self._load_package_def()

        # Configure operations
        if "operations" in self.data:
            self._load_operations()

        return True

    @pyedb_function_handler
    def _load_sources(self):
        """Imports source information from json."""

        for src in self.data["sources"]:
            src_type = src["type"]
            name = src["name"]

            positive_terminal_json = src["positive_terminal"]
            if "pin_group" in positive_terminal_json:
                pin_group = self._pedb.siwave.pin_groups[positive_terminal_json["pin_group"]]
                pos_terminal = pin_group.get_terminal(pin_group.name, True)
            else:
                ref_designator = src["reference_designator"]
                comp_layout = self._components[ref_designator]

                if "pin" in positive_terminal_json:
                    pin_name = positive_terminal_json["pin"]
                    src_name = name
                    pos_terminal = comp_layout.pins[pin_name].get_terminal(src_name, True)
                elif "net" in positive_terminal_json:  # Net
                    net_name = positive_terminal_json["net"]
                    src_name = "{}_{}".format(ref_designator, net_name)
                    pg_name = "pg_{}".format(src_name)
                    _, pg = self._pedb.siwave.create_pin_group_on_net(ref_designator, net_name, pg_name)
                    pos_terminal = pg.get_terminal(src_name, True)

            negative_terminal_json = src["negative_terminal"]
            if "pin_group" in negative_terminal_json:
                pin_group = self._pedb.siwave.pin_groups[negative_terminal_json["pin_group"]]
                neg_terminal = pin_group.get_terminal(pin_group.name + "_ref", True)
            else:
                ref_designator = src["reference_designator"]
                comp_layout = self._components[ref_designator]
                if "pin" in negative_terminal_json:
                    pin_name = negative_terminal_json["pin"]
                    src_name = name + "_ref"
                    neg_terminal = comp_layout.pins[pin_name].get_terminal(src_name, True)
                elif "net" in negative_terminal_json:
                    net_name = negative_terminal_json["net"]
                    src_name = name + "_ref"
                    pg_name = "pg_{}".format(src_name)
                    if pg_name not in self._pedb.siwave.pin_groups:
                        _, pg = self._pedb.siwave.create_pin_group_on_net(ref_designator, net_name, pg_name)
                    else:  # pragma no cover
                        pg = self._pedb.siwave.pin_groups[pg_name]
                    neg_terminal = pg.get_terminal(src_name, True)

            if src_type == "voltage":
                src_obj = self._pedb.create_voltage_source(pos_terminal, neg_terminal)
                src_obj.magnitude = src["magnitude"]
            elif src_type == "current":
                src_obj = self._pedb.create_current_source(pos_terminal, neg_terminal)
                src_obj.magnitude = src["magnitude"]
            src_obj.name = name

    @pyedb_function_handler
    def _load_stackup(self):
        """Imports stackup information from json."""
        data = self.data["stackup"]
        materials = data.get("materials")

        if materials:
            edb_materials = {i.lower(): i for i, _ in self._pedb.materials.materials.items()}
            for mat in materials:
                name = mat["name"].lower()
                if name in edb_materials:
                    self._pedb.materials.delete_material(edb_materials[name])
            for mat in materials:
                self._pedb.materials.add_material(**mat)

        layers = data.get("layers")

        if layers:
            lc = self._pedb.stackup
            input_signal_layers = [i for i in layers if i["type"].lower() == "signal"]
            if not len(input_signal_layers) == len(lc.signal_layers):
                self._pedb.logger.error("Input signal layer count do not match.")
                return False

            layer_clones = []
            doc_layer_clones = []
            for name, obj in lc.layers.items():
                if obj.is_stackup_layer:
                    if obj.type == "signal":  # keep signal layers
                        layer_clones.append(obj)
                else:
                    doc_layer_clones.append(obj)

            lc_new = LayerCollection(self._pedb)
            lc_new.auto_refresh = False
            signal_layer_ids = {}
            top_layer_clone = None

            # add all signal layers
            for l in layers:
                if l["type"] == "signal":
                    clone = layer_clones.pop(0)
                    clone.update(**l)
                    lc_new.add_layer_bottom(name=clone.name, layer_clone=clone)
                    signal_layer_ids[clone.name] = clone.id

            # add all document layers at bottom
            for l in doc_layer_clones:
                doc_layer = lc_new.add_document_layer(name=l.name, layer_clone=l)
                first_doc_layer_name = doc_layer.name

            # add all dielectric layers. Dielectric layers must be added last. Otherwise,
            # dielectric layer will occupy signal and document layer id.
            prev_layer_clone = None
            l = layers.pop(0)
            if l["type"] == "signal":
                prev_layer_clone = lc_new.layers[l["name"]]
            else:
                prev_layer_clone = lc_new.add_layer_top(**l)
            for idx, l in enumerate(layers):
                if l["type"] == "dielectric":
                    prev_layer_clone = lc_new.add_layer_below(base_layer_name=prev_layer_clone.name, **l)
                else:
                    prev_layer_clone = lc_new.layers[l["name"]]

            lc._edb_object = lc_new._edb_object
            lc_new.auto_refresh = True
            lc.update_layout()

    @pyedb_function_handler
    def _load_s_parameter(self):
        """Imports s-parameter information from json."""

        for sp in self.data["s_parameters"]:
            fpath = sp["file_path"]
            if not Path(fpath).anchor:
                fpath = str(Path(self._s_parameter_library) / fpath)
            sp_name = sp["name"]
            comp_def_name = sp["component_definition"]
            comp_def = self._pedb.definitions.component[comp_def_name]
            comp_def.add_n_port_model(fpath, sp_name)
            comp_list = dict()
            if sp["apply_to_all"]:
                comp_list.update(
                    {refdes: comp for refdes, comp in comp_def.components.items() if refdes not in sp["components"]}
                )
            else:
                comp_list.update(
                    {refdes: comp for refdes, comp in comp_def.components.items() if refdes in sp["components"]}
                )

            for refdes, comp in comp_list.items():
                if "reference_net_per_component" in sp:
                    ref_net_per_comp = sp["reference_net_per_component"]
                    ref_net = ref_net_per_comp[refdes] if refdes in ref_net_per_comp else sp["reference_net"]
                else:
                    ref_net = sp["reference_net"]
                comp.use_s_parameter_model(sp_name, reference_net=ref_net)

    @pyedb_function_handler
    def _load_operations(self):
        """Imports operation information from JSON."""
        operations = self.data["operations"]
        cutout = operations.get("cutout", None)
        if cutout:
            self._pedb.cutout(**cutout)

    @pyedb_function_handler
    def _load_package_def(self):
        """Imports package definition information from JSON."""
        comps = self._pedb.components.components
        for pkgd in self.data["package_definitions"]:
            name = pkgd["name"]
            if name in self._pedb.definitions.package:
                self._pedb.definitions.package[name].delete()
            extent_bounding_box = pkgd.get("extent_bounding_box", None)
            if extent_bounding_box:
                package_def = PackageDef(self._pedb, name=name, extent_bounding_box=extent_bounding_box)
            else:
                package_def = PackageDef(self._pedb, name=name, component_part_name=pkgd["component_definition"])
            package_def.maximum_power = pkgd["maximum_power"]
            package_def.therm_cond = pkgd["therm_cond"]
            package_def.theta_jb = pkgd["theta_jb"]
            package_def.theta_jc = pkgd["theta_jc"]
            package_def.height = pkgd["height"]

            heatsink = pkgd.get("heatsink", None)
            if heatsink:
                package_def.set_heatsink(
                    heatsink["fin_base_height"],
                    heatsink["fin_height"],
                    heatsink["fin_orientation"],
                    heatsink["fin_spacing"],
                    heatsink["fin_thickness"],
                )

            comp_def_name = pkgd["component_definition"]
            comp_def = self._pedb.definitions.component[comp_def_name]

            comp_list = dict()
            if pkgd["apply_to_all"]:
                comp_list.update(
                    {refdes: comp for refdes, comp in comp_def.components.items() if refdes not in pkgd["components"]}
                )
            else:
                comp_list.update(
                    {refdes: comp for refdes, comp in comp_def.components.items() if refdes in pkgd["components"]}
                )
            for _, i in comp_list.items():
                i.package_def = name
