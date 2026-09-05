.. _ports_and_sources:

Ports and sources
====================

Create ports, voltage/current sources, and probes for simulation.

Prerequisites
-------------

- An open ``Edb`` instance (see :doc:`../getting_started/quick_start`).
- Terminals or padstack instances to attach the excitation to (see :doc:`padstacks_and_vias`).

Public API entry points
-------------------------

- :attr:`Edb.excitation_manager <pyedb.grpc.edb.Edb.excitation_manager>` — returns
  :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`, or ``None`` if
  no database is open.
- :attr:`Edb.ports <pyedb.grpc.edb.Edb.ports>` — dictionary of all created ports, keyed by name.

Procedure
---------

1. Create a port between two padstack-instance terminals (a positive pin and its reference).

   .. code-block:: python

      pin = edb.padstacks.pins["Via1"]
      ref_pin = edb.padstacks.pins["Via2"]
      port = edb.excitation_manager.create_port(pin, ref_terminal=ref_pin)

2. Create a coaxial port directly on a component pin.

   .. code-block:: python

      edb.excitation_manager.create_port_on_component(
          component="U1", net_list=["DDR4_DQS0_P"], port_type="coax_port", reference_net="GND"
      )

3. Create a voltage source between two terminals.

   .. code-block:: python

      edb.excitation_manager.create_voltage_source(pin, ref_pin, magnitude=3.3, phase=0)

4. List all created ports.

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
   if edb.padstacks.pins:
       pin_names = list(edb.padstacks.pins.keys())
       pin = edb.padstacks.pins[pin_names[0]]
       port = edb.excitation_manager.create_port(pin)
       print("Created port:", port)

   output_path = str(Path(tempfile.gettempdir()) / "ports_output.aedb")
   edb.save_as(output_path)
   edb.close()

Expected result
----------------

``edb.excitation_manager.create_port(...)`` returns a port object (a ``GapPort``, ``WavePort``, or
similar wrapper depending on the terminal type), and the port name appears as a key in ``edb.ports``.

Backend and version notes
---------------------------

- ``edb.excitation_manager`` is available on both backends; the concrete port/terminal wrapper
  classes returned differ internally between backends because they wrap different underlying
  terminal implementations, but the method names and arguments used above are the same.
- ``Edb.create_port(...)``, ``Edb.create_voltage_source(...)``, and ``Edb.create_current_source(...)``
  (directly on the ``Edb`` object, without going through ``excitation_manager``) still exist but are
  deprecated thin wrappers. Prefer ``edb.excitation_manager.create_port(...)`` /
  ``create_voltage_source(...)`` / ``create_current_source(...)`` in new code.

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
   * - Port created but not found afterward
     - You looked it up under a different name than the auto-generated one.
     - If you did not pass ``name=``, PyEDB auto-generates a name; read it back from the returned port
       object's ``.name`` attribute, or always pass an explicit ``name=``.

See also
--------

- :doc:`padstacks_and_vias` — locating the terminals used to create ports.
- :doc:`../getting_started/object_model` — the ``edb.excitation_manager`` section.
- :doc:`simulation_setups` — configuring the simulation that uses these ports.
