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

Data model: :class:`~pyedb.configuration.cfg_components.CfgComponent`.
The ``cfg_components`` root module carries EDB-level imports (grpc/dotnet) so
we intentionally do **not** import it here.  Instead we build plain dicts that
match the schema expected by ``CfgComponent``.
"""

from __future__ import annotations

from typing import List, Literal, Optional, Union


class PinPairModel:
    """Single pin-pair RLC model entry.

    Produces a dict consumed by ``CfgComponent.pin_pair_model``.

    Parameters
    ----------
    first_pin, second_pin : str
    resistance, inductance, capacitance : str or float, optional
    is_parallel : bool
    resistance_enabled, inductance_enabled, capacitance_enabled : bool
    """

    def __init__(
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
        self.first_pin = first_pin
        self.second_pin = second_pin
        self.resistance = resistance
        self.inductance = inductance
        self.capacitance = capacitance
        self.is_parallel = is_parallel
        self.resistance_enabled = resistance_enabled
        self.inductance_enabled = inductance_enabled
        self.capacitance_enabled = capacitance_enabled

    def to_dict(self) -> dict:
        return {
            "first_pin": self.first_pin,
            "second_pin": self.second_pin,
            "resistance": self.resistance,
            "inductance": self.inductance,
            "capacitance": self.capacitance,
            "is_parallel": self.is_parallel,
            "resistance_enabled": self.resistance_enabled,
            "inductance_enabled": self.inductance_enabled,
            "capacitance_enabled": self.capacitance_enabled,
        }


class ComponentConfig:
    """Fluent builder for a single component entry.

    Produces a dict consumed by
    :class:`~pyedb.configuration.cfg_components.CfgComponent`.

    Parameters
    ----------
    reference_designator : str
    part_type : str, optional
        ``"resistor"``, ``"capacitor"``, ``"inductor"``, ``"ic"``, ``"io"``, ``"other"``.
    enabled : bool, optional
    definition : str, optional
    placement_layer : str, optional
    """

    def __init__(
        self,
        reference_designator: str,
        part_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        definition: Optional[str] = None,
        placement_layer: Optional[str] = None,
    ):
        self.reference_designator = reference_designator
        self.part_type = part_type
        self.enabled = enabled
        self.definition = definition
        self.placement_layer = placement_layer

        self.pin_pair_model: List[dict] = []
        self.s_parameter_model: dict = {}
        self.spice_model: dict = {}
        self.netlist_model: dict = {}
        self.port_properties: dict = {}
        self.solder_ball_properties: dict = {}
        self.ic_die_properties: dict = {}

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
        """Assign an S-parameter model."""
        self.s_parameter_model = {
            "model_name": model_name,
            "model_path": model_path,
            "reference_net": reference_net,
        }

    def set_spice_model(
        self,
        model_name: str,
        model_path: str,
        sub_circuit: str = "",
        terminal_pairs: Optional[List] = None,
    ):
        """Assign a SPICE model."""
        self.spice_model = {
            "model_name": model_name,
            "model_path": model_path,
            "sub_circuit": sub_circuit,
            "terminal_pairs": terminal_pairs or [],
        }

    def set_netlist_model(self, netlist: str):
        """Assign a netlist model."""
        self.netlist_model = {"netlist": netlist}

    def set_ic_die_properties(
        self,
        die_type: Literal["flip_chip", "wire_bond", "no_die"] = "no_die",
        orientation: Literal["chip_up", "chip_down"] = "chip_up",
        height: Optional[str] = None,
    ):
        """Set IC die properties."""
        data: dict = {"type": die_type}
        if die_type != "no_die":
            data["orientation"] = orientation
            if die_type == "wire_bond" and height:
                data["height"] = height
        self.ic_die_properties = data

    def set_solder_ball_properties(
        self,
        shape: Literal["cylinder", "spheroid", "no_solder_ball"] = "cylinder",
        diameter: str = "150um",
        height: str = "100um",
        material: str = "solder",
        mid_diameter: Optional[str] = None,
    ):
        """Set solder-ball properties."""
        data: dict = {"shape": shape, "diameter": diameter, "height": height, "material": material}
        if shape == "spheroid":
            data["mid_diameter"] = mid_diameter or diameter
        self.solder_ball_properties = data

    def set_port_properties(
        self,
        reference_height: str = "0",
        reference_size_auto: bool = True,
        reference_size_x: str = "0",
        reference_size_y: str = "0",
    ):
        """Set port properties for IC / IO components."""
        self.port_properties = {
            "reference_height": reference_height,
            "reference_size_auto": reference_size_auto,
            "reference_size_x": reference_size_x,
            "reference_size_y": reference_size_y,
        }

    def to_dict(self) -> dict:
        data: dict = {"reference_designator": self.reference_designator}
        for key in ("part_type", "enabled", "definition", "placement_layer"):
            val = getattr(self, key)
            if val is not None:
                data[key] = val
        if self.pin_pair_model:
            data["pin_pair_model"] = self.pin_pair_model
        if self.s_parameter_model:
            data["s_parameter_model"] = self.s_parameter_model
        if self.spice_model:
            data["spice_model"] = self.spice_model
        if self.netlist_model:
            data["netlist_model"] = self.netlist_model
        if self.port_properties:
            data["port_properties"] = self.port_properties
        if self.solder_ball_properties:
            data["solder_ball_properties"] = self.solder_ball_properties
        if self.ic_die_properties:
            data["ic_die_properties"] = self.ic_die_properties
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
        """Add a component entry.

        Returns
        -------
        ComponentConfig
            The created entry for further configuration.
        """
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

