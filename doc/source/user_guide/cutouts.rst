.. _cutouts:

Cutouts
=========

Build a cutout around a set of signal nets and their reference net, to reduce simulation size while
preserving the electrical behavior around the nets of interest.

Prerequisites
-------------

- An open ``Edb`` instance with signal and reference nets already defined (see
  :doc:`components_and_nets`).

Public API entry points
-------------------------

- :meth:`Edb.cutout <pyedb.grpc.edb.Edb.cutout>` — the high-level convenience method.
- :class:`pyedb.workflows.utilities.cutout.Cutout` — the lower-level class that ``Edb.cutout``
  delegates to; use it directly only if you need the ``smart_cutout`` option, which ``Edb.cutout``
  does not expose.

Procedure
---------

1. Identify the signal nets to keep and their reference net (commonly ``"GND"``).

   .. code-block:: python

      signal_nets = ["DDR4_DQS0_P", "DDR4_DQS0_N"]
      reference_nets = ["GND"]

2. Run the cutout, writing the result to a **new** AEDB path so the original design is preserved.

   .. code-block:: python

      output_path = "cutout_output.aedb"
      extent = edb.cutout(
          signal_nets=signal_nets,
          reference_nets=reference_nets,
          output_aedb_path=output_path,
          open_cutout_at_end=False,
      )

3. Check whether the cutout succeeded before using the result.

   .. code-block:: python

      if extent:
          print("Cutout extent points:", extent)
      else:
          print("Cutout failed or produced an empty extent.")

Complete example
-----------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   input_path = str(Path(tempfile.gettempdir()) / "cutout_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   output_path = str(Path(tempfile.gettempdir()) / "cutout_output.aedb")
   extent = edb.cutout(
       signal_nets=["DDR4_DQS0_P", "DDR4_DQS0_N"],
       reference_nets=["GND"],
       output_aedb_path=output_path,
       open_cutout_at_end=False,
   )
   print("Cutout result:", extent)

   edb.close()

Expected result
----------------

On success, ``edb.cutout(...)`` returns a list of coordinate points describing the clipping extent
polygon, and a new AEDB is written to ``output_aedb_path``; the original ``input_path`` database is
not modified (the original ``edb`` object continues pointing at ``input_path`` when
``open_cutout_at_end=False``). On failure the method can return either an empty list or ``False``
depending on which internal stage failed — always check truthiness (``if extent:``) rather than
assuming a specific empty-collection type.

Backend and version notes
---------------------------

- ``Edb.cutout`` dispatches internally to a gRPC- or DotNet-specific implementation based on the
  active backend; the public method name and parameters are identical on both.
- ``output_aedb_path=None`` (the default) cuts out the **current** database in place, overwriting
  the live in-memory design (and, if you subsequently call ``edb.save()``, the file on disk). Always
  pass an explicit ``output_aedb_path`` in introductory or exploratory scripts to avoid modifying an
  input design you want to keep.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - Cutout silently modified the original design
     - ``output_aedb_path`` was left as ``None``.
     - Always pass an explicit new path when you want to preserve the original database.
   * - ``TypeError`` calling ``len()`` on the cutout result
     - The cutout failed after exhausting ``maximum_iterations`` and returned ``False`` (a bool, not
       a list).
     - Check truthiness first: ``if not extent: # handle failure`` before calling ``len(extent)``.
   * - Cutout is too tight and clips traces needed for port references
     - The extent was computed without accounting for component models attached to nets.
     - Set ``check_terminals=True`` (and ``include_pingroups=True`` if using pin groups) so the
       extent expands to include reference terminals.

See also
--------

- :doc:`../workflows/utilities/cutout` — implementation-level reference for the ``Cutout`` class,
  including the ``smart_cutout`` option not exposed by ``Edb.cutout``.
- :doc:`components_and_nets` — finding the signal and reference net names to pass in.
