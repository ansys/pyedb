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
from pathlib import Path

import pytest

from tests.conftest import example_models_path

from pyedb.xml_parser.xml_parser import XmlParser

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edb_examples, request):
        edb_examples._create_test_folder(request.node.name)
        self.xml_file = example_models_path / "unit_test_xml_parser" / "ANSYS-SI-Verse-PCB_V1_1_CONTROL.xml"

    def test_create(self, edb_examples):
        xml_parser = XmlParser()
        xml_stackup = xml_parser.add_stackup()
        xml_materials = xml_stackup.add_materials()

        xml_materials.add_material(
            name="copper",
            conductivity=5.8e7,
        )
        assert xml_parser.stackup.materials.material[0].conductivity.value == 5.8e7

        xml_materials.add_material(
            name="fr4",
            permittivity=4.5,
            loss_tangent=0.02,
        )
        assert xml_parser.stackup.materials.material[1].permittivity.value == 4.5

        xml_layers = xml_stackup.add_layers()
        xml_layers.add_layer(
            name="Layer_TOP",
            type="signal",
            thickness=0.035,
            material="copper",
        )
        assert xml_parser.stackup.layers.layer[0].name == "Layer_TOP"

        xml_layers.add_layer(
            name="Dielectric_1",
            type="dielectric",
            thickness=0.2,
            material="fr4",
        )
        assert xml_parser.stackup.layers.layer[1].material == "fr4"

        assert Path(xml_parser.to_xml_file(Path(edb_examples.test_folder) / "test_xml_parser_create.xml")).exists()


    def test_load_from_xml(self):
        xml_parser = XmlParser.load_xml_file(self.xml_file)

        assert len(xml_parser.stackup.materials.material) == 8
        assert xml_parser.stackup.materials.material[1].name == "copper"

        assert len(xml_parser.stackup.layers.layer) == 20
        assert xml_parser.stackup.layers.layer[0].name == "top_soldermask"

    def test_load_from_cfg(self):
        from pyedb.configuration.cfg_data import CfgStackup

        xml_parser1 = XmlParser.load_xml_file(self.xml_file)
        stackup_data = xml_parser1.stackup.to_dict()

        xml_parser2 = XmlParser()
        xml_parser2.add_stackup()
        xml_parser2.stackup.import_from_cfg_stackup(CfgStackup(**stackup_data))
        assert len(xml_parser2.stackup.materials.material) == 8
        assert len(xml_parser2.stackup.layers.layer) == 20

