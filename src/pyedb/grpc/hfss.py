"""
This module contains the ``EdbHfss`` class.
"""
import math
from pyedb.grpc.edb_core.edb_data.hfss_extent_info import HfssExtentInfo
from pyedb.grpc.edb_core.edb_data.ports import BundleWavePort
from pyedb.grpc.edb_core.edb_data.ports import WavePort
from pyedb.grpc.edb_core.edb_data.primitives_data import EDBPrimitives
from pyedb.grpc.edb_core.edb_data.simulation_configuration import SimulationConfiguration
from pyedb.generic.constants import RadiationBoxType
from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.modeler.geometry_operators import GeometryOperators
import ansys.edb.utility as utility
import ansys.edb.terminal as terminal
import ansys.edb.geometry as geometry
import ansys.edb.primitive as primitive
import ansys.edb.database as database
import ansys.edb.net as net
import ansys.edb.layer as layer
import ansys.edb.hierarchy as hierarchy
import ansys.edb.simulation_setup as simulation_setup
#from ansys.edb.utility.value import Value
#from ansys.edb.terminal.terminals import PrimitiveEdge
#from ansys.edb.terminal.terminals import EdgeTerminal
#from ansys.edb.terminal.terminals import BundleTerminal
#from ansys.edb.terminal.terminals import PadstackInstanceTerminal
#from ansys.edb.geometry.point_data import PointData
#from ansys.edb.database import ProductIdType
#from ansys.edb.net.net import Net
#from ansys.edb.layer.stackup_layer import Layer
#from ansys.edb.geometry.polygon_data import PolygonData
#from ansys.edb.primitive.primitive import PrimitiveType
#from ansys.edb.utility.hfss_extent_info import HfssExtentInfo
#from ansys.edb.hierarchy.component_group import ComponentGroup
#from ansys.edb.primitive.primitive import PadstackInstance
#from ansys.edb.terminal.terminals import Terminal
#from ansys.edb.hierarchy.component_group import ComponentType
#from ansys.edb.terminal.terminals import BoundaryType
#from ansys.edb.utility.rlc import Rlc
#from ansys.edb.simulation_setup.hfss_simulation_setup import HfssSimulationSetup


class EdbHfss(object):
    """Manages EDB method to configure Hfss setup accessible from `Edb.hfss` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edb_hfss = edb_3dedbapp.hfss
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def hfss_extent_info(self):
        """HFSS extent information."""
        return HfssExtentInfo(self._pedb)

    @property
    def _logger(self):
        return self._pedb.logger

    @property
    def _edb(self):
        """EDB object.

        Returns
        -------
        Ansys.Ansoft.Edb
        """
        return self._pedb

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _layout(self):
        return self._pedb.layout

    @property
    def _cell(self):
        return self._pedb.cell

    @property
    def _db(self):
        return self._pedb.active_db

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

    @pyedb_function_handler()
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
        if isinstance(point_on_edge, (list, tuple)):
            point_on_edge = self._edb.geometry.point_data(utility.Value(point_on_edge[0]),
                                                          utility.Value(point_on_edge[1]))
        if hasattr(prim_id, "GetId"):
            prim = prim_id
        else:
            prim = [i for i in self._pedb.modeler.primitives if i.id == prim_id][0].primitive_object
        pos_edge = terminal.PrimitiveEdge.create(prim, point_on_edge)
        return terminal.EdgeTerminal.create(prim.layout, prim.net, terminal_name, pos_edge, is_ref=is_ref)

    @pyedb_function_handler()
    def get_trace_width_for_traces_with_ports(self):
        """Retrieve the trace width for traces with ports.

        Returns
        -------<
        dict
            Dictionary of trace width data.
        """
        nets = {}
        for net in self._pedb.excitations_nets:
            smallest = self._pedb.nets[net].get_smallest_trace_width()
            if smallest < 1e10:
                nets[net] = self._pedb.nets[net].get_smallest_trace_width()
        return nets

    @pyedb_function_handler()
    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create Circuit Port on Pin.

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

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.hfss.create_circuit_port_on_pin(pins[0], pins[1],50,"port_name")

        Returns
        -------
        str
            Port Name.

        """
        return self._pedb.siwave.create_circuit_port_on_pin(pos_pin, neg_pin, impedance, port_name)

    @pyedb_function_handler()
    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
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
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.hfss.create_voltage_source_on_pin(pins[0], pins[1],50,"source_name")
        """
        return self._pedb.siwave.create_voltage_source_on_pin(pos_pin, neg_pin, voltage_value, phase_value, source_name)

    @pyedb_function_handler()
    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
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
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.hfss.create_current_source_on_pin(pins[0], pins[1],50,"source_name")
        """

        return self._pedb.siwave.create_current_source_on_pin(pos_pin, neg_pin, current_value, phase_value, source_name)

    @pyedb_function_handler()
    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a Resistor boundary between two given pins.

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
            Name of the Resistor.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.components.get_pin_from_component("U2A5")
        >>> edbapp.hfss.create_resistor_on_pin(pins[0], pins[1],50,"res_name")
        """
        return self._pedb.siwave.create_resistor_on_pin(pos_pin, neg_pin, rvalue, resistor_name)

    @pyedb_function_handler()
    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        impedance_value=50,
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
            Name of the negative net name. The default is ``"GND"``.
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
        >>> edbapp.hfss.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")
        """
        return self._pedb.siwave.create_circuit_port_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            impedance_value,
            port_name,
        )

    @pyedb_function_handler()
    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        voltage_value=3.3,
        phase_value=0,
        source_name="",
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
            Name of the negative net. The default is ``"GND"``.
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
        >>> edb.hfss.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")
        """
        return self._pedb.siwave.create_voltage_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            voltage_value,
            phase_value,
            source_name,
        )

    @pyedb_function_handler()
    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        current_value=0.1,
        phase_value=0,
        source_name="",
    ):
        """Create a current source.

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
            Name of the negative net. The default is ``"GND"``.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
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
        >>> edb.hfss.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")
        """
        return self._pedb.siwave.create_current_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            current_value,
            phase_value,
            source_name,
        )

    @pyedb_function_handler()
    def create_coax_port_on_component(self, ref_des_list, net_list):
        """Create a coaxial port on a component or component list on a net or net list.
           The name of the new coaxial port is automatically assigned.

        Parameters
        ----------
        ref_des_list : list, str
            List of one or more reference designators.

        net_list : list, str
            List of one or more nets.

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
            selected_pins = [pin for pin in list(self._pedb.components[ref].pins.values()) if not pin.net.is_null
                             and pin.net_name in net_list]
            for pin_inst in selected_pins:
                port_name = "{}_{}_{}".format(ref, pin_inst.net_name, pin_inst.pin.name)
                layer_range = pin_inst.pin.get_layer_range()
                if layer_range and terminal.PadstackInstanceTerminal.create(layout=self._layout,
                                                                        name= port_name,
                                                                        net=pin_inst.pin.net,
                                                                        padstack_instance=pin_inst.pin,
                                                                        layer=layer_range[1]):
                    coax.append(port_name)
        return coax

    @pyedb_function_handler
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
            The tuple contains: (port_name, pyaedt.edb_core.edb_data.sources.ExcitationDifferential).

        Examples
        --------
        >>> edb.hfss.create_differential_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])
        """
        if not port_name:
            port_name = generate_unique_name("diff")

        if isinstance(positive_primitive_id, EDBPrimitives):
            positive_primitive_id = positive_primitive_id.id

        if isinstance(negative_primitive_id, EDBPrimitives):
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
        _edb_boundle_terminal = BundleTerminal.create([pos_term._edb_object, neg_term._edb_object])
        pos_term._edb_object.name = port_name
        return port_name, BundleWavePort(self._pedb, _edb_boundle_terminal)

    @pyedb_function_handler
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
            The tuple contains: (port_name, pyaedt.edb_core.edb_data.sources.ExcitationDifferential).

        Examples
        --------
        >>> edb.hfss.create_bundle_wave_port(0, ["-50mm", "-0mm"], 1, ["-50mm", "-0.2mm"])
        """
        if not port_name:
            port_name = generate_unique_name("bundle_port")

        if isinstance(primitives_id[0], EDBPrimitives):
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

        _edb_bundle_terminal = BundleTerminal.create([i._edb_object for i in terminals])
        return port_name, BundleWavePort(self._pedb, _edb_bundle_terminal)

    @pyedb_function_handler()
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
        res, from_layer, to_layer = pinpos.layer_range

        if not portname:
            port_name = generate_unique_name("Port_" + pinpos.net.name)
        point_term = PadstackInstanceTerminal.create(self._active_layout, pinpos.net, portname, pinpos, to_layer)
        if point_term:
            return True
        else:
            return False

    @pyedb_function_handler()
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
            reference_layer = self._pedb.stackup.signal_layers[reference_layer]._edb_layer
            if not reference_layer:
                self._logger.error("Specified layer for port {} creation was not found".format(port_name))
        if not isinstance(terminal_point, list):
            self._logger.error("Terminal point must be a list of float with providing the point location in meter")
            return False
        terminal_point = PointData(Value(terminal_point[0]), Value(terminal_point[1]))
        if reference_point and isinstance(reference_point, list):
            reference_point = PointData(Value(reference_point[0]), Value(reference_point[1]))
        if not port_name:
            port_name = generate_unique_name("Port_")
        edge = PrimitiveEdge.create(polygon.prim_obj, (terminal_point.x.value, terminal_point.y.value))
        edge_term = EdgeTerminal.create(polygon.layout, polygon.net, port_name, [edge], is_ref=False)
        if force_circuit_port:
            edge_term.is_circuit_port = True
        else:
            edge_term.is_circuit_port = False

        if port_impedance:
            edge_term.impedance = Value(port_impedance)
        edge_term.name = port_name
        if reference_polygon and reference_point:
            ref_edge = PrimitiveEdge.create(reference_polygon.prim_obj, reference_point)
            ref_edge_term = EdgeTerminal.create(reference_polygon.layout, reference_polygon.net, port_name + "_ref",
                                                ref_edge, is_ref=True)
            if reference_layer:
                ref_edge_term.reference_layer = reference_layer
            if force_circuit_port:
                ref_edge_term.is_circuit_port = True
            else:
                ref_edge_term.is_circuit_port = False

            if port_impedance:
                ref_edge_term.impedance = Value(port_impedance)
            edge_term.reference_terminal = ref_edge_term
        return True

    @pyedb_function_handler()
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
        prim_id : int, EDBPrimitives
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
            The tuple contains: (Port name, pyaedt.edb_core.edb_data.sources.Excitation).

        Examples
        --------
        >>> edb.hfss.create_wave_port(0, ["-50mm", "-0mm"])
        """
        if not port_name:
            port_name = generate_unique_name("Terminal_")

        if isinstance(prim_id, EDBPrimitives):
            prim_id = prim_id.id

        pos_edge_term = self._create_edge_terminal(prim_id, point_on_edge, port_name)
        pos_edge_term.SetImpedance(self._pedb.edb_value(impedance))

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

    @pyedb_function_handler()
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
        pos_edge_term.impedance = Value(impedance)
        if reference_layer:
            reference_layer = self._pedb.stackup.signal_layers[reference_layer]._edb_layer
            pos_edge_term.reference_layer = reference_layer

        prop = ", ".join(
            [
                "HFSS('HFSS Type'='{}'".format(hfss_type),
                " Orientation='Vertical'",
                " 'Layer Alignment'='Upper'",
                " 'Horizontal Extent Factor'='{}'".format(horizontal_extent_factor),
                " 'Vertical Extent Factor'='{}'".format(vertical_extent_factor),
                " 'PEC Launch Width'='{}')".format(pec_launch_width),
            ]
        )
        pos_edge_term.product_solver_option(ProductIdType.DESIGNER, "HFSS", prop,)
        if pos_edge_term:
            return port_name, self._pedb.hfss.excitations[port_name]
        else:
            return False

    @pyedb_function_handler()
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

        pos_edge_term.impedance = Value(impedance)
        pos_edge_term.reference_terminal = neg_edge_term
        if not layer_alignment == "Upper":
            layer_alignment = "Lower"
        pos_edge_term.product_solver_option(ProductIdType.DESIGNER, "HFSS",
            "HFSS('HFSS Type'='Gap(coax)', Orientation='Horizontal', 'Layer Alignment'='{}')".format(layer_alignment),
        )
        if pos_edge_term:
            return port_name
        else:
            return False

    @pyedb_function_handler()
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
        if not isinstance(nets, list):
            if isinstance(nets, str):
                nets = [Net.find_by_name(self._active_layout, nets)]
            elif isinstance(nets, Net):
                nets = [nets]
        else:
            temp_nets = []
            for nn in nets:
                if isinstance(nn, str):
                    temp_nets.append(Net.find_by_name(self._active_layout, nn))
                elif isinstance(nn, Net):
                    temp_nets.append(nn)
            nets = temp_nets
        port_created = False
        if nets:
            edges_pts = []
            if isinstance(reference_layer, str):
                try:
                    reference_layer = self._pedb.stackup.signal_layers[reference_layer]._edb_layer
                except:
                    raise Exception("Failed to get the layer {}".format(reference_layer))
            if not isinstance(reference_layer, Layer):
                return False
            layout_bbox = self._pedb.get_conformal_polygon_from_netlist(self._pedb.nets.netlist)
            layout_extent_segments = [pt for pt in list(layout_bbox.arc_data) if pt.is_segment]
            first_pt = layout_extent_segments[0]
            layout_extent_points = [
                [first_pt.Start.x.value, first_pt.End.x.value],
                [first_pt.Start.y.value, first_pt.End.y.value],
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
                    port_name = "{}_{}".format(net.name, path.id)
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
                                    term.reference_layer = reference_layer  # pragma no cover
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
                                port_name = "{}_{}".format(net.name, poly.id)
                                term = self._create_edge_terminal(
                                    poly.id, segment.mid_point, port_name
                                )  # pragma no cover
                                term.reference_layer = reference_layer  # pragma no cover
                                port_created = True
            if return_points_only:
                return edges_pts
        return port_created

    @pyedb_function_handler()
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
                reference_net = self._pedb.nets[reference_net]
            if not reference_net:
                self._logger.error("No reference net provided for creating port")
                return False
            if user_defined_extent:
                if isinstance(user_defined_extent, PolygonData):
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
                net_polygons = [
                    pp
                    for pp in net.primitives
                    if pp.primitive_type == PrimitiveType.POLYGON
                ]
                for poly in net_polygons:
                    mid_points = [[arc.mid_point.x.value, arc.mid_point.y.value] for arc in poly.arcs]
                    for mid_point in mid_points:
                        if GeometryOperators.point_in_polygon(mid_point, user_defined_extent) == 0:
                            port_name = generate_unique_name("{}_{}".format(poly.net.name, poly.id))
                            term = self._create_edge_terminal(poly.id, mid_point, port_name)  # pragma no cover
                            if not term.is_null:
                                self._logger.info("Terminal {} created".format(term.name))
                                term.is_circuit_port = True
                                terminal_info.append([poly.net.name, mid_point[0], mid_point[1], term.name])
                                mid_pt_data = PointData(Value(mid_point[0]), Value(mid_point[1]))
                                ref_prim = [
                                    prim
                                    for prim in reference_net.primitives
                                    if prim.polygon_data.in_polygon(mid_pt_data)
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
                                        mid_pt_data = PointData(Value(new_point[0]), Value(new_point[1]))
                                        ref_prim = [
                                            prim
                                            for prim in reference_net.primitives
                                            if prim.polygon_data.in_polygon(mid_pt_data)
                                        ]
                                        if ref_prim:
                                            self._logger.info("Reference primitive found")
                                            break
                                    if not ref_prim:
                                        self._logger.error("Failed to collect valid reference primitives for terminal")
                                if ref_prim:
                                    reference_layer = ref_prim[0].layer
                                    term.reference_layer = reference_layer
            return terminal_info
        return False

    @pyedb_function_handler()
    def get_layout_bounding_box(self, layout=None, digit_resolution=6):
        """Evaluate the layout bounding box.

        Parameters
        ----------
        layout :
            Edb layout.

        digit_resolution : int, optional
            Digit Resolution. The default value is ``6``.
        Returns
        -------
        list
            [lower left corner X, lower left corner, upper right corner X, upper right corner Y]
        """
        if layout == None:
            return False
        layout_obj_instances = layout.layout_instance.query_layout_obj_instances()
        polygon_data_list = [lobj.layout_instance_context.get_bbox(False) for lobj in layout_obj_instances]
        _bbox = geometry.PolygonData.bbox_of_polygons(polygon_data_list)
        layout_bbox = [
            round(_bbox[0].x.value, digit_resolution),
            round(_bbox[0].y.value, digit_resolution),
            round(_bbox[1].x.value, digit_resolution),
            round(_bbox[1].y.value, digit_resolution),
        ]
        return layout_bbox

    @pyedb_function_handler()
    def configure_hfss_extents(self, simulation_setup=None):
        """Configure the HFSS extent box.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Configure HFSS extent requires edb_data.simulation_configuration.SimulationConfiguration object"
            )
            return False
        hfss_extent = self._pedb.active_cell.hfss_extent_info
        if simulation_setup.radiation_box == RadiationBoxType.BoundingBox:
            hfss_extent.extent_type = utility.HfssExtentInfo.HFSSExtentInfoType.BOUNDING_BOX
        elif simulation_setup.radiation_box == RadiationBoxType.Conformal:
            hfss_extent.extent_type = HfssExtentInfo.HFSSExtentInfoType.CONFORMING
        else:
            hfss_extent.extent_type = HfssExtentInfo.HFSSExtentInfoType.CONVEX_HUL
        hfss_extent.dielectric_extent_size = (simulation_setup.dielectric_extent,
                                            simulation_setup.use_dielectric_extent_multiple)
        hfss_extent.air_box_horizontal_extent = (simulation_setup.airbox_horizontal_extent,
                                                 simulation_setup.use_airbox_horizontal_extent_multiple)
        hfss_extent.air_box_negative_vertical_extent = (simulation_setup.airbox_negative_vertical_extent,
                                                        simulation_setup.use_airbox_negative_vertical_extent_multiple)

        hfss_extent.air_box_positive_vertical_extent = (simulation_setup.airbox_positive_vertical_extent,
                                                        simulation_setup.use_airbox_positive_vertical_extent_multiple)
        hfss_extent.honor_user_dielectric = simulation_setup.honor_user_dielectric
        hfss_extent.truncate_air_box_at_ground = simulation_setup.truncate_airbox_at_ground
        hfss_extent.use_open_region = simulation_setup.use_radiation_boundary
        self._layout.cell.set_hfss_extent_info(hfss_extent)
        return True

    @pyedb_function_handler()
    def configure_hfss_analysis_setup(self, simulation_setup=None):
        """
        Configure HFSS analysis setup.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """
        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Configure HFSS analysis requires and edb_data.simulation_configuration.SimulationConfiguration object \
                               as argument"
            )
            return False
        # to complete need to understand the new implementation
        # adapt = AdaptiveFrequency()
        # adapt.adaptive_frequency = simulation_setup.mesh_freq
        # adapt.max_num_passes = int(simulation_setup.max_num_passes)  # missing in pyedb
        # adapt.max_delta = str(simulation_setup.max_mag_delta_s)
        simsetup_info = HfssSimulationSetup()
        # simsetup_info.name = simulation_setup.setup_name
        # #simsetup_info.settings.advanced_meshing.use_arc_chord_error_approx = simulation_setup.arc_angle
        # simsetup_info.settings.advanced_meshing.arc_to_chord_error = simulation_setup.use_arc_to_chord_error
        # simsetup_info.settings.advanced_meshing.arc_to_chord_error = simulation_setup.arc_to_chord_error
        # simsetup_info.sweep_data.append() =
        # general.adaptive_solution_type..AdaptiveSettings.AdaptiveFrequencyDataList = convert_py_list_to_net_list(
        #         [adapt])
        # simsetup_info.SimulationSettings.InitialMeshSettings.LambdaRefine = simulation_setup.do_lambda_refinement
        # if simulation_setup.mesh_sizefactor > 0.0:
        #     simsetup_info.SimulationSettings.InitialMeshSettings.MeshSizefactor = simulation_setup.mesh_sizefactor
        #     simsetup_info.SimulationSettings.InitialMeshSettings.LambdaRefine = False
        # simsetup_info.SimulationSettings.AdaptiveSettings.MaxRefinePerPass = 30
        # simsetup_info.settings.options.min_passes = simulation_setup.min_num_passes
        # simsetup_info.settings.options.min_converged_passes = 1
        # simsetup_info.settings.options.order_basis = simulation_setup.basis_order
        # simsetup_info..HFSSSolverSettings.UseHFSSIterativeSolver = False
        # simsetup_info.SimulationSettings.DefeatureSettings.UseDefeature = False  # set True when using defeature ratio
        # simsetup_info.SimulationSettings.DefeatureSettings.UseDefeatureAbsLength = simulation_setup.defeature_layout
        # simsetup_info.SimulationSettings.DefeatureSettings.DefeatureAbsLength = simulation_setup.defeature_abs_length
        #
        # try:
        #     if simulation_setup.add_frequency_sweep:
        #         self._logger.info("Adding frequency sweep")
        #         sweep = self._pedb.simsetupdata.SweepData(simulation_setup.sweep_name)
        #         sweep.IsDiscrete = False
        #         sweep.UseQ3DForDC = simulation_setup.use_q3d_for_dc
        #         sweep.RelativeSError = simulation_setup.relative_error
        #         sweep.InterpUsePortImpedance = False
        #         sweep.EnforceCausality = simulation_setup.enforce_causality
        #         # sweep.EnforceCausality = False
        #         sweep.EnforcePassivity = simulation_setup.enforce_passivity
        #         sweep.PassivityTolerance = simulation_setup.passivity_tolerance
        #         sweep.Frequencies.Clear()
        #
        #         if simulation_setup.sweep_type == SweepType.LogCount:  # setup_info.SweepType == 'DecadeCount'
        #             self._setup_decade_count_sweep(
        #                 sweep,
        #                 str(simulation_setup.start_freq),
        #                 str(simulation_setup.stop_freq),
        #                 str(simulation_setup.decade_count),
        #             )  # Added DecadeCount as a new attribute
        #
        #         else:
        #             sweep.Frequencies = self._pedb.simsetupdata.SweepData.SetFrequencies(
        #                 simulation_setup.start_freq,
        #                 simulation_setup.stop_freq,
        #                 simulation_setup.step_freq,
        #             )
        #
        #         simsetup_info.SweepDataList.Add(sweep)
        #     else:
        #         self._logger.info("Adding frequency sweep disabled")
        #
        # except Exception as err:
        #     self._logger.error("Exception in Sweep configuration: {0}".format(err))
        #
        sim_setup = self._edb.utility.utility.HFSSSimulationSetup(simsetup_info)
        # for setup in self._layout.cell.SimulationSetups:
        #     self._layout.cell.DeleteSimulationSetup(setup.GetName())
        #     self._logger.warning("Setup {} has been deleted".format(setup.GetName()))
        return self._layout.cell.add_simulation_setup(sim_setup)

    def _setup_decade_count_sweep(self, sweep, start_freq="1", stop_freq="1MHz", decade_count="10"):
        start_f = GeometryOperators.parse_dim_arg(start_freq)
        if start_f == 0.0:
            start_f = 10
            self._logger.warning("Decade Count sweep does not support DC value, defaulting starting frequency to 10Hz")

        stop_f = GeometryOperators.parse_dim_arg(stop_freq)
        decade_cnt = GeometryOperators.parse_dim_arg(decade_count)
        freq = start_f
        sweep.Frequencies.Add(str(freq))

        while freq < stop_f:
            freq = freq * math.pow(10, 1.0 / decade_cnt)
            sweep.Frequencies.Add(str(freq))

    @pyedb_function_handler()
    def trim_component_reference_size(self, simulation_setup=None, trim_to_terminals=False):
        """Trim the common component reference to the minimally acceptable size.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        trim_to_terminals :
            bool.
                True, reduce the reference to a box covering only the active terminals (i.e. those with
        ports).
                False, reduce the reference to the minimal size needed to cover all pins

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Trim component reference size requires an edb_data.simulation_configuration.SimulationConfiguration \
                    object as argument"
            )
            return False

        if not simulation_setup.components:  # pragma: no cover
            return

        layout = self._cell.layout
        l_inst = layout.layout_instance

        for inst in simulation_setup.components:  # pragma: no cover
            comp = ComponentGroup.find(layout, inst)
            if comp.is_null:
                continue

            terms_bbox_pts = self._get_terminals_bbox(comp, l_inst, trim_to_terminals)
            if not terms_bbox_pts:
                continue

            terms_bbox = self._edb.geometry.polygon_data.create_from_bbox(terms_bbox_pts)

            if trim_to_terminals:
                # Remove any pins that aren't interior to the Terminals bbox
                pin_list = [
                    obj
                    for obj in list(comp.layout_objs)
                    if obj.obj_type == PadstackInstance
                ]
                for pin in pin_list:
                    loi = l_inst.get_layout_obj_instance(pin, None)
                    bb_c = loi.center
                    if not terms_bbox.in_polygon(bb_c):
                        comp.remove_member(pin)

            # Set the port property reference size
            cmp_prop = comp.component_property()
            port_prop = cmp_prop.port_property
            port_prop.reference_size_auto = False
            port_prop.SetReferenceSize(
                terms_bbox_pts[1].x.value - terms_bbox_pts[0].y.value,
                terms_bbox_pts[1].y.value - terms_bbox_pts[0].y.value,
            )
            cmp_prop.port_property = port_prop
            comp.component_property = cmp_prop
            return True

    @pyedb_function_handler()
    def set_coax_port_attributes(self, simulation_setup=None):
        """Set coaxial port attribute with forcing default impedance to 50 Ohms and adjusting the coaxial extent radius.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object.

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Set coax port attribute requires an edb_data.simulation_configuration.SimulationConfiguration object \
            as argument."
            )
            return False
        net_names = [net.name for net in self._layout.nets if not net.is_power_ground]
        cmp_names = (
            simulation_setup.components if simulation_setup.components else [gg.name for gg in self._layout.groups]
        )
        ii = 0
        for cc in cmp_names:
            cmp = ComponentGroup.find(self._active_layout, cc)
            if cmp.is_null:
                self._logger.warning("RenamePorts: could not find component {0}".format(cc))
                continue
            terms = [obj for obj in list(cmp.layout_objs) if obj.obj_type == Terminal]
            for nn in net_names:
                for tt in [term for term in terms if term.net.name == nn]:
                    if not tt.impedance(Value("50ohm")):
                        self._logger.warning("Could not set terminal {0} impedance as 50ohm".format(tt.name))
                        continue
                    ii += 1

            if not simulation_setup.use_default_coax_port_radial_extension:
                # Set the Radial Extent Factor
                typ = cmp.component_type
                if typ in [ComponentType.OTHER, ComponentType.IC, ComponentType.IO]:
                    cmp_prop = cmp.component_property
                    success, diam1, diam2 = cmp_prop.solder_ball_property.diameter
                    if success and diam1 and diam2 > 0:  # pragma: no cover
                        option = (
                            "HFSS('HFSS Type'='**Invalid**', "
                            "Orientation='**Invalid**', "
                            "'Layer Alignment'='Upper', "
                            "'Horizontal Extent Factor'='5', "
                            "'Vertical Extent Factor'='3', "
                            "'Radial Extent Factor'='0.25', "
                            "'PEC Launch Width'='0mm')"
                        )
                        for tt in terms:
                            tt.set_product_solver_option(ProductIdType.DESIGNER, "HFSS", option)
        return True

    @pyedb_function_handler()
    def _get_terminals_bbox(self, comp, l_inst, terminals_only):
        terms_loi = []
        if terminals_only:
            term_list = [
                obj for obj in list(comp.layout_objs) if obj.obj_type == Terminal
            ]
            for tt in term_list:
                success, p_inst, lyr = tt.parameters
                if success and lyr:
                    loi = l_inst.get_layout_obj_instance(p_inst, None)
                    terms_loi.append(loi)
        else:
            pin_list = [
                obj
                for obj in list(comp.layout_objs)
                if obj.obj_type == PadstackInstance
            ]
            for pi in pin_list:
                loi = l_inst.get_layout_obj_instance(pi, None)
                terms_loi.append(loi)

        if len(terms_loi) == 0:
            return None

        terms_bbox = []
        for loi in terms_loi:
            # Need to account for the coax port dimension
            bb = loi.bbox
            ll = [bb[0].x.value, bb[0].y.value]
            ur = [bb[1].x.value, bb[1].y.value]
            # dim = 0.26 * max(abs(UR[0]-LL[0]), abs(UR[1]-LL[1]))  # 0.25 corresponds to the default 0.5
            # Radial Extent Factor, so set slightly larger to avoid validation errors
            dim = 0.30 * max(abs(ur[0] - ll[0]), abs(ur[1] - ll[1]))  # 0.25 corresponds to the default 0.5
            terms_bbox.append(PolygonData(ll[0] - dim, ll[1] - dim, ur[0] + dim, ur[1] + dim))
        return self._edb.geometry.polygon_data.get_bbox_of_polygons(terms_bbox)

    @pyedb_function_handler()
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
        terms = [term for term in self._layout.terminals if int(term.boundary_type) == 0]
        return len([i for i in terms if not i.is_reference_terminal])

    @pyedb_function_handler()
    def layout_defeaturing(self, simulation_setup=None):
        """Defeature the layout by reducing the number of points for polygons based on surface deviation criteria.

        Parameters
        ----------
        simulation_setup : Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Layout defeaturing requires an edb_data.simulation_configuration.SimulationConfiguration object."
            )
            return False
        self._logger.info("Starting Layout Defeaturing")
        polygon_list = self._pedb.modeler.polygons
        polygon_with_voids = self._pedb.core_layout.get_poly_with_voids(polygon_list)
        self._logger.info("Number of polygons with voids found: {0}".format(str(polygon_with_voids.Count)))
        for _poly in polygon_list:
            voids_from_current_poly = _poly.Voids
            new_poly_data = self._pedb.core_layout.defeature_polygon(setup_info=simulation_setup, poly=_poly)
            _poly.polygon_dat = new_poly_data
            if len(voids_from_current_poly) > 0:
                for void in voids_from_current_poly:
                    void_data = void.polygon_data
                    if void_data.area < float(simulation_setup.minimum_void_surface):
                        void.delete()
                        self._logger.warning(
                            "Defeaturing Polygon {0}: Deleting Void {1} area is lower than the minimum criteria".format(
                                str(_poly.id), str(void.id)
                            )
                        )
                    else:
                        self._logger.info(
                            "Defeaturing polygon {0}: void {1}".format(str(_poly.id), str(void.id))
                        )
                        new_void_data = self._pedb.core_layout.defeature_polygon(
                            setup_info=simulation_setup, poly=void_data
                        )
                        void.SetPolygonData(new_void_data)

        return True

    @pyedb_function_handler()
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
            positive_pin_term = self._pedb.components._create_terminal(positive_pin)
            negative_pin_term = self._pedb.components._create_terminal(negative_pin)
            positive_pin_term.SetBoundaryType(BoundaryType.RLC)
            negative_pin_term.SetBoundaryType(BoundaryType.RLC)
            rlc = Rlc()
            rlc.is_parallel = True
            rlc.r_enabled = True
            rlc.l_enabled = True
            rlc.c_enabled = True
            rlc.R = Value(rvalue)
            rlc.L = Value(lvalue)
            rlc.C = Value(cvalue)
            positive_pin_term.rlc_boundary_parameters = rlc
            term_name = "{}_{}_{}".format(positive_pin.component.name, positive_pin.net.name, positive_pin.name            )
            positive_pin_term.name = term_name
            negative_pin_term.name = "{}_ref".format(term_name)
            positive_pin_term.reference_terminal = negative_pin_term
            return True
        return False  # pragma no cover
