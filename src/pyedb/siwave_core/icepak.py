class Icepak:
    def __init__(self, psiw):
        self._psiw = psiw

    def run(self, name, dc_simulation_name):
        """Run Icepak analysis.

        Parameters
        ----------
        name
        dc_simulation_name

        Returns
        -------

        """
        flag = self._psiw.oproject.ScrRunIcepakSimulation(name, dc_simulation_name)
        return True if flag == 0 else False

    def set_meshing_detail(self, mesh_level=0):
        """Sets the meshing detail level for Icepak simulations.

        Parameters
        ----------
        mesh_level

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
        fidelity

        Returns
        -------

        """
        flag = self._psiw.oproject.ScrSetIcepakBoardOutlineFidelity(fidelity)
        return True if flag == 0 else False

    def set_thermal_environment(self,
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
                                gravity_vector_z=9.8):
        """Sets the thermal environment settings to use for Icepak simulations.

        Parameters
        ----------
        convection
        force_air
        top_or_ambient_temperature
        top_or_overall_flow_direction
        top_or_overall_flow_speed
        bottom_temperature
        bottom_flow_direction
        bottom_flow_speed
        gravity_vector_x
        gravity_vector_y
        gravity_vector_z

        Returns
        -------

        """
        flag = self._psiw.oproject.ScrSetIcepakThermalEnv(convection, force_air, top_or_ambient_temperature,
                                                   top_or_overall_flow_direction, top_or_overall_flow_speed,
                                                   bottom_temperature, bottom_flow_direction, bottom_flow_speed,
                                                   gravity_vector_x, gravity_vector_y, gravity_vector_z)
        return True if flag == 0 else False
