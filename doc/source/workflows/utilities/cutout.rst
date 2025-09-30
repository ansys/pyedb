.. _ref_edb_cutout:

EDB Cutout
==========

.. only:: html

   .. contents::
      :local:
      :depth: 3

--------
Overview
--------

The ``Cutout`` class creates a clipped (cut-out) EDB cell from an existing layout.
All new features, performance improvements, and bug fixes are delivered **only**
through the **gRPC** back-end.
The legacy .NET back-end is still present for compatibility; it is **deprecated**
and scheduled for removal in a future release.

--------
Quickstart
--------

.. code-block:: python

   from ansys.edb.core.cutout import Cutout

   cut = Cutout(edb)  # gRPC is selected automatically when edb.grpc == True
   cut.signals = ["DDR4_DQ0", "DDR4_DQ1"]
   cut.references = ["GND"]
   cut.expansion_size = 0.001
   polygon = cut.run()

--------
Convenience entry point
-----------------------

Existing scripts continue to work without modification:

.. code-block:: python

   edb.cutout(
       signal_nets=["DDR4_DQ0", "DDR4_DQ1"],
       reference_nets=["GND"],
       expansion_size=0.001,
   )

The ``edb.cutout`` method internally instantiates the ``Cutout`` class (gRPC-first)
and returns the same clipped cell as in previous releases.

--------
Complete parameter reference
----------------------------

The following table lists every public parameter accepted by both the class
constructor and the convenience method ``edb.cutout``.
Defaults are shown in **bold**; physical values are in **metres** unless a
``*_units`` parameter is supplied.

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Name
     - Type
     - Purpose
   * - ``signal_nets`` *(alias ``signals``)*
     - ``list[str]``
     - Net names to retain in the cut-out (required).
   * - ``reference_nets`` *(alias ``references``)*
     - ``list[str]``
     - Net names used as reference (required).
   * - ``expansion_size``
     - ``float | str``
     - Additional margin around computed extent.  **0.002**
   * - ``extent_type``
     - ``str``
     - Extent algorithm: **"ConvexHull"**, "Conforming", "Bounding".
   * - ``use_round_corner``
     - ``bool``
     - Apply rounded corners after expansion.  **False**
   * - ``custom_extent``
     - ``list[tuple[float,float]] | None``
     - Closed polygon ``[(x1,y1), …]`` overriding automatic extent.  **None**
   * - ``custom_extent_units``
     - ``str``
     - Length unit for *custom_extent*.  **"mm"**
   * - ``include_voids_in_extents``
     - ``bool``
     - Include voids ≥ 5 % of extent area while building clip polygon.  **False**
   * - ``open_cutout_at_end``
     - ``bool``
     - Load the resulting .aedb into the active ``edb`` object.  **True**
   * - ``output_file``
     - ``str``
     - Full path where the clipped .aedb is saved.  **""** (in-place)
   * - ``use_pyaedt_cutout``
     - ``bool``
     - Use PyAEDT-based clipping instead of native EDB API.  **True**
   * - ``smart_cutout``
     - ``bool``
     - Auto-enlarge *expansion_size* until every port has a reference.  **False**
   * - ``expansion_factor``
     - ``float``
     - If > 0, compute initial *expansion_size* from trace-width/dielectric.  **0**
   * - ``maximum_iterations``
     - ``int``
     - Max attempts for *smart_cutout* before giving up.  **10**
   * - ``number_of_threads``
     - ``int``
     - Worker threads for polygon clipping and padstack cleaning.  **1**
   * - ``remove_single_pin_components``
     - ``bool``
     - Delete RLC components with only one pin after cut-out.  **False**
   * - ``preserve_components_with_model``
     - ``bool``
     - Keep every pin of components that carry a Spice/S-parameter model.  **False**
   * - ``check_terminals``
     - ``bool``
     - Grow extent until all reference terminals are inside the cut-out.  **False**
   * - ``include_pingroups``
     - ``bool``
     - Ensure complete pin-groups are included (requires *check_terminals*).  **False**
   * - ``simple_pad_check``
     - ``bool``
     - Use fast centre-point padstack check instead of bounding-box.  **True**
   * - ``keep_lines_as_path``
     - ``bool``
     - Retain clipped traces as Path objects (3D Layout only).  **False**
   * - ``extent_defeature``
     - ``float``
     - Defeature tolerance for conformal extent.  **0**
   * - ``include_partial_instances``
     - ``bool``
     - Keep padstacks that only partially overlap the clip polygon.  **False**
   * - ``keep_voids``
     - ``bool``
     - Retain voids that intersect the clip polygon.  **True**

--------
Extent strategies
-----------------

The cut-out boundary can be generated with three built-in algorithms:

* ``ConvexHull`` (default) – convex hull of selected objects plus expansion
* ``Conforming`` – tight follow of geometry contours
* ``Bounding`` – simple bounding box

Additional options control corner rounding, void inclusion, multi-threading,
smart expansion, and user-supplied boundary polygons.

--------
API reference
-------------

.. currentmodule:: ansys.edb.core.cutout

.. autosummary::
   :toctree: _autosummary
   :template: class.rst
   :nosignatures:

   Cutout

.. autoclass:: ansys.edb.core.cutout.Cutout
   :members:
   :show-inheritance:
   :inherited-members:

--------
Legacy notice
-------------

The ``DotNetCutout`` class is exposed **solely** for backward compatibility.
New code must use the gRPC-based ``Cutout`` class—or the ``edb.cutout`` convenience
method—to ensure future support.