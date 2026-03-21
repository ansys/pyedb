# `src/pyedb/grpc/database/simulation_setup` skill guide

This is the deepest solver-setup layer in the gRPC backend.

Use this directory when the change is about how solver setups are represented, created, or edited after the user reaches `edb.simulation_setups`.

## AI symbol index

- container class: `pyedb.grpc.database.simulation_setups.SimulationSetups`
- aggregate public property: `edb.simulation_setups`
- convenience aggregate mapping: `edb.setups`
- common HFSS wrapper: `pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup`
- common SIwave wrapper: `pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup`

## Entry points

### Container level
- `src/pyedb/grpc/database/simulation_setups.py`
- public access from `edb.simulation_setups`
- convenience aggregate from `edb.setups`

### Per-solver wrapper level
This directory contains the solver-specific wrappers and settings objects, including HFSS, SIwave, DCIR, Q3D, RaptorX, and related sweep/settings helpers.

## AI routing table

| If the task is about... | Start here | Then inspect |
| --- | --- | --- |
| finding all setups on a design | `simulation_setups.py` | the relevant solver property |
| creating a new setup | `SimulationSetups.create(...)` | solver-specific `create(...)` wrapper |
| editing HFSS settings | `hfss_simulation_setup.py` | related HFSS settings modules |
| editing SIwave settings | `siwave_simulation_setup.py` | related SIwave settings modules |
| sweep representation | `sweep_data.py` | the solver setup using it |
| adding a new solver family | `simulation_setups.py` | all affected wrapper and settings files |

## Mental model

There are two layers:

1. a container that discovers and creates setups
2. per-solver wrappers that expose setup-specific properties and operations

Typical flow:

```python
from pyedb import Edb

edb = Edb(edbpath="board.aedb", grpc=True)
setup = edb.simulation_setups.create("setup1", solver="hfss")
setup.add_sweep(name="sweep1", start_freq="1GHz", stop_freq="10GHz", step="100MHz")
```

## Canonical solver-setup flows

### Discover existing setups
1. inspect `edb.simulation_setups`
2. choose a solver family such as `hfss`, `siwave`, or `q3d`
3. inspect the returned wrapper objects

### Create a new setup
1. call `edb.simulation_setups.create(...)` or a solver-specific helper
2. retrieve the returned wrapper
3. edit solver-specific settings on the wrapper
4. add sweep data if relevant

### Extend a solver family
1. update imports in `simulation_setups.py`
2. add cache storage in `SimulationSetups.__init__`
3. add a property accessor for the family
4. update the aggregate `setups` mapping
5. update `create(...)`
6. add targeted tests

## Responsibilities by file type

### `simulation_setups.py`
Owns:
- setup discovery from the active cell
- grouping by solver family
- convenience creation helpers
- aggregate `setups` mapping

### `*_simulation_setup.py`
Owns:
- wrapper behavior for one solver family
- create helpers for that solver type
- setup-specific operations and default conventions

### `*_settings.py`, `*_general_settings.py`, `*_advanced_settings.py`
Owns:
- narrower configuration blocks
- property wrappers around solver-specific options
- reusable setting groups used by setup wrappers

### `sweep_data.py`
Owns sweep-related modeling.

## Important architectural details

### Container aggregation
`SimulationSetups.setups` merges per-solver dictionaries into one mapping. If you add a new solver family, update the aggregate surface as well as the dedicated property.

### Setup creation contract
When adding a new solver type, update all of these places together:

1. imports in `simulation_setups.py`
2. cache dictionaries in `SimulationSetups.__init__`
3. solver-specific property accessors
4. `setups` aggregate mapping
5. `create(...)` branching logic
6. targeted tests

### Special-case setup families
Not every solver-facing configuration is a normal EDB simulation setup object. For example, CPA is handled through product properties rather than the standard simulation setup collection. Preserve those distinctions.

## Naming and API guidance

- Keep solver names consistent with existing lowercase string routing, such as `"hfss"`, `"siwave"`, `"siwave_dcir"`, `"q3d"`, and `"raptor_x"`.
- Prefer extending existing setup wrappers over adding top-level one-off helpers in `grpc/edb.py`.
- Keep convenience helpers in the container thin; push solver-specific behavior down into the relevant wrapper.

## Preferred versus compatibility surfaces

Prefer:

- `edb.simulation_setups` for grouped setup access
- `edb.setups` only when an aggregate cross-solver mapping is the right abstraction
- solver-specific wrapper files for solver-specific behavior

Use caution with:

- top-level convenience helpers that bypass the container
- cross-solver logic embedded inside a single solver wrapper
- changing setup naming or aggregation behavior without updating tests

## Test guidance

Add or update tests in these cases:

- new setup discovery behavior
- new solver creation path
- new sweep or settings wrapper behavior
- changed naming or aggregation logic in `edb.setups`

Prefer:

- unit tests for pure wrapper logic
- system tests for live solver setup creation in an EDB session

## Retrieval hints for AI agents

- Search exact setup-family names first, such as `hfss`, `siwave`, `siwave_dcir`, `q3d`, `raptor_x`, or `hfss_pi`.
- When a task mentions `edb.setups`, trace it back to `edb.simulation_setups.setups` before changing behavior.
- If a setup type is special-cased, verify whether it lives in the active cell simulation collection or in product properties.



