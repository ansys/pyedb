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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.q3d_simulation_settings import Q3DGeneralSettings as GrpcQ3DGeneralSettings


class Q3DGeneralSettings:
    def __init__(self, pedb, core: "GrpcQ3DGeneralSettings"):
        """Q3D general settings class."""
        self.core = core
        self._pedb = pedb

    @property
    def do_ac(self) -> bool:
        """Whether to perform AC analysis.

        Returns
        -------
        bool
            True if AC analysis is to be performed, False otherwise.
        """
        return self.core.do_ac

    @do_ac.setter
    def do_ac(self, value: bool):
        self.core.do_ac = value

    @property
    def do_cg(self) -> bool:
        """Whether to perform CG analysis.

        Returns
        -------
        bool
            True if CG analysis is to be performed, False otherwise.
        """
        return self.core.do_cg

    @do_cg.setter
    def do_cg(self, value: bool):
        self.core.do_cg = value

    @property
    def do_dc(self) -> bool:
        """Whether to perform DC analysis.

        Returns
        -------
        bool
            True if DC analysis is to be performed, False otherwise.
        """
        return self.core.do_dc

    @do_dc.setter
    def do_dc(self, value: bool):
        self.core.do_dc = value

    @property
    def do_dc_res_only(self) -> bool:
        """Whether to perform DC resistance only analysis.

        Returns
        -------
        bool
            True if DC resistance only analysis is to be performed, False otherwise.
        """
        return self.core.do_dc_res_only

    @do_dc_res_only.setter
    def do_dc_res_only(self, value: bool):
        self.core.do_dc_res_only = value

    @property
    def save_fields(self) -> bool:
        """Whether to save fields.

        Returns
        -------
        bool
            True if fields are to be saved, False otherwise.
        """
        return self.core.save_fields

    @save_fields.setter
    def save_fields(self, value: bool):
        self.core.save_fields = value

    @property
    def solution_frequency(self) -> float:
        """Solution frequency in Hz.

        Returns
        -------
        float
            Solution frequency in Hz.
        """
        return self._pedb.value(self.core.solution_frequency)

    @solution_frequency.setter
    def solution_frequency(self, value: float):
        self.core.solution_frequency = str(self._pedb.value(value))
