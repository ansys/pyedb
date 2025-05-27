from dataclasses import dataclass
from typing import Union


@dataclass
class CfgPinGroup:
    name: str
    reference_designator: str
    pins: list[str]
    net: Union[str, list[str]]

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgTerminal:
    pingroup: str

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgPorts:
    name: str
    type: str
    positive_terminal: CfgTerminal
    negative_terminal: CfgTerminal

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgSource:
    name: str
    type: str
    magnitude: float
    positive_terminal: CfgTerminal
    negative_terminal: CfgTerminal

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass


@dataclass
class CfgPinGroups:
    pin_groups: list[CfgPinGroup]
    ports: list[CfgPorts]
    sources: list[CfgSource]

    def _import_from_json(self):
        pass

    def _export_json(self):
        pass

    def _get_from_edb(self) -> bool:
        pass

    def _set_to_edb(self) -> bool:
        pass
