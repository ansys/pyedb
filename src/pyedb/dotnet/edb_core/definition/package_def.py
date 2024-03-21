# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pyedb.dotnet.edb_core.dotnet.database import PolygonDataDotNet
from pyedb.dotnet.edb_core.edb_data.obj_base import ObjBase
from pyedb.generic.general_methods import pyedb_function_handler


class PackageDef(ObjBase):
    """Manages EDB functionalities for package definitions.

    Parameters
    ----------
    pedb : :class:`pyedb.edb`
        Edb object.
    edb_object : object
        Edb PackageDef Object
    """

    def __init__(self, pedb, edb_object=None, name=None):
        self._pedb = pedb
        if edb_object is None and name is not None:
            self._edb_object = self.__create_from_name(name)
        else:
            self._edb_object = edb_object

    @pyedb_function_handler
    def __create_from_name(self, name):
        """Create a package defininitiion.

        Parameters
        ----------
        name: str
            Name of the package definition.

        Returns
        -------
        edb_object: object
            EDB PackageDef Object
        """
        edb_object = self._pedb.edb_api.definition.PackageDef.Create(self._pedb.active_db, name)
        pointA = self._pedb.edb_api.geometry.point_data(
            self._pedb.edb_value(0),
            self._pedb.edb_value(0),
        )

        polygon = PolygonDataDotNet(self._pedb).create_from_bbox([pointA, pointA])
        edb_object.SetExteriorBoundary(polygon)
        return edb_object

    @property
    def maximum_power(self):
        """Maximum power of the package."""
        return self._edb_object.GetMaximumPower().ToDouble()

    @maximum_power.setter
    def maximum_power(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetMaximumPower(value)

    @property
    def therm_cond(self):
        """Thermal conductivity of the package."""
        return self._edb_object.GetTherm_Cond().ToDouble()

    @therm_cond.setter
    def therm_cond(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetTherm_Cond(value)

    @property
    def theta_jb(self):
        """Theta Junction-to-Board of the package."""
        return self._edb_object.GetTheta_JB().ToDouble()

    @theta_jb.setter
    def theta_jb(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetTheta_JB(value)

    @property
    def theta_jc(self):
        """Theta Junction-to-Case of the package."""
        return self._edb_object.GetTheta_JC().ToDouble()

    @theta_jc.setter
    def theta_jc(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetTheta_JC(value)

    @property
    def height(self):
        """Height of the package."""
        return self._edb_object.GetHeight().ToDouble()

    @height.setter
    def height(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetHeight(value)
