from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgCutout:
    signal_list: list[str] = field(default_factory=list)
    reference_list: list[str] = field(default_factory=list)
    extent_type: str = "ConvexHull"
    expansion_size: float = 0.002
    use_round_corner: bool = False
    output_aedb_path: str = ""
    open_cutout_at_end: bool = True
    use_pyaedt_cutout: bool = True
    number_of_threads: int = 4
    use_pyaedt_extent_computing: bool = True
    extent_defeature: float = 0.0
    remove_single_pin_components: bool = False
    custom_extent: str = ""
    custom_extent_units: str = "mm"
    include_partial_instances: bool = False
    keep_voids: bool = True
    check_terminals: bool = False
    include_pingroups: bool = False
    expansion_factor: float = 0.0
    maximum_iterations: int = 30
    preserve_components_with_model: bool = False
    simple_pad_check: bool = True
    keep_lines_as_path: bool = False


@dataclass_json
@dataclass
class CfgOperations:
    cutout: CfgCutout = None
