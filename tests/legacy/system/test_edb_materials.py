"""Tests related to Edb
"""

import os
from pyedb.legacy.edb_core.edb_data.simulation_configuration import SimulationConfiguration
import pytest

from pyedb import Edb
from pyedb.generic.constants import RadiationBoxType, SourceType
from pyedb.generic.constants import SolverType
from tests.conftest import local_path
from tests.conftest import desktop_version
from tests.legacy.system.conftest import test_subfolder

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch):
        self.edbapp = edbapp
        self.local_scratch = local_scratch

    def test_material_properties(self):
        """Evaluate materials properties."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0127.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        assert isinstance(edbapp.materials.materials, dict)
        edbapp.materials["FR4_epoxy"].conductivity = 1
        assert edbapp.materials["FR4_epoxy"].conductivity == 1
        edbapp.materials["FR4_epoxy"].permittivity = 1
        assert edbapp.materials["FR4_epoxy"].permittivity == 1
        edbapp.materials["FR4_epoxy"].loss_tangent = 1
        assert edbapp.materials["FR4_epoxy"].loss_tangent == 1
        edbapp.materials.add_conductor_material("new_conductor", 1)
        assert not edbapp.materials.add_conductor_material("new_conductor", 1)
        edbapp.materials.add_dielectric_material("new_dielectric", 1, 2)
        assert not edbapp.materials.add_dielectric_material("new_dielectric", 1, 2)
        edbapp.materials["FR4_epoxy"].magnetic_loss_tangent = 0.01
        assert edbapp.materials["FR4_epoxy"].magnetic_loss_tangent == 0.01
        edbapp.materials["FR4_epoxy"].youngs_modulus = 5000
        assert edbapp.materials["FR4_epoxy"].youngs_modulus == 5000
        edbapp.materials["FR4_epoxy"].mass_density = 50

        assert edbapp.materials["FR4_epoxy"].mass_density == 50
        edbapp.materials["FR4_epoxy"].thermal_conductivity = 1e-5

        assert edbapp.materials["FR4_epoxy"].thermal_conductivity == 1e-5
        edbapp.materials["FR4_epoxy"].thermal_expansion_coefficient = 1e-7

        assert edbapp.materials["FR4_epoxy"].thermal_expansion_coefficient == 1e-7
        edbapp.materials["FR4_epoxy"].poisson_ratio = 1e-3
        assert edbapp.materials["FR4_epoxy"].poisson_ratio == 1e-3
        assert edbapp.materials["new_conductor"]
        assert edbapp.materials.duplicate("FR4_epoxy", "FR41")
        assert edbapp.materials["FR41"]
        assert edbapp.materials["FR4_epoxy"].conductivity == edbapp.materials["FR41"].conductivity
        assert edbapp.materials["FR4_epoxy"].permittivity == edbapp.materials["FR41"].permittivity
        assert edbapp.materials["FR4_epoxy"].loss_tangent == edbapp.materials["FR41"].loss_tangent
        assert edbapp.materials["FR4_epoxy"].magnetic_loss_tangent == edbapp.materials["FR41"].magnetic_loss_tangent
        assert edbapp.materials["FR4_epoxy"].youngs_modulus == edbapp.materials["FR41"].youngs_modulus
        assert edbapp.materials["FR4_epoxy"].mass_density == edbapp.materials["FR41"].mass_density
        assert edbapp.materials["FR4_epoxy"].thermal_conductivity == edbapp.materials["FR41"].thermal_conductivity
        assert (
            edbapp.materials["FR4_epoxy"].thermal_expansion_coefficient
            == edbapp.materials["FR41"].thermal_expansion_coefficient
        )
        assert edbapp.materials["FR4_epoxy"].poisson_ratio == edbapp.materials["FR41"].poisson_ratio
        assert edbapp.materials.add_debye_material("My_Debye2", 5, 3, 0.02, 0.05, 1e5, 1e9)
        assert edbapp.materials.add_djordjevicsarkar_material("MyDjord2", 3.3, 0.02, 3.3)
        freq = [0, 2, 3, 4, 5, 6]
        rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
        loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
        assert edbapp.materials.add_multipole_debye_material("My_MP_Debye2", freq, rel_perm, loss_tan)
        edbapp.close()
        edbapp = Edb(edbversion=desktop_version)
        assert "air" in edbapp.materials.materials
        edbapp.close()

    def test_material_load_amat(self):
        """Load material from an amat file."""
        assert "Rogers RO3003 (tm)" in self.edbapp.materials.materials_in_aedt
        material_file = os.path.join(self.edbapp.materials.syslib, "Materials.amat")
        assert self.edbapp.materials.add_material_from_aedt("Arnold_Magnetics_N28AH_-40C")
        assert "Arnold_Magnetics_N28AH_-40C" in self.edbapp.materials.materials.keys()
        assert self.edbapp.materials.load_amat(material_file)
        material_list = list(self.edbapp.materials.materials.keys())
        assert material_list
        assert len(material_list) > 0
        assert self.edbapp.materials.materials["Rogers RO3003 (tm)"].loss_tangent == 0.0013
        assert self.edbapp.materials.materials["Rogers RO3003 (tm)"].permittivity == 3.0
