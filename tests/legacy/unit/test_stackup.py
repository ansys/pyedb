import pytest
from mock import Mock
from pyedb.legacy.edb_core.stackup import Stackup

pytestmark = pytest.mark.unit

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.stackup = Stackup(Mock())

    def test_stackup_int_to_layer_types(self):
        signal_layer = self.stackup._int_to_layer_types(0)
        assert signal_layer == self.stackup.layer_types.SignalLayer
        dielectric_layer =self.stackup._int_to_layer_types(1)
        assert dielectric_layer ==self.stackup.layer_types.DielectricLayer
        conducting_layer =self.stackup._int_to_layer_types(2)
        assert conducting_layer ==self.stackup.layer_types.ConductingLayer
        airlines_layer =self.stackup._int_to_layer_types(3)
        assert airlines_layer ==self.stackup.layer_types.AirlinesLayer
        errors_layer =self.stackup._int_to_layer_types(4)
        assert errors_layer ==self.stackup.layer_types.ErrorsLayer
        symbol_layer =self.stackup._int_to_layer_types(5)
        assert symbol_layer ==self.stackup.layer_types.SymbolLayer
        measure_layer =self.stackup._int_to_layer_types(6)
        assert measure_layer ==self.stackup.layer_types.MeasureLayer
        assembly_layer =self.stackup._int_to_layer_types(8)
        assert assembly_layer ==self.stackup.layer_types.AssemblyLayer
        silkscreen_layer =self.stackup._int_to_layer_types(9)
        assert silkscreen_layer ==self.stackup.layer_types.SilkscreenLayer
        solder_mask_layer =self.stackup._int_to_layer_types(10)
        assert solder_mask_layer ==self.stackup.layer_types.SolderMaskLayer
        solder_paste_layer =self.stackup._int_to_layer_types(11)
        assert solder_paste_layer ==self.stackup.layer_types.SolderPasteLayer
        glue_layer =self.stackup._int_to_layer_types(12)
        assert glue_layer ==self.stackup.layer_types.GlueLayer
        wirebond_layer =self.stackup._int_to_layer_types(13)
        assert wirebond_layer ==self.stackup.layer_types.WirebondLayer
        user_layer =self.stackup._int_to_layer_types(14)
        assert user_layer ==self.stackup.layer_types.UserLayer
        siwave_hfss_solver_regions =self.stackup._int_to_layer_types(16)
        assert siwave_hfss_solver_regions ==self.stackup.layer_types.SIwaveHFSSSolverRegions
        outline_layer =self.stackup._int_to_layer_types(18)
        assert outline_layer ==self.stackup.layer_types.OutlineLayer
