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

from pyedb.dotnet.database.materials import (
    PERMEABILITY_DEFAULT_VALUE,
    Material,
    MaterialProperties,
    Materials,
)
from tests.conftest import local_path

pytestmark = [pytest.mark.system, pytest.mark.legacy]

PROPERTIES = (
    "conductivity",
    "dielectric_loss_tangent",
    "magnetic_loss_tangent",
    "mass_density",
    "permittivity",
    "permeability",
    "poisson_ratio",
    "specific_heat",
    "thermal_conductivity",
    "youngs_modulus",
    "thermal_expansion_coefficient",
)
DC_PROPERTIES = (
    "dielectric_model_frequency",
    "loss_tangent_at_frequency",
    "permittivity_at_frequency",
    "dc_conductivity",
    "dc_permittivity",
)
FLOAT_VALUE = 12.0
INT_VALUE = 12
STR_VALUE = "12"
VALUES = (FLOAT_VALUE, INT_VALUE, STR_VALUE)
MATERIAL_NAME = "DummyMaterial"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app_without_material):
        self.edbapp = legacy_edb_app_without_material
        self.definition = self.edbapp.core.definition

        # Remove dummy material if it exist
        material_def = self.definition.MaterialDef.FindByName(self.edbapp.active_db, MATERIAL_NAME)
        if not material_def.IsNull():
            material_def.Delete()

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def teardown_class(cls, request, edb_examples):
        yield
        # not elegant way to ensure the EDB grpc is closed after all tests
        edb = edb_examples.create_empty_edb()
        edb.close_edb()

    def test_material_name(self):
        """Evaluate material properties."""
        material_def = self.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material = Material(self.edbapp, material_def)

        assert MATERIAL_NAME == material.name

    def test_material_properties(self):
        """Evaluate material properties."""
        material_def = self.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material = Material(self.edbapp, material_def)

        for property in PROPERTIES:
            for value in VALUES:
                setattr(material, property, value)
                assert float(value) == getattr(material, property)
        assert 12 == material.loss_tangent

    def test_material_dc_properties(self):
        """Evaluate material DC properties."""
        material_def = self.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
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

    def test_material_to_dict(self):
        """Evaluate material conversion into a dictionary."""
        material_def = self.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material = Material(self.edbapp, material_def)
        for property in PROPERTIES:
            setattr(material, property, FLOAT_VALUE)
        expected_result = MaterialProperties(
            **{field: FLOAT_VALUE for field in MaterialProperties.__annotations__}
        ).model_dump()
        expected_result["name"] = MATERIAL_NAME
        # Material without DC model has None value for each DC properties
        for property in DC_PROPERTIES:
            expected_result[property] = None

        material_dict = material.to_dict()
        assert expected_result == material_dict

    def test_material_with_dc_model_to_dict(self):
        """Evaluate material conversion into a dictionary."""
        material_def = self.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material_model = self.definition.DjordjecvicSarkarModel()
        material_def.SetDielectricMaterialModel(material_model)
        material = Material(self.edbapp, material_def)
        for property in DC_PROPERTIES:
            setattr(material, property, FLOAT_VALUE)
        expected_result = MaterialProperties(
            **{field: FLOAT_VALUE for field in MaterialProperties.__annotations__}
        ).model_dump()
        expected_result["name"] = MATERIAL_NAME

        material_dict = material.to_dict()
        for property in DC_PROPERTIES:
            assert expected_result[property] == material_dict[property]

    def test_material_update_properties(self):
        """Evaluate material properties update."""
        material_def = self.definition.MaterialDef.Create(self.edbapp.active_db, MATERIAL_NAME)
        material = Material(self.edbapp, material_def)
        for property in PROPERTIES:
            setattr(material, property, FLOAT_VALUE)
        expected_value = FLOAT_VALUE + 1
        material_dict = MaterialProperties(
            **{field: expected_value for field in MaterialProperties.__annotations__}
        ).model_dump()

        material.update(material_dict)
        for property in PROPERTIES + DC_PROPERTIES:
            assert expected_value == getattr(material, property)

    def test_materials_syslib(self):
        """Evaluate system library."""
        materials = Materials(self.edbapp)

        assert materials.syslib

    def test_materials_materials(self):
        """Evaluate materials."""
        materials = Materials(self.edbapp)

        assert not materials.materials

    def test_materials_add_material(self):
        """Evalue add material."""
        materials = Materials(self.edbapp)

        material = materials.add_material(MATERIAL_NAME, permittivity=12)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_material(MATERIAL_NAME, permittivity=12)

    def test_materials_add_conductor_material(self):
        """Evalue add conductor material."""
        materials = Materials(self.edbapp)

        material = materials.add_conductor_material(MATERIAL_NAME, 12, permittivity=12)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == 0.999991
        with pytest.raises(ValueError):
            materials.add_conductor_material(MATERIAL_NAME, 12, permittivity=12)

    def test_materials_add_dielectric_material(self):
        """Evalue add dielectric material."""
        materials = Materials(self.edbapp)

        material = materials.add_dielectric_material(MATERIAL_NAME, 12, 12, conductivity=12)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_dielectric_material(MATERIAL_NAME, 12, 12, conductivity=12)

    def test_materials_add_djordjevicsarkar_dielectric(self):
        """Evalue add djordjevicsarkar dielectric material."""
        materials = Materials(self.edbapp)

        material = materials.add_djordjevicsarkar_dielectric(
            MATERIAL_NAME, 4.3, 0.02, 9, dc_conductivity=1e-12, dc_permittivity=5, conductivity=0
        )
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_djordjevicsarkar_dielectric(
                MATERIAL_NAME, 4.3, 0.02, 9, dc_conductivity=1e-12, dc_permittivity=5, conductivity=0
            )

    def test_materials_add_debye_material(self):
        """Evalue add debye material material."""
        materials = Materials(self.edbapp)

        material = materials.add_debye_material(MATERIAL_NAME, 6, 4, 0.02, 0.05, 1e9, 10e9, conductivity=0)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_debye_material(MATERIAL_NAME, 6, 4, 0.02, 0.05, 1e9, 10e9, conductivity=0)

    def test_materials_add_multipole_debye_material(self):
        """Evalue add multipole debye material."""
        materials = Materials(self.edbapp)
        frequencies = [0, 2, 3, 4, 5, 6]
        relative_permitivities = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
        loss_tangents = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]

        material = materials.add_multipole_debye_material(
            MATERIAL_NAME, frequencies, relative_permitivities, loss_tangents, conductivity=0
        )
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_multipole_debye_material(
                MATERIAL_NAME, frequencies, relative_permitivities, loss_tangents, conductivity=0
            )

    def test_materials_duplicate(self):
        """Evalue duplicate material."""
        materials = Materials(self.edbapp)
        kwargs = MaterialProperties(**{field: 12 for field in MaterialProperties.__annotations__}).model_dump()
        material = materials.add_material(MATERIAL_NAME, **kwargs)
        other_name = "OtherMaterial"

        new_material = materials.duplicate(MATERIAL_NAME, other_name)
        for mat_attribute in PROPERTIES:
            assert getattr(material, mat_attribute) == getattr(new_material, mat_attribute)
        with pytest.raises(ValueError):
            materials.duplicate(MATERIAL_NAME, other_name)

    def test_materials_delete_material(self):
        """Evaluate delete material."""
        materials = Materials(self.edbapp)

        _ = materials.add_material(MATERIAL_NAME)
        materials.delete_material(MATERIAL_NAME)
        assert MATERIAL_NAME not in materials
        with pytest.raises(ValueError):
            materials.delete_material(MATERIAL_NAME)

    def test_materials_material_property_to_id(self):
        """Evaluate materials map between material property and id."""
        materials = Materials(self.edbapp)
        permittivity_id = self.edbapp.core.definition.MaterialPropertyId.Permittivity
        invalid_id = self.edbapp.core.definition.MaterialPropertyId.InvalidProperty

        assert permittivity_id == materials.material_property_to_id("permittivity")
        assert invalid_id == materials.material_property_to_id("azertyuiop")

    def test_material_load_amat(self):
        """Evaluate load material from an AMAT file."""
        materials = Materials(self.edbapp)
        nb_materials = len(materials.materials)
        mat_file = os.path.join(self.edbapp.base_path, "syslib", "Materials.amat")

        assert materials.load_amat(mat_file)
        assert nb_materials != len(materials.materials)
        assert 0.0013 == materials["Rogers RO3003 (tm)"].dielectric_loss_tangent
        assert 3.0 == materials["Rogers RO3003 (tm)"].permittivity

    def test_materials_read_materials(self):
        """Evaluate read materials."""
        materials = Materials(self.edbapp)
        mat_file = os.path.join(local_path, "example_models", "syslib", "Materials.amat")
        name_to_material = materials.read_materials(mat_file)

        key = "FC-78"
        assert key in name_to_material
        assert name_to_material[key]["thermal_conductivity"] == 0.062
        assert name_to_material[key]["mass_density"] == 1700
        assert name_to_material[key]["specific_heat"] == 1050
        assert name_to_material[key]["thermal_expansion_coefficient"] == 0.0016
        key = "Polyflon CuFlon (tm)"
        assert key in name_to_material
        assert name_to_material[key]["permittivity"] == 2.1
        assert name_to_material[key]["dielectric_loss_tangent"] == 0.00045
        key = "Water(@360K)"
        assert key in name_to_material
        assert name_to_material[key]["thermal_conductivity"] == 0.6743
        assert name_to_material[key]["mass_density"] == 967.4
        assert name_to_material[key]["specific_heat"] == 4206
        assert name_to_material[key]["thermal_expansion_coefficient"] == 0.0006979
        key = "steel_stainless"
        assert name_to_material[key]["conductivity"] == 1100000
        assert name_to_material[key]["thermal_conductivity"] == 13.8
        assert name_to_material[key]["mass_density"] == 8055
        assert name_to_material[key]["specific_heat"] == 480
        assert name_to_material[key]["thermal_expansion_coefficient"] == 1.08e-005

    def test_materials_load_conductor_material(self):
        """Load conductor material."""
        materials = Materials(self.edbapp)
        conductor_material_properties = {"name": MATERIAL_NAME, "conductivity": 2e4}

        assert MATERIAL_NAME not in materials
        materials.load_material(conductor_material_properties)
        material = materials[MATERIAL_NAME]
        assert 2e4 == material.conductivity

    def test_materials_load_dielectric_material(self):
        """Load dielectric material."""
        materials = Materials(self.edbapp)
        dielectric_material_properties = {"name": MATERIAL_NAME, "permittivity": 12, "loss_tangent": 0.00045}

        assert MATERIAL_NAME not in materials
        materials.load_material(dielectric_material_properties)
        material = materials[MATERIAL_NAME]
        assert 0.00045 == material.loss_tangent
        assert 0.00045 == material.dielectric_loss_tangent
        assert 12 == material.permittivity

    def test_update_materials_from_syslib(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edbapp.materials.update_materials_from_sys_library(False, "copper")
        assert edbapp.materials["copper"].thermal_conductivity == 400
        edbapp.materials["FR4_epoxy"].thermal_conductivity = 1
        edbapp.materials.update_materials_from_sys_library()
        edbapp.materials["FR4_epoxy"].thermal_conductivity = 0.294
        edbapp.close(terminate_rpc_session=False)

    def test_material_thermal_modifier(self):
        THERMAL_MODIFIER = {
            "basic_quadratic_temperature_reference": 21,
            "basic_quadratic_c1": 0.1,
            "basic_quadratic_c2": 0.1,
            "advanced_quadratic_lower_limit": -270,
            "advanced_quadratic_upper_limit": 1001,
            "advanced_quadratic_auto_calculate": False,
            "advanced_quadratic_lower_constant": 1.1,
            "advanced_quadratic_upper_constant": 1.1,
        }
        material_def = self.definition.MaterialDef.Create(self.edbapp.active_db, "new_matttt")
        material = Material(self.edbapp, material_def)
        material.conductivity = 5.7e8
        assert material.set_thermal_modifier("conductivity", **THERMAL_MODIFIER)
