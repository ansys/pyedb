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

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shutil
import stat
from typing import Dict, List, Optional, Sequence, Tuple, Union

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
    ref_des: str = field(default="")
    shape: str = field(default="cylinder")
    diameter: Optional[Union[str, float]] = None
    mid_diameter: Optional[Union[str, float]] = None
    height: Optional[Union[str, float]] = None


@dataclass
class SimulationSetup:
    meshing_frequency: Union[str, float] = field(default="10GHz")
    maximum_pass_number: int = field(default=15)
    start_frequency: Union[str, float] = field(default=0)
    stop_frequency: Union[str, float] = field(default="40GHz")
    frequency_step: Union[str, float] = field(default="0.05GHz")


@dataclass
class BatchGroup:
    name: str = field(default="")
    nets: List[str] = field(default_factory=list)
    simulation_setup: SimulationSetup = None  # if None, use default in auto config


class HFSSAutoConfiguration:
    def __init__(self, edb=None):
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
        self.cutout_expansion: Union[float, str] = "2mm"
        self.auto_mesh_seeding: bool = True
        self.port_type: str = "coaxial"
        self.create_pin_group: bool = False

    _DIFF_SUFFIX = re.compile(r"_[PN]$|_[ML]$|_[+-]$", re.I)

    def auto_populate_batch_groups(
        self,
        pattern: str | list[str] | None = None,
    ) -> None:
        """
        Automatically create and populate :attr:`batch_groups` from the current
        :attr:`signal_nets`.

        This is a thin convenience wrapper around :meth:`group_nets_by_prefix`.
        It **only** executes when both:

        * :attr:`auto_evaluate_batch_groups` is ``True``, and
        * :attr:`signal_nets` is non-empty.

        Parameters
        ----------
        pattern : :class:`str` | :class:`list` [:class:`str`] | ``None``, optional
            POSIX ERE prefix pattern(s) that control which nets are grouped.

            * ``None`` *(default)* – activate **auto-discovery** mode: nets are
              clustered heuristically and then split into chunks of size
              :attr:`batch_size`.
            * :class:`str` – treat the single string as a prefix pattern
              (automatically anchored: ``pattern + ".*"``).
            * :class:`list` [:class:`str`] – each list element becomes its own
              prefix pattern; one :class:`.BatchGroup` is created **per list
              entry**, regardless of :attr:`batch_size`.

        Side-effects
        ------------
        Clears and repopulates :attr:`batch_groups` in-place.
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
        nets: Sequence[str] | None = None,
        *,
        simulation_setup: SimulationSetup | None = None,
    ) -> BatchGroup:
        """
        Append a new BatchGroup to the configuration.

        Parameters
        ----------
        name : str
            Descriptive name for the group (will also become the regex
            pattern when the group is built automatically).
        nets : Sequence[str], optional
            List of net names that belong to this batch.  If omitted
            an empty list is assumed and you can fill it later.
        simulation_setup : SimulationSetup, optional
            Per-batch simulation settings.  When None the global
            ``self.simulation_setup`` is used.

        Returns
        -------
        BatchGroup
            The freshly created instance (already appended to
            ``self.batch_groups``) so the caller can further
            manipulate it if desired.
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
        diameter: Optional[Union[str, float]] = None,
        mid_diameter: Optional[Union[str, float]] = None,
        height: Optional[Union[str, float]] = None,
    ) -> SolderBallsInfo:
        """
        Append a new :class:`.SolderBallsInfo` entry to the configuration.

        Parameters
        ----------
        ref_des : :class:`str`
            Reference designator of the component to which the solder-ball
            definition applies (e.g. ``"U1"``).
        shape : :class:`str`, default ``"cylinder"``
            Geometric model used for the solder ball. Supported values are
            ``"cylinder"``, ``"sphere"``, ``"spheroid"``, etc.
        diameter : :class:`str` | :class:`float` | ``None``, optional
            Nominal diameter.  When ``None`` HFSS auto-evaluates the value
            from the footprint.
        mid_diameter : :class:`str` | :class:`float` | ``None``, optional
            Middle diameter **required only for spheroid shapes**.  Ignored
            for all other geometries.
        height : :class:`str` | :class:`float` | ``None``, optional
            Ball height.  When ``None`` HFSS computes an appropriate value
            automatically.

        Returns
        -------
        :class:`.SolderBallsInfo`
            The newly created instance (already appended to
            :attr:`solder_balls`).  The object can be further edited in-place
            by the caller if desired.

        Examples
        --------
        >>> cfg = HfssAutoConfig()
        >>> cfg.add_solder_ball("U1", diameter="0.3mm", height="0.2mm")
        >>> cfg.add_solder_ball(
        ...     "U2",
        ...     shape="spheroid",
        ...     diameter="0.25mm",
        ...     mid_diameter="0.35mm",
        ...     height="0.18mm",
        ... )
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
        meshing_frequency: Optional[Union[str, float]] = "10GHz",
        maximum_pass_number: int = 15,
        start_frequency: Optional[Union[str, float]] = 0,
        stop_frequency: Optional[Union[str, float]] = "40GHz",
        frequency_step: Optional[Union[str, float]] = "0.05GHz",
        replace: bool = True,
    ) -> SimulationSetup:
        r"""
        Create a: class:`.SimulationSetup` instance and attach it to the configuration.

        Parameters
        ----------
        meshing_frequency : Union[:class:`str`,: class:`float`], default ``"10GHz"``
            Driven frequency used during mesh generation.
        maximum_pass_number : class:`int`, default ``15``
            Maximum number of adaptive passes.
        start_frequency : Union[:class:`str`,: class:`float`], default ``0``
            Lower bound of the sweep window.
        stop_frequency : Union[:class:`str`,: class:`float`], default ``"40GHz"``
            Upper bound of the sweep window.
        frequency_step : Union[:class:`str`,: class:`float`], default ``"0.05GHz"``
            Linear step size for the frequency sweep.
        mesh_operation_size : Union[:class:`str`,: class:`float`, ``None``], optional
            Maximum element size for mesh operations.  When ``None`` HFSS
            computes an appropriate value automatically.
        replace : class:`bool`, default ``False``
            Placement strategy for the new setup:

            * ``False`` – append a *per-batch* setup by creating an auxiliary
              :class:`.BatchGroup` (``name="extra_setup"``) whose
              :attr:`.BatchGroup.simulation_setup` points to the new object.
            * ``True`` – overwrite the **global**: attr:`simulation_setup`
              attribute of the current :class:`.HfssAutoConfig` instance.

        Returns
        -------
        :class:`.SimulationSetup`
            The newly created instance (already stored inside the configuration).

        Examples
        --------
        >>> cfg = HfssAutoConfig()
        >>> # global setup
        >>> cfg.add_simulation_setup(frequency_max="60GHz", replace=True)
        >>> # per-batch setup
        >>> cfg.add_simulation_setup(frequency_step="0.1GHz")
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
        grouped = {k[:-2] if k.endswith("*") else k: v for k, v in grouped.items()}
        for batch_group in self.batch_groups:
            batch_group.name = batch_group.name[:-2] if batch_group.name.endswith(".*") else batch_group.name
        return grouped

    def create_projects(self):
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
                    self._pedb.components.create_port_on_component(
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
                    self._pedb.components.create_port_on_component(
                        component=component,
                        net_list=self.signal_nets,
                        port_type="coax_port",
                        reference_net=self.reference_net,
                    )
        elif self.port_type in ["circuit_port", "circuit", "circuit_ports"]:
            for component in self.components:
                self._pedb.components.create_port_on_component(
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
    edb: Optional[Edb] = None,
    ansys_version: Optional[str] = None,
    grpc: Optional[bool] = None,
    source_edb_path: Optional[str] = None,
    target_edb_path: Optional[str] = None,
    signal_nets: Optional[list] = None,
    power_nets: Optional[list] = None,
    reference_net: Optional[str] = None,
    batch_size: Optional[int] = None,
    batch_groups: Optional[list] = None,
    components: Optional[list[str]] = None,
    solder_balls: Optional[list] = None,
    simulation_setup: Optional[SimulationSetup] = None,
    extent_type: Optional[str] = None,
    cutout_expansion: Optional[Union[str, float]] = None,
    auto_mesh_seeding: Optional[bool] = None,
    port_type: Optional[str] = None,
    create_pin_group: Optional[bool] = None,
) -> HFSSAutoConfiguration:
    """
    Factory function that creates an HFSSAutoConfiguration instance
    with optional overrides for every public attribute.

    Parameters
    ----------
    All parameters are optional. When omitted, the class-level defaults
    (defined in HFSSAutoConfiguration.__init__) are kept.

    Returns
    -------
    HFSSAutoConfiguration
        A fully configured instance ready for further use or inspection.
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
