from dataclasses import dataclass


@dataclass
class CfgGeneral:
    spice_model_library: str = ""
    s_parameter_library: str = ""

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass
