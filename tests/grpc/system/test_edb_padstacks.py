"""Tests related to Edb padstacks
"""
import os
import pytest

from pyedb.legacy.edb import EdbLegacy
from tests.conftest import local_path
from tests.conftest import desktop_version
from tests.legacy.system.conftest import target_path3
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path3, target_path4):
        self.edbapp = edbapp
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path3 = target_path3
        self.target_path4 = target_path4

    def test_get_pad_parameters(self):
        """Access to pad parameters."""
        pin = self.edbapp.components.get_pin_from_component("J1", pinName="1")
        parameters = self.edbapp.padstacks.get_pad_parameters(
            pin[0], "1_Top", self.edbapp.padstacks.pad_type.RegularPad
        )
        assert isinstance(parameters[1], list)
        assert isinstance(parameters[0], int)

    def test_get_vias_from_nets(self):
        """Use padstacks' get_via_instance_from_net method."""
        assert self.edbapp.padstacks.get_via_instance_from_net("GND")
        assert not self.edbapp.padstacks.get_via_instance_from_net(["GND2"])

    def test_create_with_packstack_name(self):
        """Create a padstack"""
        # Create myVia
        self.edbapp.padstacks.create(padstackname="myVia")
        assert "myVia" in list(self.edbapp.padstacks.definitions.keys())
        self.edbapp.padstacks.definitions["myVia"].hole_range = "begin_on_upper_pad"
        assert self.edbapp.padstacks.definitions["myVia"].hole_range == "begin_on_upper_pad"
        self.edbapp.padstacks.definitions["myVia"].hole_range = "through"
        assert self.edbapp.padstacks.definitions["myVia"].hole_range == "through"
        # Create myVia_vullet
        self.edbapp.padstacks.create(padstackname="myVia_bullet", antipad_shape="Bullet")
        assert "myVia_bullet" in list(self.edbapp.padstacks.definitions.keys())
    
        self.edbapp.add_design_variable("via_x", 5e-3)
        self.edbapp["via_y"] = "1mm"
        assert self.edbapp["via_y"].value == 1e-3
        assert self.edbapp["via_y"].value_string == "1mm"
        assert self.edbapp.padstacks.place(["via_x", "via_x+via_y"], "myVia", via_name="via_test1")
        assert self.edbapp.padstacks.place(["via_x", "via_x+via_y*2"], "myVia_bullet")
        self.edbapp.padstacks["via_test1"].net_name = "GND"
        assert self.edbapp.padstacks["via_test1"].net_name == "GND"
        padstack = self.edbapp.padstacks.place(["via_x", "via_x+via_y*3"], "myVia", is_pin=True)
        for test_prop in (self.edbapp.padstacks.padstack_instances, self.edbapp.padstacks.instances):
            padstack_instance = test_prop[padstack.id]
            assert padstack_instance.is_pin
            assert padstack_instance.position
            assert padstack_instance.start_layer in padstack_instance.layer_range_names
            assert padstack_instance.stop_layer in padstack_instance.layer_range_names
            padstack_instance.position = [0.001, 0.002]
            assert padstack_instance.position == [0.001, 0.002]
            assert padstack_instance.parametrize_position()
            assert isinstance(padstack_instance.rotation, float)
            self.edbapp.padstacks.create_circular_padstack(padstackname="mycircularvia")
            assert "mycircularvia" in list(self.edbapp.padstacks.definitions.keys())
            assert not padstack_instance.backdrill_top
            assert not padstack_instance.backdrill_bottom
            assert padstack_instance.delete()
            via = self.edbapp.padstacks.place([0, 0], "myVia")
            assert via.set_backdrill_top("Inner4(Sig2)", 0.5e-3)
            assert via.backdrill_top
            assert via.set_backdrill_bottom("16_Bottom", 0.5e-3)
            assert via.backdrill_bottom

    def test_padstacks_get_nets_from_pin_list(self):
        """Retrieve pin list from component and net."""
        cmp_pinlist = self.edbapp.padstacks.get_pinlist_from_component_and_net("U1", "GND")
        assert cmp_pinlist[0].GetNet().GetName()

    def test_padstack_properties_getter(self):
        """Evaluate properties"""
        for el in self.edbapp.padstacks.definitions:
            padstack = self.edbapp.padstacks.definitions[el]
            assert padstack.hole_plating_thickness is not None or False
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
            assert padstack.hole_type is not None or False
            pad = padstack.pad_by_layer[padstack.via_stop_layer]
            if not pad.shape == "NoGeometry":
                assert pad.parameters is not None or False
                assert pad.parameters_values is not None or False
                assert pad.offset_x is not None or False
                assert pad.offset_y is not None or False
                assert isinstance(pad.geometry_type, int)
            polygon = pad.polygon_data
            if polygon:
                assert polygon.GetBBox()

    def test_padstack_properties_setter(self):
        """Set padstack properties"""
        pad = self.edbapp.padstacks.definitions["c180h127"]
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
        assert abs(pad.hole_properties[0] - hole_pad) < tol
        offset_x = 7
        offset_y = 1
        pad.pad_by_layer[pad.via_stop_layer].shape = "Circle"
        pad.pad_by_layer[pad.via_stop_layer].parameters = 7
        pad.pad_by_layer[pad.via_stop_layer].offset_x = offset_x
        pad.pad_by_layer[pad.via_stop_layer].offset_y = offset_y
        assert pad.pad_by_layer[pad.via_stop_layer].parameters["Diameter"].tofloat == 7
        assert pad.pad_by_layer[pad.via_stop_layer].offset_x == str(offset_x)
        assert pad.pad_by_layer[pad.via_stop_layer].offset_y == str(offset_y)
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"Diameter": 8}
        assert pad.pad_by_layer[pad.via_stop_layer].parameters["Diameter"].tofloat == 8
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"Diameter": 1}
        pad.pad_by_layer[pad.via_stop_layer].shape = "Square"
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"Size": 1}
        pad.pad_by_layer[pad.via_stop_layer].shape = "Rectangle"
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1}
        pad.pad_by_layer[pad.via_stop_layer].shape = "Oval"
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
        pad.pad_by_layer[pad.via_stop_layer].parameters = {"XSize": 1, "YSize": 1, "CornerRadius": 1}
        pad.pad_by_layer[pad.via_stop_layer].parameters = [1, 1, 1]

    def test_padstack_get_instance_by_name(self):
        """Access padstack instance by name."""
        padstack_instances = self.edbapp.padstacks.get_padstack_instance_by_net_name("GND")
        assert len(padstack_instances)
        padstack_1 = padstack_instances[0]
        assert padstack_1.id
        assert isinstance(padstack_1.bounding_box, list)
        for v in padstack_instances:
            if not v.is_pin:
                v.name = "TestInst"
                assert v.name == "TestInst"
                break

    def test_padstack_duplicate_padstack(self):
        """Duplicate a padstack."""
        self.edbapp.padstacks.duplicate(
            target_padstack_name="c180h127",
            new_padstack_name="c180h127_NEW",
        )
        assert self.edbapp.padstacks.definitions["c180h127_NEW"]

    def test_padstack_set_pad_property(self):
        """Set pad and antipad properties of the padstack."""
        self.edbapp.padstacks.set_pad_property(
            padstack_name="c180h127",
            layer_name="new",
            pad_shape="Circle",
            pad_params="800um",
        )
        assert self.edbapp.padstacks.definitions["c180h127"].pad_by_layer["new"]

    def test_microvias(self):
        """Convert padstack to microvias 3D objects."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_128_microvias.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = EdbLegacy(target_path, edbversion=desktop_version)
        assert edbapp.padstacks.definitions["Padstack_Circle"].convert_to_3d_microvias(False)
        assert edbapp.padstacks.definitions["Padstack_Rectangle"].convert_to_3d_microvias(False, hole_wall_angle=10)
        assert edbapp.padstacks.definitions["Padstack_Polygon_p12"].convert_to_3d_microvias(False)
        edbapp.close()

    def test_split_microvias(self):
        """Convert padstack definition to multiple microvias definitions."""
        edbapp = EdbLegacy(self.target_path4, edbversion=desktop_version)
        assert len(edbapp.padstacks.definitions["C4_POWER_1"].split_to_microvias()) > 0
        edbapp.close()

    def test_padstack_plating_ratio_fixing(self):
        """Fix hole plating ratio."""        
        assert self.edbapp.padstacks.check_and_fix_via_plating()

    def test_padstack_search_reference_pins(self):
        """Search for reference pins using given criteria."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_boundaries.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = EdbLegacy(target_path, edbversion=desktop_version)
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

    def test_vias_metal_volume(self):
        """Metal volume of the via hole instance."""
        vias = [
            via
            for via in list(self.edbapp.padstacks.padstack_instances.values())
            if not via.start_layer == via.stop_layer
        ]
        assert vias[0].metal_volume
        assert vias[1].metal_volume

    def test_padstacks_create_rectangle_in_pad(self):
        """Create a rectangle inscribed inside a padstack instance pad."""
        example_model = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
        self.local_scratch.copyfolder(
            example_model,
            os.path.join(self.local_scratch.path, "padstacks2.aedb"),
        )
        edb = EdbLegacy(
            edbpath=os.path.join(self.local_scratch.path, "padstacks2.aedb"),
            edbversion=desktop_version,
            isreadonly=True,
        )
        for test_prop in (edb.padstacks.instances, edb.padstacks.padstack_instances):
            padstack_instances = list(test_prop.values())
            for padstack_instance in padstack_instances:
                result = padstack_instance.create_rectangle_in_pad("s", partition_max_order=8)
                if padstack_instance.padstack_definition != "Padstack_None":
                    assert result
                else:
                    assert not result
        edb.close()

    def test_padstaks_plot_on_matplotlib(self):
        """Plot a Net to Matplotlib 2D Chart."""
        edb_plot = EdbLegacy(self.target_path3, edbversion=desktop_version)

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
            nets="V3P3_S5",
            layers=None,
            save_plot=local_png2,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
        )
        assert os.path.exists(local_png2)

        local_png3 = os.path.join(self.local_scratch.path, "test3.png")
        edb_plot.nets.plot(
            nets=["LVL_I2C_SCL", "V3P3_S5", "GATE_V5_USB"],
            layers="TOP",
            color_by_net=True,
            save_plot=local_png3,
            plot_components_on_top=True,
            plot_components_on_bottom=True,
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
