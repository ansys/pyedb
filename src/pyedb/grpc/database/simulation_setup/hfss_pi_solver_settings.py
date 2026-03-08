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

# Try to import the ANSYS 2026.1 gRPC package
try:
    from ansys.edb.core.simulation_setup.hfss_pi_simulation_settings import (
        HFSSPISolverSettings as CoreHFSSPISolverSettings,
    )
except ImportError as e:
    print(f"ANSYS 2026.1 gRPC package not available (expected in release 2026.1): {e}")


class HFSSPISolverSettings:
    """HFSS PI solver settings class."""

    def __init__(self, pedb, core: "CoreHFSSPISolverSettings"):
        self._pedb = pedb
        self.core = core

    @property
    def enhanced_low_frequency_accuracy(self) -> bool:
        """Flag indicating if enhanced low-frequency accuracy is enabled during simulation.

        Returns
        -------
        bool
            Enhanced low frequency accuracy setting value.
        """
        return self.core.enhanced_low_frequency_accuracy

    @enhanced_low_frequency_accuracy.setter
    def enhanced_low_frequency_accuracy(self, value: bool):
        """Set enhanced low-frequency accuracy setting.

        Parameters
        ----------
        value : bool
            Enhanced low frequency accuracy setting value.
        """
        self.core.enhanced_low_frequency_accuracy = value

    @property
    def via_area_cutoff_circ_elems(self) -> str:
        """Pwr/Gnd vias with an area smaller than this value are simplified during simulation.

        Returns
        -------
        str
            Via area cutoff circular elements setting value.
        """
        return self.core.via_area_cutoff_circ_elems

    @via_area_cutoff_circ_elems.setter
    def via_area_cutoff_circ_elems(self, value: str):
        """Set via area cutoff circular elements setting.

        Parameters
        ----------
        value : str
            Via area cutoff circular elements setting value.
        """
        self.core.via_area_cutoff_circ_elems = value
