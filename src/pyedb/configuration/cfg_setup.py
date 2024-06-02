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

from enum import Enum


class FrequencySweep:
    def __init__(self, sweep_dict=None):
        self._sweep_dict = sweep_dict
        self.name = "PyEDB_sweep"
        self.type = self.SweepType.INTERPOLATING
        self.distribution = [self.Distribution()]
        if sweep_dict:
            self.name = self._sweep_dict.get("name", "PyEDB_sweep")
            frequencies = self._sweep_dict.get("frequencies", None)
            self._map_sweep_type()
            self.distribution = [self.Distribution(dist) for dist in frequencies]

    class SweepType(Enum):
        INTERPOLATING = 0
        DISCRETE = 1

    class Distribution:
        def __init__(self, distribution_dict=None):
            self.type = self.DistributionType.LINEAR_STEP
            self.start = "0GHz"
            self.stop = "10GHz"
            self.step = "10MHz"
            self.count = 100
            if distribution_dict:
                self.map(distribution_dict)

        class DistributionType(Enum):
            LINEAR_STEP = 0
            LINEAR_COUNT = 1
            LOG_SCALE = 2

        def map(self, distribution_dict):
            distribution_type = distribution_dict.get("distribution", "linear step")
            if distribution_type == "linear step":
                self.type = self.DistributionType.LINEAR_STEP
            elif distribution_type == "linear count":
                self.type = self.DistributionType.LINEAR_COUNT
            elif distribution_type == "log scale":
                self.type = self.DistributionType.LOG_SCALE
            else:
                self.type = self.DistributionType.LINEAR_STEP
            self.start = distribution_dict.get("start", "OGHz")
            self.stop = distribution_dict.get("stop", "10GHz")
            self.step = distribution_dict.get("step", "10MHz")
            self.count = distribution_dict.get("count", 100)

    def _map_sweep_type(self):
        if self._sweep_dict.get("type", "discrete"):
            self.type = self.SweepType.DISCRETE
        else:
            self.type = self.SweepType.INTERPOLATING


class CfgDcSetup:
    def __init__(self):
        self.dc_slider_position = 1
        self.dcir_settings = DcIrSettings()


class DcIrSettings:
    def __init__(self):
        self.export_dc_thermal_data = True


class CfgSetup:
    def __init__(self, pdata, setup_dict=None):
        self._pedb = pdata._pedb
        self._setup_dict = None
        self.name = "PyEDB_setup"
        self.type = self.SetupType.HFSS
        self.f_adapt = "5GHz"
        self.max_num_passes = 30
        self.max_mag_delta_s = 0.02
        self.sweeps = [FrequencySweep()]
        self.dc_settings = CfgDcSetup()
        self.si_slider_position = 1
        self.pi_slider_position = 1
        if setup_dict:
            self._setup_dict = setup_dict
            self.name = setup_dict.get("name", "PyEDB_setup")
            self._map_setup_type(setup_dict.get("type", None))
            self.f_adapt = setup_dict.get("f_adapt", "5GHz")
            self.max_mag_delta_s = setup_dict.get("max_mag_delta_s", 0.02)
            if setup_dict.get("freq_sweep", None):
                self.sweeps = [FrequencySweep(sweep) for sweep in setup_dict.get("freq_sweep", None)]
            else:
                self.sweeps = []
            self.dc_settings.dc_slider_position = setup_dict.get("dc_slider_position", 1)
            if setup_dict.get("dc_ir_settings", None):
                dc_ir_dict = setup_dict.get("dc_ir_settings")
                self.dc_settings.dcir_settings.export_dc_thermal_data = dc_ir_dict.get("export_dc_thermal_data", True)

    def _map_setup_type(self, setup_type):
        if setup_type.upper() == "HFSS":
            self.type = self.SetupType.HFSS
        elif setup_type.upper() == "HFSS_PI":
            self.type = self.SetupType.HFSS_PI
        elif setup_type.upper() == "SIWAVE_SYZ":
            self.type = self.SetupType.SIWAVE_SYZ
        elif setup_type.upper() == "SIWAVE_DC":
            self.type = self.SetupType.SIWAVE_DC
        elif setup_type.upper() == "RAPTORX":
            self.type = self.SetupType.RAPTORX
        elif setup_type.upper() == "Q3D":
            self.type = self.SetupType.Q3D
        else:
            self.type = self.SetupType.HFSS

    class SetupType(Enum):
        HFSS = 0
        SIWAVE_SYZ = 1
        SIWAVE_DC = 2
        HFSS_PI = 3
        RAPTORX = 4
        Q3D = 5

    def apply(self):
        edb_setup = None
        if self.type == self.SetupType.SIWAVE_DC:
            if self.name not in self._pedb.setups:
                edb_setup = self._pedb.create_siwave_dc_setup(self.name)
                self._pedb.logger.info("Setup {} created.".format(self.name))
            else:
                self._pedb.logger.warning("Setup {} already existing. Editing it.".format(self.name))
            edb_setup = self._pedb.setups[self.name]
            edb_setup.set_dc_slider(self.dc_settings.dc_slider_position)
            # TODO add DCIR settings in EDB setup
        elif self.type == self.SetupType.HFSS:
            if self.name not in self._pedb.setups:
                edb_setup = self._pedb.create_hfss_setup(self.name)
                self._pedb.logger.info("Setup {} created.".format(self.name))
            else:
                self._pedb.logger.warning("Setup {} already existing. Editing it.".format(self.name))
                edb_setup = self._pedb.setups[self.name]
            if not edb_setup.set_solution_single_frequency(self.f_adapt, self.max_num_passes, self.max_mag_delta_s):
                self._pedb.logger.errur(f"Failed to create HFSS simulation setup {self.name}")
        elif self.type == self.SetupType.SIWAVE_SYZ:
            if self.name not in self._pedb.setups:
                edb_setup = self._pedb.create_siwave_syz_setup(self.name)
                self._pedb.logger.info("Setup {} created.".format(self.name))
            else:
                self._pedb.logger.warning("Setup {} already existing. Editing it.".format(self.name))
                edb_setup = self._pedb.setups[self.name]
                edb_setup.si_slider_position = self.si_slider_position
                edb_setup.pi_slider_position = self.pi_slider_position
        for sweep in self.sweeps:
            for dist in sweep.distribution:
                freqs = []
                if dist.type == dist.DistributionType.LINEAR_STEP:
                    freqs.append(
                        [
                            "linear scale",
                            self._pedb.edb_value(dist.start).ToString(),
                            self._pedb.edb_value(dist.stop).ToString(),
                            self._pedb.edb_value(dist.step).ToString(),
                        ]
                    )
                elif dist.type == dist.DistributionType.LINEAR_COUNT:
                    freqs.append(
                        [
                            "linear count",
                            self._pedb.edb_value(dist.start).ToString(),
                            self._pedb.edb_value(dist.stop).ToString(),
                            int(dist.count),
                        ]
                    )
                elif dist.type == dist.DistributionType.LOG_SCALE:
                    freqs.append(
                        [
                            "log scale",
                            self._pedb.edb_value(dist.start).ToString(),
                            self._pedb.edb_value(dist.stop).ToString(),
                            int(dist.count),
                        ]
                    )
                edb_setup.add_frequency_sweep(sweep.name, frequency_sweep=freqs)
