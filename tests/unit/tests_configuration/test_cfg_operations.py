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

from pyedb.configuration.cfg_operations import CfgAutoIdentifyNets, CfgCutout, CfgOperations

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestCfgAutoIdentifyNets:
    def test_defaults(self):
        a = CfgAutoIdentifyNets()
        assert a.enabled is False
        assert a.resistor_below == 100
        assert a.inductor_below == 1
        assert a.capacitor_above == "10nF"

    def test_custom_values(self):
        a = CfgAutoIdentifyNets(enabled=True, resistor_below=50, inductor_below=2, capacitor_above="1uF")
        assert a.enabled is True
        assert a.resistor_below == 50
        assert a.capacitor_above == "1uF"


class TestCfgCutout:
    def test_defaults(self):
        c = CfgCutout()
        assert c.extent_type == "ConvexHull"
        assert c.expansion_size == 0.002
        assert c.number_of_threads == 1
        assert c.custom_extent_units == "meter"
        assert c.expansion_factor == 0

    def test_signal_and_reference_nets(self):
        c = CfgCutout(signal_nets=["SIG"], reference_nets=["GND"])
        assert c.signal_nets == ["SIG"]
        assert c.reference_nets == ["GND"]

    def test_legacy_signal_list_alias(self):
        """signal_list key is accepted via AliasChoices."""
        c = CfgCutout.model_validate({"signal_list": ["SIG"], "reference_list": ["GND"]})
        assert c.signal_nets == ["SIG"]
        assert c.reference_nets == ["GND"]

    def test_extent_type_none(self):
        c = CfgCutout(extent_type=None)
        assert c.extent_type is None

    def test_extent_type_unknown_passthrough(self):
        """Unknown extent_type values pass through unchanged."""
        c = CfgCutout(extent_type="MyCustomExtent")
        assert c.extent_type == "MyCustomExtent"

    def test_extent_type_all_aliases(self):
        for value, expected in [
            ("convexhull", "ConvexHull"),
            ("convex_hull", "ConvexHull"),
            ("conforming", "Conformal"),
            ("conformal", "Conformal"),
            ("bounding", "BoundingBox"),
            ("boundingbox", "BoundingBox"),
            ("bounding_box", "BoundingBox"),
        ]:
            c = CfgCutout(extent_type=value)
            assert c.extent_type == expected, f"{value!r} → expected {expected!r}, got {c.extent_type!r}"

    def test_auto_identify_nets_default(self):
        c = CfgCutout()
        assert c.auto_identify_nets is not None
        assert c.auto_identify_nets.enabled is False

    def test_auto_identify_nets_from_flat_kwargs(self):
        """Flat kwargs are used to build auto_identify_nets via model_validator."""
        c = CfgCutout.model_validate(
            {"auto_identify_nets_enabled": True, "resistor_below": 50, "inductor_below": 2, "capacitor_above": "1uF"}
        )
        assert c.auto_identify_nets.enabled is True
        assert c.auto_identify_nets.resistor_below == 50

    def test_auto_identify_nets_explicit_skips_validator(self):
        """When auto_identify_nets is already present, the flat-kwargs validator is skipped."""
        ain = CfgAutoIdentifyNets(enabled=True, resistor_below=200)
        c = CfgCutout(auto_identify_nets=ain)
        assert c.auto_identify_nets.resistor_below == 200

    def test_model_dump_excludes_none(self):
        c = CfgCutout(signal_nets=["SIG"])
        d = c.model_dump()
        assert "custom_extent" not in d
        assert "signal_nets" in d

    def test_model_dump_explicit_include_none(self):
        c = CfgCutout(signal_nets=["SIG"])
        d = c.model_dump(exclude_none=False)
        assert "custom_extent" in d

    def test_nets(self):
        c = CfgCutout(signal_nets=["SIG1"], reference_nets=["GND"])
        d = c.model_dump(exclude_none=True)
        assert d["signal_nets"] == ["SIG1"]
        assert d["reference_nets"] == ["GND"]

    def test_auto_identify_nets(self):
        c = CfgCutout(auto_identify_nets_enabled=True, resistor_below=200)
        d = c.model_dump(exclude_none=True)
        assert d["auto_identify_nets"]["enabled"] is True
        assert d["auto_identify_nets"]["resistor_below"] == 200

    def test_extent_type_convexhull(self):
        c = CfgCutout(extent_type="ConvexHull")
        assert c.model_dump(exclude_none=True)["extent_type"] == "ConvexHull"

    def test_extent_type_bounding_box(self):
        c = CfgCutout(extent_type="BoundingBox")
        assert c.model_dump(exclude_none=True)["extent_type"] == "BoundingBox"

    def test_extent_type_conformal(self):
        c = CfgCutout(extent_type="Conformal")
        assert c.model_dump(exclude_none=True)["extent_type"] == "Conformal"

    def test_extent_type_case_insensitive_lower(self):
        c = CfgCutout(extent_type="convexhull")
        assert c.model_dump(exclude_none=True)["extent_type"] == "ConvexHull"

    def test_extent_type_case_insensitive_upper(self):
        c = CfgCutout(extent_type="CONVEXHULL")
        assert c.model_dump(exclude_none=True)["extent_type"] == "ConvexHull"

    def test_extent_type_case_insensitive_boundingbox(self):
        c = CfgCutout(extent_type="boundingbox")
        assert c.model_dump(exclude_none=True)["extent_type"] == "BoundingBox"

    def test_extent_type_case_insensitive_conformal(self):
        c = CfgCutout(extent_type="CONFORMAL")
        assert c.model_dump(exclude_none=True)["extent_type"] == "Conformal"

    def test_expansion_size(self):
        c = CfgCutout(expansion_size=0.005)
        assert c.model_dump(exclude_none=True)["expansion_size"] == 0.005

    def test_expansion_factor(self):
        c = CfgCutout(expansion_factor=0.1)
        assert c.model_dump(exclude_none=True)["expansion_factor"] == 0.1


class TestOperationsConfig:
    def test_empty(self):
        d = CfgOperations().model_dump()
        assert d.get("cutout") is None
        assert d["generate_auto_hfss_regions"] is False

    def test_add_cutout(self):
        ops = CfgOperations()
        c = ops.add_cutout(signal_nets=["SIG1"], reference_nets=["GND"])
        assert isinstance(c, CfgCutout)
        d = ops.model_dump()
        assert "cutout" in d
        assert d["cutout"]["signal_nets"] == ["SIG1"]

    def test_add_cutout_extent_type_convexhull(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="ConvexHull")
        assert ops.model_dump(exclude_none=True)["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_case_insensitive(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="convexhull")
        assert ops.model_dump(exclude_none=True)["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_boundingbox_case_insensitive(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="BOUNDINGBOX")
        assert ops.model_dump(exclude_none=True)["cutout"]["extent_type"] == "BoundingBox"

    def test_add_cutout_expansion_size(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], expansion_size=0.003)
        assert ops.model_dump(exclude_none=True)["cutout"]["expansion_size"] == 0.003

    def test_generate_auto_hfss_regions(self):
        ops = CfgOperations()
        ops.generate_auto_hfss_regions = True
        d = ops.model_dump(exclude_none=True)
        assert d["generate_auto_hfss_regions"] is True

    def test_add_cutout_auto_identify_nets(self):
        ops = CfgOperations()
        ops.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            auto_identify_nets_enabled=True,
            resistor_below=50,
            inductor_below=2,
            capacitor_above="1uF",
        )
        ain = ops.cutout.auto_identify_nets
        assert ain.enabled is True
        assert ain.resistor_below == 50
        assert ain.capacitor_above == "1uF"

    def test_add_cutout_returns_cutout(self):
        ops = CfgOperations()
        result = ops.add_cutout()
        assert result is ops.cutout

    def test_model_dump_excludes_none_by_default(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"])
        d = ops.model_dump()
        assert "reference_nets" not in d["cutout"]
