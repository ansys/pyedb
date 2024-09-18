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

from ansys.edb.core.hierarchy.component_group import (
    ComponentGroup as GrpcComponentGroup,
)
from ansys.edb.core.terminal.terminals import BoundaryType as GrpcBoundaryType
from ansys.edb.core.utility.rlc import Rlc as GrpcRlc
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.edb_core.components import Component
from pyedb.grpc.edb_core.hierarchy.pingroup import PinGroup
from pyedb.grpc.edb_core.primitive.padstack_instances import PadstackInstance
from pyedb.grpc.edb_core.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.edb_core.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.grpc.edb_core.utility.sources import Source, SourceType


class Excitations:
    def __init__(self, pedb):
        self._pedb = pedb
        self._logger = pedb._logger

    def create_source_on_component(self, sources=None):
        """Create voltage, current source, or resistor on component.

        Parameters
        ----------
        sources : list[Source]
            List of ``pyedb.grpc.utility.sources.Source`` objects.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if not sources:  # pragma: no cover
            return False
        if isinstance(sources, Source):  # pragma: no cover
            sources = [sources]
        if isinstance(sources, list):  # pragma: no cover
            for src in sources:
                if not isinstance(src, Source):  # pragma: no cover
                    self._pedb.logger.error("List of source objects must be passed as an argument.")
                    return False
        for source in sources:
            positive_pins = self._pedb.padstack.get_instances(source.positive_node.component, source.positive_node.net)
            negative_pins = self._pedb.padstack.get_instances(source.negative_node.component, source.negative_node.net)
            positive_pin_group = self._pedb.components.create_pingroup_from_pins(positive_pins)
            if not positive_pin_group:  # pragma: no cover
                return False
            positive_pin_group = self._pedb.siwave.pin_groups[positive_pin_group.name]
            negative_pin_group = self._pedb.components.create_pingroup_from_pins(negative_pins)
            if not negative_pin_group:  # pragma: no cover
                return False
            negative_pin_group = self._pedb.siwave.pin_groups[negative_pin_group.GetName()]
            if source.source_type == SourceType.Vsource:  # pragma: no cover
                positive_pin_group_term = self._pedb.components._create_pin_group_terminal(
                    positive_pin_group,
                )
                negative_pin_group_term = self._pedb.components._create_pin_group_terminal(
                    negative_pin_group, isref=True
                )
                positive_pin_group_term.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
                negative_pin_group_term.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
                term_name = source.name
                positive_pin_group_term.SetName(term_name)
                negative_pin_group_term.SetName("{}_ref".format(term_name))
                positive_pin_group_term.source_amplitude = GrpcValue(source.amplitude)
                negative_pin_group_term.source_amplitude = GrpcValue(source.amplitude)
                positive_pin_group_term.source_phase = GrpcValue(source.phase)
                negative_pin_group_term.source_phase = GrpcValue(source.phase)
                positive_pin_group_term.impedance = GrpcValue(source.impedance)
                negative_pin_group_term.impedance = GrpcValue(source.impedance)
                positive_pin_group_term.reference_terminal = negative_pin_group_term
            elif source.source_type == SourceType.Isource:  # pragma: no cover
                positive_pin_group_term = self._pedb.components._create_pin_group_terminal(
                    positive_pin_group,
                )
                negative_pin_group_term = self._pedb.components._create_pin_group_terminal(
                    negative_pin_group, isref=True
                )
                positive_pin_group_term.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
                negative_pin_group_term.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
                positive_pin_group_term.name = source.name
                negative_pin_group_term.name = "{}_ref".format(source.name)
                positive_pin_group_term.source_amplitude = GrpcValue(source.amplitude)
                negative_pin_group_term.source_amplitude = GrpcValue(source.amplitude)
                positive_pin_group_term.source_phase = GrpcValue(source.phase)
                negative_pin_group_term.source_phase = GrpcValue(source.phase)
                positive_pin_group_term.impedance = GrpcValue(source.impedance)
                negative_pin_group_term.impedance = GrpcValue(source.impedance)
                positive_pin_group_term.reference_terminal = negative_pin_group_term
            elif source.source_type == SourceType.Rlc:  # pragma: no cover
                self._pedb.components.create(
                    pins=[positive_pins[0], negative_pins[0]],
                    component_name=source.name,
                    is_rlc=True,
                    r_value=source.r_value,
                    l_value=source.l_value,
                    c_value=source.c_value,
                )
        return True

    def create_port_on_pins(
        self,
        refdes,
        pins,
        reference_pins,
        impedance=50.0,
        port_name=None,
        pec_boundary=False,
        pingroup_on_single_pin=False,
    ):
        """Create circuit port between pins and reference ones.

        Parameters
        ----------
        refdes : Component reference designator
            str or EDBComponent object.
        pins : pin name where the terminal has to be created. Single pin or several ones can be provided.If several
        pins are provided a pin group will is created. Pin names can be the EDB name or the EDBPadstackInstance one.
        For instance the pin called ``Pin1`` located on component ``U1``, ``U1-Pin1`` or ``Pin1`` can be provided and
        will be handled.
            str, [str], EDBPadstackInstance, [EDBPadstackInstance]
        reference_pins : reference pin name used for terminal reference. Single pin or several ones can be provided.
        If several pins are provided a pin group will is created. Pin names can be the EDB name or the
        EDBPadstackInstance one. For instance the pin called ``Pin1`` located on component ``U1``, ``U1-Pin1``
        or ``Pin1`` can be provided and will be handled.
            str, [str], EDBPadstackInstance, [EDBPadstackInstance]
        impedance : Port impedance
            str, float
        port_name : str, optional
            Port name. The default is ``None``, in which case a name is automatically assigned.
        pec_boundary : bool, optional
        Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
        a perfect short is created between the pin and impedance is ignored. This
        parameter is only supported on a port created between two pins, such as
        when there is no pin group.
        pingroup_on_single_pin : bool
            If ``True`` force using pingroup definition on single pin to have the port created at the pad center. If
            ``False`` the port is created at the pad edge. Default value is ``False``.

        Returns
        -------
        EDB terminal created, or False if failed to create.

        Example:
        >>> from pyedb import Edb
        >>> edb = Edb(path_to_edb_file)
        >>> pin = "AJ6"
        >>> ref_pins = ["AM7", "AM4"]
        Or to take all reference pins
        >>> ref_pins = [pin for pin in list(edb.components["U2A5"].pins.values()) if pin.net_name == "GND"]
        >>> edb.components.create_port_on_pins(refdes="U2A5", pins=pin, reference_pins=ref_pins)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """

        if isinstance(pins, str):
            pins = [pins]
        elif isinstance(pins, PadstackInstance):
            pins = [pins.name]
        if not reference_pins:
            self._logger.error("No reference pin provided.")
            return False
        if isinstance(reference_pins, str):
            reference_pins = [reference_pins]
        if isinstance(reference_pins, list):
            _temp = []
            for ref_pin in reference_pins:
                if isinstance(ref_pin, int):
                    if ref_pin in self._pedb.padstack.instances:
                        _temp.append(self._pedb.padstack.instances[ref_pin])
                elif isinstance(ref_pin, str):
                    if ref_pin in self._pedb.padstack.instances[refdes].pins:
                        _temp.append(self._pedb.padstack.instances[refdes].pins[ref_pin])
                    else:
                        p = [pp for pp in list(self._pedb.padstack.instances.values()) if pp.name == ref_pin]
                        if p:
                            _temp.append(p)
                elif isinstance(ref_pin, PadstackInstance):
                    _temp.append(ref_pin.name)
            reference_pins = _temp
        elif isinstance(reference_pins, int):
            if reference_pins in self._pedb.padstack.instances:
                reference_pins = self._pedb.padstack.instances[reference_pins]
        if isinstance(refdes, str):
            refdes = self._pedb.padstack.instances[refdes]
        elif isinstance(refdes, GrpcComponentGroup):
            refdes = Component(self._pedb, refdes)
        refdes_pins = refdes.pins
        if any(refdes.rlc_values):
            return self._pedb.components.deactivate_rlc_component(component=refdes, create_circuit_port=True)
        if len([pin for pin in pins if isinstance(pin, str)]) == len(pins):
            cmp_pins = []
            for pin_name in pins:
                cmp_pins = [pin for pin in list(refdes_pins.values()) if pin_name == pin.name]
                if not cmp_pins:
                    for pin in list(refdes_pins.values()):
                        if pin.name and "-" in pin.name:
                            if pin_name == pin.name.split("-")[1]:
                                cmp_pins.append(pin)
            if not cmp_pins:
                self._logger.warning("No pin found during port creation. Port is not defined.")
                return
            pins = cmp_pins
        if not len([pin for pin in pins if isinstance(pin, PadstackInstance)]) == len(pins):
            self._logger.error("Pin list must contain only pins instances")
            return False
        if not port_name:
            port_name = "Port_{}_{}".format(pins[0].net_name, pins[0].name)
        if len([pin for pin in reference_pins if isinstance(pin, str)]) == len(reference_pins):
            ref_cmp_pins = []
            for ref_pin_name in reference_pins:
                if ref_pin_name in refdes_pins:
                    ref_cmp_pins.append(refdes_pins[ref_pin_name])
                elif "-" in ref_pin_name:
                    if ref_pin_name.split("-")[1] in refdes_pins:
                        ref_cmp_pins.append(refdes_pins[ref_pin_name.split("-")[1]])
            if not ref_cmp_pins:
                self._logger.error("No reference pins found.")
                return False
            reference_pins = ref_cmp_pins
        if len(pins) > 1 or pingroup_on_single_pin:
            pec_boundary = False
            self._logger.info(
                "Disabling PEC boundary creation, this feature is supported on single pin "
                "ports only, {} pins found".format(len(pins))
            )
            group_name = "group_{}".format(port_name)
            pin_group = self._pedb.components.create_pingroup_from_pins(pins, group_name)
            term = self._pedb.components._create_pin_group_terminal(pingroup=pin_group, term_name=port_name)

        else:
            term = self._pedb.components._create_terminal(pins[0], term_name=port_name)
        term.is_circuit_port = True
        if len(reference_pins) > 1 or pingroup_on_single_pin:
            pec_boundary = False
            self._logger.info(
                "Disabling PEC boundary creation. This feature is supported on single pin"
                "ports only {} reference pins found.".format(len(reference_pins))
            )
            ref_group_name = "group_{}_ref".format(port_name)
            ref_pin_group = self._pedb.components.create_pingroup_from_pins(reference_pins, ref_group_name)
            ref_pin_group = self._pedb.siwave.pin_groups[ref_pin_group.name]
            ref_term = self._pedb.components._create_pin_group_terminal(
                pingroup=ref_pin_group, term_name=port_name + "_ref"
            )

        else:
            ref_term = self._pedb.components._create_terminal(
                reference_pins[0].primitive_object, term_name=port_name + "_ref"
            )
        ref_term.is_circuit_port = True
        term.impedance = GrpcValue(impedance)
        term.reference_terminal = ref_term
        if pec_boundary:
            term.is_circuit_port = False
            ref_term.is_circuit_port = False
            term.boundary_type = GrpcBoundaryType.PEC
            ref_term.boundary_type = GrpcBoundaryType.PEC
            self._logger.info(
                "PEC boundary created between pin {} and reference pin {}".format(pins[0].name, reference_pins[0].name)
            )
        if term:
            return term
        return False

    def create_port_on_component(
        self,
        component,
        net_list,
        port_type=SourceType.CoaxPort,
        do_pingroup=True,
        reference_net="gnd",
        port_name=None,
        solder_balls_height=None,
        solder_balls_size=None,
        solder_balls_mid_size=None,
        extend_reference_pins_outside_component=False,
    ):
        """Create ports on a component.

        Parameters
        ----------
        component : str or  self._pedb.component
            EDB component or str component name.
        net_list : str or list of string.
            List of nets where ports must be created on the component.
            If the net is not part of the component, this parameter is skipped.
        port_type : SourceType enumerator, CoaxPort or CircuitPort
            Type of port to create. ``CoaxPort`` generates solder balls.
            ``CircuitPort`` generates circuit ports on pins belonging to the net list.
        do_pingroup : bool
            True activate pingroup during port creation (only used with combination of CircPort),
            False will take the closest reference pin and generate one port per signal pin.
        refnet : string or list of string.
            list of the reference net.
        port_name : str
            Port name for overwriting the default port-naming convention,
            which is ``[component][net][pin]``. The port name must be unique.
            If a port with the specified name already exists, the
            default naming convention is used so that port creation does
            not fail.
        solder_balls_height : float, optional
            Solder balls height used for the component. When provided default value is overwritten and must be
            provided in meter.
        solder_balls_size : float, optional
            Solder balls diameter. When provided auto evaluation based on padstack size will be disabled.
        solder_balls_mid_size : float, optional
            Solder balls mid-diameter. When provided if value is different than solder balls size, spheroid shape will
            be switched.
        extend_reference_pins_outside_component : bool
            When no reference pins are found on the component extend the pins search with taking the closest one. If
            `do_pingroup` is `True` will be set to `False`. Default value is `False`.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> net_list = ["M_DQ<1>", "M_DQ<2>", "M_DQ<3>", "M_DQ<4>", "M_DQ<5>"]
        >>> edbapp.components.create_port_on_component(cmp="U2A5", net_list=net_list,
        >>> port_type=SourceType.CoaxPort, do_pingroup=False, refnet="GND")

        """
        if isinstance(component, str):
            component = self._pedb.components.instances[component]

        if not isinstance(net_list, list):
            net_list = [net_list]
        for net in net_list:
            if not isinstance(net, str):
                try:
                    net_name = net.name
                    if net_name != "":
                        net_list.append(net_name)
                except:
                    pass
        if reference_net in net_list:
            net_list.remove(reference_net)
        cmp_pins = [p for p in component.pins if p.net.name in net_list]
        for p in cmp_pins:  # pragma no cover
            p.is_layout_pin = True
        if len(cmp_pins) == 0:
            self._logger.info(
                "No pins found on component {}, searching padstack instances instead".format(component.GetName())
            )
            return False
        pin_layers = cmp_pins[0].padstack_def.data.get_layer_names()
        if port_type == SourceType.CoaxPort:
            if not solder_balls_height:
                solder_balls_height = self._pedb.components.instances[component.name].solder_ball_height
            if not solder_balls_size:
                solder_balls_size = self._pedb.components.instances[component.name].solder_ball_diameter[0]
            if not solder_balls_mid_size:
                solder_balls_mid_size = self._pedb.components.instances[component.name].solder_ball_diameter[1]
            ref_pins = [p for p in component.pins if p.net.name in reference_net]
            if not ref_pins:
                self._logger.error(
                    "No reference pins found on component. You might consider"
                    "using Circuit port instead since reference pins can be extended"
                    "outside the component when not found if argument extend_reference_pins_outside_component is True."
                )
                return False
            pad_params = self._pedb.padstack.get_pad_parameters(pin=cmp_pins[0], layername=pin_layers[0], pad_type=0)
            if not pad_params[0] == 7:
                if not solder_balls_size:  # pragma no cover
                    sball_diam = min([GrpcValue(val).value for val in pad_params[1]])
                    sball_mid_diam = sball_diam
                else:  # pragma no cover
                    sball_diam = solder_balls_size
                    if solder_balls_mid_size:
                        sball_mid_diam = solder_balls_mid_size
                    else:
                        sball_mid_diam = solder_balls_size
                if not solder_balls_height:  # pragma no cover
                    solder_balls_height = 2 * sball_diam / 3
            else:  # pragma no cover
                if not solder_balls_size:
                    bbox = pad_params[1]
                    sball_diam = min([abs(bbox[2] - bbox[0]), abs(bbox[3] - bbox[1])]) * 0.8
                else:
                    sball_diam = solder_balls_size
                if not solder_balls_height:
                    solder_balls_height = 2 * sball_diam / 3
                if solder_balls_mid_size:
                    sball_mid_diam = solder_balls_mid_size
                else:
                    sball_mid_diam = sball_diam
            sball_shape = "Cylinder"
            if not sball_diam == sball_mid_diam:
                sball_shape = "Spheroid"
            self._pedb.components.set_solder_ball(
                component=component,
                sball_height=solder_balls_height,
                sball_diam=sball_diam,
                sball_mid_diam=sball_mid_diam,
                shape=sball_shape,
            )
            for pin in cmp_pins:
                self._pedb.padstack.create_coax_port(padstackinstance=pin, name=port_name)

        elif port_type == SourceType.CircPort:  # pragma no cover
            ref_pins = [p for p in component.pins if p.net.name in reference_net]
            for p in ref_pins:
                p.is_layout_pin = True
            if not ref_pins:
                self._logger.warning("No reference pins found on component")
                if not extend_reference_pins_outside_component:
                    self._logger.warning(
                        "argument extend_reference_pins_outside_component is False. You might want "
                        "setting to True to extend the reference pin search outside the component"
                    )
                else:
                    do_pingroup = False
            if do_pingroup:
                if len(ref_pins) == 1:
                    ref_pins.is_pin = True
                    ref_pin_group_term = self._create_terminal(ref_pins[0])
                else:
                    for pin in ref_pins:
                        pin.is_pin = True
                    ref_pin_group = self.create_pingroup_from_pins(ref_pins)
                    if not ref_pin_group:
                        self._logger.error(f"Failed to create reference pin group on component {component.GetName()}.")
                        return False
                    ref_pin_group = self._pedb.siwave.pin_groups[ref_pin_group.GetName()]
                    ref_pin_group_term = self._create_pin_group_terminal(ref_pin_group, isref=False)
                    if not ref_pin_group_term:
                        self._logger.error(
                            f"Failed to create reference pin group terminal on component {component.GetName()}"
                        )
                        return False
                for net in net_list:
                    pins = [pin for pin in component.pins if pin.net.name == net]
                    if pins:
                        if len(pins) == 1:
                            pin_term = self._create_terminal(pins[0])
                            if pin_term:
                                pin_term.reference_terminal = ref_pin_group_term
                        else:
                            pin_group = self._pedb.components.create_pingroup_from_pins(pins)
                            if not pin_group:
                                return False
                            pin_group = self._pedb.siwave.pin_groups[pin_group.GetName()]
                            pin_group_term = self._create_pin_group_terminal(pin_group)
                            if pin_group_term:
                                pin_group_term.reference_terminal = ref_pin_group_term
                    else:
                        self._logger.info("No pins found on component {} for the net {}".format(component, net))
            else:
                for net in net_list:
                    pins = [pin for pin in component.pins if pin.net.name == net]
                    for pin in pins:
                        if ref_pins:
                            self.create_port_on_pins(component, pin, ref_pins)
                        else:
                            if extend_reference_pins_outside_component:
                                _pin = PadstackInstance(self._pedb, pin)
                                ref_pin = _pin.get_reference_pins(
                                    reference_net=reference_net[0],
                                    max_limit=1,
                                    component_only=False,
                                    search_radius=3e-3,
                                )
                                if ref_pin:
                                    self.create_port_on_pins(component, [pin.name], ref_pin[0].id)
                            else:
                                self._logger.error("Skipping port creation no reference pin found.")
        return True

    def _create_terminal(self, pin, term_name=None):
        """Create terminal on component pin.

        Parameters
        ----------
        pin : Edb padstack instance.

        term_name : Terminal name (Optional).
            str.

        Returns
        -------
        EDB terminal.
        """

        from_layer, _ = pin.get_layer_range()
        if term_name is None:
            term_name = "{}.{}.{}".format(pin.component.name, pin.name, pin.net.name)
        for term in list(self._pedb.active_layout.Terminals):
            if term.name == term_name:
                return term
        return PadstackInstanceTerminal.create(pin.layout, pin.net, term_name, pin, from_layer)

    def add_port_on_rlc_component(self, component=None, circuit_ports=True, pec_boundary=False):
        """Deactivate RLC component and replace it with a circuit port.
        The circuit port supports only two-pin components.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.

        circuit_ports : bool
            ``True`` will replace RLC component by circuit ports, ``False`` gap ports compatible with HFSS 3D modeler
            export.

        pec_boundary : bool, optional
            Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
            a perfect short is created between the pin and impedance is ignored. This
            parameter is only supported on a port created between two pins, such as
            when there is no pin group.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(component, str):  # pragma: no cover
            component = self._pedb.components.instances[component]
        if not isinstance(component, Component):  # pragma: no cover
            return False
        self._pedb.components.set_component_rlc(component.refdes)
        pins = self._pedb.padstacks.get_instances(component.refdes)
        if len(pins) == 2:  # pragma: no cover
            pin_layers = pins[0].get_pin_layer_range()
            pos_pin_term = PadstackInstanceTerminal.create(
                self._pedb._active_layout,
                pins[0].net,
                "{}_{}".format(component.name, pins[0].name),
                pins[0],
                pin_layers[0],
                False,
            )
            if not pos_pin_term:  # pragma: no cover
                return False
            neg_pin_term = PadstackInstanceTerminal.create(
                self._pedb._active_layout,
                pins[1].net,
                "{}_{}_ref".format(component.name, pins[1].name),
                pins[1],
                pin_layers[0],
                False,
            )
            if not neg_pin_term:  # pragma: no cover
                return False
            if pec_boundary:
                pos_pin_term.boundary_type = GrpcBoundaryType.PEC
                neg_pin_term.boundary_type = GrpcBoundaryType.PEC
            else:
                pos_pin_term.boundary_type = GrpcBoundaryType.PORT
                neg_pin_term.boundary_type = GrpcBoundaryType.PORT
            pos_pin_term.name = component.name
            pos_pin_term.reference_terminal = neg_pin_term
            if circuit_ports and not pec_boundary:
                pos_pin_term.is_circuit_port = True
                neg_pin_term.is_circuit_port = True
            elif pec_boundary:
                pos_pin_term.is_circuit_port = False
                neg_pin_term.is_circuit_port = False
            else:
                pos_pin_term.is_circuit_port = False
                neg_pin_term.is_circuit_port = False
            self._logger.info("Component {} has been replaced by port".format(component.refdes))
            return True
        return False

    def add_rlc_boundary(self, component=None, circuit_type=True):
        """Add RLC gap boundary on component and replace it with a circuit port.
        The circuit port supports only 2-pin components.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.
        circuit_type : bool
            When ``True`` circuit type are defined, if ``False`` gap type will be used instead (compatible with HFSS 3D
            modeler). Default value is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(component, str):  # pragma: no cover
            component = self._pedb.components.instances[component]
        if not isinstance(component, Component):  # pragma: no cover
            return False
        self._pedb.components.set_component_rlc(component.name)
        pins = component.pins
        if len(pins) == 2:  # pragma: no cover
            pin_layer = pins[0].get_layer_range()[0]
            pos_pin_term = PadstackInstanceTerminal.create(
                self._pedb._active_layout,
                pins[0].net,
                "{}_{}".format(component.name, pins[0].name),
                pins[0],
                pin_layer,
                False,
            )
            if not pos_pin_term:  # pragma: no cover
                return False
            neg_pin_term = PadstackInstanceTerminal.create(
                self._pedb._active_layout,
                pins[1].net,
                "{}_{}_ref".format(component.name, pins[1].name),
                pins[1],
                pin_layer,
                True,
            )
            if not neg_pin_term:  # pragma: no cover
                return False
            pos_pin_term.boundary_type = GrpcBoundaryType.RLC
            if not circuit_type:
                pos_pin_term.is_circuit_port = False
            else:
                pos_pin_term.is_circuit_port = True
            pos_pin_term.name = component.name
            neg_pin_term.boundary_type = GrpcBoundaryType.RLC
            if not circuit_type:
                neg_pin_term.is_circuit_port = False
            else:
                neg_pin_term.is_circuit_port = True
            pos_pin_term.reference_terminal = neg_pin_term
            rlc_values = component.rlc_values
            rlc = GrpcRlc()
            if rlc_values[0]:
                rlc.r_enabled = True
                rlc.r = GrpcValue(rlc_values[0])
            if rlc_values[1]:
                rlc.l_enabled = True
                rlc.l = GrpcValue(rlc_values[1])
            if rlc_values[2]:
                rlc.c_enabled = True
                rlc.c = GrpcValue(rlc_values[2])
            rlc.is_parallel = component.is_parallel_rlc
            pos_pin_term.rlc_boundary = rlc
            self._logger.info("Component {} has been replaced by port".format(component.refdes))
            return True

    def _create_pin_group_terminal(self, pingroup, isref=False, term_name=None, term_type="circuit"):
        """Creates an EDB pin group terminal from a given EDB pin group.

        Parameters
        ----------
        pingroup : Pin group.

        isref : bool
        Specify if this terminal a reference terminal.

        term_name : Terminal name (Optional). If not provided default name is Component name, Pin name, Net name.
            str.

        term_type: Type of terminal, gap, circuit or auto.
        str.
        Returns
        -------
        Edb pin group terminal.
        """
        if not isinstance(pingroup, PinGroup):
            self._logger.error(f"{pingroup} is not a PinGroup instance,")
            return False
        pin = pingroup.pins[0]
        if term_name is None:
            term_name = "{}.{}.{}".format(pin.component.name, pin.name, pin.net.name)
        for t in list(self._pedb.active_layout.Terminals):
            if t.name == term_name:
                self._logger.warning(
                    f"Terminal {term_name} already created in current layout. Returning the "
                    f"already defined one. Make sure to delete the terminal before to create a new one."
                )
                return t
        pingroup_term = PinGroupTerminal.create(
            layout=self._pedb._active_layout, name=term_name, net=pingroup.net, pin_group=pingroup, is_ref=isref
        )
        if term_type == "circuit" or "auto":
            pingroup_term.is_circuit_port = True
        return pingroup_term
