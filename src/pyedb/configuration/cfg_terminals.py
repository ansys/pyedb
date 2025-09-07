from typing import Union, Optional, Dict, List, Literal

from pydantic import BaseModel


class CfgBase(BaseModel):
    model_config = {"populate_by_name": True,
                    "extra": "forbid", }


class CfgTerminal(CfgBase):
    name: str
    impedance: Union[float, int, str]
    is_circuit_port: bool
    reference_terminal: Optional[str] = None
    amplitude: Optional[Union[float, int, str]] = 1
    phase: Optional[Union[float, int, str]] = 0
    terminal_to_ground: Optional[Literal["kNoGround", "kNegative", "kPositive"]] = "kNoGround"
    boundary_type: Literal[
        "PortBoundary",
        "PecBoundary",
        "RlcBoundary",
        "kCurrentSource",
        "kVoltageSource",
        "kNexximGround",
        "kNexximPort",
        "kDcTerminal",
        "kVoltageProbe",
        "InvalidBoundary",
    ]
    hfss_type: Literal["Wave", "Gap", None]


class CfgPadstackInstanceTerminal(CfgTerminal):
    terminal_type: str = "padstack_instance"
    padstack_instance: str
    padstack_instance_id: Optional[int] = None
    layer: Optional[Union[str, None]] = None


class CfgPinGroupTerminal(CfgTerminal):
    terminal_type: str = "pin_group"
    is_circuit_port: bool = True
    pin_group: str


class CfgPointTerminal(CfgTerminal):
    terminal_type: str = "point"
    x: Union[float, int, str]
    y: Union[float, int, str]
    layer: str
    net: str


class CfgEdgeTerminal(CfgTerminal):
    terminal_type: str = "edge"
    name: str
    primitive: str
    point_on_edge_x: Union[float, int, str]
    point_on_edge_y: Union[float, int, str]
    horizontal_extent_factor: Union[int, str]
    vertical_extent_factor: Union[int, str]
    pec_launch_width: Union[int, str]


class CfgBundleTerminal(CfgTerminal):
    terminal_type: str = "bundle"
    terminals: List[str]
    reference_terminal: Optional[str] = None
    is_reference_terminal: bool = False


CfgTerminal.model_rebuild()


class CfgTerminals(CfgBase):
    terminals: List[
        Union[CfgPadstackInstanceTerminal, CfgPinGroupTerminal, CfgPointTerminal, CfgEdgeTerminal, CfgBundleTerminal, dict]]

    @classmethod
    def create(cls, terminals: List[dict]):
        terminal_list = []
        for i in terminals:
            terminal_type = i.pop("terminal_type")
            if terminal_type == "padstack_instance":
                temp = CfgPadstackInstanceTerminal(**i)
                terminal_list.append(temp)
            elif terminal_type == "pin_group":
                temp = CfgPinGroupTerminal(**i)
                terminal_list.append(temp)
            elif terminal_type == "point":
                temp = CfgPointTerminal(**i)
                terminal_list.append(temp)
            elif terminal_type == "edge":
                temp = CfgEdgeTerminal(**i)
                terminal_list.append(temp)
            elif terminal_type == "bundle":
                temp = CfgBundleTerminal(**i)
                terminal_list.append(temp)

        return cls(terminals=terminal_list)

    def add_padstack_instance_terminal(
            self,
            padstack_instance,
            name,
            impedance,
            is_circuit_port,
            boundary_type,
            hfss_type,
            reference_terminal=None,
            amplitude=1,
            phase=0,
            terminal_to_ground="kNoGround",
            padstack_instance_id=None
    ):
        terminal = CfgPadstackInstanceTerminal(
            padstack_instance=padstack_instance,
            name=name,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            layer=None,
            hfss_type=hfss_type,
            padstack_instance_id=padstack_instance_id
        )
        self.terminals.append(terminal)

    def add_pin_group_terminal(
            self,
            pin_group,
            name,
            impedance,
            boundary_type,
            reference_terminal=None,
            amplitude=1,
            phase=0,
            terminal_to_ground=False,
    ):
        terminal = CfgPinGroupTerminal(
            pin_group=pin_group,
            name=name,
            impedance=impedance,
            is_circuit_port=True,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            hfss_type=None
        )
        self.terminals.append(terminal)

    def add_point_terminal(
            self,
            x,
            y,
            layer,
            name,
            impedance,
            is_circuit_port,
            boundary_type,
            reference_terminal=None,
            amplitude=1,
            phase=0,
            terminal_to_ground=False,
            is_reference_terminal=False,
    ):
        terminal = CfgPointTerminal(
            x=x,
            y=y,
            layer=layer,
            name=name,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            is_reference_terminal=is_reference_terminal
        )
        self.terminals.append(terminal)

    def add_edge_terminal(
            self,
            name,
            impedance,
            is_circuit_port,
            boundary_type,
            primitive,
            point_on_edge_x,
            point_on_edge_y,
            horizontal_extent_factor=6,
            vertical_extent_factor=8,
            pec_launch_width="0.02mm",
            reference_terminal=None,
            amplitude=1,
            phase=0,
            terminal_to_ground=False,
            is_reference_terminal=False,
    ):
        terminal = CfgEdgeTerminal(
            name=name,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            is_reference_terminal=is_reference_terminal,
            primitive=primitive,
            point_on_edge_x=point_on_edge_x,
            point_on_edge_y=point_on_edge_y,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width
        )
        self.terminals.append(terminal)

    def add_bundle_terminal(
            self,
            terminals: List[Union[CfgPadstackInstanceTerminal, CfgPinGroupTerminal, CfgPointTerminal, CfgEdgeTerminal]],
            name,
            impedance,
            is_circuit_port,
            boundary_type,
            reference_terminal=None,
            amplitude=1,
            phase=0,
            terminal_to_ground=False,
    ):
        terminal = CfgBundleTerminal(
            terminals=terminals,
            name=name,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground
        )
        self.terminals.append(terminal)
