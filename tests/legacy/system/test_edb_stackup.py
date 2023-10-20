"""Tests related to Edb stackup
"""

import pytest
from pyedb import Edb
from tests.conftest import desktop_version

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_stackup_get_signal_layers(self):
        """Report residual copper area per layer."""
        assert self.edbapp.stackup.residual_copper_area_per_layer()

    def test_stackup_limits(self):
        """Retrieve stackup limits."""
        assert self.edbapp.stackup.limits()

    def test_stackup_add_outline(self):
        """Add an outline layer named ``"Outline1"`` if it is not present."""
        edbapp = Edb(
            edbversion=desktop_version,
        )
        assert edbapp.stackup.add_outline_layer("Outline1")
        assert not edbapp.stackup.add_outline_layer("Outline1")
        edbapp.stackup.add_layer("1_Top")
        assert edbapp.stackup.layers["1_Top"].thickness == 3.5e-05
        edbapp.stackup.layers["1_Top"].thickness = 4e-5
        assert edbapp.stackup.layers["1_Top"].thickness == 4e-05
        edbapp.close()

    def test_stackup_create_symmetric_stackup(self):
        """Create a symmetric stackup."""
        app_edb = Edb(edbversion=desktop_version)
        assert not app_edb.stackup.create_symmetric_stackup(9)
        assert app_edb.stackup.create_symmetric_stackup(8)
        app_edb.close()

        app_edb = Edb(edbversion=desktop_version)
        assert app_edb.stackup.create_symmetric_stackup(8, soldermask=False)
        app_edb.close()

    # def test_stackup_int_to_layer_types(self):
    #     stackup = self.edbapp.stackup
    #     signal_layer = stackup._int_to_layer_types(0)
    #     assert signal_layer == stackup.layer_types.SignalLayer
    #     dielectric_layer = stackup._int_to_layer_types(1)
    #     assert dielectric_layer == stackup.layer_types.DielectricLayer
    #     conducting_layer = stackup._int_to_layer_types(2)
    #     assert conducting_layer == stackup.layer_types.ConductingLayer
    #     airlines_layer = stackup._int_to_layer_types(3)
    #     assert airlines_layer == stackup.layer_types.AirlinesLayer
    #     errors_layer = stackup._int_to_layer_types(4)
    #     assert errors_layer == stackup.layer_types.ErrorsLayer
    #     symbol_layer = stackup._int_to_layer_types(5)
    #     assert symbol_layer == stackup.layer_types.SymbolLayer
    #     measure_layer = stackup._int_to_layer_types(6)
    #     assert measure_layer == stackup.layer_types.MeasureLayer
    #     assembly_layer = stackup._int_to_layer_types(8)
    #     assert assembly_layer == stackup.layer_types.AssemblyLayer
    #     silkscreen_layer = stackup._int_to_layer_types(9)
    #     assert silkscreen_layer == stackup.layer_types.SilkscreenLayer
    #     solder_mask_layer = stackup._int_to_layer_types(10)
    #     assert solder_mask_layer == stackup.layer_types.SolderMaskLayer
    #     solder_paste_layer = stackup._int_to_layer_types(11)
    #     assert solder_paste_layer == stackup.layer_types.SolderPasteLayer
    #     glue_layer = stackup._int_to_layer_types(12)
    #     assert glue_layer == stackup.layer_types.GlueLayer
    #     wirebond_layer = stackup._int_to_layer_types(13)
    #     assert wirebond_layer == stackup.layer_types.WirebondLayer
    #     user_layer = stackup._int_to_layer_types(14)
    #     assert user_layer == stackup.layer_types.UserLayer
    #     siwave_hfss_solver_regions = stackup._int_to_layer_types(16)
    #     assert siwave_hfss_solver_regions == stackup.layer_types.SIwaveHFSSSolverRegions
    #     outline_layer = stackup._int_to_layer_types(18)
    #     assert outline_layer == stackup.layer_types.OutlineLayer

    def test_100_layer_types_to_int(self):
        stackup = self.edbapp.stackup
        signal_layer = stackup._layer_types_to_int(stackup.layer_types.SignalLayer)
        assert signal_layer == 0
        dielectric_layer = stackup._layer_types_to_int(stackup.layer_types.DielectricLayer)
        assert dielectric_layer == 1
        conducting_layer = stackup._layer_types_to_int(stackup.layer_types.ConductingLayer)
        assert conducting_layer == 2
        airlines_layer = stackup._layer_types_to_int(stackup.layer_types.AirlinesLayer)
        assert airlines_layer == 3
        errors_layer = stackup._layer_types_to_int(stackup.layer_types.ErrorsLayer)
        assert errors_layer == 4
        symbol_layer = stackup._layer_types_to_int(stackup.layer_types.SymbolLayer)
        assert symbol_layer == 5
        measure_layer = stackup._layer_types_to_int(stackup.layer_types.MeasureLayer)
        assert measure_layer == 6
        assembly_layer = stackup._layer_types_to_int(stackup.layer_types.AssemblyLayer)
        assert assembly_layer == 8
        silkscreen_layer = stackup._layer_types_to_int(stackup.layer_types.SilkscreenLayer)
        assert silkscreen_layer == 9
        solder_mask_layer = stackup._layer_types_to_int(stackup.layer_types.SolderMaskLayer)
        assert solder_mask_layer == 10
        solder_paste_layer = stackup._layer_types_to_int(stackup.layer_types.SolderPasteLayer)
        assert solder_paste_layer == 11
        glue_layer = stackup._layer_types_to_int(stackup.layer_types.GlueLayer)
        assert glue_layer == 12
        wirebond_layer = stackup._layer_types_to_int(stackup.layer_types.WirebondLayer)
        assert wirebond_layer == 13
        user_layer = stackup._layer_types_to_int(stackup.layer_types.UserLayer)
        assert user_layer == 14
        siwave_hfss_solver_regions = stackup._layer_types_to_int(stackup.layer_types.SIwaveHFSSSolverRegions)
        assert siwave_hfss_solver_regions == 16
        outline_layer = stackup._layer_types_to_int(stackup.layer_types.OutlineLayer)
        assert outline_layer == 18
