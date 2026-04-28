# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Components builder API.

``CfgComponent`` (root module) requires live EDB/gRPC imports so we define
pure-data pydantic models here and build ``ComponentConfig`` on top of them.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from pyedb.configuration.cfg_common import CfgBaseModel


# ── sub-structure pydantic models ─────────────────────────────────────────────


class PinPairModel(CfgBaseModel):
    """Single pin-pair RLC entry."""

    first_pin: str
    second_pin: str
    resistance: Optional[Union[str, float]] = None
    inductance: Optional[Union[str, float]] = None
    capacitance: Optional[Union[str, float]] = None
    is_parallel: bool = False
    resistance_enabled: bool = False
    inductance_enabled: bool = False
    capacitance_enabled: bool = False

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(self, first_pin: str, second_pin: str, **kwargs):
        super().__init__(first_pin=first_pin, second_pin=second_pin, **kwargs)

    def to_dict(self) -> dict:
        return self.model_dump()


class _SParameterModelData(CfgBaseModel):
    model_name: str
    model_path: str
    reference_net: str
    model_config = {"populate_by_name": True, "extra": "allow"}


class _SpiceModelData(CfgBaseModel):
    model_name: str
    model_path: str
    sub_circuit: str = ""
    terminal_pairs: List[Any] = Field(default_factory=list)
    model_config = {"populate_by_name": True, "extra": "allow"}


class _NetlistModelData(CfgBaseModel):
    netlist: str
    model_config = {"populate_by_name": True, "extra": "allow"}


class _IcDieProperties(CfgBaseModel):
    type: Literal["flip_chip", "wire_bond", "no_die"] = "no_die"
    orientation: Optional[Literal["chip_up", "chip_down"]] = None
    height: Optional[str] = None
    model_config = {"populate_by_name": True, "extra": "allow"}


class _SolderBallProperties(CfgBaseModel):
    shape: Literal["cylinder", "spheroid", "no_solder_ball"] = "cylinder"
    diameter: str = "150um"
    height: str = "100um"
    material: str = "solder"
    mid_diameter: Optional[str] = None
    model_config = {"populate_by_name": True, "extra": "allow"}


class _PortProperties(CfgBaseModel):
    reference_height: str = "0"
    reference_size_auto: bool = True
    reference_size_x: str = "0"
    reference_size_y: str = "0"
    model_config = {"populate_by_name": True, "extra": "allow"}


# ── root pydantic data model ──────────────────────────────────────────────────


class _CfgComponentData(BaseModel):
    """Pure-data pydantic model for a component configuration entry."""

    reference_designator: str
    part_type: Optional[str] = None
    enabled: Optional[bool] = None
    definition: Optional[str] = None
    placement_layer: Optional[str] = None

    pin_pair_model: List[Dict] = Field(default_factory=list)
    s_parameter_model: Optional[_SParameterModelData] = None
    spice_model: Optional[_SpiceModelData] = None
    netlist_model: Optional[_NetlistModelData] = None
    ic_die_properties: Optional[_IcDieProperties] = None
    solder_ball_properties: Optional[_SolderBallProperties] = None
    port_properties: Optional[_PortProperties] = None

    model_config = {"populate_by_name": True, "extra": "allow"}


# ── builder ───────────────────────────────────────────────────────────────────


class ComponentConfig(_CfgComponentData):
    """Fluent builder for a single component entry.

    Inherits all fields from ``_CfgComponentData``.  Adds convenience setter
    methods on top — no field redefinition needed.
    """

    def __init__(self, reference_designator: str, **kwargs):
        super().__init__(reference_designator=reference_designator, **kwargs)

    # ── model helpers ─────────────────────────────────────────────────────

    def add_pin_pair_rlc(
        self,
        first_pin: str,
        second_pin: str,
        resistance: Optional[Union[str, float]] = None,
        inductance: Optional[Union[str, float]] = None,
        capacitance: Optional[Union[str, float]] = None,
        is_parallel: bool = False,
        resistance_enabled: bool = False,
        inductance_enabled: bool = False,
        capacitance_enabled: bool = False,
    ):
        """Append a pin-pair RLC model entry."""
        self.pin_pair_model.append(
            PinPairModel(
                first_pin=first_pin,
                second_pin=second_pin,
                resistance=resistance,
                inductance=inductance,
                capacitance=capacitance,
                is_parallel=is_parallel,
                resistance_enabled=resistance_enabled,
                inductance_enabled=inductance_enabled,
                capacitance_enabled=capacitance_enabled,
            ).to_dict()
        )

    def set_s_parameter_model(self, model_name: str, model_path: str, reference_net: str):
        self.s_parameter_model = _SParameterModelData(
            model_name=model_name, model_path=model_path, reference_net=reference_net
        )

    def set_spice_model(self, model_name: str, model_path: str, sub_circuit: str = "", terminal_pairs=None):
        self.spice_model = _SpiceModelData(
            model_name=model_name, model_path=model_path,
            sub_circuit=sub_circuit, terminal_pairs=terminal_pairs or []
        )

    def set_netlist_model(self, netlist: str):
        self.netlist_model = _NetlistModelData(netlist=netlist)

    def set_ic_die_properties(
        self,
        die_type: Literal["flip_chip", "wire_bond", "no_die"] = "no_die",
        orientation: Literal["chip_up", "chip_down"] = "chip_up",
        height: Optional[str] = None,
    ):
        data: dict = {"type": die_type}
        if die_type != "no_die":
            data["orientation"] = orientation
            if die_type == "wire_bond" and height:
                data["height"] = height
        self.ic_die_properties = _IcDieProperties(**data)

    def set_solder_ball_properties(
        self,
        shape: Literal["cylinder", "spheroid", "no_solder_ball"] = "cylinder",
        diameter: str = "150um",
        height: str = "100um",
        material: str = "solder",
        mid_diameter: Optional[str] = None,
    ):
        data: dict = {"shape": shape, "diameter": diameter, "height": height, "material": material}
        if shape == "spheroid":
            data["mid_diameter"] = mid_diameter or diameter
        self.solder_ball_properties = _SolderBallProperties(**data)

    def set_port_properties(
        self,
        reference_height: str = "0",
        reference_size_auto: bool = True,
        reference_size_x: str = "0",
        reference_size_y: str = "0",
    ):
        self.port_properties = _PortProperties(
            reference_height=reference_height,
            reference_size_auto=reference_size_auto,
            reference_size_x=reference_size_x,
            reference_size_y=reference_size_y,
        )

    def to_dict(self) -> dict:
        data: dict = {"reference_designator": self.reference_designator}
        for key in ("part_type", "enabled", "definition", "placement_layer"):
            val = getattr(self, key)
            if val is not None:
                data[key] = val
        if self.pin_pair_model:
            data["pin_pair_model"] = self.pin_pair_model
        for key, attr in (
            ("s_parameter_model", self.s_parameter_model),
            ("spice_model", self.spice_model),
            ("netlist_model", self.netlist_model),
            ("ic_die_properties", self.ic_die_properties),
            ("solder_ball_properties", self.solder_ball_properties),
            ("port_properties", self.port_properties),
        ):
            if attr is not None:
                data[key] = attr.model_dump(exclude_none=True)
        return data


class ComponentsConfig:
    """Fluent builder for the ``components`` configuration list."""

    def __init__(self):
        self._components: List[ComponentConfig] = []

    def add(
        self,
        reference_designator: str,
        part_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        definition: Optional[str] = None,
        placement_layer: Optional[str] = None,
    ) -> ComponentConfig:
        comp = ComponentConfig(
            reference_designator=reference_designator,
            part_type=part_type,
            enabled=enabled,
            definition=definition,
            placement_layer=placement_layer,
        )
        self._components.append(comp)
        return comp

    def to_list(self) -> List[dict]:
        return [c.to_dict() for c in self._components]

