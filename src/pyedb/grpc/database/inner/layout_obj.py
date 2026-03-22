# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import dataclass
import re

from ansys.edb.core.database import ProductIdType as CoreProductIdType

from pyedb.grpc.database.inner.base import ObjBase


@dataclass
class HFSSProductProperty:
    hfss_type: str = "Gap"
    orientation: str = ""
    layer_alignment: str = ""
    horizontal_extent_factor: float = 0.0
    vertical_extent_factor: float = 0.0
    pec_launch_width: str = "10um"

    def to_hfss_string(self) -> str:
        def _fmt_num(val: float) -> str:
            try:
                v = float(val)
            except Exception:
                return str(val)
            # Render as integer when the float is integral
            if v.is_integer():
                return str(int(v))
            return str(v)

        h_val = _fmt_num(self.horizontal_extent_factor)
        v_val = _fmt_num(self.vertical_extent_factor)

        return (
            "HFSS("
            f"'HFSS Type'='{self.hfss_type}',  "
            f"Orientation='{self.orientation}',  "
            f"'Layer Alignment'='{self.layer_alignment}',  "
            f"'Horizontal Extent Factor'='{h_val}',  "
            f"'Vertical Extent Factor'='{v_val}',  "
            f"'PEC Launch Width'='{self.pec_launch_width}'"
            ")"
        )


def parse_hfss_string(s: str | None) -> HFSSProductProperty:
    if s is None:
        return HFSSProductProperty()

    def get(key: str) -> str | None:
        match = re.search(rf"'{re.escape(key)}'='([^']*)'", s)
        return match.group(1) if match else None

    defaults = HFSSProductProperty()

    return HFSSProductProperty(
        hfss_type=get("HFSS Type") or defaults.hfss_type,
        orientation=get("Orientation") or defaults.orientation,
        layer_alignment=get("Layer Alignment") or defaults.layer_alignment,
        horizontal_extent_factor=float(get("Horizontal Extent Factor") or defaults.horizontal_extent_factor),
        vertical_extent_factor=float(get("Vertical Extent Factor") or defaults.vertical_extent_factor),
        pec_launch_width=get("PEC Launch Width") or defaults.pec_launch_width,
    )


class LayoutObj(ObjBase):
    """Represents a layout object."""

    def __init__(self, pedb, core):
        super().__init__(pedb, core)

    @property
    def _edb_properties(self):
        p = self.core.get_product_property(CoreProductIdType.DESIGNER, 18)
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self.core.set_product_property(CoreProductIdType.DESIGNER, 18, value)

    @property
    def _hfss_properties(self) -> HFSSProductProperty:
        return parse_hfss_string(self.core.product_solver_option(CoreProductIdType.DESIGNER, "HFSS"))

    @_hfss_properties.setter
    def _hfss_properties(self, value):
        if isinstance(value, HFSSProductProperty):
            self.core.product_solver_option(CoreProductIdType.DESIGNER, "HFSS", value.to_hfss_string())
