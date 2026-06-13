.. _siwave_log_parser_api:

======================================================================
SIwave log parser -- ``pyedb.workflows.utilities.siwave_log_parser``
======================================================================

.. automodule:: pyedb.workflows.utilities.siwave_log_parser
   :no-members:
   :noindex:


Overview
--------

The SIwave log parser extracts structured data from Ansys SIwave batch solve logs,
including version information, batch execution metadata, simulation settings,
warnings, profiling data, and completion status.

**Key Features:**

- Automatic detection of simulation completion status (Normal Completion vs. Aborted)
- Extraction of electrical short warnings with precise coordinates
- Performance profiling data (timing, memory usage)
- Support for multiple timestamp formats
- JSON export capability


Quick start
-----------

Basic usage:

.. code-block:: python

   from pyedb.workflows.utilities.siwave_log_parser import SiwaveLogParser

   # Parse a SIwave log file
   parser = SiwaveLogParser("path/to/siwave.log")
   log = parser.parse()

   # Check simulation status
   if log.is_completed():
       print(f"✓ Simulation completed successfully")
   else:
       print(f"✗ Simulation failed or was aborted")

   # Display summary
   log.summary()

   # Export to JSON
   log.to_json("results.json", indent=2)


Top-level façade
----------------

.. autoclass:: SiwaveLogParser
   :members:
   :special-members: __init__
   :show-inheritance:


Aggregated result object
-------------------------

.. autoclass:: ParsedSiwaveLog
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Data containers
---------------

Version information
~~~~~~~~~~~~~~~~~~~

.. autoclass:: AEDTVersion
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Batch execution metadata
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: BatchInfo
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Simulation settings
~~~~~~~~~~~~~~~~~~~

.. autoclass:: SimSettings
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Warning entries
~~~~~~~~~~~~~~~

.. autoclass:: WarningEntry
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Profile entries
~~~~~~~~~~~~~~~

.. autoclass:: ProfileEntry
   :members:
   :exclude-members: __dataclass_fields__,__dataclass_params__,__post_init__
   :show-inheritance:


Block parsers (advanced usage)
-------------------------------

These parsers handle specific sections of the log file. Most users does not need
to use them directly, as they are orchestrated by :class:`SiwaveLogParser`.

.. autoclass:: HeaderBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. autoclass:: BatchSettingsBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. autoclass:: WarningsBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:

.. autoclass:: ProfileBlockParser
   :members:
   :special-members: __init__
   :show-inheritance:


Base class
~~~~~~~~~~

.. autoclass:: BlockParser
   :members:
   :special-members: __init__
   :show-inheritance:


Utility helpers
---------------

The functions below are private by convention (leading underscore) but are
exposed in the documentation for contributors and advanced users.

.. autofunction:: _parse_ts

.. autofunction:: _split_kv

.. autofunction:: _as_dict


Examples
--------

Check simulation completion status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyedb.workflows.utilities.siwave_log_parser import SiwaveLogParser

   parser = SiwaveLogParser("siwave.log")
   log = parser.parse()

   if log.is_completed():
       print("Status:", log.batch.status)
       print("Runtime:", log.batch.stopped - log.batch.started)
   else:
       print("Simulation was aborted or failed")


Extract warnings
~~~~~~~~~~~~~~~~

.. code-block:: python

   parser = SiwaveLogParser("siwave.log")
   log = parser.parse()

   # Get all electrical short warnings
   shorts = [w for w in log.warnings if w.category == "SHORT"]

   for warning in shorts:
       print(f"Short between {warning.net1} and {warning.net2}")
       print(f"  Layer: {warning.layer}")
       print(f"  Location: ({warning.x:.3f}, {warning.y:.3f}) mm")


Analyze performance
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   parser = SiwaveLogParser("siwave.log")
   log = parser.parse()

   # Display profiling information
   for entry in log.profile:
       print(f"Task: {entry.task}")
       print(f"  Real Time: {entry.real_time}")
       print(f"  CPU Time: {entry.cpu_time}")
       print(f"  Memory: {entry.memory}")


Batch processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   from pathlib import Path
   from pyedb.workflows.utilities.siwave_log_parser import SiwaveLogParser

   # Process multiple log files
   log_dir = Path("simulation_results")
   completed = []
   failed = []

   for log_file in log_dir.glob("**/*.log"):
       try:
           parser = SiwaveLogParser(log_file)
           log = parser.parse()

           if log.is_completed():
               completed.append(
                   {
                       "project": log.batch.path,
                       "warnings": len(log.warnings),
                       "runtime": (log.batch.stopped - log.batch.started).total_seconds(),
                   }
               )
           else:
               failed.append({"project": log.batch.path, "status": log.batch.status})
       except Exception as e:
           print(f"Failed to parse {log_file}: {e}")

   print(f"Completed: {len(completed)}, Failed: {len(failed)}")


Export to JSON
~~~~~~~~~~~~~~

.. code-block:: python

   parser = SiwaveLogParser("siwave.log")
   log = parser.parse()

   # Export with pretty formatting
   log.to_json("results.json", indent=2)

   # Convert to dictionary for further processing
   data = log.to_dict()


See also
--------

- :ref:`hfss_log_parser_api` - HFSS log parser with similar functionality
- :ref:`workflows_api` - Workflow utilities overview

