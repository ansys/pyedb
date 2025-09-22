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

    @staticmethod
    def _longest_common_prefix(strings: Sequence[str]) -> str:
        """
        Return the longest common prefix among *strings*.

        Comparison is case-insensitive and stops at the first character that is
        **not** alphanumeric or underscore.  This matches typical SI/PI naming
        conventions (e.g. ``CLK_``, ``DATA_``, ``PWR_``).
        """
        if not strings:
            return ""

        # Normalised copy for comparison
        normed = [re.sub(r"[^A-Za-z0-9_]", "", s).upper() for s in strings]
        s_min, s_max = min(normed), max(normed)

        idx = 0
        while idx < len(s_min) and s_min[idx] == s_max[idx]:
            idx += 1

        # Map back to original case
        return strings[0][:idx]

    def _infer_prefix_patterns(self, nets: Sequence[str]) -> List[str]:
        """
        Heuristically derive prefix patterns from *nets*.

        The algorithm performs a single left-to-right pass:

        1. Sort the net list.
        2. Start a new group with the first net.
        3. For every subsequent net, try to merge it into the **last** group if the
           common prefix is non-empty **and** the group would still contain at
           least 5 % of the total nets.
        4. Convert each final group into the regex pattern ``<prefix>.*``.

        The 5 % threshold prevents hundreds of tiny groups while still splitting
        clearly different prefixes.

        Parameters
        ----------
        nets : Sequence[str]
            Raw net names.

        Returns
        -------
        List[str]
            List of regex patterns suitable for `re.match`.
        """
        if not nets:
            return []

        total = len(nets)
        min_group_size = max(1, int(0.05 * total))

        groups: List[Tuple[str, List[str]]] = []  # (prefix, members)

        for net in sorted(nets):
            # Attempt to merge into the last group
            if groups:
                last_prefix, last_members = groups[-1]
                trial_prefix = self._longest_common_prefix(last_members + [net])
                if trial_prefix and len(last_members) + 1 >= min_group_size:
                    groups[-1] = (trial_prefix, last_members + [net])
                    continue

            # Start new group
            groups.append((net, [net]))

        # Build regex patterns – escape literal part, then wildcard
        return [re.escape(pfx) + r".*" for pfx, _ in groups]

    def group_nets_by_prefix(
        self,
        nets: Sequence[str],
        *,
        prefix_patterns: Optional[Sequence[str]] = None,
    ) -> Dict[str, List[List[str]]]:
        """
        Group nets by name prefix.

        Groups can be further split into fixed-size batches.  When no patterns are
        supplied, they are inferred automatically from the data set.

        Parameters
        ----------
        nets : Sequence[str]
            Complete list of net names.
        prefix_patterns : Sequence[str], optional
            Regex patterns (POSIX ERE) that define the prefixes to be grouped.
            Example: ``["CLK.*", "DATA.*", "PWR.*", "GND.*"]``.
            If *None*, patterns are derived heuristically (see
            :func:`_infer_prefix_patterns`).
        batch_size : int, optional
            Maximum number of nets in each returned sub-list.  If *None*, every
            prefix yields exactly **one** group containing all matching nets.

        Returns
        -------
        Dict[str, List[List[str]]]
            Keys are the original pattern strings (or the auto-generated ones).
            Values are lists of groups; each group is alphabetically sorted.
            Nets that do **not** match any pattern are placed under the key
            ``"UNMATCHED"``.

        Examples
        --------
        >>> nets = ["CLK_100M", "CLK_200M", "DATA0", "DATA1", "PWR_1V0"]
        >>> group_nets_by_prefix(nets, prefix_patterns=["CLK.*", "DATA.*"])
        {'CLK.*': [['CLK_100M', 'CLK_200M']], 'DATA.*': [['DATA0', 'DATA1']], 'UNMATCHED': [['PWR_1V0']]}

        Auto-grouping with batching:

        >>> group_nets_by_prefix(nets, batch_size=2)
        {'CLK.*': [['CLK_100M', 'CLK_200M']], 'DATA.*': [['DATA0', 'DATA1']], 'PWR.*': [['PWR_1V0']]}
        """
        if not nets:
            return {}

        # ------------------------------------------------------------------ #
        # 1. Determine patterns
        # ------------------------------------------------------------------ #
        if prefix_patterns is None:
            patterns = self._infer_prefix_patterns(nets)
        else:
            patterns = list(prefix_patterns)

        # ------------------------------------------------------------------ #
        # 2. Compile regexes
        # ------------------------------------------------------------------ #
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]

        # ------------------------------------------------------------------ #
        # 3. Bucket nets
        # ------------------------------------------------------------------ #
        buckets: Dict[str, List[str]] = defaultdict(list)
        for net in nets:
            for pat, orig in zip(compiled, patterns):
                if pat.match(net):
                    buckets[orig].append(net)
                    break
            else:
                buckets["UNMATCHED"].append(net)

        # ------------------------------------------------------------------ #
        # 4. Build final structure
        # ------------------------------------------------------------------ #
        grouped: Dict[str, List[List[str]]] = {}
        for pat in list(patterns) + ["UNMATCHED"]:
            lst = sorted(buckets.get(pat, []))
            if not lst:
                continue
            if self.batch_size is None:
                grouped[pat] = [lst]
            else:
                grouped[pat] = [lst[i : i + self.batch_size] for i in range(0, len(lst), self.batch_size)]

        for group_patterns in grouped.keys():
            for nets in grouped[group_patterns]:
                self.batch_groups.append(BatchGroup(name=group_patterns, nets=nets))
