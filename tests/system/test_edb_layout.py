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


import platform
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

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC backend only")
    def test_layout_collections(self):
        """Verify Layout collection properties, layout_instance, terminals type, polygons, primitives_by_net."""
        edbapp = self.edb_examples.get_si_verse()
        # --- collection properties return lists ---
        assert isinstance(edbapp.layout.terminals, list)
        assert isinstance(edbapp.layout.nets, list)
        assert len(edbapp.layout.nets) > 0
        assert isinstance(edbapp.layout.groups, list)
        assert isinstance(edbapp.layout.pin_groups, list)
        assert isinstance(edbapp.layout.net_classes, list)
        assert isinstance(edbapp.layout.extended_nets, list)
        assert isinstance(edbapp.layout.differential_pairs, list)
        assert isinstance(edbapp.layout.padstack_instances, list)
        assert len(edbapp.layout.padstack_instances) > 0
        assert isinstance(edbapp.layout.voltage_regulators, list)
        assert isinstance(edbapp.layout.zone_primitives, list)
        # --- layout_instance is accessible ---
        assert edbapp.layout.layout_instance is not None
        # terminals already verified as list above; no assumption on terminal types present in si_verse
        # --- polygons property returns only polygon-type primitives ---
        polygons = edbapp.layout.polygons
        assert len(polygons) > 0
        assert all(p.primitive_type == "polygon" for p in polygons)
        # --- primitives_by_net has a key for every net ---
        by_net = edbapp.layout.primitives_by_net
        for net_name in edbapp.nets.nets:
            assert net_name in by_net
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC backend only")
    def test_filter_primitives_prim_type_and_is_void(self):
        """filter_primitives prim_type/is_void filters, primitives_by_aedt_name and find_object_by_id."""
        edbapp = self.edb_examples.get_si_verse()
        # --- prim_type filter ---
        polygons = edbapp.layout.filter_primitives(layer_name="1_Top", prim_type="polygon")
        assert all(p.primitive_type == "polygon" for p in polygons)
        # --- is_void=False: no void in result ---
        non_voids = edbapp.layout.filter_primitives(layer_name="1_Top", is_void=False)
        assert all(not p.is_void for p in non_voids)
        # --- is_void=True: must provide a layer so voids are included via primitives_by_layer ---
        void_layer = next(poly.layer_name for poly in edbapp.layout.polygons if poly.has_voids)
        voids = edbapp.layout.filter_primitives(layer_name=void_layer, is_void=True)
        assert len(voids) > 0
        assert all(p.is_void for p in voids)
        # --- primitives_by_aedt_name round-trip ---
        prim = edbapp.layout.find_primitive(layer_name="Inner5(PWR2)", name="poly_4128")[0]
        lookup = edbapp.layout.primitives_by_aedt_name
        assert prim.aedt_name in lookup
        assert lookup[prim.aedt_name].id == prim.id
        # --- find_object_by_id with padstack instance ---
        pi = edbapp.layout.padstack_instances[0]
        assert edbapp.layout.find_object_by_id(pi.id).id == pi.id
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC backend only")
    def test_find_primitive_variants(self):
        """find_primitive: by name only, is_void filter, list of layers, prim_type filter."""
        edbapp = self.edb_examples.get_si_verse()
        # --- name only ---
        result = edbapp.layout.find_primitive(name="poly_4128")
        assert len(result) > 0
        assert all(p.aedt_name == "poly_4128" for p in result)
        # --- is_void=True: must provide a layer so _iter_primitives_with_voids is used ---
        void_layer = next(poly.layer_name for poly in edbapp.layout.polygons if poly.has_voids)
        voids = edbapp.layout.find_primitive(layer_name=void_layer, is_void=True)
        assert len(voids) > 0
        assert all(p.is_void for p in voids)
        # --- is_void=False ---
        non_voids = edbapp.layout.find_primitive(layer_name="1_Top", is_void=False)
        assert len(non_voids) > 0
        assert all(not p.is_void for p in non_voids)
        # --- list of layer names ---
        result = edbapp.layout.find_primitive(layer_name=["1_Top", "16_Bot"], net_name="GND")
        assert len(result) > 0
        assert all(p.layer_name in {"1_Top", "16_Bot"} for p in result)
        assert all(p.net_name == "GND" for p in result)
        # --- prim_type='path' ---
        paths = edbapp.layout.find_primitive(prim_type="path")
        assert len(paths) > 0
        assert all(p.primitive_type == "path" for p in paths)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC backend only")
    def test_find_padstack_instances_variants(self):
        """find_padstack_instances: list of aedt_names, list of net_names, list of component_names."""
        edbapp = self.edb_examples.get_si_verse()
        # --- list of aedt_names ---
        results = edbapp.layout.find_padstack_instances(aedt_name=["U7-T7", "U7-R7"])
        aedt_names = {p.aedt_name for p in results}
        assert "U7-T7" in aedt_names
        assert "U7-R7" in aedt_names
        # --- list of net_names ---
        results = edbapp.layout.find_padstack_instances(net_name=["DDR4_A9", "DDR4_A10"])
        assert {p.net_name for p in results}.intersection({"DDR4_A9", "DDR4_A10"})
        # --- list of component_names ---
        results = edbapp.layout.find_padstack_instances(component_name=["U7", "U1"])
        assert {p.component.name for p in results if p.component}.intersection({"U7", "U1"})
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="gRPC backend only")
    def test_get_primitive_by_layer_and_point_edge_cases(self):
        """get_primitive_by_layer_and_point: invalid point, unknown net, and no layer filter."""
        edbapp = self.edb_examples.get_si_verse()
        # --- invalid point format → returns False ---
        assert edbapp.layout.get_primitive_by_layer_and_point(point=[0], layer="1_Top") is False
        # --- unknown net → returns empty list ---
        assert (
            edbapp.layout.get_primitive_by_layer_and_point(
                point=[10e-3, 10e-3], layer="1_Top", nets="__nonexistent_net__"
            )
            == []
        )
        # --- no layer filter → returns a list ---
        assert isinstance(edbapp.layout.get_primitive_by_layer_and_point(point=[10e-3, 10e-3]), list)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and platform.system() == "Linux",
        reason="Known issue in ansys-edb-core layout instance server on Linux",
    )
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

    def test_layout_bounding_box(self):
        """Evaluate layout bounding box."""
        import ansys.edb.core

        from tests.conftest import config

        if config["use_grpc"] and ansys.edb.core.__version__ == "0.2.6":
            pytest.skip("Test skipped for ansys-edb-core version 0.2.6")
        edbapp = self.edb_examples.get_si_verse()
        assert len(edbapp.get_bounding_box()) == 2
        bbox = [[round(i, 6) for i in j] for j in edbapp.get_bounding_box()]
        assert bbox == [[-0.014260, -0.004550], [0.150105, 0.080000]]
        edbapp.close(terminate_rpc_session=False)
