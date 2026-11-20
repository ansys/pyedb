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

"""Tests related to Edb"""

import math
import os

import pytest

from pyedb.configuration.cfg_stackup import MaterialProperties

# PERMEABILITY_DEFAULT_VALUE is 1 in both dotnet and grpc implementations
PERMEABILITY_DEFAULT_VALUE = 1

from tests.conftest import config, local_path

pytestmark = [pytest.mark.system, pytest.mark.legacy]
from tests.system.base_test_class import BaseTestClass

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


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_material_name(self):
        """Evaluate material properties."""
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material(MATERIAL_NAME)
        assert MATERIAL_NAME == material.name
        edbapp.close(terminate_rpc_session=False)

    def test_material_properties(self):
        """Evaluate material properties."""
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material(MATERIAL_NAME)
        for property in PROPERTIES:
            for value in VALUES:
                setattr(material, property, value)
                assert float(value) == getattr(material, property)
        assert 12 == material.dielectric_loss_tangent
        edbapp.close(terminate_rpc_session=False)

    def test_material_to_dict(self):
        """Evaluate material conversion into a dictionary."""
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material(MATERIAL_NAME)
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
        edbapp.close(terminate_rpc_session=False)

    def test_material_with_dc_model_to_dict(self):
        """Evaluate material conversion into a dictionary."""
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material(MATERIAL_NAME)
        material.set_djordjecvic_sarkar_model()
        for property in DC_PROPERTIES:
            setattr(material, property, FLOAT_VALUE)
        expected_result = MaterialProperties(
            **{field: FLOAT_VALUE for field in MaterialProperties.__annotations__}
        ).model_dump()
        expected_result["name"] = MATERIAL_NAME

        material_dict = material.to_dict()
        for property in DC_PROPERTIES:
            if property in material_dict:
                # checking values only because grpc does not return default values like DotNet
                assert expected_result[property] == material_dict[property]
        edbapp.close(terminate_rpc_session=False)

    def test_material_update_properties(self):
        """Evaluate material properties update."""
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material(MATERIAL_NAME)
        for property in PROPERTIES:
            setattr(material, property, FLOAT_VALUE)
        expected_value = FLOAT_VALUE + 1
        material_dict = MaterialProperties(
            **{field: expected_value for field in MaterialProperties.__annotations__ if field not in DC_PROPERTIES}
        ).model_dump()

        material.update(material_dict)
        for property in PROPERTIES:
            assert expected_value == getattr(material, property)
        edbapp.close(terminate_rpc_session=False)

    def test_materials_syslib(self):
        """Evaluate system library."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        assert materials.syslib
        edbapp.close(terminate_rpc_session=False)

    def test_materials_materials(self):
        """Evaluate materials."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        assert not materials.materials
        edbapp.close(terminate_rpc_session=False)

    def test_materials_add_material(self):
        """Evalue add material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        material = materials.add_material(MATERIAL_NAME, permittivity=12)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_material(MATERIAL_NAME, permittivity=12)
        edbapp.close(terminate_rpc_session=False)

    def test_materials_add_conductor_material(self):
        """Evalue add conductor material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        material = materials.add_conductor_material(MATERIAL_NAME, 12, permittivity=12)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert round(material.permeability, 3) == 1.0
        with pytest.raises(ValueError):
            materials.add_conductor_material(MATERIAL_NAME, 12, permittivity=12)
        edbapp.close(terminate_rpc_session=False)

    def test_materials_add_dielectric_material(self):
        """Evalue add dielectric material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        material = materials.add_dielectric_material(MATERIAL_NAME, 12, 12, conductivity=12)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_dielectric_material(MATERIAL_NAME, 12, 12, conductivity=12)
        edbapp.close(terminate_rpc_session=False)

    def test_materials_add_djordjevicsarkar_dielectric(self):
        """Evalue add djordjevicsarkar dielectric material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
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
        materials[MATERIAL_NAME].conductivity = 1e6
        assert not materials[MATERIAL_NAME].conductivity == 1e6
        edbapp.close(terminate_rpc_session=False)

    def test_materials_add_debye_material(self):
        """Evalue add debye material material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        material = materials.add_debye_material(MATERIAL_NAME, 6, 4, 0.02, 0.05, 1e9, 10e9, conductivity=0)
        assert material
        assert material.name == materials[MATERIAL_NAME].name
        # Check default values
        assert material.permeability == PERMEABILITY_DEFAULT_VALUE
        with pytest.raises(ValueError):
            materials.add_debye_material(MATERIAL_NAME, 6, 4, 0.02, 0.05, 1e9, 10e9, conductivity=0)
        edbapp.close(terminate_rpc_session=False)

    def test_materials_add_multipole_debye_material(self):
        """Evalue add multipole debye material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
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
        edbapp.close(terminate_rpc_session=False)

    def test_materials_duplicate(self):
        """Evalue duplicate material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        kwargs = MaterialProperties(**{field: 12 for field in MaterialProperties.__annotations__}).model_dump()
        material = materials.add_material(MATERIAL_NAME, **kwargs)
        other_name = "OtherMaterial"

        new_material = materials.duplicate(MATERIAL_NAME, other_name)
        for mat_attribute in PROPERTIES:
            assert getattr(material, mat_attribute) == getattr(new_material, mat_attribute)
        with pytest.raises(ValueError):
            materials.duplicate(MATERIAL_NAME, other_name)
        edbapp.close(terminate_rpc_session=False)

    def test_materials_delete_material(self):
        """Evaluate delete material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        _ = materials.add_material(MATERIAL_NAME)
        materials.delete_material(MATERIAL_NAME)
        assert MATERIAL_NAME not in materials
        with pytest.raises(ValueError):
            materials.delete_material(MATERIAL_NAME)
        edbapp.close(terminate_rpc_session=False)

    def test_material_load_amat(self):
        """Evaluate load material from an AMAT file."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        nb_materials = len(materials.materials)
        mat_file = os.path.join(edbapp.base_path, "syslib", "Materials.amat")

        assert materials.load_amat(mat_file)
        assert nb_materials != len(materials.materials)
        assert 0.0013 == materials["Rogers RO3003 (tm)"].dielectric_loss_tangent
        assert 3.0 == materials["Rogers RO3003 (tm)"].permittivity
        edbapp.close(terminate_rpc_session=False)

    def test_materials_read_materials(self):
        """Evaluate read materials."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
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
        edbapp.close(terminate_rpc_session=False)

    def test_materials_load_conductor_material(self):
        """Load conductor material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        conductor_material_properties = {"name": MATERIAL_NAME, "conductivity": 2e4}

        assert MATERIAL_NAME not in materials
        materials.load_material(conductor_material_properties)
        material = materials[MATERIAL_NAME]
        assert 2e4 == material.conductivity
        edbapp.close(terminate_rpc_session=False)

    def test_materials_load_dielectric_material(self):
        """Load dielectric material."""
        edbapp = self.edb_examples.create_empty_edb()
        materials = edbapp.materials
        dielectric_material_properties = {"name": MATERIAL_NAME, "permittivity": 12, "loss_tangent": 0.00045}

        assert MATERIAL_NAME not in materials
        materials.load_material(dielectric_material_properties)
        material = materials[MATERIAL_NAME]
        material.dielectric_loss_tangent = 0.00045
        assert material.dielectric_loss_tangent == 0.00045
        assert 12 == material.permittivity
        edbapp.close(terminate_rpc_session=False)

    def test_update_materials_from_syslib(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.materials.add_material("copper")
        edbapp.materials.update_materials_from_sys_library(False, "copper")
        assert edbapp.materials["copper"].thermal_conductivity == 400
        edbapp.materials.add_material("FR4_epoxy")
        edbapp.materials.update_materials_from_sys_library()
        edbapp.materials["FR4_epoxy"].thermal_conductivity = 0.294
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config.use_grpc, reason="Causing memory violation")
    def test_material_thermal_modifier(self):
        edbapp = self.edb_examples.create_empty_edb()
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
        material = edbapp.materials.add_material("new_material")
        material.conductivity = 5.7e8
        assert material.set_thermal_modifier("conductivity", **THERMAL_MODIFIER)
        edbapp.close(terminate_rpc_session=False)


@pytest.mark.skipif(not config.use_grpc, reason="Material equations are only supported by the gRPC backend")
class TestMaterialEquations(BaseTestClass):
    PERMITTIVITY_EQUATION = "3.24799+0.00785013*ln((2.53303e+22+Freq*Freq)/(1.93339e+09+Freq*Freq))"
    CONDUCTIVITY_EQUATION = "1e-12+8.73444e-13*Freq*(atan(Freq/43970.3)-atan(Freq/1.59155e+11))"
    XML_CONTENT = f"""<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<c:Control xmlns:c="http://www.ansys.com/control" schemaVersion="1.0">
  <Stackup schemaVersion="1.0">
    <Materials>
      <Material Name="AIR">
        <Permittivity><Double>1</Double></Permittivity>
        <Permeability><Double>1</Double></Permeability>
        <DielectricLossTangent><Double>0</Double></DielectricLossTangent>
      </Material>
      <Material Name="COPPER_LEGACY">
        <Conductivity><Double>58000000</Double></Conductivity>
      </Material>
      <Material Name="GL107_Nom">
        <Permittivity><Equation>{PERMITTIVITY_EQUATION}</Equation></Permittivity>
        <Conductivity><Equation>{CONDUCTIVITY_EQUATION}</Equation></Conductivity>
        <DielectricLossTangent><Double>0</Double></DielectricLossTangent>
        <MagneticLossTangent><Double>0</Double></MagneticLossTangent>
      </Material>
    </Materials>
    <Layers LengthUnit="um">
      <Layer Color="#d63b07" FillMaterial="GL107_Nom" Material="COPPER_LEGACY" Name="TOP"
             Thickness="18" Type="conductor"/>
      <Layer Color="#44614c" Material="GL107_Nom" Name="DIEL" Thickness="30" Type="dielectric"/>
      <Layer Color="#5c4300" FillMaterial="GL107_Nom" Material="COPPER_LEGACY" Name="BOTTOM"
             Thickness="18" Type="conductor"/>
      <Layer Color="#88c36a" Name="Outline" Type="outline"/>
    </Layers>
  </Stackup>
</c:Control>
"""

    @staticmethod
    def _permittivity(frequency):
        return 3.24799 + 0.00785013 * math.log((2.53303e22 + frequency**2) / (1.93339e9 + frequency**2))

    @staticmethod
    def _conductivity(frequency):
        return 1e-12 + 8.73444e-13 * frequency * (math.atan(frequency / 43970.3) - math.atan(frequency / 1.59155e11))

    def _write_xml(self):
        xml_file = os.path.join(self.edb_examples.test_folder, "equation_stackup.xml")
        with open(xml_file, "w", encoding="utf-8") as f:
            f.write(self.XML_CONTENT)
        return xml_file

    def test_material_equation_properties(self):
        """Set frequency dependent equations on dielectric properties."""
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material(MATERIAL_NAME)
        assert not material.is_frequency_dependent
        assert material.equations == {}

        material.set_property_equation("permittivity", self.PERMITTIVITY_EQUATION)
        material.set_property_equation("conductivity", self.CONDUCTIVITY_EQUATION)
        assert material.equations == {
            "permittivity": self.PERMITTIVITY_EQUATION,
            "conductivity": self.CONDUCTIVITY_EQUATION,
        }
        assert material.is_frequency_dependent
        assert material.get_property_equation("permittivity") == self.PERMITTIVITY_EQUATION
        assert material.get_property_equation("permeability") is None
        for frequency in (1e6, 1e9, 10e9):
            assert material.get_property_at_frequency("permittivity", frequency) == pytest.approx(
                self._permittivity(frequency), rel=1e-6
            )
            assert material.get_property_at_frequency("conductivity", frequency) == pytest.approx(
                self._conductivity(frequency), rel=1e-6
            )
        assert material.get_property_at_frequency("permittivity", "1GHz") == pytest.approx(
            self._permittivity(1e9), rel=1e-6
        )
        # Constant properties are returned as is
        assert material.get_property_at_frequency("permeability", 1e9) == PERMEABILITY_DEFAULT_VALUE
        # The equation is kept when the material is converted to a dictionary
        material_dict = material.to_dict()
        assert material_dict["permittivity"] == self.PERMITTIVITY_EQUATION
        assert material_dict["conductivity"] == self.CONDUCTIVITY_EQUATION

        material.permittivity = 4.4
        assert "permittivity" not in material.equations
        assert material.permittivity == 4.4
        edbapp.close(terminate_rpc_session=False)

    def test_material_equation_invalid_arguments(self):
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material(MATERIAL_NAME)
        with pytest.raises(ValueError):
            material.set_property_equation("unknown_property", "1+Freq")
        with pytest.raises(ValueError):
            material.set_property_equation("permittivity", "")
        with pytest.raises(ValueError):
            material.get_property_equation("unknown_property")
        edbapp.close(terminate_rpc_session=False)

    def test_add_material_with_equations(self):
        """Create materials with frequency dependent equations."""
        edbapp = self.edb_examples.create_empty_edb()
        dielectric = edbapp.materials.add_dielectric_material("ds_equation", self.PERMITTIVITY_EQUATION, 0.0)
        dielectric.conductivity = self.CONDUCTIVITY_EQUATION
        assert dielectric.is_frequency_dependent
        assert dielectric.permittivity == pytest.approx(self._permittivity(1e9), rel=1e-6)

        conductor = edbapp.materials.add_conductor_material("metal_equation", "5.8e7*(1-1e-12*Freq)")
        assert conductor.equations == {"conductivity": "5.8e7*(1-1e-12*Freq)"}
        assert conductor.get_property_at_frequency("conductivity", 1e9) == pytest.approx(5.8e7 * (1 - 1e-3))
        assert conductor.get_property_at_frequency("conductivity", 1e6) == pytest.approx(5.8e7 * (1 - 1e-6))
        edbapp.close(terminate_rpc_session=False)

    def test_materials_load_xml(self):
        """Load materials with equations from an XML file."""
        edbapp = self.edb_examples.create_empty_edb()
        xml_file = self._write_xml()
        materials = edbapp.materials.load_xml(xml_file)
        assert set(materials) == {"AIR", "COPPER_LEGACY", "GL107_Nom"}
        assert {"AIR", "COPPER_LEGACY", "GL107_Nom"} <= set(edbapp.materials.materials)

        material = edbapp.materials["GL107_Nom"]
        assert material.equations == {
            "permittivity": self.PERMITTIVITY_EQUATION,
            "conductivity": self.CONDUCTIVITY_EQUATION,
        }
        assert material.get_property_at_frequency("permittivity", 5e9) == pytest.approx(
            self._permittivity(5e9), rel=1e-6
        )
        assert material.get_property_at_frequency("conductivity", 5e9) == pytest.approx(
            self._conductivity(5e9), rel=1e-6
        )
        assert edbapp.materials["COPPER_LEGACY"].conductivity == 58000000
        assert edbapp.materials["AIR"].permittivity == 1
        assert not edbapp.materials["COPPER_LEGACY"].is_frequency_dependent

        # Existing materials are updated in place, unless overwrite is disabled
        material.permittivity = 4.4
        edbapp.materials.load_xml(xml_file, overwrite=False)
        assert "permittivity" not in edbapp.materials["GL107_Nom"].equations
        edbapp.materials.load_xml(xml_file)
        assert edbapp.materials["GL107_Nom"].equations["permittivity"] == self.PERMITTIVITY_EQUATION

        with pytest.raises(FileNotFoundError):
            edbapp.materials.load_xml(os.path.join(self.edb_examples.test_folder, "missing.xml"))
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_load_xml_with_equations(self):
        """Load a stackup XML file with frequency dependent materials."""
        edbapp = self.edb_examples.create_empty_edb()
        xml_file = self._write_xml()
        assert edbapp.stackup.load(xml_file)
        assert list(edbapp.stackup.layers) == ["TOP", "DIEL", "BOTTOM"]
        assert edbapp.stackup.layers["TOP"].material == "COPPER_LEGACY"
        assert edbapp.stackup.layers["DIEL"].material == "GL107_Nom"
        assert edbapp.materials["GL107_Nom"].equations["permittivity"] == self.PERMITTIVITY_EQUATION
        assert edbapp.materials["GL107_Nom"].equations["conductivity"] == self.CONDUCTIVITY_EQUATION
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_load_from_xml_with_equations(self):
        """Load a stackup XML file with the control file import."""
        edbapp = self.edb_examples.create_empty_edb()
        xml_file = self._write_xml()
        assert edbapp.stackup.load_from_xml(xml_file)
        assert {"TOP", "DIEL", "BOTTOM"} <= set(edbapp.stackup.layers)
        assert edbapp.stackup.layers["DIEL"].material == "GL107_Nom"
        assert edbapp.materials["GL107_Nom"].equations["permittivity"] == self.PERMITTIVITY_EQUATION
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_export_xml_with_equations(self):
        """Equations are preserved when the stackup is exported to XML."""
        from pyedb.xml_parser.xml_parser import XmlParser

        edbapp = self.edb_examples.create_empty_edb()
        assert edbapp.stackup.load_from_xml(self._write_xml())
        exported = os.path.join(self.edb_examples.test_folder, "exported_stackup.xml")
        assert edbapp.stackup.export(exported)
        edbapp.close(terminate_rpc_session=False)

        materials = {m.name: m for m in XmlParser.load_xml_file(exported).stackup.materials.material}
        assert materials["GL107_Nom"].permittivity.equation == self.PERMITTIVITY_EQUATION
        assert materials["GL107_Nom"].conductivity.equation == self.CONDUCTIVITY_EQUATION
        assert materials["COPPER_LEGACY"].conductivity.value == 58000000


class TestDielectricModel(BaseTestClass):
    def test_djordjevic_sarkar_model_properties(self):
        """Evaluate Djordjevic-Sarkar model properties."""
        edbapp = self.edb_examples.create_empty_edb()
        material = edbapp.materials.add_material("ds_model")
        material.set_djordjecvic_sarkar_model()
        ds_model = material.dielectric_material_model
        assert ds_model.dc_conductivity == 1e-12
        assert ds_model.dc_relative_permittivity == 5
        assert ds_model.frequency == 1e9
        assert ds_model.loss_tangent_at_frequency == 0.02
        assert ds_model.relative_permittivity_at_frequency == 4
        if not config.use_grpc:
            assert ds_model.use_dc_relative_permittivity is False
        edbapp.close(terminate_rpc_session=False)
