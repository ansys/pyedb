import json

from pyedb.generic.general_methods import (
    pyedb_function_handler,
)


class Configuration:
    """Enables export and import of a JSON configuration file that can be applied to a new or existing design."""

    def __init__(self, pedb):
        self._pedb = pedb

    @pyedb_function_handler
    def load(self, config_file):
        """Import configuration settings from a JSON file and apply it to the current design.

        Parameters
        ----------
        config_file : str
            Full path to json file.

        Returns
        -------
        dict
            Config dictionary.
        """

        components = self._pedb.components.components
        with open(config_file, "r") as f:
            data = json.load(f)

        json_components = data["components"] if "components" in data else []
        for comp in json_components:
            refdes = comp["reference_designator"]
            part_type = comp["part_type"].lower()
            if part_type == "resistor":
                part_type = "Resistor"
            elif part_type == "capacitor":
                part_type = "Capacitor"
            elif part_type == "io":
                part_type = "IO"
            elif part_type == "ic":
                part_type = "IC"
            else:
                part_type = "Other"

            comp_layout = components[refdes]
            comp_layout.type = part_type

            if part_type in ["Resistor", "Capacitor", "Inductor"]:
                comp_layout.is_enabled = comp["enabled"]
                rlc_model = comp["rlc_model"] if "rlc_model" in comp else None
                # n_port_model = comp["NPortModel"] if "NPortModel" in comp else None
                # netlist_model = comp["NetlistModel"] if "NetlistModel" in comp else None
                # spice_model = comp["SpiceModel"] if "SpiceModel" in comp else None

                if rlc_model:
                    model_layout = comp_layout.model

                    pin_pairs = rlc_model["pin_pairs"] if "pin_pairs" in rlc_model else None
                    if pin_pairs:
                        for pp in model_layout.pin_pairs:
                            model_layout.delete_pin_pair_rlc(pp)

                        for pp in pin_pairs:
                            rlc_model_type = pp["type"]
                            p1 = pp["p1"]
                            p2 = pp["p2"]

                            r = pp["resistance"] if "resistance" in pp else None
                            l = pp["inductance"] if "inductance" in pp else None
                            c = pp["capacitance"] if "capacitance" in pp else None

                            pin_pair = self._pedb.edb_api.utility.PinPair(p1, p2)
                            rlc = self._pedb.edb_api.utility.Rlc()

                            rlc.IsParallel = False if rlc_model_type == "series" else True
                            if not r is None:
                                rlc.REnabled = True
                                rlc.R = self._pedb.edb_value(r)
                            else:
                                rlc.REnabled = False

                            if not l is None:
                                rlc.LEnabled = True
                                rlc.L = self._pedb.edb_value(l)
                            else:
                                rlc.LEnabled = False

                            if not c is None:
                                rlc.CEnabled = True
                                rlc.C = self._pedb.edb_value(c)
                            else:
                                rlc.CEnabled = False

                            model_layout.set_pin_pair_rlc(pin_pair, rlc)
                        comp_layout.model = model_layout

            # Configure port properties
            port_properties = comp["port_properties"] if "port_properties" in comp else None
            if port_properties:
                ref_offset = port_properties["reference_offset"]
                ref_size_auto = port_properties["reference_size_auto"]
                ref_size_x = port_properties["reference_size_x"]
                ref_size_y = port_properties["reference_size_y"]
            else:
                ref_offset = 0
                ref_size_auto = True
                ref_size_x = 0
                ref_size_y = 0

            # Configure solder ball properties
            solder_ball_properties = comp["solder_ball_properties"] if "solder_ball_properties" in comp else None
            if solder_ball_properties:
                shape = solder_ball_properties["shape"]
                diameter = solder_ball_properties["diameter"]
                mid_diameter = (
                    solder_ball_properties["mid_diameter"] if "mid_diameter" in solder_ball_properties else diameter
                )
                height = solder_ball_properties["height"]

                self._pedb.components.set_solder_ball(
                    component=refdes,
                    sball_diam=diameter,
                    sball_mid_diam=mid_diameter,
                    sball_height=height,
                    shape=shape,
                    auto_reference_size=ref_size_auto,
                    reference_height=ref_offset,
                    reference_size_x=ref_size_x,
                    reference_size_y=ref_size_y,
                )

            # Configure ports
            if "ports" in comp:
                for port in comp["ports"]:
                    port_type = port["type"]
                    pos = port["from"]
                    if "pin" in pos:
                        pin_name = pos["pin"]
                        port_name = "{}_{}".format(refdes, pin_name)
                        pos_terminal = comp_layout.pins[pin_name].get_terminal(port_name, True)
                    else:  # Net
                        net_name = pos["net"]
                        port_name = "{}_{}".format(refdes, net_name)
                        if port_type == "circuit":
                            pg_name = "pg_{}".format(port_name)
                            _, pg = self._pedb.siwave.create_pin_group_on_net(refdes, net_name, pg_name)
                            pos_terminal = pg.get_terminal(port_name, True)
                        else:  # Coax port
                            for _, p in comp_layout.pins.items():
                                if p.net_name == net_name:
                                    pos_terminal = p.get_terminal(port_name, True)
                                    break

                    if port_type == "circuit":
                        neg = port["to"]
                        if "pin" in neg:
                            pin_name = neg["pin"]
                            port_name = "{}_{}_ref".format(refdes, pin_name)
                            neg_terminal = comp_layout.pins[pin_name].get_terminal(port_name, True)
                        else:
                            net_name = neg["net"]
                            port_name = "{}_{}_ref".format(refdes, net_name)
                            pg_name = "pg_{}".format(port_name)
                            if pg_name not in self._pedb.siwave.pin_groups:
                                _, pg = self._pedb.siwave.create_pin_group_on_net(refdes, net_name, pg_name)
                            else:
                                pg = self._pedb.siwave.pin_groups[pg_name]
                            neg_terminal = pg.get_terminal(port_name, True)

                        self._pedb.create_port(pos_terminal, neg_terminal, True)
                    else:
                        self._pedb.create_port(pos_terminal)

            # Configure sources
            if "sources" in comp:
                for src in comp["sources"]:
                    src_type = src["type"]
                    pos = src["from"]
                    if "pin" in pos:
                        pin_name = pos["pin"]
                        src_name = "{}_{}".format(refdes, pin_name)
                        pos_terminal = comp_layout.pins[pin_name].get_terminal(src_name, True)
                    else:  # Net
                        net_name = pos["net"]
                        src_name = "{}_{}".format(refdes, net_name)
                        pg_name = "pg_{}".format(src_name)
                        _, pg = self._pedb.siwave.create_pin_group_on_net(refdes, net_name, pg_name)
                        pos_terminal = pg.get_terminal(src_name, True)

                    neg = src["to"]
                    if "pin" in neg:
                        pin_name = neg["pin"]
                        src_name = "{}_{}_ref".format(refdes, pin_name)
                        neg_terminal = comp_layout.pins[pin_name].get_terminal(src_name, True)
                    else:
                        net_name = neg["net"]
                        src_name = "{}_{}_ref".format(refdes, net_name)
                        pg_name = "pg_{}".format(src_name)
                        if pg_name not in self._pedb.siwave.pin_groups:
                            _, pg = self._pedb.siwave.create_pin_group_on_net(refdes, net_name, pg_name)
                        else:
                            pg = self._pedb.siwave.pin_groups[pg_name]
                        neg_terminal = pg.get_terminal(src_name, True)

                    if src_type == "voltage":
                        src_obj = self._pedb.create_voltage_source(pos_terminal, neg_terminal)
                        src_obj.magnitude = src["magnitude"]
                    elif src_type == "current":
                        src_obj = self._pedb.create_current_source(pos_terminal, neg_terminal)
                        src_obj.magnitude = src["magnitude"]

        # Configure HFSS setup
        setups = data["setups"] if "setups" in data else []
        for setup in setups:
            setup_type = setup["type"]

            edb_setup = None
            name = setup["name"]

            if setup_type.lower() == "siwave_dc":
                edb_setup = self._pedb.create_siwave_dc_setup(name)
                edb_setup.set_dc_slider = setup["dc_slider_position"]
            else:
                if setup_type.lower() == "hfss":
                    edb_setup = self._pedb.create_hfss_setup(name)
                    edb_setup.set_solution_single_frequency(
                        setup["f_adapt"], max_num_passes=setup["max_num_passes"], max_delta_s=setup["max_mag_delta_s"]
                    )
                elif setup_type.lower() == "siwave_syz":
                    name = setup["name"]
                    edb_setup = self._pedb.create_siwave_syz_setup(name)
                    edb_setup.si_slider_position = setup["si_slider_position"]

                if "freq_sweep" in setup:
                    for fsweep in setup["freq_sweep"]:
                        frequencies = fsweep["frequencies"]
                        freqs = []

                        for d in frequencies:
                            if d["distribution"] == "linear_step":
                                freqs.append(
                                    [
                                        "linear scale",
                                        self._pedb.edb_value(d["Start"]).ToString(),
                                        self._pedb.edb_value(d["Stop"]).ToString(),
                                        self._pedb.edb_value(d["Step"]).ToString(),
                                    ]
                                )
                            elif d["distribution"] == "linear_count":
                                freqs.append(
                                    [
                                        "linear count",
                                        self._pedb.edb_value(d["start"]).ToString(),
                                        self._pedb.edb_value(d["stop"]).ToString(),
                                        int(d["points"]),
                                    ]
                                )
                            elif d["distribution"] == "log_scale":
                                freqs.append(
                                    [
                                        "log scale",
                                        self._pedb.edb_value(d["start"]).ToString(),
                                        self._pedb.edb_value(d["stop"]).ToString(),
                                        int(d["samples"]),
                                    ]
                                )

                        edb_setup.add_frequency_sweep(
                            fsweep["name"],
                            frequency_sweep=freqs,
                        )

        # Configure stackup
        stackup = data["stackup"] if "stackup" in data else None
        if stackup:
            materials = stackup["materials"] if "materials" in stackup else []
            materials_reformatted = {}
            for mat in materials:
                new_mat = {}
                new_mat["name"] = mat["name"]
                if "conductivity" in mat:
                    new_mat["conductivity"] = mat["conductivity"]
                if "permittivity" in mat:
                    new_mat["permittivity"] = mat["permittivity"]
                if "dielectricLoss_tangent" in mat:
                    new_mat["loss_tangent"] = mat["dielectricLoss_tangent"]

                materials_reformatted[mat["name"]] = new_mat

            layers = stackup["layers"]
            layers_reformatted = {}

            for l in layers:
                lyr = {
                    "name": l["name"],
                    "type": l["type"],
                    "material": l["material"],
                    "thickness": l["thickness"],
                }
                if "fill_material" in l:
                    lyr["dielectric_fill"] = l["fill_material"]
                layers_reformatted[l["name"]] = lyr
            stackup_reformated = {"layers": layers_reformatted, "materials": materials_reformatted}
            self._pedb.stackup.load(stackup_reformated)

        return data
