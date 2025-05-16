from copy import deepcopy as copy


class Signal:
    """vias and traces."""

    class Via:

        class Trace:
            def __init__(self, name, net_name, layer, width, clearance, incremental_path: list[list], end_cap_style="round"):
                self.name = name
                self.net_name = net_name
                self.layer = layer
                self.width = width
                self.clearance = clearance
                self.incremental_path = incremental_path
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
        def flipped_dx(self):
            return f"{self.dx}*{self.flip_dx}"

        @property
        def base_x(self):
            return f"{self.x}+{self.flipped_dx}"

        @property
        def base_y(self):
            return f"{self.y}+{self.dy}"

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
                     anti_pad_diameter,
                     x,
                     y,
                     dx,
                     dy,
                     flip_dx,
                     trace=None):
            self.name = name
            self.net_name = net_name,
            self.padstack_def = padstack_def
            self.start_layer = start_layer
            self.stop_layer = stop_layer
            self.anti_pad_diameter = anti_pad_diameter
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            self.flip_dx = -1 if flip_dx else 1

            self.traces = []

            if trace is not None:
                trace = self.Trace(
                    f"{self.name}_trace",
                    self.net_name,
                    self.stop_layer,
                    trace["width"],
                    trace["clearance"],
                    [[x, y], [self.flipped_dx, dy]]
                )
                self.traces.append(trace)

        def create(self, cfg_modeler):
            for trace in self.traces:
                trace.create(cfg_modeler)
            padstack = # todo

    @property
    def voids(self):
        voids = []
        for via in self.vias:
            voids.extend(via.voids)
        return voids

    def __init__(self, net_name, base_x, base_y, stacked_vias, flip_dx=False):
        self.net_name = net_name
        self.base_x = base_x
        self.base_y = base_y

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
                           anti_pad_diameter=i["antipad_diameter"],
                           x=x,
                           y=y,
                           dx=dx,
                           dy=dy,
                           flip_dx=flip_dx,
                           trace=trace
                           )
            x = via.base_x
            y = via.base_y

            self.vias.append(via)

    def create(self, cfg_modeler):
        for i in self.vias:
            i.create(cfg_modeler)


class DiffSignal:

    def __init__(self, name, px, py, nx, ny, stacked_vias):
        self.name = name
        self.px = px
        self.py = py
        self.nx = nx
        self.ny = ny

        self.via_p = Signal(f"{name}_P", px, py, stacked_vias, False)
        self.via_n = Signal(f"{name}_N", nx, ny, stacked_vias, True)
