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

from pyedb.dotnet.edb_core.geometry.polygon_data import PolygonData
from pyedb.dotnet.edb_core.utilities.obj_base import ObjBase
from pyedb.edb_logger import pyedb_logger


class PackageDef(ObjBase):
    """Manages EDB functionalities for package definitions.

    Parameters
    ----------
    pedb : :class:`pyedb.edb`
        Edb object.
    edb_object : object
    Edb PackageDef Object
        component_part_name : str, optional
        Part name of the component.
    extent_bounding_box : list, optional
        Bounding box defines the shape of the package. For example, [[0, 0], ["2mm", "2mm"]].

    """

    def __init__(self, pedb, edb_object=None, name=None, component_part_name=None, extent_bounding_box=None):
        super().__init__(pedb, edb_object)
        if self._edb_object is None and name is not None:
            self._edb_object = self.__create_from_name(name, component_part_name, extent_bounding_box)
        else:
            self._edb_object = edb_object

    def __create_from_name(self, name, component_part_name=None, extent_bounding_box=None):
        """Create a package definition.

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
        if component_part_name:
            x_pt1, y_pt1, x_pt2, y_pt2 = list(
                self._pedb.components.definitions[component_part_name].components.values()
            )[0].bounding_box
            x_mid = (x_pt1 + x_pt2) / 2
            y_mid = (y_pt1 + y_pt2) / 2
            bbox = [[y_pt1 - y_mid, x_pt1 - x_mid], [y_pt2 - y_mid, x_pt2 - x_mid]]
        else:
            bbox = extent_bounding_box
        if bbox is None:
            pyedb_logger.warning(
                "Package creation uses bounding box but it cannot be inferred. "
                "Please set argument 'component_part_name' or 'extent_bounding_box'."
            )
        polygon_data = PolygonData(self._pedb, create_from_bounding_box=True, points=bbox)

        edb_object.SetExteriorBoundary(polygon_data._edb_object)
        return edb_object

    def delete(self):
        """Delete a package definition object from the database."""
        return self._edb_object.Delete()

    @property
    def exterior_boundary(self):
        """Get the exterior boundary of a package definition."""
        return PolygonData(self._pedb, self._edb_object.GetExteriorBoundary()).points

    @exterior_boundary.setter
    def exterior_boundary(self, value):
        self._edb_object.SetExteriorBoundary(value._edb_object)

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

    def set_heatsink(self, fin_base_height, fin_height, fin_orientation, fin_spacing, fin_thickness):
        from pyedb.dotnet.edb_core.utilities.heatsink import HeatSink

        heatsink = HeatSink(self._pedb)
        heatsink.fin_base_height = fin_base_height
        heatsink.fin_height = fin_height
        heatsink.fin_orientation = fin_orientation
        heatsink.fin_spacing = fin_spacing
        heatsink.fin_thickness = fin_thickness
        self._edb_object.SetHeatSink(heatsink._edb_object)

    @property
    def heatsink(self):
        """Component heatsink."""
        from pyedb.dotnet.edb_core.utilities.heatsink import HeatSink

        flag, edb_object = self._edb_object.GetHeatSink()
        if flag:
            return HeatSink(self._pedb, edb_object)
        else:
            return None
