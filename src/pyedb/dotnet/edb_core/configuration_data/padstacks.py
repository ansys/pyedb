from enum import Enum


class Padstacks:
    def __init__(self, pedb, padstack_dict):
        self._pedb = pedb
        self._definitions_dict = padstack_dict.get("definitions", None)
        self._instances_dict = padstack_dict.get("instances", None)
        self.definitions = {}
        self.instances = {}
        self._update()

    def _update(self):
        if self._definitions_dict:
            for def_name, definition_dict in self._definitions_dict.items():
                if not def_name in self.definitions:
                    self.definitions[def_name] = Definition(self._pedb, definition_dict)
        if self._instances_dict:
            for inst_name, inst_dict in self._instances_dict.items():
                if not inst_name in self.instances:
                    self.instances[inst_name] = Instance(self._pedb, inst_dict)


class Definition:
    def __init__(self, pedb, definition_dict):
        self._pedb = pedb
        self.definition = definition_dict
        self.name = self.definition["name"]
        self.hole_diameter = self.definition["hole_diameter"]
        self.hole_plating_thickness = self.definition["hole_plating_thickness"]
        self.hole_material = self.definition["hole_material"]
        self.hole_range = self.definition["hole_range"]

    def apply(self):
        padstack_defs = self._pedb.padstacks.definitions
        pdef = padstack_defs[self.name]
        pdef.hole_diameter = self.hole_diameter
        pdef.hole_plating_thickness = self.hole_plating_thickness
        pdef.material = self.hole_material
        pdef.hole_range = self.hole_range


class BackDrill:
    def __init__(self, backdrill_dict):
        self.backdrill_type = self.BackDrillType.BOTTOM
        self.drill_to_layer = backdrill_dict["drill_to_layer"]
        self.drill_diameter = backdrill_dict["drill_diameter"]
        self.stub_length = backdrill_dict["stub_length"]

    class BackDrillType(Enum):
        BOTTOM = 0
        TOP = 1


class Instance:
    def __init__(self, pedb, instances_dict):
        self._pedb = pedb
        self.instance = instances_dict
        self.name = self.instance["name"]
        self.backdrill_top = self.instance["backdrill_top"]
        self.backdrill_top = None
        self.backdrill_bottom = None
        self._update()

    def _update(self):
        backdrill_top = self.instance.get("backdrill_top", None)
        if backdrill_top:
            self.backdrill_top = BackDrill(backdrill_top).BackDrillType.TOP
        backdrill_bottom = self.instance.get("backdrill_bottom", None)
        if backdrill_top:
            self.backdrill_bottom = BackDrill(backdrill_bottom)

    def apply(self):
        padstack_instances = self._pedb.padstacks.instances_by_name
        inst = padstack_instances[self.name]
        if self.backdrill_top:
            inst.set_backdrill_top(
                self.backdrill_top.drill_to_layer, self.backdrill_top.drill_diameter, self.backdrill_top.stub_length
            )
        if self.backdrill_bottom:
            inst.set_backdrill_bottom(
                self.backdrill_bottom.drill_to_layer,
                self.backdrill_bottom.drill_diameter,
                self.backdrill_bottom.stub_length,
            )
