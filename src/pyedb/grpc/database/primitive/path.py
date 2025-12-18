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
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pyedb.grpc.database.net.net import Net

from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.primitive.path import (
    Path as GrpcPath,
    PathCornerType as GrpcPathCornerType,
    PathEndCapType as GrpcPathEndCapType,
)

from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import Value


class Path(Primitive):
    def __init__(self, pedb, edb_object=None):
        if edb_object:
            self.core = edb_object
            Primitive.__init__(self, pedb, edb_object)
        self._pedb = pedb

    @property
    def width(self) -> float:
        """Path width.

        Returns
        -------
        float
            Path width or None.
        """
        return Value(self.core.width)

    @width.setter
    def width(self, value):
        self.core.width = Value(value)

    @property
    def length(self) -> float:
        """Path length in meters.

        Returns
        -------
        float
            Path length in meters.
        """
        center_line_arcs = self.core.center_line.arc_data
        path_length = 0.0
        for arc in center_line_arcs:
            path_length += arc.length
        end_cap_style = self.core.get_end_cap_style()
        if end_cap_style:
            if not end_cap_style[0].value == 1:
                path_length += self.width / 2
            if not end_cap_style[1].value == 1:
                path_length += self.width / 2
        return round(path_length, 9)

    @classmethod
    def create(
        cls,
        layout,
        layer: Union[str, Layer] = None,
        net: Union[str, "Net"] = None,
        width: float = 100e-6,
        end_cap1: Union[str, GrpcPathEndCapType] = "flat",
        end_cap2: Union[str, GrpcPathEndCapType] = "flat",
        corner_style: Union[str, GrpcPathCornerType] = "sharp",
        points: Union[list, GrpcPolygonData] = None,
    ):
        """
        Create a path in the specified layout, layer, and net with the given parameters.

        Parameters
        ----------
        layout : Layout, optional
            The layout in which the path will be created. If not provided, the active layout of the `pedb` instance
            will be used.
        layer : Union[str, Layer], optional
            The layer in which the path will be created. This parameter is required and must be specified.
        net : Union[str, Net], optional
            The net to which the path will belong. If not provided, the path will not be associated with a net.
        width : float, optional
            The width of the path in meters. The default value is `100e-6`.
        end_cap1 : str, optional
            The style of the first end cap. Options are `"flat"`, `"round"`, `"extended"`, and `"clipped"`.
            The default value is `"flat"`.
        end_cap2 : str, optional
            The style of the second end cap. Options are `"flat"`, `"round"`, `"extended"`, and `"clipped"`.
            The default value is `"flat"`.
        corner_style : str, optional
            The style of the path corners. Options are `"sharp"`, `"round"`, and `"mitter"`.
            The default value is `"sharp"`.
        points : Union[list, GrpcPolygonData], optional
            The points defining the path. This can be a list of points or an instance of `GrpcPolygonData`.
            This parameter is required and must be specified.

        Returns
        -------
        :class:`Path <pyedb.grpc.database.primitive.path.Path>`
            The created path object.

        Raises
        ------
        ValueError
            If the `points` parameter is not provided.

        Notes
        -----
        - If `points` is provided as a list, it will be converted to a `GrpcPolygonData` object.
        - The created path is added to the modeler primitives of the `pedb` instance.

        """
        if layout is None:
            raise Exception("Layout parameter is required to create a path.")
        end_cap_mapping = {
            "flat": GrpcPathEndCapType.FLAT,
            "round": GrpcPathEndCapType.ROUND,
            "extended": GrpcPathEndCapType.EXTENDED,
            "clipped": GrpcPathEndCapType.CLIPPED,
        }
        corner_style_mapping = {
            "round": GrpcPathCornerType.ROUND,
            "mitter": GrpcPathCornerType.MITER,
            "sharp": GrpcPathCornerType.SHARP,
        }
        if isinstance(end_cap1, str):
            end_cap1 = end_cap_mapping[end_cap1.lower()]
        if isinstance(end_cap2, str):
            end_cap2 = end_cap_mapping[end_cap2.lower()]
        if isinstance(corner_style, str):
            corner_style = corner_style_mapping[corner_style.lower()]
        if not points:
            raise ValueError("Points are required to create a path.")
        if isinstance(points, list):
            points = GrpcPolygonData(points=points)
        _path = GrpcPath.create(
            layout=layout.core,
            layer=layer,
            net=net.core,
            width=Value(width),
            end_cap1=end_cap1,
            end_cap2=end_cap2,
            corner_style=corner_style,
            points=points,
        )

        # keeping cache synced
        new_path = cls(layout._pedb, _path)
        layout._pedb.modeler._add_primitive(new_path)
        return new_path

    def delete(self):
        """Delete the path object."""
        # keeping cache synced
        self._pedb.modeler._remove_primitive(self)
        self.core.delete()

    def add_point(self, x, y, incremental=True) -> bool:
        """Add a point at the end of the path.

        Parameters
        ----------
        x: str, int, float
            X coordinate.
        y: str, in, float
            Y coordinate.
        incremental: bool
            Add point incrementally. If True, coordinates of the added point is incremental to the last point.
            The default value is ``True``.

        Returns
        -------
        bool
        """
        if incremental:
            points = self.center_line
            points.append([x, y])
            points = GrpcPolygonData(points=points)
            self.core.center_line = points
            return True
        else:
            Exception("Only incremental point addition is supported currently.")
            return False

    def clone(self):
        """Clone a primitive object with keeping same definition and location.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        mapping = {
            "round": GrpcPathCornerType.ROUND,
            "mitter": GrpcPathCornerType.MITER,
            "sharp": GrpcPathCornerType.SHARP,
        }

        cloned_path = GrpcPath.create(
            layout=self._pedb.active_layout.core,
            layer=self.layer,
            net=self.net.core,
            width=Value(self.width),
            end_cap1=self.core.get_end_cap_style()[0],
            end_cap2=self.core.get_end_cap_style()[1],
            corner_style=mapping[self.corner_style],
            points=GrpcPolygonData(self.center_line),
        )
        if not cloned_path.is_null:
            return Path(self._pedb, cloned_path)

    #

    def create_edge_port(
        self,
        name,
        position="End",
        port_type="Wave",
        reference_layer=None,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """

        Parameters
        ----------
        name : str
            Name of the port.
        position : str, optional
            Position of the port. The default is ``"End"``, in which case the port is created at the end of the trace.
            Options are ``"Start"`` and ``"End"``.
        port_type : str, optional
            Type of the port. The default is ``"Wave"``, in which case a wave port is created. Options are ``"Wave"``
             and ``"Gap"``.
        reference_layer : str, optional
            Name of the references layer. The default is ``None``. Only available for gap port.
        horizontal_extent_factor : int, optional
            Horizontal extent factor of the wave port. The default is ``5``.
        vertical_extent_factor : int, optional
            Vertical extent factor of the wave port. The default is ``3``.
        pec_launch_width : float, str, optional
            Perfect electrical conductor width of the wave port. The default is ``"0.01mm"``.

        Returns
        -------
            :class:`GapPort <pyedb.grpc.database.ports.port.GapPort>`

        Examples
        --------
        >>> edbapp = pyedb.dotnet.Edb("myproject.aedb")
        >>> sig = appedb.modeler.create_trace([[0, 0], ["9mm", 0]], "TOP", "1mm", "SIG", "Flat", "Flat")
        >>> sig.create_edge_port("pcb_port", "end", "Wave", None, 8, 8)

        """
        center_line = self.get_center_line()
        pos = center_line[-1] if position.lower() == "end" else center_line[0]

        # if port_type.lower() == "wave":
        #     return self._pedb.hfss.create_wave_port(
        #         self.id, pos, name, 50, horizontal_extent_factor, vertical_extent_factor, pec_launch_width
        #     )
        # else:
        return self._pedb.hfss.create_edge_port_vertical(
            self.edb_uid,
            pos,
            name,
            50,
            reference_layer,
            hfss_type=port_type,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )

    def create_via_fence(self, distance, gap, padstack_name, net_name="GND"):
        """Create via fences on both sides of the trace.

        Parameters
        ----------
        distance: str, float
            Distance between via fence and trace center line.
        gap: str, float
            Gap between vias.
        padstack_name: str
            Name of the via padstack.
        net_name: str, optional
            Name of the net.

        """

        def getAngle(v1, v2):  # pragma: no cover
            v1_mag = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
            v2_mag = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            dotsum = v1[0] * v2[0] + v1[1] * v2[1]
            if v1[0] * v2[1] - v1[1] * v2[0] > 0:
                scale = 1
            else:
                scale = -1
            dtheta = scale * math.acos(dotsum / (v1_mag * v2_mag))

            return dtheta

        def get_locations(line, gap):  # pragma: no cover
            location = [line[0]]
            residual = 0

            for n in range(len(line) - 1):
                x0, y0 = line[n]
                x1, y1 = line[n + 1]
                length = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
                dx, dy = (x1 - x0) / length, (y1 - y0) / length
                x = x0 - dx * residual
                y = y0 - dy * residual
                length = length + residual
                while length >= gap:
                    x += gap * dx
                    y += gap * dy
                    location.append((x, y))
                    length -= gap

                residual = length
            return location

        def get_parallet_lines(pts, distance):  # pragma: no cover
            leftline = []
            rightline = []

            x0, y0 = pts[0]
            x1, y1 = pts[1]
            vector = (x1 - x0, y1 - y0)
            orientation1 = getAngle((1, 0), vector)

            leftturn = orientation1 + math.pi / 2
            righrturn = orientation1 - math.pi / 2
            leftPt = (x0 + distance * math.cos(leftturn), y0 + distance * math.sin(leftturn))
            leftline.append(leftPt)
            rightPt = (x0 + distance * math.cos(righrturn), y0 + distance * math.sin(righrturn))
            rightline.append(rightPt)

            for n in range(1, len(pts) - 1):
                x0, y0 = pts[n - 1]
                x1, y1 = pts[n]
                x2, y2 = pts[n + 1]

                v1 = (x1 - x0, y1 - y0)
                v2 = (x2 - x1, y2 - y1)
                dtheta = getAngle(v1, v2)
                orientation1 = getAngle((1, 0), v1)

                leftturn = orientation1 + dtheta / 2 + math.pi / 2
                righrturn = orientation1 + dtheta / 2 - math.pi / 2

                distance2 = distance / math.sin((math.pi - dtheta) / 2)
                leftPt = (x1 + distance2 * math.cos(leftturn), y1 + distance2 * math.sin(leftturn))
                leftline.append(leftPt)
                rightPt = (x1 + distance2 * math.cos(righrturn), y1 + distance2 * math.sin(righrturn))
                rightline.append(rightPt)

            x0, y0 = pts[-2]
            x1, y1 = pts[-1]

            vector = (x1 - x0, y1 - y0)
            orientation1 = getAngle((1, 0), vector)
            leftturn = orientation1 + math.pi / 2
            righrturn = orientation1 - math.pi / 2
            leftPt = (x1 + distance * math.cos(leftturn), y1 + distance * math.sin(leftturn))
            leftline.append(leftPt)
            rightPt = (x1 + distance * math.cos(righrturn), y1 + distance * math.sin(righrturn))
            rightline.append(rightPt)
            return leftline, rightline

        distance = Value(distance)
        gap = Value(gap)
        center_line = self.center_line
        leftline, rightline = get_parallet_lines(center_line, distance)
        for x, y in get_locations(rightline, gap) + get_locations(leftline, gap):
            self._pedb.padstacks.place([x, y], padstack_name, net_name=net_name)

    @property
    def center_line(self) -> list[list[float]]:
        """Path center line

        Returns
        -------
        List[float]

        """
        return self.get_center_line()

    def get_center_line(self) -> list[list[float]]:
        """Retrieve center line points list.

        Returns
        -------
        List[List[float, float]].

        """
        return [[Value(pt.x), Value(pt.y)] for pt in self.core.center_line.points]

    @property
    def corner_style(self) -> str:
        """Path's corner style as string.

        Returns
        -------
        str
            Values supported for the setter `"round"`, `"mitter"`, `"sharp"`

        """
        return self.core.corner_style.name.lower()

    @corner_style.setter
    def corner_style(self, corner_type):
        if isinstance(corner_type, str):
            mapping = {
                "round": GrpcPathCornerType.ROUND,
                "mitter": GrpcPathCornerType.MITER,
                "sharp": GrpcPathCornerType.SHARP,
            }
            self.corner_style = mapping[corner_type]

    @property
    def end_cap1(self) -> str:
        """Path's start style as string.

        Returns
        -------
        str
            Values supported for the setter `"flat"`, `"round"`, `"extended"`

        """
        return self.core.get_end_cap_style()[0].name.lower()

    @end_cap1.setter
    def end_cap1(self, end_cap_style):
        if isinstance(end_cap_style, str):
            mapping = {
                "flat": GrpcPathEndCapType.FLAT,
                "round": GrpcPathEndCapType.ROUND,
                "extended": GrpcPathEndCapType.EXTENDED,
            }
            self.core.set_end_cap_style(mapping[end_cap_style], self.core.get_end_cap_style()[1].value)

    @property
    def end_cap2(self) -> str:
        """Path's end style as string.

        Returns
        -------
        str
            Values supported for the setter `"flat"`, `"round"`, `"extended"`

        """
        return self.core.get_end_cap_style()[1].name.lower()

    @end_cap2.setter
    def end_cap2(self, end_cap_style):
        if isinstance(end_cap_style, str):
            mapping = {
                "flat": GrpcPathEndCapType.FLAT,
                "round": GrpcPathEndCapType.ROUND,
                "extended": GrpcPathEndCapType.EXTENDED,
            }
            self.core.set_end_cap_style(self.core.get_end_cap_style()[0].value, mapping[end_cap_style])
