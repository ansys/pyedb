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

"""Tests related to Edb stackup"""

import math
import os

import pytest

from tests.conftest import GRPC, desktop_version, local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):

    def test_stackup_get_signal_layers(self):
        """Report residual copper area per layer."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.stackup.residual_copper_area_per_layer()
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_limits(self):
        """Retrieve stackup limits."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.stackup.limits()
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_add_outline(self):
        """Add an outline layer named ``"Outline1"`` if it is not present."""
        edbapp = self.edb_examples.create_empty_edb()
        assert edbapp.stackup.add_outline_layer()
        assert "Outline" in edbapp.stackup.non_stackup_layers
        edbapp.stackup.add_layer("1_Top")
        assert edbapp.stackup.layers["1_Top"].thickness == 3.5e-05
        edbapp.stackup.layers["1_Top"].thickness = 4e-5
        assert edbapp.stackup.layers["1_Top"].thickness == 4e-05
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_create_symmetric_stackup(self):
        """Create a symmetric stackup."""
        app_edb = self.edb_examples.create_empty_edb()
        assert not app_edb.stackup.create_symmetric_stackup(9)
        assert app_edb.stackup.create_symmetric_stackup(8)
        app_edb.close(terminate_rpc_session=False)

        app_edb = self.edb_examples.create_empty_edb()
        assert app_edb.stackup.create_symmetric_stackup(8, soldermask=False)
        app_edb.close(terminate_rpc_session=False)

    def test_stackup_place_a3dcomp_3d_placement(self):
        """Place a 3D Component into current layout."""
        source_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/lam_for_bottom_place.aedb")[0]
        laminate_edb = self.edb_examples.load_edb(source_path)
        chip_a3dcomp = self.edb_examples.copy_test_files_into_local_folder("TEDB/chip.a3dcomp")[0]
        try:
            layout = laminate_edb.active_layout
            if laminate_edb.grpc:
                cell_instances = layout.core.cell_instances
            else:
                cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 0
            assert laminate_edb.stackup.place_a3dcomp_3d_placement(
                chip_a3dcomp,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                place_on_top=True,
            )
            if laminate_edb.grpc:
                cell_instances = layout.core.cell_instances
            else:
                cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 1
            cell_instance = cell_instances[0]
            if laminate_edb.grpc:
                assert cell_instance.placement_3d
            else:
                assert cell_instance.Is3DPlacement()
            if laminate_edb.grpc:
                transform = cell_instance.transform3d
                local_origin = transform.matrix[3][:3]
                angle = transform.z_y_x_rotation.magnitude
                loc = [
                    transform.shift.x.value,
                    transform.shift.y.value,
                    transform.shift.z.value,
                ]
                assert local_origin == [0.0, 0.0, 0.00017]
                assert angle == 0.0
                assert loc == [0.0, 0.0, 0.00017]
            else:
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
                origin_point = laminate_edb.core.Geometry.Point3DData(zero_value, zero_value, zero_value)
                x_axis_point = laminate_edb.core.Geometry.Point3DData(one_value, zero_value, zero_value)
                assert local_origin.IsEqual(origin_point)
                assert rotation_axis_from.IsEqual(x_axis_point)
                assert rotation_axis_to.IsEqual(x_axis_point)
                assert angle.IsEqual(zero_value)
                assert loc.IsEqual(
                    laminate_edb.core.Geometry.Point3DData(zero_value, zero_value, laminate_edb.edb_value(170e-6))
                )
            assert laminate_edb.save_edb()
        finally:
            laminate_edb.close(terminate_rpc_session=False)

    def test_stackup_place_a3dcomp_3d_placement_on_bottom(self):
        """Place a 3D Component into current layout."""
        source_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/lam_for_bottom_place.aedb")[0]
        laminate_edb = self.edb_examples.load_edb(source_path)
        chip_a3dcomp = self.edb_examples.copy_test_files_into_local_folder("TEDB/chip.a3dcomp")[0]
        try:
            layout = laminate_edb.active_layout
            if laminate_edb.grpc:
                cell_instances = layout.core.cell_instances
            else:
                cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 0
            assert laminate_edb.stackup.place_a3dcomp_3d_placement(
                chip_a3dcomp,
                angle=90.0,
                offset_x=0.5e-3,
                offset_y=-0.5e-3,
                place_on_top=False,
            )
            if laminate_edb.grpc:
                cell_instances = layout.core.cell_instances
            else:
                cell_instances = list(layout.CellInstances)
            assert len(cell_instances) == 1
            cell_instance = cell_instances[0]
            if laminate_edb.grpc:
                assert cell_instance.placement_3d
            else:
                assert cell_instance.Is3DPlacement()
            if laminate_edb.grpc:
                transform = cell_instance.transform3d
                local_origin = transform.matrix[3][:3]
                assert local_origin == [0.0005, -0.0005, 0.0]
                assert transform.z_y_x_rotation.magnitude == 0.0
                assert transform.shift.x.value == 0.0005
                assert transform.shift.y.value == -0.0005
                assert transform.shift.z.value == 0.0
            else:
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
                origin_point = laminate_edb.core.Geometry.Point3DData(zero_value, zero_value, zero_value)
                x_axis_point = laminate_edb.core.Geometry.Point3DData(one_value, zero_value, zero_value)
                assert local_origin.IsEqual(origin_point)
                assert rotation_axis_from.IsEqual(x_axis_point)
                assert rotation_axis_to.IsEqual(
                    laminate_edb.core.Geometry.Point3DData(zero_value, laminate_edb.edb_value(-1.0), zero_value)
                )
                assert angle.IsEqual(flip_angle_value)
                assert loc.IsEqual(
                    laminate_edb.core.Geometry.Point3DData(
                        laminate_edb.edb_value(0.5e-3),
                        laminate_edb.edb_value(-0.5e-3),
                        zero_value,
                    )
                )
            assert laminate_edb.save_edb()
        finally:
            laminate_edb.close(terminate_rpc_session=False)

    def test_stackup_properties_0(self):
        """Evaluate various stackup properties."""
        source_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/ANSYS-HSD_V1.aedb")[0]
        edbapp = self.edb_examples.load_edb(source_path)
        assert isinstance(edbapp.stackup.layers, dict)
        assert isinstance(edbapp.stackup.signal_layers, dict)
        assert isinstance(edbapp.stackup.dielectric_layers, dict)
        assert isinstance(edbapp.stackup.non_stackup_layers, dict)
        assert not edbapp.stackup["Outline"].is_stackup_layer
        assert edbapp.stackup["1_Top"].conductivity
        assert edbapp.stackup["DE1"].permittivity
        assert edbapp.stackup.add_layer("new_layer")
        new_layer = edbapp.stackup["new_layer"]
        assert new_layer.is_stackup_layer
        assert not new_layer.is_negative
        new_layer.name = "renamed_layer"
        assert new_layer.name == "renamed_layer"
        rename_layer = edbapp.stackup["renamed_layer"]
        rename_layer.thickness = 50e-6
        assert rename_layer.thickness == 50e-6
        rename_layer.etch_factor = 0
        rename_layer.etch_factor = 2
        assert rename_layer.etch_factor == 2
        assert rename_layer.material
        assert rename_layer.type
        assert rename_layer.dielectric_fill

        rename_layer.roughness_enabled = True
        assert rename_layer.roughness_enabled
        rename_layer.roughness_enabled = False
        assert not rename_layer.roughness_enabled
        assert rename_layer.assign_roughness_model("groisse", groisse_roughness="2um")
        assert rename_layer.assign_roughness_model(apply_on_surface="1_Top")
        assert rename_layer.assign_roughness_model(apply_on_surface="bottom")
        assert rename_layer.assign_roughness_model(apply_on_surface="side")
        assert edbapp.stackup.add_layer("new_above", "1_Top", "insert_above")
        assert edbapp.stackup.add_layer("new_below", "1_Top", "insert_below")
        assert edbapp.stackup.add_layer("new_bottom", "1_Top", "add_on_bottom", "dielectric")
        assert edbapp.stackup.remove_layer("new_bottom")
        assert "new_bottom" not in edbapp.stackup.layers

        assert edbapp.stackup["1_Top"].color
        edbapp.stackup["1_Top"].color = [0, 120, 0]
        assert list(edbapp.stackup["1_Top"].color) == [0, 120, 0]  # grpc is returning tuple
        edbapp.stackup["1_Top"].transparency = 10
        assert edbapp.stackup["1_Top"].transparency == 10
        assert edbapp.stackup.mode.lower() == "laminate"
        edbapp.stackup.mode = "Overlapping"
        assert edbapp.stackup.mode.lower() == "overlapping"
        # TODO check Multizone is getting stuck both grpc and dotnet.
        # edbapp.stackup.mode = "MultiZone"
        # assert edbapp.stackup.mode.lower() == "multiZone"
        # edbapp.stackup.mode = "Overlapping"
        # assert edbapp.stackup.mode.lower() == "overlapping"
        assert edbapp.stackup.add_layer("new_bottom", "1_Top", "add_at_elevation", "dielectric", elevation=0.0003)
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_properties_1(self):
        """Evaluate various stackup properties."""
        edbapp = self.edb_examples.create_empty_edb()
        import_method = edbapp.stackup.load
        export_method = edbapp.stackup.export

        assert import_method(self.edb_examples.copy_test_files_into_local_folder("TEDB/ansys_pcb_stackup.csv")[0])
        assert "18_Bottom" in edbapp.stackup.layers.keys()
        assert edbapp.stackup.add_layer("19_Bottom", None, "add_on_top", material="iron")
        export_stackup_path = os.path.join(self.edb_examples.test_folder, "export_stackup.csv")
        assert export_method(export_stackup_path)
        assert os.path.exists(export_stackup_path)

        edbapp.close(terminate_rpc_session=False)

    def test_stackup_properties_2(self):
        """Evaluate various stackup properties."""
        edbapp = self.edb_examples.create_empty_edb()
        import_method = edbapp.stackup.load
        export_method = edbapp.stackup.export

        assert import_method(self.edb_examples.copy_test_files_into_local_folder("TEDB/ansys_pcb_stackup.csv")[0])
        assert "18_Bottom" in edbapp.stackup.layers.keys()
        assert edbapp.stackup.add_layer("19_Bottom", None, "add_on_top", material="iron")
        export_stackup_path = os.path.join(self.edb_examples.test_folder, "export_stackup.csv")
        assert export_method(export_stackup_path)
        assert os.path.exists(export_stackup_path)
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_layer_properties(self):
        """Evaluate various layer properties."""
        # TODO
        # edbapp = edb_examples.get_si_verse()
        # edbapp.stackup.load(os.path.join(local_path, "example_models", test_subfolder, "ansys_pcb_stackup.xml"))
        # layer = edbapp.stackup["1_Top"]
        # layer.name = "TOP"
        # assert layer.name == "TOP"
        # layer.type = "dielectric"
        # assert layer.type == "dielectric"
        # layer.type = "signal"
        # layer.color = (0, 0, 0)
        # assert layer.color == (0, 0, 0)
        # layer.transparency = 0
        # assert layer.transparency == 0
        # layer.etch_factor = 2
        # assert layer.etch_factor == 2
        # layer.thickness = 50e-6
        # assert layer.thickness == 50e-6
        # assert layer.lower_elevation
        # assert layer.upper_elevation
        # layer.is_negative = True
        # assert layer.is_negative
        # assert not layer.is_via_layer
        # assert layer.material == "copper"
        # edbapp.close(terminate_rpc_session=False)
        pass

    def test_stackup_load_json(self):
        """Import stackup from a file."""

        source_path, fpath = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/ANSYS-HSD_V1.aedb", "TEDB/stackup.json"]
        )
        edbapp = self.edb_examples.load_edb(source_path)
        edbapp.stackup.load(fpath)
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_export_json(self):
        """Export stackup into a JSON file."""
        import json

        MATERIAL_MEGTRON_4 = {
            "name": "Megtron4",
            "conductivity": 0.0,
            "dielectric_loss_tangent": 0.005,
            "magnetic_loss_tangent": 0.0,
            "mass_density": 0.0,
            "permittivity": 3.77,
            "permeability": 0.0,
            "poisson_ratio": 0.0,
            "specific_heat": 0.0,
            "thermal_conductivity": 0.0,
            "youngs_modulus": 0.0,
            "thermal_expansion_coefficient": 0.0,
            "dc_conductivity": None,
            "dc_permittivity": None,
            "dielectric_model_frequency": None,
            "loss_tangent_at_frequency": None,
            "permittivity_at_frequency": None,
        }
        LAYER_DE_2 = {
            "name": "DE2",
            "color": [128, 128, 128],
            "type": "dielectric",
            "material": "Megtron4_2",
            "dielectric_fill": None,
            "thickness": 8.8e-05,
            "etch_factor": 0.0,
            "roughness_enabled": False,
            "top_hallhuray_nodule_radius": 0.0,
            "top_hallhuray_surface_ratio": 0.0,
            "bottom_hallhuray_nodule_radius": 0.0,
            "bottom_hallhuray_surface_ratio": 0.0,
            "side_hallhuray_nodule_radius": 0.0,
            "side_hallhuray_surface_ratio": 0.0,
            "upper_elevation": 0.001596,
            "lower_elevation": 0.001508,
        }

        source_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/ANSYS-HSD_V1.aedb")[0]
        edbapp = self.edb_examples.load_edb(source_path)
        json_path = os.path.join(self.edb_examples.test_folder, "exported_stackup.json")

        assert edbapp.stackup.export(json_path)
        with open(json_path, "r") as json_file:
            data = json.load(json_file)
            # Check material
            for parameter, value in MATERIAL_MEGTRON_4.items():
                assert data["materials"]["Megtron4"][parameter] == value
            # Check layer
            for parameter, value in LAYER_DE_2.items():
                if not edbapp.grpc and parameter in ["upper_elevation", "lower_elevation"]:
                    # dotnet is returning 0 elevation on dielectric layer which is wrong.
                    assert data["layers"]["DE2"][parameter] == 0.0
                else:
                    if data["layers"]["DE2"][parameter] == "":
                        value = ""
                    assert data["layers"]["DE2"][parameter] == value
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=GRPC, reason="Need to implement Configuration support with grpc")
    def test_stackup_load_xml(self):
        file_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/ansys_pcb_stackup.xml")[0]
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.stackup.load(file_path)
        assert "Inner1" in list(edbapp.stackup.layers.keys())  # Renamed layer
        assert "DE1" not in edbapp.stackup.layers.keys()  # Removed layer
        assert edbapp.stackup.export(os.path.join(self.edb_examples.test_folder, "stackup.xml"))
        assert round(edbapp.stackup.signal_layers["1_Top"].thickness, 6) == 3.5e-5
        assert edbapp.stackup.load_from_xml(file_path)
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_load_layer_renamed(self):
        """Import stackup from a file."""
        source_path, fpath = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/ANSYS-HSD_V1.aedb", "TEDB/stackup_renamed.json"]
        )

        edbapp = self.edb_examples.load_edb(source_path)
        edbapp.stackup.load(fpath, rename=True)
        assert "1_Top_renamed" in edbapp.stackup.layers
        assert "DE1_renamed" in edbapp.stackup.layers
        assert "16_Bottom_renamed" in edbapp.stackup.layers
        edbapp.close(terminate_rpc_session=False)

    def test_stackup_place_in_3d_with_flipped_stackup(self):
        """Place into another cell using 3d placement method with and
        without flipping the current layer stackup.
        """
        edb_path, edbpath2 = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/simple.aedb", "TEDB/example_package.aedb"]
        )
        edb1 = self.edb_examples.load_edb(edb_path)

        edb2 = self.edb_examples.load_edb(edbpath2)
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=False,
            solder_height=0.0,
        )
        if edb2.grpc:
            edb2.close(terminate_rpc_session=False)
        else:
            edb2.close(terminate_rpc_session=False)
        edb2 = self.edb_examples.load_edb(edbpath2 )
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=False,
            solder_height=0.0,
        )
        if edb2.grpc:
            edb2.close(terminate_rpc_session=False)
        else:
            edb2.close(terminate_rpc_session=False)
        edb2 = self.edb_examples.load_edb(edbpath2 )
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=True,
            solder_height=0.0,
        )
        if edb2.grpc:
            edb2.close(terminate_rpc_session=False)
        else:
            edb2.close(terminate_rpc_session=False)
        edb2 = self.edb_examples.load_edb(edbpath2)
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=True,
            solder_height=0.0,
        )
        if edb2.grpc:
            edb2.close(terminate_rpc_session=False)
        else:
            edb2.close(terminate_rpc_session=False)
        edb1.close(terminate_rpc_session=False)

    def test_stackup_place_instance_with_flipped_stackup(self):
        """Place into another cell using 3d placement method with and
        without flipping the current layer stackup.
        """
        edb_path,target_path = self.edb_examples.copy_test_files_into_local_folder(["TEDB/simple.aedb","TEDB/example_package.aedb"])
        edb1 = self.edb_examples.load_edb(edb_path)

        edb2 = self.edb_examples.load_edb(target_path)
        assert edb1.stackup.place_instance(
            edb2,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=False,
            solder_height=0.0,
        )
        assert edb1.stackup.place_instance(
            edb2,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=False,
            solder_height=0.0,
        )
        assert edb1.stackup.place_instance(
            edb2,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=True,
            solder_height=0.0,
        )
        assert edb1.stackup.place_instance(
            edb2,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=True,
            solder_height=0.0,
        )
        if edb2.grpc:
            edb2.close(terminate_rpc_session=False)
        else:
            edb2.close(terminate_rpc_session=False)
        edb1.close(terminate_rpc_session=False)

    def test_stackup_place_in_layout_with_flipped_stackup(self):
        """Place into another cell using layer placement method with and
        without flipping the current layer stackup.
        """
        # TODO
        # edb2 = Edb(self.target_path, edbversion=desktop_version)
        # assert edb2.stackup.place_in_layout(
        #     self.edbapp,
        #     angle=0.0,
        #     offset_x="41.783mm",
        #     offset_y="35.179mm",
        #     flipped_stackup=True,
        #     place_on_top=True,
        # )
        # edb2.close(terminate_rpc_session=False)
        pass

    def test_stackup_place_on_top_of_lam_with_mold(self):
        """Place on top lam with mold using 3d placement method"""
        fpath, chip = self.edb_examples.copy_test_files_into_local_folder(["TEDB/lam_with_mold.aedb", "TEDB/chip.aedb"])
        laminateEdb = self.edb_examples.load_edb(fpath)
        chipEdb = self.edb_examples.load_edb(chip)
            
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=False,
                place_on_top=True,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert transform.matrix[3][:3] == [0, 0, 0.00017]
                assert transform.shift.magnitude == 0.00017
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                originPoint = chipEdb.point_3d(0.0, 0.0, 0.0)
                xAxisPoint = chipEdb.point_3d(1.0, 0.0, 0.0)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.point_3d(0.0, 0.0, chipEdb.edb_value(170e-6)))
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_stackup_place_on_bottom_of_lam_with_mold(self):
        """Place on lam with mold using 3d placement method"""

        laminateEdb_path, chipEdb_path = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/lam_with_mold.aedb", "TEDB/chip_flipped_stackup.aedb"]
        )
        laminateEdb = self.edb_examples.load_edb(laminateEdb_path)
        chipEdb = self.edb_examples.load_edb(chipEdb_path)
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=False,
                place_on_top=True,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert transform.matrix[3][:3] == [0, 0, 0.00017]
                assert transform.shift.magnitude == 0.00017
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                originPoint = chipEdb.point_3d(0.0, 0.0, 0.0)
                xAxisPoint = chipEdb.point_3d(1.0, 0.0, 0.0)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.point_3d(0.0, 0.0, chipEdb.edb_value(170e-6)))
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_stackup_place_on_top_of_lam_with_mold_solder(self):
        """Place on top of lam with mold solder using 3d placement method."""
        path1 ,path2 = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/lam_with_mold.aedb", "TEDB/chip_solder.aedb"]
        )
        laminateEdb = self.edb_examples.load_edb(path1        )
        chipEdb = self.edb_examples.load_edb(path2        )
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=False,
                place_on_top=True,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert transform.matrix[3][:3] == [0, 0, 0.00019]
                assert transform.shift.magnitude == 0.00019
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.core.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(190e-6)))
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_stackup_place_on_bottom_of_lam_with_mold_solder(self):
        """Place on bottom of lam with mold solder using 3d placement method."""

        laminateEdb_path, chipEdb_path = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/lam_with_mold.aedb", "TEDB/chip_solder.aedb"]
        )
        laminateEdb = self.edb_examples.load_edb(laminateEdb_path)
        chipEdb = self.edb_examples.load_edb(chipEdb_path)
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=True,
                place_on_top=False,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert [round(val, 6) for val in transform.matrix[3][:3]] == [0.0, 0.0, -2e-5]
                assert round(transform.shift.magnitude, 6) == 2e-5
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.core.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(-20e-6)))
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_stackup_place_on_top_with_zoffset_chip(self):
        """Place on top of lam with mold chip zoffset using 3d placement method."""
        laminateEdb_path, chipEdb_path = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/lam_with_mold.aedb", "TEDB/chip_zoffset.aedb"]
        )
        laminateEdb = self.edb_examples.load_edb(laminateEdb_path)
        chipEdb = self.edb_examples.load_edb(chipEdb_path)
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=True,
                place_on_top=False,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert [round(val, 6) for val in transform.matrix[3][:3]] == [0.0, 0.0, 1e-05]
                assert round(transform.shift.magnitude, 6) == 1e-5
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.core.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.ToDouble() == math.pi
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_stackup_place_on_bottom_with_zoffset_chip(self):
        """Place on bottom of lam with mold chip zoffset using 3d placement method."""

        laminateEdb_path, chipEdb_path = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/lam_with_mold.aedb", "TEDB/chip_zoffset.aedb"]
        )
        laminateEdb = self.edb_examples.load_edb(laminateEdb_path)
        chipEdb = self.edb_examples.load_edb(chipEdb_path)
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=True,
                place_on_top=False,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert [round(val, 6) for val in transform.matrix[3][:3]] == [0.0, 0.0, 1e-05]
                assert round(transform.shift.magnitude, 6) == 1e-5
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.core.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(10e-6)))
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_stackup_place_on_top_with_zoffset_solder_chip(self):
        """Place on top of lam with mold chip zoffset using 3d placement method."""
        laminateEdb_path, chipEdb_path = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/lam_with_mold.aedb", "TEDB/chip_zoffset_solder.aedb"]
        )
        laminateEdb = self.edb_examples.load_edb(laminateEdb_path)
        chipEdb = self.edb_examples.load_edb(chipEdb_path)
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=True,
                place_on_top=False,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert [round(val, 6) for val in transform.matrix[3][:3]] == [0.0, 0.0, 2e-05]
                assert round(transform.shift.magnitude, 6) == 2e-5
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.core.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.ToDouble() == math.pi
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_stackup_place_on_bottom_with_zoffset_solder_chip(self):
        """Place on bottom of lam with mold chip zoffset using 3d placement method."""

        laminateEdb_path, chipEdb_path = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/lam_with_mold.aedb", "TEDB/chip_zoffset_solder.aedb"]
        )
        laminateEdb = self.edb_examples.load_edb(laminateEdb_path)
        chipEdb = self.edb_examples.load_edb(chipEdb_path)
        try:
            layout = laminateEdb.active_layout
            if chipEdb.grpc:
                cellInstances = layout.core.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=True,
                place_on_top=False,
            )
            if chipEdb.grpc:
                merged_cell = [cell for cell in chipEdb.circuit_cells if cell.name == "lam_with_mold"][0]
                assert not merged_cell.is_null
            else:
                merged_cell = chipEdb.core.Cell.Cell.FindByName(
                    chipEdb.active_db, chipEdb.core.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
            if chipEdb.grpc:
                layout = merged_cell.layout
            else:
                layout = merged_cell.GetLayout()
            if chipEdb.grpc:
                cellInstances = layout.cell_instances
            else:
                cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            if chipEdb.grpc:
                assert cellInstance.placement_3d
            else:
                assert cellInstance.Is3DPlacement()
            if chipEdb.grpc:
                transform = cellInstance.transform3d
                assert [round(val, 6) for val in transform.matrix[3][:3]] == [0.0, 0.0, 2e-05]
                assert round(transform.shift.magnitude, 6) == 2e-5
            else:
                if desktop_version > "2023.1":
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                        _,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.core.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.core.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(20e-6)))
        finally:
            if chipEdb.grpc:
                chipEdb.close(terminate_rpc_session=False)
            else:
                chipEdb.close(terminate_rpc_session=False)
            laminateEdb.close(terminate_rpc_session=False)

    def test_18_stackup(self):
        # TODO
        # def validate_material(pedb_materials, material, delta):
        #     pedb_mat = pedb_materials[material["name"]]
        #     if not material["dielectric_model_frequency"]:
        #         assert (pedb_mat.conductivity - material["conductivity"]) < delta
        #         assert (pedb_mat.permittivity - material["permittivity"]) < delta
        #         assert (pedb_mat.dielectric_loss_tangent - material["dielectric_loss_tangent"]) < delta
        #         assert (pedb_mat.permeability - material["permeability"]) < delta
        #         assert (pedb_mat.magnetic_loss_tangent - material["magnetic_loss_tangent"]) < delta
        #     assert (pedb_mat.mass_density - material["mass_density"]) < delta
        #     assert (pedb_mat.poisson_ratio - material["poisson_ratio"]) < delta
        #     assert (pedb_mat.specific_heat - material["specific_heat"]) < delta
        #     assert (pedb_mat.thermal_conductivity - material["thermal_conductivity"]) < delta
        #     assert (pedb_mat.youngs_modulus - material["youngs_modulus"]) < delta
        #     assert (pedb_mat.thermal_expansion_coefficient - material["thermal_expansion_coefficient"]) < delta
        #     if material["dc_conductivity"] is not None:
        #         assert (pedb_mat.dc_conductivity - material["dc_conductivity"]) < delta
        #     else:
        #         assert pedb_mat.dc_conductivity == material["dc_conductivity"]
        #     if material["dc_permittivity"] is not None:
        #         assert (pedb_mat.dc_permittivity - material["dc_permittivity"]) < delta
        #     else:
        #         assert pedb_mat.dc_permittivity == material["dc_permittivity"]
        #     if material["dielectric_model_frequency"] is not None:
        #         assert (pedb_mat.dielectric_model_frequency - material["dielectric_model_frequency"]) < delta
        #     else:
        #         assert pedb_mat.dielectric_model_frequency == material["dielectric_model_frequency"]
        #     if material["loss_tangent_at_frequency"] is not None:
        #         assert (pedb_mat.loss_tangent_at_frequency - material["loss_tangent_at_frequency"]) < delta
        #     else:
        #         assert pedb_mat.loss_tangent_at_frequency == material["loss_tangent_at_frequency"]
        #     if material["permittivity_at_frequency"] is not None:
        #         assert (pedb_mat.permittivity_at_frequency - material["permittivity_at_frequency"]) < delta
        #     else:
        #         assert pedb_mat.permittivity_at_frequency == material["permittivity_at_frequency"]
        #
        # import json
        #
        # target_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        # out_edb = os.path.join(self.edb_examples.test_folder, "ANSYS-HSD_V1_test.aedb")
        # self.local_scratch.copyfolder(target_path, out_edb)
        # json_path = os.path.join(local_path, "example_models", test_subfolder, "test_mat.json")
        # edbapp = Edb(out_edb, edbversion=desktop_version)
        # edbapp.stackup.load(json_path)
        # edbapp.save_edb()
        # delta = 1e-6
        # f = open(json_path)
        # json_dict = json.load(f)
        # dict_materials = json_dict["materials"]
        # for material_dict in dict_materials.values():
        #     validate_material(edbapp.materials, material_dict, delta)
        # for k, v in json_dict.items():
        #     if k == "layers":
        #         for layer_name, layer in v.items():
        #             pedb_lay = edbapp.stackup.layers[layer_name]
        #             assert list(pedb_lay.color) == layer["color"]
        #             assert pedb_lay.type == layer["type"]
        #             if isinstance(layer["material"], str):
        #                 assert pedb_lay.material.lower() == layer["material"].lower()
        #             else:
        #                 assert 0 == validate_material(edbapp.materials, layer["material"], delta)
        #             if isinstance(layer["dielectric_fill"], str) or layer["dielectric_fill"] is None:
        #                 assert pedb_lay.dielectric_fill == layer["dielectric_fill"]
        #             else:
        #                 assert 0 == validate_material(edbapp.materials, layer["dielectric_fill"], delta)
        #             assert (pedb_lay.thickness - layer["thickness"]) < delta
        #             assert (pedb_lay.etch_factor - layer["etch_factor"]) < delta
        #             assert pedb_lay.roughness_enabled == layer["roughness_enabled"]
        #             if layer["roughness_enabled"]:
        #                 assert (pedb_lay.top_hallhuray_nodule_radius - layer["top_hallhuray_nodule_radius"]) < delta
        #                 assert (pedb_lay.top_hallhuray_surface_ratio - layer["top_hallhuray_surface_ratio"]) < delta
        #                 assert (
        #                     pedb_lay.bottom_hallhuray_nodule_radius - layer["bottom_hallhuray_nodule_radius"]
        #                 ) < delta
        #                 assert (
        #                     pedb_lay.bottom_hallhuray_surface_ratio - layer["bottom_hallhuray_surface_ratio"]
        #                 ) < delta
        #                 assert (pedb_lay.side_hallhuray_nodule_radius - layer["side_hallhuray_nodule_radius"]) < delta
        #                 assert (pedb_lay.side_hallhuray_surface_ratio - layer["side_hallhuray_surface_ratio"]) < delta
        # edbapp.close(terminate_rpc_session=False)
        pass

    def test_19(self):
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.stackup.add_layer_top(name="add_layer_top")
        assert list(edbapp.stackup.layers.values())[0].name == "add_layer_top"
        assert edbapp.stackup.add_layer_bottom(name="add_layer_bottom")
        assert list(edbapp.stackup.layers.values())[-1].name == "add_layer_bottom"
        assert edbapp.stackup.add_layer_below(name="add_layer_below", base_layer_name="1_Top")
        base_layer = edbapp.stackup.layers["1_Top"]
        l_id = edbapp.stackup.layers_by_id.index([base_layer.id, base_layer.name])
        assert edbapp.stackup.layers_by_id[l_id + 1][1] == "add_layer_below"
        assert edbapp.stackup.add_layer_above(name="add_layer_above", base_layer_name="1_Top")
        base_layer = edbapp.stackup.layers["1_Top"]
        l_id = edbapp.stackup.layers_by_id.index([base_layer.id, base_layer.name])
        assert edbapp.stackup.layers_by_id[l_id - 1][1] == "add_layer_above"
        edbapp.close(terminate_rpc_session=False)

    def test_test_layers_consolidated(self):
        edbapp = self.edb_examples.get_si_verse()
        layers = edbapp.stackup.layers
        assert len(layers) == 15
        assert list(edbapp.stackup.layers.keys()) == [
            "1_Top",
            "DE1",
            "Inner1(GND1)",
            "DE2",
            "Inner2(PWR1)",
            "DE3",
            "Inner3(Sig1)",
            "Megtron4-1mm",
            "Inner4(Sig2)",
            "DE5",
            "Inner5(PWR2)",
            "DE6",
            "Inner6(GND2)",
            "DE7",
            "16_Bottom",
        ]
        signal_layer = edbapp.stackup.signal_layers["1_Top"]
        assert not signal_layer.roughness_enabled
        signal_layer.roughness_enabled = True
        assert signal_layer.roughness_enabled
        signal_layer.roughness_enabled = False
        if edbapp.grpc:
            # groisse roughness only implemented in grpc
            assert signal_layer.bottom_groisse_roughness == 0.0
            signal_layer.bottom_groisse_roughness = 1e-6
            assert signal_layer.bottom_groisse_roughness == 1e-6
            signal_layer.top_groisse_roughness = 2e-6
            assert signal_layer.top_groisse_roughness == 2e-6
            signal_layer.side_groisse_roughness = 3e-6
            assert signal_layer.side_groisse_roughness == 3e-6
        signal_layer.bottom_hallhuray_nodule_radius = 1e-9
        assert signal_layer.bottom_hallhuray_nodule_radius == 1e-9
        signal_layer.bottom_hallhuray_surface_ratio = 0.5
        assert signal_layer.bottom_hallhuray_surface_ratio == 0.5
        signal_layer.color = (128, 128, 128)
        assert tuple(signal_layer.color) == (128, 128, 128)  # dotnet returns list so casting as tuple for compatibility
        signal_layer.etch_factor = 0.6
        assert signal_layer.etch_factor == 0.6
        signal_layer.roughness_enabled = True
        assert signal_layer.roughness_enabled is True
        signal_layer.thickness = 1.5e-4
        assert signal_layer.thickness == 1.5e-4
        signal_layer.top_groisse_roughness = 2e-6
        assert signal_layer.top_groisse_roughness == 2e-6
        signal_layer.top_hallhuray_nodule_radius = 2e-9
        assert signal_layer.top_hallhuray_nodule_radius == 2e-9
        signal_layer.top_hallhuray_surface_ratio = 0.7
        assert signal_layer.top_hallhuray_surface_ratio == 0.7
        dielectric_layer = edbapp.stackup.dielectric_layers["DE1"]
        assert dielectric_layer.dielectric_fill is None
        dielectric_layer.color = (200, 200, 200)
        assert tuple(dielectric_layer.color) == (200, 200, 200)
        dielectric_layer.thickness = 2e-4
        assert dielectric_layer.thickness == 2e-4
        assert len(edbapp.stackup.dielectric_layers) == 7
        non_stackup_layers = edbapp.stackup.non_stackup_layers
        assert len(non_stackup_layers) == 11
        outline_layer = non_stackup_layers["Outline"]
        assert not outline_layer.is_stackup_layer
        edbapp.close(terminate_rpc_session=False)
