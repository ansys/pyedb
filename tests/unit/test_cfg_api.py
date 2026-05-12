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

from pyedb.configuration.cfg_package_definition import CfgHeatSink, CfgPackage, CfgPackageDefinitions

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestPackageDefinitionConfig:
    def test_minimal(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA_256")
        d = pkg.to_dict()
        assert d == {"name": "PKG1", "component_definition": "BGA_256"}

    def test_with_thermal_properties(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA_256", maximum_power="5W", theta_jb="10C/W")
        d = pkg.to_dict()
        assert d["maximum_power"] == "5W"
        assert d["theta_jb"] == "10C/W"

    def test_with_heatsink(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA_256")
        hs = pkg.set_heatsink(fin_height="3mm", fin_spacing="1mm")
        assert isinstance(hs, CfgHeatSink)
        d = pkg.to_dict()
        assert "heatsink" in d
        assert d["heatsink"]["fin_height"] == "3mm"

    def test_apply_to_all(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA", apply_to_all=True)
        d = pkg.to_dict()
        assert d["apply_to_all"] is True

    def test_explicit_components(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA", apply_to_all=False, components=["U1", "U2"])
        d = pkg.to_dict()
        assert d["components"] == ["U1", "U2"]

    def test_empty_heatsink_not_emitted(self):
        pkg = CfgPackage(name="PKG1", component_definition="BGA")
        # no set_heatsink call → no heatsink key
        assert "heatsink" not in pkg.to_dict()


class TestPackageDefinitionsConfig:
    def test_empty(self):
        assert CfgPackageDefinitions().to_list() == []

    def test_add(self):
        pc = CfgPackageDefinitions()
        pkg = pc.add("PKG1", "BGA_256", maximum_power="5W")
        assert isinstance(pkg, CfgPackage)
        lst = pc.to_list()
        assert len(lst) == 1
        assert lst[0]["name"] == "PKG1"

    def test_add_all_explicit_params(self):
        """PackageDefinitionsConfig.add exposes all thermal fields explicitly."""
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
        d = pkg.to_dict()
        assert d["maximum_power"] == "5W"
        assert d["thermal_conductivity"] == "0.3W/mK"
        assert d["theta_jb"] == "10C/W"
        assert d["theta_jc"] == "5C/W"
        assert d["height"] == "1mm"

    def test_multiple(self):
        pc = CfgPackageDefinitions()
        pc.add("P1", "DEF1")
        pc.add("P2", "DEF2", theta_jc="5C/W")
        assert len(pc.to_list()) == 2
