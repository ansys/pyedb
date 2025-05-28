from dataclasses import dataclass


@dataclass
class CfgNets:
    power_ground_nets: list[str] = "default_factory"
    signal_nets: list[str] = "default_factory"
