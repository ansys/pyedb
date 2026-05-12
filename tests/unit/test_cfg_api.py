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

from pyedb.configuration.cfg_padstacks import CfgPadstackDefinition, CfgPadstackInstance, CfgPadstacks

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestPadstackDefinitionConfig:
    def test_minimal(self):
        p = CfgPadstackDefinition(name="via_0.2")
        d = p.to_dict()
        assert d == {"name": "via_0.2"}

    def test_with_properties(self):
        p = CfgPadstackDefinition(name="via", hole_plating_thickness="25um", material="copper")
        d = p.to_dict()
        assert d["hole_plating_thickness"] == "25um"
        assert d["material"] == "copper"

    def test_all_explicit_params(self):
        """All CfgPadstackDefinition fields are explicit — no **kwargs."""
        p = CfgPadstackDefinition(
            name="via_full",
            hole_plating_thickness="25um",
            material="copper",
            hole_range="upper_pad_to_lower_pad",
            pad_parameters={"pad_type": "circle"},
            hole_parameters={"shape": "circle"},
            solder_ball_parameters={"diameter": "150um"},
        )
        d = p.to_dict()
        assert d["hole_range"] == "upper_pad_to_lower_pad"
        assert d["pad_parameters"]["pad_type"] == "circle"
        assert d["solder_ball_parameters"]["diameter"] == "150um"


class TestPadstackInstanceConfig:
    def test_minimal(self):
        inst = CfgPadstackInstance(name="via_1", net_name="GND")
        d = inst.to_dict()
        assert d["name"] == "via_1"
        assert d["net_name"] == "GND"

    def test_layer_range(self):
        inst = CfgPadstackInstance(layer_range=["top", "bot"])
        d = inst.to_dict()
        assert d["layer_range"] == ["top", "bot"]

    def test_all_explicit_params(self):
        """All CfgPadstackInstance fields are explicit — no **kwargs."""
        inst = CfgPadstackInstance(
            name="v2",
            net_name="SIG",
            definition="via_0.2",
            layer_range=["top", "L2"],
            position=[0.001, 0.002],
            rotation=45,
            is_pin=False,
            hole_override_enabled=True,
            hole_override_diameter="0.22mm",
            solder_ball_layer="top",
        )
        d = inst.to_dict()
        assert d["definition"] == "via_0.2"
        assert d["hole_override_enabled"] is True
        assert d["hole_override_diameter"] == "0.22mm"
        assert d["solder_ball_layer"] == "top"

    def test_backdrill(self):
        inst = CfgPadstackInstance(name="via_bd")
        inst.set_backdrill("L4", "0.3mm", drill_from_bottom=True)
        d = inst.to_dict()
        assert d["backdrill_parameters"]["from_bottom"]["drill_to_layer"] == "L4"

    def test_backdrill_with_stub(self):
        inst = CfgPadstackInstance(name="via_bd2")
        inst.set_backdrill("L4", "0.3mm", stub_length="0.05mm", drill_from_bottom=False)
        d = inst.to_dict()
        assert "from_top" in d["backdrill_parameters"]
        assert d["backdrill_parameters"]["from_top"]["stub_length"] == "0.05mm"

    def test_backdrill_chaining(self):
        """set_backdrill returns self for method chaining."""
        inst = CfgPadstackInstance(name="via")
        result = inst.set_backdrill("L3", "0.25mm")
        assert result is inst


class TestPadstacksConfig:
    def test_empty(self):
        assert CfgPadstacks().to_dict() == {}

    def test_add_definition(self):
        ps = CfgPadstacks()
        pdef = ps.add_definition("via", material="copper")
        assert isinstance(pdef, CfgPadstackDefinition)
        d = ps.to_dict()
        assert d["definitions"][0]["name"] == "via"

    def test_add_definition_all_params(self):
        ps = CfgPadstacks()
        ps.add_definition(
            "via_full",
            hole_plating_thickness="25um",
            material="copper",
            hole_range="upper_pad_to_lower_pad",
        )
        d = ps.to_dict()["definitions"][0]
        assert d["hole_range"] == "upper_pad_to_lower_pad"

    def test_add_instance(self):
        ps = CfgPadstacks()
        inst = ps.add_instance(name="v1", net_name="SIG1")
        assert isinstance(inst, CfgPadstackInstance)
        d = ps.to_dict()
        assert d["instances"][0]["name"] == "v1"

    def test_add_instance_all_params(self):
        ps = CfgPadstacks()
        ps.add_instance(
            name="v2",
            net_name="GND",
            definition="via_0.2",
            layer_range=["top", "bot"],
            position=[0.001, 0.002],
            rotation=0,
            is_pin=False,
            hole_override_enabled=False,
        )
        d = ps.to_dict()["instances"][0]
        assert d["definition"] == "via_0.2"
        assert d["layer_range"] == ["top", "bot"]
