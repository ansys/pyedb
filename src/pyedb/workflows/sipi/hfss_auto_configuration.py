from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Sequence, Tuple, Union


@dataclass
class SolderBallsInfo:
    ref_des: str = field(default="")
    shape: str = field(default="cylinder")
    diameter: Union[str, float] = None  # auto evaluated if None
    mid_diameter: Optional[Union[str, float]] = None  # Only for spheroid shape
    height: Union[str, float] = None  # auto evaluated if None


@dataclass
class SimulationSetup:
    meshing_frequency: Union[str, float] = field(default="10GHz")
    frequency_min: Union[str, float] = field(default=0)
    frequency_max: Union[str, float] = field(default="40GHz")
    frequency_step: Union[str, float] = field(default="0.05GHz")
    mesh_operation_size: Union[str, float] = None  # auto evaluated if None


@dataclass
class BatchGroup:
    name: str = field(default="")
    nets: List[str] = field(default_factory=list)
    simulation_setup: SimulationSetup = None  # if None, use default in auto config


@dataclass
class HfssAutoConfig:
    edb_path: str = field(default="")
    cfg_path: str = field(default="")
    edb_version: str = field(default="2025.2")
    signal_nets: list = field(default_factory=list)
    power_ground_nets: list = field(default_factory=list)
    batch_size: int = field(default=2)
    batch_groups: list[BatchGroup] = field(default_factory=list)
    auto_evaluate_batch_groups: bool = field(default=True)
    components: list[str] = field(default_factory=list)
    solder_balls: list[SolderBallsInfo] = field(default_factory=list)
    simulation_setup: SimulationSetup = field(default_factory=SimulationSetup)
    extent_type: str = field(default="bounding_box")

    # ------------------------------------------------------------------
    #  NEW / CHANGED METHODS
    # ------------------------------------------------------------------
    _DIFF_SUFFIX = re.compile(r"_[PN]$|_[ML]$|_[+-]$", re.I)

    def update(self, net_prefix=None):
        if self.auto_evaluate_batch_groups and self.signal_nets:
            self.group_nets_by_prefix(net_prefix)

    @staticmethod
    def _longest_common_prefix(strings: Sequence[str]) -> str:
        if not strings:
            return ""
        normed = [re.sub(r"[^A-Za-z0-9_]", "", s).upper() for s in strings]
        s_min, s_max = min(normed), max(normed)
        idx = 0
        while idx < len(s_min) and s_min[idx] == s_max[idx]:
            idx += 1
        return strings[0][:idx]

    def _infer_prefix_patterns(self, nets: Sequence[str]) -> List[str]:
        if not nets:
            return []
        total = len(nets)
        min_group_size = max(1, int(0.05 * total))
        groups: List[Tuple[str, List[str]]] = []
        for net in sorted(nets):
            if groups:
                last_prefix, last_members = groups[-1]
                trial_prefix = self._longest_common_prefix(last_members + [net])
                if trial_prefix and len(last_members) + 1 >= min_group_size:
                    groups[-1] = (trial_prefix, last_members + [net])
                    continue
            groups.append((net, [net]))
        return [re.escape(pfx) + r".*" for pfx, _ in groups]

    def _base_name(self, net: str) -> str:
        return self._DIFF_SUFFIX.sub("", net)

    def _build_diff_pairs(self, nets: Sequence[str]) -> List[Tuple[str, List[str]]]:
        buckets: Dict[str, List[str]] = defaultdict(list)
        for n in nets:
            buckets[self._base_name(n)].append(n)
        clusters = []
        for base, members in buckets.items():
            if len(members) >= 2 or not self._DIFF_SUFFIX.search(members[0]):
                clusters.append((base, sorted(members)))
        return clusters

    def group_nets_by_prefix(
        self,
        prefix_patterns: Optional[Sequence[str]] = None,
    ) -> Dict[str, List[List[str]]]:
        r"""
        Group signal nets into *disjoint* batches while preserving differential pairs.

        Behaviour in a nutshell
        -----------------------
        1. Nets that form differential pairs (``PCIe_RX0_P`` / ``PCIe_RX0_N``, ``USB3_TX_M`` / ``USB3_TX_P`` …)
           are **never split**; they always appear in the **same** batch.
        2. Every net is assigned to **exactly one** batch.
        3. No batch contains only a single net; orphans are merged into the largest compatible group.
        4. When *prefix_patterns* is supplied **only** nets that match one of those patterns are
           returned; everything else is silently ignored.
        5. If *prefix_patterns* is supplied the caller gets **one group per pattern** regardless of
           :attr:`batch_size`; when it is ``None`` the legacy auto-discovery mode is used and
           :attr:`batch_size` is honoured.

        Parameters
        ----------
        prefix_patterns : Sequence[str], optional
            POSIX ERE patterns that define the prefixes to be grouped.
            Example: ``["PCIe", "USB"]``  ➜  interpreted as ``["PCIe.*", "USB.*"]``.
            If ``None`` patterns are derived heuristically from the data set
            (see :meth:`_infer_prefix_patterns`).

        Returns
        -------
        Dict[str, List[List[str]]]
            Keys are the original / generated pattern strings.
            Values are lists of batches; each batch is an alphabetically sorted
            list of net names.  When *prefix_patterns* was supplied the list
            contains **exactly one** element (the complete group); in auto-discovery
            mode the list may contain multiple slices sized according to
            :attr:`batch_size`.

        Examples
        --------
        Explicit grouping (production intent)::

            >>> cfg.signal_nets = ["PCIe_RX0_P", "PCIe_RX0_N", "PCIe_TX0_P",
            ...                    "USB3_DP", "USB3_DN", "DDR4_A0", "DDR4_A1"]
            >>> cfg.batch_size = 1_000          # ignored when patterns are supplied
            >>> cfg.group_nets_by_prefix(["PCIe", "USB"])
            {'PCIe.*': [['PCIe_RX0_N', 'PCIe_RX0_P', 'PCIe_TX0_P']],
             'USB.*':  [['USB3_DN', 'USB3_DP']]}

        Auto-discovery with batching::

            >>> cfg.group_nets_by_prefix()      # batch_size = 2
            {'PCIe.*': [['PCIe_RX0_N', 'PCIe_RX0_P'], ['PCIe_TX0_P']],
             'USB.*':  [['USB3_DN', 'USB3_DP']],
             'DDR4.*': [['DDR4_A0', 'DDR4_A1']]}

        Notes
        -----
        * Differential recognition strips the suffixes ``_[PN]``, ``_[ML]``, ``_[+-]``
          (case-insensitive).
        * The function updates the instance attribute :attr:`batch_groups` in place.
        """
        if not self.signal_nets:
            return {}

        clusters = self._build_diff_pairs(self.signal_nets)

        # ---------- 1.  patterns  ------------------------------------------
        if prefix_patterns is None:
            patterns = self._infer_prefix_patterns([base for base, _ in clusters])
        else:
            patterns = [p if p.endswith(".*") else p + ".*" for p in prefix_patterns]

        compiled = [re.compile(p, re.I) for p in patterns]

        # ---------- 2.  bucket clusters ------------------------------------
        buckets: Dict[str, List[Tuple[str, List[str]]]] = defaultdict(list)
        for base, members in clusters:
            for pat, orig in zip(compiled, patterns):
                if pat.match(base):
                    buckets[orig].append((base, members))
                    break

        # ---------- 3.  flatten --------------------------------------------
        flat: Dict[str, List[str]] = {}
        for pat in patterns:
            if pat not in buckets:
                continue
            flat[pat] = []
            for _, members in buckets[pat]:
                flat[pat].extend(members)
            flat[pat].sort()

        # ---------- 4.  merge singles --------------------------------------
        singles = [k for k, lst in flat.items() if len(lst) == 1]
        if singles:
            biggest = max(flat.keys(), key=lambda k: len(flat[k]))
            for k in singles:
                flat[biggest].extend(flat[k])
                del flat[k]
            flat[biggest].sort()

        # ---------- 5.  ONE group per supplied prefix -----------------------
        grouped: Dict[str, List[List[str]]] = {}
        for pat, lst in flat.items():
            if prefix_patterns is None:
                # old auto-mode – respect batch_size
                if self.batch_size is None:
                    grouped[pat] = [lst]
                else:
                    grouped[pat] = [lst[i : i + self.batch_size] for i in range(0, len(lst), self.batch_size)]
            else:
                # user-mode – exactly one group per requested prefix
                grouped[pat] = [lst]

        # ---------- 6.  update instance -------------------------------------
        self.batch_groups.clear()
        for pat, batches in grouped.items():
            for nets in batches:
                self.batch_groups.append(BatchGroup(name=pat, nets=nets))
        return grouped


# ------------------------------------------------------------------
#  Quick self-test
# ------------------------------------------------------------------
if __name__ == "__main__":
    cfg = HfssAutoConfig(
        signal_nets=[
            "PCIe_RX0_P",
            "PCIe_RX0_N",
            "PCIe_RX1_P",
            "PCIe_RX1_N",
            "PCIe_TX0_P",
            "PCIe_TX0_N",
            "DDR4_A0",
            "DDR4_A1",
            "DDR4_A2",
            "CLK_100M",
            "CLK_200M",
            "RANDOM",
        ],
        batch_size=3,
    )
    cfg.update()
    for bg in cfg.batch_groups:
        print(bg.name, bg.nets)
