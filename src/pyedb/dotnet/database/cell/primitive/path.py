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

from pyedb.dotnet.database.cell.primitive.primitive import Primitive
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.point_data import PointData


class Path(Primitive):
    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)

    @property
    def width(self):
        """Path width.

        Returns
        -------
        float
            Path width or None.
        """
        return self._edb_object.GetWidth()

    @width.setter
    def width(self, value):
        self.primitive_object.SetWidth(self._pedb.edb_value(value))

    def get_end_cap_style(self):
        """Get path end cap styles.

        Returns
        -------
        tuple[
            :class:`PathEndCapType`,
            :class:`PathEndCapType`
        ]

            Returns a tuple of the following format:

            **(end_cap1, end_cap2)**

            **end_cap1** : End cap style of path start end cap.

            **end_cap2** : End cap style of path end  cap.
        """
        return self._edb_object.GetEndCapStyle()

    def set_end_cap_style(self, end_cap1, end_cap2):
        """Set path end cap styles.

        Parameters
        ----------
        end_cap1: :class:`PathEndCapType`
            End cap style of path start end cap.
        end_cap2: :class:`PathEndCapType`
            End cap style of path end cap.
        """
        self._edb_object.SetEndCapStyle(end_cap1, end_cap2)

    @property
    def length(self):
        """Path length in meters.

        Returns
        -------
        float
            Path length in meters.
        """
        center_line_arcs = list(self._edb_object.GetCenterLine().GetArcData())
        path_length = 0.0
        for arc in center_line_arcs:
            path_length += arc.GetLength()
        if self.get_end_cap_style()[0]:
            if not self.get_end_cap_style()[1].value__ == 1:
                path_length += self.width / 2
            if not self.get_end_cap_style()[2].value__ == 1:
                path_length += self.width / 2
        return path_length

    def add_point(self, x, y, incremental=False):
        """Add a point at the end of the path.

        Parameters
        ----------
        x: str, int, float
            X coordinate.
        y: str, in, float
            Y coordinate.
        incremental: bool
            Add point incrementally. If True, coordinates of the added point is incremental to the last point.
            The default value is ``False``.

        Returns
        -------
        bool
        """
        center_line = self._edb_object.GetCenterLine()

        if incremental:
            x = self._pedb.edb_value(x)
            y = self._pedb.edb_value(y)
            last_point = list(center_line.Points)[-1]
            x = "({})+({})".format(x, last_point.X.ToString())
            y = "({})+({})".format(y, last_point.Y.ToString())
        center_line.AddPoint(PointData.create_from_xy(self._pedb, x=x, y=y)._edb_object)
        return self._edb_object.SetCenterLine(center_line)

    def get_center_line(self, to_string=False):
        """Get the center line of the trace.

        Parameters
        ----------
        to_string : bool, optional
            Type of return. The default is ``"False"``.

        Returns
        -------
        list

        """
        if to_string:
            return [[p.X.ToString(), p.Y.ToString()] for p in list(self._edb_object.GetCenterLine().Points)]
        else:
            return [[p.X.ToDouble(), p.Y.ToDouble()] for p in list(self._edb_object.GetCenterLine().Points)]

    def clone(self):
        """Clone a primitive object with keeping same definition and location.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        corner_style = self.corner_style
        end_cap_style = self.get_end_cap_style()
        cloned_path = self._app.core.Cell.Primitive.Path.Create(
            self._app.active_layout,
            self.layer_name,
            self.net._edb_object,
            self._edb_object.GetWidthValue(),
            end_cap_style[1],
            end_cap_style[2],
            corner_style,
            self._edb_object.GetCenterLine(),
        )
        if cloned_path:
            return cloned_path

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
            :class:`dotnet.database.edb_data.sources.ExcitationPorts`

        Examples
        --------
        >>> edbapp = pyedb.dotnet.Edb("myproject.aedb")
        >>> sig = appedb.modeler.create_trace([[0, 0], ["9mm", 0]], "TOP", "1mm", "SIG", "Flat", "Flat")
        >>> sig.create_edge_port("pcb_port", "end", "Wave", None, 8, 8)

        """
        center_line = self.get_center_line()
        pos = center_line[-1] if position.lower() == "end" else center_line[0]

        if port_type.lower() == "wave":
            return self._app.hfss.create_wave_port(
                self.id, pos, name, 50, horizontal_extent_factor, vertical_extent_factor, pec_launch_width
            )
        else:
            return self._app.hfss.create_edge_port_vertical(self.id, pos, name, 50, reference_layer)

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

        Returns
        -------
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

        def getLocations(line, gap):  # pragma: no cover
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

        def getParalletLines(pts, distance):  # pragma: no cover
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

        distance = self._pedb.edb_value(distance).ToDouble()
        gap = self._pedb.edb_value(gap).ToDouble()
        center_line = self.get_center_line()
        leftline, rightline = getParalletLines(center_line, distance)
        for x, y in getLocations(rightline, gap) + getLocations(leftline, gap):
            self._pedb.padstacks.place([x, y], padstack_name, net_name=net_name)

    @property
    def center_line(self):
        """:class:`PolygonData <ansys.edb.geometry.PolygonData>`: Center line for this Path."""
        edb_center_line = self._edb_object.GetCenterLine()
        return [[pt.X.ToDouble(), pt.Y.ToDouble()] for pt in list(edb_center_line.Points)]

    @center_line.setter
    def center_line(self, value):
        if isinstance(value, list):
            points = [self._pedb.point_data(i[0], i[1]) for i in value]
            polygon_data = self._edb.Geometry.PolygonData(convert_py_list_to_net_list(points), False)
            self._edb_object.SetCenterLine(polygon_data)

    def get_center_line_polygon_data(self):
        """Gets center lines of the path as a PolygonData object."""
        edb_object = self._edb_object.GetCenterLine()
        return self._pedb.pedb_class.database.geometry.polygon_data.PolygonData(self._pedb, edb_object=edb_object)

    def set_center_line_polygon_data(self, polygon_data):
        """Sets center lines of the path from a PolygonData object."""
        if not self._edb_object.SetCenterLine(polygon_data._edb_object):
            raise ValueError
        else:
            return True

    @property
    def corner_style(self):
        """:class:`PathCornerType`: Path's corner style."""
        return self._edb_object.GetCornerStyle()

    @corner_style.setter
    def corner_style(self, corner_type):
        self._edb_object.SetCornerStyle(corner_type)
