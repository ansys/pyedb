.. _ref_grpc_edb_design_guide:

gRPC EDB architecture and getting started with PyEDB
====================================================

This document is a user-focused introduction to PyEDB architecture and design
navigation.

Its goal is to help new users understand:

* how to start a PyEDB session,
* how the ``Edb`` entry point relates to the gRPC implementation,
* how to navigate an EDB design from the highest-level API,
* and how to retrieve common information efficiently.

The emphasis is on the gRPC architecture under ``src/pyedb/grpc`` because this
is the long-term supported direction for PyEDB. However, the recommended public
import for users remains the top-level PyEDB entry point.

.. contents::
   :local:
   :depth: 2

The recommended way to import ``Edb``
-------------------------------------

For user scripts and documentation, import ``Edb`` from the top-level package:

.. code-block:: python

   from pyedb import Edb

This is the public entry point that PyEDB users should learn first.

At instantiation time, the ``grpc`` flag selects which backend is used:

* ``grpc=False`` selects the legacy DotNet backend.
* ``grpc=True`` selects the gRPC backend.

.. important::

   The current default is ``grpc=False``.

   This means that if you do not pass the flag explicitly, PyEDB uses the
   legacy backend for now. For new development, it is a good practice to pass
   the flag intentionally so that the backend choice is always explicit in your
   script.

Recommended patterns are:

.. code-block:: python

   from pyedb import Edb

   # Explicitly use the current default backend
   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=False)

.. code-block:: python

   from pyedb import Edb

   # Prefer this for new gRPC-based workflows when the AEDT version supports it
   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=True)

.. note::

   In the source code, the top-level ``pyedb.Edb`` function dispatches to the
   appropriate backend implementation based on the value of ``grpc``.
   When ``grpc=True``, it instantiates the gRPC ``Edb`` class implemented under
   ``src/pyedb/grpc``.

Version support for gRPC
------------------------

The gRPC backend requires a supported AEDT version.

From the current implementation:

* ``grpc=True`` is supported only for AEDT 2025 R2 and later.
* If you request ``grpc=True`` with an older version, PyEDB raises an error.

In practice, this means:

.. code-block:: python

   from pyedb import Edb

   edb = Edb(
       edbpath=r"C:\projects\board.aedb",
       version="2025.2",
       grpc=True,
   )

If you are writing onboarding material or reusable automation scripts, prefer
showing the ``grpc`` flag explicitly.

Why start from ``Edb``
----------------------

``Edb`` is the main session object in PyEDB.

From a user perspective, it is the single entry point to the design:

* it opens or creates the database,
* it selects the active design cell,
* it exposes the main managers used to inspect and edit the design,
* and it gives access to the most common engineering domains such as stackup,
  nets, components, primitives, padstacks, ports, and simulation setup.

A good mental model is:

*``Edb`` is your open design session, and almost every task starts by asking
which part of the design you want to inspect next.*

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

The user-facing architecture can be understood in three layers.

Layer 1: public entry point
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is what users normally write:

.. code-block:: python

   from pyedb import Edb

   edb = Edb(..., grpc=True)

This entry point chooses the backend and returns the corresponding ``Edb``
implementation.

Layer 2: the application session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once instantiated, ``Edb`` becomes the root of your interaction with the
project.

It gives access to high-level managers such as:

* ``edb.layout``
* ``edb.stackup``
* ``edb.nets``
* ``edb.components``
* ``edb.modeler``
* ``edb.padstacks``
* ``edb.materials``
* ``edb.definitions``
* ``edb.excitation_manager``
* ``edb.hfss``
* ``edb.siwave``

Layer 3: domain objects
~~~~~~~~~~~~~~~~~~~~~~~

Those managers return smaller, task-oriented wrapper objects such as:

* net objects,
* component objects,
* primitive objects,
* stackup layer objects,
* padstack instances,
* terminals and ports.

This layered structure is what makes PyEDB approachable: users begin from one
session object and then navigate toward the design domain they need.

A simple architecture view is:

.. code-block:: text

   from pyedb import Edb
            |
            v
          Edb session
            |
            +-- layout      -> primitives, terminals, groups, pin groups
            +-- stackup     -> signal layers, dielectric layers, all layers
            +-- nets        -> net-centric traversal
            +-- components  -> component-centric traversal
            +-- modeler     -> geometry creation and geometry helpers
            +-- padstacks   -> padstack definitions and instances
            +-- hfss        -> HFSS setup workflows
            +-- siwave      -> SIwave setup workflows

How to think about design navigation
------------------------------------

When users are new to PyEDB, the main challenge is not usually syntax. It is
knowing *where to start*.

A practical rule is:

* Start from ``Edb``.
* Pick the manager that matches your engineering question.
* Then walk from that manager to the lower-level objects you need.

Use this decision guide:

* ``I want to understand the design structure`` -> start with ``edb.active_cell`` and ``edb.layout``
* ``I want to inspect layers`` -> start with ``edb.stackup``
* ``I want to work by electrical connectivity`` -> start with ``edb.nets``
* ``I want to work by reference designator or part`` -> start with ``edb.components``
* ``I want to inspect or create geometry`` -> start with ``edb.layout`` or ``edb.modeler``
* ``I want to inspect ports, sources, or terminals`` -> start with ``edb.ports``, ``edb.sources``, or ``edb.terminals``

This document follows that same progression.

Get started: first useful things to inspect
-------------------------------------------

Once an ``Edb`` session is open, the first questions most users ask are:

* Which design am I in?
* Which layers exist?
* Which nets exist?
* Which components exist?
* How many primitives are in the layout?

A small getting-started snippet is:

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

This one example already introduces the most important idea in PyEDB:
information is grouped into clear managers hanging from ``Edb``.

Design scope: database, cell, and layout
----------------------------------------

Before diving into geometry or connectivity, it helps to understand the design
scope.

The most common high-level objects are:

* ``edb.active_db`` for the open database,
* ``edb.cell_names`` for available cell names,
* ``edb.active_cell`` for the current cell,
* ``edb.layout`` for the active layout wrapper.

Typical usage:

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=True)
   try:
       print(edb.cell_names)

       if edb.cell_names:
           edb.active_cell = edb.cell_names[0]

       print("Active cell:", edb.active_cell.name)
       print("Primitive count:", len(edb.layout.primitives))
   finally:
       edb.close()

.. note::

   When you change ``edb.active_cell``, PyEDB refreshes the high-level view of
   the design for that cell. In user code, the safest habit is to reacquire
   objects such as layers, nets, or components after switching cells.

Navigate by stackup
-------------------

Use ``edb.stackup`` when your question is layer-centric.

This is the natural entry point for tasks such as:

* listing all layers,
* separating signal and dielectric layers,
* reading thickness and material information,
* retrieving a specific layer by name.

Common entry points are:

* ``edb.stackup.layers``
* ``edb.stackup.signal_layers``
* ``edb.stackup.all_layers``
* ``edb.stackup["TOP"]``

Example:

.. code-block:: python

   for layer_name, layer in edb.stackup.layers.items():
       print(layer_name, layer.thickness, layer.material)

Useful questions answered by ``stackup``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print("Number of stackup layers:", edb.stackup.num_layers)

   top = edb.stackup["TOP"]
   if top:
       print(top.name)
       print(top.thickness)
       print(top.material)

Why this matters
~~~~~~~~~~~~~~~~

The stackup is often the first stable map of the design. Even before you know
specific net or component names, layer names already tell you how the design is
organized physically.

Navigate by net connectivity
----------------------------

Use ``edb.nets`` when your question is electrical.

This is the best starting point for tasks such as:

* listing nets,
* checking whether a net exists,
* inspecting which primitives belong to a net,
* finding padstack instances or connected components on a net.

Common entry points are:

* ``edb.nets.nets``
* ``edb.nets.netlist``
* ``edb.nets["GND"]``

Example:

.. code-block:: python

   gnd = edb.nets["GND"]
   print("Net:", gnd.name)
   print("Primitive count:", len(gnd.primitives))
   print("Padstack instance count:", len(gnd.padstack_instances))
   print("Connected components:", list(gnd.components))

Why start from nets
~~~~~~~~~~~~~~~~~~~

If your question sounds like one of these, ``edb.nets`` is usually the right
entry point:

* Which objects belong to ``GND``?
* Which components are connected to ``VDD``?
* How many vias are on a given net?
* What geometry is attached to a specific signal?

Navigate by component
---------------------

Use ``edb.components`` when your question is instance-centric.

This is the natural path for tasks such as:

* retrieving one component by reference designator,
* listing a component's pins,
* checking which nets a component touches,
* inspecting component definitions and models.

Common entry points are:

* ``edb.components.instances``
* ``edb.components["U1"]``
* ``edb.components.get_component_by_name("U1")``
* ``edb.components.get_pin_from_component("U1", net_name="GND")``

Example:

.. code-block:: python

   u1 = edb.components["U1"]
   print("Name:", u1.name)
   print("Type:", u1.component_type)
   print("Nets:", sorted(u1.nets))

   for pin_name, pin in u1.pins.items():
       print(pin_name, pin.net_name, pin.layer_name)

Why start from components
~~~~~~~~~~~~~~~~~~~~~~~~~

If your question starts from a reference designator such as ``U1``, ``J1``, or
``R15``, do not search the whole layout first. Start from ``edb.components``.
That keeps the script shorter and makes the intent clearer.

Navigate by layout and primitives
---------------------------------

Use ``edb.layout`` when you want to inspect the active layout directly.

This is the preferred read-oriented entry point for:

* enumerating primitives,
* enumerating terminals,
* enumerating groups and pin groups,
* filtering primitives by layer name, primitive name, or net name.

Common entry points are:

* ``edb.layout.primitives``
* ``edb.layout.terminals``
* ``edb.layout.nets``
* ``edb.layout.find_primitive(...)``

Example:

.. code-block:: python

   top_gnd_prims = edb.layout.find_primitive(layer_name="TOP", net_name="GND")
   for prim in top_gnd_prims:
       print(prim.aedt_name, prim.type, prim.layer_name, prim.net_name)

Primitive objects expose properties such as:

* ``primitive.aedt_name``
* ``primitive.layer_name``
* ``primitive.net_name``
* ``primitive.polygon_data``
* ``primitive.voids``
* ``primitive.area()``

When to use ``modeler``
~~~~~~~~~~~~~~~~~~~~~~~

Use ``edb.modeler`` when the task is not only inspection, but also geometry
creation or geometry-centric helper operations.

Typical examples are:

* ``edb.modeler.create_path(...)``
* ``edb.modeler.create_polygon(...)``
* ``edb.modeler.create_rectangle(...)``
* ``edb.modeler.create_circle(...)``

.. note::

   For read-only primitive traversal, prefer ``edb.layout.primitives``.
   In the gRPC implementation, this is the clearer and more future-facing way
   to inspect layout geometry.

Navigate by ports, sources, and terminals
-----------------------------------------

Not every design question starts from layers or nets. Sometimes users need to
inspect excitations and measurement objects.

In those cases, the most useful entry points are:

* ``edb.terminals``
* ``edb.ports``
* ``edb.sources``
* ``edb.probes``
* ``edb.excitation_manager``

Use these when the question is about:

* which ports exist,
* how terminals are organized,
* which sources are defined,
* or where probes are placed.

Retrieval cookbook
------------------

This section shows short examples that users can adapt immediately.

Design summary
~~~~~~~~~~~~~~

.. code-block:: python

   print("Cell:", edb.active_cell.name)
   print("Layer count:", len(edb.stackup.layers))
   print("Net count:", len(edb.nets.nets))
   print("Component count:", len(edb.components.instances))
   print("Primitive count:", len(edb.layout.primitives))

List all stackup layers
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   for name, layer in edb.stackup.layers.items():
       print(name, layer.material, layer.thickness)

Get one net and inspect its content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   net = edb.nets["VDD"]
   print(net.name)
   print(len(net.primitives))
   print(len(net.padstack_instances))

   for refdes, component in net.components.items():
       print(refdes, component.component_type)

Get one component and inspect its pins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   component = edb.components["J1"]
   print(component.part_name)

   for pin_name, pin in component.pins.items():
       print(pin_name, pin.net_name, pin.position)

Filter pins of a component by net name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   gnd_pins = edb.components.get_pin_from_component("U1", net_name="GND")
   for pin in gnd_pins:
       print(pin.name, pin.net_name)

Find primitives on one layer for one net
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   prims = edb.layout.find_primitive(layer_name="TOP", net_name="GND")
   for prim in prims:
       print(prim.aedt_name, prim.type)

Switch to another cell
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   if len(edb.cell_names) > 1:
       edb.active_cell = edb.cell_names[1]
       print("Now working on:", edb.active_cell.name)

A beginner-friendly exploration workflow
----------------------------------------

For a new design, a practical learning sequence is:

1. Open the design with ``from pyedb import Edb``.
2. Pass the backend explicitly with ``grpc=True`` or ``grpc=False``.
3. Print ``edb.cell_names`` and confirm ``edb.active_cell``.
4. Inspect ``edb.stackup.layers`` to understand the physical organization.
5. Inspect ``edb.nets.netlist`` to understand connectivity naming.
6. Inspect ``edb.components.instances`` to understand design population.
7. Use ``edb.layout.primitives`` or ``edb.layout.find_primitive(...)`` for targeted geometry inspection.

This progression usually gives users a clear view of both the electrical and
physical structure of the board without overwhelming them with low-level API
concepts.

How the gRPC architecture maps to the source tree
-------------------------------------------------

The following source locations are the most useful if you want to understand
how the documented behavior is organized in the code base.

* ``src/pyedb/generic/design_types.py``

  * Public ``Edb`` entry point.
  * Selects the backend according to the ``grpc`` flag.

* ``src/pyedb/grpc/edb.py``

  * Main gRPC ``Edb`` implementation.
  * Exposes the user-facing managers reachable from an open session.

* ``src/pyedb/grpc/edb_init.py``

  * Session startup, database opening and closing, and common database access.

* ``src/pyedb/grpc/database/layout/layout.py``

  * Layout-oriented traversal.
  * Access to primitives, nets, terminals, groups, and pin groups.

* ``src/pyedb/grpc/database/stackup.py``

  * Stackup and layer access.

* ``src/pyedb/grpc/database/nets.py`` and ``src/pyedb/grpc/database/net/net.py``

  * Net manager and per-net wrapper objects.

* ``src/pyedb/grpc/database/components.py`` and ``src/pyedb/grpc/database/hierarchy/component.py``

  * Component manager and per-component wrapper objects.

* ``src/pyedb/grpc/database/modeler.py``

  * Geometry creation helpers and geometry-centric utilities.

* ``src/pyedb/grpc/database/primitive``

  * Primitive wrappers such as path, polygon, rectangle, circle, bondwire, and padstack instance.

Guidelines for writing clear PyEDB scripts
------------------------------------------

When writing user scripts or tutorials, these habits improve readability and
maintainability:

1. Always import with ``from pyedb import Edb``.
2. Always pass ``grpc=True`` or ``grpc=False`` explicitly.
3. Start from the highest-level manager that matches the question.
4. Prefer dictionaries and named lookups over positional indexing when possible.
5. Keep exploration code close to the design domain: layers with ``stackup``, nets with ``nets``, components with ``components``.
6. Close the session explicitly with ``edb.close()``.

A compact production-style skeleton is:

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=r"C:\projects\board.aedb", version="2025.2", grpc=True)
   try:
       # Read or modify the design here
       print(edb.active_cell.name)
   finally:
       edb.close()

Summary
-------

The most important concept for new users is simple:

*PyEDB starts from one public entry point, ``from pyedb import Edb``, and the
``grpc`` flag decides which backend is used.*

From there, the gRPC API is best understood as a set of focused managers
attached to ``Edb``:

* ``stackup`` for layers,
* ``nets`` for connectivity,
* ``components`` for placed parts,
* ``layout`` for inspection,
* ``modeler`` for geometry creation and editing.

If you remember one navigation rule, remember this one:

*start from ``Edb``, choose the manager that matches your engineering question,
and then walk from that manager to the design objects you need.*
