.. _pi_example_power_aware_dcir:

PI example: prepare a power-aware DCIR analysis
====================================================

A complete, step-by-step power-integrity (PI) workflow: open a board, classify power/ground nets,
check for DC shorts, create a DC voltage source and a DCIR simulation setup, and validate the
model is ready for a SIwave DCIR solve — all using license-free layout preparation.

What you will learn
--------------------

- How to classify power and ground nets explicitly, and verify the classification.
- How to run a pre-solve DC-short check so shorted nets are caught before consuming solver time.
- How to create a DC voltage source on a component/net pair using the recommended net-level API.
- How to create a SIwave DCIR simulation setup and reference the source in it.
- How to validate the model is simulation-ready without running the solver.

When to use this workflow
----------------------------

Use this workflow when you need to analyze IR drop, current density, or loop resistance on a power
delivery network (VRM to load, or a specific power rail) using SIwave DCIR, and you want a
repeatable, scriptable model-preparation step that runs identically across many board revisions.

Prerequisites
-------------

- An open ``Edb`` instance pointing at a design that contains a power net, a ground net, and a
  component that has pins on both (see :doc:`../getting_started/quick_start` for how to open an
  existing design).
- Familiarity with :doc:`components_and_nets` (net lookup and classification) and
  :doc:`validation_and_drc` (DC-short checking).

Software and license requirements
-------------------------------------

- A licensed local AEDT installation, release 2026.1 or later for the default gRPC backend.
- Everything in this example — net classification, DC-short checking, source creation, and DCIR
  setup creation — is **license-free layout preparation**. No SIwave solver license is consumed
  until the DCIR analysis is actually run, which is intentionally **not** part of this example.

Input design and provenance
-------------------------------

This example assumes a board with a power net (for example ``"VCC"`` or ``"1V0"``), a ground net
named ``"GND"``, and a component (for example ``"U1"``) with pins on both nets. Substitute your
own net and component names.

API concepts introduced
---------------------------

- :meth:`Nets.classify_nets <pyedb.grpc.database.nets.Nets.classify_nets>` — explicitly mark nets
  as power/ground versus signal.
- :meth:`LayoutValidation.dc_shorts <pyedb.grpc.database.layout_validation.LayoutValidation.
  dc_shorts>` — detect accidental shorts between nets before solving.
- :meth:`SourceExcitation.create_voltage_source_on_net <pyedb.grpc.database.source_excitations.
  SourceExcitation.create_voltage_source_on_net>` — create a DC voltage source directly from
  component + net names.
- :meth:`SimulationSetups.create_siwave_dcir_setup <pyedb.grpc.database.simulation_setups.
  SimulationSetups.create_siwave_dcir_setup>` — add a SIwave DCIR analysis setup.
- :meth:`SIWaveDCIRSimulationSettings.add_source_terminal_to_ground
  <pyedb.grpc.database.simulation_setup.siwave_dcir_settings.SIWaveDCIRSimulationSettings.
  add_source_terminal_to_ground>` — register which terminal of a source is treated as the DCIR
  reference (ground) node.

Complete executable example
--------------------------------

.. code-block:: python

   import shutil
   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # --- 1. Define inputs -------------------------------------------------------------
   # Replace with the path to your own design; this example assumes it already contains
   # a power net, a "GND" reference net, and a component with pins on both.
   source_path = "my_power_board.aedb"
   power_net = "VCC"
   ground_net = "GND"
   component = "U1"
   voltage = 3.3  # volts

   # --- 2. Create a working copy (never edit the source design in place) --------------
   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_pi_example_"))
   working_copy = work_dir / "board_copy.aedb"
   shutil.copytree(source_path, working_copy)

   # --- 3. Open the database -----------------------------------------------------------
   edb = Edb(edbpath=str(working_copy), version="2026.1")

   # --- 4. Inspect: confirm the expected nets and component exist ---------------------
   for net_name in (power_net, ground_net):
       assert net_name in edb.nets.netlist, f"Net {net_name!r} not found in this design"
   assert component in edb.components.instances, f"Component {component!r} not found"

   # --- 5. Classify power/ground nets explicitly and verify the classification --------
   edb.nets.classify_nets(power_nets=[power_net, ground_net])
   assert edb.nets.is_power_gound_net(
       [power_net]
   ), f"{power_net!r} was not classified as power/ground"
   assert edb.nets.is_power_gound_net(
       [ground_net]
   ), f"{ground_net!r} was not classified as power/ground"
   print("Power/ground nets:", list(edb.nets.power.keys()))

   # --- 6. Pre-solve validation: check for DC shorts before doing anything else --------
   shorts = edb.layout_validation.dc_shorts()
   assert not shorts, f"Found {len(shorts)} DC short(s) before source creation: {shorts}"
   print("No DC shorts found. Proceeding with source creation.")

   # --- 7. Create a DC voltage source between the power net and ground net ------------
   source_name = edb.excitation_manager.create_voltage_source_on_net(
       positive_component_name=component,
       positive_net_name=power_net,
       negative_component_name=component,
       negative_net_name=ground_net,
       voltage_value=voltage,
       source_name=f"VSRC_{component}_{power_net}",
   )

   # --- 8. Validate the in-memory result before proceeding -----------------------------
   assert source_name, f"Voltage source on {power_net!r} was not created"
   print(f"Created voltage source: {source_name}")

   # --- 9. Create a SIwave DCIR setup and reference the source as the ground terminal -
   dcir_setup = edb.simulation_setups.create_siwave_dcir_setup(name="DCIR_Setup")
   assert "DCIR_Setup" in edb.setups, "DCIR setup was not created"
   dcir_setup.settings.add_source_terminal_to_ground(source_name, 1)
   assert (
       source_name in dcir_setup.settings.source_terms_to_ground
   ), "Source was not registered as a DCIR ground reference"

   # --- 10. Post-solve-independent validation: re-check for DC shorts after source ----
   #         creation, since adding a source can occasionally reveal a modeling issue.
   shorts_after = edb.layout_validation.dc_shorts()
   assert (
       not shorts_after
   ), f"Found {len(shorts_after)} DC short(s) after source creation: {shorts_after}"

   # --- 11. Save the database (never overwrite the source design) --------------------
   output_path = str(Path(tempfile.gettempdir()) / "pi_example_output.aedb")
   edb.save_as(output_path)

   # --- 12. Close resources -------------------------------------------------------------
   edb.close()

   # --- 13. Reopen and verify persistence ------------------------------------------------
   edb_reopened = Edb(edbpath=output_path, version="2026.1")
   assert (
       "DCIR_Setup" in edb_reopened.setups
   ), "DCIR setup did not persist after save_as + reopen"
   assert edb_reopened.nets.is_power_gound_net(
       [power_net]
   ), "Net classification did not persist"
   print("Verified: DCIR setup and net classification persisted after reopening.")
   edb_reopened.close()

   print(
       f"PI model preparation complete. Ready for DCIR solve at {output_path} (not run here)."
   )

Expected output
-------------------

.. code-block:: console

   Power/ground nets: ['VCC', 'GND']
   No DC shorts found. Proceeding with source creation.
   Created voltage source: VSRC_U1_VCC
   Verified: DCIR setup and net classification persisted after reopening.
   PI model preparation complete. Ready for DCIR solve at /tmp/pi_example_output.aedb (not run here).

Deterministic verification
-------------------------------

Two DC-short checks bracket the source-creation step (before and after), so a regression
introduced by the source itself is caught immediately rather than surfacing later as a confusing
solver error. Net classification, source creation, and DCIR setup creation are each verified with
an explicit membership check (``is_power_gound_net``, truthy source name, key presence in
``edb.setups``) rather than by assuming success from the absence of an exception. The final block
independently reopens the saved database to confirm persistence.

Common failures and diagnostics
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``dc_shorts()`` returns one or more ``[net_name, net_name]`` pairs
     - Two nets are electrically connected (through a via, plane overlap, or a zero-value
       resistor) that should not be.
     - Investigate each pair before proceeding; a DCIR solve on a shorted design produces
       misleading results rather than failing outright.
   * - ``create_voltage_source_on_net(...)`` raises ``IndexError``
     - No pins were found for the requested component/net combination. The method builds a pin
       group and then reads ``positive_pins[0].net`` unconditionally, so an empty pin list raises
       rather than returning ``None`` or ``False``.
     - Verify with ``edb.components.get_pin_from_component(component, net_name)`` **before** calling
       ``create_voltage_source_on_net``; an empty list means the source cannot be created with
       these arguments.
   * - ``classify_nets(power_nets="VCC")`` (a single string) has no effect
     - ``classify_nets`` only accepts a **list** of net names for ``power_nets``/``signal_nets``; a
       bare string is silently treated as empty and no net is reclassified.
     - Always pass a list, even for a single net: ``classify_nets(power_nets=["VCC"])``.
   * - ``add_source_terminal_to_ground`` does not seem to affect the solve
     - The ``terminal`` argument (``0`` or ``1``) selects which side of the source (positive or
       negative) is treated as the DCIR reference; the wrong value silently produces a valid but
       incorrect reference assignment.
     - Confirm with ``dcir_setup.settings.source_terms_to_ground`` after calling it, as shown in
       step 9, and cross-check against your source's intended polarity.

Cleanup
-----------

Both ``edb`` sessions are explicitly closed above. Remove the temporary working directory
(``work_dir``) once you are done inspecting the output, for example with
``shutil.rmtree(work_dir, ignore_errors=True)``.

Next recommended example
-----------------------------

- :doc:`../user_guide/validation_and_drc` — run the broader DRC engine (spacing, annular ring,
  manufacturing rules) in addition to the DC-short check shown here.
- SI example: :doc:`si_example_wave_ports` — the equivalent step-by-step workflow for a
  signal-integrity S-parameter extraction.

Related conceptual pages
-----------------------------

- :doc:`../getting_started/object_model` — the ``edb.nets``, ``edb.layout_validation``, and
  ``edb.simulation_setups`` sections.
- :doc:`components_and_nets` — net classification fundamentals.

Related API-reference pages
--------------------------------

- :class:`Nets <pyedb.grpc.database.nets.Nets>`
- :class:`LayoutValidation <pyedb.grpc.database.layout_validation.LayoutValidation>`
- :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`
- :class:`SIWaveDCIRSimulationSetup <pyedb.grpc.database.simulation_setup.
  siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup>`

Version compatibility notes
--------------------------------

- ``classify_nets``, ``dc_shorts``, ``create_voltage_source_on_net``, and
  ``create_siwave_dcir_setup`` are available on both the gRPC and DotNet backends with the same
  signatures.
- This example targets the gRPC backend (``version="2026.1"`` or later). For the deprecated
  DotNet backend, pass ``grpc=False`` and install ``pyedb[dotnet]``.
