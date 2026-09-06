.. _stackup_and_materials:

Stackup and materials
=======================

Define layer stacks and the materials assigned to them.

Prerequisites
-------------

- An open ``Edb`` instance (see :doc:`../getting_started/quick_start`).
- Familiarity with the :doc:`../getting_started/object_model` navigation model.

Public API entry points
-------------------------

- :attr:`Edb.stackup <pyedb.grpc.edb.Edb.stackup>` — returns
  :class:`Stackup <pyedb.grpc.database.stackup.Stackup>`.
- :attr:`Edb.materials <pyedb.grpc.edb.Edb.materials>` — returns
  :class:`Materials <pyedb.grpc.database.definition.materials.Materials>`.

Procedure
---------

1. Inspect the current stackup.

   .. code-block:: python

      layers = edb.stackup.layers
      print(list(layers.keys()))

2. Add a conductor material, then a dielectric material.

   .. code-block:: python

      edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
      edb.materials.add_dielectric_material(
          name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01
      )

3. Add a signal layer on top of the stack, referencing the new materials.

   .. code-block:: python

      edb.stackup.add_layer(
          layer_name="TOP",
          layer_type="signal",
          material="gold",
          filling_material="silicon",
          thickness="35um",
      )

4. Read back a layer property.

   .. code-block:: python

      top = edb.stackup["TOP"]
      print(top.thickness, top.material)

Complete example
-----------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   input_path = str(Path(tempfile.gettempdir()) / "stackup_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
   edb.materials.add_dielectric_material(
       name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01
   )
   edb.stackup.add_layer(
       layer_name="TOP",
       layer_type="signal",
       material="gold",
       filling_material="silicon",
       thickness="35um",
   )

   # Validate the in-memory result before saving.
   assert "TOP" in edb.stackup.layers, "Layer 'TOP' was not added in memory"
   assert (
       edb.stackup["TOP"].material == "gold"
   ), "Layer 'TOP' does not reference material 'gold'"
   assert (
       abs(edb.stackup["TOP"].thickness - 35e-6) < 1e-9
   ), "Layer 'TOP' thickness is not 35 um"

   output_path = str(Path(tempfile.gettempdir()) / "stackup_output.aedb")
   edb.save_as(output_path)
   edb.close()

   # Reopen the saved database and verify the stackup change persisted to disk.
   edb_reopened = Edb(edbpath=output_path, version="2026.1")
   assert (
       "TOP" in edb_reopened.stackup.layers
   ), "Layer 'TOP' did not persist after save_as + reopen"
   assert (
       edb_reopened.stackup["TOP"].material == "gold"
   ), "Persisted layer lost its material assignment"
   edb_reopened.close()

Expected result
----------------

``edb.stackup.layers`` includes ``"TOP"`` with ``material == "gold"`` and a ``thickness`` value
corresponding to 35 micrometers (``StackupLayer.thickness`` returns a numeric value expressed in
meters, so 35 um is ``35e-6``). The modified database is written to ``output_path``; the input
database is untouched. All four ``assert`` statements above pass with no traceback: the first two
check the in-memory result immediately after the mutation, the last two check that the change survived
a ``save_as``/close/reopen cycle.

Backend and version notes
---------------------------

- ``edb.stackup`` and ``edb.materials`` are available on both the gRPC and DotNet backends with the
  same property names.
- ``edb.materials`` does not cache its internal dictionary between accesses; each access to
  ``edb.materials.materials`` recomputes it from the live database, so repeated large-scale reads in a
  tight loop may be slower than caching the returned ``dict`` yourself in a local variable.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``ValueError`` when calling ``add_material``
     - A material with that name (case-insensitive) already exists.
     - Use a different name, or look up the existing material with ``edb.materials["name"]`` and
       edit its properties directly.
   * - New layer does not appear in ``edb.stackup.layers``
     - ``layer_type`` was not ``"signal"`` or ``"dielectric"`` (for example ``"silkscreen"``); such
       layers are added to ``edb.stackup.non_stackup_layers`` instead.
     - Use ``edb.stackup["LayerName"]`` (checks both stackup and non-stackup layers) instead of
       ``edb.stackup.layers`` if you are not sure which category the layer belongs to.
   * - Material referenced by a layer looks unset
     - The material name was not registered with ``edb.materials`` before being referenced.
     - Call ``edb.materials.add_material`` (or ``add_conductor_material`` /
       ``add_dielectric_material``) before calling ``add_layer`` with that material name. PyEDB also
       attempts to auto-load well-known material names from the AEDT system library.

See also
--------

- :doc:`../getting_started/object_model` — the ``edb.stackup`` and ``edb.materials`` sections.
- :doc:`../getting_started/quick_start` — a runnable end-to-end example that adds a layer.
- :doc:`../configuration/index` — declarative stackup definition via JSON/TOML configuration files.
