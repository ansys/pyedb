.. _ports_and_sources:

Ports and sources
====================

Create ports, voltage/current sources, and probes for simulation.

Prerequisites
-------------

- An open ``Edb`` instance (see :doc:`../getting_started/quick_start`).
- Padstack instances (pins or vias) to attach the excitation to (see :doc:`padstacks_and_vias`).

Public API entry points
-------------------------

- :attr:`Edb.excitation_manager <pyedb.grpc.edb.Edb.excitation_manager>` — returns
  :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`, or ``None`` if
  no database is open.
- :attr:`Edb.ports <pyedb.grpc.edb.Edb.ports>` — dictionary of all created ports, keyed by name.
- :meth:`PadstackInstance.create_port <pyedb.grpc.database.primitive.padstack_instance.
  PadstackInstance.create_port>` — the simplest way to create a port directly from a pin or via,
  without building terminal objects by hand.

.. important::

   ``edb.excitation_manager.create_port(...)`` and ``create_voltage_source(...)`` operate on
   **terminal** objects (for example a ``PadstackInstanceTerminal``), not on raw ``PadstackInstance``
   pin/via objects returned by ``edb.padstacks.pins``. Passing a ``PadstackInstance`` directly to
   ``edb.excitation_manager.create_port(...)`` raises an ``AttributeError`` because
   ``PadstackInstance`` has no ``boundary_type`` attribute. Use one of the two patterns below instead.

Procedure
---------

1. Create a port between two pins using the padstack-instance convenience method (recommended for
   most cases — it builds the required terminal objects for you).

   .. code-block:: python

      pin = edb.padstacks.pins["Via1"]  # keys are instance names (str)
      ref_pin = edb.padstacks.pins["Via2"]
      port = pin.create_port(reference=ref_pin)

2. Create a port explicitly through ``excitation_manager`` when you need direct control over the
   terminal objects (for example a specific layer for each terminal).

   .. code-block:: python

      from pyedb.grpc.database.terminal.padstack_instance_terminal import (
          PadstackInstanceTerminal,
      )

      pin = edb.padstacks.pins["Via1"]
      ref_pin = edb.padstacks.pins["Via2"]
      top_layer, _ = pin.get_layer_range()
      ref_top_layer, _ = ref_pin.get_layer_range()
      pos_terminal = PadstackInstanceTerminal.create(
          layout=edb.layout, name="port_pos", padstack_instance=pin, layer=top_layer
      )
      ref_terminal = PadstackInstanceTerminal.create(
          layout=edb.layout, name="port_ref", padstack_instance=ref_pin, layer=ref_top_layer
      )
      port = edb.excitation_manager.create_port(
          pos_terminal, ref_terminal=ref_terminal, name="Port1"
      )

3. Create a coaxial port directly on a component pin.

   .. code-block:: python

      edb.excitation_manager.create_port_on_component(
          component="U1", net_list=["DDR4_DQS0_P"], port_type="coax_port", reference_net="GND"
      )

4. Create a voltage source between two pins.

   .. code-block:: python

      edb.excitation_manager.create_voltage_source(pin, ref_pin, magnitude=3.3, phase=0)

5. List all created ports.

   .. code-block:: python

      print(list(edb.ports.keys()))

Complete example
-----------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   input_path = str(Path(tempfile.gettempdir()) / "ports_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   # A freshly created, empty database has no padstack instances yet; this example
   # shows the call pattern for a design that already has vias or pins placed.
   if len(edb.padstacks.pins) >= 2:
       pin_names = list(edb.padstacks.pins.keys())
       pin = edb.padstacks.pins[pin_names[0]]
       ref_pin = edb.padstacks.pins[pin_names[1]]
       port = pin.create_port(reference=ref_pin, name="Port1")
       print("Created port:", port)

       # Validate the in-memory result before saving: the port must be a key in edb.ports.
       assert "Port1" in edb.ports, "Port1 was not registered in edb.ports"
   else:
       print("Fewer than 2 padstack instances available; skipping port creation.")

   output_path = str(Path(tempfile.gettempdir()) / "ports_output.aedb")
   edb.save_as(output_path)
   edb.close()

   # Reopen the saved database and verify the port persisted.
   edb_reopened = Edb(edbpath=output_path, version="2026.1")
   if "Port1" in edb_reopened.ports:
       print("Verified: Port1 persisted after save_as + reopen.")
   edb_reopened.close()

Expected result
----------------

``pin.create_port(...)`` (and ``edb.excitation_manager.create_port(...)``) return a port object (a
``GapPort``, ``WavePort``, or similar wrapper depending on the terminal type), and the port name
appears as a key in ``edb.ports``. Both checks above are deterministic: the first asserts the
in-memory result immediately after creation, the second confirms the port survived a
``save_as``/close/reopen cycle.

Backend and version notes
---------------------------

- ``edb.excitation_manager`` is available on both backends; the concrete port/terminal wrapper
  classes returned differ internally between backends because they wrap different underlying
  terminal implementations, but the method names and arguments used above are the same.
- ``Edb.create_port(...)``, ``Edb.create_voltage_source(...)``, and ``Edb.create_current_source(...)``
  (directly on the ``Edb`` object, without going through ``excitation_manager``) still exist but are
  deprecated thin wrappers. Prefer ``edb.excitation_manager.create_port(...)`` /
  ``create_voltage_source(...)`` / ``create_current_source(...)``, or
  ``PadstackInstance.create_port(...)`` shown above, in new code.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``edb.excitation_manager`` is ``None``
     - No active database is open (``edb.active_db`` is falsy).
     - Make sure the ``Edb`` object was successfully created or opened before accessing this
       property.
   * - ``AttributeError: 'PadstackInstance' object has no attribute 'boundary_type'``
     - A raw ``PadstackInstance`` (from ``edb.padstacks.pins``) was passed directly to
       ``edb.excitation_manager.create_port(...)`` instead of a terminal object.
     - Use ``pin.create_port(reference=ref_pin)`` (procedure step 1), or build
       ``PadstackInstanceTerminal`` objects explicitly first (procedure step 2).
   * - Port created but not found afterward
     - You looked it up under a different name than the auto-generated one.
     - If you did not pass ``name=``, PyEDB auto-generates a name; read it back from the returned port
       object's ``.name`` attribute, or always pass an explicit ``name=``.

See also
--------

- :doc:`padstacks_and_vias` — locating the pins used to create ports.
- :doc:`../getting_started/object_model` — the ``edb.excitation_manager`` section.
- :doc:`simulation_setups` — configuring the simulation that uses these ports.
- :doc:`si_example_wave_ports` — a complete signal-integrity workflow that creates ports on a
  differential pair using the higher-level ``create_circuit_port_on_net`` net-level API.
- :doc:`pi_example_power_aware_dcir` — a complete power-integrity workflow that creates a DC
  voltage source using ``create_voltage_source_on_net``.
