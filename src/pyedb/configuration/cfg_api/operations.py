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

"""Operations builder API."""

from __future__ import annotations

from typing import List, Optional, Union

from pyedb.configuration.cfg_operations import CfgAutoIdentifyNets, CfgCutout, CfgOperations


class CutoutConfig(CfgCutout):
    """Fluent builder for a cutout operation.

    Inherits all fields from :class:`~pyedb.configuration.cfg_operations.CfgCutout`.
    Accepts ``signal_nets`` / ``reference_nets`` as well as ``auto_identify_nets_enabled``
    convenience parameters in addition to all underlying pydantic fields.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(
        self,
        signal_nets=None,
        reference_nets=None,
        auto_identify_nets_enabled: bool = False,
        resistor_below=100,
        inductor_below=1,
        capacitor_above="10nF",
        **kwargs,
    ):
        super().__init__(
            signal_list=signal_nets,
            reference_list=reference_nets,
            auto_identify_nets=CfgAutoIdentifyNets(
                enabled=auto_identify_nets_enabled,
                resistor_below=resistor_below,
                inductor_below=inductor_below,
                capacitor_above=capacitor_above,
            ),
            **kwargs,
        )

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True, by_alias=True)


class OperationsConfig(CfgOperations):
    """Fluent builder for the ``operations`` configuration section.

    Inherits from :class:`~pyedb.configuration.cfg_operations.CfgOperations`.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def add_cutout(
        self,
        signal_nets=None,
        reference_nets=None,
        **kwargs,
    ) -> CutoutConfig:
        self.cutout = CutoutConfig(signal_nets=signal_nets, reference_nets=reference_nets, **kwargs)
        return self.cutout

    def to_dict(self) -> dict:
        data: dict = {}
        if self.cutout is not None:
            if hasattr(self.cutout, "to_dict"):
                data["cutout"] = self.cutout.to_dict()
            else:
                data["cutout"] = dict(self.cutout)
        if self.generate_auto_hfss_regions:
            data["generate_auto_hfss_regions"] = self.generate_auto_hfss_regions
        return data
