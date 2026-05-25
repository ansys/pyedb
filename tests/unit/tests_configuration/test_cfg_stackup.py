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

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_stackup import CfgLayer, CfgMaterial, CfgStackup


class TestLayerConfig:
    def test_name_only(self):
        layer = CfgLayer(name="top")
        d = layer.model_dump(exclude_none=True)
        assert d["name"] == "top"

    def test_signal_layer(self):
        layer = CfgLayer(name="top", type="signal", material="copper", thickness="35um")
        d = layer.model_dump(exclude_none=True)
        assert d["layer_type"] == "signal"
        assert d["material"] == "copper"
        assert d["thickness"] == "35um"

    def test_explicit_params(self):
        """All layer params are explicit — no **kwargs required."""
        layer = CfgLayer(name="sig", type="signal", material="copper", fill_material="fr4", thickness="18um")
        d = layer.model_dump(exclude_none=True)
        assert d["fill_material"] == "fr4"
        assert d["thickness"] == "18um"

    def test_set_huray_roughness(self):
        layer = CfgLayer(name="top")
        layer.set_huray_roughness("0.1um", "2.9")
        d = layer.model_dump(exclude_none=True)
        assert d["roughness"]["enabled"] is True
        assert d["roughness"]["top"]["model"] == "huray"
        assert d["roughness"]["top"]["nodule_radius"] == "0.1um"
        assert d["roughness"]["top"]["surface_ratio"] == "2.9"

    def test_set_huray_roughness_partial_surfaces(self):
        layer = CfgLayer(name="top")
        layer.set_huray_roughness("0.1um", "2.9", top=True, bottom=False, side=False)
        d = layer.model_dump(exclude_none=True)
        assert "top" in d["roughness"]
        assert "bottom" not in d["roughness"]
        assert "side" not in d["roughness"]

    def test_set_groisse_roughness(self):
        layer = CfgLayer(name="inner1")
        layer.set_groisse_roughness(0.3e-6)
        d = layer.model_dump(exclude_none=True)
        assert d["roughness"]["top"]["model"] == "groisse"
        assert d["roughness"]["top"]["roughness"] == 0.3e-6

    def test_set_etching(self):
        layer = CfgLayer(name="top")
        layer.set_etching(factor=0.4, etch_power_ground_nets=True)
        d = layer.model_dump(exclude_none=True)
        assert d["etching"]["factor"] == 0.4
        assert d["etching"]["etch_power_ground_nets"] is True
        assert d["etching"]["enabled"] is True

    def test_method_chaining(self):
        """set_huray_roughness and set_etching return self for chaining."""
        layer = CfgLayer(name="top")
        result = layer.set_huray_roughness("0.1um", "2.9").set_etching(factor=0.3)
        assert result is layer
        d = layer.model_dump(exclude_none=True)
        assert "roughness" in d
        assert "etching" in d


class TestMaterialConfig:
    def test_name_only(self):
        m = CfgMaterial(name="copper")
        d = m.model_dump(exclude_none=True)
        assert d == {"name": "copper"}

    def test_conductivity(self):
        m = CfgMaterial(name="copper", conductivity=5.8e7)
        d = m.model_dump(exclude_none=True)
        assert d["conductivity"] == 5.8e7

    def test_dielectric_props(self):
        m = CfgMaterial(name="fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
        d = m.model_dump(exclude_none=True)
        assert d["permittivity"] == 4.4
        assert d["dielectric_loss_tangent"] == 0.02

    def test_all_known_properties(self):
        props = {
            "conductivity": 1e6,
            "dielectric_loss_tangent": 0.01,
            "magnetic_loss_tangent": 0.001,
            "mass_density": 8960,
            "permittivity": 4.4,
            "permeability": 1.0,
            "poisson_ratio": 0.34,
            "specific_heat": 385,
            "thermal_conductivity": 401,
            "youngs_modulus": 110e9,
            "thermal_expansion_coefficient": 17e-6,
            "dc_conductivity": 1e5,
            "dc_permittivity": 4.0,
            "dielectric_model_frequency": 1e9,
            "loss_tangent_at_frequency": 0.01,
            "permittivity_at_frequency": 4.3,
        }
        m = CfgMaterial(name="mat", **props)
        d = m.model_dump(exclude_none=True)
        for key, val in props.items():
            assert d[key] == val

    def test_explicit_params_no_kwargs(self):
        """All material properties are explicit — no **kwargs required."""
        m = CfgMaterial(
            name="silver",
            conductivity=6.3e7,
            permittivity=1.0,
            dielectric_loss_tangent=0.0,
            magnetic_loss_tangent=0.0,
            mass_density=10490,
            permeability=1.0,
            poisson_ratio=0.37,
            specific_heat=235,
            thermal_conductivity=429,
            youngs_modulus=83e9,
            thermal_expansion_coefficient=19e-6,
        )
        d = m.model_dump(exclude_none=True)
        assert d["conductivity"] == 6.3e7
        assert d["mass_density"] == 10490


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

    def test_add_signal_layer_returns_layer_config(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        assert isinstance(lyr, CfgLayer)

    def test_layer_roughness_via_stackup(self):
        s = CfgStackup()
        lyr = s.add_signal_layer("top")
        lyr.set_huray_roughness("0.1um", "2.9")
        d = s.model_dump(exclude_none=True)["layers"][0]
        assert d["roughness"]["top"]["model"] == "huray"

    def test_get_layer_from_edb_with_pedb(self):
        """get_layer loads from EDB when not in cache."""
        from unittest.mock import MagicMock

        mock_layer = MagicMock()
        mock_layer.properties = {"type": "signal", "material": "copper", "thickness": "35um"}
        mock_pedb = MagicMock()
        mock_pedb.stackup.all_layers = {"top": mock_layer}
        s = CfgStackup()
        s._set_pedb(mock_pedb)
        lyr = s.get_layer("top")
        assert lyr.name == "top"
        assert lyr.layer_type == "signal"
        assert lyr.material == "copper"

    def test_get_layer_from_edb_not_found_raises(self):
        from unittest.mock import MagicMock

        mock_pedb = MagicMock()
        mock_pedb.stackup.all_layers = {}
        s = CfgStackup()
        s._set_pedb(mock_pedb)
        with pytest.raises(KeyError, match="missing"):
            s.get_layer("missing")

    def test_get_layers_raises_without_pedb(self):
        s = CfgStackup()
        with pytest.raises(KeyError):
            s.get_layers()

    def test_get_layers_with_pedb(self):
        from unittest.mock import MagicMock

        mock_layer = MagicMock()
        mock_layer.properties = {"type": "signal", "material": "copper", "thickness": "35um"}
        mock_pedb = MagicMock()
        mock_pedb.stackup.all_layers = {"top": mock_layer}
        s = CfgStackup()
        s._set_pedb(mock_pedb)
        layers = s.get_layers()
        assert len(layers) == 1
        assert layers[0].name == "top"

    def test_get_signal_layers_raises_without_pedb(self):
        s = CfgStackup()
        with pytest.raises(KeyError):
            s.get_signal_layers()

    def test_get_signal_layers_with_pedb(self):
        from unittest.mock import MagicMock

        mock_layer = MagicMock()
        mock_layer.properties = {"type": "signal", "material": "copper", "thickness": "35um"}
        mock_pedb = MagicMock()
        mock_pedb.stackup.signal_layers = {"top": mock_layer}
        mock_pedb.stackup.all_layers = {"top": mock_layer}
        s = CfgStackup()
        s._set_pedb(mock_pedb)
        sig_layers = s.get_signal_layers()
        assert len(sig_layers) == 1
        assert sig_layers[0].type == "signal"

    def test_get_material_from_edb_with_pedb(self):
        from unittest.mock import MagicMock

        mock_mat = MagicMock()
        mock_mat.to_dict.return_value = {"name": "copper", "conductivity": 5.8e7}
        mock_pedb = MagicMock()
        mock_pedb.materials.materials = {"copper": mock_mat}
        s = CfgStackup()
        s._set_pedb(mock_pedb)
        mat = s.get_material("copper")
        assert mat.name == "copper"
        assert mat.conductivity == 5.8e7

    def test_get_material_from_edb_not_found_raises(self):
        from unittest.mock import MagicMock

        mock_pedb = MagicMock()
        mock_pedb.materials.materials = {}
        s = CfgStackup()
        s._set_pedb(mock_pedb)
        with pytest.raises(KeyError, match="missing"):
            s.get_material("missing")

    def test_add_material_config_with_name_override(self):
        """add_material with config object and explicit name overrides the config name."""
        s = CfgStackup()
        mat_cfg = CfgMaterial(name="old_name", conductivity=5.8e7)
        mat = s.add_material(name="new_name", config=mat_cfg)
        assert mat.name == "new_name"
        assert mat.conductivity == 5.8e7

    def test_normalize_thickness_numeric_layer(self):
        """normalize_thickness handles numeric (non-string) thickness."""
        s = CfgStackup()
        s.add_signal_layer(name="top", thickness=35e-6)
        s.normalize_thickness("m")
        # numeric thickness gets f"{val}m" appended
        assert s.layers[0].thickness == f"{35e-6}m"


class TestCfgStackupAddMaterial:
    def test_returns_material_config_instance(self):
        s = CfgStackup()
        mat = s.add_material("copper", conductivity=5.8e7)
        assert isinstance(mat, CfgMaterial)

    def test_material_appended_to_list(self):
        s = CfgStackup()
        s.add_material("copper", conductivity=5.8e7)
        d = s.model_dump(exclude_none=True)
        assert "materials" in d
        assert len(d["materials"]) == 1
        assert d["materials"][0]["name"] == "copper"

    def test_material_conductivity_stored(self):
        s = CfgStackup()
        s.add_material("copper", conductivity=5.8e7)
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert d["conductivity"] == 5.8e7

    def test_material_dielectric_properties(self):
        s = CfgStackup()
        s.add_material("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert d["permittivity"] == 4.4
        assert d["dielectric_loss_tangent"] == 0.02

    def test_material_thermal_properties(self):
        s = CfgStackup()
        s.add_material("fr4", thermal_conductivity=0.3, mass_density=1900, specific_heat=1050)
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert d["thermal_conductivity"] == 0.3
        assert d["mass_density"] == 1900
        assert d["specific_heat"] == 1050

    def test_material_mechanical_properties(self):
        s = CfgStackup()
        s.add_material("copper", youngs_modulus=110e9, poisson_ratio=0.34, thermal_expansion_coefficient=17e-6)
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert d["youngs_modulus"] == 110e9
        assert d["poisson_ratio"] == 0.34
        assert d["thermal_expansion_coefficient"] == 17e-6

    def test_material_dc_override_properties(self):
        s = CfgStackup()
        s.add_material("mat", dc_conductivity=1e5, dc_permittivity=4.0)
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert d["dc_conductivity"] == 1e5
        assert d["dc_permittivity"] == 4.0

    def test_material_frequency_dependent_properties(self):
        s = CfgStackup()
        s.add_material(
            "mat",
            dielectric_model_frequency=1e9,
            loss_tangent_at_frequency=0.01,
            permittivity_at_frequency=4.3,
        )
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert d["dielectric_model_frequency"] == 1e9
        assert d["loss_tangent_at_frequency"] == 0.01
        assert d["permittivity_at_frequency"] == 4.3

    def test_multiple_materials_accumulated(self):
        s = CfgStackup()
        s.add_material("copper", conductivity=5.8e7)
        s.add_material("fr4", permittivity=4.4)
        s.add_material("air", permittivity=1.0)
        d = s.model_dump(exclude_none=True)
        assert len(d["materials"]) == 3
        names = [m["name"] for m in d["materials"]]
        assert names == ["copper", "fr4", "air"]

    def test_name_only_no_extra_keys(self):
        s = CfgStackup()
        s.add_material("mymat")
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert d == {"name": "mymat"}

    def test_none_values_not_included(self):
        s = CfgStackup()
        s.add_material("copper", conductivity=5.8e7, permittivity=None)
        d = s.model_dump(exclude_none=True)["materials"][0]
        assert "permittivity" not in d

    def test_all_properties(self):
        s = CfgStackup()
        props = {
            "conductivity": 1e6,
            "permittivity": 4.4,
            "dielectric_loss_tangent": 0.01,
            "magnetic_loss_tangent": 0.001,
            "mass_density": 8960,
            "permeability": 1.0,
            "poisson_ratio": 0.34,
            "specific_heat": 385,
            "thermal_conductivity": 401,
            "youngs_modulus": 110e9,
            "thermal_expansion_coefficient": 17e-6,
            "dc_conductivity": 1e5,
            "dc_permittivity": 4.0,
            "dielectric_model_frequency": 1e9,
            "loss_tangent_at_frequency": 0.01,
            "permittivity_at_frequency": 4.3,
        }
        s.add_material("full_mat", **props)
        d = s.model_dump(exclude_none=True)["materials"][0]
        for key, val in props.items():
            assert d[key] == val
