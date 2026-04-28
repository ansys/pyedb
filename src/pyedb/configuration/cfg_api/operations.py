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

"""Operations builder API.

Data models:
  :class:`~pyedb.configuration.cfg_operations.CfgCutout`
  :class:`~pyedb.configuration.cfg_operations.CfgAutoIdentifyNets`
  :class:`~pyedb.configuration.cfg_operations.CfgOperations`
"""

from __future__ import annotations

from typing import Any, List, Optional, Union

from pyedb.configuration.cfg_operations import CfgAutoIdentifyNets, CfgCutout, CfgOperations


class OperationsConfig:
    """Fluent builder for the ``operations`` configuration section.

    Wraps :class:`~pyedb.configuration.cfg_operations.CfgOperations`.

    Examples
    --------
    >>> cfg.operations.set_cutout(signal_nets=["SIG1"], reference_nets=["GND"])
    """

    def __init__(self):
        self._model = CfgOperations()

    def set_cutout(
        self,
        signal_nets: Optional[List[str]] = None,
        reference_nets: Optional[List[str]] = None,
        extent_type: str = "ConvexHull",
        expansion_size: Union[float, str] = 0.002,
        number_of_threads: int = 1,
        auto_identify_enabled: bool = False,
        resistor_below: Union[float, str, int] = 100,
        inductor_below: Union[float, str, int] = 1,
        capacitor_above: Union[float, str, int] = "10nF",
    ):
        """Configure design cutout.

        Parameters
        ----------
        signal_nets, reference_nets : list of str
        extent_type : str  e.g. ``"ConvexHull"``, ``"BoundingBox"``
        expansion_size : float or str
        number_of_threads : int
        auto_identify_enabled : bool
        resistor_below, inductor_below, capacitor_above : auto-identify thresholds
        """
        auto_identify = CfgAutoIdentifyNets(
            enabled=auto_identify_enabled,
            resistor_below=resistor_below,
            inductor_below=inductor_below,
            capacitor_above=capacitor_above,
        )
        self._model.cutout = CfgCutout(
            auto_identify_nets=auto_identify,
            signal_list=signal_nets,
            reference_list=reference_nets,
            extent_type=extent_type,
            expansion_size=expansion_size,
            number_of_threads=number_of_threads,
        )

    def enable_auto_hfss_regions(self, enable: bool = True):
        """Enable automatic HFSS region generation."""
        self._model.generate_auto_hfss_regions = enable

    def to_dict(self) -> dict:
        return self._model.model_dump(exclude_none=True, by_alias=False)


# Backward-compatible alias
CutoutConfig = CfgCutout

