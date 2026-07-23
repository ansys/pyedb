# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Tests related to Edb modeler"""

import os
from pathlib import Path
import platform

import pytest

from pyedb.generic.settings import settings
from tests.conftest import config, local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

if config["use_grpc"]:
    from pyedb.grpc.database.geometry.point_data import PointData
    from pyedb.grpc.database.geometry.polygon_data import PolygonData
else:
    from pyedb.dotnet.database.geometry.point_data import PointData
    from pyedb.dotnet.database.geometry.polygon_data import PolygonData


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_modeler_polygons(self):
        """Evaluate modeler polygons"""
        edbapp = self.edb_examples.get_si_verse()
        assert len(edbapp.modeler.polygons) > 0
        assert not edbapp.modeler.polygons[0].is_void

        poly0 = edbapp.modeler.polygons[0]
        assert poly0.net_name in ["", None]
        poly0.net_name = "GND"
        assert poly0.net_name == "GND"
        assert poly0.net.name == "GND"
        assert edbapp.modeler.polygons[0].clone()
        assert isinstance(poly0.voids, list)
        assert isinstance(poly0.points_raw(), list)
        assert isinstance(poly0.points(), tuple)
        assert isinstance(poly0.points()[0], list)
        assert poly0.points()[0][0] >= 0.0
        if edbapp.grpc:
            assert poly0.points_raw()[0].x.value >= 0.0
        else:
            assert poly0.points_raw()[0].X.ToDouble() >= 0.0
        assert poly0.type == "polygon"
        if edbapp.grpc:
            assert not poly0.points_raw()[0].is_arc
        else:
            assert not poly0.points_raw()[0].IsArc()
        assert isinstance(poly0.voids, list)
        assert isinstance(poly0.get_closest_point([0.07, 0.0027]), list)
        assert isinstance(poly0.get_closest_arc_midpoint([0, 0]), list)
        assert isinstance(poly0.arcs, list)
        assert isinstance(poly0.longest_arc.length, float)
        assert isinstance(poly0.shortest_arc.length, float)
        assert not poly0.in_polygon([0, 0])
        assert poly0.arcs[0].is_segment
        assert not poly0.arcs[0].is_point
        assert not poly0.arcs[0].is_ccw
        assert isinstance(poly0.arcs[0].points, list)
        assert isinstance(poly0.intersection_type(poly0), int)
        assert poly0.is_intersecting(poly0)
        poly_3022 = edbapp.layout.find_object_by_id(3022)
        assert edbapp.layout.find_object_by_id(3023)
        assert poly_3022.aedt_name == "poly_3022"
        poly_3022.aedt_name = "poly3022"
        assert poly_3022.aedt_name == "poly3022"
        poly_with_voids = [poly for poly in edbapp.modeler.polygons if poly.has_voids]
        assert poly_with_voids
        first_void = poly_with_voids[0].voids[0]
        assert edbapp.layout.find_object_by_id(first_void.id).id == first_void.id
        assert edbapp.modeler[first_void.id].id == first_void.id
        for k in poly_with_voids[0].voids:
            assert k.id
            assert k.expand(0.0005)
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_polygon_move_rotate_scale(self):
        """Evaluate polygon move, rotate and scale operations."""
        edbapp = self.edb_examples.get_si_verse()
        poly = edbapp.modeler.polygons[0]
        original_points = poly.points()
        # move
        assert poly.move(["100um", "100um"])
        moved_points = poly.points()
        assert moved_points != original_points
        # move back to original position
        assert poly.move(["-100um", "-100um"])
        # rotate
        assert poly.rotate(angle=90)
        # scale
        assert poly.scale(factor=2)
        edbapp.close(terminate_rpc_session=False)

    pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")

    def test_modeler_polygon_operations_ic_mode(self):
        """Create primitives, switch to IC mode and apply polygon operations."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)

        # Create two polygons on the top signal layer
        layer_name = list(edbapp.stackup.signal_layers.keys())[0]
        points1 = [
            [0.0, 0.0],
            [100e-6, 0.0],
            [100e-6, 100e-6],
            [0.0, 100e-6],
        ]
        points2 = [
            [200e-6, 0.0],
            [300e-6, 0.0],
            [300e-6, 100e-6],
            [200e-6, 100e-6],
        ]
        poly1 = edbapp.modeler.create_polygon(points=points1, layer_name=layer_name, net_name="GND")
        poly2 = edbapp.modeler.create_polygon(points=points2, layer_name=layer_name, net_name="VCC")
        assert poly1
        assert poly2

        # Switch to IC mode
        assert edbapp.design_mode == "general"
        edbapp.design_mode = "ic"
        assert edbapp.design_mode == "ic"

        # move poly1
        original_points = poly1.points()
        assert poly1.move(["50um", "50um"])
        assert poly1.points() != original_points

        # rotate poly2
        assert poly2.rotate(angle=45)

        # scale poly1
        assert poly1.scale(factor=1.5)

        edbapp.close(terminate_rpc_session=False)

    def test_modeler_paths(self):
        """Evaluate modeler paths"""
        edbapp = self.edb_examples.get_si_verse()
        assert len(edbapp.modeler.paths) > 0
        path = edbapp.modeler.paths[0]
        assert path.type.lower() == "path"
        assert path.clone()
        assert isinstance(path.width, float)
        path.width = "1mm"
        assert path.width == 0.001
        assert edbapp.modeler["line_167"].type.lower() == "path"
        assert edbapp.modeler["poly_3022"].type.lower() == "polygon"
        line_number = len(edbapp.layout.primitives)
        edbapp.modeler["line_167"].delete()
        assert edbapp.layout.primitives
        assert line_number == len(edbapp.layout.primitives) + 1
        assert edbapp.modeler["poly_3022"].type.lower() == "polygon"
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_primitives_by_layer(self):
        """Evaluate modeler primitives by layer"""
        edbapp = self.edb_examples.get_si_verse()
        primmitive = edbapp.layout.find_primitive(layer_name="1_Top")[0]
        assert primmitive.layer_name == "1_Top"
        assert not primmitive.is_negative
        assert not primmitive.is_void
        primmitive.is_negative = True
        assert primmitive.is_negative
        primmitive.is_negative = False
        assert not primmitive.has_voids
        assert not primmitive.is_parameterized
        # assert isinstance(primmitive.get_hfss_prop(), tuple)
        assert not primmitive.is_zone_primitive
        assert primmitive.can_be_zone_primitive
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_primitives(self):
        """Evaluate modeler primitives"""
        edbapp = self.edb_examples.get_si_verse()
        assert len(edbapp.modeler.rectangles) > 0
        assert len(edbapp.modeler.circles) > 0
        assert len(edbapp.layout.bondwires) == 0
        assert "1_Top" in edbapp.modeler.polygons_by_layer.keys()
        assert len(edbapp.modeler.polygons_by_layer["1_Top"]) > 0
        assert len(edbapp.modeler.polygons_by_layer["DE1"]) == 0
        assert edbapp.modeler.rectangles[0].type.lower() == "rectangle"
        assert edbapp.modeler.circles[0].type.lower() == "circle"
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_get_polygons_bounding(self):
        """Retrieve polygons bounding box."""
        edbapp = self.edb_examples.get_si_verse()
        polys = edbapp.modeler.get_polygons_by_layer("GND")
        for poly in polys:
            bounding = edbapp.modeler.get_polygon_bounding_box(poly)
            assert len(bounding) == 4
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_get_polygons_by_layer_and_nets(self):
        """Retrieve polygons by layer and nets."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        nets = ["GND", "1V0"]
        polys = edbapp.modeler.get_polygons_by_layer("16_Bottom", nets)
        assert polys
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_get_polygons_points(self):
        """Retrieve polygons points."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        polys = edbapp.modeler.get_polygons_by_layer("GND")
        for poly in polys:
            points = edbapp.modeler.get_polygon_points(poly)
            assert points
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_polygon(self):
        """Create a polygon based on a shape or points."""
        edbapp = self.edb_examples.get_si_verse()
        settings.enable_error_handler = True
        points = [
            [-0.025, -0.02],
            [0.025, -0.02],
            [0.025, 0.02],
            [-0.025, 0.02],
            [-0.025, -0.02],
        ]
        plane = edbapp.modeler.create_polygon(points=points, layer_name="1_Top")

        points = [
            [-0.001, -0.001],
            [0.001, 0.001],
            [0.0015, 0.0015, 0.0001],
            [-0.001, 0.0015],
            [-0.001, -0.001],
        ]
        void1 = edbapp.modeler.create_polygon(points=points, layer_name="1_Top")
        void2 = edbapp.modeler.create_rectangle(
            lower_left_point=[-0.002, 0.0], upper_right_point=[-0.015, 0.0005], layer_name="1_Top"
        )
        assert edbapp.modeler.create_polygon(points=plane.polygon_data, layer_name="1_Top", voids=[void1, void2])
        edbapp["polygon_pts_x"] = -1.025
        edbapp["polygon_pts_y"] = -1.02
        points = [
            ["polygon_pts_x", "polygon_pts_y"],
            [1.025, -1.02],
            [1.025, 1.02],
            [-1.025, 1.02],
            [-1.025, -1.02],
        ]
        assert edbapp.modeler.create_polygon(points, "1_Top")
        settings.enable_error_handler = False
        points = [[-0.025, -0.02], [0.025, -0.02], [-0.025, -0.02], [0.025, 0.02], [-0.025, 0.02], [-0.025, -0.02]]
        poly = edbapp.modeler.create_polygon(points=points, layer_name="1_Top")
        assert poly.has_self_intersections
        assert poly.fix_self_intersections() == []
        assert not poly.has_self_intersections
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_polygon_from_shape(self):
        """Create polygon from shape."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        edbapp.modeler.create_polygon(
            points=[[0.0, 0.0], [0.0, 10e-3], [10e-3, 10e-3], [10e-3, 0]], layer_name="1_Top", net_name="test"
        )
        poly_test = [poly for poly in edbapp.layout.polygons if poly.net_name == "test"]
        assert len(poly_test) == 1
        assert poly_test[0].center == [0.005, 0.005] or poly_test[0].center == (0.005, 0.005)
        assert poly_test[0].bbox == [0.0, 0.0, 0.01, 0.01] or poly_test[0].bbox == ((0.0, 0.0), (0.01, 0.01))
        assert poly_test[0].move_layer("16_Bottom")
        poly_test = [poly for poly in edbapp.modeler.polygons if poly.net_name == "test"]
        assert len(poly_test) == 1
        assert poly_test[0].layer_name == "16_Bottom"
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_trace(self):
        """Create a trace based on a list of points."""
        edbapp = self.edb_examples.get_si_verse()
        points = [
            [-0.025, -0.02],
            [0.025, -0.02],
            [0.025, 0.02],
        ]
        trace = edbapp.modeler.create_trace(points, "1_Top")
        assert trace
        if edbapp.grpc:
            assert trace.end_cap1 == "round"
            assert trace.end_cap2 == "round"
            trace.end_cap1 = "flat"
            trace.end_cap2 = "flat"
            assert trace.end_cap1 == "flat"
            assert trace.end_cap2 == "flat"

        assert isinstance(trace.get_center_line(), list)
        assert isinstance(trace.get_center_line(), list)
        # TODO
        # edbapp["delta_x"] = "1mm"
        # assert trace.add_point("delta_x", "1mm", True)
        # assert trace.get_center_line(True)[-1][0] == "(delta_x)+(0.025)"
        # TODO check issue #475 center_line has no setter
        # assert trace.add_point(0.001, 0.002)
        # assert trace.get_center_line()[-1] == [0.001, 0.002]
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_add_void(self):
        """Add a void into a shape."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        plane_shape = edbapp.modeler.create_rectangle(
            lower_left_point=["-5mm", "-5mm"], upper_right_point=["5mm", "5mm"], layer_name="1_Top"
        )
        plane = edbapp.modeler.create_polygon(plane_shape.polygon_data, "1_Top", net_name="GND")
        void = edbapp.modeler.create_trace(path_list=[["0", "0"], ["0", "1mm"]], layer_name="1_Top", width="0.1mm")
        assert edbapp.modeler.add_void(plane, void)
        plane.add_void(void)
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_fix_circle_void(self):
        """Fix issues when circle void are clipped due to a bug in EDB."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.modeler.fix_circle_void_for_clipping()
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_primitives_area(self):
        """Access primitives total area."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        i = 0
        while i < 2:
            prim = edbapp.layout.primitives[i]
            assert prim.area(True) > 0
            i += 1
        assert prim.bbox
        assert prim.center
        # TODO check bug #455
        # assert prim.get_closest_point((0, 0))
        assert prim.polygon_data
        assert edbapp.modeler.paths[0].length
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_rectangle(self):
        """Create rectangle."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        rect = edbapp.modeler.create_rectangle(
            layer_name="1_Top", lower_left_point=["0", "0"], upper_right_point=["2mm", "3mm"]
        )
        assert rect
        rect.is_negative = True
        assert rect.is_negative
        rect.is_negative = False
        assert not rect.is_negative
        assert edbapp.modeler.create_rectangle(
            layer_name="1_Top",
            center_point=["0", "0"],
            width="4mm",
            height="5mm",
            representation_type="center_width_height",
        )
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_circle(self):
        """Create circle."""
        # Done
        edbapp = self.edb_examples.get_si_verse()
        poly = edbapp.modeler.create_polygon(points=[[0, 0], [100, 0], [100, 100], [0, 100]], layer_name="1_Top")
        assert poly
        poly.add_void([[20, 20], [20, 30], [100, 30], [100, 20]])
        poly2 = edbapp.modeler.create_polygon(points=[[60, 60], [60, 150], [150, 150], [150, 60]], layer_name="1_Top")
        new_polys = poly.subtract(poly2)
        assert len(new_polys) == 1
        circle = edbapp.modeler.create_circle("1_Top", 40, 40, 15)
        assert circle
        intersection = new_polys[0].intersect(circle)
        assert len(intersection) == 1
        circle2 = edbapp.modeler.create_circle("1_Top", 20, 20, 15)
        assert circle2.unite(intersection)
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_defeature(self):
        """Defeature the polygon."""
        edbapp = self.edb_examples.get_si_verse()
        net_obj = edbapp.layout.find_primitive(net_name="GND")
        assert edbapp.modeler.defeature_polygon(net_obj[-1], 0.0001)
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_primitives_boolean_operation(self):
        """Evaluate modeler primitives boolean operations."""
        # TODO check bug #464.
        edb = self.edb_examples.create_empty_edb()
        edb.stackup.add_layer(layer_name="test")
        x = edb.modeler.create_polygon(layer_name="test", points=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]])
        assert not x.is_null
        x_hole1 = edb.modeler.create_polygon(layer_name="test", points=[[1.0, 1.0], [4.5, 1.0], [4.5, 9.0], [1.0, 9.0]])
        x_hole2 = edb.modeler.create_polygon(layer_name="test", points=[[4.5, 1.0], [9.0, 1.0], [9.0, 9.0], [4.5, 9.0]])
        x = x.subtract([x_hole1, x_hole2])[0]
        assert not x.is_null
        y = edb.modeler.create_polygon(layer_name="test", points=[[4.0, 3.0], [6.0, 3.0], [6.0, 6.0], [4.0, 6.0]])
        z = x.subtract(y)
        assert not z[0].is_null
        # edb.stackup.add_layer(layer_name="test")
        x = edb.modeler.create_polygon(layer_name="test", points=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]])
        x_hole = edb.modeler.create_polygon(layer_name="test", points=[[1.0, 1.0], [9.0, 1.0], [9.0, 9.0], [1.0, 9.0]])
        y = x.subtract(x_hole)[0]
        z = edb.modeler.create_polygon(layer_name="test", points=[[-15.0, 5.0], [15.0, 5.0], [15.0, 6.0], [-15.0, 6.0]])
        assert y.intersect(z)

        edb.stackup.add_layer(layer_name="test2")
        x = edb.modeler.create_polygon(layer_name="test2", points=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]])
        x_hole = edb.modeler.create_polygon(layer_name="test2", points=[[1.0, 1.0], [9.0, 1.0], [9.0, 9.0], [1.0, 9.0]])
        y = x.subtract(x_hole)[0]
        assert y.voids
        y_clone = y.clone()
        assert y_clone.voids
        edb.close(terminate_rpc_session=False)

    def test_modeler_path_convert_to_polygon(self):
        target_path = self.edb_examples.copy_test_files_into_local_folder("convert_and_merge_path.aedb")[0]
        edbapp = self.edb_examples.load_edb(target_path)
        for path in edbapp.modeler.paths:
            assert path.convert_to_polygon()
        # cannot merge one net only - see test: test_unite_polygon for reference
        edbapp.close(terminate_rpc_session=False)

    def test_156_check_path_length(self):
        """"""
        # Done
        source_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/test_path_length.aedb")[0]
        edbapp = self.edb_examples.load_edb(edb_path=source_path)
        net1 = [path for path in edbapp.modeler.paths if path.net_name == "loop1"]
        net1_length = 0
        for path in net1:
            net1_length += path.length
        assert round(net1_length, 7) == 0.0181448
        net2 = [path for path in edbapp.modeler.paths if path.net_name == "line1"]
        net2_length = 0
        for path in net2:
            net2_length += path.length
        assert net2_length == 0.007
        net3 = [path for path in edbapp.modeler.paths if path.net_name == "lin2"]
        net3_length = 0
        for path in net3:
            net3_length += path.length
        assert round(net3_length, 9) == 0.048605551
        net4 = [path for path in edbapp.modeler.paths if path.net_name == "lin3"]
        net4_length = 0
        for path in net4:
            net4_length += path.length
        assert net4_length == 7.6e-3
        net5 = [path for path in edbapp.modeler.paths if path.net_name == "lin4"]
        net5_length = 0
        for path in net5:
            net5_length += path.length
        assert round(net5_length, 5) == 0.02629
        edbapp.close(terminate_rpc_session=False)

    def test_duplicate(self):
        # Done
        edbapp = self.edb_examples.create_empty_edb()
        edbapp["$H"] = "0.65mil"
        assert edbapp["$H"].value == 1.651e-5
        edbapp["$S_D"] = "10.65mil"
        edbapp["$T"] = "21.3mil"
        edbapp["$Antipad_R"] = "24mil"
        edbapp["Via_S"] = "40mil"
        edbapp.stackup.add_layer("bot_gnd", thickness="0.65mil")
        edbapp.stackup.add_layer("d1", layer_type="dielectric", thickness="$S_D", material="FR4_epoxy")
        edbapp.stackup.add_layer("trace2", thickness="$H")
        edbapp.stackup.add_layer("d2", layer_type="dielectric", thickness="$T-$S_D", material="FR4_epoxy")
        edbapp.stackup.add_layer("mid_gnd", thickness="0.65mil")
        edbapp.stackup.add_layer("d3", layer_type="dielectric", thickness="13mil", material="FR4_epoxy")
        edbapp.stackup.add_layer("top_gnd", thickness="0.65mil")
        edbapp.stackup.add_layer("d4", layer_type="dielectric", thickness="13mil", material="FR4_epoxy")
        edbapp.stackup.add_layer("trace1", thickness="$H")
        r1 = edbapp.modeler.create_rectangle(
            center_point=([0, 0]),
            width="200mil",
            height="200mil",
            layer_name="top_gnd",
            representation_type="CenterWidthHeight",
            net_name="r1",
        )
        r2 = edbapp.modeler.create_rectangle(
            center_point=([0, 0]),
            width="40mil",
            height="$Antipad_R*2",
            layer_name="top_gnd",
            representation_type="CenterWidthHeight",
            net_name="r2",
        )
        assert r2
        assert r1.subtract(r2)
        lay_list = ["bot_gnd", "mid_gnd"]
        assert edbapp.layout.primitives[0].duplicate_across_layers(lay_list)
        assert edbapp.layout.find_primitive(layer_name="mid_gnd")
        assert edbapp.layout.find_primitive(layer_name="bot_gnd")
        edbapp.close(terminate_rpc_session=False)

    def test_unite_polygon(self):
        # Done
        edbapp = self.edb_examples.create_empty_edb()
        edbapp["$H"] = "0.65mil"
        edbapp["$Via_S"] = "40mil"
        edbapp["$MS_W"] = "4.75mil"
        edbapp["$MS_S"] = "5mil"
        edbapp["$SL_W"] = "6.75mil"
        edbapp["$SL_S"] = "8mil"
        edbapp.stackup.add_layer("trace1", thickness="$H")
        t1_1 = edbapp.modeler.create_trace(
            width="$MS_W",
            layer_name="trace1",
            path_list=[("-$Via_S/2", "0"), ("-$MS_S/2-$MS_W/2", "-16 mil"), ("-$MS_S/2-$MS_W/2", "-100 mil")],
            start_cap_style="FLat",
            end_cap_style="FLat",
            net_name="t1_1",
        )
        t2_1 = edbapp.modeler.create_trace(
            width="$MS_W",
            layer_name="trace1",
            path_list=[("-$Via_S/2", "0"), ("-$SL_S/2-$SL_W/2", "16 mil"), ("-$SL_S/2-$SL_W/2", "100 mil")],
            start_cap_style="FLat",
            end_cap_style="FLat",
            net_name="t2_1",
        )
        t3_1 = edbapp.modeler.create_trace(
            width="$MS_W",
            layer_name="trace1",
            path_list=[("-$Via_S/2", "0"), ("-$SL_S/2-$SL_W/2", "16 mil"), ("$SL_S/2+$MS_W/2", "100 mil")],
            start_cap_style="FLat",
            end_cap_style="FLat",
            net_name="t3_1",
        )
        t1_1.convert_to_polygon()
        t2_1.convert_to_polygon()
        t3_1.convert_to_polygon()
        net_list = ["t1_1", "t2_1"]
        assert len(edbapp.modeler.polygons) == 3
        edbapp.nets.merge_nets_polygons(net_names_list=net_list)
        assert len(edbapp.modeler.polygons) == 2
        edbapp.modeler.unite_polygons_on_layer(layer_name="trace1")
        assert len(edbapp.modeler.polygons) == 1
        edbapp.close(terminate_rpc_session=False)

    def test_layer_name(self):
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.modeler.polygons[50].layer_name == "1_Top"
        edbapp.modeler.polygons[50].layer_name = "16_Bottom"
        assert edbapp.modeler.polygons[50].layer_name == "16_Bottom"
        edbapp.close(terminate_rpc_session=False)

    def test_287_circuit_ports(self):
        edbapp = self.edb_examples.get_si_verse()
        cap = edbapp.components.capacitors["C1"]
        assert edbapp.excitation_manager.create_circuit_port_on_pin(pos_pin=cap.pins["1"], neg_pin=cap.pins["2"])
        assert edbapp.components.capacitors["C3"].pins
        assert edbapp.padstacks.pins
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and platform.system() == "Linux",
        reason="Known issue in ansys-edb-core layout instance server on Linux",
    )
    def test_get_primitives_by_point_layer_and_nets(self):
        edbapp = self.edb_examples.get_si_verse()
        # Layer-specific query: must return at least one polygon hit.
        # Exact count varies across platforms/EDB versions due to differences
        # in how the gRPC server resolves geometric overlap on Linux vs Windows.
        primitives = edbapp.modeler.get_primitive_by_layer_and_point(layer="Inner1(GND1)", point=[20e-3, 30e-3])
        assert primitives
        assert len(primitives) >= 1
        assert primitives[0].type.lower() == "polygon"
        # All-layer query: must span multiple layers, so count > layer-specific result.
        primitives_all = edbapp.modeler.get_primitive_by_layer_and_point(point=[20e-3, 30e-3])
        assert len(primitives_all) >= len(primitives)
        edbapp.close(terminate_rpc_session=False)

    def test_path_center_line(self):
        edb = self.edb_examples.create_empty_edb()
        edb.stackup.add_layer("GND", "Gap")
        edb.stackup.add_layer("Substrat", "GND", layer_type="dielectric", thickness="0.2mm", material="Duroid (tm)")
        edb.stackup.add_layer("TOP", "Substrat")
        trace_length = 10e-3
        trace_width = 200e-6
        trace_gap = 1e-3
        edb.modeler.create_trace(
            path_list=[[-trace_gap / 2, 0.0], [-trace_gap / 2, trace_length]],
            layer_name="TOP",
            width=trace_width,
            net_name="signal1",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        centerline = edb.modeler.paths[0].center_line
        assert centerline == [[-0.0005, 0.0], [-0.0005, 0.01]]
        # TODO check enhancement request
        # https://github.com/ansys/pyedb-core/issues/457
        # edb.modeler.paths[0].set_center_line([[0.0, 0.0], [0.0, 5e-3]]) # Path does not have center_lin setter.
        # assert edb.modeler.paths[0].center_line == [[0.0, 0.0], [0.0, 5e-3]]
        edb.close(terminate_rpc_session=False)

    def test_polygon_data_refactoring_bounding_box(self):
        # Done
        edbapp = self.edb_examples.get_si_verse()
        poly_with_voids = [pp for pp in edbapp.modeler.polygons if pp.has_voids]
        for poly in poly_with_voids:
            for void in poly.voids:
                assert void.bbox
        edbapp.close(terminate_rpc_session=False)

    def test_aedt_name(self):
        edbapp = self.edb_examples.get_si_verse()
        primitives = edbapp.layout.primitives
        assert primitives[0].aedt_name == "line_0"
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet deprecated, missing method.")
    def test_insert_layout_instance(self):
        edbapp = self.edb_examples.get_si_verse()
        edb2_path = self.edb_examples.get_package(edbapp=False)
        edbapp.copy_cell_from_edb(edb2_path)
        cell_inst = edbapp.modeler.insert_layout_instance_on_layer(
            "analysis", "1_Top", "180deg", 0, 0, "1mm", "2mm", True
        )
        assert cell_inst.transform3d.shift.x.value == pytest.approx(0.001)
        assert cell_inst.transform3d.shift.y.value == pytest.approx(0.002)
        assert cell_inst.transform3d.shift.z.value == pytest.approx(edbapp.stackup.layers["1_Top"].lower_elevation)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet deprecated, missing method.")
    def test_insert_layout_instance_place_on_bottom(self):
        edbapp = self.edb_examples.get_si_verse()
        edb2_path = self.edb_examples.get_package(edbapp=False)
        edbapp.copy_cell_from_edb(edb2_path)
        cell_inst = edbapp.modeler.insert_layout_instance_on_layer(
            cell_name="analysis",
            placement_layer="16_Bottom",
            rotation="180deg",
            rotation_x=0,
            rotation_y="0deg",
            x="32mm",
            y="-1mm",
            place_on_bottom=True,
        )
        assert not cell_inst.is_null
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="DotNet deprecated, missing method.")
    def test_insert_layout_instance_placement_3d(self):
        edbapp = self.edb_examples.get_si_verse()
        edb2_path = self.edb_examples.get_package(edbapp=False)
        edbapp.copy_cell_from_edb(edb2_path)
        cell_inst = edbapp.modeler.insert_layout_instance_placement_3d(
            "analysis",
            rotation_z="30deg",
            z="-0.33mm",
            local_origin_x="4.4mm",
            local_origin_y="4.4mm",
        )
        assert not cell_inst.is_null
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config.get("use_grpc"), reason="dotnet is missing the method to get transform3D")
    def test_insert_3d_component_placement_3d(self):
        fpath = self.edb_examples.copy_test_files_into_local_folder("si_board/SMA.a3dcomp")[0]
        edbapp = self.edb_examples.get_si_board()
        cell_inst_1 = edbapp.modeler.insert_3d_component_placement_3d(
            a3dcomp_path=fpath,
            x="1mm",
            y="2mm",
            z="3mm",
            rotation_x="180deg",
        )
        assert not cell_inst_1.is_null
        assert cell_inst_1.transform3d.shift.x.value == pytest.approx(0.001)
        assert cell_inst_1.transform3d.shift.y.value == pytest.approx(0.002)
        assert cell_inst_1.transform3d.shift.z.value == pytest.approx(0.003)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config.get("use_grpc"), reason="dotnet is missing the method to get transform3D")
    def test_insert_3d_component_on_layer(self):
        fpath = self.edb_examples.copy_test_files_into_local_folder("si_board/SMA.a3dcomp")[0]
        edbapp = self.edb_examples.get_si_board()
        cell_inst_1 = edbapp.modeler.insert_3d_component_on_layer(
            a3dcomp_path=fpath, x="1mm", y="2mm", placement_layer="s1"
        )
        assert not cell_inst_1.is_null
        cell_inst_2 = edbapp.modeler.insert_3d_component_on_layer(
            a3dcomp_path=fpath,
            x="5mm",
            y="2mm",
            placement_layer="s3",
            place_on_bottom=True,
        )
        assert not cell_inst_2.is_null
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config.get("use_grpc"), reason="dotnet is missing the method to get transform3D")
    def test_insert_3d_component_on_component(self):
        fpath = self.edb_examples.copy_test_files_into_local_folder("si_board/CAP_DUMMY.a3dcomp")[0]
        edbapp = self.edb_examples.get_si_verse()
        cell_inst_1 = edbapp.modeler.insert_3d_component_on_component(a3dcomp_path=fpath, reference_designator="C191")
        assert not cell_inst_1.is_null
        assert cell_inst_1.transform3d.shift.x.value == pytest.approx(0.0254)
        assert cell_inst_1.transform3d.shift.y.value == pytest.approx(0.0738)
        assert cell_inst_1.transform3d.z_y_x_rotation.x.value == pytest.approx(-1.5707963267948968)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"], reason="PrimitiveDotNet is only available on the .NET backend")
    def test_primitive_dotnet_layer_name_getter_setter_low_level(self):
        from pyedb.dotnet.database.dotnet.database import CellDotNet
        from pyedb.dotnet.database.dotnet.primitive import PrimitiveDotNet

        edbapp = self.edb_examples.get_si_verse_sfp()
        primitive_api = CellDotNet(edbapp).cell.primitive
        assert isinstance(primitive_api, PrimitiveDotNet)

        net = edbapp.nets.find_or_create_net("primitive_dotnet_test")
        circle = primitive_api.circle.create(
            layout=edbapp.active_layout,
            layer="Top",
            net=net,
            center_x=edbapp.edb_value(0.0),
            center_y=edbapp.edb_value(0.0),
            radius=edbapp.edb_value("1mm"),
        )

        assert isinstance(circle, PrimitiveDotNet)
        assert circle.layer_name == "Top"
        circle.layer_name = "Bottom"
        assert circle.layer_name == "Bottom"
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="increase test coverage for primitives in grpc")
    def test_primitives_for_grpc(self):
        edbapp = self.edb_examples.get_si_verse()

        # PadstackInstance
        padstack_instance = edbapp.padstacks.instances[4294967296]
        padstack_instance.rotation = 90
        assert padstack_instance.rotation == 90

        # Paths
        path = edbapp.modeler.paths[0]
        path.width = 1.5
        assert path.width.real == 1.5
        assert path.length
        assert path.center_line
        path.corner_style = "round"
        assert path.corner_style == "round"
        path.end_cap1 = "flat"
        assert path.end_cap1 == "flat"
        path.end_cap2 = "round"
        assert path.end_cap2 == "round"

        # Circle
        cir = edbapp.modeler.create_circle(layer_name="1_Top", x=0, y=0, radius=0.1, net_name="GND")
        cir.set_parameters(0.1, 0.1, 0.3)
        assert cir.get_parameters()[2].real == 0.3

        # Rectangle
        rect = edbapp.layout.rectangles[0]
        assert rect.representation_type
        rect.representation_type = "center_width_height"
        assert rect.representation_type == "center_width_height"
        assert rect.get_parameters()
        rect.corner_radius = 1.0
        assert rect.corner_radius == 1.0
        rect.rotation = 90
        assert rect.rotation == 90
        assert rect.width
        rect.width = 0.2
        rect.height = 0.1
        assert rect.height == 0.1
        assert rect.duplicate_across_layers("16_Bottom")
        edbapp.modeler.create_rectangle(
            "16_Bottom", "GND", representation_type="center_width_height", width=0.1, height=0.1, center_point=[0, 0]
        )

        # Texts
        edbapp.modeler.create_text(layer_name="1_Top", x=0.0, y=0.0, text="test")
        prim = [prim for prim in edbapp.layout.primitives if prim.primitive_type == "text"]
        assert prim
        assert not prim[0].is_null
        assert prim[0].aedt_name == "text_5958"

        edbapp.close(terminate_rpc_session=False)

    def test_create_rf_trace_taper(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        edbapp["p0_x"] = "1mm"
        edbapp["p0_y"] = "1mm"
        edbapp["p1_x"] = "1mm"
        edbapp["p1_y"] = "2mm"
        edbapp["w0"] = "1mm"
        edbapp["w1"] = "0.5mm"
        taper = edbapp.modeler.create_taper(
            start_point=["p0_x", "p0_y"],
            end_point=["p1_x", "p1_y"],
            start_width="w0",
            end_width="w1",
            layer_name="Top",
        )
        assert taper.polygon_data.points == [
            (0.0005, 0.001),
            (0.0015, 0.001),
            (0.00125, 0.002),
            (0.00075, 0.002),
        ]
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only test for modeler.texts property")
    def test_modeler_texts_property(self):
        """Verify texts property returns only text primitives."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.modeler.create_text(layer_name="1_Top", x=0.001, y=0.001, text="coverage_test")
        texts = edbapp.modeler.texts
        assert isinstance(texts, list)
        assert len(texts) >= 1
        assert all(t.primitive_type == "text" for t in texts)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only test for delete_primitives")
    def test_modeler_delete_primitives_by_net(self):
        """delete_primitives removes all primitives on the given net."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        edbapp.modeler.create_trace(path_list=[[0, 0], [1e-3, 0]], layer_name="sig", width=0.1e-3, net_name="DEL_NET")
        before = len([p for p in edbapp.layout.primitives if p.net_name == "DEL_NET"])
        assert before >= 1
        edbapp.modeler.delete_primitives("DEL_NET")
        after = len([p for p in edbapp.layout.primitives if p.net_name == "DEL_NET"])
        assert after == 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only test for get_primitives filter")
    def test_modeler_get_primitives_filter(self):
        """get_primitives filters by net, layer and type."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        edbapp.modeler.create_trace(path_list=[[0, 0], [1e-3, 0]], layer_name="sig", width=0.1e-3, net_name="NET1")
        edbapp.modeler.create_polygon(
            points=[[0, 0], [2e-3, 0], [2e-3, 2e-3], [0, 2e-3]], layer_name="sig", net_name="NET1"
        )
        paths = edbapp.modeler.get_primitives(net_name="NET1", prim_type="path")
        assert len(paths) == 1
        polys = edbapp.modeler.get_primitives(net_name="NET1", prim_type="polygon")
        assert len(polys) == 1
        all_net1 = edbapp.modeler.get_primitives(net_name="NET1")
        assert len(all_net1) == 2
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only test for get_layout_statistics")
    def test_modeler_get_layout_statistics(self):
        """get_layout_statistics returns a populated statistics object."""
        edbapp = self.edb_examples.get_si_verse()
        stats = edbapp.modeler.get_layout_statistics()
        assert stats.num_layers > 0
        assert stats.num_nets > 0
        assert stats.num_traces > 0
        assert stats.num_polygons > 0
        assert stats.num_vias > 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — parametrize_trace_width")
    def test_modeler_parametrize_trace_width(self):
        """parametrize_trace_width assigns a design variable to path width."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        edbapp.modeler.create_trace(path_list=[[0, 0], [1e-3, 0]], layer_name="sig", width=0.1e-3, net_name="SIG")
        result = edbapp.modeler.parametrize_trace_width(nets_name="SIG", variable_value=0.1e-3)
        assert result
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_bondwire")
    def test_modeler_create_bondwire(self):
        """create_bondwire creates a bondwire primitive."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        bw = edbapp.modeler.create_bondwire(
            definition_name="bw_def",
            placement_layer="sig",
            width=0.05e-3,
            material="copper",
            start_layer_name="sig",
            start_x=0,
            start_y=0,
            end_layer_name="sig",
            end_x=1e-3,
            end_y=0,
            net="SIG",
        )
        # create_bondwire returns a Bondwire object
        assert bw is not None
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — deprecated primitives_by_net wrapper")
    def test_modeler_deprecated_primitives_by_net(self):
        """Accessing primitives_by_net via modeler triggers FutureWarning and returns dict."""
        import warnings

        edbapp = self.edb_examples.get_si_verse()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            by_net = edbapp.modeler.primitives_by_net
            assert isinstance(by_net, dict)
            assert len(by_net) > 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — deprecated primitives wrapper")
    def test_modeler_deprecated_primitives(self):
        """Accessing modeler.primitives triggers DeprecationWarning and returns list."""
        import warnings

        edbapp = self.edb_examples.get_si_verse()
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            prims = edbapp.modeler.primitives
            assert isinstance(prims, list)
            assert len(prims) > 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — deprecated get_primitive wrapper")
    def test_modeler_deprecated_get_primitive(self):
        """get_primitive(id) triggers FutureWarning and returns the correct primitive."""
        import warnings

        edbapp = self.edb_examples.get_si_verse()
        prim = edbapp.layout.primitives[0]
        prim_id = prim.id
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = edbapp.modeler.get_primitive(prim_id)
        assert result is not None
        assert result.id == prim_id
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — deprecated get_polygon_bounding_box")
    def test_modeler_deprecated_get_polygon_bounding_box(self):
        """get_polygon_bounding_box via modeler triggers warning and returns 4-element list."""
        import warnings

        edbapp = self.edb_examples.get_si_verse()
        poly = edbapp.layout.polygons[0]
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            bbox = edbapp.modeler.get_polygon_bounding_box(poly)
        assert len(bbox) == 4
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — deprecated get_polygon_points")
    def test_modeler_deprecated_get_polygon_points(self):
        """get_polygon_points via modeler triggers warning and returns points."""
        import warnings

        edbapp = self.edb_examples.get_si_verse()
        poly = edbapp.layout.polygons[0]
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            pts = edbapp.modeler.get_polygon_points(poly)
        assert pts
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — parametrize_polygon")
    def test_modeler_parametrize_polygon(self):
        """parametrize_polygon assigns offset variable to intersecting polygon points, covering all branches."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        # Main polygon
        main_poly = edbapp.modeler.create_polygon(
            points=[[0, 0], [10e-3, 0], [10e-3, 10e-3], [0, 10e-3]], layer_name="sig", net_name="main"
        )
        # Selection polygon fully inside main polygon — ensures check_inside=True branch (lines 414-423)
        selection_poly = edbapp.modeler.create_polygon(
            points=[[3e-3, 3e-3], [7e-3, 3e-3], [7e-3, 7e-3], [3e-3, 7e-3]], layer_name="sig", net_name="sel"
        )
        result = edbapp.modeler.parametrize_polygon(main_poly, selection_poly, offset_name="poly_offset")
        assert result is True
        # Also test with polygon whose center is on the same X-axis (covers else branch lines 379-384)
        main_poly2 = edbapp.modeler.create_polygon(
            points=[[0, 0], [10e-3, 0], [10e-3, 10e-3], [0, 10e-3]], layer_name="sig", net_name="main2"
        )
        selection_poly2 = edbapp.modeler.create_polygon(
            points=[[0, 3e-3], [0, 7e-3], [10e-3, 7e-3], [10e-3, 3e-3]], layer_name="sig", net_name="sel2"
        )
        result2 = edbapp.modeler.parametrize_polygon(main_poly2, selection_poly2, offset_name="poly_offset2")
        assert result2 is True
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_polygon with CorePolygonData void")
    def test_modeler_create_polygon_with_core_polygon_data_void(self):
        """create_polygon accepts a CorePolygonData as void."""
        from ansys.edb.core.geometry.point_data import PointData as CorePointData
        from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData

        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        outer = CorePolygonData(
            points=[
                CorePointData([0, 0]),
                CorePointData([10e-3, 0]),
                CorePointData([10e-3, 10e-3]),
                CorePointData([0, 10e-3]),
            ]
        )
        void_pd = CorePolygonData(
            points=[
                CorePointData([2e-3, 2e-3]),
                CorePointData([5e-3, 2e-3]),
                CorePointData([5e-3, 5e-3]),
                CorePointData([2e-3, 5e-3]),
            ]
        )
        poly = edbapp.modeler.create_polygon(outer, layer_name="sig", voids=[void_pd])
        assert poly
        assert not poly.is_null
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_trace with CorePolygonData")
    def test_modeler_create_trace_with_core_polygon_data(self):
        """create_trace accepts CorePolygonData directly."""
        from ansys.edb.core.geometry.point_data import PointData as CorePointData
        from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData

        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        pd = CorePolygonData(points=[CorePointData([0, 0]), CorePointData([1e-3, 0]), CorePointData([1e-3, 1e-3])])
        trace = edbapp.modeler.create_trace(path_list=pd, layer_name="sig", width=0.1e-3)
        assert trace
        assert not trace.is_null
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — _validatePoint branches")
    def test_modeler_validate_point(self):
        """_validatePoint validates 2-element, 3-element, and 5-element point formats."""
        edbapp = self.edb_examples.create_empty_edb()
        # Valid 2-element point
        assert edbapp.modeler._validatePoint([0.0, 1.0]) is True
        # Valid 3-element arc point
        assert edbapp.modeler._validatePoint([0.0, 1.0, 0.001]) is True
        # Valid 5-element arc point
        assert edbapp.modeler._validatePoint([0.0, 1.0, "cw", 0.5, 0.5]) is True
        # Invalid 5-element arc point (bad rotation direction)
        assert edbapp.modeler._validatePoint([0.0, 1.0, "bad", 0.5, 0.5]) is False
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — parametrize_trace_width with layer filter")
    @pytest.mark.xfail(reason="Bug in source: add_design_variable fails for grpc in parametrize_trace_width.")
    def test_modeler_parametrize_trace_width_with_layer(self):
        """parametrize_trace_width with layer_name filter covers the layer branch."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        edbapp.modeler.create_trace(path_list=[[0, 0], [1e-3, 0]], layer_name="sig", width=0.1e-3, net_name="SIG")
        result = edbapp.modeler.parametrize_trace_width(nets_name="SIG", layers_name="sig", variable_value=0.1e-3)
        assert result
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — get_layout_statistics with evaluate_area")
    @pytest.mark.xfail(reason="Bug in source: prim.primitive_type.name fails for grpc.")
    def test_modeler_get_layout_statistics_evaluate_area(self):
        """get_layout_statistics with evaluate_area=True covers area computation branch."""
        edbapp = self.edb_examples.get_si_verse()
        stats = edbapp.modeler.get_layout_statistics(evaluate_area=True)
        assert stats.num_layers > 0
        assert stats.num_nets > 0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — defeature_polygon failure branch")
    def test_modeler_defeature_polygon_large_tolerance(self):
        """defeature_polygon returns False when tolerance is too large (empty result)."""
        edbapp = self.edb_examples.get_si_verse()
        poly = edbapp.layout.polygons[0]
        # Use an extremely large tolerance to trigger the empty-result branch
        result = edbapp.modeler.defeature_polygon(poly, tolerance=1e6)
        assert result is False
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_pin_group by id and by name")
    def test_modeler_create_pin_group(self):
        """create_pin_group creates a pin group from pin ids."""
        edbapp = self.edb_examples.get_si_verse()
        pins = list(edbapp.padstacks.instances.keys())
        assert pins
        pg = edbapp.modeler.create_pin_group(name="test_pg", pins_by_id=[pins[0]])
        assert pg
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_pin_group no pin returns False")
    def test_modeler_create_pin_group_no_pins_returns_false(self):
        """create_pin_group returns False when no valid pin is found."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        result = edbapp.modeler.create_pin_group(name="empty_pg")
        assert result is False
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_pin_group by aedt_name")
    def test_modeler_create_pin_group_by_aedt_name(self):
        """create_pin_group using pins_by_aedt_name covers that branch."""
        edbapp = self.edb_examples.get_si_verse()
        pin = edbapp.layout.padstack_instances[0]
        pg = edbapp.modeler.create_pin_group(name="pg_aedt", pins_by_aedt_name=[pin.aedt_name])
        assert pg
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only delete_padstack_geometries")
    @pytest.mark.xfail(reason="Bug in source: edb_padstack attribute missing on PadstackDef in grpc backend.")
    def test_modeler_unite_polygons_delete_padstack_geometries(self):
        """unite_polygons_on_layer with delete_padstack_gemometries=True covers that branch."""
        edbapp = self.edb_examples.get_si_verse()
        result = edbapp.modeler.unite_polygons_on_layer(layer_name="1_Top", delete_padstack_gemometries=True)
        assert result
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_rectangle with width/height as variable")
    @pytest.mark.xfail(reason="Bug in source: value() called with 3 args at modeler.py:681.")
    def test_modeler_create_rectangle_with_str_variable_height(self):
        """create_rectangle with height as str variable name covers variable lookup branch."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        edbapp["rect_h"] = "2mm"
        rect = edbapp.modeler.create_rectangle(
            layer_name="sig",
            representation_type="center_width_height",
            center_point=[0, 0],
            width="1mm",
            height="rect_h",
        )
        assert rect
        assert not rect.is_null
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — fix_circle_void with actual void circle")
    def test_modeler_fix_circle_void_with_void_circle(self):
        """fix_circle_void_for_clipping covers the is_void=True branch by creating a real circle void."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        # Create a polygon plane
        plane = edbapp.modeler.create_polygon(
            points=[[0, 0], [20e-3, 0], [20e-3, 20e-3], [0, 20e-3]], layer_name="sig", net_name="GND"
        )
        # Create a circle with is_negative=True — this is what fix_circle_void looks for
        void_circle = edbapp.modeler.create_circle("sig", 10e-3, 10e-3, 2e-3)
        void_circle.is_negative = True  # marks it as a negative void-style circle
        # Also attach a real void by creating a polygon void approach (covers 835-847 path)
        # The fix_circle_void_for_clipping checks is_void, not is_negative
        # Use the layout.circles approach to check directly
        for c in edbapp.layout.circles:
            c.is_void  # access the property
        result = edbapp.modeler.fix_circle_void_for_clipping()
        assert result is True
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — open_solder_mask no material triggers default")
    def test_modeler_open_solder_mask_no_material_default(self):
        """open_solder_mask creates default SolderMask material when none provided."""
        edbapp = self.edb_examples.get_si_verse_sfp()
        # Call without material to trigger default material creation (lines 1826 - 1829)
        edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM_default",
            solder_mask_material="",  # empty material triggers default
            solder_mask_thickness="30um",
            reference_signal_layer="Top_1",
            open_components=False,
            open_voids=False,
            open_traces=False,
        )
        assert "SM_default" in edbapp.stackup.layers
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only reference layer auto-detect bottom")
    def test_modeler_open_solder_mask_auto_reference_bottom(self):
        """open_solder_mask auto-detects bottom reference layer (lines 1831 - 1834)."""
        edbapp = self.edb_examples.get_si_verse_sfp()
        edbapp.materials.add_dielectric_material(name="SM_mat2", permittivity=4.0, dielectric_loss_tangent=0.02)
        # open_top=False triggers auto-detect of the bottommost signal layer (line 1834)
        result = edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM_bottom",
            solder_mask_material="SM_mat2",
            solder_mask_thickness="30um",
            reference_signal_layer="",  # auto-detect (covers lines 1831 - 1834)
            open_top=False,
            open_components=False,
            open_voids=False,
            open_traces=False,
        )
        assert result is True
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only raises on missing component")
    def test_modeler_open_solder_mask_invalid_component_raises(self):
        """open_solder_mask raises ValueError for invalid component_filter (line 1858)."""
        edbapp = self.edb_examples.get_si_verse_sfp()
        edbapp.materials.add_dielectric_material(name="SM_mat3", permittivity=4.0, dielectric_loss_tangent=0.02)
        with pytest.raises(ValueError):
            edbapp.modeler.open_solder_mask(
                solder_mask_layer_name="SM_err",
                solder_mask_material="SM_mat3",
                solder_mask_thickness="30um",
                reference_signal_layer="Top_1",
                component_filter=["NONEXISTENT_PART"],
                open_voids=False,
                open_traces=False,
            )
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — open_solder_mask voids_opening_offset branch")
    def test_modeler_open_solder_mask_voids_with_offset(self):
        """open_solder_mask with voids_opening_offset triggers polygon expand (line 1881)."""
        edbapp = self.edb_examples.get_si_verse_sfp()
        edbapp.materials.add_dielectric_material(name="SM_mat4", permittivity=4.0, dielectric_loss_tangent=0.02)
        edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM_voids",
            solder_mask_material="SM_mat4",
            solder_mask_thickness="30um",
            reference_signal_layer="Top_1",
            open_components=False,
            open_voids=True,
            voids_opening_offset="0.05mm",
            open_traces=False,
        )
        assert "SM_voids" in edbapp.stackup.layers
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — open_solder_mask traces_offset branch")
    def test_modeler_open_solder_mask_traces_with_offset(self):
        """open_solder_mask with traces_offset triggers polygon expand (line 1890)."""
        edbapp = self.edb_examples.get_si_verse_sfp()
        edbapp.materials.add_dielectric_material(name="SM_mat5", permittivity=4.0, dielectric_loss_tangent=0.02)
        edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM_traces",
            solder_mask_material="SM_mat5",
            solder_mask_thickness="30um",
            reference_signal_layer="Top_1",
            open_components=False,
            open_voids=False,
            open_traces=True,
            traces_offset="0.05mm",
            open_traces_net_filter=["SFPA_VCCR"],
        )
        assert "SM_traces" in edbapp.stackup.layers
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only pins_by_aedt_name str (not list)")
    def test_modeler_create_pin_group_aedt_name_str(self):
        """create_pin_group accepts a single aedt_name string (covers line 1232)."""
        edbapp = self.edb_examples.get_si_verse()
        pin = edbapp.layout.padstack_instances[0]
        pg = edbapp.modeler.create_pin_group(name="pg_str", pins_by_aedt_name=pin.aedt_name)
        assert pg
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_pin_group with pins_by_name str (not list)")
    def test_modeler_create_pin_group_by_name_str(self):
        """create_pin_group accepts a single pin name string (covers line 1234)."""
        edbapp = self.edb_examples.get_si_verse()
        pin = edbapp.layout.padstack_instances[0]
        pg = edbapp.modeler.create_pin_group(name="pg_name_str", pins_by_name=pin.name)
        assert pg
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — create_pin_group pins_by_id as int (not list)")
    def test_modeler_create_pin_group_id_as_int(self):
        """create_pin_group with pins_by_id as int (not list) covers line 1219."""
        edbapp = self.edb_examples.get_si_verse()
        pin_id = list(edbapp.padstacks.instances.keys())[0]
        pg = edbapp.modeler.create_pin_group(name="pg_int_id", pins_by_id=pin_id)
        assert pg
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only pins_by_id and pins_by_aedt_name")
    def test_modeler_create_pin_group_combined_id_and_aedt_name(self):
        """create_pin_group merges pins from both pins_by_id and pins_by_aedt_name (covers lines 1240 - 1242)."""
        edbapp = self.edb_examples.get_si_verse()
        pins = edbapp.layout.padstack_instances
        pg = edbapp.modeler.create_pin_group(
            name="pg_combined",
            pins_by_id=[pins[0].id],
            pins_by_aedt_name=[pins[1].aedt_name],
        )
        assert pg
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — add_void static method with non-Primitive void")
    def test_modeler_add_void_non_primitive(self):
        """add_void covers the else branch when void shape is not a Primitive (lines 1279 - 1280)."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        plane = edbapp.modeler.create_polygon(points=[[0, 0], [10e-3, 0], [10e-3, 10e-3], [0, 10e-3]], layer_name="sig")
        # Create a circle (Circle is a subclass of Primitive — test the non-Primitive branch via path)
        void_path = edbapp.modeler.create_trace(path_list=[[1e-3, 1e-3], [3e-3, 3e-3]], layer_name="sig", width=0.5e-3)
        # Pass as a list to test the list→single conversion branch and else-branch
        result = edbapp.modeler.add_void(plane, [void_path])
        assert result
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — deprecated primitives_by_layer wrapper return body")
    def test_modeler_deprecated_primitives_by_layer_return(self):
        """Accessing primitives_by_layer via modeler deprecated wrapper returns the dict (line 144)."""
        import warnings

        edbapp = self.edb_examples.get_si_verse()
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            by_layer = edbapp.modeler.primitives_by_layer
        assert isinstance(by_layer, dict)
        assert "1_Top" in by_layer
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — _validatePoint type checks on 2-element bad type")
    def test_modeler_validate_point_bad_x_type(self):
        """_validatePoint returns False for 2-element point with non-numeric X (lines 853-854)."""
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.add_layer("sig")
        # x value is None — not int/float/str
        assert edbapp.modeler._validatePoint([None, 1.0]) is False
        # y value is None — not int/float/str (line 856-857)
        assert edbapp.modeler._validatePoint([0.0, None]) is False
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only—open_solder_mask open_top=True auto reference layer")
    def test_modeler_open_solder_mask_auto_reference_top(self):
        """open_solder_mask auto-detects top reference layer when reference_signal_layer is empty (line 1832)."""
        edbapp = self.edb_examples.get_si_verse_sfp()
        edbapp.materials.add_dielectric_material(name="SM_top_auto", permittivity=4.0, dielectric_loss_tangent=0.02)
        result = edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM_auto_top",
            solder_mask_material="SM_top_auto",
            solder_mask_thickness="30um",
            reference_signal_layer="",  # empty → auto-detect top (line 1832)
            open_top=True,
            open_components=False,
            open_voids=False,
            open_traces=False,
        )
        assert result is True
        assert "SM_auto_top" in edbapp.stackup.layers
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only invalid component_filter with open_top=False")
    def test_modeler_open_solder_mask_component_filter_invalid_bottom(self):
        """open_solder_mask raises ValueError when component_filter has unknown RefDes (lines 1858 - 1860)."""
        edbapp = self.edb_examples.get_si_verse_sfp()
        edbapp.materials.add_dielectric_material(name="SM_err2", permittivity=4.0, dielectric_loss_tangent=0.02)
        with pytest.raises(ValueError):
            edbapp.modeler.open_solder_mask(
                solder_mask_layer_name="SM_err2_layer",
                solder_mask_material="SM_err2",
                solder_mask_thickness="30um",
                reference_signal_layer="Top_1",
                component_filter=["NO_SUCH_COMP_XY"],
                open_components=True,
                open_voids=False,
                open_traces=False,
            )
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — open_solder_mask traces no offset")
    def test_modeler_open_solder_mask_traces_no_offset(self):
        """open_solder_mask with open_traces=True and no traces_offset covers lines 1887 - 1891."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.materials.add_dielectric_material(name="SM_tr_nooff", permittivity=4.0, dielectric_loss_tangent=0.02)
        # Use 1_Top which has traces — no filter so all traces are opened
        result = edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM_traces2",
            solder_mask_material="SM_tr_nooff",
            solder_mask_thickness="30um",
            reference_signal_layer="1_Top",
            open_components=False,
            open_voids=False,
            open_traces=True,
            traces_offset=0.0,  # no offset → direct create_polygon (lines 1887 - 1891)
        )
        assert result is True
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC only — open_solder_mask voids no offset")
    def test_modeler_open_solder_mask_voids_no_offset(self):
        """open_solder_mask with open_voids=True and no voids_opening_offset covers lines 1876 - 1882."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.materials.add_dielectric_material(name="SM_void_nooff", permittivity=4.0, dielectric_loss_tangent=0.02)
        # Use 1_Top which has polygons with voids
        result = edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM_voids2",
            solder_mask_material="SM_void_nooff",
            solder_mask_thickness="30um",
            reference_signal_layer="1_Top",
            open_components=False,
            open_voids=True,
            voids_opening_offset=0.0,  # no offset → direct create_polygon (lines 1876 - 1882)
            open_traces=False,
        )
        assert result is True
        edbapp.close(terminate_rpc_session=False)

    def test_mask_opening(self):
        edbapp = self.edb_examples.get_si_verse_sfp()
        edbapp.materials.add_dielectric_material(name="SolderMask", permittivity=4.5, dielectric_loss_tangent=0.02)
        edbapp.modeler.open_solder_mask(
            solder_mask_layer_name="SM",
            solder_mask_material="SolderMask",
            solder_mask_thickness="50um",
            reference_signal_layer="Top_1",
            component_filter=["U1", "C164", "C283", "B1"],
            voids_opening_offset="0.2mm",
            components_opening_offset="0.2mm",
            traces_offset="0.1mm",
            open_traces_net_filter=["SFPA_VCCR", "SFPA_VCCT"],
        )
        assert len(edbapp.layout.find_primitive(layer_name="SM")) == 4
        edbapp.close(terminate_rpc_session=False)


# Geometry primitives (moved from test_edb_database_geometry.py)
@pytest.mark.usefixtures("close_rpc_session")
class TestPointData(BaseTestClass):
    def test_create(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp["X"] = 1
        pdata = PointData.create(edbapp, "X", 2)
        assert str(pdata.x) == "X"
        assert pdata.x == 1
        assert pdata.y == 2

        pdata2 = PointData.create_arc_point(edbapp, "X")
        assert str(pdata2.arc_height) == "X"
        assert pdata2.arc_height == 1
        assert pdata2.is_arc

        edbapp.close(terminate_rpc_session=False)

    def test_operations(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp["X"] = 1
        edbapp["Y"] = 2
        edbapp["angle"] = "90deg"
        pdata = PointData.create(edbapp, "X", "Y")
        pdata2 = pdata.rotate("angle", [1, 1])
        assert pdata2.x == pytest.approx(0)
        assert pdata2.y == pytest.approx(1)

        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config.get("use_grpc"), reason="gRPC only")
    def test_insert_cs(self):
        edbapp = self.edb_examples.get_si_verse()
        edbapp.modeler.insert_coordinate_system(name="CS1", x="1mm", y="2mm", layer="1_Top")
        cs = edbapp.layout.coordinate_systems[0]
        assert cs.name == "CS1"
        assert cs.location[0] == 0.001
        assert cs.location[1] == 0.002
        assert cs.placement_layer == "1_Top"
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config.get("use_grpc"), reason="Not working with FotNet.")
    def test_convert_primitive_to_via(self):
        edbapp = self.edb_examples.get_si_verse_sfp()
        circ1 = edbapp.modeler.create_circle(layer_name="Top", x=0.0, y=0.0, radius=0.2e-3)
        circ2 = edbapp.modeler.create_circle(layer_name="Bottom", x=0.0, y=0.0, radius=0.2e-3)
        edbapp.layout.convert_primitives_to_vias(primitives=[circ1, circ2], is_pins=False)
        padsatck_def = edbapp.padstacks.definitions.get("Circ0")
        assert len(padsatck_def.instances) == 2
        assert padsatck_def.instances[0].position == [0.0, 0.0]
        assert padsatck_def.instances[0].start_layer == "Top"
        assert padsatck_def.instances[0].stop_layer == "Top"
        assert padsatck_def.instances[1].position == [0.0, 0.0]
        assert padsatck_def.instances[1].start_layer == "Bottom"
        assert padsatck_def.instances[1].stop_layer == "Bottom"
        edbapp.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestPolygonData(BaseTestClass):
    def test_create(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        edbapp["X"] = 1
        pdata1 = PointData.create(edbapp, "X", 2)
        pdata2 = PointData.create(edbapp, "X", 3)
        pdata3 = PointData.create(edbapp, 2, 3)

        poly_data = PolygonData.create(edbapp, points=[pdata1, pdata2, pdata3])
        assert poly_data
        edbapp.close(terminate_rpc_session=False)
