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

import builtins
from unittest.mock import mock_open

from mock import MagicMock, PropertyMock, patch
import pytest

from pyedb.dotnet.database.materials import Materials

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]

MATERIALS = """
$begin 'Polyflon CuFlon (tm)'
  $begin 'AttachedData'
    $begin 'MatAppearanceData'
      property_data='appearance_data'
      Red=230
      Green=225
      Blue=220
    $end 'MatAppearanceData'
  $end 'AttachedData'
  simple('permittivity', 2.1)
  simple('dielectric_loss_tangent', 0.00045)
  ModTime=1499970477
$end 'Polyflon CuFlon (tm)'
$begin 'Water(@360K)'
  $begin 'MaterialDef'
    $begin 'Water(@360K)'
      CoordinateSystemType='Cartesian'
      BulkOrSurfaceType=1
      $begin 'PhysicsTypes'
        set('Thermal')
      $end 'PhysicsTypes'
      $begin 'AttachedData'
        $begin 'MatAppearanceData'
          property_data='appearance_data'
          Red=0
          Green=128
          Blue=255
          Transparency=0.8
        $end 'MatAppearanceData'
      $end 'AttachedData'
      thermal_conductivity='0.6743'
      mass_density='967.4'
      specific_heat='4206'
      thermal_expansion_coeffcient='0.0006979'
      $begin 'thermal_material_type'
        property_type='ChoiceProperty'
        Choice='Fluid'
      $end 'thermal_material_type'
      $begin 'clarity_type'
        property_type='ChoiceProperty'
        Choice='Transparent'
      $end 'clarity_type'
      material_refractive_index='1.333'
      diffusivity='1.657e-007'
      molecular_mass='0.018015'
      viscosity='0.000324'
      ModTime=1592011950
    $end 'Water(@360K)'
  $end 'MaterialDef'
$end 'Water(@360K)'
"""


@patch("pyedb.dotnet.database.materials.Materials.materials", new_callable=PropertyMock)
@patch.object(builtins, "open", new_callable=mock_open, read_data=MATERIALS)
def test_materials_read_materials(mock_file_open, mock_materials_property):
    """Read materials from an AMAT file."""
    mock_materials_property.return_value = ["copper"]
    materials = Materials(MagicMock())
    expected_res = {
        "Polyflon CuFlon (tm)": {"permittivity": 2.1, "dielectric_loss_tangent": 0.00045},
        "Water(@360K)": {
            "thermal_conductivity": 0.6743,
            "mass_density": 967.4,
            "specific_heat": 4206.0,
            "thermal_expansion_coefficient": 0.0006979,
        },
    }
    mats = materials.read_materials("some path")
    assert mats == expected_res
