import json
from pathlib import Path

import numpy as np
import pandas as pd

from pyedb import Edb
from pyedb.generic.general_methods import generate_unique_name


class Pair:
    def __init__(self, name, net_names, **kwargs):
        self.design_type = ""
        self.name = name
        self.net_names = net_names
        self.core_pdef = kwargs.get("core_pdef", "blind_via")
        self.has_stitching_vias = kwargs.get("has_stitching_vias", False)

        self.bga_locations = []
        self.vias = None
        self.trace_out = []

        self.fanout_port_location = []

        self.p_via_loc = []  # [[via1 x, y], [via2 x, u]]
        self.n_via_loc = []  # [[via1 x, y], [via2 x, u]]

        self.via_to_via_traces = []

        self.pkg_trace_out_lower_port_location = None
        self.pkg_trace_out_upper_port_location = None
        self.pcb_trace_out_lower_port_location = None
        self.pcb_trace_out_upper_port_location = None

    @property
    def race_track_path_list(self):
        temp = []
        start_stop_layer = []
        for v in self.vias:
            start_stop_layer.append([v["padstack_definition"], v["start_layer"], v["stop_layer"]])
        temp.append(list(zip(start_stop_layer, self.p_via_loc, self.n_via_loc)))
        # ['blind_via', 'L2', 'L3', is_core_via], [x_loc, y_loc], [x_loc, y_loc]
        return temp

    @property
    def core_via_start_layer(self):
        start_layer = [i["start_layer"] for i in self.vias if i["padstack_definition"] == self.core_pdef][0]
        return start_layer

    @property
    def core_via_stop_layer(self):
        stop_layer = [i["stop_layer"] for i in self.vias if i["padstack_definition"] == self.core_pdef][0]
        return stop_layer

    @property
    def bga_pin_location(self):
        return [[f"{loc[1]}*pitch", f"{loc[0]}*pitch"] for loc in self.bga_locations]

    @property
    def fanout_via_location_outer(self):
        return [self.p_via_loc[-1], self.n_via_loc[-1]]  # [[p_x, p_y], [n_x, n_y]]

    @property
    def fanout_via_location_inner(self):
        return [self.p_via_loc[0], self.n_via_loc[0]]  # [[p_x, p_y], [n_x, n_y]]

    @property
    def pkg_trace_out_lower_params(self):
        if len(self.trace_out) == 2:
            temp = self.trace_out[1].copy()
        else:
            return

        temp["name"] = self.name
        temp["net_names"] = self.net_names
        temp["fanout_via_location"] = self.fanout_via_location_inner
        temp["base_via_loc"] = self.bga_locations
        temp["port_location"] = self.pkg_trace_out_lower_port_location
        return temp

    @property
    def pkg_trace_out_upper_params(self):
        temp = self.trace_out[0].copy()
        temp["name"] = self.name
        temp["net_names"] = self.net_names
        temp["fanout_via_location"] = self.fanout_via_location_outer
        temp["base_via_loc"] = self.bga_locations
        temp["port_location"] = self.pkg_trace_out_upper_port_location
        return temp

    @property
    def pcb_trace_out_lower_params(self):
        if len(self.trace_out) == 2:
            temp = self.trace_out[1].copy()
        else:
            temp = self.trace_out[0].copy()

        temp["name"] = self.name
        temp["net_names"] = self.net_names
        temp["fanout_via_location"] = self.fanout_via_location_outer
        temp["base_via_loc"] = self.fanout_via_location_outer
        temp["port_location"] = self.pcb_trace_out_lower_port_location
        return temp

    @property
    def pcb_trace_out_upper_params(self):
        if len(self.trace_out) == 2:
            temp = self.trace_out[0].copy()
        else:
            return
        temp["name"] = self.name
        temp["net_names"] = self.net_names
        temp["fanout_via_location"] = self.fanout_via_location_inner
        temp["base_via_loc"] = self.fanout_via_location_inner
        temp["port_location"] = self.pcb_trace_out_upper_port_location
        return temp


class GroundVia:
    def __init__(self):
        self.bga_locations = []
        self.pattern_1_params = None  # {"distance": "0.2mm", "core_via_start_layer": "L6", "core_via_stop_layer": "L7"}


class ViaDesignConfig:
    @property
    def plane_size(self):
        y_size = len(self.pin_map["locations"])
        x_size = len(self.pin_map["locations"][0]) - 1
        return x_size, y_size

    @property
    def lower_left_point(self):
        return ["-plane_extend", "-plane_extend-pitch"]

    @property
    def upper_right_point(self):
        return [f"{self.plane_size[0]}*pitch+plane_extend", f"{self.plane_size[1]}*pitch+plane_extend"]

    def __init__(self, config_file: Path, version=""):
        self._version = version
        self._design_name = ""
        self._working_dir = ""
        self.pkg_stackup = []
        self.pcb_stackup = []

        self._variables = []
        self._padstack_instances = []
        self._padstack_definition = []
        self._traces = []
        self._planes = []
        self._voids = []
        self._components = []
        self._ports = []

        if isinstance(config_file, str):
            config_file = Path(config_file)
        self.config_file_path = config_file

        with open(config_file, "r") as f:
            self.config = json.load(f)

        with open(config_file.parent / self.config["materials"], "r") as f:
            self.materials = json.load(f)

        if self.design_type == "pkg":
            with open(config_file.parent / self.config["pkg_stackup"], "r") as f:
                self.pkg_stackup = json.load(f)

        if self.include_pcb or self.design_type == "pcb":
            with open(config_file.parent / self.config["pcb_stackup"], "r") as f:
                self.pcb_stackup = json.load(f)

        with open(config_file.parent / self.config["padstacks"], "r") as f:
            self.padstacks = json.load(f)

        with open(config_file.parent / self.config["pin_map"], "r") as f:
            self.pin_map = json.load(f)

        with open(config_file.parent / self.config["technology"], "r") as f:
            self.technology = json.load(f)

        with open(config_file.parent / self.config["setup"], "r") as f:
            self.setup = json.load(f)

        if self.include_pcb:
            pdef_bga = [i for i in self.padstacks if i["name"] == "bga"][0]
            pdef_bga["solder_ball_parameters"] = {
                "shape": self.technology["bga_component"]["solder_ball_shape"],
                "diameter": self.technology["bga_component"]["solder_ball_diameter"],
                "mid_diameter": self.technology["bga_component"].get("solder_ball_mid_diameter"),
                "placement": "above_padstack",
                "material": "solder",
            }

        locations = pd.DataFrame(self.pin_map["locations"])

        self.pcb_via_pairs = []
        self.pkg_via_pairs = []

        for name, nets in self.pin_map["signal_pairs"].items():
            bga_locations = []
            for net_name in nets:
                bga_locations.append((locations == net_name).stack()[(locations == net_name).stack()].index.tolist()[0])

            tech = self.technology["signal_pair"][name]
            if self.design_type == "pkg":
                sp = Pair(name, nets)
                sp.design_type = "pkg"
                sp.vias = tech["pkg_signal_via"]
                sp.trace_out = tech["pkg_trace"]
                sp.bga_locations = bga_locations
                self.pkg_via_pairs.append(sp)

            if self.include_pcb or self.design_type == "pcb":
                sp = Pair(name, nets, core_pdef="pcb_via")
                sp.design_type = "pcb"
                sp.vias = tech["pcb_signal_via"]
                sp.trace_out = tech["pcb_trace"]
                sp.bga_locations = bga_locations
                sp.has_stitching_vias = tech.get("has_stitching_vias", False)
                self.pcb_via_pairs.append(sp)

        if self.design_type == "pkg":
            self.pkg_ground_vias = GroundVia()
            for i in (locations == "GND").stack()[(locations == "GND").stack()].index.tolist():
                self.pkg_ground_vias.bga_locations.append(i)
                self.pkg_ground_vias.pattern_1_params = self.technology["pkg_ground_via"]

        if self.design_type == "pcb" or self.include_pcb:
            self.pcb_ground_vias = GroundVia()
            for i in (locations == "GND").stack()[(locations == "GND").stack()].index.tolist():
                self.pcb_ground_vias.bga_locations.append(i)
                self.pcb_ground_vias.pattern_1_params = self.technology["pcb_ground_via"]

    def create_ports_on_bga(self):
        ports = []
        for obj in self.pcb_via_pairs + self.pkg_via_pairs:
            for idx, i in enumerate(obj.net_names):
                port_name = f"{obj.name}_p_coax_port" if idx == 0 else f"{obj.name}_n_coax_port"
                port = {
                    "name": port_name,
                    "reference_designator": "U1",
                    "type": "coax",
                    "positive_terminal": {"net": i},
                }
                ports.append(port)
        return ports

    @property
    def signal_layers(self) -> list:
        return [i["name"] for i in self.stackup if i["type"].lower() == "signal"]

    @property
    def signal_layers_pkg(self) -> list:
        return [i["name"] for i in self.pkg_stackup if i["type"].lower() == "signal"]

    @property
    def signal_layers_pcb(self) -> list:
        return [i["name"] for i in self.pcb_stackup if i["type"].lower() == "signal"]

    @property
    def pcb_signal_layer_list(self) -> list:
        return [i["name"] for i in self.pcb_stackup if i["type"].lower() == "signal"]

    @property
    def stackup(self):
        temp = []
        for layer in self.pkg_stackup:
            l2 = layer.copy()
            temp.append(l2)

        if self.pcb_stackup:
            temp.append(
                {
                    "name": "PKG_PCB_AIR",
                    "type": "dielectric",
                    "material": "air",
                    "thickness": self.technology["bga_component"]["solder_ball_height"],
                }
            )
        for layer in self.pcb_stackup:
            l2 = layer.copy()
            temp.append(l2)
        return temp

    @property
    def working_dir(self):
        if not self._working_dir:
            wdir = self.config.get("working_directory")
            if wdir is not None:
                self._working_dir = Path(wdir)
            else:
                working_dir = self.config_file_path.parent / "via_designs"
                working_dir.mkdir(parents=True, exist_ok=True)
                self._working_dir = working_dir
        return self._working_dir

    @property
    def design_name(self):
        if not self._design_name:
            self._design_name = Path(generate_unique_name(self.config_file_path.stem))
        return self._design_name

    @property
    def design_type(self):
        return self.config["design_type"].lower()

    @property
    def include_pcb(self):
        return self.config["include_pcb"] if self.design_type == "pkg" else None

    @property
    def version(self):
        if self._version:
            return self._version
        else:
            return self.config["version"]

    def _create_variables(self):
        self._variables.extend(
            [
                {"name": "plane_extend", "value": self.technology["plane_extend"], "description": "general"},
                {"name": "pitch", "value": self.technology["pitch"], "description": "general"},
            ]
        )

        if self.design_type == "pkg":
            for name, _ in self.pin_map["signal_pairs"].items():
                die_side_stitching_via_dy = self.technology["signal_pair"][name]["pkg_trace"][0]["stitching_via_dy"]
                self._variables.extend(
                    [
                        {
                            "name": f"{name}_die_side_stitching_via_dy",
                            "value": die_side_stitching_via_dy,
                            "description": "general",
                        },
                    ]
                )
        elif self.include_pcb or self.design_type == "pcb":
            self._variables.extend(
                [
                    {"name": "pcb_stitching_via_distance", "value": "1mm", "description": "general"},
                ]
            )

        else:
            pass

    def create_design(self):
        self._create_variables()

        new_vars, padstack_defs = self._create_padstack_defs()
        self._variables.extend(new_vars)
        self._padstack_definition.extend(padstack_defs)

        if self.design_type == "pkg":
            for df in self.pkg_via_pairs:
                self._create_signal_via_transition(df, design_type="pkg")

                self._create_return_via_pkg(df)

                port_location = self._create_signal_fanout_type_1(df.pkg_trace_out_upper_params, design_type="pkg")
                layer = df.pkg_trace_out_upper_params["layer"]
                name = df.pkg_trace_out_upper_params["name"]
                port = {
                    "name": f"pkg_{name}_{layer}_wave_port",
                    "type": "diff_wave_port",
                    "positive_terminal": {"primitive_name": port_location[0][0], "point_on_edge": port_location[0][1]},
                    "negative_terminal": {"primitive_name": port_location[1][0], "point_on_edge": port_location[1][1]},
                    "horizontal_extent_factor": 6,
                    "vertical_extent_factor": 4,
                    "pec_launch_width": "0.02mm",
                }
                self._ports.append(port)

                df.pkg_trace_out_upper_port_location = port_location

                if df.pkg_trace_out_lower_params:
                    port_location = self._create_signal_fanout_type_1(df.pkg_trace_out_lower_params, design_type="pkg")
                    layer = df.pkg_trace_out_lower_params["layer"]
                    name = df.pkg_trace_out_lower_params["name"]
                    port = {
                        "name": f"pkg_{name}_{layer}_wave_port",
                        "type": "diff_wave_port",
                        "positive_terminal": {
                            "primitive_name": port_location[0][0],
                            "point_on_edge": port_location[0][1],
                        },
                        "negative_terminal": {
                            "primitive_name": port_location[1][0],
                            "point_on_edge": port_location[1][1],
                        },
                        "horizontal_extent_factor": 6,
                        "vertical_extent_factor": 4,
                        "pec_launch_width": "0.02mm",
                    }
                    self._ports.append(port)

                self._create_race_track(df, design_type="pkg")
                # self._create_bga_component(placement_layer="PKG_BOT")
            self._create_gnd_vias(design_type="pkg")

        if self.include_pcb or self.design_type == "pcb":
            for df in self.pcb_via_pairs:
                self._create_signal_via_transition(df, design_type="pcb")
                if df.has_stitching_vias:
                    self._create_return_via_pcb(df)

                port_location = self._create_signal_fanout_type_1(df.pcb_trace_out_lower_params, design_type="pcb")
                layer = df.pcb_trace_out_lower_params["layer"]
                name = df.pcb_trace_out_lower_params["name"]
                port = {
                    "name": f"pkg_{name}_{layer}_wave_port",
                    "type": "diff_wave_port",
                    "positive_terminal": {"primitive_name": port_location[0][0], "point_on_edge": port_location[0][1]},
                    "negative_terminal": {"primitive_name": port_location[1][0], "point_on_edge": port_location[1][1]},
                    "horizontal_extent_factor": 6,
                    "vertical_extent_factor": 4,
                    "pec_launch_width": "0.02mm",
                }
                self._ports.append(port)

                if df.pcb_trace_out_upper_params:
                    port_location = self._create_signal_fanout_type_1(df.pcb_trace_out_upper_params, design_type="pcb")
                    layer = df.pcb_trace_out_upper_params["layer"]
                    name = df.pcb_trace_out_upper_params["name"]
                    port = {
                        "name": f"pkg_{name}_{layer}_wave_port",
                        "type": "diff_wave_port",
                        "positive_terminal": {
                            "primitive_name": port_location[0][0],
                            "point_on_edge": port_location[0][1],
                        },
                        "negative_terminal": {
                            "primitive_name": port_location[1][0],
                            "point_on_edge": port_location[1][1],
                        },
                        "horizontal_extent_factor": 6,
                        "vertical_extent_factor": 4,
                        "pec_launch_width": "0.02mm",
                    }
                    self._ports.append(port)
                # self._create_bga_component(placement_layer="PCB_TOP")
                self._create_race_track(df, design_type="pcb")
            self._create_gnd_vias(design_type="pcb")

        bga_params = self.technology["bga_component"]
        if self.design_type == "pcb":
            if bga_params["enabled"] is True:
                self._create_bga_component(bga_params, placement_layer="PCB_TOP")
        elif self.design_type == "pkg":
            if self.include_pcb:
                self._create_solder_ball()
            else:
                if bga_params["enabled"] is True:
                    self._create_bga_component(bga_params, placement_layer="PKG_BOT")

        planes = self._create_planes()
        self._planes.extend(planes)

        if not self.include_pcb:
            self._ports.extend(self.create_ports_on_bga())

        data = {"general": {"suppress_pads": True, "anti_pads_always_on": True}}

        stackup = {"materials": self.materials, "layers": self.stackup}
        data["stackup"] = stackup
        data["variables"] = self._variables
        data["ports"] = self._ports
        data["setups"] = [self.setup]

        modeler = {
            "padstack_definitions": self._padstack_definition,
            "padstack_instances": self._padstack_instances,
            "traces": self._traces,
            "planes": self._planes,
            "components": self._components,
        }
        data["modeler"] = modeler
        return data

    def _create_padstack_defs(self):
        new_variables = []
        cfg_padstacks = []
        for pad in self.padstacks:
            name = pad["name"]

            hole_diameter = pad.get("hole_diameter")
            if hole_diameter:
                var_hole_diameter = f"${name}_hole_diameter"
                new_variables.append({"name": var_hole_diameter, "value": hole_diameter, "description": "padstack"})
                hole_parameters = {"shape": "circle", "diameter": var_hole_diameter}
            else:
                hole_parameters = None

            pad_diameter = pad["pad_diameter"]
            var_pad_diameter = f"${name}_pad_diameter"
            new_variables.append({"name": var_pad_diameter, "value": pad_diameter, "description": "padstack"})
            shape = pad["shape"]
            if shape == "circle":
                regular_pad = []
                for layer in self.signal_layers:
                    regular_pad.append(
                        {
                            "layer_name": layer,
                            "shape": shape,
                            "diameter": var_pad_diameter,
                        }
                    )
            else:  # shape == "rectangle":
                x_size = pad["x_size"]
                y_size = pad["y_size"]
                var_pad_x_size = f"${name}_pad_x_size"
                var_pad_y_size = f"${name}_pad_y_size"
                new_variables.append({"name": var_pad_x_size, "value": x_size, "description": "padstack"})
                new_variables.append({"name": var_pad_y_size, "value": y_size, "description": "padstack"})

                regular_pad = []
                for layer in self.signal_layers:
                    regular_pad.append(
                        {
                            "layer_name": layer,
                            "shape": shape,
                            "x_size": var_pad_x_size,
                            "y_size": var_pad_y_size,
                        }
                    )

            anti_pad_diameter = pad["anti_pad_diameter"]

            # anti_pad = []
            for layer in self.signal_layers:
                if name in ["bga", "blind_via"]:
                    var_anti_pad_diameter = f"${name}_anti_pad_diameter"
                    new_variables.append(
                        {"name": var_anti_pad_diameter, "value": anti_pad_diameter, "description": "layer={l}"}
                    )
                    break
                else:
                    var_anti_pad_diameter = f"${name}_anti_pad_diameter_{layer}"
                    new_variables.append(
                        {"name": var_anti_pad_diameter, "value": anti_pad_diameter, "description": f"layer={layer}"}
                    )

            pad_parameters = {
                "regular_pad": regular_pad,
                # "anti_pad": anti_pad
            }

            new_p_def = {"name": name, "pad_parameters": pad_parameters}
            if hole_diameter:
                new_p_def.update(
                    {
                        "hole_parameters": hole_parameters,
                        "hole_range": pad["hole_range"],
                    }
                )

            if pad.get("solder_ball_parameters"):
                new_p_def["solder_ball_parameters"] = pad["solder_ball_parameters"]
            cfg_padstacks.append(new_p_def)
        return new_variables, cfg_padstacks

    def _create_race_track(self, diff_pair: Pair, design_type):
        voids = []
        for i in diff_pair.race_track_path_list:
            for j in i:
                pdef, p1, p2 = j
                pdef_name, start_layer, stop_layer = pdef
                flag = False
                for layer in self.signal_layers:
                    if layer == start_layer:
                        flag = True
                    if layer in ["PCB_TOP", "PKG_BOT"]:
                        if layer == stop_layer:
                            flag = False
                        continue
                    if flag:
                        width = (
                            f"${pdef_name}_anti_pad_diameter"
                            if pdef_name == "blind_via"
                            else f"${pdef_name}_anti_pad_diameter_{layer}"
                        )
                        trace = {
                            "path": [p1, p2],
                            "width": width,
                            "layer": layer,
                            "name": f"{pdef_name}_{layer}_race_track",
                            "net_name": "GND",
                        }
                        void = trace.copy()
                        void["void_type"] = "trace"
                        voids.append(void)

                    if layer == stop_layer:
                        flag = False

        if design_type == "pkg":
            for layer in self.signal_layers_pkg:
                if layer in ["PCB_TOP", "PKG_BOT"]:
                    continue
                trace = {
                    "path": diff_pair.bga_pin_location,
                    "width": "$bga_anti_pad_diameter",
                    "layer": layer,
                    "name": f"bga_{layer}_race_track",
                    "net_name": "GND",
                    "void_type": "trace",
                }
                voids.append(trace)
        self._voids.extend(voids)
        # self._traces.extend(voids)
        return voids

    def _create_return_via_pkg(self, diff_pair: Pair):
        pd_instances = []
        for pin_idx, pin_loc in enumerate(diff_pair.bga_pin_location):
            for idx, layer in enumerate(self.signal_layers_pkg):
                if layer == self.signal_layers_pkg[-1]:
                    break
                pdef = "blind_via" if layer == diff_pair.core_via_start_layer else "micro_via"
                if not pin_idx % 2:
                    init_angle = "pi*5/8" if idx % 2 else "pi*1/2"
                else:
                    init_angle = "pi*13/8" if idx % 2 else "pi*3/2"
                distance = f"$bga_anti_pad_diameter/2+${pdef}_hole_diameter/2"
                via_list = np.arange(4) if idx % 2 else np.arange(5)
                for i in via_list:
                    angle = f"{init_angle}+{i}*1/4*pi"
                    x_loc = f"{pin_loc[0]}+cos({angle})*({distance})"
                    y_loc = f"{pin_loc[1]}+sin({angle})*({distance})"
                    pd_instances.append(
                        {
                            # "name": f"{diff_pair.name}_p_return_",
                            "definition": pdef,
                            "layer_range": [layer, self.signal_layers_pkg[idx + 1]],
                            "net_name": "GND",
                            "position": [x_loc, y_loc],
                            "is_pin": False,
                        }
                    )

        for idx, loc in enumerate(diff_pair.fanout_via_location_outer):
            x_loc = loc[0]
            y_loc = f"{loc[1]}+{diff_pair.name}_die_side_stitching_via_dy/2"
            pd_instances.append(
                {
                    # "name": f"{diff_pair.name}_p_return_",
                    "definition": "micro_via",
                    "layer_range": [
                        diff_pair.pkg_trace_out_upper_params["layer"],
                        self.signal_layers_pkg[
                            self.signal_layers_pkg.index(diff_pair.pkg_trace_out_upper_params["layer"]) + 1
                        ],
                    ],
                    "net_name": "GND",
                    "position": [x_loc, y_loc],
                    "is_pin": False,
                }
            )
        self._padstack_instances.extend(pd_instances)
        return pd_instances

    def _create_return_via_pcb(self, diff_pair: Pair):
        pd_instances = []
        pdef = diff_pair.core_pdef
        for pin_idx, pin_loc in enumerate(diff_pair.bga_pin_location):
            if not pin_idx % 2:
                init_angle = "pi*4/8"
            else:
                init_angle = "pi*3/2"
            distance = "pcb_stitching_via_distance"
            via_list = np.arange(4)
            for i in via_list:
                angle = f"{init_angle}+{i}*1/3*pi"
                x_loc = f"{pin_loc[0]}+cos({angle})*({distance})"
                y_loc = f"{pin_loc[1]}+sin({angle})*({distance})"
                pd_instances.append(
                    {
                        # "name": f"{diff_pair.name}_p_return_",
                        "definition": pdef,
                        "layer_range": [diff_pair.core_via_start_layer, diff_pair.core_via_stop_layer],
                        "net_name": "GND",
                        "position": [x_loc, y_loc],
                        "is_pin": False,
                    }
                )
            self._padstack_instances.extend(pd_instances)

    def _create_bga_component(self, params, placement_layer):
        p_instances = []
        bga_comp_pins = []
        for row, row_obj in enumerate(self.pin_map["locations"]):
            for col, obj in enumerate(row_obj):
                if obj is None:
                    continue
                net_name = obj
                x_loc = f"{col}*pitch"
                y_loc = f"{row}*pitch"
                name = f"via_{row}_{col}" if net_name == "GND" else net_name
                name = f"{name}_bga"

                temp = {
                    "name": name,
                    "definition": "bga",
                    "net_name": net_name,
                    "position": [x_loc, y_loc],
                    "layer_range": [placement_layer, placement_layer],
                    "is_pin": True,
                }
                p_instances.append(temp)
                bga_comp_pins.append(name)

        solder_ball_property = {
            "shape": self.technology["bga_component"]["solder_ball_shape"],
            "diameter": self.technology["bga_component"]["solder_ball_diameter"],
            "mid_diameter": self.technology["bga_component"]["solder_ball_mid_diameter"],
            "height": self.technology["bga_component"]["solder_ball_height"],
        }
        comp = {
            "reference_designator": "U1",
            "pins": bga_comp_pins,
            "part_type": "io",
            "definition": "BGA",
            "placement_layer": placement_layer,
            "solder_ball_properties": solder_ball_property,
            "port_properties": {
                "reference_offset": "0mm",
                "reference_size_auto": True,
                "reference_size_x": 0,
                "reference_size_y": 0,
            },
        }
        self._components.append(comp)
        self._padstack_instances.extend(p_instances)
        return comp, p_instances

    def _create_solder_ball(self):
        p_instances = []
        bga_comp_pins = []
        for row, row_obj in enumerate(self.pin_map["locations"]):
            for col, obj in enumerate(row_obj):
                if obj is None:
                    continue
                net_name = obj
                x_loc = f"{col}*pitch"
                y_loc = f"{row}*pitch"
                name = f"via_{row}_{col}" if net_name == "GND" else net_name
                pcb_name = f"{name}_bga"

                temp_pcb_side = {
                    "name": pcb_name,
                    "definition": "bga",
                    "net_name": net_name,
                    "position": [x_loc, y_loc],
                    "layer_range": ["PCB_TOP", "PCB_TOP"],
                    "is_pin": True,
                    "solder_ball_layer": "PKG_BOT",
                }
                p_instances.append(temp_pcb_side)
                bga_comp_pins.append(pcb_name)

                temp_pkg_side = temp_pcb_side.copy()
                temp_pkg_side["name"] = f"{name}_pkg"
                temp_pkg_side["layer_range"] = ["PKG_BOT", "PKG_BOT"]
                temp_pkg_side.pop("solder_ball_layer")
                p_instances.append(temp_pkg_side)

        self._padstack_instances.extend(p_instances)
        return p_instances

    def _create_gnd_vias(self, design_type):
        variables = []
        traces = []
        voids = []

        ground_vias = self.pkg_ground_vias if design_type == "pkg" else self.pcb_ground_vias
        distance = f"{design_type}_ground_via_distance"

        if ground_vias.bga_locations:
            variables.append(
                {"name": distance, "value": ground_vias.pattern_1_params["distance"], "description": "ground_via"}
            )
        pd_insts = []

        for location in ground_vias.bga_locations:
            row, col = location
            via_name = f"{design_type}_via_{row}_{col}"
            if design_type == "pcb" and self.technology["bga_component"]["enabled"] is True:
                dx = self.technology["bga_component"]["fanout_dx"]
                dy = self.technology["bga_component"]["fanout_dy"]
                x_loc_0 = f"{col}*pitch"
                y_loc_0 = f"{row}*pitch"
                x_loc = f"{x_loc_0}+{dx}"
                y_loc = f"{y_loc_0}-{dy}"

                trace_name = f"bga_fanout_trace_via_{row}_{col}"
                trace_width = self.technology["bga_component"]["fanout_width"]
                trace = {
                    "path": [[x_loc_0, y_loc_0], [x_loc, y_loc]],
                    "width": trace_width,
                    "name": trace_name,
                    "layer": "PCB_TOP",
                    "net_name": "GND",
                }
                traces.append(trace)
            else:
                x_loc = f"{col}*pitch"
                y_loc = f"{row}*pitch"

            pd = {
                "name": f"{design_type}_{via_name}_cvia_{row}_{col}",
                "definition": "blind_via" if design_type == "pkg" else "pcb_via",
                "layer_range": [
                    ground_vias.pattern_1_params["core_via_start_layer"],
                    ground_vias.pattern_1_params["core_via_stop_layer"],
                ],
                "net_name": "GND",
                "position": [x_loc, y_loc],
                "is_pin": False,
            }
            pd_insts.append(pd)

            if design_type == "pkg":
                flag = True
                for idx, layer in enumerate(self.signal_layers_pkg):
                    if layer == ground_vias.pattern_1_params["core_via_start_layer"]:
                        flag = False
                    elif layer == ground_vias.pattern_1_params["core_via_stop_layer"]:
                        flag = True

                    if idx < len(self.signal_layers_pkg) - 1:
                        if flag:
                            start_layer = layer
                            end_layer = self.signal_layers_pkg[idx + 1]
                        else:
                            start_layer = ground_vias.pattern_1_params["core_via_start_layer"]
                            end_layer = ground_vias.pattern_1_params["core_via_stop_layer"]
                    else:
                        break

                    if flag:
                        angle = 0
                        for micro_via_idx, i in enumerate(["pi*1/2"] * 4):
                            angle = f"{angle} + {i}"
                            guvia_1_x_loc = f"{x_loc}+cos({angle})*{distance}"
                            guvia_1_y_loc = f"{y_loc}+sin({angle})*{distance}"

                            uvia_pd = {
                                "name": f"{design_type}_{via_name}_uvia_{start_layer}_{end_layer}_{micro_via_idx}",
                                "definition": "micro_via",
                                "net_name": "GND",
                                "position": [guvia_1_x_loc, guvia_1_y_loc],
                                "layer_range": [start_layer, end_layer],
                                "is_pin": False,
                            }
                            pd_insts.append(uvia_pd)

        self._padstack_instances.extend(pd_insts)
        self._variables.extend(variables)
        self._traces.extend(traces)
        self._voids.extend(voids)

        return variables, traces, voids, pd_insts

    def _create_signal_via_transition(self, diff_pair: Pair, design_type):  # pragma no cover
        trace_layer_name = "stop_layer" if design_type == "pkg" else "start_layer"

        fanout_polarity = "1" if design_type == "pkg" else "-1"
        variables = []
        pd_insts = []
        traces = []
        voids = []

        local_traces = []
        for net_idx, net_name in enumerate(diff_pair.net_names):
            if design_type == "pkg":
                pn_coef = 1 if net_idx == 0 else -1
            else:
                pn_coef = 1
            x_loc = f"{diff_pair.bga_locations[net_idx][1]}*pitch"
            y_loc = f"{diff_pair.bga_locations[net_idx][0]}*pitch"

            path = [[x_loc, y_loc]]
            for _, v in enumerate(diff_pair.vias):
                trace_layer = v[trace_layer_name]
                if v.get("trace", True):  # whether to create trace
                    dx = f"{diff_pair.name}_via_{trace_layer}_dx"
                    if net_idx == 1:
                        variables.append({"name": dx, "value": v["dx"]})

                    dy = f"{diff_pair.name}_via_{trace_layer}_dy"
                    if net_idx == 1:
                        variables.append({"name": dy, "value": v["dy"]})

                    x_loc = f"{x_loc}+{dx}*({pn_coef})"
                    y_loc = f"{y_loc}+{dy}*{fanout_polarity}"

                    last_point = [x_loc, y_loc]
                    path.append(last_point)
                    trace = v.copy()
                    trace["net_name"] = net_name
                    trace["path"] = path
                    trace["layer"] = trace_layer

                    width = f"{diff_pair.name}_via_{trace_layer}_trace_width"
                    if net_idx == 1:
                        variables.append({"name": width, "value": v["trace_width"]})
                    trace["width"] = width

                    clearance = f"{diff_pair.name}_via_{trace_layer}_trace_clearance"
                    if net_idx == 1:
                        variables.append({"name": clearance, "value": f"{width}+2*{v['trace_clearance']}"})
                    trace["void_width"] = clearance

                    local_traces.append(trace)
                    path = [last_point]

                start_layer = v["start_layer"]
                stop_layer = v["stop_layer"]

                pdef = v["padstack_definition"]
                if pdef == "micro_via":
                    start_idx = self.signal_layers.index(start_layer)
                    stop_idx = self.signal_layers.index(stop_layer)
                    for i in np.arange(start_idx, stop_idx):
                        temp_start = self.signal_layers[i]
                        temp_stop = self.signal_layers[i + 1]
                        temp = {
                            "name": f"{net_name}_via_{start_layer}_{stop_layer}_{i}",
                            "definition": pdef,
                            "layer_range": [temp_start, temp_stop],
                            "net_name": net_name,
                            "position": [x_loc, y_loc],
                            "is_pin": False,
                        }
                        pd_insts.append(temp)
                else:
                    temp = {
                        "name": f"{net_name}_via_{start_layer}_{stop_layer}",
                        "definition": pdef,
                        "layer_range": [start_layer, stop_layer],
                        "net_name": net_name,
                        "position": [x_loc, y_loc],
                        "is_pin": False,
                    }

                    back_drilling = v.get("backdrill_parameters")
                    if back_drilling:
                        temp["backdrill_parameters"] = back_drilling
                    pd_insts.append(temp)

                if True:  # v.get("race_track"):
                    if net_idx % 2 == 0:
                        diff_pair.p_via_loc.append([x_loc, y_loc])
                    else:
                        diff_pair.n_via_loc.append([x_loc, y_loc])

        for idx, t in enumerate(local_traces):
            net_name = t["net_name"]
            path = t["path"]
            diff_pair.via_to_via_traces.append(path)
            trace = {
                "path": path,
                "width": t["width"],
                "name": f"{net_name}_via_{idx}_trace",
                "layer": t["layer"],
                "net_name": net_name,
            }
            traces.append(trace)

            if trace["layer"] not in ["PCB_TOP", "PKG_BOT"]:
                void = trace.copy()
                void["name"] = f"{net_name}_via_{idx}_clearance"
                void["width"] = t["void_width"]
                void["void_type"] = "trace"
                voids.append(void)
                # traces.append(void)

        self._variables.extend(variables)
        self._padstack_instances.extend(pd_insts)
        self._traces.extend(traces)
        self._voids.extend(voids)
        return variables, pd_insts, traces, voids

    def _create_planes(self):
        planes = []

        for layer in self.signal_layers:
            if layer in ["PCB_TOP", "PKG_BOT"]:
                continue
            p = dict()
            p["name"] = f"GND_{layer}"
            p["layer"] = layer
            p["net_name"] = "GND"
            p["lower_left_point"] = self.lower_left_point
            p["upper_right_point"] = self.upper_right_point
            temp = []
            for v in self._voids:
                if v["layer"] == layer:
                    temp.append(v["name"])
                    if v["void_type"] == "trace":
                        self._traces.append(v)
                    elif v["void_type"] == "plane":
                        self._planes.append(v)

            p["voids"] = temp
            planes.append(p)
        return planes

    def _create_signal_fanout_type_1(self, params, design_type):
        trace_out_direction = 1 if params["trace_out_direction"] == "forward" else -1

        variables = []
        traces = []
        voids = []
        planes = []

        die_side_port_location = []
        trace_corner_location = []

        width, gap, clearance, shift, length = 0, 0, 0, 0, 0
        for idx, via_loc in enumerate(params["fanout_via_location"]):
            pn_polarity = -1 if idx == 0 else 1

            if idx == 0:
                width = f"{design_type}_{params['name']}_{params['layer']}_trace_width"
                variables.append({"name": width, "value": params["width"], "description": params["name"]})
                gap = f"{design_type}_{params['name']}_{params['layer']}_trace_gap"
                variables.append({"name": gap, "value": params["gap"], "description": params["name"]})
                shift = f"{design_type}_{params['name']}_{params['layer']}_trace_corner_shift"
                variables.append({"name": shift, "value": params["shift"], "description": params["name"]})
                if design_type == "pkg":
                    length = f"{design_type}_{params['name']}_{params['layer']}_trace_length"
                    variables.append({"name": length, "value": params["length"], "description": params["name"]})

            path = [via_loc]
            if design_type == "pkg":
                x_loc = f"{params['base_via_loc'][idx][1]}*pitch+{pn_polarity}*(-0.5*pitch+{gap}/2+{width}/2)"
            elif design_type == "pcb":
                x_loc = f"{params['base_via_loc'][idx][0]}+{pn_polarity}*(-0.5*pitch+{gap}/2+{width}/2)"

            y_loc = f"{via_loc[1]}+{shift}*{trace_out_direction}"

            path.append([x_loc, y_loc])
            trace_corner_location.append([x_loc, y_loc])

            if design_type == "pkg":
                y_loc = f"{y_loc}+{length}*{trace_out_direction}"
            elif trace_out_direction == 1:
                y_loc = self.upper_right_point[1]
            else:
                y_loc = "-plane_extend-pitch"
            path.append([x_loc, y_loc])

            trace_name = f"{design_type}_{params['name']}_{params['layer']}_trace_{params['net_names'][idx]}"
            trace = {
                "path": path,
                "width": width,
                "name": trace_name,
                "layer": params["layer"],
                "net_name": params["net_names"][idx],
                "start_cap_style": "flat",
                "end_cap_style": "flat",
                "corner_style": "sharp",
            }
            if design_type == "pkg":
                trace["path"] = path[1:]
            traces.append(trace)

            if idx == 0:
                clearance = f"{design_type}_{params['name']}_{params['layer']}_trace_clearance"
                variables.append({"name": clearance, "value": params["clearance"], "description": params["name"]})
            void = trace.copy()
            void["path"] = path
            void["width"] = f"{width}+2*{clearance}"
            void["name"] = trace_name + "_clearance"
            void["end_cap_style"] = "extended"
            void["void_type"] = "trace"

            voids.append(void)
            # traces.append(void)

            if design_type == "pkg":
                # create teardrop
                # td_angle1 = f"atan({shift}/(pitch/2-{gap}/2-{width}/2))"
                trace_p0_x, trace_p0_y = path[0]
                trace_p1_x, trace_p1_y = path[1]
                trace_dx = f"abs({trace_p1_x}-({trace_p0_x}))"
                trace_dy = f"abs({trace_p1_y}-({trace_p0_y}))"

                td_angle2 = f"atan({trace_dx}/{trace_dy})"

                td_dx = f"$micro_via_pad_diameter/2*cos({td_angle2})"
                td_dy = f"$micro_via_pad_diameter/2*sin({td_angle2})"

                p0 = [f"{trace_p1_x}- {width}/2*{pn_polarity}", trace_p1_y]
                p1 = [f"{trace_p1_x}+ {width}/2*{pn_polarity}", trace_p1_y]
                p2 = [f"{td_dx}*{pn_polarity}", f"{td_dy}*{trace_out_direction}"]
                p3 = [f"{td_dx}*{pn_polarity}*-1", f"{td_dy}*-1*{trace_out_direction}"]

                pts2 = [p0, p1]
                for i in [p2, p3]:
                    pts2.append([f"{i[0]}+{via_loc[0]}", f"{i[1]}+{via_loc[1]}"])

                poly = {
                    "type": "polygon",
                    "name": f"{design_type}_{params['name']}_{params['layer']}_teardrop_{params['net_names'][idx]}",
                    "layer": params["layer"],
                    "net_name": params["net_names"][idx],
                    "points": pts2,
                }
                planes.append(poly)

            last_point = path[-1]
            die_side_port_location.append([trace_name, last_point])

        # create void
        v_loc = params["fanout_via_location"].copy()
        v_loc.reverse()
        pts = trace_corner_location + v_loc

        void = {
            "type": "polygon",
            "name": f"{design_type}_{params['name']}_{params['layer']}_trapezoid_void",
            "layer": params["layer"],
            "net_name": "GND",
            "points": pts,
            "void_type": "plane",
        }
        voids.append(void)
        # planes.append(void)
        self._variables.extend(variables)
        self._traces.extend(traces)
        self._voids.extend(voids)
        self._planes.extend(planes)
        return die_side_port_location

    def create_edb(self, data) -> str:
        edb_path = str(self.working_dir / self.design_name.with_suffix(".aedb"))
        print(edb_path)
        edbapp = Edb(edbpath=edb_path, edbversion=self.version)
        edbapp.configuration.load(data, apply_file=True)
        edbapp.save()
        edbapp.close()
        return edb_path

    def save_cfg_to_file(self, data):
        with open(self.working_dir / self.design_name.with_suffix(".json"), "w") as f:
            json.dump(data, f, indent=4)
