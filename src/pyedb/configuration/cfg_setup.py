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


class CfgSetup:
    class Common:
        @property
        def pyedb_obj(self):
            return self.parent.pyedb_obj

        def __init__(self, parent):
            self.parent = parent
            self.pedb = parent.pedb

        def _apply_freq_sweep(self, edb_setup):
            for i in self.parent.freq_sweep:
                f_set = []
                freq_string = []
                for f in i.get("frequencies", []):
                    if isinstance(f, dict):
                        increment = f.get("increment", f.get("points", f.get("samples", f.get("step"))))
                        f_set.append([f["distribution"], f["start"], f["stop"], increment])
                    else:
                        freq_string.append(f)
                sweep = edb_setup.add_sweep(i["name"], frequency_set=f_set, sweep_type=i["type"])
                if len(freq_string) > 0:
                    sweep.frequency_string = freq_string

    class Grpc(Common):
        def __init__(self, parent):
            super().__init__(parent)

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, pedb_obj, **kwargs):
        self.pedb = pedb
        self.pyedb_obj = pedb_obj
        self.name = kwargs.get("name")
        self.type = kwargs.get("type").lower() if kwargs.get("type") else None

        self.freq_sweep = []

        self.freq_sweep = kwargs.get("freq_sweep", [])

        if self.pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)

    def _to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
        }


class CfgSIwaveACSetup(CfgSetup):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)
        self.si_slider_position = kwargs.get("si_slider_position")
        self.pi_slider_position = kwargs.get("pi_slider_position")

    def set_parameters_to_edb(self):
        if self.name in self.pedb.setups:
            raise "Setup {} already existing. Editing it.".format(self.name)

        kwargs = (
            {"si_slider_position": self.si_slider_position}
            if self.si_slider_position is not None
            else {"pi_slider_position": self.pi_slider_position}
        )

        edb_setup = self.pedb.create_siwave_syz_setup(name=self.name, **kwargs)
        self._apply_freq_sweep(edb_setup)


class CfgSIwaveDCSetup(CfgSetup):
    def __init__(self, pedb, **kwargs):
        super().__init__(pedb, **kwargs)
        self.dc_slider_position = kwargs.get("dc_slider_position")
        self.dc_ir_settings = CfgDcIrSettings(**kwargs.get("dc_ir_settings", {}))
        self.freq_sweep = None

    def set_parameters_to_edb(self):
        edb_setup = self.pedb.create_siwave_dc_setup(name=self.name, dc_slider_position=self.dc_slider_position)
        for k, v in self.dc_ir_settings.get_attributes().items():
            if k == "dc_slider_postion":
                edb_setup.dc_settings.dc_slider_position = v
            else:
                setattr(edb_setup.dc_ir_settings, k, v)


class CfgHFSSSetup(CfgSetup):
    class Grpc(CfgSetup.Common):

        def __init__(self, parent):
            super().__init__(parent)

        def set_parameters_to_edb(self):
            if self.parent.name in self.pedb.setups:
                raise "Setup {} already existing. Editing it.".format(self.parent.name)

            edb_setup = self.pedb.create_hfss_setup(self.parent.name)
            edb_setup.set_solution_single_frequency(self.parent.f_adapt, self.parent.max_num_passes,
                                                    self.parent.max_mag_delta_s)

            self._apply_freq_sweep(edb_setup)

            for i in self.parent.mesh_operations:
                edb_setup.add_length_mesh_operation(
                    name=i["name"],
                    max_elements=i.get("max_elements", 1000),
                    max_length=i.get("max_length", "1mm"),
                    restrict_length=i.get("restrict_length", True),
                    refine_inside=i.get("refine_inside", False),
                    #mesh_region=i.get(mesh_region),
                    net_layer_list=i.get("nets_layers_list", {}),
                )

        def retrieve_parameters_from_edb(self):
            self.parent.name = self.pyedb_obj.name
            self.parent.type = self.pyedb_obj.type
            adaptive_frequency_data_list = list(self.pyedb_obj.adaptive_settings.adaptive_frequency_data_list)[0]
            self.parent.f_adapt = adaptive_frequency_data_list.adaptive_frequency
            self.parent.max_num_passes = adaptive_frequency_data_list.max_passes
            self.parent.max_mag_delta_s = adaptive_frequency_data_list.max_delta
            self.parent.freq_sweep = []
            for name, sw in self.pyedb_obj.sweeps.items():
                self.parent.freq_sweep.append({
                    "name": name,
                    "type": sw.type,
                    "frequencies": sw.frequency_string
                })

            self.parent.mesh_operations = []
            for name, mop in self.pyedb_obj.mesh_operations.items():
                self.parent.mesh_operations.append({
                    "name": name,
                    "type": mop.type,
                    "max_elements": mop.max_elements,
                    "max_length": mop.max_length,
                    "restrict_length": mop.restrict_length,
                    "refine_inside": mop.refine_inside,
                    "nets_layers_list": mop.nets_layers_list
                })

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, pyedb_obj, **kwargs):
        super().__init__(pedb, pyedb_obj, **kwargs)

        self.f_adapt = kwargs.get("f_adapt")
        self.max_num_passes = kwargs.get("max_num_passes")
        self.max_mag_delta_s = kwargs.get("max_mag_delta_s")

        self.mesh_operations = kwargs.get("mesh_operations", [])

    def to_dict(self):
        temp = self._to_dict()
        temp.update({
            "f_adapt": self.f_adapt,
            "max_num_passes": self.max_num_passes,
            "max_mag_delta_s": self.max_mag_delta_s,
            "mesh_operations": self.mesh_operations,
            "freq_sweep": self.freq_sweep
        })
        return temp


class CfgDcIrSettings:
    def __init__(self, **kwargs):
        self.export_dc_thermal_data = kwargs.get("export_dc_thermal_data")


class CfgSetups:
    def __init__(self, pedb, setups_data):
        self.pedb = pedb
        self.setups = []
        for stp in setups_data:
            if stp.get("type").lower() == "hfss":
                self.setups.append(CfgHFSSSetup(self.pedb, None, **stp))
            elif stp.get("type").lower() in ["siwave_ac", "siwave_syz"]:
                self.setups.append(CfgSIwaveACSetup(self.pedb, **stp))
            elif stp.get("type").lower() == "siwave_dc":
                self.setups.append(CfgSIwaveDCSetup(self.pedb, **stp))

    def apply(self):
        for s in self.setups:
            s.api.set_parameters_to_edb()

    def to_dict(self):
        return [i.to_dict() for i in self.setups]

    def retrieve_parameters_from_edb(self):
        self.setups = []
        for _, setup in self.pedb.setups.items():
            if setup.type == "hfss":
                hfss = CfgHFSSSetup(self.pedb, setup)
                hfss.api.retrieve_parameters_from_edb()
                self.setups.append(hfss)

    def get_data_from_db(self):
        setups = []
        for _, s in self.pedb.setups.items():
            if float(self.pedb.edbversion) < 2025.1:
                if not s.type == "hfss":
                    self.pedb.logger.warning("Only HFSS setups are exported in 2024 R2 and earlier version.")
                    continue

            stp = {}
            if self.pedb.grpc:
                from ansys.edb.core.simulation_setup.mesh_operation import (
                    LengthMeshOperation as GrpcLengthMeshOperation,
                )

                s_type = s.type.name.lower()
                if s_type == "hfss":
                    for p_name in CfgHFSSSetup(self.pedb).__dict__:
                        if p_name.startswith("_"):
                            continue
                        elif p_name == "type":
                            stp[p_name] = s.type.name.lower()
                        elif p_name == "f_adapt":
                            stp[p_name] = s.settings.general.single_frequency_adaptive_solution.adaptive_frequency
                        elif p_name == "max_num_passes":
                            stp[p_name] = s.settings.general.single_frequency_adaptive_solution.max_passes
                        elif p_name == "max_mag_delta_s":
                            stp[p_name] = s.settings.general.single_frequency_adaptive_solution.max_delta
                        elif p_name == "freq_sweep":
                            f_sweep = []
                            for sw in s.sweep_data:
                                sweep_data = {}
                                for sw_p_name in CfgSweepData().__dict__:
                                    if sw_p_name == "frequencies":
                                        pass  # Frequencies cannot be read from EDB
                                    else:
                                        sweep_data[sw_p_name] = getattr(sw, sw_p_name)
                                f_sweep.append(sweep_data)
                            stp["freq_sweep"] = f_sweep
                        elif p_name == "mesh_operations":
                            mops = []
                            for i in s.mesh_operations:
                                mop = {}
                                for mop_p_name in CfgLengthMeshOperation().__dict__:
                                    if mop_p_name == "type":
                                        if isinstance(i, GrpcLengthMeshOperation):
                                            mop[mop_p_name] = "length"
                                    elif mop_p_name == "nets_layers_list":
                                        mop[mop_p_name] = i.__dict__["_net_layer_info"]
                                    elif mop_p_name == "restrict_length":
                                        mop[mop_p_name] = i.__dict__["_restrict_max_length"]
                                    else:
                                        mop[mop_p_name] = i.__dict__[f"_{mop_p_name}"]
                                mops.append(mop)
                            stp["mesh_operations"] = mops
                        else:
                            stp[p_name] = getattr(s, p_name)

                elif s_type == "siwave_ac":
                    for p_name in CfgSIwaveACSetup(self.pedb).__dict__:
                        if p_name.startswith("_"):
                            continue
                        elif p_name == "freq_sweep":
                            pass  # Bug in EDB API
                        else:
                            stp[p_name] = getattr(s, p_name)
                elif s_type == "siwave_dc":
                    for p_name in CfgSIwaveDCSetup(self.pedb).__dict__:
                        if p_name.startswith("_"):
                            continue
                        elif p_name == "freq_sweep":
                            pass
                        elif p_name == "dc_ir_settings":
                            dc_ir_s = {}
                            for dcir_p_name in CfgDcIrSettings().__dict__:
                                dc_ir_s[dcir_p_name] = getattr(s.dc_ir_settings, dcir_p_name)
                            stp["dc_ir_settings"] = dc_ir_s
                        elif p_name == "dc_slider_position":
                            stp[p_name] = getattr(s.dc_settings, p_name)
                        else:
                            stp[p_name] = getattr(s, p_name)
            else:
                for _, s in self.pedb.setups.items():
                    if float(self.pedb.edbversion) < 2025.1:
                        if not s.type == "hfss":
                            self.pedb.logger.warning("Only HFSS setups are exported in 2024 R2 and earlier version.")
                            continue
                    if s.type == "hfss":
                        for p_name in CfgHFSSSetup(self.pedb).__dict__:
                            if p_name.startswith("_"):
                                continue
                            elif p_name == "type":
                                stp[p_name] = s.type
                            elif p_name == "f_adapt":
                                stp[p_name] = list(s.adaptive_settings.adaptive_frequency_data_list)[
                                    0
                                ].adaptive_frequency
                            elif p_name == "max_num_passes":
                                stp[p_name] = list(s.adaptive_settings.adaptive_frequency_data_list)[0].max_passes
                            elif p_name == "max_mag_delta_s":
                                stp[p_name] = list(s.adaptive_settings.adaptive_frequency_data_list)[0].max_delta
                            elif p_name == "freq_sweep":
                                f_sweep = []
                                for sw in s.sweeps.items():
                                    sweep_data = {}
                                    for sw_p_name in CfgSweepData().__dict__:
                                        if sw_p_name == "frequencies":
                                            pass  # Frequencies cannot be read from EDB
                                        else:
                                            sweep_data[sw_p_name] = getattr(sw[1], sw_p_name)
                                    f_sweep.append(sweep_data)
                                stp["freq_sweep"] = f_sweep
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

                    elif s.type == "siwave_ac":
                        for p_name in CfgSIwaveACSetup(self.pedb).__dict__:
                            if p_name.startswith("_"):
                                continue
                            elif p_name == "freq_sweep":
                                pass  # Bug in EDB API
                            else:
                                stp[p_name] = getattr(s, p_name)
                    elif s.type == "siwave_dc":
                        for p_name in CfgSIwaveDCSetup(self.pedb).__dict__:
                            if p_name.startswith("_"):
                                continue
                            elif p_name == "freq_sweep":
                                pass
                            elif p_name == "dc_ir_settings":
                                dc_ir_s = {}
                                for dcir_p_name in CfgDcIrSettings().__dict__:
                                    dc_ir_s[dcir_p_name] = getattr(s.dc_ir_settings, dcir_p_name)
                                stp["dc_ir_settings"] = dc_ir_s
                            elif p_name == "dc_slider_position":
                                stp[p_name] = getattr(s.dc_settings, p_name)
                            else:
                                stp[p_name] = getattr(s, p_name)
            setups.append(stp)
        return setups
