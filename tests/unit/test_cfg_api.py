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

from pyedb.configuration.cfg_spice_models import CfgSpiceModel, CfgSpiceModels

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestCfgSpiceModel:
    def test_basic(self):
        s = CfgSpiceModel(name="ic_spice", component_definition="IC_U1", file_path="/ic.sp")
        assert s.name == "ic_spice"
        assert s.component_definition == "IC_U1"
        assert s.apply_to_all is True

    def test_sub_circuit(self):
        s = CfgSpiceModel(name="ic", component_definition="IC_DEF", file_path="ic.sp", sub_circuit_name="IC_SUB")
        assert s.sub_circuit_name == "IC_SUB"

    def test_components_list(self):
        s = CfgSpiceModel(name="ic", component_definition="DEF", file_path="ic.sp", apply_to_all=False, components=["U1", "U2"])
        assert s.apply_to_all is False
        assert s.components == ["U1", "U2"]

    def test_terminal_pairs(self):
        s = CfgSpiceModel(name="ic", component_definition="DEF", file_path="ic.sp", terminal_pairs=[["1", "2"]])
        assert s.terminal_pairs == [["1", "2"]]

    def test_components_string_coerced_to_list(self):
        s = CfgSpiceModel(name="ic", component_definition="DEF", file_path="ic.sp", components="U1")
        assert s.components == ["U1"]

    def test_defaults(self):
        s = CfgSpiceModel(name="ic", component_definition="DEF", file_path="ic.sp")
        assert s.sub_circuit_name == ""
        assert s.components == []
        assert s.terminal_pairs is None


class TestCfgSpiceModels:
    def test_empty(self):
        sc = CfgSpiceModels()
        assert sc.models == []

    def test_add(self):
        sc = CfgSpiceModels()
        m = sc.add(name="sp1", component_definition="DEF", file_path="f.sp")
        assert isinstance(m, CfgSpiceModel)
        assert sc.models[0].name == "sp1"

    def test_add_all_params(self):
        sc = CfgSpiceModels()
        m = sc.add(name="sp1", component_definition="DEF", file_path="f.sp", sub_circuit_name="SUB", apply_to_all=False, components=["U1"], terminal_pairs=[["1", "2"]])
        assert m.sub_circuit_name == "SUB"
        assert m.apply_to_all is False
        assert m.components == ["U1"]
        assert m.terminal_pairs == [["1", "2"]]

    def test_add_multiple(self):
        sc = CfgSpiceModels()
        sc.add(name="sp1", component_definition="DEF1", file_path="f1.sp")
        sc.add(name="sp2", component_definition="DEF2", file_path="f2.sp")
        assert len(sc.models) == 2
        assert sc.models[1].name == "sp2"

    def test_init_with_data(self):
        sc = CfgSpiceModels(data=[{"name": "m1", "component_definition": "DEF", "file_path": "f.sp"}])
        assert len(sc.models) == 1
        assert sc.models[0].name == "m1"
