from dataclasses import dataclass


@dataclass
class CfgPinPair:
    type: str
    p1: str = "1"
    p2: str = "2"
    capacitance = ""
    inductance = ""
    resistance = ""

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgSolderBallProperties:
    shape: str = "cylinder"
    diameter: str = "150um"
    height: str = "100um"

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgPortProperties:
    reference_offset: float = 0
    reference_size_auto: bool = True
    reference_size_x: float = 0.0
    reference_size_y: float = 0.0

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgComponents:
    reference_designator: str
    part_type: str
    enabled: bool
    rlc_model: dict[str, list[CfgPinPair]]
    solder_ball_properties: CfgSolderBallProperties
    port_properties: CfgPortProperties

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass
