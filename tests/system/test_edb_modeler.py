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

"""Tests related to Edb modeler"""

import os
from pathlib import Path

import pytest

from pyedb.generic.settings import settings
from tests.conftest import local_path, test_subfolder, config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_modeler_polygons(self, edb_examples):
        """Evaluate modeler polygons"""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert len(edbapp.modeler.polygons) > 0
        assert not edbapp.modeler.polygons[0].is_void

        poly0 = edbapp.modeler.polygons[0]
        assert edbapp.modeler.polygons[0].clone()
        assert isinstance(poly0.voids, list)
        # TODO convert point_raw as property in dotnet to be compliant with grpc.
        if edbapp.grpc:
            assert isinstance(poly0.points_raw, list)
        else:
            assert isinstance(poly0.points_raw(), list)
        assert isinstance(poly0.points(), tuple)
        assert isinstance(poly0.points()[0], list)
        assert poly0.points()[0][0] >= 0.0
        if edbapp.grpc:
            assert poly0.points_raw[0].x.value >= 0.0
        else:
            assert poly0.points_raw()[0].X.ToDouble() >= 0.0
        # TODO check is polygon.type should return "polygon" instead of "Polygon",
        assert poly0.type.lower() == "polygon"
        if edbapp.grpc:
            assert not poly0.points_raw[0].is_arc
        else:
            assert not poly0.points_raw()[0].IsArc()
        assert isinstance(poly0.voids, list)
        # TODO check bug 455
        # assert isinstance(poly0.get_closest_point([0.07, 0.0027]), list)
        assert isinstance(poly0.get_closest_arc_midpoint([0, 0]), list)
        assert isinstance(poly0.arcs, list)
        assert isinstance(poly0.longest_arc.length, float)
        assert isinstance(poly0.shortest_arc.length, float)
        assert not poly0.in_polygon([0, 0])
        # TODO make grpc arc.is_segment a property
        if edbapp.grpc:
            assert poly0.arcs[0].is_segment()
        else:
            assert poly0.arcs[0].is_segment
        # TODO make grpc arc.is_point a property
        if edbapp.grpc:
            assert not poly0.arcs[0].is_point()
        else:
            assert not poly0.arcs[0].is_point
        # TODO make grpc arc.is_cww a property
        if edbapp.grpc:
            assert not poly0.arcs[0].is_ccw()
        else:
            assert not poly0.arcs[0].is_ccw
        assert isinstance(poly0.arcs[0].points, list)
        assert isinstance(poly0.intersection_type(poly0), int)
        assert poly0.is_intersecting(poly0)
        poly_3022 = edbapp.modeler.get_primitive(3022)
        assert edbapp.modeler.get_primitive(3023)
        assert poly_3022.aedt_name == "poly_3022"
        poly_3022.aedt_name = "poly3022"
        assert poly_3022.aedt_name == "poly3022"
        poly_with_voids = [poly for poly in edbapp.modeler.polygons if poly.has_voids]
        assert poly_with_voids
        for k in poly_with_voids[0].voids:
            assert k.id
            assert k.expand(0.0005)
        if edbapp.grpc:
            poly_167 = [i for i in edbapp.modeler.paths if i.edb_uid == 167][0]
        else:
            poly_167 = [i for i in edbapp.modeler.paths if i.id == 167][0]
        if edbapp.grpc:
            # Only available with grpc
            assert poly_167.expand(0.0005)
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_paths(self, edb_examples):
        """Evaluate modeler paths"""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert len(edbapp.modeler.paths) > 0
        path = edbapp.modeler.paths[0]
        # TODO check for dotnet primitive.type returning only small letters.
        assert path.type.lower() == "path"
        assert path.clone()
        assert isinstance(path.width, float)
        path.width = "1mm"
        assert path.width == 0.001
        assert edbapp.modeler["line_167"].type.lower() == "path"
        assert edbapp.modeler["poly_3022"].type.lower() == "polygon"
        line_number = len(edbapp.modeler.primitives)
        edbapp.modeler["line_167"].delete()
        assert edbapp.modeler.primitives
        assert line_number == len(edbapp.modeler.primitives) + 1
        assert edbapp.modeler["poly_3022"].type.lower() == "polygon"
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_primitives_by_layer(self, edb_examples):
        """Evaluate modeler primitives by layer"""
        # Done
        edbapp = edb_examples.get_si_verse()
        primmitive = edbapp.modeler.primitives_by_layer["1_Top"][0]
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

    def test_modeler_primitives(self, edb_examples):
        """Evaluate modeler primitives"""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert len(edbapp.modeler.rectangles) > 0
        assert len(edbapp.modeler.circles) > 0
        assert len(edbapp.layout.bondwires) == 0
        assert "1_Top" in edbapp.modeler.polygons_by_layer.keys()
        assert len(edbapp.modeler.polygons_by_layer["1_Top"]) > 0
        assert len(edbapp.modeler.polygons_by_layer["DE1"]) == 0
        assert edbapp.modeler.rectangles[0].type.lower() == "rectangle"
        assert edbapp.modeler.circles[0].type.lower() == "circle"
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_get_polygons_bounding(self, edb_examples):
        """Retrieve polygons bounding box."""
        # Done
        edbapp = edb_examples.get_si_verse()
        polys = edbapp.modeler.get_polygons_by_layer("GND")
        for poly in polys:
            bounding = edbapp.modeler.get_polygon_bounding_box(poly)
            assert len(bounding) == 4
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_get_polygons_by_layer_and_nets(self, edb_examples):
        """Retrieve polygons by layer and nets."""
        # Done
        edbapp = edb_examples.get_si_verse()
        nets = ["GND", "1V0"]
        polys = edbapp.modeler.get_polygons_by_layer("16_Bottom", nets)
        assert polys
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_get_polygons_points(self, edb_examples):
        """Retrieve polygons points."""
        # Done
        edbapp = edb_examples.get_si_verse()
        polys = edbapp.modeler.get_polygons_by_layer("GND")
        for poly in polys:
            points = edbapp.modeler.get_polygon_points(poly)
            assert points
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_polygon(self, edb_examples):
        """Create a polygon based on a shape or points."""
        edbapp = edb_examples.get_si_verse()
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

    def test_modeler_create_polygon_from_shape(self, edb_examples):
        """Create polygon from shape."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.modeler.create_polygon(
            points=[[0.0, 0.0], [0.0, 10e-3], [10e-3, 10e-3], [10e-3, 0]], layer_name="1_Top", net_name="test"
        )
        poly_test = [poly for poly in edbapp.modeler.polygons if poly.net_name == "test"]
        assert len(poly_test) == 1
        assert poly_test[0].center == [0.005, 0.005]
        assert poly_test[0].bbox == [0.0, 0.0, 0.01, 0.01]
        assert poly_test[0].move_layer("16_Bottom")
        poly_test = [poly for poly in edbapp.modeler.polygons if poly.net_name == "test"]
        assert len(poly_test) == 1
        assert poly_test[0].layer_name == "16_Bottom"
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_trace(self, edb_examples):
        """Create a trace based on a list of points."""
        # Done
        edbapp = edb_examples.get_si_verse()
        points = [
            [-0.025, -0.02],
            [0.025, -0.02],
            [0.025, 0.02],
        ]
        trace = edbapp.modeler.create_trace(points, "1_Top")
        trace.aedt_name
        assert trace
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

    def test_modeler_add_void(self, edb_examples):
        """Add a void into a shape."""
        # Done
        edbapp = edb_examples.get_si_verse()
        plane_shape = edbapp.modeler.create_rectangle(
            lower_left_point=["-5mm", "-5mm"], upper_right_point=["5mm", "5mm"], layer_name="1_Top"
        )
        plane = edbapp.modeler.create_polygon(plane_shape.polygon_data, "1_Top", net_name="GND")
        void = edbapp.modeler.create_trace(path_list=[["0", "0"], ["0", "1mm"]], layer_name="1_Top", width="0.1mm")
        assert edbapp.modeler.add_void(plane, void)
        plane.add_void(void)
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_fix_circle_void(self, edb_examples):
        """Fix issues when circle void are clipped due to a bug in EDB."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.modeler.fix_circle_void_for_clipping()
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_primitives_area(self, edb_examples):
        """Access primitives total area."""
        # Done
        edbapp = edb_examples.get_si_verse()
        i = 0
        while i < 2:
            prim = edbapp.modeler.primitives[i]
            assert prim.area(True) > 0
            i += 1
        assert prim.bbox
        assert prim.center
        # TODO check bug #455
        # assert prim.get_closest_point((0, 0))
        assert prim.polygon_data
        assert edbapp.modeler.paths[0].length
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_create_rectangle(self, edb_examples):
        """Create rectangle."""
        # Done
        edbapp = edb_examples.get_si_verse()
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

    def test_modeler_create_circle(self, edb_examples):
        """Create circle."""
        # Done
        edbapp = edb_examples.get_si_verse()
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

    def test_modeler_defeature(self, edb_examples):
        """Defeature the polygon."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.modeler.defeature_polygon(edbapp.modeler.primitives_by_net["GND"][-1], 0.0001)
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_primitives_boolean_operation(self, edb_examples):
        """Evaluate modeler primitives boolean operations."""
        # TODO check bug #464.
        edb = edb_examples.create_empty_edb()
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

    def test_modeler_path_convert_to_polygon(self, edb_examples):
        # Done
        target_path = os.path.join(local_path, "example_models", "convert_and_merge_path.aedb")
        edbapp = edb_examples.load_edb(target_path)
        for path in edbapp.modeler.paths:
            assert path.convert_to_polygon()
        # cannot merge one net only - see test: test_unite_polygon for reference
        edbapp.close(terminate_rpc_session=False)

    def test_156_check_path_length(self, edb_examples):
        """"""
        # Done
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_path_length.aedb")
        edbapp = edb_examples.load_edb(edb_path=source_path)
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

    def test_duplicate(self, edb_examples):
        # Done
        edbapp = edb_examples.create_empty_edb()
        edbapp["$H"] = "0.65mil"
        assert edbapp["$H"] == 1.651e-5
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
        assert edbapp.modeler.primitives[0].duplicate_across_layers(lay_list)
        assert edbapp.modeler.primitives_by_layer["mid_gnd"]
        assert edbapp.modeler.primitives_by_layer["bot_gnd"]
        edbapp.close(terminate_rpc_session=False)

    def test_unite_polygon(self, edb_examples):
        # Done
        edbapp = edb_examples.create_empty_edb()
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

    def test_layer_name(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.modeler.polygons[50].layer_name == "1_Top"
        edbapp.modeler.polygons[50].layer_name = "16_Bottom"
        assert edbapp.modeler.polygons[50].layer_name == "16_Bottom"
        edbapp.close(terminate_rpc_session=False)

    def test_287_circuit_ports(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        cap = edbapp.components.capacitors["C1"]
        assert edbapp.siwave.create_circuit_port_on_pin(pos_pin=cap.pins["1"], neg_pin=cap.pins["2"])
        assert edbapp.components.capacitors["C3"].pins
        assert edbapp.padstacks.pins
        edbapp.close(terminate_rpc_session=False)

    def test_get_primitives_by_point_layer_and_nets(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        primitives = edbapp.modeler.get_primitive_by_layer_and_point(layer="Inner1(GND1)", point=[20e-3, 30e-3])
        assert primitives
        assert len(primitives) == 1
        assert primitives[0].type.lower() == "polygon"
        primitives = edbapp.modeler.get_primitive_by_layer_and_point(point=[20e-3, 30e-3])
        assert len(primitives) == 3
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="This test fails randomly, needs to be fixed.")
    def test_arbitrary_wave_ports(self, edb_examples):
        # Done
        example_folder = os.path.join(local_path, "example_models", test_subfolder)
        source_path_edb = os.path.join(example_folder, "example_arbitrary_wave_ports.aedb")
        temp_directory = os.path.join(self.local_scratch.path, "test_wave_ports")
        target_path_edb = os.path.join(temp_directory, "test.aedb")
        work_dir = os.path.join(temp_directory, "_work")
        output_edb = os.path.join(temp_directory, "wave_ports.aedb")
        self.local_scratch.copyfolder(source_path_edb, target_path_edb)
        edbapp = edb_examples.load_edb(edb_path=target_path_edb, copy_to_temp=False)
        assert edbapp.create_model_for_arbitrary_wave_ports(
            temp_directory=work_dir,
            output_edb=output_edb,
            mounting_side="top",
        )
        edbapp.close(terminate_rpc_session=False)
        test_edb = edb_examples.load_edb(edb_path=output_edb, copy_to_temp=False)
        assert len(list(test_edb.nets.signal.keys())) == 13
        assert len(list(test_edb.stackup.layers.keys())) == 3
        assert "ref" in test_edb.stackup.layers
        assert len(test_edb.modeler.polygons) == 12
        test_edb.close(terminate_rpc_session=False)

    def test_path_center_line(self, edb_examples):
        edb = edb_examples.create_empty_edb()
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

    def test_polygon_data_refactoring_bounding_box(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        poly_with_voids = [pp for pp in edbapp.modeler.polygons if pp.has_voids]
        for poly in poly_with_voids:
            for void in poly.voids:
                assert void.bbox
        edbapp.close(terminate_rpc_session=False)

    def test_aedt_name(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        primitives = edbapp.modeler.primitives
        assert primitives[0].aedt_name == "line_0"

    def test_insert_layout_instance(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edb2_path = edb_examples.get_package(edbapp=False)
        edbapp.copy_cell_from_edb(edb2_path)
        cell_inst = edbapp.modeler.insert_layout_instance("analysis", "1_Top", 2, "180deg", "1mm", "2mm", True)
        assert cell_inst.transform.rotation.value == pytest.approx(3.14159265358979)
        assert cell_inst.transform.scale.value == pytest.approx(2)
        assert cell_inst.transform.offset_x.value == pytest.approx(0.001)
        assert cell_inst.transform.offset_y.value == pytest.approx(0.002)
        assert cell_inst.transform.mirror
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config.get("use_grpc"), reason="bug in dotnet core")
    def test_insert_3d_component_placement_3d(self, edb_examples):
        edbapp = edb_examples.get_si_board(additional_files_folders=["si_board/SMA.a3dcomp"])
        cell_inst_1 = edbapp.modeler.insert_3d_component_placement_3d(
            a3dcomp_path=Path(edbapp.edbpath).with_name("SMA.a3dcomp"),
            x="1mm",
            y="2mm",
            z="3mm",
            rotation_x="180deg",
        )
        assert cell_inst_1.transform3d.shift.x.value == pytest.approx(0.001)
        assert cell_inst_1.transform3d.shift.y.value == pytest.approx(0.002)
        assert cell_inst_1.transform3d.shift.z.value == pytest.approx(0.003)
        edbapp.close(terminate_rpc_session=False)
