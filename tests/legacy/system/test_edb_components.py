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

"""Tests related to Edb components
"""
import math
import os

import pytest

# from pyedb import Edb
from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]

bom_example = "bom_example.csv"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_components_get_pin_from_component(self):
        """Evaluate access to a pin from a component."""
        comp = self.edbapp.components.get_component_by_name("J1")
        assert comp is not None
        pin = self.edbapp.components.get_pin_from_component("J1", pinName="1")
        assert pin is not False

    def test_components_create_coax_port_on_component(self):
        """Create a coaxial port on a component from its pin."""
        coax_port = self.edbapp.components["U6"].pins["R3"].create_coax_port("coax_port")
        coax_port.radial_extent_factor = 3
        assert coax_port.radial_extent_factor == 3
        assert coax_port.component
        assert self.edbapp.components["U6"].pins["R3"].get_terminal()
        assert self.edbapp.components["U6"].pins["R3"].id
        assert self.edbapp.terminals
        assert self.edbapp.ports
        assert self.edbapp.components["U6"].pins["R3"].get_connected_objects()

    def test_components_properties(self):
        """Access components properties."""
        assert len(self.edbapp.components.components) > 2
        assert len(self.edbapp.components.inductors) > 0
        assert len(self.edbapp.components.resistors) > 0
        assert len(self.edbapp.components.capacitors) > 0
        assert len(self.edbapp.components.ICs) > 0
        assert len(self.edbapp.components.IOs) > 0
        assert len(self.edbapp.components.Others) > 0

    def test_components_rlc_components_values(self):
        """Update values of an RLC component."""
        assert self.edbapp.components.set_component_rlc("C1", res_value=1e-3, cap_value="10e-6", isparallel=False)
        assert self.edbapp.components.set_component_rlc("L10", res_value=1e-3, ind_value="10e-6", isparallel=True)

    def test_components_R1_queries(self):
        """Evaluate queries over component R1."""
        assert "R1" in list(self.edbapp.components.components.keys())
        assert not self.edbapp.components.components["R1"].is_null
        assert self.edbapp.components.components["R1"].res_value
        assert self.edbapp.components.components["R1"].placement_layer
        assert self.edbapp.components.components["R1"].component_def
        assert self.edbapp.components.components["R1"].location
        assert isinstance(self.edbapp.components.components["R1"].lower_elevation, float)
        assert isinstance(self.edbapp.components.components["R1"].upper_elevation, float)
        assert self.edbapp.components.components["R1"].top_bottom_association == 2
        assert self.edbapp.components.components["R1"].pinlist
        assert self.edbapp.components.components["R1"].pins
        assert self.edbapp.components.components["R1"].pins["1"].pin_number
        assert self.edbapp.components.components["R1"].pins["1"].component_pin

        assert self.edbapp.components.components["R1"].pins["1"].component
        assert (
            self.edbapp.components.components["R1"].pins["1"].lower_elevation
            == self.edbapp.components.components["R1"].lower_elevation
        )
        assert (
            self.edbapp.components.components["R1"].pins["1"].placement_layer
            == self.edbapp.components.components["R1"].placement_layer
        )
        assert (
            self.edbapp.components.components["R1"].pins["1"].upper_elevation
            == self.edbapp.components.components["R1"].upper_elevation
        )
        assert (
            self.edbapp.components.components["R1"].pins["1"].top_bottom_association
            == self.edbapp.components.components["R1"].top_bottom_association
        )
        assert self.edbapp.components.components["R1"].pins["1"].position
        assert self.edbapp.components.components["R1"].pins["1"].rotation

    def test_components_create_clearance_on_component(self):
        """Evaluate the creation of a clearance on soldermask."""
        comp = self.edbapp.components.components["U1"]
        assert comp.create_clearance_on_component()

    def test_components_get_components_from_nets(self):
        """Access to components from nets."""
        assert self.edbapp.components.get_components_from_nets("DDR4_DQS0_P")

    def test_components_resistors(self):
        """Evaluate the components resistors."""
        assert "R1" in list(self.edbapp.components.resistors.keys())
        assert "C1" not in list(self.edbapp.components.resistors.keys())

    def test_components_capacitors(self):
        """Evaluate the components capacitors."""
        assert "C1" in list(self.edbapp.components.capacitors.keys())
        assert "R1" not in list(self.edbapp.components.capacitors.keys())

    def test_components_inductors(self):
        """Evaluate the components inductors."""
        assert "L10" in list(self.edbapp.components.inductors.keys())
        assert "R1" not in list(self.edbapp.components.inductors.keys())

    def test_components_integrated_circuits(self):
        """Evaluate the components integrated circuits."""
        assert "U1" in list(self.edbapp.components.ICs.keys())
        assert "R1" not in list(self.edbapp.components.ICs.keys())

    def test_components_inputs_outputs(self):
        """Evaluate the components inputs and outputs."""
        assert "X1" in list(self.edbapp.components.IOs.keys())
        assert "R1" not in list(self.edbapp.components.IOs.keys())

    def test_components_others(self):
        """Evaluate the components other core components."""
        assert "B1" in self.edbapp.components.Others
        assert "R1" not in self.edbapp.components.Others

    def test_components_components_by_partname(self):
        """Evaluate the components by partname"""
        comp = self.edbapp.components.components_by_partname
        assert "ALTR-FBGA24_A-130" in comp
        assert len(comp["ALTR-FBGA24_A-130"]) == 1

    def test_components_get_through_resistor_list(self):
        """Evaluate the components retrieve through resistors."""
        assert self.edbapp.components.get_through_resistor_list(10)

    def test_components_get_rats(self):
        """Retrieve a list of dictionaries of the reference designator, pin names, and net names."""
        assert len(self.edbapp.components.get_rats()) > 0

    def test_components_get_component_net_connections_info(self):
        """Evaluate net connection information."""
        assert len(self.edbapp.components.get_component_net_connection_info("U1")) > 0

    def test_components_get_pin_name_and_position(self):
        """Retrieve components name and position."""
        cmp_pinlist = self.edbapp.padstacks.get_pinlist_from_component_and_net("U6", "GND")
        pin_name = self.edbapp.components.get_aedt_pin_name(cmp_pinlist[0])
        assert type(pin_name) is str
        assert len(pin_name) > 0
        assert len(cmp_pinlist[0].position) == 2
        assert len(self.edbapp.components.get_pin_position(cmp_pinlist[0])) == 2

    def test_components_get_pins_name_from_net(self):
        """Retrieve pins belonging to a net."""
        cmp_pinlist = self.edbapp.components.get_pin_from_component("U6")
        assert len(self.edbapp.components.get_pins_name_from_net("GND", cmp_pinlist)) > 0
        assert len(self.edbapp.components.get_pins_name_from_net("5V", cmp_pinlist)) == 0

    def test_components_delete_single_pin_rlc(self):
        """Delete all RLC components with a single pin."""
        assert len(self.edbapp.components.delete_single_pin_rlc()) == 0

    def test_components_set_component_rlc(self):
        """Update values for an RLC component."""
        assert self.edbapp.components.set_component_rlc("R1", 30, 1e-9, 1e-12)

    def test_components_disable_rlc_component(self):
        """Disable a RLC component."""
        assert self.edbapp.components.disable_rlc_component("R1")

    def test_components_delete(self):
        """Delete a component."""
        assert self.edbapp.components.delete("R1")

    def test_components_set_model(self):
        """Assign component model."""
        assert self.edbapp.components.set_component_model(
            "C10",
            modelpath=os.path.join(
                local_path,
                "example_models",
                test_subfolder,
                "GRM32ER72A225KA35_25C_0V.sp",
            ),
            modelname="GRM32ER72A225KA35_25C_0V",
        )
        assert not self.edbapp.components.set_component_model(
            "C100000",
            modelpath=os.path.join(
                local_path,
                test_subfolder,
                "GRM32ER72A225KA35_25C_0V.sp",
            ),
            modelname="GRM32ER72A225KA35_25C_0V",
        )

    def test_modeler_parametrize_layout(self):
        """Parametrize a polygon"""
        assert len(self.edbapp.modeler.polygons) > 0
        for el in self.edbapp.modeler.polygons:
            if el.GetId() == 5953:
                poly = el
        for el in self.edbapp.modeler.polygons:
            if el.GetId() == 5954:
                selection_poly = el
        assert self.edbapp.modeler.parametrize_polygon(poly, selection_poly)

    def test_components_update_from_bom(self):
        """Update components with values coming from a BOM file."""
        assert self.edbapp.components.update_rlc_from_bom(
            os.path.join(local_path, "example_models", test_subfolder, bom_example),
            delimiter=",",
            valuefield="Value",
            comptype="Prod name",
            refdes="RefDes",
        )
        assert not self.edbapp.components.components["R2"].is_enabled
        self.edbapp.components.components["R2"].is_enabled = True
        assert self.edbapp.components.components["R2"].is_enabled

    def test_components_export_bom(self):
        """Export Bom file from layout."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_bom.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        edbapp.components.import_bom(os.path.join(local_path, "example_models", test_subfolder, "bom_example_2.csv"))
        assert not edbapp.components.instances["R2"].is_enabled
        assert edbapp.components.instances["U13"].partname == "SLAB-QFN-24-2550x2550TP_V"

        export_bom_path = os.path.join(self.local_scratch.path, "export_bom.csv")
        assert edbapp.components.export_bom(export_bom_path)
        edbapp.close()

    def test_components_create_component_from_pins(self):
        """Create a component from a pin."""
        pins = self.edbapp.components.get_pin_from_component("R13")
        component = self.edbapp.components.create(pins, "newcomp")
        assert component
        assert component.part_name == "newcomp"
        assert len(component.pins) == 2

    def test_convert_resistor_value(self):
        """Convert a resistor value."""
        from pyedb.dotnet.edb_core.components import resistor_value_parser

        assert resistor_value_parser("100meg")

    def test_components_create_solder_ball_on_component(self):
        """Set cylindrical solder balls on a given component"""
        assert self.edbapp.components.set_solder_ball("U1", shape="Spheroid")
        assert self.edbapp.components.set_solder_ball("U6", sball_height=None)
        assert self.edbapp.components.set_solder_ball(
            "U6", sball_height="100um", auto_reference_size=False, chip_orientation="chip_up"
        )

    def test_components_short_component(self):
        """Short pins of component with a trace."""
        assert self.edbapp.components.short_component_pins("U12", width=0.2e-3)
        assert self.edbapp.components.short_component_pins("U10", ["2", "5"])

    def test_components_type(self):
        """Retrieve components type."""
        comp = self.edbapp.components["R4"]
        comp.type = "Resistor"
        assert comp.type == "Resistor"
        comp.type = "Inductor"
        assert comp.type == "Inductor"
        comp.type = "Capacitor"
        assert comp.type == "Capacitor"
        comp.type = "IO"
        assert comp.type == "IO"
        comp.type = "IC"
        assert comp.type == "IC"
        comp.type = "Other"
        assert comp.type == "Other"

    def test_componenets_deactivate_rlc(self):
        """Deactivate RLC component and convert to a circuit port."""
        assert self.edbapp.components.deactivate_rlc_component(component="C1", create_circuit_port=False)
        assert self.edbapp.ports["C1"]
        assert self.edbapp.components["C1"].is_enabled is False
        assert self.edbapp.components.deactivate_rlc_component(component="C2", create_circuit_port=True)
        self.edbapp.components["C2"].is_enabled = False
        assert self.edbapp.components["C2"].is_enabled is False
        self.edbapp.components["C2"].is_enabled = True
        assert self.edbapp.components["C2"].is_enabled is True
        pins = [*self.edbapp.components.components["L10"].pins.values()]
        self.edbapp.components.create_port_on_pins("L10", pins[0], pins[1])
        assert self.edbapp.components["L10"].is_enabled is False
        assert "L10" in self.edbapp.ports.keys()

    def test_components_definitions(self):
        """Evaluate components definition."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0126.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        assert edbapp.components.components
        assert edbapp.components.definitions
        comp_def = edbapp.components.definitions["CAPC2012X12N"]
        assert comp_def
        comp_def.part_name = "CAPC2012X12N_new"
        assert comp_def.part_name == "CAPC2012X12N_new"
        assert len(comp_def.components) > 0
        cap = edbapp.components.definitions["CAPC2012X12N_new"]
        assert cap.type == "Capacitor"
        cap.type = "Resistor"
        assert cap.type == "Resistor"

        export_path = os.path.join(self.local_scratch.path, "comp_definition.csv")
        assert edbapp.components.export_definition(export_path)
        assert edbapp.components.import_definition(export_path)

        assert edbapp.components.definitions["CAPC3216X180X20ML20"].assign_rlc_model(1, 2, 3)
        sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
        assert edbapp.components.definitions["CAPC3216X180X55ML20T25"].assign_s_param_model(sparam_path)
        ref_file = edbapp.components.definitions["CAPC3216X180X55ML20T25"].reference_file
        assert ref_file
        spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")
        assert edbapp.components.definitions["CAPMP7343X31N"].assign_spice_model(spice_path)
        edbapp.close()

    def test_rlc_component_values_getter_setter(self):
        """Evaluate component values getter and setter."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0136.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
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
        edbapp.close()

    def test_create_port_on_pin(self):
        """Create port on pins."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0134b.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        pin = "A24"
        ref_pins = [pin for pin in list(edbapp.components["U1"].pins.values()) if pin.net_name == "GND"]
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=pin, reference_pins=ref_pins)
        assert edbapp.components.create_port_on_pins(refdes="U1", pins="C1", reference_pins=["A11"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins="C2", reference_pins=["A11"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=["A24"], reference_pins=["A11", "A16"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=["A26"], reference_pins=["A11", "A16", "A17"])
        assert edbapp.components.create_port_on_pins(refdes="U1", pins=["A28"], reference_pins=["A11", "A16"])
        edbapp.close()

    def test_replace_rlc_by_gap_boundaries(self):
        """Replace RLC component by RLC gap boundaries."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_boundaries.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        for refdes, cmp in edbapp.components.components.items():
            edbapp.components.replace_rlc_by_gap_boundaries(refdes)
        rlc_list = [
            term for term in list(edbapp.active_layout.Terminals) if str(term.GetBoundaryType()) == "RlcBoundary"
        ]
        assert len(rlc_list) == 944
        edbapp.close()

    def test_components_get_component_placement_vector(self):
        """Get the placement vector between 2 components."""
        edb2 = Edb(self.target_path4, edbversion=desktop_version)
        for _, cmp in edb2.components.instances.items():
            assert isinstance(cmp.solder_ball_placement, int)
        mounted_cmp = edb2.components.get_component_by_name("BGA")._edb_object
        hosting_cmp = self.edbapp.components.get_component_by_name("U1")._edb_object
        (
            result,
            vector,
            rotation,
            solder_ball_height,
        ) = self.edbapp.components.get_component_placement_vector(
            mounted_component=mounted_cmp,
            hosting_component=hosting_cmp,
            mounted_component_pin1="A10",
            mounted_component_pin2="A12",
            hosting_component_pin1="A2",
            hosting_component_pin2="A4",
        )
        assert result
        assert abs(abs(rotation) - math.pi / 2) < 1e-9
        assert solder_ball_height == 0.00033
        assert len(vector) == 2
        (
            result,
            vector,
            rotation,
            solder_ball_height,
        ) = self.edbapp.components.get_component_placement_vector(
            mounted_component=mounted_cmp,
            hosting_component=hosting_cmp,
            mounted_component_pin1="A10",
            mounted_component_pin2="A12",
            hosting_component_pin1="A2",
            hosting_component_pin2="A4",
            flipped=True,
        )
        assert result
        assert abs(rotation + math.pi / 2) < 1e-9
        assert solder_ball_height == 0.00033
        assert len(vector) == 2
        edb2.close()

    def test_components_assign(self):
        """Assign RLC model, S-parameter model and spice model."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_17.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
        spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")

        edbapp = Edb(target_path, edbversion=desktop_version)
        comp = edbapp.components.instances["R2"]
        assert not comp.assign_rlc_model()
        comp.assign_rlc_model(1, None, 3, False)
        assert (
            not comp.is_parallel_rlc
            and float(comp.res_value) == 1
            and float(comp.ind_value) == 0
            and float(comp.cap_value) == 3
        )
        comp.assign_rlc_model(1, 2, 3, True)
        assert comp.is_parallel_rlc
        assert (
            comp.is_parallel_rlc
            and float(comp.res_value) == 1
            and float(comp.ind_value) == 2
            and float(comp.cap_value) == 3
        )
        assert comp.value
        assert not comp.spice_model and not comp.s_param_model and not comp.netlist_model
        assert comp.assign_s_param_model(sparam_path) and comp.value
        assert comp.s_param_model
        assert edbapp.components.nport_comp_definition
        assert comp.assign_spice_model(spice_path) and comp.value
        assert comp.spice_model
        comp.type = "Inductor"
        comp.value = 10  # This command set the model back to ideal RLC
        assert comp.type == "Inductor" and comp.value == 10 and float(comp.ind_value) == 10
        edbapp.close()

    def test_components_bounding_box(self):
        """Get component's bounding box."""
        target_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        out_edb = os.path.join(self.local_scratch.path, "get_comp_bbox.aedb")
        self.local_scratch.copyfolder(target_path, out_edb)
        edbapp = Edb(out_edb, edbversion=desktop_version)
        component = edbapp.components.instances["U1"]
        assert component.bounding_box
        assert isinstance(component.rotation, float)
        edbapp.close()

    def test_pec_boundary_ports(self):
        """Check pec boundary ports."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_custom_sball_height", "ANSYS-HSD_V1.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        edbapp.components.create_port_on_pins(refdes="U1", pins="AU38", reference_pins="AU37", pec_boundary=True)
        assert edbapp.terminals["Port_GND_U1-AU38"].boundary_type == "PecBoundary"
        assert edbapp.terminals["Port_GND_U1-AU38_ref"].boundary_type == "PecBoundary"
        edbapp.components.deactivate_rlc_component(component="C5", create_circuit_port=True, pec_boundary=True)
        edbapp.components.add_port_on_rlc_component(component="C65", circuit_ports=False, pec_boundary=True)
        assert edbapp.terminals["C5"].boundary_type == "PecBoundary"
        assert edbapp.terminals["C65"].boundary_type == "PecBoundary"

    def test_is_top_mounted(self):
        """Check is_top_mounted property."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_is_top_property", "test.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, desktop_version)
        assert edbapp.components.instances["U1"].is_top_mounted
        assert not edbapp.components.instances["C347"].is_top_mounted
        assert not edbapp.components.instances["R67"].is_top_mounted
        edbapp.close_edb()

    def test_instances(self):
        """Check instances access and values."""
        example_folder = os.path.join(local_path, "example_models", test_subfolder)
        source_path_edb = os.path.join(example_folder, "ANSYS-HSD_V1.aedb")
        target_path_edb = os.path.join(self.local_scratch.path, "test_component", "test.aedb")
        self.local_scratch.copyfolder(source_path_edb, target_path_edb)
        edbapp = Edb(target_path_edb, desktop_version)
        comp_pins = edbapp.components.instances["U1"].pins
        pins = [comp_pins["AM38"], comp_pins["AL37"]]
        edbapp.components.create(
            component_part_name="Test_part", component_name="Test", is_rlc=True, r_value=12.2, pins=pins
        )
        assert edbapp.components.instances["Test"]
        assert edbapp.components.instances["Test"].res_value == str(12.2)
        assert edbapp.components.instances["Test"].ind_value == "0"
        assert edbapp.components.instances["Test"].cap_value == "0"
        assert edbapp.components.instances["Test"].center == [0.06800000116, 0.01649999875]
        edbapp.close_edb()

    def test_create_package_def(self):
        """Check the creation of package definition."""
        assert self.edbapp.components["C200"].create_package_def(component_part_name="SMTC-MECT-110-01-M-D-RA1_V")
        assert not self.edbapp.components["C200"].create_package_def()
        assert self.edbapp.components["C200"].package_def.name == "C200_CAPC3216X180X55ML20T25"

    def test_solder_ball_getter_setter(self):
        cmp = self.edbapp.components["X1"]
        cmp.solder_ball_height = 0.0
        assert cmp.solder_ball_height == 0.0
        cmp.solder_ball_height = "100um"
        assert cmp.solder_ball_height == 100e-6
        assert cmp.solder_ball_shape
        cmp.solder_ball_shape = "Cylinder"
        assert cmp.solder_ball_shape == "Cylinder"
        cmp.solder_ball_shape = 0
        assert cmp.solder_ball_shape == "None"
        cmp.solder_ball_shape = 1
        assert cmp.solder_ball_shape == "Cylinder"
        cmp.solder_ball_shape = "Spheroid"
        assert cmp.solder_ball_shape == "Spheroid"
        cmp.solder_ball_shape = "Cylinder"
        cmp.solder_ball_shape = 2
        assert cmp.solder_ball_shape == "Spheroid"
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
        edbapp = edb_examples.get_si_verse()
        assert edbapp.components.create_pingroup_from_pins([*edbapp.components.components["Q1"].pins.values()])
        assert edbapp.components._create_pin_group_terminal(edbapp.padstacks.pingroups[0], term_type="circuit")
        edbapp.close()

    def test_component_lib(self):
        edbapp = Edb()
        comp_lib = edbapp.components.get_vendor_libraries()
        assert len(comp_lib.capacitors) == 13
        assert len(comp_lib.inductors) == 7
        network = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].s_parameters
        assert network
        assert network.frequency.npoints == 400
        network.write_touchstone(os.path.join(edbapp.directory, "test_export.s2p"))
        assert os.path.isfile(os.path.join(edbapp.directory, "test_export.s2p"))

    def test_export_gds_comp_xml(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        xml_output = os.path.join(self.local_scratch.path,'test.xml')
        assert edbapp.export_gds_comp_xml(['U1', 'U2', 'C2', 'R1'],
                                          control_path=xml_output)
        assert os.path.isfile(xml_output)
        edbapp.close()
