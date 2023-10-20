"""Tests related to Edb stackup
"""

import os
import pytest
from pyedb import Edb
from tests.conftest import desktop_version
from tests.conftest import local_path
from tests.legacy.system.conftest import test_subfolder

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

    # def test_100_layer_types_to_int(self):
    #     stackup = self.edbapp.stackup
    #     signal_layer = stackup._layer_types_to_int(stackup.layer_types.SignalLayer)
    #     assert signal_layer == 0
    #     dielectric_layer = stackup._layer_types_to_int(stackup.layer_types.DielectricLayer)
    #     assert dielectric_layer == 1
    #     conducting_layer = stackup._layer_types_to_int(stackup.layer_types.ConductingLayer)
    #     assert conducting_layer == 2
    #     airlines_layer = stackup._layer_types_to_int(stackup.layer_types.AirlinesLayer)
    #     assert airlines_layer == 3
    #     errors_layer = stackup._layer_types_to_int(stackup.layer_types.ErrorsLayer)
    #     assert errors_layer == 4
    #     symbol_layer = stackup._layer_types_to_int(stackup.layer_types.SymbolLayer)
    #     assert symbol_layer == 5
    #     measure_layer = stackup._layer_types_to_int(stackup.layer_types.MeasureLayer)
    #     assert measure_layer == 6
    #     assembly_layer = stackup._layer_types_to_int(stackup.layer_types.AssemblyLayer)
    #     assert assembly_layer == 8
    #     silkscreen_layer = stackup._layer_types_to_int(stackup.layer_types.SilkscreenLayer)
    #     assert silkscreen_layer == 9
    #     solder_mask_layer = stackup._layer_types_to_int(stackup.layer_types.SolderMaskLayer)
    #     assert solder_mask_layer == 10
    #     solder_paste_layer = stackup._layer_types_to_int(stackup.layer_types.SolderPasteLayer)
    #     assert solder_paste_layer == 11
    #     glue_layer = stackup._layer_types_to_int(stackup.layer_types.GlueLayer)
    #     assert glue_layer == 12
    #     wirebond_layer = stackup._layer_types_to_int(stackup.layer_types.WirebondLayer)
    #     assert wirebond_layer == 13
    #     user_layer = stackup._layer_types_to_int(stackup.layer_types.UserLayer)
    #     assert user_layer == 14
    #     siwave_hfss_solver_regions = stackup._layer_types_to_int(stackup.layer_types.SIwaveHFSSSolverRegions)
    #     assert siwave_hfss_solver_regions == 16
    #     outline_layer = stackup._layer_types_to_int(stackup.layer_types.OutlineLayer)
    #     assert outline_layer == 18

    def test_stackup_place_a3dcomp_3d_placement(self):
        """Place a 3D Component into current layout."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "lam_for_bottom_place.aedb")
        target_path = os.path.join(self.local_scratch.path, "output.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        laminate_edb = Edb(target_path, edbversion=desktop_version)
        chip_a3dcomp = os.path.join(local_path, "example_models", test_subfolder, "chip.a3dcomp")
        try:
            layout = laminate_edb.active_layout
            cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 0
            assert laminate_edb.stackup.place_a3dcomp_3d_placement(
                chip_a3dcomp,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                place_on_top=True,
            )
            cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 1
            cell_instance = cell_instances[0]
            assert cell_instance.Is3DPlacement()
            if desktop_version > "2023.1":
                (
                    res,
                    local_origin,
                    rotation_axis_from,
                    rotation_axis_to,
                    angle,
                    loc,
                    _,
                ) = cell_instance.Get3DTransformation()
            else:
                (
                    res,
                    local_origin,
                    rotation_axis_from,
                    rotation_axis_to,
                    angle,
                    loc,
                ) = cell_instance.Get3DTransformation()
            assert res
            zero_value = laminate_edb.edb_value(0)
            one_value = laminate_edb.edb_value(1)
            origin_point = laminate_edb.edb_api.geometry.point3d_data(zero_value, zero_value, zero_value)
            x_axis_point = laminate_edb.edb_api.geometry.point3d_data(one_value, zero_value, zero_value)
            assert local_origin.IsEqual(origin_point)
            assert rotation_axis_from.IsEqual(x_axis_point)
            assert rotation_axis_to.IsEqual(x_axis_point)
            assert angle.IsEqual(zero_value)
            assert loc.IsEqual(
                laminate_edb.edb_api.geometry.point3d_data(zero_value, zero_value, laminate_edb.edb_value(170e-6))
            )
            assert laminate_edb.save_edb()
        finally:
            laminate_edb.close()

    def test_stackup_place_a3dcomp_3d_placement_on_bottom(self):
        """Place a 3D Component into current layout."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "lam_for_bottom_place.aedb")
        target_path = os.path.join(self.local_scratch.path, "output.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        laminate_edb = Edb(target_path, edbversion=desktop_version)
        chip_a3dcomp = os.path.join(local_path, "example_models", test_subfolder, "chip.a3dcomp")
        try:
            layout = laminate_edb.active_layout
            cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 0
            assert laminate_edb.stackup.place_a3dcomp_3d_placement(
                chip_a3dcomp,
                angle=90.0,
                offset_x=0.5e-3,
                offset_y=-0.5e-3,
                place_on_top=False,
            )
            cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 1
            cell_instance = cell_instances[0]
            assert cell_instance.Is3DPlacement()
            if desktop_version > "2023.1":
                (
                    res,
                    local_origin,
                    rotation_axis_from,
                    rotation_axis_to,
                    angle,
                    loc,
                    mirror,
                ) = cell_instance.Get3DTransformation()
            else:
                (
                    res,
                    local_origin,
                    rotation_axis_from,
                    rotation_axis_to,
                    angle,
                    loc,
                ) = cell_instance.Get3DTransformation()
            assert res
            zero_value = laminate_edb.edb_value(0)
            one_value = laminate_edb.edb_value(1)
            flip_angle_value = laminate_edb.edb_value("180deg")
            origin_point = laminate_edb.edb_api.geometry.point3d_data(zero_value, zero_value, zero_value)
            x_axis_point = laminate_edb.edb_api.geometry.point3d_data(one_value, zero_value, zero_value)
            assert local_origin.IsEqual(origin_point)
            assert rotation_axis_from.IsEqual(x_axis_point)
            assert rotation_axis_to.IsEqual(
                laminate_edb.edb_api.geometry.point3d_data(zero_value, laminate_edb.edb_value(-1.0), zero_value)
            )
            assert angle.IsEqual(flip_angle_value)
            assert loc.IsEqual(
                laminate_edb.edb_api.geometry.point3d_data(
                    laminate_edb.edb_value(0.5e-3),
                    laminate_edb.edb_value(-0.5e-3),
                    zero_value,
                )
            )
            assert laminate_edb.save_edb()
        finally:
            laminate_edb.close()
