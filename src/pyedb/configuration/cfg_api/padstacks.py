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

"""
Build the ``padstacks`` configuration section.

This module wraps the padstack-related configuration models with small builder
classes for definitions, placed instances, and optional backdrill settings.
"""

from __future__ import annotations

from typing import List, Optional

from pyedb.configuration.cfg_padstacks import (
    CfgPadstackDefinition,
    CfgPadstackInstance,
)


class PadstackDefinitionConfig:
    """
    Fluent builder for a padstack definition.

    Wraps :class:`~pyedb.configuration.cfg_padstacks.CfgPadstackDefinition`.

    Parameters
    ----------
    name : str
    **kwargs
        Any field accepted by ``CfgPadstackDefinition``.

    """

    def __init__(self, name: str, **kwargs):
        """
        Initialize a padstack definition.

        Parameters
        ----------
        name : str
            Padstack definition name.
        **kwargs
            Configuration fields.

        """
        self._model = CfgPadstackDefinition(name=name, **kwargs)

    def to_dict(self) -> dict:
        """
        Serialize the padstack definition.

        Returns
        -------
        dict
            Dictionary containing only explicitly configured definition fields.

        """
        return self._model.model_dump(exclude_none=True)


class PadstackInstanceConfig:
    """
    Fluent builder for a padstack instance.

    Wraps :class:`~pyedb.configuration.cfg_padstacks.CfgPadstackInstance`.

    Parameters
    ----------
    **kwargs
        Any field accepted by ``CfgPadstackInstance``
        (name, net_name, layer_range, …).

    """

    def __init__(self, **kwargs):
        """
        Initialize a padstack instance configuration.

        Parameters
        ----------
        **kwargs
            Configuration fields.

        """
        self._model = CfgPadstackInstance(**kwargs)

    def set_backdrill(
        self,
        drill_to_layer: str,
        diameter: str,
        stub_length: Optional[str] = None,
        drill_from_bottom: bool = True,
    ):
        """
        Configure backdrill parameters.

        Parameters
        ----------
        drill_to_layer : str
            Target layer for the backdrill operation.
        diameter : str
            Backdrill hole diameter.
        stub_length : str, optional
            Stub length remaining after backdrilling.
        drill_from_bottom : bool
            Whether to drill from the bottom of the stackup.

        """
        self._model.backdrill_parameters.add_backdrill_to_layer(
            drill_to_layer=drill_to_layer,
            diameter=diameter,
            stub_length=stub_length,
            drill_from_bottom=drill_from_bottom,
        )

    def to_dict(self) -> dict:
        """
        Serialize the padstack instance.

        Returns
        -------
        dict
            Dictionary containing only explicitly configured instance fields.

        """
        return self._model.model_dump(exclude_none=True, by_alias=False)


class PadstacksConfig:
    """Fluent builder for the ``padstacks`` configuration section."""

    def __init__(self):
        """Initialize the padstacks configuration."""
        self._definitions: List[PadstackDefinitionConfig] = []
        self._instances: List[PadstackInstanceConfig] = []

    def add_definition(self, name: str, **kwargs) -> PadstackDefinitionConfig:
        """
        Add a padstack definition.

        Returns
        -------
        PadstackDefinitionConfig

        """
        pdef = PadstackDefinitionConfig(name, **kwargs)
        self._definitions.append(pdef)
        return pdef

    def add_instance(self, **kwargs) -> PadstackInstanceConfig:
        """
        Add a padstack instance.

        Returns
        -------
        PadstackInstanceConfig

        """
        inst = PadstackInstanceConfig(**kwargs)
        self._instances.append(inst)
        return inst

    def to_dict(self) -> dict:
        """
        Serialize all configured padstack definitions and instances.

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
