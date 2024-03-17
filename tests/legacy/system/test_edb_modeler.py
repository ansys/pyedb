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

"""Tests related to Edb modeler
"""

import os
import pytest

from pyedb.dotnet.edb import Edb
from pyedb.generic.settings import settings
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_modeler_polygons(self):
        """Evaluate modeler polygons"""
        assert len(self.edbapp.modeler.polygons) > 0
        assert self.edbapp.modeler.polygons[0].is_void == self.edbapp.modeler.polygons[0].IsVoid()

        poly0 = self.edbapp.modeler.polygons[0]
        assert self.edbapp.modeler.polygons[0].clone()
        assert isinstance(poly0.voids, list)
        assert isinstance(poly0.points_raw(), list)
        assert isinstance(poly0.points(), tuple)
        assert isinstance(poly0.points()[0], list)
        assert poly0.points()[0][0] >= 0.0
        assert poly0.points_raw()[0].X.ToDouble() >= 0.0
        assert poly0.type == "Polygon"
        assert not poly0.is_arc(poly0.points_raw()[0])
        assert isinstance(poly0.voids, list)
        assert isinstance(poly0.get_closest_point([0, 0]), list)
        assert isinstance(poly0.get_closest_arc_midpoint([0, 0]), list)
        assert isinstance(poly0.arcs, list)
        assert isinstance(poly0.longest_arc.length, float)
        assert isinstance(poly0.shortest_arc.length, float)
        assert not poly0.in_polygon([0, 0])
        assert isinstance(poly0.arcs[0].center, list)
        assert isinstance(poly0.arcs[0].radius, float)
        assert poly0.arcs[0].is_segment
        assert not poly0.arcs[0].is_point
        assert not poly0.arcs[0].is_ccw
        assert isinstance(poly0.arcs[0].points_raw, list)
        assert isinstance(poly0.arcs[0].points, tuple)
        assert isinstance(poly0.intersection_type(poly0), int)
        assert poly0.is_intersecting(poly0)

    def test_modeler_paths(self):
        """Evaluate modeler paths"""
        assert len(self.edbapp.modeler.paths) > 0
        assert self.edbapp.modeler.paths[0].type == "Path"
        assert self.edbapp.modeler.paths[0].clone()
        assert isinstance(self.edbapp.modeler.paths[0].width, float)
        self.edbapp.modeler.paths[0].width = "1mm"
        assert self.edbapp.modeler.paths[0].width == 0.001

    def test_modeler_primitives_by_layer(self):
        """Evaluate modeler primitives by layer"""
        assert self.edbapp.modeler.primitives_by_layer["1_Top"][0].layer_name == "1_Top"
        assert self.edbapp.modeler.primitives_by_layer["1_Top"][0].layer.GetName() == "1_Top"
        assert not self.edbapp.modeler.primitives_by_layer["1_Top"][0].is_negative
        assert not self.edbapp.modeler.primitives_by_layer["1_Top"][0].is_void
        self.edbapp.modeler.primitives_by_layer["1_Top"][0].is_negative = True
        assert self.edbapp.modeler.primitives_by_layer["1_Top"][0].is_negative
        self.edbapp.modeler.primitives_by_layer["1_Top"][0].is_negative = False
        assert not self.edbapp.modeler.primitives_by_layer["1_Top"][0].has_voids
        assert not self.edbapp.modeler.primitives_by_layer["1_Top"][0].is_parameterized
        assert isinstance(self.edbapp.modeler.primitives_by_layer["1_Top"][0].get_hfss_prop(), tuple)
        assert not self.edbapp.modeler.primitives_by_layer["1_Top"][0].is_zone_primitive
        assert self.edbapp.modeler.primitives_by_layer["1_Top"][0].can_be_zone_primitive

    def test_modeler_primitives(self):
        """Evaluate modeler primitives"""
        assert len(self.edbapp.modeler.rectangles) > 0
        assert len(self.edbapp.modeler.circles) > 0
        assert len(self.edbapp.modeler.bondwires) == 0
        assert "1_Top" in self.edbapp.modeler.polygons_by_layer.keys()
        assert len(self.edbapp.modeler.polygons_by_layer["1_Top"]) > 0
        assert len(self.edbapp.modeler.polygons_by_layer["DE1"]) == 0
        assert self.edbapp.modeler.rectangles[0].type == "Rectangle"
        assert self.edbapp.modeler.circles[0].type == "Circle"

    def test_modeler_get_polygons_bounding(self):
        """Retrieve polygons bounding box."""
        polys = self.edbapp.modeler.get_polygons_by_layer("GND")
        for poly in polys:
            bounding = self.edbapp.modeler.get_polygon_bounding_box(poly)
            assert len(bounding) == 4

    def test_modeler_get_polygons_by_layer_and_nets(self):
        """Retrieve polygons by layer and nets."""
        nets = ["GND", "1V0"]
        polys = self.edbapp.modeler.get_polygons_by_layer("16_Bottom", nets)
        assert polys

    def test_modeler_get_polygons_points(self):
        """Retrieve polygons points."""
        polys = self.edbapp.modeler.get_polygons_by_layer("GND")
        for poly in polys:
            points = self.edbapp.modeler.get_polygon_points(poly)
            assert points

    def test_modeler_create_polygon(self):
        """Create a polygon based on a shape or points."""
        settings.enable_error_handler = True
        points = [
            [-0.025, -0.02],
            [0.025, -0.02],
            [0.025, 0.02],
            [-0.025, 0.02],
            [-0.025, -0.02],
        ]
        plane = self.edbapp.modeler.Shape("polygon", points=points)
        points = [
            [-0.001, -0.001],
            [0.001, -0.001, "ccw", 0.0, -0.0012],
            [0.001, 0.001],
            [0.0015, 0.0015, 0.0001],
            [-0.001, 0.0015],
            [-0.001, -0.001],
        ]
        void1 = self.edbapp.modeler.Shape("polygon", points=points)
        void2 = self.edbapp.modeler.Shape("rectangle", [-0.002, 0.0], [-0.015, 0.0005])
        assert self.edbapp.modeler.create_polygon(plane, "1_Top", [void1, void2])
        self.edbapp["polygon_pts_x"] = -1.025
        self.edbapp["polygon_pts_y"] = -1.02
        points = [
            ["polygon_pts_x", "polygon_pts_y"],
            [1.025, -1.02],
            [1.025, 1.02],
            [-1.025, 1.02],
            [-1.025, -1.02],
        ]
        assert self.edbapp.modeler.create_polygon(points, "1_Top")
        settings.enable_error_handler = False

    def test_modeler_create_polygon_from_shape(self):
        """Create polygon from shape."""
        example_folder = os.path.join(local_path, "example_models", test_subfolder)
        source_path_edb = os.path.join(example_folder, "ANSYS-HSD_V1.aedb")
        target_path_edb = os.path.join(self.local_scratch.path, "test_create_polygon", "test.aedb")
        self.local_scratch.copyfolder(source_path_edb, target_path_edb)
        edbapp = Edb(target_path_edb, desktop_version)
        edbapp.modeler.create_polygon(
            main_shape=[[0.0, 0.0], [0.0, 10e-3], [10e-3, 10e-3], [10e-3, 0]], layer_name="1_Top", net_name="test"
        )
        poly_test = [poly for poly in edbapp.modeler.polygons if poly.net_name == "test"]
        assert len(poly_test) == 1
        assert poly_test[0].center == [0.005, 0.005]
        assert poly_test[0].bbox == [0.0, 0.0, 0.01, 0.01]
        assert poly_test[0].move_layer("16_Bottom")
        poly_test = [poly for poly in edbapp.modeler.polygons if poly.net_name == "test"]
        assert len(poly_test) == 1
        assert poly_test[0].layer_name == "16_Bottom"
        edbapp.close_edb()

    def test_modeler_create_trace(self):
        """Create a trace based on a list of points."""
        points = [
            [-0.025, -0.02],
            [0.025, -0.02],
            [0.025, 0.02],
        ]
        trace = self.edbapp.modeler.create_trace(points, "1_Top")
        assert trace
        assert isinstance(trace.get_center_line(), list)
        assert isinstance(trace.get_center_line(True), list)
        self.edbapp["delta_x"] = "1mm"
        assert trace.add_point("delta_x", "1mm", True)
        assert trace.get_center_line(True)[-1][0] == "(delta_x)+(0.025)"
        assert trace.add_point(0.001, 0.002)
        assert trace.get_center_line()[-1] == [0.001, 0.002]

    def test_modeler_add_void(self):
        """Add a void into a shape."""
        plane_shape = self.edbapp.modeler.Shape("rectangle", pointA=["-5mm", "-5mm"], pointB=["5mm", "5mm"])
        plane = self.edbapp.modeler.create_polygon(plane_shape, "1_Top", net_name="GND")
        void = self.edbapp.modeler.create_trace([["0", "0"], ["0", "1mm"]], layer_name="1_Top", width="0.1mm")
        assert self.edbapp.modeler.add_void(plane, void)
        assert plane.add_void(void)

    def test_modeler_fix_circle_void(self):
        """Fix issues when circle void are clipped due to a bug in EDB."""
        assert self.edbapp.modeler.fix_circle_void_for_clipping()

    def test_modeler_primitives_area(self):
        """Access primitives total area."""
        i = 0
        while i < 10:
            assert self.edbapp.modeler.primitives[i].area(False) > 0
            assert self.edbapp.modeler.primitives[i].area(True) > 0
            i += 1
        assert self.edbapp.modeler.primitives[i].bbox
        assert self.edbapp.modeler.primitives[i].center
        assert self.edbapp.modeler.primitives[i].get_closest_point((0, 0))
        assert self.edbapp.modeler.primitives[i].polygon_data
        assert self.edbapp.modeler.paths[0].length

    def test_modeler_create_rectangle(self):
        """Create rectangle."""
        rect = self.edbapp.modeler.create_rectangle("1_Top", "SIG1", ["0", "0"], ["2mm", "3mm"])
        assert rect
        rect.is_negative = True
        assert rect.is_negative
        rect.is_negative = False
        assert not rect.is_negative
        assert self.edbapp.modeler.create_rectangle(
            "1_Top",
            "SIG2",
            center_point=["0", "0"],
            width="4mm",
            height="5mm",
            representation_type="CenterWidthHeight",
        )

    def test_modeler_create_circle(self):
        """Create circle."""
        poly = self.edbapp.modeler.create_polygon_from_points([[0, 0], [100, 0], [100, 100], [0, 100]], "1_Top")
        assert poly
        poly.add_void([[20, 20], [20, 30], [100, 30], [100, 20]])
        poly2 = self.edbapp.modeler.create_polygon_from_points([[60, 60], [60, 150], [150, 150], [150, 60]], "1_Top")
        new_polys = poly.subtract(poly2)
        assert len(new_polys) == 1
        circle = self.edbapp.modeler.create_circle("1_Top", 40, 40, 15)
        assert circle
        intersection = new_polys[0].intersect(circle)
        assert len(intersection) == 1
        circle2 = self.edbapp.modeler.create_circle("1_Top", 20, 20, 15)
        assert circle2.unite(intersection)

    def test_modeler_defeature(self):
        """Defeature the polygon."""
        assert self.edbapp.modeler.defeature_polygon(self.edbapp.modeler.primitives_by_net["GND"][-1], 0.01)

    def test_modeler_primitives_boolean_operation(self):
        """Evaluate modeler primitives boolean operations."""
        from pyedb.dotnet.edb import Edb

        edb = Edb()
        edb.stackup.add_layer(layer_name="test")
        x = edb.modeler.create_polygon(
            layer_name="test", main_shape=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
        )
        assert x
        x_hole1 = edb.modeler.create_polygon(
            layer_name="test", main_shape=[[1.0, 1.0], [4.5, 1.0], [4.5, 9.0], [1.0, 9.0]]
        )
        x_hole2 = edb.modeler.create_polygon(
            layer_name="test", main_shape=[[4.5, 1.0], [9.0, 1.0], [9.0, 9.0], [4.5, 9.0]]
        )
        x = x.subtract([x_hole1, x_hole2])[0]
        assert x
        y = edb.modeler.create_polygon(layer_name="foo", main_shape=[[4.0, 3.0], [6.0, 3.0], [6.0, 6.0], [4.0, 6.0]])
        z = x.subtract(y)
        assert z
        edb.stackup.add_layer(layer_name="foo")
        x = edb.modeler.create_polygon(
            layer_name="foo", main_shape=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
        )
        x_hole = edb.modeler.create_polygon(
            layer_name="foo", main_shape=[[1.0, 1.0], [9.0, 1.0], [9.0, 9.0], [1.0, 9.0]]
        )
        y = x.subtract(x_hole)[0]
        z = edb.modeler.create_polygon(
            layer_name="foo", main_shape=[[-15.0, 5.0], [15.0, 5.0], [15.0, 6.0], [-15.0, 6.0]]
        )
        assert y.intersect(z)

        edb.stackup.add_layer(layer_name="test2")
        x = edb.modeler.create_polygon(
            layer_name="test2", main_shape=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
        )
        x_hole = edb.modeler.create_polygon(
            layer_name="test2", main_shape=[[1.0, 1.0], [9.0, 1.0], [9.0, 9.0], [1.0, 9.0]]
        )
        y = x.subtract(x_hole)[0]
        assert y.voids
        y_clone = y.clone()
        assert y_clone.voids
        edb.close()

    def test_modeler_path_convert_to_polygon(self):
        target_path = os.path.join(local_path, "example_models", "convert_and_merge_path.aedb")
        edbapp = Edb(target_path, edbversion=desktop_version)
        for path in edbapp.modeler.paths:
            assert path.convert_to_polygon()
        assert edbapp.nets.merge_nets_polygons("test")
        edbapp.close()

    def test_156_check_path_length(self):
        """"""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_path_length.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_path_length", "test.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, desktop_version)
        net1 = [path for path in edbapp.modeler.paths if path.net_name == "loop1"]
        net1_length = 0
        for path in net1:
            net1_length += path.length
        assert net1_length == 0.01814480090225562
        net2 = [path for path in edbapp.modeler.paths if path.net_name == "line1"]
        net2_length = 0
        for path in net2:
            net2_length += path.length
        assert net2_length == 0.007
        net3 = [path for path in edbapp.modeler.paths if path.net_name == "lin2"]
        net3_length = 0
        for path in net3:
            net3_length += path.length
        assert net3_length == 0.04860555127546401
        net4 = [path for path in edbapp.modeler.paths if path.net_name == "lin3"]
        net4_length = 0
        for path in net4:
            net4_length += path.length
        assert net4_length == 7.6e-3
        net5 = [path for path in edbapp.modeler.paths if path.net_name == "lin4"]
        net5_length = 0
        for path in net5:
            net5_length += path.length
        assert net5_length == 0.026285623899038543
        edbapp.close_edb()

    def test_convert_to_polugon_error(self):
        edbapp = Edb()
        edbapp["$H"] = "0.65mil"
        assert edbapp["$H"].value_string == "0.65mil"
        edbapp["Via_S"] = "40mil"
        edbapp["MS_W"] = "4.75mil"
        edbapp.stackup.add_layer("trace1", thickness="$H")
        edbapp.modeler.create_trace(width="MS_W", layer_name="trace1",path_list=[("-Via_S/2", "0"), ("-MS_S/2-MS_W/2", "-16 mil"),("-MS_S/2-MS_W/2", "-100 mil")], start_cap_style="FLat",end_cap_style="FLat", net_name="t1_1")
        assert edbapp.modeler.primitives[0].convert_to_polygon()
        assert not edbapp.modeler.primitives[0].convert_to_polygon()
        edbapp.close()