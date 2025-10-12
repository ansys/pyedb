from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Any, Dict, List, Optional


def _to_hz(text: str) -> float:
    """Convert 3GHz / 100kHz / 10MHz → Hz."""
    m = re.match(r"(?P<val>[\d.]+)\s*(?P<unit>[kMG]?Hz)", text, re.I)
    if not m:
        return math.nan
    val, unit = float(m["val"]), m["unit"].lower()
    scale = {"hz": 1, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
    return val * scale[unit]


def _to_sec(mm_ss: str) -> int:
    """Convert 'MM:SS' or 'H:MM:SS' or 'HH:MM:SS' → seconds."""
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
    name: str
    file: Path
    design: str = ""
    user: str = ""
    cmd_line: str = ""


@dataclass(slots=True)
class InitMesh:
    tetrahedra: int
    memory_mb: float
    real_time_sec: int
    cpu_time_sec: int


@dataclass(slots=True)
class AdaptivePass:
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
    def parse(self) -> ProjectInfo:
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
    def parse(self) -> List[AdaptivePass]:
        passes: List[AdaptivePass] = []
        current: Dict[str, Any] = {}
        for line in self.lines:
            if m := re.search(r"Adaptive Pass (?P<n>\d+).*Frequency: (?P<f>[\d.kMGHz]+)", line, re.I):
                current = {"pass": int(m["n"]), "freq": _to_hz(m["f"])}
            if m := re.search(r"Tetrahedra: (?P<tet>\d+)", line):
                current["tet"] = int(m["tet"])
            if m := re.search(r"Matrix size: (?P<sz>\d+)", line):
                current["matrix"] = int(m["sz"])
            if m := re.search(r"Memory (?P<mem>[\d.]+) M", line):
                current["mem"] = float(m["mem"])
            if m := re.search(r"Max Mag\. Delta S:\s*(?P<ds>[\d.]+)", line):
                current["delta_s"] = float(m["ds"])
            if m := re.search(r"Elapsed time.*:\s*(?P<et>[\d:]+)", line):
                current["elapsed"] = _to_sec(m["et"])
            if "[CONVERGE]" in line and "Pass Number" in line:
                current["converged"] = True
                passes.append(
                    AdaptivePass(
                        pass_nr=current["pass"],
                        freq_hz=current["freq"],
                        tetrahedra=current["tet"],
                        matrix_size=current["matrix"],
                        memory_mb=current["mem"],
                        delta_s=current.get("delta_s"),
                        converged=current.get("converged", False),
                        elapsed_sec=current.get("elapsed", 0),
                    )
                )
        return passes


class SweepBlockParser(BlockParser):
    def parse(self) -> Optional[Sweep]:
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
    BLOCK_MAP: Dict[str, type[BlockParser]] = {
        "project": ProjectBlockParser,
        "init_mesh": InitMeshBlockParser,
        "adaptive": AdaptiveBlockParser,
        "sweep": SweepBlockParser,
    }

    def __init__(self, log_path: str | Path):
        self.path = Path(log_path)

    def parse(self) -> ParsedLog:
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
    project: ProjectInfo
    init_mesh: InitMesh
    adaptive: List[AdaptivePass]
    sweep: Optional[Sweep]

    def to_dict(self) -> dict:
        return _as_dict(self)

    def is_converged(self) -> bool:
        """True if at least one adaptive pass reached convergence."""
        return any(p.converged for p in self.adaptive)

    def adaptive_passes(self) -> List[AdaptivePass]:
        """Alias to keep API explicit."""
        return self.adaptive

    def memory_on_convergence(self) -> float:
        """Memory (MB) of the **last** converged pass, or NaN."""
        for p in reversed(self.adaptive):
            if p.converged:
                return p.memory_mb
        return math.nan

    def is_completed(self) -> bool:
        """
        Heuristic:  simulation is considered completed when
        - at least one adaptive pass converged **and**
        - a frequency-sweep block exists with elapsed time > 0
        """
        return self.is_converged() and self.sweep is not None and self.sweep.elapsed_sec > 0

    def errors(self) -> List[str]:
        """
        Return **error** lines only (skip warnings).
        ANSYS prefixes errors with [error] or *** ERROR ***.
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
