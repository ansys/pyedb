src.pyedb.workflows.utilities.siwave_log_parser
===============================================

.. py:module:: src.pyedb.workflows.utilities.siwave_log_parser

.. autoapi-nested-parse::

   SIwave log file parser for extracting simulation results and metrics.

   This module provides tools to parse Ansys SIwave batch simulation logs into
   structured dataclasses, making it easy to extract timing information, warnings,
   profile data, and simulation status.

   Examples
   --------
   Basic usage for parsing a SIwave log file:

   >>> from pyedb.workflows.utilities.siwave_log_parser import SiwaveLogParser
   >>> parser = SiwaveLogParser(r"C:\path  o\siwave.log")
   >>> log = parser.parse()
   >>> log.summary()
   >>> log.to_json("siwave.json")

   Check simulation completion status:

   >>> if log.is_completed():
   ...     print("Simulation completed successfully")
   ... else:
   ...     print("Simulation failed or was aborted")



Attributes
----------

.. autoapisummary::

   src.pyedb.workflows.utilities.siwave_log_parser.RE_TS_DATE_FIRST
   src.pyedb.workflows.utilities.siwave_log_parser.RE_TS_TIME_FIRST
   src.pyedb.workflows.utilities.siwave_log_parser.parser


Classes
-------

.. autoapisummary::

   src.pyedb.workflows.utilities.siwave_log_parser.AEDTVersion
   src.pyedb.workflows.utilities.siwave_log_parser.BatchInfo
   src.pyedb.workflows.utilities.siwave_log_parser.SimSettings
   src.pyedb.workflows.utilities.siwave_log_parser.WarningEntry
   src.pyedb.workflows.utilities.siwave_log_parser.ProfileEntry
   src.pyedb.workflows.utilities.siwave_log_parser.BlockParser
   src.pyedb.workflows.utilities.siwave_log_parser.HeaderBlockParser
   src.pyedb.workflows.utilities.siwave_log_parser.BatchSettingsBlockParser
   src.pyedb.workflows.utilities.siwave_log_parser.WarningsBlockParser
   src.pyedb.workflows.utilities.siwave_log_parser.ProfileBlockParser
   src.pyedb.workflows.utilities.siwave_log_parser.ParsedSiwaveLog
   src.pyedb.workflows.utilities.siwave_log_parser.SiwaveLogParser


Module Contents
---------------

.. py:data:: RE_TS_DATE_FIRST

.. py:data:: RE_TS_TIME_FIRST

.. py:class:: AEDTVersion

   AEDT version information extracted from log header.

   Attributes
   ----------
   version : str
       AEDT version number (e.g., ``'2025.1'``).
   build : str
       Build identifier.
   location : str
       Installation path of AEDT.

   Examples
   --------
   >>> version = AEDTVersion(version="2025.1", build="12345", location="C:\Program Files\AnsysEM")
   >>> version.version
   '2025.1'


   .. py:attribute:: version
      :type:  str


   .. py:attribute:: build
      :type:  str


   .. py:attribute:: location
      :type:  str


.. py:class:: BatchInfo

   Batch simulation run metadata.

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
   ...     path="C:\project\design.siw",
   ...     started=datetime(2025, 11, 10, 9, 0, 0),
   ...     stopped=datetime(2025, 11, 10, 10, 30, 0),
   ...     run_by="engineer",
   ...     temp_dir="C:\temp",
   ...     project_dir="C:\project",
   ...     status="Normal Completion",
   ... )
   >>> batch.status
   'Normal Completion'


   .. py:attribute:: path
      :type:  str


   .. py:attribute:: started
      :type:  datetime.datetime


   .. py:attribute:: stopped
      :type:  datetime.datetime


   .. py:attribute:: run_by
      :type:  str


   .. py:attribute:: temp_dir
      :type:  str


   .. py:attribute:: project_dir
      :type:  str


   .. py:attribute:: status
      :type:  str
      :value: ''



.. py:class:: SimSettings

   Simulation settings and configuration.

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


   .. py:attribute:: design_type
      :type:  str


   .. py:attribute:: allow_off_core
      :type:  bool


   .. py:attribute:: manual_settings
      :type:  bool


   .. py:attribute:: two_level
      :type:  bool


   .. py:attribute:: distribution_types
      :type:  list[str]


   .. py:attribute:: machines
      :type:  list[str]


.. py:class:: WarningEntry

   Single warning message from the simulation log.

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


   .. py:attribute:: timestamp
      :type:  datetime.datetime


   .. py:attribute:: category
      :type:  str


   .. py:attribute:: net1
      :type:  str


   .. py:attribute:: net2
      :type:  str


   .. py:attribute:: layer
      :type:  str


   .. py:attribute:: x
      :type:  float


   .. py:attribute:: y
      :type:  float


   .. py:attribute:: message
      :type:  str


.. py:class:: ProfileEntry

   Performance profile entry showing task timing and resource usage.

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


   .. py:attribute:: timestamp
      :type:  datetime.datetime


   .. py:attribute:: task
      :type:  str


   .. py:attribute:: real_time
      :type:  str | None
      :value: None



   .. py:attribute:: cpu_time
      :type:  str | None
      :value: None



   .. py:attribute:: memory
      :type:  str | None
      :value: None



   .. py:attribute:: extra
      :type:  dict[str, str]


.. py:class:: BlockParser(lines: list[str])

   Base class for a single block parser.

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


   .. py:attribute:: lines


   .. py:method:: parse() -> Any
      :abstractmethod:


      Parse the stored lines.

      Returns
      -------
      Any
          Parsed data structure.



.. py:class:: HeaderBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


   Extract AEDT version information from the log header.

   This parser searches through log lines to find version, build, and
   installation location information.

   Examples
   --------
   >>> lines = [
   ...     "ANSYS Electromagnetics Suite Version 2025.1 Build: 12345",
   ...     "Location: C:\Program Files\AnsysEM\v251",
   ... ]
   >>> parser = HeaderBlockParser(lines)
   >>> version = parser.parse()
   >>> version.version
   '2025.1'


   .. py:method:: parse() -> AEDTVersion

      Parse the stored lines and return an AEDTVersion instance.

      Returns
      -------
      AEDTVersion
          Populated version data object containing version, build, and location.

      Examples
      --------
      >>> lines = ["Version 2025.1 Build: 12345", "Location: C:\AnsysEM"]
      >>> parser = HeaderBlockParser(lines)
      >>> info = parser.parse()
      >>> info.build
      '12345'



.. py:class:: BatchSettingsBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


   Extract batch information and simulation settings from the log.

   This parser processes batch run metadata including timestamps, user info,
   directories, and simulation configuration settings.

   Examples
   --------
   >>> lines = [
   ...     "Batch Solve/Save: C:\project\design.siw",
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


   .. py:method:: parse() -> tuple[BatchInfo, SimSettings]

      Parse batch information and simulation settings.

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



.. py:class:: WarningsBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


   Extract warning entries from the simulation log.

   This parser identifies and extracts warning messages, particularly focusing
   on electrical short warnings with location information.

   Examples
   --------
   >>> lines = [
   ...     "11/10/2025 09:15:30 AM [warning] Geometry on nets VCC and GND on layer \"TOP\" "
   ...     "are electrically shorted at approximately (12.5, 34.8)mm"
   ... ]
   >>> parser = WarningsBlockParser(lines)
   >>> warnings = parser.parse()
   >>> warnings[0].category
   'SHORT'
   >>> warnings[0].net1
   'VCC'


   .. py:method:: parse() -> list[WarningEntry]

      Parse warning messages from log lines.

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



.. py:class:: ProfileBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


   Extract profile entries showing task timing and resource usage.

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


   .. py:method:: parse() -> list[ProfileEntry]

      Parse profile entries showing task timing and resource usage.

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



.. py:class:: ParsedSiwaveLog

   Root container returned by SiwaveLogParser.parse().

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
   ...     aedt=AEDTVersion(version="2025.1", build="123", location="C:\AEDT"),
   ...     batch=BatchInfo(
   ...         path="C:\project\test.siw",
   ...         started=datetime(2025, 11, 10, 9, 0, 0),
   ...         stopped=datetime(2025, 11, 10, 10, 0, 0),
   ...         run_by="engineer",
   ...         temp_dir="C:\temp",
   ...         project_dir="C:\project",
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


   .. py:attribute:: aedt
      :type:  AEDTVersion


   .. py:attribute:: batch
      :type:  BatchInfo


   .. py:attribute:: settings
      :type:  SimSettings


   .. py:attribute:: warnings
      :type:  list[WarningEntry]
      :value: []



   .. py:attribute:: profile
      :type:  list[ProfileEntry]
      :value: []



   .. py:method:: summary() -> None

      Print a summary of the parsed log to stdout.

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



   .. py:method:: is_completed() -> bool

      Check if the simulation completed normally.

      Returns
      -------
      bool
          ``True`` if status is ``'Normal Completion'``, ``False`` otherwise.

      Examples
      --------
      >>> log = ParsedSiwaveLog(
      ...     aedt=AEDTVersion("2025.1", "123", "C:\AEDT"),
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



   .. py:method:: is_aborted() -> bool

      Check if the simulation was aborted.

      Returns
      -------
      bool
          ``True`` if simulation did not complete normally, ``False`` otherwise.

      Examples
      --------
      >>> log = ParsedSiwaveLog(
      ...     aedt=AEDTVersion("2025.1", "123", "C:\AEDT"),
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



   .. py:method:: to_json(fp: str, **kw) -> None

      Serialize parsed log to JSON file.

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



   .. py:method:: to_dict() -> dict

      Deep-convert the entire object to JSON-serializable primitives.

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



.. py:class:: SiwaveLogParser(log_path: str | pathlib.Path)

   High-level parser that orchestrates all block parsers.

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


   .. py:attribute:: BLOCK_MAP
      :type:  dict[str, type[BlockParser]]


   .. py:attribute:: path


   .. py:method:: parse() -> ParsedSiwaveLog

      Execute all sub-parsers and return a unified object.

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



.. py:data:: parser

