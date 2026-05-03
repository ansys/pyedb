# AGENTS.md - PyEDB AI Coding Agent Guide

## Architecture

PyEDB is a Python API for Ansys Electronics Database (EDB/AEDB) layout design automation. It has a **dual-backend** architecture:

- **`src/pyedb/grpc/`** — Primary backend using gRPC (`ansys-edb-core`) for remote/cross-platform access
- **`src/pyedb/dotnet/`** — **Deprecated** legacy backend using .NET/pythonnet (`ansys-pythonnet`). Do not add new features here.
- **`src/pyedb/configuration/`** — JSON/Pydantic-based configuration system (`cfg_*.py` files) for declarative design setup

Entry point: `from pyedb import Edb`. Backend selection via `grpc=True/False` parameter. Both backends expose the same high-level API surface.

## Project Layout

```
src/pyedb/          # Main package (version from __init__.py via flit)
  dotnet/edb.py     # Legacy Edb class (dotnet backend)
  grpc/edb.py       # gRPC Edb class
  configuration/    # Pydantic models for JSON-driven configuration (cfg_*.py)
  common/           # Shared utilities across backends
  generic/          # Generic helpers
tests/
  unit/             # Fast tests, no license needed (marker: @pytest.mark.unit)
  integration/      # Require EDB/AEDT license (marker: @pytest.mark.integration)
  system/           # Full system tests (marker: @pytest.mark.system)
  example_models/   # Test fixture .aedb projects and data
```

## Development Commands

```bash
pip install -e ".[tests,all]"       # Editable install with test + optional deps
pytest tests/unit -m unit           # Run unit tests only (no license needed)
pytest -m "not slow"                # Skip slow tests
ruff check src/                     # Lint (line-length=120, numpy docstrings)
ruff format src/                    # Format
```

## Conventions & Patterns

- **Build system**: Flit (`flit_core`). Version is dynamic from `__init__.py`.
- **Linting**: Ruff with numpy-style docstrings. Line length 120. Many rules intentionally ignored (see `pyproject.toml [tool.ruff.lint] ignore`).
- **Config models**: `src/pyedb/configuration/cfg_*.py` use Pydantic v2 models. The main orchestrator is `configuration.py`.
- **Test markers**: Use `@pytest.mark.unit`, `@pytest.mark.grpc`, `@pytest.mark.legacy`, `@pytest.mark.no_licence` as appropriate.
- **Changelog**: Uses towncrier. Add fragments to `doc/changelog.d/` named `<PR#>.<type>.md` (types: added, fixed, maintenance, dependencies, documentation, test, miscellaneous).
- **Platform-specific deps**: `pywin32` on Windows, `cffi` on Linux for .NET interop.

## Key Integration Points

- `ansys-edb-core` — gRPC client stubs for EDB server communication
- `ansys-pythonnet` — .NET CLR bridge for legacy dotnet backend
- Pydantic v2 — all configuration/validation models
- `defusedxml`/`xmltodict` — XML parsing for EDB data

## When Modifying Code

- **Prioritize the gRPC backend** (`src/pyedb/grpc/`). New features and bug fixes should target gRPC first.
- The dotnet backend is **deprecated** — avoid adding new functionality there unless explicitly required for maintenance.
- Configuration additions go in a `cfg_*.py` file with a Pydantic model, registered in `configuration.py`.
- Test fixtures (`.aedb` folders) live in `tests/example_models/`.



