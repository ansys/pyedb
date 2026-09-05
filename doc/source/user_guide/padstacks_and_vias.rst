.. _padstacks_and_vias:

Padstacks and vias
====================

Inspect padstack definitions, work with placed padstack instances (pins and vias), and configure
back-drilling.

Prerequisites
-------------

- An open ``Edb`` instance (see :doc:`../getting_started/quick_start`).

Public API entry points
-------------------------

- :attr:`Edb.padstacks <pyedb.grpc.edb.Edb.padstacks>` — returns
  :class:`Padstacks <pyedb.grpc.database.padstacks.Padstacks>`.
- :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>` — a
  single placed pin or via.

Procedure
---------

1. Create a padstack definition.

   .. code-block:: python

      pad_name = edb.padstacks.create(
          padstackname="my_via", holediam="0.2mm", paddiam="0.4mm", antipaddiam="0.6mm"
      )

2. List all padstack definitions.

   .. code-block:: python

      print(list(edb.padstacks.definitions.keys()))

3. Inspect a placed padstack instance (pin or via).

   .. code-block:: python

      instance = list(edb.padstacks.pins.values())[0]
      print(instance.name, instance.net_name, instance.start_layer, instance.stop_layer)

4. Configure back-drilling on a via.

   .. code-block:: python

      instance.set_back_drill_by_layer(
          drill_to_layer="Inner4(Sig2)", diameter="0.5mm", from_bottom=True
      )

Complete example
-----------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   input_path = str(Path(tempfile.gettempdir()) / "padstacks_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   pad_name = edb.padstacks.create(
       padstackname="my_via", holediam="0.2mm", paddiam="0.4mm", antipaddiam="0.6mm"
   )
   print("Created padstack definition:", pad_name)
   print("All definitions:", list(edb.padstacks.definitions.keys()))

   output_path = str(Path(tempfile.gettempdir()) / "padstacks_output.aedb")
   edb.save_as(output_path)
   edb.close()

Expected result
----------------

``edb.padstacks.create(...)`` returns the padstack name as a string (``"my_via"``), and that name
appears as a key in ``edb.padstacks.definitions``. The modified database is written to
``output_path``.

Backend and version notes
---------------------------

- ``edb.padstacks`` is available on both backends with the same property name.
- Passing ``fill_material`` to ``set_back_drill_by_layer`` / ``set_back_drill_by_depth`` requires
  Ansys release 2027.1 or later; on earlier releases the argument is accepted but ignored with a
  warning.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``Padstacks.pins`` dictionary keys are not the values you expected
     - Despite being named ``pins``, entries are keyed by pin/instance **name** (a string), not by a
       numeric database ID.
     - Iterate ``edb.padstacks.pins.values()`` if you only need the objects, or use
       ``instance.name`` / ``instance.id`` explicitly rather than assuming the dict key's type.
   * - ``set_backdrill_top`` / ``set_backdrill_bottom`` raise a ``FutureWarning``
     - These methods are deprecated.
     - Use ``set_back_drill_by_layer(...)`` or ``set_back_drill_by_depth(...)`` instead.
   * - ``AttributeError`` when calling ``create_port()`` on a padstack instance
     - The instance has no attached component (``instance.component`` is ``False``) and a name was
       not supplied.
     - Pass an explicit ``name=`` argument to ``create_port(...)`` when the padstack instance is not
       part of a component.

See also
--------

- :doc:`ports_and_sources` — creating ports on padstack instances.
- :doc:`../getting_started/object_model` — the ``edb.padstacks`` section.
- :doc:`common_tasks` — additional recipes.
