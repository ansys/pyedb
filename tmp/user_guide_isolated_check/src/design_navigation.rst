.. _ref_grpc_edb_design_guide:
.. _ref_design_navigation:

PyEDB architecture and design navigation
========================================

This guide helps users get started with PyEDB from the highest-level entry
point, understand how the gRPC architecture is exposed through the API, and
navigate an EDB design efficiently.

The focus is on the gRPC implementation under ``src/pyedb/grpc``, which is the
long-term supported direction for PyEDB. For user code, however, the
recommended import remains the public top-level entry point.

.. contents::
   :local:
   :depth: 2

Start with the public ``Edb`` entry point
-----------------------------------------

For user scripts and documentation, import ``Edb`` from the top-level package:

.. code-block:: python

   from pyedb import Edb

At instantiation time, the ``grpc`` flag selects the backend:

* ``grpc=False`` selects the legacy DotNet backend.
* ``grpc=True`` selects the gRPC backend.

.. important::

   The current default is ``grpc=False``.

   Even though the default is still ``False``, it is better to pass
   ``grpc=True`` or ``grpc=False`` explicitly so that the intent of the script
   is clear.

Typical usage patterns are:

.. code-block:: python

   from pyedb import Edb

   # Current default backend, made explicit
   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=False)

.. code-block:: python

   from pyedb import Edb

   # Recommended for new workflows when the installed AEDT version supports it
   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=True)

.. note::

   In the current implementation, the public ``pyedb.Edb`` entry point selects
   the backend and returns the corresponding implementation. When
   ``grpc=True``, it dispatches to the gRPC ``Edb`` class implemented under
   ``src/pyedb/grpc``.

gRPC version support
--------------------

The gRPC backend requires a supported AEDT version.

From the current implementation:

* ``grpc=True`` is supported only for AEDT 2025 R2 and later.
* Requesting ``grpc=True`` with an older version raises an error.

If you are writing onboarding material or reusable automation scripts, always
show the ``grpc`` flag explicitly.

What ``Edb`` represents
-----------------------

``Edb`` is the main session object in PyEDB.

From a user perspective, it is the open design session from which almost every
task begins. It gives access to the active design and to the main managers used
to inspect or edit it.

A useful mental model is:

*``Edb`` is your open design session, and the next step is simply choosing
which part of the design you want to explore.*

A minimal session looks like this:

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=True)
   try:
       print(edb.cell_names)
       print(edb.active_cell.name)
   finally:
       edb.close()

PyEDB architecture at a glance
------------------------------

The user-facing architecture can be understood in three layers:

1. **Public entry point**

   Users write ``from pyedb import Edb`` and choose the backend with the
   ``grpc`` flag.

2. **Application session**

   The ``Edb`` object becomes the root of the interaction with the project.

3. **Domain managers and objects**

   ``Edb`` exposes managers such as ``stackup``, ``nets``, ``components``,
   ``layout``, and ``modeler``. Those managers then return focused objects such
   as layers, nets, components, pins, primitives, and terminals.

You can picture the architecture like this:

.. code-block:: text

   from pyedb import Edb
            |
            v
          Edb session
            |
            +-- layout      -> primitives, terminals, groups, pin groups
            +-- stackup     -> layers and physical organization
            +-- nets        -> connectivity-centric traversal
            +-- components  -> component-centric traversal
            +-- modeler     -> geometry creation and helper queries
            +-- padstacks   -> padstack definitions and instances
            +-- hfss        -> HFSS workflows
            +-- siwave      -> SIwave workflows

Choose the right starting point
-------------------------------

When users are new to PyEDB, the hardest part is usually not syntax. It is
knowing where to start.

The simplest rule is:

* start from ``Edb``,
* pick the manager that matches your engineering question,
* then walk from that manager to the design objects you need.

.. list-table:: Which manager should I use?
   :header-rows: 1
   :widths: 32 22 46

   * - If your question is...
     - Start here
     - Typical next step
   * - Which design is active? What does the layout contain?
     - ``edb.active_cell`` or ``edb.layout``
     - Inspect primitives, terminals, groups, or cell names
   * - Which layers exist and what are their materials or thicknesses?
     - ``edb.stackup``
     - Read ``layers``, ``signal_layers``, or one named layer
   * - Which objects belong to a net?
     - ``edb.nets``
     - Get a net and inspect its primitives, padstacks, or connected components
   * - Which pins or nets belong to a component?
     - ``edb.components``
     - Get a component and inspect its pins, nets, or definition
   * - I want to inspect or create geometry
     - ``edb.layout`` or ``edb.modeler``
     - Find primitives or create paths, polygons, rectangles, and circles
   * - Which ports, sources, or terminals exist?
     - ``edb.ports``, ``edb.sources``, or ``edb.terminals``
     - Inspect excitations and terminal objects

First inspection steps
----------------------

Once an ``Edb`` session is open, the first useful questions are usually:

* Which cell is active?
* How many layers, nets, components, and primitives exist?
* What is the overall structure of the design?

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=True)
   try:
       print("Cells:", edb.cell_names)
       print("Active cell:", edb.active_cell.name)
       print("Layer count:", len(edb.stackup.layers))
       print("Net count:", len(edb.nets.nets))
       print("Component count:", len(edb.components.instances))
       print("Primitive count:", len(edb.layout.primitives))
   finally:
       edb.close()

This already reveals the core organization of a PyEDB design: information is
grouped into focused managers hanging from ``Edb``.

Navigate the design by scope
----------------------------

Before diving into layers, nets, or components, it helps to understand the
design scope.

The most useful high-level entry points are:

* ``edb.active_db`` for the open database,
* ``edb.cell_names`` for the available design cells,
* ``edb.active_cell`` for the current cell,
* ``edb.layout`` for the active layout wrapper.

.. code-block:: python

   print(edb.cell_names)
   print(edb.active_cell.name)
   print(len(edb.layout.primitives))

.. note::

   If you switch ``edb.active_cell``, reacquire dependent objects such as nets,
   layers, or components afterwards. That keeps the script aligned with the
   newly active design.

Navigate by stackup
-------------------

Use ``edb.stackup`` when your question is layer-centric.

Typical use cases are:

* list all layers,
* separate signal and dielectric layers,
* read thickness and material information,
* retrieve a specific layer by name.

Useful entry points are:

* ``edb.stackup.layers``
* ``edb.stackup.signal_layers``
* ``edb.stackup.all_layers``
* ``edb.stackup["TOP"]``

.. code-block:: python

   for layer_name, layer in edb.stackup.layers.items():
       print(layer_name, layer.material, layer.thickness)

The stackup is often the best first physical map of the design. Even before you
know specific net or component names, layer names already show how the design
is organized.

Navigate by net connectivity
----------------------------

Use ``edb.nets`` when your question is electrical.

Typical use cases are:

* list nets,
* check whether a net exists,
* inspect primitives on a net,
* retrieve padstack instances or connected components on a net.

Useful entry points are:

* ``edb.nets.nets``
* ``edb.nets.netlist``
* ``edb.nets["GND"]``

.. code-block:: python

   gnd = edb.nets["GND"]
   print(gnd.name)
   print(len(gnd.primitives))
   print(len(gnd.padstack_instances))
   print(list(gnd.components))

If your question sounds like *Which objects belong to ``GND``?* or *Which
components are connected to ``VDD``?*, start from ``edb.nets``.

Navigate by component
---------------------

Use ``edb.components`` when your question is instance-centric.

Typical use cases are:

* retrieve a component by reference designator,
* inspect its pins,
* list the nets it touches,
* inspect its definition or model.

Useful entry points are:

* ``edb.components.instances``
* ``edb.components["U1"]``
* ``edb.components.get_component_by_name("U1")``
* ``edb.components.get_pin_from_component("U1", net_name="GND")``

.. code-block:: python

   u1 = edb.components["U1"]
   print(u1.name)
   print(u1.component_type)
   print(sorted(u1.nets))

   for pin_name, pin in u1.pins.items():
       print(pin_name, pin.net_name, pin.layer_name)

If your question starts from ``U1``, ``J1``, or ``R15``, start from
``edb.components`` rather than searching the whole layout first.

Navigate by layout and primitives
---------------------------------

Use ``edb.layout`` when you want to inspect the active layout directly.

This is the preferred read-oriented entry point for:

* enumerating primitives,
* enumerating terminals,
* enumerating groups and pin groups,
* filtering primitives by layer, primitive name, or net name.

Useful entry points are:

* ``edb.layout.primitives``
* ``edb.layout.terminals``
* ``edb.layout.nets``
* ``edb.layout.find_primitive(...)``

.. code-block:: python

   top_gnd_prims = edb.layout.find_primitive(layer_name="TOP", net_name="GND")
   for prim in top_gnd_prims:
       print(prim.aedt_name, prim.type, prim.layer_name, prim.net_name)

Primitive objects commonly expose information such as ``aedt_name``,
``layer_name``, ``net_name``, ``polygon_data``, ``voids``, and ``area()``.

Use ``edb.modeler`` when the task is not only inspection, but also geometry
creation or geometry-centric helper operations such as creating paths,
polygons, rectangles, and circles.

Navigate by ports, sources, and terminals
-----------------------------------------

For excitation and measurement questions, start from:

* ``edb.terminals``
* ``edb.ports``
* ``edb.sources``
* ``edb.probes``
* ``edb.excitation_manager``

Use these entry points when the question is about which ports exist, how
terminals are organized, which sources are defined, or where probes are placed.

Retrieval cookbook
------------------

These short snippets are meant to be copied into exploratory scripts.

.. code-block:: python

   # Design summary
   print(edb.active_cell.name)
   print(len(edb.stackup.layers))
   print(len(edb.nets.nets))
   print(len(edb.components.instances))
   print(len(edb.layout.primitives))

.. code-block:: python

   # List all stackup layers
   for name, layer in edb.stackup.layers.items():
       print(name, layer.material, layer.thickness)

.. code-block:: python

   # Inspect one net
   net = edb.nets["VDD"]
   print(net.name)
   print(len(net.primitives))
   print(len(net.padstack_instances))

.. code-block:: python

   # Inspect one component
   component = edb.components["J1"]
   print(component.part_name)
   for pin_name, pin in component.pins.items():
       print(pin_name, pin.net_name, pin.position)

.. code-block:: python

   # Find primitives on one layer for one net
   prims = edb.layout.find_primitive(layer_name="TOP", net_name="GND")
   for prim in prims:
       print(prim.aedt_name, prim.type)

A beginner-friendly exploration workflow
----------------------------------------

For a new design, a practical learning sequence is:

1. Open the design with ``from pyedb import Edb``.
2. Pass the backend explicitly with ``grpc=True`` or ``grpc=False``.
3. Print ``edb.cell_names`` and confirm ``edb.active_cell``.
4. Inspect ``edb.stackup.layers`` to understand the physical organization.
5. Inspect ``edb.nets.netlist`` to understand connectivity naming.
6. Inspect ``edb.components.instances`` to understand the placed parts.
7. Use ``edb.layout.primitives`` or ``edb.layout.find_primitive(...)`` for targeted geometry inspection.

This progression gives users a clear view of both the electrical and physical
structure of a design without requiring low-level knowledge of the backend.

How the gRPC architecture maps to the source tree
-------------------------------------------------

If you want to connect the user-facing API to the code base, these source files
are the most relevant:

* ``src/pyedb/generic/design_types.py``

  * Public ``Edb`` entry point.
  * Selects the backend according to the ``grpc`` flag.

* ``src/pyedb/grpc/edb.py``

  * Main gRPC ``Edb`` implementation.
  * Exposes the managers reachable from an open session.

* ``src/pyedb/grpc/edb_init.py``

  * Session startup and database opening and closing.

* ``src/pyedb/grpc/database/layout/layout.py``

  * Layout-oriented traversal.

* ``src/pyedb/grpc/database/stackup.py``

  * Stackup and layer access.

* ``src/pyedb/grpc/database/nets.py`` and ``src/pyedb/grpc/database/net/net.py``

  * Net manager and per-net objects.

* ``src/pyedb/grpc/database/components.py`` and ``src/pyedb/grpc/database/hierarchy/component.py``

  * Component manager and per-component objects.

* ``src/pyedb/grpc/database/modeler.py``

  * Geometry creation helpers and geometry-centric utilities.

Guidelines for writing clear PyEDB scripts
------------------------------------------

When writing user scripts or tutorials, these habits improve readability:

1. Import with ``from pyedb import Edb``.
2. Pass ``grpc=True`` or ``grpc=False`` explicitly.
3. Start from the highest-level manager that matches the question.
4. Prefer named lookups and dictionaries when possible.
5. Keep layer questions in ``stackup``, connectivity questions in ``nets``, and part questions in ``components``.
6. Close the session explicitly with ``edb.close()``.

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=True)
   try:
       print(edb.active_cell.name)
   finally:
       edb.close()

Summary
-------

The key idea for new users is straightforward:

*PyEDB starts from one public entry point, ``from pyedb import Edb``, and the
``grpc`` flag decides which backend is used.*

From there, the design is best explored through focused managers attached to
``Edb``:

* ``stackup`` for layers,
* ``nets`` for connectivity,
* ``components`` for placed parts,
* ``layout`` for inspection,
* ``modeler`` for geometry creation and editing.

If you remember one rule, remember this one:

*start from ``Edb``, choose the manager that matches your engineering question,
and then walk from that manager to the design objects you need.*

