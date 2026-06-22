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

from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_package_definition import CfgHeatSink, CfgPackage, CfgPackageDefinitions

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestCfgHeatSink:
    def test_minimal(self):
        hs = CfgHeatSink()
        assert hs.fin_height is None

    def test_all_fields(self):
        hs = CfgHeatSink(
            fin_base_height="0.5mm",
            fin_height="3mm",
            fin_orientation="x_oriented",
            fin_spacing="1mm",
            fin_thickness="0.2mm",
        )
        d = hs.model_dump(exclude_none=True)
        assert d["fin_height"] == "3mm"
        assert d["fin_orientation"] == "x_oriented"
        assert d["fin_thickness"] == "0.2mm"

    def test_get_attributes_excludes_none(self):
        hs = CfgHeatSink(fin_height="3mm")
        attrs = hs.get_attributes()
        assert "fin_height" in attrs
        assert "fin_base_height" not in attrs

    def test_get_attributes_with_exclude(self):
        hs = CfgHeatSink(fin_height="3mm", fin_spacing="1mm")
        attrs = hs.get_attributes(exclude=["fin_spacing"])
        # get_attributes on CfgHeatSink ignores the exclude arg (passes to model_dump)
        assert "fin_height" in attrs


class TestPackageDefinitionConfig:
    def test_minimal(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA_256")
        d = pkg.model_dump(exclude_none=True)
        assert d["name"] == "PKG1"
        assert d["component_definition"] == "BGA_256"
        assert set(d.keys()) <= {"name", "component_definition", "components"}

    def test_with_thermal_properties(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA_256", maximum_power="5W", theta_jb="10C/W")
        d = pkg.model_dump(exclude_none=True)
        assert d["maximum_power"] == "5W"
        assert d["theta_jb"] == "10C/W"

    def test_with_heatsink(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA_256")
        hs = pkg.set_heatsink(fin_height="3mm", fin_spacing="1mm")
        assert isinstance(hs, CfgHeatSink)
        d = pkg.model_dump(exclude_none=True)
        assert "heatsink" in d
        assert d["heatsink"]["fin_height"] == "3mm"

    def test_set_heatsink_all_params(self):
        pkg = CfgPackage(name="P", component_definition="D")
        hs = pkg.set_heatsink(
            fin_base_height="0.5mm",
            fin_height="3mm",
            fin_orientation="x_oriented",
            fin_spacing="1mm",
            fin_thickness="0.2mm",
        )
        assert hs.fin_orientation == "x_oriented"
        assert hs.fin_thickness == "0.2mm"

    def test_apply_to_all(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA", apply_to_all=True)
        d = pkg.model_dump(exclude_none=True)
        assert d["apply_to_all"] is True

    def test_explicit_components(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA", apply_to_all=False, components=["U1", "U2"])
        d = pkg.model_dump(exclude_none=True)
        assert d["components"] == ["U1", "U2"]

    def test_empty_heatsink_not_emitted(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA")
        # no set_heatsink call → no heatsink key
        assert "heatsink" not in pkg.model_dump(exclude_none=True)

    def test_heatsink_from_cfgheatsink_instance(self):
        """Passing a CfgHeatSink instance directly works."""
        pkg = CfgPackage(
            name="P",
            component_definition="D",
            heatsink=CfgHeatSink(fin_height="3mm", fin_spacing="1mm"),
        )
        assert isinstance(pkg.heatsink, CfgHeatSink)
        assert pkg.heatsink.fin_height == "3mm"

    def test_heatsink_from_raw_dict(self):
        """Pydantic v2 natively coerces a raw dict to CfgHeatSink (no custom validator needed)."""
        pkg = CfgPackage.model_validate({"name": "P", "component_definition": "D", "heatsink": {"fin_height": "3mm"}})
        assert isinstance(pkg.heatsink, CfgHeatSink)
        assert pkg.heatsink.fin_height == "3mm"

    def test_coerce_heatsink_empty_dict_stays_none(self):
        """An empty heatsink dict is not coerced — results in an empty CfgHeatSink."""
        pkg = CfgPackage(name="P", component_definition="D", heatsink=CfgHeatSink())
        assert isinstance(pkg.heatsink, CfgHeatSink)
        assert pkg.heatsink.fin_height is None

    def test_get_attributes_excludes_protected(self):
        pkg = CfgPackage(name="P", component_definition="D", maximum_power="5W", theta_jb="10C/W")
        attrs = pkg.get_attributes()
        assert "maximum_power" in attrs
        assert "theta_jb" in attrs
        assert "name" not in attrs
        assert "component_definition" not in attrs
        assert "heatsink" not in attrs

    def test_get_attributes_with_extra_exclude(self):
        pkg = CfgPackage(name="P", component_definition="D", maximum_power="5W", theta_jb="10C/W")
        attrs = pkg.get_attributes(exclude=["maximum_power"])
        assert "maximum_power" not in attrs
        assert "theta_jb" in attrs

    def test_get_attributes_with_exclude_list(self):
        pkg = CfgPackage(name="P", component_definition="D", maximum_power="5W", theta_jb="10C/W")
        attrs = pkg.get_attributes(exclude=["maximum_power", "theta_jb"])
        assert "maximum_power" not in attrs
        assert "theta_jb" not in attrs

    def test_set_attributes_on_mock(self):
        pkg = CfgPackage(name="P", component_definition="D", maximum_power="5W")
        mock_obj = MagicMock(spec=["maximum_power"])
        pkg.set_attributes(mock_obj)
        mock_obj.__setattr__("maximum_power", "5W")

    def test_set_attributes_raises_on_invalid_attr(self):
        pkg = CfgPackage(name="P", component_definition="D", maximum_power="5W")
        mock_obj = MagicMock(spec=[])  # no attributes
        with pytest.raises(AttributeError):
            pkg.set_attributes(mock_obj)

    def test_extent_bounding_box(self):
        pkg = CfgPackage(name="P", component_definition="D", extent_bounding_box={"x": 1, "y": 2})
        d = pkg.model_dump(exclude_none=True)
        assert d["extent_bounding_box"] == {"x": 1, "y": 2}


class TestPackageDefinitionsConfig:
    def test_empty(self):
        assert CfgPackageDefinitions().packages == []

    def test_init_from_data(self):
        data = [{"name": "PKG1", "component_definition": "BGA"}]
        pc = CfgPackageDefinitions(data=data)
        assert len(pc.packages) == 1
        assert pc.packages[0].name == "PKG1"

    def test_init_from_data_with_heatsink(self):
        data = [{"name": "P", "component_definition": "D", "heatsink": CfgHeatSink(fin_height="3mm")}]
        pc = CfgPackageDefinitions(data=data)
        assert isinstance(pc.packages[0].heatsink, CfgHeatSink)

    def test_add(self):
        pc = CfgPackageDefinitions()
        pkg = pc.add("PKG1", "BGA_256", maximum_power="5W")
        assert isinstance(pkg, CfgPackage)
        lst = [p.model_dump(exclude_none=True) for p in pc.packages]
        assert len(lst) == 1
        assert lst[0]["name"] == "PKG1"

    def test_add_all_explicit_params(self):
        pc = CfgPackageDefinitions()
        pkg = pc.add(
            name="PKG1",
            component_definition="BGA_256",
            apply_to_all=True,
            maximum_power="5W",
            thermal_conductivity="0.3W/mK",
            theta_jb="10C/W",
            theta_jc="5C/W",
            height="1mm",
        )
        d = pkg.model_dump(exclude_none=True)
        assert d["maximum_power"] == "5W"
        assert d["thermal_conductivity"] == "0.3W/mK"
        assert d["theta_jb"] == "10C/W"
        assert d["theta_jc"] == "5C/W"
        assert d["height"] == "1mm"

    def test_add_with_components(self):
        pc = CfgPackageDefinitions()
        pkg = pc.add("P", "D", components=["U1", "U2"])
        assert pkg.components == ["U1", "U2"]

    def test_add_with_extent_bounding_box(self):
        pc = CfgPackageDefinitions()
        pkg = pc.add("P", "D", extent_bounding_box={"x": 1})
        assert pkg.extent_bounding_box == {"x": 1}

    def test_multiple(self):
        pc = CfgPackageDefinitions()
        pc.add("P1", "DEF1")
        pc.add("P2", "DEF2", theta_jc="5C/W")
        assert len(pc.packages) == 2

    def test_add_then_set_heatsink(self):
        pc = CfgPackageDefinitions()
        pkg = pc.add("P", "D")
        pkg.set_heatsink(fin_height="2mm")
        assert pc.packages[0].heatsink.fin_height == "2mm"
