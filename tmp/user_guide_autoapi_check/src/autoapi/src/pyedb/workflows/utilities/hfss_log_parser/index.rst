src.pyedb.workflows.utilities.hfss_log_parser
=============================================

.. py:module:: src.pyedb.workflows.utilities.hfss_log_parser

.. autoapi-nested-parse::

   HFSS log file parser for extracting simulation results and metrics.



Classes
-------

.. autoapisummary::

   src.pyedb.workflows.utilities.hfss_log_parser.ProjectInfo
   src.pyedb.workflows.utilities.hfss_log_parser.InitMesh
   src.pyedb.workflows.utilities.hfss_log_parser.AdaptivePass
   src.pyedb.workflows.utilities.hfss_log_parser.Sweep
   src.pyedb.workflows.utilities.hfss_log_parser.BlockParser
   src.pyedb.workflows.utilities.hfss_log_parser.ProjectBlockParser
   src.pyedb.workflows.utilities.hfss_log_parser.InitMeshBlockParser
   src.pyedb.workflows.utilities.hfss_log_parser.AdaptiveBlockParser
   src.pyedb.workflows.utilities.hfss_log_parser.SweepBlockParser
   src.pyedb.workflows.utilities.hfss_log_parser.HFSSLogParser
   src.pyedb.workflows.utilities.hfss_log_parser.ParsedLog


Module Contents
---------------

.. py:class:: ProjectInfo

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


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: file
      :type:  pathlib.Path


   .. py:attribute:: design
      :type:  str
      :value: ''



   .. py:attribute:: user
      :type:  str
      :value: ''



   .. py:attribute:: cmd_line
      :type:  str
      :value: ''



.. py:class:: InitMesh

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


   .. py:attribute:: tetrahedra
      :type:  int


   .. py:attribute:: memory_mb
      :type:  float


   .. py:attribute:: real_time_sec
      :type:  int


   .. py:attribute:: cpu_time_sec
      :type:  int


.. py:class:: AdaptivePass

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


   .. py:attribute:: pass_nr
      :type:  int


   .. py:attribute:: freq_hz
      :type:  float


   .. py:attribute:: tetrahedra
      :type:  int


   .. py:attribute:: matrix_size
      :type:  int


   .. py:attribute:: memory_mb
      :type:  float


   .. py:attribute:: delta_s
      :type:  Optional[float]


   .. py:attribute:: converged
      :type:  bool


   .. py:attribute:: elapsed_sec
      :type:  int


.. py:class:: Sweep

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


   .. py:attribute:: type
      :type:  str


   .. py:attribute:: frequencies
      :type:  int


   .. py:attribute:: solved
      :type:  list[float]


   .. py:attribute:: elapsed_sec
      :type:  int


.. py:class:: BlockParser(lines: list[str])

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


   .. py:attribute:: lines


   .. py:method:: parse() -> Any
      :abstractmethod:


      Parse the stored lines.

      Returns
      -------
      Any
          Parsed data structure.



.. py:class:: ProjectBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


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


   .. py:method:: parse() -> ProjectInfo

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



.. py:class:: InitMeshBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


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


   .. py:method:: parse() -> InitMesh

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



.. py:class:: AdaptiveBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


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


   .. py:method:: parse() -> list[AdaptivePass]

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



.. py:class:: SweepBlockParser(lines: list[str])

   Bases: :py:obj:`BlockParser`


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


   .. py:method:: parse() -> Optional[Sweep]

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



.. py:class:: HFSSLogParser(log_path: str | pathlib.Path)

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


   .. py:attribute:: BLOCK_MAP
      :type:  dict[str, type[BlockParser]]


   .. py:attribute:: path


   .. py:method:: parse() -> ParsedLog

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



.. py:class:: ParsedLog

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


   .. py:attribute:: project
      :type:  ProjectInfo


   .. py:attribute:: init_mesh
      :type:  InitMesh


   .. py:attribute:: adaptive
      :type:  list[AdaptivePass]


   .. py:attribute:: sweep
      :type:  Optional[Sweep]


   .. py:method:: to_dict() -> dict

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



   .. py:method:: is_converged() -> bool

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



   .. py:method:: adaptive_passes() -> list[AdaptivePass]

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



   .. py:method:: memory_on_convergence() -> float

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



   .. py:method:: is_completed() -> bool

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



   .. py:method:: errors() -> list[str]

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



