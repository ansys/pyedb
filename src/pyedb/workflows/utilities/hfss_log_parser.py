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

"""HFSS log file parser for extracting simulation results and metrics."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Any, Optional


def _to_hz(text: str) -> float:
    """
    Convert a human-readable frequency string to hertz.

    Parse frequency expressions with standard SI prefixes (k, M, G) and
    convert them to numerical values in hertz.

    Parameters
    ----------
    text : str
        Frequency expression such as ``'3 GHz'``, ``'100 kHz'``, or ``'10MHz'``.
        Spaces between value and unit are optional.

    Returns
    -------
    float
        Numerical value in Hz. Returns ``math.nan`` if the string cannot be parsed.

    Examples
    --------
    >>> _to_hz("3 GHz")
    3000000000.0
    >>> _to_hz("100 kHz")
    100000.0
    >>> _to_hz("10MHz")
    10000000.0
    >>> _to_hz("2.4GHz")
    2400000000.0
    >>> import math
    >>> math.isnan(_to_hz("invalid"))
    True

    """
    m = re.match(r"(?P<val>[\d.]+)\s*(?P<unit>[kMG]?Hz)", text, re.I)
    if not m:
        return math.nan
    val, unit = float(m["val"]), m["unit"].lower()
    scale = {"hz": 1, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
    return val * scale[unit]


def _to_sec(mm_ss: str) -> int:
    """
    Convert an Ansys time stamp to seconds.

    Parse time stamps in various formats (MM:SS, H:MM:SS, or HH:MM:SS) and
    convert them to total elapsed seconds.

    Parameters
    ----------
    mm_ss : str
        Time stamp extracted from the log in format ``MM:SS``, ``H:MM:SS``,
        or ``HH:MM:SS``.

    Returns
    -------
    int
        Total elapsed seconds.

    Examples
    --------
    >>> _to_sec("02:30")
    150
    >>> _to_sec("1:15:45")
    4545
    >>> _to_sec("12:30:00")
    45000
    >>> _to_sec("00:05")
    5

    """
    parts = mm_ss.strip().split(":")
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    if len(parts) == 3:  # H:MM:SS or HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def _as_dict(obj: Any) -> Any:
    """
    Recursively convert dataclasses to plain Python types.

    Convert dataclass instances, lists, and Path objects to JSON-serializable
    primitive types (dict, list, str, etc.).

    Parameters
    ----------
    obj : Any
        Object to convert. Can be a dataclass instance, list, Path, or primitive type.

    Returns
    -------
    Any
        Plain Python type representation. Dataclasses become dicts, Paths become
        strings, lists are recursively processed, and primitives pass through unchanged.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>> from pathlib import Path
    >>> @dataclass
    ... class Point:
    ...     x: int
    ...     y: int
    >>> _as_dict(Point(1, 2))
    {'x': 1, 'y': 2}
    >>> _as_dict(Path("/tmp/file.txt"))
    '/tmp/file.txt'
    >>> _as_dict([1, 2, Path("/test")])
    [1, 2, '/test']

    """
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

    Attributes
    ----------
    name : str
        Project name (without extension).
    file : pathlib.Path
        Full path to the project file.
    design : str, optional
        Active design name. The default is ``""``.
    user : str, optional
        OS user that launched the solve. The default is ``""``.
    cmd_line : str, optional
        Exact command line used for the run. The default is ``""``.

    Examples
    --------
    >>> from pathlib import Path
    >>> info = ProjectInfo(
    ...     name="Patch_Antenna", file=Path("/project/antenna.aedt"), design="HFSSDesign1", user="engineer"
    ... )
    >>> info.name
    'Patch_Antenna'

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

    Attributes
    ----------
    tetrahedra : int
        Number of tetrahedra created.
    memory_mb : float
        Peak memory consumption in megabytes.
    real_time_sec : int
        Wall clock time in seconds.
    cpu_time_sec : int
        CPU time in seconds.

    Examples
    --------
    >>> mesh = InitMesh(tetrahedra=5000, memory_mb=128.5, real_time_sec=45, cpu_time_sec=42)
    >>> mesh.tetrahedra
    5000
    >>> mesh.memory_mb
    128.5

    """

    tetrahedra: int
    memory_mb: float
    real_time_sec: int
    cpu_time_sec: int


@dataclass(slots=True)
class AdaptivePass:
    """
    Single adaptive solution pass with convergence metrics.

    Attributes
    ----------
    pass_nr : int
        1-based pass index.
    freq_hz : float
        Target frequency in hertz.
    tetrahedra : int
        Number of tetrahedra at end of pass.
    matrix_size : int
        Order of the FEM matrix.
    memory_mb : float
        Memory used in megabytes.
    delta_s : float, optional
        Maximum |ΔS| observed. The default is ``None`` until reported.
    converged : bool
        ``True`` if this pass triggered convergence.
    elapsed_sec : int
        Wall time spent in this pass.

    Examples
    --------
    >>> pass1 = AdaptivePass(
    ...     pass_nr=1,
    ...     freq_hz=3e9,
    ...     tetrahedra=10000,
    ...     matrix_size=5000,
    ...     memory_mb=256.0,
    ...     delta_s=0.02,
    ...     converged=False,
    ...     elapsed_sec=120,
    ... )
    >>> pass1.pass_nr
    1
    >>> pass1.converged
    False

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

    Attributes
    ----------
    type : str
        Sweep algorithm: ``Interpolating``, ``Discrete`` or ``Fast``.
    frequencies : int
        Total number of frequency points requested.
    solved : list of float
        List of frequencies (Hz) actually solved.
    elapsed_sec : int
        Wall clock time for the entire sweep.

    Examples
    --------
    >>> sweep = Sweep(type="Interpolating", frequencies=101, solved=[1e9, 2e9, 3e9], elapsed_sec=300)
    >>> sweep.type
    'Interpolating'
    >>> len(sweep.solved)
    3

    """

    type: str
    frequencies: int
    solved: list[float]
    elapsed_sec: int


class BlockParser:
    """
    Base class for a single block parser.

    Parameters
    ----------
    lines : list of str
        Lines of text to parse from the log file.

    Examples
    --------
    >>> lines = ["Line 1", "Line 2"]
    >>> parser = BlockParser(lines)
    >>> parser.lines
    ['Line 1', 'Line 2']

    """

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    def parse(self) -> Any:
        """
        Parse the stored lines.

        Returns
        -------
        Any
            Parsed data structure.

        """
        raise NotImplementedError


class ProjectBlockParser(BlockParser):
    """
    Extract project meta-data from the log header.

    This parser searches for project name, design name, user information,
    and command line arguments in the log file header section.

    Examples
    --------
    >>> lines = [
    ...     "Project: MyProject, Design: HFSSDesign1",
    ...     "Running as user: engineer",
    ...     'Using command line: "ansysedt.exe"',
    ...     "Batch Solve/Save: /path/to/project.aedt",
    ... ]
    >>> parser = ProjectBlockParser(lines)
    >>> info = parser.parse()
    >>> info.name
    'MyProject'

    """

    def parse(self) -> ProjectInfo:
        """
        Parse the stored lines and return a ProjectInfo instance.

        Returns
        -------
        ProjectInfo
            Populated project meta-data object.

        Examples
        --------
        >>> lines = ["Project: Antenna, Design: HFSS1", "Batch Solve/Save: /tmp/antenna.aedt"]
        >>> parser = ProjectBlockParser(lines)
        >>> info = parser.parse()
        >>> info.name
        'Antenna'

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
    """
    Extract initial mesh statistics from the log.

    This parser searches for the initial meshing profile section and extracts
    tetrahedra count, memory usage, and timing information.

    Examples
    --------
    >>> lines = [
    ...     "[PROFILE] Initial Meshing",
    ...     "Tetrahedra: 5000",
    ...     "Memory 128.5 MB",
    ...     "Real Time 00:45",
    ...     "CPU Time 00:42",
    ... ]
    >>> parser = InitMeshBlockParser(lines)
    >>> mesh = parser.parse()
    >>> mesh.tetrahedra
    5000

    """

    def parse(self) -> InitMesh:
        """
        Parse initial mesh statistics from log lines.

        Returns
        -------
        InitMesh
            Initial mesh metrics including tetrahedra count, memory, and timing.

        Examples
        --------
        >>> lines = ["[PROFILE] Initial Meshing", "Tetrahedra: 10000"]
        >>> parser = InitMeshBlockParser(lines)
        >>> mesh = parser.parse()
        >>> mesh.tetrahedra
        10000

        """
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
    Build a list of AdaptivePass objects from the adaptive section.

    This parser extracts all adaptive pass information including convergence
    status, frequency, mesh statistics, and delta-S values.

    Examples
    --------
    >>> lines = [
    ...     "Adaptive Pass 1 at Frequency: 3 GHz",
    ...     "Tetrahedra: 10000",
    ...     "Matrix size: 5000",
    ...     "Memory 256.0 MB",
    ...     "Max Mag. Delta S: 0.02",
    ...     "[CONVERGE] Solution has converged at pass number 1",
    ...     "Adaptive Passes converged",
    ... ]
    >>> parser = AdaptiveBlockParser(lines)
    >>> passes = parser.parse()
    >>> passes[0].pass_nr
    1
    >>> passes[0].converged
    True

    """

    def parse(self) -> list[AdaptivePass]:
        """
        Parse every adaptive pass and determine which one triggered convergence.

        Returns
        -------
        list of AdaptivePass
            Ordered list of passes (pass_nr always increases).

        Examples
        --------
        >>> lines = ["Adaptive Pass 1 at Frequency: 2 GHz", "Tetrahedra: 8000"]
        >>> parser = AdaptiveBlockParser(lines)
        >>> passes = parser.parse()
        >>> len(passes)
        0

        """
        passes: list[AdaptivePass] = []
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
    Extract frequency-sweep summary from the log.

    This parser searches for frequency sweep information including sweep type,
    number of frequencies, and elapsed time.

    Examples
    --------
    >>> lines = [
    ...     "Interpolating Sweep",
    ...     "101 Frequencies",
    ...     "Frequency - 1 GHz",
    ...     "Frequency - 2 GHz",
    ...     "Elapsed time: 00:05:00",
    ... ]
    >>> parser = SweepBlockParser(lines)
    >>> sweep = parser.parse()
    >>> sweep.type
    'Interpolating'
    >>> sweep.frequencies
    101

    """

    def parse(self) -> Optional[Sweep]:
        """
        Return sweep information or None if no sweep block exists.

        Returns
        -------
        Sweep or None
            Sweep summary object, or ``None`` if the log contains no sweep block.

        Examples
        --------
        >>> lines = ["No sweep data"]
        >>> parser = SweepBlockParser(lines)
        >>> parser.parse() is None
        True

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
    High-level parser that orchestrates all block parsers.

    This class provides the main interface for parsing HFSS log files.
    It coordinates multiple specialized parsers to extract project info,
    mesh statistics, adaptive passes, and sweep data.

    Parameters
    ----------
    log_path : str or pathlib.Path
        Path to the HFSS log file to parse.

    Examples
    --------
    >>> from pathlib import Path
    >>> log = HFSSLogParser("/tmp/project.aedt.batchinfo.1234/hfss.log")
    >>> data = log.parse()
    >>> data.is_converged()
    True

    Parse and check for errors:

    >>> log = HFSSLogParser("simulation.log")
    >>> result = log.parse()
    >>> if result.errors():
    ...     print("Errors found:", result.errors())
    ... else:
    ...     print("No errors detected")

    """

    BLOCK_MAP: dict[str, type[BlockParser]] = {
        "project": ProjectBlockParser,
        "init_mesh": InitMeshBlockParser,
        "adaptive": AdaptiveBlockParser,
        "sweep": SweepBlockParser,
    }

    def __init__(self, log_path: str | Path) -> None:
        self.path = Path(log_path)

    def parse(self) -> ParsedLog:
        """
        Execute all sub-parsers and return a unified object.

        Returns
        -------
        ParsedLog
            Structured representation of the entire log including project info,
            mesh statistics, adaptive passes, and sweep data.

        Examples
        --------
        >>> log = HFSSLogParser("hfss.log")
        >>> result = log.parse()
        >>> print(f"Converged: {result.is_converged()}")
        >>> print(f"Passes: {len(result.adaptive)}")

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
    Root container returned by HFSSLogParser.parse().

    This class holds all parsed information from an HFSS log file and provides
    convenience methods for checking convergence, completion status, and
    extracting specific metrics.

    Attributes
    ----------
    project : ProjectInfo
        Project meta-data including name, file path, and design information.
    init_mesh : InitMesh
        Initial mesh statistics.
    adaptive : list of AdaptivePass
        Adaptive passes in chronological order.
    sweep : Sweep or None
        Frequency-sweep summary, or ``None`` if no sweep was performed.

    Examples
    --------
    >>> from pathlib import Path
    >>> parsed = ParsedLog(
    ...     project=ProjectInfo(name="Test", file=Path("/tmp/test.aedt")),
    ...     init_mesh=InitMesh(tetrahedra=5000, memory_mb=100, real_time_sec=30, cpu_time_sec=28),
    ...     adaptive=[],
    ...     sweep=None,
    ... )
    >>> parsed.project.name
    'Test'

    """

    project: ProjectInfo
    init_mesh: InitMesh
    adaptive: list[AdaptivePass]
    sweep: Optional[Sweep]

    def to_dict(self) -> dict:
        """
        Deep-convert the entire object to JSON-serializable primitives.

        Returns
        -------
        dict
            Plain dict/list/scalar structure suitable for JSON serialization.

        Examples
        --------
        >>> parsed = ParsedLog(project=..., init_mesh=..., adaptive=[], sweep=None)
        >>> data_dict = parsed.to_dict()
        >>> isinstance(data_dict, dict)
        True

        """
        return _as_dict(self)

    def is_converged(self) -> bool:
        """
        Check if the adaptive solver declared convergence.

        Returns
        -------
        bool
            ``True`` if at least one adaptive pass converged, ``False`` otherwise.

        Examples
        --------
        >>> parsed = ParsedLog(
        ...     project=ProjectInfo(name="T", file=Path("/t")),
        ...     init_mesh=InitMesh(tetrahedra=100, memory_mb=10, real_time_sec=5, cpu_time_sec=5),
        ...     adaptive=[
        ...         AdaptivePass(
        ...             pass_nr=1,
        ...             freq_hz=1e9,
        ...             tetrahedra=100,
        ...             matrix_size=50,
        ...             memory_mb=10,
        ...             delta_s=0.01,
        ...             converged=True,
        ...             elapsed_sec=10,
        ...         )
        ...     ],
        ...     sweep=None,
        ... )
        >>> parsed.is_converged()
        True

        """
        return self.adaptive[-1].converged if self.adaptive else False

    def adaptive_passes(self) -> list[AdaptivePass]:
        """
        Return the list of adaptive passes.

        Returns
        -------
        list of AdaptivePass
            All adaptive passes in chronological order.

        Examples
        --------
        >>> parsed = ParsedLog(project=..., init_mesh=..., adaptive=[pass1, pass2], sweep=None)
        >>> passes = parsed.adaptive_passes()
        >>> len(passes)
        2

        """
        return self.adaptive

    def memory_on_convergence(self) -> float:
        """
        Memory consumed by the last converged adaptive pass.

        Returns
        -------
        float
            Memory in megabytes, or ``math.nan`` if no pass converged.

        Examples
        --------
        >>> parsed = ParsedLog(
        ...     project=ProjectInfo(name="T", file=Path("/t")),
        ...     init_mesh=InitMesh(tetrahedra=100, memory_mb=10, real_time_sec=5, cpu_time_sec=5),
        ...     adaptive=[
        ...         AdaptivePass(
        ...             pass_nr=1,
        ...             freq_hz=1e9,
        ...             tetrahedra=100,
        ...             matrix_size=50,
        ...             memory_mb=256.5,
        ...             delta_s=0.01,
        ...             converged=True,
        ...             elapsed_sec=10,
        ...         )
        ...     ],
        ...     sweep=None,
        ... )
        >>> parsed.memory_on_convergence()
        256.5

        """
        for p in reversed(self.adaptive):
            if p.converged:
                return p.memory_mb
        return math.nan

    def is_completed(self) -> bool:
        """
        Check if the simulation completed successfully.

        A simulation is considered complete when both adaptive convergence
        occurred and a frequency sweep was executed.

        Returns
        -------
        bool
            ``True`` if converged and sweep completed, ``False`` otherwise.

        Examples
        --------
        >>> parsed = ParsedLog(
        ...     project=ProjectInfo(name="T", file=Path("/t")),
        ...     init_mesh=InitMesh(tetrahedra=100, memory_mb=10, real_time_sec=5, cpu_time_sec=5),
        ...     adaptive=[
        ...         AdaptivePass(
        ...             pass_nr=1,
        ...             freq_hz=1e9,
        ...             tetrahedra=100,
        ...             matrix_size=50,
        ...             memory_mb=256,
        ...             delta_s=0.01,
        ...             converged=True,
        ...             elapsed_sec=10,
        ...         )
        ...     ],
        ...     sweep=Sweep(type="Interpolating", frequencies=11, solved=[1e9], elapsed_sec=30),
        ... )
        >>> parsed.is_completed()
        True

        """
        return self.is_converged() and self.sweep is not None and self.sweep.elapsed_sec > 0

    def errors(self) -> list[str]:
        """
        Extract error lines from the log file.

        Searches the log for lines containing error markers like ``[error]``
        or ``*** ERROR ***``. Warnings are ignored.

        Returns
        -------
        list of str
            List of stripped error lines, empty if none found.

        Examples
        --------
        >>> parsed = ParsedLog(project=..., init_mesh=..., adaptive=[], sweep=None)
        >>> errs = parsed.errors()
        >>> len(errs)
        0

        """
        errs: list[str] = []
        # we keep the raw lines inside the ProjectBlockParser – expose them
        raw = self._raw_lines  # added below
        for line in raw:
            if re.search(r"\[error\]|\*\*\* ERROR \*\*\*", line, re.I):
                errs.append(line.strip())
        return errs

    @property
    def _raw_lines(self) -> list[str]:
        # cache lazily
        if not hasattr(self, "__raw"):
            self.__raw = self.project.file.with_suffix(".log").read_text(encoding="utf-8", errors="ignore").splitlines()
        return self.__raw
