from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.utility.value import Value as GrpcValue

import pyedb.siwave_core.cpa.simulation_setup_data_model
from pyedb.siwave_core.cpa.simulation_setup_data_model import SIwaveCpaSetup, Vrm
from pyedb.siwave_core.product_properties import SIwaveProperties


class ChannelSetup:
    def __init__(self, pedb, cfg_channel_setup=None):
        self._pedb = pedb
        self.__init_values()
        if cfg_channel_setup:
            self._apply_cfg_object(cfg_channel_setup)

    def __init_values(self):
        self.die_name = ""
        self.pin_grouping_mode = "perpin"
        self.channel_component_exposure = {}

    def _apply_cfg_object(self, channel_setup):
        self.die_name = channel_setup.die_name
        self.channel_component_exposure = channel_setup.channel_component_exposure
        self.pin_grouping_mode = channel_setup.pin_grouping_mode
        self.vrm = channel_setup.vrm_setup if hasattr(channel_setup, "vrm_setup") else []  # type: ignore[union-attr]

    @property
    def die_name(self):
        return self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_DIE_NAME
        ).value

    @die_name.setter
    def die_name(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_DIE_NAME, value
        )

    @property
    def pin_grouping_mode(self):
        mode_mapping = {-1: "perpin", 0: "ploc", 1: "usediepingroups"}
        pg_mode = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_PIN_GROUPING_MODE
        ).value
        return mode_mapping[int(pg_mode.split(":")[1])] if pg_mode else "perpin"

    @pin_grouping_mode.setter
    def pin_grouping_mode(self, value):
        mapping = {"perpin": -1, "ploc": 0, "usediepingroups": 1}
        if isinstance(value, str):
            if not value in mapping:
                raise f"value {value} not supported, must be {list(mapping.keys())}"
            value = mapping[value]
        if not value in [-1, 0, 1]:
            raise f"wrong value {value}"
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_PIN_GROUPING_MODE, self.die_name + ":" + str(value)
        )

    @property
    def channel_component_exposure(self):
        cmp_exposure = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG
        ).value
        cmp_dict = {}
        for comp in cmp_exposure.split("*"):
            _comp = comp.split(":")
            cmp_dict[_comp[0]] = bool(_comp[1])
        return cmp_dict

    @channel_component_exposure.setter
    def channel_component_exposure(self, value):
        if not isinstance(value, dict):
            raise "Channel component exposure input must be a dictionary."
        channel_comp_exposure = ""
        for comp, enabled in value.items():
            if channel_comp_exposure:
                channel_comp_exposure += "*"
            channel_comp_exposure += f"{comp}:{int(enabled)}"
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG, channel_comp_exposure
        )

    @property
    def vrm(self):
        vrm = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_VRM_SETUP
        ).value
        vrm_list = []
        for _vrm in vrm.split("*"):
            vrm_obj = Vrm()
            _vrm_values = _vrm.split(":")
            if len(_vrm_values) != 4:
                raise ValueError(
                    f"Invalid VRM format: {_vrm}. Expected format is 'name:voltage:power_net:reference_net'."
                )
            vrm_obj.name = _vrm_values[0]
            vrm_obj.voltage = float(_vrm_values[1])
            vrm_obj.power_net = _vrm_values[2]
            vrm_obj.reference_net = _vrm_values[3]
            vrm_list.append(vrm_obj)
        return vrm_list

    @vrm.setter
    def vrm(self, value):
        if not isinstance(value, list):
            raise "vrm setter must have list as input."
        vrm_str = ""
        for vrm in value:
            if isinstance(vrm, pyedb.siwave_core.cpa.simulation_setup_data_model.Vrm):
                if vrm_str:
                    vrm_str += "*"
                vrm_str += vrm.name
                vrm_str += ":"
                vrm_str += str(vrm.voltage)
                vrm_str += ":"
                vrm_str += vrm.power_net
                vrm_str += ":"
                vrm_str += vrm.reference_net
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_VRM_SETUP, vrm_str
        )

    # vrm_setup: Vrm = None


class SolverOptions:
    def __init__(self, pedb, cfg_solver_options=None):
        self._pedb = pedb
        self.__init_values()
        if cfg_solver_options:
            self._apply_cfg_object(cfg_solver_options)

    def __init_values(
        self,
    ):
        self.mode = "si"
        self.custom_refinement = False
        self.extraction_frequency = "10Ghz"
        self.compute_capacitance = True
        self.compute_dc_rl = True
        self.compute_dc_parameters = True
        self.compute_dc_cg = True
        self.compute_ac_rl = True
        self.ground_power_nets_for_si = True
        self.small_hole_diameter = 0.0
        self.adaptive_refinement_cg_max_passes = 10
        self.adaptive_refinement_rl_max_passes = 10
        self.adaptive_refinement_cg_percent_error = 0.02
        self.adaptive_refinement_rl_percent_error = 0.02
        self.rl_percent_refinement_per_pass = 0.33
        self.cg_percent_refinement_per_pass = 0.33
        self.return_path_net_for_loop_parameters = True

    def _apply_cfg_object(self, solver_options):
        self.extraction_mode = solver_options.extraction_mode
        self.custom_refinement = solver_options.custom_refinement
        self.extraction_frequency = solver_options.extraction_frequency
        self.compute_capacitance = solver_options.compute_capacitance
        self.compute_dc_parameters = solver_options.compute_dc_parameters
        self.compute_dc_rl = solver_options.compute_dc_rl
        self.compute_dc_cg = solver_options.compute_dc_cg
        self.compute_ac_rl = solver_options.compute_ac_rl
        self.ground_power_nets_for_si = solver_options.ground_power_ground_nets_for_si
        self.small_hole_diameter = solver_options.small_hole_diameter
        self.adaptive_refinement_cg_max_passes = solver_options.cg_max_passes
        self.adaptive_refinement_rl_max_passes = solver_options.rl_max_passes
        self.adaptive_refinement_cg_percent_error = solver_options.cg_percent_error
        self.adaptive_refinement_rl_percent_error = solver_options.rl_percent_error
        self.rl_percent_refinement_per_pass = solver_options.rl_percent_refinement_per_pass
        self.return_path_net_for_loop_parameters = solver_options.return_path_net_for_loop_parameters

    @property
    def extraction_mode(self):
        mode = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_MODE
        ).value
        if mode == "1":
            return "si"
        return "pi"

    @extraction_mode.setter
    def extraction_mode(self, value):
        if value == "si":
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_MODE, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_MODE, "0"
            )

    @property
    def custom_refinement(self):
        refine = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CUSTOM_REFINEMENT
        ).value
        if refine == "1":
            return True
        return False

    @custom_refinement.setter
    def custom_refinement(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CUSTOM_REFINEMENT, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CUSTOM_REFINEMENT, "0"
            )

    @property
    def extraction_frequency(self):
        return self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_FREQUENCY
        ).value

    @extraction_frequency.setter
    def extraction_frequency(self, value):
        freq = str(GrpcValue(value))
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_FREQUENCY, freq
        )

    @property
    def compute_capacitance(self):
        compute = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_CAPACITANCE
        ).value
        if compute == "1":
            return True
        return False

    @compute_capacitance.setter
    def compute_capacitance(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_CAPACITANCE, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_CAPACITANCE, "0"
            )

    @property
    def compute_dc_parameters(self):
        compute = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_DC_PARAMS
        ).value
        if compute == "1":
            return True
        return False

    @compute_dc_parameters.setter
    def compute_dc_parameters(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_DC_PARAMS, "1"
            )
        else:
            self._pedb.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_DC_PARAMS, "0"
            )

    @property
    def compute_dc_rl(self):
        _res = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL
        ).value
        if _res == "1":
            return True
        return False

    @compute_dc_rl.setter
    def compute_dc_rl(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL, "0"
            )

    @property
    def compute_dc_cg(self):
        _res = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG
        ).value
        if _res == "1":
            return True
        return False

    @compute_dc_cg.setter
    def compute_dc_cg(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG, "0"
            )

    @property
    def compute_ac_rl(self):
        _res = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL
        ).value
        if _res == "1":
            return True
        return False

    @compute_ac_rl.setter
    def compute_ac_rl(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL, "0"
            )

    @property
    def ground_power_nets_for_si(self):
        _res = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI
        ).value
        if _res == "1":
            return True
        return False

    @ground_power_nets_for_si.setter
    def ground_power_nets_for_si(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI, "0"
            )

    @property
    def small_hole_diameter(self):
        _res = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER
        ).value
        if _res == "-1":
            return "auto"
        else:
            return float(_res)

    @small_hole_diameter.setter
    def small_hole_diameter(self, value):
        if value == "auto" or value == -1:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER, "-1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER, str(GrpcValue(value))
            )

    @property
    def model_type(self):
        return self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_MODEL_TYPE
        ).value

    @model_type.setter
    def model_type(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_MODEL_TYPE, value.lower()
        )

    @property
    def adaptive_refinement_cg_max_passes(self):
        return int(
            self._pedb.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES
            ).value
        )

    @adaptive_refinement_cg_max_passes.setter
    def adaptive_refinement_cg_max_passes(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES, str(int(value))
        )

    @property
    def adaptive_refinement_cg_percent_error(self):
        return float(
            self._pedb.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR
            ).value
        )

    @adaptive_refinement_cg_percent_error.setter
    def adaptive_refinement_cg_percent_error(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR, str(float(value))
        )

    @property
    def cg_percent_refinement_per_pass(self):
        return float(
            self._pedb.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS
            ).value
        )

    @cg_percent_refinement_per_pass.setter
    def cg_percent_refinement_per_pass(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS,
            str(float(value)),
        )

    @property
    def adaptive_refinement_rl_max_passes(self):
        return int(
            float(
                self._pedb.active_cell.get_product_property(
                    GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES
                ).value
            )
        )

    @adaptive_refinement_rl_max_passes.setter
    def adaptive_refinement_rl_max_passes(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES, str(float(value))
        )

    @property
    def adaptive_refinement_rl_percent_error(self):
        return float(
            self._pedb.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR
            ).value
        )

    @adaptive_refinement_rl_percent_error.setter
    def adaptive_refinement_rl_percent_error(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR, str(float(value))
        )

    @property
    def rl_percent_refinement_per_pass(self):
        return float(
            self._pedb.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS
            ).value
        )

    @rl_percent_refinement_per_pass.setter
    def rl_percent_refinement_per_pass(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS,
            str(float(value)),
        )

    @property
    def return_path_net_for_loop_parameters(self):
        _res = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_RETURN_PATH_NET_FOR_LOOP_PARAMS
        ).value
        if _res == "1":
            return True
        return False

    @return_path_net_for_loop_parameters.setter
    def return_path_net_for_loop_parameters(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_RETURN_PATH_NET_FOR_LOOP_PARAMS, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_RETURN_PATH_NET_FOR_LOOP_PARAMS, "0"
            )


class SIWaveCPASimulationSetup:
    def __init__(self, pedb, name=None, siwave_cpa_setup_class=None):
        self._pedb = pedb
        self._channel_setup = ChannelSetup(pedb)
        self._solver_options = SolverOptions(pedb)
        if isinstance(siwave_cpa_setup_class, SIwaveCpaSetup):
            self._apply_cfg_object(siwave_cpa_setup_class)
        else:
            self.__init_values()

        if (
            not self._pedb.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE,
                SIwaveProperties.CPA_SIM_NAME,
            )
            == name
        ):
            self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME, name)

    def __init_values(self):
        self.mode = "channel"
        self.model_type = "rlcg"
        self.use_q3d_solver = False
        self.net_processing_mode = "all"

    def _apply_cfg_object(self, siwave_cpa_setup_class):
        if isinstance(siwave_cpa_setup_class, SIwaveCpaSetup):
            self.name = siwave_cpa_setup_class.name
            self.mode = siwave_cpa_setup_class.mode
            self.nets_to_process = siwave_cpa_setup_class.nets_to_process
            self.model_type = siwave_cpa_setup_class.model_type
            self.use_q3d_solver = siwave_cpa_setup_class.use_q3d_solver
            self.net_processing_mode = siwave_cpa_setup_class.net_processing_mode
            self.channel_setup = ChannelSetup(self._pedb, siwave_cpa_setup_class.channel_setup)
            self.solver_options = SolverOptions(self._pedb, siwave_cpa_setup_class.solver_options)

    @property
    def name(self) -> str:
        return self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME
        ).value

    @name.setter
    def name(self, value):
        self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME, value)

    @property
    def mode(self):
        cpa_mode = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_SETUP
        ).value
        if cpa_mode == "1":
            return "channel"
        return "no_channel"

    @mode.setter
    def mode(self, value):
        if value == "channel":
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_SETUP, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_SETUP, "0"
            )

    @property
    def model_type(self):
        mod_type = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ESD_R_MODEL
        ).value
        if mod_type == "0":
            return "rlcg"
        else:
            return "esd_r"

    @model_type.setter
    def model_type(self, value):
        if value == "rlcg":
            self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ESD_R_MODEL, "0")
        elif value == "esd_r":
            self._pedb.active_cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ESD_R_MODEL, "1")

    @property
    def use_q3d_solver(self):
        return bool(
            int(
                self._pedb.active_cell.get_product_property(
                    GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_USE_Q3D_SOLVER
                ).value
            )
        )

    @use_q3d_solver.setter
    def use_q3d_solver(self, value):
        if value:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_USE_Q3D_SOLVER, "1"
            )
        else:
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_USE_Q3D_SOLVER, "0"
            )

    @property
    def net_processing_mode(self):
        return self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_NET_PROCESSING_MODE
        ).value

    @net_processing_mode.setter
    def net_processing_mode(self, value):
        self._pedb.active_cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_NET_PROCESSING_MODE, str(value)
        )

    @property
    def channel_setup(self):
        return self._channel_setup

    @channel_setup.setter
    def channel_setup(self, value):
        if isinstance(value, ChannelSetup):
            self._channel_setup = value

    @property
    def solver_options(self):
        return self._solver_options

    @solver_options.setter
    def solver_options(self, value):
        if isinstance(value, SolverOptions):
            self._solver_options = value

    @property
    def nets_to_process(self):
        nets = self._pedb.active_cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_NETS_TO_PROCESS
        ).value
        return nets.split("*")

    @nets_to_process.setter
    def nets_to_process(self, value):
        if isinstance(value, list):
            nets = "*".join(value)
            self._pedb.active_cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_NETS_TO_PROCESS, nets
            )
        else:
            raise TypeError("nets_to_process must be a list of strings.")
