from dataclasses import dataclass


@dataclass
class CfgSpiceModelLib:
    spice_model_library: str


@dataclass
class CfgSpiceModel:
    name: str
    component_definition: str
    file_path: str
    sub_circuit_name: str
    apply_to_all: bool
    components: [str]


@dataclass
class CfgSpiceModels:
    general: CfgSpiceModelLib = None
    spice_models: list[CfgSpiceModel] = "default_factory"
