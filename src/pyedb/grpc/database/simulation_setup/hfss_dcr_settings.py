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
    from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
        HFSSDCRSettings as GrpcHFSSDCRSettings,
    )


class HFSSDCRSettings:
    """PyEDB HFSS DC settings class."""

    def __init__(self, pedb, core: "GrpcHFSSDCRSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def max_passes(self) -> int:
        """Maximum number of conduction adaptive passes."""
        return self.core.max_passes

    @max_passes.setter
    def max_passes(self, value: int):
        """Set maximum number of conduction adaptive passes."""
        self.core.max_passes = value

    @property
    def min_converged_passes(self) -> int:
        """Minimum number of converged conduction adaptive passes."""
        return self.core.min_converged_passes

    @min_converged_passes.setter
    def min_converged_passes(self, value: int):
        """Set minimum number of converged conduction adaptive passes."""
        self.core.min_converged_passes = value

    @property
    def min_passes(self) -> int:
        """Minimum number of conduction adaptive passes."""
        return self.core.min_passes

    @min_passes.setter
    def min_passes(self, value: int):
        """Set minimum number of conduction adaptive passes."""
        self.core.min_passes = value

    @property
    def percent_error(self) -> float:
        """Conduction adaptive percent error."""
        return self.core.percent_error

    @percent_error.setter
    def percent_error(self, value: float):
        """Set conduction adaptive percent error."""
        self.core.percent_error = value

    @property
    def percent_refinement_per_pass(self) -> float:
        """Conduction adaptive percent refinement per pass."""
        return self.core.percent_refinement_per_pass

    @percent_refinement_per_pass.setter
    def percent_refinement_per_pass(self, value: float):
        """Set conduction adaptive percent refinement per pass."""
        self.core.percent_refinement_per_pass = value
