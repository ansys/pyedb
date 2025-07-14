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

"""Tests related to Edb padstacks
"""
import os

import pytest

from pyedb.grpc.edb import Edb as Edb
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.grpc]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path3, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path3 = target_path3
        self.target_path4 = target_path4

    def test_get_pad_parameters(self, edb_examples):
        """Access to pad parameters."""
        # Done
        edbapp = edb_examples.get_si_verse()
        pin = edbapp.components.get_pin_from_component("J1", pin_name="1")
        parameters = edbapp.padstacks.get_pad_parameters(pin=pin[0], layername="1_Top", pad_type="regular_pad")
        assert isinstance(parameters[1], list)
        assert isinstance(parameters[0], str)
        edbapp.close()

    def test_get_vias_from_nets(self, edb_examples):
        """Use padstacks' get_via_instance_from_net method."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.padstacks.get_via_instance_from_net("GND")
        assert not edbapp.padstacks.get_via_instance_from_net(["GND2"])
        edbapp.close()

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
        assert edbapp.padstacks.place(["via_x", "via_x+via_y"], "myVia", via_name="via_test1")
        assert edbapp.padstacks.place(["via_x", "via_x+via_y*2"], "myVia_bullet")
        edbapp.padstacks["via_test1"].net_name = "GND"
        assert edbapp.padstacks["via_test1"].net_name == "GND"
        padstack = edbapp.padstacks.place(["via_x", "via_x+via_y*3"], "myVia", is_pin=True)
        padstack_instance = edbapp.padstacks.instances[padstack.edb_uid]
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
        padstack_instance.delete()
        via = edbapp.padstacks.place([0, 0], "myVia")
        via.set_back_drill_by_layer(drill_to_layer="Inner4(Sig2)", diameter=0.5e-3, offset=0.0, from_bottom=True)
        assert via.get_back_drill_by_layer()[0] == "Inner4(Sig2)"
        assert via.get_back_drill_by_layer()[1] == 0.0
        assert via.get_back_drill_by_layer()[2] == 5e-4
        assert via.backdrill_bottom

        # via = edbapp.padstacks.instances_by_name["Via1266"]
        # via.backdrill_parameters = {
        #     "from_bottom": {"drill_to_layer": "Inner5(PWR2)", "diameter": "0.4mm", "stub_length": "0.1mm"},
        #     "from_top": {"drill_to_layer": "Inner2(PWR1)", "diameter": "0.41mm", "stub_length": "0.11mm"},
        # }
        # assert via.backdrill_parameters == {
        #     "from_bottom": {"drill_to_layer": "Inner5(PWR2)", "diameter": "0.4mm", "stub_length": "0.1mm"},
        #     "from_top": {"drill_to_layer": "Inner2(PWR1)", "diameter": "0.41mm", "stub_length": "0.11mm"},
        # }
        edbapp.close()

    def test_padstacks_get_nets_from_pin_list(self, edb_examples):
        """Retrieve pin list from component and net."""
        # Done
        edbapp = edb_examples.get_si_verse()
        cmp_pinlist = edbapp.padstacks.get_pinlist_from_component_and_net("U1", "GND")
        assert cmp_pinlist[0].net.name
        edbapp.close()

    def test_padstack_properties_getter(self, edb_examples):
        """Evaluate properties"""
        # Done
        edbapp = edb_examples.get_si_verse()
        for name in list(edbapp.padstacks.definitions.keys()):
            padstack = edbapp.padstacks.definitions[name]
            assert padstack.hole_plating_thickness is not None or False
            assert padstack.hole_plating_ratio is not None or False
            assert padstack.start_layer is not None or False
            assert padstack.stop_layer is not None or False
            assert padstack.material is not None or False
            assert padstack.hole_finished_size is not None or False
            assert padstack.hole_rotation is not None or False
            assert padstack.hole_offset_x is not None or False
            assert padstack.hole_offset_y is not None or False
            pad = padstack.pad_by_layer[padstack.stop_layer]
            if not pad.shape == "NoGeometry":
                assert pad.parameters_values is not None or False
                assert pad.offset_x is not None or False
                assert pad.offset_y is not None or False
                assert isinstance(pad.geometry_type, int)
            polygon = pad.polygon_data
            if polygon:
                assert polygon.bbox()
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
        offset_x = 7
        offset_y = 1
        # pad.pad_by_layer[pad.stop_layer].shape = "circle"
        pad.pad_by_layer[pad.stop_layer].offset_x = offset_x
        pad.pad_by_layer[pad.stop_layer].offset_y = offset_y
        assert pad.pad_by_layer[pad.stop_layer].offset_x == 7
        assert pad.pad_by_layer[pad.stop_layer].offset_y == 1
        # pad.pad_by_layer[pad.stop_layer].parameters = {"Diameter": 8}
        # assert pad.pad_by_layer[pad.stop_layer].parameters["Diameter"].tofloat == 8
        # pad.pad_by_layer[pad.stop_layer].parameters = {"Diameter": 1}
        # pad.pad_by_layer[pad.stop_layer].shape = "Square"
        # pad.pad_by_layer[pad.stop_layer].parameters = {"Size": 1}
        # pad.pad_by_layer[pad.stop_layer].shape = "Rectangle"
        # pad.pad_by_layer[pad.stop_layer].parameters = {"XSize": 1, "YSize": 1}
        # pad.pad_by_layer[pad.stop_layer].shape = "Oval"
        # pad.pad_by_layer[pad.stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
        # pad.pad_by_layer[pad.stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
        # pad.pad_by_layer[pad.stop_layer].parameters = [1, 1, 1]
        edbapp.close()

    def test_padstack_get_instance(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.padstacks.get_instances(name="Via1961")
        assert edbapp.padstacks.get_instances(definition_name="v35h15")
        assert edbapp.padstacks.get_instances(net_name="1V0")
        assert edbapp.padstacks.get_instances(component_reference_designator="U7")
        """Access padstack instance by name."""
        padstack_instances = edbapp.padstacks.get_instances(net_name="GND")
        assert len(padstack_instances)
        padstack_1 = padstack_instances[0]
        assert padstack_1.id
        assert isinstance(padstack_1.bounding_box, list)
        for v in padstack_instances:
            if not v.is_pin:
                v.name = "TestInst"
                assert v.name == "TestInst"
                break
        edbapp.close()

    def test_padstack_duplicate_padstack(self, edb_examples):
        """Duplicate a padstack."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.padstacks.duplicate(
            target_padstack_name="c180h127",
            new_padstack_name="c180h127_NEW",
        )
        assert edbapp.padstacks.definitions["c180h127_NEW"]
        edbapp.close()

    def test_padstack_set_pad_property(self, edb_examples):
        """Set pad and antipad properties of the padstack."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.padstacks.set_pad_property(
            padstack_name="c180h127",
            layer_name="new",
            pad_shape="Circle",
            pad_params="800um",
        )
        assert edbapp.padstacks.definitions["c180h127"].pad_by_layer["new"]
        edbapp.close()

    def test_microvias(self):
        """Convert padstack to microvias 3D objects."""
        # TODO later
        # source_path = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
        # target_path = os.path.join(self.local_scratch.path, "test_128_microvias.aedb")
        # self.local_scratch.copyfolder(source_path, target_path)
        # edbapp = Edb(target_path, edbversion=desktop_version, restart_rpc_server=True, kill_all_instances=True)
        # assert edbapp.padstacks.definitions["Padstack_Circle"].convert_to_3d_microvias(False)
        # assert edbapp.padstacks.definitions["Padstack_Rectangle"].convert_to_3d_microvias(False, hole_wall_angle=10)
        # assert edbapp.padstacks.definitions["Padstack_Polygon_p12"].convert_to_3d_microvias(False)
        # assert edbapp.padstacks.definitions["MyVia"].convert_to_3d_microvias(
        #     convert_only_signal_vias=False, delete_padstack_def=False
        # )
        # assert edbapp.padstacks.definitions["MyVia_square"].convert_to_3d_microvias(
        #     convert_only_signal_vias=False, delete_padstack_def=False
        # )
        # assert edbapp.padstacks.definitions["MyVia_rectangle"].convert_to_3d_microvias(
        #     convert_only_signal_vias=False, delete_padstack_def=False
        # )
        # assert not edbapp.padstacks.definitions["MyVia_poly"].convert_to_3d_microvias(
        #     convert_only_signal_vias=False, delete_padstack_def=False
        # )
        # edbapp.close()
        pass

    def test_split_microvias(self):
        """Convert padstack definition to multiple microvias definitions."""
        edbapp = Edb(self.target_path4, edbversion=desktop_version)
        assert len(edbapp.padstacks.definitions["C4_POWER_1"].split_to_microvias()) > 0
        edbapp.close()

    def test_padstack_plating_ratio_fixing(self, edb_examples):
        """Fix hole plating ratio."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.padstacks.check_and_fix_via_plating()
        edbapp.close()

    def test_padstack_search_reference_pins(self, edb_examples):
        """Search for reference pins using given criteria."""
        # Done
        edbapp = edb_examples.get_si_verse()
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
        edbapp.close()

    def test_vias_metal_volume(self, edb_examples):
        """Metal volume of via hole instance."""
        # Done
        edbapp = edb_examples.get_si_verse()
        vias = [via for via in list(edbapp.padstacks.instances.values()) if not via.start_layer == via.stop_layer]
        assert vias[0].metal_volume
        assert vias[1].metal_volume
        edbapp.close()

    def test_padstacks_create_rectangle_in_pad(self):
        """Create a rectangle inscribed inside a padstack instance pad."""
        example_model = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
        self.local_scratch.copyfolder(
            example_model,
            os.path.join(self.local_scratch.path, "padstacks2.aedb"),
        )
        edb = Edb(
            edbpath=os.path.join(self.local_scratch.path, "padstacks2.aedb"),
            edbversion=desktop_version,
            restart_rpc_server=True,
        )
        for test_prop in (edb.padstacks.instances, edb.padstacks.instances):
            padstack_instances = list(test_prop.values())
            for padstack_instance in padstack_instances:
                result = padstack_instance.create_rectangle_in_pad("s", partition_max_order=8)
                if result:
                    if padstack_instance.padstack_definition != "Padstack_None":
                        assert result.points()
                    else:
                        assert not result.points()
        edb.close()

    def test_padstaks_plot_on_matplotlib(self):
        """Plot a Net to Matplotlib 2D Chart."""
        # Done
        edb_plot = Edb(self.target_path3, edbversion=desktop_version, restart_rpc_server=True)

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
        assert edb_plot.modeler.primitives[0].plot(show=False)
        local_png2 = os.path.join(self.local_scratch.path, "test2.png")
        edb_plot.nets.plot(
            nets="DDR4_DQS7_N",
            layers=None,
            save_plot=local_png2,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
        )
        assert os.path.exists(local_png2)

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
        edb_plot.close()

    def test_update_padstacks_after_layer_name_changed(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        signal_layer_list = list(edbapp.stackup.signal_layers.values())
        old_layers = []
        for n_layer, layer in enumerate(signal_layer_list):
            new_name = f"new_signal_name_{n_layer}"
            old_layers.append(layer.name)
            layer.name = new_name
        for layer_name in list(edbapp.stackup.layers.keys()):
            print(f"New layer name is {layer_name}")
        for padstack_inst in list(edbapp.padstacks.instances.values())[:100]:
            padsatck_layers = padstack_inst.layer_range_names
            assert padsatck_layers not in old_layers
        edbapp.close_edb()

    def test_hole(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.padstacks.definitions["v35h15"].hole_diameter = "0.16mm"
        assert edbapp.padstacks.definitions["v35h15"].hole_diameter == 0.00016
        edbapp.close()

    def test_padstack_instances_rtree_index(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        index = edbapp.padstacks.get_padstack_instances_rtree_index()
        assert index.bounds == [-0.013785, -0.00225, 0.148, 0.078]
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
        edbapp.close()

    def test_polygon_based_padstack(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
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
        edbapp.close()

    def test_via_fence(self):
        # TODO check bug #466 status polygon based via
        # source_path = os.path.join(local_path, "example_models", test_subfolder, "via_fence_generic_project.aedb")
        # target_path1 = os.path.join(self.local_scratch.path, "test_pvia_fence", "via_fence1.aedb")
        # target_path2 = os.path.join(self.local_scratch.path, "test_pvia_fence", "via_fence2.aedb")
        # self.local_scratch.copyfolder(source_path, target_path1)
        # self.local_scratch.copyfolder(source_path, target_path2)
        # edbapp = Edb(target_path1, edbversion=desktop_version, restart_rpc_server=True)
        # assert edbapp.padstacks.merge_via_along_lines(net_name="GND", distance_threshold=2e-3, minimum_via_number=6)
        # assert not edbapp.padstacks.merge_via_along_lines(
        #     net_name="test_dummy", distance_threshold=2e-3, minimum_via_number=6
        # )
        # assert "main_via" in edbapp.padstacks.definitions
        # assert "via_central" in edbapp.padstacks.definitions
        # edbapp.close(terminate_rpc_session=False)
        # edbapp = Edb(target_path2, edbversion=desktop_version)
        # assert edbapp.padstacks.merge_via_along_lines(
        #     net_name="GND", distance_threshold=2e-3, minimum_via_number=6, selected_angles=[0, 180]
        # )
        # assert "main_via" in edbapp.padstacks.definitions
        # assert "via_central" in edbapp.padstacks.definitions
        # edbapp.close()
        pass

    # def test_pad_parameter(self, edb_examples):
    #     edbapp = edb_examples.get_si_verse()
    #     o_pad_params = edbapp.padstacks.definitions["v35h15"].pad_by_layer
    #     assert o_pad_params["1_Top"][0].name == "PADGEOMTYPE_CIRCLE"
    #
    #     i_pad_params = {}
    #     i_pad_params["regular_pad"] = [
    #         {"layer_name": "1_Top", "shape": "circle", "offset_x": "0.1mm", "rotation": "0", "diameter": "0.5mm"}
    #     ]
    #     i_pad_params["anti_pad"] = [{"layer_name": "1_Top", "shape": "circle", "diameter": "1mm"}]
    #     i_pad_params["thermal_pad"] = [
    #         {
    #             "layer_name": "1_Top",
    #             "shape": "round90",
    #             "inner": "1mm",
    #             "channel_width": "0.2mm",
    #             "isolation_gap": "0.3mm",
    #         }
    #     ]
    #     edbapp.padstacks.definitions["v35h15"].pad_parameters = i_pad_params
    #     o2_pad_params = edbapp.padstacks.definitions["v35h15"].pad_parameters
    #     assert o2_pad_params["regular_pad"][0]["diameter"] == "0.5mm"
    #     assert o2_pad_params["regular_pad"][0]["offset_x"] == "0.1mm"
    #     assert o2_pad_params["anti_pad"][0]["diameter"] == "1mm"
    #     assert o2_pad_params["thermal_pad"][0]["inner"] == "1mm"
    #     assert o2_pad_params["thermal_pad"][0]["channel_width"] == "0.2mm"
    #
    # def test_pad_parameter2(self, edb_examples):
    #     edbapp = edb_examples.get_si_verse()
    #     o_hole_params = edbapp.padstacks.definitions["v35h15"].hole_parameters
    #     assert o_hole_params["shape"] == "circle"
    #     edbapp.padstacks.definitions["v35h15"].hole_parameters = {"shape": "circle", "diameter": "0.2mm"}
    #     assert edbapp.padstacks.definitions["v35h15"].hole_parameters["diameter"] == "0.2mm"

    def test_via_merge(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        polygon = [[[118e-3, 60e-3], [125e-3, 60e-3], [124e-3, 56e-3], [118e-3, 56e-3]]]
        result = edbapp.padstacks.merge_via(contour_boxes=polygon, start_layer="1_Top", stop_layer="16_Bottom")
        assert len(result) == 1
        edbapp.close()

    def test_reduce_via_in_bounding_box(self):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "vias_300.aedb")
        edbapp = Edb(edbpath=source_path, edbversion=desktop_version)
        assert len(edbapp.padstacks.instances) == 301
        # empty bounding box
        assert edbapp.padstacks.reduce_via_in_bounding_box([-16e-3, -7e-3, -13e-3, -6e-3], 10, 10) is False
        # over sampling
        assert edbapp.padstacks.reduce_via_in_bounding_box([-20e-3, -10e-3, 20e-3, 10e-3], 20, 20) is False
        assert edbapp.padstacks.reduce_via_in_bounding_box([-20e-3, -10e-3, 20e-3, 10e-3], 10, 10) is True
        assert len(edbapp.padstacks.instances) == 96
        edbapp.close_edb()

    def test_via_merge3(self):
        source_path = os.path.join(local_path, "example_models", "TEDB", "merge_via_4layers.aedb")
        edbapp = Edb(edbpath=source_path, edbversion=desktop_version)

        merged_via = edbapp.padstacks.merge_via(
            contour_boxes=[[[11e-3, -5e-3], [17e-3, -5e-3], [17e-3, 1e-3], [11e-3, 1e-3], [11e-3, -5e-3]]],
            net_filter=["NET_3"],
            start_layer="layer1",
            stop_layer="layer2",
        )

        assert edbapp.padstacks.instances[merged_via[0]].net_name == "NET_1"
        assert edbapp.padstacks.instances[merged_via[0]].start_layer == "layer1"
        assert edbapp.padstacks.instances[merged_via[0]].stop_layer == "layer2"
        edbapp.close()


def test_dbscan():
    source_path = os.path.join(local_path, "example_models", "TEDB", "merge_via_4layers.aedb")
    edbapp = Edb(edbpath=source_path, edbversion=desktop_version)

    # "NET_1" one cluster with 20 vias
    net_vias = [_x.edb_uid for _x in edbapp.padstacks.get_via_instance_from_net("NET_1")]
    all_vias = {via_id: edbapp.padstacks.instances[via_id].position for via_id in net_vias}
    clusters1 = edbapp.padstacks.dbscan(all_vias, eps=2e-3, min_samples=3)

    # all nets two clusters with 21 vias each
    net_vias = [_x.edb_uid for _x in edbapp.padstacks.get_via_instance_from_net()]
    all_vias = {via_id: edbapp.padstacks.instances[via_id].position for via_id in net_vias}
    clusters2 = edbapp.padstacks.dbscan(all_vias, eps=2e-3, min_samples=3)

    assert len(clusters1) == 1
    assert len(clusters1[0]) == 20
    assert len(clusters2) == 2
    assert len(clusters2[1]) == 21
