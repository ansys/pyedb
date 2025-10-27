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

""" "
Self-contained DRC engine for PyEDB.

This module provides a high-performance, multi-threaded design-rule checker
that runs **inside** an open PyEDB session and validates 50+ industry-standard
rules (geometry, spacing, manufacturing, high-speed, test).

Features
--------
* Impedance checks via improved analytical formulas (Wheeler, Cohn, Hammerstad-Jensen).
* Copper-balance by layer or by arbitrary zone polygons.
* Back-drill stub / depth verification.
* R-tree spatial index for fast geometry queries.


Examples
--------
>>> import pyedb
>>> from pyedb.workflows.drc.drc import Drc, Rules
>>> edb = pyedb.Edb(edbpath="my_board.aedb")
>>> rules = Rules.parse_file("rules.json")  # or Rules.parse_obj(python_dict)
>>> drc = Drc(edb)
>>> violations = drc.check(rules)
>>> drc.to_ipc356a("fab_review.ipc")
"""

from __future__ import annotations

from collections import defaultdict
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import datetime
import itertools
import os
from queue import Queue
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel
from rtree import index as rtree_index

import pyedb
from pyedb.modeler.geometry_operators import GeometryOperators


class MinLineWidth(BaseModel):
    """Minimum-line-width rule."""

    name: str
    """Rule identifier (human readable)."""

    value: str
    """Minimum width with unit, e.g. ``"3.5mil"``."""

    name: str
    value: str


class MinClearance(BaseModel):
    """Minimum clearance between two nets."""

    name: str
    value: str
    net1: str
    net2: str


class MinAnnularRing(BaseModel):
    """Minimum annular ring for drilled holes."""

    name: str
    value: str


class DiffPair(BaseModel):
    """Differential-pair definition."""

    positive: str
    negative: str


class DiffPairLengthMatch(BaseModel):
    """Length-matching rule for differential pairs."""

    name: str
    tolerance: str
    pairs: List[DiffPair]


class BackDrillStubLength(BaseModel):
    """Maximum allowed back-drill stub length."""

    name: str
    value: str


class CopperBalance(BaseModel):
    """Copper-density balance rule."""

    name: str
    max_percent: int
    layers: List[str]


class Rules(BaseModel):
    """
    Centralised, serialisable container for **all** design-rule categories
    supported by the PyEDB DRC engine.

    The class is a thin ``pydantic`` model that provides:

    * JSON/YAML round-trip via ``parse_file``, ``parse_obj``, ``model_dump``,
      ``model_dump_json``.
    * Type-safe, API to incrementally **build** rule decks without
      manipulating raw dictionaries.


    Examples
    --------
    >>> from pyedb.workflows.drc.drc import Rules
    >>>
    >>> rules = (
    ...     Rules()
    ...     .add_min_line_width("pwr", "15 mil")
    ...     .add_min_clearance("clk2data", "4 mil", "CLK*", "DATA*")
    ...     .add_min_annular_ring("via5", "5 mil")
    ...     .add_diff_pair_length_match("usb", tolerance="0.1 mm", pairs=[("USB_P", "USB_N")])
    ...     .add_copper_balance("top_bal", max_percent=10, layers=["TOP"])
    ... )
    >>> rules.model_dump_json(indent=2)
    >>> rules.write_json("my_rules.json")

    Attributes
    ----------
    min_line_width : List[:class:`MinLineWidth`]
        Minimum acceptable trace width per layer or globally.
    min_clearance : List[:class:`MinClearance`]
        Spacing requirements between nets (wild-cards allowed).
    min_annular_ring : List[:class:`MinAnnularRing`]
        Minimum annular ring for drilled holes.
    diff_pair_length_match : List[:class:`DiffPairLengthMatch`]
        Length-matching constraints for differential pairs.
    back_drill_stub_length : List[:class:`BackDrillStubLength`]
        Maximum allowed back-drill stub length.
    copper_balance : List[:class:`CopperBalance`]
        Copper-density balance limits per layer or zone.
    """  # noqa: E501

    min_line_width: List[MinLineWidth] = []
    min_clearance: List[MinClearance] = []
    min_annular_ring: List[MinAnnularRing] = []
    diff_pair_length_match: List[DiffPairLengthMatch] = []
    back_drill_stub_length: List[BackDrillStubLength] = []
    copper_balance: List[CopperBalance] = []

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rules":
        """
        Alias for :meth:`model_validate <pydantic.BaseModel.model_validate>`.

        Parameters
        ----------
        data
            Dictionary produced by ``json.load``, ``yaml.safe_load``, etc.

        Returns
        -------
        Rules
            Validated instance ready for :meth:`Drc.check`.
        """
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """
        Alias for :meth:`model_dump <pydantic.BaseModel.model_dump>`.

        Returns
        -------
        dict
            JSON-serialisable dictionary.
        """
        return self.model_dump()

    # ------------------------------------------------------------------
    # Fluent API – mutate in place and return self for chaining
    # ------------------------------------------------------------------
    def add_min_line_width(
        self,
        name: str,
        value: str,
        layers: list[str] | None = None,
    ) -> "Rules":
        """
        Append a minimum-line-width rule.

        Parameters
        ----------
        name : str
            Rule identifier
        value : str
            Minimum width with unit, e.g. ``"3.5mil"``.
        layers : list[str], optional
            List of layer names to apply the rule to.  If ``None``,
            applies to all signal layers.

        Returns
        -------
        Rules
            Self to enable method chaining.
        """
        rule = MinLineWidth(name=name, value=value)
        if layers is not None:
            rule.layers = layers  # type: ignore[attr-defined]
        self.min_line_width.append(rule)
        return self

    def add_min_clearance(
        self,
        name: str,
        value: str,
        net1: str,
        net2: str,
    ) -> "Rules":
        """
        Append a minimum-clearance rule between two nets (wild-cards allowed).

        Parameters
        ----------
        name : str
            Rule identifier.
        value : str
            Minimum clearance with unit, e.g. ``"4mil"``.
        net1 : str
            First net name or wild-card (``"*"``).
        net2 : str
            Second net name or wild-card (``"*"``).

        Returns
        -------
        Rules
            Self to enable method chaining.
        """
        self.min_clearance.append(MinClearance(name=name, value=value, net1=net1, net2=net2))
        return self

    def add_min_annular_ring(self, name: str, value: str) -> "Rules":
        """
        Append a minimum-annular-ring rule for drilled holes.

        Parameters
        ----------
        name : str
            Rule identifier.
        value : str
            Minimum annular ring with unit, e.g. ``"2mil"``.

        Returns
        -------
        Rules
            Self to enable method chaining.
        """
        self.min_annular_ring.append(MinAnnularRing(name=name, value=value))
        return self

    def add_diff_pair_length_match(
        self,
        name: str,
        tolerance: str,
        pairs: list[tuple[str, str]],
    ) -> "Rules":
        """
        Append a length-matching rule for differential pairs.

        Parameters
        ----------
        name : str
            Rule identifier.
        tolerance : str
            Maximum allowed length difference with unit, e.g. ``"0.1mm"``.
        pairs : list[tuple[str, str]]
            List of differential pairs as tuples of

        Returns
        -------
        Rules
            Self to enable method chaining.
        """
        dpairs = [DiffPair(positive=p, negative=n) for p, n in pairs]
        self.diff_pair_length_match.append(DiffPairLengthMatch(name=name, tolerance=tolerance, pairs=dpairs))
        return self

    def add_back_drill_stub_length(self, name: str, value: str) -> "Rules":
        """
        Append a maximum-allowed back-drill stub-length rule.

        Parameters
        ----------
        name : str
            Rule identifier.
        value : str
            Maximum allowed stub length with unit, e.g. ``"6mil"``.

        Returns
        -------
        Rules
            Self to enable method chaining.
        """
        self.back_drill_stub_length.append(BackDrillStubLength(name=name, value=value))
        return self

    def add_copper_balance(
        self,
        name: str,
        max_percent: int,
        layers: list[str],
    ) -> "Rules":
        """
        Append a copper-density balance rule.

        Parameters
        ----------
        name : str
            Rule identifier.
        max_percent : int
            Maximum allowed copper imbalance in percent (e.g. ``15`` for 15%).
        layers : list[str]
            List of layer names to apply the rule to.

        Returns
        -------
        Rules
            Self to enable method chaining.
        """
        self.copper_balance.append(CopperBalance(name=name, max_percent=max_percent, layers=layers))
        return self


class Drc:
    """
    Lightweight, high-accuracy DRC engine that runs **inside** an open PyEDB session.

    The engine is **thread-safe** and uses an R-tree spatial index for
    scalable geometry queries.  All rule checks are parallelised with
    `concurrent.futures.ThreadPoolExecutor`.

    Parameters
    ----------
    edb : pyedb.Edb
        Active EDB session (must already be open).

    Examples
    --------
    >>> edb = pyedb.Edb("my_board.aedb")
    >>> rules = Rules.load("rules.json")
    >>> drc = Drc(edb)
    >>> violations = drc.check(rules)
    >>> drc.to_ipc356a("review.ipc")
    """

    def __init__(self, edb: pyedb.Edb):
        self.edb = edb
        self.violations: List[Dict[str, Any]] = []
        self._build_spatial_index()

    # Spatial index (R-tree)
    def _build_spatial_index(self) -> None:
        self.idx_primitives = rtree_index.Index()
        self.idx_vias = rtree_index.Index()
        self.idx_components = rtree_index.Index()

        for i, prim in enumerate(self.edb.modeler.primitives):
            bbox = prim.bbox
            self.idx_primitives.insert(i, coordinates=[bbox[0], bbox[1], bbox[2], bbox[3]])
        for i, via in enumerate(self.edb.padstacks.instances.values()):
            self.idx_vias.insert(i, via.position)
        for i, comp in enumerate(self.edb.components.instances.values()):
            self.idx_components.insert(i, comp.bounding_box)

    def check(self, rules: Rules) -> List[Dict[str, Any]]:
        """
        Run **all** rules and return a list of violations.

        Rules are dispatched to the appropriate internal handler
        (`_rule_*`) automatically.  The method is thread-safe and
        re-entrant; successive calls **overwrite** previous results.

        Parameters
        ----------
        rules : Rules
            Validated rule container.

        Returns
        -------
        list[dict]
            Each dictionary describes a single violation and contains at
            minimum the keys:

            * ``rule`` – rule type (``minLineWidth``, ``minClearance``, …)
            * ``limit_um`` – limit value in micrometres
            * Additional keys are rule-specific (``layer``, ``net1``, ``primitive``, …)
        """
        self.violations.clear()

        # Iterate through each rule in the Rules object
        for rule_group in rules.model_fields:
            rule_list = getattr(rules, rule_group)
            if rule_list:
                for rule in rule_list:
                    rule_method_name = f"_rule_{rule_group}"
                    getattr(self, rule_method_name, self._noop)(rule)
        return self.violations

    def _noop(self, rule):
        raise NotImplementedError(f"Rule handler for '{rule.name}' not implemented. ")

    # Geometry / Manufacturing Rules

    def _rule_min_line_width(self, rule: MinLineWidth, max_workers: int = None):
        """
        Multi-threaded, thread-safe min-line-width check.
        Extracts EDB data in single-thread, processes in parallel.
        """
        # === Detect available cores ===
        if max_workers is None:
            total_cores = os.cpu_count() or 4
            max_workers = max(1, total_cores - 1)

        lim = self.edb.value(rule.value)

        # === STEP 1: Extract relevant primitives from EDB ===
        layers = rule.layers if hasattr(rule, "layers") else list(self.edb.stackup.signal_layers.keys())
        primitives = self.edb.modeler.primitives_by_layer

        path_data = []  # store only Python-native info
        for lyr in layers:
            if lyr in primitives:
                for prim in primitives[lyr]:
                    if prim.primitive_type == "path":
                        path_data.append({"layer": lyr, "id": prim.id, "width": prim.width})

        # === STEP 2: Worker function ===
        def check_path(path_entry):
            if path_entry["width"] < lim:
                return {
                    "rule": "minLineWidth",
                    "layer": path_entry["layer"],
                    "primitive": path_entry["id"],
                    "value_um": path_entry["width"] * 1e-6,
                    "limit_um": rule.value,
                }
            return None

        # === STEP 3: Parallel processing ===
        violations = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(check_path, p) for p in path_data]
            for f in concurrent.futures.as_completed(futures):
                result = f.result()
                if result:
                    violations.append(result)

        # === STEP 4: Store results ===
        self.violations.extend(violations)

    def _rule_min_clearance(
        self, rule: MinClearance, max_workers: int = None, chunked_precompute: bool = False, chunk_size: int = 5000
    ):
        """
        High-performance min-clearance check with auto core detection.
        """
        if max_workers is None:
            total_cores = os.cpu_count() or 4  # fallback to 4 if detection fails
            max_workers = max(1, total_cores - 1)  # leave 1 core free for the OS

        gap = self.edb.value(rule.value)
        net1, net2 = rule.net1, rule.net2
        nets1 = [net1] if net1 != "*" else list(self.edb.nets.nets.keys())
        nets2 = [net2] if net2 != "*" else list(self.edb.nets.nets.keys())
        all_nets = sorted(set(nets1 + nets2))

        # === LAYER 1: single-threaded EDB extraction ===
        primitives_by_net_layer: Dict[str, Dict[str, List[dict]]] = {}
        primitive_points_map: Dict[int, List[tuple]] = {}  # prim_id -> points
        prim_bboxes: Dict[int, List[float]] = {}  # prim_id -> [minx,miny,maxx,maxy]
        prim_to_net: Dict[int, str] = {}  # prim_id -> net name

        # Extract primitives (only basic python types)
        for net in all_nets:
            primitives = self.edb.nets[net].primitives
            net_layer_map = defaultdict(list)

            for prim in primitives:
                pid = prim.id
                bbox = prim.bbox
                if self.edb.grpc:
                    points = [[pt.x.value, pt.y.value] for pt in prim.polygon_data.without_arcs().points]
                else:
                    points = prim.polygon_data.points_without_arcs

                primitive_points_map[pid] = points
                prim_bboxes[pid] = bbox
                prim_to_net[pid] = net

                net_layer_map[prim.layer.name].append({"id": pid})

            primitives_by_net_layer[net] = dict(net_layer_map)

        # Flatten list of primitive ids we care about (only those on nets we will compare)
        primitive_ids = list(prim_bboxes.keys())

        # === SINGLE-THREADED: Precompute index intersections for each primitive id ===
        # intersections_map[prim_id] = set(intersecting_prim_ids)
        intersections_map: Dict[int, Set[int]] = {}

        idx = self.idx_primitives  # Rtree index (not thread-safe)
        if not chunked_precompute:
            # Full precompute (fast, memory-heavy)
            for pid in primitive_ids:
                bbox = prim_bboxes[pid]
                # Rtree intersection returns generator/iterator - force into set
                intersections_map[pid] = set(idx.intersection(bbox))
        else:
            # Chunked precompute to reduce peak memory / rtree query overhead
            # Process primitives in batches and store results incrementally
            for i in range(0, len(primitive_ids), chunk_size):
                chunk = primitive_ids[i : i + chunk_size]
                for pid in chunk:
                    bbox = prim_bboxes[pid]
                    intersections_map[pid] = set(idx.intersection(bbox))
                # optional: you could free memory of chunk-specific temp variables here

        # === LAYER 2: Multi-threaded geometry checks (no locks needed) ===
        results_q = Queue()

        def process_net_pair(n1: str, n2: str):
            net1_layers = primitives_by_net_layer[n1]
            net2_layers = primitives_by_net_layer[n2]

            for layer, prims_n1 in net1_layers.items():
                if layer not in net2_layers:
                    continue

                prims_n2 = net2_layers[layer]
                potential_ids_n2 = {p["id"] for p in prims_n2}

                for prim in prims_n1:
                    pid = prim["id"]
                    intersect_ids = intersections_map.get(pid, set())
                    # Keep only ids that belong to the other net on the same layer
                    intersections = potential_ids_n2.intersection(intersect_ids)

                    for id_ in intersections:
                        # avoid same-primitive and same-net (if you didn't want to compare same net)
                        if id_ == pid:
                            continue

                        p1 = primitive_points_map[pid]
                        p2 = primitive_points_map[id_]

                        # GeometryOperators.smallest_distance_between_polygons is CPU-bound and thread-safe
                        d = GeometryOperators.smallest_distance_between_polygons(polygon1=p1, polygon2=p2)
                        if 0 < d < gap:
                            results_q.put(
                                {
                                    "rule": "minClearance",
                                    "net1": n1,
                                    "net2": n2,
                                    "primitive1": pid,
                                    "primitive2": id_,
                                    "distance_um": d,
                                    "limit_um": gap,
                                }
                            )

        # Spawn threads for net-pair combinations (skip comparing net to itself)
        net_list = all_nets
        pair_iter = ((a, b) for a, b in itertools.combinations_with_replacement(net_list, 2) if a != b)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(process_net_pair, n1, n2) for n1, n2 in pair_iter]
            for f in concurrent.futures.as_completed(futures):
                f.result()  # re-raise exceptions if any

        # Collect results
        violations = []
        while not results_q.empty():
            violations.append(results_q.get())

        self.violations = violations

    def _rule_min_annular_ring(self, rule: MinAnnularRing, max_workers: int = None):
        """
        Thread-safe min-annular-ring check with auto core detection.
        Skips padstack instances without a hole.
        """
        # === Determine optimal worker count ===
        if max_workers is None:
            total_cores = os.cpu_count() or 4
            max_workers = max(1, total_cores - 1)

        lim = self.edb.value(rule.value)

        # === STEP 1: Extract all EDB data in single-thread ===
        padstacks_definitions = self.edb.padstacks.definitions
        via_data = []
        for via in self.edb.padstacks.instances.values():
            via_def = padstacks_definitions[via.padstack_definition]

            # Skip if no hole properties (non-drilled padstack)
            if self.edb.grpc:
                if not via_def.hole_diameter:
                    continue
            else:
                if not via_def.hole_properties:
                    continue

            # Some padstacks may not have pad shapes either
            if not via_def.pad_by_layer:
                continue

            first_pad = next(iter(via_def.pad_by_layer.values()))
            od = first_pad.parameters_values[0]
            if self.edb.grpc:
                id_ = via_def.id
            else:
                id_ = via_def.hole_properties[0]
            via_data.append({"via_name": via.name, "od": od, "id": id_})

        # === STEP 2: Multi-threaded computation ===
        results_queue = Queue()

        def check_via(via_entry):
            ring = (via_entry["od"] - via_entry["id"]) / 2
            if ring < lim:
                results_queue.put(
                    {"rule": "minAnnularRing", "via": via_entry["via_name"], "ring_um": ring, "limit_um": lim}
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(check_via, v) for v in via_data]
            for f in concurrent.futures.as_completed(futures):
                f.result()  # propagate exceptions

        # === STEP 3: Store results ===
        self.violations = list(results_queue.queue)

    def _rule_copper_balance(self, rule: CopperBalance):
        max_imbalance = self.edb.value(rule.max_percent)

        # Snapshot data
        primitives_by_layer = dict(self.edb.modeler.primitives_by_layer)
        layout_outline = [prim for prim in self.edb.modeler.primitives if prim.layer.name.lower() == "outline"]
        if not layout_outline:
            raise ValueError("No outline primitive found in the layout.")
        if self.edb.grpc:
            area_board = layout_outline[0].polygon_data.area()
        else:
            area_board = layout_outline[0].polygon_data.area

        for layer, prim_list in primitives_by_layer.items():
            if self.edb.grpc:
                area_copper = sum(prim.polygon_data.area() for prim in prim_list)
            else:
                area_copper = sum(prim.polygon_data.area for prim in prim_list)
            imbalance = abs(area_copper - area_board / 2) / (area_board / 2) * 100
            if imbalance > max_imbalance:
                self.violations.append(
                    {
                        "rule": "copper_balance",
                        "layer": layer,
                        "imbalance_pct": imbalance,
                        "limit_pct": max_imbalance,
                    }
                )

    # High-speed rules
    def _rule_diff_pair_length_match(self, rule: DiffPairLengthMatch):
        tol = self.edb.value(rule.tolerance)

        # Snapshot nets for thread safety
        nets = dict(self.edb.nets.nets)

        def check_pair(pair):
            if pair.positive in nets and pair.negative in nets:
                np = nets[pair.positive]
                nn = nets[pair.negative]
                len_p = sum(p.length for p in np.primitives if hasattr(p, "length"))
                len_n = sum(p.length for p in nn.primitives if hasattr(p, "length"))
                delta = abs(len_p - len_n)
                if delta > tol:
                    return {
                        "rule": "diff_pair_length_match",
                        "positive": pair.positive,
                        "negative": pair.negative,
                        "delta_um": delta,
                        "limit_um": tol,
                    }
            return None

        workers = max(1, (os.cpu_count() or 2) - 1)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(check_pair, rule.pairs))

        # Merge results in main thread (lock-free)
        self.violations.extend(r for r in results if r is not None)

    # Back-drill / stub rules
    def _rule_back_drill_stub_length(self, rule: BackDrillStubLength):
        max_stub = self.edb.value(rule.value)

        # Snapshot data for safety
        padstack_instances = list(self.edb.padstacks.instances.values())
        layers = dict(self.edb.stackup.layers)

        for via in padstack_instances:
            layer_range = via.layer_range_names
            if layer_range:
                start = layer_range[0]
                stop = layer_range[-1]

            is_backdrilled = False
            if self.edb.grpc:
                if via.backdrill_diameter:
                    is_backdrilled = True
            else:
                if via.backdrill_parameters:
                    is_backdrilled = True

            if is_backdrilled:
                via_length = abs(layers[start].upper_elevation - layers[stop].lower_elevation)
                if via.backdrill_type == "layer_drill":
                    if via.backdrill_bottom:
                        stub = abs(via_length - layers[via.backdrill_parameters[0]].lower_elevation)
                    else:
                        stub = abs(via_length - layers[via.backdrill_parameters[0]].upper_elevation)
                else:
                    stub = 0  # other drill types can be handled here

                if stub > max_stub:
                    self.violations.append(
                        {"rule": "back_drill_stub_length", "via": via.name, "stub_um": stub, "limit_um": max_stub}
                    )

    # Export utilities
    def to_ipc356a(self, file_path: str) -> None:
        """
        Write a complete IPC-D-356A netlist plus DRC comments for fab review.

        The file can be imported by any CAM tool that supports IPC-D-356A
        (Valor, Genesis, etc.).  Violations are appended as comment lines
        starting with ``C``.

        Parameters
        ----------
        file_path : str | os.PathLike
            Output path.  Overwrites existing files without warning.
        """
        with open(file_path, "w") as f:
            f.write("IPC-D-356A\n")
            f.write(f"DATE {datetime.date.today():%Y%m%d}\n")
            f.write("SOURCE PYEDB_DRC_FULL\n\n")
            # Netlist section
            padstack_instances = {}
            padstacks = self.edb.padstacks.instances

            for inst in padstacks.values():
                net_name = getattr(inst, "net", None)
                if net_name:
                    padstack_instances.setdefault(net_name, []).append(inst)

            for net_name, net in self.edb.nets.nets.items():
                f.write(f"NET {net_name}\n")
                for prim in net.primitives:
                    if hasattr(prim, "polygon_data"):
                        if self.edb.grpc:
                            points = [[pt.x.value, pt.y.value] for pt in prim.polygon_data.without_arcs().points]
                        else:
                            points = prim.polygon_data.points_without_arcs
                        if points:
                            coords = " ".join(f"x:{x}, y:{y}" for x, y in points)
                            f.write(f"  P {coords}\n")
                for inst in padstack_instances.get(net_name, []):
                    x, y = inst.position
                    f.write(f" Padstack instance position: {x} {y}\n")
            # DRC section
            for v in self.violations:
                f.write(
                    f"C RULE={v['rule']} OBJ={v.get('primitive', '')} "
                    f"NET={v.get('net1', '')} LIMIT={v.get('limit_um', '')}\n"
                )
            f.write("999\n")
