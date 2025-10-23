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


class HeatSink:
    """Heatsink model description.

    Parameters
    ----------
    pedb : :class:`pyedb.dotnet.edb.Edb`
        Inherited object.
    edb_object : :class:`Ansys.Ansoft.Edb.Utility.HeatSink`,
    """

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._fin_orientation_type = {
            "x_oriented": self._pedb.core.Utility.HeatSinkFinOrientation.XOriented,
            "y_oriented": self._pedb.core.Utility.HeatSinkFinOrientation.YOriented,
            "other_oriented": self._pedb.core.Utility.HeatSinkFinOrientation.OtherOriented,
        }

        if edb_object:
            self._edb_object = edb_object
        else:
            self._edb_object = self._pedb.core.Utility.HeatSink()

    @property
    def fin_base_height(self):
        """The base elevation of the fins."""
        return self._edb_object.FinBaseHeight.ToDouble()

    @fin_base_height.setter
    def fin_base_height(self, value):
        self._edb_object.FinBaseHeight = self._pedb.edb_value(value)

    @property
    def fin_height(self):
        """The fin height."""
        return self._edb_object.FinHeight.ToDouble()

    @fin_height.setter
    def fin_height(self, value):
        self._edb_object.FinHeight = self._pedb.edb_value(value)

    @property
    def fin_orientation(self):
        """The fin orientation."""
        temp = self._edb_object.FinOrientation
        return list(self._fin_orientation_type.keys())[list(self._fin_orientation_type.values()).index(temp)]

    @fin_orientation.setter
    def fin_orientation(self, value):
        self._edb_object.FinOrientation = self._fin_orientation_type[value]

    @property
    def fin_spacing(self):
        """The fin spacing."""
        return self._edb_object.FinSpacing.ToDouble()

    @fin_spacing.setter
    def fin_spacing(self, value):
        self._edb_object.FinSpacing = self._pedb.edb_value(value)

    @property
    def fin_thickness(self):
        """The fin thickness."""
        return self._edb_object.FinThickness.ToDouble()

    @fin_thickness.setter
    def fin_thickness(self, value):
        self._edb_object.FinThickness = self._pedb.edb_value(value)
