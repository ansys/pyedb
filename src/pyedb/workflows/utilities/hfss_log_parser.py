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

from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Any, Dict, List, Optional


def _to_hz(text: str) -> float:
    """
    Convert a human-readable frequency string to hertz.

    :param text: Frequency expression such as ``'3 GHz'``, ``'100 kHz'``, ``'10MHz'``.
    :type text: str
    :return: Numerical value in Hz. Returns :py:const:`math.nan` if the string
             cannot be parsed.
    :rtype: float
    """
    m = re.match(r"(?P<val>[\d.]+)\s*(?P<unit>[kMG]?Hz)", text, re.I)
    if not m:
        return math.nan
    val, unit = float(m["val"]), m["unit"].lower()
    scale = {"hz": 1, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
    return val * scale[unit]


def _to_sec(mm_ss: str) -> int:
    """
    Convert an ANSYS time stamp to seconds.

    Accepts ``MM:SS``, ``H:MM:SS`` or ``HH:MM:SS``.

    :param mm_ss: Time stamp extracted from the log.
    :type mm_ss: str
    :return: Total elapsed seconds.
    :rtype: int
    """
    parts = mm_ss.strip().split(":")
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    if len(parts) == 3:  # H:MM:SS or HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def _as_dict(obj: Any) -> Any:
    """Recursively convert dataclasses / lists / primitives to plain Python types."""
    if hasattr(obj, "__dataclass_fields__"):
        return {f: _as_dict(getattr(obj, f)) for f in obj.__dataclass_fields__}
    if isinstance(obj, list):
        return [_as_dict(i) for i in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj


@dataclass(slots=True)
class ProjectInfo:
    """
    Basic meta-data extracted from the header of an HFSS batch log.

    :ivar str name: Project name (without extension).
    :ivar ~pathlib.Path file: Full path to the project file.
    :ivar str design: Active design name (may be empty).
    :ivar str user: OS user that launched the solve.
    :ivar str cmd_line: Exact command line used for the run.
    """

    name: str
    file: Path
    design: str = ""
    user: str = ""
    cmd_line: str = ""


@dataclass(slots=True)
class InitMesh:
    """
    Statistics reported during the initial tetrahedral meshing phase.

    :ivar int tetrahedra: Number of tetrahedra created.
    :ivar float memory_mb: Peak memory consumption in megabytes.
    :ivar int real_time_sec: Wall clock time in seconds.
    :ivar int cpu_time_sec: CPU time in seconds.
    """

    tetrahedra: int
    memory_mb: float
    real_time_sec: int
    cpu_time_sec: int


@dataclass(slots=True)
class AdaptivePass:
    """
    Single adaptive solution pass (frequency, delta-S, memory, …).

    :ivar int pass_nr: 1-based pass index.
    :ivar float freq_hz: Target frequency in hertz.
    :ivar int tetrahedra: Number of tetrahedra at *end* of pass.
    :ivar int matrix_size: Order of the FEM matrix.
    :ivar float memory_mb: Memory used in megabytes.
    :ivar float delta_s: Maximum |ΔS| observed (``None`` until reported).
    :ivar bool converged: ``True`` if this pass triggered convergence.
    :ivar int elapsed_sec: Wall time spent in this pass.
    """

    pass_nr: int
    freq_hz: float
    tetrahedra: int
    matrix_size: int
    memory_mb: float
    delta_s: Optional[float]
    converged: bool
    elapsed_sec: int


@dataclass(slots=True)
class Sweep:
    """
    Frequency-sweep summary block.

    :ivar str type: Sweep algorithm: ``Interpolating``, ``Discrete`` or ``Fast``.
    :ivar int frequencies: Total number of frequency points requested.
    :ivar list[float] solved: List of frequencies (Hz) actually solved.
    :ivar int elapsed_sec: Wall clock time for the entire sweep.
    """

    type: str
    frequencies: int
    solved: List[float]
    elapsed_sec: int


class BlockParser:
    """Base class for a single block parser."""

    def __init__(self, lines: List[str]) -> None:
        self.lines = lines

    def parse(self) -> Any:
        raise NotImplementedError


class ProjectBlockParser(BlockParser):
    """
    Extract project meta-data from the log header.

    Example::

        >>> block = ProjectBlockParser(lines)
        >>> info = block.parse()
        >>> info.name
        'Patch_Antenna'
    """

    def parse(self) -> ProjectInfo:
        """
        Parse the stored lines and return a :class:`ProjectInfo` instance.

        :return: Populated data object.
        :rtype: ProjectInfo
        :raises ValueError: If mandatory fields (project name or file path)
                            cannot be located.
        """
        proj, design, user, cmd = "", "", "", ""
        for line in self.lines:
            if m := re.search(r"Project:(?P<proj>[^,]+),\s*Design:(?P<des>[^,]+)", line):
                proj, design = m["proj"].strip(), m["des"].strip()
            if m := re.search(r"Running as user\s*:\s*(?P<user>.+)", line):
                user = m["user"].strip()
            if m := re.search(r'Using command line:\s*(?P<cmd>".+")', line):
                cmd = m["cmd"]
        # file is the batch-solve argument
        file = Path(re.search(r"Batch Solve/Save:\s*(?P<file>.+)", "\n".join(self.lines))["file"])
        return ProjectInfo(name=proj, file=file, design=design, user=user, cmd_line=cmd)


class InitMeshBlockParser(BlockParser):
    def parse(self) -> InitMesh:
        tet = mem = rt = ct = None
        for idx, line in enumerate(self.lines):
            if "[PROFILE] Initial Meshing" in line:
                # scan forward up to 10 lines for the pieces
                for future in self.lines[idx : idx + 10]:
                    if m := re.search(r"Tetrahedra: (?P<tet>\d+)", future):
                        tet = int(m["tet"])
                    if m := re.search(r"Memory (?P<mem>[\d.]+) M", future):
                        mem = float(m["mem"])
                    if m := re.search(r"Real Time (?P<rt>[\d:]+)", future):
                        rt = _to_sec(m["rt"])
                    if m := re.search(r"CPU Time (?P<ct>[\d:]+)", future):
                        ct = _to_sec(m["ct"])
                if all(v is not None for v in (tet, mem, rt, ct)):
                    return InitMesh(tetrahedra=tet, memory_mb=mem, real_time_sec=rt, cpu_time_sec=ct)
                break
        raise ValueError("Initial mesh block not found")


class AdaptiveBlockParser(BlockParser):
    """
    Build a list of :class:`AdaptivePass` objects from the adaptive section.
    """

    def parse(self) -> List[AdaptivePass]:
        """
        Parse every adaptive pass and determine which one triggered convergence.

        :return: Ordered list of passes (pass_nr always increases).
        :rtype: list[AdaptivePass]
        """
        passes: List[AdaptivePass] = []
        current: Optional[AdaptivePass] = None
        last_converge_pass: Optional[int] = None
        adaptive_converged_line_found = False

        for lineno, line in enumerate(self.lines, 1):
            # ---- Check for "Adaptive Passes converged" literal string (check every line) ----
            if "Adaptive Passes converged" in line:
                adaptive_converged_line_found = True

            # ---- new adaptive pass ----------------------------------
            if m := re.search(r"Adaptive Pass (?P<n>\d+).*Frequency: (?P<f>[\d.kMGHz]+)", line, re.I):
                current = AdaptivePass(
                    pass_nr=int(m["n"]),
                    freq_hz=_to_hz(m["f"]),
                    tetrahedra=0,
                    matrix_size=0,
                    memory_mb=0.0,
                    delta_s=None,
                    converged=False,
                    elapsed_sec=0,
                )

            if not current:
                continue

            # ---- collect details ------------------------------------
            if m := re.search(r"Tetrahedra: (?P<tet>\d+)", line):
                current.tetrahedra = int(m["tet"])
            if m := re.search(r"Matrix size: (?P<sz>\d+)", line):
                current.matrix_size = int(m["sz"])
            if m := re.search(r"Memory (?P<mem>[\d.]+) M", line):
                current.memory_mb = float(m["mem"])
            if m := re.search(r"Max Mag\. Delta S:\s*(?P<ds>[\d.]+)", line):
                current.delta_s = float(m["ds"])
            if m := re.search(r"Elapsed time.*:\s*(?P<et>[\d:]+)", line):
                current.elapsed_sec = _to_sec(m["et"])

            # ---- store pass when [CONVERGE] appears -----------------
            if m := re.search(r"\[CONVERGE].*pass number\D+(?P<n>\d+)", line, re.I):
                passes.append(current)
                last_converge_pass = int(m["n"])
                current = None

        # ---- final decision ----------------------------------------
        if adaptive_converged_line_found and last_converge_pass is not None:
            for p in passes:
                p.converged = p.pass_nr == last_converge_pass
        return passes


class SweepBlockParser(BlockParser):
    """
    Extract frequency-sweep summary (if present).
    """

    def parse(self) -> Optional[Sweep]:
        """
        Return sweep information or ``None`` if the log contains no sweep block.

        :return: Sweep summary object.
        :rtype: Sweep | None
        """
        sweep_type, freqs, solved, elapsed = "", 0, [], 0
        for line in self.lines:
            if m := re.search(r"Interpolating|Discrete|Fast", line):
                sweep_type = m.group(0)
            if m := re.search(r"(?P<n>\d+)\s*Frequencies", line):
                freqs = int(m["n"])
            if m := re.search(r"Frequency - (?P<f>[\d.kMGHz]+)", line, re.I):
                solved.append(_to_hz(m["f"]))
            if m := re.search(r"Elapsed time.*:\s*(?P<et>[\d:]+)", line):
                elapsed = _to_sec(m["et"])
        if freqs:
            return Sweep(type=sweep_type or "Interpolating", frequencies=freqs, solved=solved, elapsed_sec=elapsed)
        return None


class HFSSLogParser:
    """
    High-level façade that orchestrates all block parsers.

    Typical usage::

        >>> log = HFSSLogParser("/tmp/project.aedt.batchinfo.1234/hfss.log")
        >>> data = log.parse()
        >>> data.is_converged()
        True
    """

    BLOCK_MAP: Dict[str, type[BlockParser]] = {
        "project": ProjectBlockParser,
        "init_mesh": InitMeshBlockParser,
        "adaptive": AdaptiveBlockParser,
        "sweep": SweepBlockParser,
    }

    def __init__(self, log_path: str | Path):
        self.path = Path(log_path)

    def parse(self) -> ParsedLog:
        """
        Execute all sub-parsers and return a unified object.

        :return: Structured representation of the entire log.
        :rtype: ParsedLog
        :raises FileNotFoundError: If *log_path* does not exist.
        :raises ValueError: If a mandatory block cannot be parsed.
        """
        text = self.path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()

        project = ProjectBlockParser(lines).parse()
        init_mesh = InitMeshBlockParser(lines).parse()
        adaptive = AdaptiveBlockParser(lines).parse()
        sweep = SweepBlockParser(lines).parse()

        return ParsedLog(
            project=project,
            init_mesh=init_mesh,
            adaptive=adaptive,
            sweep=sweep,
        )


@dataclass(slots=True)
class ParsedLog:
    """
    Root container returned by :meth:`HFSSLogParser.parse`.

    :ivar ProjectInfo project: Project meta-data.
    :ivar InitMesh init_mesh: Initial-mesh metrics.
    :ivar list[AdaptivePass] adaptive: Adaptive passes in chronological order.
    :ivar Sweep | None sweep: Frequency-sweep summary (``None`` if absent).
    """

    project: ProjectInfo
    init_mesh: InitMesh
    adaptive: List[AdaptivePass]
    sweep: Optional[Sweep]

    def to_dict(self) -> dict:
        """
        Deep-convert the entire object to JSON-serialisable primitives.

        :return: Plain ``dict`` / ``list`` / scalar structure.
        :rtype: dict[str, Any]
        """
        return _as_dict(self)

    def is_converged(self) -> bool:
        """
        Return ``True`` if the adaptive solver declared convergence.

        :rtype: bool
        """
        return self.adaptive[-1].converged if self.adaptive else False

    def adaptive_passes(self) -> List[AdaptivePass]:
        """Alias to keep API explicit."""
        return self.adaptive

    def memory_on_convergence(self) -> float:
        """
        Memory (MB) consumed by the *last* converged adaptive pass.

        :return: Megabytes, or :py:const:`math.nan` if no pass converged.
        :rtype: float
        """
        for p in reversed(self.adaptive):
            if p.converged:
                return p.memory_mb
        return math.nan

    def is_completed(self) -> bool:
        """
        Heuristic indicating a successful end-to-end solve.

        A simulation is considered complete when **both** of the following
        conditions are satisfied:

        1. At least one adaptive pass converged.
        2. A frequency-sweep block exists with elapsed time greater than zero.

        :rtype: bool
        """
        return self.is_converged() and self.sweep is not None and self.sweep.elapsed_sec > 0

    def errors(self) -> List[str]:
        """
        Extract only **error** lines (warnings are ignored).

        ANSYS marks errors with ``[error]`` or ``*** ERROR ***``.

        :return: List of stripped error lines (empty if none).
        :rtype: list[str]
        """
        errs: List[str] = []
        # we keep the raw lines inside the ProjectBlockParser – expose them
        raw = self._raw_lines  # added below
        for line in raw:
            if re.search(r"\[error\]|\*\*\* ERROR \*\*\*", line, re.I):
                errs.append(line.strip())
        return errs

    @property
    def _raw_lines(self) -> List[str]:
        # cache lazily
        if not hasattr(self, "__raw"):
            self.__raw = self.project.file.with_suffix(".log").read_text(encoding="utf-8", errors="ignore").splitlines()
        return self.__raw
