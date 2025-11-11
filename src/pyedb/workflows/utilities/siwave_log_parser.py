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


"""
siwave_log_parser.py
Parse Ansys SIwave batch logs into dataclasses.

Usage
-----
>>> from pyedb.workflows.utilities.siwave_log_parser import SiwaveLogParser
>>> parser = SiwaveLogParser(r"C:\path\to\siwave.log")
>>> log = parser.parse()
>>> log.summary()
>>> log.to_json("siwave.json")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
# Format 1: MM/DD/YYYY HH:MM:SS AM/PM
RE_TS_DATE_FIRST = re.compile(r"(?P<date>\d{1,2}/\d{1,2}/\d{4})\s+(?P<time>\d{1,2}:\d{2}:\d{2})\s+(?P<ampm>AM|PM)")
# Format 2: HH:MM:SS AM/PM  Mon DD, YYYY
RE_TS_TIME_FIRST = re.compile(
    r"(?P<time>\d{1,2}:\d{2}:\d{2})\s+(?P<ampm>AM|PM)\s+(?P<month>\w{3})\s+(?P<day>\d{1,2}),\s+(?P<year>\d{4})"
)


def _parse_ts(txt: str) -> datetime:
    """
    Convert timestamp strings to datetime.

    Supports two formats:
    - '11/10/2025 05:46:09 PM' (date first)
    - '11:55:29 AM  Oct 12, 2025' (time first)
    """
    # Try date-first format
    m = RE_TS_DATE_FIRST.search(txt)
    if m:
        return datetime.strptime(f"{m['date']} {m['time']} {m['ampm']}", "%m/%d/%Y %I:%M:%S %p")

    # Try time-first format
    m = RE_TS_TIME_FIRST.search(txt)
    if m:
        return datetime.strptime(
            f"{m['month']} {m['day']}, {m['year']} {m['time']} {m['ampm']}", "%b %d, %Y %I:%M:%S %p"
        )

    raise ValueError(f"Cannot parse timestamp: {txt!r}")


def _split_kv(line: str, sep: str = ":") -> tuple[str, str]:
    """Return (key, value) from 'key: value'."""
    k, _, v = line.partition(sep)
    return k.strip(), v.strip()


def _as_dict(obj: Any) -> Any:
    """Recursively convert dataclasses / lists / primitives to plain Python types."""
    if hasattr(obj, "__dataclass_fields__"):
        return {f: _as_dict(getattr(obj, f)) for f in obj.__dataclass_fields__}
    if isinstance(obj, list):
        return [_as_dict(i) for i in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj


# ------------------------------------------------------------------
# Dataclasses
# ------------------------------------------------------------------
@dataclass(slots=True)
class AEDTVersion:
    version: str
    build: str
    location: str


@dataclass(slots=True)
class BatchInfo:
    path: str
    started: datetime
    stopped: datetime
    run_by: str
    temp_dir: str
    project_dir: str
    status: str = ""  # "Normal Completion", "Aborted", etc.


@dataclass(slots=True)
class SimSettings:
    design_type: str
    allow_off_core: bool
    manual_settings: bool
    two_level: bool
    distribution_types: List[str]
    machines: List[str]


@dataclass(slots=True)
class WarningEntry:
    timestamp: datetime
    category: str  # 'SHORT' | 'OTHER'
    net1: str
    net2: str
    layer: str
    x: float
    y: float
    message: str


@dataclass(slots=True)
class ProfileEntry:
    timestamp: datetime
    task: str
    real_time: Optional[str] = None
    cpu_time: Optional[str] = None
    memory: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict)


# ------------------------------------------------------------------
# Block Parsers
# ------------------------------------------------------------------
class BlockParser:
    """Base class for a single block parser."""

    def __init__(self, lines: List[str]) -> None:
        self.lines = lines

    def parse(self) -> Any:
        raise NotImplementedError


class HeaderBlockParser(BlockParser):
    """Extract AEDT version information from the log header."""

    def parse(self) -> AEDTVersion:
        """
        Parse the stored lines and return an AEDTVersion instance.

        :return: Populated data object.
        :rtype: AEDTVersion
        """
        pat_ver = re.compile(r"Version\s+([^,]+).*Build:\s+(.+)")
        pat_loc = re.compile(r"Location:\s+(.+)")
        ver, build, loc = "", "", ""
        for ln in self.lines:
            if m := pat_ver.search(ln):
                ver, build = m.groups()
            if m := pat_loc.search(ln):
                loc = m[1]
            if ver and loc:
                break
        return AEDTVersion(version=ver.strip(), build=build.strip(), location=loc.strip())


class BatchSettingsBlockParser(BlockParser):
    """Extract batch info and simulation settings."""

    def parse(self) -> tuple[BatchInfo, SimSettings]:
        """
        Parse batch information and simulation settings.

        :return: Tuple of (BatchInfo, SimSettings).
        :rtype: tuple[BatchInfo, SimSettings]
        """
        batch_path = ""
        started = stopped = None
        run_by = ""
        temp_dir = ""
        project_dir = ""
        status = ""
        design_type = ""
        allow_off_core = False
        manual_settings = False
        two_level = False
        dist_types: List[str] = []
        machines: List[str] = []

        for ln in self.lines:
            ln_stripped = ln.strip()
            if ln_stripped.startswith("Batch Solve/Save:"):
                batch_path = ln_stripped.split(":", 1)[1].strip()
            elif ln_stripped.startswith("Starting Batch Run:"):
                started = _parse_ts(ln_stripped)
            elif ln_stripped.startswith("Running as user :"):
                run_by = ln_stripped.split(":", 1)[1].strip()
            elif ln_stripped.startswith("Temp directory:"):
                temp_dir = ln_stripped.split(":", 1)[1].strip()
            elif ln_stripped.startswith("Project directory:"):
                project_dir = ln_stripped.split(":", 1)[1].strip()
            elif ln_stripped.startswith("Stopping Batch Run:"):
                stopped = _parse_ts(ln_stripped)
            elif ln_stripped.startswith("Design type:"):
                design_type = ln_stripped.split(":", 1)[1].strip()
            elif ln_stripped.startswith("Allow off core:"):
                allow_off_core = ln_stripped.split(":", 1)[1].strip().lower() == "true"
            elif ln_stripped.startswith("Using manual settings"):
                manual_settings = True
            elif ln_stripped.startswith("Two level:"):
                two_level = ln_stripped.split(":", 1)[1].strip().lower() == "enabled"
            elif ln_stripped.startswith("Distribution types:"):
                dist_types = [x.strip() for x in ln_stripped.split(":", 1)[1].split(",")]
            elif ln_stripped.startswith("localhost RAM:"):
                machines.append(ln_stripped)

            # Status can appear in PROFILE lines like: "Status: Normal Completion"
            if "Status:" in ln and not status:
                # Extract status from anywhere in the line
                if m := re.search(r"Status:\s*([^,(]+)", ln):
                    status = m.group(1).strip()

        batch = BatchInfo(
            path=batch_path,
            started=started or datetime.min,
            stopped=stopped or datetime.min,
            run_by=run_by,
            temp_dir=temp_dir,
            project_dir=project_dir,
            status=status,
        )
        settings = SimSettings(
            design_type=design_type,
            allow_off_core=allow_off_core,
            manual_settings=manual_settings,
            two_level=two_level,
            distribution_types=dist_types,
            machines=machines,
        )
        return batch, settings


class WarningsBlockParser(BlockParser):
    """Extract warning entries from the log."""

    def parse(self) -> List[WarningEntry]:
        """
        Parse warning messages.

        :return: List of warning entries.
        :rtype: list[WarningEntry]
        """
        pat = re.compile(
            r".*Geometry on nets (?P<n1>\w+) and (?P<n2>\w+) on layer \"(?P<layer>\w+)\" "
            r"are electrically shorted at approximately \((?P<x>[-\d.]+),\s*(?P<y>[-\d.]+)\)mm"
        )
        out: List[WarningEntry] = []
        for ln in self.lines:
            if "electrically shorted" not in ln:
                continue

            # Check if line has a timestamp before trying to parse
            if not RE_TS_DATE_FIRST.search(ln) and not RE_TS_TIME_FIRST.search(ln):
                # Skip lines without timestamps
                continue

            try:
                ts = _parse_ts(ln)
            except ValueError:
                # Skip lines where timestamp parsing fails
                continue

            m = pat.search(ln)
            if m:
                out.append(
                    WarningEntry(
                        timestamp=ts,
                        category="SHORT",
                        net1=m["n1"],
                        net2=m["n2"],
                        layer=m["layer"],
                        x=float(m["x"]),
                        y=float(m["y"]),
                        message=ln.split(":", 3)[-1].strip(),
                    )
                )
            else:
                out.append(
                    WarningEntry(
                        timestamp=ts,
                        category="OTHER",
                        net1="",
                        net2="",
                        layer="",
                        x=0.0,
                        y=0.0,
                        message=ln.split(":", 3)[-1].strip(),
                    )
                )
        return out


class ProfileBlockParser(BlockParser):
    """Extract profile entries from the log."""

    def parse(self) -> List[ProfileEntry]:
        """
        Parse profile entries showing task timing and resource usage.

        :return: List of profile entries.
        :rtype: list[ProfileEntry]
        """
        pat = re.compile(r".*\[PROFILE\]\s+(?P<task>.+?)\s*:\s*(?P<rest>.+)")
        out: List[ProfileEntry] = []
        for ln in self.lines:
            if "[PROFILE]" not in ln:
                continue

            # Check if line has a timestamp before trying to parse
            if not RE_TS_DATE_FIRST.search(ln) and not RE_TS_TIME_FIRST.search(ln):
                # Skip lines without timestamps
                continue

            try:
                ts = _parse_ts(ln)
            except ValueError:
                # Skip lines where timestamp parsing fails
                continue

            m = pat.search(ln)
            if not m:
                continue
            task, rest = m["task"], m["rest"]
            rt = ct = mem = None
            extras: Dict[str, str] = {}
            for chunk in rest.split(":"):
                chunk = chunk.strip()
                if chunk.startswith("Real Time"):
                    rt = chunk.split(None, 2)[2]
                elif chunk.startswith("CPU Time"):
                    ct = chunk.split(None, 2)[2]
                elif chunk.startswith("Memory"):
                    mem = chunk.split(None, 1)[1]
                elif "Number of" in chunk:
                    k, v = _split_kv(chunk)
                    extras[k] = v
            out.append(ProfileEntry(timestamp=ts, task=task, real_time=rt, cpu_time=ct, memory=mem, extra=extras))
        return out


# ------------------------------------------------------------------
# Parsed Log Container
# ------------------------------------------------------------------
@dataclass(slots=True)
class ParsedSiwaveLog:
    """
    Root container returned by SiwaveLogParser.parse().

    :ivar AEDTVersion aedt: AEDT version information.
    :ivar BatchInfo batch: Batch run metadata.
    :ivar SimSettings settings: Simulation settings.
    :ivar list[WarningEntry] warnings: Warning entries from the log.
    :ivar list[ProfileEntry] profile: Profile/timing entries.
    """

    aedt: AEDTVersion
    batch: BatchInfo
    settings: SimSettings
    warnings: List[WarningEntry] = field(default_factory=list)
    profile: List[ProfileEntry] = field(default_factory=list)

    def summary(self) -> None:
        """Print a summary of the parsed log."""
        print("Project :", Path(self.batch.path).stem)
        print("Run by  :", self.batch.run_by)
        print("Started :", self.batch.started.strftime("%c"))
        print("Stopped :", self.batch.stopped.strftime("%c"))
        print("Status  :", self.batch.status or "Unknown")
        print("Warnings:", len(self.warnings))
        print("Profile entries:", len(self.profile))

    def is_completed(self) -> bool:
        """
        Check if the simulation completed normally.

        :return: True if status is "Normal Completion", False otherwise.
        :rtype: bool
        """
        return self.batch.status == "Normal Completion"

    def is_aborted(self) -> bool:
        """
        Check if the simulation was aborted.

        :return: True if simulation did not complete normally, False otherwise.
        :rtype: bool
        """
        return bool(self.batch.status) and self.batch.status != "Normal Completion"

    def to_json(self, fp: str, **kw) -> None:
        """
        Serialise to JSON (datetime→ISO).

        :param fp: File path to write JSON to.
        :type fp: str
        :param kw: Additional keyword arguments for json.dumps.
        """
        Path(fp).write_text(json.dumps(self.to_dict(), **kw), encoding="utf-8")

    def to_dict(self) -> dict:
        """
        Deep-convert the entire object to JSON-serialisable primitives.

        :return: Plain dict / list / scalar structure.
        :rtype: dict[str, Any]
        """
        return _as_dict(self)


# ------------------------------------------------------------------
# Main Parser Façade
# ------------------------------------------------------------------
class SiwaveLogParser:
    """
    High-level façade that orchestrates all block parsers.

    Typical usage::

        >>> parser = SiwaveLogParser("/tmp/siwave.log")
        >>> log = parser.parse()
        >>> log.summary()
        >>> log.to_json("output.json")
    """

    BLOCK_MAP: Dict[str, type[BlockParser]] = {
        "header": HeaderBlockParser,
        "batch_settings": BatchSettingsBlockParser,
        "warnings": WarningsBlockParser,
        "profile": ProfileBlockParser,
    }

    def __init__(self, log_path: str | Path):
        """
        Initialize the parser with a log file path.

        :param log_path: Path to the SIwave log file.
        :type log_path: str | Path
        """
        self.path = Path(log_path)

    def parse(self) -> ParsedSiwaveLog:
        """
        Execute all sub-parsers and return a unified object.

        :return: Structured representation of the entire log.
        :rtype: ParsedSiwaveLog
        :raises FileNotFoundError: If log_path does not exist.
        :raises ValueError: If a mandatory block cannot be parsed.
        """
        text = self.path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()

        aedt = HeaderBlockParser(lines).parse()
        batch, settings = BatchSettingsBlockParser(lines).parse()
        warnings = WarningsBlockParser(lines).parse()
        profile = ProfileBlockParser(lines).parse()

        return ParsedSiwaveLog(
            aedt=aedt,
            batch=batch,
            settings=settings,
            warnings=warnings,
            profile=profile,
        )


# Quick demo when run as script
if __name__ == "__main__":
    import pprint
    import sys

    if len(sys.argv) != 2:
        print("Usage: python siwave_log_parser.py path/to/siwave.log")
        sys.exit(1)

    parser = SiwaveLogParser(sys.argv[1])
    log = parser.parse()
    log.summary()
    print("\nFirst 3 warnings:")
    pprint.pp(log.warnings[:3])
    print("\nLast 3 profile entries:")
    pprint.pp(log.profile[-3:])
