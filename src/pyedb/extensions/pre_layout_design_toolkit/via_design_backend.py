import os
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


class TraceBase:
    @property
    def path(self):
        path = [self.incremental_path[0]]
        x, y = self.incremental_path[0]
        for x0, y0 in self.incremental_path[1:]:
            x = f"{x}+({x0})"
            y = f"{y}+({y0})"
            path.append([x, y])
        return path

    def __init__(self,
                 p_via,
                 name,
                 net_name,
                 layer,
                 width,
                 clearance,
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

    def populate_config(self, cfg):
        cfg["variables"].extend(self.variables)
        trace = {"name": self.name,
                 "layer": self.layer,
                 "width": self.width,
                 "incremental_path": self.incremental_path,
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
            port = {
                "name": f"port_{self.name}",
                "type": "wave_port",
                "primitive_name": self.name,
                "point_on_edge": self.path[-1],
                "horizontal_extent_factor": self.port["horizontal_extent_factor"],
                "vertical_extent_factor": self.port["vertical_extent_factor"],
                "pec_launch_width": "0.02mm",
            }
            cfg["ports"].append(port)


class Trace(TraceBase):

    def __init__(self, incremental_path: list[list], **kwargs):
        super().__init__(**kwargs)

        self.incremental_path = [
            i if idx == 0 else [f"{i[0]}*{-1 if self.flip_dx else 1}", f"{i[1]}*{-1 if self.flip_dy else 1}"] for idx, i
            in enumerate(incremental_path)]


class DiffTraceVertical(TraceBase):
    @property
    def incremental_path(self):
        temp = [[self.p_via.x, self.p_via.y]]

        if self.p_via.p_signal.is_positive:
            dx = f"pitch-abs({self.p_via.x}-{self.p_via.p_signal.base_x})-{self.width}/2-{self.separation}/2"
        else:
            dx = f"abs({self.p_via.x}-{self.p_via.p_signal.base_x})-{self.width}/2-{self.separation}/2"
        dx = f"({dx})*{-1 if self.flip_dx else 1}"
        temp.append([
            dx,
            self.p_via.y
        ]
        )
        temp.append([0, self.incremental_path_dy[1]])
        return temp

    def __init__(self, separation, incremental_path_dy, **kwargs):
        super().__init__(**kwargs)
        self.separation = create_variable(self, "separation", separation)
        self.incremental_path_dy = incremental_path_dy


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
                if not fanout_trace["is_differential"]:
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
                else:
                    trace = DiffTraceVertical(
                        p_via=self,
                        name=f"{self.net_name}_{layer}_fanout",
                        net_name=self.net_name,
                        layer=layer,
                        width=fanout_trace["width"],
                        clearance=fanout_trace["clearance"],
                        flip_dx=self.flip_dx,
                        flip_dy=self.flip_dy,
                        end_cap_style=fanout_trace["end_cap_style"],
                        port=fanout_trace["port"],
                        separation=fanout_trace["separation"],
                        incremental_path_dy=fanout_trace["incremental_path_dy"],
                    )
                self.traces.append(trace)

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

    def __init__(self, signal_name, name_suffix: Union[None, str], base_x, base_y, stacked_vias,
                 conductor_layers, invert_flip_dx, invert_flip_dy, is_positive):
        self.is_positive = is_positive
        self.net_name = signal_name if name_suffix is None else f"{signal_name}_{name_suffix}"
        self.name_suffix = name_suffix
        self.base_x = base_x
        self.base_y = base_y
        self.conductor_layers = conductor_layers

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
                    conductor_layers=self.conductor_layers,
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
                               conductor_layers=self.conductor_layers,
                               )
            x = via.x
            y = via.y

            self.vias.append(via)

    def populate_config(self, cfg_modeler):
        for i in self.vias:
            i.populate_config(cfg_modeler)


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
                    signal_name=f"{name}",
                    name_suffix=None,
                    base_x=f"{x}*pitch",
                    base_y=f"{y}*pitch",
                    stacked_vias=stacked_vias_reversed,
                    conductor_layers=self.conductor_layers,
                    invert_flip_dx=False,
                    invert_flip_dy=False,
                    is_positive=True,
                )
                signals.append(s)
        return signals

    def parser_differential_signals(self, data):
        signals = []
        for pair_name, signal_data in data.items():
            signal_p_name, signal_n_name = signal_data["signals"]
            fanout = signal_data["fanout_trace"]
            p_x, p_y = self.get_signal_location(signal_p_name)[0]
            n_x, n_y = self.get_signal_location(signal_n_name)[0]
            stacked_vias = signal_data["stacked_vias"]
            for idx, f in fanout.items():
                stacked_vias[idx]["fanout_trace"] = f
            stacked_vias_reversed = list(reversed(stacked_vias))

            signal_p = Signal(
                signal_name=pair_name,
                name_suffix="P",
                base_x=f"{p_x}*pitch",
                base_y=f"{p_y}*pitch",
                stacked_vias=stacked_vias_reversed,
                conductor_layers=self.conductor_layers,
                invert_flip_dx=False,
                invert_flip_dy=False,
                is_positive=True,
            )
            signals.append(signal_p)
            signal_n = Signal(
                signal_name=pair_name,
                name_suffix="N",
                base_x=f"{n_x}*pitch",
                base_y=f"{n_y}*pitch",
                stacked_vias=stacked_vias_reversed,
                conductor_layers=self.conductor_layers,
                invert_flip_dx=True,
                invert_flip_dy=False,
                is_positive=False
            )
            signals.append(signal_n)
        return signals

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

        for signal in self.differential_signals:
            signal.populate_config(cfg)
            voids.extend(signal.voids)

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
