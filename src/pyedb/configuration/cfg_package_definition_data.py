from dataclasses import dataclass


@dataclass
class CfgHeatSink:
    fin_base_height: float
    fin_height: float
    fin_orientation: str
    fin_spacing: float
    fin_thickness: float

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgPackageDefinition:
    name: str
    component_definition: str
    maximum_power: float
    therm_cond: float
    theta_jb: float
    theta_jc: float
    height: float
    heatsink: CfgHeatSink

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass
