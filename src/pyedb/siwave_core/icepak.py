class Icepak:
    def __init__(self, psiw):
        self._psiw = psiw

    def run(self, name, dc_simulation_name):
        flag = self._psiw.oproject.ScrRunIcepakSimulation(name, dc_simulation_name)
        return True if not flag else False

    def set_meshing_detail(self, mesh_level=0):
        flag = self._psiw.oproject.ScrSetIcepakMeshingDetail({0: "basic", 1: "detailed", 2: "exhaustive"}[mesh_level])
        return True if not flag else False

    def set_board_outline_fidelity(self, fidelity=2):
        flag = self._psiw.oproject.ScrSetIcepakBoardOutlineFidelity(fidelity)
        return True if not flag else False
