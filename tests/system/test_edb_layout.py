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


import pytest

from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestClass(BaseTestClass):
    def test_find(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.layout.find_primitive(layer_name="Inner5(PWR2)", name="poly_4128", net_name=["2V5"])
        assert edbapp.layout.find_padstack_instances(aedt_name="U7-T7")[0].aedt_name == "U7-T7"
        assert len(edbapp.layout.find_padstack_instances(component_name="U7"))
        assert edbapp.layout.find_padstack_instances(component_name="U7", component_pin_name="T7")[0].name == "T7"
        assert edbapp.layout.find_padstack_instances(component_name="U7", net_name="DDR4_A9")[0].aedt_name == "U7-R7"
        assert edbapp.layout.find_padstack_instances(aedt_name="U7-R7")[0].aedt_name == "U7-R7"
        assert edbapp.layout.find_padstack_instances(instance_id=4294967296)[0].id == 4294967296
        edbapp.close(terminate_rpc_session=False)

    def test_primitives(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        prim = edbapp.layout.find_primitive(layer_name="Inner5(PWR2)", name="poly_4128", net_name=["2V5"])[0]
        assert prim.polygon_data.is_inside(["111.4mm", 44.7e-3])
        edbapp.close(terminate_rpc_session=False)

    def test_primitive_path(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        if not edbapp.grpc:
            # TODO check if center line setter defined in grpc.
            path_obj = edbapp.layout.find_primitive(name="line_272")[0]
            center_line = path_obj.center_line
            center_line[0] = [0, 0]
            path_obj.center_line = center_line
            assert path_obj.center_line[0] == [0, 0]
        edbapp.close(terminate_rpc_session=False)
