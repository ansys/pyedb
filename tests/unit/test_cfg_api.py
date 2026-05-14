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

from pyedb.configuration.cfg_modeler import CfgModeler, CfgPlane, CfgTrace

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestModelerConfig:
    def test_empty(self):
        m = CfgModeler()
        assert m.traces == []
        assert m.planes == []

    def test_add_trace(self):
        m = CfgModeler()
        m.add_trace("t1", "top", "0.15mm", net_name="SIG1", path=[[0, 0], [0.01, 0]])
        assert len(m.traces) == 1
        t = m.traces[0]
        assert t.name == "t1"
        assert t.layer == "top"
        assert t.width == "0.15mm"
        assert t.net_name == "SIG1"

    def test_add_rectangular_plane(self):
        m = CfgModeler()
        m.add_rectangular_plane(
            "GND_L", "gnd_rect", "GND", lower_left_point=[-0.05, -0.05], upper_right_point=[0.05, 0.05]
        )
        plane = m.planes[0]
        assert plane.type == "rectangle"
        assert plane.net_name == "GND"

    def test_add_circular_plane(self):
        m = CfgModeler()
        m.add_circular_plane("L1", "circle1", "GND", radius="0.5mm", position=[0.01, 0.02])
        assert m.planes[0].type == "circle"
        assert m.planes[0].radius == "0.5mm"

    def test_add_polygon_plane(self):
        m = CfgModeler()
        m.add_polygon_plane("L2", "poly1", "VDD", points=[[0, 0], [0.01, 0], [0.01, 0.01], [0, 0.01]])
        assert m.planes[0].type == "polygon"
        assert len(m.planes[0].points) == 4

    def test_delete_primitives_by_layer(self):
        m = CfgModeler()
        m.delete_primitives_by_layer(["old_layer1", "old_layer2"])
        assert m.primitives_to_delete["layer_name"] == ["old_layer1", "old_layer2"]

    def test_delete_primitives_by_name(self):
        m = CfgModeler()
        m.delete_primitives_by_name(["prim1", "prim2"])
        assert m.primitives_to_delete["name"] == ["prim1", "prim2"]

    def test_delete_primitives_by_net(self):
        m = CfgModeler()
        m.delete_primitives_by_net(["old_net"])
        assert m.primitives_to_delete["net_name"] == ["old_net"]

    def test_add_trace_incremental_path(self):
        m = CfgModeler()
        m.add_trace("t2", "bot", "0.1mm", incremental_path=[[0, 0], [0.005, 0]])
        t = m.traces[0]
        assert t.incremental_path == [[0, 0], [0.005, 0]]
        assert t.path == []

    def test_add_trace_default_styles(self):
        m = CfgModeler()
        t = m.add_trace("t3", "top", "0.1mm")
        assert t.start_cap_style == "round"
        assert t.end_cap_style == "round"
        assert t.corner_style == "sharp"

    def test_add_trace_custom_styles(self):
        m = CfgModeler()
        t = m.add_trace("t4", "top", "0.1mm", start_cap_style="flat", end_cap_style="extended", corner_style="mitered")
        assert t.start_cap_style == "flat"
        assert t.end_cap_style == "extended"
        assert t.corner_style == "mitered"

    def test_multiple_traces(self):
        m = CfgModeler()
        m.add_trace("t1", "top", "0.1mm")
        m.add_trace("t2", "bot", "0.2mm")
        assert len(m.traces) == 2
        assert m.traces[1].layer == "bot"

    def test_multiple_planes(self):
        m = CfgModeler()
        m.add_rectangular_plane("L1", "r1", "GND")
        m.add_circular_plane("L2", "c1", "VDD", radius="1mm")
        assert len(m.planes) == 2

    def test_init_from_data_dict_traces(self):
        data = {"traces": [{"name": "t1", "layer": "top", "width": "0.1mm", "path": [[0, 0], [1e-3, 0]]}]}
        m = CfgModeler(data=data)
        assert len(m.traces) == 1
        assert m.traces[0].name == "t1"

    def test_init_from_data_dict_planes(self):
        data = {"planes": [{"name": "p1", "layer": "bot", "net_name": "GND", "type": "rectangle"}]}
        m = CfgModeler(data=data)
        assert len(m.planes) == 1
        assert m.planes[0].net_name == "GND"

    def test_init_from_data_primitives_to_delete(self):
        data = {"primitives_to_delete": {"layer_name": ["L1"], "name": [], "net_name": []}}
        m = CfgModeler(data=data)
        assert m.primitives_to_delete["layer_name"] == ["L1"]

    def test_trace_model_dump(self):
        t = CfgTrace(name="t1", layer="top", width="0.1mm")
        d = t.model_dump()
        assert d["name"] == "t1"
        assert d["width"] == "0.1mm"

    def test_plane_model_dump(self):
        p = CfgPlane(name="p1", layer="top", net_name="GND", type="rectangle")
        d = p.model_dump()
        assert d["type"] == "rectangle"
        assert d["net_name"] == "GND"

    def test_delete_primitives_accumulates(self):
        m = CfgModeler()
        m.delete_primitives_by_layer(["L1"])
        m.delete_primitives_by_layer(["L2"])
        assert m.primitives_to_delete["layer_name"] == ["L1", "L2"]
