"""Tests related to Edb modeler
"""

import pytest

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
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
