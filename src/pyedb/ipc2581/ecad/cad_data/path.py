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

from pyedb.generic.general_methods import ET
from pyedb.ipc2581.content.entry_line import EntryLine
from pyedb.ipc2581.ecad.cad_data.polygon import PolyStep, PolyType


class Path(object):
    """Class describing an IPC2581 trace."""

    def __init__(self, ipc, pedb):
        self._ipc = ipc
        self._pedb = pedb
        self.location_x = 0.0
        self.location_y = 0.0
        self.poly_steps = []
        self.entry_line = EntryLine()
        self.width_ref_id = ""

    def add_path_step(self, path_step=None):  # pragma no cover
        if not self._pedb.grpc:
            arcs = path_step.primitive_object.GetCenterLine().GetArcData()
            if not arcs:
                return
            self.line_width = self._ipc.from_meter_to_units(path_step.primitive_object.GetWidth(), self._ipc.units)
            self.width_ref_id = "ROUND_{}".format(self.line_width)
            if not self.width_ref_id in self._ipc.content.dict_line.dict_lines:
                entry_line = EntryLine()
                entry_line.line_width = self.line_width
                self._ipc.content.dict_line.dict_lines[self.width_ref_id] = entry_line
            # first point
            arc = arcs[0]
            new_segment_tep = PolyStep()
            new_segment_tep.x = arc.Start.X.ToDouble()
            new_segment_tep.y = arc.Start.Y.ToDouble()
            self.poly_steps.append(new_segment_tep)
            if arc.Height == 0:
                new_segment_tep = PolyStep()
                new_segment_tep.poly_type = PolyType.Segment
                new_segment_tep.x = arc.End.X.ToDouble()
                new_segment_tep.y = arc.End.Y.ToDouble()
                self.poly_steps.append(new_segment_tep)
            else:
                arc_center = arc.GetCenter()
                new_poly_step = PolyStep()
                new_poly_step.poly_type = PolyType.Curve
                new_poly_step.center_X = arc_center.X.ToDouble()
                new_poly_step.center_y = arc_center.Y.ToDouble()
                new_poly_step.x = arc.End.X.ToDouble()
                new_poly_step.y = arc.End.Y.ToDouble()
                new_poly_step.clock_wise = not arc.IsCCW()
                self.poly_steps.append(new_poly_step)
            for arc in list(arcs)[1:]:
                if arc.Height == 0:
                    new_segment_tep = PolyStep()
                    new_segment_tep.poly_type = PolyType.Segment
                    new_segment_tep.x = arc.End.X.ToDouble()
                    new_segment_tep.y = arc.End.Y.ToDouble()
                    self.poly_steps.append(new_segment_tep)
                else:
                    arc_center = arc.GetCenter()
                    new_poly_step = PolyStep()
                    new_poly_step.poly_type = PolyType.Curve
                    new_poly_step.center_X = arc_center.X.ToDouble()
                    new_poly_step.center_y = arc_center.Y.ToDouble()
                    new_poly_step.x = arc.End.X.ToDouble()
                    new_poly_step.y = arc.End.Y.ToDouble()
                    new_poly_step.clock_wise = not arc.IsCCW()
                    self.poly_steps.append(new_poly_step)
        else:
            arcs = path_step.cast().center_line.arc_data
            if not arcs:
                return
            self.line_width = self._ipc.from_meter_to_units(path_step.cast().width.value, self._ipc.units)
            self.width_ref_id = "ROUND_{}".format(self.line_width)
            if not self.width_ref_id in self._ipc.content.dict_line.dict_lines:
                entry_line = EntryLine()
                entry_line.line_width = self.line_width
                self._ipc.content.dict_line.dict_lines[self.width_ref_id] = entry_line
            # first point
            arc = arcs[0]
            new_segment_tep = PolyStep()
            new_segment_tep.x = arc.start.x.value
            new_segment_tep.y = arc.start.y.value
            self.poly_steps.append(new_segment_tep)
            if arc.height == 0:
                new_segment_tep = PolyStep()
                new_segment_tep.poly_type = PolyType.Segment
                new_segment_tep.x = arc.end.x.value
                new_segment_tep.y = arc.end.y.value
                self.poly_steps.append(new_segment_tep)
            else:
                arc_center = arc.center
                new_poly_step = PolyStep()
                new_poly_step.poly_type = PolyType.Curve
                new_poly_step.center_X = arc_center.x.value
                new_poly_step.center_y = arc_center.y.value
                new_poly_step.x = arc.end.x.value
                new_poly_step.y = arc.end.y.value
                new_poly_step.clock_wise = not arc.is_ccw
                self.poly_steps.append(new_poly_step)
            for arc in list(arcs)[1:]:
                if arc.height == 0:
                    new_segment_tep = PolyStep()
                    new_segment_tep.poly_type = PolyType.Segment
                    new_segment_tep.x = arc.end.x.value
                    new_segment_tep.y = arc.end.y.value
                    self.poly_steps.append(new_segment_tep)
                else:
                    arc_center = arc.center
                    new_poly_step = PolyStep()
                    new_poly_step.poly_type = PolyType.Curve
                    new_poly_step.center_X = arc_center.x.value
                    new_poly_step.center_y = arc_center.y.value
                    new_poly_step.x = arc.end.x.value
                    new_poly_step.y = arc.end.y.value
                    new_poly_step.clock_wise = not arc.is_ccw
                    self.poly_steps.append(new_poly_step)

    def write_xml(self, net_root):  # pragma no cover
        if not self.poly_steps:
            return
        feature = ET.SubElement(net_root, "Features")
        location = ET.SubElement(feature, "Location")
        location.set("x", "0")
        location.set("y", "0")
        polyline = ET.SubElement(feature, "Polyline")
        polyline_begin = ET.SubElement(polyline, "PolyBegin")
        polyline_begin.set("x", str(self._ipc.from_meter_to_units(self.poly_steps[0].x, self._ipc.units)))
        polyline_begin.set("y", str(self._ipc.from_meter_to_units(self.poly_steps[0].y, self._ipc.units)))
        for poly_step in self.poly_steps[1:]:
            poly_step.write_xml(polyline, self._ipc)
        line_disc_ref = ET.SubElement(polyline, "LineDescRef")
        line_disc_ref.set("id", self.width_ref_id)


class PathStep(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
