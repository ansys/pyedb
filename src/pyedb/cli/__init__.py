from __future__ import annotations

import code
from pathlib import Path

try:
    import typer
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "typer is required for the PyEDB CLI. Please install with 'pip install pyedb' or 'pip install typer'."
    ) from e

from pyedb import __version__
from pyedb.cli import common

app = typer.Typer(no_args_is_help=True, help="PyEDB command line interface.")
config_app = typer.Typer(help="Configuration commands.")
export_app = typer.Typer(help="Export commands.")

_JSON_OPTION = typer.Option(False, "--json", help="Output results as JSON.")


def _set_json(json_output: bool) -> None:
    if json_output:
        common.json_mode = True


@app.callback()
def main_callback(
    json_output: bool = _JSON_OPTION,
) -> None:
    """CLI entrypoint for PyEDB."""
    _set_json(json_output)


@export_app.callback()
def export_callback(
    json_output: bool = _JSON_OPTION,
) -> None:
    """Export commands."""
    _set_json(json_output)


@config_app.callback()
def config_callback(
    json_output: bool = _JSON_OPTION,
) -> None:
    """Configuration commands."""
    _set_json(json_output)


@app.command()
def version() -> None:
    """Display the installed PyEDB version."""
    data = {"version": __version__}
    if common.json_mode:
        common.print_output(data=data)
    else:
        typer.echo("PyEDB version: ", nl=False)
        typer.secho(__version__, fg="cyan")


@app.command()
def create(
    path: str = typer.Option(..., "--path", "-p", help="Path for the new .aedb database."),
    version: str = typer.Option(None, "--version", help="AEDT/EDB version to use."),
) -> None:
    """Create a new EDB."""

    def _run() -> None:
        new_path = common.ensure_new_aedb_path(path)
        resolved_version = common.resolve_version(version)
        Edb = common.get_edb_class()
        edb = Edb(new_path, version=resolved_version)
        edb.save()
        resolved_path = edb.edbpath
        edb.close()
        data = {"edb_path": resolved_path, "version": resolved_version}
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Created EDB '{resolved_path}'", fg="green")

    common.run_with_error_handling(_run)


@app.command()
def save(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional output .aedb path. When provided, save as a copy.",
    ),
) -> None:
    """Open the current EDB and save it, optionally to a new path."""

    def _run() -> None:
        with common.managed_edb(edb_path=path) as (db, context):
            if output:
                output_path = common.ensure_new_aedb_path(output)
                db.save_as(output_path)
                data = {"saved": True, "source_edb": context["edb_path"], "edb_path": output_path}
            else:
                db.save()
                data = {"saved": True, "edb_path": db.edbpath}
            if common.json_mode:
                common.print_output(data=data)
            else:
                target_path = data["edb_path"]
                typer.secho(f"Saved '{target_path}'", fg="green")

    common.run_with_error_handling(_run)


def _export_aedt_project(
    method_name: str,
    output_kind: str,
    path: str,
    output: str,
    nets: list[str] | None,
    num_cores: int | None,
    aedt_file_name: str | None,
    hidden: bool,
) -> None:
    """Execute an AEDT project export with a shared option set."""

    def _run() -> None:
        output_path = str(Path(output).expanduser().resolve())
        with common.managed_edb(edb_path=path) as (db, _):
            export_method = getattr(db, method_name, None)
            if export_method is None:
                raise RuntimeError(f"Current backend does not support '{output_kind}' export.")
            exported = export_method(
                output_path,
                net_list=nets or None,
                num_cores=num_cores,
                aedt_file_name=aedt_file_name,
                hidden=hidden,
            )
            data = {
                "exported": True,
                "edb_path": db.edbpath,
                "export_type": output_kind,
                "project_path": exported,
            }
            if common.json_mode:
                common.print_output(data=data)
            else:
                typer.secho(f"{output_kind.upper()} exported to '{exported}'", fg="green")

    common.run_with_error_handling(_run)


@export_app.command("ipc2581")
def export_ipc2581(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(..., "--output", "-o", help="Output IPC2581 file path."),
    translator_path: str = typer.Option(None, "--translator-path", help="Optional Ansys translator executable path."),
) -> None:
    """Export the design to IPC2581."""

    def _run() -> None:
        output_path = str(Path(output).expanduser().resolve())
        with common.managed_edb(edb_path=path) as (db, _):
            exported = db.export_to_ipc2581(
                anstranslator_full_path=translator_path or "",
                ipc_path=output_path,
            )
            data = {"exported": True, "edb_path": db.edbpath, "ipc2581_path": exported}
            if common.json_mode:
                common.print_output(data=data)
            else:
                typer.secho(f"IPC2581 exported to '{exported}'", fg="green")

    common.run_with_error_handling(_run)


@export_app.command("hfss")
def export_hfss(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(..., "--output", "-o", help="Output directory."),
    net: list[str] | None = typer.Option(None, "--net", help="Repeat to export only selected nets."),
    num_cores: int | None = typer.Option(None, "--num-cores", help="Number of cores to use."),
    aedt_file_name: str | None = typer.Option(None, "--aedt-file-name", help="Custom AEDT file name."),
    hidden: bool = typer.Option(False, "--hidden", help="Run Siwave in hidden mode."),
) -> None:
    """Export the design to an HFSS AEDT project."""
    _export_aedt_project("export_hfss", "hfss", path, output, net, num_cores, aedt_file_name, hidden)


@export_app.command("q3d")
def export_q3d(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(..., "--output", "-o", help="Output directory."),
    net: list[str] | None = typer.Option(None, "--net", help="Repeat to export only selected nets."),
    num_cores: int | None = typer.Option(None, "--num-cores", help="Number of cores to use."),
    aedt_file_name: str | None = typer.Option(None, "--aedt-file-name", help="Custom AEDT file name."),
    hidden: bool = typer.Option(False, "--hidden", help="Run Siwave in hidden mode."),
) -> None:
    """Export the design to a Q3D AEDT project."""
    _export_aedt_project("export_q3d", "q3d", path, output, net, num_cores, aedt_file_name, hidden)


@export_app.command("maxwell")
def export_maxwell(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(..., "--output", "-o", help="Output directory."),
    net: list[str] | None = typer.Option(None, "--net", help="Repeat to export only selected nets."),
    num_cores: int | None = typer.Option(None, "--num-cores", help="Number of cores to use."),
    aedt_file_name: str | None = typer.Option(None, "--aedt-file-name", help="Custom AEDT file name."),
    hidden: bool = typer.Option(False, "--hidden", help="Run Siwave in hidden mode."),
) -> None:
    """Export the design to a Maxwell AEDT project."""
    _export_aedt_project("export_maxwell", "maxwell", path, output, net, num_cores, aedt_file_name, hidden)


@export_app.command("siwave-dc-results")
def export_siwave_dc_results(
    siwave_project: str = typer.Option(..., "--siwave-project", help="Path to the SIwave project."),
    solution_name: str = typer.Option(..., "--solution-name", help="DC analysis solution name."),
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output_folder: str | None = typer.Option(None, "--output-folder", help="Optional report output folder."),
    html_report: bool = typer.Option(True, "--html-report/--no-html-report", help="Export the HTML report."),
    vias: bool = typer.Option(True, "--vias/--no-vias", help="Export the vias report."),
    voltage_probes: bool = typer.Option(
        True,
        "--voltage-probes/--no-voltage-probes",
        help="Export the voltage probe report.",
    ),
    current_sources: bool = typer.Option(
        True,
        "--current-sources/--no-current-sources",
        help="Export the current source report.",
    ),
    voltage_sources: bool = typer.Option(
        True,
        "--voltage-sources/--no-voltage-sources",
        help="Export the voltage source report.",
    ),
    power_tree: bool = typer.Option(True, "--power-tree/--no-power-tree", help="Export the power tree image."),
    loop_res: bool = typer.Option(
        True,
        "--loop-res/--no-loop-res",
        help="Export the loop resistance report.",
    ),
) -> None:
    """Export SIwave DC analysis results."""

    def _run() -> None:
        project_path = str(Path(siwave_project).expanduser().resolve())
        reports_folder = str(Path(output_folder).expanduser().resolve()) if output_folder else None
        with common.managed_edb(edb_path=path) as (db, _):
            exported = db.export_siwave_dc_results(
                project_path,
                solution_name,
                output_folder=reports_folder,
                html_report=html_report,
                vias=vias,
                voltage_probes=voltage_probes,
                current_sources=current_sources,
                voltage_sources=voltage_sources,
                power_tree=power_tree,
                loop_res=loop_res,
            )
            data = {
                "exported": True,
                "edb_path": db.edbpath,
                "export_type": "siwave-dc-results",
                "files": exported,
            }
            if common.json_mode:
                common.print_output(data=data)
            else:
                typer.secho(f"SIwave DC results exported ({len(exported)} files)", fg="green")

    common.run_with_error_handling(_run)


@export_app.command("gds-comp-xml")
def export_gds_comp_xml(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(..., "--output", "-o", help="Output XML control file path."),
    component: list[str] | None = typer.Option(
        None,
        "--component",
        help="Repeat to export selected components only. Exports all when omitted.",
    ),
    unit: str = typer.Option("mm", "--unit", help="Output length unit."),
) -> None:
    """Export the GDS component XML control file."""

    def _run() -> None:
        output_path = str(Path(output).expanduser().resolve())
        with common.managed_edb(edb_path=path) as (db, _):
            exported = db.export_gds_comp_xml(component or None, gds_comps_unit=unit, control_path=output_path)
            if not exported:
                raise RuntimeError("Failed to export GDS component XML.")
            data = {
                "exported": True,
                "edb_path": db.edbpath,
                "export_type": "gds-comp-xml",
                "xml_path": output_path,
            }
            if common.json_mode:
                common.print_output(data=data)
            else:
                typer.secho(f"GDS component XML exported to '{output_path}'", fg="green")

    common.run_with_error_handling(_run)


@export_app.command("layout-component")
def export_layout_component(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(..., "--output", "-o", help="Output .aedbcomp path."),
) -> None:
    """Export the current layout as an AEDB component."""

    def _run() -> None:
        output_path = str(Path(output).expanduser().resolve())
        with common.managed_edb(edb_path=path) as (db, _):
            export_method = getattr(db, "export_layout_component", None)
            if export_method is None:
                raise RuntimeError("Current backend does not support layout-component export.")
            exported = export_method(output_path)
            if not exported:
                raise RuntimeError("Failed to export layout component.")
            data = {
                "exported": True,
                "edb_path": db.edbpath,
                "export_type": "layout-component",
                "component_path": output_path,
            }
            if common.json_mode:
                common.print_output(data=data)
            else:
                typer.secho(f"Layout component exported to '{output_path}'", fg="green")

    common.run_with_error_handling(_run)


@config_app.command("export")
def export_config(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    output: str = typer.Option(..., "--output", "-o", help="Output config file (.json or .toml)."),
) -> None:
    """Export configuration data from the current EDB."""

    def _run() -> None:
        with common.managed_edb(edb_path=path) as (db, _):
            payload = db.configuration.get_data_from_db(**common.CONFIG_EXPORT_FLAGS)
        output_path = common.save_config_payload(output, payload)
        data = {"exported": True, "config_path": output_path}
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Configuration exported to '{output_path}'", fg="green")

    common.run_with_error_handling(_run)


@config_app.command("apply")
def apply_config(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    config: str = typer.Option(..., "--config", "-c", help="Config file path (.json or .toml)."),
    output: str = typer.Option(None, "--output", "-o", help="Optional output .aedb path."),
) -> None:
    """Apply a config file to the current EDB."""

    def _run() -> None:
        config_path = common.normalize_path(config)
        if output:
            output_path = common.ensure_new_aedb_path(output)
        else:
            output_path = None
        with common.managed_edb(edb_path=path) as (db, context):
            db.configuration.load(config_path, apply_file=True, output_file=output_path, open_at_the_end=False)
            if not output_path:
                db.save()
        active_path = output_path or context["edb_path"]
        data = {"applied": True, "config_path": config_path, "edb_path": active_path}
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Applied config '{config_path}' to '{active_path}'", fg="green")

    common.run_with_error_handling(_run)


@config_app.command("validate")
def validate_config(path: str = typer.Option(..., "--path", "-p", help="Config file path (.json or .toml).")) -> None:
    """Validate a config file shape without applying it."""

    def _run() -> None:
        payload, normalized_path = common.load_config_payload(path)
        CfgData = common.get_cfg_data_class()
        validated = CfgData(**payload).to_dict()
        data = {"valid": True, "config_path": normalized_path, "sections": sorted(validated)}
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Config '{normalized_path}' is valid", fg="green")

    common.run_with_error_handling(_run)


def exec_code(
    script_path: str | None = typer.Argument(None, help="Python script to execute against the EDB."),
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
    code_snippet: str | None = typer.Option(None, "--code", help="Inline Python code to execute."),
    save_on_success: bool = typer.Option(
        True,
        "--save/--no-save",
        help="Save the database after successful execution.",
    ),
) -> None:
    """Open an EDB, execute Python code, then close it."""

    def _run() -> None:
        if bool(script_path) == bool(code_snippet):
            raise RuntimeError("Provide either a script path or --code.")

        with common.managed_edb(edb_path=path) as (db, context):
            namespace = common.build_console_namespace(db)
            if code_snippet:
                exec(compile(code_snippet, "<pyedb-cli>", "exec"), namespace, namespace)
                executed = "<inline>"
            else:
                script_file = Path(script_path).expanduser()
                if not script_file.exists():
                    raise RuntimeError(f"Script file '{script_file}' does not exist.")
                exec(compile(script_file.read_text(encoding="utf-8"), str(script_file), "exec"), namespace, namespace)
                executed = str(script_file.resolve())

            if save_on_success:
                db.save()

        data = {
            "executed": True,
            "script": executed,
            "edb_path": context["edb_path"],
            "saved": save_on_success,
        }
        if common.json_mode:
            common.print_output(data=data)
        else:
            typer.secho(f"Executed script against '{context['edb_path']}'", fg="green")

    common.run_with_error_handling(_run)


app.command(name="exec")(exec_code)


@app.command()
def attach(
    path: str = typer.Option(..., "--path", "-p", help="EDB path (.aedb folder or edb.def file)."),
) -> None:
    """Open an interactive Python console with a live EDB session."""

    def _run() -> None:
        with common.managed_edb(edb_path=path) as (db, _):
            banner = (
                "PyEDB interactive console\n"
                f"Active EDB: {db.edbpath}\n"
                "Available names: edb, save(), save_as(path), export_ipc2581(...), export_hfss(...), "
                "export_q3d(...), export_maxwell(...), export_siwave_dc_results(...), export_gds_comp_xml(...), "
                "export_layout_component(...), close()\n"
                "Exit with Ctrl-Z then Enter on Windows."
            )
            code.interact(banner=banner, local=common.build_console_namespace(db))

    common.run_with_error_handling(_run)


app.add_typer(export_app, name="export")
app.add_typer(config_app, name="config")

__all__ = ["app"]
