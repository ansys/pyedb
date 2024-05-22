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


class Icepak:
    """SIwave Icepak."""

    def __init__(self, psiw):
        self._psiw = psiw

    def run(self, name, dc_simulation_name):
        """Run Icepak analysis.

        Parameters
        ----------
        name : str,
            Name of the Icepak simulation.
        dc_simulation_name: str
            Name of the dc simulation.

        Returns
        -------

        """
        self._psiw._logger.info("Running Icepak simulation.")
        flag = self._psiw.oproject.ScrRunIcepakSimulation(name, dc_simulation_name)
        return True if flag == 0 else False

    def set_meshing_detail(self, mesh_level=0):
        """Sets the meshing detail level for Icepak simulations.

        Parameters
        ----------
        mesh_level : int, optional
            Meshing level.

        Returns
        -------

        """
        flag = self._psiw.oproject.ScrSetIcepakMeshingDetail({0: "basic", 1: "detailed", 2: "exhaustive"}[mesh_level])
        return True if flag == 0 else False

    def set_board_outline_fidelity(self, fidelity=2):
        """Specifies the minimum edge length when modifying the board outline for export to Icepak. This
        minimum edge length is used when indiscretion arcs into a series of straight lines and when
        simplifying the outline to remove very small edges.

        Parameters
        ----------
        fidelity : int, float, optional
            Fidelity level in mm.

        Returns
        -------

        """
        flag = self._psiw.oproject.ScrSetIcepakBoardOutlineFidelity(fidelity)
        return True if flag == 0 else False

    def set_thermal_environment(
        self,
        convection=True,
        force_air=True,
        top_or_ambient_temperature=22,
        top_or_overall_flow_direction="+X",
        top_or_overall_flow_speed=2,
        bottom_temperature=22,
        bottom_flow_direction="+X",
        bottom_flow_speed=2,
        gravity_vector_x=0,
        gravity_vector_y=0,
        gravity_vector_z=9.8,
    ):
        """Sets the thermal environment settings to use for Icepak simulations.

        Parameters
        ----------
        convection : bool, optional
        force_air : bool, optional
        top_or_ambient_temperature: int, float, optional
            Temperature above PCB in degrees Celsius.
        top_or_overall_flow_direction : str, optional
            Flow direction above PCB.
        top_or_overall_flow_speed : int, float, optional
            Flow speed above PCB.
        bottom_temperature : int, float, optional
            Temperature below PCB in degrees Celsius.
        bottom_flow_direction : str, optional
            Flow direction below PCB.
        bottom_flow_speed : int, float, optional
            Flow speed below PCB.
        gravity_vector_x : int, float, optional
            Gravity vector x for natural convection.
        gravity_vector_y : int, float, optional
            Gravity vector y for natural convection.
        gravity_vector_z : int, float, optional
            Gravity vector z for natural convection.

        Returns
        -------

        """
        flag = self._psiw.oproject.ScrSetIcepakThermalEnv(
            convection,
            force_air,
            top_or_ambient_temperature,
            top_or_overall_flow_direction,
            top_or_overall_flow_speed,
            bottom_temperature,
            bottom_flow_direction,
            bottom_flow_speed,
            gravity_vector_x,
            gravity_vector_y,
            gravity_vector_z,
        )
        return True if flag == 0 else False

    def export_report(self, simulation_name, file_path):
        """Export Icepak simulation report to a file.

        Parameters
        ----------
        simulation_name : str
            Name of the Icepak simulation.
        file_path : str
            Path to the report file.

        Returns
        -------

        """
        flag = self._psiw.oproject.ScrExportIcepakSimReport(simulation_name, file_path)
        return True if flag == 0 else False
