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

from pyedb.dotnet.edb_core.configuration_data.boundaries import Boundaries
from pyedb.dotnet.edb_core.configuration_data.component import Component
from pyedb.dotnet.edb_core.configuration_data.nets import Nets
from pyedb.dotnet.edb_core.definition.package_def import PackageDef
from pyedb.generic.general_methods import pyedb_function_handler


class Configuration:
    """Enables export and import of a JSON configuration file that can be applied to a new or existing design."""

    def __init__(self, pedb):
        self._pedb = pedb
        self._components = self._pedb.components.components
        self.data = None
        self.components = {}
        self.boundaries = None
        self.nets = None
        self._s_parameter_library = ""
        self._spice_model_library = ""

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
            self.data = config_file
        elif os.path.isfile(config_file):
            with open(config_file, "r") as f:
                if config_file.endswith(".json"):
                    self.data = json.load(f)
                elif config_file.endswith(".toml"):
                    self.data = toml.load(f)
        else:  # pragma: no cover
            return False

        if not append:  # pragma: no cover
            self.data = {}
        for k, v in self.data.items():
            if k == "components":
                for component in v:
                    comp = Component(self._pedb, component)
                    if comp.reference_designator not in self.components:
                        self.components[comp.reference_designator] = comp
            elif k == "boundaries":
                self.boundaries = Boundaries(self._pedb, v)

            elif k == "nets":
                self.nets = Nets(self._pedb, v)

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
        return self.data

    @pyedb_function_handler()
    def run(self):
        """Apply configuration settings to the current design"""

        # Configure components
        if not self.data:
            self._pedb.logger.error("No data loaded. Please load a configuration file.")
            return False

        # Configure padstacks
        if "padstacks" in self.data:
            self._load_padstacks()

        # Configure pin groups
        if "pin_groups" in self.data:
            self._load_pin_groups()

        # Configure ports
        if "ports" in self.data:
            self._load_ports()

        # Configure sources
        if "sources" in self.data:
            self._load_sources()

        # Configure HFSS setup
        if "setups" in self.data:
            self._load_setups()

        # Configure stackup
        if "stackup" in self.data:
            self._load_stackup()

        # Configure S-parameter
        if "s_parameters" in self.data:
            self._load_s_parameter()

        # Configure SPICE models
        if "spice_models" in self.data:
            self._load_spice_models()

        # Configure package definitions
        if "package_definitions" in self.data:
            self._load_package_def()

        # Configure operations
        if "operations" in self.data:
            self._load_operations()

        return True

    @pyedb_function_handler
    def _load_ports(self):
        """Imports port information from json."""
        for port in self.data["ports"]:
            port_type = port["type"]

            positive_terminal_json = port["positive_terminal"]
            pos_terminal = ""
            if "pin_group" in positive_terminal_json:
                pin_group = self._pedb.siwave.pin_groups[positive_terminal_json["pin_group"]]
                port_name = pin_group.name if "name" not in port else port["name"]
                pos_terminal = pin_group.get_terminal(port_name, True)

            else:
                ref_designator = port["reference_designator"]
                comp_layout = self._components[ref_designator]

                if "pin" in positive_terminal_json:
                    pin_name = positive_terminal_json["pin"]
                    port_name = "{}_{}".format(ref_designator, pin_name) if "name" not in port else port["name"]
                    pos_terminal = comp_layout.pins[pin_name].get_terminal(port_name, True)
                else:  # Net
                    net_name = positive_terminal_json["net"]
                    port_name = "{}_{}".format(ref_designator, net_name) if "name" not in port else port["name"]
                    if port_type == "circuit":
                        pg_name = "pg_{}".format(port_name)
                        _, pg = self._pedb.siwave.create_pin_group_on_net(ref_designator, net_name, pg_name)
                        pos_terminal = pg.get_terminal(port_name, True)
                    else:  # Coax port
                        for _, p in comp_layout.pins.items():
                            if p.net_name == net_name:
                                pos_terminal = p.get_terminal(port_name, True)
                                break

            if port_type == "circuit":
                negative_terminal_json = port["negative_terminal"]
                if "pin_group" in negative_terminal_json:
                    pin_group = self._pedb.siwave.pin_groups[negative_terminal_json["pin_group"]]
                    neg_terminal = pin_group.get_terminal(pin_group.name + "_ref", True)
                elif "pin" in negative_terminal_json:
                    pin_name = negative_terminal_json["pin"]
                    port_name = "{}_{}_ref".format(ref_designator, pin_name)
                    neg_terminal = comp_layout.pins[pin_name].get_terminal(port_name, True)
                else:
                    net_name = negative_terminal_json["net"]
                    port_name = "{}_{}_ref".format(ref_designator, net_name)
                    pg_name = "pg_{}".format(port_name)
                    if pg_name not in self._pedb.siwave.pin_groups:
                        _, pg = self._pedb.siwave.create_pin_group_on_net(ref_designator, net_name, pg_name)
                    else:
                        pg = self._pedb.siwave.pin_groups[pg_name]
                    neg_terminal = pg.get_terminal(port_name, True)

                self._pedb.create_port(pos_terminal, neg_terminal, True)
            else:
                self._pedb.create_port(pos_terminal)

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
    def _load_setups(self):
        """Imports setup information from json."""
        for setup in self.data["setups"]:
            setup_type = setup["type"]

            edb_setup = None
            name = setup["name"]

            if setup_type.lower() == "siwave_dc":
                if name not in self._pedb.setups:
                    self._pedb.logger.info("Setup {} created.".format(name))
                    edb_setup = self._pedb.create_siwave_dc_setup(name)
                else:
                    self._pedb.logger.warning("Setup {} already existing. Editing it.".format(name))
                    edb_setup = self._pedb.setups[name]
                edb_setup.set_dc_slider(setup["dc_slider_position"])
                dc_ir_settings = setup.get("dc_ir_settings", None)
                if dc_ir_settings:
                    for k, v in dc_ir_settings.items():
                        if k not in dir(edb_setup.dc_ir_settings):
                            self._pedb.logger.error(f"Invalid keyword {k}")
                        else:
                            setattr(edb_setup.dc_ir_settings, k, v)
            else:
                if setup_type.lower() == "hfss":
                    if name not in self._pedb.setups:
                        self._pedb.logger.info("Setup {} created.".format(name))
                        edb_setup = self._pedb.create_hfss_setup(name)
                    else:
                        self._pedb.logger.warning("Setup {} already existing. Editing it.".format(name))
                        edb_setup = self._pedb.setups[name]
                    edb_setup.set_solution_single_frequency(
                        setup["f_adapt"], max_num_passes=setup["max_num_passes"], max_delta_s=setup["max_mag_delta_s"]
                    )
                elif setup_type.lower() == "siwave_syz":
                    name = setup["name"]
                    if name not in self._pedb.setups:
                        self._pedb.logger.info("Setup {} created.".format(name))
                        edb_setup = self._pedb.create_siwave_syz_setup(name)
                    else:
                        self._pedb.logger.warning("Setup {} already existing. Editing it.".format(name))
                        edb_setup = self._pedb.setups[name]
                    if "si_slider_position" in setup:
                        edb_setup.si_slider_position = setup["si_slider_position"]
                    if "pi_slider_position" in setup:
                        edb_setup.pi_slider_position = setup["pi_slider_position"]

                if "freq_sweep" in setup:
                    for fsweep in setup["freq_sweep"]:
                        frequencies = fsweep["frequencies"]
                        freqs = []

                        for d in frequencies:
                            if d["distribution"] == "linear step":
                                freqs.append(
                                    [
                                        "linear scale",
                                        self._pedb.edb_value(d["start"]).ToString(),
                                        self._pedb.edb_value(d["stop"]).ToString(),
                                        self._pedb.edb_value(d["step"]).ToString(),
                                    ]
                                )
                            elif d["distribution"] == "linear count":
                                freqs.append(
                                    [
                                        "linear count",
                                        self._pedb.edb_value(d["start"]).ToString(),
                                        self._pedb.edb_value(d["stop"]).ToString(),
                                        int(d["points"]),
                                    ]
                                )
                            elif d["distribution"] == "log scale":
                                freqs.append(
                                    [
                                        "log scale",
                                        self._pedb.edb_value(d["start"]).ToString(),
                                        self._pedb.edb_value(d["stop"]).ToString(),
                                        int(d["samples"]),
                                    ]
                                )

                        edb_setup.add_frequency_sweep(
                            fsweep["name"],
                            frequency_sweep=freqs,
                        )

    @pyedb_function_handler
    def _load_stackup(self):
        """Imports stackup information from json."""
        data = self.data["stackup"]
        materials = data["materials"] if "materials" in data else []
        materials_reformatted = {}
        for mat in materials:
            new_mat = {}
            new_mat["name"] = mat["name"]
            if "conductivity" in mat:
                new_mat["conductivity"] = mat["conductivity"]
            if "permittivity" in mat:
                new_mat["permittivity"] = mat["permittivity"]
            if "dielectricLoss_tangent" in mat:
                new_mat["loss_tangent"] = mat["dielectricLoss_tangent"]

            materials_reformatted[mat["name"]] = new_mat

        layers = data["layers"]
        layers_reformatted = {}

        for l in layers:
            lyr = {
                "name": l["name"],
                "type": l["type"],
                "material": l["material"],
                "thickness": l["thickness"],
            }
            if "fill_material" in l:
                lyr["dielectric_fill"] = l["fill_material"]
            layers_reformatted[l["name"]] = lyr
        stackup_reformated = {"layers": layers_reformatted, "materials": materials_reformatted}
        self._pedb.stackup.load(stackup_reformated)

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
    def _load_spice_models(self):
        """Imports SPICE information from json."""

        for sp in self.data["spice_models"]:
            fpath = sp["file_path"]
            if not Path(fpath).anchor:
                fpath = str(Path(self._spice_model_library) / fpath)
            sp_name = sp["name"]
            sub_circuit_name = sp.get("sub_circuit_name", None)
            comp_def_name = sp["component_definition"]
            comp_def = self._pedb.definitions.component[comp_def_name]
            comps = comp_def.components
            if sp["apply_to_all"]:
                for refdes, comp in comps.items():
                    if refdes not in sp["components"]:
                        comp.assign_spice_model(fpath, sp_name, sub_circuit_name)
            else:
                for refdes, comp in comps.items():
                    if refdes in sp["components"]:
                        comp.assign_spice_model(fpath, sp_name, sub_circuit_name)

    @pyedb_function_handler
    def _load_pin_groups(self):
        """Imports pin groups information from JSON."""
        comps = self._pedb.components.components
        for pg in self.data["pin_groups"]:
            name = pg["name"]
            ref_designator = pg["reference_designator"]
            if "pins" in pg:
                self._pedb.siwave.create_pin_group(ref_designator, pg["pins"], name)
            elif "net" in pg:
                nets = pg["net"]
                nets = nets if isinstance(nets, list) else [nets]
                comp = comps[ref_designator]
                pins = [p for p, obj in comp.pins.items() if obj.net_name in nets]
                self._pedb.siwave.create_pin_group(ref_designator, pins, name)
            else:
                pins = [i for i in comps[ref_designator].pins.keys()]
                self._pedb.siwave.create_pin_group(ref_designator, pins, name)

    @pyedb_function_handler
    def _load_general(self):
        """Imports general information from JSON."""

    @pyedb_function_handler
    def _load_operations(self):
        """Imports operation information from JSON."""
        operations = self.data["operations"]
        cutout = operations.get("cutout", None)
        if cutout:
            self._pedb.cutout(**cutout)

    @pyedb_function_handler
    def _load_padstacks(self):
        """Imports padstack information from JSON."""
        padstacks = self.data["padstacks"]
        definitions = padstacks.get("definitions", None)
        if definitions:
            padstack_defs = self._pedb.padstacks.definitions
            for value in definitions:
                pdef = padstack_defs[value["name"]]
                if "hole_diameter" in value:
                    pdef.hole_diameter = value["hole_diameter"]
                if "hole_plating_thickness" in value:
                    pdef.hole_plating_thickness = value["hole_plating_thickness"]
                if "hole_material" in value:
                    pdef.material = value["hole_material"]
                if "hole_range" in value:
                    pdef.hole_range = value["hole_range"]
        instances = padstacks.get("instances", None)
        if instances:
            padstack_instances = self._pedb.padstacks.instances_by_name
            for value in instances:
                inst = padstack_instances[value["name"]]
                backdrill_top = value.get("backdrill_top", None)
                if backdrill_top:
                    inst.set_backdrill_top(
                        backdrill_top["drill_to_layer"], backdrill_top["drill_diameter"], backdrill_top["stub_length"]
                    )
                backdrill_bottom = value.get("backdrill_bottom", None)
                if backdrill_top:
                    inst.set_backdrill_bottom(
                        backdrill_bottom["drill_to_layer"],
                        backdrill_bottom["drill_diameter"],
                        backdrill_bottom["stub_length"],
                    )

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
