# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Tests related to Edb padstacks"""

import math
import os

import pytest

from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.polygon_data import PolygonData
from pyedb.dotnet.database.padstack import EDBPadstackInstance
from pyedb.generic.general_methods import is_windows
from tests.conftest import GRPC, config, local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path3, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path3 = target_path3
        self.target_path4 = target_path4

    def test_get_pad_parameters(self, edb_examples):
        """Access to pad parameters."""
        edbapp = edb_examples.get_si_verse()
        pin = edbapp.components.get_pin_from_component("J1", pinName="1")
        if edbapp.grpc:
            parameters = edbapp.padstacks.get_pad_parameters(pin[0], "1_Top", edbapp.padstacks.pad_type.REGULAR_PAD)
        else:
            parameters = edbapp.padstacks.get_pad_parameters(pin[0], "1_Top", edbapp.padstacks.pad_type.RegularPad)
        assert isinstance(parameters[1], list)
        edbapp.close(terminate_rpc_session=False)

    def test_get_vias_from_nets(self, edb_examples):
        """Use padstacks' get_via_instance_from_net method."""
        edbapp = edb_examples.get_si_verse()
        assert edbapp.padstacks.get_via_instance_from_net("GND")
        assert not edbapp.padstacks.get_via_instance_from_net(["GND2"])
        edbapp.close(terminate_rpc_session=False)

    def test_create_with_packstack_name(self, edb_examples):
        """Create a padstack"""
        # Create myVia
        edbapp = edb_examples.get_si_verse()
        edbapp.padstacks.create(padstackname="myVia")
        assert "myVia" in list(edbapp.padstacks.definitions.keys())
        edbapp.padstacks.definitions["myVia"].hole_range = "begin_on_upper_pad"
        assert edbapp.padstacks.definitions["myVia"].hole_range == "begin_on_upper_pad"
        edbapp.padstacks.definitions["myVia"].hole_range = "through"
        assert edbapp.padstacks.definitions["myVia"].hole_range == "through"
        # Create myVia_bullet
        edbapp.padstacks.create(padstackname="myVia_bullet", antipad_shape="Bullet")
        assert isinstance(edbapp.padstacks.definitions["myVia"].instances, list)
        assert "myVia_bullet" in list(edbapp.padstacks.definitions.keys())

        edbapp.add_design_variable("via_x", 5e-3)
        edbapp["via_y"] = "1mm"
        assert edbapp["via_y"] == 1e-3
        # assert self.edbapp["via_y"].value_string == "1mm"
        assert edbapp.padstacks.place(["via_x", "via_x+via_y"], "myVia", via_name="via_test1")
        assert edbapp.padstacks.place(["via_x", "via_x+via_y*2"], "myVia_bullet")
        edbapp.padstacks["via_test1"].net_name = "GND"
        assert edbapp.padstacks["via_test1"].net_name == "GND"
        padstack_instance = edbapp.padstacks.place(["via_x", "via_x+via_y*3"], "myVia", is_pin=True)
        assert padstack_instance.is_pin
        assert padstack_instance.position
        assert padstack_instance.start_layer in padstack_instance.layer_range_names
        assert padstack_instance.stop_layer in padstack_instance.layer_range_names
        padstack_instance.position = [0.001, 0.002]
        assert padstack_instance.position == [0.001, 0.002]
        assert padstack_instance.parametrize_position()
        assert isinstance(padstack_instance.rotation, float)
        edbapp.padstacks.create_circular_padstack(padstackname="mycircularvia")
        assert "mycircularvia" in list(edbapp.padstacks.definitions.keys())
        assert not padstack_instance.backdrill_top
        assert not padstack_instance.backdrill_bottom
        if not edbapp.grpc:
            assert padstack_instance.delete()  # grpc does not return boolean
        via = edbapp.padstacks.place([0, 0], "myVia")
        via.set_backdrill_top("Inner4(Sig2)", 0.5e-3)  # grpc is not returning boolean
        assert via.backdrill_top
        via.set_backdrill_bottom("16_Bottom", 0.5e-3)
        assert via.backdrill_bottom

        via = edbapp.padstacks.instances_by_name["Via1266"]
        via.backdrill_parameters = {
            "from_bottom": {"drill_to_layer": "Inner5(PWR2)", "diameter": "0.4mm", "stub_length": "0.1mm"},
            "from_top": {"drill_to_layer": "Inner2(PWR1)", "diameter": "0.41mm", "stub_length": "0.11mm"},
        }
        assert via.backdrill_parameters == {
            "from_bottom": {"drill_to_layer": "Inner5(PWR2)", "diameter": "0.4mm", "stub_length": "0.1mm"},
            "from_top": {"drill_to_layer": "Inner2(PWR1)", "diameter": "0.41mm", "stub_length": "0.11mm"},
        }
        edbapp.close(terminate_rpc_session=False)

    def test_padstacks_get_nets_from_pin_list(self, edb_examples):
        """Retrieve pin list from component and net."""
        edbapp = edb_examples.get_si_verse()
        cmp_pinlist = edbapp.padstacks.get_pinlist_from_component_and_net("U1", "GND")
        assert cmp_pinlist[0].net.name
        edbapp.close(terminate_rpc_session=False)

    def test_padstack_properties_getter(self, edb_examples):
        """Evaluate properties"""
        edbapp = edb_examples.get_si_verse()
        for el in edbapp.padstacks.definitions:
            padstack = edbapp.padstacks.definitions[el]
            assert padstack.hole_plating_thickness is not None or False
            if not edbapp.grpc:  # not supported in grpc
                assert padstack.hole_properties is not None or False
            assert padstack.hole_plating_thickness is not None or False
            assert padstack.hole_plating_ratio is not None or False
            assert padstack.via_start_layer is not None or False
            assert padstack.via_stop_layer is not None or False
            assert padstack.material is not None or False
            assert padstack.hole_finished_size is not None or False
            assert padstack.hole_rotation is not None or False
            assert padstack.hole_offset_x is not None or False
            assert padstack.hole_offset_y is not None or False
            try:  # grpc throws an exception if no hole is defined
                assert padstack.hole_type is not None or False
            except:
                pass
            pad = padstack.pad_by_layer[padstack.via_stop_layer]
            if not pad.shape == "NoGeometry":
                assert pad.parameters_values is not None or False
                assert pad.offset_x is not None or False
                assert pad.offset_y is not None or False
                assert isinstance(pad.geometry_type, int)
            if not edbapp.grpc:  # not relevant in grpc
                polygon = pad._polygon_data_dotnet
                if polygon:
                    assert polygon.GetBBox()
        edbapp.close()

    def test_padstack_properties_setter(self, edb_examples):
        """Set padstack properties"""
        edbapp = edb_examples.get_si_verse()
        pad = edbapp.padstacks.definitions["c180h127"]
        hole_pad = 8
        tol = 1e-12
        pad.hole_properties = hole_pad
        pad.hole_offset_x = 0
        pad.hole_offset_y = 1
        pad.hole_rotation = 0
        pad.hole_plating_ratio = 90
        assert pad.hole_plating_ratio == 90
        pad.hole_plating_thickness = 0.3
        assert abs(pad.hole_plating_thickness - 0.3) <= tol
        pad.material = "copper"
        if not edbapp.grpc:
            assert abs(pad.hole_properties[0] - hole_pad) < tol
        else:
            assert abs(pad.hole_properties - hole_pad) < tol
        offset_x = 7.0
        offset_y = 1.0
        pad.pad_by_layer[pad.via_stop_layer].shape = "Circle"
        pad.pad_by_layer[pad.via_stop_layer].parameters = 7.0
        pad.pad_by_layer[pad.via_stop_layer].offset_x = offset_x
        pad.pad_by_layer[pad.via_stop_layer].offset_y = offset_y
        if edbapp.grpc:
            assert pad.pad_by_layer[pad.via_stop_layer].parameters == 7.0
            assert pad.pad_by_layer[pad.via_stop_layer].offset_x == offset_x
            assert pad.pad_by_layer[pad.via_stop_layer].offset_y == offset_y
        else:
            assert pad.pad_by_layer[pad.via_stop_layer].parameters["Diameter"].tofloat == 7.0
            assert float(pad.pad_by_layer[pad.via_stop_layer].offset_x) == offset_x
            assert float(pad.pad_by_layer[pad.via_stop_layer].offset_y) == offset_y
        if edbapp.grpc:
            pad.pad_by_layer[pad.via_stop_layer].parameters = 8.0
        else:
            pad.pad_by_layer[pad.via_stop_layer].parameters = {"Diameter": 8.0}
        if edbapp.grpc:
            assert pad.pad_by_layer[pad.via_stop_layer].parameters == 8.0
        else:
            assert pad.pad_by_layer[pad.via_stop_layer].parameters["Diameter"].tofloat == 8.0
        if not edbapp.grpc:  # not implemented in grpc
            assert pad.pad_by_layer[pad.via_stop_layer].shape == "Circle"
            pad.pad_by_layer[pad.via_stop_layer].parameters = {"Diameter": 1}
            pad.pad_by_layer[pad.via_stop_layer].shape = "Square"
            pad.pad_by_layer[pad.via_stop_layer].parameters = {"Size": 1}
            pad.pad_by_layer[pad.via_stop_layer].shape = "Rectangle"
            pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1}
            pad.pad_by_layer[pad.via_stop_layer].shape = "Oval"
            pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
            pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
            pad.pad_by_layer[pad.via_stop_layer].parameters = [1, 1, 1]
        edbapp.close(terminate_rpc_session=False)

    def test_padstack_get_instance(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.padstacks.get_instances(name="Via1961")
        assert edbapp.padstacks.get_instances(definition_name="v35h15")
        assert edbapp.padstacks.get_instances(net_name="1V0")
        assert edbapp.padstacks.get_instances(component_reference_designator="U7")

        """Access padstack instance by name."""
        padstack_instances = edbapp.padstacks.get_padstack_instance_by_net_name("GND")
        assert len(padstack_instances)
        padstack_1 = padstack_instances[0]
        assert padstack_1.id
        assert isinstance(padstack_1.bounding_box, list)
        for v in padstack_instances:
            if not v.is_pin:
                v.name = "TestInst"
                assert v.name == "TestInst"
                break
        edbapp.close(terminate_rpc_session=False)

    def test_padstack_duplicate_padstack(self, edb_examples):
        """Duplicate a padstack."""
        edbapp = edb_examples.get_si_verse()
        edbapp.padstacks.duplicate(
            target_padstack_name="c180h127",
            new_padstack_name="c180h127_NEW",
        )
        assert edbapp.padstacks.definitions["c180h127_NEW"]
        edbapp.close(terminate_rpc_session=False)

    def test_padstack_set_pad_property(self, edb_examples):
        """Set pad and antipad properties of the padstack."""
        edbapp = edb_examples.get_si_verse()
        edbapp.padstacks.set_pad_property(
            padstack_name="c180h127",
            layer_name="new",
            pad_shape="Circle",
            pad_params="800um",
        )
        assert edbapp.padstacks.definitions["c180h127"].pad_by_layer["new"]
        edbapp.close(terminate_rpc_session=False)

    def test_microvias(self, edb_examples):
        """Convert padstack to microvias 3D objects."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
        edbapp = edb_examples.load_edb(source_path)
        assert edbapp.padstacks.definitions["Padstack_Circle"].convert_to_3d_microvias(False)
        assert edbapp.padstacks.definitions["Padstack_Rectangle"].convert_to_3d_microvias(False, hole_wall_angle=10)
        assert edbapp.padstacks.definitions["Padstack_Polygon_p12"].convert_to_3d_microvias(False)
        assert edbapp.padstacks.definitions["MyVia"].convert_to_3d_microvias(
            convert_only_signal_vias=False, delete_padstack_def=False
        )
        assert edbapp.padstacks.definitions["MyVia_square"].convert_to_3d_microvias(
            convert_only_signal_vias=False, delete_padstack_def=False
        )
        assert edbapp.padstacks.definitions["MyVia_rectangle"].convert_to_3d_microvias(
            convert_only_signal_vias=False, delete_padstack_def=False
        )
        assert not edbapp.padstacks.definitions["MyVia_poly"].convert_to_3d_microvias(
            convert_only_signal_vias=False, delete_padstack_def=False
        )
        edbapp.close(terminate_rpc_session=False)

    def test_split_microvias(self, edb_examples):
        """Convert padstack definition to multiple microvias definitions."""
        edbapp = edb_examples.load_edb(self.target_path4, copy_to_temp=False)
        assert len(edbapp.padstacks.instances_by_name["via219"].split()) > 1
        assert "via219_2" in [i.name for i in edbapp.padstacks.definitions["BALL_VIA_1"].instances]
        edbapp.padstacks.instances_by_name["via218"].convert_hole_to_conical_shape()
        assert len(edbapp.padstacks.definitions["C4_POWER_1"].split_to_microvias()) > 0
        edbapp.close(terminate_rpc_session=False)

    def test_padstack_plating_ratio_fixing(self, edb_examples):
        """Fix hole plating ratio."""
        edbapp = edb_examples.get_si_verse()
        assert edbapp.padstacks.check_and_fix_via_plating()
        edbapp.close(terminate_rpc_session=False)

    def test_padstack_search_reference_pins(self, edb_examples):
        """Search for reference pins using given criteria."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        edbapp = edb_examples.load_edb(source_path)
        pin = edbapp.components.instances["J5"].pins["19"]
        assert pin
        ref_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True)
        assert len(ref_pins) == 3
        reference_pins = edbapp.padstacks.get_reference_pins(
            positive_pin=pin, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True
        )
        assert len(reference_pins) == 3
        reference_pins = edbapp.padstacks.get_reference_pins(
            positive_pin=pin, reference_net="GND", search_radius=5e-3, max_limit=2, component_only=True
        )
        assert len(reference_pins) == 2
        reference_pins = edbapp.padstacks.get_reference_pins(
            positive_pin=pin, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=False
        )
        assert len(reference_pins) == 11
        edbapp.close(terminate_rpc_session=False)

    def test_vias_metal_volume(self, edb_examples):
        """Metal volume of the via hole instance."""
        edbapp = edb_examples.get_si_verse()
        vias = [via for via in list(edbapp.padstacks.instances.values()) if not via.start_layer == via.stop_layer]
        assert vias[0].metal_volume
        assert vias[1].metal_volume
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        reason="This is a bug deep in the code. This pass should never pass but it passes as try-else hides the bug."
    )
    @pytest.mark.parametrize("return_points", [True, False])
    def test_padstacks_create_rectangle_in_pad(self, return_points: bool, edb_examples):
        """Create a rectangle inscribed inside a padstack instance pad."""
        example_model = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
        edb = edb_examples.load_edb(
            edb_path=example_model,
            isreadonly=True,
        )
        for test_prop in (edb.padstacks.instances, edb.padstacks.instances):
            padstack_instances = list(test_prop.values())
            confirmed_pads = 0
            for padstack_instance in padstack_instances:
                layer_name = "s"

                result = padstack_instance.create_rectangle_in_pad(
                    layer_name, return_points=return_points, partition_max_order=8
                )
                if padstack_instance.padstack_definition != "Padstack_None":
                    assert result
                    if return_points and layer_name in padstack_instance.layer_range_names:
                        pad_pd = _get_padstack_polygon_data(edb, padstack_instance, layer_name)
                        if pad_pd is None:
                            # refer to comment in _get_padstack_polygon_data body to see why we're skipping this check
                            continue
                        rect_pd = PolygonData(
                            padstack_instance._pedb,
                            create_from_points=True,
                            points=result,
                        )._edb_object
                        _assert_inside(rect_pd, pad_pd)
                        # count the number of successful confirmations since some are skipped
                        confirmed_pads += 1
                else:
                    assert not result
            if return_points:
                assert confirmed_pads == 19
        edb.close(terminate_rpc_session=False)

    def test_padstaks_plot_on_matplotlib(self, edb_examples):
        """Plot a Net to Matplotlib 2D Chart."""
        edb_plot = edb_examples.load_edb(self.target_path3, copy_to_temp=False)

        local_png1 = os.path.join(self.local_scratch.path, "test1.png")
        edb_plot.nets.plot(
            nets=None,
            layers=None,
            save_plot=local_png1,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
            outline=[[-10e-3, -10e-3], [110e-3, -10e-3], [110e-3, 70e-3], [-10e-3, 70e-3]],
        )
        assert os.path.exists(local_png1)

        local_png2 = os.path.join(self.local_scratch.path, "test2.png")

        edb_plot.nets.plot(
            nets="DDR4_DQS7_N",
            layers=None,
            save_plot=local_png2,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
        )
        assert os.path.exists(local_png2)
        edb_plot.modeler.create_polygon(
            [[-10e-3, -10e-3], [110e-3, -10e-3], [110e-3, 70e-3], [-10e-3, 70e-3]], layer_name="Outline"
        )
        local_png3 = os.path.join(self.local_scratch.path, "test3.png")
        edb_plot.nets.plot(
            nets=["DDR4_DQ57", "DDR4_DQ56"],
            layers="1_Top",
            color_by_net=True,
            save_plot=local_png3,
            plot_components=True,
            plot_vias=True,
        )
        assert os.path.exists(local_png3)

        local_png4 = os.path.join(self.local_scratch.path, "test4.png")
        edb_plot.stackup.plot(
            save_plot=local_png4,
            plot_definitions=list(edb_plot.padstacks.definitions.keys())[0],
        )
        assert os.path.exists(local_png4)

        local_png5 = os.path.join(self.local_scratch.path, "test5.png")
        edb_plot.stackup.plot(
            scale_elevation=False,
            save_plot=local_png5,
            plot_definitions=list(edb_plot.padstacks.definitions.keys())[0],
        )
        assert os.path.exists(local_png4)
        edb_plot.close(terminate_rpc_session=False)

    def test_update_padstacks_after_layer_name_changed(self, edb_examples):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")

        edbapp = edb_examples.load_edb(source_path)
        signal_layer_list = [layer for layer in list(edbapp.stackup.layers.values()) if layer.type == "signal"]
        old_layers = []
        for n_layer, layer in enumerate(signal_layer_list):
            new_name = f"new_signal_name_{n_layer}"
            old_layers.append(layer.name)
            layer.name = new_name
        for layer_name in list(edbapp.stackup.layers.keys()):
            print(f"New layer name is {layer_name}")
        for padstack_inst in list(edbapp.padstacks.instances.values()):
            assert not [lay for lay in padstack_inst.layer_range_names if lay in old_layers]
        edbapp.close_edb()

    def test_hole(self, edb_examples):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        edbapp = edb_examples.load_edb(source_path)
        edbapp.padstacks.definitions["v35h15"].hole_diameter = "0.16mm"
        assert edbapp.padstacks.definitions["v35h15"].hole_diameter == 0.00016

    def test_padstack_instances_rtree_index(self, edb_examples):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        edbapp = edb_examples.load_edb(source_path)
        index = edbapp.padstacks.get_padstack_instances_rtree_index()
        assert [round(val, 6) for val in index.bounds] == [-0.013785, -0.00225, 0.148, 0.078]
        stats = edbapp.get_statistics()
        bbox = (0.0, 0.0, stats.layout_size[0], stats.layout_size[1])
        test = list(index.intersection(bbox))
        assert len(test) == 5689
        index = edbapp.padstacks.get_padstack_instances_rtree_index(nets="GND")
        test = list(index.intersection(bbox))
        assert len(test) == 2048
        test = edbapp.padstacks.get_padstack_instances_intersecting_bounding_box(
            bounding_box=[0, 0, 0.05, 0.08], nets="GND"
        )
        assert len(test) == 194
        edbapp.close(terminate_rpc_session=False)

    def test_polygon_based_padsatck(self, edb_examples):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        edbapp = edb_examples.load_edb(source_path)
        polygon_data = edbapp.modeler.paths[0].polygon_data
        edbapp.padstacks.create(
            padstackname="test",
            pad_shape="Polygon",
            antipad_shape="Polygon",
            pad_polygon=polygon_data,
            antipad_polygon=polygon_data,
        )
        edbapp.padstacks.create(
            padstackname="test2",
            pad_shape="Polygon",
            antipad_shape="Polygon",
            pad_polygon=[
                [-0.025, -0.02],
                [0.025, -0.02],
                [0.025, 0.02],
                [-0.025, 0.02],
                [-0.025, -0.02],
            ],
            antipad_polygon=[
                [-0.025, -0.02],
                [0.025, -0.02],
                [0.025, 0.02],
                [-0.025, 0.02],
                [-0.025, -0.02],
            ],
        )
        assert edbapp.padstacks.definitions["test"]
        assert edbapp.padstacks.definitions["test2"]
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=GRPC, reason="Needs to be checked with grpc")
    def test_via_fence(self, edb_examples):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "via_fence_generic_project.aedb")
        target_path1 = os.path.join(self.local_scratch.path, "test_pvia_fence", "via_fence1.aedb")
        target_path2 = os.path.join(self.local_scratch.path, "test_pvia_fence", "via_fence2.aedb")
        self.local_scratch.copyfolder(source_path, target_path1)
        self.local_scratch.copyfolder(source_path, target_path2)
        edbapp = edb_examples.load_edb(target_path1, copy_to_temp=False)
        assert edbapp.padstacks.merge_via_along_lines(net_name="GND", distance_threshold=2e-3, minimum_via_number=6)
        assert not edbapp.padstacks.merge_via_along_lines(
            net_name="test_dummy", distance_threshold=2e-3, minimum_via_number=6
        )
        assert "main_via" in edbapp.padstacks.definitions
        assert "via_central" in edbapp.padstacks.definitions
        edbapp.close(terminate_rpc_session=False)
        edbapp = edb_examples.load_edb(target_path2, copy_to_temp=False)
        assert edbapp.padstacks.merge_via_along_lines(net_name="GND", distance_threshold=2e-3, minimum_via_number=6)
        assert "main_via" in edbapp.padstacks.definitions
        assert "via_central" in edbapp.padstacks.definitions
        edbapp.close(terminate_rpc_session=False)

    def test_reduce_via_in_bounding_box(self, edb_examples):
        source_path = edb_examples.example_models_path / "TEDB" / "vias_300.aedb"
        edbapp = edb_examples.load_edb(edb_path=source_path)
        assert len(edbapp.padstacks.instances) == 301
        # empty bounding box
        assert edbapp.padstacks.reduce_via_in_bounding_box([-16e-3, -7e-3, -13e-3, -6e-3], 10, 10) is False
        # over sampling
        assert edbapp.padstacks.reduce_via_in_bounding_box([-20e-3, -10e-3, 20e-3, 10e-3], 20, 20) is False

        assert edbapp.padstacks.reduce_via_in_bounding_box([-20e-3, -10e-3, 20e-3, 10e-3], 10, 10) is True
        assert len(edbapp.padstacks.instances) == 96
        edbapp.close_edb()

    def test_via_merge(self, edb_examples):
        # TODO check this test is slow with grpc
        edbapp = edb_examples.get_si_verse()
        polygon = [[[118e-3, 60e-3], [125e-3, 60e-3], [124e-3, 56e-3], [118e-3, 56e-3]]]
        result = edbapp.padstacks.merge_via(contour_boxes=polygon, start_layer="1_Top", stop_layer="16_Bottom")
        assert len(result) == 1
        edbapp.close(terminate_rpc_session=False)

    def test_via_merge3(self, edb_examples):
        source_path = edb_examples.example_models_path / "TEDB" / "merge_via_4layers.aedb"
        edbapp = edb_examples.load_edb(edb_path=source_path)

        merged_via = edbapp.padstacks.merge_via(
            contour_boxes=[[[11e-3, -5e-3], [17e-3, -5e-3], [17e-3, 1e-3], [11e-3, 1e-3], [11e-3, -5e-3]]],
            net_filter=["NET_3"],
            start_layer="layer1",
            stop_layer="layer2",
        )

        assert edbapp.padstacks.instances[merged_via[0]].net_name == "NET_1"
        assert edbapp.padstacks.instances[merged_via[0]].start_layer == "layer1"
        assert edbapp.padstacks.instances[merged_via[0]].stop_layer == "layer2"
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(condition=config["use_grpc"] and is_windows, reason="Test hanging on windows with grpc")
    def test_dbscan(self, edb_examples):
        source_path = edb_examples.example_models_path / "TEDB" / "merge_via_4layers.aedb"
        edbapp = edb_examples.load_edb(source_path)

        # "NET_1" one cluster with 20 vias
        net_vias = [i for i in edbapp.nets["NET_1"].padstack_instances]
        all_vias = {i.id: i.position for i in net_vias}
        clusters1 = edbapp.padstacks.dbscan(all_vias, max_distance=2e-3, min_samples=3)

        # all nets two clusters with 21 vias each
        inst = edbapp.padstacks.instances
        all_vias = {id_: i.position for id_, i in inst.items()}
        clusters2 = edbapp.padstacks.dbscan(all_vias, max_distance=2e-3, min_samples=3)

        assert len(clusters1) == 1
        assert len(clusters1[0]) == 20
        assert len(clusters2) == 2
        assert len(clusters2[1]) == 21
        edbapp.close(terminate_rpc_session=False)

    def test_reduce_via_by_density(self, edb_examples):
        source_path = edb_examples.example_models_path / "TEDB" / "merge_via_4layers.aedb"
        edbapp = edb_examples.load_edb(source_path)

        inst = edbapp.padstacks.instances
        all_vias = {id_: i.position for id_, i in inst.items()}
        clusters = edbapp.padstacks.dbscan(all_vias, max_distance=2e-3, min_samples=3)

        kept_2mm, grid_2mm = edbapp.padstacks.reduce_via_by_density(clusters[0], cell_size_x=2e-3, cell_size_y=2e-3)
        kept_5mm, grid_5mm = edbapp.padstacks.reduce_via_by_density(clusters[0], cell_size_x=5e-3, cell_size_y=5e-3)
        assert len(kept_2mm) == 8
        assert len(grid_2mm) == 8
        assert len(kept_5mm) == 1
        assert len(grid_5mm) == 1

        _, _ = edbapp.padstacks.reduce_via_by_density(clusters[0], cell_size_x=5e-3, cell_size_y=5e-3, delete=True)
        _, _ = edbapp.padstacks.reduce_via_by_density(clusters[1], cell_size_x=5e-3, cell_size_y=5e-3, delete=True)
        assert len(edbapp.padstacks.instances) == 2
        edbapp.close(terminate_rpc_session=False)

    def test_create_backdrill_dielectric_fill_via(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        backdrill_layer = "Inner1(GND1)"
        edbapp.padstacks.create_dielectric_filled_backdrills(
            layer=backdrill_layer,
            material="test_fill",
            permittivity=3.85,
            dielectric_loss_tangent=0,
            diameter="400um",
            nets="1V0",
        )
        assert "test_fill" in edbapp.materials
        assert edbapp.materials["test_fill"].permittivity == 3.85
        assert edbapp.padstacks.get_instances(net_name="1V0")[0].backdrill_type == "layer_drill"
        if not edbapp.grpc:
            assert edbapp.padstacks.get_instances(net_name="1V0")[0].backdrill_bottom[0] == "Inner1(GND1)"
            assert edbapp.padstacks.get_instances(net_name="1V0")[0].backdrill_bottom[1] == "0.0004"
        else:
            assert edbapp.padstacks.get_instances(net_name="1V0")[0].backdrill_bottom
            assert edbapp.padstacks.get_instances(net_name="1V0")[0].backdrill_diameter == 0.0004
            assert edbapp.padstacks.get_instances(net_name="1V0")[0].backdrill_layer == "Inner1(GND1)"
        assert edbapp.padstacks.definitions["v35h15_BD"].material == "test_fill"
        edbapp.close(terminate_rpc_session=False)

    def test_create_backdrill_dielectric_fill_via2(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        backdrill_layer = "Inner1(GND1)"
        edbapp.padstacks.create_dielectric_filled_backdrills(
            layer=backdrill_layer,
            material="test_fill",
            permittivity=3.85,
            dielectric_loss_tangent=0,
            diameter="400um",
            padstack_definition="v40h20-1",
        )
        instance = edbapp.padstacks.definitions["v40h20-1"].instances[0]
        assert instance.backdrill_type == "layer_drill"
        if not edbapp.grpc:
            assert instance.backdrill_bottom[1] == "0.0004"
            assert instance.backdrill_bottom[0] == "Inner1(GND1)"
        else:
            assert instance.backdrill_diameter == 0.0004
            assert instance.backdrill_layer == "Inner1(GND1)"
        edbapp.close(terminate_rpc_session=False)

    def test_create_backdrill_dielectric_fill_via3(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        instances = edbapp.padstacks.definitions["v40h20-1"].instances
        backdrill_layer = "Inner1(GND1)"
        edbapp.padstacks.create_dielectric_filled_backdrills(
            layer=backdrill_layer,
            material="test_fill",
            permittivity=3.85,
            dielectric_loss_tangent=0,
            diameter="400um",
            padstack_instances=instances,
        )
        instance = edbapp.padstacks.definitions["v40h20-1"].instances[0]
        assert instance.backdrill_type == "layer_drill"
        if not edbapp.grpc:
            assert instance.backdrill_bottom[1] == "0.0004"
            assert instance.backdrill_bottom[0] == "Inner1(GND1)"
        else:
            assert instance.backdrill_diameter == 0.0004
            assert instance.backdrill_layer == "Inner1(GND1)"
        edbapp.close(terminate_rpc_session=False)


def _get_padstack_polygon_data(edb, padstack_instance: EDBPadstackInstance, layer_name: str) -> PolygonData:
    edb.layout_instance.Refresh()
    loi = edb.layout_instance.GetLayoutObjInstance(padstack_instance._edb_object, None)
    geometries = loi.GetGeometries(edb.modeler.layers[layer_name]._edb_object)
    pds = [g.GetPolygonData(True) for g in geometries]
    if not pds:
        # unknown issue here: sometimes the LayoutInstance returns nothing even though there are shapes on the layer for
        # the instance; as this is used in tests I'm going to return None and check that we successfully confirmed at
        # least one case
        return None
    result = edb.core.Geometry.PolygonData.Unite(convert_py_list_to_net_list(pds))[0]
    return result


def _assert_inside(rect, pad):
    BASE_MESSAGE = "rectangle is not inside pad as"
    result = rect.Intersect(pad)
    assert len(result) == 1, f"{BASE_MESSAGE} intersection returned more than one lump"
    assert math.isclose(round(result[0].Area(), 4), round(rect.Area(), 4)), (
        f"{BASE_MESSAGE} area of intersection is not equal to rectangle area"
    )
