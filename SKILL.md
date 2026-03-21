# PyEDB skill map

This repository exposes a user-facing `Edb` entry point and two implementation backends.

## AI quick-start

If an AI agent only reads one file first, it should read this file and then jump to the most relevant nested `SKILL.md`.

### Canonical public import

- symbol: `pyedb.Edb`
- import: `from pyedb import Edb`
- backend factory: `src/pyedb/generic/design_types.py`
- gRPC root class: `pyedb.grpc.edb.Edb`
- .NET root class: `pyedb.dotnet.edb.Edb`

## Compact cross-file architecture diagram

```text
user code
  -> from pyedb import Edb
	 -> src/pyedb/__init__.py
		-> src/pyedb/generic/design_types.py
		   -> chooses backend from grpc flag
			  -> src/pyedb/dotnet/edb.py
			  -> src/pyedb/grpc/edb.py
				 -> exposes manager properties
					-> src/pyedb/grpc/database/layout/layout.py
					-> src/pyedb/grpc/database/modeler.py
					-> src/pyedb/grpc/database/source_excitations.py
					-> src/pyedb/grpc/database/stackup.py
					-> src/pyedb/grpc/database/definitions.py
					-> src/pyedb/grpc/database/layout_validation.py
					-> src/pyedb/grpc/database/simulation_setups.py
					   -> src/pyedb/grpc/database/simulation_setup/*

tests and docs
  -> tests/ validates public and backend behavior
  -> doc/ explains public workflows and architecture
```

## Top 20 most important public symbols

These are the highest-value symbols for AI retrieval when the task is user-facing or gRPC-architecture-focused.

1. `pyedb.Edb`
2. `pyedb.generic.design_types.Edb`
3. `pyedb.grpc.edb.Edb`
4. `pyedb.dotnet.edb.Edb`
5. `edb.active_cell`
6. `edb.layout`
7. `edb.modeler`
8. `edb.components`
9. `edb.nets`
10. `edb.padstacks`
11. `edb.stackup`
12. `edb.materials`
13. `edb.definitions`
14. `edb.excitation_manager`
15. `edb.terminals`
16. `edb.ports`
17. `edb.layout_validation`
18. `edb.simulation_setups`
19. `edb.setups`
20. `edb.hfss`

If a symbol lookup starts from one of these names, the next step is usually to inspect the matching property in `src/pyedb/grpc/edb.py` or the public factory in `src/pyedb/generic/design_types.py`.

Start from the public import contract:

```python
from pyedb import Edb

edb = Edb(edbpath="my_design.aedb")
edb_grpc = Edb(edbpath="my_design.aedb", grpc=True)
```

Important defaults and expectations:

- `from pyedb import Edb` is the preferred public import.
- `grpc=False` is the default path today.
- The implementation selection happens in `src/pyedb/generic/design_types.py`.
- The gRPC implementation lives under `src/pyedb/grpc`.
- The legacy official implementation lives under `src/pyedb/dotnet`.

## AI routing table

| If the task is about... | Start here | Then inspect |
| --- | --- | --- |
| public import or constructor behavior | `src/pyedb/__init__.py` | `src/pyedb/generic/design_types.py` |
| backend selection | `src/pyedb/generic/design_types.py` | `src/pyedb/grpc/edb.py`, `src/pyedb/dotnet/edb.py` |
| gRPC architecture | `src/pyedb/grpc/SKILL.md` | `src/pyedb/grpc/edb.py` |
| geometry queries | `src/pyedb/grpc/database/layout/layout.py` | `src/pyedb/grpc/database/SKILL.md` |
| primitive creation or edit | `src/pyedb/grpc/database/modeler.py` | `src/pyedb/grpc/database/SKILL.md` |
| ports and sources | `src/pyedb/grpc/database/source_excitations.py` | `src/pyedb/grpc/edb.py` |
| reusable definitions | `src/pyedb/grpc/database/definitions.py` | `src/pyedb/grpc/database/definition/` |
| stackup and materials | `src/pyedb/grpc/database/stackup.py` | `src/pyedb/grpc/database/definition/materials.py` |
| simulation setups | `src/pyedb/grpc/database/simulation_setups.py` | `src/pyedb/grpc/database/simulation_setup/` |
| test placement | `tests/SKILL.md` | matching file under `tests/system/` or `tests/unit/` |

## Read this repository from top to bottom

### 1. Public package layer
- `src/pyedb/__init__.py`
- `src/pyedb/generic/design_types.py`

This layer defines what users import and how the backend is selected.

### 2. Backend entry points
- `src/pyedb/dotnet/edb.py`
- `src/pyedb/grpc/edb.py`

This layer owns the top-level `Edb` classes for each backend.

### 3. Manager and wrapper layer
- `src/pyedb/grpc/database/`
- `src/pyedb/dotnet/database/`

This layer contains the managers reached from `Edb`, such as components, stackup, nets, padstacks, layout, modeler, definitions, excitations, and simulation setups.

### 4. Validation, workflows, and configuration
- `src/pyedb/configuration/`
- `src/pyedb/workflows/`
- `src/pyedb/extensions/`

### 5. Tests and documentation
- `tests/`
- `doc/`

## High-level architecture

For most user journeys, navigation starts at `Edb` and then branches into managers:

- `edb.components`
- `edb.stackup`
- `edb.materials`
- `edb.padstacks`
- `edb.nets`
- `edb.layout`
- `edb.modeler`
- `edb.layout_validation`
- `edb.excitation_manager`
- `edb.simulation_setups`
- `edb.definitions`

## Canonical user journeys

### Open and inspect a design
1. `from pyedb import Edb`
2. instantiate `Edb(...)`
3. inspect `edb.active_cell`
4. navigate with `edb.layout`, `edb.components`, `edb.nets`, and `edb.stackup`

### Query geometry
1. start from `edb.layout`
2. inspect `edb.layout.primitives` or use `edb.layout.find_primitive(...)`
3. move to primitive wrappers under `src/pyedb/grpc/database/primitive/`

### Modify geometry
1. find existing objects through `edb.layout`
2. create or edit through `edb.modeler`
3. validate behavior with targeted system tests

### Create ports or sources
1. inspect `edb.terminals` or `edb.layout.terminals`
2. create new excitations through `edb.excitation_manager`
3. verify through `edb.ports` or `edb.sources`

### Build simulation flows
1. configure stackup, materials, geometry, and excitations
2. create setups through `edb.simulation_setups`
3. use solver-specific managers such as `edb.hfss` or `edb.siwave` only for solver-focused tasks

Rule of thumb:

- Use `layout` to traverse, inspect, and query design content.
- Use `modeler` to create or edit primitives.
- Use `excitation_manager` for ports and sources.
- Use `definitions` for reusable database definitions.
- Use `simulation_setups` for solver setup containers.

## Preferred versus compatibility surfaces

Prefer these surfaces in new code:

- `from pyedb import Edb`
- `edb.layout` for traversal and geometry queries
- `edb.modeler` for primitive creation and editing
- `edb.excitation_manager` for ports and sources
- `edb.simulation_setups` for setup discovery and creation

Treat these as compatibility or backend-internal surfaces unless the task explicitly requires them:

- direct user-facing imports from `pyedb.grpc.edb` or `pyedb.dotnet.edb`
- deprecated aliases preserved for compatibility
- backend-private details that bypass the public factory

## Deprecated API index

This index is intentionally compact and optimized for retrieval. It is not guaranteed to be exhaustive across the entire repository.

| Deprecated or compatibility surface | Preferred surface | Notes |
| --- | --- | --- |
| `edb.source_excitation` | `edb.excitation_manager` | gRPC alias retained for compatibility |
| `edb.excitations` | `edb.ports` | `ports` is the preferred property |
| `Definitions.component_defs` | `Definitions.components` | definitions alias |
| `Definitions.component` | `Definitions.components` | definitions alias |
| `Definitions.package_defs` | `Definitions.packages` | definitions alias |
| `Definitions.package` | `Definitions.packages` | definitions alias |
| `Definitions.apd_bondwire_defs` | `Definitions.apd_bondwires` | definitions alias |
| `Definitions.jedec4_bondwire_defs` | `Definitions.jedec4_bondwires` | definitions alias |
| `Definitions.jedec5_bondwire_defs` | `Definitions.jedec5_bondwires` | definitions alias |
| `Definitions.add_package_def(...)` | `Definitions.add_package(...)` | method alias |

AI rule: if a task touches one of these names, inspect and prefer the replacement surface first, and only preserve the deprecated surface when backward compatibility is required.

## Repository map for contributors

- See `src/pyedb/SKILL.md` for the public API and backend factory.
- See `src/pyedb/grpc/SKILL.md` for the gRPC `Edb` architecture.
- See `src/pyedb/grpc/database/SKILL.md` for advanced manager and wrapper patterns.
- See `src/pyedb/grpc/database/simulation_setup/SKILL.md` for deep solver setup guidance.
- See `tests/SKILL.md` for the test strategy.

## Working rules

- Keep the public `from pyedb import Edb` workflow stable.
- Treat `src/pyedb/generic/design_types.py` as the public factory contract.
- Prefer targeted tests over broad expensive runs.
- When changing gRPC behavior, update both implementation notes and tests.
- Preserve deprecated aliases unless the project is intentionally removing them.
- Avoid mixing layout-query responsibilities into `modeler` and vice versa.

## Typical validation commands

```powershell
python -m pytest tests\unit
python -m pytest tests\system -m grpc
python -m pytest tests\system\test_edb_modeler.py
python -m ruff check src tests
```




