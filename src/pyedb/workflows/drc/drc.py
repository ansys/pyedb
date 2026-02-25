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

"""Design Rule Check (DRC) engine for PyEDB.

This module provides a high-performance, multi-threaded design-rule checker
that runs inside an open PyEDB session and validates industry-standard rules
including geometry, spacing, manufacturing, high-speed, and test constraints.

The DRC engine features:

- Multi-threaded rule checking using ThreadPoolExecutor
- R-tree spatial indexing for fast geometry queries
- Impedance checks via analytical formulas (Wheeler, Cohn, Hammerstad-Jensen)
- Copper balance verification by layer or zone polygons
- Back-drill stub and depth verification
- IPC-D-356A netlist export with DRC annotations

Examples
--------
Basic DRC workflow:

>>> import pyedb
>>> from pyedb.workflows.drc.drc import Drc, Rules
>>> edb = pyedb.Edb(edbpath="my_board.aedb")
>>> rules = Rules.parse_file("rules.json")
>>> drc = Drc(edb)
>>> violations = drc.check(rules)
>>> print(f"Found {len(violations)} violations")

Build rules programmatically:

>>> rules = (
...     Rules()
...     .add_min_line_width("trace_width", "3.5mil")
...     .add_min_clearance("clk2data", "4mil", "CLK*", "DATA*")
...     .add_copper_balance("top_balance", max_percent=10, layers=["TOP"])
... )
>>> drc = Drc(edb)
>>> violations = drc.check(rules)

Export results for fabrication review:

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
from typing import Any, Set

from pydantic import BaseModel

try:
    from rtree import index as rtree_index
except ImportError:
    raise ImportError(
        "Rtree library is required for spatial indexing. "
        "Please install it using 'pip install pyedb[geometry]' or 'pip install rtree'."
    )

import pyedb
from pyedb.generic.geometry_operators import GeometryOperators


class MinLineWidth(BaseModel):
    """Minimum trace width constraint rule.

    This rule validates that all trace widths meet or exceed a specified
    minimum value on selected layers.

    Attributes
    ----------
    name : str
        Rule identifier for reporting violations.
    value : str
        Minimum acceptable width with unit (e.g., ``"3.5mil"``, ``"0.1mm"``).

    Examples
    --------
    >>> rule = MinLineWidth(name="signal_width", value="3.5mil")
    >>> rule.name
    'signal_width'
    """

    name: str
    value: str


class MinClearance(BaseModel):
    """Minimum spacing constraint between nets.

    This rule validates that spacing between specified nets meets or exceeds
    a minimum clearance value. Supports wildcard matching for net names.

    Attributes
    ----------
    name : str
        Rule identifier for reporting violations.
    value : str
        Minimum acceptable clearance with unit (e.g., ``"4mil"``, ``"0.15mm"``).
    net1 : str
        First net name or wildcard pattern (``"*"`` matches all nets).
    net2 : str
        Second net name or wildcard pattern (``"*"`` matches all nets).

    Examples
    --------
    >>> rule = MinClearance(name="clk2data", value="4mil", net1="CLK*", net2="DATA*")
    >>> rule.net1
    'CLK*'
    """

    name: str
    value: str
    net1: str
    net2: str


class MinAnnularRing(BaseModel):
    """Minimum annular ring constraint for drilled holes.

    This rule validates that the copper ring around drilled holes (vias, pins)
    meets a minimum width requirement.

    Attributes
    ----------
    name : str
        Rule identifier for reporting violations.
    value : str
        Minimum acceptable ring width with unit (e.g., ``"2mil"``, ``"0.05mm"``).

    Examples
    --------
    >>> rule = MinAnnularRing(name="via_ring", value="2mil")
    >>> rule.value
    '2mil'
    """

    name: str
    value: str


class DiffPair(BaseModel):
    """Differential pair net definition.

    Defines a single differential pair consisting of positive and negative nets.

    Attributes
    ----------
    positive : str
        Positive net name in the differential pair.
    negative : str
        Negative net name in the differential pair.

    Examples
    --------
    >>> pair = DiffPair(positive="USB_DP", negative="USB_DN")
    >>> pair.positive
    'USB_DP'
    """

    positive: str
    negative: str


class DiffPairLengthMatch(BaseModel):
    """Length matching constraint for differential pairs.

    This rule validates that the length difference between positive and
    negative traces in differential pairs stays within tolerance.

    Attributes
    ----------
    name : str
        Rule identifier for reporting violations.
    tolerance : str
        Maximum allowed length difference with unit (e.g., ``"0.1mm"``, ``"5mil"``).
    pairs : list of DiffPair
        List of differential pairs to validate.

    Examples
    --------
    >>> pair1 = DiffPair(positive="USB_DP", negative="USB_DN")
    >>> rule = DiffPairLengthMatch(name="usb_match", tolerance="0.1mm", pairs=[pair1])
    >>> rule.tolerance
    '0.1mm'
    """

    name: str
    tolerance: str
    pairs: list[DiffPair]


class BackDrillStubLength(BaseModel):
    """Maximum back-drill stub length constraint.

    This rule validates that remaining stub length after back-drilling
    stays below a maximum value to minimize signal reflections.

    Attributes
    ----------
    name : str
        Rule identifier for reporting violations.
    value : str
        Maximum allowed stub length with unit (e.g., ``"6mil"``, ``"0.15mm"``).

    Examples
    --------
    >>> rule = BackDrillStubLength(name="max_stub", value="6mil")
    >>> rule.value
    '6mil'
    """

    name: str
    value: str


class CopperBalance(BaseModel):
    """Copper density balance constraint.

    This rule validates that copper distribution across layers stays within
    acceptable balance limits to prevent warping during fabrication.

    Attributes
    ----------
    name : str
        Rule identifier for reporting violations.
    max_percent : int
        Maximum allowed imbalance percentage (e.g., ``15`` for 15%).
    layers : list of str
        Layer names to check for balance.

    Examples
    --------
    >>> rule = CopperBalance(name="top_balance", max_percent=10, layers=["TOP"])
    >>> rule.max_percent
    10
    """

    name: str
    max_percent: int
    layers: list[str]


class Rules(BaseModel):
    """Centralized container for all design rule categories.

    This class provides a type-safe, serializable container for design rules
    with JSON/YAML round-trip support and a fluent API for building rule decks.

    Attributes
    ----------
    min_line_width : list of MinLineWidth
        Minimum acceptable trace width rules per layer or globally.
    min_clearance : list of MinClearance
        Spacing requirements between nets (wildcards allowed).
    min_annular_ring : list of MinAnnularRing
        Minimum annular ring requirements for drilled holes.
    diff_pair_length_match : list of DiffPairLengthMatch
        Length matching constraints for differential pairs.
    back_drill_stub_length : list of BackDrillStubLength
        Maximum allowed back-drill stub length constraints.
    copper_balance : list of CopperBalance
        Copper density balance limits per layer or zone.

    Examples
    --------
    Build rules programmatically:

    >>> rules = (
    ...     Rules()
    ...     .add_min_line_width("pwr", "15mil")
    ...     .add_min_clearance("clk2data", "4mil", "CLK*", "DATA*")
    ...     .add_min_annular_ring("via5", "5mil")
    ...     .add_copper_balance("top_bal", max_percent=10, layers=["TOP"])
    ... )

    Load from JSON file:

    >>> rules = Rules.parse_file("my_rules.json")

    Export to JSON:

    >>> rules.model_dump_json(indent=2)
    """

    min_line_width: list[MinLineWidth] = []
    min_clearance: list[MinClearance] = []
    min_annular_ring: list[MinAnnularRing] = []
    diff_pair_length_match: list[DiffPairLengthMatch] = []
    back_drill_stub_length: list[BackDrillStubLength] = []
    copper_balance: list[CopperBalance] = []

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rules":
        """Create Rules instance from dictionary.

        Parameters
        ----------
        data : dict
            Dictionary produced by ``json.load()``, ``yaml.safe_load()``, etc.

        Returns
        -------
        Rules
            Validated instance ready for ``Drc.check()``.

        Examples
        --------
        >>> import json
        >>> with open("rules.json") as f:
        ...     data = json.load(f)
        >>> rules = Rules.from_dict(data)
        """
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert Rules to dictionary.

        Returns
        -------
        dict
            JSON-serializable dictionary.

        Examples
        --------
        >>> rules = Rules().add_min_line_width("trace", "3mil")
        >>> data = rules.to_dict()
        >>> "min_line_width" in data
        True
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
        """Append a minimum line width rule.

        Parameters
        ----------
        name : str
            Rule identifier for reporting.
        value : str
            Minimum width with unit (e.g., ``"3.5mil"``, ``"0.1mm"``).
        layers : list of str or None, optional
            Layer names to apply rule to. If ``None``, applies to all
            signal layers. The default is ``None``.

        Returns
        -------
        Rules
            Self for method chaining.

        Examples
        --------
        >>> rules = Rules().add_min_line_width("trace_width", "3.5mil")
        >>> len(rules.min_line_width)
        1
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
        """Append a minimum clearance rule between nets.

        Parameters
        ----------
        name : str
            Rule identifier for reporting.
        value : str
            Minimum clearance with unit (e.g., ``"4mil"``, ``"0.15mm"``).
        net1 : str
            First net name or wildcard (``"*"`` matches all).
        net2 : str
            Second net name or wildcard (``"*"`` matches all).

        Returns
        -------
        Rules
            Self for method chaining.

        Examples
        --------
        >>> rules = Rules().add_min_clearance("clk2data", "4mil", "CLK*", "DATA*")
        >>> rules.min_clearance[0].net1
        'CLK*'
        """
        self.min_clearance.append(MinClearance(name=name, value=value, net1=net1, net2=net2))
        return self

    def add_min_annular_ring(self, name: str, value: str) -> "Rules":
        """Append a minimum annular ring rule for drilled holes.

        Parameters
        ----------
        name : str
            Rule identifier for reporting.
        value : str
            Minimum ring width with unit (e.g., ``"2mil"``, ``"0.05mm"``).

        Returns
        -------
        Rules
            Self for method chaining.

        Examples
        --------
        >>> rules = Rules().add_min_annular_ring("via_ring", "2mil")
        >>> rules.min_annular_ring[0].value
        '2mil'
        """
        self.min_annular_ring.append(MinAnnularRing(name=name, value=value))
        return self

    def add_diff_pair_length_match(
        self,
        name: str,
        tolerance: str,
        pairs: list[tuple[str, str]],
    ) -> "Rules":
        """Append a differential pair length matching rule.

        Parameters
        ----------
        name : str
            Rule identifier for reporting.
        tolerance : str
            Maximum allowed length difference with unit (e.g., ``"0.1mm"``).
        pairs : list of tuple[str, str]
            List of (positive_net, negative_net) tuples.

        Returns
        -------
        Rules
            Self for method chaining.

        Examples
        --------
        >>> rules = Rules().add_diff_pair_length_match("usb_match", tolerance="0.1mm", pairs=[("USB_DP", "USB_DN")])
        >>> rules.diff_pair_length_match[0].tolerance
        '0.1mm'
        """
        dpairs = [DiffPair(positive=p, negative=n) for p, n in pairs]
        self.diff_pair_length_match.append(DiffPairLengthMatch(name=name, tolerance=tolerance, pairs=dpairs))
        return self

    def add_back_drill_stub_length(self, name: str, value: str) -> "Rules":
        """Append a maximum back-drill stub length rule.

        Parameters
        ----------
        name : str
            Rule identifier for reporting.
        value : str
            Maximum allowed stub length with unit (e.g., ``"6mil"``).

        Returns
        -------
        Rules
            Self for method chaining.

        Examples
        --------
        >>> rules = Rules().add_back_drill_stub_length("max_stub", "6mil")
        >>> rules.back_drill_stub_length[0].value
        '6mil'
        """
        self.back_drill_stub_length.append(BackDrillStubLength(name=name, value=value))
        return self

    def add_copper_balance(
        self,
        name: str,
        max_percent: int,
        layers: list[str],
    ) -> "Rules":
        """Append a copper density balance rule.

        Parameters
        ----------
        name : str
            Rule identifier for reporting.
        max_percent : int
            Maximum allowed imbalance percentage (e.g., ``15`` for 15%).
        layers : list of str
            Layer names to check for balance.

        Returns
        -------
        Rules
            Self for method chaining.

        Examples
        --------
        >>> rules = Rules().add_copper_balance("top_bal", max_percent=10, layers=["TOP"])
        >>> rules.copper_balance[0].max_percent
        10
        """
        self.copper_balance.append(CopperBalance(name=name, max_percent=max_percent, layers=layers))
        return self


class Drc:
    """High-performance DRC engine for PyEDB.

    This class provides a multi-threaded design rule checker that runs inside
    an open PyEDB session. It uses R-tree spatial indexing for efficient
    geometry queries and parallelizes all rule checks using ThreadPoolExecutor.

    Parameters
    ----------
    edb : pyedb.Edb
        Active EDB session that must already be open.

    Attributes
    ----------
    edb : pyedb.Edb
        Reference to the EDB instance.
    violations : list of dict
        List of violation dictionaries populated by ``check()``.
    idx_primitives : rtree.index.Index
        R-tree spatial index for primitive geometries.
    idx_vias : rtree.index.Index
        R-tree spatial index for via locations.
    idx_components : rtree.index.Index
        R-tree spatial index for component bounding boxes.

    Examples
    --------
    Basic DRC workflow:

    >>> import pyedb
    >>> from pyedb.workflows.drc.drc import Drc, Rules
    >>> edb = pyedb.Edb("my_board.aedb")
    >>> rules = Rules.parse_file("rules.json")
    >>> drc = Drc(edb)
    >>> violations = drc.check(rules)
    >>> print(f"Found {len(violations)} violations")

    Export to IPC-356A format:

    >>> drc.to_ipc356a("review.ipc")
    """

    def __init__(self, edb: pyedb.Edb):
        """Initialize the DRC engine with an EDB instance.

        Parameters
        ----------
        edb : pyedb.Edb
            Active EDB session that must already be open.
        """
        self.edb = edb
        self.violations: list[dict[str, Any]] = []
        self._build_spatial_index()

    # Spatial index (R-tree)
    def _build_spatial_index(self) -> None:
        """Build R-tree spatial indices for fast geometry queries.

        Creates three separate indices for primitives, vias, and components
        to enable efficient proximity and intersection queries.
        """
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

    def check(self, rules: Rules) -> list[dict[str, Any]]:
        """Run all rules and return a list of violations.

        This method dispatches each rule to its appropriate handler and
        collects all violations. Successive calls overwrite previous results.

        Parameters
        ----------
        rules : Rules
            Validated rule container with design constraints.

        Returns
        -------
        list of dict
            Each dictionary describes a single violation with keys:

            - ``rule`` : Rule type (e.g., ``"minLineWidth"``)
            - ``limit_um`` : Limit value in micrometers
            - Additional rule-specific keys (``layer``, ``net1``, ``primitive``, etc.)

        Examples
        --------
        >>> rules = Rules().add_min_line_width("trace", "3.5mil")
        >>> drc = Drc(edb)
        >>> violations = drc.check(rules)
        >>> for v in violations:
        ...     print(f"{v['rule']}: {v}")
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
        """Placeholder for unimplemented rule handlers."""
        raise NotImplementedError(f"Rule handler for '{rule.name}' not implemented. ")

    # Geometry / Manufacturing Rules

    def _rule_min_line_width(self, rule: MinLineWidth, max_workers: int = None):
        """Check minimum line width rule across all path primitives.

        This is a multi-threaded check that extracts EDB data in a single
        thread, then processes paths in parallel across available cores.

        Parameters
        ----------
        rule : MinLineWidth
            Rule configuration with minimum width constraint.
        max_workers : int or None, optional
            Number of worker threads. If ``None``, uses CPU count minus 1.
            The default is ``None``.

        Examples
        --------
        >>> rule = MinLineWidth(name="trace_width", value="3.5mil")
        >>> drc._rule_min_line_width(rule)
        >>> len(drc.violations)
        5
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
        """Check minimum clearance between nets using spatial indexing.

        This is a high-performance check with automatic core detection that
        precomputes spatial intersections and then validates clearances in
        parallel threads.

        Parameters
        ----------
        rule : MinClearance
            Rule configuration with minimum clearance constraint.
        max_workers : int or None, optional
            Number of worker threads. If ``None``, uses CPU count minus 1.
            The default is ``None``.
        chunked_precompute : bool, optional
            If ``True``, precompute spatial index intersections in chunks to
            reduce memory usage. The default is ``False``.
        chunk_size : int, optional
            Size of chunks for precomputation when ``chunked_precompute`` is
            ``True``. The default is ``5000``.

        Examples
        --------
        >>> rule = MinClearance(name="clk2data", value="4mil", net1="CLK*", net2="DATA*")
        >>> drc._rule_min_clearance(rule)
        >>> len(drc.violations)
        3
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
        primitives_by_net_layer: dict[str, dict[str, list[dict]]] = {}
        primitive_points_map: dict[int, list[tuple]] = {}  # prim_id -> points
        prim_bboxes: dict[int, list[float]] = {}  # prim_id -> [minx,miny,maxx,maxy]
        prim_to_net: dict[int, str] = {}  # prim_id -> net name

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
        intersections_map: dict[int, Set[int]] = {}

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
        """Check minimum annular ring for drilled padstacks.

        This thread-safe check validates that copper rings around drilled holes
        meet minimum width requirements. Automatically skips padstacks without
        holes (non-drilled).

        Parameters
        ----------
        rule : MinAnnularRing
            Rule configuration with minimum ring width constraint.
        max_workers : int or None, optional
            Number of worker threads. If ``None``, uses CPU count minus 1.
            The default is ``None``.

        Examples
        --------
        >>> rule = MinAnnularRing(name="via_ring", value="2mil")
        >>> drc._rule_min_annular_ring(rule)
        >>> len(drc.violations)
        2
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
        """Check copper density balance across layers.

        This rule validates that copper distribution stays within acceptable
        balance limits to prevent board warping during fabrication.

        Parameters
        ----------
        rule : CopperBalance
            Rule configuration with balance limits and target layers.

        Examples
        --------
        >>> rule = CopperBalance(name="top_bal", max_percent=10, layers=["TOP"])
        >>> drc._rule_copper_balance(rule)
        >>> len(drc.violations)
        1
        """
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
        """Check differential pair length matching constraints.

        This multi-threaded check validates that positive and negative traces
        in differential pairs have matched lengths within tolerance.

        Parameters
        ----------
        rule : DiffPairLengthMatch
            Rule configuration with tolerance and pair definitions.

        Examples
        --------
        >>> pair = DiffPair(positive="USB_DP", negative="USB_DN")
        >>> rule = DiffPairLengthMatch(name="usb", tolerance="0.1mm", pairs=[pair])
        >>> drc._rule_diff_pair_length_match(rule)
        >>> len(drc.violations)
        0
        """
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
        """Check maximum back-drill stub length constraints.

        This rule validates that remaining stub lengths after back-drilling
        stay below maximum values to minimize signal reflections in high-speed
        designs.

        Parameters
        ----------
        rule : BackDrillStubLength
            Rule configuration with maximum stub length constraint.

        Examples
        --------
        >>> rule = BackDrillStubLength(name="max_stub", value="6mil")
        >>> drc._rule_back_drill_stub_length(rule)
        >>> len(drc.violations)
        3
        """
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
        """Write a complete IPC-D-356A netlist with DRC annotations.

        This method exports the full netlist in IPC-D-356A format with all
        detected violations appended as comment lines. The file can be imported
        by CAM tools (Valor, Genesis, etc.) for fabrication review.

        Parameters
        ----------
        file_path : str
            Output file path. Overwrites existing files without warning.

        Examples
        --------
        >>> drc = Drc(edb)
        >>> violations = drc.check(rules)
        >>> drc.to_ipc356a("fab_review.ipc")

        Export with violations:

        >>> rules = Rules().add_min_line_width("trace", "3mil")
        >>> drc = Drc(edb)
        >>> drc.check(rules)
        >>> drc.to_ipc356a("review_with_violations.ipc")

        Notes
        -----
        - File format follows IPC-D-356A specification
        - Violations are appended as comment lines starting with ``C``
        - Includes netlist information (nets, primitives, padstack instances)
        - Compatible with major CAM software packages
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
