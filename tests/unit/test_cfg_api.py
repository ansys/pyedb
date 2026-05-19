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

from pyedb.configuration.cfg_stackup import CfgLayer, CfgMaterial, CfgStackup

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


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
