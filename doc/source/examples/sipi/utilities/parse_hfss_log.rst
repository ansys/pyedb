.. _parse_hfss_log_example:

Parse and audit an HFSS solver log
==================================

This example parses a stored HFSS solver log without launching AEDT. It checks
completion and convergence, reports solver errors, reviews initial and adaptive
mesh statistics, and exports a structured JSON summary suitable for CI
artifacts.

Learning objectives
-------------------

* Parse an HFSS log into structured result objects.
* Distinguish solver completion from adaptive convergence.
* Inspect the initial mesh and every adaptive pass.
* Track tetrahedra, matrix size, memory, elapsed time, and delta-S values.
* Inspect frequency-sweep information when present.
* Extract error lines from an unsuccessful run.
* Export a JSON-serializable result for CI and regression analysis.

Test fixtures
-------------

Store small, sanitized text fixtures with the tests:

.. code-block:: text

   tests/system_examples/data/hfss/
   |-- converged_run.log
   |-- unconverged_run.log
   `-- failed_run.log

The fixtures must not contain user names, machine names, confidential project
paths, or proprietary layout data.

Run the example
---------------

.. literalinclude:: ../../../../../tests/system_examples/utilities/parse_hfss_log.py
   :language: python
   :linenos:
   :caption: parse_hfss_log.py

Expected output
---------------

.. code-block:: text

   <output_directory>/hfss_run.json

The JSON artifact should contain the project information, initial mesh,
adaptive passes, optional sweep data, completion status, convergence status,
and extracted errors.

Validation checks
-----------------

Verify that:

* The converged fixture is reported as completed and converged.
* The unconverged fixture can be completed without being reported as converged.
* The failed fixture exposes the expected error lines.
* The initial tetrahedra, memory, and timing values match the fixture.
* Adaptive passes remain in chronological order.
* The final converged pass reports the expected delta-S and memory values.
* Sweep data is present only when the log contains a sweep summary.
* The exported dictionary is JSON serializable.
* The command returns a nonzero status for a failed or incomplete run.

Completion and convergence
--------------------------

Treat completion and convergence as separate checks:

* ``is_completed()`` indicates whether the solver run completed successfully.
* ``is_converged()`` indicates whether at least one adaptive pass declared
  convergence.
* ``errors()`` returns solver error lines and ignores warnings.

A completed solve is not necessarily converged. Likewise, a converged adaptive
section does not replace project-level checks of ports, setup, sweep, and model
fidelity.

Use in CI
---------

This example does not require an AEDT or solver license. Run it in ordinary
unit or documentation CI with checked-in log fixtures. Persist the JSON summary
as a CI artifact so mesh growth, convergence, memory, and runtime can be
compared across changes.

A useful regression policy can check:

* Completion and convergence status.
* Number of adaptive passes.
* Final delta-S.
* Tetrahedra and matrix-size growth.
* Memory on convergence.
* Initial-mesh and adaptive-pass elapsed time.
* Presence of solver errors.

Avoid imposing universal regression thresholds in the generic example. Select
project-specific limits from representative baseline runs.

Related APIs
------------

* :class:`pyedb.workflows.utilities.hfss_log_parser.HFSSLogParser`
* :class:`pyedb.workflows.utilities.hfss_log_parser.ParsedLog`
* :class:`pyedb.workflows.utilities.hfss_log_parser.ProjectInfo`
* :class:`pyedb.workflows.utilities.hfss_log_parser.InitMesh`
* :class:`pyedb.workflows.utilities.hfss_log_parser.AdaptivePass`
* :class:`pyedb.workflows.utilities.hfss_log_parser.Sweep`
