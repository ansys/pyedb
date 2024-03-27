# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Tests related to Edb
"""

import os

import pytest

from pyedb.dotnet.edb import Edb
from src.pyedb.dotnet.edb_core.materials import Material, MaterialProperties
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]

PROPERTIES = ("conductivity", "dielectric_loss_tangent", "magnetic_loss_tangent", "mass_density",
                          "permittivity", "permeability", "poisson_ratio", "specific_heat",
                          "thermal_conductivity", "youngs_modulus", "thermal_expansion_coefficient")
DC_PROPERTIES = ("dielectric_model_frequency", "loss_tangent_at_frequency", "permittivity_at_frequency", "dc_conductivity", "dc_permittivity")
FLOAT_VALUE = 12.
INT_VALUE = 12
STR_VALUE = "12"
VALUES = (FLOAT_VALUE, INT_VALUE, STR_VALUE)
MATERIAL_NAME = "dummy_material"

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.definition = self.edbapp.edb_api.definition

    def test_material_name(self):
        """Evaluate material properties."""
        material_def = self.edbapp.edb_api.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material = Material(self.edbapp, material_def)

        assert MATERIAL_NAME == material.name

        material_def.Delete()

    def test_material_properties(self):
        """Evaluate material properties."""
        material_def = self.edbapp.edb_api.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material = Material(self.edbapp, material_def)

        for property in PROPERTIES:
            for value in VALUES:
                setattr(material, property, value)
                assert float(value) == getattr(material, property)

        material_def.Delete()

    def test_material_dc_properties(self):
        """Evaluate material DC properties."""
        material_def = self.edbapp.edb_api.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material_model = self.definition.DjordjecvicSarkarModel()
        material_def.SetDielectricMaterialModel(material_model)
        material = Material(self.edbapp, material_def)

        for property in DC_PROPERTIES:
            for value in (INT_VALUE, FLOAT_VALUE):
                setattr(material, property, value)
                assert float(value) == getattr(material, property)
            # NOTE: Other properties do not accept EDB calls with string value
            if property == "loss_tangent_at_frequency":
                setattr(material, property, STR_VALUE)
                assert float(STR_VALUE) == getattr(material, property)
        
        material_def.Delete()

    def test_material_to_dict(self):
        """Evaluate material convertion into a dictionary."""
        material_def = self.edbapp.edb_api.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material_model = self.definition.DjordjecvicSarkarModel()
        material_def.SetDielectricMaterialModel(material_model)
        material = Material(self.edbapp, material_def)
        for property in PROPERTIES + DC_PROPERTIES:
            setattr(material, property, FLOAT_VALUE)
        material_dict = material.to_dict() 
        expected_result = MaterialProperties(**{field: FLOAT_VALUE for field in MaterialProperties.__annotations__}).model_dump()
        expected_result["name"] = MATERIAL_NAME

        assert expected_result == material_dict
        
        material_def.Delete()

    def test_material_update_properties(self):
        """Evaluate material properties update."""
        material_def = self.edbapp.edb_api.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material_model = self.definition.DjordjecvicSarkarModel()
        material_def.SetDielectricMaterialModel(material_model)
        material = Material(self.edbapp, material_def)
        for property in PROPERTIES + DC_PROPERTIES:
            setattr(material, property, FLOAT_VALUE)
        expected_value = FLOAT_VALUE + 1

        material_dict = MaterialProperties(**{field: expected_value for field in MaterialProperties.__annotations__}).model_dump()
        material.update(material_dict)
        for property in PROPERTIES + DC_PROPERTIES:
            assert expected_value == getattr(material, property)

        material_def.Delete()

