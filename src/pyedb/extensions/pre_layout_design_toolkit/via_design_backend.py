from copy import deepcopy as copy
from typing import Union


class Signal:
    """vias and traces."""

    class Via:

        class Trace:
            def __init__(self, name, net_name, layer, width, clearance, incremental_path: list[list],
                         flip_dx=False,
                         flip_dy=False,
                         end_cap_style="round"):
                self.name = name
                self.net_name = net_name
                self.layer = layer
                self.width = width
                self.clearance = clearance
                self.incremental_path = [
                    i if idx == 0 else [f"{i[0]}*{-1 if flip_dx else 1}", f"{i[1]}*{-1 if flip_dy else 1}"] for idx, i
                    in enumerate(incremental_path)]
                self.end_cap_style = end_cap_style

                self.voids = []

            def create(self, cfg_modeler):
                trace = {"name": self.name,
                         "layer": self.layer,
                         "width": self.width,
                         "incremental_path": self.incremental_path,
                         "net_name": self.net_name,
                         "start_cap_style": "round",
                         "end_cap_style": self.end_cap_style,
                         "corner_style": "round"}
                cfg_modeler["traces"].append(trace)
                trace_void = copy(trace)
                trace_void["name"] = f"{self.name}_void"
                trace_void["width"] = f"{self.width}+2*{self.clearance}"
                cfg_modeler["traces"].append(trace_void)
                self.voids.append(trace_void)

        @property
        def x(self):
            return f"{self.base_x}+{self.dx}"

        @property
        def y(self):
            return f"{self.base_y}+{self.dy}"

        @property
        def voids(self):
            voids = []
            for trace in self.traces:
                voids.extend(trace.voids)
            return voids

        def __init__(self,
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
                     connection_trace: Union[dict, Trace] = None,
                     with_solder_ball=False,
                     backdrill_parameters=None,
                     fanout_trace: Union[dict, Trace] = None):
            self.name = name
            self.net_name = net_name,
            self.padstack_def = padstack_def
            self.start_layer = start_layer
            self.stop_layer = stop_layer
            self.base_x = base_x
            self.base_y = base_y
            self.dx = dx if flip_dx else f"-1*{dx}"
            self.dy = dy if flip_dy else f"-1*{dy}"
            self.with_solder_ball = with_solder_ball
            self.backdrill_parameters = backdrill_parameters

            self.traces = []

            if connection_trace is not None:
                trace = self.Trace(
                    f"{self.name}_trace",
                    self.net_name,
                    self.stop_layer,
                    connection_trace["width"],
                    connection_trace["clearance"],
                    [[base_x, base_y], [dx, dy]],
                    flip_dx=flip_dx,
                    flip_dy=flip_dy
                )
                self.traces.append(trace)
            if fanout_trace is not None:
                trace = self.Trace(
                    f"{self.name}_fanout_trace",
                    self.net_name,
                    self.stop_layer,
                    fanout_trace["width"],
                    fanout_trace["clearance"],
                    fanout_trace["incremental_path"],
                    flip_dx=fanout_trace["flip_dx"],
                    flip_dy=fanout_trace["flip_dy"],
                    end_cap_style="flat"
                )
                self.traces.append(trace)

        def create(self, cfg_modeler):
            for trace in self.traces:
                trace.create(cfg_modeler)
            padstack_instances = {
                "name": self.name,
                "definition": self.padstack_def,
                "layer_range": [self.start_layer, self.stop_layer],
                "position": [self.x, self.y],
                "net_name": self.net_name,
            }
            if self.with_solder_ball:
                padstack_instances["solder_ball_layer"] = self.start_layer
                padstack_instances["solder_ball_width"] = self.dx
            if self.backdrill_parameters is not None:
                padstack_instances["backdrill_parameters"] = self.backdrill_parameters

            cfg_modeler["padstacks"]["instances"].append(padstack_instances)

    @property
    def voids(self):
        voids = []
        for via in self.vias:
            voids.extend(via.voids)
        return voids

    def __init__(self, net_name, base_x, base_y, stacked_vias, padstack_def=None, flip_dx=False):
        self.net_name = net_name
        self.base_x = base_x
        self.base_y = base_y
        self.padstack_def = padstack_def

        self.vias = []
        x = self.base_x
        y = self.base_y
        for i in stacked_vias:
            dx = i['dx']
            dy = i["dy"]

            trace = i.get("trace")
            start_layer = i["start_layer"]
            stop_layer = i["stop_layer"]

            via = self.Via(name=f"{self.net_name}_{start_layer}_{stop_layer}",
                           net_name=self.net_name,
                           padstack_def=i["padstack_def"],
                           start_layer=start_layer,
                           stop_layer=stop_layer,
                           base_x=x,
                           base_y=y,
                           dx=dx,
                           dy=dy,
                           flip_dx=flip_dx,
                           flip_dy=False,
                           connection_trace=trace
                           )
            x = via.x
            y = via.y

            self.vias.append(via)

    def create(self, cfg_modeler):
        for i in self.padstack_def:
            cfg_modeler["padstacks"]["definitions"].append(i)
        for i in self.vias:
            i.create(cfg_modeler)


class DiffSignal:

    def __init__(self, name, px, py, nx, ny, stacked_vias, padstack_def):
        self.name = name
        self.px = px
        self.py = py
        self.nx = nx
        self.ny = ny

        self.via_p = Signal(f"{name}_P", px, py, stacked_vias, padstack_def, False)
        self.via_n = Signal(f"{name}_N", nx, ny, stacked_vias, padstack_def, True)


class Board:
    def __init__(self):
        pass
