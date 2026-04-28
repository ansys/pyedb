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

"""SIwave log file parser for extracting simulation results and metrics.

This module provides tools to parse Ansys SIwave batch simulation logs into
structured dataclasses, making it easy to extract timing information, warnings,
profile data, and simulation status.

Examples
--------
Basic usage for parsing a SIwave log file:

>>> from pyedb.workflows.utilities.siwave_log_parser import SiwaveLogParser
>>> parser = SiwaveLogParser(r"C:\path\to\siwave.log")
>>> log = parser.parse()
>>> log.summary()
>>> log.to_json("siwave.json")

Check simulation completion status:

>>> if log.is_completed():
...     print("Simulation completed successfully")
... else:
...     print("Simulation failed or was aborted")

"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any

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
    """Convert timestamp strings to datetime objects.

    Parse timestamp strings in two different SIwave log formats and return
    a datetime object. Supports both date-first and time-first formats.

    Parameters
    ----------
    txt : str
        Timestamp string from SIwave log. Supports two formats:

        - Date-first: ``'11/10/2025 05:46:09 PM'``
        - Time-first: ``'11:55:29 AM  Oct 12, 2025'``

    Returns
    -------
    datetime
        Parsed datetime object.

    Examples
    --------
    >>> _parse_ts("11/10/2025 05:46:09 PM")
    datetime.datetime(2025, 11, 10, 17, 46, 9)
    >>> _parse_ts("11:55:29 AM  Oct 12, 2025")
    datetime.datetime(2025, 10, 12, 11, 55, 29)
    >>> try:
    ...     _parse_ts("invalid timestamp")
    ... except ValueError as e:
    ...     print("Cannot parse")
    Cannot parse

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
    """Split a key-value line into key and value strings.

    Parse lines in the format ``'key: value'`` and return a tuple of the
    stripped key and value parts.

    Parameters
    ----------
    line : str
        Input line containing a separator.
    sep : str, optional
        Separator character. The default is ``":"``.

    Returns
    -------
    tuple[str, str]
        Tuple of (key, value) with whitespace stripped from both.

    Examples
    --------
    >>> _split_kv("Real Time: 00:05:30")
    ('Real Time', '00:05:30')
    >>> _split_kv("Number of cores=4", sep="=")
    ('Number of cores', '4')
    >>> _split_kv("Status:  Normal Completion")
    ('Status', 'Normal Completion')

    """
    k, _, v = line.partition(sep)
    return k.strip(), v.strip()


def _as_dict(obj: Any) -> Any:
    """Recursively convert dataclasses to JSON-serializable primitives.

    Convert dataclass instances, lists, and Path objects to plain Python types
    that can be serialized to JSON.

    Parameters
    ----------
    obj : Any
        Object to convert. Can be a dataclass, list, Path, or primitive type.

    Returns
    -------
    Any
        Plain Python representation. Dataclasses become dicts, Paths become
        strings, lists are recursively processed, and primitives pass through.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>> from pathlib import Path
    >>> @dataclass
    ... class Sample:
    ...     name: str
    ...     value: int
    >>> _as_dict(Sample("test", 42))
    {'name': 'test', 'value': 42}
    >>> _as_dict(Path("/tmp/file.txt"))
    '/tmp/file.txt'
    >>> _as_dict([1, 2, Path("/test"), "hello"])
    [1, 2, '/test', 'hello']

    """
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
    """AEDT version information extracted from log header.

    Attributes
    ----------
    version : str
        AEDT version number (e.g., ``'2026.1'``).
    build : str
        Build identifier.
    location : str
        Installation path of AEDT.

    Examples
    --------
    >>> version = AEDTVersion(version="2026.1", build="12345", location="C:\\Program Files\\AnsysEM")
    >>> version.version
    '2026.1'

    """

    version: str
    build: str
    location: str


@dataclass(slots=True)
class BatchInfo:
    """Batch simulation run metadata.

    Attributes
    ----------
    path : str
        Full path to the project file.
    started : datetime
        Simulation start timestamp.
    stopped : datetime
        Simulation stop timestamp.
    run_by : str
        Username who executed the simulation.
    temp_dir : str
        Temporary directory used during simulation.
    project_dir : str
        Project working directory.
    status : str, optional
        Simulation completion status such as ``'Normal Completion'`` or ``'Aborted'``.
        The default is ``""``.

    Examples
    --------
    >>> from datetime import datetime
    >>> batch = BatchInfo(
    ...     path="C:\\project\\design.siw",
    ...     started=datetime(2025, 11, 10, 9, 0, 0),
    ...     stopped=datetime(2025, 11, 10, 10, 30, 0),
    ...     run_by="engineer",
    ...     temp_dir="C:\\temp",
    ...     project_dir="C:\\project",
    ...     status="Normal Completion",
    ... )
    >>> batch.status
    'Normal Completion'

    """

    path: str
    started: datetime
    stopped: datetime
    run_by: str
    temp_dir: str
    project_dir: str
    status: str = ""  # "Normal Completion", "Aborted", etc.


@dataclass(slots=True)
class SimSettings:
    """Simulation settings and configuration.

    Attributes
    ----------
    design_type : str
        Type of design being simulated.
    allow_off_core : bool
        Whether off-core solving is enabled.
    manual_settings : bool
        Whether manual settings are being used.
    two_level : bool
        Whether two-level solving is enabled.
    distribution_types : list of str
        Distribution types configured for the simulation.
    machines : list of str
        Machine specifications (RAM, cores, etc.).

    Examples
    --------
    >>> settings = SimSettings(
    ...     design_type="SIwave",
    ...     allow_off_core=True,
    ...     manual_settings=False,
    ...     two_level=True,
    ...     distribution_types=["Local"],
    ...     machines=["localhost RAM: 32GB"],
    ... )
    >>> settings.allow_off_core
    True

    """

    design_type: str
    allow_off_core: bool
    manual_settings: bool
    two_level: bool
    distribution_types: list[str]
    machines: list[str]


@dataclass(slots=True)
class WarningEntry:
    """Single warning message from the simulation log.

    Attributes
    ----------
    timestamp : datetime
        When the warning occurred.
    category : str
        Warning category: ``'SHORT'`` for electrical shorts or ``'OTHER'`` for
        other warnings.
    net1 : str
        First net involved (for SHORT warnings).
    net2 : str
        Second net involved (for SHORT warnings).
    layer : str
        Layer name where the issue occurred.
    x : float
        X-coordinate in millimeters.
    y : float
        Y-coordinate in millimeters.
    message : str
        Complete warning message text.

    Examples
    --------
    >>> from datetime import datetime
    >>> warning = WarningEntry(
    ...     timestamp=datetime(2025, 11, 10, 9, 15, 30),
    ...     category="SHORT",
    ...     net1="VCC",
    ...     net2="GND",
    ...     layer="TOP",
    ...     x=12.5,
    ...     y=34.8,
    ...     message="Nets are electrically shorted",
    ... )
    >>> warning.category
    'SHORT'

    """

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
    """Performance profile entry showing task timing and resource usage.

    Attributes
    ----------
    timestamp : datetime
        When the task completed.
    task : str
        Task or operation name.
    real_time : str, optional
        Wall clock time in human-readable format. The default is ``None``.
    cpu_time : str, optional
        CPU time consumed. The default is ``None``.
    memory : str, optional
        Peak memory usage. The default is ``None``.
    extra : dict of str to str, optional
        Additional metrics (e.g., number of elements). The default is an empty dict.

    Examples
    --------
    >>> from datetime import datetime
    >>> profile = ProfileEntry(
    ...     timestamp=datetime(2025, 11, 10, 9, 30, 0),
    ...     task="Mesh Generation",
    ...     real_time="00:05:30",
    ...     cpu_time="00:05:25",
    ...     memory="2.5 GB",
    ...     extra={"Number of elements": "50000"},
    ... )
    >>> profile.task
    'Mesh Generation'

    """

    timestamp: datetime
    task: str
    real_time: str | None = None
    cpu_time: str | None = None
    memory: str | None = None
    extra: dict[str, str] = field(default_factory=dict)


# ------------------------------------------------------------------
# Block Parsers
# ------------------------------------------------------------------
class BlockParser:
    """Base class for a single block parser.

    Parameters
    ----------
    lines : list of str
        Lines of text to parse from the log file.

    Examples
    --------
    >>> lines = ["Line 1", "Line 2", "Line 3"]
    >>> parser = BlockParser(lines)
    >>> parser.lines
    ['Line 1', 'Line 2', 'Line 3']

    """

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    def parse(self) -> Any:
        """Parse the stored lines.

        Returns
        -------
        Any
            Parsed data structure.

        """
        raise NotImplementedError


class HeaderBlockParser(BlockParser):
    """Extract AEDT version information from the log header.

    This parser searches through log lines to find version, build, and
    installation location information.

    Examples
    --------
    >>> lines = [
    ...     "ANSYS Electromagnetics Suite Version 2026.1 Build: 12345",
    ...     "Location: C:\\Program Files\\AnsysEM\\v261",
    ... ]
    >>> parser = HeaderBlockParser(lines)
    >>> version = parser.parse()
    >>> version.version
    '2026.1'

    """

    def parse(self) -> AEDTVersion:
        """Parse the stored lines and return an AEDTVersion instance.

        Returns
        -------
        AEDTVersion
            Populated version data object containing version, build, and location.

        Examples
        --------
        >>> lines = ["Version 2026.1 Build: 12345", "Location: C:\\AnsysEM"]
        >>> parser = HeaderBlockParser(lines)
        >>> info = parser.parse()
        >>> info.build
        '12345'

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
    """Extract batch information and simulation settings from the log.

    This parser processes batch run metadata including timestamps, user info,
    directories, and simulation configuration settings.

    Examples
    --------
    >>> lines = [
    ...     "Batch Solve/Save: C:\\project\\design.siw",
    ...     "Starting Batch Run: 11/10/2025 09:00:00 AM",
    ...     "Running as user : engineer",
    ...     "Design type: SIwave",
    ...     "Allow off core: True",
    ... ]
    >>> parser = BatchSettingsBlockParser(lines)
    >>> batch, settings = parser.parse()
    >>> batch.run_by
    'engineer'
    >>> settings.design_type
    'SIwave'

    """

    def parse(self) -> tuple[BatchInfo, SimSettings]:
        """Parse batch information and simulation settings.

        Returns
        -------
        tuple[BatchInfo, SimSettings]
            Tuple containing batch run metadata and simulation settings.

        Examples
        --------
        >>> lines = ["Batch Solve/Save: test.siw", "Design type: SIwave"]
        >>> parser = BatchSettingsBlockParser(lines)
        >>> batch, settings = parser.parse()
        >>> isinstance(batch, BatchInfo)
        True
        >>> isinstance(settings, SimSettings)
        True

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
        dist_types: list[str] = []
        machines: list[str] = []

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
    """Extract warning entries from the simulation log.

    This parser identifies and extracts warning messages, particularly focusing
    on electrical short warnings with location information.

    Examples
    --------
    >>> lines = [
    ...     "11/10/2025 09:15:30 AM [warning] Geometry on nets VCC and GND on layer \\"TOP\\" "
    ...     "are electrically shorted at approximately (12.5, 34.8)mm"
    ... ]
    >>> parser = WarningsBlockParser(lines)
    >>> warnings = parser.parse()
    >>> warnings[0].category
    'SHORT'
    >>> warnings[0].net1
    'VCC'

    """

    def parse(self) -> list[WarningEntry]:
        """Parse warning messages from log lines.

        Returns
        -------
        list of WarningEntry
            List of parsed warning entries with categorization and location data.

        Examples
        --------
        >>> lines = ["No warnings"]
        >>> parser = WarningsBlockParser(lines)
        >>> warnings = parser.parse()
        >>> len(warnings)
        0

        """
        pat = re.compile(
            r".*Geometry on nets (?P<n1>\w+) and (?P<n2>\w+) on layer \"(?P<layer>\w+)\" "
            r"are electrically shorted at approximately \((?P<x>[-\d.]+),\s*(?P<y>[-\d.]+)\)mm"
        )
        out: list[WarningEntry] = []
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
    """Extract profile entries showing task timing and resource usage.

    This parser processes [PROFILE] tagged lines to extract performance metrics
    including real time, CPU time, memory usage, and additional task-specific data.

    Examples
    --------
    >>> lines = [
    ...     "11/10/2025 09:30:00 AM [PROFILE] Mesh Generation : Real Time 00:05:30 : "
    ...     "CPU Time 00:05:25 : Memory 2.5 GB : Number of elements: 50000"
    ... ]
    >>> parser = ProfileBlockParser(lines)
    >>> profiles = parser.parse()
    >>> profiles[0].task
    'Mesh Generation'
    >>> profiles[0].real_time
    '00:05:30'

    """

    def parse(self) -> list[ProfileEntry]:
        """Parse profile entries showing task timing and resource usage.

        Returns
        -------
        list of ProfileEntry
            List of profile entries with timing and resource consumption data.

        Examples
        --------
        >>> lines = ["Regular log line without profile"]
        >>> parser = ProfileBlockParser(lines)
        >>> profiles = parser.parse()
        >>> len(profiles)
        0

        """
        pat = re.compile(r".*\[PROFILE\]\s+(?P<task>.+?)\s*:\s*(?P<rest>.+)")
        out: list[ProfileEntry] = []
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
            extras: dict[str, str] = {}
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
    """Root container returned by SiwaveLogParser.parse().

    This class holds all parsed information from a SIwave log file and provides
    convenience methods for checking completion status, generating summaries,
    and exporting data.

    Attributes
    ----------
    aedt : AEDTVersion
        AEDT version information extracted from log header.
    batch : BatchInfo
        Batch run metadata including timestamps and user info.
    settings : SimSettings
        Simulation settings and configuration.
    warnings : list of WarningEntry
        Warning entries from the log. The default is an empty list.
    profile : list of ProfileEntry
        Profile/timing entries showing task performance. The default is an empty list.

    Examples
    --------
    >>> from datetime import datetime
    >>> from pathlib import Path
    >>> log = ParsedSiwaveLog(
    ...     aedt=AEDTVersion(version="2026.1", build="123", location="C:\\AEDT"),
    ...     batch=BatchInfo(
    ...         path="C:\\project\\test.siw",
    ...         started=datetime(2025, 11, 10, 9, 0, 0),
    ...         stopped=datetime(2025, 11, 10, 10, 0, 0),
    ...         run_by="engineer",
    ...         temp_dir="C:\\temp",
    ...         project_dir="C:\\project",
    ...         status="Normal Completion",
    ...     ),
    ...     settings=SimSettings(
    ...         design_type="SIwave",
    ...         allow_off_core=True,
    ...         manual_settings=False,
    ...         two_level=False,
    ...         distribution_types=["Local"],
    ...         machines=[],
    ...     ),
    ... )
    >>> log.is_completed()
    True

    """

    aedt: AEDTVersion
    batch: BatchInfo
    settings: SimSettings
    warnings: list[WarningEntry] = field(default_factory=list)
    profile: list[ProfileEntry] = field(default_factory=list)

    def summary(self) -> None:
        """Print a summary of the parsed log to stdout.

        Examples
        --------
        >>> log = ParsedSiwaveLog(aedt=..., batch=..., settings=...)
        >>> log.summary()
        Project : test_design
        Run by  : engineer
        Started : Mon Nov 10 09:00:00 2025
        Stopped : Mon Nov 10 10:00:00 2025
        Status  : Normal Completion
        Warnings: 0
        Profile entries: 0

        """
        print("Project :", Path(self.batch.path).stem)
        print("Run by  :", self.batch.run_by)
        print("Started :", self.batch.started.strftime("%c"))
        print("Stopped :", self.batch.stopped.strftime("%c"))
        print("Status  :", self.batch.status or "Unknown")
        print("Warnings:", len(self.warnings))
        print("Profile entries:", len(self.profile))

    def is_completed(self) -> bool:
        """Check if the simulation completed normally.

        Returns
        -------
        bool
            ``True`` if status is ``'Normal Completion'``, ``False`` otherwise.

        Examples
        --------
        >>> log = ParsedSiwaveLog(
        ...     aedt=AEDTVersion("2026.1", "123", "C:\\AEDT"),
        ...     batch=BatchInfo(
        ...         path="test.siw",
        ...         started=datetime(2025, 1, 1),
        ...         stopped=datetime(2025, 1, 1),
        ...         run_by="user",
        ...         temp_dir="",
        ...         project_dir="",
        ...         status="Normal Completion",
        ...     ),
        ...     settings=SimSettings("", False, False, False, [], []),
        ... )
        >>> log.is_completed()
        True

        """
        return self.batch.status == "Normal Completion"

    def is_aborted(self) -> bool:
        """Check if the simulation was aborted.

        Returns
        -------
        bool
            ``True`` if simulation did not complete normally, ``False`` otherwise.

        Examples
        --------
        >>> log = ParsedSiwaveLog(
        ...     aedt=AEDTVersion("2026.1", "123", "C:\\AEDT"),
        ...     batch=BatchInfo(
        ...         path="test.siw",
        ...         started=datetime(2025, 1, 1),
        ...         stopped=datetime(2025, 1, 1),
        ...         run_by="user",
        ...         temp_dir="",
        ...         project_dir="",
        ...         status="Aborted",
        ...     ),
        ...     settings=SimSettings("", False, False, False, [], []),
        ... )
        >>> log.is_aborted()
        True

        """
        return bool(self.batch.status) and self.batch.status != "Normal Completion"

    def to_json(self, fp: str, **kw) -> None:
        """Serialize parsed log to JSON file.

        Parameters
        ----------
        fp : str
            File path to write JSON to.
        **kw
            Additional keyword arguments passed to ``json.dumps()``.

        Examples
        --------
        >>> log = ParsedSiwaveLog(aedt=..., batch=..., settings=...)
        >>> log.to_json("output.json", indent=2)

        """
        Path(fp).write_text(json.dumps(self.to_dict(), **kw), encoding="utf-8")

    def to_dict(self) -> dict:
        """Deep-convert the entire object to JSON-serializable primitives.

        Returns
        -------
        dict
            Plain dict/list/scalar structure suitable for JSON serialization.

        Examples
        --------
        >>> log = ParsedSiwaveLog(aedt=..., batch=..., settings=...)
        >>> data_dict = log.to_dict()
        >>> isinstance(data_dict, dict)
        True
        >>> "aedt" in data_dict
        True

        """
        return _as_dict(self)


# ------------------------------------------------------------------
# Main Parser Façade
# ------------------------------------------------------------------
class SiwaveLogParser:
    """High-level parser that orchestrates all block parsers.

    This class provides the main interface for parsing SIwave log files.
    It coordinates multiple specialized parsers to extract version info,
    batch metadata, simulation settings, warnings, and profile data.

    Parameters
    ----------
    log_path : str or pathlib.Path
        Path to the SIwave log file to parse.

    Examples
    --------
    Basic usage:

    >>> from pyedb.workflows.utilities.siwave_log_parser import SiwaveLogParser
    >>> parser = SiwaveLogParser("/tmp/siwave.log")
    >>> log = parser.parse()
    >>> log.summary()
    Project : my_design
    Run by  : engineer
    ...

    Check for warnings:

    >>> parser = SiwaveLogParser("simulation.log")
    >>> log = parser.parse()
    >>> if log.warnings:
    ...     print(f"Found {len(log.warnings)} warnings")
    ...     for w in log.warnings[:3]:
    ...         print(f"  {w.category}: {w.message}")

    Export to JSON:

    >>> parser = SiwaveLogParser("simulation.log")
    >>> log = parser.parse()
    >>> log.to_json("output.json", indent=2)

    """

    BLOCK_MAP: dict[str, type[BlockParser]] = {
        "header": HeaderBlockParser,
        "batch_settings": BatchSettingsBlockParser,
        "warnings": WarningsBlockParser,
        "profile": ProfileBlockParser,
    }

    def __init__(self, log_path: str | Path):
        """Initialize the parser with a log file path.

        Parameters
        ----------
        log_path : str or pathlib.Path
            Path to the SIwave log file.

        """
        self.path = Path(log_path)

    def parse(self) -> ParsedSiwaveLog:
        """Execute all sub-parsers and return a unified object.

        Returns
        -------
        ParsedSiwaveLog
            Structured representation of the entire log including version info,
            batch metadata, settings, warnings, and profile data.

        Examples
        --------
        Parse and check completion:

        >>> parser = SiwaveLogParser("siwave.log")
        >>> log = parser.parse()
        >>> if log.is_completed():
        ...     print("Simulation completed successfully")
        ... else:
        ...     print("Simulation did not complete")

        Access profile data:

        >>> parser = SiwaveLogParser("siwave.log")
        >>> log = parser.parse()
        >>> for entry in log.profile:
        ...     print(f"{entry.task}: {entry.real_time}")

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
