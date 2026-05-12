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

from pyedb.configuration.cfg_modeler import CfgModeler

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestModelerConfig:
    def test_empty(self):
        assert CfgModeler().to_dict() == {}

    def test_add_trace(self):
        m = CfgModeler()
        m.add_trace("t1", "top", "0.15mm", net_name="SIG1", path=[[0, 0], [0.01, 0]])
        d = m.to_dict()
        assert len(d["traces"]) == 1
        t = d["traces"][0]
        assert t["name"] == "t1"
        assert t["layer"] == "top"
        assert t["width"] == "0.15mm"
        assert t["net_name"] == "SIG1"

    def test_add_rectangular_plane(self):
        m = CfgModeler()
        m.add_rectangular_plane(
            "GND_L", "gnd_rect", "GND", lower_left_point=[-0.05, -0.05], upper_right_point=[0.05, 0.05]
        )
        d = m.to_dict()
        plane = d["planes"][0]
        assert plane["type"] == "rectangle"
        assert plane["net_name"] == "GND"

    def test_add_circular_plane(self):
        m = CfgModeler()
        m.add_circular_plane("L1", "circle1", "GND", radius="0.5mm", position=[0.01, 0.02])
        d = m.to_dict()
        assert d["planes"][0]["type"] == "circle"
        assert d["planes"][0]["radius"] == "0.5mm"

    def test_add_polygon_plane(self):
        m = CfgModeler()
        m.add_polygon_plane("L2", "poly1", "VDD", points=[[0, 0], [0.01, 0], [0.01, 0.01], [0, 0.01]])
        d = m.to_dict()
        assert d["planes"][0]["type"] == "polygon"
        assert len(d["planes"][0]["points"]) == 4

    def test_delete_primitives_by_layer(self):
        m = CfgModeler()
        m.delete_primitives_by_layer(["old_layer1", "old_layer2"])
        d = m.to_dict()
        assert d["primitives_to_delete"]["layer_name"] == ["old_layer1", "old_layer2"]

    def test_delete_primitives_by_name(self):
        m = CfgModeler()
        m.delete_primitives_by_name(["prim1", "prim2"])
        assert m.to_dict()["primitives_to_delete"]["name"] == ["prim1", "prim2"]

    def test_delete_primitives_by_net(self):
        m = CfgModeler()
        m.delete_primitives_by_net(["old_net"])
        assert m.to_dict()["primitives_to_delete"]["net_name"] == ["old_net"]
