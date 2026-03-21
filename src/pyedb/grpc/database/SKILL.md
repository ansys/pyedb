# `src/pyedb/grpc/database` skill guide

This package contains the advanced gRPC object model for PyEDB.

If `grpc/edb.py` is the control tower, this package is the design graph.

## AI symbol index

- traversal manager: `pyedb.grpc.database.layout.layout.Layout`
- geometry editor: `pyedb.grpc.database.modeler.Modeler`
- port and source layer: `pyedb.grpc.database.source_excitations.SourceExcitation`
- stackup layer: `pyedb.grpc.database.stackup.Stackup`
- validation layer: `pyedb.grpc.database.layout_validation.LayoutValidation`
- definitions layer: `pyedb.grpc.database.definitions.Definitions`
- setup container: `pyedb.grpc.database.simulation_setups.SimulationSetups`

## Text architecture diagram for gRPC database classes

```text
pyedb.grpc.edb.Edb
  -> layout : Layout
	 -> primitives -> primitive wrappers in `primitive/`
	 -> terminals -> terminal wrappers in `terminal/`
	 -> nets -> net wrappers in `net/`
  -> modeler : Modeler
	 -> creates/edits Path, Polygon, Rectangle, Circle, Bondwire, PadstackInstance
  -> components : Components
  -> padstacks : Padstacks
  -> materials : Materials
  -> stackup : Stackup
  -> definitions : Definitions
	 -> components -> ComponentDef
	 -> packages -> PackageDef
	 -> bondwire definitions
  -> excitation_manager : SourceExcitation
	 -> port wrappers
	 -> source wrappers
	 -> terminal creation helpers
  -> layout_validation : LayoutValidation
  -> simulation_setups : SimulationSetups
	 -> HfssSimulationSetup
	 -> SiwaveSimulationSetup
	 -> SIWaveDCIRSimulationSetup
	 -> RaptorXSimulationSetup
	 -> Q3DSimulationSetup
	 -> HFSSPISimulationSetup

cross-cutting wrapper rule
  -> most objects keep `self._pedb`
  -> many objects wrap a `core` object from `ansys.edb.core`
```

Interpretation for AI agents:

- if the task begins with `edb.layout`, stay in query/traversal code first
- if the task begins with `edb.modeler`, stay in creation/edit code first
- if the task begins with `edb.excitation_manager`, inspect `source_excitations.py`
- if the task begins with `edb.simulation_setups`, inspect `simulation_setups.py` before solver-specific wrappers

## Core design pattern

Most classes in this package follow the same structure:

- keep a reference to the owning `Edb` instance as `self._pedb`
- wrap one `ansys.edb.core` object, usually exposed as `core`
- expose a Pythonic property and method surface above the raw EDB API

This pattern appears in managers, primitive wrappers, terminals, definitions, and solver setup objects.

## AI routing table

| If the task is about... | Preferred module | Why |
| --- | --- | --- |
| finding existing primitives | `layout/layout.py` | query and traversal live here |
| creating or editing primitives | `modeler.py` | mutation belongs here |
| working with individual primitive wrappers | `primitive/` | wrapper classes live here |
| creating ports, sources, or excitations | `source_excitations.py` | shared source/port logic is centralized here |
| working with physical layers or materials | `stackup.py` | stackup topology lives here |
| working with reusable database definitions | `definitions.py` and `definition/` | definitions are separate from placed instances |
| connectivity cleanup or short detection | `layout_validation.py` | validation logic lives here |
| setup discovery or creation | `simulation_setups.py` | container for all solver setups |

## High-value subpackages

### `layout/`
Use this area for design traversal.

Examples:
- `edb.layout.primitives`
- `edb.layout.nets`
- `edb.layout.terminals`
- `edb.layout.find_primitive(...)`

Use `layout` when the task is to find, enumerate, or filter existing design objects.

### `primitive/`
Primitive wrapper classes live here.

Examples:
- `Path`
- `Polygon`
- `Rectangle`
- `Circle`
- `PadstackInstance`
- `Bondwire`

These wrappers provide the object-level surface used by both `layout` and `modeler`.

### `modeler.py`
Use this area for geometry creation and editing.

The current project direction is:

- geometry queries belong in `layout`
- primitive authoring and mutation belong in `modeler`

If a helper creates, reshapes, or deletes geometry, `modeler` is usually the right home.

### `source_excitations.py`
This file centralizes port, source, and excitation workflows that were historically spread across solver-specific surfaces.

Prefer routing new source and port creation work here and exposing it via `edb.excitation_manager`.

### `stackup.py`
This area owns the physical layer stack, layer collections, thickness, materials, and related topology.

### `definitions.py` and `definition/`
This area owns reusable database definitions, such as component definitions, package definitions, and wirebond-related definitions.

Use this area when the change affects reusable definitions rather than placed layout instances.

### `layout_validation.py`
This area handles structural and connectivity checks, such as DC shorts and disjoint-net cleanup.

### `simulation_setups.py` and `simulation_setup/`
This area owns solver setup discovery, creation, and solver-specific wrapper classes.

## Canonical object-navigation flows

### From `Edb` to layout objects
1. start at `edb.layout`
2. enumerate `layout.primitives`, `layout.terminals`, or `layout.nets`
3. inspect the returned wrappers
4. drop into the related wrapper class under `primitive/`, `terminal/`, or `net/`

### From `Edb` to geometry edits
1. locate an object through `edb.layout`
2. use `edb.modeler` to create, reshape, or delete geometry
3. verify indexes or caches still reflect the change

### From `Edb` to reusable definitions
1. inspect placed instances through managers such as `edb.components` or `edb.padstacks`
2. inspect reusable definitions through `edb.definitions`
3. edit the definition wrapper rather than the placed instance when the change is definition-wide

### From `Edb` to solver setup objects
1. use `edb.simulation_setups`
2. retrieve a solver-family mapping or create a new setup
3. drop into the corresponding wrapper under `simulation_setup/`

## Recommended navigation path from `Edb`

### Inspect a design
1. start with `edb.active_cell`
2. move to `edb.layout`
3. inspect wrappers from `layout.primitives`, `layout.terminals`, `layout.nets`
4. move to `edb.components`, `edb.nets`, `edb.padstacks`, or `edb.definitions` as needed

### Modify geometry
1. find objects through `edb.layout`
2. create or edit them through `edb.modeler`
3. clear or refresh caches if the manager keeps indexes

### Create ports or sources
1. inspect terminals through `edb.layout.terminals` or `edb.terminals`
2. create new excitations through `edb.excitation_manager`
3. confirm the new objects through `edb.ports`, `edb.sources`, or `edb.terminals`

### Build simulation flows
1. configure geometry and references
2. create ports and sources
3. create setups through `edb.simulation_setups`
4. use solver-specific managers such as `edb.hfss` or `edb.siwave` only for solver-focused operations

## Architectural boundaries worth preserving

- `layout` is query-first.
- `modeler` is edit-first.
- `definitions` covers reusable definitions, not placed instances.
- `source_excitations` is the shared source and port layer.
- `simulation_setups` is the setup container; `simulation_setup/` contains the per-solver wrappers.

## Preferred versus compatibility surfaces

Prefer in new code:

- `edb.layout` for retrieval and search
- `edb.modeler` for creation and edit
- `edb.excitation_manager` for ports and sources
- `edb.definitions` for reusable definitions
- `edb.simulation_setups` for setup discovery and creation

Treat as compatibility or secondary surfaces:

- deprecated aliases exposed by `edb.py` or `definitions.py`
- duplicate helpers that overlap between managers
- raw `ansys.edb.core` returns when a wrapper surface exists

## Deprecated API index

This list focuses on commonly encountered compatibility surfaces in the gRPC database layer.

| Deprecated or compatibility surface | Preferred surface | Location |
| --- | --- | --- |
| `edb.source_excitation` | `edb.excitation_manager` | `src/pyedb/grpc/edb.py` |
| `edb.excitations` | `edb.ports` | `src/pyedb/grpc/edb.py` |
| `Definitions.component_defs` | `Definitions.components` | `src/pyedb/grpc/database/definitions.py` |
| `Definitions.component` | `Definitions.components` | `src/pyedb/grpc/database/definitions.py` |
| `Definitions.package_defs` | `Definitions.packages` | `src/pyedb/grpc/database/definitions.py` |
| `Definitions.package` | `Definitions.packages` | `src/pyedb/grpc/database/definitions.py` |
| `Definitions.apd_bondwire_defs` | `Definitions.apd_bondwires` | `src/pyedb/grpc/database/definitions.py` |
| `Definitions.jedec4_bondwire_defs` | `Definitions.jedec4_bondwires` | `src/pyedb/grpc/database/definitions.py` |
| `Definitions.jedec5_bondwire_defs` | `Definitions.jedec5_bondwires` | `src/pyedb/grpc/database/definitions.py` |
| `Definitions.add_package_def(...)` | `Definitions.add_package(...)` | `src/pyedb/grpc/database/definitions.py` |

AI rule: when a task mentions one of these names, update or test the preferred surface first, then preserve the compatibility alias only if the repository still guarantees it.

## Common implementation pitfalls

### Cache invalidation
`modeler.py` keeps primitive indexes. If code changes the active cell or mutates primitives, make sure caches are refreshed when necessary.

### Deprecated aliases
Some surfaces are intentionally preserved as deprecated aliases. Keep them stable unless a coordinated removal is planned.

Examples include:
- `source_excitation` -> `excitation_manager`
- several aliases in `definitions.py`

### Wrapper returns
Prefer returning PyEDB wrappers when the public API expects PyEDB objects. Returning raw `ansys.edb.core` objects accidentally makes the API inconsistent.

### Cross-manager duplication
Before adding a new helper, search for similar behavior in:
- `layout.py`
- `modeler.py`
- `source_excitations.py`
- `stackup.py`
- `definitions.py`
- `layout_validation.py`

## Where new code usually belongs

- new search helpers: `layout/`
- new primitive creation helpers: `modeler.py`
- new source or port flows: `source_excitations.py`
- new stackup or material flows: `stackup.py` or `definition/materials.py`
- new reusable database definitions: `definitions.py` or `definition/`
- new solver-setup wrappers: `simulation_setup/`

## Test mapping

- wrapper-only logic: add unit tests first
- live EDB traversal or mutation: add system tests
- backend-specific behavior: use gRPC-marked tests where appropriate

## Retrieval hints for AI agents

- Search by exact manager names first, such as `layout`, `modeler`, `definitions`, or `simulation_setups`.
- If a symbol is reached as `edb.<manager>`, inspect the corresponding property in `src/pyedb/grpc/edb.py` before editing the manager itself.
- When responsibilities seem ambiguous, prefer the query-versus-edit boundary documented above.




