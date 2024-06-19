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

from pyedb.configuration.cfg_common import CfgBase


class CfgFrequencies(CfgBase):
    def __init__(self, **kwargs):
        self.distribution = kwargs.get('distribution').replace(" ", "_") if kwargs.get("distribution") else None
        self.start = kwargs.get('start')
        self.stop = kwargs.get('stop')
        self.increment = kwargs.get('increment', kwargs.get('points', kwargs.get("samples", kwargs.get("step"))))


class CfgSweepData(CfgBase):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.type = kwargs.get("type").lower() if kwargs.get("type") else None
        self.frequencies = []
        for kw in kwargs.get('frequencies', []):
            self.frequencies.append(CfgFrequencies(**kw))


class CfgSetup(CfgBase):
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs.get("name")
        self.type = kwargs.get("type").lower() if kwargs.get("type") else None


class CfgSIwaveSetup(CfgSetup):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)
        self.si_slider_position = 1
        self.pi_slider_position = 1


class CfgSIwaveDCSetup(CfgSetup):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)
        self.dc_settings = CfgDcSetup()


class CfgHFSSSetup(CfgSetup):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)

        self.f_adapt = kwargs.get("f_adapt")
        self.max_num_passes = kwargs.get("max_num_passes")
        self.max_mag_delta_s = kwargs.get("max_mag_delta_s")

        self.mesh_operations = []
        for i in kwargs.get("mesh_operations", []):
            self.mesh_operations.append(CfgLengthMeshOperation(**i))

        self.freq_sweep = []
        for i in kwargs.get("freq_sweep", []):
            self.freq_sweep.append(CfgSweepData(**i))

    def apply(self):
        if self.name in self._pedb.setups:
            raise "Setup {} already existing. Editing it.".format(self.name)

        edb_setup = self._pedb.create_hfss_setup(self.name)
        edb_setup.set_solution_single_frequency(self.f_adapt, self.max_num_passes, self.max_mag_delta_s)
        for i in self.freq_sweep:
            f_set = []
            kw = {}
            for attr in i.get_attributes(exclude="name"):
                if attr == "frequencies":
                    for f in i.frequencies:
                        f_set.append([f.distribution, f.start, f.stop, f.increment])
                else:
                    kw[attr] = getattr(i, attr)
            edb_setup.add_sweep(i.name, frequency_set=f_set, **kw)

        for i in self.mesh_operations:
            edb_setup.add_length_mesh_operation(net_layer_list=i.nets_layers_list,
                                                name=i.name,
                                                #max_elements=i.max_elements,
                                                max_length=i.max_length,
                                                #restrict_elements=i.restrict_max_elements,
                                                restrict_length=i.restrict_length,
                                                refine_inside=i.refine_inside,
                                                #mesh_region=i.mesh_region
                                                )


class CfgDcSetup:
    def __init__(self):
        self.dc_slider_position = 1
        self.dcir_settings = DcIrSettings()


class DcIrSettings:
    def __init__(self):
        self.export_dc_thermal_data = True


class CfgMeshOperation(CfgBase):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.type = kwargs.get("type")
        #self.mesh_region = kwargs.get("mesh_region")
        self.nets_layers_list = kwargs.get("nets_layers_list", {})
        self.refine_inside = kwargs.get("refine_inside", False)


class CfgLengthMeshOperation(CfgMeshOperation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # waiting bug review
        #self.restrict_max_elements = kwargs.get("restrict_max_elements", True)
        #self.max_elements = kwargs.get("max_elements", 1000)
        self.restrict_length = kwargs.get("restrict_length", True)
        self.max_length = kwargs.get("max_length", "1mm")


class CfgSetups:
    def __init__(self, pedb, setups_data):
        self._pedb = pedb
        self.setups = []
        for stp in setups_data:
            if stp.get("type").lower() == "hfss":
                self.setups.append(CfgHFSSSetup(self._pedb, **stp))
            elif stp.get("type").lower() == "siwave":
                self.setups.append(CfgSIwaveSetup(self._pedb, **stp))
            elif stp.get("type").lower() == "siwave_dc":
                self.setups.append(CfgSIwaveDCSetup(self._pedb, **stp))

    def apply(self):
        for s in self.setups:
            s.apply()

    def get_data_from_db(self):
        setups = []
        for _, s in self._pedb.setups.items():
            stp = {}
            if s.setup_type == "kHFSS":
                for p_name in CfgHFSSSetup(self._pedb).__dict__:
                    if p_name.startswith("_"):
                        continue
                    elif p_name == "type":
                        stp[p_name] = s.type
                    elif p_name == "f_adapt":
                        stp[p_name] = list(s.adaptive_settings.adaptive_frequency_data_list)[0].adaptive_frequency
                    elif p_name == "max_num_passes":
                        stp[p_name] = list(s.adaptive_settings.adaptive_frequency_data_list)[0].max_passes
                    elif p_name == "max_mag_delta_s":
                        stp[p_name] = list(s.adaptive_settings.adaptive_frequency_data_list)[0].max_delta
                    elif p_name == "freq_sweep":
                        stp["freq_sweep"] = []
                        for _, sw in s.sweeps.items():
                            sweep_data = {}
                            for sw_p_name in CfgSweepData().__dict__:
                                if sw_p_name == "frequencies":
                                    pass  # Frequencies cannot be read from EDB
                                else:
                                    sweep_data[sw_p_name] = getattr(sw, sw_p_name)
                            stp["freq_sweep"].append(sweep_data)
                    elif p_name == "mesh_operations":
                        mops = []
                        for _, i in s.mesh_operations.items():
                            mop = {}
                            for mop_p_name in CfgLengthMeshOperation().__dict__:
                                mop[mop_p_name] = getattr(i, mop_p_name)
                            mops.append(mop)
                        stp["mesh_operations"] = mops
                    else:
                        stp[p_name] = getattr(s, p_name)
            setups.append(stp)
        return setups
