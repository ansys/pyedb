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
    HFSSPISignalNetsSettings as GrpcHFSSPISignalNetsSettings,
)


class HFSSPISignalNetsSettings:
    """PyEDB HFSS PI signal nets settings class."""

    def __init__(self, pedb, core: "GrpcHFSSPISignalNetsSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def conductor_modeling(self) -> str:
        """Get the conductor modeling method.

        Returns
        -------
        str
            The conductor modeling method. Accepted values are 'mesh_inside' and 'impedance_boundary'.

        """
        return self.core.conductor_modeling.name.lower()

    @conductor_modeling.setter
    def conductor_modeling(self, value: str):
        """Set the conductor modeling method.

        Parameters
        ----------
        value : str
            The conductor modeling method.

        """
        model = self.core.conductor_modeling
        if not value.lower() in ["mesh_inside", "impedance_boundary"]:
            raise ValueError(
                "Invalid conductor modeling method. Accepted values are 'mesh_inside' and 'impedance_boundary'."
            )
        model.name = value.upper()
        self.core.conductor_modeling = model

    @property
    def error_tolerance(self) -> str:
        """Get the error tolerance.

        Returns
        -------
        str
            The error tolerance. Values are `et_0_0`, `et_0_02`, `et_0_04`, `et_0_06`, `et_0_08`, `et_0_1`
            `et_0_2`, `et_0_5`, `et_1_0`.
        """
        return self.core.error_tolerance.name.lower()

    @error_tolerance.setter
    def error_tolerance(self, value: str):
        """Set the error tolerance.

        Parameters
        ----------
        value : str
            The error tolerance. Values are `et_0_0`, `et_0_02`, `et_0_04`, `et_0_06`, `et_0_08`, `et_0_1`
            `et_0_2`, `et_0_5`, `et_1_0`.
        """
        tolerance = self.core.error_tolerance
        valid_values = ["et_0_0", "et_0_02", "et_0_04", "et_0_06", "et_0_08", "et_0_1", "et_0_2", "et_0_5", "et_1_0"]
        if not value.lower() in valid_values:
            raise ValueError(f"Invalid error tolerance. Accepted values are {valid_values}.")
        tolerance.name = value.upper()
        self.core.error_tolerance = tolerance

    @property
    def include_improved_dielectric_fill_refinement(self) -> bool:
        """Get the flag for improved dielectric fill refinement.

        Returns
        -------
        bool
            True if improved dielectric fill refinement is included, False otherwise.

        """
        return self.core.include_improved_dielectric_fill_refinement

    @include_improved_dielectric_fill_refinement.setter
    def include_improved_dielectric_fill_refinement(self, value: bool):
        self.core.include_improved_dielectric_fill_refinement = value

    @property
    def include_improved_loss_handling(self) -> bool:
        """Get the flag for improved loss handling.

        Returns
        -------
        bool
            True if improved loss handling is included, False otherwise.

        """
        return self.core.include_improved_loss_handling

    @include_improved_loss_handling.setter
    def include_improved_loss_handling(self, value: bool):
        self.core.include_improved_loss_handling = value
