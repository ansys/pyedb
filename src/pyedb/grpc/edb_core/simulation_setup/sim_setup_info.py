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

from pyedb.dotnet.edb_core.sim_setup_data.data.simulation_settings import (  # HFSSSimulationSettings
    HFSSPISimulationSettings,
)
from pyedb.dotnet.edb_core.sim_setup_data.data.sweep_data import SweepData


class SimSetupInfo:
    def __init__(
        self,
        pedb,
        sim_setup,
        edb_object=None,
        setup_type: str = None,
        name: str = None,
    ):
        self._pedb = pedb
        self.sim_setup = sim_setup
        simulation_setup_type = {
            "kHFSS": self._pedb.simsetupdata.HFSSSimulationSettings,
            "kPEM": None,
            "kSIwave": self._pedb.simsetupdata.SIwave.SIWSimulationSettings,
            "kLNA": None,
            "kTransient": None,
            "kQEye": None,
            "kVEye": None,
            "kAMI": None,
            "kAnalysisOption": None,
            "kSIwaveDCIR": self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings,
            "kSIwaveEMI": None,
            "kHFSSPI": self._pedb.simsetupdata.HFSSPISimulationSettings,
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }

        if edb_object is None:
            self._edb_object = self._pedb.simsetupdata.SimSetupInfo[simulation_setup_type[setup_type]]()
            self._edb_object.Name = name
        else:
            self._edb_object = edb_object

    @property
    def name(self):
        return self._edb_object.Name

    @name.setter
    def name(self, name):
        self._edb_object.Name = name

    @property
    def position(self):
        return self._edb_object.Position

    @property
    def sim_setup_type(self):
        """
        "kHFSS": self._pedb.simsetupdata.HFSSSimulationSettings,
        "kPEM": None,
        "kSIwave": self._pedb.simsetupdata.SIwave.SIWSimulationSettings,
        "kLNA": None,
        "kTransient": None,
        "kQEye": None,
        "kVEye": None,
        "kAMI": None,
        "kAnalysisOption": None,
        "kSIwaveDCIR": self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings,
        "kSIwaveEMI": None,
        "kHFSSPI": self._pedb.simsetupdata.HFSSPISimulationSettings,
        "kDDRwizard": None,
        "kQ3D": None,
        "kNumSetupTypes": None,
        """

        return self._edb_object.SimSetupType.ToString()

    @property
    def simulation_settings(self):
        if self.sim_setup_type == "kHFSS":
            return self._edb_object.SimulationSettings
            # todo refactor HFSS
            # return HFSSSimulationSettings(self._pedb, self.sim_setup, self._edb_object.SimulationSettings)
        elif self.sim_setup_type == "kHFSSPI":
            return HFSSPISimulationSettings(self._pedb, self.sim_setup, self._edb_object.SimulationSettings)
        elif self.sim_setup_type == "kSIwave":  # todo refactor
            return self._edb_object.SimulationSettings

        elif self.sim_setup_type == "kSIwaveDCIR":  # todo refactor
            return self._edb_object.SimulationSettings

    @property
    def sweep_data_list(self):
        return [
            SweepData(self._pedb, edb_object=i, sim_setup=self.sim_setup) for i in list(self._edb_object.SweepDataList)
        ]

    def add_sweep_data(self, sweep_data):
        sweep_data._sim_setup = self.sim_setup
        self._edb_object.SweepDataList.Add(sweep_data._edb_object)
