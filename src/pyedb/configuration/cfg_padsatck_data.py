from dataclasses import dataclass


@dataclass
class CfgDefinition:
    name: str
    hole_diameter: str
    hole_plating_thickness: str
    hole_material: str
    hole_range: str = "through"

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgBackDrillTop:
    drill_to_layer: str
    drill_diameter: str
    stub_length: str

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgBackDrillBottom:
    drill_to_layer: str
    drill_diameter: str
    stub_length: str

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgInstance:
    name: str
    backdrill_top: CfgBackDrillTop
    backdrill_bottom: CfgBackDrillBottom

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgPadStack:
    definitions: list[CfgDefinition]
    instances: list[CfgInstance]

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass
