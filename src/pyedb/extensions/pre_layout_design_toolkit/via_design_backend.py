import os
import re
from copy import deepcopy as copy
from typing import Union

import numpy as np
import pandas as pd


def create_variable(obj, name_suffix, value):
    var_name = f"{obj.name}_{name_suffix}"
    var_value = value
    obj.variables.append(
        {"name": var_name, "value": var_value, "description": f"Net name = {obj.net_name}"},
    )
    return var_name


class Trace:

    def __init__(self,
                 p_via,
                 name,
                 net_name,
                 layer,
                 width,
                 clearance,
                 incremental_path: list[list],
                 flip_dx,
                 flip_dy,
                 end_cap_style,
                 port: Union[dict, None]):
        self.p_via = p_via
        self.variables = []
        self.name = name
        self.net_name = net_name
        self.layer = layer
        self.width = create_variable(self, "width", width)
        self.clearance = create_variable(self, "clearance", clearance)
        self.flip_dx = flip_dx
        self.flip_dy = flip_dy
        self.end_cap_style = end_cap_style
        self.port = port

        self.voids = []

        self.incremental_path = [
            i if idx == 0 else [f"{i[0]}*{-1 if self.flip_dx else 1}", f"{i[1]}*{-1 if self.flip_dy else 1}"] for idx, i
            in enumerate(incremental_path)]

        self.path = [self.incremental_path[0]]
        x, y = self.incremental_path[0]
        for x0, y0 in self.incremental_path[1:]:
            x = f"{x}+({x0})"
            y = f"{y}+({y0})"
            self.path.append([x, y])

    def populate_config(self, cfg):
        cfg["variables"].extend(self.variables)
        trace = {"name": self.name,
                 "layer": self.layer,
                 "width": self.width,
                 # "incremental_path": self.incremental_path,
                 "path": self.path,
                 "net_name": self.net_name,
                 "start_cap_style": "round",
                 "end_cap_style": self.end_cap_style,
                 "corner_style": "round"}
        cfg["modeler"]["traces"].append(trace)

        trace_void = copy(trace)
        trace_void["name"] = f"{self.name}_void"
        trace_void["width"] = f"{self.width}+2*{self.clearance}"
        trace_void["end_cap_style"] = "round"
        cfg["modeler"]["traces"].append(trace_void)
        self.voids.append(trace_void)

        if self.port is not None:
            port = self.get_port_cfg()
            cfg["ports"].append(port)

    def get_port_cfg(self):
        return {
            "name": f"port_{self.name}",
            "type": "wave_port",
            "primitive_name": self.name,
            "point_on_edge": self.path[-1],
            "horizontal_extent_factor": self.port["horizontal_extent_factor"],
            "vertical_extent_factor": self.port["vertical_extent_factor"],
            "pec_launch_width": "0.02mm",
        }


class Signal:
    """vias and traces."""

    class GroundVia:

        @property
        def x(self):
            return f"{self.base_x}+{self.dx}"

        @property
        def y(self):
            return f"{self.base_y}+{self.dy}"

        @property
        def voids(self):
            voids = self._voids
            for trace in self.traces:
                voids.extend(trace.voids)
            return voids

        def __init__(self,
                     p_signal,
                     name,
                     net_name,
                     padstack_def,
                     start_layer,
                     stop_layer,
                     base_x,
                     base_y,
                     dx,
                     dy,
                     flip_dx,
                     flip_dy,
                     connection_trace: Union[dict, Trace],
                     with_solder_ball,
                     backdrill_parameters,
                     conductor_layers: list
                     ):
            self.p_signal = p_signal
            self.variables = []
            self.name = name
            self.net_name = net_name
            self.padstack_def = padstack_def
            self.start_layer = start_layer
            self.stop_layer = stop_layer
            self.base_x = base_x
            self.base_y = base_y

            var_dx = create_variable(self, "dx", dx)
            var_dy = create_variable(self, "dy", dy)
            self.flip_dx = flip_dx
            self.flip_dy = flip_dy
            self.dx = var_dx if flip_dx is False else f"-1*({var_dx})"
            self.dy = var_dy if flip_dy is False else f"-1*({var_dy})"
            self.with_solder_ball = with_solder_ball
            self.backdrill_parameters = backdrill_parameters
            self.conductor_layers = conductor_layers

            self.traces = []
            self.fanout_traces = []
            self._voids = []

            if connection_trace is not None:
                trace = Trace(
                    p_via=self,
                    name=f"{self.name}_trace",
                    net_name=self.net_name,
                    layer=self.stop_layer,
                    width=connection_trace["width"],
                    clearance=connection_trace["clearance"],
                    incremental_path=[[base_x, base_y], [var_dx, var_dy]],
                    flip_dx=flip_dx,
                    flip_dy=flip_dy,
                    end_cap_style="round",
                    port=None
                )
                self.traces.append(trace)

        def populate_config(self, cfg):
            cfg["variables"].extend(self.variables)

            for trace in self.traces:
                trace.populate_config(cfg)

            for trace in self.fanout_traces:
                trace.populate_config(cfg)

            padstack_instance = {
                "name": self.name,
                "definition": self.padstack_def,
                "layer_range": [self.start_layer, self.stop_layer],
                "position": [self.x, self.y],
                "net_name": self.net_name,
            }
            if self.with_solder_ball:
                padstack_instance["solder_ball_layer"] = self.start_layer
                padstack_instance["solder_ball_width"] = self.dx
            if self.backdrill_parameters is not None:
                padstack_instance["backdrill_parameters"] = self.backdrill_parameters

            cfg["modeler"]["padstack_instances"].append(padstack_instance)

    class Via(GroundVia):
        def __init__(self, anti_pad_diameter, fanout_trace: Union[dict, Trace], **kwargs):
            super().__init__(**kwargs)

            self.anti_pad_diameter = create_variable(self, "anti_pad_diameter", anti_pad_diameter)
            if fanout_trace is not None:
                layer = fanout_trace["layer"]

                incremental_path = copy([[self.x, self.y]])
                incremental_path.extend(fanout_trace["incremental_path"])

                trace = Trace(
                    p_via=self,
                    name=f"{self.net_name}_{layer}_fanout",
                    net_name=self.net_name,
                    layer=layer,
                    width=fanout_trace["width"],
                    clearance=fanout_trace["clearance"],
                    incremental_path=incremental_path,
                    flip_dx=self.flip_dx,
                    flip_dy=self.flip_dy,
                    end_cap_style=fanout_trace["end_cap_style"],
                    port=fanout_trace["port"]
                )

                self.fanout_traces.append(trace)

        def populate_config(self, cfg):
            super().populate_config(cfg)
            if self.start_layer == self.stop_layer:
                anti_pad = {
                    "type": "circle",
                    "name": f"{self.name}_anti_pad_{self.start_layer}",
                    "layer": self.start_layer,
                    "net_name": self.net_name,
                    "position": [self.x, self.y],
                    "radius": f"{self.anti_pad_diameter}/2",
                }
                cfg["modeler"]["planes"].append(anti_pad)
                self.voids.append(anti_pad)
            else:
                start_layer_idx = self.conductor_layers.index(self.start_layer)
                stop_layer_idx = self.conductor_layers.index(self.stop_layer)
                for i in np.arange(start_layer_idx, stop_layer_idx + 1):
                    anti_pad = {
                        "type": "circle",
                        "name": f"{self.name}_anti_pad_{self.conductor_layers[i]}",
                        "layer": self.conductor_layers[i],
                        "net_name": self.net_name,
                        "position": [self.x, self.y],
                        "radius": f"{self.anti_pad_diameter}/2",
                    }
                    cfg["modeler"]["planes"].append(anti_pad)
                    self.voids.append(anti_pad)

    @property
    def voids(self):
        voids = []
        for via in self.vias:
            voids.extend(via.voids)
        return voids

    def __init__(self, p_board, signal_name, name_suffix: Union[None, str], base_x, base_y, stacked_vias,
                 invert_flip_dx, invert_flip_dy):
        self.p_board = p_board
        self.net_name = signal_name if name_suffix is None else f"{signal_name}_{name_suffix}"
        self.name_suffix = name_suffix
        self.base_x = base_x
        self.base_y = base_y

        self.vias = []
        x = self.base_x
        y = self.base_y
        for i in stacked_vias:
            dx = i['dx']
            dy = i["dy"]

            connection_trace = i["connection_trace"]
            start_layer = i["start_layer"]
            stop_layer = i["stop_layer"]

            flip_x_1 = not i["flip_dx"] if invert_flip_dx else i["flip_dx"]
            flip_y_1 = not i["flip_dy"] if invert_flip_dy else i["flip_dy"]
            if i["padstack_def"].startswith("BGA"):
                flip_x_1 = False
                flip_y_1 = False

            if self.net_name.startswith("GND"):
                via = self.GroundVia(
                    p_signal=self,
                    name=f"{self.net_name}_{start_layer}_{stop_layer}",
                    net_name=self.net_name,
                    padstack_def=i["padstack_def"],
                    start_layer=start_layer,
                    stop_layer=stop_layer,
                    base_x=x,
                    base_y=y,
                    dx=dx,
                    dy=dy,
                    flip_dx=flip_x_1,
                    flip_dy=flip_y_1,
                    connection_trace=connection_trace,
                    with_solder_ball=i["with_solder_ball"],
                    backdrill_parameters=i["backdrill_parameters"],
                    conductor_layers=self.p_board.conductor_layers,
                )
            else:
                via = self.Via(p_signal=self,
                               name=f"{self.net_name}_{start_layer}_{stop_layer}",
                               net_name=self.net_name,
                               padstack_def=i["padstack_def"],
                               start_layer=start_layer,
                               stop_layer=stop_layer,
                               base_x=x,
                               base_y=y,
                               anti_pad_diameter=i["anti_pad_diameter"],
                               dx=dx,
                               dy=dy,
                               flip_dx=flip_x_1,
                               flip_dy=flip_y_1,
                               connection_trace=connection_trace,
                               with_solder_ball=i["with_solder_ball"],
                               backdrill_parameters=i["backdrill_parameters"],
                               fanout_trace=i["fanout_trace"],
                               conductor_layers=self.p_board.conductor_layers,
                               )
            x = via.x
            y = via.y

            self.vias.append(via)

    def populate_config(self, cfg_modeler):
        for i in self.vias:
            i.populate_config(cfg_modeler)


class DiffSignal:
    def __init__(self, p_board, name, signals, fanout_trace, stacked_vias):
        self.p_board = p_board
        self.name = name
        self.signal_p_name, self.signal_n_name = signals
        self.fanout_trace = fanout_trace
        self.stacked_vias = stacked_vias

        self.variables = []
        self.voids = []
        self.diff_ports = []

        p_x, p_y = self.p_board.get_signal_location(self.signal_p_name)[0]
        n_x, n_y = self.p_board.get_signal_location(self.signal_n_name)[0]
        p_x = f"{p_x}*pitch"
        p_y = f"{p_y}*pitch"
        n_x = f"{n_x}*pitch"
        n_y = f"{n_y}*pitch"

        vars_sep = {}
        for idx, trace in self.fanout_trace.items():
            trace2 = {}
            trace2["layer"] = trace["layer"]
            trace2["width"] = trace["width"]
            trace2["clearance"] = trace["clearance"]
            trace2["end_cap_style"] = trace["end_cap_style"]
            trace2["port"] = trace["port"]

            incremental_path_dy = trace["incremental_path_dy"]
            incremental_path = [[0, incremental_path_dy[0]], [0, incremental_path_dy[1]]]
            trace2["incremental_path"] = incremental_path

            self.stacked_vias[idx]["fanout_trace"] = trace2

            var_separation = f"{self.name}_{trace['layer']}_fanout_separation"
            self.variables.append(
                {"name": var_separation, "value": trace["separation"]},
            )
            vars_sep[trace["layer"]] = var_separation

        stacked_vias_reversed = list(reversed(stacked_vias))

        pcb_fanout_center = f"{p_x}+pitch/2"
        pkg_fanout_center = f"{p_x}+pitch"
        # fanout_x = f"{diff_center}-({var_separation})/2"

        self.signal_p = Signal(
            p_board=self.p_board,
            signal_name=self.name,
            name_suffix="P",
            base_x=p_x,
            base_y=p_y,
            stacked_vias=stacked_vias_reversed,
            invert_flip_dx=False,
            invert_flip_dy=False,
        )

        diff_ports = {}
        for v in self.signal_p.vias:
            for t in v.fanout_traces:
                var_sep = vars_sep[t.layer]
                if t.layer.startswith("PCB"):
                    t.path[1][0] = f"{pcb_fanout_center}-{var_sep}"
                    t.path[2][0] = f"{pcb_fanout_center}-{var_sep}"
                else:
                    t.path[1][0] = f"{pkg_fanout_center}-{var_sep}"
                    t.path[2][0] = f"{pkg_fanout_center}-{var_sep}"

        self.signal_n = Signal(
            p_board=self.p_board,
            signal_name=self.name,
            name_suffix="N",
            base_x=n_x,
            base_y=n_y,
            stacked_vias=stacked_vias_reversed,
            invert_flip_dx=True,
            invert_flip_dy=False,
        )
        for v in self.signal_n.vias:
            for t in v.fanout_traces:
                var_sep = vars_sep[t.layer]
                if t.layer.startswith("PCB"):
                    t.path[1][0] = f"{pcb_fanout_center}+{var_sep}"
                    t.path[2][0] = f"{pcb_fanout_center}+{var_sep}"
                else:
                    t.path[1][0] = f"{pkg_fanout_center}+{var_sep}"
                    t.path[2][0] = f"{pkg_fanout_center}+{var_sep}"

        for v_idx, v in enumerate(self.signal_p.vias):
            for t_idx, t_p in enumerate(v.fanout_traces):
                port_p = t_p.get_port_cfg()
                t_p.port = None
                t_n = self.signal_n.vias[v_idx].fanout_traces[t_idx]
                port_n = t_n.get_port_cfg()
                t_n.port = None
                pattern = r'^(.*)_([NPnp])_(.*)$'
                m1 = re.match(pattern, port_p["name"])

                diff_port = {
                    "name": f"{m1.group(1)}_{m1.group(3)}",
                    "type": "diff_wave_port",
                    "positive_terminal": {"primitive_name": port_p["primitive_name"], "point_on_edge": port_p["point_on_edge"]},
                    "negative_terminal": {"primitive_name": port_n["primitive_name"], "point_on_edge": port_n["point_on_edge"]},
                    "horizontal_extent_factor": port_p["horizontal_extent_factor"],
                    "vertical_extent_factor": port_n["vertical_extent_factor"],
                    "pec_launch_width": "0,2mm",
                }
                self.diff_ports.append(diff_port)

    def populate_config(self, cfg):
        cfg["variables"].extend(self.variables)
        self.signal_p.populate_config(cfg)
        self.voids.extend(self.signal_p.voids)
        self.signal_n.populate_config(cfg)
        self.voids.extend(self.signal_n.voids)
        cfg["ports"].extend(self.diff_ports)


class Board:
    @property
    def conductor_layers(self):
        return [i["name"] for i in self.stackup if i["type"] == "signal"]

    def __init__(self, stackup, padstack_defs, outline_extent, pitch, pin_map, signals, differential_signals):
        self.variables = [{"name": "pitch", "value": pitch, "description": ""}]

        self.stackup = stackup
        self.padstack_defs = padstack_defs
        self.outline_extent = outline_extent

        self.pin_map = pin_map
        self.signals = self.parser_signals(signals) if signals is not None else []
        self.differential_signals = self.parser_differential_signals(
            differential_signals) if differential_signals is not None else []

    def get_signal_location(self, signal_name):
        pin_map = pd.DataFrame(self.pin_map)
        temp = (pin_map == signal_name).stack()
        xy = [[i[1], i[0]] for i in temp[temp].index.tolist()]
        return xy

    def parser_signals(self, data):
        signals = []

        for name, signal_data in data.items():
            fanout = signal_data["fanout_trace"]
            stacked_vias = signal_data["stacked_vias"]
            for idx, f in fanout.items():
                stacked_vias[idx]["fanout_trace"] = f

            stacked_vias_reversed = list(reversed(stacked_vias))
            for x, y in self.get_signal_location(name):
                s = Signal(
                    p_board=self,
                    signal_name=name,
                    name_suffix=None,
                    base_x=f"{x}*pitch",
                    base_y=f"{y}*pitch",
                    stacked_vias=stacked_vias_reversed,
                    invert_flip_dx=False,
                    invert_flip_dy=False,
                )
                signals.append(s)
        return signals

    def parser_differential_signals(self, data):
        diff_signals = []
        for name, temp in data.items():
            signals = temp["signals"]
            fanout_trace = temp["fanout_trace"]
            stacked_vias = temp["stacked_vias"]
            diff_signal = DiffSignal(self, name, signals, fanout_trace, stacked_vias)
            diff_signals.append(diff_signal)
        return diff_signals

    def populate_config(self, cfg):
        cfg["variables"].extend(self.variables)

        cfg["stackup"]["layers"] = self.stackup
        for p in self.padstack_defs:
            regular_pad = []
            for layer in self.conductor_layers:
                regular_pad.append({
                    "layer_name": layer,
                    "shape": "circle",
                    "diameter": p["pad_diameter"],
                })
            pdef = {
                "name": p["name"],
                "material": "copper",
                "hole_range": "upper_pad_to_lower_pad",
                "pad_parameters": {"regular_pad": regular_pad},
                "hole_parameters": {
                    "shape": "circle",
                    "diameter": p["hole_diameter"],
                },
            }
            cfg["modeler"]["padstack_definitions"].append(pdef)

        voids = []
        for signal in self.signals:
            signal.populate_config(cfg)
            voids.extend(signal.voids)

        for diff_signal in self.differential_signals:
            diff_signal.populate_config(cfg)
            voids.extend(diff_signal.voids)

        matrix = np.array(self.pin_map)
        y_size_count, x_size_count = matrix.shape
        x_lower_left = f"-1*({self.outline_extent})"
        x_upper_right = f"({self.outline_extent})+{x_size_count}*pitch"
        y_lower_left = f"-1*({self.outline_extent})"
        y_upper_right = f"({self.outline_extent})+{y_size_count}*pitch"
        for l in self.conductor_layers:
            p = {
                "type": "rectangle",
                "name": f"GND_{l}",
                "layer": l,
                "net_name": "GND",
                "lower_left_point": [x_lower_left, y_lower_left],
                "upper_right_point": [x_upper_right, y_upper_right],
                "voids": []
            }
            for v in voids:
                if v["layer"] == l:
                    p["voids"].append(v["name"])
            cfg["modeler"]["planes"].append(p)
        return
