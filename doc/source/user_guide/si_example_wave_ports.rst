.. _si_example_wave_ports:

SI example: prepare a high-speed differential channel for HFSS 3D Layout
==========================================================================

A complete, step-by-step signal-integrity (SI) workflow: open a board, find a high-speed
differential pair, build ports on it, add an HFSS 3D Layout setup, and validate everything is
ready for simulation — all using license-free layout preparation (no solver run required).

What you will learn
--------------------

- How to classify nets and locate a high-speed differential pair by name.
- How to create ports on a differential pair using the recommended net-level API.
- How to add an HFSS 3D Layout setup with a frequency sweep.
- How to validate that the model is simulation-ready **before** spending solver license time.

When to use this workflow
----------------------------

Use this workflow when you need to extract S-parameters for a high-speed serial or parallel bus
(USB, PCIe, DDR, SerDes) from a PCB or package layout, and you want to prepare and validate the
model programmatically instead of manually clicking through HFSS 3D Layout.

Prerequisites
-------------

- An open ``Edb`` instance pointing at a design that contains a differential pair (see
  :doc:`../getting_started/quick_start` for how to open an existing design; a freshly created,
  empty database has no nets to work with).
- Familiarity with :doc:`components_and_nets` (net lookup) and :doc:`ports_and_sources` (port
  creation fundamentals).

Software and license requirements
-------------------------------------

- A licensed local AEDT installation, release 2026.1 or later for the default gRPC backend (see
  :doc:`../getting_started/backend_compatibility_migration`).
- Everything in this example — net classification, port creation, and HFSS setup creation — is
  **license-free layout preparation**. No SI/HFSS solver license is consumed until you actually
  run the solve, which is intentionally **not** part of this example. See
  :doc:`../getting_started/object_model` for the PyEDB/PyAEDT boundary: PyEDB prepares the model,
  PyAEDT (or the AEDT GUI) drives the solve.

Input design and provenance
-------------------------------

This example assumes a board with a differential pair following a ``<NAME>_P`` / ``<NAME>_N``
naming convention (for example ``USB3_D_P`` / ``USB3_D_N``, or ``DDR4_DQS0_P`` /
``DDR4_DQS0_N``), a reference net named ``"GND"``, and a component (for example ``"U1"``) with
pins on both differential nets. Substitute your own net and component names; the pattern is the
same regardless of the bus.

API concepts introduced
---------------------------

- :meth:`DifferentialPairs.auto_identify <pyedb.grpc.database.net.differential_pair.
  DifferentialPairs.auto_identify>` — detect ``_P``/``_N`` net pairs automatically.
- :meth:`SourceExcitation.create_circuit_port_on_net <pyedb.grpc.database.source_excitations.
  SourceExcitation.create_circuit_port_on_net>` — create a port directly from component + net
  names, without manually building terminal objects (the recommended entry point for most SI
  port-creation tasks; contrast with the lower-level ``create_port`` pattern in
  :doc:`ports_and_sources`).
- :meth:`SimulationSetups.create_hfss_setup <pyedb.grpc.database.simulation_setups.
  SimulationSetups.create_hfss_setup>` — add an HFSS 3D Layout analysis setup with a frequency
  sweep.

Complete executable example
--------------------------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # --- 1. Define inputs -------------------------------------------------------------
   # Replace with the path to your own design; this example assumes it already contains
   # a differential pair and a "GND" reference net.
   source_path = "my_high_speed_board.aedb"
   positive_net = "USB3_D_P"
   negative_net = "USB3_D_N"
   component = "U1"
   reference_net = "GND"

   # --- 2. Create a working copy (never edit the source design in place) --------------
   import shutil

   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_si_example_"))
   working_copy = work_dir / "board_copy.aedb"
   shutil.copytree(source_path, working_copy)

   # --- 3. Open the database -----------------------------------------------------------
   edb = Edb(edbpath=str(working_copy), version="2026.1")

   # --- 4. Inspect: confirm the expected nets exist before doing anything else ---------
   for net_name in (positive_net, negative_net, reference_net):
       assert net_name in edb.nets.netlist, f"Net {net_name!r} not found in this design"
   assert component in edb.components.instances, f"Component {component!r} not found"

   # --- 5. Classify nets: make sure the reference net is recognized as power/ground ----
   edb.nets.classify_nets(
       power_nets=[reference_net], signal_nets=[positive_net, negative_net]
   )
   assert edb.nets.is_power_gound_net(
       [reference_net]
   ), f"{reference_net!r} was not classified as power/ground"

   # --- 6. Auto-identify (or explicitly create) the differential pair ------------------
   identified_pairs = edb.differential_pairs.auto_identify()
   pair_name = f"DIFF_{positive_net.removesuffix('_P')}"
   if pair_name not in edb.differential_pairs.items:
       edb.differential_pairs.create(
           name=pair_name, net_p=positive_net, net_n=negative_net
       )
   assert pair_name in edb.differential_pairs.items, "Differential pair was not created"

   # --- 7. Create a circuit port on each leg of the differential pair ------------------
   # create_circuit_port_on_net groups all pins on the net into a pin group and creates the
   # port directly from component + net names -- no manual terminal construction needed.
   port_p = edb.excitation_manager.create_circuit_port_on_net(
       positive_component_name=component,
       positive_net_name=positive_net,
       negative_component_name=component,
       negative_net_name=reference_net,
       impedance_value=50,
       port_name=f"Port_{positive_net}",
   )
   port_n = edb.excitation_manager.create_circuit_port_on_net(
       positive_component_name=component,
       positive_net_name=negative_net,
       negative_component_name=component,
       negative_net_name=reference_net,
       impedance_value=50,
       port_name=f"Port_{negative_net}",
   )

   # --- 8. Validate the in-memory result: both ports must exist before saving ---------
   assert port_p and port_p in edb.ports, f"Port on {positive_net!r} was not created"
   assert port_n and port_n in edb.ports, f"Port on {negative_net!r} was not created"
   print(f"Created {len(edb.ports)} port(s): {list(edb.ports.keys())}")

   # --- 9. Add an HFSS 3D Layout setup with a frequency sweep -------------------------
   hfss_setup = edb.simulation_setups.create_hfss_setup(
       name="HFSS_SI_Setup", start_freq="0Hz", stop_freq="20GHz", step_freq="0.05GHz"
   )
   assert "HFSS_SI_Setup" in edb.setups, "HFSS setup was not created"

   # --- 10. Save the database (never overwrite the source design) --------------------
   output_path = str(Path(tempfile.gettempdir()) / "si_example_output.aedb")
   edb.save_as(output_path)

   # --- 11. Close resources -------------------------------------------------------------
   edb.close()

   # --- 12. Reopen and verify persistence ------------------------------------------------
   edb_reopened = Edb(edbpath=output_path, version="2026.1")
   assert port_p in edb_reopened.ports, "Port did not persist after save_as + reopen"
   assert port_n in edb_reopened.ports, "Port did not persist after save_as + reopen"
   assert (
       "HFSS_SI_Setup" in edb_reopened.setups
   ), "HFSS setup did not persist after save_as + reopen"
   print("Verified: ports and HFSS setup persisted after reopening.")
   edb_reopened.close()

   print(
       f"SI model preparation complete. Ready for solve at {output_path} (not run in this example)."
   )

Expected output
-------------------

.. code-block:: console

   Created 2 port(s): ['Port_USB3_D_P', 'Port_USB3_D_N']
   Verified: ports and HFSS setup persisted after reopening.
   SI model preparation complete. Ready for solve at /tmp/si_example_output.aedb (not run in this example).

Deterministic verification
-------------------------------

Every step that changes the database is followed by an ``assert`` that checks a concrete,
enumerable fact (net membership, port presence in ``edb.ports``, setup presence in
``edb.setups``) rather than the absence of an exception. The final block reopens the saved
database independently and re-checks the same facts, confirming persistence rather than assuming
``save_as`` succeeded.

Common failures and diagnostics
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``AssertionError`` at step 4 (net not found)
     - The net names in this example do not match your design's actual naming convention.
     - List actual net names first: ``print(edb.nets.netlist)``, and substitute the correct
       ``_P``/``_N`` pair and reference net name.
   * - ``create_circuit_port_on_net(...)`` returns ``False``
     - No pins were found for the requested component/net combination — the component name does
       not exist, or has no pins on that net.
     - Verify with ``edb.components.get_pin_from_component(component, net_name)`` first; an empty
       list means the port cannot be created with these arguments.
   * - ``auto_identify()`` returns an empty list
     - Net names do not end with the default ``"_P"``/``"_N"`` suffixes.
     - Pass explicit suffixes: ``edb.differential_pairs.auto_identify(positive_differentiator="_p", negative_differentiator="_n")``,
       or skip auto-identification and call ``edb.differential_pairs.create(...)`` directly as shown
       in step 6.
   * - HFSS setup name already exists
     - ``create_hfss_setup`` (via ``SimulationSetups.create``) returns ``None`` if a setup with the
       same name already exists on the cell.
     - Choose a unique setup name, or look up and edit the existing setup via
       ``edb.setups["HFSS_SI_Setup"]``.

Cleanup
-----------

Both ``edb`` sessions are explicitly closed above. Remove the temporary working directory
(``work_dir``) once you are done inspecting the output, for example with
``shutil.rmtree(work_dir, ignore_errors=True)``.

Next recommended example
-----------------------------

- :doc:`../user_guide/cutouts` — reduce the model to just the region around this differential pair
  before solving, to cut simulation time.
- PI example: :doc:`pi_example_power_aware_dcir` — the equivalent step-by-step workflow for a
  power-integrity DCIR analysis.

Related conceptual pages
-----------------------------

- :doc:`../getting_started/object_model` — the ``edb.excitation_manager`` and
  ``edb.simulation_setups`` sections.
- :doc:`ports_and_sources` — the full terminal/port/source concept reference, including the
  lower-level ``create_port`` pattern this example's higher-level ``create_circuit_port_on_net``
  wraps.

Related API-reference pages
--------------------------------

- :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`
- :class:`DifferentialPairs <pyedb.grpc.database.net.differential_pair.DifferentialPairs>`
- :class:`SimulationSetups <pyedb.grpc.database.simulation_setups.SimulationSetups>`

Version compatibility notes
--------------------------------

- ``create_circuit_port_on_net``, ``classify_nets``, and ``auto_identify`` are available on both
  the gRPC and DotNet backends with the same signatures.
- This example targets the gRPC backend (``version="2026.1"`` or later). For the deprecated
  DotNet backend, pass ``grpc=False`` and install ``pyedb[dotnet]``; the method calls themselves
  are unchanged.
