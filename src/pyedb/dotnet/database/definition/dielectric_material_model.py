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

from pyedb.dotnet.database.utilities.obj_base import ObjBase
from pyedb.dotnet.database.utilities.value import Value


class DielectricMaterialModel(ObjBase):
    """Class for dielectric material model."""


class DjordjecvicSarkarModel(DielectricMaterialModel):
    """Class for Djordjecvic-Sarkar model."""

    @classmethod
    def create(cls, pedb) -> "DjordjecvicSarkarModel":
        """Constructs a Djordjecvic-Sarkar model with the following default values.
        Frequency: 1GHz. Relative Permitivity: 4. Loss Tangent: 0.02.Use DC relative permitivity: false.
        DC relative permitivity: 5.DC conductivity: 1e-12."""
        return cls(pedb, pedb._edb.Definition.DjordjecvicSarkarModel())

    @property
    def dc_conductivity(self) -> float | Value:
        """DC conductivity."""
        return self._pedb.value(self._edb_object.GetDCConductivity())

    @dc_conductivity.setter
    def dc_conductivity(self, value: float | Value):
        self._edb_object.SetDCConductivity(value)

    @property
    def dc_relative_permittivity(self) -> float | Value:
        """DC relative permittivity."""
        return self._pedb.value(self._edb_object.GetDCRelativePermitivity())

    @dc_relative_permittivity.setter
    def dc_relative_permittivity(self, value: float | Value):
        self._edb_object.SetDCRelativePermitivity(value)

    @property
    def frequency(self) -> float | Value:
        """Frequency in Hz."""
        return self._pedb.value(self._edb_object.GetFrequency()) * 1e9

    @frequency.setter
    def frequency(self, value: float | Value):
        value = self._pedb.value(value) * 1e-9
        self._edb_object.SetFrequency(value)

    @property
    def loss_tangent_at_frequency(self) -> float | Value:
        """Loss tangent at frequency."""
        return self._pedb.value(self._edb_object.GetLossTangentAtFrequency())

    @loss_tangent_at_frequency.setter
    def loss_tangent_at_frequency(self, value: float | Value):
        self._edb_object.SetLossTangentAtFrequency(self._pedb.value(value).core)

    @property
    def relative_permittivity_at_frequency(self):
        return self._pedb.value(self._edb_object.GetRelativePermitivityAtFrequency())

    @relative_permittivity_at_frequency.setter
    def relative_permittivity_at_frequency(self, value: float | Value):
        self._edb_object.SetRelativePermitivityAtFrequency(self._pedb.value(value))

    @property
    def use_dc_relative_permittivity(self):
        """whether the DC relative permittivity nominal value is used"""
        return self._edb_object.UseDCRelativePermitivity()

    @use_dc_relative_permittivity.setter
    def use_dc_relative_permittivity(self, value: bool):
        self._edb_object.SetUseDCRelativePermitivity(value)


class DebyeModel(DielectricMaterialModel):
    """Class for Debye model."""


class MultipoleDebyeModel(DielectricMaterialModel):
    """Class for multipole Debye model."""
