# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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


from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
    AdaptType as GrpcAdaptType,
    HFSSGeneralSettings as GrpcHFSSGeneralSettings,
)


class HFSSGeneralSettings(GrpcHFSSGeneralSettings):
    """PyEDB-core HFSS general settings class."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = pedb

    @property
    def adaptive_solution_type(self) -> str:
        """Adaptive solution type.

        Returns
        -------
        str
            Adaptive solution type name.

        """
        return self.adaptive_solution_type.name

    @adaptive_solution_type.setter
    def adaptive_solution_type(self, value):
        if isinstance(value, str):
            if value.lower() == "single":
                self.adaptive_solution_type = GrpcAdaptType.SINGLE
            elif value.lower() == "multi_frequencies":
                self.adaptive_solution_type = GrpcAdaptType.MULTI_FREQUENCIES
            elif value.lower() == "broad_band":
                self.adaptive_solution_type = GrpcAdaptType.BROADBAND
            elif value.lower() == "num_adapt_type":
                self.adaptive_solution_type = GrpcAdaptType.NUM_ADAPT_TYPE
