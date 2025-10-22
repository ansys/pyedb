# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

    @staticmethod
    def set_frequency_string(sweep, freq_string):
        sweep.frequency_string = freq_string

    def apply_freq_sweep(self, edb_setup):
        for i in self.freq_sweep:
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
                self.set_frequency_string(sweep, freq_string)

    def __init__(self, pedb, pedb_obj, **kwargs):
        self.pedb = pedb
        self.pyedb_obj = pedb_obj
        self.name = kwargs["name"]
        self.type = ""

        self.freq_sweep = []

        self.freq_sweep = kwargs.get("freq_sweep", [])

    def _to_dict_setup(self):
        return {
            "name": self.name,
            "type": self.type,
        }


class CfgSIwaveACSetup(CfgSetup):
    def set_parameters_to_edb(self):
        if self.name in self.pedb.setups:
            raise "Setup {} already existing. Editing it.".format(self.name)

        edb_setup = self.pedb.create_siwave_syz_setup(name=self.name)
        if self.si_slider_position is not None:
            edb_setup.si_slider_position = self.si_slider_position
        else:
            edb_setup.pi_slider_position = self.pi_slider_position
        self.apply_freq_sweep(edb_setup)

    def retrieve_parameters_from_edb(self):
        self.use_si_settings = self.pyedb_obj.use_si_settings
        self.si_slider_position = self.pyedb_obj.si_slider_position
        self.pi_slider_position = self.pyedb_obj.pi_slider_position

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
    def retrieve_parameters_from_edb(self):
        self.dc_slider_position = self.pyedb_obj.dc_settings.dc_slider_position
        dc_ir_settings = dict()
        dc_ir_settings["export_dc_thermal_data"] = self.pyedb_obj.dc_ir_settings.export_dc_thermal_data
        self.dc_ir_settings = dc_ir_settings

    def set_parameters_to_edb(self):
        edb_setup = self.pedb.create_siwave_dc_setup(name=self.name, dc_slider_position=self.dc_slider_position)
        edb_setup.dc_settings.dc_slider_position = self.dc_slider_position
        dc_ir_settings = self.dc_ir_settings
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
    def set_parameters_to_edb(self):
        if self.name in self.pedb.setups:
            raise "Setup {} already existing. Editing it.".format(self.name)

        edb_setup = self.pedb.create_hfss_setup(self.name)
        edb_setup.set_solution_single_frequency(self.f_adapt, self.max_num_passes, self.max_mag_delta_s)

        self.apply_freq_sweep(edb_setup)

        if self.auto_mesh_operation:
            edb_setup.auto_mesh_operation(**self.auto_mesh_operation)

        for i in self.mesh_operations:
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
        adaptive_frequency_data_list = list(self.pyedb_obj.adaptive_settings.adaptive_frequency_data_list)[0]
        self.f_adapt = adaptive_frequency_data_list.adaptive_frequency
        self.max_num_passes = adaptive_frequency_data_list.max_passes
        self.max_mag_delta_s = adaptive_frequency_data_list.max_delta
        self.freq_sweep = []
        for name, sw in self.pyedb_obj.sweeps.items():
            self.freq_sweep.append({"name": name, "type": sw.type, "frequencies": sw.frequency_string})

        self.mesh_operations = []
        for name, mop in self.pyedb_obj.mesh_operations.items():
            self.mesh_operations.append(
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

        self.auto_mesh_operation = kwargs.get("auto_mesh_operation", None)
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
    def retrieve_parameters_from_edb(self):
        self.setups = []
        for _, setup in self._pedb.setups.items():
            if setup.type == "hfss":
                hfss = CfgHFSSSetup(self._pedb, setup, name=setup.name)
                hfss.retrieve_parameters_from_edb()
                self.setups.append(hfss)
            elif setup.type == "siwave_dc":
                siwave_dc = CfgSIwaveDCSetup(self._pedb, setup, name=setup.name)
                siwave_dc.retrieve_parameters_from_edb()
                self.setups.append(siwave_dc)
            elif setup.type == "siwave_ac":
                siwave_ac = CfgSIwaveACSetup(self._pedb, setup, name=setup.name)
                siwave_ac.retrieve_parameters_from_edb()
                self.setups.append(siwave_ac)

    def __init__(self, pedb, setups_data):
        self._pedb = pedb
        self.setups = []
        for stp in setups_data:
            if stp["type"].lower() == "hfss":
                self.setups.append(CfgHFSSSetup(self._pedb, None, **stp))
            elif stp["type"].lower() in ["siwave_ac", "siwave_syz"]:
                self.setups.append(CfgSIwaveACSetup(self._pedb, None, **stp))
            elif stp["type"].lower() == "siwave_dc":
                self.setups.append(CfgSIwaveDCSetup(self._pedb, None, **stp))

    def apply(self):
        for s in self.setups:
            s.set_parameters_to_edb()

    def to_dict(self):
        return [i.to_dict() for i in self.setups]
