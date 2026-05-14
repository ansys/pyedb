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

from pyedb.configuration.cfg_s_parameter_models import CfgSParameterModel, CfgSParameters

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]

class TestCfgSParameterModel:
    def test_basic(self):
        m = CfgSParameterModel(name="model1", component_definition="CAP_100nF", file_path="/path/c.s2p")
        d = m.model_dump()
        assert d["name"] == "model1"
        assert d["component_definition"] == "CAP_100nF"
        assert d["file_path"] == "/path/c.s2p"
        assert d["apply_to_all"] is True

    def test_with_components(self):
        m = CfgSParameterModel(
            name="m1", component_definition="DEF", file_path="f.s2p", apply_to_all=False, components=["C1", "C2"]
        )
        d = m.model_dump()
        assert d["apply_to_all"] is False
        assert d["components"] == ["C1", "C2"]

    def test_reference_net_per_component(self):
        m = CfgSParameterModel(
            name="m1", component_definition="DEF", file_path="f.s2p", reference_net_per_component={"C1": "GND1"}
        )
        d = m.model_dump()
        assert d["reference_net_per_component"] == {"C1": "GND1"}

    def test_pin_order(self):
        m = CfgSParameterModel(name="m1", component_definition="DEF", file_path="f.s2p", pin_order=["1", "2"])
        assert m.model_dump()["pin_order"] == ["1", "2"]

    def test_pin_order_none_by_default(self):
        m = CfgSParameterModel(name="m1", component_definition="DEF", file_path="f.s2p")
        assert m.model_dump()["pin_order"] is None


class TestCfgSParameters:
    def test_empty(self):
        sc = CfgSParameters()
        assert sc.models == []

    def test_add(self):
        sc = CfgSParameters()
        m = sc.add("model1", "CAP", "f.s2p")
        assert isinstance(m, CfgSParameterModel)
        assert sc.models[0].name == "model1"

    def test_add_returns_model_with_correct_fields(self):
        sc = CfgSParameters()
        m = sc.add("m1", "DEF", "f.s2p", reference_net="GND", apply_to_all=False, components=["C1"])
        assert m.reference_net == "GND"
        assert m.apply_to_all is False
        assert m.components == ["C1"]

    def test_get_data_from_db_no_pedb(self):
        sc = CfgSParameters()
        sc.add("m1", "DEF", "f.s2p")
        result = sc.get_data_from_db([])
        assert isinstance(result, list)
        assert result[0]["name"] == "m1"
