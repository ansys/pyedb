# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_padstacks import (
    CfgBackdrillParameters,
    CfgPadstackDefinition,
    CfgPadstackInstance,
    CfgPadstacks,
)


class TestCfgPadstackInstanceExtra:
    def test_rotation_coerced_to_string(self):
        inst = CfgPadstackInstance(name="v", rotation=90)
        assert inst.rotation == "90"

    def test_rotation_float_coerced(self):
        inst = CfgPadstackInstance(name="v", rotation=45.5)
        assert inst.rotation == "45.5"

    def test_rotation_none(self):
        inst = CfgPadstackInstance(name="v")
        assert inst.rotation is None

    def test_eid_alias(self):
        """eid field accepts 'id' as alias in dict input."""
        inst = CfgPadstackInstance.model_validate({"name": "v", "id": 42})
        assert inst.eid == 42

    def test_backdrill_default_empty(self):
        inst = CfgPadstackInstance(name="v")
        assert inst.backdrill_parameters is not None
        assert inst.backdrill_parameters.from_top is None
        assert inst.backdrill_parameters.from_bottom is None

    def test_set_backdrill_from_top(self):
        inst = CfgPadstackInstance(name="v")
        inst.set_backdrill("L2", "0.3mm", drill_from_bottom=False)
        assert inst.backdrill_parameters.from_top is not None
        assert inst.backdrill_parameters.from_bottom is None

    def test_set_backdrill_from_bottom(self):
        inst = CfgPadstackInstance(name="v")
        inst.set_backdrill("L5", "0.25mm", drill_from_bottom=True)
        assert inst.backdrill_parameters.from_bottom is not None
        assert inst.backdrill_parameters.from_top is None

    def test_backdrill_excluded_when_empty(self):
        inst = CfgPadstackInstance(name="v", net_name="GND")
        d = inst.model_dump(exclude_none=True)
        # empty backdrill_parameters should not pollute the serialized output
        bd = d.get("backdrill_parameters", {})
        assert bd.get("from_top") is None
        assert bd.get("from_bottom") is None

    def test_id_property(self):
        inst = CfgPadstackInstance(name="v", eid=7)
        assert inst._id == 7

    def test_create_classmethod(self):
        inst = CfgPadstackInstance.create(name="v_created", net_name="SIG")
        assert isinstance(inst, CfgPadstackInstance)
        assert inst.name == "v_created"
        assert inst.backdrill_parameters is not None

    def test_set_backdrill_reinitialises_when_none(self):
        """set_backdrill creates CfgBackdrillParameters if it was None."""
        inst = CfgPadstackInstance(name="v")
        inst.backdrill_parameters = None  # force None
        inst.set_backdrill("L3", "0.25mm")
        assert inst.backdrill_parameters is not None
        assert inst.backdrill_parameters.from_bottom is not None


class TestPadstacksConfig:
    def test_empty(self):
        result = CfgPadstacks().model_dump(exclude_none=True, exclude_defaults=True)
        assert result == {}

    def test_add_definition(self):
        ps = CfgPadstacks()
        pdef = ps.add_definition("via", material="copper")
        assert isinstance(pdef, CfgPadstackDefinition)
        d = ps.model_dump(exclude_none=True)
        assert d["definitions"][0]["name"] == "via"

    def test_add_definition_all_params(self):
        ps = CfgPadstacks()
        ps.add_definition(
            "via_full",
            hole_plating_thickness="25um",
            material="copper",
            hole_range="upper_pad_to_lower_pad",
        )
        d = ps.model_dump(exclude_none=True)["definitions"][0]
        assert d["hole_range"] == "upper_pad_to_lower_pad"

    def test_add_instance(self):
        ps = CfgPadstacks()
        inst = ps.add_instance(name="v1", net_name="SIG1")
        assert isinstance(inst, CfgPadstackInstance)
        d = ps.model_dump(exclude_none=True)
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
        d = ps.model_dump(exclude_none=True)["instances"][0]
        assert d["definition"] == "via_0.2"
        assert d["layer_range"] == ["top", "bot"]

    def test_clean(self):
        ps = CfgPadstacks()
        ps.add_definition("via")
        ps.add_instance(name="v1")
        ps.clean()
        assert ps.definitions == []
        assert ps.instances == []

    def test_add_definition_with_hole_diameter(self):
        ps = CfgPadstacks()
        ps.add_definition("via", hole_diameter="0.2mm", pad_layers=["top", "bot"], pad_diameter="0.5mm")
        d = ps.model_dump(exclude_none=True)["definitions"][0]
        assert d["hole_parameters"]["diameter"] == "0.2mm"
        assert d["hole_parameters"]["shape"] == "circle"
        assert d["pad_parameters"]["regular_pad"][0]["diameter"] == "0.5mm"

    def test_add_definition_with_anti_pad(self):
        ps = CfgPadstacks()
        ps.add_definition(
            "via",
            hole_diameter="0.2mm",
            pad_diameter="0.5mm",
            anti_pad_diameter="0.8mm",
            pad_layers=["top"],
        )
        d = ps.model_dump(exclude_none=True)["definitions"][0]
        assert d["pad_parameters"]["anti_pad"][0]["diameter"] == "0.8mm"

    def test_add_definition_rectangle_pad(self):
        ps = CfgPadstacks()
        ps.add_definition("via", pad_shape="rectangle", pad_x_size="0.5mm", pad_y_size="0.3mm", pad_layers=["top"])
        d = ps.model_dump(exclude_none=True)["definitions"][0]
        pad = d["pad_parameters"]["regular_pad"][0]
        assert pad["shape"] == "rectangle"
        assert pad["x_size"] == "0.5mm"
        assert pad["y_size"] == "0.3mm"

    def test_add_definition_no_layers_no_pad_params(self):
        """No pad_parameters built when pad_diameter not given."""
        ps = CfgPadstacks()
        ps.add_definition("via", material="copper")
        d = ps.model_dump(exclude_none=True)["definitions"][0]
        assert "pad_parameters" not in d

    def test_get_definition_from_cache(self):
        ps = CfgPadstacks()
        ps.add_definition("via_cached", material="gold")
        result = ps.get_definition("via_cached")
        assert result.material == "gold"

    def test_get_definition_raises_without_pedb(self):
        ps = CfgPadstacks()
        with pytest.raises(KeyError):
            ps.get_definition("nonexistent")

    def test_get_instance_from_cache(self):
        ps = CfgPadstacks()
        ps.add_instance(name="v_cached", net_name="GND")
        result = ps.get_instance("v_cached")
        assert result.net_name == "GND"

    def test_get_instance_raises_without_pedb(self):
        ps = CfgPadstacks()
        with pytest.raises(KeyError):
            ps.get_instance("nonexistent")

    def test_deprecated_add_padstack_definition(self):
        ps = CfgPadstacks()
        with pytest.warns(FutureWarning):
            ps.add_padstack_definition(name="via_dep")
        assert ps.definitions[0].name == "via_dep"

    def test_deprecated_add_padstack_instance(self):
        ps = CfgPadstacks()
        with pytest.warns(FutureWarning):
            ps.add_padstack_instance(name="v_dep")
        assert ps.instances[0].name == "v_dep"

    def test_multiple_definitions(self):
        ps = CfgPadstacks()
        ps.add_definition("via1")
        ps.add_definition("via2")
        assert len(ps.definitions) == 2

    def test_multiple_instances(self):
        ps = CfgPadstacks()
        ps.add_instance(name="v1")
        ps.add_instance(name="v2")
        assert len(ps.instances) == 2

    def test_create_classmethod_no_pedb(self):
        ps = CfgPadstacks.create()
        assert isinstance(ps, CfgPadstacks)
        assert ps._pedb is None

    def test_create_classmethod_with_pedb(self):
        mock_pedb = MagicMock()
        ps = CfgPadstacks.create(pedb=mock_pedb)
        assert ps._pedb is mock_pedb

    def test_set_pedb(self):
        mock_pedb = MagicMock()
        ps = CfgPadstacks()
        ps._set_pedb(mock_pedb)
        assert ps._pedb is mock_pedb

    def test_set_cfg_stackup(self):
        mock_stackup = MagicMock()
        ps = CfgPadstacks()
        ps._set_cfg_stackup(mock_stackup)
        assert ps._cfg_stackup is mock_stackup

    def test_to_dict_empty(self):
        ps = CfgPadstacks()
        assert ps._to_dict() == {}

    def test_to_dict_with_definitions(self):
        ps = CfgPadstacks()
        ps.add_definition("via", material="copper")
        d = ps._to_dict()
        assert d["definitions"][0]["name"] == "via"

    def test_to_dict_with_instances(self):
        ps = CfgPadstacks()
        ps.add_instance(name="v1", net_name="GND")
        d = ps._to_dict()
        assert d["instances"][0]["name"] == "v1"

    def test_add_definition_with_cfg_stackup_layers(self):
        """add_definition resolves signal layers from _cfg_stackup when pad_layers is None."""
        mock_layer = MagicMock()
        mock_layer.name = "1_Top"
        mock_stackup = MagicMock()
        mock_stackup.get_signal_layers.return_value = [mock_layer]
        ps = CfgPadstacks()
        ps._set_cfg_stackup(mock_stackup)
        ps.add_definition("via", pad_diameter="0.5mm", anti_pad_diameter="0.8mm")
        d = ps.model_dump(exclude_none=True)["definitions"][0]
        assert d["pad_parameters"]["regular_pad"][0]["layer_name"] == "1_Top"
        assert d["pad_parameters"]["anti_pad"][0]["layer_name"] == "1_Top"


class TestPadstackDefinitionConfig:
    def test_minimal(self):
        p = CfgPadstackDefinition(name="via_0.2")
        d = p.model_dump(exclude_none=True)
        assert d == {"name": "via_0.2"}

    def test_with_properties(self):
        p = CfgPadstackDefinition(name="via", hole_plating_thickness="25um", material="copper")
        d = p.model_dump(exclude_none=True)
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
        d = p.model_dump(exclude_none=True)
        assert d["hole_range"] == "upper_pad_to_lower_pad"
        assert d["pad_parameters"]["pad_type"] == "circle"
        assert d["solder_ball_parameters"]["diameter"] == "150um"

    def test_create_classmethod(self):
        p = CfgPadstackDefinition.create(name="via_created", material="copper")
        assert isinstance(p, CfgPadstackDefinition)
        assert p.material == "copper"


class TestPadstackInstanceConfig:
    def test_minimal(self):
        inst = CfgPadstackInstance(name="via_1", net_name="GND")
        d = inst.model_dump(exclude_none=True)
        assert d["name"] == "via_1"
        assert d["net_name"] == "GND"

    def test_layer_range(self):
        inst = CfgPadstackInstance(layer_range=["top", "bot"])
        d = inst.model_dump(exclude_none=True)
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
        d = inst.model_dump(exclude_none=True)
        assert d["definition"] == "via_0.2"
        assert d["hole_override_enabled"] is True
        assert d["hole_override_diameter"] == "0.22mm"
        assert d["solder_ball_layer"] == "top"

    def test_backdrill(self):
        inst = CfgPadstackInstance(name="via_bd")
        inst.set_backdrill("L4", "0.3mm", drill_from_bottom=True)
        d = inst.model_dump(exclude_none=True)
        assert d["backdrill_parameters"]["from_bottom"]["drill_to_layer"] == "L4"

    def test_backdrill_with_stub(self):
        inst = CfgPadstackInstance(name="via_bd2")
        inst.set_backdrill("L4", "0.3mm", stub_length="0.05mm", drill_from_bottom=False)
        d = inst.model_dump(exclude_none=True)
        assert "from_top" in d["backdrill_parameters"]
        assert d["backdrill_parameters"]["from_top"]["stub_length"] == "0.05mm"

    def test_backdrill_chaining(self):
        """set_backdrill returns self for method chaining."""
        inst = CfgPadstackInstance(name="via")
        result = inst.set_backdrill("L3", "0.25mm")
        assert result is inst


class TestCfgBackdrillParameters:
    def test_from_bottom_no_stub(self):
        bd = CfgBackdrillParameters()
        bd.add_backdrill_to_layer("L4", "0.3mm", drill_from_bottom=True)
        assert bd.from_bottom.drill_to_layer == "L4"
        assert bd.from_bottom.diameter == "0.3mm"
        assert bd.from_top is None

    def test_from_top_with_stub(self):
        bd = CfgBackdrillParameters()
        bd.add_backdrill_to_layer("L2", "0.25mm", stub_length="0.05mm", drill_from_bottom=False)
        assert bd.from_top.drill_to_layer == "L2"
        assert bd.from_top.stub_length == "0.05mm"
        assert bd.from_bottom is None

    def test_both_sides(self):
        bd = CfgBackdrillParameters()
        bd.add_backdrill_to_layer("L2", "0.25mm", drill_from_bottom=False)
        bd.add_backdrill_to_layer("L5", "0.3mm", drill_from_bottom=True)
        assert bd.from_top is not None
        assert bd.from_bottom is not None

    def test_model_dump(self):
        bd = CfgBackdrillParameters()
        bd.add_backdrill_to_layer("L3", "0.3mm", drill_from_bottom=True)
        d = bd.model_dump(exclude_none=True)
        assert d["from_bottom"]["drill_to_layer"] == "L3"
        assert "from_top" not in d


class TestCfgPadstacksGetDefinitionFromEdb:
    def test_get_definition_cached(self):
        ps = CfgPadstacks()
        ps.add_definition("via_0.2", material="copper")
        result = ps.get_definition("via_0.2")
        assert result.name == "via_0.2"

    def test_get_definition_raises_without_pedb(self):
        ps = CfgPadstacks()
        with pytest.raises(KeyError, match="missing"):
            ps.get_definition("missing")

    def test_get_definition_from_edb(self):
        mock_pdef = MagicMock()
        mock_pdef.name = "via_0.2"
        mock_pdef.hole_plating_thickness = "25um"
        mock_pdef.material = "copper"
        mock_pdef.hole_range = "through"
        mock_pdef.get_pad_parameters.return_value = {}
        mock_pdef.get_hole_parameters.return_value = {}
        mock_pdef.get_solder_parameters.return_value = {}
        mock_pedb = MagicMock()
        mock_pedb.padstacks.definitions = {"via_0.2": mock_pdef}
        ps = CfgPadstacks.create(pedb=mock_pedb)
        pdef = ps.get_definition("via_0.2")
        assert pdef.name == "via_0.2"

    def test_get_definition_not_found_in_edb_raises(self):
        mock_pedb = MagicMock()
        mock_pedb.padstacks.definitions = {}
        ps = CfgPadstacks.create(pedb=mock_pedb)
        with pytest.raises(KeyError, match="missing"):
            ps.get_definition("missing")

    def test_get_instance_cached(self):
        ps = CfgPadstacks()
        ps.add_instance(name="via_A1", net_name="GND")
        result = ps.get_instance("via_A1")
        assert result.name == "via_A1"

    def test_get_instance_raises_without_pedb(self):
        ps = CfgPadstacks()
        with pytest.raises(KeyError, match="missing"):
            ps.get_instance("missing")

    def test_get_instance_from_edb(self):
        mock_inst = MagicMock()
        mock_inst.aedt_name = "via_A1"
        mock_inst.is_pin = False
        mock_inst.padstack_definition = "via_0.2"
        mock_inst.backdrill_parameters = None
        mock_inst.position_and_rotation = [0.001, 0.002, 0.0]
        mock_inst.get_hole_overrides.return_value = (False, "0")
        mock_inst.solderball_layer = None
        mock_inst.start_layer = "top"
        mock_inst.stop_layer = "bot"
        mock_pedb = MagicMock()
        mock_pedb.padstacks.instances_by_name = {"via_A1": mock_inst}
        ps = CfgPadstacks.create(pedb=mock_pedb)
        inst = ps.get_instance("via_A1")
        assert inst.name == "via_A1"

    def test_get_instance_not_found_in_edb_raises(self):
        mock_pedb = MagicMock()
        mock_pedb.padstacks.instances_by_name = {}
        ps = CfgPadstacks.create(pedb=mock_pedb)
        with pytest.raises(KeyError, match="missing"):
            ps.get_instance("missing")

    def test_build_pad_params_no_stackup_no_layers(self):
        """_build_pad_parameters uses empty layers list when no pad_layers and no _cfg_stackup."""
        ps = CfgPadstacks()
        result = ps._build_pad_parameters(
            pad_layers=None,
            pad_shape="circle",
            pad_diameter="0.2mm",
            pad_x_size=None,
            pad_y_size=None,
            pad_offset_x="0",
            pad_offset_y="0",
            pad_rotation="0",
            anti_pad_shape=None,
            anti_pad_diameter=None,
            anti_pad_x_size=None,
            anti_pad_y_size=None,
        )
        assert result == {}
