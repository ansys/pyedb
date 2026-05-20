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

from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_padstacks import (
    CfgBackdrillParameters,
    CfgPadstackDefinition,
    CfgPadstackInstance,
    CfgPadstacks,
)
from pyedb.configuration.cfg_stackup import CfgLayer, CfgMaterial, CfgStackup

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


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


class TestCfgStackup:
    def test_empty(self):
        s = CfgStackup()
        d = s.model_dump(exclude_none=True, by_alias=True)
        assert d == {"materials": [], "layers": []}

    def test_add_material(self):
        s = CfgStackup()
        mat = s.add_material(name="copper", conductivity=5.8e7)
        assert isinstance(mat, CfgMaterial)
        assert len(s.materials) == 1
        assert s.materials[0].name == "copper"

    def test_add_material_all_props(self):
        s = CfgStackup()
        s.add_material(
            name="fr4", permittivity=4.4, dielectric_loss_tangent=0.02, thermal_conductivity=0.3, mass_density=1900
        )
        d = s.materials[0].model_dump(exclude_none=True)
        assert d["permittivity"] == 4.4
        assert d["thermal_conductivity"] == 0.3
        assert d["mass_density"] == 1900

    def test_add_layer(self):
        s = CfgStackup()
        s.add_layer(name="top", layer_type="signal", material="copper", thickness="35um")
        assert s.layers[0].name == "top"

    def test_add_layer_type_alias(self):
        """type= kwarg is accepted as alias for layer_type=."""
        s = CfgStackup()
        s.add_layer(name="top", layer_type="signal", material="copper", thickness="35um")
        assert s.layers[0].layer_type == "signal"

    def test_add_layer_explicit_fill_material(self):
        s = CfgStackup()
        s.add_layer(name="sig", layer_type="signal", material="copper", fill_material="fr4", thickness="18um")
        lyr = s.layers[0]
        assert lyr.fill_material == "fr4"
        assert lyr.thickness == "18um"

    def test_add_signal_layer_convenience(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("sig_top")
        assert isinstance(lyr, CfgLayer)
        assert lyr.layer_type == "signal"
        assert lyr.fill_material == "FR4_epoxy"

    def test_add_dielectric_layer_convenience(self):
        s = CfgStackup()
        lyr = s.add_dielectric_layer("diel_1")
        assert isinstance(lyr, CfgLayer)
        assert lyr.layer_type == "dielectric"
        assert lyr.material == "FR4_epoxy"

    def test_layer_order_preserved(self):
        s = CfgStackup()
        s.add_signal_layer("top")
        s.add_dielectric_layer("diel")
        s.add_signal_layer("bot")
        names = [layer.name for layer in s.layers]
        assert names == ["top", "diel", "bot"]

    def test_multiple_materials(self):
        s = CfgStackup()
        s.add_material(name="copper", conductivity=5.8e7)
        s.add_material(name="fr4", permittivity=4.4)
        assert len(s.materials) == 2

    def test_layer_roughness(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        lyr.set_huray_roughness("0.1um", "2.9")
        assert s.layers[0].roughness.top.model == "huray"

    def test_layer_groisse_roughness(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        lyr.set_groisse_roughness("0.3um")
        r = s.layers[0].roughness
        assert r.top.model == "groisse"
        assert r.top.roughness == "0.3um"
        assert r.bottom.model == "groisse"
        assert r.side.model == "groisse"

    def test_layer_roughness_selective_surfaces(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        lyr.set_huray_roughness("0.1um", "2.9", top=True, bottom=False, side=False)
        r = s.layers[0].roughness
        assert r.top is not None
        assert r.bottom is None
        assert r.side is None

    def test_layer_roughness_enabled_flag(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        lyr.set_huray_roughness("0.1um", "2.9", enabled=False)
        assert s.layers[0].roughness.enabled is False

    def test_layer_etching(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        lyr.set_etching(factor=0.4, etch_power_ground_nets=True)
        e = s.layers[0].etching
        assert e.factor == 0.4
        assert e.etch_power_ground_nets is True
        assert e.enabled is True

    def test_layer_etching_disabled(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        lyr.set_etching(enabled=False)
        assert s.layers[0].etching.enabled is False

    def test_layer_method_chaining(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        result = lyr.set_huray_roughness("0.1um", "2.9").set_etching(factor=0.3)
        assert result is lyr

    def test_layer_type_property(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        assert lyr.type == "signal"

    def test_add_layer_at_bottom(self):
        s = CfgStackup()
        lyr = s.add_layer_at_bottom(name="diel", type="dielectric", material="FR4_epoxy", thickness="100um")
        assert lyr.name == "diel"
        assert s.layers[0] is lyr

    def test_add_layer_at_bottom_from_cfg_layer(self):
        s = CfgStackup()
        existing = CfgLayer(name="top", type="signal", material="copper", thickness="35um")
        lyr = s.add_layer_at_bottom(config=existing)
        assert lyr.name == "top"
        assert lyr.material == "copper"

    def test_add_layer_at_bottom_name_override(self):
        s = CfgStackup()
        existing = CfgLayer(name="old_name", type="signal")
        lyr = s.add_layer_at_bottom(name="new_name", config=existing)
        assert lyr.name == "new_name"

    def test_get_layer_from_cache(self):
        s = CfgStackup()
        s.add_signal_layer("top")
        lyr = s.get_layer("top")
        assert lyr.name == "top"
        assert lyr is s.layers[0]

    def test_get_layer_not_found_without_pedb_raises(self):
        s = CfgStackup()
        with pytest.raises(KeyError, match="top"):
            s.get_layer("top")

    def test_get_material_from_cache(self):
        s = CfgStackup()
        s.add_material(name="copper", conductivity=5.8e7)
        mat = s.get_material("copper")
        assert mat.name == "copper"
        assert mat is s.materials[0]

    def test_get_material_not_found_without_pedb_raises(self):
        s = CfgStackup()
        with pytest.raises(KeyError, match="copper"):
            s.get_material("copper")

    def test_normalize_thickness_um(self):
        s = CfgStackup()
        s.add_signal_layer(name="top", thickness="35um")
        s.normalize_thickness("um")
        assert s.layers[0].thickness == "35.0um"

    def test_normalize_thickness_m(self):
        s = CfgStackup()
        s.add_signal_layer(name="top", thickness="35um")
        s.normalize_thickness("m")
        assert s.layers[0].thickness == "3.5e-05m"

    def test_normalize_thickness_invalid_unit_raises(self):
        s = CfgStackup()
        s.add_signal_layer(name="top", thickness="35um")
        with pytest.raises(ValueError, match="Unsupported unit"):
            s.normalize_thickness("nm")

    def test_add_material_config_object(self):
        s = CfgStackup()
        mat_cfg = CfgMaterial(name="copper", conductivity=5.8e7)
        s.add_material(config=mat_cfg)
        assert s.materials[0].conductivity == 5.8e7

    def test_add_material_config_dict(self):
        s = CfgStackup()
        s.add_material(config={"name": "fr4", "permittivity": 4.4})
        assert s.materials[0].permittivity == 4.4

    def test_duplicate_in_builder_raises(self):
        s = CfgStackup()
        s.add_material(name="copper", conductivity=5.8e7)
        with pytest.raises(ValueError, match="already exists"):
            s.add_material(name="copper", conductivity=4.1e7)

    def test_duplicate_error_message_advises_get_material(self):
        s = CfgStackup()
        s.add_material(name="fr4", permittivity=4.4)
        with pytest.raises(ValueError, match="get_material"):
            s.add_material("fr4")

    def test_duplicate_check_in_edb_raises(self):
        mock_pedb = MagicMock()
        mock_pedb.materials.materials = {"copper": MagicMock()}
        s = CfgStackup()
        s._set_pedb(mock_pedb)
        with pytest.raises(ValueError, match="already exists"):
            s.add_material(name="copper", conductivity=5.8e7)

    def test_no_duplicate_check_without_pedb(self):
        s = CfgStackup()
        s.add_material(name="copper", conductivity=5.8e7)
        with pytest.raises(ValueError):
            s.add_material("copper")
