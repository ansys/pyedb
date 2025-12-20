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


import math
from typing import Union

from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.primitive.polygon import Polygon as GrpcPolygon

from pyedb.grpc.database.geometry.polygon_data import PolygonData
from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.layers.stackup_layer import StackupLayer
from pyedb.grpc.database.layout.layout import Layout
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import Value


class Polygon(Primitive):
    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb
        Primitive.__init__(self, pedb, edb_object)

    @property
    def layer(self) -> Layer:
        """Layer of the polygon.

        Returns
        -------
        :class:`Layer <pyedb.edb.database.layers.layer.Layer>`
            Layer object.

        """
        from pyedb.grpc.database.layers.layer import Layer

        return Layer(self.core.layer)

    @layer.setter
    def layer(self, value: Union[str, Layer]):
        """Set layer of the polygon.

        Parameters
        ----------
        value : Union[str, :class:`Layer <pyedb.edb.database.layers.layer.Layer>`]
            Layer name or Layer object.

        """
        if isinstance(value, str):
            if value in self._pedb.stackup.layers:
                self.core.layer = self._pedb.stackup.layers[value].core
            else:
                raise ValueError(f"Layer {value} does not exist in the stackup.")
        elif isinstance(value, StackupLayer) or isinstance(value, Layer):
            self.core.layer = value.core
        else:
            raise TypeError("Value must be a string or Layer object.")

    @property
    def type(self) -> str:
        """Primitive type.

        Return
        ------
        str
            Polygon type.

        """
        return self.core.primitive_type.name.lower()

    @property
    def has_self_intersections(self) -> bool:
        """Check if Polygon has self intersections.

        Returns
        -------
        bool
        """
        return self.polygon_data.has_self_intersections()

    @classmethod
    def create(cls, layout: Layout, layer: Union[str, Layer], net: Union[str, "Net"] = None, polygon_data=None):
        """
        Create a polygon in the specified layout, layer, and net using the provided polygon data.

        Parameters
        ----------
        layout : Layout
            The layout in which the polygon will be created. If not provided, the active layout of the `pedb`
            instance will be used.
        layer : Union[str, Layer]
            The layer in which the polygon will be created. This parameter is required and must be specified.
        net : Union[str, Net], optional
            The net to which the polygon will belong. If not provided, the polygon will not be associated with a
            net.
        polygon_data : list or GrpcPolygonData, optional
            The data defining the polygon. This can be a list of points or an instance of `GrpcPolygonData`.
            This parameter is required and must be specified.

        Returns
        -------
        :class:`Polygon <ansys.edb.core.primitive.polygon.Polygon>`
            The created polygon object.

        Raises
        ------
        ValueError
            If the `layer` parameter is not provided.
        ValueError
            If the `polygon_data` parameter is not provided.

        Notes
        -----
        - If `polygon_data` is provided as a list, it will be converted to a `GrpcPolygonData` object.
        - The created polygon is added to the modeler primitives of the `pedb` instance.

        """
        from pyedb.grpc.database.net.net import Net

        if not layout:
            raise Exception("Layout is required to create a polygon.")
        if not layer:
            raise ValueError("Layer is required to create a polygon.")
        if not polygon_data:
            raise ValueError("Polygon data or point list is required to create a polygon.")
        if isinstance(polygon_data, list):
            polygon_data = GrpcPolygonData(polygon_data)
        if isinstance(polygon_data, PolygonData):
            polygon_data = polygon_data.core
        if isinstance(layer, Layer):
            layer = layer.core
        if isinstance(net, Net):
            net = net.core
        edb_object = GrpcPolygon.create(layout=layout.core, layer=layer, net=net, polygon_data=polygon_data)
        new_polygon = cls(layout._pedb, edb_object)
        # keep modeler cache in sync
        layout._pedb.modeler._add_primitive(new_polygon)

        return new_polygon

    def delete(self):
        """Delete polygon from layout."""
        # keeping cache in sync
        self._pedb.modeler._remove_primitive(self)
        self.core.delete()

    def fix_self_intersections(self) -> list[any]:
        """Remove self intersections if they exist.

        Returns
        -------
        List[:class:`Polygon <ansys.edb.core.primitive.polygon.Polygon>`]
            All new polygons created from the removal operation.

        """
        new_polys = []
        if self.has_self_intersections:
            new_polygons = self.polygon_data.core.remove_self_intersections()
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
        voids = self.voids
        polygon_data = self.polygon_data
        cloned_polygon = self.create(
            layout=self._pedb.active_layout, layer=self.layer, net=self.net, polygon_data=polygon_data
        )
        for void in voids:
            cloned_polygon.add_void(void)
        return cloned_polygon

    def duplicate_across_layers(self, layers) -> bool:
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
                            polygon_data=void.polygon_data,
                        )
                        duplicate_polygon.add_void(duplicate_void)
            else:
                return False
        return True

    def move(self, vector) -> bool:
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
            _vector = [Value(pt) for pt in vector]
            self.polygon_data = PolygonData(self.polygon_data.core.move(_vector))
            return True
        return False

    def scale(self, factor, center=None) -> bool:
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
                center = self.polygon_data.core.bounding_circle()[0]
                if center:
                    self.polygon_data = PolygonData(self.polygon_data.core.scale(factor, center))
                    return True
                else:
                    self._pedb.logger.error(f"Failed to evaluate center on primitive {self.id}")
            elif isinstance(center, list) and len(center) == 2:
                center = GrpcPointData([Value(center[0]), Value(center[1])])
                self.polygon_data = PolygonData(self.polygon_data.core.scale(factor, center))
                return True
        return False

    def rotate(self, angle, center=None) -> bool:
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
                center = self.polygon_data.core.bounding_circle()[0]
                if center:
                    self.polygon_data = self.polygon_data.core.rotate(angle * math.pi / 180, center)
                    return True
            elif isinstance(center, list) and len(center) == 2:
                self.polygon_data = self.polygon_data.core.rotate(angle * math.pi / 180, center)
                return True
        return False

    def move_layer(self, layer) -> bool:
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
            self.layer = self._pedb.stackup.layers.get(layer, None)
            if layer:
                return True
        return False

    def in_polygon(
        self,
        point_data,
        include_partial=True,
    ) -> bool:
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
        int_val = 1 if self.polygon_data.core.is_inside(GrpcPointData(point_data)) else 0
        if int_val == 0:
            return False
        else:
            int_val = self.polygon_data.core.intersection_type(GrpcPolygonData(point_data))
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
            polygon = self._pedb.modeler.create_polygon(
                points=polygon, layer_name=self.layer.name, net_name=self.net_name
            )
        self.core.add_void(polygon.core)
