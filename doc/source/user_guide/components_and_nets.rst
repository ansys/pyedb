.. _components_and_nets:

Components and nets
======================

Inspect and edit component placement, and find, rename, or group nets.

Prerequisites
-------------

- An open ``Edb`` instance (see :doc:`../getting_started/quick_start`).

Public API entry points
-------------------------

- :attr:`Edb.components <pyedb.grpc.edb.Edb.components>` — returns
  :class:`Components <pyedb.grpc.database.components.Components>`.
- :attr:`Edb.nets <pyedb.grpc.edb.Edb.nets>` — returns :class:`Nets <pyedb.grpc.database.nets.Nets>`.
- :attr:`Edb.differential_pairs <pyedb.grpc.edb.Edb.differential_pairs>` — returns
  :class:`DifferentialPairs <pyedb.grpc.database.net.differential_pair.DifferentialPairs>`.

Procedure
---------

1. Look up a component by reference designator and inspect it.

   .. code-block:: python

      comp = edb.components["R1"]
      print(comp.name, comp.location, comp.part_name)

2. Move the component.

   .. code-block:: python

      comp.location = [0.01, 0.02]

3. List all net names, then rename one.

   .. code-block:: python

      print(edb.nets.netlist)
      net = edb.nets["DDR0_DQ0"]
      net.name = "DDR0_DQ0_NEW"

4. Auto-identify and create a differential pair.

   .. code-block:: python

      edb.differential_pairs.auto_identify()
      pair = edb.differential_pairs.create(name="USB_DP", net_p="USB_P", net_n="USB_N")

Complete example
-----------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   input_path = str(Path(tempfile.gettempdir()) / "components_nets_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   # edb.components.instances and edb.nets.netlist are empty on a freshly created,
   # unpopulated database; this example shows the calls used once a design is loaded.
   print("Components:", list(edb.components.instances.keys()))
   print("Nets:", edb.nets.netlist)

   output_path = str(Path(tempfile.gettempdir()) / "components_nets_output.aedb")
   edb.save_as(output_path)
   edb.close()

Expected result
----------------

``edb.components.instances`` returns a ``dict[str, Component]`` keyed by reference designator (for
example ``"R1"``, ``"U1"``). ``edb.nets.netlist`` returns a ``list[str]`` of net names. On a newly
created, empty database both are empty; open an existing design to see populated results.

Backend and version notes
---------------------------

- ``edb.components`` and ``edb.nets`` are available on both backends with the same property names.
- ``Components.instances`` and ``Nets.netlist`` reflect the in-memory database immediately after any
  mutation; call ``edb.save()`` or ``edb.save_as(...)`` to persist changes to disk.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``KeyError`` from ``edb.components["X"]`` or ``edb.nets["X"]``
     - The component or net name does not exist, or the name case does not match.
     - Check the exact name with ``list(edb.components.instances.keys())`` or ``edb.nets.netlist``
       first.
   * - Component deletion has no effect on other pins
     - ``Components.delete(component_name)`` removes a single component by name; it does not accept a
       list of names.
     - Call ``delete`` once per component name, or iterate over a list of names yourself.
   * - Differential pair not detected by ``auto_identify()``
     - The net names do not end with the expected suffixes.
     - Pass explicit suffixes: ``edb.differential_pairs.auto_identify(positive_differentiator="_P", negative_differentiator="_N")``
       (these are the defaults; adjust them to match your net naming convention), or create the pair
       explicitly with ``edb.differential_pairs.create(name=..., net_p=..., net_n=...)``.

See also
--------

- :doc:`../getting_started/object_model` — the ``edb.components`` and ``edb.nets`` sections.
- :doc:`common_tasks` — additional net- and component-editing recipes.
- :doc:`cutouts` — building a cutout around a set of signal and reference nets.
