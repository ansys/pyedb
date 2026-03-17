.. _ref_grpc_edb_design_guide:
.. _ref_design_navigation:

PyEDB architecture and design navigation
========================================

This guide explains how to get started with PyEDB, how the main architectural
pieces fit together, and how to navigate an EDB design efficiently.

The goal is to help you understand:

* how to start from the public ``Edb`` entry point,
* how backend selection works,
* how PyEDB maps to the underlying EDB technologies,
* and how to move from a design session to layers, nets, components, and geometry.

.. contents::
   :local:
   :depth: 2

For a quick overview of the main gRPC-facing managers, see
:ref:`ref_grpc_manager_overview`. For excitation workflows, see
:ref:`ref_excitation_architecture`. For setup organization, see
:ref:`ref_simulation_setup_architecture`.

Start with the public ``Edb`` entry point
-----------------------------------------

For user scripts and documentation, import ``Edb`` from the top-level package:

.. code-block:: python

   from pyedb import Edb

At instantiation time, the ``grpc`` flag selects the backend:

* ``grpc=False`` uses the DotNet backend.
* ``grpc=True`` uses the gRPC backend.

.. important::

   The current default is ``grpc=False``.

   DotNet is the current official backend. For clarity, it is still a good
   practice to pass ``grpc=True`` or ``grpc=False`` explicitly in user scripts.

Typical usage patterns are:

.. code-block:: python

   from pyedb import Edb

   # Current official backend
   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2026.1", grpc=False)

.. code-block:: python

   from pyedb import Edb

   # New gRPC backend
   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2026.1", grpc=True)

.. note::

   The public ``pyedb.Edb`` entry point selects the backend and returns the
   corresponding implementation. The same high-level entry point is therefore
   used for both backends.

.. _ref_backend_overview:

Backend overview
----------------

PyEDB currently supports two backend implementations behind the same public API.

.. list-table:: Backend selection at a glance
   :header-rows: 1
   :widths: 18 20 20 42

   * - Flag
     - Backend
     - Current status
     - Notes
   * - ``grpc=False``
     - DotNet
     - Current official backend
     - Uses the .NET-based EDB access layer and remains the default behavior
   * - ``grpc=True``
     - gRPC
     - New backend
     - Uses ``ansys-edb-core`` and requires Ansys 2026.1 or later

The gRPC backend requires a supported AEDT version:

* ``grpc=True`` requires Ansys 2026.1 or later.
* Requesting ``grpc=True`` with an older version raises an error.

If you are writing introductory material or reusable automation scripts, always
show the ``grpc`` flag explicitly.

PyEDB architecture at a glance
------------------------------

PyEDB is the user-facing Python library. It provides one high-level API that
can work with two different backends.

A practical way to understand the architecture is:

1. **PyEDB** provides the user API and the ``Edb`` entry point.
2. **DotNet backend** is the current official implementation.
3. **gRPC backend** is the newer implementation and is based on
   ``ansys-edb-core``.
4. **Ansys EDB technologies** provide the underlying database capabilities used
   by those backends.

In practice, users work with PyEDB objects such as ``Edb``, ``Stackup``,
``Nets``, and ``Components``, while PyEDB delegates the low-level work to the
selected backend.

You can picture the user-facing architecture like this:

.. code-block:: text

   from pyedb import Edb
            |
            v
          Edb session
            |
            +-- stackup     -> layers and physical organization
            +-- nets        -> connectivity-centric traversal
            +-- components  -> component-centric traversal
            +-- layout      -> geometry queries, primitives, terminals, groups
            +-- modeler     -> primitive creation and editing
            +-- padstacks   -> padstack definitions and instances
            +-- definitions -> component, package, and bondwire definitions
            +-- layout_validation -> design checks and validation helpers
            +-- excitation_manager -> sources and port excitations
            +-- simulation_setups -> setup containers by solver
            +-- hfss        -> HFSS workflows
            +-- siwave      -> SIwave workflows

.. _ref_grpc_manager_overview:

Key managers exposed by ``Edb``
-------------------------------

In PyEDB implementation, ``Edb`` is the root object and the main entry point
to a set of focused managers. The most important ones are:

.. list-table:: Main managers exposed from ``Edb``
   :header-rows: 1
   :widths: 28 72

   * - Manager
     - Primary role
   * - ``edb.stackup``
     - Access stackup layers, signal layers, dielectric layers, and physical layer properties
   * - ``edb.nets``
     - Navigate the design by electrical connectivity
   * - ``edb.components``
     - Navigate the design by placed parts, reference designators, and pins
   * - ``edb.layout``
     - Run geometry queries and inspect primitives, terminals, groups, and pin groups
   * - ``edb.modeler``
     - Create and edit primitive geometry
   * - ``edb.padstacks``
     - Access padstack definitions and padstack instances
   * - ``edb.definitions``
     - Access component, package, and bondwire definitions
   * - ``edb.layout_validation``
     - Run design checks and validation utilities
   * - ``edb.excitation_manager``
     - Manage source and port excitations in one place
   * - ``edb.simulation_setups``
     - Access setup collections for HFSS, SIwave, DCIR, CPA, Q3D, and RaptorX
   * - ``edb.hfss`` and ``edb.siwave``
     - Access solver-specific workflows; some older excitation helpers remain here as deprecated APIs

For API all details, see the *API reference* section. This section keeps
the architectural view intentionally compact.

What ``Edb`` represents
-----------------------

``Edb`` is the main session object in PyEDB.

From a user perspective, it is the open design session from which almost every
workflow begins. It gives access to the active design and to the managers used
to inspect or edit it.

A useful mental model is:

*``Edb`` is your open design session, and the next step is choosing which part
of the design you want to explore.*

A minimal session looks like this:

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2026.1", grpc=True)
   try:
       print(edb.cell_names)
       print(edb.active_cell.name)
   finally:
       edb.close()

.. _ref_edb_hierarchy:

The EDB hierarchy
-----------------

Understanding the EDB hierarchy makes design navigation much easier.

PyEDB wraps these concepts into user-friendly Python objects. For example:

* ``Edb`` gives you the active project and cell,
* ``edb.stackup`` gives you access to layers,
* ``edb.nets`` gives you net-centric traversal,
* ``edb.components`` gives you component-centric traversal,
* ``edb.layout`` gives you direct access to layout content such as primitives,
* ``edb.definitions`` gives you access to reusable design definitions,
* ``edb.layout_validation`` gives you access to validation tools,
* ``edb.simulation_setups`` gives you access to setup collections by solver.

.. _ref_excitation_architecture:

Sources, ports, and excitations
-------------------------------

One important architectural point in PyEDB API is the role of
``SourceExcitation``.

In PyEDB, source and port excitation workflows are centralized through the
``SourceExcitation`` manager, which is exposed from ``Edb`` as
``edb.excitation_manager``.

This means that, from a class-architecture point of view, excitation-related
operations are no longer best understood as belonging to ``Hfss`` or
``Siwave``. Instead, they are grouped into a dedicated manager focused on
ports, sources, and excitation objects.

Typical entry points are:

* ``edb.excitation_manager``
* ``edb.ports``
* ``edb.sources``
* ``edb.terminals``

.. note::

   ``edb.source_excitation`` still exists, but is deprecated in favor of
   ``edb.excitation_manager``.

This centralization is especially useful because both ``Hfss`` and ``Siwave``
still contain deprecated methods and properties related to ports and
excitations. When documenting the PyEDB architecture, it is therefore clearer
to present ``SourceExcitation`` as the main class for these workflows.

.. _ref_simulation_setup_architecture:

Simulation setup organization
-----------------------------

Simulation setups are also centralized through a dedicated manager:

* ``edb.simulation_setups`` returns a ``SimulationSetups`` object.
* ``edb.setups`` provides a merged view of all setups.

The ``SimulationSetups`` manager groups setups by solver family, including:

* HFSS,
* SIwave,
* SIwave DCIR,
* SIwave CPA,
* Q3D,
* RaptorX,
* and HFSS-PI.

This is the recommended architectural view for PyEDB API because it avoids
scattering setup access across multiple legacy-style properties.

.. note::

   Some convenience properties still exist on ``Edb`` for backward
   compatibility, such as ``edb.hfss_setups``, ``edb.siwave_dc_setups``, and
   ``edb.siwave_ac_setups``. In the gRPC architecture, the preferred entry
   point is ``edb.simulation_setups``.

.. _ref_manager_selection:

Choose the right starting point
-------------------------------

When users are new to PyEDB, the hardest part is usually not syntax. It is
knowing where to start.

The simplest rule is:

* start from ``Edb``,
* pick the manager that matches your engineering question,
* then walk from that manager to the design objects you need.

.. list-table:: Which manager should you use?
   :header-rows: 1
   :widths: 32 22 46

   * - Question
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
   * - Which reusable definitions exist in the design?
     - ``edb.definitions``
     - Inspect component, package, or bondwire definitions
   * - Query geometry or inspect existing primitives
     - ``edb.layout``
     - Find primitives, inspect layout objects, and run geometry-oriented queries
   * - Create or edit primitives
     - ``edb.modeler``
     - Create and edit paths, polygons, rectangles, circles, and related objects
   * - Validate the layout or run checks
     - ``edb.layout_validation``
     - Run validation and inspection helpers
   * - Inspect or create simulation setups
     - ``edb.simulation_setups``
     - Read or create setups by solver family
   * - Which ports, sources, or terminals exist?
     - ``edb.excitation_manager``, ``edb.ports``, or ``edb.terminals``
     - Inspect or create ports, sources, and excitation objects

First inspection steps
----------------------

Once an ``Edb`` session is open, the first useful questions are usually:

* Which cell is active?
* How many layers, nets, components, and primitives exist?
* What is the overall structure of the design?

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2026.1", grpc=True)
   try:
       print("Cells:", edb.cell_names)
       print("Active cell:", edb.active_cell.name)
       print("Layer count:", len(edb.stackup.layers))
       print("Net count:", len(edb.nets.nets))
       print("Component count:", len(edb.components.instances))
       print("Primitive count:", len(edb.layout.primitives))
   finally:
       edb.close()

This already shows the core organization of a PyEDB design: information is
exposed through focused managers attached to ``Edb``.

For a manager-level summary, see :ref:`ref_grpc_manager_overview`.

.. _ref_design_scope_navigation:

Navigate the design by scope
----------------------------

Before diving into layers, nets, or components, it helps to understand the
current design scope.

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

.. _ref_stackup_navigation:

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

.. _ref_net_navigation:

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

.. _ref_component_navigation:

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

.. _ref_definitions_navigation:

Navigate by definitions
-----------------------

Use ``edb.definitions`` when your question is about reusable design definitions
rather than placed instances.

This is the right entry point for tasks such as:

* inspecting component definitions,
* inspecting package definitions,
* inspecting bondwire definitions.

This manager is useful when you want to understand the design library content
that supports placed components and package-related data.

.. _ref_layout_navigation:

Navigate by layout and geometry queries
---------------------------------------

Use ``edb.layout`` when you want to inspect the active layout directly.

This is the preferred entry point for geometry queries and layout inspection.

Typical use cases are:

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

In the intended PyEDB architecture, geometry queries belong to ``Layout``. This
keeps read-oriented geometry access in one place.

Navigate by primitive creation and editing
------------------------------------------

Use ``edb.modeler`` when the task is to create or edit primitive geometry.

Typical examples are:

* creating paths,
* creating polygons,
* creating rectangles,
* creating circles,
* editing primitive geometry.

In PyEDB architecture, ``Modeler`` is best understood as the primitive
creation and editing manager rather than the main entry point for geometry
queries.

.. _ref_validation_setup_navigation:

Navigate by validation and simulation setup
-------------------------------------------

Use ``edb.layout_validation`` when the goal is to inspect design quality,
perform validation, or run layout checks.

Use ``edb.simulation_setups`` when the goal is to inspect, organize, or create
analysis setups for supported solvers.

These two managers are important parts of the PyEDB class architecture because
they keep validation and setup management separated from geometry and
connectivity traversal.

.. _ref_ports_sources_navigation:

Navigate by ports, sources, and terminals
-----------------------------------------

For excitation and measurement questions, start from:

* ``edb.excitation_manager``
* ``edb.terminals``
* ``edb.ports``
* ``edb.sources``
* ``edb.probes``

Use these entry points when the question is about which ports exist, how
terminals are organized, which sources are defined, or where probes are placed.

In PyEDB architecture, this is the preferred way to present excitation
workflows because source and port handling has been consolidated into the
``SourceExcitation`` manager rather than being split conceptually between
``Hfss`` and ``Siwave``.

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
8. Use ``edb.modeler`` when you need to create or edit primitives.

This progression gives users a clear view of both the electrical and physical
structure of a design without requiring low-level knowledge of the backend.

How the architecture maps to the source tree
--------------------------------------------

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

  * Layout-oriented traversal and geometry queries.

* ``src/pyedb/grpc/database/stackup.py``

  * Stackup and layer access.

* ``src/pyedb/grpc/database/source_excitations.py``

  * Source and port excitation management.
  * Central location for excitation workflows in the gRPC architecture.

* ``src/pyedb/grpc/database/simulation_setups.py``

  * Central access to setup collections for multiple solvers.

* ``src/pyedb/grpc/database/definitions.py``

  * Definitions access for reusable objects such as components and packages.

* ``src/pyedb/grpc/database/layout_validation.py``

  * Layout validation helpers.

* ``src/pyedb/grpc/database/nets.py`` and ``src/pyedb/grpc/database/net/net.py``

  * Net manager and per-net objects.

* ``src/pyedb/grpc/database/components.py`` and ``src/pyedb/grpc/database/hierarchy/component.py``

  * Component manager and per-component objects.

* ``src/pyedb/grpc/database/modeler.py``

  * Primitive creation and editing helpers.

Guidelines for writing clear PyEDB scripts
------------------------------------------

When writing user scripts or tutorials, these habits improve readability:

1. Import with ``from pyedb import Edb``.
2. Pass ``grpc=True`` or ``grpc=False`` explicitly.
3. Start from the highest-level manager that matches the question.
4. Prefer named queries and dictionaries when possible.
5. Keep layer questions in ``stackup``, connectivity questions in ``nets``, and part questions in ``components``.
6. Close the session explicitly with ``edb.close()``.

For navigation patterns, see :ref:`ref_manager_selection` and
:ref:`ref_design_scope_navigation`.

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2026.1", grpc=True)
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

