from dataclasses import dataclass

from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.siwave_core.cpa.simulation_setup_data_model import SIwaveCpaSetup
from pyedb.siwave_core.product_properties import SIwaveProperties


@dataclass
class Vrm:
    name: str = ""
    voltage: float = 0.0
    power_net: str = ""
    reference_net: str = ""


class ChannelSetup:
    def __init__(self, pedb):
        self._pedb = pedb
        self._vrm = Vrm(pedb)

    @property
    def die_name(self):
        return self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_DIE_NAME)

    @die_name.setter
    def die_name(self, value):
        self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_DIE_NAME, value)

    @property
    def pin_grouping_mode(self):
        mode_mapping = {-1: "perpin", 0: "ploc", 1: "usediepingroups"}
        pg_mode = self._pedb.cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_PIN_GROUPING_MODE, self.die_name
        )
        return mode_mapping[int(pg_mode)]

    @pin_grouping_mode.setter
    def pin_grouping_mode(self, value):
        mapping = {"perpin": -1, "ploc": 0, "usediepingroups": 1}
        if isinstance(value, str):
            if not value in mapping:
                raise f"value {value} not supported, must be {list(mapping.keys())}"
            value = mapping[value]
        if not value in [-1, 0, 1]:
            raise f"wrong value {value}"
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_PIN_GROUPING_MODE, self.die_name + ":" + str(value)
        )

    @property
    def channel_component_exposure(self):
        cmp_exposure = self._pedb.cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG
        )
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
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG, channel_comp_exposure
        )

    @property
    def vrm(self):
        vrm = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_VRM_SETUP)
        vrm_list = []
        for _vrm in vrm.split("*"):
            vrm_obj = Vrm()
            _vrm_values = _vrm.plit(":")
            vrm_obj.name = _vrm_values[0]
            vrm_obj.voltage = _vrm_values[1]
            vrm_obj.power_net = _vrm_values[2]
            vrm_obj.reference_net = _vrm_values[3]
            vrm_list.append(vrm_obj)
        return

    @vrm.setter
    def vrm(self, value):
        if not isinstance(value, list):
            raise "vrm setter must have list as input."
        vrm_str = ""
        for vrm in value:
            if isinstance(vrm, Vrm):
                if vrm_str:
                    vrm_str += "*"
                vrm_str += vrm.name
                vrm_str += str(vrm.voltage)
                vrm_str += vrm.power_net
                vrm_str += vrm.reference_net
        self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_VRM_SETUP, vrm_str)

    # vrm_setup: Vrm = None


class SolverOptions:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def mode(self):
        mode = bool(
            self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_MODE)
        )
        if mode == "1":
            return "si"
        return "pi"

    @mode.setter
    def mode(self, value):
        if value == "si":
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_MODE, "1")
        else:
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_MODE, "0")

    @property
    def custom_refinement(self):
        refine = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CUSTOM_REFINEMENT)
        if refine == "1":
            return True
        return False

    @custom_refinement.setter
    def custom_refinement(self, value):
        if value:
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CUSTOM_REFINEMENT, "1")
        else:
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CUSTOM_REFINEMENT, "0")

    @property
    def extraction_frequency(self):
        return self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_FREQUENCY)

    @extraction_frequency.setter
    def extraction_frequency(self, value):
        freq = str(GrpcValue(value))
        self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_EXTRACTION_FREQUENCY, freq)

    @property
    def compute_capacitance(self):
        compute = self._pedb.cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_CAPACITANCE
        )
        if compute == "1":
            return True
        return False

    @compute_capacitance.setter
    def compute_capacitance(self, value):
        if value:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_CAPACITANCE, "1"
            )
        else:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_CAPACITANCE, "0"
            )

    @property
    def compute_dc_parameters(self):
        compute = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_DC_PARAMS)
        if compute == "1":
            return True
        return False

    @compute_dc_parameters.setter
    def compute_dc_parameters(self, value):
        if value:
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_DC_PARAMS, "1")
        else:
            self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_COMPUTE_DC_PARAMS, "0")

    @property
    def compute_dc_rl(self):
        _res = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL)
        if _res == "1":
            return True
        return False

    @compute_dc_rl.setter
    def compute_dc_rl(self, value):
        if value:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL, "1"
            )
        else:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL, "0"
            )

    @property
    def compute_dc_cg(self):
        _res = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG)
        if _res == "1":
            return True
        return False

    @compute_dc_cg.setter
    def compute_dc_cg(self, value):
        if value:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG, "1"
            )
        else:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG, "0"
            )

    @property
    def compute_ac_rl(self):
        _res = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL)
        if _res == "1":
            return True
        return False

    @compute_ac_rl.setter
    def compute_ac_rl(self, value):
        if value:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL, "1"
            )
        else:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL, "0"
            )

    @property
    def ground_power_nets_for_si(self):
        _res = self._pedb.cell.get_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI
        )
        if _res == "1":
            return True
        return False

    @ground_power_nets_for_si.setter
    def ground_power_nets_for_si(self, value):
        if value:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI, "1"
            )
        else:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI, "0"
            )

    @property
    def small_hole_diameter(self):
        _res = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER)
        if _res == "-1":
            return -1
        else:
            return GrpcValue(_res).value

    @small_hole_diameter.setter
    def small_hole_diameter(self, value):
        if value == "auto" or value == -1:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER, "-1"
            )
        else:
            self._pedb.cell.set_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER, str(GrpcValue(value))
            )

    @property
    def model_type(self):
        return self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_MODEL_TYPE)

    @model_type.setter
    def model_type(self, value):
        self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_MODEL_TYPE, value.lower())

    @property
    def adaptive_refinement_cg_max_passes(self):
        return int(
            self._pedb.cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES
            )
        )

    @adaptive_refinement_cg_max_passes.setter
    def adaptive_refinement_cg_max_passes(self, value):
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES, str(int(value))
        )

    @property
    def adaptive_refinement_cg_percent_error(self):
        return float(
            self._pedb.cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR
            )
        )

    @adaptive_refinement_cg_percent_error.setter
    def adaptive_refinement_cg_percent_error(self, value):
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR, str(float(value))
        )

    @property
    def cg_percent_refinement_per_pass(self):
        return float(
            self._pedb.cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS
            )
        )

    @cg_percent_refinement_per_pass.setter
    def cg_percent_refinement_per_pass(self, value):
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS,
            str(float(value)),
        )

    @property
    def adaptive_refinement_rl_max_passes(self):
        return int(
            self._pedb.cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES
            )
        )

    @adaptive_refinement_rl_max_passes.setter
    def adaptive_refinement_rl_max_passes(self, value):
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES, str(float(value))
        )

    @property
    def adaptive_refinement_rl_percent_error(self):
        return float(
            self._pedb.cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR
            )
        )

    @adaptive_refinement_rl_percent_error.setter
    def adaptive_refinement_rl_percent_error(self, value):
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR, str(float(value))
        )

    @property
    def rl_percent_refinement_per_pass(self):
        return float(
            self._pedb.cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS
            )
        )

    @rl_percent_refinement_per_pass.setter
    def rl_percent_refinement_per_pass(self, value):
        self._pedb.cell.set_product_property(
            GrpcProductIdType.SIWAVE,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS,
            str(float(value)),
        )


class SIWaveCPASimulationSetup:
    def __init__(self, pedb, name=None, siwave_cpa_setup=None):
        self._pedb = pedb
        self._channel_setup = ChannelSetup(pedb)
        self._solver_options = SolverOptions(pedb)
        if isinstance(siwave_cpa_setup, SIwaveCpaSetup):
            pass

        if (
            not self._pedb.cell.get_product_property(
                GrpcProductIdType.SIWAVE,
                SIwaveProperties.CPA_SIM_NAME,
            )
            == name
        ):
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME, name)

    @property
    def name(self) -> str:
        return self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME)

    @name.setter
    def name(self, value):
        self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME, value)

    @property
    def mode(self):
        cpa_mode = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_SETUP)
        if cpa_mode == "1":
            return "channel"
        return "no_channel"

    @mode.setter
    def mode(self, value):
        if value == "channel":
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_SETUP, "1")
        else:
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_CHANNEL_SETUP, "0")

    @property
    def model_type(self):
        mod_type = self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ESD_R_MODEL)
        if mod_type == "0":
            return "rlcg"
        else:
            return "esd_r"

    @model_type.setter
    def model_type(self, value):
        if value == "rlcg":
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ESD_R_MODEL, "0")
        elif value == "esd_r":
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_ESD_R_MODEL, "1")

    @property
    def use_q3d(self):
        return bool(self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_USE_Q3D_SOLVER))

    @use_q3d.setter
    def use_q3d(self, value):
        if value:
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_USE_Q3D_SOLVER, "1")
        else:
            self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_USE_Q3D_SOLVER, "0")

    @property
    def net_processing_mode(self):
        if bool(self._pedb.cell.get_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_NETS_TO_PROCESS)):
            return "all"
        else:
            return "userdefined"

    @net_processing_mode.setter
    def net_processing_mode(self, value):
        self._pedb.cell.set_product_property(GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_NETS_TO_PROCESS, str(value))

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
