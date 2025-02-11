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

from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.component_group import (
    ComponentGroup as GrpcComponentGroup,
)
from ansys.edb.core.terminal.terminals import BoundaryType as GrpcBoundaryType
from ansys.edb.core.terminal.terminals import EdgeTerminal as GrpcEdgeTerminal
from ansys.edb.core.terminal.terminals import PrimitiveEdge as GrpcPrimitiveEdge
from ansys.edb.core.utility.rlc import Rlc as GrpcRlc
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.layers.stackup_layer import StackupLayer
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.ports.ports import BundleWavePort, WavePort
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.terminal.bundle_terminal import BundleTerminal
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.terminal.pingroup_terminal import PinGroupTerminal
from pyedb.grpc.database.terminal.point_terminal import PointTerminal
from pyedb.grpc.database.utility.sources import Source, SourceType
from pyedb.modeler.geometry_operators import GeometryOperators


class SourceExcitation:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def _logger(self):
        return self._pedb.logger

    @property
    def excitations(self):
        """Get all excitations."""
        return self._pedb.excitations

    @property
    def sources(self):
        """Get all sources."""
        return self._pedb.sources

    @property
    def probes(self):
        """Get all probes."""
        return self._pedb.probes

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
        from pyedb.grpc.database.components import Component

        if isinstance(pins, str):
            pins = [pins]
        elif isinstance(pins, PadstackInstance):
            pins = [pins.name]
        if not reference_pins:
            self._logger.error("No reference pin provided.")
            return False
        if isinstance(reference_pins, str):
            reference_pins = [reference_pins]
        elif isinstance(reference_pins, int):
            reference_pins = [reference_pins]
        elif isinstance(reference_pins, PadstackInstance):
            reference_pins = [reference_pins]
        if isinstance(reference_pins, list):
            _temp = []
            for ref_pin in reference_pins:
                if isinstance(ref_pin, int):
                    pins = self._pedb.padstacks.instances
                    reference_pins = [pins[ref_pin] for ref_pin in reference_pins if ref_pin in pins]
                    # if reference_pins in pins:
                    #     reference_pins = pins[reference_pins]
                elif isinstance(ref_pin, str):
                    component_pins = self._pedb.components.instances[refdes].pins
                    if ref_pin in component_pins:
                        _temp.append(component_pins[ref_pin])
                    else:
                        p = [pp for pp in list(self._pedb.padstack.instances.values()) if pp.name == ref_pin]
                        if p:
                            _temp.extend(p)
                elif isinstance(ref_pin, PadstackInstance):
                    _temp.append(ref_pin)
            reference_pins = _temp
        if isinstance(refdes, str):
            refdes = self._pedb.components.instances[refdes]
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
            pin = pins[0]
            if pin.net.is_null:
                pin_net_name = "no_net"
            else:
                pin_net_name = pin.net.name
            port_name = f"Port_{pin_net_name}_{refdes.name}_{pins[0].name}"

        ref_cmp_pins = []
        for ref_pin in reference_pins:
            if ref_pin.name in refdes_pins:
                ref_cmp_pins.append(ref_pin)
            elif "-" in ref_pin.name:
                if ref_pin.name.split("-")[1] in refdes_pins:
                    ref_cmp_pins.append(ref_pin)
            elif "via" in ref_pin.name:
                _ref_pin = [
                    pin for pin in list(self._pedb.padstacks.instances.values()) if pin.aedt_name == ref_pin.name
                ]
                if _ref_pin:
                    _ref_pin[0].is_layout_pin = True
                    ref_cmp_pins.append(_ref_pin[0])
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
            term = self._create_pin_group_terminal(pingroup=pin_group, term_name=port_name)

        else:
            term = self._create_terminal(pins[0], term_name=port_name)
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
            ref_term = self._create_pin_group_terminal(pingroup=ref_pin_group, term_name=port_name + "_ref")

        else:
            ref_term = self._create_terminal(reference_pins[0], term_name=port_name + "_ref")
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
        port_type : str, optional
            Type of port to create. ``coax_port`` generates solder balls.
            ``circuit_port`` generates circuit ports on pins belonging to the net list.
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
                    if net_name:
                        net_list.append(net_name)
                except:
                    pass
        if reference_net in net_list:
            net_list.remove(reference_net)
        cmp_pins = [p for p in list(component.pins.values()) if p.net_name in net_list]
        for p in cmp_pins:  # pragma no cover
            p.is_layout_pin = True
        if len(cmp_pins) == 0:
            self._logger.info(f"No pins found on component {component.name}, searching padstack instances instead")
            return False
        pin_layers = cmp_pins[0].padstack_def.data.layer_names
        if port_type == "coax_port":
            if not solder_balls_height:
                solder_balls_height = self._pedb.components.instances[component.name].solder_ball_height
            if not solder_balls_size:
                solder_balls_size = self._pedb.components.instances[component.name].solder_ball_diameter[0]
            if not solder_balls_mid_size:
                solder_balls_mid_size = self._pedb.components.instances[component.name].solder_ball_diameter[1]
            ref_pins = [p for p in list(component.pins.values()) if p.net_name in reference_net]
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

        elif port_type == "circuit_port":  # pragma no cover
            ref_pins = [p for p in list(component.pins.values()) if p.net_name in reference_net]
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
                    ref_pin_group = self._pedb.components.create_pingroup_from_pins(ref_pins)
                    if ref_pin_group.is_null:
                        self._logger.error(f"Failed to create reference pin group on component {component.GetName()}.")
                        return False
                    ref_pin_group_term = self._create_pin_group_terminal(ref_pin_group, isref=False)
                    if not ref_pin_group_term:
                        self._logger.error(
                            f"Failed to create reference pin group terminal on component {component.GetName()}"
                        )
                        return False
                for net in net_list:
                    pins = [pin for pin in list(component.pins.values()) if pin.net_name == net]
                    if pins:
                        if len(pins) == 1:
                            pin_term = self._create_terminal(pins[0])
                            if pin_term:
                                pin_term.reference_terminal = ref_pin_group_term
                        else:
                            pin_group = self._pedb.components.create_pingroup_from_pins(pins)
                            if pin_group.is_null:
                                self._logger.error(
                                    f"Failed to create pin group terminal on component {component.GetName()}"
                                )
                                return False
                            pin_group_term = self._create_pin_group_terminal(pin_group)
                            if pin_group_term:
                                pin_group_term.reference_terminal = ref_pin_group_term
                    else:
                        self._logger.info("No pins found on component {} for the net {}".format(component, net))
            else:
                for net in net_list:
                    pins = [pin for pin in list(component.pins.values()) if pin.net_name == net]
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
                                    if not isinstance(ref_pin, list):
                                        ref_pin = [ref_pin]
                                    self.create_port_on_pins(component, [pin.name], ref_pin[0])
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
        for term in list(self._pedb.active_layout.terminals):
            if term.name == term_name:
                return term
        return PadstackInstanceTerminal.create(
            layout=self._pedb.layout, name=term_name, padstack_instance=pin, layer=from_layer, net=pin.net, is_ref=False
        )

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
        from pyedb.grpc.database.components import Component

        if isinstance(component, str):
            component = self._pedb.components.instances[component]
        if not isinstance(component, Component):  # pragma: no cover
            return False
        self._pedb.components.set_component_rlc(component.refdes)
        pins = list(self._pedb.components.instances[component.refdes].pins.values())
        if len(pins) == 2:
            pin_layers = pins[0].get_layer_range()
            pos_pin_term = PadstackInstanceTerminal.create(
                layout=self._pedb.active_layout,
                name=f"{component.name}_{pins[0].name}",
                padstack_instance=pins[0],
                layer=pin_layers[0],
                net=pins[0].net,
                is_ref=False,
            )
            if not pos_pin_term:  # pragma: no cover
                return False
            neg_pin_term = PadstackInstanceTerminal.create(
                layout=self._pedb.active_layout,
                name="{}_{}_ref".format(component.name, pins[1].name),
                padstack_instance=pins[1],
                layer=pin_layers[0],
                net=pins[1].net,
                is_ref=False,
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
            self._logger.info(f"Component {component.refdes} has been replaced by port")
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
        from pyedb.grpc.database.components import Component

        if isinstance(component, str):  # pragma: no cover
            component = self._pedb.components.instances[component]
        if not isinstance(component, Component):  # pragma: no cover
            return False
        self._pedb.components.set_component_rlc(component.name)
        pins = list(component.pins.values())
        if len(pins) == 2:  # pragma: no cover
            pin_layer = pins[0].get_layer_range()[0]
            pos_pin_term = PadstackInstanceTerminal.create(
                layout=self._pedb.active_layout,
                net=pins[0].net,
                name=f"{component.name}_{pins[0].name}",
                padstack_instance=pins[0],
                layer=pin_layer,
                is_ref=False,
            )
            if not pos_pin_term:  # pragma: no cover
                return False
            neg_pin_term = PadstackInstanceTerminal.create(
                layout=self._pedb.active_layout,
                net=pins[1].net,
                name="{}_{}_ref".format(component.name, pins[1].name),
                padstack_instance=pins[1],
                layer=pin_layer,
                is_ref=True,
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
        if pingroup.is_null:
            self._logger.error(f"{pingroup} is null")
        pin = PadstackInstance(self._pedb, pingroup.pins[0])
        if term_name is None:
            term_name = f"{pin.component.name}.{pin.name}.{pin.net_name}"
        for t in self._pedb.active_layout.terminals:
            if t.name == term_name:
                self._logger.warning(
                    f"Terminal {term_name} already created in current layout. Returning the "
                    f"already defined one. Make sure to delete the terminal before to create a new one."
                )
                return t
        pingroup_term = PinGroupTerminal.create(
            layout=self._pedb.active_layout, name=term_name, net=pingroup.net, pin_group=pingroup, is_ref=isref
        )
        if term_type == "circuit" or "auto":
            pingroup_term.is_circuit_port = True
        return pingroup_term

    def create_coax_port(self, padstackinstance, use_dot_separator=True, name=None, create_on_top=True):
        """Create HFSS 3Dlayout coaxial lumped port on a pastack
        Requires to have solder ball defined before calling this method.

        Parameters
        ----------
        padstackinstance : `Edb.Cell.Primitive.PadstackInstance` or int
            Padstack instance object.
        use_dot_separator : bool, optional
            Whether to use ``.`` as the separator for the naming convention, which
            is ``[component][net][pin]``. The default is ``True``. If ``False``, ``_`` is
            used as the separator instead.
        name : str
            Port name for overwriting the default port-naming convention,
            which is ``[component][net][pin]``. The port name must be unique.
            If a port with the specified name already exists, the
            default naming convention is used so that port creation does
            not fail.

        Returns
        -------
        str
            Terminal name.

        """
        if isinstance(padstackinstance, int):
            padstackinstance = self._pedb.padstacks.instances[padstackinstance]
        cmp_name = padstackinstance.component.name
        if cmp_name == "":
            cmp_name = "no_comp"
        net_name = padstackinstance.net.name
        if net_name == "":
            net_name = "no_net"
        pin_name = padstackinstance.name
        if pin_name == "":
            pin_name = "no_pin_name"
        if use_dot_separator:
            port_name = "{0}.{1}.{2}".format(cmp_name, pin_name, net_name)
        else:
            port_name = "{0}_{1}_{2}".format(cmp_name, pin_name, net_name)
        padstackinstance.is_layout_pin = True
        layer_range = padstackinstance.get_layer_range()
        if create_on_top:
            terminal_layer = layer_range[0]
        else:
            terminal_layer = layer_range[1]
        if name:
            port_name = name
        if self._port_exist(port_name):
            port_name = generate_unique_name(port_name, n=2)
            self._logger.info("An existing port already has this same name. Renaming to {}.".format(port_name))
        PadstackInstanceTerminal.create(
            layout=self._pedb._active_layout,
            name=port_name,
            padstack_instance=padstackinstance,
            layer=terminal_layer,
            net=padstackinstance.net,
            is_ref=False,
        )
        return port_name

    def _port_exist(self, port_name):
        return any(port for port in list(self._pedb.excitations.keys()) if port == port_name)

    def _create_edge_terminal(self, prim_id, point_on_edge, terminal_name=None, is_ref=False):
        """Create an edge terminal.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        terminal_name : str, optional
            Name of the terminal. The default is ``None``, in which case the
            default name is assigned.
        is_ref : bool, optional
            Whether it is a reference terminal. The default is ``False``.

        Returns
        -------
        Edb.Cell.Terminal.EdgeTerminal
        """
        if not terminal_name:
            terminal_name = generate_unique_name("Terminal_")
        if isinstance(point_on_edge, tuple):
            point_on_edge = GrpcPointData(point_on_edge)
        prim = [i for i in self._pedb.modeler.primitives if i.id == prim_id]
        if not prim:
            self._pedb.logger.error(f"No primitive found for ID {prim_id}")
            return False
        prim = prim[0]
        pos_edge = [GrpcPrimitiveEdge.create(prim, point_on_edge)]
        return GrpcEdgeTerminal.create(
            layout=prim.layout, name=terminal_name, edges=pos_edge, net=prim.net, is_ref=is_ref
        )

    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create a circuit port on a pin.

        Parameters
        ----------
        pos_pin : Object
            Edb Pin
        neg_pin : Object
            Edb Pin
        impedance : float
            Port Impedance
        port_name : str, optional
            Port Name

        Returns
        -------
        str
            Port Name.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.siwave.create_circuit_port_on_pin(pins[0], pins[1], 50, "port_name")
        """
        if not port_name:
            port_name = f"Port_{pos_pin.component.name}_{pos_pin.net_name}_{neg_pin.component.name}_{neg_pin.net_name}"
        return self._create_terminal_on_pins(
            positive_pin=pos_pin, negative_pin=neg_pin, impedance=impedance, name=port_name
        )

    def _create_terminal_on_pins(
        self,
        positive_pin,
        negative_pin,
        name=None,
        use_pin_top_layer=True,
        source_type="circuit_port",
        impedance=50,
        magnitude=0,
        phase=0,
        r=0,
        l=0,
        c=0,
    ):
        """Create a terminal on pins.

        Parameters
        ----------
        positive_pin : :class: `PadstackInstance`
            Positive padstack instance.
        negative_pin : :class: `PadstackInstance`
            Negative padstack instance.
        name : str, optional
            terminal name
        use_pin_top_layer : bool, optional
            Use :class: `PadstackInstance` top layer or bottom for terminal assignment.
        source_type : str, optional
            Specify the source type created. Supported values: `"circuit_port"`, `"lumped_port"`, `"current_source"`,
            `"voltage_port"`, `"rlc"`.
        impedance : float, int or str, optional
            Terminal impedance value
        magnitude : float, int or str, optional
            Terminal magnitude.
        phase : float, int or str, optional
            Terminal phase
        r : float, int
            Resistor value
        l : float, int
            Inductor value
        c : float, int
            Capacitor value
        """

        top_layer_pos, bottom_layer_pos = positive_pin.get_layer_range()
        top_layer_neg, bottom_layer_neg = negative_pin.get_layer_range()
        pos_term_layer = bottom_layer_pos
        neg_term_layer = bottom_layer_neg
        if use_pin_top_layer:
            pos_term_layer = top_layer_pos
            neg_term_layer = top_layer_neg
        if not name:
            name = positive_pin.name
        pos_terminal = PadstackInstanceTerminal.create(
            layout=self._pedb.active_layout,
            padstack_instance=positive_pin,
            name=name,
            layer=pos_term_layer,
            is_ref=False,
            net=positive_pin.net,
        )

        neg_terminal = PadstackInstanceTerminal.create(
            layout=self._pedb.active_layout,
            padstack_instance=negative_pin,
            name=negative_pin.name,
            layer=neg_term_layer,
            is_ref=False,
            net=negative_pin.net,
        )
        if source_type in ["circuit_port", "lumped_port"]:
            pos_terminal.boundary_type = GrpcBoundaryType.PORT
            neg_terminal.boundary_type = GrpcBoundaryType.PORT
            pos_terminal.impedance = GrpcValue(impedance)
            if source_type == "lumped_port":
                pos_terminal.is_circuit_port = False
                neg_terminal.is_circuit_port = False
            else:
                pos_terminal.is_circuit_port = True
                neg_terminal.is_circuit_port = True
            pos_terminal.reference_terminal = neg_terminal
            pos_terminal.name = name

        elif source_type == "current_source":
            pos_terminal.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
            neg_terminal.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
            pos_terminal.source_amplitude = GrpcValue(magnitude)
            pos_terminal.source_phase = GrpcValue(phase)
            pos_terminal.impedance = GrpcValue(impedance)
            pos_terminal.reference_terminal = neg_terminal
            pos_terminal.name = name

        elif source_type == "voltage_source":
            pos_terminal.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
            neg_terminal.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
            pos_terminal.source_amplitude = GrpcValue(magnitude)
            pos_terminal.impedance = GrpcValue(impedance)
            pos_terminal.source_phase = GrpcValue(phase)
            pos_terminal.reference_terminal = neg_terminal
            pos_terminal.name = name

        elif source_type == "rlc":
            pos_terminal.boundary_type = GrpcBoundaryType.RLC
            neg_terminal.boundary_type = GrpcBoundaryType.RLC
            pos_terminal.reference_terminal = neg_terminal
            rlc = GrpcRlc()
            rlc.r_enabled = bool(r)
            rlc.l_enabled = bool(l)
            rlc.c_enabled = bool(c)
            rlc.r = GrpcValue(r)
            rlc.l = GrpcValue(l)
            rlc.c = GrpcValue(c)
            pos_terminal.rlc_boundary_parameters = rlc
            pos_terminal.name = name

        else:
            self._pedb.logger.error("No valid source type specified.")
            return False
        return pos_terminal.name

    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=0, phase_value=0, source_name=None):
        """Create a voltage source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitations.create_voltage_source_on_pin(pins[0], pins[1], 50, "source_name")
        """

        if not source_name:
            source_name = (
                f"VSource_{pos_pin.component.name}_{pos_pin.net_name}_{neg_pin.component.name}_{neg_pin.net_name}"
            )
        return self._create_terminal_on_pins(
            positive_pin=pos_pin,
            negative_pin=neg_pin,
            name=source_name,
            magnitude=voltage_value,
            phase=phase_value,
            source_type="voltage_source",
        )

    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0, phase_value=0, source_name=None):
        """Create a voltage source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins = edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitations.create_voltage_source_on_pin(pins[0], pins[1], 50, "source_name")
        """

        if not source_name:
            source_name = (
                f"VSource_{pos_pin.component.name}_{pos_pin.net_name}_{neg_pin.component.name}_{neg_pin.net_name}"
            )
        return self._create_terminal_on_pins(
            positive_pin=pos_pin,
            negative_pin=neg_pin,
            name=source_name,
            magnitude=current_value,
            phase=phase_value,
            source_type="current_source",
        )

    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a Resistor boundary between two given pins..

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        rvalue : float, optional
            Resistance value. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.

        Returns
        -------
        str
            Name of the resistor.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.excitation.create_resistor_on_pin(pins[0], pins[1],50,"res_name")
        """
        if not resistor_name:
            resistor_name = (
                f"Res_{pos_pin.component.name}_{pos_pin.net.name}_{neg_pin.component.name}_{neg_pin.net.name}"
            )
        return self._create_terminal_on_pins(
            positive_pin=pos_pin, negative_pin=neg_pin, name=resistor_name, source_type="rlc", r=rvalue
        )

    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        impedance=50,
        port_name="",
    ):
        """Create a circuit port on a NET.

        It groups all pins belonging to the specified net and then applies the port on PinGroups.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        impedance_value : float, optional
            Port impedance value. The default is ``50``.
        port_name : str, optional
            Name of the port. The default is ``""``.

        Returns
        -------
        str
            The name of the port.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.excitations.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        if not port_name:
            port_name = (
                f"Port_{positive_component_name}_{positive_net_name}_{negative_component_name}_{negative_net_name}"
            )
        positive_pins = []
        for pin in list(self._pedb.components.instances[positive_component_name].pins.values()):
            if pin and not pin.net.is_null:
                if pin.net_name == positive_net_name:
                    positive_pins.append(pin)
        if not positive_pins:
            self._pedb.logger.error(
                f"No positive pins found component {positive_component_name} net {positive_net_name}"
            )
            return False
        negative_pins = []
        for pin in list(self._pedb.components.instances[negative_component_name].pins.values()):
            if pin and not pin.net.is_null:
                if pin.net_name == negative_net_name:
                    negative_pins.append(pin)
        if not negative_pins:
            self._pedb.logger.error(
                f"No negative pins found component {negative_component_name} net {negative_net_name}"
            )
            return False

        return self.create_pin_group_terminal(
            positive_pins=positive_pins,
            negatives_pins=negative_pins,
            name=port_name,
            impedance=impedance,
            source_type="circuit_port",
        )

    def create_pin_group_terminal(
        self,
        positive_pins,
        negatives_pins,
        name=None,
        impedance=50,
        source_type="circuit_port",
        magnitude=1.0,
        phase=0,
        r=0.0,
        l=0.0,
        c=0.0,
    ):
        """Create a pin group terminal.

        Parameters
        ----------
        positive_pins : positive pins used.
            :class: `PadstackInstance` or List[:class: ´PadstackInstance´]
        negatives_pins : negative pins used.
            :class: `PadstackInstance` or List[:class: ´PadstackInstance´]
        impedance : float, int or str
            Terminal impedance. Default value is `50` Ohms.
        source_type : str
            Source type assigned on terminal. Supported values : `"circuit_port"`, `"lumped_port"`, `"current_source"`,
            `"voltage_source"`, `"rlc"`, `"dc_terminal"`. Default value is `"circuit_port"`.
        name : str, optional
            Source name.
        magnitude : float, int or str, optional
            source magnitude.
        phase : float, int or str, optional
            phase magnitude.
        r : float, optional
            Resistor value.
        l : float, optional
            Inductor value.
        c : float, optional
            Capacitor value.
        """
        if isinstance(positive_pins, PadstackInstance):
            positive_pins = [positive_pins]
        if negatives_pins:
            if isinstance(negatives_pins, PadstackInstance):
                negatives_pins = [negatives_pins]
        if not name:
            name = (
                f"Port_{positive_pins[0].component.name}_{positive_pins[0].net.name}_{positive_pins[0].name}_"
                f"{negatives_pins.name}"
            )
        if name in [i.name for i in self._pedb.active_layout.terminals]:
            name = generate_unique_name(name, n=3)
            self._logger.warning(f"Port already exists with same name. Renaming to {name}")

        pos_pin_group = self._pedb.components.create_pingroup_from_pins(positive_pins)
        pos_pingroup_terminal = PinGroupTerminal.create(
            layout=self._pedb.active_layout,
            name=name,
            pin_group=pos_pin_group,
            net=positive_pins[0].net,
            is_ref=False,
        )
        if not source_type == "dc_terminal":
            neg_pin_group = self._pedb.components.create_pingroup_from_pins(negatives_pins)
            neg_pingroup_terminal = PinGroupTerminal.create(
                layout=self._pedb.active_layout,
                name=f"{name}_ref",
                pin_group=neg_pin_group,
                net=negatives_pins[0].net,
                is_ref=False,
            )
        if source_type in ["circuit_port", "lumped_port"]:
            pos_pingroup_terminal.boundary_type = GrpcBoundaryType.PORT
            pos_pingroup_terminal.impedance = GrpcValue(impedance)
            if len(positive_pins) > 1 and len(negatives_pins) > 1:
                if source_type == "lumped_port":
                    source_type = "circuit_port"
            if source_type == "circuit_port":
                pos_pingroup_terminal.is_circuit_port = True
                neg_pingroup_terminal.is_circuit_port = True
            else:
                pos_pingroup_terminal.is_circuit_port = False
                neg_pingroup_terminal.is_circuit_port = False
            pos_pingroup_terminal.reference_terminal = neg_pingroup_terminal
            pos_pingroup_terminal.name = name

        elif source_type == "current_source":
            pos_pingroup_terminal.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
            neg_pingroup_terminal.boundary_type = GrpcBoundaryType.CURRENT_SOURCE
            pos_pingroup_terminal.source_amplitude = GrpcValue(magnitude)
            pos_pingroup_terminal.source_phase = GrpcValue(phase)
            pos_pingroup_terminal.reference_terminal = neg_pingroup_terminal
            pos_pingroup_terminal.name = name

        elif source_type == "voltage_source":
            pos_pingroup_terminal.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
            neg_pingroup_terminal.boundary_type = GrpcBoundaryType.VOLTAGE_SOURCE
            pos_pingroup_terminal.source_amplitude = GrpcValue(magnitude)
            pos_pingroup_terminal.source_phase = GrpcValue(phase)
            pos_pingroup_terminal.reference_terminal = neg_pingroup_terminal
            pos_pingroup_terminal.name = name

        elif source_type == "rlc":
            pos_pingroup_terminal.boundary_type = GrpcBoundaryType.RLC
            neg_pingroup_terminal.boundary_type = GrpcBoundaryType.RLC
            pos_pingroup_terminal.reference_terminal = neg_pingroup_terminal
            Rlc = GrpcRlc()
            Rlc.r_enabled = bool(r)
            Rlc.l_enabled = bool(l)
            Rlc.c_enabled = bool(c)
            Rlc.r = GrpcValue(r)
            Rlc.l = GrpcValue(l)
            Rlc.c = GrpcValue(c)
            pos_pingroup_terminal.rlc_boundary_parameters = Rlc

        elif source_type == "dc_terminal":
            pos_pingroup_terminal.boundary_type = GrpcBoundaryType.DC_TERMINAL
        else:
            pass
        return pos_pingroup_terminal.name

    def _check_gnd(self, component_name):
        negative_net_name = None
        if self._pedb.nets.is_net_in_component(component_name, "GND"):
            negative_net_name = "GND"
        elif self._pedb.nets.is_net_in_component(component_name, "PGND"):
            negative_net_name = "PGND"
        elif self._pedb.nets.is_net_in_component(component_name, "AGND"):
            negative_net_name = "AGND"
        elif self._pedb.nets.is_net_in_component(component_name, "DGND"):
            negative_net_name = "DGND"
        if not negative_net_name:
            raise ValueError("No GND, PGND, AGND, DGND found. Please setup the negative net name manually.")
        return negative_net_name

    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        voltage_value=3.3,
        phase_value=0,
        source_name=None,
    ):
        """Create a voltage source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            The name of the source.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.excitations.create_voltage_source_on_net("U2A5","V1P5_S3","U2A5","GND",3.3,0,"source_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)

        if not source_name:
            source_name = (
                f"Vsource_{positive_component_name}_{positive_net_name}_"
                f"{negative_component_name}_{negative_net_name}"
            )
        return self.create_pin_group_terminal(
            positive_pins=pos_node_pins,
            negatives_pins=neg_node_pins,
            name=source_name,
            magnitude=voltage_value,
            phase=phase_value,
            impedance=1e-6,
            source_type="voltage_source",
        )

    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name=None,
        current_value=3.3,
        phase_value=0,
        source_name=None,
    ):
        """Create a voltage source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``None`` which will look for GND Nets.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            The name of the source.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.excitations.create_voltage_source_on_net("U2A5","V1P5_S3","U2A5","GND",3.3,0,"source_name")
        """
        if not negative_component_name:
            negative_component_name = positive_component_name
        if not negative_net_name:
            negative_net_name = self._check_gnd(negative_component_name)
        pos_node_pins = self._pedb.components.get_pin_from_component(positive_component_name, positive_net_name)
        neg_node_pins = self._pedb.components.get_pin_from_component(negative_component_name, negative_net_name)

        if not source_name:
            source_name = (
                f"Vsource_{positive_component_name}_{positive_net_name}_"
                f"{negative_component_name}_{negative_net_name}"
            )
        return self.create_pin_group_terminal(
            positive_pins=pos_node_pins,
            negatives_pins=neg_node_pins,
            name=source_name,
            magnitude=current_value,
            phase=phase_value,
            impedance=1e6,
            source_type="current_source",
        )

    def create_coax_port_on_component(self, ref_des_list, net_list, delete_existing_terminal=False):
        """Create a coaxial port on a component or component list on a net or net list.
           The name of the new coaxial port is automatically assigned.

        Parameters
        ----------
        ref_des_list : list, str
            List of one or more reference designators.

        net_list : list, str
            List of one or more nets.

        delete_existing_terminal : bool
            Delete existing terminal with same name if exists.
            Port naming convention is `ref_des`_`pin.net.name`_`pin.name`

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        coax = []
        if not isinstance(ref_des_list, list):
            ref_des_list = [ref_des_list]
        if not isinstance(net_list, list):
            net_list = [net_list]
        for ref in ref_des_list:
            for _, pin in self._pedb.components.instances[ref].pins.items():
                try:  # trying due to grpc crash when no net is defined on pin.
                    try:
                        pin_net = pin.net
                    except:
                        pin_net = None
                    if pin_net and pin.net.is_null:
                        self._logger.warning(f"Pin {pin.id} has no net defined")
                    elif pin.net.name in net_list:
                        pin.is_pin = True
                        port_name = f"{ref}_{pin.net.name}_{pin.name}"
                        if self.check_before_terminal_assignement(
                            connectable=pin, delete_existing_terminal=delete_existing_terminal
                        ):
                            top_layer = pin.get_layer_range()[0]
                            term = PadstackInstanceTerminal.create(
                                layout=pin.layout,
                                name=port_name,
                                padstack_instance=pin,
                                layer=top_layer,
                                net=pin.net,
                                is_ref=False,
                            )
                            if not term.is_null:
                                coax.append(port_name)
                except RuntimeError as error:
                    self._logger.error(error)
        return coax

    def check_before_terminal_assignement(self, connectable, delete_existing_terminal=False):
        if not connectable:
            return False
        existing_terminals = [term for term in self._pedb.active_layout.terminals if term.id == connectable.id]
        if existing_terminals:
            if not delete_existing_terminal:
                self._pedb.logger.error(
                    f"Terminal {connectable.name} already defined in design, please make sure to have unique name."
                )
                return False
            else:
                if isinstance(connectable, PadstackInstanceTerminal):
                    self._pedb.logger.error(
                        f"Terminal {connectable.name} already defined, check status on bug "
                        f"https://github.com/ansys/pyedb-core/issues/429"
                    )
                    return False
        else:
            return True

    def create_differential_wave_port(
        self,
        positive_primitive_id,
        positive_points_on_edge,
        negative_primitive_id,
        negative_points_on_edge,
        port_name=None,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """Create a differential wave port.

        Parameters
        ----------
        positive_primitive_id : int, EDBPrimitives
            Primitive ID of the positive terminal.
        positive_points_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be close to the target edge but not on the two
            ends of the edge.
        negative_primitive_id : int, EDBPrimitives
            Primitive ID of the negative terminal.
        negative_points_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be close to the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        tuple
            The tuple contains: (port_name, pyedb.dotnet.database.edb_data.sources.ExcitationDifferential).

        Examples
        --------
        >>> edb.hfss.create_differential_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])
        """
        if not port_name:
            port_name = generate_unique_name("diff")

        if isinstance(positive_primitive_id, Primitive):
            positive_primitive_id = positive_primitive_id.id

        if isinstance(negative_primitive_id, Primitive):
            negative_primitive_id = negative_primitive_id.id

        _, pos_term = self.create_wave_port(
            positive_primitive_id,
            positive_points_on_edge,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )
        _, neg_term = self.create_wave_port(
            negative_primitive_id,
            negative_points_on_edge,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )
        edb_list = [pos_term, neg_term]

        boundle_terminal = BundleTerminal.create(edb_list)
        boundle_terminal.name = port_name
        bundle_term = boundle_terminal.terminals
        bundle_term[0].name = port_name + ":T1"
        bundle_term[1].mame = port_name + ":T2"
        return port_name, boundle_terminal

    def create_wave_port(
        self,
        prim_id,
        point_on_edge,
        port_name=None,
        impedance=50,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """Create a wave port.

        Parameters
        ----------
        prim_id : int, Primitive
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        impedance : int, float, optional
            Impedance of the port. The default value is ``50``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        tuple
            The tuple contains: (Port name, pyedb.dotnet.database.edb_data.sources.Excitation).

        Examples
        --------
        >>> edb.excitations.create_wave_port(0, ["-50mm", "-0mm"])
        """
        if not port_name:
            port_name = generate_unique_name("Terminal_")

        if isinstance(prim_id, Primitive):
            prim_id = prim_id.id
        pos_edge_term = self._create_edge_terminal(prim_id, point_on_edge, port_name)
        pos_edge_term.impedance = GrpcValue(impedance)
        wave_port = WavePort(self._pedb, pos_edge_term)
        wave_port.horizontal_extent_factor = horizontal_extent_factor
        wave_port.vertical_extent_factor = vertical_extent_factor
        wave_port.pec_launch_width = pec_launch_width
        wave_port.hfss_type = "Wave"
        wave_port.do_renormalize = True
        if pos_edge_term:
            return port_name, wave_port
        else:
            return False

    def create_edge_port_vertical(
        self,
        prim_id,
        point_on_edge,
        port_name=None,
        impedance=50,
        reference_layer=None,
        hfss_type="Gap",
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """Create a vertical edge port.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        impedance : int, float, optional
            Impedance of the port. The default value is ``50``.
        reference_layer : str, optional
            Reference layer of the port. The default is ``None``.
        hfss_type : str, optional
            Type of the port. The default value is ``"Gap"``. Options are ``"Gap"``, ``"Wave"``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        radial_extent_factor : int, float, optional
            Radial extent factor. The default value is ``0``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        str
            Port name.
        """
        if not port_name:
            port_name = generate_unique_name("Terminal_")
        pos_edge_term = self._create_edge_terminal(prim_id, point_on_edge, port_name)
        pos_edge_term.impedance = GrpcValue(impedance)
        if reference_layer:
            reference_layer = self._pedb.stackup.signal_layers[reference_layer]
            pos_edge_term.reference_layer = reference_layer

        prop = ", ".join(
            [
                f"HFSS('HFSS Type'='{hfss_type}'",
                " Orientation='Vertical'",
                " 'Layer Alignment'='Upper'",
                f" 'Horizontal Extent Factor'='{horizontal_extent_factor}'",
                f" 'Vertical Extent Factor'='{vertical_extent_factor}'",
                f" 'PEC Launch Width'='{pec_launch_width}')",
            ]
        )
        pos_edge_term.set_product_solver_option(
            GrpcProductIdType.DESIGNER,
            "HFSS",
            prop,
        )
        if not pos_edge_term.is_null:
            return pos_edge_term
        else:
            return False

    def create_edge_port_horizontal(
        self,
        prim_id,
        point_on_edge,
        ref_prim_id=None,
        point_on_ref_edge=None,
        port_name=None,
        impedance=50,
        layer_alignment="Upper",
    ):
        """Create a horizontal edge port.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        ref_prim_id : int, optional
            Reference primitive ID. The default is ``None``.
        point_on_ref_edge : list, optional
            Coordinate of the point to define the reference edge
            terminal. The point must be on the target edge but not
            on the two ends of the edge. The default is ``None``.
        port_name : str, optional
            Name of the port. The default is ``None``.
        impedance : int, float, optional
            Impedance of the port. The default value is ``50``.
        layer_alignment : str, optional
            Layer alignment. The default value is ``Upper``. Options are ``"Upper"``, ``"Lower"``.

        Returns
        -------
        str
            Name of the port.
        """
        pos_edge_term = self._create_edge_terminal(prim_id, point_on_edge, port_name)
        neg_edge_term = self._create_edge_terminal(ref_prim_id, point_on_ref_edge, port_name + "_ref", is_ref=True)

        pos_edge_term.impedance = GrpcValue(impedance)
        pos_edge_term.reference_terminal = neg_edge_term
        if not layer_alignment == "Upper":
            layer_alignment = "Lower"
        pos_edge_term.set_product_solver_option(
            GrpcProductIdType.DESIGNER,
            "HFSS",
            f"HFSS('HFSS Type'='Gap(coax)', Orientation='Horizontal', 'Layer Alignment'='{layer_alignment}')",
        )
        if pos_edge_term:
            return port_name
        else:
            return False

    def create_lumped_port_on_net(
        self, nets=None, reference_layer=None, return_points_only=False, digit_resolution=6, at_bounding_box=True
    ):
        """Create an edge port on nets. This command looks for traces and polygons on the
        nets and tries to assign vertical lumped port.

        Parameters
        ----------
        nets : list, optional
            List of nets, str or Edb net.

        reference_layer : str, Edb layer.
             Name or Edb layer object.

        return_points_only : bool, optional
            Use this boolean when you want to return only the points from the edges and not creating ports. Default
            value is ``False``.

        digit_resolution : int, optional
            The number of digits carried for the edge location accuracy. The default value is ``6``.

        at_bounding_box : bool
            When ``True`` will keep the edges from traces at the layout bounding box location. This is recommended when
             a cutout has been performed before and lumped ports have to be created on ending traces. Default value is
             ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(nets, str):
            nets = [self._pedb.nets.signal[nets]]
        if isinstance(nets, Net):
            nets = [nets]
        nets = [self._pedb.nets.signal[net] for net in nets if isinstance(net, str)]
        port_created = False
        if nets:
            edges_pts = []
            if isinstance(reference_layer, str):
                try:
                    reference_layer = self._pedb.stackup.signal_layers[reference_layer]
                except:
                    raise Exception(f"Failed to get the layer {reference_layer}")
            if not isinstance(reference_layer, StackupLayer):
                return False
            layout_bbox = self._pedb.get_conformal_polygon_from_netlist(self._pedb.nets.netlist)
            layout_extent_segments = [pt for pt in list(layout_bbox.arc_data) if pt.is_segment]
            first_pt = layout_extent_segments[0]
            layout_extent_points = [
                [first_pt.start.x.value, first_pt.end.x.value],
                [first_pt.Start.y.value, first_pt.end.y.value],
            ]
            for segment in layout_extent_segments[1:]:
                end_point = (segment.end.x.value, segment.end.y.value)
                layout_extent_points[0].append(end_point[0])
                layout_extent_points[1].append(end_point[1])
            for net in nets:
                net_primitives = self._pedb.nets[net.name].primitives
                net_paths = [pp for pp in net_primitives if pp.type == "Path"]
                for path in net_paths:
                    trace_path_pts = list(path.center_line.Points)
                    port_name = f"{net.name}_{path.id}"
                    for pt in trace_path_pts:
                        _pt = [
                            round(pt.x.value, digit_resolution),
                            round(pt.y.value, digit_resolution),
                        ]
                        if at_bounding_box:
                            if GeometryOperators.point_in_polygon(_pt, layout_extent_points) == 0:
                                if return_points_only:
                                    edges_pts.append(_pt)
                                else:
                                    term = self._create_edge_terminal(path.id, pt, port_name)  # pragma no cover
                                    term.reference_layer = reference_layer
                                    port_created = True
                        else:
                            if return_points_only:  # pragma: no cover
                                edges_pts.append(_pt)
                            else:
                                term = self._create_edge_terminal(path.id, pt, port_name)
                                term.reference_layer = reference_layer
                                port_created = True
                net_poly = [pp for pp in net_primitives if pp.type == "Polygon"]
                for poly in net_poly:
                    poly_segment = [aa for aa in poly.arcs if aa.is_segment]
                    for segment in poly_segment:
                        if (
                            GeometryOperators.point_in_polygon(
                                [segment.mid_point.x.value, segment.mid_point.y.value], layout_extent_points
                            )
                            == 0
                        ):
                            if return_points_only:
                                edges_pts.append(segment.mid_point)
                            else:
                                port_name = f"{net.name}_{poly.id}"
                                term = self._create_edge_terminal(
                                    poly.id, segment.mid_point, port_name
                                )  # pragma no cover
                                term.set_reference_layer = reference_layer
                                port_created = True
            if return_points_only:
                return edges_pts
        return port_created

    def create_vertical_circuit_port_on_clipped_traces(self, nets=None, reference_net=None, user_defined_extent=None):
        """Create an edge port on clipped signal traces.

        Parameters
        ----------
        nets : list, optional
            String of one net or EDB net or a list of multiple nets or EDB nets.

        reference_net : str, Edb net.
             Name or EDB reference net.

        user_defined_extent : [x, y], EDB PolygonData
            Use this point list or PolygonData object to check if ports are at this polygon border.

        Returns
        -------
        [[str]]
            Nested list of str, with net name as first value, X value for point at border, Y value for point at border,
            and terminal name.
        """
        if not isinstance(nets, list):
            if isinstance(nets, str):
                nets = list(self._pedb.nets.signal.values())
        else:
            nets = [self._pedb.nets.signal[net] for net in nets]
        if nets:
            if isinstance(reference_net, str):
                reference_net = self._pedb.nets.nets[reference_net]
            if not reference_net:
                self._logger.error("No reference net provided for creating port")
                return False
            if user_defined_extent:
                if isinstance(user_defined_extent, GrpcPolygonData):
                    _points = [pt for pt in list(user_defined_extent.points)]
                    _x = []
                    _y = []
                    for pt in _points:
                        if pt.x.value < 1e100 and pt.y.value < 1e100:
                            _x.append(pt.x.value)
                            _y.append(pt.y.value)
                    user_defined_extent = [_x, _y]
            terminal_info = []
            for net in nets:
                net_polygons = [prim for prim in self._pedb.modeler.primitives if prim.type in ["polygon", "rectangle"]]
                for poly in net_polygons:
                    mid_points = [[arc.midpoint.x.value, arc.midpoint.y.value] for arc in poly.arcs]
                    for mid_point in mid_points:
                        if GeometryOperators.point_in_polygon(mid_point, user_defined_extent) == 0:
                            port_name = generate_unique_name(f"{poly.net_name}_{poly.id}")
                            term = self._create_edge_terminal(poly.id, mid_point, port_name)  # pragma no cover
                            if not term.is_null:
                                self._logger.info(f"Terminal {term.name} created")
                                term.is_circuit_port = True
                                terminal_info.append([poly.net_name, mid_point[0], mid_point[1], term.name])
                                mid_pt_data = GrpcPointData(mid_point)
                                ref_prim = [
                                    prim
                                    for prim in reference_net.primitives
                                    if prim.polygon_data.point_in_polygon(mid_pt_data)
                                ]
                                if not ref_prim:
                                    self._logger.warning("no reference primitive found, trying to extend scanning area")
                                    scanning_zone = [
                                        (mid_point[0] - mid_point[0] * 1e-3, mid_point[1] - mid_point[1] * 1e-3),
                                        (mid_point[0] - mid_point[0] * 1e-3, mid_point[1] + mid_point[1] * 1e-3),
                                        (mid_point[0] + mid_point[0] * 1e-3, mid_point[1] + mid_point[1] * 1e-3),
                                        (mid_point[0] + mid_point[0] * 1e-3, mid_point[1] - mid_point[1] * 1e-3),
                                    ]
                                    for new_point in scanning_zone:
                                        mid_pt_data = GrpcPointData(new_point)
                                        ref_prim = [
                                            prim
                                            for prim in reference_net.primitives
                                            if prim.polygon_data.point_in_polygon(mid_pt_data)
                                        ]
                                        if ref_prim:
                                            self._logger.info("Reference primitive found")
                                            break
                                    if not ref_prim:
                                        self._logger.error("Failed to collect valid reference primitives for terminal")
                                if ref_prim:
                                    reference_layer = ref_prim[0].layer
                                    if term.reference_layer == reference_layer:
                                        self._logger.info(f"Port {port_name} created")
            return terminal_info
        return False

    def create_bundle_wave_port(
        self,
        primitives_id,
        points_on_edge,
        port_name=None,
        horizontal_extent_factor=5,
        vertical_extent_factor=3,
        pec_launch_width="0.01mm",
    ):
        """Create a bundle wave port.

        Parameters
        ----------
        primitives_id : list
            Primitive ID of the positive terminal.
        points_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be close to the target edge but not on the two
            ends of the edge.
        port_name : str, optional
            Name of the port. The default is ``None``.
        horizontal_extent_factor : int, float, optional
            Horizontal extent factor. The default value is ``5``.
        vertical_extent_factor : int, float, optional
            Vertical extent factor. The default value is ``3``.
        pec_launch_width : str, optional
            Launch Width of PEC. The default value is ``"0.01mm"``.

        Returns
        -------
        tuple
            The tuple contains: (port_name, pyedb.egacy.database.edb_data.sources.ExcitationDifferential).

        Examples
        --------
        >>> edb.excitations.create_bundle_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])
        """
        if not port_name:
            port_name = generate_unique_name("bundle_port")

        if isinstance(primitives_id[0], Primitive):
            primitives_id = [i.id for i in primitives_id]

        terminals = []
        _port_name = port_name
        for p_id, loc in list(zip(primitives_id, points_on_edge)):
            _, term = self.create_wave_port(
                p_id,
                loc,
                port_name=_port_name,
                horizontal_extent_factor=horizontal_extent_factor,
                vertical_extent_factor=vertical_extent_factor,
                pec_launch_width=pec_launch_width,
            )
            _port_name = None
            terminals.append(term)

        _edb_bundle_terminal = BundleTerminal.create(terminals)
        return port_name, BundleWavePort(self._pedb, _edb_bundle_terminal)

    def create_hfss_ports_on_padstack(self, pinpos, portname=None):
        """Create an HFSS port on a padstack.

        Parameters
        ----------
        pinpos :
            Position of the pin.

        portname : str, optional
             Name of the port. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        top_layer, bottom_layer = pinpos.get_layer_range()

        if not portname:
            portname = generate_unique_name("Port_" + pinpos.net.name)
        edbpointTerm_pos = PadstackInstanceTerminal.create(
            padstack_instance=pinpos, name=portname, layer=top_layer, is_ref=False
        )
        if edbpointTerm_pos:
            return True
        else:
            return False

    def get_ports_number(self):
        """Return the total number of excitation ports in a layout.

        Parameters
        ----------
        None

        Returns
        -------
        int
           Number of ports.

        """
        terms = [term for term in self._pedb.layout.terminals]
        return len([i for i in terms if not i.is_reference_terminal])

    def create_rlc_boundary_on_pins(self, positive_pin=None, negative_pin=None, rvalue=0.0, lvalue=0.0, cvalue=0.0):
        """Create hfss rlc boundary on pins.

        Parameters
        ----------
        positive_pin : Positive pin.
            Edb.Cell.Primitive.PadstackInstance

        negative_pin : Negative pin.
            Edb.Cell.Primitive.PadstackInstance

        rvalue : Resistance value

        lvalue : Inductance value

        cvalue . Capacitance value.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if positive_pin and negative_pin:
            positive_pin_term = positive_pin.get_terminal(create_new_terminal=True)
            negative_pin_term = negative_pin.get_terminal(create_new_terminal=True)
            positive_pin_term.boundary_type = GrpcBoundaryType.RLC
            negative_pin_term.boundary_type = GrpcBoundaryType.RLC
            rlc = GrpcRlc()
            rlc.is_parallel = True
            rlc.r_enabled = True
            rlc.l_enabled = True
            rlc.c_enabled = True
            rlc.r = GrpcValue(rvalue)
            rlc.l = GrpcValue(lvalue)
            rlc.c = GrpcValue(cvalue)
            positive_pin_term.rlc_boundary_parameters = rlc
            term_name = f"{positive_pin.component.name}_{positive_pin.net.name}_{positive_pin.name}"
            positive_pin_term.name = term_name
            negative_pin_term.name = f"{term_name}_ref"
            positive_pin_term.reference_terminal = negative_pin_term
            return positive_pin_term
        return False

    def create_edge_port_on_polygon(
        self,
        polygon=None,
        reference_polygon=None,
        terminal_point=None,
        reference_point=None,
        reference_layer=None,
        port_name=None,
        port_impedance=50.0,
        force_circuit_port=False,
    ):
        """Create lumped port between two edges from two different polygons. Can also create a vertical port when
        the reference layer name is only provided. When a port is created between two edge from two polygons which don't
        belong to the same layer, a circuit port will be automatically created instead of lumped. To enforce the circuit
        port instead of lumped,use the boolean force_circuit_port.

        Parameters
        ----------
        polygon : The EDB polygon object used to assign the port.
            Edb.Cell.Primitive.Polygon object.

        reference_polygon : The EDB polygon object used to define the port reference.
            Edb.Cell.Primitive.Polygon object.

        terminal_point : The coordinate of the point to define the edge terminal of the port. This point must be
        located on the edge of the polygon where the port has to be placed. For instance taking the middle point
        of an edge is a good practice but any point of the edge should be valid. Taking a corner might cause unwanted
        port location.
            list[float, float] with values provided in meter.

        reference_point : same as terminal_point but used for defining the reference location on the edge.
            list[float, float] with values provided in meter.

        reference_layer : Name used to define port reference for vertical ports.
            str the layer name.

        port_name : Name of the port.
            str.

        port_impedance : port impedance value. Default value is 50 Ohms.
            float, impedance value.

        force_circuit_port ; used to force circuit port creation instead of lumped. Works for vertical and coplanar
        ports.

        Examples
        --------

        >>> edb_path = path_to_edb
        >>> edb = Edb(edb_path)
        >>> poly_list = [poly for poly in list(edb.layout.primitives) if poly.GetPrimitiveType() == 2]
        >>> port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
        >>> ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]
        >>> port_location = [-65e-3, -13e-3]
        >>> ref_location = [-63e-3, -13e-3]
        >>> edb.hfss.create_edge_port_on_polygon(polygon=port_poly, reference_polygon=ref_poly,
        >>> terminal_point=port_location, reference_point=ref_location)

        """
        if not polygon:
            self._logger.error("No polygon provided for port {} creation".format(port_name))
            return False
        if reference_layer:
            reference_layer = self._pedb.stackup.signal_layers[reference_layer]
            if not reference_layer:
                self._logger.error("Specified layer for port {} creation was not found".format(port_name))
        if not isinstance(terminal_point, list):
            self._logger.error("Terminal point must be a list of float with providing the point location in meter")
            return False
        terminal_point = GrpcPointData(terminal_point)
        if reference_point and isinstance(reference_point, list):
            reference_point = GrpcPointData(reference_point)
        if not port_name:
            port_name = generate_unique_name("Port_")
        edge = GrpcPrimitiveEdge.create(polygon, terminal_point)
        edges = [edge]
        edge_term = GrpcEdgeTerminal.create(
            layout=polygon.layout, edges=edges, net=polygon.net, name=port_name, is_ref=False
        )
        if force_circuit_port:
            edge_term.is_circuit_port = True
        else:
            edge_term.is_circuit_port = False

        if port_impedance:
            edge_term.impedance = GrpcValue(port_impedance)
        edge_term.name = port_name
        if reference_polygon and reference_point:
            ref_edge = GrpcPrimitiveEdge.create(reference_polygon, reference_point)
            ref_edges = [ref_edge]
            ref_edge_term = GrpcEdgeTerminal.create(
                layout=reference_polygon.layout,
                name=port_name + "_ref",
                edges=ref_edges,
                net=reference_polygon.net,
                is_ref=True,
            )
            if reference_layer:
                ref_edge_term.reference_layer = reference_layer
            if force_circuit_port:
                ref_edge_term.is_circuit_port = True
            else:
                ref_edge_term.is_circuit_port = False

            if port_impedance:
                ref_edge_term.impedance = GrpcValue(port_impedance)
            edge_term.reference_terminal = ref_edge_term
        return True

    def create_port_between_pin_and_layer(
        self, component_name=None, pins_name=None, layer_name=None, reference_net=None, impedance=50.0
    ):
        """Create circuit port between pin and a reference layer.

        Parameters
        ----------
        component_name : str
            Component name. The default is ``None``.
        pins_name : str
            Pin name or list of pin names. The default is ``None``.
        layer_name : str
            Layer name. The default is ``None``.
        reference_net : str
            Reference net name. The default is ``None``.
        impedance : float, optional
            Port impedance. The default is ``50.0`` in ohms.

        Returns
        -------
        PadstackInstanceTerminal
            Created terminal.

        """
        if not pins_name:
            pins_name = []
        if pins_name:
            if not isinstance(pins_name, list):  # pragma no cover
                pins_name = [pins_name]
            if not reference_net:
                self._logger.info("no reference net provided, searching net {} instead.".format(layer_name))
                reference_net = self._pedb.nets.get_net_by_name(layer_name)
                if not reference_net:  # pragma no cover
                    self._logger.error("reference net {} not found.".format(layer_name))
                    return False
            else:
                if not isinstance(reference_net, Net):  # pragma no cover
                    reference_net = self._pedb.nets.get_net_by_name(reference_net)
                if not reference_net:
                    self._logger.error("Net {} not found".format(reference_net))
                    return False
            terms = []
            pins = self._pedb.components.instances[component_name].pins
            for __pin in pins_name:
                if __pin in pins:
                    pin = pins[__pin]
                    term_name = f"{pin.component.name}_{pin.net.name}_{pin.component}"
                    start_layer, stop_layer = pin.get_layer_range()
                    if start_layer:
                        positive_terminal = PadstackInstanceTerminal.create(
                            layout=pin.layout, net=pin.net, padstack_instance=pin, name=term_name, layer=start_layer
                        )
                        positive_terminal.boundary_type = GrpcBoundaryType.PORT
                        positive_terminal.impedance = GrpcValue(impedance)
                        positive_terminal.Is_circuit_port = True
                        position = GrpcPointData(self._pedb.components.get_pin_position(pin))
                        negative_terminal = PointTerminal.create(
                            layout=self._pedb.active_layout,
                            net=reference_net,
                            layer=self._pedb.stackup.signal_layers[layer_name],
                            name=f"{term_name}_ref",
                            point=position,
                        )
                        negative_terminal.boundary_type = GrpcBoundaryType.PORT
                        negative_terminal.impedance = GrpcValue(impedance)
                        negative_terminal.is_circuit_port = True
                        positive_terminal.reference_terminal = negative_terminal
                        self._logger.info("Port {} successfully created".format(term_name))
                        if not positive_terminal.is_null:
                            terms.append(positive_terminal)
                else:
                    self._logger.error(f"pin {__pin} not found on component {component_name}")
                if terms:
                    return terms
            return False

    def create_current_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None
    ):
        """Create current source between two pin groups.

        Parameters
        ----------
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        magnitude : int, float, optional
            Magnitude of the source.
        phase : int, float, optional
            Phase of the source

        Returns
        -------
        bool

        """
        pos_pin_group = next(pg for pg in self._pedb.layout.pin_groups if pg.name == pos_pin_group_name)
        if not pos_pin_group:
            self._pedb.logger.error(f"Pin group {pos_pin_group_name} not found.")
            return False
        pos_terminal = pos_pin_group.create_current_source_terminal(magnitude, phase)
        if name:
            pos_terminal.name = name
        else:
            name = generate_unique_name("isource")
            pos_terminal.name = name
        neg_pin_group = next(pg for pg in self._pedb.layout.pin_groups if pg.name == neg_pin_group_name)
        if not neg_pin_group:
            self._pedb.logger.error(f"Pin group {pos_pin_group_name} not found.")
            return False
        neg_terminal = neg_pin_group.create_current_source_terminal()
        neg_terminal.name = f"{name}_ref"
        pos_terminal.reference_terminal = neg_terminal
        return True

    def create_voltage_source_on_pin_group(
        self, pos_pin_group_name, neg_pin_group_name, magnitude=1, phase=0, name=None, impedance=0.001
    ):
        """Create voltage source between two pin groups.

        Parameters
        ----------
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        magnitude : int, float, optional
            Magnitude of the source.
        phase : int, float, optional
            Phase of the source

        Returns
        -------
        bool

        """
        pos_pin_group = next(pg for pg in self._pedb.layout.pin_groups if pg.name == pos_pin_group_name)
        if not pos_pin_group:
            self._pedb.logger.error(f"Pingroup {pos_pin_group_name} not found.")
            return False
        pos_terminal = pos_pin_group.create_voltage_source_terminal(magnitude, phase, impedance)
        if name:
            pos_terminal.name = name
        else:
            name = generate_unique_name("vsource")
            pos_terminal.name = name
        neg_pin_group_name = next(pg for pg in self._pedb.layout.pin_groups if pg.name == neg_pin_group_name)
        if not neg_pin_group_name:
            self._pedb.logger.error(f"Pingroup {neg_pin_group_name} not found.")
            return False
        neg_terminal = neg_pin_group_name.create_voltage_source_terminal(magnitude, phase)
        neg_terminal.name = f"{name}_ref"
        pos_terminal.reference_terminal = neg_terminal
        return True

    def create_voltage_probe_on_pin_group(self, probe_name, pos_pin_group_name, neg_pin_group_name, impedance=1000000):
        """Create voltage probe between two pin groups.

        Parameters
        ----------
        probe_name : str
            Name of the probe.
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        impedance : int, float, optional
            Phase of the source.

        Returns
        -------
        bool

        """
        pos_pin_group = next(pg for pg in self._pedb.layout.pin_groups if pg.name == pos_pin_group_name)
        if not pos_pin_group:
            self._pedb.logger.error(f"Pingroup {pos_pin_group_name} not found.")
            return False
        pos_terminal = pos_pin_group.create_voltage_probe_terminal(impedance)
        if probe_name:
            pos_terminal.name = probe_name
        else:
            probe_name = generate_unique_name("vprobe")
            pos_terminal.name = probe_name
        neg_pin_group = next(pg for pg in self._pedb.layout.pin_groups if pg.name == neg_pin_group_name)
        if not neg_pin_group:
            self._pedb.logger.error(f"Pingroup {neg_pin_group_name} not found.")
            return False
        neg_terminal = neg_pin_group.create_voltage_probe_terminal()
        neg_terminal.name = f"{probe_name}_ref"
        pos_terminal.reference_terminal = neg_terminal
        return not pos_terminal.is_null

    def create_dc_terminal(
        self,
        component_name,
        net_name,
        source_name=None,
    ):
        """Create a dc terminal.

        Parameters
        ----------
        component_name : str
            Name of the positive component.
        net_name : str
            Name of the positive net.

        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            The name of the source.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.siwave.create_dc_terminal("U2A5", "V1P5_S3", "source_name")
        """

        node_pin = self._pedb.components.get_pin_from_component(component_name, net_name)
        if node_pin:
            node_pin = node_pin[0]
        if not source_name:
            source_name = f"DC_{component_name}_{net_name}"
        return self.create_pin_group_terminal(
            positive_pins=node_pin, name=source_name, source_type="dc_terminal", negatives_pins=None
        )

    def create_circuit_port_on_pin_group(self, pos_pin_group_name, neg_pin_group_name, impedance=50, name=None):
        """Create a port between two pin groups.

        Parameters
        ----------
        pos_pin_group_name : str
            Name of the positive pin group.
        neg_pin_group_name : str
            Name of the negative pin group.
        impedance : int, float, optional
            Impedance of the port. Default is ``50``.
        name : str, optional
            Port name.

        Returns
        -------
        bool

        """
        pos_pin_group = next(pg for pg in self._pedb.layout.pin_groups if pg.name == pos_pin_group_name)
        if not pos_pin_group:
            self._pedb.logger.error("No positive pin group found")
            return False
        pos_terminal = pos_pin_group.create_port_terminal(impedance)
        if name:  # pragma: no cover
            pos_terminal.name = name
        else:
            name = generate_unique_name("port")
            pos_terminal.name = name
        neg_pin_group = next(pg for pg in self._pedb.layout.pin_groups if pg.name == neg_pin_group_name)
        neg_terminal = neg_pin_group.create_port_terminal(impedance)
        neg_terminal.name = f"{name}_ref"
        pos_terminal.reference_terminal = neg_terminal
        return True

    def place_voltage_probe(
        self,
        name,
        positive_net_name,
        positive_location,
        positive_layer,
        negative_net_name,
        negative_location,
        negative_layer,
    ):
        """Place a voltage probe between two points.

        Parameters
        ----------
        name : str,
            Name of the probe.
        positive_net_name : str
            Name of the positive net.
        positive_location : list
            Location of the positive terminal.
        positive_layer : str,
            Layer of the positive terminal.
        negative_net_name : str,
            Name of the negative net.
        negative_location : list
            Location of the negative terminal.
        negative_layer : str
            Layer of the negative terminal.
        """
        p_terminal = PointTerminal.create(
            layout=self._pedb.active_layout,
            net=positive_net_name,
            layer=positive_layer,
            name=name,
            point=GrpcPointData(positive_location),
        )
        n_terminal = PointTerminal.create(
            layout=self._pedb.active_layout,
            net=negative_net_name,
            layer=negative_layer,
            name=f"{name}_ref",
            point=GrpcPointData(negative_location),
        )
        p_terminal.reference_terminal = n_terminal
        return self._pedb.create_voltage_probe(p_terminal, n_terminal)
