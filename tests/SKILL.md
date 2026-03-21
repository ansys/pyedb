# `tests` skill guide

Use this directory to understand how PyEDB validates changes.

## AI symbol index

- shared fixture entry point: `tests/conftest.py`
- public constructor under test: `pyedb.Edb`
- common gRPC modeler tests: `tests/system/test_edb_modeler.py`
- common layout tests: `tests/system/test_edb_layout.py`
- common stackup tests: `tests/system/test_edb_stackup.py`

## Test suite layout

- `tests/unit/` for isolated logic and lightweight wrappers
- `tests/system/` for live EDB workflows and backend behavior
- `tests/integration/` for broader multi-part scenarios
- `tests/utils/` and shared fixtures in `tests/conftest.py`

## AI routing table

| If the change is about... | Prefer tests in... | Notes |
| --- | --- | --- |
| public `Edb` import or factory behavior | `tests/unit/` or focused system tests | validate `from pyedb import Edb` behavior |
| gRPC manager behavior | `tests/system/` | often needs a live design |
| wrapper-only helper logic | `tests/unit/` | prefer the lightest test possible |
| primitive creation or edit | `tests/system/test_edb_modeler.py` | pair with layout assertions when needed |
| geometry queries | `tests/system/test_edb_layout.py` | especially when query ownership matters |
| stackup and materials | `tests/system/test_edb_stackup.py` | add definition tests if materials are involved |
| definitions | `tests/system/test_edb_definition.py` | use reusable-definition assertions |
| validation or cleanup | `tests/system/test_layout_validation.py` | check both reporting and fix behavior |
| simulation setup behavior | matching setup-related system tests | add unit coverage for pure wrapper logic |

## Markers

The project defines markers such as:

- `grpc`
- `legacy`
- `unit`
- `integration`
- `system`
- `slow`
- `no_licence`

Use the narrowest marker set that describes the test.

## Backend-aware testing

The public entry point remains:

```python
from pyedb import Edb
```

For gRPC-specific tests, instantiate explicitly with `grpc=True`.

```python
from pyedb import Edb

edb = Edb(edbpath="example.aedb", version="2025.2", grpc=True)
```

## Canonical testing flows

### Add a test for a new manager method
1. identify the public access path, such as `edb.layout` or `edb.modeler`
2. find the nearest existing test module for that manager
3. add the narrowest test that proves the new behavior
4. run the targeted test module first

### Add a test for moved responsibilities
1. verify the new preferred manager, for example `layout` instead of `modeler` for queries
2. update or add tests in the manager that now owns the behavior
3. keep compatibility tests if a deprecated alias still exists

### Add a test for deprecated aliases
1. test the preferred surface
2. test the deprecated alias only when compatibility is still promised
3. assert both behavior and warning semantics when relevant

## Where to add tests

### Public factory behavior
Add tests near the package-level or system-level surfaces that validate `from pyedb import Edb` workflows.

### gRPC manager behavior
If the change affects `edb.layout`, `edb.modeler`, `edb.excitation_manager`, `edb.stackup`, `edb.definitions`, or `edb.simulation_setups`, prefer:

- unit tests when the logic can be isolated
- system tests when a live design is required

### Geometry and primitive behavior
Look first at:
- `tests/system/test_edb_modeler.py`
- `tests/system/test_edb_layout.py`
- `tests/system/test_edb_padstacks.py`
- `tests/system/test_edb_nets.py`

### Stackup, definitions, and validation
Look first at:
- `tests/system/test_edb_stackup.py`
- `tests/system/test_edb_definition.py`
- `tests/system/test_layout_validation.py`

## Practical rules

- Prefer targeted tests over running the entire suite.
- Reuse existing fixtures and example models where possible.
- Close live sessions cleanly in gRPC flows.
- If you add a deprecated alias, test both the preferred surface and the alias when compatibility matters.
- If you move a responsibility from one manager to another, update tests to reflect the new ownership boundary.

## Preferred versus avoided testing patterns

Prefer:

- public API entry points over backend-internal setup in tests, unless the test is explicitly backend-internal
- the narrowest fixture and smallest example model that reproduces the behavior
- one focused assertion cluster per behavior change

Avoid unless necessary:

- broad suite runs before a focused test passes
- tests that reach around the public manager surface when the public path is the behavior under change
- duplicating the same behavior in multiple test modules without a good reason

## Useful commands

```powershell
python -m pytest tests\unit
python -m pytest tests\system\test_edb_modeler.py
python -m pytest tests\system -m grpc
python -m pytest tests\system\test_edb_stackup.py
```



