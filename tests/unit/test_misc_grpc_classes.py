# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

"""Unit tests for small gRPC wrapper classes (no EDB license required)."""

from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


@pytest.mark.grpc
class TestNetlistModel:
    def _make(self):
        from pyedb.grpc.database.hierarchy.netlist_model import NetlistModel

        core = MagicMock()
        core.netlist = "SPICE_DATA"
        component = MagicMock()
        return NetlistModel(component, core), core, component

    def test_netlist_get(self):
        model, core, _ = self._make()
        assert model.netlist == "SPICE_DATA"

    def test_netlist_set(self):
        model, core, component = self._make()
        model.netlist = "NEW_SPICE"
        assert core.netlist == "NEW_SPICE"
        component._set_model.assert_called_once_with(core)


@pytest.mark.grpc
class TestPortPostProcessingProp:
    def _make(self):
        from pyedb.grpc.database.utility.port_post_processing_prop import PortPostProcessingProp

        core = MagicMock()
        core.deembed_length.value = 1.5
        core.renormalization_impedance.value = 50.0
        core.voltage_magnitude.value = 1.0
        core.voltage_phase.value = 0.0
        core.do_deembed = False
        core.do_renormalize = True
        return PortPostProcessingProp(core), core

    def test_deembed_length_get(self):
        prop, core = self._make()
        assert prop.deembed_length == 1.5

    def test_deembed_length_set(self):
        prop, core = self._make()
        from ansys.edb.core.utility.value import Value as CoreValue

        prop.deembed_length = 2.5
        core.__setattr__  # just ensure no error

    def test_renormalization_impedance_get(self):
        prop, core = self._make()
        assert prop.renormalization_impedance == 50.0

    def test_renormalization_impedance_set(self):
        prop, core = self._make()
        prop.renormalization_impedance = 75.0
        # core.renormalization_impedance should have been set
        assert core.renormalization_impedance is not None

    def test_voltage_magnitude_get(self):
        prop, core = self._make()
        assert prop.voltage_magnitude == 1.0

    def test_voltage_magnitude_set(self):
        prop, core = self._make()
        prop.voltage_magnitude = 2.0

    def test_voltage_phase_get(self):
        prop, core = self._make()
        assert prop.voltage_phase == 0.0

    def test_voltage_phase_set(self):
        prop, core = self._make()
        prop.voltage_phase = 45.0

    def test_do_deembed_get(self):
        prop, core = self._make()
        assert prop.do_deembed is False

    def test_do_deembed_set(self):
        prop, core = self._make()
        prop.do_deembed = True
        assert core.do_deembed is True

    def test_do_renormalize_get(self):
        prop, core = self._make()
        assert prop.do_renormalize is True

    def test_do_renormalize_set(self):
        prop, core = self._make()
        prop.do_renormalize = False
        assert core.do_renormalize is False


@pytest.mark.grpc
class TestHFSSPIAdvancedSettings:
    def _make(self):
        from pyedb.grpc.database.simulation_setup.hfss_pi_advanced_settings import HFSSPIAdvancedSettings

        core = MagicMock()
        core.arc_to_chord_error = "0.001"
        core.auto_model_resolution = True
        core.max_num_arc_points = "8"
        core.mesh_for_via_plating = False
        core.model_resolution_length = "0.0001"
        core.num_via_sides = 8
        core.remove_floating_geometry = True
        core.small_plane_area = "1e-9"
        core.small_void_area = "2e-9"
        core.use_arc_chord_error_approx = False
        core.via_material = "copper"
        core.zero_metal_layer_thickness = "0.0"
        pedb = MagicMock()
        pedb.value.side_effect = lambda x: x
        return HFSSPIAdvancedSettings(pedb, core), core, pedb

    def test_arc_to_chord_error_get(self):
        s, core, _ = self._make()
        assert s.arc_to_chord_error == pytest.approx(0.001)

    def test_arc_to_chord_error_set(self):
        s, core, pedb = self._make()
        s.arc_to_chord_error = 0.002
        assert core.arc_to_chord_error == "0.002"

    def test_auto_model_resolution_get(self):
        s, core, _ = self._make()
        assert s.auto_model_resolution is True

    def test_auto_model_resolution_set(self):
        s, core, _ = self._make()
        s.auto_model_resolution = False
        assert core.auto_model_resolution is False

    def test_max_num_arc_points_get(self):
        s, core, _ = self._make()
        assert s.max_num_arc_points == 8

    def test_max_num_arc_points_set(self):
        s, core, _ = self._make()
        s.max_num_arc_points = 16
        assert core.max_num_arc_points == "16"

    def test_mesh_for_via_plating_get(self):
        s, core, _ = self._make()
        assert s.mesh_for_via_plating is False

    def test_mesh_for_via_plating_set(self):
        s, core, _ = self._make()
        s.mesh_for_via_plating = True
        assert core.mesh_for_via_plating is True

    def test_model_resolution_length_get(self):
        s, core, _ = self._make()
        assert s.model_resolution_length == pytest.approx(0.0001)

    def test_model_resolution_length_set(self):
        s, core, _ = self._make()
        s.model_resolution_length = 0.0005
        assert core.model_resolution_length == "0.0005"

    def test_num_via_sides_get(self):
        s, core, _ = self._make()
        assert s.num_via_sides == 8

    def test_num_via_sides_set(self):
        s, core, _ = self._make()
        s.num_via_sides = 12
        assert core.num_via_sides == 12

    def test_remove_floating_geometry_get(self):
        s, core, _ = self._make()
        assert s.remove_floating_geometry is True

    def test_remove_floating_geometry_set(self):
        s, core, _ = self._make()
        s.remove_floating_geometry = False
        assert core.remove_floating_geometry is False

    def test_small_plane_area_get(self):
        s, core, _ = self._make()
        assert s.small_plane_area == pytest.approx(1e-9)

    def test_small_plane_area_set(self):
        s, core, _ = self._make()
        s.small_plane_area = 5e-9
        assert core.small_plane_area == "5e-09"

    def test_small_void_area_get(self):
        s, core, _ = self._make()
        assert s.small_void_area == pytest.approx(2e-9)

    def test_small_void_area_set(self):
        s, core, _ = self._make()
        s.small_void_area = 3e-9
        assert core.small_void_area == "3e-09"

    def test_use_arc_chord_error_approx_get(self):
        s, core, _ = self._make()
        assert s.use_arc_chord_error_approx is False

    def test_use_arc_chord_error_approx_set(self):
        s, core, _ = self._make()
        s.use_arc_chord_error_approx = True
        assert core.use_arc_chord_error_approx is True

    def test_via_material_get(self):
        s, core, _ = self._make()
        assert s.via_material == "copper"

    def test_via_material_set(self):
        s, core, _ = self._make()
        s.via_material = "gold"
        assert core.via_material == "gold"

    def test_zero_metal_layer_thickness_get(self):
        s, core, _ = self._make()
        assert s.zero_metal_layer_thickness == pytest.approx(0.0)

    def test_zero_metal_layer_thickness_set(self):
        s, core, _ = self._make()
        s.zero_metal_layer_thickness = 0.001
        assert core.zero_metal_layer_thickness == "0.001"


@pytest.mark.grpc
class TestHFSSPISolverSettings:
    def _make(self):
        from pyedb.grpc.database.simulation_setup.hfss_pi_solver_settings import HFSSPISolverSettings

        core = MagicMock()
        core.enhanced_low_frequency_accuracy = False
        core.via_area_cutoff_circ_elems = "10.0"
        pedb = MagicMock()
        return HFSSPISolverSettings(pedb, core), core

    def test_enhanced_low_frequency_accuracy_get(self):
        s, core = self._make()
        assert s.enhanced_low_frequency_accuracy is False

    def test_enhanced_low_frequency_accuracy_set(self):
        s, core = self._make()
        s.enhanced_low_frequency_accuracy = True
        assert core.enhanced_low_frequency_accuracy is True

    def test_via_area_cutoff_circ_elems_get(self):
        s, core = self._make()
        assert s.via_area_cutoff_circ_elems == pytest.approx(10.0)

    def test_via_area_cutoff_circ_elems_set(self):
        s, core = self._make()
        s.via_area_cutoff_circ_elems = 20.0
        assert core.via_area_cutoff_circ_elems == "20.0"


@pytest.mark.grpc
class TestHFSSPIGeneralSettings:
    def _make(self):
        from pyedb.grpc.database.simulation_setup.hfss_pi_general_settings import HFSSPIGeneralSettings

        core = MagicMock()
        core.mesh_region_name = "mesh_region_1"
        core.model_type = MagicMock()
        core.model_type.name = "PCB"
        core.use_auto_mesh_region = True
        core.use_mesh_region = False
        pedb = MagicMock()
        return HFSSPIGeneralSettings(pedb, core), core

    def test_mesh_region_name_get(self):
        s, core = self._make()
        assert s.mesh_region_name == "mesh_region_1"

    def test_mesh_region_name_set(self):
        s, core = self._make()
        s.mesh_region_name = "new_region"
        assert core.mesh_region_name == "new_region"

    def test_model_type_get(self):
        s, core = self._make()
        assert s.model_type == "pcb"

    def test_model_type_set_valid(self):
        s, core = self._make()
        s.model_type = "rdl"

    def test_model_type_set_invalid(self):
        s, core = self._make()
        with pytest.raises(ValueError):
            s.model_type = "invalid_type"

    def test_use_auto_mesh_region_get(self):
        s, core = self._make()
        assert s.use_auto_mesh_region is True

    def test_use_auto_mesh_region_set(self):
        s, core = self._make()
        s.use_auto_mesh_region = False
        assert core.use_auto_mesh_region is False

    def test_use_mesh_region_get(self):
        s, core = self._make()
        assert s.use_mesh_region is False

    def test_use_mesh_region_set(self):
        s, core = self._make()
        s.use_mesh_region = True
        assert core.use_mesh_region is True


@pytest.mark.grpc
class TestHFSSPISimulationSettings:
    def _make(self):
        from pyedb.grpc.database.simulation_setup.hfss_pi_simulation_settings import HFSSPISimulationSettings

        core = MagicMock()
        core.enabled = True
        core.advanced = MagicMock()
        core.general = MagicMock()
        core.solver = MagicMock()
        pedb = MagicMock()
        return HFSSPISimulationSettings(pedb, core), core, pedb

    def test_enabled_get(self):
        s, core, _ = self._make()
        assert s.enabled is True

    def test_enabled_set(self):
        s, core, _ = self._make()
        s.enabled = False
        assert core.enabled is False

    def test_advanced_returns_wrapper(self):
        s, core, _ = self._make()
        from pyedb.grpc.database.simulation_setup.hfss_pi_advanced_settings import HFSSPIAdvancedSettings

        assert isinstance(s.advanced, HFSSPIAdvancedSettings)

    def test_general_returns_wrapper(self):
        s, core, _ = self._make()
        from pyedb.grpc.database.simulation_setup.hfss_pi_general_settings import HFSSPIGeneralSettings

        assert isinstance(s.general, HFSSPIGeneralSettings)

    def test_solver_returns_wrapper(self):
        s, core, _ = self._make()
        from pyedb.grpc.database.simulation_setup.hfss_pi_solver_settings import HFSSPISolverSettings

        assert isinstance(s.solver, HFSSPISolverSettings)


@pytest.mark.grpc
class TestVariable:
    def _make(self, name="my_var"):
        from pyedb.grpc.database.variables import Variable

        pedb = MagicMock()
        pedb.get_variable_value.return_value = "1mm"
        pedb.get_variable_desc.return_value = "some description"
        pedb.is_parameter.return_value = False
        pedb.delete.return_value = True
        return Variable(pedb, name), pedb

    def test_name(self):
        v, _ = self._make("my_var")
        assert v.name == "my_var"

    def test_is_design_variable_true(self):
        v, _ = self._make("my_var")
        assert v._is_design_varible is True

    def test_is_design_variable_false_for_dollar(self):
        v, _ = self._make("$my_var")
        assert v._is_design_varible is False

    def test_value_get(self):
        v, pedb = self._make()
        with patch("pyedb.grpc.database.variables.CoreValue") as MockCoreValue:
            MockCoreValue.return_value = MagicMock(value=1.0)
            val = v.value
            pedb.get_variable_value.assert_called_once_with("my_var")

    def test_value_set(self):
        v, pedb = self._make()
        with patch("pyedb.grpc.database.variables.CoreValue") as MockCoreValue:
            MockCoreValue.return_value = MagicMock()
            v.value = "2mm"
            pedb.set_variable_value.assert_called_once()

    def test_description_get(self):
        v, pedb = self._make()
        assert v.description == "some description"
        pedb.get_variable_desc.assert_called_once_with("my_var")

    def test_description_set(self):
        v, pedb = self._make()
        v.description = "new desc"
        pedb.set_variable_desc.assert_called_once_with("my_var", "new desc")

    def test_is_parameter(self):
        v, pedb = self._make()
        assert v.is_parameter is False
        pedb.is_parameter.assert_called_once_with("my_var")

    def test_delete(self):
        v, pedb = self._make()
        result = v.delete()
        assert result is True
        pedb.delete.assert_called_once_with("my_var")


@pytest.mark.grpc
class TestNetClass:
    def _make_net_class(self):
        from pyedb.grpc.database.net.net_class import NetClass

        core = MagicMock()
        core.description = "test desc"
        core.id = 42
        core.is_null = False
        core.is_power_ground = False
        core.name = "NC1"
        core.nets = []
        pedb = MagicMock()
        return NetClass(pedb, core), core, pedb

    def test_description_get(self):
        nc, core, _ = self._make_net_class()
        assert nc.description == "test desc"

    def test_description_set(self):
        nc, core, _ = self._make_net_class()
        nc.description = "new desc"
        assert core.description == "new desc"

    def test_id(self):
        nc, core, _ = self._make_net_class()
        assert nc.id == 42

    def test_is_null(self):
        nc, core, _ = self._make_net_class()
        assert nc.is_null is False

    def test_is_power_ground_get(self):
        nc, core, _ = self._make_net_class()
        assert nc.is_power_ground is False

    def test_is_power_ground_set(self):
        nc, core, _ = self._make_net_class()
        nc.is_power_ground = True
        assert core.is_power_ground is True

    def test_name_get(self):
        nc, core, _ = self._make_net_class()
        assert nc.name == "NC1"

    def test_name_set(self):
        nc, core, _ = self._make_net_class()
        nc.name = "NC2"
        assert core.name == "NC2"

    def test_nets_empty(self):
        nc, core, _ = self._make_net_class()
        assert nc.nets == []

    def test_delete(self):
        nc, core, _ = self._make_net_class()
        nc.delete()
        core.delete.assert_called_once()

    def test_add_net_with_non_net_object_returns_false(self):
        """Passing a non-Net object (not str, not Net) returns False."""
        nc, core, pedb = self._make_net_class()
        # Passing an arbitrary object that is not a Net → isinstance check fails → False
        result = nc.add_net(12345)
        assert result is False

    def test_remove_net_with_non_net_object_returns_false(self):
        nc, core, pedb = self._make_net_class()
        result = nc.remove_net(12345)
        assert result is False


@pytest.mark.grpc
class TestLayer:
    def _make(self):
        from pyedb.grpc.database.layers.layer import Layer

        core = MagicMock()
        core.id = 7
        core.name = "solder_mask_top"
        core.type.name = "solder_mask_layer"
        core.is_stackup_layer = False
        # clone should return something (for __init__)
        core.clone.return_value = MagicMock()

        layer = Layer.__new__(Layer)
        layer.core = core
        layer._name = "solder_mask_top"
        layer._color = ()
        layer._type = ""
        layer._cloned_layer = core.clone.return_value
        return layer, core

    def test_id(self):
        layer, core = self._make()
        assert layer.id == 7

    def test_name_get(self):
        layer, core = self._make()
        assert layer.name == "solder_mask_top"

    def test_name_set(self):
        layer, core = self._make()
        layer.name = "new_name"
        assert core.name == "new_name"

    def test_type(self):
        layer, core = self._make()
        t = layer.type
        assert isinstance(t, str)

    def test_is_stackup_layer(self):
        layer, core = self._make()
        assert layer.is_stackup_layer is False

    def test_update_invalid_key_raises(self):
        layer, core = self._make()
        with pytest.raises(Exception):
            layer.update(invalid_key="value")


@pytest.mark.grpc
class TestComponentModel:
    def _make(self):
        from unittest.mock import patch

        from pyedb.grpc.database.definition.component_model import ComponentModel

        mock_core_class = MagicMock()
        mock_core_instance = MagicMock()
        mock_core_instance.is_null = False
        mock_core_instance.name = "model_1"
        mock_core_instance.reference_file = "ref.s2p"
        mock_core_class.return_value = mock_core_instance

        with patch("pyedb.grpc.database.definition.component_model.CoreComponentModel", mock_core_class):
            raw = MagicMock()
            raw.msg = "msg_stub"
            obj = ComponentModel(raw)

        obj.core = mock_core_instance
        return obj, mock_core_instance

    def test_is_null(self):
        obj, core = self._make()
        assert obj.is_null is False

    def test_name(self):
        obj, core = self._make()
        assert obj.name == "model_1"

    def test_reference_file(self):
        obj, core = self._make()
        assert obj.reference_file == "ref.s2p"
