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

from ansys.edb.core.utility.heat_sink import (
    HeatSinkFinOrientation as GrpcHeatSinkFinOrientation,
)
from ansys.edb.core.utility.value import Value as GrpcValue


class HeatSink:
    """Heatsink model description.

    Parameters
    ----------
    pedb : :class:`Edb < pyedb.grpc.edb.Edb>`
        Inherited object.
    """

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object
        self._fin_orientation_type = {
            "x_oriented": GrpcHeatSinkFinOrientation.X_ORIENTED,
            "y_oriented": GrpcHeatSinkFinOrientation.Y_ORIENTED,
            "other_oriented": GrpcHeatSinkFinOrientation.OTHER_ORIENTED,
        }

    @property
    def fin_base_height(self) -> float:
        """The base elevation of the fins.

        Returns
        -------
        float
            Height value.
        """
        return self._edb_object.fin_base_height.value

    @fin_base_height.setter
    def fin_base_height(self, value):
        self._edb_object.fin_base_height = GrpcValue(value)

    @property
    def fin_height(self) -> float:
        """Fin height.

        Returns
        -------
        float
            Fin height value.

        """
        return self._edb_object.fin_height.value

    @fin_height.setter
    def fin_height(self, value):
        self._edb_object.fin_height = GrpcValue(value)

    @property
    def fin_orientation(self) -> str:
        """Fin orientation.

        Returns
        -------
        str
            Fin orientation.
        """
        return self._edb_object.fin_orientation.name.lower()

    @fin_orientation.setter
    def fin_orientation(self, value):
        self._edb_object.fin_orientation = self._fin_orientation_type[value]

    @property
    def fin_spacing(self) -> float:
        """Fin spacing.

        Returns
        -------
        float
            Fin spacing value.

        """
        return self._edb_object.fin_spacing.value

    @fin_spacing.setter
    def fin_spacing(self, value):
        self._edb_object.fin_spacing = GrpcValue(value)

    @property
    def fin_thickness(self) -> float:
        """Fin thickness.

        Returns
        -------
        float
            Fin thickness value.

        """
        return self._edb_object.fin_thickness.value

    @fin_thickness.setter
    def fin_thickness(self, value):
        self._edb_object.fin_thickness = GrpcValue(value)
