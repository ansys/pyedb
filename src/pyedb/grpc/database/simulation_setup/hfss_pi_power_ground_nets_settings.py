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


from ansys.edb.core.simulation_setup.hfss_pi_simulation_settings import (
    HFSSPIPowerGroundNetsSettings as CoreHFSSPIPowerGroundNetsSettings,
)


class HFSSPIPowerGroundNetsSettings:
    """PyEDB HFSS PI Power/Ground Nets settings class."""

    def __init__(self, pedb, core: "CoreHFSSPIPowerGroundNetsSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def auto_detect_ignore_small_holes_min_diameter(self) -> bool:
        """Flag indicating whether to automatically detect a diameter that holes smaller than the diameter
        will be ignored.

        Returns
        -------
        bool
            True if auto-detect ignore small holes minimum diameter is enabled, False otherwise.

        """
        return self.core.auto_detect_ignore_small_holes_min_diameter

    @auto_detect_ignore_small_holes_min_diameter.setter
    def auto_detect_ignore_small_holes_min_diameter(self, value: bool):
        self.core.auto_detect_ignore_small_holes_min_diameter = value

    @property
    def ignore_small_holes_min_diameter(self) -> str:
        """Diameter that holes smaller than the diameter will be ignored.

        Returns
        -------
        str
            Minimum diameter for holes to be ignored.

        """
        return self.core.ignore_small_holes_min_diameter

    @ignore_small_holes_min_diameter.setter
    def ignore_small_holes_min_diameter(self, value: str):
        self.core.ignore_small_holes_min_diameter = value

    @property
    def improved_loss_model(self) -> str:
        """Improved loss model setting.

        Returns
        -------
        str
            Improved loss model setting. Values are `level_1`, `level_2`, `level_3`.

        """
        return self.core.improved_loss_model.name.lower()

    @improved_loss_model.setter
    def improved_loss_model(self, value: str):
        model = self.core.improved_loss_model
        enum_value = model.__class__[value.upper()]
        self.core.improved_loss_model = enum_value
