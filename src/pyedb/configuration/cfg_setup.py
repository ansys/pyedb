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
    """
    Parameters
    ----------
    name : str, optional
    type : str
        Type of the setup. Optionals are ``"hfss"``, ``"siwave_ac"``, ``"siwave_dc"``.

    """

    class Common:
        class Grpc:
            def __init__(self, parent):
                self.parent = parent

            def apply_freq_sweep(self, edb_setup):
                for i in self.parent.parent.freq_sweep:
                    f_set = []
                    freq_string = []
                    for f in i.get("frequencies", []):
                        if isinstance(f, dict):
                            increment = f.get("increment", f.get("points", f.get("samples", f.get("step"))))
                            f_set.append([f["distribution"], f["start"], f["stop"], increment])
                        else:
                            freq_string.append(f)
                    discrete_sweep = True
                    if i["type"] == "interpolation":
                        discrete_sweep = False
                    if freq_string:
                        for _sweep in freq_string:
                            _sw = _sweep.split(" ")
                            edb_setup.add_sweep(
                                name=i["name"],
                                distribution=_sw[0],
                                start_freq=_sw[1],
                                stop_freq=_sw[2],
                                step=_sw[3],
                                discrete=discrete_sweep,
                            )
                    else:
                        edb_setup.add_sweep(i["name"], frequency_set=f_set, discrete=discrete_sweep)

        class DotNet(Grpc):
            def __init__(self, parent):
                super().__init__(parent)

            @staticmethod
            def set_frequency_string(sweep, freq_string):
                sweep.frequency_string = freq_string

            def apply_freq_sweep(self, edb_setup):
                for i in self.parent.parent.freq_sweep:
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
                        self.parent.api.set_frequency_string(sweep, freq_string)

        @property
        def pyedb_obj(self):
            return self.parent.pyedb_obj

        def __init__(self, parent):
            self.parent = parent
            self.pedb = parent.pedb
            if self.pedb.grpc:
                self.api = self.Grpc(self)
            else:
                self.api = self.DotNet(self)

        def _retrieve_parameters_from_edb_common(self):
            self.parent.name = self.pyedb_obj.name
            self.parent.type = self.pyedb_obj.type

        def _apply_freq_sweep(self, edb_setup):
            self.api.apply_freq_sweep(edb_setup)

    class Grpc(Common):
        def __init__(self, parent):
            super().__init__(parent)

        def set_parameters_to_edb(self):
            pass

        def retrieve_parameters_from_edb(self):
            pass

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, pedb_obj, **kwargs):
        self.pedb = pedb
        self.pyedb_obj = pedb_obj
        self.name = kwargs.get("name")
        self.type = ""

        self.freq_sweep = []

        self.freq_sweep = kwargs.get("freq_sweep", [])

        if self.pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)

    def _to_dict_setup(self):
        return {
            "name": self.name,
            "type": self.type,
        }


class CfgSIwaveACSetup(CfgSetup):
    class Grpc(CfgSetup.Common):
        def __init__(self, parent):
            super().__init__(parent)

        def set_parameters_to_edb(self):
            if self.parent.name in self.pedb.setups:
                raise "Setup {} already existing. Editing it.".format(self.parent.name)

            edb_setup = self.pedb.create_siwave_syz_setup(name=self.parent.name)
            if self.parent.si_slider_position is not None:
                edb_setup.si_slider_position = self.parent.si_slider_position
            else:
                edb_setup.pi_slider_position = self.parent.pi_slider_position
            self._apply_freq_sweep(edb_setup)

        def retrieve_parameters_from_edb(self):
            self._retrieve_parameters_from_edb_common()
            self.parent.use_si_settings = self.pyedb_obj.use_si_settings
            self.parent.si_slider_position = self.pyedb_obj.si_slider_position
            self.parent.pi_slider_position = self.pyedb_obj.pi_slider_position

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, pyedb_obj, **kwargs):
        super().__init__(pedb, pyedb_obj, **kwargs)
        self.type = "siwave_ac"
        self.use_si_settings = kwargs.get("use_si_settings", True)
        self.si_slider_position = kwargs.get("si_slider_position", 1)
        self.pi_slider_position = kwargs.get("pi_slider_position", 1)

    def to_dict(self):
        temp = self._to_dict_setup()
        temp.update(
            {
                "use_si_settings": self.use_si_settings,
                "si_slider_position": self.si_slider_position,
                "pi_slider_position": self.pi_slider_position,
            }
        )
        return temp


class CfgSIwaveDCSetup(CfgSetup):
    class Grpc(CfgSetup.Common):
        def __init__(self, parent):
            super().__init__(parent)

        def set_parameters_to_edb(self):
            edb_setup = self.pedb.create_siwave_dc_setup(
                name=self.parent.name, dc_slider_position=self.parent.dc_slider_position
            )
            edb_setup.settings.dc.dc_slider_pos = self.parent.dc_slider_position
            edb_setup.settings.export_dc_thermal_data = self.parent.dc_ir_settings.get("export_dc_thermal_data", False)

        def retrieve_parameters_from_edb(self):
            self._retrieve_parameters_from_edb_common()
            self.parent.dc_slider_position = self.pyedb_obj.dc_settings.dc_slider_position
            dc_ir_settings = dict()
            dc_ir_settings["export_dc_thermal_data"] = self.pyedb_obj.dc_ir_settings.export_dc_thermal_data
            self.parent.dc_ir_settings = dc_ir_settings

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

        def set_parameters_to_edb(self):
            edb_setup = self.pedb.create_siwave_dc_setup(
                name=self.parent.name, dc_slider_position=self.parent.dc_slider_position
            )
            edb_setup.dc_settings.dc_slider_position = self.parent.dc_slider_position
            dc_ir_settings = self.parent.dc_ir_settings
            edb_setup.dc_ir_settings.export_dc_thermal_data = dc_ir_settings.get("export_dc_thermal_data", False)

    def __init__(self, pedb, pyedb_obj, **kwargs):
        super().__init__(pedb, pyedb_obj, **kwargs)
        self.type = "siwave_dc"
        self.dc_slider_position = kwargs.get("dc_slider_position")
        self.dc_ir_settings = kwargs.get("dc_ir_settings", {})

    def to_dict(self):
        temp = self._to_dict_setup()
        temp.update({"dc_slider_position": self.dc_slider_position, "dc_ir_settings": self.dc_ir_settings})
        return temp


class CfgHFSSSetup(CfgSetup):
    class Grpc(CfgSetup.Common):
        def __init__(self, parent):
            super().__init__(parent)

        def set_parameters_to_edb(self):
            if self.parent.name in self.pedb.setups:
                raise "Setup {} already existing. Editing it.".format(self.parent.name)

            edb_setup = self.pedb.create_hfss_setup(self.parent.name)
            edb_setup.set_solution_single_frequency(
                self.parent.f_adapt, self.parent.max_num_passes, self.parent.max_mag_delta_s
            )

            self._apply_freq_sweep(edb_setup)

            for i in self.parent.mesh_operations:
                edb_setup.add_length_mesh_operation(
                    name=i["name"],
                    max_elements=i.get("max_elements", 1000),
                    max_length=i.get("max_length", "1mm"),
                    restrict_length=i.get("restrict_length", True),
                    refine_inside=i.get("refine_inside", False),
                    # mesh_region=i.get(mesh_region),
                    net_layer_list=i.get("nets_layers_list", {}),
                )

        def retrieve_parameters_from_edb(self):
            self._retrieve_parameters_from_edb_common()
            single_frequency_adaptive_solution = self.pyedb_obj.settings.general.single_frequency_adaptive_solution
            self.parent.f_adapt = single_frequency_adaptive_solution.adaptive_frequency
            self.parent.max_num_passes = single_frequency_adaptive_solution.max_passes
            self.parent.max_mag_delta_s = float(single_frequency_adaptive_solution.max_delta)
            self.parent.freq_sweep = []
            setup_sweeps = self.sort_sweep_data(self.pyedb_obj.sweep_data)
            for setup_name, sweeps in setup_sweeps.items():
                sw_name = sweeps[0].name
                sw_type = sweeps[0].type.name.lower().split("_")[0]
                freq_strings = [f.frequency_string for f in sweeps]
                self.parent.freq_sweep.append({"name": sw_name, "type": sw_type, "frequencies": freq_strings})

            self.parent.mesh_operations = []
            from ansys.edb.core.simulation_setup.mesh_operation import (
                LengthMeshOperation as GrpcLengthMeshOperation,
            )

            for mesh_op in self.pyedb_obj.mesh_operations:
                if isinstance(mesh_op, GrpcLengthMeshOperation):
                    mop_type = "length"
                else:
                    mop_type = "skin"
                self.parent.mesh_operations.append(
                    {
                        "name": mesh_op.name,
                        "type": mop_type,
                        "max_elements": mesh_op.max_elements,
                        "max_length": mesh_op.max_length,
                        "restrict_length": mesh_op.restrict_max_length,
                        "refine_inside": mesh_op.refine_inside,
                        "nets_layers_list": mesh_op.net_layer_info,
                    }
                )

        @staticmethod
        def sort_sweep_data(sweep_data):
            """grpc sweep data contains all sweeps for each setup, we need to sort thwm by setup"""
            setups = {}
            for sweep in sweep_data:
                if sweep.name not in setups:
                    setups[sweep.name] = [sweep]
                else:
                    setups[sweep.name].append(sweep)
            return setups

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

        def retrieve_parameters_from_edb(self):
            self._retrieve_parameters_from_edb_common()
            adaptive_frequency_data_list = list(self.pyedb_obj.adaptive_settings.adaptive_frequency_data_list)[0]
            self.parent.f_adapt = adaptive_frequency_data_list.adaptive_frequency
            self.parent.max_num_passes = adaptive_frequency_data_list.max_passes
            self.parent.max_mag_delta_s = adaptive_frequency_data_list.max_delta
            self.parent.freq_sweep = []
            for name, sw in self.pyedb_obj.sweeps.items():
                self.parent.freq_sweep.append({"name": name, "type": sw.type, "frequencies": sw.frequency_string})

            self.parent.mesh_operations = []
            for name, mop in self.pyedb_obj.mesh_operations.items():
                self.parent.mesh_operations.append(
                    {
                        "name": name,
                        "type": mop.type,
                        "max_elements": mop.max_elements,
                        "max_length": mop.max_length,
                        "restrict_length": mop.restrict_length,
                        "refine_inside": mop.refine_inside,
                        "nets_layers_list": mop.nets_layers_list,
                    }
                )

    def __init__(self, pedb, pyedb_obj, **kwargs):
        super().__init__(pedb, pyedb_obj, **kwargs)
        self.type = "hfss"
        self.f_adapt = kwargs.get("f_adapt")
        self.max_num_passes = kwargs.get("max_num_passes")
        self.max_mag_delta_s = kwargs.get("max_mag_delta_s")

        self.mesh_operations = kwargs.get("mesh_operations", [])

    def to_dict(self):
        temp = self._to_dict_setup()
        temp.update(
            {
                "f_adapt": self.f_adapt,
                "max_num_passes": self.max_num_passes,
                "max_mag_delta_s": self.max_mag_delta_s,
                "mesh_operations": self.mesh_operations,
                "freq_sweep": self.freq_sweep,
            }
        )
        return temp


class CfgSetups:
    class Grpc:
        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent.pedb

        def retrieve_parameters_from_edb(self):
            self.parent.setups = []
            for _, setup in self._pedb.setups.items():
                if setup.type.name.lower() == "hfss":
                    hfss = CfgHFSSSetup(self._pedb, setup)
                    hfss.api.retrieve_parameters_from_edb()
                    self.parent.setups.append(hfss)
                elif setup.type.name.lower() == "si_wave_dcir":
                    siwave_dc = CfgSIwaveDCSetup(self._pedb, setup)
                    siwave_dc.api.retrieve_parameters_from_edb()
                    self.parent.setups.append(siwave_dc)
                elif setup.type.name.lower() == "si_wave":
                    siwave_ac = CfgSIwaveACSetup(self._pedb, setup)
                    siwave_ac.api.retrieve_parameters_from_edb()
                    self.parent.setups.append(siwave_ac)
                elif setup.type.name.lower() == "raptor_x":
                    pass

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

        def retrieve_parameters_from_edb(self):
            self.parent.setups = []
            for _, setup in self._pedb.setups.items():
                if setup.type == "hfss":
                    hfss = CfgHFSSSetup(self._pedb, setup)
                    hfss.api.retrieve_parameters_from_edb()
                    self.parent.setups.append(hfss)
                elif setup.type == "siwave_dc":
                    siwave_dc = CfgSIwaveDCSetup(self._pedb, setup)
                    siwave_dc.api.retrieve_parameters_from_edb()
                    self.parent.setups.append(siwave_dc)
                elif setup.type == "siwave_ac":
                    siwave_ac = CfgSIwaveACSetup(self._pedb, setup)
                    siwave_ac.api.retrieve_parameters_from_edb()
                    self.parent.setups.append(siwave_ac)

    def __init__(self, pedb, setups_data):
        self.pedb = pedb
        self.setups = []
        if self.pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)
        for stp in setups_data:
            if stp["type"].lower() == "hfss":
                self.setups.append(CfgHFSSSetup(self.pedb, None, **stp))
            elif stp["type"].lower() in ["siwave_ac", "siwave_syz"]:
                self.setups.append(CfgSIwaveACSetup(self.pedb, None, **stp))
            elif stp["type"].lower() == "siwave_dc":
                self.setups.append(CfgSIwaveDCSetup(self.pedb, None, **stp))

    def apply(self):
        for s in self.setups:
            s.api.set_parameters_to_edb()

    def to_dict(self):
        return [i.to_dict() for i in self.setups]

    def retrieve_parameters_from_edb(self):
        self.api.retrieve_parameters_from_edb()
