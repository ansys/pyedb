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

"""System tests for RF library components"""

import os

import pytest

from pyedb.rf_libraries.base_functions import (
    CPW,
    DifferentialTLine,
    HatchGround,
    InterdigitalCapacitor,
    RadialStub,
    RatRace,
    SpiralInductor,
)

pytestmark = [pytest.mark.system, pytest.mark.grpc]

ON_CI = os.environ.get("CI", "false").lower() == "true"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_cpw(self, edb_examples):
        edb = edb_examples.create_empty_edb()
        edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
        edb.materials.add_dielectric_material(name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        edb.stackup.add_layer(
            layer_name="METAL_BOT", material="gold", thickness="4um", layer_type="signal", fillMaterial="air"
        )
        edb.stackup.add_layer(
            layer_name="substrate",
            base_layer="METAL_BOT",
            material="silicon",
            thickness="100um",
            layer_type="dielectric",
        )
        edb.stackup.add_layer(
            layer_name="METAL_TOP",
            base_layer="substrate",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="SiO2",
        )

        cpw = CPW(
            edb_cell=edb,
            width=10e-6,
            gap=5e-6,
            layer="METAL_TOP",
            ground_net="GND",
            ground_layer="METAL_BOT",
            length=1e-3,
        )
        cpw.substrate.er = edb.materials["silicon"].permittivity
        cpw.substrate.h = 100e-6
        cpw.create()
        assert round(cpw.analytical_z0, 3) == 17.561
        assert cpw.gap == 5e-6
        assert cpw.ground_layer == "METAL_BOT"
        assert len(edb.modeler.rectangles) == 4
        assert edb.modeler.rectangles[0].net.name == "SIG"
        assert edb.modeler.rectangles[0].bbox == [-5e-06, 0.0, 5e-06, 0.001]
        assert edb.variables["g"] == 5e-06
        assert edb.variables["w"] == 1e-05
        edb.close()

    def test_diff_tline(self, edb_examples):
        edb = edb_examples.create_empty_edb()
        edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
        edb.materials.add_dielectric_material(name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        edb.stackup.add_layer(
            layer_name="METAL_BOT", material="gold", thickness="4um", layer_type="signal", fillMaterial="air"
        )
        edb.stackup.add_layer(
            layer_name="substrate",
            base_layer="METAL_BOT",
            material="silicon",
            thickness="100um",
            layer_type="dielectric",
        )
        edb.stackup.add_layer(
            layer_name="METAL_TOP",
            base_layer="substrate",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="air",
        )

        pair = DifferentialTLine(edb, layer="METAL_TOP", length=10e-3, width=0.2e-3, spacing=0.18e-3)
        pair.create()
        assert round(pair.diff_impedance, 3) == 95.723
        assert len(edb.modeler.paths) == 2
        assert edb.modeler.paths[0].net.name == "P"
        assert edb.modeler.paths[0].center_line == [[0.0, 0.0], [0.01, 0.0]]
        edb.close()

    def test_hatch_grounded(self, edb_examples):
        edb = edb_examples.create_empty_edb()
        edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
        edb.materials.add_dielectric_material(name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        edb.stackup.add_layer(
            layer_name="METAL_BOT", material="gold", thickness="4um", layer_type="signal", fillMaterial="air"
        )
        edb.stackup.add_layer(
            layer_name="substrate",
            base_layer="METAL_BOT",
            material="silicon",
            thickness="100um",
            layer_type="dielectric",
        )
        edb.stackup.add_layer(
            layer_name="METAL_TOP",
            base_layer="substrate",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="air",
        )

        hatch = HatchGround(
            edb_cell=edb, width=100e-6, pitch=225e-6, fill_target=50.0, layer_gnd="METAL_BOT", board_size=10e-3
        )
        hatch.create()
        assert round(hatch.copper_fill_ratio, 2) == 69.75
        assert hatch.board_size == 0.01
        assert edb.modeler.polygons[0].net.name == "GND"
        assert len(edb.modeler.polygons[0].arcs) == 356
        edb.close()

    def test_interdigited_capacitor(self, edb_examples):
        edb = edb_examples.create_empty_edb()
        edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
        edb.materials.add_dielectric_material(name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        edb.stackup.add_layer(
            layer_name="METAL_BOT", material="gold", thickness="4um", layer_type="signal", fillMaterial="air"
        )
        edb.stackup.add_layer(
            layer_name="substrate",
            base_layer="METAL_BOT",
            material="silicon",
            thickness="100um",
            layer_type="dielectric",
        )
        edb.stackup.add_layer(
            layer_name="METAL_TOP",
            base_layer="substrate",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="air",
        )

        idc = InterdigitalCapacitor(
            edb_cell=edb,
            fingers=12,
            finger_length="0.9mm",
            finger_width="0.08mm",
            gap="0.04mm",
            comb_gap="0.06mm",
            bus_width="0.25mm",
            layer="METAL_TOP",
            net_a="P1",
            net_b="P2",
        )
        idc.substrate.er = edb.materials["silicon"].permittivity
        idc.create()
        assert round(idc.capacitance_pf, 3) == 2.276
        assert len(edb.modeler.rectangles) == 26
        assert edb.modeler.rectangles[0].net.name == "P1"
        edb.close()

    def test_radial_stud(self, edb_examples):
        edb = edb_examples.create_empty_edb()
        edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
        edb.materials.add_dielectric_material(name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        edb.stackup.add_layer(
            layer_name="METAL_BOT", material="gold", thickness="4um", layer_type="signal", fillMaterial="air"
        )
        edb.stackup.add_layer(
            layer_name="substrate",
            base_layer="METAL_BOT",
            material="silicon",
            thickness="100um",
            layer_type="dielectric",
        )
        edb.stackup.add_layer(
            layer_name="METAL_TOP",
            base_layer="substrate",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="SiO2",
        )

        stub = RadialStub(edb, layer="METAL_TOP", width=200e-6, radius=1e-3)
        stub.create()
        assert round(stub.electrical_length_deg, 3) == 5.038
        assert edb.modeler.polygons[0].net.name == "RF"
        assert edb.modeler.rectangles[0].net.name == "RF"
        edb.close()

    def test_rat_race(self, edb_examples):
        edb = edb_examples.create_empty_edb()
        edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
        edb.materials.add_dielectric_material(name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        edb.stackup.add_layer(
            layer_name="METAL_BOT", material="gold", thickness="4um", layer_type="signal", fillMaterial="air"
        )
        edb.stackup.add_layer(
            layer_name="substrate",
            base_layer="METAL_BOT",
            material="silicon",
            thickness="100um",
            layer_type="dielectric",
        )
        edb.stackup.add_layer(
            layer_name="METAL_TOP",
            base_layer="substrate",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="air",
        )

        rat_race = RatRace(
            edb_cell=edb,
            z0=50,
            freq=10e9,
            layer="METAL_TOP",
            net="RR",
            width=0.2e-3,
            nr_segments=32,
            bottom_layer="METAL_BOT",
        )
        rat_race.substrate.er = edb.materials["silicon"].permittivity
        rat_race.create()
        assert round(rat_race.circumference, 3) == 0.013
        assert len(edb.modeler.paths) == 5
        assert edb.modeler.paths[0].net.name == "RR"
        edb.close()

    def test_spiral_inductor(self, edb_examples):
        edb = edb_examples.create_empty_edb()
        edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
        edb.materials.add_dielectric_material(name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01)
        edb.materials.add_dielectric_material(name="SiO2", permittivity=4, dielectric_loss_tangent=0)
        edb.materials.add_dielectric_material(name="air", permittivity=1, dielectric_loss_tangent=0)

        edb.stackup.add_layer(
            layer_name="METAL_BOT", material="gold", thickness="4um", layer_type="signal", fillMaterial="air"
        )
        edb.stackup.add_layer(
            layer_name="substrate",
            base_layer="METAL_BOT",
            material="silicon",
            thickness="100um",
            layer_type="dielectric",
        )
        edb.stackup.add_layer(
            layer_name="METAL_TOP",
            base_layer="substrate",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="SiO2",
        )
        edb.stackup.add_layer(
            layer_name="oxyde", base_layer="METAL_TOP", material="SiO2", thickness="4um", layer_type="dielectric"
        )
        edb.stackup.add_layer(
            layer_name="BRIDGE",
            base_layer="oxyde",
            material="gold",
            thickness="4um",
            layer_type="signal",
            fillMaterial="air",
        )
        edb.stackup.mode = "Overlapping"
        edb.stackup.add_layer(
            layer_name="via", material="gold", thickness="4um", layer_type="signal", base_layer="BRIDGE"
        )
        edb.stackup.layers["via"].lower_elevation = edb.stackup.layers["METAL_TOP"].upper_elevation
        spiral = SpiralInductor(
            edb_cell=edb, turns=10, layer="METAL_TOP", bridge_layer="BRIDGE", via_layer="via", ground_layer="METAL_BOT"
        )
        spiral.substrate.er = edb.materials["silicon"].permittivity
        spiral.substrate.h = 100e-6  # 100um
        assert round(spiral.inductance_nh, 3) == 59.599
        spiral.create()
        assert len(edb.modeler.rectangles) == 2
        assert len(edb.modeler.paths) == 2
        assert edb.modeler.paths[0].net.name == "IN"
        edb.close()
