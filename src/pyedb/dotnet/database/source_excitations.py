# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from pyedb.dotnet.database.cell.primitive.primitive import Primitive
from pyedb.dotnet.database.edb_data.ports import WavePort
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.point_data import PointData
from pyedb.generic.general_methods import generate_unique_name


class SourceExcitation:
    """Manage sources and excitations."""

    def __init__(self, pedb):
        self._pedb = pedb

    def get_edge_from_port(self, port):
        res, primitive, point = port._edb_object.GetEdges()[0].GetParameters()

        primitive = Primitive(self._pedb, primitive)
        point =[point.X.ToString(), point.Y.ToString()]
        return res, primitive, point

    def create_padstack_instance_terminal(self, name="", padstack_instance_id=None, padstack_instance_name=None):
        pds = self._pedb.layout.find_padstack_instances(
            instance_id=padstack_instance_id,
            aedt_name=padstack_instance_name,
            component_name=None,
            component_pin_name=None,
        )
        if len(pds) == 0:
            raise ValueError(f"Padstack instance {padstack_instance_id} or {padstack_instance_name} not found.")
        else:
            pds = pds[0]

        _name = name if name else generate_unique_name(pds.aedt_name)
        terminal = pds.create_terminal(name=_name)
        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: padstack_instance_id={padstack_instance_id}, "
                f"padstack_instance_name={padstack_instance_name}, name={name}."
            )
        return terminal

    def create_pin_group_terminal(self, pin_group, name=""):
        _name = name if name else generate_unique_name(pin_group)
        pg = self._pedb.siwave.pin_groups[pin_group]
        terminal = pg.create_terminal(name=_name)
        if terminal.is_null:
            raise RuntimeError(f"Failed to create terminal. Input arguments: pin_group={pin_group}, name={name}.")
        return terminal

    def create_point_terminal(self, x, y, layer, net, name=""):
        from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal

        _name = name if name else f"point_{layer}_{x}_{y}"
        location = [x, y]
        point_terminal = PointTerminal(self._pedb)
        terminal = point_terminal.create(_name, net, location, layer)
        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: x={x}, y={y}, layer={layer}, net={net}, name={name}."
            )
        return terminal

    def create_edge_terminal(self, primitive_name, x, y, name=""):
        from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal

        _name = name if name else f"{primitive_name}_{x}_{y}"

        pt = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(self._pedb, x=x, y=y)
        primitive = self._pedb.layout.primitives_by_aedt_name[primitive_name]
        edge = self._pedb.core.Cell.Terminal.PrimitiveEdge.Create(primitive._edb_object, pt._edb_object)
        edge = convert_py_list_to_net_list(edge, self._pedb.core.Cell.Terminal.Edge)
        _terminal = self._pedb.core.Cell.Terminal.EdgeTerminal.Create(
            primitive._edb_object.GetLayout(),
            primitive._edb_object.GetNet(),
            _name,
            edge,
            isRef=False,
        )
        terminal = EdgeTerminal(self._pedb, _terminal)

        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: primitive_name={primitive_name}, x={x}, y={y},"
                f" name={name}."
            )
        return terminal

    def create_bundle_terminal(self, terminals, name=""):
        from pyedb.dotnet.database.cell.terminal.bundle_terminal import BundleTerminal

        _name = name if name else f"{generate_unique_name('bundle')}"

        terminal = BundleTerminal.create(self._pedb, _name, terminals)
        bundle_term = terminal.terminals
        bundle_term[0].name = _name + ":T1"
        bundle_term[1].mame = _name + ":T2"

    def create_edge_port(self, location, primitive_name, name, impedance=50, is_wave_port=True,
                         horizontal_extent_factor=1, vertical_extent_factor=1, pec_launch_width=0.0001) -> WavePort:
        """Create an edge port on a primitive specific location.

        Parameters
        ----------
        location : list
            Port location.
        primitive_name : str
            Name of primitive.
        name : str
            Port name.
        impedance : float, optional
            Impedance.
        is_wave_port : bool, optional
            Whether if it is a wave port or gap port.
        horizontal_extent_factor : float, optional
            Horizontal extent factor for wave ports.
        vertical_extent_factor  : float, optional
            Vertical extent factor for wave ports.
        pec_launch_width : float, optional
            Pec launcher width for wave ports.

        """
        point_on_edge =  self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(self._pedb,
                self._pedb.value(location[0]), self._pedb.value(location[1])
            )._edb_object
        primitive = self._pedb.layout.primitives_by_aedt_name[primitive_name]
        pos_edge = self._pedb.core.Cell.Terminal.PrimitiveEdge.Create(primitive._edb_object, point_on_edge)
        pos_edge = convert_py_list_to_net_list(pos_edge, self._pedb.core.Cell.Terminal.Edge)
        edge_term = self._pedb.core.Cell.Terminal.EdgeTerminal.Create(
            primitive._edb_object.GetLayout(),
            primitive._edb_object.GetNet(),
            name,
            pos_edge,
            isRef=False,
        )
        edge_term.SetImpedance(self._pedb.edb_value(impedance))
        wave_port = WavePort(self._pedb, edge_term)
        wave_port.horizontal_extent_factor = horizontal_extent_factor
        wave_port.vertical_extent_factor = vertical_extent_factor
        wave_port.pec_launch_width = pec_launch_width
        if is_wave_port == "wave_port":
            wave_port.hfss_type = "Wave"
        else:
            wave_port.hfss_type = "Gap"
        wave_port.do_renormalize = True
        return wave_port



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
        terminal_point = self._pedb.pedb_class.database.geometry.point_data.PointData(
                self._pedb.value(terminal_point[0]), self._pedb.value(terminal_point[1])
            )
        if reference_point and isinstance(reference_point, list):
            reference_point = self._pedb.pedb_class.database.geometry.point_data.PointData(
                self._pedb.value(reference_point[0]), self._pedb.value(reference_point[1])
            )
        if not port_name:
            port_name = generate_unique_name("Port_")
        edge = self._edb.Cell.Terminal.PrimitiveEdge.Create(polygon._edb_object, terminal_point)
        edges = convert_py_list_to_net_list(edge, self._edb.Cell.Terminal.Edge)
        edge_term = self._edb.Cell.Terminal.EdgeTerminal.Create(
            polygon._edb_object.GetLayout(), polygon._edb_object.GetNet(), port_name, edges, isRef=False
        )
        if force_circuit_port:
            edge_term.SetIsCircuitPort(True)
        else:
            edge_term.SetIsCircuitPort(False)

        if port_impedance:
            edge_term.SetImpedance(self._pedb.edb_value(port_impedance))
        edge_term.SetName(port_name)
        if reference_polygon and reference_point:
            ref_edge = self._edb.Cell.Terminal.PrimitiveEdge.Create(reference_polygon._edb_object, reference_point)
            ref_edges = convert_py_list_to_net_list(ref_edge, self._edb.Cell.Terminal.Edge)
            ref_edge_term = self._edb.Cell.Terminal.EdgeTerminal.Create(
                reference_polygon._edb_object.GetLayout(),
                reference_polygon._edb_object.GetNet(),
                port_name + "_ref",
                ref_edges,
                isRef=True,
            )
            if reference_layer:
                ref_edge_term.SetReferenceLayer(reference_layer)
            if force_circuit_port:
                ref_edge_term.SetIsCircuitPort(True)
            else:
                ref_edge_term.SetIsCircuitPort(False)

            if port_impedance:
                ref_edge_term.SetImpedance(self._pedb.edb_value(port_impedance))
            edge_term.SetReferenceTerminal(ref_edge_term)
        return True

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
        >>> edb.hfss.create_wave_port(0, ["-50mm", "-0mm"])
        """
        if not port_name:
            port_name = generate_unique_name("Terminal_")

        if isinstance(prim_id, Primitive):
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
        pos_edge_term.SetImpedance(self._pedb.edb_value(impedance))
        if reference_layer:
            reference_layer = self._pedb.stackup.signal_layers[reference_layer]._edb_layer
            pos_edge_term.SetReferenceLayer(reference_layer)

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
        pos_edge_term.SetProductSolverOption(
            self._pedb.core.ProductId.Designer,
            "HFSS",
            prop,
        )
        if pos_edge_term:
            return port_name, self._pedb.hfss.excitations[port_name]
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

        pos_edge_term.SetImpedance(self._pedb.edb_value(impedance))
        pos_edge_term.SetReferenceTerminal(neg_edge_term)
        if not layer_alignment == "Upper":
            layer_alignment = "Lower"
        pos_edge_term.SetProductSolverOption(
            self._pedb.core.ProductId.Designer,
            "HFSS",
            "HFSS('HFSS Type'='Gap(coax)', Orientation='Horizontal', 'Layer Alignment'='{}')".format(layer_alignment),
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
        if not isinstance(nets, list):
            if isinstance(nets, str):
                nets = [self._edb.Cell.net.find_by_name(self._active_layout, nets)]
            elif isinstance(nets, self._edb.Cell.net.net):
                nets = [nets]
        else:
            temp_nets = []
            for nn in nets:
                if isinstance(nn, str):
                    temp_nets.append(self._edb.Cell.net.find_by_name(self._active_layout, nn))
                elif isinstance(nn, self._edb.Cell.net.net):
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
            if not isinstance(reference_layer, self._edb.Cell.ILayerReadOnly):
                return False
            layout = nets[0].GetLayout()
            layout_bbox = self._pedb.get_conformal_polygon_from_netlist(self._pedb.nets.netlist)
            layout_extent_segments = [pt for pt in list(layout_bbox.GetArcData()) if pt.IsSegment()]
            first_pt = layout_extent_segments[0]
            layout_extent_points = [
                [first_pt.Start.X.ToDouble(), first_pt.End.X.ToDouble()],
                [first_pt.Start.Y.ToDouble(), first_pt.End.Y.ToDouble()],
            ]
            for segment in layout_extent_segments[1:]:
                end_point = (segment.End.X.ToDouble(), segment.End.Y.ToDouble())
                layout_extent_points[0].append(end_point[0])
                layout_extent_points[1].append(end_point[1])
            for net in nets:
                net_primitives = self._pedb.nets[net.name].primitives
                net_paths = [pp for pp in net_primitives if pp.type == "Path"]
                for path in net_paths:
                    trace_path_pts = list(path.center_line.Points)
                    port_name = "{}_{}".format(net.name, path.GetId())
                    for pt in trace_path_pts:
                        _pt = [
                            round(pt.X.ToDouble(), digit_resolution),
                            round(pt.Y.ToDouble(), digit_resolution),
                        ]
                        if at_bounding_box:
                            if GeometryOperators.point_in_polygon(_pt, layout_extent_points) == 0:
                                if return_points_only:
                                    edges_pts.append(_pt)
                                else:
                                    term = self._create_edge_terminal(path.id, pt, port_name)  # pragma no cover
                                    term.SetReferenceLayer(reference_layer)  # pragma no cover
                                    port_created = True
                        else:
                            if return_points_only:  # pragma: no cover
                                edges_pts.append(_pt)
                            else:
                                term = self._create_edge_terminal(path.id, pt, port_name)
                                term.SetReferenceLayer(reference_layer)
                                port_created = True
                net_poly = [pp for pp in net_primitives if pp.type == "Polygon"]
                for poly in net_poly:
                    poly_segment = [aa for aa in poly.arcs if aa.is_segment]
                    for segment in poly_segment:
                        if (
                            GeometryOperators.point_in_polygon(
                                [segment.mid_point.X.ToDouble(), segment.mid_point.Y.ToDouble()], layout_extent_points
                            )
                            == 0
                        ):
                            if return_points_only:
                                edges_pts.append(segment.mid_point)
                            else:
                                port_name = "{}_{}".format(net.name, poly.GetId())
                                term = self._create_edge_terminal(
                                    poly.id, segment.mid_point, port_name
                                )  # pragma no cover
                                term.SetReferenceLayer(reference_layer)  # pragma no cover
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
                reference_net = self._pedb.nets[reference_net]
            if not reference_net:
                self._logger.error("No reference net provided for creating port")
                return False
            if user_defined_extent:
                if isinstance(user_defined_extent, self._edb.Geometry.PolygonData):
                    _points = [pt for pt in list(user_defined_extent.Points)]
                    _x = []
                    _y = []
                    for pt in _points:
                        if pt.X.ToDouble() < 1e100 and pt.Y.ToDouble() < 1e100:
                            _x.append(pt.X.ToDouble())
                            _y.append(pt.Y.ToDouble())
                    user_defined_extent = [_x, _y]
            terminal_info = []
            for net in nets:
                net_polygons = [
                    pp
                    for pp in net.primitives
                    if pp._edb_object.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Polygon
                ]
                for poly in net_polygons:
                    mid_points = [[arc.mid_point.X.ToDouble(), arc.mid_point.Y.ToDouble()] for arc in poly.arcs]
                    for mid_point in mid_points:
                        if GeometryOperators.point_in_polygon(mid_point, user_defined_extent) == 0:
                            port_name = generate_unique_name("{}_{}".format(poly.net.name, poly.id))
                            term = self._create_edge_terminal(poly.id, mid_point, port_name)  # pragma no cover
                            if not term.IsNull():
                                self._logger.info("Terminal {} created".format(term.GetName()))
                                term.SetIsCircuitPort(True)
                                terminal_info.append([poly.net.name, mid_point[0], mid_point[1], term.GetName()])
                                mid_pt_data = self._edb.Geometry.PointData(
                                    self._edb.Utility.Value(mid_point[0]), self._edb.Utility.Value(mid_point[1])
                                )
                                ref_prim = [
                                    prim
                                    for prim in reference_net.primitives
                                    if prim.polygon_data._edb_object.PointInPolygon(mid_pt_data)
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
                                        mid_pt_data = self._edb.Geometry.PointData(
                                            self._edb.Utility.Value(new_point[0]), self._edb.Utility.Value(new_point[1])
                                        )
                                        ref_prim = [
                                            prim
                                            for prim in reference_net.primitives
                                            if prim.polygon_data.core.PointInPolygon(mid_pt_data)
                                        ]
                                        if ref_prim:
                                            self._logger.info("Reference primitive found")
                                            break
                                    if not ref_prim:
                                        self._logger.error("Failed to collect valid reference primitives for terminal")
                                if ref_prim:
                                    reference_layer = ref_prim[0].layer._edb_layer
                                    if term.SetReferenceLayer(reference_layer):  # pragma no cover
                                        self._logger.info("Port {} created".format(port_name))
            return terminal_info
        return False
