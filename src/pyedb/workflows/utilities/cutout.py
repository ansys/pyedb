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


import os
import shutil
import time
from typing import List, Union

from ansys.edb.core.geometry.polygon_data import ExtentType as GrpcExtentType, PolygonData as GrpcPolygonData

from pyedb.dotnet.database.general import convert_py_list_to_net_list


class Cutout:
    def __new__(self, edb):
        if edb.grpc:
            return GrpcCutout(edb)
        else:
            return DotNetCutout(edb)


class GrpcCutout:
    """Create a clipped (cut-out) EDB cell from an existing layout.
    High-performance EDB cut-out utility.

    Attributes
    ----------
    signals : list[str]
        List of signal net names to keep in the cut-out.
    references : list[str]
        List of reference net names to keep in the cut-out.
    extent_type : str
        Extent algorithm: ``ConvexHull`` (default), ``Conforming``, ``Bounding``.
    expansion_size : float
        Additional margin (metres) around the computed extent.  Default 0.002.
    use_round_corner : bool
        Round the corners of the expanded extent.  Default ``False``.
    custom_extent : list[tuple[float, float]] | None
        Optional closed polygon [(x1,y1), …] overriding any automatic extent.
    custom_extent_units : str
        Length unit for *custom_extent*.  Default ``mm``.
    include_voids_in_extents : bool
        Include voids ≥ 5 % of the extent area when building the clip polygon.
    open_cutout_at_end : bool
        Open the resulting cut-out database in the active Edb object.  Default ``True``.
    use_pyaedt_cutout : bool
        Use the PyAEDT based implementation instead of native EDB API.  Default ``True``.
    smart_cutout : bool
        Automatically enlarge *expansion_size* until all ports have reference.  Default ``False``.
    expansion_factor : float
        If > 0, compute initial *expansion_size* from trace-width/dielectric.  Default 0.
    maximum_iterations : int
        Maximum attempts for *smart_cutout* before giving up.  Default 10.
    number_of_threads : int
        Worker threads for polygon clipping and padstack cleaning.  Default 1.
    remove_single_pin_components : bool
        Delete RLC components with only one pin after cut-out.  Default ``False``.
    preserve_components_with_model : bool
        Keep every pin of components that carry a Spice/S-parameter model.  Default ``False``.
    check_terminals : bool
        Grow extent until all reference terminals are inside the cut-out.  Default ``False``.
    include_pingroups : bool
        Ensure complete pin-groups are included (needs *check_terminals*).  Default ``False``.
    simple_pad_check : bool
        Use fast centre-point padstack check instead of bounding-box.  Default ``True``.
    keep_lines_as_path : bool
        Keep clipped traces as Path objects (3D Layout only).  Default ``False``.
    extent_defeature : float
        Defeature tolerance (metres) for conformal extent.  Default 0.
    include_partial_instances : bool
        Include padstacks that only partially overlap the clip polygon.  Default ``False``.
    keep_voids : bool
        Retain voids that intersect the clip polygon.  Default ``True``.


    The cut-out can be produced with three different extent strategies:

    * ``ConvexHull`` (default)
    * ``Conforming`` (tight follow of geometry)
    * ``Bounding`` (simple bounding box)

    Multi-threaded execution, automatic terminal expansion and smart
    expansion-factor logic are supported.

    Examples
    --------
    >>> cut = Cutout(edb)
    >>> cut.signals = ["DDR4_DQ0", "DDR4_DQ1"]
    >>> cut.references = ["GND"]
    >>> cut.expansion_size = 0.001
    >>> polygon = cut.run()
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, edb):
        self._edb = edb
        self.signals: List[str] = []  # list of signal nets
        self.references: List[str] = []  # list of reference nets
        self.extent_type: str = "ConvexHull"  # ConvexHull | Conforming | Bounding
        self.expansion_size: Union[str, float] = 0.002  # metres
        self.use_round_corner: bool = False
        self.output_file: str = ""  # output .aedb folder
        self.open_cutout_at_end: bool = True
        self.use_pyaedt_cutout: bool = True
        self.smart_cutout: bool = False
        self.number_of_threads: int = 2
        self.use_pyaedt_extent_computing: bool = True
        self.extent_defeature: Union[int, float] = 0
        self.remove_single_pin_components: bool = False
        self.custom_extent: List[float, float] = None
        self.custom_extent_units: str = "mm"
        self.include_partial_instances: bool = False
        self.keep_voids: bool = True
        self.check_terminals: bool = False
        self.include_pingroups: bool = False
        self.expansion_factor: Union[int, float] = 0
        self.maximum_iterations: int = 10
        self.preserve_components_with_model: bool = False
        self.simple_pad_check: bool = True
        self.keep_lines_as_path: bool = False
        self.include_voids_in_extents: bool = False

    @property
    def logger(self):
        """Edb logger."""
        return self._edb.logger

    @property
    def _modeler(self):
        return self._edb.modeler

    def calculate_initial_extent(self, expansion_factor):
        """Compute a float representing the larger number between the dielectric thickness or trace width
        multiplied by the nW factor. The trace width search is limited to nets with ports attached.

        Parameters
        ----------
        expansion_factor : float
            Value for the width multiplier (nW factor).

        Returns
        -------
        float
        """
        nets = []
        for port in self._edb.excitations.values():
            nets.append(port.net_name)
        for port in self._edb.sources.values():
            nets.append(port.net_name)
        nets = list(set(nets))
        max_width = 0
        for net in nets:
            for primitive in self._edb.nets[net].primitives:
                if primitive.type == "Path":
                    max_width = max(max_width, primitive.width)

        for layer in list(self._edb.stackup.dielectric_layers.values()):
            max_width = max(max_width, layer.thickness)

        max_width = max_width * expansion_factor
        self.logger.info("The W factor is {}, The initial extent = {:e}".format(expansion_factor, max_width))
        return max_width

    def _create_convex_hull(
        self,
        tolerance=1e-12,
    ):
        _polys = []
        _pins_to_preserve, _ = self.pins_to_preserve()
        if _pins_to_preserve:
            insts = self._edb.padstacks.instances
            for i in _pins_to_preserve:
                p = insts[i].position

                pos_1 = [i - 10e-6 for i in p]
                pos_3 = [i + 10e-6 for i in p]
                pos_4 = [pos_1[0], pos_3[1]]
                pos_2 = [pos_3[0], pos_1[1]]
                pts = [pos_1, pos_2, pos_3, pos_4, pos_1]
                rectangle_data = GrpcPolygonData(points=pts)
                _polys.append(rectangle_data)
        for prim in self._edb.modeler.primitives:
            if prim is not None and prim.net_name in self.signals:
                _polys.append(prim.core.polygon_data)
        if self.smart_cutout:
            objs_data = self._smart_cut()
            if objs_data:
                _polys.extend(objs_data)

        _poly = GrpcPolygonData.convex_hull(_polys)
        extent = _poly.expand(
            offset=self.expansion_size,
            round_corner=self.use_round_corner,
            max_corner_ext=self.expansion_size,
            tol=tolerance,
        )[0]
        return extent

    def _create_conformal(
        self,
        tolerance=1e-12,
    ):
        _polys = []
        _pins_to_preserve, _ = self.pins_to_preserve()
        if _pins_to_preserve:
            insts = self._edb.padstacks.instances
            for i in _pins_to_preserve:
                p = insts[i].position
                pos_1 = [i - 75e-6 for i in p]
                pos_2 = [i + 75e-6 for i in p]
                plane = self._edb.modeler.create_rectangle(lower_left_point=pos_1, upper_right_point=pos_2)
                rectangle_data = plane.polygon_data
                _polys.append(rectangle_data)

        for prim in self._edb.modeler.primitives:
            if prim is not None and prim.net_name in self.signals:
                _polys.append(prim)
        if self.smart_cutout:
            objs_data = self._smart_cut()
            _polys.extend(objs_data)
        k = 0
        expansion_size = self.expansion_size
        delta = self.expansion_size / 5
        _poly_unite = []
        while k < 10:
            unite_polys = []
            for i in _polys:
                if hasattr(i, "polygon_data"):
                    obj_data = i.polygon_data.core.expand(
                        offset=expansion_size,
                        round_corner=self.use_round_corner,
                        max_corner_ext=expansion_size,
                        tol=tolerance,
                    )
                else:
                    obj_data = i.core.expand(
                        offset=expansion_size,
                        round_corner=self.use_round_corner,
                        max_corner_ext=expansion_size,
                        tol=tolerance,
                    )
                if self.include_voids_in_extents and hasattr(i, "polygon_data") and i.core.has_voids and obj_data:
                    for void in i.voids:
                        void_data = void.polygon_data.expand(
                            offset=-1 * expansion_size,
                            round_corner=self.use_round_corner,
                            max_corner_ext=expansion_size,
                            tol=tolerance,
                        )
                        if void_data:
                            for v in list(void_data):
                                obj_data[0].add_hole(v)
                if obj_data:
                    if not self.include_voids_in_extents:
                        unite_polys.extend(list(obj_data))
                    else:
                        voids_poly = []
                        try:
                            if i.has_voids:
                                area = i.area()
                                for void in i.voids:
                                    void_polydata = void.polygon_data
                                    if void_polydata.area() >= 0.05 * area:
                                        voids_poly.append(void_polydata)
                                if voids_poly:
                                    obj_data = obj_data[0].subtract(list(obj_data), voids_poly)
                        except Exception as e:
                            self.logger.error(
                                f"A(n) {type(e).__name__} error occurred in method _create_conformal of "
                                f"class GrpcCutout at iteration {k} for data {i}: {str(e)}"
                            )
                        finally:
                            unite_polys.extend(list(obj_data))
            _poly_unite = GrpcPolygonData.unite(unite_polys)
            if len(_poly_unite) == 1:
                self.logger.info("Correctly computed Extension at first iteration.")
                return _poly_unite[0]
            k += 1
            expansion_size += delta
        if len(_poly_unite) == 1:
            self.logger.info("Correctly computed Extension in {} iterations.".format(k))
            return _poly_unite[0]
        else:
            self.logger.info("Failed to Correctly computed Extension.")
            areas = [i.area() for i in _poly_unite]
            return _poly_unite[areas.index(max(areas))]

    def _smart_cut(self):
        _polys = []
        terms = [term for term in self._edb.layout.terminals if int(term.boundary_type) in [0, 3, 4, 7, 8]]
        locations = []
        for term in terms:
            if term.net.name in self.references:
                position = term.position
                locations.append([position.x.value, position.y.value])
        for point in locations:
            points = [
                [self._edb.value(point[0] - self.expansion_size), self._edb.value(point[1] - self.expansion_size)],
                [self._edb.value(point[0] - self.expansion_size), self._edb.value(point[1] + self.expansion_size)],
                [self._edb.value(point[0] + self.expansion_size), self._edb.value(point[1] - self.expansion_size)],
                [self._edb.value(point[0] + self.expansion_size), self._edb.value(point[1] + self.expansion_size)],
            ]
            _polys.append(GrpcPolygonData(points=points))
        return _polys

    def pins_to_preserve(self):
        _pins_to_preserve = []
        _nets_to_preserve = []

        if self.preserve_components_with_model:
            for el in self._edb.layout.groups:
                if el.model_type in [
                    "SPICEModel",
                    "SParameterModel",
                    "NetlistModel",
                ] and list(set(el.nets[:]) & set(self.signals[:])):
                    _pins_to_preserve.extend([i.id for i in el.pins.values()])
                    _nets_to_preserve.extend(el.nets)
        if self.include_pingroups:
            for pingroup in self._edb.padstacks.pingroups:
                for pin in pingroup.pins.values():
                    if pin.net_name in self.references:
                        _pins_to_preserve.append(pin.id)
        return _pins_to_preserve, _nets_to_preserve

    def _compute_pyaedt_extent(self):
        signal_nets = [self._edb.nets.nets[n].core for n in self.signals]

        if str(self.extent_type).lower() in ["conforming", "conformal", "1"]:
            _poly = self._create_conformal(
                1e-12,
            )

        elif str(self.extent_type).lower() in ["bounding", "0", "bounding_box", "bbox", "boundingbox"]:
            _poly = self._edb.layout.core.expanded_extent(
                signal_nets,
                GrpcExtentType.BOUNDING_BOX,
                self.expansion_size,
                False,
                self.use_round_corner,
                1,
            )
        else:
            _poly = self._create_convex_hull(
                1e-12,
            )
            _poly_list = [_poly]
            _poly = GrpcPolygonData.convex_hull(_poly_list)
        return _poly

    def _compute_legacy_extent(self):
        if str(self.extent_type).lower() in ["conforming", "conformal", "1"]:
            extent_type = GrpcExtentType.CONFORMING
        elif str(self.extent_type).lower() in ["bounding", "bounding_box", "bbox", "0", "boundingbox"]:
            extent_type = GrpcExtentType.BOUNDING_BOX
        else:
            extent_type = self._edb.core.Geometry.ExtentType.ConvexHull
        _poly = self._edb.layout.expanded_extent(
            self.signals,
            extent_type,
            self.expansion_size,
            False,
            self.use_round_corner,
            1,
        )
        return _poly

    def _extent(self):
        """Compute extent with native EDB API."""
        if self.custom_extent:
            point_list = self.custom_extent[::]
            if point_list[0] != point_list[-1]:
                point_list.append(point_list[0])
            point_list = [
                [
                    self._edb.number_with_units(i[0], self.custom_extent_units),
                    self._edb.number_with_units(i[1], self.custom_extent_units),
                ]
                for i in point_list
            ]
            _poly = GrpcPolygonData(points=point_list)
        else:
            if self.use_pyaedt_extent_computing:
                _poly = self._compute_pyaedt_extent()
            else:
                _poly = self._compute_legacy_extent()
            _poly1 = _poly.without_arcs()
            if self.include_voids_in_extents:
                for hole in list(_poly.holes):
                    if hole.area() >= 0.05 * _poly1.area():
                        _poly1.add_hole(hole)
            _poly = _poly1
        return _poly

    def _add_setups(self, _cutout):
        id = 1
        for _setup in self._edb.active_cell.simulation_setups:
            # Empty string '' if coming from setup copy and don't set explicitly.
            _setup_name = _setup.name
            _setup.name = "HFSS Setup " + str(id)  # Set name of analysis setup
            # Write the simulation setup info into the cell/design setup
            # _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design
            # id += 1
            # _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design
            # finish adding setup for grpc

    def _create_cutout_legacy(
        self,
    ):
        _poly = self._extent()
        # Create new cutout cell/design
        # validate nets in layout
        net_signals = [net.core for net in self._edb.layout.nets if net.name in self.signals]

        # reference nets in layout
        ref_nets = [net.core for net in self._edb.layout.nets if net.name in self.references]

        # validate references in layout
        _netsClip = [net.core for net in self._edb.layout.nets if net.name in self.references]
        included_nets_list = net_signals + ref_nets
        # included_nets = [net for net in self._edb.layout.nets if net.name in included_nets_list]
        _cutout = self._edb.active_cell.cutout(included_nets_list, _netsClip, _poly, True)
        # Analysis setups do not come over with the clipped design copy,
        # so add the analysis setups from the original here.
        self._add_setups(_cutout)

        _dbCells = [_cutout]
        if self.output_file:
            from ansys.edb.core.database import Database as GrpcDatabase

            db2 = GrpcDatabase.create(self.output_file)
            _success = db2.save()
            db2.copy_cells(_dbCells)  # Copies cutout cell/design to db2 project
            if len(list(db2.top_circuit_cells)) > 0:
                for net in db2.top_circuit_cells[0].layout.nets:
                    if not net.name in included_nets_list:
                        net.delete()
                _success = db2.save()
            for c in self._edb._db.top_circuit_cells:
                if c.name == _cutout.name:
                    c.delete()
            if self.open_cutout_at_end:  # pragma: no cover
                self._edb._db = db2
                self._edb.edbpath = self.output_file
                self._edb._active_cell = self._edb.top_circuit_cells[0]
                self._edb.edbpath = self._edb.directory
                self._edb._init_objects()
                if self.remove_single_pin_components:
                    self._edb.components.delete_single_pin_rlc()
                    self.logger.info_timer("Single Pins components deleted")
                    self._edb.components.refresh_components()
            else:
                if self.remove_single_pin_components:
                    self._edb.components.delete_single_pin_rlc()
                    self.logger.info_timer("Single Pins components deleted")
                    self._edb.components.refresh_components()
                db2.close()
                source = os.path.join(self.output_file, "edb.def.tmp")
                target = os.path.join(self.output_file, "edb.def")
                if os.path.exists(source) and not os.path.exists(target):
                    try:
                        shutil.copy(source, target)
                    except Exception as e:
                        self.logger.error(f"Failed to copy {source} to {target} - {type(e).__name__}: {str(e)}")
        elif self.open_cutout_at_end:
            self._edb._active_cell = _cutout
            self._edb._init_objects()
            if self.remove_single_pin_components:
                self._edb.components.delete_single_pin_rlc()
                self.logger.info_timer("Single Pins components deleted")
                self._edb.components.refresh_components()
        return [[pt.x.value, pt.y.value] for pt in _poly.without_arcs().points]

    def _create_cutout_multithread(self):
        """
        Optimised cut-out that is GRPC friendly.
        EDB is **NOT** thread-safe and every write flushes the cache.
        -----------------------------------------------------------
        1.  READ  – collect everything that is required
        2.  COMPUTE – decide what has to be deleted / created
        3.  WRITE – one single, serial, write-pass
        -----------------------------------------------------------
        """
        _t0 = time.time()
        self.logger.info("GRPC cut-out started")
        timer_start = time.time()
        self.expansion_size = self._edb.value(self.expansion_size)

        # ------------------------------------------------------------------
        # 1.  READ ONLY – everything that can be queried without side effects
        # ------------------------------------------------------------------
        _t = time.time()
        all_nets = {net.name: net for net in self._edb.nets.nets.values()}
        all_padstack_instances = list(self._edb.padstacks.instances.values())
        all_primitives = list(self._edb.modeler.primitives)
        all_components = list(self._edb.components.instances.values())
        nets_num = len(all_nets)
        inst_num = len(all_padstack_instances)
        prim_num = len(all_primitives)
        comp_num = len(all_components)
        self.logger.info(f"[READ] Data collection finished in {time.time() - _t:.3f} s")
        self.logger.info(
            f"Nets:{nets_num}, padstack_instances:{inst_num}, primitives:{prim_num}, components:{comp_num}"
        )

        # preserve original net list logic
        if self.custom_extent:
            reference_list = (
                all_nets.keys() if not (self.signals or self.references) else self.signals + self.references
            )
            full_list = reference_list
        else:
            full_list = self.signals + self.references
            reference_list = self.references

        pins_to_preserve, nets_to_preserve = self.pins_to_preserve()

        # build extent polygon
        _t = time.time()
        extent_poly = self._extent()
        if not extent_poly.points:
            self.logger.error("Failed to create extent polygon")
            return []
        self.logger.info(f"[EXTENT] Polygon created in {time.time() - _t:.3f} s")

        # 2.  COMPUTE – decide what has to be deleted / created
        _t = time.time()
        # nets
        nets_to_delete = [
            net for name, net in all_nets.items() if name not in full_list and name not in nets_to_preserve
        ]

        # padstacks
        pins_to_delete, reference_pinsts = [], []
        for p in all_padstack_instances:
            if p.id in pins_to_preserve:
                continue
            if p.net_name not in full_list:
                pins_to_delete.append(p)
            elif p.net_name in reference_list:
                reference_pinsts.append(p)

        # primitives
        signal_prims, reference_prims, reference_paths, prim_to_delete = [], [], [], []
        for prim in all_primitives:
            if not prim:
                continue
            net = prim.net_name
            if net not in full_list and net not in nets_to_preserve:
                prim_to_delete.append(prim)
            elif net in self.signals:
                signal_prims.append(prim)
            elif net in reference_list and not prim.is_void:
                if self.keep_lines_as_path and prim.type == "path":
                    reference_paths.append(prim)
                else:
                    reference_prims.append(prim)

        # geometry clipping – only *compute* new polygons, do **not** create them yet
        pins_to_clip, prims_to_clip, poly_to_create = [], [], []

        # padstacks
        for p in reference_pinsts:
            if not p.in_polygon(extent_poly, include_partial=self.include_partial_instances):
                pins_to_clip.append(p)

        # paths
        for path in reference_paths:
            pdata = path.polygon_data
            if extent_poly.intersection_type(pdata) == 0:
                prims_to_clip.append(path)
                continue
            if not path.core.set_clip_info(extent_poly, True):
                # clipping failed – treat as polygon
                reference_prims.append(path)

        # reference primitives
        for prim in reference_prims:
            pdata = prim.polygon_data
            int_type = extent_poly.intersection_type(pdata).value
            if int_type in (0, 4):  # completely outside
                prims_to_clip.append(prim)
            elif int_type == 2:  # completely inside – keep
                continue
            elif int_type in (1, 3):  # partial – clip
                clipped_list = extent_poly.intersect(extent_poly, pdata)
                for p in clipped_list:
                    if not p.points:
                        continue
                    voids_data = [v.polygon_data for v in prim.voids]
                    if voids_data:
                        for poly_void in p.subtract(p, voids_data):
                            if poly_void.points:
                                poly_to_create.append([poly_void, prim.layer.name, prim.net_name, []])
                    else:
                        poly_to_create.append([p, prim.layer.name, prim.net_name, []])
                prims_to_clip.append(prim)

        # components
        components_to_delete = [comp for comp in all_components if comp.numpins == 0]
        self.logger.info(f"[COMPUTE] Decision lists ready in {time.time() - _t:.3f} s")
        # ------------------------------------------------------------------
        # 3.  WRITE – single serial pass, no interleaved reads
        # ------------------------------------------------------------------
        _t = time.time()
        self.logger.info("Starting single write-pass")
        self.logger.info(f"Deleting {len(nets_to_delete)} nets")
        for net in nets_to_delete:
            net.delete()

        # padstacks
        total_pins_to_delete = pins_to_delete + pins_to_clip
        _t1 = time.time()
        self._edb.padstacks.delete_batch_instances(total_pins_to_delete)
        self.logger.info(f"{len(total_pins_to_delete)} pad-stack instances deleted in {time.time() - _t1:.3f} s")

        # primitives
        total_primitive_to_delete = prim_to_delete + prims_to_clip + [v for prim in prims_to_clip for v in prim.voids]
        _t1 = time.time()
        self._edb.modeler.delete_batch_primitives(total_primitive_to_delete)
        self.logger.info(f"{len(total_primitive_to_delete)} primitives deleted in {time.time() - _t1:.3f} s")

        # new polygons
        _t1 = time.time()
        for p_data, layer, net, voids in poly_to_create:
            self._edb.modeler.create_polygon(p_data, layer, net_name=net, voids=voids)
        self.logger.info(f"{len(poly_to_create)} primitives created in {time.time() - _t1:.3f} s")

        # components
        _t1 = time.time()
        for comp in components_to_delete:
            comp.delete()
        if self.remove_single_pin_components:
            self._edb.components.delete_single_pin_rlc()
        self.logger.info(f"{len(components_to_delete)} components deleted in {time.time() - _t1:.3f} s")
        self._edb.components.refresh_components()
        self.logger.info(f"[WRITE] All writes finished in {time.time() - _t:.3f} s")

        # final save
        if self.output_file:
            self._edb.save_as(self.output_file)

        self.logger.info_timer("GRPC-safe cut-out completed", _t0)
        return [[pt.x.value, pt.y.value] for pt in extent_poly.without_arcs().points]

    def run(self):
        if not self.use_pyaedt_cutout:
            return self._create_cutout_legacy()
        else:
            out_file = self.output_file
            expansion_size = self.expansion_size
            if not self.smart_cutout:
                self.maximum_iterations = 1
                self.expansion_factor = 0
            elif self.expansion_factor > 0:
                expansion_size = self.calculate_initial_extent(self.expansion_factor)
                self._edb.save()
                self.output_file = self._edb.edbpath.replace(".aedb", "_smart_cutout_temp.aedb")

            legacy_path = self._edb.edbpath
            start = time.time()
            working_cutout = False
            i = 1
            expansion = self._edb.value(expansion_size)
            result = False
            while i <= self.maximum_iterations:
                self.logger.info("-----------------------------------------")
                self.logger.info(f"Trying cutout with {expansion * 1e3}mm expansion size")
                self.logger.info("-----------------------------------------")
                result = self._create_cutout_multithread()
                if result:
                    if self.smart_cutout:
                        if not self._edb.are_port_reference_terminals_connected():
                            raise RuntimeError("Smart cutout failed.")
                    self.output_file = out_file
                    if self.output_file:
                        self._edb.save_as(self.output_file)
                    else:
                        self._edb.save_as(legacy_path)
                    working_cutout = True
                    if not self.open_cutout_at_end and self._edb.edbpath != legacy_path:
                        self._edb.close()
                        self._edb.edbpath = legacy_path
                        self._edb.open_edb()
                    break
                self._edb.close()
                self._edb.edbpath = legacy_path
                self._edb.open_edb()
                i += 1
                expansion = expansion_size * i
            if working_cutout:
                msg = f"Cutout completed in {i} iterations with expansion size of {float(expansion) * 1e3}mm"
                self.logger.info_timer(msg, start)
            else:
                msg = f"Cutout failed after {i} iterations and expansion size of {float(expansion) * 1e3}mm"
                self.logger.info_timer(msg, start)
                return False
            return result


class DotNetCutout:
    """Create a clipped (cut-out) EDB cell from an existing layout.
    High-performance EDB cut-out utility.

    Attributes
    ----------
    signals : list[str]
        List of signal net names to keep in the cut-out.
    references : list[str]
        List of reference net names to keep in the cut-out.
    extent_type : str
        Extent algorithm: ``ConvexHull`` (default), ``Conforming``, ``Bounding``.
    expansion_size : float
        Additional margin (metres) around the computed extent.  Default 0.002.
    use_round_corner : bool
        Round the corners of the expanded extent.  Default ``False``.
    custom_extent : list[tuple[float, float]] | None
        Optional closed polygon [(x1,y1), …] overriding any automatic extent.
    custom_extent_units : str
        Length unit for *custom_extent*.  Default ``mm``.
    include_voids_in_extents : bool
        Include voids ≥ 5 % of the extent area when building the clip polygon.
    open_cutout_at_end : bool
        Open the resulting cut-out database in the active Edb object.  Default ``True``.
    use_pyaedt_cutout : bool
        Use the PyAEDT based implementation instead of native EDB API.  Default ``True``.
    smart_cutout : bool
        Automatically enlarge *expansion_size* until all ports have reference.  Default ``False``.
    expansion_factor : float
        If > 0, compute initial *expansion_size* from trace-width/dielectric.  Default 0.
    maximum_iterations : int
        Maximum attempts for *smart_cutout* before giving up.  Default 10.
    number_of_threads : int
        Worker threads for polygon clipping and padstack cleaning.  Default 1.
    remove_single_pin_components : bool
        Delete RLC components with only one pin after cut-out.  Default ``False``.
    preserve_components_with_model : bool
        Keep every pin of components that carry a Spice/S-parameter model.  Default ``False``.
    check_terminals : bool
        Grow extent until all reference terminals are inside the cut-out.  Default ``False``.
    include_pingroups : bool
        Ensure complete pin-groups are included (needs *check_terminals*).  Default ``False``.
    simple_pad_check : bool
        Use fast centre-point padstack check instead of bounding-box.  Default ``True``.
    keep_lines_as_path : bool
        Keep clipped traces as Path objects (3D Layout only).  Default ``False``.
    extent_defeature : float
        Defeature tolerance (metres) for conformal extent.  Default 0.
    include_partial_instances : bool
        Include padstacks that only partially overlap the clip polygon.  Default ``False``.
    keep_voids : bool
        Retain voids that intersect the clip polygon.  Default ``True``.


    The cut-out can be produced with three different extent strategies:

    * ``ConvexHull`` (default)
    * ``Conforming`` (tight follow of geometry)
    * ``Bounding`` (simple bounding box)

    Multi-threaded execution, automatic terminal expansion and smart
    expansion-factor logic are supported.

    Examples
    --------
    >>> cut = Cutout(edb)
    >>> cut.signals = ["DDR4_DQ0", "DDR4_DQ1"]
    >>> cut.references = ["GND"]
    >>> cut.expansion_size = 0.001
    >>> polygon = cut.run()
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, edb):
        self._edb = edb
        self.signals: List[str] = []  # list of signal nets
        self.references: List[str] = []  # list of reference nets
        self.extent_type: str = "ConvexHull"  # ConvexHull | Conforming | Bounding
        self.expansion_size: Union[str, float] = 0.002  # metres
        self.use_round_corner: bool = False
        self.output_file: str = ""  # output .aedb folder
        self.open_cutout_at_end: bool = True
        self.use_pyaedt_cutout: bool = True
        self.smart_cutout: bool = False
        self.number_of_threads: int = 2
        self.use_pyaedt_extent_computing: bool = True
        self.extent_defeature: Union[int, float] = 0
        self.remove_single_pin_components: bool = False
        self.custom_extent: List[float, float] = None
        self.custom_extent_units: str = "mm"
        self.include_partial_instances: bool = False
        self.keep_voids: bool = True
        self.check_terminals: bool = False
        self.include_pingroups: bool = False
        self.expansion_factor: Union[int, float] = 0
        self.maximum_iterations: int = 10
        self.preserve_components_with_model: bool = False
        self.simple_pad_check: bool = True
        self.keep_lines_as_path: bool = False
        self.include_voids_in_extents: bool = False

    @property
    def logger(self):
        """Edb logger."""
        return self._edb.logger

    @property
    def _modeler(self):
        return self._edb.modeler

    def calculate_initial_extent(self, expansion_factor):
        """Compute a float representing the larger number between the dielectric thickness or trace width
        multiplied by the nW factor. The trace width search is limited to nets with ports attached.

        Parameters
        ----------
        expansion_factor : float
            Value for the width multiplier (nW factor).

        Returns
        -------
        float
        """
        nets = []
        for port in self._edb.excitations.values():
            nets.append(port.net_name)
        for port in self._edb.sources.values():
            nets.append(port.net_name)
        nets = list(set(nets))
        max_width = 0
        for net in nets:
            for primitive in self._edb.nets[net].primitives:
                if primitive.type == "Path":
                    max_width = max(max_width, primitive.width)

        for layer in list(self._edb.stackup.dielectric_layers.values()):
            max_width = max(max_width, layer.thickness)

        max_width = max_width * expansion_factor
        self.logger.info("The W factor is {}, The initial extent = {:e}".format(expansion_factor, max_width))
        return max_width

    def _create_convex_hull(
        self,
        tolerance=1e-12,
    ):
        _polys = []
        _pins_to_preserve, _ = self.pins_to_preserve()
        if _pins_to_preserve:
            insts = self._edb.padstacks.instances
            for i in _pins_to_preserve:
                p = insts[i].position
                pos_1 = [i - 1e-12 for i in p]
                pos_2 = [i + 1e-12 for i in p]
                plane = self._edb.modeler.Shape("rectangle", pointA=pos_1, pointB=pos_2)
                rectangle_data = self._edb.modeler.shape_to_polygon_data(plane)
                _polys.append(rectangle_data)
        for prim in self._edb.modeler.primitives:
            if prim is not None and prim.net_name in self.signals:
                _polys.append(prim.primitive_object.GetPolygonData())
        if self.smart_cutout:
            objs_data = self._smart_cut()
            if objs_data:
                _polys.extend(objs_data)
        _poly = self._edb.core.Geometry.PolygonData.GetConvexHullOfPolygons(convert_py_list_to_net_list(_polys))
        _poly = _poly.Expand(self.expansion_size, tolerance, self.use_round_corner, self.expansion_size)
        _poly_list = convert_py_list_to_net_list(list(_poly)[0])
        _poly = self._edb.core.Geometry.PolygonData.GetConvexHullOfPolygons(_poly_list)
        return _poly

    def _create_conformal(
        self,
        tolerance=1e-12,
    ):
        _polys = []
        _pins_to_preserve, _ = self.pins_to_preserve()
        if _pins_to_preserve:
            insts = self._edb.padstacks.instances
            for i in _pins_to_preserve:
                p = insts[i].position
                pos_1 = [i - self.expansion_size for i in p]
                pos_2 = [i + self.expansion_size for i in p]
                plane = self._edb.modeler.Shape("rectangle", pointA=pos_1, pointB=pos_2)
                rectangle_data = self._edb.modeler.shape_to_polygon_data(plane)
                _polys.append(rectangle_data)

        for prim in self._edb.modeler.primitives:
            if prim is not None and prim.net_name in self.signals:
                _polys.append(prim)
        if self.smart_cutout:
            objs_data = self._smart_cut()
            _polys.extend(objs_data)
        k = 0
        expansion_size = self.expansion_size
        delta = self.expansion_size / 5
        _poly_unite = []
        while k < 10:
            unite_polys = []
            for i in _polys:
                if "PolygonData" not in str(i):
                    obj_data = i.primitive_object.GetPolygonData().Expand(
                        expansion_size, tolerance, self.use_round_corner, expansion_size
                    )
                else:
                    obj_data = i.Expand(expansion_size, tolerance, self.use_round_corner, expansion_size)
                if self.include_voids_in_extents and "PolygonData" not in str(i) and i.has_voids and obj_data:
                    for void in i.voids:
                        void_data = void.primitive_object.GetPolygonData().Expand(
                            -1 * expansion_size, tolerance, self.use_round_corner, expansion_size
                        )
                        if void_data:
                            for v in list(void_data):
                                obj_data[0].AddHole(v)
                if obj_data:
                    if not self.include_voids_in_extents:
                        unite_polys.extend(list(obj_data))
                    else:
                        voids_poly = []
                        try:
                            if i.HasVoids():
                                area = i.area()
                                for void in i.Voids:
                                    void_polydata = void.GetPolygonData()
                                    if void_polydata.Area() >= 0.05 * area:
                                        voids_poly.append(void_polydata)
                                if voids_poly:
                                    obj_data = obj_data[0].Subtract(
                                        convert_py_list_to_net_list(list(obj_data)),
                                        convert_py_list_to_net_list(voids_poly),
                                    )
                        except Exception as e:
                            self.logger.error(
                                f"A(n) {type(e).__name__} error occurred in method _create_conformal of "
                                f"class DotNetCutout at iteration {k} for data {i}: {str(e)}"
                            )
                        finally:
                            unite_polys.extend(list(obj_data))
            _poly_unite = self._edb.core.Geometry.PolygonData.Unite(convert_py_list_to_net_list(unite_polys))
            if len(_poly_unite) == 1:
                self.logger.info("Correctly computed Extension at first iteration.")
                return _poly_unite[0]
            k += 1
            expansion_size += delta
        if len(_poly_unite) == 1:
            self.logger.info("Correctly computed Extension in {} iterations.".format(k))
            return _poly_unite[0]
        else:
            self.logger.info("Failed to Correctly computed Extension.")
            areas = [i.Area() for i in _poly_unite]
            return _poly_unite[areas.index(max(areas))]

    def _smart_cut(self):
        from pyedb.dotnet.clr_module import Tuple

        _polys = []
        terms = [
            term for term in self._edb.layout.terminals if int(term._edb_object.GetBoundaryType()) in [0, 3, 4, 7, 8]
        ]
        locations = []
        for term in terms:
            if term._edb_object.GetTerminalType().ToString() == "PointTerminal" and term.net.name in self.references:
                pd = term._edb_object.GetParameters()[1]
                locations.append([pd.X.ToDouble(), pd.Y.ToDouble()])
        for point in locations:
            pointA = self._edb.core.geometry.point_data(
                self._edb.edb_value(point[0] - self.expansion_size),
                self._edb.edb_value(point[1] - self.expansion_size),
            )
            pointB = self._edb.core.geometry.point_data(
                self._edb.edb_value(point[0] + self.expansion_size),
                self._edb.edb_value(point[1] + self.expansion_size),
            )

            points = Tuple[
                self._edb.core.geometry.geometry.PointData,
                self._edb.core.geometry.geometry.PointData,
            ](pointA, pointB)
            _polys.append(self._edb.core.geometry.polygon_data.create_from_bbox(points))
        return _polys

    def pins_to_preserve(self):
        _pins_to_preserve = []
        _nets_to_preserve = []

        if self.preserve_components_with_model:
            for el in self._edb.layout.groups:
                if el.model_type in [
                    "SPICEModel",
                    "SParameterModel",
                    "NetlistModel",
                ] and list(set(el.nets[:]) & set(self.signals[:])):
                    _pins_to_preserve.extend([i.id for i in el.pins.values()])
                    _nets_to_preserve.extend(el.nets)
        if self.include_pingroups:
            for pingroup in self._edb.padstacks.pingroups:
                for pin in pingroup.pins.values():
                    if pin.net_name in self.references:
                        _pins_to_preserve.append(pin.id)
        return _pins_to_preserve, _nets_to_preserve

    def _compute_pyaedt_extent(self):
        signal_nets = [self._edb.nets.nets[n] for n in self.signals]

        if str(self.extent_type).lower() in ["conforming", "conformal", "1"]:
            _poly = self._create_conformal(
                1e-12,
            )

        elif str(self.extent_type).lower() in ["bounding", "0", "bounding_box", "bbox", "boundingbox"]:
            _poly = self._edb.layout.expanded_extent(
                signal_nets,
                self._edb.core.Geometry.ExtentType.BoundingBox,
                self.expansion_size,
                False,
                self.use_round_corner,
                1,
            )
        else:
            _poly = self._create_convex_hull(
                1e-12,
            )
            _poly_list = convert_py_list_to_net_list([_poly])
            _poly = self._edb.core.Geometry.PolygonData.GetConvexHullOfPolygons(_poly_list)
        return _poly

    def _compute_legacy_extent(self):
        if str(self.extent_type).lower() in ["conforming", "conformal", "1"]:
            extent_type = self._edb.core.Geometry.ExtentType.Conforming
        elif str(self.extent_type).lower() in ["bounding", "0", "bounding_box", "bbox", "boundingbox"]:
            extent_type = self._edb.core.Geometry.ExtentType.BoundingBox
        else:
            extent_type = self._edb.core.Geometry.ExtentType.ConvexHull
        _poly = self._edb.layout.expanded_extent(
            self.signals,
            extent_type,
            self.expansion_size,
            False,
            self.use_round_corner,
            1,
        )
        return _poly

    def _extent(self):
        """Compute extent with native EDB API."""
        if self.custom_extent:
            point_list = self.custom_extent[::]
            if point_list[0] != point_list[-1]:
                point_list.append(point_list[0])
            point_list = [
                [
                    self._edb.number_with_units(i[0], self.custom_extent_units),
                    self._edb.number_with_units(i[1], self.custom_extent_units),
                ]
                for i in point_list
            ]
            plane = self._modeler.Shape("polygon", points=point_list)
            _poly = self._modeler.shape_to_polygon_data(plane)
        else:
            if self.use_pyaedt_extent_computing:
                _poly = self._compute_pyaedt_extent()
            else:
                _poly = self._compute_legacy_extent()
            _poly1 = _poly.CreateFromArcs(_poly.GetArcData(), True)
            if self.include_voids_in_extents:
                for hole in list(_poly.Holes):
                    if hole.Area() >= 0.05 * _poly1.Area():
                        _poly1.AddHole(hole)
            _poly = _poly1
        return _poly

    def _add_setups(self, _cutout):
        id = 1
        for _setup in self._edb.active_cell.SimulationSetups:
            # Empty string '' if coming from setup copy and don't set explicitly.
            _setup_name = _setup.GetName()
            if "GetSimSetupInfo" in dir(_setup):
                # setup is an Ansys.Ansoft.Edb.Utility.HFSSSimulationSetup object
                _hfssSimSetupInfo = _setup.GetSimSetupInfo()
                _hfssSimSetupInfo.Name = "HFSS Setup " + str(id)  # Set name of analysis setup
                # Write the simulation setup info into the cell/design setup
                _setup.SetSimSetupInfo(_hfssSimSetupInfo)
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design
                id += 1
            else:
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design

    def _create_cutout_legacy(
        self,
    ):
        _poly = self._extent()
        # Create new cutout cell/design
        # validate nets in layout
        net_signals = [net for net in self._edb.layout.nets if net.name in self.signals]

        # reference nets in layout
        ref_nets = [net for net in self._edb.layout.nets if net.name in self.references]

        # validate references in layout
        _netsClip = convert_py_list_to_net_list(
            [net.api_object for net in self._edb.layout.nets if net.name in self.references]
        )
        included_nets_list = net_signals + ref_nets
        included_nets = convert_py_list_to_net_list(
            [net.api_object for net in self._edb.layout.nets if net.name in included_nets_list]
        )
        _cutout = self._edb.active_cell.CutOut(included_nets, _netsClip, _poly, True)
        # Analysis setups do not come over with the clipped design copy,
        # so add the analysis setups from the original here.
        self._add_setups(_cutout)

        _dbCells = [_cutout]
        if self.output_file:
            db2 = self._edb.core.Database.Create(self.output_file)
            _success = db2.Save()
            _dbCells = convert_py_list_to_net_list(_dbCells)
            db2.CopyCells(_dbCells)  # Copies cutout cell/design to db2 project
            if len(list(db2.CircuitCells)) > 0:
                for net in list(list(db2.CircuitCells)[0].GetLayout().Nets):
                    if not net.GetName() in included_nets_list:
                        net.Delete()
                _success = db2.Save()
            for c in list(self._edb._db.TopCircuitCells):
                if c.GetName() == _cutout.GetName():
                    c.Delete()
            if self.open_cutout_at_end:  # pragma: no cover
                self._edb._db = db2
                self._edb.edbpath = self.output_file
                self._edb._active_cell = list(self._edb.top_circuit_cells)[0]
                self._edb.edbpath = self._edb.directory
                self._edb._init_objects()
                if self.remove_single_pin_components:
                    self._edb.components.delete_single_pin_rlc()
                    self.logger.info_timer("Single Pins components deleted")
                    self._edb.components.refresh_components()
            else:
                if self.remove_single_pin_components:
                    self._edb.components.delete_single_pin_rlc()
                    self.logger.info_timer("Single Pins components deleted")
                    self._edb.components.refresh_components()
                db2.Close()
                source = os.path.join(self.output_file, "edb.def.tmp")
                target = os.path.join(self.output_file, "edb.def")
                self._edb._wait_for_file_release(file_to_release=self.output_file)
                if os.path.exists(source) and not os.path.exists(target):
                    try:
                        shutil.copy(source, target)
                    except Exception as e:
                        self.logger.error(f"Failed to copy {source} to {target} - {type(e).__name__}: {str(e)}")
        elif self.open_cutout_at_end:
            self._edb._active_cell = _cutout
            self._edb._init_objects()
            if self.__remove_single_pin_components:
                self._edb.components.delete_single_pin_rlc()
                self.logger.info_timer("Single Pins components deleted")
                self._edb.components.refresh_components()
        return [[pt.X.ToDouble(), pt.Y.ToDouble()] for pt in list(_poly.GetPolygonWithoutArcs().Points)]

    def _create_cutout_multithread(
        self,
    ):
        from concurrent.futures import ThreadPoolExecutor

        if self.output_file:
            self._edb.save_as(self.output_file)
        self.logger.info("Cutout Multithread started.")
        self.expansion_size = self._edb.value(self.expansion_size)

        timer_start = self.logger.reset_timer()
        if self.custom_extent:
            if not self.signals and not self.references:
                reference_list = self._edb.nets.netlist[::]
                all_list = reference_list
            else:
                reference_list = self.signals + self.references
                all_list = reference_list
        else:
            all_list = self.signals + self.references
            reference_list = self.references

        pins_to_preserve, nets_to_preserve = self.pins_to_preserve()
        for i in self._edb.nets.nets.values():
            name = i.name
            if name not in all_list and name not in nets_to_preserve:
                i.net_object.Delete()

        reference_pinsts = []
        reference_prims = []
        reference_paths = []
        pins_to_delete = []

        def check_instances(item):
            net_name = item.net_name
            item_id = item.id
            if net_name not in all_list and item_id not in pins_to_preserve:
                pins_to_delete.append(item)
            elif net_name in reference_list and item_id not in pins_to_preserve:
                reference_pinsts.append(item)

        with ThreadPoolExecutor(self.number_of_threads) as pool:
            pool.map(lambda item: check_instances(item), self._edb.layout.padstack_instances)

        for i in pins_to_delete:
            i.delete()

        prim_to_delete = []

        def check_prims(item):
            if item:
                net_name = item.net_name
                if net_name not in all_list:
                    prim_to_delete.append(item)
                elif net_name in reference_list and not item.is_void:
                    if self.keep_lines_as_path and item.type == "Path":
                        reference_paths.append(item)
                    else:
                        reference_prims.append(item)

        with ThreadPoolExecutor(self.number_of_threads) as pool:
            pool.map(lambda item: check_prims(item), self._edb.modeler.primitives)

        for i in prim_to_delete:
            i.delete()

        self.logger.info_timer("Net clean up")
        self.logger.reset_timer()

        _poly = self._extent()
        if not _poly or _poly.IsNull():
            self.logger.error("Failed to create Extent.")
            return []
        self.logger.info_timer("Extent Creation")
        self.logger.reset_timer()

        _poly_list = convert_py_list_to_net_list([_poly])
        prims_to_delete = []
        poly_to_create = []
        pins_to_delete = []

        def intersect(poly1, poly2):
            if not isinstance(poly2, list):
                poly2 = [poly2]
            return list(
                poly1.Intersect(
                    convert_py_list_to_net_list(poly1),
                    convert_py_list_to_net_list(poly2),
                )
            )

        def subtract(poly, voids):
            return poly.Subtract(convert_py_list_to_net_list(poly), convert_py_list_to_net_list(voids))

        def clip_path(path):
            pdata = path.polygon_data._edb_object
            int_data = _poly.GetIntersectionType(pdata)
            if int_data == 0:
                prims_to_delete.append(path)
                return
            result = path._edb_object.SetClipInfo(_poly, True)
            if not result:
                self.logger.info("Failed to clip path {}. Clipping as polygon.".format(path.id))
                reference_prims.append(path)

        def clean_prim(prim_1):  # pragma: no cover
            pdata = prim_1.polygon_data._edb_object
            int_data = _poly.GetIntersectionType(pdata)
            if int_data == 2:
                if not self.include_voids_in_extents:
                    return
                skip = False
                for hole in list(_poly.Holes):
                    if hole.GetIntersectionType(pdata) == 0:
                        prims_to_delete.append(prim_1)
                        return
                    elif hole.GetIntersectionType(pdata) == 1:
                        skip = True
                if skip:
                    return
            elif int_data == 0:
                prims_to_delete.append(prim_1)
                return
            list_poly = intersect(_poly, pdata)
            if list_poly:
                net = prim_1.net_name
                voids = prim_1.voids
                for p in list_poly:
                    if p.IsNull():
                        continue
                    # points = list(p.Points)
                    list_void = []
                    if voids:
                        voids_data = [void.polygon_data._edb_object for void in voids]
                        list_prims = subtract(p, voids_data)
                        for prim in list_prims:
                            if not prim.IsNull():
                                poly_to_create.append([prim, prim_1.layer.name, net, list_void])
                    else:
                        poly_to_create.append([p, prim_1.layer.name, net, list_void])

            prims_to_delete.append(prim_1)

        def pins_clean(pinst):
            if not pinst.in_polygon(
                _poly, include_partial=self.include_partial_instances, simple_check=self.simple_pad_check
            ):
                pins_to_delete.append(pinst)

        if not self.simple_pad_check:
            pad_cores = 1
        else:
            pad_cores = self.number_of_threads
        with ThreadPoolExecutor(pad_cores) as pool:
            pool.map(lambda item: pins_clean(item), reference_pinsts)

        for pin in pins_to_delete:
            pin.delete()

        self.logger.info_timer("{} Padstack Instances deleted.".format(len(pins_to_delete)))
        self.logger.reset_timer()

        with ThreadPoolExecutor(self.number_of_threads) as pool:
            pool.map(lambda item: clip_path(item), reference_paths)
        with ThreadPoolExecutor(self.number_of_threads) as pool:
            pool.map(lambda item: clean_prim(item), reference_prims)

        for el in poly_to_create:
            self._edb.modeler.create_polygon(el[0], el[1], net_name=el[2], voids=el[3])

        for prim in prims_to_delete:
            prim.delete()

        self.logger.info_timer("{} Primitives deleted.".format(len(prims_to_delete)))
        self.logger.reset_timer()

        i = 0
        for _, val in self._edb.components.instances.items():
            if val.numpins == 0:
                val.edbcomponent.Delete()
                i += 1
                i += 1
        self.logger.info("{} components deleted".format(i))
        if self.remove_single_pin_components:
            self._edb.components.delete_single_pin_rlc()
            self.logger.info_timer("Single Pins components deleted")

        self._edb.components.refresh_components()
        if self.output_file:
            self._edb.save_edb()
        self.logger.info_timer("Cutout completed.", timer_start)
        self.logger.reset_timer()
        return [[pt.X.ToDouble(), pt.Y.ToDouble()] for pt in list(_poly.GetPolygonWithoutArcs().Points)]

    def run(self):
        if not self.use_pyaedt_cutout:
            return self._create_cutout_legacy()
        else:
            out_file = self.output_file
            expansion_size = self.expansion_size
            if not self.smart_cutout:
                self.maximum_iterations = 1
                self.expansion_factor = 0
            elif self.expansion_factor > 0:
                expansion_size = self.calculate_initial_extent(self.expansion_factor)
                self._edb.save()
                self.output_file = self._edb.edbpath.replace(".aedb", "_smart_cutout_temp.aedb")

            legacy_path = self._edb.edbpath
            start = time.time()
            working_cutout = False
            i = 1
            expansion = self._edb.value(expansion_size)
            result = False
            while i <= self.maximum_iterations:
                self.logger.info("-----------------------------------------")
                self.logger.info(f"Trying cutout with {expansion * 1e3}mm expansion size")
                self.logger.info("-----------------------------------------")
                result = self._create_cutout_multithread()
                if result:
                    if self.smart_cutout:
                        if not self._edb.are_port_reference_terminals_connected():
                            raise RuntimeError("Smart cutout failed.")
                    self.output_file = out_file
                    if self.output_file:
                        self._edb.save_as(self.output_file)
                    else:
                        self._edb.save_as(legacy_path)
                    working_cutout = True
                    if not self.open_cutout_at_end and self._edb.edbpath != legacy_path:
                        self._edb.close()
                        self._edb.edbpath = legacy_path
                        self._edb.open_edb()
                    break
                self._edb.close()
                self._edb.edbpath = legacy_path
                self._edb.open_edb()
                i += 1
                expansion = expansion_size * i
            if working_cutout:
                msg = "Cutout completed in {} iterations with expansion size of {}mm".format(i, expansion * 1e3)
                self.logger.info_timer(msg, start)
            else:
                msg = "Cutout failed after {} iterations and expansion size of {}mm".format(i, expansion * 1e3)
                self.logger.info_timer(msg, start)
                return False
            return result
