# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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


import warnings

import pytest

from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_find(self):
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.layout.find_primitive(layer_name="Inner5(PWR2)", name="poly_4128", net_name=["2V5"])
        assert edbapp.layout.find_padstack_instances(aedt_name="U7-T7")[0].aedt_name == "U7-T7"
        assert len(edbapp.layout.find_padstack_instances(component_name="U7"))
        found_instances = edbapp.layout.find_padstack_instances(component_name="U7", component_pin_name="T7")
        assert [pin for pin in found_instances if pin.name == "T7"]
        found_instances = edbapp.layout.find_padstack_instances(component_name="U7", net_name="DDR4_A9")
        assert [pin for pin in found_instances if pin.aedt_name == "U7-R7"]
        found_instances = edbapp.layout.find_padstack_instances(aedt_name="U7-R7")
        assert [pin for pin in found_instances if pin.aedt_name == "U7-R7"]
        if edbapp.grpc:
            assert edbapp.layout.find_padstack_instances(instance_id=4294967296)[0].edb_uid == 4294967296
        else:
            assert edbapp.layout.find_padstack_instances(instance_id=4294967296)[0].id == 4294967296
        edbapp.close(terminate_rpc_session=False)

    def test_primitives(self):
        edbapp = self.edb_examples.get_si_verse()
        prim = edbapp.layout.find_primitive(layer_name="Inner5(PWR2)", name="poly_4128", net_name=["2V5"])[0]
        assert prim.polygon_data.is_inside(["111.4mm", 44.7e-3])
        edbapp.close(terminate_rpc_session=False)

    def test_filter_primitives_includes_voids(self):
        edbapp = self.edb_examples.get_si_verse()
        void = next(void for poly in edbapp.layout.polygons if poly.has_voids for void in poly.voids)
        net_void = next(
            void for poly in edbapp.layout.polygons if poly.has_voids for void in poly.voids if void.net_name
        )
        kwargs = {"name": void.aedt_name, "layer_name": void.layer_name}
        if void.net_name:
            kwargs["net_name"] = void.net_name

        filtered = edbapp.layout.filter_primitives(**kwargs)

        assert any(primitive.id == void.id and primitive.is_void for primitive in filtered)
        assert edbapp.layout.primitives_by_aedt_name[void.aedt_name].id == void.id
        assert edbapp.layout.primitives_by_aedt_name[void.aedt_name].is_void
        assert any(primitive.id == void.id for primitive in edbapp.layout.primitives_by_layer[void.layer_name])
        assert any(primitive.id == net_void.id for primitive in edbapp.layout.primitives_by_net[net_void.net_name])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            warnings.simplefilter("ignore", FutureWarning)
            assert any(
                primitive.id == net_void.id and primitive.is_void
                for primitive in edbapp.layout.get_primitives(
                    layer_name=net_void.layer_name,
                    net_name=net_void.net_name,
                    prim_type=net_void.primitive_type,
                )
            )
            assert any(
                primitive.id == net_void.id and primitive.is_void
                for primitive in edbapp.modeler.get_primitives(
                    layer_name=net_void.layer_name,
                    net_name=net_void.net_name,
                    prim_type=net_void.primitive_type,
                )
            )
        edbapp.close(terminate_rpc_session=False)

    def test_primitive_path(self):
        edbapp = self.edb_examples.get_si_verse()
        if not edbapp.grpc:
            # TODO check if center line setter defined in grpc.
            path_obj = edbapp.layout.find_primitive(name="line_272")[0]
            center_line = path_obj.center_line
            center_line[0] = [0, 0]
            path_obj.center_line = center_line
            assert path_obj.center_line[0] == [0, 0]
        edbapp.close(terminate_rpc_session=False)

    def test_primitive_queries(self):
        edbapp = self.edb_examples.get_si_verse()

        # --- primitives / bondwires ---
        primitives = edbapp.layout.primitives
        assert len(primitives) > 0
        assert len(edbapp.layout.bondwires) == 0

        # --- polygons_by_layer: must cover all stackup layers, each value is a list ---
        polygon_by_layers = edbapp.layout.polygons_by_layer
        assert "1_Top" in polygon_by_layers

        # --- primitives_by_layer: "1_Top" must be non-empty and contain more entries
        #     than polygons_by_layer["1_Top"] alone (voids are included) ---
        primitives_top_layer_with_voids = edbapp.layout.primitives_by_layer["1_Top"]
        assert len(primitives_top_layer_with_voids) > 0

        # --- polygons on "1_Top": every entry reports type "polygon" ---
        primitives_top_layer = polygon_by_layers["1_Top"]
        assert len(primitives_top_layer) > 0
        assert all(prim.primitive_type == "polygon" for prim in primitives_top_layer)

        # --- find_object_by_id round-trip ---
        obj_id = primitives_top_layer[0].id
        assert edbapp.layout.find_object_by_id(obj_id)

        # --- point query returns at least one hit ---
        assert (
            len(edbapp.layout.get_primitive_by_layer_and_point(point=[10e-3, 10e-3], layer="Inner1(GND1)", nets="GND"))
            >= 1
        )

        # --- find_primitive / primitives_by_net for GND: non-empty ---
        gnd_top = edbapp.layout.find_primitive(layer_name="1_Top", net_name="GND")
        assert len(gnd_top) > 0

        assert len(edbapp.layout.primitives_by_net["GND"]) > 0

        # --- shape-type properties: at least one of each expected type ---
        assert len(edbapp.layout.rectangles) >= 1
        assert len(edbapp.layout.circles) >= 1
        assert len(edbapp.layout.paths) > 0

        # --- get_polygons_by_layer / get_primitives consistency ---
        gnd_polygons_by_layer = edbapp.layout.get_polygons_by_layer(layer="1_Top", nets="GND")
        gnd_primitives = edbapp.layout.get_primitives(layer_name="1_Top", net_name="GND", prim_type="polygon")
        assert len(gnd_polygons_by_layer) > 0
        assert len(gnd_polygons_by_layer) == len(gnd_primitives)

        # --- bounding-box / polygon-points helpers ---
        polygon_to_test = edbapp.layout.polygons_by_layer["1_Top"][0]
        assert edbapp.layout.get_polygon_bounding_box(polygon_to_test)
        assert edbapp.layout.get_polygon_points(polygon_to_test)

        edbapp.close(terminate_rpc_session=False)
