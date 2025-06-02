from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgBoundaries:
    open_region: bool = True
    open_region_type: str = "radiation"
    pml_visible: bool = False
    pml_operation_frequency: str = "5ghz"
    pml_radiation_factor: int = 10
    dielectric_extents_type: str = "bounding_box"
    dielectric_base_polygon: str = ""
    horizontal_padding: float = 0
    honor_primitives_on_dielectric_layers: bool = True
    air_box_extents_type: str = "bounding_box"
    air_box_base_polygon: str = ""
    air_box_truncate_model_ground_layers: bool = False
    air_box_horizontal_padding: float = 0.15
    air_box_positive_vertical_padding: float = 1
    air_box_negative_vertical_padding: float = 1
