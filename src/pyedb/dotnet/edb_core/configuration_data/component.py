from enum import Enum


class RlcModel:
    def __init__(self):
        self.resistance = 50.0
        self.inductance = 0.0
        self.capacitance = 0.0
        self.rlc_model_type = self.RlcModelType.SERIES
        self.enabled = False
        self.pin_pairs = []

    class RlcModelType(Enum):
        SERIES = 0
        PARALLEL = 1


class PortProperties:
    def __init__(self):
        self.ref_offset = 0.0
        self.ref_size_auto = True
        self.ref_size_x = 0.0
        self.ref_size_y = 0.0


class SolderBallsProperties:
    def __init__(self):
        self.shape = self.Shape.CYLINDER
        self.diameter = 0.0
        self.mid_diameter = 0.0
        self.height = 0.0

    class Shape(Enum):
        CYLINDER = 0
        SPHEROID = 1


class Component:
    def __init__(self, pedb):
        self._pedb = pedb
        self.reference_designator = ""
        self.part_type = self.ComponentType.RESISTOR
        self.enabled = True
        self.rlc_model = RlcModel()
        self.port_properties = PortProperties()
        self.solder_balls_properties = SolderBallsProperties()

    class ComponentType(Enum):
        RESISTOR = 0
        INDUCTOR = 1
        CAPACITOR = 2
        IO = 3
        IC = 4
        OTHER = 5

    def _import_dict(self, comp_dict):
        part_type = comp_dict["part_type"].lower()
        if part_type == "resistor":
            self.part_type = self.part_type.RESISTOR
        elif part_type == "capacitor":
            self.part_type = self.part_type.CAPACITOR
        elif part_type == "inductor":
            self.part_type = self.part_type.INDUCTOR
        elif part_type == "io":
            self.part_type = self.part_type.IO
        elif part_type == "ic":
            self.part_type = self.part_type.IC
        else:
            self.part_type = self.part_type.OTHER

        if self.part_type in [0, 1, 2]:
            rlc_model = comp_dict["rlc_model"] if "rlc_model" in comp_dict else None
            if rlc_model:
                pin_pairs = rlc_model["pin_pairs"] if "pin_pairs" in rlc_model else None
                if pin_pairs:
                    for pp in pin_pairs:
                        if pp["type"] == "Parallel":
                            self.rlc_model.rlc_model_type = self.rlc_model.rlc_model_type.PARALLEL

                        self.rlc_model.pin_pairs.append(pp["p1"])
                        self.rlc_model.pin_pairs.append(pp["p2"])
                        self.rlc_model.resistance = pp["resistance"] if "resistance" in pp else None
                        self.rlc_model.inductance = pp["inductance"] if "inductance" in pp else None
                        self.rlc_model.capacitance = pp["capacitance"] if "capacitance" in pp else None

        port_properties = comp_dict["port_properties"] if "port_properties" in comp_dict else None
        if port_properties:
            self.port_properties.ref_offset = float(port_properties["reference_offset"])
            self.port_properties.ref_size_auto = bool(port_properties["reference_size_auto"])
            self.port_properties.ref_size_x = float(port_properties["reference_size_x"])
            self.port_properties.ref_size_y = float(port_properties["reference_size_y"])

        solder_ball_properties = comp_dict["solder_ball_properties"] if "solder_ball_properties" in comp_dict else None
        if solder_ball_properties:
            if solder_ball_properties["shape"].lower() == "spheroid":
                self.solder_balls_properties.shape = self.solder_balls_properties.shape.SPHEROID
            self.solder_balls_properties.diameter = float(solder_ball_properties["diameter"])
            self.solder_balls_properties.mid_diameter = (
                float(solder_ball_properties["mid_diameter"])
                if "mid_diameter" in solder_ball_properties
                else self.solder_balls_properties.diameter
            )
            self.solder_balls_properties.height = float(solder_ball_properties["height"])
