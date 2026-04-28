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

"""Build current and voltage source configuration entries."""

from __future__ import annotations

from typing import List, Optional, Union


class SourceConfig:

    """Current or voltage source definition.

    Parameters
    ----------
    name : str
    source_type : str
        ``"current"`` or ``"voltage"``.
    positive_terminal : dict
    negative_terminal : dict
    magnitude : float
    impedance : float or str, optional
    reference_designator : str, optional
    distributed : bool

    """

    def __init__(
        self,
        name: str,
        source_type: str,
        positive_terminal: dict,
        negative_terminal: dict,
        magnitude: float = 0.001,
        impedance: Optional[Union[float, str]] = None,
        reference_designator: Optional[str] = None,
        distributed: bool = False,
    ):
        """Initialize a source configuration.

        Parameters
        ----------
        name : str
            Source name.
        source_type : str
            ``"current"`` or ``"voltage"``.
        positive_terminal : dict
            Positive terminal specifier.
        negative_terminal : dict
            Negative terminal specifier.
        magnitude : float, default: 0.001
            Source magnitude.
        impedance : float or str, optional
            Source impedance.
        reference_designator : str, optional
            Component reference designator used to disambiguate the terminal.
        distributed : bool, default: False
            Whether the source is distributed.

        """
        self.name = name
        self.type = source_type
        self.positive_terminal = positive_terminal
        self.negative_terminal = negative_terminal
        self.magnitude = magnitude
        self.impedance = impedance
        self.reference_designator = reference_designator
        self.distributed = distributed

    def to_dict(self) -> dict:
        """Serialize the source definition.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``sources`` configuration
            list.

        """
        data: dict = {
            "name": self.name,
            "type": self.type,
            "positive_terminal": self.positive_terminal,
            "negative_terminal": self.negative_terminal,
            "magnitude": self.magnitude,
        }
        if self.impedance is not None:
            data["impedance"] = self.impedance
        if self.reference_designator:
            data["reference_designator"] = self.reference_designator
        if self.distributed:
            data["distributed"] = self.distributed
        return data


class SourcesConfig:

    """Collect source definitions for serialization."""

    def __init__(self):
        """Initialize the sources configuration."""
        self._sources: List[SourceConfig] = []

    def add_current_source(
        self,
        name: str,
        positive_terminal: dict,
        negative_terminal: dict,
        magnitude: float = 0.001,
        impedance: Optional[Union[float, str]] = None,
        reference_designator: Optional[str] = None,
        distributed: bool = False,
    ) -> SourceConfig:
        """Add a current source.

        Parameters
        ----------
        name : str
            Source name.
        positive_terminal : dict
            Positive terminal specifier.
        negative_terminal : dict
            Negative terminal specifier.
        magnitude : float
            Source magnitude.
        impedance : float or str, optional
            Source impedance.
        reference_designator : str, optional
            Component reference designator used to disambiguate the terminal.
        distributed : bool
            Whether the source is distributed.

        Returns
        -------
        SourceConfig

        """
        src = SourceConfig(
            name=name,
            source_type="current",
            positive_terminal=positive_terminal,
            negative_terminal=negative_terminal,
            magnitude=magnitude,
            impedance=impedance,
            reference_designator=reference_designator,
            distributed=distributed,
        )
        self._sources.append(src)
        return src

    def add_voltage_source(
        self,
        name: str,
        positive_terminal: dict,
        negative_terminal: dict,
        magnitude: float = 1.0,
        impedance: Optional[Union[float, str]] = None,
        reference_designator: Optional[str] = None,
        distributed: bool = False,
    ) -> SourceConfig:
        """Add a voltage source.

        Parameters
        ----------
        name : str
            Source name.
        positive_terminal : dict
            Positive terminal specifier.
        negative_terminal : dict
            Negative terminal specifier.
        magnitude : float, default: 1.0
            Source magnitude.
        impedance : float or str, optional
            Source impedance.
        reference_designator : str, optional
            Component reference designator used to disambiguate the terminal.
        distributed : bool, default: False
            Whether the source is distributed.

        Returns
        -------
        SourceConfig
            Newly created source entry.

        """
        src = SourceConfig(
            name=name,
            source_type="voltage",
            positive_terminal=positive_terminal,
            negative_terminal=negative_terminal,
            magnitude=magnitude,
            impedance=impedance,
            reference_designator=reference_designator,
            distributed=distributed,
        )
        self._sources.append(src)
        return src

    def to_list(self) -> List[dict]:
        """Serialize all configured sources.

        Returns
        -------
        list[dict]
            Source definitions in insertion order.

        """
        return [s.to_dict() for s in self._sources]
