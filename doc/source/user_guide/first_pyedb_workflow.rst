.. _first_pyedb_workflow:

Your first PyEDB workflow, explained step by step
=====================================================

A narrative, beginner-oriented walkthrough that explains not just *what* to type but *why* each
step exists. If you already completed :doc:`../getting_started/quick_start`, this page goes one
level deeper: it opens a **real** design instead of an empty one, and explains the reasoning behind
every decision (why a copy, why ``save_as``, why check before you query) so you can generalize the
pattern to your own scripts.

Who this is for
-------------------

Someone who has never automated EDB before, whether from a PCB/package design background with
limited Python experience, or a Python background with limited EDB experience. If you already know
the PyEDB object model well, skip to :doc:`../getting_started/object_model` and the task-oriented
pages in this user guide instead.

The five stages of any PyEDB script
----------------------------------------

Every PyEDB automation script — no matter how simple or advanced — follows the same five stages.
Internalizing this shape is more valuable than memorizing any single method name:

1. **Locate your input.** Know exactly which ``.aedb`` folder you are about to open, and never plan
   to write your changes back into it directly.
2. **Open safely.** Open a *copy*, and verify the open actually succeeded before doing anything
   else.
3. **Ask questions before making changes.** Inspect the design (layers, nets, components) so your
   script's assumptions ("this net exists", "this component has 4 pins") are verified facts, not
   guesses.
4. **Change one thing at a time, and check it.** Make a deliberate modification, then immediately
   verify the in-memory result before moving on.
5. **Save, close, and prove it stuck.** Save to a new location, close the session, then reopen and
   re-check — because "the script didn't crash" is not the same as "the change is on disk."

The rest of this page walks through these five stages with a single, complete, runnable script.

Stage 1 — Locate your input
--------------------------------

An EDB design is a folder ending in ``.aedb`` (for example ``my_board.aedb``), not a single file.
Before writing any PyEDB code, find that folder and treat it as **read-only** for the rest of this
workflow.

.. code-block:: python

   from pathlib import Path

   source_path = Path("my_board.aedb")
   assert (
       source_path.exists() and source_path.is_dir()
   ), f"Expected an .aedb folder at {source_path}"

Why an assertion here, before you have even imported ``Edb``? Because every failure that happens
*later* in a script (a confusing gRPC error three steps down) is harder to diagnose than one clear
message at the very first line: "the input you gave me does not exist."

Stage 2 — Open safely
--------------------------

Never open the source folder directly if you plan to make any change. Copy it first, and open the
copy. This single habit eliminates the most common PyEDB support question: "I ran a script and now
my only copy of the board is different from what I expected."

.. code-block:: python

   import shutil
   import tempfile

   from pyedb import Edb

   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_first_workflow_"))
   working_copy = work_dir / source_path.name
   shutil.copytree(source_path, working_copy)

   edb = Edb(edbpath=str(working_copy), version="2026.1")

   # Verify the open actually succeeded before trusting anything else in this session.
   assert edb.active_cell is not None, "Edb() did not raise, but no active cell was found"
   print(f"Opened {working_copy.name}. Active cell: {edb.active_cell}")

If ``Edb(...)`` raises here, see the "Common problems" table on :doc:`../getting_started/quick_start`
— the most frequent causes are a missing/mismatched AEDT installation or an unsupported ``version``.

Stage 3 — Ask questions before making changes
--------------------------------------------------

Before modifying anything, build a small mental map of the design by asking concrete questions and
printing the answers. This is the step most tutorials skip, and the one that saves the most time in
practice.

.. code-block:: python

   # "How big is this design, roughly?"
   print(f"{len(edb.stackup.layers)} stackup layers")
   print(f"{len(edb.nets.netlist)} nets")
   print(f"{len(edb.components.instances)} components")

   # "Which layers are signal versus dielectric?"
   signal_layer_names = list(edb.stackup.signal_layers.keys())
   print(f"Signal layers: {signal_layer_names}")

   # "Does the net I'm about to work with actually exist?"
   target_net = "GND"
   if target_net in edb.nets.netlist:
       print(f"Net {target_net!r} found.")
   else:
       print(
           f"Net {target_net!r} NOT found. Available nets (first 10): {edb.nets.netlist[:10]}"
       )

This "check first, act second" pattern — used throughout every page in this user guide — turns "my
script raised a ``KeyError`` and I don't know why" into "my script printed the ten closest available
names and I fixed my typo in five seconds."

Stage 4 — Change one thing at a time, and check it
--------------------------------------------------------

Pick exactly one, well-defined modification. Here, we rename a net (a common, low-risk first
modification) — but the pattern (mutate, then assert) generalizes to any change described elsewhere
in this user guide (:doc:`stackup_and_materials`, :doc:`ports_and_sources`, and so on).

.. code-block:: python

   if edb.nets.netlist:
       old_name = edb.nets.netlist[0]
       new_name = f"{old_name}_RENAMED"

       edb.nets[old_name].name = new_name

       # Check the in-memory result immediately -- do not wait until after saving to find out
       # whether the rename actually took effect.
       assert new_name in edb.nets.netlist, "Rename did not take effect in memory"
       assert (
           old_name not in edb.nets.netlist
       ), "Old net name is still present after rename"
       print(f"Renamed net {old_name!r} to {new_name!r}.")
   else:
       print("This design has no nets; skipping the rename step.")

Stage 5 — Save, close, and prove it stuck
-----------------------------------------------

Saving to a **new** path (``save_as``) keeps your working copy — and, transitively, the original
source design — untouched. Then, crucially, reopen the saved output in a fresh session and check
the same fact you just changed. This is the step every beginner example in this user guide now
includes, and the step that turns "I assume it worked" into "I know it worked."

.. code-block:: python

   output_path = str(work_dir / "board_output.aedb")
   edb.save_as(output_path)
   edb.close()

   edb_reopened = Edb(edbpath=output_path, version="2026.1")
   assert new_name in edb_reopened.nets.netlist, "Renamed net did not persist after reopen"
   print(f"Verified: {new_name!r} persisted after save_as + reopen.")
   edb_reopened.close()

   print(f"Workflow complete. Output saved at {output_path}.")

Putting it all together
----------------------------

The complete, runnable script combining all five stages:

.. code-block:: python
   :caption: first_pyedb_workflow.py

   import shutil
   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # Stage 1: locate your input.
   source_path = Path("my_board.aedb")
   assert (
       source_path.exists() and source_path.is_dir()
   ), f"Expected an .aedb folder at {source_path}"

   # Stage 2: open safely (copy first, then open, then verify).
   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_first_workflow_"))
   working_copy = work_dir / source_path.name
   shutil.copytree(source_path, working_copy)
   edb = Edb(edbpath=str(working_copy), version="2026.1")
   assert edb.active_cell is not None, "Edb() did not raise, but no active cell was found"
   print(f"Opened {working_copy.name}. Active cell: {edb.active_cell}")

   # Stage 3: ask questions before making changes.
   print(
       f"{len(edb.stackup.layers)} stackup layers, {len(edb.nets.netlist)} nets, "
       f"{len(edb.components.instances)} components"
   )

   # Stage 4: change one thing at a time, and check it.
   renamed_from = renamed_to = None
   if edb.nets.netlist:
       renamed_from = edb.nets.netlist[0]
       renamed_to = f"{renamed_from}_RENAMED"
       edb.nets[renamed_from].name = renamed_to
       assert renamed_to in edb.nets.netlist, "Rename did not take effect in memory"
       print(f"Renamed net {renamed_from!r} to {renamed_to!r}.")

   # Stage 5: save, close, and prove it stuck.
   output_path = str(work_dir / "board_output.aedb")
   edb.save_as(output_path)
   edb.close()

   edb_reopened = Edb(edbpath=output_path, version="2026.1")
   if renamed_to is not None:
       assert (
           renamed_to in edb_reopened.nets.netlist
       ), "Renamed net did not persist after reopen"
       print(f"Verified: {renamed_to!r} persisted after save_as + reopen.")
   edb_reopened.close()

   print(f"Workflow complete. Output saved at {output_path}.")

Expected output
-------------------

.. code-block:: console

   Opened my_board.aedb. Active cell: <ansys.edb.core.layout.cell.Cell object at 0x...>
   12 stackup layers, 187 nets, 42 components
   Renamed net 'GND' to 'GND_RENAMED'.
   Verified: 'GND_RENAMED' persisted after save_as + reopen.
   Workflow complete. Output saved at /tmp/.../board_output.aedb

Common errors
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``AssertionError`` at Stage 1
     - ``source_path`` does not point at a real ``.aedb`` folder.
     - Double-check the path; remember an EDB "file" is actually a folder.
   * - Script hangs or raises a gRPC connection error at Stage 2
     - AEDT/``ansys-edb-core`` is not installed, or the requested ``version`` is not installed.
     - See the "Common problems" table on :doc:`../getting_started/quick_start`.
   * - ``KeyError`` at Stage 4 when looking up a net or component by name
     - The exact name differs from what you expect (case, whitespace, or the name simply does not
       exist in this design).
     - This is exactly why Stage 3 exists — always print and check available names before assuming
       one exists.

Cleanup
-----------

Both ``edb`` sessions are explicitly closed above. Remove ``work_dir`` when you are done inspecting
the output, for example with ``shutil.rmtree(work_dir, ignore_errors=True)``.

Next steps
--------------

- :doc:`../getting_started/object_model` — learn the full navigation map of what ``Edb`` exposes,
  now that you have seen the five-stage pattern applied once.
- :doc:`design_inventory_report` — a richer version of Stage 3 that produces a complete,
  machine-readable design snapshot.
- :doc:`components_and_nets`, :doc:`stackup_and_materials`, :doc:`geometry_and_connectivity`,
  :doc:`ports_and_sources` — the same five-stage pattern applied to every other PyEDB domain.
- :doc:`si_example_wave_ports` and :doc:`pi_example_power_aware_dcir` — complete, industry-specific
  workflows that build on this same pattern.
