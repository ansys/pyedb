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

from ansys.edb.core.definition.package_def import PackageDef as GrpcPackageDef
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData

from pyedb.generic.settings import settings
from pyedb.grpc.database.utility.heat_sink import HeatSink
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.decorators import deprecated_property


class PackageDef:
    """Manages EDB package definitions.

    Parameters
    ----------
    pedb : :class:`Edb <pyedb.grpc.edb.Edb>`
        Edb object.
    edb_object : object
    Edb PackageDef Object
        component_part_name : str, optional
        Part name of the component.
    extent_bounding_box : list, optional
        Bounding box defines the shape of the package. For example, [[0, 0], ["2mm", "2mm"]].

    """

    def __init__(self, pedb, edb_object=None, name=None, component_part_name=None, extent_bounding_box=None):
        if not edb_object:
            if name:
                edb_object = GrpcPackageDef.create(db=pedb.active_db, name=name)
            else:
                raise AttributeError("Name must be provided to create and instantiate a PackageDef object.")
        self.core = edb_object
        self._pedb = pedb
        self._heat_sink = None
        if not self.core and name:
            self.__create_from_name(name, component_part_name, extent_bounding_box)

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
        self.core = GrpcPackageDef.create(self._pedb.active_db, name)
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
            settings.logger.warning(
                "Package creation uses bounding box but it cannot be inferred. "
                "Please set argument 'component_part_name' or 'extent_bounding_box'."
            )
        polygon_data = GrpcPolygonData(points=bbox)
        self.exterior_boundary = polygon_data

    @property
    def name(self):
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @property
    def exterior_boundary(self) -> GrpcPolygonData:
        """Get the exterior boundary of a package definition.

        Returns
        -------
        :class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

        """
        return GrpcPolygonData(self.core.exterior_boundary.points)

    @exterior_boundary.setter
    def exterior_boundary(self, value):
        self.core.exterior_boundary = value

    @property
    def maximum_power(self) -> float:
        """Maximum power of the package.

        Returns
        -------
        float
            maximum power value.
        """
        return Value(self.core.maximum_power)

    @maximum_power.setter
    def maximum_power(self, value):
        self.core.maximum_power = Value(value)

    @property
    def thermal_conductivity(self) -> float:
        """Thermal conductivity of the package.

        Returns
        -------
        float
            Thermal conductivity value.

        """
        return Value(self.core.thermal_conductivity)

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        self.core.thermal_conductivity = Value(value)

    @property
    def theta_jb(self) -> float:
        """Theta Junction-to-Board of the package.

        Returns
        -------
        float
            Theta jb value.
        """
        return Value(self.core.theta_jb)

    @theta_jb.setter
    def theta_jb(self, value):
        self.core.theta_jb = Value(value)

    @property
    def theta_jc(self) -> float:
        """Theta Junction-to-Case of the package.

        Returns
        -------
        float
            Theta jc value.
        """
        return Value(self.core.theta_jc)

    @theta_jc.setter
    def theta_jc(self, value):
        self.core.theta_jc = Value(value)

    @property
    def height(self) -> float:
        """Height of the package.

        Returns
        -------
        float
            Height value.
        """
        return Value(self.core.height)

    @height.setter
    def height(self, value):
        self.core.height = Value(value)

    @property
    def heat_sink(self) -> HeatSink:
        """Package heat sink.

        Returns
        -------
        :class:`HeatSink <pyedb.grpc.database.utility.heat_sink.HeatSink>`
            HeatSink object.
        """
        try:
            return HeatSink(self._pedb, self.core.heat_sink)
        except Exception as e:
            settings.logger.error(
                f"A(n) {type(e).__name__} error occurred while attempting to access 'heatsink' "
                f"property for object {self}: {str(e)}"
            )

    @property
    @deprecated_property
    def heatsink(self):
        """Property added for .NET compatibility.
        . deprecated:: pyedb 0.43.0
        Use :func:`heat_sink` instead.

        """
        return self.heat_sink

    @staticmethod
    def create(edb, name: str) -> "PackageDef":
        """Create a package definition.

        Parameters
        ----------
        edb : :class:`Edb <pyedb.grpc.edb.Edb>`
            Edb object.
        name: str
            Name of the package definition.

        Returns
        -------
        :class:`PackageDef <pyedb.grpc.database.definition.package_def.PackageDef>`
            PackageDef object.
        """
        grpc_package = GrpcPackageDef.create(edb.active_db, name)
        if grpc_package.is_null:
            raise RuntimeError(f"Failed to create package {name}")
        return PackageDef(edb, grpc_package)

    def set_heatsink(self, fin_base_height, fin_height, fin_orientation, fin_spacing, fin_thickness) -> HeatSink:
        """Set Heat sink.
        Parameters
        ----------
        fin_base_height : str, float
            Fin base height.
        fin_height : str, float
            Fin height.
        fin_orientation : str
            Fin orientation. Supported values, `x_oriented`, `y_oriented`.
        fin_spacing : str, float
            Fin spacing.
        fin_thickness : str, float
            Fin thickness.
        """
        from ansys.edb.core.utility.heat_sink import (
            HeatSink as GrpcHeatSink,
            HeatSinkFinOrientation as GrpcHeatSinkFinOrientation,
        )

        if fin_orientation == "x_oriented":
            fin_orientation = GrpcHeatSinkFinOrientation.X_ORIENTED
        elif fin_orientation == "y_oriented":
            fin_orientation = GrpcHeatSinkFinOrientation.Y_ORIENTED
        else:
            fin_orientation = GrpcHeatSinkFinOrientation.OTHER_ORIENTED
        self.core.heat_sink = GrpcHeatSink(
            Value(fin_thickness),
            Value(fin_spacing),
            Value(fin_base_height),
            Value(fin_height),
            fin_orientation,
        )
        return self.heat_sink
