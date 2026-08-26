.. _parse_siwave_log_example:

Parse and audit a SIwave batch log
==================================

This example parses a stored SIwave batch log without launching AEDT. It checks
completion status, reports warnings and profiling information, and writes a
structured JSON summary suitable for CI artifacts.

Learning objectives
-------------------

* Parse a SIwave log into structured result objects.
* Detect normal completion, failure, or abortion.
* Inspect warning categories and important messages.
* Review profiling and timing entries.
* Export the parsed result to JSON.
* Return a failing process status for an unsuccessful batch run.

Test fixtures
-------------

Store small, sanitized text fixtures with the tests:

.. code-block:: text

   tests/system_examples/data/siwave/
   |-- normal_completion.log
   `-- aborted_run.log

The fixtures must not contain user names, machine names, confidential project
paths, or proprietary layout data.

Run the example
---------------

.. literalinclude:: ../../../../../tests/system_examples/utilities/parse_siwave_log.py
   :language: python
   :linenos:
   :caption: parse_siwave_log.py

Expected output
---------------

.. code-block:: text

   <output_directory>/siwave_run.json

Validation checks
-----------------

Verify that:

* The normal fixture is reported as completed.
* The aborted fixture is reported as unsuccessful.
* Version and batch metadata are extracted.
* Expected warnings are found.
* Profiling entries are available when present in the log.
* The exported JSON is valid and contains the completion status.
* The command returns a nonzero status for an unsuccessful run.

Run in CI
---------

This example does not require an AEDT or solver license. Run it in the ordinary
unit or documentation CI job using checked-in log fixtures.

Related APIs
------------

* :class:`pyedb.workflows.utilities.siwave_log_parser.SiwaveLogParser`
* :class:`pyedb.workflows.utilities.siwave_log_parser.ParsedSiwaveLog`
