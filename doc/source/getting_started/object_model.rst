.. _object_model:

The Edb object model
======================

This page explains how the public ``Edb`` entry point exposes the rest of the PyEDB API, so that once you
understand this one navigation model you can predict where to find any capability without searching the
full API reference.

Every property name below is the exact, current public attribute name on ``pyedb.grpc.edb.Edb`` (the class
returned by ``from pyedb import Edb`` when the gRPC backend is selected). The DotNet backend
(``pyedb.dotnet.edb.Edb``) exposes the same property names unless a "Backend notes" callout says otherwise.

How to obtain the entry point
------------------------------

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath="my_project.aedb", version="2026.1")

``Edb`` is a factory function, not a class: it inspects the ``grpc`` argument (explicit or auto-resolved from
``version``) and returns either a ``pyedb.grpc.edb.Edb`` or a ``pyedb.dotnet.edb.Edb`` instance. Both expose
the same public property names described below. See :doc:`backend_compatibility_migration` for the
selection rule.

Navigation map
--------------

.. code-block:: text

   Edb
   ├── active_cell / cell_names          # Current design
   ├── stackup                            # Layers, materials assigned to layers
   ├── materials                          # Material property library
   ├── components                         # Component instances (indexable: edb["R1"])
   ├── nets                               # Net objects and net names (edb.nets.netlist)
   ├── net_classes / differential_pairs   # Net groupings
   ├── padstacks                          # Padstack definitions and via/pin instances
   ├── excitation_manager                 # Ports and sources (create_port, create_voltage_source, ...)
   ├── modeler / layout                   # Geometry: traces, polygons, primitives
   ├── simulation_setups                  # HFSS / SIwave setup objects
   ├── configuration                      # JSON/TOML declarative configuration interface
   ├── layout_validation                  # DC shorts, illegal net names, and other checks
   └── save() / save_as() / close()       # Lifecycle (see below)

Each object below answers the same eight questions.

``edb.stackup``
----------------

- **How do I obtain it?** ``edb.stackup`` (property, always available once ``Edb`` is initialized).
- **What does it own?** The layer collection: signal, dielectric, and non-stackup layers.
- **What does it return?** ``edb.stackup.layers`` returns ``dict[str, StackupLayer]``, keyed by layer name.
- **Does it mutate the database?** Yes. ``edb.stackup.add_layer(...)`` inserts a layer into the live,
  in-memory database immediately.
- **Does it require saving?** Yes, changes are only persisted to disk on ``edb.save()`` or ``edb.save_as()``.
- **Available on both backends?** Yes.
- **Preferred public API:** :meth:`Stackup.add_layer <pyedb.grpc.database.stackup.Stackup.add_layer>`,
  :attr:`Stackup.layers <pyedb.grpc.database.stackup.Stackup.layers>`.
- **Smallest example:**

  .. code-block:: python

     edb.stackup.add_layer(
         layer_name="TOP", layer_type="signal", material="copper", thickness="35um"
     )
     print(list(edb.stackup.layers.keys()))

``edb.materials``
-------------------

- **How do I obtain it?** ``edb.materials``.
- **What does it own?** Named material definitions (conductors and dielectrics) referenced by stackup
  layers and padstacks.
- **What does it return?** Individual materials are accessed via helper methods such as
  ``add_material`` / ``add_conductor_material`` / ``add_dielectric_material``.
- **Does it mutate the database?** Yes, immediately in memory.
- **Does it require saving?** Yes.
- **Available on both backends?** Yes.
- **Smallest example:**

  .. code-block:: python

     edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)

``edb.components``
---------------------

- **How do I obtain it?** ``edb.components``.
- **What does it own?** Component instances placed on the board.
- **What does it return?** ``edb.components["R1"]`` returns a single
  :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`; ``edb.components.instances``
  returns ``dict[str, Component]`` for all components.
- **Does it mutate the database?** Yes (for example setting ``comp.location`` moves the component
  immediately).
- **Does it require saving?** Yes.
- **Available on both backends?** Yes.
- **Smallest example:**

  .. code-block:: python

     comp = edb.components["R1"]
     print(comp.name, comp.location)

``edb.nets``
--------------

- **How do I obtain it?** ``edb.nets``.
- **What does it own?** All nets in the layout.
- **What does it return?** ``edb.nets["DDR0_DQ0"]`` returns a single
  :class:`Net <pyedb.grpc.database.net.net.Net>`; ``edb.nets.netlist`` returns ``list[str]`` of all net
  names.
- **Does it mutate the database?** Renaming a net (``net.name = "..."``) mutates the database immediately.
- **Does it require saving?** Yes.
- **Available on both backends?** Yes.
- **Smallest example:**

  .. code-block:: python

     net = edb.nets["DDR0_DQ0"]
     net.name = "DDR0_DQ0_NEW"

``edb.padstacks``
-------------------

- **How do I obtain it?** ``edb.padstacks``.
- **What does it own?** Padstack definitions (via/pin geometry templates) and the padstack instances
  placed in the layout.
- **What does it return?** ``edb.padstacks.pins`` returns ``dict[int, PadstackInstance]``.
- **Does it mutate the database?** Yes, for creation/editing operations.
- **Does it require saving?** Yes.
- **Available on both backends?** Yes.

``edb.excitation_manager``
-----------------------------

- **How do I obtain it?** ``edb.excitation_manager`` (returns ``None`` if no active database is open).
- **What does it own?** Port and source creation/management
  (:class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`).
- **What does it return?** ``create_port(terminal, ref_terminal=None, is_circuit_port=False, name=None)``
  returns a port object (``GapPort`` or ``WavePort``);
  ``create_voltage_source(terminal, ref_terminal, magnitude=1, phase=0)`` returns a terminal or ``bool``.
- **Does it mutate the database?** Yes.
- **Does it require saving?** Yes.
- **Available on both backends?** Yes, though the concrete port/terminal object types differ between
  backends because they wrap different underlying terminal implementations.
- **Smallest example:**

  .. code-block:: python

     pin = edb.padstacks.pins[1]
     ref_pin = edb.padstacks.pins[2]
     port = edb.excitation_manager.create_port(pin, ref_terminal=ref_pin)

``edb.modeler`` / ``edb.layout``
-----------------------------------

- **How do I obtain it?** ``edb.modeler`` (geometry creation helpers) or ``edb.layout`` (lower-level
  primitive access).
- **What does it own?** Traces, polygons, and other layout primitives.
- **What does it return?** ``edb.modeler.create_rectangle(...)``, ``edb.modeler.create_trace(...)``, and
  similar creation methods return primitive objects.
- **Does it mutate the database?** Yes.
- **Does it require saving?** Yes.
- **Available on both backends?** Yes.

``edb.simulation_setups``
----------------------------

- **How do I obtain it?** ``edb.simulation_setups``.
- **What does it own?** HFSS and SIwave simulation setup objects for the current cell.
- **What does it return?** ``create_siwave_setup(name=None, start_freq=None, stop_freq=None, ...)`` and
  ``create_siwave_dcir_setup(name=None, **kwargs)`` return setup objects.
- **Does it mutate the database?** Yes.
- **Does it require saving?** Yes.
- **Available on both backends?** Yes.

.. note::

   ``Edb.create_siwave_syz_setup`` and ``Edb.create_siwave_dc_setup`` (directly on the ``Edb`` object)
   still exist but are deprecated thin wrappers around ``edb.simulation_setups.create_siwave_setup`` and
   ``edb.simulation_setups.create_siwave_dcir_setup``. Prefer the ``simulation_setups`` interface in new
   code.

``edb.configuration``
------------------------

- **How do I obtain it?** ``edb.configuration``.
- **What does it own?** The declarative JSON/TOML configuration interface described in
  :doc:`../configuration/index`.
- **What does it return?** Methods to export the current design to a configuration file and apply a
  configuration file to the current design.
- **Does it mutate the database?** Yes, when applying a configuration.
- **Does it require saving?** Yes.
- **Available on both backends?** Yes.

``edb.layout_validation``
----------------------------

- **How do I obtain it?** ``edb.layout_validation``.
- **What does it own?** Validation and repair routines:
  :meth:`dc_shorts <pyedb.grpc.database.layout_validation.LayoutValidation.dc_shorts>`,
  ``disjoint_nets``, ``fix_self_intersections``, ``illegal_net_names``, ``illegal_rlc_values``.
- **What does it return?** Depends on the method; ``dc_shorts()`` returns ``list[list[str]]`` of shorted
  net-name pairs.
- **Does it mutate the database?** Only when called with ``fix=True``.
- **Does it require saving?** Yes, if a fix was applied.
- **Available on both backends?** Yes.

Database lifecycle
--------------------

- ``edb.save()`` persists changes to the current ``edbpath`` in place.
- ``edb.save_as(path, version="")`` persists the database to a **new** location, optionally downgrading
  the EDB format to an older AEDT version. Use this in tutorials and introductory examples so the
  original input database is never modified.
- ``edb.close(terminate_rpc_session=None)`` closes the database. On the gRPC backend, unsaved changes are
  lost, and by default the RPC server shuts down once the last open database is closed (pass
  ``terminate_rpc_session=False`` to keep the server alive for other open databases).
- ``Edb`` supports the context-manager protocol (``with Edb(...) as edb:``), which calls ``close()``
  automatically, including when an exception is raised.

See also
--------

- :doc:`quick_start` for a runnable end-to-end example using several of these objects together.
- :doc:`../user_guide/design_navigation` for the full architecture and backend-selection discussion.
- :doc:`../user_guide/common_tasks` for task-oriented recipes.
- :doc:`backend_compatibility_migration` for backend defaults and version support.
