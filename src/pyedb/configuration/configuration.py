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

import toml

from pyedb.configuration.cfg_data import CfgData
from pyedb.dotnet.edb_core.definition.package_def import PackageDef
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
        if self.cfg_data.stackup:
            self.cfg_data.stackup.apply()

        # Configure S-parameter
        for s_parameter_model in self.cfg_data.s_parameters:
            s_parameter_model.apply()

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
