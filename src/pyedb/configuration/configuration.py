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


class Configuration:
    """Enables export and import of a JSON configuration file that can be applied to a new or existing design."""

    def __init__(self, pedb):
        self._pedb = pedb
        self._components = self._pedb.components.instances
        self.data = {}
        self._s_parameter_library = ""
        self._spice_model_library = ""
        self.cfg_data = CfgData(self._pedb)

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

    def run(self):
        """Apply configuration settings to the current design"""

        # Configure boundary settings
        if self.cfg_data.boundaries:
            self.cfg_data.boundaries.apply()

        # Configure nets
        if self.cfg_data.nets:
            self.cfg_data.nets.apply()

        # Configure components
        self.cfg_data.components.apply()

        # Configure padstacks
        if self.cfg_data.padstacks:
            self.cfg_data.padstacks.apply()

        # Configure pin groups
        self.cfg_data.pin_groups.apply()

        # Configure ports
        self.cfg_data.ports.apply()

        # Configure sources
        self.cfg_data.sources.apply()

        # Configure setup
        self.cfg_data.setups.apply()

        # Configure stackup
        self.cfg_data.stackup.apply()

        # Configure S-parameter
        for s_parameter_model in self.cfg_data.s_parameters:
            s_parameter_model.apply()

        # Configure SPICE models
        for spice_model in self.cfg_data.spice_models:
            spice_model.apply()

        # Configure package definitions
        self.cfg_data.package_definitions.apply()

        # Configure operations
        self.cfg_data.operations.apply()

        return True

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
            input_signal_layers = [i for i in layers if i["type"].lower() == "signal"]
            if not len(input_signal_layers) == len(self._pedb.stackup.signal_layers):
                self._pedb.logger.error("Input signal layer count do not match.")
                return False

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
                if l["type"] == "signal":
                    layer_id = lc_signal_layers[signal_idx]
                    layer_name = id_name[layer_id]
                    self._pedb.stackup.layers[layer_name].update(**l)
                    signal_idx = signal_idx + 1

            # add all dielectric layers. Dielectric layers must be added last. Otherwise,
            # dielectric layer will occupy signal and document layer id.
            prev_layer_clone = None
            l = layers.pop(0)
            if l["type"] == "signal":
                prev_layer_clone = self._pedb.stackup.layers[l["name"]]
            else:
                prev_layer_clone = self._pedb.stackup.add_layer_top(**l)
            for idx, l in enumerate(layers):
                if l["type"] == "dielectric":
                    prev_layer_clone = self._pedb.stackup.add_layer_below(base_layer_name=prev_layer_clone.name, **l)
                elif l["type"] == "signal":
                    prev_layer_clone = self._pedb.stackup.layers[l["name"]]

    def _load_package_def(self):
        """Imports package definition information from JSON."""
        comps = self._pedb.components.instances
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

    def get_data_from_db(self, **kwargs):
        """Get configuration data from layout.

        Parameters
        ----------
        stackup

        Returns
        -------

        """
        self._pedb.logger.info("Getting data from layout database.")
        data = {}
        if kwargs.get("stackup", False):
            data["stackup"] = self.cfg_data.stackup.get_data_from_db()
        if kwargs.get("package_definitions", False):
            data["package_definitions"] = self.cfg_data.package_definitions.get_data_from_db()
        if kwargs.get("setups", False):
            data["setups"] = self.cfg_data.setups.get_data_from_db()
        if kwargs.get("sources", False):
            data["sources"] = self.cfg_data.sources.get_data_from_db()
        if kwargs.get("ports", False):
            data["ports"] = self.cfg_data.ports.get_data_from_db()
        if kwargs.get("components", False):
            data["components"] = self.cfg_data.components.get_data_from_db()
        if kwargs.get("nets", False):
            data["nets"] = self.cfg_data.nets.get_data_from_db()
        if kwargs.get("pin_groups", False):
            data["pin_groups"] = self.cfg_data.pin_groups.get_data_from_db()

        return data

    def export(
        self,
        file_path,
        stackup=True,
        package_definitions=True,
        setups=True,
        sources=True,
        ports=True,
        nets=True,
        pin_groups=True,
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
        Returns
        -------
        bool
        """
        file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        file_path = file_path if file_path.suffix == ".json" else file_path.with_suffix(".json")
        data = self.get_data_from_db(
            stackup=stackup,
            package_definitions=package_definitions,
            setups=setups,
            sources=sources,
            ports=ports,
            nets=nets,
            pin_groups=pin_groups,
        )
        with open(file_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True if os.path.isfile(file_path) else False
