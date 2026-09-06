.. _geometry_and_connectivity:

Geometry and connectivity
============================

Find and inspect layout primitives (traces, polygons, rectangles, circles) by layer, net, or type, and
locate the padstack instances (vias, pins) connected to a given net.

Prerequisites
-------------

- An open ``Edb`` instance (see :doc:`../getting_started/quick_start`).
- Familiarity with the :doc:`../getting_started/object_model` navigation model, in particular the
  ``edb.layout`` section.

Public API entry points
-------------------------

- :attr:`Edb.layout <pyedb.grpc.edb.Edb.layout>` — returns
  :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`, the recommended entry point for
  **querying** primitives.
- :attr:`Edb.modeler <pyedb.grpc.edb.Edb.modeler>` — returns
  :class:`Modeler <pyedb.grpc.database.modeler.Modeler>`, the recommended entry point for **creating**
  new geometry (``create_trace``, ``create_rectangle``, and similar methods). Several ``Modeler``
  query properties (``primitives``, ``primitives_by_layer``, ``primitives_by_net``) are deprecated
  aliases that forward to the ``edb.layout`` equivalents below — use ``edb.layout`` directly in new
  code.
- :attr:`Edb.padstacks <pyedb.grpc.edb.Edb.padstacks>` — returns
  :class:`Padstacks <pyedb.grpc.database.padstacks.Padstacks>`, used here to find padstack instances
  (vias/pins) on a net.

Procedure
---------

1. List every primitive in the design, then narrow down by net, layer, and type using
   :meth:`Layout.filter_primitives <pyedb.grpc.database.layout.layout.Layout.filter_primitives>`.

   .. code-block:: python

      all_primitives = edb.layout.primitives
      print(f"{len(all_primitives)} primitives in the design")

      # Primitives on a specific net.
      net_primitives = edb.layout.filter_primitives(net_name="DDR4_DQS0_P")

      # Primitives on a specific layer.
      layer_primitives = edb.layout.filter_primitives(layer_name="TOP")

      # Primitives of a specific type ("circle", "rectangle", "polygon", "path", "bondwire").
      traces = edb.layout.filter_primitives(prim_type="path")

      # Combine filters: traces on a given net and layer at the same time.
      signal_traces = edb.layout.filter_primitives(
          net_name="DDR4_DQS0_P", layer_name="TOP", prim_type="path"
      )

2. Group primitives by layer or by net in a single call, when you need the full breakdown rather than
   one filtered subset.

   .. code-block:: python

      by_layer = edb.layout.primitives_by_layer  # dict[str, list[Primitive]]
      by_net = edb.layout.primitives_by_net  # dict[str, list[Primitive]]
      print({layer: len(prims) for layer, prims in by_layer.items()})

3. Use the type-specific shortcuts when you only need one primitive type across the whole design.

   .. code-block:: python

      print(len(edb.layout.paths), "paths")
      print(len(edb.layout.polygons), "polygons")
      print(len(edb.layout.rectangles), "rectangles")
      print(len(edb.layout.circles), "circles")

4. Find the padstack instances (vias/pins) connected to a given net.

   .. code-block:: python

      net_name = "GND"
      vias_on_net = [pin for pin in edb.padstacks.pins.values() if pin.net_name == net_name]
      print(f"{len(vias_on_net)} padstack instances on net {net_name!r}")

Complete example
-----------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   input_path = str(Path(tempfile.gettempdir()) / "geometry_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   # On a freshly created, empty database every query below returns an empty result; open an
   # existing design (see the object-model page for how to open one) to see populated results.
   all_primitives = edb.layout.primitives
   print(f"{len(all_primitives)} total primitives")

   # Query by net: distinguish "net has no primitives" from "net does not exist".
   net_name = "GND"
   if net_name in edb.nets.netlist:
       net_primitives = edb.layout.filter_primitives(net_name=net_name)
       print(f"{len(net_primitives)} primitives on net {net_name!r}")
   else:
       print(
           f"Net {net_name!r} does not exist in this design. Available nets: {edb.nets.netlist[:10]}"
       )

   # Query by layer: distinguish "layer has no primitives" from "layer does not exist".
   layer_name = "TOP"
   if layer_name in edb.stackup.layers:
       layer_primitives = edb.layout.filter_primitives(layer_name=layer_name)
       print(f"{len(layer_primitives)} primitives on layer {layer_name!r}")
   else:
       print(
           f"Layer {layer_name!r} does not exist. Available layers: {list(edb.stackup.layers.keys())}"
       )

   # Deterministic check: filtering by type only ever returns primitives of that type.
   traces = edb.layout.filter_primitives(prim_type="path")
   assert all(
       p.primitive_type == "path" for p in traces
   ), "filter_primitives returned a non-path primitive"

   output_path = str(Path(tempfile.gettempdir()) / "geometry_output.aedb")
   edb.save_as(output_path)
   edb.close()

Expected result
----------------

``edb.layout.primitives`` returns ``list[Primitive]`` for every primitive in the design.
``edb.layout.filter_primitives(...)`` returns a possibly-empty ``list[Primitive]`` matching all of the
criteria supplied — an empty result means "no primitives matched," which is different from "the net or
layer name does not exist" (checked separately above via ``edb.nets.netlist`` / ``edb.stackup.layers``
membership). The ``assert`` on primitive type is deterministic and independent of which dataset is
open: any primitive returned by ``prim_type="path"`` must itself report ``primitive_type == "path"``.

Backend and version notes
---------------------------

- ``edb.layout`` and ``edb.modeler`` are available on both backends with the same property and method
  names.
- ``edb.modeler.primitives``, ``primitives_by_layer``, and ``primitives_by_net`` are deprecated
  aliases; they still work but emit a ``DeprecationWarning`` and forward to the ``edb.layout``
  equivalents shown in this page. Prefer ``edb.layout`` directly in new code.
- ``Layout.filter_primitives`` accepts both lowercase EDB-style primitive-type strings (``"polygon"``)
  and the exact value returned by ``primitive.primitive_type`` — passing an unrecognized string simply
  matches nothing rather than raising an error, so a typo in ``prim_type`` silently returns an empty
  list. Verify the exact spelling by printing ``{p.primitive_type for p in edb.layout.primitives}``
  first if a filter unexpectedly returns nothing.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``filter_primitives(net_name=...)`` returns an empty list
     - Either the net genuinely has no primitives, or the net name does not exist at all.
     - Check ``net_name in edb.nets.netlist`` first (procedure step 4 pattern) to distinguish the two
       cases before concluding the query is wrong.
   * - ``filter_primitives(prim_type=...)`` returns an empty list unexpectedly
     - The ``prim_type`` string does not match any primitive's ``primitive_type`` value (for example a
       typo, or an unsupported type name).
     - Print ``{p.primitive_type for p in edb.layout.primitives}`` to see the exact type strings
       present in this design, then pass one of those values.
   * - ``edb.modeler.primitives`` emits a ``DeprecationWarning``
     - This property is a deprecated alias.
     - Use ``edb.layout.primitives`` instead; the returned value is identical.

See also
--------

- :doc:`../getting_started/object_model` — the ``edb.modeler`` / ``edb.layout`` section.
- :doc:`padstacks_and_vias` — finding padstack instances (vias, pins) rather than primitives.
- :doc:`components_and_nets` — finding the net names to filter by.
- :doc:`cutouts` — building a cutout around a set of nets found using the patterns on this page.
- :doc:`find_isolated_vias` — using ``get_connected_objects`` to detect disconnected vias.
