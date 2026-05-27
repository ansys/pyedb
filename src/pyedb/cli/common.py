from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
from typing import Any

import toml

try:
    import typer
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "typer is required for the PyEDB CLI. Please install with 'pip install pyedb' or 'pip install typer'."
    ) from e

json_mode = False

CONFIG_EXPORT_FLAGS = {
    "general": True,
    "variables": True,
    "stackup": True,
    "package_definitions": True,
    "setups": True,
    "terminals": True,
    "sources": True,
    "ports": True,
    "nets": True,
    "pin_groups": True,
    "operations": True,
    "components": True,
    "boundaries": True,
    "s_parameters": True,
    "padstacks": True,
}


def print_output(data: Any = None, error: str | None = None) -> None:
    """Print structured output for JSON mode."""
    if not json_mode:
        return
    if error:
        typer.echo(json.dumps({"status": "error", "error": str(error)}))
    else:
        typer.echo(json.dumps({"status": "ok", "data": data}))


def run_with_error_handling(func) -> None:
    """Execute a command body with consistent CLI error reporting."""
    try:
        func()
    except typer.Exit:
        raise
    except Exception as e:
        if json_mode:
            print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1) from e


def get_edb_class():
    """Return the runtime Edb class."""
    from pyedb import Edb

    return Edb


def resolve_version(version: str | None) -> str | None:
    """Return *version* if given, otherwise detect the latest installed AEDT version."""
    if version:
        return version
    from pyedb.misc.misc import current_version

    detected = current_version()
    if detected:
        return detected
    return None


def get_cfg_data_class():
    """Return the runtime configuration model class."""
    from pyedb.configuration.cfg_data import CfgData

    return CfgData


def normalize_path(path: str | Path) -> str:
    """Normalize a path to an absolute string."""
    return str(Path(path).expanduser().resolve())


def ensure_existing_edb_path(path: str | Path) -> str:
    """Validate and normalize an existing EDB path."""
    resolved = Path(path).expanduser()
    if resolved.is_file() and resolved.name.lower() == "edb.def":
        return str(resolved.resolve())
    if resolved.is_dir() and resolved.suffix.lower() == ".aedb" and (resolved / "edb.def").exists():
        return str(resolved.resolve())
    raise RuntimeError(f"'{path}' is not an existing .aedb database or edb.def file.")


def ensure_new_aedb_path(path: str | Path) -> str:
    """Validate and normalize a new AEDB directory path."""
    resolved = Path(path).expanduser()
    if resolved.suffix.lower() != ".aedb":
        raise RuntimeError("Output path must end with '.aedb'.")
    if resolved.exists():
        raise RuntimeError(f"'{resolved}' already exists.")
    return str(resolved.resolve())


@contextmanager
def managed_edb(
    edb_path: str,
    version: str | None = None,
    cellname: str | None = None,
    isreadonly: bool = False,
):
    """Open an EDB from an explicit path and close it on exit."""
    existing_path = ensure_existing_edb_path(edb_path)
    context = {
        "edb_path": existing_path,
        "version": version,
        "cellname": cellname,
        "isreadonly": bool(isreadonly),
    }
    Edb = get_edb_class()
    edb = Edb(
        existing_path,
        version=resolve_version(version),
        cellname=cellname,
        isreadonly=isreadonly,
    )
    try:
        yield edb, context
    finally:
        edb.close()


def load_config_payload(path: str | Path) -> tuple[dict[str, Any], str]:
    """Load a JSON or TOML config payload."""
    normalized_path = normalize_path(path)
    config_path = Path(normalized_path)
    if not config_path.exists():
        raise RuntimeError(f"Config file '{config_path}' does not exist.")
    if config_path.suffix.lower() == ".json":
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    elif config_path.suffix.lower() == ".toml":
        payload = toml.loads(config_path.read_text(encoding="utf-8"))
    else:
        raise RuntimeError("Config file must end with '.json' or '.toml'.")
    if not isinstance(payload, dict):
        raise RuntimeError("Config file must contain a JSON/TOML object at the top level.")
    return payload, normalized_path


def save_config_payload(path: str | Path, payload: dict[str, Any]) -> str:
    """Write a JSON or TOML config payload to disk."""
    output_path = Path(path).expanduser()
    if output_path.suffix.lower() not in {".json", ".toml"}:
        output_path = output_path.with_suffix(".json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".json":
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    else:
        output_path.write_text(toml.dumps(payload), encoding="utf-8")
    return str(output_path.resolve())


def build_console_namespace(edb) -> dict[str, Any]:
    """Create the interactive namespace exposed by attach/run commands."""
    return {
        "edb": edb,
        "save": edb.save,
        "save_as": edb.save_as,
        "close": edb.close,
        "export_ipc2581": edb.export_to_ipc2581,
        "export_hfss": getattr(edb, "export_hfss", None),
        "export_q3d": getattr(edb, "export_q3d", None),
        "export_maxwell": getattr(edb, "export_maxwell", None),
        "export_siwave_dc_results": getattr(edb, "export_siwave_dc_results", None),
        "export_gds_comp_xml": getattr(edb, "export_gds_comp_xml", None),
        "export_layout_component": getattr(edb, "export_layout_component", None),
        "Path": Path,
        "json": json,
    }
