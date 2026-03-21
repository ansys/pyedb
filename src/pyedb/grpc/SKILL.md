# `src/pyedb/grpc` skill guide

This directory contains the gRPC implementation of PyEDB.

The top-level entry point is `src/pyedb/grpc/edb.py`, where `class Edb(EdbInit)` exposes the gRPC design session and all major managers.

## AI symbol index

- root class: `pyedb.grpc.edb.Edb`
- session bootstrap base: `pyedb.grpc.edb_init.EdbInit`
- main manager file: `src/pyedb/grpc/edb.py`
- database package: `src/pyedb/grpc/database/`
- preferred public import for users: `from pyedb import Edb`

## Start here

Open these files in order:

1. `edb.py`
2. `edb_init.py`
3. `database/`

`edb.py` is the control tower. It owns session lifecycle, active design selection, cached managers, and most high-level convenience methods.

## Mental model

A gRPC `Edb` instance does three things:

1. opens or creates the database session
2. tracks the active database, cell, and layout
3. exposes manager properties that wrap focused areas of the model

## Text architecture diagram for gRPC class relationships

```text
from pyedb import Edb
  -> pyedb.generic.design_types.Edb(..., grpc=True)
	 -> pyedb.grpc.edb.Edb : EdbInit
		-> active_db
		-> active_cell
		   -> active_layout / layout : pyedb.grpc.database.layout.layout.Layout
			  -> primitives -> primitive wrappers in `primitive/`
				 -> Path
				 -> Polygon
				 -> Rectangle
				 -> Circle
				 -> PadstackInstance
				 -> Bondwire
			  -> terminals -> terminal wrappers in `terminal/`
			  -> nets -> net wrappers in `net/`
		   -> modeler : pyedb.grpc.database.modeler.Modeler
			  -> creates and edits primitive wrappers
		   -> components : pyedb.grpc.database.components.Components
		   -> padstacks : pyedb.grpc.database.padstacks.Padstacks
		   -> materials : pyedb.grpc.database.definition.materials.Materials
		   -> stackup : pyedb.grpc.database.stackup.Stackup
		   -> definitions : pyedb.grpc.database.definitions.Definitions
			  -> ComponentDef
			  -> PackageDef
			  -> wirebond definition wrappers
		   -> excitation_manager : pyedb.grpc.database.source_excitations.SourceExcitation
			  -> terminals, sources, and port wrappers
		   -> layout_validation : pyedb.grpc.database.layout_validation.LayoutValidation
		   -> simulation_setups : pyedb.grpc.database.simulation_setups.SimulationSetups
			  -> hfss -> HfssSimulationSetup
			  -> siwave -> SiwaveSimulationSetup
			  -> siwave_dcir -> SIWaveDCIRSimulationSetup
			  -> raptor_x -> RaptorXSimulationSetup
			  -> q3d -> Q3DSimulationSetup
			  -> hfss_pi -> HFSSPISimulationSetup
		   -> hfss : pyedb.grpc.database.hfss.Hfss
		   -> siwave : pyedb.grpc.database.siwave.Siwave

shared pattern for most database-layer wrappers
  -> wrapper stores `self._pedb`
  -> wrapper often stores `core`
  -> wrapper exposes a Pythonic API over `ansys.edb.core`
```

## Object instance flow diagram

```text
Edb instance
  -> active_db
	 -> database-level collections and variables
  -> active_cell
	 -> selected design / circuit cell
	 -> active_cell.layout
		-> layout core object passed into Layout(self, active_cell.layout)
		   -> Layout.core
			  -> core.primitives
				 -> wrapper factory in `layout/layout.py`
					-> Path(self._pedb, core_primitive)
					-> Polygon(self._pedb, core_primitive)
					-> Rectangle(self._pedb, core_primitive)
					-> Circle(self._pedb, core_primitive)
					-> PadstackInstance(self._pedb, core_primitive)
					-> Bondwire(self._pedb, core_primitive)
			  -> core.terminals
				 -> terminal wrappers in `terminal/`
			  -> core.nets
				 -> net wrappers in `net/`

cached manager pattern on Edb
  -> `edb.layout` caches `Layout`
  -> `edb.modeler` caches `Modeler`
  -> `edb.components` caches `Components`
  -> `edb.padstacks` caches `Padstacks`
  -> `edb.hfss` caches `Hfss`
  -> `edb.siwave` caches `Siwave`

non-persistent access patterns
  -> `edb.layout_validation` returns a fresh `LayoutValidation`
  -> `edb.definitions` returns a fresh `Definitions`
  -> `edb.simulation_setups` returns a fresh `SimulationSetups`
```

Why this matters for AI agents:

- if the task is about wrapper behavior, trace from `active_cell.layout` to `Layout.core` and then to the wrapper factory
- if the task is about stale state, inspect which `Edb` properties cache managers and which ones rebuild objects on access
- if the task is about the selected design, inspect where `active_cell` is set and where `_init_objects()` is triggered

AI reading order for this diagram:

1. start at `pyedb.generic.design_types.Edb`
2. jump to `pyedb.grpc.edb.Edb`
3. trace the property that matches `edb.<manager>`
4. open the corresponding class under `src/pyedb/grpc/database/`

Typical navigation looks like this:

```python
from pyedb import Edb

edb = Edb(edbpath="board.aedb", grpc=True)
layout = edb.layout
components = edb.components
stackup = edb.stackup
```

## AI routing table

| If the task is about... | Start here | Then inspect |
| --- | --- | --- |
| session open/close and active design state | `src/pyedb/grpc/edb.py` | `src/pyedb/grpc/edb_init.py` |
| manager exposure from `Edb` | `src/pyedb/grpc/edb.py` | matching file under `database/` |
| layout traversal and object lookup | `edb.layout` | `src/pyedb/grpc/database/layout/layout.py` |
| primitive creation and geometry editing | `edb.modeler` | `src/pyedb/grpc/database/modeler.py` |
| ports and sources | `edb.excitation_manager` | `src/pyedb/grpc/database/source_excitations.py` |
| stackup or materials | `edb.stackup`, `edb.materials` | `src/pyedb/grpc/database/stackup.py` |
| definitions | `edb.definitions` | `src/pyedb/grpc/database/definitions.py` |
| validation | `edb.layout_validation` | `src/pyedb/grpc/database/layout_validation.py` |
| setups | `edb.simulation_setups` | `src/pyedb/grpc/database/simulation_setups.py` |

## Manager-to-test mapping

| gRPC manager or surface | Start with these tests | Why |
| --- | --- | --- |
| `edb.layout` | `tests/system/test_edb_layout.py` | layout traversal and query ownership |
| `edb.modeler` | `tests/system/test_edb_modeler.py` | primitive creation and edit workflows |
| `edb.components` | `tests/system/test_edb_components.py` | component-level behavior |
| `edb.nets` | `tests/system/test_edb_nets.py`, `tests/system/test_edb_net_classes.py`, `tests/system/test_edb_extended_nets.py`, `tests/system/test_edb_differential_pairs.py` | net and connectivity surfaces |
| `edb.padstacks` | `tests/system/test_edb_padstacks.py` | padstack definitions and instances |
| `edb.stackup` | `tests/system/test_edb_stackup.py` | layer and stackup topology |
| `edb.materials` | `tests/system/test_edb_materials.py` | material behavior |
| `edb.definitions` | `tests/system/test_edb_definition.py` | reusable definition wrappers |
| `edb.layout_validation` | `tests/system/test_layout_validation.py` | short detection and cleanup flows |
| `edb.siwave` and setup-related flows | `tests/system/test_siwave.py`, `tests/system/test_siwave_features.py` | solver-facing workflows present in the repository |
| public factory and broad gRPC session behavior | `tests/system/test_edb.py`, `tests/system/test_edb_bis.py`, `tests/system/conftest.py` | entry-point and session patterns |

AI rule for tests:

1. start from the public manager path, such as `edb.layout` or `edb.modeler`
2. open the matching property in `src/pyedb/grpc/edb.py`
3. inspect the target implementation file
4. validate against the mapped system test module first

## Property cache matrix for `pyedb.grpc.edb.Edb`

This matrix is based on the current property implementations in `src/pyedb/grpc/edb.py`.

| Property | Backing field or source | Access pattern | AI debugging note |
| --- | --- | --- | --- |
| `active_db` | `self.db` | direct | database handle, not a wrapper cache |
| `active_cell` | `self._active_cell` | stored state | changing it triggers `_init_objects()` |
| `layout` | `self._layout` | cached-once per active cell | reset when `active_cell` changes |
| `active_layout` | `self.layout` | alias | follow `layout` behavior |
| `layout_instance` | `self._layout_instance` | cached-once | depends on `layout.core.layout_instance` |
| `components` | `self._components` | cached-once | stable manager after first access |
| `modeler` | `self._modeler` | cached-once | cache cleared when first created for a cell |
| `padstacks` | `self._padstack` | cached-once | stable manager after first access |
| `nets` | `self._nets` | cached-once | stable manager after first access |
| `extended_nets` | `self._extended_nets` | cached-once | independent cached manager |
| `differential_pairs` | `self._differential_pairs` | cached-once | independent cached manager |
| `hfss` | `self._hfss` | cached-once | stable solver manager |
| `siwave` | `self._siwave` | cached-once | stable solver manager |
| `configuration` | `self._configuration` | cached-once | stable configuration wrapper |
| `excitation_manager` | `self._source_excitation` | returns pre-initialized manager | inspect `_init_objects()` if it is unexpectedly `None` |
| `source_excitation` | `self.excitation_manager` | deprecated alias | use only for compatibility |
| `stackup` | `self._stackup` | recreated on access | not a stable cache despite backing field |
| `materials` | `self._materials` | recreated on access | not a stable cache despite backing field |
| `layout_validation` | `LayoutValidation(self)` | fresh object per access | good place to look for stateless validation logic |
| `definitions` | `Definitions(self)` | fresh object per access | definitions wrapper is rebuilt each time |
| `simulation_setups` | `SimulationSetups(self)` | fresh object per access | aggregated setup view, not a persistent cache |
| `setups` | `self.simulation_setups.setups` | delegated fresh view | trace through `simulation_setups` first |
| `net_classes` | `NetClasses(self)` | fresh object per access | not cached on `Edb` |

Practical AI rule:

- suspect stale state first for cached managers like `layout`, `modeler`, `components`, `nets`, `hfss`, and `siwave`
- suspect recomputation first for `stackup`, `materials`, `definitions`, `layout_validation`, and `simulation_setups`

## Common debugging paths

### 1. Wrong design or wrong objects are being inspected
Symptoms:

- expected objects are missing
- layout queries return data from a different design
- newly active design does not match the returned wrappers

Trace in this order:

1. inspect `edb.active_cell`
2. inspect the `active_cell` setter in `src/pyedb/grpc/edb.py`
3. confirm `_init_objects()` runs when the active cell changes
4. then re-check `edb.layout`, `edb.modeler`, and other managers

### 2. Layout or primitive results look stale after edits
Symptoms:

- geometry queries still show old objects
- lookups do not reflect recent create or delete operations

Trace in this order:

1. inspect `edb.layout` cache behavior
2. inspect `edb.modeler` cache behavior and `Modeler.clear_cache()`
3. verify whether the change happened through `modeler` or another path
4. confirm the relevant test in `tests/system/test_edb_modeler.py` or `tests/system/test_edb_layout.py`

### 3. A manager exists, but returns unexpected wrapper types or raw core objects
Symptoms:

- public API returns raw `ansys.edb.core` objects where PyEDB wrappers are expected
- downstream code fails because wrapper properties are missing

Trace in this order:

1. inspect the property in `src/pyedb/grpc/edb.py`
2. inspect the wrapper factory or manager implementation under `src/pyedb/grpc/database/`
3. confirm whether the public API should return a wrapper or a raw core object
4. add or update a focused test around the public surface

### 4. Source or port behavior is inconsistent
Symptoms:

- a deprecated property is used accidentally
- expected terminals, sources, or ports are missing

Trace in this order:

1. prefer `edb.excitation_manager` over `edb.source_excitation`
2. inspect `src/pyedb/grpc/database/source_excitations.py`
3. verify terminal visibility through `edb.terminals`, `edb.ports`, and `edb.sources`
4. validate with the nearest system test module covering the workflow

### 5. Setup data looks incomplete or duplicated
Symptoms:

- `edb.setups` does not match expectations
- per-solver setup dictionaries and aggregate setup views differ

Trace in this order:

1. inspect `edb.simulation_setups`
2. inspect `src/pyedb/grpc/database/simulation_setups.py`
3. verify whether the setup family is standard or special-cased
4. only then inspect the individual solver wrapper in `simulation_setup/`

### 6. Deprecated name confusion
Symptoms:

- code changes the wrong surface because an alias and a preferred surface both exist
- tests pass on an old alias but miss the intended public API

Trace in this order:

1. search the deprecated API index in the relevant `SKILL.md`
2. inspect the preferred property or method first
3. preserve the deprecated alias only when compatibility is still required
4. test both surfaces only if backward compatibility matters

## Key managers exposed by `Edb`

### Design state
- `active_db`
- `active_cell`
- `active_layout`
- `layout_instance`
- `variables`, `design_variables`, `project_variables`

### Structural managers
- `components`
- `nets`
- `padstacks`
- `materials`
- `stackup`
- `definitions`

### Layout and geometry
- `layout` for traversal and geometry queries
- `modeler` for primitive creation and editing
- `layout_validation` for connectivity and cleanup checks

### Sources and ports
- `excitation_manager`
- `ports`, `sources`, `terminals`

Note: `source_excitation` is a deprecated alias. New code should use `excitation_manager`.

### Simulation-facing managers
- `hfss`
- `siwave`
- `simulation_setups`
- `setups`

## Canonical navigation flows

### Open and navigate a gRPC design
1. instantiate `Edb(edbpath=..., grpc=True)`
2. inspect `edb.active_db`, `edb.active_cell`, and `edb.active_layout`
3. branch into focused managers such as `edb.layout`, `edb.components`, or `edb.stackup`

### Find information in the design
1. start with `edb.layout`
2. inspect `layout.primitives`, `layout.terminals`, or `layout.nets`
3. move to wrappers in `src/pyedb/grpc/database/primitive/` or related subpackages

### Modify geometry safely
1. locate objects through `edb.layout`
2. modify or create through `edb.modeler`
3. refresh caches if the code path keeps cached objects
4. validate with targeted tests

### Create sources and ports
1. inspect `edb.terminals` or `edb.layout.terminals`
2. create through `edb.excitation_manager`
3. verify through `edb.ports` and `edb.sources`

### Create analysis setups
1. configure geometry and excitations
2. use `edb.simulation_setups`
3. drop into solver-specific wrappers only for solver-specific behavior

## Query-versus-edit rule

Keep the current responsibility boundary in mind:

- `layout` is the preferred place to retrieve and search geometry.
- `modeler` is the preferred place to create and modify primitives.

If you are deciding where to add a new helper:

- put read-only traversal and search in `layout`
- put creation, mutation, and geometry authoring in `modeler`

## Preferred versus deprecated surfaces

Prefer in new code:

- `edb.layout`
- `edb.modeler`
- `edb.excitation_manager`
- `edb.simulation_setups`
- `edb.definitions`

Compatibility or deprecated surfaces:

- `edb.source_excitation` is a deprecated alias for `edb.excitation_manager`
- backend-direct imports are acceptable for backend-internal work, but not preferred for user guidance

## How object wrapping works

Most gRPC objects are lightweight Python wrappers around `ansys.edb.core` objects.

Common patterns:

- wrappers receive `self._pedb`
- wrappers keep a `core` object
- manager properties are lazy
- many properties rebuild dictionaries on demand

This means you should be careful about:

- stale cached data after changing the active cell
- stale geometry caches after creating or deleting primitives
- wrapper methods that should return other wrappers, not raw core objects, unless the raw object is intentional

## Version and runtime note

The current gRPC entry point enforces a minimum release gate in `edb.py`.

Before changing that gate or documenting it elsewhere, verify the active project policy and keep the code, docs, and tests aligned.

## Where to go next

- For manager and wrapper patterns, read `database/SKILL.md`.
- For solver setup architecture, read `database/simulation_setup/SKILL.md`.
- For test coverage expectations, read `tests/SKILL.md` at the repository root.






