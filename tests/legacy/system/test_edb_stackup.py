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

"""Tests related to Edb stackup
"""

import math
import os

import pytest

from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
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
        assert edbapp.stackup.add_outline_layer()
        assert "Outline" in edbapp.stackup.non_stackup_layers
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

    def test_stackup_properties_0(self):
        """Evaluate various stackup properties."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0124.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
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
        assert edbapp.stackup["1_Top"].color == [0, 120, 0]
        edbapp.stackup["1_Top"].transparency = 10
        assert edbapp.stackup["1_Top"].transparency == 10
        assert edbapp.stackup.mode == "Laminate"
        edbapp.stackup.mode = "Overlapping"
        assert edbapp.stackup.mode == "Overlapping"
        edbapp.stackup.mode = "MultiZone"
        assert edbapp.stackup.mode == "MultiZone"
        edbapp.stackup.mode = "Overlapping"
        assert edbapp.stackup.mode == "Overlapping"
        assert edbapp.stackup.add_layer("new_bottom", "1_Top", "add_at_elevation", "dielectric", elevation=0.0003)
        edbapp.close()

    def test_stackup_properties_1(self):
        """Evaluate various stackup properties."""
        edbapp = Edb(edbversion=desktop_version)
        import_method = edbapp.stackup.load
        export_method = edbapp.stackup.export

        assert import_method(os.path.join(local_path, "example_models", test_subfolder, "ansys_pcb_stackup.csv"))
        assert "18_Bottom" in edbapp.stackup.layers.keys()
        assert edbapp.stackup.add_layer("19_Bottom", None, "add_on_top", material="iron")
        export_stackup_path = os.path.join(self.local_scratch.path, "export_galileo_stackup.csv")
        assert export_method(export_stackup_path)
        assert os.path.exists(export_stackup_path)

        edbapp.close()

    def test_stackup_properties_2(self):
        """Evaluate various stackup properties."""
        edbapp = Edb(edbversion=desktop_version)
        import_method = edbapp.stackup.load
        export_method = edbapp.stackup.export

        assert import_method(os.path.join(local_path, "example_models", test_subfolder, "ansys_pcb_stackup.csv"))
        assert "18_Bottom" in edbapp.stackup.layers.keys()
        assert edbapp.stackup.add_layer("19_Bottom", None, "add_on_top", material="iron")
        export_stackup_path = os.path.join(self.local_scratch.path, "export_galileo_stackup.csv")
        assert export_method(export_stackup_path)
        assert os.path.exists(export_stackup_path)
        edbapp.close()

    def test_stackup_layer_properties(self):
        """Evaluate various layer properties."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0126.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        edbapp.stackup.load(os.path.join(local_path, "example_models", test_subfolder, "ansys_pcb_stackup.xml"))
        layer = edbapp.stackup["1_Top"]
        layer.name = "TOP"
        assert layer.name == "TOP"
        layer.type = "dielectric"
        assert layer.type == "dielectric"
        layer.type = "signal"
        layer.color = [0, 0, 0]
        assert layer.color == [0, 0, 0]
        layer.transparency = 0
        assert layer.transparency == 0
        layer.etch_factor = 2
        assert layer.etch_factor == 2
        layer.thickness = 50e-6
        assert layer.thickness == 50e-6
        assert layer.lower_elevation
        assert layer.upper_elevation
        layer.is_negative = True
        assert layer.is_negative
        assert not layer.is_via_layer
        assert layer.material == "copper"
        edbapp.close()

    def test_stackup_load_json(self):
        """Import stackup from a file."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        fpath = os.path.join(local_path, "example_models", test_subfolder, "stackup.json")
        edbapp = Edb(source_path, edbversion=desktop_version)
        edbapp.stackup.load(fpath)
        edbapp.close()

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
            "upper_elevation": 0.0,
            "lower_elevation": 0.0,
        }
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        edbapp = Edb(source_path, edbversion=desktop_version)
        json_path = os.path.join(self.local_scratch.path, "exported_stackup.json")

        assert edbapp.stackup.export(json_path)
        with open(json_path, "r") as json_file:
            data = json.load(json_file)
            # Check material
            assert MATERIAL_MEGTRON_4 == data["materials"]["Megtron4"]
            # Check layer
            assert LAYER_DE_2 == data["layers"]["DE2"]
        edbapp.close()

    def test_stackup_load_xml(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.stackup.load(os.path.join(local_path, "example_models", test_subfolder, "ansys_pcb_stackup.xml"))
        assert "Inner1" in list(edbapp.stackup.layers.keys())  # Renamed layer
        assert "DE1" not in edbapp.stackup.layers.keys()  # Removed layer
        assert edbapp.stackup.export(os.path.join(self.local_scratch.path, "stackup.xml"))
        assert round(edbapp.stackup.signal_layers["1_Top"].thickness, 6) == 3.5e-5

    def test_stackup_load_layer_renamed(self):
        """Import stackup from a file."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        fpath = os.path.join(local_path, "example_models", test_subfolder, "stackup_renamed.json")
        edbapp = Edb(source_path, edbversion=desktop_version)
        edbapp.stackup.load(fpath, rename=True)
        assert "1_Top_renamed" in edbapp.stackup.layers
        assert "DE1_renamed" in edbapp.stackup.layers
        assert "16_Bottom_renamed" in edbapp.stackup.layers
        edbapp.close()

    def test_stackup_place_in_3d_with_flipped_stackup(self):
        """Place into another cell using 3d placement method with and
        without flipping the current layer stackup.
        """
        edb_path = os.path.join(self.target_path2, "edb.def")
        edb1 = Edb(edb_path, edbversion=desktop_version)

        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=False,
            solder_height=0.0,
        )
        edb2.close()
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=False,
            solder_height=0.0,
        )
        edb2.close()
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=True,
            solder_height=0.0,
        )
        edb2.close()
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=True,
            solder_height=0.0,
        )
        edb2.close()
        edb1.close()

    def test_stackup_place_instance_with_flipped_stackup(self):
        """Place into another cell using 3d placement method with and
        without flipping the current layer stackup.
        """
        edb_path = os.path.join(self.target_path2, "edb.def")
        edb1 = Edb(edb_path, edbversion=desktop_version)

        edb2 = Edb(self.target_path, edbversion=desktop_version)
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
        edb2.close()
        edb1.close()

    def test_stackup_place_in_layout_with_flipped_stackup(self):
        """Place into another cell using layer placement method with and
        without flipping the current layer stackup.
        """
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.stackup.place_in_layout(
            self.edbapp,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=True,
        )
        edb2.close()

    def test_stackup_place_on_top_of_lam_with_mold(self):
        """Place on top lam with mold using 3d placement method"""
        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip.aedb"),
            edbversion=desktop_version,
        )
        try:
            cellInstances = laminateEdb.layout.cell_instances
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=False,
                place_on_top=True,
            )
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            chipEdb.close()
            laminateEdb.close()

    def test_stackup_place_on_bottom_of_lam_with_mold(self):
        """Place on lam with mold using 3d placement method"""

        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip_flipped_stackup.aedb"),
            edbversion=desktop_version,
        )
        try:
            layout = laminateEdb.active_layout
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.stackup.place_in_layout_3d_placement(
                laminateEdb,
                angle=0.0,
                offset_x=0.0,
                offset_y=0.0,
                flipped_stackup=False,
                place_on_top=False,
            )
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            assert loc.IsEqual(chipEdb.point_3d(0.0, 0.0, chipEdb.edb_value(-90e-6)))
        finally:
            chipEdb.close()
            laminateEdb.close()

    def test_stackup_place_on_top_of_lam_with_mold_solder(self):
        """Place on top of lam with mold solder using 3d placement method."""
        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip_solder.aedb"),
            edbversion=desktop_version,
        )
        try:
            layout = laminateEdb.active_layout
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
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            originPoint = chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb_api.geometry.point3d_data(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(zeroValue)
            assert loc.IsEqual(chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, chipEdb.edb_value(190e-6)))
        finally:
            chipEdb.close()
            laminateEdb.close()

    def test_stackup_place_on_bottom_of_lam_with_mold_solder(self):
        """Place on bottom of lam with mold solder using 3d placement method."""

        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip_solder.aedb"),
            edbversion=desktop_version,
        )
        try:
            layout = laminateEdb.active_layout
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
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            originPoint = chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb_api.geometry.point3d_data(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(chipEdb.edb_value(math.pi))
            assert loc.IsEqual(chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, chipEdb.edb_value(-20e-6)))
        finally:
            chipEdb.close()
            laminateEdb.close()

    def test_stackup_place_on_top_with_zoffset_chip(self):
        """Place on top of lam with mold chip zoffset using 3d placement method."""
        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset.aedb"),
            edbversion=desktop_version,
        )
        try:
            layout = laminateEdb.active_layout
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
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            originPoint = chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb_api.geometry.point3d_data(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(zeroValue)
            assert loc.IsEqual(chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, chipEdb.edb_value(160e-6)))
        finally:
            chipEdb.close()
            laminateEdb.close()

    def test_stackup_place_on_bottom_with_zoffset_chip(self):
        """Place on bottom of lam with mold chip zoffset using 3d placement method."""

        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset.aedb"),
            edbversion=desktop_version,
        )
        try:
            layout = laminateEdb.active_layout
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
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            originPoint = chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb_api.geometry.point3d_data(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(chipEdb.edb_value(math.pi))
            assert loc.IsEqual(chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, chipEdb.edb_value(10e-6)))
        finally:
            chipEdb.close()
            laminateEdb.close()

    def test_stackup_place_on_top_with_zoffset_solder_chip(self):
        """Place on top of lam with mold chip zoffset using 3d placement method."""
        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset_solder.aedb"),
            edbversion=desktop_version,
        )
        try:
            layout = laminateEdb.active_layout
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
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            originPoint = chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb_api.geometry.point3d_data(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(zeroValue)
            assert loc.IsEqual(chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, chipEdb.edb_value(150e-6)))
        finally:
            chipEdb.close()
            laminateEdb.close()

    def test_stackup_place_on_bottom_with_zoffset_solder_chip(self):
        """Place on bottom of lam with mold chip zoffset using 3d placement method."""

        laminateEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
            edbversion=desktop_version,
        )
        chipEdb = Edb(
            os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset_solder.aedb"),
            edbversion=desktop_version,
        )
        try:
            layout = laminateEdb.active_layout
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
            merged_cell = chipEdb.edb_api.cell.cell.FindByName(
                chipEdb.active_db, chipEdb.edb_api.cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
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
            originPoint = chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb_api.geometry.point3d_data(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(chipEdb.edb_value(math.pi))
            assert loc.IsEqual(chipEdb.edb_api.geometry.point3d_data(zeroValue, zeroValue, chipEdb.edb_value(20e-6)))
        finally:
            chipEdb.close()
            laminateEdb.close()

    def test_18_stackup(self):
        def validate_material(pedb_materials, material, delta):
            pedb_mat = pedb_materials[material["name"]]
            if not material["dielectric_model_frequency"]:
                assert (pedb_mat.conductivity - material["conductivity"]) < delta
                assert (pedb_mat.permittivity - material["permittivity"]) < delta
                assert (pedb_mat.dielectric_loss_tangent - material["dielectric_loss_tangent"]) < delta
                assert (pedb_mat.permeability - material["permeability"]) < delta
                assert (pedb_mat.magnetic_loss_tangent - material["magnetic_loss_tangent"]) < delta
            assert (pedb_mat.mass_density - material["mass_density"]) < delta
            assert (pedb_mat.poisson_ratio - material["poisson_ratio"]) < delta
            assert (pedb_mat.specific_heat - material["specific_heat"]) < delta
            assert (pedb_mat.thermal_conductivity - material["thermal_conductivity"]) < delta
            assert (pedb_mat.youngs_modulus - material["youngs_modulus"]) < delta
            assert (pedb_mat.thermal_expansion_coefficient - material["thermal_expansion_coefficient"]) < delta
            if material["dc_conductivity"] is not None:
                assert (pedb_mat.dc_conductivity - material["dc_conductivity"]) < delta
            else:
                assert pedb_mat.dc_conductivity == material["dc_conductivity"]
            if material["dc_permittivity"] is not None:
                assert (pedb_mat.dc_permittivity - material["dc_permittivity"]) < delta
            else:
                assert pedb_mat.dc_permittivity == material["dc_permittivity"]
            if material["dielectric_model_frequency"] is not None:
                assert (pedb_mat.dielectric_model_frequency - material["dielectric_model_frequency"]) < delta
            else:
                assert pedb_mat.dielectric_model_frequency == material["dielectric_model_frequency"]
            if material["loss_tangent_at_frequency"] is not None:
                assert (pedb_mat.loss_tangent_at_frequency - material["loss_tangent_at_frequency"]) < delta
            else:
                assert pedb_mat.loss_tangent_at_frequency == material["loss_tangent_at_frequency"]
            if material["permittivity_at_frequency"] is not None:
                assert (pedb_mat.permittivity_at_frequency - material["permittivity_at_frequency"]) < delta
            else:
                assert pedb_mat.permittivity_at_frequency == material["permittivity_at_frequency"]

        import json

        target_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        out_edb = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_test.aedb")
        self.local_scratch.copyfolder(target_path, out_edb)
        json_path = os.path.join(local_path, "example_models", test_subfolder, "test_mat.json")
        edbapp = Edb(out_edb, edbversion=desktop_version)
        edbapp.stackup.load(json_path)
        edbapp.save_edb()
        delta = 1e-6
        f = open(json_path)
        json_dict = json.load(f)
        dict_materials = json_dict["materials"]
        for material_dict in dict_materials.values():
            validate_material(edbapp.materials, material_dict, delta)
        for k, v in json_dict.items():
            if k == "layers":
                for layer_name, layer in v.items():
                    pedb_lay = edbapp.stackup.layers[layer_name]
                    assert list(pedb_lay.color) == layer["color"]
                    assert pedb_lay.type == layer["type"]
                    if isinstance(layer["material"], str):
                        assert pedb_lay.material.lower() == layer["material"].lower()
                    else:
                        assert 0 == validate_material(edbapp.materials, layer["material"], delta)
                    if isinstance(layer["dielectric_fill"], str) or layer["dielectric_fill"] is None:
                        assert pedb_lay.dielectric_fill == layer["dielectric_fill"]
                    else:
                        assert 0 == validate_material(edbapp.materials, layer["dielectric_fill"], delta)
                    assert (pedb_lay.thickness - layer["thickness"]) < delta
                    assert (pedb_lay.etch_factor - layer["etch_factor"]) < delta
                    # assert pedb_lay.roughness_enabled == layer["roughness_enabled"]
                    if layer["roughness_enabled"]:
                        assert (pedb_lay.top_hallhuray_nodule_radius - layer["top_hallhuray_nodule_radius"]) < delta
                        assert (pedb_lay.top_hallhuray_surface_ratio - layer["top_hallhuray_surface_ratio"]) < delta
                        assert (
                            pedb_lay.bottom_hallhuray_nodule_radius - layer["bottom_hallhuray_nodule_radius"]
                        ) < delta
                        assert (
                            pedb_lay.bottom_hallhuray_surface_ratio - layer["bottom_hallhuray_surface_ratio"]
                        ) < delta
                        assert (pedb_lay.side_hallhuray_nodule_radius - layer["side_hallhuray_nodule_radius"]) < delta
                        assert (pedb_lay.side_hallhuray_surface_ratio - layer["side_hallhuray_surface_ratio"]) < delta
        edbapp.close()

    def test_19(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
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

    def test_20_layer_properties(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        data = {
            "name": "1_Top",
            "type": "signal",
            "material": "copper",
            "fill_material": "Solder Resist",
            "thickness": "0.03mm",
            "color": [255, 0, 0],
            "roughness": {
                "top": {"model": "huray", "nodule_radius": "0.1um", "surface_ratio": "1"},
                "bottom": {"model": "groisse", "roughness": "2um"},
                "side": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "2.9"},
                "enabled": True,
            },
        }
        edbapp.stackup.layers["1_Top"].properties = data
        layer_data = edbapp.stackup.layers["1_Top"].properties
        assert layer_data == data
        edbapp.close()

    def test_roughness(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        for layer_name, layer in edbapp.stackup.signal_layers.items():
            layer.roughness_enabled = True
            layer.etch_factor = 0.1
            layer.top_hallhuray_nodule_radius = 4e-7
            layer.top_hallhuray_surface_ratio = 2.7
            layer.bottom_hallhuray_nodule_radius = 4e-7
            layer.bottom_hallhuray_surface_ratio = 2.7
            layer.side_hallhuray_nodule_radius = 4e-7
            layer.side_hallhuray_surface_ratio = 2.7
            assert layer.top_hallhuray_nodule_radius == 4e-7
            assert layer.top_hallhuray_surface_ratio == 2.7
            assert layer.bottom_hallhuray_nodule_radius == 4e-7
            assert layer.bottom_hallhuray_surface_ratio == 2.7
            assert layer.side_hallhuray_nodule_radius == 4e-7
            assert layer.side_hallhuray_surface_ratio == 2.7
        edbapp.close()
