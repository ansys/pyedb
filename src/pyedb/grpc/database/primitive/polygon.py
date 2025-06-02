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


import math

from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.primitive.polygon import Polygon as GrpcPolygon
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.database.primitive.primitive import Primitive


class Polygon(GrpcPolygon, Primitive):
    def __init__(self, pedb, edb_object):
        GrpcPolygon.__init__(self, edb_object.msg)
        Primitive.__init__(self, pedb, edb_object)
        self._pedb = pedb

    @property
    def type(self):
        """Primitive type.

        Return
        ------
        str
            Polygon type.

        """
        return self.primitive_type.name.lower()

    @property
    def has_self_intersections(self):
        """Check if Polygon has self intersections.

        Returns
        -------
        bool
        """
        return self.polygon_data.has_self_intersections()

    def fix_self_intersections(self):
        """Remove self intersections if they exist.

        Returns
        -------
        List[:class:`Polygon <ansys.edb.core.primitive.polygon.Polygon>`]
            All new polygons created from the removal operation.

        """
        new_polys = []
        if self.has_self_intersections:
            new_polygons = self.polygon_data.remove_self_intersections()
            self.polygon_data = new_polygons[0]
            for p in new_polygons[1:]:
                cloned_poly = self.create(
                    layout=self._pedb.active_layout, layer=self.layer.name, net=self.net, polygon_data=p
                )
                new_polys.append(cloned_poly)
        return new_polys

    def clone(self):
        """Duplicate polygon.

        Returns
        -------
        :class:`Polygon <ansys.edb.core.primitive.polygon.Polygon>`
            Cloned polygon.

        """
        polygon_data = self.polygon_data
        duplicated_polygon = self.create(
            layout=self._pedb.active_layout, layer=self.layer, net=self.net, polygon_data=polygon_data
        )
        for void in self.voids:
            duplicated_polygon.add_void(void)
        return duplicated_polygon

    def duplicate_across_layers(self, layers):
        """Duplicate across layer a primitive object.

        Parameters:

        layers: list
            list of str, with layer names

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        for layer in layers:
            if layer in self._pedb.stackup.layers:
                duplicate_polygon = self.create(
                    layout=self._pedb.active_layout, layer=layer, net=self.net.name, polygon_data=self.polygon_data
                )
                if duplicate_polygon:
                    for void in self.voids:
                        duplicate_void = self.create(
                            layout=self._pedb.active_layout,
                            layer=layer,
                            net=self.net.name,
                            polygon_data=void.cast().polygon_data,
                        )
                        duplicate_polygon.add_void(duplicate_void)
            else:
                return False
        return True

    def move(self, vector):
        """Move polygon along a vector.

        Parameters
        ----------
        vector : List of float or str [x,y].

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edbapp = ansys.aedt.core.Edb("myproject.aedb")
        >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
        >>> for polygon in top_layer_polygon:
        >>>     polygon.move(vector=["2mm", "100um"])
        """
        if vector and isinstance(vector, list) and len(vector) == 2:
            _vector = [GrpcValue(pt).value for pt in vector]
            self.polygon_data = self.polygon_data.move(_vector)
            return True
        return False

    def scale(self, factor, center=None):
        """Scales the polygon relative to a center point by a factor.

        Parameters
        ----------
        factor : float
            Scaling factor.
        center : List of float or str [x,y], optional
            If None scaling is done from polygon center.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.
        """
        if not isinstance(factor, str):
            factor = float(factor)
            if not center:
                center = self.polygon_data.bounding_circle()[0]
                if center:
                    self.polygon_data = self.polygon_data.scale(factor, center)
                    return True
                else:
                    self._pedb.logger.error(f"Failed to evaluate center on primitive {self.id}")
            elif isinstance(center, list) and len(center) == 2:
                center = GrpcPointData([GrpcValue(center[0]), GrpcValue(center[1])])
                self.polygon_data = self.polygon_data.scale(factor, center)
                return True
        return False

    def rotate(self, angle, center=None):
        """Rotate polygon around a center point by an angle.

        Parameters
        ----------
        angle : float
            Value of the rotation angle in degree.
        center : List of float or str [x,y], optional
            If None rotation is done from polygon center.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edbapp = ansys.aedt.core.Edb("myproject.aedb")
        >>> top_layer_polygon = [poly for poly in edbapp.modeler.polygons if poly.layer_name == "Top Layer"]
        >>> for polygon in top_layer_polygon:
        >>>     polygon.rotate(angle=45)
        """
        if angle:
            if not center:
                center = self.polygon_data.bounding_circle()[0]
                if center:
                    self.polygon_data = self.polygon_data.rotate(angle * math.pi / 180, center)
                    return True
            elif isinstance(center, list) and len(center) == 2:
                self.polygon_data = self.polygon_data.rotate(angle * math.pi / 180, center)
                return True
        return False

    def move_layer(self, layer):
        """Move polygon to given layer.

        Parameters
        ----------
        layer : str
            layer name.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.
        """
        if layer and isinstance(layer, str) and layer in self._pedb.stackup.signal_layers:
            self.layer = self._pedb.stackup.layers[layer]
            return True
        return False

    def in_polygon(
        self,
        point_data,
        include_partial=True,
    ):
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        point_data : PointData Object or list of float
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        int_val = 1 if self.polygon_data.is_inside(GrpcPointData(point_data)) else 0
        if int_val == 0:
            return False
        else:
            int_val = self.polygon_data.intersection_type(GrpcPolygonData(point_data))
        # Intersection type:
        # 0 = objects do not intersect
        # 1 = this object fully inside other (no common contour points)
        # 2 = other object fully inside this
        # 3 = common contour points 4 = undefined intersection
        if int_val == 0:
            return False
        elif include_partial:
            return True
        elif int_val < 3:
            return True
        else:
            return False

    def add_void(self, polygon):
        if isinstance(polygon, list):
            polygon = self._pedb.modeler.create_polygon(points=polygon, layer_name=self.layer.name)
        return self._edb_object.add_void(polygon._edb_object)
