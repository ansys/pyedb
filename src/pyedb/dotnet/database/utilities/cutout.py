import os
import shutil
import time

from pyedb.dotnet.database.general import convert_py_list_to_net_list


class Cutout:
    def __init__(self, edb):
        self._edb = edb
        self.__signal_nets = []
        self.__reference_nets = []
        self.__extent_type = "ConvexHull"
        self.__expansion_size = 0.002
        self.__use_round_corner = False
        self.__output_aedb_path = None
        self.__open_cutout_at_end = True
        self.__use_pyaedt_cutout = True
        self.__smart_cutout = False
        self.__number_of_threads = 1
        self.__use_pyaedt_extent_computing = True
        self.__extent_defeature = 0
        self.__remove_single_pin_components = False
        self.__custom_extent = None
        self.__custom_extent_units = "mm"
        self.__include_partial_instances = False
        self.__keep_voids = True
        self.__check_terminals = False
        self.__include_pingroups = False
        self.__expansion_factor = 0
        self.__maximum_iterations = 10
        self.__preserve_components_with_model = False
        self.__simple_pad_check = True
        self.__keep_lines_as_path = False
        self.__include_voids_in_extents = False

    @property
    def remove_single_pin_components(self):
        """Whether to remove single pin components after cutout to simplify validation check."""
        return self.__remove_single_pin_components

    @remove_single_pin_components.setter
    def remove_single_pin_components(self, value):
        self.__remove_single_pin_components = value

    @property
    def simple_pad_check(self):
        """Whether to apply a simple padstack check on the center
        of the padstack or a complete check based on bounding box.
        Second option can be much slower."""
        return self.__simple_pad_check

    @simple_pad_check.setter
    def simple_pad_check(self, value):
        self.__simple_pad_check = value

    @property
    def signals(self):
        """List of signals to apply cutout."""
        return self.__signal_nets if isinstance(self.__signal_nets, list) else [self.__signal_nets]

    @signals.setter
    def signals(self, value):
        self.__signal_nets = value

    @property
    def references(self):
        """List of reference nets to apply cutout."""
        return self.__reference_nets if isinstance(self.__reference_nets, list) else [self.__reference_nets]

    @references.setter
    def references(self, value):
        self.__reference_nets = value

    @property
    def extent_type(self):
        """Extent type."""
        return self.__extent_type

    @extent_type.setter
    def extent_type(self, value):
        self.__extent_type = value

    @property
    def expansion_size(self):
        """Expansion size of the cutout in meters."""
        return self.__expansion_size

    @expansion_size.setter
    def expansion_size(self, value):
        self.__expansion_size = value

    @property
    def use_round_corner(self):
        """Whether to use round corner for extension or not.
        Default is ``False``."""
        return self.__use_round_corner

    @use_round_corner.setter
    def use_round_corner(self, value):
        self.__use_round_corner = value

    @property
    def output_file(self):
        """Output aedb path folder."""
        return self.__output_aedb_path

    @output_file.setter
    def output_file(self, value):
        self.__output_aedb_path = value

    @property
    def open_cutout_at_end(self):
        """Whether if open or not cutout file at the end."""
        return self.__open_cutout_at_end

    @open_cutout_at_end.setter
    def open_cutout_at_end(self, value):
        self.__open_cutout_at_end = value

    @property
    def use_pyaedt_cutout(self):
        """Use default pyaedt cutout instead of API cutout."""
        return self.__use_pyaedt_cutout

    @use_pyaedt_cutout.setter
    def use_pyaedt_cutout(self, value):
        self.__use_pyaedt_cutout = value

    @property
    def number_of_threads(self):
        """Number of threads to be used during pyaedt cutout."""
        return self.__number_of_threads

    @number_of_threads.setter
    def number_of_threads(self, value):
        self.__number_of_threads = value

    @property
    def use_pyaedt_extent_computing(self):
        """Use Pyaedt to compute extent."""
        return self.__use_pyaedt_extent_computing

    @use_pyaedt_extent_computing.setter
    def use_pyaedt_extent_computing(self, value):
        self.__use_pyaedt_extent_computing = value

    @property
    def extent_defeature(self):
        """Whether if defeature the extent after creation or not and relative value in meter.
        This applies only to conformal extent."""
        return self.__extent_defeature

    @extent_defeature.setter
    def extent_defeature(self, value):
        self.__extent_defeature = value

    @property
    def custom_extent(self):
        """Applies a custom extent point list to the cutout."""
        return self.__custom_extent

    @custom_extent.setter
    def custom_extent(self, value):
        self.__custom_extent = value

    @property
    def custom_extent_units(self):
        """Applies a custom extent point list to the cutout."""
        return self.__custom_extent_units

    @custom_extent_units.setter
    def custom_extent_units(self, value):
        self.__custom_extent_units = value

    @property
    def include_partial_instances(self):
        """Whether to include padstack instances that have bounding boxes intersecting with point list polygons.
        This operation may slow down the cutout export.Valid only if `custom_extend` and
        `use_pyaedt_cutout` is provided."""
        return self.__include_partial_instances

    @include_partial_instances.setter
    def include_partial_instances(self, value):
        self.__include_partial_instances = value

    @property
    def keep_voids(self):
        """Boolean used for keep or not the voids intersecting the polygon used for clipping the layout.
        Default value is ``True``, ``False`` will remove the voids.Valid only if `custom_extend` is provided.
        """
        return self.__keep_voids

    @keep_voids.setter
    def keep_voids(self, value):
        self.__keep_voids = value

    @property
    def check_terminals(self):
        """Whether to check for all reference terminals and increase extent to include them into the cutout.
        This applies to components which have a model (spice, touchstone or netlist) associated.
        """
        return self.__check_terminals

    @check_terminals.setter
    def check_terminals(self, value):
        self.__check_terminals = value

    @property
    def include_pingroups(self):
        """Whether to check for all pingroups terminals and increase extent to include them into the cutout.
        It requires ``check_terminals``.
        """
        return self.__include_pingroups

    @include_pingroups.setter
    def include_pingroups(self, value):
        self.__include_pingroups = value

    @property
    def preserve_components_with_model(self):
        """Whether to preserve all pins of components that have associated models (Spice or NPort).
        This parameter is applicable only for a PyAEDT cutout (except point list).
        """
        return self.__preserve_components_with_model

    @preserve_components_with_model.setter
    def preserve_components_with_model(self, value):
        self.__preserve_components_with_model = value

    @property
    def keep_lines_as_path(self):
        """Whether to keep the lines as Path after they are cutout or convert them to PolygonData.
        This feature works only in Electronics Desktop (3D Layout).
        If the flag is set to ``True`` it can cause issues in SiWave once the Edb is imported.
        Default is ``False`` to generate PolygonData of cut lines.
        """
        return self.__keep_lines_as_path

    @keep_lines_as_path.setter
    def keep_lines_as_path(self, value):
        self.__keep_lines_as_path = value

    @property
    def include_voids_in_extents(self):
        """Whether to compute and include voids in pyaedt extent before the cutout. Cutout time can be affected.
        It works only with Conforming cutout.
        Default is ``False`` to generate extent without voids.
        """
        return self.__include_voids_in_extents

    @include_voids_in_extents.setter
    def include_voids_in_extents(self, value):
        self.__include_voids_in_extents = value

    @property
    def smart_cutout(self):
        """Whether to apply smart cutout or not. If ``expansion_factor`` is 0 it will be set to 2."""
        return self.__smart_cutout

    @smart_cutout.setter
    def smart_cutout(self, value):
        self.__smart_cutout = value
        if value and self.expansion_factor == 0:
            self.expansion_factor = 2

    @property
    def expansion_factor(self):
        """The method computes a float representing the largest number between
        the dielectric thickness or trace width multiplied by the expansion_factor factor.
        The trace width search is limited to nets with ports attached. Works only if `use_pyaedt_cutout`.
        Default is `0` to disable the search.
        """
        return self.__expansion_factor

    @expansion_factor.setter
    def expansion_factor(self, value):
        self.__expansion_factor = value
        if value > 0:
            self.smart_cutout = True

    @property
    def maximum_iterations(self):
        """Maximum number of iterations before stopping a search for a cutout with an error.
        Default is `10`.
        """
        return self.__maximum_iterations

    @maximum_iterations.setter
    def maximum_iterations(self, value):
        self.__maximum_iterations = value

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
                        except:
                            pass
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
        if str(self.extent_type).lower() in ["conforming", "conformal", "1"]:
            _poly = self._create_conformal(
                1e-12,
            )
        elif str(self.extent_type).lower() in ["bounding", "0"]:
            _poly = self._edb.layout.expanded_extent(
                self.signals,
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
        elif str(self.extent_type).lower() in ["bounding", "0"]:
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
        expansion_size = self._edb.edb_value(self.expansion_size).ToDouble()

        # validate nets in layout
        net_signals = [net for net in self._edb.layout.nets if net.name in self.signals]

        # validate references in layout
        _netsClip = convert_py_list_to_net_list(
            [net.api_object for net in self._edb.layout.nets if net.name in self.references]
        )
        included_nets_list = self.signals + self.references
        included_nets = convert_py_list_to_net_list(
            [net.api_object for net in self._edb.layout.nets if net.name in included_nets_list]
        )
        _cutout = self._edb.active_cell.CutOut(included_nets, _netsClip, _poly, True)
        # Analysis setups do not come over with the clipped design copy,
        # so add the analysis setups from the original here.
        self._add_setups(_cutout)

        _dbCells = [_cutout]
        if self.output_file():
            db2 = self._edb.core.Database.Create(self.output_file())
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
                    except:
                        pass
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
                if result and self._edb.are_port_reference_terminals_connected():
                    if self.output_file:
                        if self.smart_cutout:
                            self.output_file = out_file
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
