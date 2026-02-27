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

"""HFSS automatic configuration workflow for SI/PI analysis.

This module provides tools to automatically configure HFSS simulations from EDB designs,
including net grouping, batch processing, cutout generation, port creation, and
simulation setup.

Examples
--------
Basic workflow for automatic HFSS configuration:

>>> from pyedb import Edb
>>> from pyedb.workflows.sipi.hfss_auto_configuration import HFSSAutoConfiguration
>>> edb = Edb("design.aedb")
>>> config = HFSSAutoConfiguration(edb)
>>> config.source_edb_path = "design.aedb"
>>> config.target_edb_path = "design_hfss.aedb"
>>> config.auto_populate_batch_groups()
>>> config.create_projects()

Create configuration with specific net groups:

>>> config = HFSSAutoConfiguration()
>>> config.source_edb_path = "my_design.aedb"
>>> config.group_nets_by_prefix(["DDR", "PCIe", "USB"])
>>> config.add_solder_ball("U1", diameter="0.3mm", height="0.2mm")
>>> config.create_projects()
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shutil
import stat

from pyedb import Edb

# patterns used for Regex matching of ground/reference nets
ref_patterns = [
    r"^GND\d*$",
    r"^GND_\w+",
    r"^GND$",
    r"^VSS\d*$",
    r"^VSS\w*",
    r"^DGND$",
    r"^AGND$",
    r"^PGND$",
    r"^EGND$",
    r"^SGND$",
    r"^REF$",
    r"^VREF[A-Z0-9]*",
    r"^VREF$",
    r"^VREF_\d+\.\d+V$",
    r".*_REF$",
    r".*REF$",
    r"^VR[A-Z0-9]*",
    r"^VTT$",
    r"^VTT\d*V$",
    r"^VDDQ_REF$",
    r"^VPP$",
    r"^VCCO_\w+",
    r"^VCCA_\w+",
    r"^VCCD_\w+",
    r"^VSYS$",
    r"^VBUS$",
    r"^0V$",
    r"^0V_\w+",
    r"^GND plane$",
    r"^GROUND$",
    r"^SENSE\d*$",
    r"^KSENSE\w*",
    r"^CAL\d*$",
    r"^CAL_\w+",
    r"^VCM\d*$",
    r"^VCM\w+",
    r"^BGREF$",
    r"^BGVREF$",
    r"^VREFP$",
    r"^VREFN$",
    r"^AVSS$",
    r"^AVDD$",
    r"^DVSS$",
    r"^DVDD$",
]

combined_ref = re.compile("|".join("(?:%s)" % p for p in ref_patterns), re.I)


@dataclass
class SolderBallsInfo:
    """Solder ball configuration for component modeling.

    This dataclass stores geometric parameters for solder ball definitions
    used in HFSS port creation and component modeling.

    Attributes
    ----------
    ref_des : str
        Reference designator of the component. The default is ``""``.
    shape : str
        Geometric shape of the solder ball: ``"cylinder"``, ``"sphere"``,
        or ``"spheroid"``. The default is ``"cylinder"``.
    diameter : str or float or None
        Nominal diameter of the solder ball. The default is ``None``.
    mid_diameter : str or float or None
        Middle diameter for spheroid shapes only. The default is ``None``.
    height : str or float or None
        Height of the solder ball. The default is ``None``.

    Examples
    --------
    >>> ball = SolderBallsInfo(ref_des="U1", shape="cylinder", diameter="0.3mm", height="0.2mm")
    >>> ball.ref_des
    'U1'
    >>> ball.diameter
    '0.3mm'
    """

    ref_des: str = field(default="")
    shape: str = field(default="cylinder")
    diameter: str | float | None = None
    mid_diameter: str | float | None = None
    height: str | float | None = None


@dataclass
class SimulationSetup:
    """HFSS simulation setup parameters.

    This dataclass defines the simulation configuration including meshing
    frequency, convergence criteria, and frequency sweep settings.

    Attributes
    ----------
    meshing_frequency : str or float
        Driven frequency used during mesh generation. The default is ``"10GHz"``.
    maximum_pass_number : int
        Maximum number of adaptive passes. The default is ``15``.
    start_frequency : str or float
        Lower bound of the frequency sweep. The default is ``0``.
    stop_frequency : str or float
        Upper bound of the frequency sweep. The default is ``"40GHz"``.
    frequency_step : str or float
        Linear step size for the frequency sweep. The default is ``"0.05GHz"``.

    Examples
    --------
    >>> setup = SimulationSetup(meshing_frequency="5GHz", maximum_pass_number=20, stop_frequency="60GHz")
    >>> setup.maximum_pass_number
    20
    >>> setup.stop_frequency
    '60GHz'
    """

    meshing_frequency: str | float = field(default="10GHz")
    maximum_pass_number: int = field(default=15)
    start_frequency: str | float = field(default=0)
    stop_frequency: str | float = field(default="40GHz")
    frequency_step: str | float = field(default="0.05GHz")


@dataclass
class BatchGroup:
    """Group of nets to be processed together in a batch simulation.

    This dataclass represents a collection of signal nets that will be
    simulated together with optional custom simulation settings.

    Attributes
    ----------
    name : str
        Descriptive name for the batch group. The default is ``""``.
    nets : list of str
        List of net names to include in this batch. The default is an empty list.
    simulation_setup : SimulationSetup or None
        Custom simulation settings for this batch. If ``None``, the global
        configuration settings are used. The default is ``None``.

    Examples
    --------
    >>> group = BatchGroup(
    ...     name="DDR4_Signals",
    ...     nets=["DDR4_DQ0", "DDR4_DQ1", "DDR4_CLK"],
    ...     simulation_setup=SimulationSetup(stop_frequency="20GHz"),
    ... )
    >>> group.name
    'DDR4_Signals'
    >>> len(group.nets)
    3
    """

    name: str = field(default="")
    nets: list[str] = field(default_factory=list)
    simulation_setup: SimulationSetup | None = None


class HFSSAutoConfiguration:
    """Automatic HFSS simulation configuration from EDB designs.

    This class automates the process of configuring HFSS simulations including
    net grouping, cutout creation, port generation, and simulation setup.

    Parameters
    ----------
    edb : Edb or None, optional
        Existing EDB object instance. If ``None``, a new instance will be created
        from the source path. The default is ``None``.

    Attributes
    ----------
    ansys_version : str
        ANSYS Electronics Desktop version to use. The default is ``"2025.2"``.
    grpc : bool
        Whether to use gRPC API mode. The default is ``True``.
    source_edb_path : str
        Path to the source EDB file.
    target_edb_path : str
        Path where the configured EDB will be saved.
    batch_group_folder : str
        Folder path for storing batch group projects.
    signal_nets : list
        List of signal net names to include in the simulation.
    power_nets : list
        List of power net names.
    reference_net : str
        Name of the reference (ground) net.
    batch_size : int
        Maximum number of nets per batch group. The default is ``100``.
    batch_groups : list of BatchGroup
        Configured batch groups for simulation.
    components : list of str
        Component reference designators to include.
    solder_balls : list of SolderBallsInfo
        Solder ball configurations for components.
    simulation_setup : SimulationSetup
        Global simulation settings.
    extent_type : str
        Cutout extent algorithm: ``"bounding_box"``, ``"convex_hull"``,
        or ``"conformal"``. The default is ``"bounding_box"``.
    cutout_expansion : str or float
        Cutout expansion margin. The default is ``"2mm"``.
    auto_mesh_seeding : bool
        Enable automatic mesh seeding. The default is ``True``.
    port_type : str
        Port type to create: ``"coaxial"`` or ``"circuit_port"``.
        The default is ``"coaxial"``.
    create_pin_group : bool
        Whether to create pin groups for circuit ports. The default is ``False``.

    Examples
    --------
    Basic configuration:

    >>> from pyedb import Edb
    >>> config = HFSSAutoConfiguration()
    >>> config.source_edb_path = "design.aedb"
    >>> config.target_edb_path = "design_hfss.aedb"
    >>> config.auto_populate_batch_groups()
    >>> config.create_projects()

    Configure with existing EDB:

    >>> edb = Edb("design.aedb")
    >>> config = HFSSAutoConfiguration(edb)
    >>> config.signal_nets = ["DDR4_DQ0", "DDR4_CLK"]
    >>> config.reference_net = "GND"
    >>> config.add_solder_ball("U1", diameter="0.3mm", height="0.2mm")
    """

    def __init__(self, edb=None):
        """Initialize the HFSS automatic configuration.

        Parameters
        ----------
        edb : Edb or None, optional
            Existing EDB object instance. The default is ``None``.
        """
        self._pedb = edb
        self.ansys_version: str = "2025.2"
        self.grpc: bool = True
        self.source_edb_path: str = ""
        self.target_edb_path: str = ""
        self.batch_group_folder: str = ""
        self.signal_nets: list = []
        self.power_nets: list = []
        self.reference_net: str = ""
        self.batch_size: int = 100
        self.batch_groups: list[BatchGroup] = []
        self.components: list[str] = []
        self.solder_balls: list[SolderBallsInfo] = []
        self.simulation_setup: SimulationSetup = SimulationSetup()
        self.extent_type: str = "bounding_box"
        self.cutout_expansion: float | str = "2mm"
        self.auto_mesh_seeding: bool = True
        self.port_type: str = "coaxial"
        self.create_pin_group: bool = False

    _DIFF_SUFFIX = re.compile(r"_[PN]$|_[ML]$|_[+-]$", re.I)

    def auto_populate_batch_groups(
        self,
        pattern: str | list[str] | None = None,
    ) -> None:
        """Automatically create and populate batch groups from signal nets.

        This method discovers signal nets, identifies reference nets, and groups
        nets by prefix patterns. It is a convenience wrapper around
        ``group_nets_by_prefix()``.

        Parameters
        ----------
        pattern : str or list of str or None, optional
            POSIX ERE prefix pattern(s) controlling which nets are grouped:

            - ``None`` (default) - Auto-discovery mode: nets are clustered
              heuristically and split into chunks of size ``batch_size``.
            - str - Single string prefix pattern (automatically anchored:
              ``pattern + ".*"``).
            - list of str - Each element becomes its own prefix pattern;
              one ``BatchGroup`` created per list entry, regardless of
              ``batch_size``.

        Examples
        --------
        Auto-discovery with automatic grouping:

        >>> config = HFSSAutoConfiguration()
        >>> config.source_edb_path = "design.aedb"
        >>> config.auto_populate_batch_groups()
        >>> len(config.batch_groups)
        5

        Group by specific prefixes:

        >>> config = HFSSAutoConfiguration()
        >>> config.source_edb_path = "design.aedb"
        >>> config.auto_populate_batch_groups(["DDR4", "PCIe", "USB"])
        >>> [g.name for g in config.batch_groups]
        ['DDR4', 'PCIe', 'USB']

        Notes
        -----
        - Clears and repopulates ``batch_groups`` in-place
        - Automatically identifies reference nets (typically GND variants)
        - Opens and closes the EDB internally
        """
        if not self._pedb:
            self._pedb = Edb(edbpath=self.source_edb_path, version=self.ansys_version, grpc=self.grpc)
        self.signal_nets = list(self._pedb.nets.signal.keys())
        all_power_nets = list(self._pedb.nets.power.keys())
        reference_nets = [n for n in all_power_nets if combined_ref.match(n)]

        # --- guarantee: any net whose *upper-case* name contains "GND" comes first ---
        def __key(n):
            return (0, n) if "GND" in n.upper() else (1, n)

        _ref_nets = list(sorted(reference_nets, key=__key))
        if len(_ref_nets) > 1:
            self._pedb.logger.warning(
                f"Multiple candidate reference nets found: {_ref_nets}. Using {_ref_nets[0]} as the reference net."
            )
            self.reference_net = _ref_nets[0]
        self.power_nets = [n for n in all_power_nets if n not in _ref_nets]
        self.group_nets_by_prefix(pattern)
        self._pedb.close(terminate_rpc_session=False)

    def add_batch_group(
        self,
        name: str,
        nets: list[str] | None = None,
        *,
        simulation_setup: SimulationSetup | None = None,
    ) -> BatchGroup:
        """Append a new BatchGroup to the configuration.

        Parameters
        ----------
        name : str
            Descriptive name for the group. Will also become the regex pattern
            when the group is built automatically.
        nets : list of str or None, optional
            List of net names that belong to this batch. If ``None``, an empty
            list is assumed and can be filled later. The default is ``None``.
        simulation_setup : SimulationSetup or None, optional
            Per-batch simulation settings. When ``None``, the global
            ``self.simulation_setup`` is used. The default is ``None``.

        Returns
        -------
        BatchGroup
            The freshly created instance (already appended to ``batch_groups``)
            for further manipulation if desired.

        Examples
        --------
        >>> config = HFSSAutoConfiguration()
        >>> group = config.add_batch_group("DDR4", nets=["DDR4_DQ0", "DDR4_CLK"])
        >>> group.name
        'DDR4'
        >>> len(group.nets)
        2

        Add group with custom setup:

        >>> setup = SimulationSetup(stop_frequency="30GHz")
        >>> group = config.add_batch_group("PCIe", simulation_setup=setup)
        >>> group.simulation_setup.stop_frequency
        '30GHz'
        """
        bg = BatchGroup(
            name=name,
            nets=list(nets or []),
            simulation_setup=simulation_setup,
        )
        self.batch_groups.append(bg)
        return bg

    def add_solder_ball(
        self,
        ref_des: str,
        shape: str = "cylinder",
        diameter: str | float | None = None,
        mid_diameter: str | float | None = None,
        height: str | float | None = None,
    ) -> SolderBallsInfo:
        """Append a new solder ball definition to the configuration.

        Parameters
        ----------
        ref_des : str
            Reference designator of the component to which the solder ball
            definition applies (e.g., ``"U1"``).
        shape : str, optional
            Geometric model used for the solder ball. Supported values are
            ``"cylinder"``, ``"sphere"``, ``"spheroid"``. The default is
            ``"cylinder"``.
        diameter : str or float or None, optional
            Nominal diameter. When ``None``, HFSS auto-evaluates the value
            from the footprint. The default is ``None``.
        mid_diameter : str or float or None, optional
            Middle diameter required only for spheroid shapes. Ignored for
            all other geometries. The default is ``None``.
        height : str or float or None, optional
            Ball height. When ``None``, HFSS computes an appropriate value
            automatically. The default is ``None``.

        Returns
        -------
        SolderBallsInfo
            The newly created instance (already appended to ``solder_balls``).
            The object can be further edited in-place if desired.

        Examples
        --------
        Add cylinder solder balls:

        >>> config = HFSSAutoConfiguration()
        >>> config.add_solder_ball("U1", diameter="0.3mm", height="0.2mm")
        >>> config.solder_balls[0].ref_des
        'U1'

        Add spheroid solder balls:

        >>> config.add_solder_ball("U2", shape="spheroid", diameter="0.25mm", mid_diameter="0.35mm", height="0.18mm")
        >>> config.solder_balls[1].shape
        'spheroid'
        """
        sb = SolderBallsInfo(
            ref_des=ref_des,
            shape=shape,
            diameter=diameter,
            mid_diameter=mid_diameter,
            height=height,
        )
        self.solder_balls.append(sb)
        return sb

    def add_simulation_setup(
        self,
        meshing_frequency: str | float | None = "10GHz",
        maximum_pass_number: int = 15,
        start_frequency: str | float | None = 0,
        stop_frequency: str | float | None = "40GHz",
        frequency_step: str | float | None = "0.05GHz",
        replace: bool = True,
    ) -> SimulationSetup:
        """Create a SimulationSetup instance and attach it to the configuration.

        Parameters
        ----------
        meshing_frequency : str or float or None, optional
            Driven frequency used during mesh generation. The default is ``"10GHz"``.
        maximum_pass_number : int, optional
            Maximum number of adaptive passes. The default is ``15``.
        start_frequency : str or float or None, optional
            Lower bound of the sweep window. The default is ``0``.
        stop_frequency : str or float or None, optional
            Upper bound of the sweep window. The default is ``"40GHz"``.
        frequency_step : str or float or None, optional
            Linear step size for the frequency sweep. The default is ``"0.05GHz"``.
        replace : bool, optional
            Placement strategy for the new setup:

            - ``False`` - Append a per-batch setup by creating an auxiliary
              ``BatchGroup`` (``name="extra_setup"``) whose ``simulation_setup``
              points to the new object.
            - ``True`` - Overwrite the global ``simulation_setup`` attribute of
              the current instance. The default is ``True``.

        Returns
        -------
        SimulationSetup
            The newly created instance (already stored inside the configuration).

        Examples
        --------
        Create global setup:

        >>> config = HFSSAutoConfiguration()
        >>> config.add_simulation_setup(stop_frequency="60GHz", replace=True)
        >>> config.simulation_setup.stop_frequency
        '60GHz'

        Create per-batch setup:

        >>> config.add_simulation_setup(frequency_step="0.1GHz", replace=False)
        >>> config.batch_groups[-1].name
        'extra_setup'
        """
        setup = SimulationSetup(
            meshing_frequency=meshing_frequency,
            maximum_pass_number=maximum_pass_number,
            start_frequency=start_frequency,
            stop_frequency=stop_frequency,
            frequency_step=frequency_step,
        )
        if replace:
            self.simulation_setup = setup
        else:
            self.batch_groups.append(BatchGroup(name="extra_setup", simulation_setup=setup))
        return setup

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
        prefix_patterns: list[str] | None = None,
    ) -> dict[str, list[list[str]]]:
        """Group signal nets into disjoint batches while preserving differential pairs.

        This method organizes signal nets into batches based on prefix patterns,
        ensuring differential pairs (e.g., ``_P``/``_N``, ``_M``/``_L``) stay together.

        Parameters
        ----------
        prefix_patterns : list of str or None, optional
            POSIX ERE patterns that define the prefixes to be grouped.
            Example: ``["PCIe", "USB"]`` → interpreted as ``["PCIe.*", "USB.*"]``.
            If ``None``, patterns are derived heuristically from the data set.

        Returns
        -------
        dict[str, list[list[str]]]
            Keys are the original or generated pattern strings.
            Values are lists of batches; each batch is an alphabetically sorted
            list of net names. When ``prefix_patterns`` was supplied, the list
            contains exactly one element (the complete group); in auto-discovery
            mode, the list may contain multiple slices sized according to
            ``batch_size``.

        Examples
        --------
        Explicit grouping:

        >>> config = HFSSAutoConfiguration()
        >>> config.signal_nets = ["PCIe_RX0_P", "PCIe_RX0_N", "USB3_DP", "DDR4_A0"]
        >>> config.group_nets_by_prefix(["PCIe", "USB"])
        {'PCIe': [['PCIe_RX0_N', 'PCIe_RX0_P']], 'USB': [['USB3_DP']]}

        Auto-discovery with batching:

        >>> config.batch_size = 2
        >>> config.group_nets_by_prefix()
        {'PCIe': [['PCIe_RX0_N', 'PCIe_RX0_P']], 'USB': [['USB3_DP']], 'DDR4': [['DDR4_A0']]}

        Notes
        -----
        - Differential recognition strips the suffixes ``_[PN]``, ``_[ML]``, ``_[+-]``
          (case-insensitive).
        - The function updates the instance attribute ``batch_groups`` in place.
        - Every net is assigned to exactly one batch.
        - No batch contains only a single net; orphans are merged into the largest
          compatible group.
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
        grouped = {k[:-2] if k.endswith("*") else k: v for k, v in grouped.items()}
        for batch_group in self.batch_groups:
            batch_group.name = batch_group.name[:-2] if batch_group.name.endswith(".*") else batch_group.name
        return grouped

    def create_projects(self):
        """Generate HFSS projects from configured batch groups.

        This method executes the complete workflow for each batch group including:

        1. Copying source EDB to target location
        2. Creating cutout with specified nets
        3. Creating ports on components
        4. Setting up simulation parameters
        5. Saving configured project

        When multiple batch groups exist, each group is processed into a separate
        project file stored in the ``batch_group_folder`` directory.

        Examples
        --------
        Create single project:

        >>> config = HFSSAutoConfiguration()
        >>> config.source_edb_path = "design.aedb"
        >>> config.target_edb_path = "design_hfss.aedb"
        >>> config.signal_nets = ["DDR4_DQ0", "DDR4_CLK"]
        >>> config.reference_net = "GND"
        >>> config.components = ["U1"]
        >>> config.create_projects()

        Create multiple batch projects:

        >>> config = HFSSAutoConfiguration()
        >>> config.source_edb_path = "design.aedb"
        >>> config.auto_populate_batch_groups(["DDR4", "PCIe"])
        >>> config.create_projects()
        >>> # Creates projects in batch_groups/DDR4.aedb and batch_groups/PCIe.aedb

        Notes
        -----
        - For multiple batch groups, projects are saved in ``batch_group_folder``
        - Each batch can have custom simulation settings
        - Automatically handles EDB session management
        """

        def del_ro(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if not self.batch_groups:
            self._copy_edb_and_open_project()
            if not self._pedb:
                self._create_project(close_rpc=True)
            else:
                self._create_project(close_rpc=False)
        else:
            batch_count = 0
            if os.path.isdir(self.batch_group_folder):
                shutil.rmtree(self.batch_group_folder)
            for batch_group in self.batch_groups:
                batch_count += 1
                if not self.batch_group_folder:
                    self.batch_group_folder = os.path.join(str(Path(self.source_edb_path).parent), "batch_groups")
                    if batch_count == 1 and os.path.isdir(self.batch_group_folder):
                        os.chdir(os.path.expanduser("~"))
                        shutil.rmtree(self.batch_group_folder, onerror=del_ro)
                if batch_group.simulation_setup:
                    self.simulation_setup = batch_group.simulation_setup
                self.signal_nets = batch_group.nets
                self.target_edb_path = os.path.join(self.batch_group_folder, batch_group.name + ".aedb")
                self._copy_edb_and_open_project()
                if batch_count == len(self.batch_groups):
                    self._create_project(close_rpc=True)
                else:
                    self._create_project(close_rpc=False)

    def _copy_edb_and_open_project(self):
        if not self.source_edb_path:
            raise ValueError("source EDB path is empty.")
        shutil.copytree(self.source_edb_path, self.target_edb_path)
        if not os.path.isdir(self.target_edb_path):
            raise FileNotFoundError(f"Failed to copy EDB to {self.target_edb_path}")
        self._pedb = Edb(edbpath=self.target_edb_path, version=self.ansys_version, grpc=self.grpc)

    def __get_components_using_signal_nets(self):
        self.components = list(
            set(
                [
                    refdes
                    for refdes, comp in self._pedb.components.instances.items()
                    if comp.type.lower() not in ["resistor", "capacitor", "inductor"]
                    and not set(comp.nets).isdisjoint(self.signal_nets)
                ]
            )
        )

    def _create_project(self, close_rpc: bool = True):
        if not self.target_edb_path:
            raise ValueError("Project path is empty.")
        if not self.signal_nets:
            raise ValueError("No signal nets defined.")
        if not self.reference_net:
            raise ValueError("No reference net defined.")
        # step 1: cutout
        self._pedb.logger.info(f"Creating project {self.target_edb_path}")
        self._pedb.logger.info(f"step 1: cutout")
        clipped_nets = self.power_nets
        clipped_nets.append(self.reference_net)
        self._pedb.cutout(
            signal_list=self.signal_nets,
            reference_list=clipped_nets,
            extent_type=self.extent_type,
            expansion_size=self.cutout_expansion,
        )
        # step 2: create Ports
        self._pedb.logger.info(f"step 2: creating ports")
        if not self.components:
            self._pedb.logger.info("No components provided, searching component instances")
            self.__get_components_using_signal_nets()
            if not self.components:
                raise ValueError("No components found in the design.")
        if self.port_type in ["coaxial", "coax", "coax_port", "coaxial_port"]:
            if self.solder_balls:
                for solder_ball in self.solder_balls:
                    comp = solder_ball.ref_des
                    if not comp in self.components:
                        self._pedb.logger.warning(f"Component {comp} not found in the design, skipping")
                        continue
                    self._pedb.excitation_manager.create_port_on_component(
                        component=comp,
                        net_list=self.signal_nets,
                        port_type="coax_port",
                        reference_net=self.reference_net,
                        solder_balls_height=solder_ball.height,
                        solder_balls_size=solder_ball.diameter,
                        solder_balls_mid_size=solder_ball.mid_diameter,
                    )
            else:
                for component in self.components:
                    self._pedb.excitation_manager.create_port_on_component(
                        component=component,
                        net_list=self.signal_nets,
                        port_type="coax_port",
                        reference_net=self.reference_net,
                    )
        elif self.port_type in ["circuit_port", "circuit", "circuit_ports"]:
            for component in self.components:
                self._pedb.excitation_manager.create_port_on_component(
                    component=component,
                    net_list=self.signal_nets,
                    port_type="circuit_port",
                    do_pingroup=self.create_pin_group,
                    reference_net=self.reference_net,
                )

        self._pedb.logger.info(f"Ports created: {len(self._pedb.hfss.excitations)}")
        # step 3: create simulation setup
        self._pedb.logger.info(f"step 3: creating simulation setup")
        setup = self._pedb.hfss.add_setup("Setup1")
        setup.adaptive_settings.max_passes = self.simulation_setup.maximum_pass_number
        if not self.grpc:
            setup.adaptive_settings.adaptive_frequency_data_list[
                0
            ].adaptive_frequency = self.simulation_setup.meshing_frequency
        else:
            setup.settings.mesh_frequency = self.simulation_setup.meshing_frequency
        setup.add_sweep(
            "AutoSweep",
            start_freq=self.simulation_setup.start_frequency,
            stop_freq=self.simulation_setup.stop_frequency,
            step=self.simulation_setup.frequency_step,
        )
        if self.auto_mesh_seeding:
            setup.auto_mesh_operation()
        self._pedb.save()
        self._pedb.close(terminate_rpc_session=close_rpc)


def create_hfss_auto_configuration(
    edb: Edb | None = None,
    ansys_version: str | None = None,
    grpc: bool | None = None,
    source_edb_path: str | None = None,
    target_edb_path: str | None = None,
    signal_nets: list | None = None,
    power_nets: list | None = None,
    reference_net: str | None = None,
    batch_size: int | None = None,
    batch_groups: list | None = None,
    components: list[str] | None = None,
    solder_balls: list | None = None,
    simulation_setup: SimulationSetup | None = None,
    extent_type: str | None = None,
    cutout_expansion: str | float | None = None,
    auto_mesh_seeding: bool | None = None,
    port_type: str | None = None,
    create_pin_group: bool | None = None,
) -> HFSSAutoConfiguration:
    """Factory function to create an HFSSAutoConfiguration instance with optional overrides.

    This function creates a configuration object with all specified parameters,
    providing a convenient alternative to manual attribute assignment.

    Parameters
    ----------
    edb : Edb or None, optional
        Existing EDB object instance. The default is ``None``.
    ansys_version : str or None, optional
        ANSYS Electronics Desktop version. The default is ``None``.
    grpc : bool or None, optional
        Whether to use gRPC API mode. The default is ``None``.
    source_edb_path : str or None, optional
        Path to the source EDB file. The default is ``None``.
    target_edb_path : str or None, optional
        Path where configured EDB will be saved. The default is ``None``.
    signal_nets : list or None, optional
        List of signal net names. The default is ``None``.
    power_nets : list or None, optional
        List of power net names. The default is ``None``.
    reference_net : str or None, optional
        Name of reference (ground) net. The default is ``None``.
    batch_size : int or None, optional
        Maximum nets per batch group. The default is ``None``.
    batch_groups : list or None, optional
        Pre-configured batch groups. The default is ``None``.
    components : list of str or None, optional
        Component reference designators. The default is ``None``.
    solder_balls : list or None, optional
        Solder ball configurations. The default is ``None``.
    simulation_setup : SimulationSetup or None, optional
        Global simulation settings. The default is ``None``.
    extent_type : str or None, optional
        Cutout extent algorithm. The default is ``None``.
    cutout_expansion : str or float or None, optional
        Cutout expansion margin. The default is ``None``.
    auto_mesh_seeding : bool or None, optional
        Enable automatic mesh seeding. The default is ``None``.
    port_type : str or None, optional
        Port type to create. The default is ``None``.
    create_pin_group : bool or None, optional
        Whether to create pin groups. The default is ``None``.

    Returns
    -------
    HFSSAutoConfiguration
        Fully configured instance ready for use.

    Examples
    --------
    Create with basic settings:

    >>> config = create_hfss_auto_configuration(
    ...     source_edb_path="design.aedb",
    ...     target_edb_path="design_hfss.aedb",
    ...     signal_nets=["DDR4_DQ0", "DDR4_CLK"],
    ...     reference_net="GND",
    ... )
    >>> config.source_edb_path
    'design.aedb'

    Create with custom simulation setup:

    >>> setup = SimulationSetup(stop_frequency="60GHz")
    >>> config = create_hfss_auto_configuration(
    ...     source_edb_path="design.aedb", simulation_setup=setup, port_type="circuit_port"
    ... )
    >>> config.simulation_setup.stop_frequency
    '60GHz'
    """
    cfg = HFSSAutoConfiguration(edb)

    # Scalar overrides
    for attr, value in (
        ("ansys_version", ansys_version),
        ("grpc", grpc),
        ("source_edb_path", source_edb_path),
        ("target_edb_path", target_edb_path),
        ("batch_size", batch_size),
        ("extent_type", extent_type),
        ("cutout_expansion", cutout_expansion),
        ("auto_mesh_seeding", auto_mesh_seeding),
        ("port_type", port_type),
        ("create_pin_group", create_pin_group),
    ):
        if value is not None:
            setattr(cfg, attr, value)

    # List / container overrides
    if signal_nets is not None:
        cfg.signal_nets = signal_nets
    if power_nets is not None:
        cfg.power_nets = power_nets
    if reference_net is not None:
        cfg.reference_net = reference_net
    if batch_groups is not None:
        cfg.batch_groups = batch_groups
    if components is not None:
        cfg.components = components
    if solder_balls is not None:
        cfg.solder_balls = solder_balls
    if simulation_setup is not None:
        cfg.simulation_setup = simulation_setup

    return cfg
