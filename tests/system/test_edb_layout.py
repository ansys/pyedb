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


import pytest

from tests.conftest import config, use_grpc
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    @pytest.mark.skipif(
        config["use_grpc"] and config["desktopVersion"] < "2026.1",
        reason="This test is failing in grpc. To be validated in 26R1.",
    )
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

    @pytest.mark.skipif(use_grpc, reason="Not yet implemented in grpc. Waiting for DotNet validation first")
    def test_primitive_queries(self):
        edbapp = self.edb_examples.get_si_verse()
        assert len(edbapp.layout.primitives) == 2111
        assert len(edbapp.layout.bondwires) == 0
        polygon_by_layers = edbapp.layout.polygons_by_layer
        assert len(polygon_by_layers) == 19
        assert len(edbapp.layout.primitives_by_layer["1_Top"]) == 1232
        assert len(edbapp.layout.polygons_by_layer) == 19
        primitives_top_layer = polygon_by_layers["1_Top"]
        assert len(primitives_top_layer) == 134
        assert len([prim for prim in primitives_top_layer if prim.primitive_type == "polygon"]) == len(
            primitives_top_layer
        )
        obj_id = primitives_top_layer[0].id
        assert edbapp.layout.find_object_by_id(obj_id)
        assert (
            len(edbapp.layout.get_primitive_by_layer_and_point(point=[10e-3, 10e-3], layer="Inner1(GND1)", nets="GND"))
            == 1
        )
        assert len(edbapp.layout.find_primitive(layer_name="1_Top", net_name="GND")) == 383
        assert len(edbapp.layout.primitives_by_net["GND"]) == 446
        assert len(edbapp.layout.rectangles) == 1
        assert len(edbapp.layout.circles) == 1
        assert len(edbapp.layout.paths) == 1839
        assert len(edbapp.layout.get_polygons_by_layer(layer="1_Top", nets="GND")) == 24
        polygon_to_test = edbapp.layout.polygons_by_layer["1_Top"][0]
        assert edbapp.layout.get_polygon_bounding_box(polygon_to_test)
        assert edbapp.layout.get_polygon_points(polygon_to_test)
        assert len(edbapp.layout.get_primitives(layer_name="1_Top", net_name="GND", prim_type="polygon")) == 24
        edbapp.close(terminate_rpc_session=False)
