# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Tests related to Edb component definitions"""

import os

import pytest

from pyedb.grpc.database.definition.wirebond_def import ApdBondwireDef, Jedec4BondwireDef, Jedec5BondwireDef
from tests.conftest import config, local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_definitions(self):
        edbapp = self.edb_examples.get_si_verse()
        assert isinstance(edbapp.definitions.components, dict)
        assert isinstance(edbapp.definitions.packages, dict)
        edbapp.close(terminate_rpc_session=False)

    def test_component_s_parameter(self):
        edbapp = self.edb_examples.get_si_verse()
        sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
        edbapp.definitions.components["CAPC3216X180X55ML20T25"].add_n_port_model(
            sparam_path, "GRM32_DC0V_25degC_series"
        )
        assert edbapp.definitions.components["CAPC3216X180X55ML20T25"].component_models
        cap_model = list(edbapp.definitions.components["CAPC3216X180X55ML20T25"].component_models.values())[0]
        assert not cap_model.is_null
        assert cap_model.reference_file
        assert edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")
        edbapp.close(terminate_rpc_session=False)

    def test_add_package_def(self):
        # Done
        edbapp = self.edb_examples.get_si_verse()
        package = edbapp.definitions.add_package("package_1", "SMTC-MECT-110-01-M-D-RA1_V")
        assert package
        package.maximum_power = 1
        assert edbapp.definitions.packages["package_1"].maximum_power == 1
        package.thermal_conductivity = 1
        assert edbapp.definitions.packages["package_1"].thermal_conductivity == 1
        package.theta_jb = 1
        assert edbapp.definitions.packages["package_1"].theta_jb == 1
        package.theta_jc = 1
        assert edbapp.definitions.packages["package_1"].theta_jc == 1
        package.height = 1
        assert edbapp.definitions.packages["package_1"].height == 1
        assert package.set_heatsink("1mm", "2mm", "x_oriented", "3mm", "4mm")
        assert package.heat_sink.fin_base_height == 0.001
        assert package.heat_sink.fin_height == 0.002
        assert package.heat_sink.fin_orientation == "x_oriented"
        assert package.heat_sink.fin_spacing == 0.003
        assert package.heat_sink.fin_thickness == 0.004
        package.name = "package_1b"
        assert edbapp.definitions.packages["package_1b"]

        assert edbapp.definitions.add_package("package_2", boundary_points=[["-1mm", "-1mm"], ["1mm", "1mm"]])
        edbapp.components["J5"].package_def = "package_2"
        assert edbapp.components["J5"].package_def.name == "package_2"
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_wirebond_definitions(self):
        edbapp = self.edb_examples.get_wirebond_jedec4_project()
        assert list(edbapp.definitions.jedec4_bondwires.keys())[0] == "Default"
        assert list(edbapp.definitions.jedec5_bondwires.keys())[0] == "Default"
        jedec4_bw = list(edbapp.definitions.jedec4_bondwires.values())[0]
        jedec4_bw.height = 20e-6
        assert jedec4_bw.height == 20e-6
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_jedec5_set_parameters(self):
        """Regression: Jedec5BondwireDef.set_parameters must accept height + two angles."""
        edbapp = self.edb_examples.get_wirebond_jedec4_project()
        jedec5_bw = list(edbapp.definitions.jedec5_bondwires.values())[0]

        # set_parameters must accept three arguments without raising TypeError
        jedec5_bw.set_parameters(100e-6, 90.0, 45.0)
        height, die_pad_angle, lead_pad_angle = jedec5_bw.get_parameters()
        assert height == 100e-6
        assert die_pad_angle == 90.0
        assert lead_pad_angle == 45.0
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_jedec5_height_property_preserves_angles(self):
        """Regression: setting height via property must not reset die/lead pad angles."""
        edbapp = self.edb_examples.get_wirebond_jedec4_project()
        jedec5_bw = list(edbapp.definitions.jedec5_bondwires.values())[0]

        # Establish a known state first
        jedec5_bw.set_parameters(50e-6, 80.0, 40.0)
        # Now change only the height through the property
        jedec5_bw.height = 120e-6
        height, die_pad_angle, lead_pad_angle = jedec5_bw.get_parameters()
        assert height == 120e-6
        assert die_pad_angle == 80.0  # must be preserved
        assert lead_pad_angle == 40.0  # must be preserved
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_create_and_find_jedec4_bondwire_def(self):
        """Create a Jedec4 bondwire definition, set its height, and find it by name."""
        edbapp = self.edb_examples.create_empty_edb()
        name = "J4_system_test"

        j4 = Jedec4BondwireDef.create(edbapp, name)
        assert j4 is not None
        assert j4.name == name

        j4.set_parameters(75e-6)
        assert j4.height == 75e-6

        found = Jedec4BondwireDef.find_by_name(edbapp, name)
        assert found is not None
        assert found.name == name
        assert found.height == 75e-6

        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_create_and_find_jedec5_bondwire_def(self):
        """Create a Jedec5 bondwire definition, set all three parameters, and find it by name."""
        edbapp = self.edb_examples.create_empty_edb()
        name = "J5_system_test"

        j5 = Jedec5BondwireDef.create(edbapp, name)
        assert j5 is not None
        assert j5.name == name

        j5.set_parameters(100e-6, 90.0, 45.0)
        height, die_pad_angle, lead_pad_angle = j5.get_parameters()
        assert height == 100e-6
        assert die_pad_angle == 90.0
        assert lead_pad_angle == 45.0

        found = Jedec5BondwireDef.find_by_name(edbapp, name)
        assert found is not None
        assert found.name == name

        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_create_and_find_apd_bondwire_def(self):
        """Create an APD bondwire definition, read its parameter block, and find it by name."""
        edbapp = self.edb_examples.create_empty_edb()
        name = "APD_system_test"

        apd = ApdBondwireDef.create(edbapp, name)
        assert apd is not None
        assert apd.name == name

        # get_parameters returns the bwd descriptor block (non-empty string)
        params = apd.get_parameters()
        assert isinstance(params, str)
        assert len(params) > 0

        # parameter_block property exposes the same value
        assert apd.parameter_block == params

        # set_parameters round-trips the same block back
        apd.set_parameters(params)
        assert apd.get_parameters() == params

        # Verify height raises AttributeError for APD definitions
        with pytest.raises(AttributeError):
            _ = apd.height

        found = ApdBondwireDef.find_by_name(edbapp, name)
        assert found is not None
        assert found.name == name

        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_jedec4_find_by_name_returns_none_for_missing(self):
        """find_by_name must return None when definition does not exist."""
        edbapp = self.edb_examples.create_empty_edb()
        result = Jedec4BondwireDef.find_by_name(edbapp, "does_not_exist")
        assert result is None
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_jedec5_find_by_name_returns_none_for_missing(self):
        """find_by_name must return None when definition does not exist."""
        edbapp = self.edb_examples.create_empty_edb()
        result = Jedec5BondwireDef.find_by_name(edbapp, "does_not_exist")
        assert result is None
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_apd_find_by_name_returns_none_for_missing(self):
        """find_by_name must return None when definition does not exist."""
        edbapp = self.edb_examples.create_empty_edb()
        result = ApdBondwireDef.find_by_name(edbapp, "does_not_exist")
        assert result is None
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Regression test for gRPC Value owner requirement.")
    def test_parametric_padstack_definitions_created(self):
        """set_pad_parameters must accept project-variable strings as pad/hole sizes.

        Regression: raw parameter strings such as ``"$PAD_DIAM"`` were passed
        directly to the gRPC ``CorePadstackDefData.set_pad_parameters(sizes=...)``
        call without being wrapped in a ``Value`` object that carries an owner
        (``active_db`` for ``$``-prefixed project variables).  The gRPC server
        silently dropped the geometry, producing empty pad definitions.

        Fix: every dimension in ``set_pad_parameters`` / ``set_hole_parameters``
        is now routed through ``self._pedb._value_setter()``.
        """
        edbapp = self.edb_examples.create_empty_edb()

        # A minimal two-layer stackup is required before padstack operations
        edbapp.stackup.add_layer("Top", layer_type="signal", material="copper", thickness="35um")
        edbapp.stackup.add_layer("Bot", method="add_on_bottom", layer_type="signal", thickness="35um")

        # Declare project-level variables ($-prefixed → owner is active_db)
        edbapp["$PAD_DIAM"] = "0.25mm"
        edbapp["$HOLE_DIAM"] = "0.1mm"

        signal_layers = list(edbapp.stackup.signal_layers.keys())
        assert signal_layers, "Stackup must expose at least one signal layer"

        # Create the definition shell and apply parameterised pad/hole data directly
        edbapp.padstacks.create(padstackname="PARAM_VIA", holediam=0)
        pdef = edbapp.padstacks.definitions["PARAM_VIA"]

        pad_params = {
            "regular_pad": [
                {"layer_name": layer, "shape": "circle", "diameter": "$PAD_DIAM"} for layer in signal_layers
            ]
        }
        pdef.set_pad_parameters(pad_params)
        pdef.set_hole_parameters({"shape": "circle", "diameter": "$HOLE_DIAM"})

        assert "PARAM_VIA" in edbapp.padstacks.definitions, "PARAM_VIA definition must exist after creation"
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Regression test for gRPC Value owner requirement.")
    def test_parametric_padstack_pad_sizes_resolved(self):
        """Pad/hole sizes expressed as project variables must resolve to correct numeric values.

        After ``set_pad_parameters`` and ``set_hole_parameters`` are called with
        ``"$PAD_DIAM"`` / ``"$HOLE_DIAM"``, ``pad_by_layer[layer].parameters_values``
        must return the evaluated float (e.g. 0.00025 for ``"0.25mm"``).
        """
        edbapp = self.edb_examples.create_empty_edb()

        # Minimal stackup
        edbapp.stackup.add_layer("Top", layer_type="signal", material="copper", thickness="35um")
        first_layer = "Top"

        edbapp["$PAD_DIAM"] = "0.25mm"
        edbapp["$HOLE_DIAM"] = "0.1mm"

        edbapp.padstacks.create(padstackname="PARAM_VIA2", holediam=0)
        pdef = edbapp.padstacks.definitions["PARAM_VIA2"]
        pdef.set_pad_parameters(
            {"regular_pad": [{"layer_name": first_layer, "shape": "circle", "diameter": "$PAD_DIAM"}]}
        )
        pdef.set_hole_parameters({"shape": "circle", "diameter": "$HOLE_DIAM"})

        # Pad diameter must resolve to 0.25 mm
        pad = pdef.pad_by_layer.get(first_layer)
        assert pad is not None, f"Pad not found on layer {first_layer}"
        params = pad.parameters_values
        assert params and len(params) > 0, "parameters_values must be non-empty after set_pad_parameters"
        assert abs(float(params[0]) - 0.00025) < 1e-9, (
            f"Pad diameter expected 0.00025 m (0.25 mm), got {float(params[0])}"
        )

        # Hole diameter must resolve to 0.1 mm
        hole_diam = float(pdef.hole_diameter)
        assert abs(hole_diam - 0.0001) < 1e-9, f"Hole diameter expected 0.0001 m (0.1 mm), got {hole_diam}"

        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Regression test for gRPC net-name handling.")
    def test_parametric_padstack_place_no_ghost_nets(self):
        """padstacks.place() must assign the exact requested net — no ghost net_XXXX nets.

        Regression: ``PadstackInstance.create()`` used ``dict.get(name, Net.create(...random...))``
        which Python always evaluates eagerly, so a randomly-named ``net_XXXX`` net was
        created on every single ``place()`` call, even when the net already existed.

        Fix: replaced with ``dict.get(name) or Net.create(layout, name)`` so the
        fallback only fires when the net is genuinely absent, and always uses the
        correct name.
        """
        import re

        edbapp = self.edb_examples.create_empty_edb()

        # Minimal stackup required for padstack placement
        edbapp.stackup.add_layer("Top", layer_type="signal", material="copper", thickness="35um")
        edbapp.stackup.add_layer("Bot", method="add_on_bottom", layer_type="signal", thickness="35um")

        edbapp.padstacks.create(padstackname="VIA_NET_TEST", paddiam="0.2mm", holediam="0.1mm")

        # Place instances on two named nets — neither exists yet when first placed
        edbapp.padstacks.place([0, 0], "VIA_NET_TEST", net_name="SIG")
        edbapp.padstacks.place([1e-3, 0], "VIA_NET_TEST", net_name="GND")
        edbapp.padstacks.place([2e-3, 0], "VIA_NET_TEST", net_name="SIG")

        net_names = list(edbapp.nets.nets.keys())

        # Both requested nets must exist with their exact names
        assert "SIG" in net_names, f"Net 'SIG' not found; nets present: {net_names}"
        assert "GND" in net_names, f"Net 'GND' not found; nets present: {net_names}"

        # No ghost net_XXXX nets should have been created
        ghost_nets = [n for n in net_names if re.match(r"^net_[A-Z0-9]{4,}$", n, re.IGNORECASE)]
        assert not ghost_nets, f"Ghost nets found after padstack placement: {ghost_nets}"

        # Verify instance-to-net assignment is correct
        instances = list(edbapp.padstacks.instances.values())
        sig_count = sum(1 for i in instances if i.net_name == "SIG")
        gnd_count = sum(1 for i in instances if i.net_name == "GND")
        assert sig_count == 2, f"Expected 2 SIG instances, got {sig_count}"
        assert gnd_count == 1, f"Expected 1 GND instance, got {gnd_count}"

        edbapp.close(terminate_rpc_session=False)
