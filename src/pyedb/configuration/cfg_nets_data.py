from dataclasses import dataclass


@dataclass
class CfgNets:
    power_ground_nets: list[str]
    signal_nets: list[str]

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass
