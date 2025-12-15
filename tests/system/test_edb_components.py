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

"""Tests related to Edb components"""

import math
import os

import pytest

from tests.conftest import local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]

bom_example = "bom_example.csv"


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_components_get_pin_from_component(self, edb_examples):
        """Evaluate access to a pin from a component."""
        edb = edb_examples.get_si_verse()
        comp = edb.components.get_component_by_name("J1")
        assert comp is not None
        pin = edb.components.get_pin_from_component("J1", pin_name="1")
        # TODO check if we agree to return aedt_name when it's a layout pin.
        assert pin[0].name == "1"
        edb.close(terminate_rpc_session=False)

    def test_components_create_coax_port_on_component(self, edb_examples):
        """Create a coaxial port on a component from its pin."""
        # Done
        edb = edb_examples.get_si_verse()
        coax_port = edb.components["U6"].pins["R3"].create_coax_port("coax_port")
        coax_port.radial_extent_factor = 3
        assert coax_port.radial_extent_factor == 3
        assert coax_port.component
        assert edb.components["U6"].pins["R3"].get_terminal()
        assert edb.components["U6"].pins["R3"].id
        assert edb.terminals
        assert edb.ports
        # TODO check with grpc it was only 1 object returned. Check for bug fixed.
        if edb.grpc:
            assert len(edb.components["U6"].pins["R3"].get_connected_objects()) == 1
        else:
            assert len(edb.components["U6"].pins["R3"].get_connected_objects()) == 17
        edb.close(terminate_rpc_session=False)

    def test_components_properties(self, edb_examples):
        """Access components properties."""
        # Done
        edb = edb_examples.get_si_verse()
        assert len(edb.components.instances) > 2
        assert len(edb.components.inductors) > 0
        assert len(edb.components.resistors) > 0
        assert len(edb.components.capacitors) > 0
        assert len(edb.components.ICs) > 0
        assert len(edb.components.IOs) > 0
        assert len(edb.components.Others) > 0
        edb.close(terminate_rpc_session=False)

    def test_components_rlc_components_values(self, edb_examples):
        """Update values of an RLC component."""
        # Done
        edb = edb_examples.get_si_verse()
        assert edb.components.set_component_rlc("C1", res_value=0.1, cap_value="5e-6", ind_value=1e-9, isparallel=False)
        component = edb.components.instances["C1"]
        assert component.rlc_values == [0.1, 1e-9, 5e-6]
        assert edb.components.set_component_rlc("L10", res_value=1e-3, ind_value="10e-6", isparallel=True)
        component = edb.components.instances["L10"]
        assert component.rlc_values == [1e-3, 10e-6, 0.0]
        edb.close(terminate_rpc_session=False)

    def test_components_r1_queries(self, edb_examples):
        """Evaluate queries over component R1."""
        # Done
        edb = edb_examples.get_si_verse()
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

    def test_components_create_clearance_on_component(self, edb_examples):
        """Evaluate the creation of a clearance on soldermask."""
        # Done
        edb = edb_examples.get_si_verse()
        comp = edb.components.instances["U1"]
        assert comp.create_clearance_on_component()
        edb.close(terminate_rpc_session=False)

    def test_components_get_components_from_nets(self, edb_examples):
        """Access to components from nets."""
        # Done
        edb = edb_examples.get_si_verse()
        assert edb.components.get_components_from_nets("DDR4_DQS0_P")
        edb.close(terminate_rpc_session=False)

    def test_components_resistors(self, edb_examples):
        """Evaluate component resistors."""
        # Done
        edb = edb_examples.get_si_verse()
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

    def test_components_get_pin_name_and_position(self, edb_examples):
        """Retrieve component name and position."""
        # Done
        edb = edb_examples.get_si_verse()
        cmp_pinlist = edb.padstacks.get_pinlist_from_component_and_net("U6", "GND")
        pin_name = edb.components.get_aedt_pin_name(cmp_pinlist[0])
        assert type(pin_name) is str
        assert len(pin_name) > 0
        assert len(cmp_pinlist[0].position) == 2
        assert len(edb.components.get_pin_position(cmp_pinlist[0])) == 2
        edb.close(terminate_rpc_session=False)

    def test_components_get_pins_name_from_net(self, edb_examples):
        """Retrieve pins belonging to a net."""
        # Done
        edb = edb_examples.get_si_verse()
        cmp_pinlist = edb.components.get_pin_from_component("U6")
        assert len(edb.components.get_pins_name_from_net("GND", cmp_pinlist)) > 0
        assert len(edb.components.get_pins_name_from_net("5V", cmp_pinlist)) == 0
        edb.close(terminate_rpc_session=False)

    def test_components_delete_single_pin_rlc(self, edb_examples):
        """Delete all RLC components with a single pin."""
        edb = edb_examples.get_si_verse()
        assert len(edb.components.delete_single_pin_rlc()) == 0
        edb.close(terminate_rpc_session=False)

    def test_components_set_component_rlc(self, edb_examples):
        """Update values for an RLC component."""
        # Done
        edb = edb_examples.get_si_verse()
        assert edb.components.set_component_rlc("R1", 30, 1e-9, 1e-12)
        assert edb.components.disable_rlc_component("R1")
        assert edb.components.delete("R1")
        edb.close(terminate_rpc_session=False)

    def test_components_set_model(self, edb_examples):
        """Assign component model."""
        # Done
        edb = edb_examples.get_si_verse()
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
        assert not edb.components.set_component_model(
            "C100000",
            modelpath=os.path.join(
                local_path,
                test_subfolder,
                "GRM32ER72A225KA35_25C_0V.sp",
            ),
            modelname="GRM32ER72A225KA35_25C_0V",
        )
        edb.close(terminate_rpc_session=False)

    def test_modeler_parametrize_layout(self, edb_examples):
        """Parametrize a polygon"""
        # Done
        edb = edb_examples.get_si_verse()
        assert len(edb.modeler.polygons) > 0
        for el in edb.modeler.polygons:
            if edb.grpc:
                # TODO check enhancement request #550 status to remove this condition.
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

    def test_components_update_from_bom(self, edb_examples):
        """Update components with values coming from a BOM file."""
        # Done
        edb = edb_examples.get_si_verse()
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

    def test_components_export_bom(self, edb_examples):
        """Export Bom file from layout."""
        edb = edb_examples.get_si_verse()
        edb.components.import_bom(os.path.join(local_path, "example_models", test_subfolder, "bom_example_2.csv"))
        assert not edb.components.instances["R2"].enabled
        assert edb.components.instances["U13"].partname == "SLAB-QFN-24-2550x2550TP_V"

        export_bom_path = os.path.join(self.local_scratch.path, "export_bom.csv")
        assert edb.components.export_bom(export_bom_path)
        edb.close(terminate_rpc_session=False)

    def test_components_create_component_from_pins(self, edb_examples):
        """Create a component from a pin."""
        edb = edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("R13")
        component = edb.components.create(pins, "newcomp")
        assert component
        assert component.part_name == "newcomp"
        assert len(component.pins) == 2
        edb.close(terminate_rpc_session=False)

    def test_convert_resistor_value(self):
        """Convert a resistor value."""
        from pyedb.dotnet.database.components import resistor_value_parser

        assert resistor_value_parser("100meg")

    def test_components_create_solder_ball_on_component(self, edb_examples):
        """Set cylindrical solder balls on a given component"""
        # Done
        edb = edb_examples.get_si_verse()
        assert edb.components.set_solder_ball("U1", shape="Spheroid")
        assert edb.components.set_solder_ball("U6", sball_height=None)
        assert edb.components.set_solder_ball(
            "U6", sball_height="100um", auto_reference_size=False, chip_orientation="chip_up"
        )
        edb.close(terminate_rpc_session=False)

    def test_components_short_component(self, edb_examples):
        """Short pins of component with a trace."""
        # Done
        edb = edb_examples.get_si_verse()
        assert edb.components.short_component_pins("U12", width=0.2e-3)
        assert edb.components.short_component_pins("U10", ["2", "5"])
        edb.close(terminate_rpc_session=False)

    def test_components_type(self, edb_examples):
        """Retrieve components type."""
        # TODO adding lower on getter since DotNet is returning Capital letter for the first one.
        edb = edb_examples.get_si_verse()
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

    def test_componenets_deactivate_rlc(self, edb_examples):
        """Deactivate RLC component and convert to a circuit port."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.components.deactivate_rlc_component(component="C1", create_circuit_port=False)
        assert edbapp.ports["C1"]
        assert edbapp.components["C1"].is_enabled is False
        assert edbapp.components.deactivate_rlc_component(component="C2", create_circuit_port=True)
        edbapp.components["C2"].is_enabled = False
        assert edbapp.components["C2"].is_enabled is False
        edbapp.components["C2"].is_enabled = True
        assert edbapp.components["C2"].is_enabled is True
        pins = [*edbapp.components.instances["L10"].pins.values()]
        edbapp.components.create_port_on_pins("L10", pins[0], pins[1])
        assert edbapp.components["L10"].is_enabled is False
        assert "L10" in edbapp.ports.keys()

    def test_components_definitions(self, edb_examples):
        """Evaluate components definition."""
        edbapp = edb_examples.get_si_verse()
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

        export_path = os.path.join(self.local_scratch.path, "comp_definition.csv")
        # TODO check config file 2.0
        # assert edbapp.components.export_definition(export_path)
        # assert edbapp.components.import_definition(export_path)

        # assert edbapp.components.definitions["CAPC3216X180X20ML20"].assign_rlc_model(1, 2, 3)
        # sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
        # assert edbapp.components.definitions["CAPC3216X180X55ML20T25"].assign_s_param_model(sparam_path)
        # ref_file = edbapp.components.definitions["CAPC3216X180X55ML20T25"].reference_file
        # assert ref_file
        # spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")
        # assert edbapp.components.definitions["CAPMP7343X31N"].assign_spice_model(spice_path)
        edbapp.close(terminate_rpc_session=False)

    def test_rlc_component_values_getter_setter(self, edb_examples):
        """Evaluate component values getter and setter."""
        # Done
        edbapp = edb_examples.get_si_verse()
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

    def test_create_port_on_pin(self, edb_examples):
        """Create port on pins."""
        # Done
        edbapp = edb_examples.get_si_verse()
        pin = "A24"
        ref_pins = [pin for pin in list(edbapp.components["U1"].pins.values()) if pin.net_name == "GND"]
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=pin, reference_pins=ref_pins)
        assert edbapp.components.create_port_on_pins(refdes="U1", pins="C1", reference_pins=["A11"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins="C2", reference_pins=["A11"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=["A24"], reference_pins=["A11", "A16"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=["A26"], reference_pins=["A11", "A16", "A17"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=["A28"], reference_pins=["A11", "A16"])
        edbapp.close(terminate_rpc_session=False)

    def test_replace_rlc_by_gap_boundaries(self, edb_examples):
        """Replace RLC component by RLC gap boundaries."""
        # TODO check how we can return same boundary_type between grpc and dotnet.
        edbapp = edb_examples.get_si_verse()
        names = [i for i in edbapp.components.instances.keys()][::]
        for refdes in names:
            edbapp.components.replace_rlc_by_gap_boundaries(refdes)
        if edbapp.grpc:
            rlc_list = [term for term in list(edbapp.terminals.values()) if term.boundary_type == "rlc"]
        else:
            rlc_list = [term for term in list(edbapp.terminals.values()) if term.boundary_type == "RlcBoundary"]
        assert len(rlc_list) == 944
        edbapp.close(terminate_rpc_session=False)

    def test_components_get_component_placement_vector(self, edb_examples):
        """Get the placement vector between 2 components."""
        edbapp = edb_examples.get_si_verse()
        edb2 = edb_examples.load_edb(self.target_path4, copy_to_temp=False)
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

    def test_components_assign(self, edb_examples):
        """Assign RLC model, S-parameter model and spice model."""
        # Done
        edbapp = edb_examples.get_si_verse()
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
        edbapp.close(terminate_rpc_session=False)

    def test_components_bounding_box(self, edb_examples):
        """Get component's bounding box."""
        # Done
        edbapp = edb_examples.get_si_verse()
        component = edbapp.components.instances["U1"]
        assert component.bounding_box
        assert isinstance(component.rotation, float)
        edbapp.close(terminate_rpc_session=False)

    def test_pec_boundary_ports(self, edb_examples):
        """Check pec boundary ports."""
        # TODO check how we can return only pec in dotnet.
        edbapp = edb_examples.get_si_verse()
        edbapp.components.create_port_on_pins(refdes="U1", pins="AU38", reference_pins="AU37", pec_boundary=True)
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

    def test_is_top_mounted(self, edb_examples):
        """Check is_top_mounted property."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.components.instances["U1"].is_top_mounted
        assert not edbapp.components.instances["C347"].is_top_mounted
        assert not edbapp.components.instances["R67"].is_top_mounted
        edbapp.close_edb()

    def test_instances(self, edb_examples):
        """Check instances access and values."""
        # Done
        edbapp = edb_examples.get_si_verse()
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
            assert edbapp.components.instances["Test"].center == [0.07950000102, 0.03399999804]
        else:
            assert edbapp.components.instances["Test"].center == [0.068, 0.0165]
        edbapp.close_edb()

    def test_create_package_def(self, edb_examples):
        """Check the creation of package definition."""
        # Done
        edb = edb_examples.get_si_verse()
        assert edb.components["C200"].create_package_def(component_part_name="SMTC-MECT-110-01-M-D-RA1_V")
        assert not edb.components["C200"].create_package_def()
        assert edb.components["C200"].package_def.name == "C200_CAPC3216X180X55ML20T25"
        edb.close(terminate_rpc_session=False)

    def test_solder_ball_getter_setter(self, edb_examples):
        # Done
        edb = edb_examples.get_si_verse()
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
        assert round(diam1, 6) == 200e-6
        assert round(diam2, 6) == 200e-6
        cmp.solder_ball_diameter = ("100um", "100um")
        diam1, diam2 = cmp.solder_ball_diameter
        assert round(diam1, 6) == 100e-6
        assert round(diam2, 6) == 100e-6

    def test_create_pingroup_from_pins_types(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.components.create_pingroup_from_pins([*edbapp.components.instances["Q1"].pins.values()])
        assert edbapp.components._create_pin_group_terminal(edbapp.padstacks.pingroups[0], term_type="circuit")
        edbapp.close(terminate_rpc_session=False)

    def test_component_lib(self, edb_examples):
        # Done
        edbapp = edb_examples.create_empty_edb()
        comp_lib = edbapp.components.get_vendor_libraries()
        assert len(comp_lib.capacitors) == 13
        assert len(comp_lib.inductors) == 7
        network = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].s_parameters
        test_esr = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].esr
        test_esl = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].esl
        assert round(test_esr, 4) == 1.7552
        assert round(test_esl, 12) == 2.59e-10
        assert network
        assert network.frequency.npoints == 400
        network.write_touchstone(os.path.join(edbapp.edbpath, "test_export.s2p"))
        assert os.path.isfile(os.path.join(edbapp.edbpath, "test_export.s2p"))

    def test_properties(self, edb_examples):
        # TODO check with config file 2.0
        edbapp = edb_examples.get_si_verse()
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

    def test_ic_die_properties(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        component: Component = edbapp.components["U8"]
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
            assert ic_die_properties.die_type == "none"
            assert ic_die_properties.height == 0.0
            ic_die_properties.height = 1e-3
            assert ic_die_properties.height == 1e-3
        edbapp.close(terminate_rpc_session=False)

    def test_rlc_component_302(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        pins = edbapp.components.get_pin_from_component("C31")
        component = edbapp.components.create([pins[0], pins[1]], r_value=1.2, component_name="TEST", is_rlc=True)
        assert component
        assert component.name == "TEST"
        assert component.location == [0.13275000120000002, 0.07350000032]
        assert component.res_value == 1.2
        edbapp.close(terminate_rpc_session=False)

    def test_export_gds_comp_xml(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        xml_output = os.path.join(self.local_scratch.path, "test.xml")
        assert edbapp.export_gds_comp_xml(["U1", "U2", "C2", "R1"], control_path=xml_output)
        assert os.path.isfile(xml_output)
        edbapp.close(terminate_rpc_session=False)
