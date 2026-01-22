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


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.siwave_simulation_settings import (
        SIWaveGeneralSettings as GrpcSIWaveGeneralSettings,
    )


class SIWaveGeneralSettings:
    def __init__(self, pedb, core: "GrpcSIWaveGeneralSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def pi_slider_pos(self) -> int:
        """Position of the PI slider.

        Returns
        -------
        int
            Position value.
        """
        return self.core.pi_slider_pos

    @pi_slider_pos.setter
    def pi_slider_pos(self, value: int):
        self.core.pi_slider_pos = value

    @property
    def si_slider_pos(self) -> int:
        """Position of the SI slider.

        Returns
        -------
        int
            Position value.
        """
        return self.core.si_slider_pos

    @si_slider_pos.setter
    def si_slider_pos(self, value: int):
        self.core.si_slider_pos = value

    @property
    def use_custom_settings(self) -> bool:
        """Flag to indicate if custom settings are used.

        Returns
        -------
        bool
            True if custom settings are used, False otherwise.
        """
        return self.core.use_custom_settings

    @use_custom_settings.setter
    def use_custom_settings(self, value: bool):
        self.core.use_custom_settings = value

    @property
    def use_si_settings(self) -> bool:
        """Flag to indicate if SI settings are used.

        Returns
        -------
        bool
            True if SI settings are used, False otherwise.
        """
        return self.core.use_si_settings

    @use_si_settings.setter
    def use_si_settings(self, value: bool):
        self.core.use_si_settings = value
