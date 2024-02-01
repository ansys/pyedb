import builtins
from unittest.mock import mock_open

from mock import MagicMock, PropertyMock, patch
import pytest

from pyedb.dotnet.edb_core.materials import Materials

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


@patch("pyedb.dotnet.edb_core.materials.Materials.materials", new_callable=PropertyMock)
@patch.object(builtins, "open", new_callable=mock_open, read_data=MATERIALS)
def test_materials_read_materials(mock_file_open, mock_materials_property):
    """Read materials from an AMAT file."""
    mock_materials_property.return_value = ["copper"]
    materials = Materials(MagicMock())
    expected_res = {
        "Polyflon CuFlon (tm)": {"permittivity": 2.1, "tangent_delta": 0.00045},
        "Water(@360K)": {
            "thermal_conductivity": 0.6743,
            "mass_density": 967.4,
            "specific_heat": 4206,
            "thermal_expansion_coeffcient": 0.0006979,
        },
    }
    mats = materials.read_materials("some path")
    assert mats == expected_res
