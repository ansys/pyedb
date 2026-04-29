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

"""Build the ``padstacks`` configuration section.

This module wraps the padstack-related configuration models with small builder
classes for definitions, placed instances, and optional backdrill settings.

Typical usage
-------------
>>> cfg.padstacks.add_definition("via_0.2", material="copper", hole_plating_thickness="25um")
>>> inst = cfg.padstacks.add_instance(name="v1", net_name="GND", layer_range=["top", "bot"])
>>> inst.set_backdrill("L3", "0.25mm", drill_from_bottom=True)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union

from pyedb.configuration.cfg_padstacks import (
    CfgPadstackDefinition,
    CfgPadstackInstance,
)


class PadstackDefinitionConfig:
    """Fluent builder for a padstack definition.

    Wraps :class:`~pyedb.configuration.cfg_padstacks.CfgPadstackDefinition`.

    Parameters
    ----------
    name : str
        Padstack definition name.
    hole_plating_thickness : str or float, optional
        Plating thickness of the drill hole, e.g. ``"25um"``.
    material : str, optional
        Hole conductor material name (alias ``hole_material``).
    hole_range : str, optional
        Layer range the hole spans (e.g. ``"upper_pad_to_lower_pad"``).
    pad_parameters : dict, optional
        Raw pad-parameter dictionary as consumed by the EDB padstack API.
    hole_parameters : dict, optional
        Raw hole-parameter dictionary.
    solder_ball_parameters : dict, optional
        Raw solder-ball parameter dictionary.
    """

    def __init__(
        self,
        name: str,
        hole_plating_thickness: Optional[Union[str, float]] = None,
        material: Optional[str] = None,
        hole_range: Optional[str] = None,
        pad_parameters: Optional[dict] = None,
        hole_parameters: Optional[dict] = None,
        solder_ball_parameters: Optional[dict] = None,
    ):
        """Initialize a padstack definition.

        Parameters
        ----------
        name : str
            Padstack definition name.
        hole_plating_thickness : str or float, optional
            Plating thickness, e.g. ``"25um"``.
        material : str, optional
            Hole conductor material.
        hole_range : str, optional
            Layer range the hole spans.
        pad_parameters : dict, optional
            Raw pad-parameter dictionary.
        hole_parameters : dict, optional
            Raw hole-parameter dictionary.
        solder_ball_parameters : dict, optional
            Raw solder-ball parameter dictionary.
        """
        kwargs = {k: v for k, v in {
            "name": name,
            "hole_plating_thickness": hole_plating_thickness,
            "hole_material": material,
            "hole_range": hole_range,
            "pad_parameters": pad_parameters,
            "hole_parameters": hole_parameters,
            "solder_ball_parameters": solder_ball_parameters,
        }.items() if v is not None}
        self._model = CfgPadstackDefinition(**kwargs)

    def to_dict(self) -> dict:
        """Serialize the padstack definition.

        Returns
        -------
        dict
            Dictionary containing only explicitly configured definition fields.
        """
        return self._model.model_dump(exclude_none=True)


class PadstackInstanceConfig:
    """Fluent builder for a padstack instance.

    Wraps :class:`~pyedb.configuration.cfg_padstacks.CfgPadstackInstance`.

    Parameters
    ----------
    name : str, optional
        Instance name (AEDT name).
    net_name : str, optional
        Net the instance belongs to.
    definition : str, optional
        Padstack definition name.
    layer_range : list of str, optional
        ``[start_layer, stop_layer]`` for the via span.
    position : list of str or float, optional
        ``[x, y]`` placement position in metres.
    rotation : str or float, optional
        Rotation angle in degrees.
    is_pin : bool, default: ``False``
        Whether the instance is a component pin.
    hole_override_enabled : bool, optional
        Enable hole-size override.
    hole_override_diameter : str or float, optional
        Override drill diameter.
    solder_ball_layer : str, optional
        Layer on which the solder ball sits.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        net_name: Optional[str] = None,
        definition: Optional[str] = None,
        layer_range: Optional[List[str]] = None,
        position: Optional[List[Union[str, float]]] = None,
        rotation: Optional[Union[str, float]] = None,
        is_pin: bool = False,
        hole_override_enabled: Optional[bool] = None,
        hole_override_diameter: Optional[Union[str, float]] = None,
        solder_ball_layer: Optional[str] = None,
    ):
        """Initialize a padstack instance configuration.

        Parameters
        ----------
        name : str, optional
            Instance name.
        net_name : str, optional
            Net name.
        definition : str, optional
            Padstack definition name.
        layer_range : list of str, optional
            ``[start_layer, stop_layer]``.
        position : list of str or float, optional
            ``[x, y]`` placement in metres.
        rotation : str or float, optional
            Rotation in degrees.
        is_pin : bool, default: ``False``
            Whether the instance is a component pin.
        hole_override_enabled : bool, optional
            Enable hole-size override.
        hole_override_diameter : str or float, optional
            Override drill diameter.
        solder_ball_layer : str, optional
            Layer on which the solder ball sits.
        """
        kwargs = {k: v for k, v in {
            "name": name,
            "net_name": net_name,
            "definition": definition,
            "layer_range": layer_range,
            "position": position,
            "rotation": str(rotation) if rotation is not None else None,
            "is_pin": is_pin,
            "hole_override_enabled": hole_override_enabled,
            "hole_override_diameter": hole_override_diameter,
            "solder_ball_layer": solder_ball_layer,
        }.items() if v is not None}
        self._model = CfgPadstackInstance(**kwargs)

    def set_backdrill(
        self,
        drill_to_layer: str,
        diameter: str,
        stub_length: Optional[str] = None,
        drill_from_bottom: bool = True,
    ) -> "PadstackInstanceConfig":
        """Configure backdrill parameters.

        Parameters
        ----------
        drill_to_layer : str
            Target layer for the backdrill operation.
        diameter : str
            Backdrill hole diameter, e.g. ``"0.25mm"``.
        stub_length : str, optional
            Stub length remaining after backdrilling.
        drill_from_bottom : bool, default: ``True``
            ``True`` = drill from the bottom surface; ``False`` = from the top.

        Returns
        -------
        PadstackInstanceConfig
            *self*, for method chaining.
        """
        self._model.backdrill_parameters.add_backdrill_to_layer(
            drill_to_layer=drill_to_layer,
            diameter=diameter,
            stub_length=stub_length,
            drill_from_bottom=drill_from_bottom,
        )
        return self

    def to_dict(self) -> dict:
        """Serialize the padstack instance.

        Returns
        -------
        dict
            Dictionary containing only explicitly configured instance fields.
        """
        return self._model.model_dump(exclude_none=True, by_alias=False)


class PadstacksConfig:
    """Fluent builder for the ``padstacks`` configuration section.

    Examples
    --------
    >>> cfg.padstacks.add_definition("via_0.2", material="copper", hole_plating_thickness="25um")
    >>> inst = cfg.padstacks.add_instance(name="v1", net_name="GND", layer_range=["top", "bot"])
    >>> inst.set_backdrill("L3", "0.25mm", drill_from_bottom=True)
    """

    def __init__(self):
        """Initialize the padstacks configuration."""
        self._definitions: List[PadstackDefinitionConfig] = []
        self._instances: List[PadstackInstanceConfig] = []

    def add_definition(
        self,
        name: str,
        hole_plating_thickness: Optional[Union[str, float]] = None,
        material: Optional[str] = None,
        hole_range: Optional[str] = None,
        pad_parameters: Optional[dict] = None,
        hole_parameters: Optional[dict] = None,
        solder_ball_parameters: Optional[dict] = None,
    ) -> PadstackDefinitionConfig:
        """Add a padstack definition.

        Parameters
        ----------
        name : str
            Padstack definition name.
        hole_plating_thickness : str or float, optional
            Plating thickness, e.g. ``"25um"``.
        material : str, optional
            Hole conductor material.
        hole_range : str, optional
            Layer range the hole spans.
        pad_parameters : dict, optional
            Raw pad-parameter dictionary.
        hole_parameters : dict, optional
            Raw hole-parameter dictionary.
        solder_ball_parameters : dict, optional
            Raw solder-ball parameter dictionary.

        Returns
        -------
        PadstackDefinitionConfig
            Newly created definition builder.
        """
        pdef = PadstackDefinitionConfig(
            name=name,
            hole_plating_thickness=hole_plating_thickness,
            material=material,
            hole_range=hole_range,
            pad_parameters=pad_parameters,
            hole_parameters=hole_parameters,
            solder_ball_parameters=solder_ball_parameters,
        )
        self._definitions.append(pdef)
        return pdef

    def add_instance(
        self,
        name: Optional[str] = None,
        net_name: Optional[str] = None,
        definition: Optional[str] = None,
        layer_range: Optional[List[str]] = None,
        position: Optional[List[Union[str, float]]] = None,
        rotation: Optional[Union[str, float]] = None,
        is_pin: bool = False,
        hole_override_enabled: Optional[bool] = None,
        hole_override_diameter: Optional[Union[str, float]] = None,
        solder_ball_layer: Optional[str] = None,
    ) -> PadstackInstanceConfig:
        """Add a padstack instance.

        Parameters
        ----------
        name : str, optional
            Instance name (AEDT name).
        net_name : str, optional
            Net the instance belongs to.
        definition : str, optional
            Padstack definition name.
        layer_range : list of str, optional
            ``[start_layer, stop_layer]`` for the via span.
        position : list of str or float, optional
            ``[x, y]`` placement position in metres.
        rotation : str or float, optional
            Rotation angle in degrees.
        is_pin : bool, default: ``False``
            Whether the instance is a component pin.
        hole_override_enabled : bool, optional
            Enable hole-size override.
        hole_override_diameter : str or float, optional
            Override drill diameter.
        solder_ball_layer : str, optional
            Layer on which the solder ball sits.

        Returns
        -------
        PadstackInstanceConfig
            Newly created instance builder; call :meth:`set_backdrill` to
            add back-drill parameters.
        """
        inst = PadstackInstanceConfig(
            name=name,
            net_name=net_name,
            definition=definition,
            layer_range=layer_range,
            position=position,
            rotation=rotation,
            is_pin=is_pin,
            hole_override_enabled=hole_override_enabled,
            hole_override_diameter=hole_override_diameter,
            solder_ball_layer=solder_ball_layer,
        )
        self._instances.append(inst)
        return inst

    def to_dict(self) -> dict:
        """Serialize all configured padstack definitions and instances.

        Returns
        -------
        dict
            Dictionary containing ``definitions`` and/or ``instances`` when
            present.

        """
        data: dict = {}
        if self._definitions:
            data["definitions"] = [d.to_dict() for d in self._definitions]
        if self._instances:
            data["instances"] = [i.to_dict() for i in self._instances]
        return data
