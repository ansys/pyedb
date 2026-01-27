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
import warnings

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
        HFSSDCRSettings as CoreHFSSDCRSettings,
    )


class HFSSDCRSettings:
    """PyEDB HFSS DC settings class."""

    def __init__(self, pedb, core: "CoreHFSSDCRSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def conduction_max_passes(self) -> int:
        """Maximum number of conduction adaptive passes.

        ... deprecated:: 0.77.3
        Use :attr:`max_passes <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.max_passes>`
        nstead.
        """
        warnings.warn("`conduction_max_passes` is deprecated. Use `max_passes` instead.", DeprecationWarning)
        return self.max_passes

    @conduction_max_passes.setter
    def conduction_max_passes(self, value: int):
        """Set maximum number of conduction adaptive passes.

        ... deprecated:: 0.77.3
        Use :attr:`max_passes <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.max_passes>`
        instead.
        """
        warnings.warn("`conduction_max_passes` is deprecated. Use `max_passes` instead.", DeprecationWarning)
        self.max_passes = value

    @property
    def max_passes(self) -> int:
        """Maximum number of conduction adaptive passes."""
        return self.core.max_passes

    @max_passes.setter
    def max_passes(self, value: int):
        """Set maximum number of conduction adaptive passes."""
        self.core.max_passes = value

    @property
    def conduction_min_converged_passes(self) -> int:
        """Minimum number of converged conduction adaptive passes.

        ... deprecated:: 0.77.3
        Use :attr:`min_converged_passes
        <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.min_converged_passes>`
        instead.
        """
        warnings.warn(
            "`conduction_min_converged_passes` is deprecated. Use `min_converged_passes` instead.", DeprecationWarning
        )
        return self.min_converged_passes

    @conduction_min_converged_passes.setter
    def conduction_min_converged_passes(self, value: int):
        """Set minimum number of converged conduction adaptive passes.

        ... deprecated:: 0.77.3
        Use :attr:`min_converged_passes
        <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.min_converged_passes>`
        instead.
        """
        warnings.warn(
            "`conduction_min_converged_passes` is deprecated. Use `min_converged_passes` instead.", DeprecationWarning
        )
        self.min_converged_passes = value

    @property
    def min_converged_passes(self) -> int:
        """Minimum number of converged conduction adaptive passes."""
        return self.core.min_converged_passes

    @min_converged_passes.setter
    def min_converged_passes(self, value: int):
        """Set minimum number of converged conduction adaptive passes."""
        self.core.min_converged_passes = value

    @property
    def conduction_min_passes(self) -> int:
        """Minimum number of conduction adaptive passes.

        ... deprecated:: 0.77.3
        Use :attr:`min_passes <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.min_passes>`
        instead.
        """
        warnings.warn("`conduction_min_passes` is deprecated. Use `min_passes` instead.", DeprecationWarning)
        return self.min_passes

    @conduction_min_passes.setter
    def conduction_min_passes(self, value: int):
        """Set minimum number of conduction adaptive passes.

        ... deprecated:: 0.77.3
        Use :attr:`min_passes
        <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.min_passes>`
        instead.
        """
        warnings.warn("`conduction_min_passes` is deprecated. Use `min_passes` instead.", DeprecationWarning)
        self.min_passes = value

    @property
    def min_passes(self) -> int:
        """Minimum number of conduction adaptive passes."""
        return self.core.min_passes

    @min_passes.setter
    def min_passes(self, value: int):
        """Set minimum number of conduction adaptive passes."""
        self.core.min_passes = value

    @property
    def conduction_per_error(self) -> float:
        """Conduction adaptive percent error.

        ... deprecated:: 0.77.3
        Use :attr:`percent_error <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.percent_error>`
        instead.
        """
        warnings.warn("`conduction_percent_error` is deprecated. Use `percent_error` instead.", DeprecationWarning)
        return self.percent_error

    @conduction_per_error.setter
    def conduction_per_error(self, value: float):
        """Set conduction adaptive percent error.

        ... deprecated:: 0.77.3
        Use :attr:`percent_error <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.percent_error>`
        instead.
        """
        warnings.warn("`conduction_percent_error` is deprecated. Use `percent_error` instead.", DeprecationWarning)
        self.percent_error = value

    @property
    def percent_error(self) -> float:
        """Conduction adaptive percent error."""
        return self.core.percent_error

    @percent_error.setter
    def percent_error(self, value: float):
        """Set conduction adaptive percent error."""
        self.core.percent_error = value

    @property
    def conduction_per_refine(self) -> float:
        """Conduction adaptive percent refinement per pass.

        ... deprecated:: 0.77.3
        Use :attr:
        `percent_refinement_per_pass
        <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.percent_refinement_per_pass>`
        instead.
        """
        return self.percent_refinement_per_pass

    @conduction_per_refine.setter
    def conduction_per_refine(self, value: float):
        """Set conduction adaptive percent refinement per pass.

        ... deprecated:: 0.77.3
        Use :attr:
        `percent_refinement_per_pass
        <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings.percent_refinement_per_pass>`
        instead.
        """
        self.percent_refinement_per_pass = value

    @property
    def percent_refinement_per_pass(self) -> float:
        """Conduction adaptive percent refinement per pass."""
        return self.core.percent_refinement_per_pass

    @percent_refinement_per_pass.setter
    def percent_refinement_per_pass(self, value: float):
        """Set conduction adaptive percent refinement per pass."""
        self.core.percent_refinement_per_pass = value
