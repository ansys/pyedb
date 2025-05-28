from dataclasses import dataclass


@dataclass
class CfgSparameter:
    name: str
    component_definition: str
    file_path: str
    apply_to_all: bool
    components: list[str]
    reference_net: str
    reference_net_per_component: dict[str, str]


@dataclass
class CfgSparameters:
    general: dict[str, str] = "default_factory"
    s_parameters: list[CfgSparameter] = "default_factory"
