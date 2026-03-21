# `src/pyedb` skill guide

This package is the public face of PyEDB.

## AI symbol index

- public import symbol: `pyedb.Edb`
- public factory implementation: `pyedb.generic.design_types.Edb`
- package re-export file: `src/pyedb/__init__.py`
- .NET backend class: `pyedb.dotnet.edb.Edb`
- gRPC backend class: `pyedb.grpc.edb.Edb`

If a user writes:

```python
from pyedb import Edb
```

this package is responsible for making that import work and for dispatching to the correct backend.

## AI decision table

| If you need to understand... | Read first | Then read |
| --- | --- | --- |
| how `from pyedb import Edb` works | `src/pyedb/__init__.py` | `src/pyedb/generic/design_types.py` |
| constructor arguments and defaults | `src/pyedb/generic/design_types.py` | backend `edb.py` file |
| why `grpc=True` changes behavior | `src/pyedb/generic/design_types.py` | `src/pyedb/grpc/edb.py` |
| default backend behavior | `src/pyedb/generic/design_types.py` | `src/pyedb/dotnet/edb.py` |
| user-facing examples | docs using `from pyedb import Edb` | backend-specific docs only if needed |

## Key files

### `__init__.py`
- Re-exports the public `Edb` symbol.
- Re-exports `Siwave`.
- Carries package version metadata.

### `generic/design_types.py`
This is the most important high-level file in the package.

It defines the overloaded `Edb(...)` factory that selects:

- the .NET implementation when `grpc=False`
- the gRPC implementation when `grpc=True`

It is the first place to inspect when you need to understand:

- the user-visible constructor signature
- default argument values
- backend selection behavior
- deprecation aliases on constructor arguments

## Public API contract

Changes here are high impact because they affect every user workflow.

Preserve these expectations unless the project is intentionally making a breaking change:

- `from pyedb import Edb` remains valid.
- `Edb(..., grpc=False)` continues to route to the .NET backend.
- `Edb(..., grpc=True)` continues to route to the gRPC backend.
- The constructor remains friendly to both existing AEDB paths and importable board files.

## Canonical flows

### Public import flow
1. user writes `from pyedb import Edb`
2. `src/pyedb/__init__.py` re-exports the public symbol
3. `src/pyedb/generic/design_types.py` chooses the backend
4. runtime returns either `pyedb.dotnet.edb.Edb` or `pyedb.grpc.edb.Edb`

### Backend selection flow
1. parse constructor arguments in `generic/design_types.py`
2. inspect `grpc` flag
3. import the selected backend lazily
4. instantiate the backend-specific `Edb`

## Backend split

### .NET backend
- Implementation root: `src/pyedb/dotnet/`
- Current default path from the public factory

### gRPC backend
- Implementation root: `src/pyedb/grpc/`
- New architecture work should generally land here when the feature is gRPC-specific

## When you modify this package

Check all of the following:

1. User import paths still look natural.
2. Constructor typing and overloads still match runtime behavior.
3. Deprecation helpers still point to the right argument names.
4. Documentation examples still use the public import, not an internal backend import, unless the example is intentionally backend-specific.
5. Tests still cover both default and explicit backend selection when relevant.

## Good navigation order

1. `src/pyedb/__init__.py`
2. `src/pyedb/generic/design_types.py`
3. `src/pyedb/grpc/edb.py` or `src/pyedb/dotnet/edb.py`
4. backend manager packages under `database/`

## Common mistakes to avoid

- Do not bypass the factory in user-facing guidance unless the task is explicitly backend-internal.
- Do not move backend-selection logic into `__init__.py`.
- Do not change default argument values casually; they are part of the public feel of the library.
- Do not document gRPC-only behavior as universal behavior.

## Preferred and avoided surfaces for AI-generated changes

Prefer:

- `from pyedb import Edb` in user documentation and tests
- `pyedb.generic.design_types.Edb` when investigating factory behavior
- backend-specific imports only for backend-internal code or tests

Avoid unless explicitly required:

- user guidance that imports `Edb` from a backend module directly
- changing overloads without checking runtime behavior
- changing default `grpc=False` behavior without coordinated docs and tests

## Related skill files

- repository root `SKILL.md`
- `src/pyedb/grpc/SKILL.md`
- `src/pyedb/grpc/database/SKILL.md`



