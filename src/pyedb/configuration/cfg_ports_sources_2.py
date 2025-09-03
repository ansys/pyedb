from typing import Union, Optional, Dict, List, Literal

from pydantic import BaseModel


class CfgAutoProperties(BaseModel):
    radius: Union[str, float, int]
    net: str
    orientation: int  # The preferred port orientation: 0: vertical, 1: horizontal.


class CfgTerminal(BaseModel):
    name: str
    boundary_type: str
    component: str
    auto_properties: Optional[CfgAutoProperties]
    impedance: Union[str, float, int]
    net: str
    reference_layer: Optional[str]
    reference_terminal: Optional[str]
    source_amplitude: Optional[Union[str, float, int]]
    source_phase: Optional[Union[str, float, int]]
    terminal_to_ground: Optional[Literal["no_ground", "negative", "positive"]]
    is_auto_port: Optional[bool] = False
    is_circuit_port: Optional[bool] = False
    eid = Optional[int]

    terminal_type: str


# class CfgEdgeTerminal(CfgTerminal):

class CfgPadstackInstanceTerminal(CfgTerminal):
    terminal_type = "padstack"
    padstack_instance: str


class CfgPinGroupTerminal(CfgTerminal):
    terminal_type = "pin_group"
    pin_group: str


class CfgPointTerminal(CfgTerminal):
    terminal_type = "coordinate"
    point: List[Union[str, float, int]]
    layer: str


terminal_type_mapping = {
    "padstack": CfgPadstackInstanceTerminal,
    "pin_group": CfgPinGroupTerminal,
    "coordinate": CfgPointTerminal
}


class CfgPort(BaseModel):
    name: str
    type: Literal["circuit", "coax", "wave", "gap", "wave_port", "gap_port"]
    reference_designator: Optional[str] = None
    impedance: Union[float, int]
    positive_terminal: Dict[str, Union[CfgPadstackInstanceTerminal, CfgPinGroupTerminal, CfgPointTerminal]]
    negative_terminal: Optional[
        Dict[str, Union[CfgPadstackInstanceTerminal, CfgPinGroupTerminal, CfgPointTerminal]]] = None


class CfgPorts(BaseModel):
    _pedb = None
    ports: Optional[List[CfgPort]] = []

    @staticmethod
    def __type_mapping(data):
        terminal_type = list(data.keys())[0]
        terminal_data = data[terminal_type]
        return {terminal_type: terminal_type_mapping[terminal_type](**terminal_data)}

    def add_circuit_port(self, port_name: str,
                         positive_terminal: dict,
                         negative_terminal: dict):
        p_terminal = self._type_mapping(positive_terminal)
        n_terminal = self._type_mapping(negative_terminal)
        port = CfgPort(
            name=port_name,
            type="circuit",
            impedance=list(p_terminal.values())[0].impedance,
            positive_terminal=p_terminal,
            negative_terminal=n_terminal,
        )
        self.ports.append(port)

    def add_coax_port(self, port_name: str,
                      positive_terminal: dict,
                      impedance: Optional[Union[float, int]] = 50,
                      reference_designator: str = None):
        terminal_type = list(positive_terminal.keys())[0]
        terminal_data = positive_terminal[terminal_type]
        net = terminal_data.get("net")
        pin = terminal_data.get("pin")
        padstack = terminal_data.get("padstack")
        eid = terminal_data.get("eid")

        pds = []
        if net:
            if not reference_designator:
                raise ValueError("For coax port with net defined, reference_designator must be provided.")
            temp = self._pedb.layout.find_padstack_instances(component_name=reference_designator, net_name=net)
            pds.extend(temp)
        elif pin:
            if not reference_designator:
                raise ValueError("For coax port with pin defined, reference_designator must be provided.")
            temp = self._pedb.layout.find_padstack_instances(component_name=reference_designator, component_pin_name=pin)
            pds.extend(temp)
        elif padstack:
            temp = self._pedb.layout.find_padstack_instances(aedt_name=padstack)
            pds.extend(temp)
        elif eid:
            temp = self._pedb.layout.find_padstack_instances(instance_id=eid)
            pds.extend(temp)
        else:
            raise ValueError("For coax port, one of net, pin, padstack, or eid must be provided in positive_terminal.")

        for i in pds:
            p_terminal = CfgPadstackInstanceTerminal(**{"padstack_instance": i.padstack_instance,
                                   "eid": i.id})
            temp = CfgPort(
                name=port_name,
                type="coax",
                impedance=impedance,
                positive_terminal={p_terminal.terminal_type: p_terminal},
                negative_terminal=None
            )
            self.ports.append(temp)

