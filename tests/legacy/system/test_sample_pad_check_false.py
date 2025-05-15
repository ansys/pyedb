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
        self.definition = self.edbapp.edb_api.definition

        # Remove dummy material if it exist
        material_def = self.definition.MaterialDef.FindByName(self.edbapp.active_db, MATERIAL_NAME)
        if not material_def.IsNull():
            material_def.Delete()

    def test_create_custom_cutout_0(self, edb_examples):
        """Create custom cutout 0."""
        edbapp = edb_examples.get_si_verse()

        assert edbapp.cutout(
            signal_list=["SFPA_RX_P", "SFPA_RX_N"],
            reference_list=["GND"],
            extent_type="ConvexHull",
            simple_pad_check=False,
        )
        edbapp.close()

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
