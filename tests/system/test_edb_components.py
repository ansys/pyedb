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

"""Tests related to Edb components"""

import math
import os

import pytest

from tests.conftest import config, local_path, test_subfolder, use_grpc
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]

bom_example = "bom_example.csv"


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_components_get_pin_from_component(self):
        """Evaluate access to a pin from a component."""
        edb = self.edb_examples.get_si_verse()
        comp = edb.components.get_component_by_name("J1")
        assert comp is not None
        pin = edb.components.get_pin_from_component("J1", pin_name="1")
        # TODO check if we agree to return aedt_name when it's a layout pin.
        assert pin[0].name == "1"
        edb.close(terminate_rpc_session=False)

    def test_components_create_coax_port_on_component(self):
        """Create a coaxial port on a component from its pin."""
        edb = self.edb_examples.get_si_verse()
        coax_port = edb.components["U6"].pins["R3"].create_coax_port("coax_port")
        coax_port.radial_extent_factor = 3
        assert coax_port.radial_extent_factor == 3
        assert coax_port.component
        assert edb.components["U6"].pins["R3"].get_terminal()
        assert edb.components["U6"].pins["R3"].id
        assert edb.terminals
        assert edb.ports
        assert len(edb.components["U6"].pins["R3"].get_connected_objects()) == 17
        edb.close(terminate_rpc_session=False)

    def test_components_properties(self):
        """Access components properties."""
        edb = self.edb_examples.get_si_verse()
        assert len(edb.components.instances) > 2
        assert len(edb.components.inductors) > 0
        assert len(edb.components.resistors) > 0
        assert len(edb.components.capacitors) > 0
        assert len(edb.components.ICs) > 0
        assert len(edb.components.IOs) > 0
        assert len(edb.components.Others) > 0
        edb.close(terminate_rpc_session=False)

    def test_components_rlc_components_values(self):
        """Update values of an RLC component."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.set_component_rlc("C1", res_value=0.1, cap_value="5e-6", ind_value=1e-9, isparallel=False)
        component = edb.components.instances["C1"]
        assert component.rlc_values == [0.1, 1e-9, 5e-6]
        assert edb.components.set_component_rlc("L10", res_value=1e-3, ind_value="10e-6", isparallel=True)
        component = edb.components.instances["L10"]
        assert component.rlc_values == [1e-3, 10e-6, 0.0]
        edb.close(terminate_rpc_session=False)

    def test_components_r1_queries(self):
        """Evaluate queries over component R1."""
        edb = self.edb_examples.get_si_verse()
        assert "R1" in list(edb.components.instances.keys())
        assert not edb.components.instances["R1"].is_null
        assert edb.components.instances["R1"].res_value == 6200
        assert edb.components.instances["R1"].placement_layer == "16_Bottom"
        if edb.grpc:
            assert not edb.components.instances["R1"].component_def.is_null
        else:
            # grpc returns ComponentDef object while DotNet just the string for the name.
            assert edb.components.instances["R1"].component_def
        location = edb.components.instances["R1"].location
        assert location[0] == 0.11167500144
        assert location[1] == 0.04072499856
        assert edb.components.instances["R1"].lower_elevation == 0.0
        assert edb.components.instances["R1"].upper_elevation == pytest.approx(35e-6)
        assert edb.components.instances["R1"].top_bottom_association == 2
        assert len(edb.components.instances["R1"].pinlist) == 2
        assert edb.components.instances["R1"].pins
        assert edb.components.instances["R1"].pins["1"].aedt_name == "R1-1"
        assert edb.components.instances["R1"].pins["1"].component_pin == "1"

        assert not edb.components.instances["R1"].pins["1"].component.is_null
        assert (
            edb.components.instances["R1"].pins["1"].placement_layer == edb.components.instances["R1"].placement_layer
        )
        assert (
            edb.components.instances["R1"].pins["1"].upper_elevation == edb.components.instances["R1"].upper_elevation
        )
        assert (
            edb.components.instances["R1"].pins["1"].top_bottom_association
            == edb.components.instances["R1"].top_bottom_association
        )
        assert [round(i, 6) for i in edb.components.instances["R1"].pins["1"].position] == [0.111675, 0.039975]
        assert round(edb.components.instances["R1"].pins["1"].rotation, 6) == -1.570796
        edb.close(terminate_rpc_session=False)

    def test_components_create_clearance_on_component(self):
        """Evaluate the creation of a clearance on soldermask."""
        edb = self.edb_examples.get_si_verse_sfp()
        comp = edb.components.instances["U1"]
        assert comp.create_clearance_on_component()
        edb.close(terminate_rpc_session=False)

    def test_components_get_components_from_nets(self):
        """Access to components from nets."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.get_components_from_nets("DDR4_DQS0_P")
        edb.close(terminate_rpc_session=False)

    def test_components_resistors(self):
        """Evaluate component resistors."""
        edb = self.edb_examples.get_si_verse()
        assert "R1" in list(edb.components.resistors.keys())
        assert "C1" not in list(edb.components.resistors.keys())
        assert "C1" in list(edb.components.capacitors.keys())
        assert "R1" not in list(edb.components.capacitors.keys())
        assert "L10" in list(edb.components.inductors.keys())
        assert "R1" not in list(edb.components.inductors.keys())
        assert "U1" in list(edb.components.ICs.keys())
        assert "R1" not in list(edb.components.ICs.keys())
        assert "X1" in list(edb.components.IOs.keys())
        assert "R1" not in list(edb.components.IOs.keys())
        assert "B1" in edb.components.Others
        assert "R1" not in edb.components.Others
        comp = edb.components.components_by_partname
        assert "ALTR-FBGA24_A-130" in comp
        assert len(comp["ALTR-FBGA24_A-130"]) == 1
        edb.components.get_through_resistor_list(10)
        assert len(edb.components.get_rats()) > 0
        assert len(edb.components.get_component_net_connection_info("U1")) > 0
        edb.close(terminate_rpc_session=False)

    def test_components_get_pin_name_and_position(self):
        """Retrieve component name and position."""
        edb = self.edb_examples.get_si_verse()
        cmp_pinlist = edb.padstacks.get_pinlist_from_component_and_net("U6", "GND")
        pin_name = edb.components.get_aedt_pin_name(cmp_pinlist[0])
        assert type(pin_name) is str
        assert len(pin_name) > 0
        assert len(cmp_pinlist[0].position) == 2
        assert len(edb.components.get_pin_position(cmp_pinlist[0])) == 2
        edb.close(terminate_rpc_session=False)

    def test_components_get_pins_name_from_net(self):
        """Retrieve pins belonging to a net."""
        edb = self.edb_examples.get_si_verse()
        cmp_pinlist = edb.components.get_pin_from_component("U6")
        assert len(edb.components.get_pins_name_from_net("GND", cmp_pinlist)) > 0
        assert len(edb.components.get_pins_name_from_net("5V", cmp_pinlist)) == 0
        edb.close(terminate_rpc_session=False)

    def test_components_delete_single_pin_rlc(self):
        """Delete all RLC components with a single pin."""
        edb = self.edb_examples.get_si_verse()
        assert len(edb.components.delete_single_pin_rlc()) == 0
        edb.close(terminate_rpc_session=False)

    def test_components_set_component_rlc(self):
        """Update values for an RLC component."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.set_component_rlc("R1", 30, 1e-9, 1e-12)
        assert edb.components.disable_rlc_component("R1")
        assert edb.components.delete("R1")
        edb.close(terminate_rpc_session=False)

    def test_components_set_model(self):
        """Assign component model."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.set_component_model(
            "C10",
            modelpath=os.path.join(
                local_path,
                "example_models",
                test_subfolder,
                "GRM32ER72A225KA35_25C_0V.sp",
            ),
            modelname="GRM32ER72A225KA35_25C_0V",
        )
        try:
            edb.components.set_component_model(
                "C100000",
                modelpath=os.path.join(
                    local_path,
                    test_subfolder,
                    "GRM32ER72A225KA35_25C_0V.sp",
                ),
                modelname="GRM32ER72A225KA35_25C_0V",
            )
        except ValueError as e:
            assert str(e) == f"Component C100000 not found in the layout."
        edb.close(terminate_rpc_session=False)

    def test_modeler_parametrize_layout(self):
        """Parametrize a polygon"""
        edb = self.edb_examples.get_si_verse()
        assert len(edb.modeler.polygons) > 0
        for el in edb.modeler.polygons:
            if edb.grpc:
                if el.edb_uid == 5953:
                    poly = el
            else:
                if el.id == 5953:
                    poly = el
        for el in edb.modeler.polygons:
            if edb.grpc:
                # TODO check enhancement request #550 status to remove this condition.
                if el.edb_uid == 5954:
                    selection_poly = el
            else:
                if el.id == 5954:
                    selection_poly = el
        assert edb.modeler.parametrize_polygon(poly, selection_poly)
        edb.close(terminate_rpc_session=False)

    def test_components_update_from_bom(self):
        """Update components with values coming from a BOM file."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.update_rlc_from_bom(
            os.path.join(local_path, "example_models", test_subfolder, bom_example),
            delimiter=",",
            valuefield="Value",
            comptype="Prod name",
            refdes="RefDes",
        )
        assert not edb.components.instances["R2"].enabled
        edb.components.instances["R2"].enabled = True
        assert edb.components.instances["R2"].enabled
        edb.close(terminate_rpc_session=False)

    def test_components_export_bom(self):
        """Export Bom file from layout."""
        edb = self.edb_examples.get_si_verse()
        edb.components.import_bom(os.path.join(local_path, "example_models", test_subfolder, "bom_example_2.csv"))
        assert not edb.components.instances["R2"].enabled
        assert edb.components.instances["U13"].partname == "SLAB-QFN-24-2550x2550TP_V"

        export_bom_path = os.path.join(self.edb_examples.test_folder, "export_bom.csv")
        assert edb.components.export_bom(export_bom_path)
        edb.close(terminate_rpc_session=False)

    def test_components_create_component_from_pins(self):
        """Create a component from a pin."""
        edb = self.edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("R13")
        component = edb.components.create(pins, "newcomp")
        assert component
        assert component.part_name == "newcomp"
        assert len(component.pins) == 2
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(use_grpc, reason="DotNet module not available in gRPC mode without .NET installation")
    def test_convert_resistor_value(self):
        """Convert a resistor value."""
        from pyedb.dotnet.database.components import resistor_value_parser

        assert resistor_value_parser("100meg")

    def test_components_create_solder_ball_on_component(self):
        """Set cylindrical solder balls on a given component"""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.set_solder_ball("U1", shape="Spheroid")
        assert edb.components.set_solder_ball("U6", sball_height=None)
        assert edb.components.set_solder_ball(
            "U6", sball_height="100um", auto_reference_size=False, chip_orientation="chip_up"
        )
        assert edb.components["U6"].solder_ball_shape == "cylinder"
        edb.components["U6"].solder_ball_shape = None
        assert edb.components["U6"].solder_ball_shape == "none"
        edb.close(terminate_rpc_session=False)

    def test_components_short_component(self):
        """Short pins of component with a trace."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.short_component_pins("U12", width=0.2e-3)
        assert edb.components.short_component_pins("U10", ["2", "5"])
        edb.close(terminate_rpc_session=False)

    def test_components_type(self):
        """Retrieve components type."""
        edb = self.edb_examples.get_si_verse()
        comp = edb.components["R4"]
        comp.type = "resistor"
        assert comp.type.lower() == "resistor"
        comp.type = "inductor"
        assert comp.type.lower() == "inductor"
        comp.type = "capacitor"
        assert comp.type.lower() == "capacitor"
        comp.type = "io"
        assert comp.type.lower() == "io"
        comp.type = "ic"
        assert comp.type.lower() == "ic"
        comp.type = "other"
        assert comp.type.lower() == "other"
        edb.close(terminate_rpc_session=False)

    def test_componenets_deactivate_rlc(self):
        """Deactivate RLC component and convert to a circuit port."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.components.deactivate_rlc_component(component="C1", create_circuit_port=False)
        assert "C1" not in edbapp.ports
        assert edbapp.components["C1"].is_enabled is False
        assert edbapp.components.deactivate_rlc_component(component="C2", create_circuit_port=True)
        edbapp.components["C2"].is_enabled = False
        assert edbapp.components["C2"].is_enabled is False
        edbapp.components["C2"].is_enabled = True
        assert edbapp.components["C2"].is_enabled is True
        pins = [*edbapp.components.instances["L10"].pins.values()]
        edbapp.excitation_manager.create_port_on_pins("L10", pins[0], pins[1])
        assert edbapp.components["L10"].is_enabled is False
        assert "L10" in edbapp.ports.keys()

    def test_components_definitions(self):
        """Evaluate components definition."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.components.instances
        assert edbapp.components.definitions
        comp_def = edbapp.components.definitions["CAPC2012X12N"]
        assert comp_def
        comp_def.part_name = "CAPC2012X12N_new"
        assert comp_def.part_name == "CAPC2012X12N_new"
        assert len(comp_def.components) > 0
        cap = edbapp.components.definitions["CAPC2012X12N_new"]
        assert cap.type.lower() == "capacitor"
        cap.type = "resistor"
        assert cap.type.lower() == "resistor"
        edbapp.close(terminate_rpc_session=False)

    def test_rlc_component_values_getter_setter(self):
        """Evaluate component values getter and setter."""
        edbapp = self.edb_examples.get_si_verse()
        components_to_change = [res for res in list(edbapp.components.Others.values()) if res.partname == "A93549-027"]
        for res in components_to_change:
            res.type = "Resistor"
            res.res_value = [25, 0, 0]
            res.res_value = 10
            assert res.res_value == 10
            res.rlc_values = [20, 1e-9, 1e-12]
            assert res.res_value == 20
            assert res.ind_value == 1e-9
            assert res.cap_value == 1e-12
            res.res_value = 12.5
            assert res.res_value == 12.5 and res.ind_value == 1e-9 and res.cap_value == 1e-12
            res.ind_value = 5e-9
            assert res.res_value == 12.5 and res.ind_value == 5e-9 and res.cap_value == 1e-12
            res.cap_value = 8e-12
            assert res.res_value == 12.5 and res.ind_value == 5e-9 and res.cap_value == 8e-12
        edbapp.close(terminate_rpc_session=False)

    def test_create_port_on_pin(self):
        """Create port on pins."""
        edbapp = self.edb_examples.get_si_verse()
        pin = "A24"
        ref_pins = [pin for pin in list(edbapp.components["U1"].pins.values()) if pin.net_name == "GND"]
        assert edbapp.excitation_manager.create_port_on_pins(refdes="U1", pins=pin, reference_pins=ref_pins)
        assert edbapp.excitation_manager.create_port_on_pins(refdes="U1", pins="C1", reference_pins=["A11"])
        assert edbapp.excitation_manager.create_port_on_pins(refdes="U1", pins="C2", reference_pins=["A11"])
        assert edbapp.excitation_manager.create_port_on_pins(refdes="U1", pins=["A24"], reference_pins=["A11", "A16"])
        assert edbapp.excitation_manager.create_port_on_pins(
            refdes="U1", pins=["A26"], reference_pins=["A11", "A16", "A17"]
        )
        assert edbapp.excitation_manager.create_port_on_pins(refdes="U1", pins=["A28"], reference_pins=["A11", "A16"])
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(config["desktopVersion"] < "2026.1" and config["use_grpc"], reason="Requires 2026R1")
    def test_replace_rlc_by_gap_boundaries(self):
        """Replace RLC component by RLC gap boundaries."""
        # TODO check how we can return same boundary_type between grpc and dotnet.
        edbapp = self.edb_examples.get_si_verse()
        names = [i for i in edbapp.components.instances.keys()][:5]
        for refdes in names:
            edbapp.components.replace_rlc_by_gap_boundaries(refdes)
        if edbapp.grpc:
            rlc_list = [term for term in list(edbapp.terminals.values()) if term.boundary_type == "rlc"]
        else:
            rlc_list = [term for term in list(edbapp.terminals.values()) if term.boundary_type == "RlcBoundary"]
        assert len(rlc_list) == 10
        edbapp.close(terminate_rpc_session=False)

    def test_components_get_component_placement_vector(self):
        """Get the placement vector between 2 components."""
        target_path4 = self.edb_examples.copy_test_files_into_local_folder("TEDB/Package.aedb")[0]
        edbapp = self.edb_examples.get_si_verse()
        edb2 = self.edb_examples.load_edb(target_path4)
        for _, cmp in edb2.components.instances.items():
            assert isinstance(cmp.solder_ball_placement, int)
        mounted_cmp = edb2.components.get_component_by_name("BGA")
        hosting_cmp = edbapp.components.get_component_by_name("U1")
        (
            result,
            vector,
            rotation,
            solder_ball_height,
        ) = edbapp.components.get_component_placement_vector(
            mounted_component=mounted_cmp,
            hosting_component=hosting_cmp,
            mounted_component_pin1="A10",
            mounted_component_pin2="A12",
            hosting_component_pin1="A2",
            hosting_component_pin2="A4",
        )
        assert result
        if edbapp.grpc:
            # TODO check why grpc and dotnet are returning different values.
            assert abs(abs(rotation) - math.pi / 2) * 180 / math.pi == 90.0
        else:
            assert abs(abs(rotation) - math.pi / 2) * 180 / math.pi == 0.0
        assert solder_ball_height == 0.00033
        assert len(vector) == 2
        if edbapp.grpc:
            # grpc default behavior is to terminate rpc session when closing edb.
            edbapp.close(terminate_rpc_session=False)
        else:
            edbapp.close(terminate_rpc_session=False)
        edb2.close(terminate_rpc_session=False)

    def test_components_assign(self):
        """Assign RLC model, S-parameter model and spice model."""
        edbapp = self.edb_examples.get_si_verse()
        sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
        spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")
        comp = edbapp.components.instances["R2"]
        assert not comp.assign_rlc_model()
        comp.assign_rlc_model(1, None, 3, False)
        assert not comp.is_parallel_rlc and comp.res_value == 1 and comp.ind_value == 0 and comp.cap_value == 3
        comp.assign_rlc_model(1, 2, 3, True)
        assert comp.is_parallel_rlc
        assert comp.is_parallel_rlc and comp.res_value == 1 and comp.ind_value == 2 and comp.cap_value == 3
        assert comp.rlc_values
        assert not comp.spice_model and not comp.s_param_model and not comp.netlist_model
        comp.assign_s_param_model(sparam_path)
        assert comp.s_param_model
        assert not comp.s_param_model.is_null
        comp.assign_spice_model(spice_path)
        assert comp.spice_model
        comp.type = "inductor"
        comp.value = 10  # This command set the model back to ideal RLC
        assert comp.type.lower() == "inductor" and comp.value == 10 and float(comp.ind_value) == 10

        edbapp.components["C164"].assign_spice_model(
            spice_path, sub_circuit_name="GRM32ER60J227ME05_DC0V_25degC", terminal_pairs=[["port1", 2], ["port2", 1]]
        )
        # adding cutout section to test pin preservation handle
        assert edbapp.cutout(
            signal_nets=["DDR4_DQS0_P", "DDR4_DQS0_N", "5V"],
            reference_nets=["GND"],
            extent_type="convex_hull",
            use_pyaedt_extent_computing=True,
            include_pingroups=True,
            check_terminals=True,
            expansion_factor="1mm",
            preserve_components_with_model=True,
        )
        # TODO: second cutout on an already-cut layout causes null transform errors in gRPC — skip for now.
        edbapp.close(terminate_rpc_session=False)

    def test_components_bounding_box(self):
        """Get component's bounding box."""
        edbapp = self.edb_examples.get_si_verse()
        component = edbapp.components.instances["U1"]
        assert component.id
        assert component.bounding_box
        assert isinstance(component.rotation, float)
        edbapp.close(terminate_rpc_session=False)

    def test_pec_boundary_ports(self):
        """Check pec boundary ports."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.excitation_manager.create_port_on_pins(
            refdes="U1", pins="AU38", reference_pins="AU37", pec_boundary=True
        )
        if edbapp.grpc:
            assert edbapp.terminals["Port_GND_U1_AU38"].boundary_type == "pec"
            assert edbapp.terminals["Port_GND_U1_AU38_ref"].boundary_type == "pec"
        else:
            assert edbapp.terminals["Port_GND_U1_AU38"].boundary_type == "PecBoundary"
            assert edbapp.terminals["Port_GND_U1_AU38_ref"].boundary_type == "PecBoundary"
        edbapp.components.deactivate_rlc_component(component="C5", create_circuit_port=True, pec_boundary=True)
        edbapp.components.add_port_on_rlc_component(component="C65", circuit_ports=False, pec_boundary=True)
        if edbapp.grpc:
            assert edbapp.terminals["C5"].boundary_type == "pec"
            assert edbapp.terminals["C65"].boundary_type == "pec"
        else:
            assert edbapp.terminals["C5"].boundary_type == "PecBoundary"
            assert edbapp.terminals["C65"].boundary_type == "PecBoundary"
        edbapp.close(terminate_rpc_session=False)

    def test_is_top_mounted(self):
        """Check is_top_mounted property."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.components.instances["U1"].is_top_mounted
        assert not edbapp.components.instances["C347"].is_top_mounted
        assert not edbapp.components.instances["R67"].is_top_mounted
        edbapp.close(terminate_rpc_session=False)

    def test_instances(self):
        """Check instances access and values."""
        edbapp = self.edb_examples.get_si_verse()
        comp_pins = edbapp.components.instances["U1"].pins
        pins = [comp_pins["AM38"], comp_pins["AL37"]]
        edbapp.components.create(
            component_part_name="Test_part", component_name="Test", is_rlc=True, r_value=12.2, pins=pins
        )
        assert edbapp.components.instances["Test"]
        assert edbapp.components.instances["Test"].res_value == 12.2
        assert edbapp.components.instances["Test"].ind_value == 0
        assert edbapp.components.instances["Test"].cap_value == 0
        if edbapp.grpc:
            # TODO check why grpc is returning different center value.
            assert edbapp.components.instances["Test"].center == (0.07950000102, 0.03399999804)
        else:
            assert edbapp.components.instances["Test"].center == [0.068, 0.0165]
        edbapp.close(terminate_rpc_session=False)

    def test_create_package_def(self):
        """Check the creation of package definition."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components["C200"].create_package_def(component_part_name="SMTC-MECT-110-01-M-D-RA1_V")
        assert not edb.components["C200"].create_package_def()
        assert edb.components["C200"].package_def.name == "C200_CAPC3216X180X55ML20T25"
        if edb.grpc:
            pkg_def = edb.components["C200"].package_def
            assert not pkg_def.exterior_boundary.points
            assert pkg_def.set_exterior_boundary_from_bbox("C200")
            assert len(pkg_def.exterior_boundary.points) == 4
            assert len(pkg_def.exterior_boundary_with_arcs.arcs) == 4
            assert pkg_def.set_exterior_boundary_from_bbox(edb.components.instances["C200"])
        edb.close(terminate_rpc_session=False)

    def test_solder_ball_getter_setter(self):
        edb = self.edb_examples.get_si_verse()
        cmp = edb.components.instances["X1"]
        cmp.solder_ball_height = 0.0
        assert cmp.solder_ball_height == 0.0
        cmp.solder_ball_height = "100um"
        assert cmp.solder_ball_height == pytest.approx(100e-6)
        assert cmp.solder_ball_shape
        cmp.solder_ball_shape = "cylinder"
        assert cmp.solder_ball_shape == "cylinder"
        cmp.solder_ball_shape = "spheroid"
        assert cmp.solder_ball_shape == "spheroid"
        cmp.solder_ball_shape = "cylinder"
        assert cmp.solder_ball_diameter == (0.0, 0.0)
        cmp.solder_ball_diameter = "200um"
        diam1, diam2 = cmp.solder_ball_diameter
        assert diam1 == pytest.approx(200e-6)
        assert diam2 == pytest.approx(200e-6)
        cmp.solder_ball_diameter = ("100um", "100um")
        diam1, diam2 = cmp.solder_ball_diameter
        assert diam1 == pytest.approx(100e-6)
        assert diam2 == pytest.approx(100e-6)
        cmp.solder_ball_material = "copper"
        assert cmp.solder_ball_material == "copper"
        # material not defined is not applied
        cmp.solder_ball_material = "copper_2"
        assert not cmp.solder_ball_material == "copper_2"
        edb.components.set_solder_ball(
            component="U1",
            sball_diam="100um",
            sball_height="150um",
            shape="cylinder",
            material_name="copper_test",
        )
        cmp2 = edb.components.instances["U1"]
        assert "copper_test" in edb.materials
        assert cmp2.solder_ball_material == "copper_test"
        assert cmp2.solder_ball_height == pytest.approx(150e-6)
        assert cmp.solder_ball_diameter == (pytest.approx(100e-6), pytest.approx(100e-6))
        edb.close(terminate_rpc_session=False)

    def test_create_pingroup_from_pins_types(self):
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.components.create_pingroup_from_pins([*edbapp.components.instances["Q1"].pins.values()])
        assert edbapp.excitation_manager._create_pin_group_terminal(edbapp.padstacks.pingroups[0], term_type="circuit")
        edbapp.close(terminate_rpc_session=False)

    def test_component_lib(self):
        edbapp = self.edb_examples.create_empty_edb()
        comp_lib = edbapp.components.get_vendor_libraries()
        assert len(comp_lib.capacitors) > 0
        assert len(comp_lib.inductors) > 0
        network = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].s_parameters
        test_esr = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].esr
        test_esl = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].esl
        assert round(test_esr, 4) == 1.7552
        assert round(test_esl, 12) == 2.59e-10
        assert network
        assert network.frequency.npoints == 400
        network.write_touchstone(os.path.join(edbapp.edbpath, "test_export.s2p"))
        assert os.path.isfile(os.path.join(edbapp.edbpath, "test_export.s2p"))

    def test_properties(self):
        edbapp = self.edb_examples.get_si_verse()
        pp = {
            "pin_pair_model": [
                {
                    "first_pin": "2",
                    "second_pin": "1",
                    "is_parallel": True,
                    "resistance": "10ohm",
                    "resistance_enabled": True,
                    "inductance": "1nH",
                    "inductance_enabled": True,
                    "capacitance": "1nF",
                    "capacitance_enabled": True,
                }
            ]
        }
        edbapp.components["C378"].model_properties = pp
        assert edbapp.components["C378"].model_properties == pp
        edbapp.close(terminate_rpc_session=False)

    def test_ic_die_properties(self):
        edbapp = self.edb_examples.get_si_verse()
        component = edbapp.components["U8"]
        if edbapp.grpc:
            assert component.ic_die_properties.die_orientation == "chip_up"
            component.ic_die_properties.die_orientation = "chip_down"
            assert component.ic_die_properties.die_orientation == "chip_down"
            assert component.ic_die_properties.die_type == "none"
            assert component.ic_die_properties.height == 0.0
            component.ic_die_properties.height = 1e-3
            assert component.ic_die_properties.height == 1e-3
        else:
            ic_die_properties = component.ic_die_properties
            assert ic_die_properties.die_orientation == "chip_up"
            ic_die_properties.orientation = "chip_down"
            assert ic_die_properties.orientation == "chip_down"
            assert ic_die_properties.die_type in ["none", "no_die"]
            assert ic_die_properties.height == 0.0
            ic_die_properties.height = 1e-3
            assert ic_die_properties.height == 1e-3
        edbapp.close(terminate_rpc_session=False)

    def test_rlc_component_302(self):
        edbapp = self.edb_examples.get_si_verse()
        pins = edbapp.components.get_pin_from_component("C31")
        component = edbapp.components.create([pins[0], pins[1]], r_value=1.2, component_name="TEST", is_rlc=True)
        assert component
        assert component.name == "TEST"
        comp_location = component.location
        assert round(comp_location[0], 8) == 0.13275000
        assert round(comp_location[1], 8) == 0.07350000
        assert component.res_value == 1.2
        edbapp.close(terminate_rpc_session=False)

    def test_export_gds_comp_xml(self):
        edbapp = self.edb_examples.get_si_verse()
        xml_output = os.path.join(self.edb_examples.test_folder, "test.xml")
        assert edbapp.export_gds_comp_xml(["U1", "U2", "C2", "R1"], control_path=xml_output)
        assert os.path.isfile(xml_output)
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_find_by_reference_designator(self):
        """find_by_reference_designator returns the same object as instances[]."""
        edb = self.edb_examples.get_si_verse()
        comp = edb.components.find_by_reference_designator("R1")
        assert comp is not None
        assert comp.name == "R1"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_pins_with_filters(self):
        """get_pins() with net_name and pin_name filters."""
        edb = self.edb_examples.get_si_verse()
        # no filter – all pins
        all_pins = edb.components.get_pins("U6")
        assert len(all_pins) > 0
        # net filter
        gnd_pins = edb.components.get_pins("U6", net_name="GND")
        assert len(gnd_pins) > 0
        for pin in gnd_pins.values():
            assert pin.net_name == "GND"
        # pin name filter
        first_pin_name = list(edb.components.get_pins("R1").keys())[0]
        filtered = edb.components.get_pins("R1", pin_name=first_pin_name)
        assert len(filtered) == 1
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_nets_from_pin_list(self):
        """get_nets_from_pin_list() returns unique net names."""
        edb = self.edb_examples.get_si_verse()
        pins = list(edb.components.instances["U1"].pins.values())[:10]
        nets = edb.components.get_nets_from_pin_list(pins)
        assert isinstance(nets, list)
        assert len(nets) > 0
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_rats(self):
        """get_rats() returns a non-empty list of connection info dicts."""
        edb = self.edb_examples.get_si_verse()
        rats = edb.components.get_rats()
        assert isinstance(rats, list)
        assert len(rats) > 0
        # Each entry must have the expected keys
        assert "refdes" in rats[0]
        assert "pin_name" in rats[0]
        assert "net_name" in rats[0]
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_component_net_connection_info(self):
        """get_component_net_connection_info returns correct structure."""
        edb = self.edb_examples.get_si_verse()
        info = edb.components.get_component_net_connection_info("R1")
        assert "refdes" in info
        assert "pin_name" in info
        assert "net_name" in info
        assert len(info["pin_name"]) == 2  # R1 has 2 pins
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_through_resistor_list(self):
        """get_through_resistor_list returns resistors below threshold."""
        edb = self.edb_examples.get_si_verse()
        result = edb.components.get_through_resistor_list(threshold=10)
        assert isinstance(result, list)
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_nport_comp_definition(self):
        """nport_comp_definition returns a dict of definitions with a reference file."""
        edb = self.edb_examples.get_si_verse()
        result = edb.components.nport_comp_definition
        assert isinstance(result, dict)
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_components_by_partname(self):
        """components_by_partname groups components correctly."""
        edb = self.edb_examples.get_si_verse()
        by_part = edb.components.components_by_partname
        assert isinstance(by_part, dict)
        assert len(by_part) > 0
        # Each value must be a non-empty list
        for part, comps in by_part.items():
            assert isinstance(comps, list)
            assert len(comps) >= 1
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_create_pin_group_on_net(self):
        """create_pin_group_on_net creates a pin group for all GND pins on U6."""
        edb = self.edb_examples.get_si_verse()
        result = edb.components.create_pin_group_on_net("U6", "GND", "pg_U6_GND")
        assert result is not False
        group_name, pg = result
        assert group_name == "pg_U6_GND"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_create_pin_group(self):
        """create_pin_group creates a pin group from a list of pin names on a known net."""
        edb = self.edb_examples.get_si_verse()
        # Use pins that are on a real net so create_pin_group succeeds
        gnd_pins = [
            name
            for name, pin in edb.components.instances["U1"].pins.items()
            if not pin.net.is_null and pin.net.name == "GND"
        ]
        assert gnd_pins, "Expected at least one GND pin on U1"
        result = edb.components.create_pin_group("U1", gnd_pins[:2], "pg_u1_manual")
        assert result is not False
        group_name, pg = result
        assert group_name == "pg_u1_manual"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_add_port_on_rlc_component(self):
        """add_port_on_rlc_component creates a circuit port on an RLC component."""
        edb = self.edb_examples.get_si_verse()
        result = edb.components.add_port_on_rlc_component(component="C65", circuit_ports=True)
        assert result is True
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_structures_3d(self):
        """structures_3d property returns a dict (may be empty on si_verse)."""
        edb = self.edb_examples.get_si_verse()
        result = edb.components.structures_3d
        assert isinstance(result, dict)
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_export_and_import_definition(self):
        """export_definition / import_definition round-trip RLC model."""
        edb = self.edb_examples.get_si_verse()
        export_path = os.path.join(self.edb_examples.test_folder, "comp_def.json")
        assert edb.components.export_definition(export_path)
        assert os.path.isfile(export_path)
        assert edb.components.import_definition(export_path)
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_solder_ball_height(self):
        """get_solder_ball_height returns a float for a component with solder balls."""
        edb = self.edb_examples.get_si_verse()
        # Set a solder ball first to ensure it has a value
        edb.components.set_solder_ball("U1", sball_diam="100um", sball_height="150um")
        height = edb.components.get_solder_ball_height("U1")
        assert isinstance(height, float)
        assert height == pytest.approx(150e-6)
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_set_solder_ball_ic_component_properties_persisted(self):
        """set_solder_ball correctly persists all solder-ball and die properties for an IC component.

        Regression test for the bug where ICComponentProperty sub-property getters return
        server-side copies that were mutated but never linked back via the typed setter
        (SetSolderBallProperty / SetDieProperty / SetPortProperty), so no changes were
        reflected on the component.
        """
        edb = self.edb_examples.get_si_verse()
        comp = edb.components["U1"]
        assert comp.component_type == "ic", "U1 must be an IC component for this test to be meaningful"

        sball_diam = 330e-6
        sball_height = 330e-6
        assert edb.components.set_solder_ball("U1", sball_diam=sball_diam, sball_height=sball_height)

        # Height must be persisted
        height = edb.components.get_solder_ball_height("U1")
        assert isinstance(height, float)
        assert height == pytest.approx(sball_height, rel=1e-3), f"Expected height {sball_height}, got {height}"

        # Shape must be cylinder (default)
        assert comp.solder_ball_shape == "cylinder"

        # Diameter must be persisted
        diam_result = comp.solder_ball_diameter
        assert diam_result is not None, "solder_ball_diameter should not be None after set_solder_ball"
        top_diam = float(diam_result[0])
        assert top_diam == pytest.approx(sball_diam, rel=1e-3), f"Expected diameter {sball_diam}, got {top_diam}"

        # IC die type must be set to flipchip
        die_props = comp.ic_die_properties
        assert die_props is not None, "ic_die_properties should be available for IC component"
        assert die_props.die_type == "flipchip", f"Expected die_type 'flipchip', got '{die_props.die_type}'"

        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_aedt_pin_name(self):
        """get_aedt_pin_name returns a string AEDT pin name."""
        edb = self.edb_examples.get_si_verse()
        pin = list(edb.components.instances["R1"].pins.values())[0]
        name = edb.components.get_aedt_pin_name(pin)
        assert isinstance(name, str)
        assert len(name) > 0
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_disable_rlc_component(self):
        """disable_rlc_component disables an RLC component model."""
        edb = self.edb_examples.get_si_verse()
        assert edb.components.disable_rlc_component("C1")
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_create_component_no_rlc(self):
        """create() can create a non-RLC component (OTHER type)."""
        edb = self.edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("C5")
        comp = edb.components.create(pins, "NonRlcComp")
        assert comp is not False
        assert comp.name == "NonRlcComp"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_create_component_rlc_with_part_name(self):
        """create() with component_part_name uses _get_component_definition."""
        edb = self.edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("R13")
        comp = edb.components.create(
            pins, "TestRlcPartName", component_part_name="TestRlcPart", is_rlc=True, r_value=47.0
        )
        assert comp is not False
        assert comp.name == "TestRlcPartName"
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_get_pins_name_from_net_no_pin_list(self):
        """get_pins_name_from_net without explicit pin_list searches all components."""
        edb = self.edb_examples.get_si_verse()
        names = edb.components.get_pins_name_from_net("GND")
        assert isinstance(names, list)
        assert len(names) > 0
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")
    def test_grpc_delete_single_pin_rlc_deactivate(self):
        """delete_single_pin_rlc with deactivate_only=True disables components."""
        edb = self.edb_examples.get_si_verse()
        result = edb.components.delete_single_pin_rlc(deactivate_only=True)
        # Returns empty list in deactivate mode
        assert result == []
        edb.close(terminate_rpc_session=False)

    def test_create_rlc_component(self):
        """Create RLC components from pins."""
        edb = self.edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.components.create([pins[0], ref_pins[0]], "test_0rlc", r_value=1.67, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_1rlc", r_value=None, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_2rlc", r_value=None, c_value=1e-13)
        edb.close(terminate_rpc_session=False)
