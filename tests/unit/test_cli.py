# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import json
from pathlib import Path
import subprocess as _subprocess
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from pyedb.cli import app, common

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


class FakeConfiguration:
    def __init__(self, edb):
        self._edb = edb
        self.loaded = []
        self.export_flags = None

    def get_data_from_db(self, **kwargs):
        self.export_flags = kwargs
        return {"general": {"anti_pads_always_on": False}, "nets": {"signal_nets": ["SIG1"]}}

    def load(self, path, apply_file=False, output_file=None, open_at_the_end=True):
        self.loaded.append(
            {
                "path": str(path),
                "apply_file": apply_file,
                "output_file": output_file,
                "open_at_the_end": open_at_the_end,
            }
        )
        if output_file:
            output_dir = Path(output_file)
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "edb.def").write_text("", encoding="utf-8")


class FakeEdb:
    instances = []

    def __init__(self, edbpath, version=None, isreadonly=False, **kwargs):
        self.initial_path = str(edbpath)
        self.version = version
        self.isreadonly = isreadonly
        self.kwargs = kwargs
        self.saved = False
        self.closed = False
        self.saved_as_paths = []
        self.exported_ipc_path = None
        self.exported_projects = {}
        self.exported_dc_results = None
        self.exported_gds_xml = None
        self.exported_layout_component_path = None
        self.configuration = FakeConfiguration(self)
        self.marker = None

        path = Path(edbpath)
        if path.name.lower() == "edb.def":
            self.edbpath = str(path.parent.resolve())
        elif path.suffix.lower() == ".aedb":
            path.mkdir(parents=True, exist_ok=True)
            (path / "edb.def").write_text("", encoding="utf-8")
            self.edbpath = str(path.resolve())
        elif path.suffix.lower() in {".brd", ".gds", ".xml", ".dxf", ".tgz", ".mcm", ".zip"}:
            output = path.with_suffix(".aedb")
            output.mkdir(parents=True, exist_ok=True)
            (output / "edb.def").write_text("", encoding="utf-8")
            self.edbpath = str(output.resolve())
        else:
            self.edbpath = str(path.resolve())

        FakeEdb.instances.append(self)

    def save(self):
        self.saved = True
        return True

    def save_as(self, path, version=""):
        output = Path(path)
        output.mkdir(parents=True, exist_ok=True)
        (output / "edb.def").write_text("", encoding="utf-8")
        self.saved_as_paths.append(str(output.resolve()))
        return True

    def close(self, terminate_rpc_session=None):
        self.closed = True
        return True

    def export_to_ipc2581(self, edbpath="", anstranslator_full_path="", ipc_path=None):
        output = Path(ipc_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("ipc2581", encoding="utf-8")
        self.exported_ipc_path = str(output.resolve())
        return self.exported_ipc_path

    def _export_aedt_project(
        self,
        export_type,
        path_to_output,
        net_list=None,
        num_cores=None,
        aedt_file_name=None,
        hidden=False,
    ):
        output_dir = Path(path_to_output)
        output_dir.mkdir(parents=True, exist_ok=True)
        file_name = aedt_file_name or export_type
        project_path = output_dir / f"{file_name}.aedt"
        project_path.write_text(export_type, encoding="utf-8")
        self.exported_projects[export_type] = {
            "path": str(project_path.resolve()),
            "net_list": net_list,
            "num_cores": num_cores,
            "aedt_file_name": aedt_file_name,
            "hidden": hidden,
        }
        return str(project_path.resolve())

    def export_hfss(self, path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False):
        return self._export_aedt_project("hfss", path_to_output, net_list, num_cores, aedt_file_name, hidden)

    def export_q3d(self, path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False):
        return self._export_aedt_project("q3d", path_to_output, net_list, num_cores, aedt_file_name, hidden)

    def export_maxwell(self, path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False):
        return self._export_aedt_project("maxwell", path_to_output, net_list, num_cores, aedt_file_name, hidden)

    def export_siwave_dc_results(
        self,
        siwave_project,
        solution_name,
        output_folder=None,
        html_report=True,
        vias=True,
        voltage_probes=True,
        current_sources=True,
        voltage_sources=True,
        power_tree=True,
        loop_res=True,
    ):
        base_dir = Path(output_folder) if output_folder else Path(self.edbpath) / "dc-results"
        base_dir.mkdir(parents=True, exist_ok=True)
        files = []
        requested = {
            "html_report": html_report,
            "vias": vias,
            "voltage_probes": voltage_probes,
            "current_sources": current_sources,
            "voltage_sources": voltage_sources,
            "power_tree": power_tree,
            "loop_res": loop_res,
        }
        for name, enabled in requested.items():
            if enabled:
                output = base_dir / f"{name}.txt"
                output.write_text(name, encoding="utf-8")
                files.append(str(output.resolve()))
        self.exported_dc_results = {
            "siwave_project": siwave_project,
            "solution_name": solution_name,
            "output_folder": str(base_dir.resolve()),
            "files": files,
        }
        return files

    def export_gds_comp_xml(self, comps_to_export, gds_comps_unit="mm", control_path=None):
        output = Path(control_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("<gds />", encoding="utf-8")
        self.exported_gds_xml = {
            "components": comps_to_export,
            "unit": gds_comps_unit,
            "path": str(output.resolve()),
        }
        return True

    def export_layout_component(self, component_path):
        output = Path(component_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("aedbcomp", encoding="utf-8")
        self.exported_layout_component_path = str(output.resolve())
        return True


class FakeCfgData:
    def __init__(self, **kwargs):
        self._data = kwargs

    def to_dict(self):
        return self._data


@pytest.fixture(autouse=True)
def cli_test_environment(monkeypatch, tmp_path):
    FakeEdb.instances.clear()
    common.json_mode = False
    monkeypatch.setattr(common, "get_edb_class", lambda: FakeEdb)
    monkeypatch.setattr(common, "get_cfg_data_class", lambda: FakeCfgData)


@pytest.fixture
def runner():
    return CliRunner()


def make_aedb(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "edb.def").write_text("", encoding="utf-8")
    return path


def test_version_json(runner):
    result = runner.invoke(app, ["--json", "version"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "data" in data and "version" in data["data"]


def test_json_flag_at_export_subgroup_level(runner):
    """--json placed after the export sub-group name must still activate JSON mode."""
    result = runner.invoke(app, ["export", "--json", "ipc2581", "--help"])
    assert result.exit_code == 0


def test_json_flag_at_config_subgroup_level(runner):
    """--json placed after the config sub-group name must still activate JSON mode."""
    result = runner.invoke(app, ["config", "--json", "validate", "--help"])
    assert result.exit_code == 0


def test_export_ipc2581_uses_explicit_edb(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "active.aedb")
    ipc_path = tmp_path / "exports" / "board.xml"

    result = runner.invoke(app, ["export", "ipc2581", "--path", str(edb_path), "--output", str(ipc_path)])

    assert result.exit_code == 0
    assert ipc_path.exists()
    assert FakeEdb.instances[-1].exported_ipc_path == str(ipc_path.resolve())


@pytest.mark.parametrize("command", ["hfss", "q3d", "maxwell"])
def test_export_aedt_projects_use_shared_options(runner, tmp_path, command):
    edb_path = make_aedb(tmp_path / "active.aedb")
    output_dir = tmp_path / command

    result = runner.invoke(
        app,
        [
            "export",
            command,
            "--path",
            str(edb_path),
            "--output",
            str(output_dir),
            "--net",
            "SIG1",
            "--net",
            "SIG2",
            "--num-cores",
            "4",
            "--aedt-file-name",
            "custom_name",
            "--hidden",
        ],
    )

    assert result.exit_code == 0
    exported = FakeEdb.instances[-1].exported_projects[command]
    assert Path(exported["path"]).exists()
    assert exported["net_list"] == ["SIG1", "SIG2"]
    assert exported["num_cores"] == 4
    assert exported["aedt_file_name"] == "custom_name"
    assert exported["hidden"] is True


def test_export_siwave_dc_results(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "active.aedb")
    siwave_project = tmp_path / "board.siw"
    siwave_project.write_text("siwave", encoding="utf-8")
    output_dir = tmp_path / "dc-results"

    result = runner.invoke(
        app,
        [
            "export",
            "siwave-dc-results",
            "--path",
            str(edb_path),
            "--siwave-project",
            str(siwave_project),
            "--solution-name",
            "DC1",
            "--output-folder",
            str(output_dir),
            "--no-power-tree",
        ],
    )

    assert result.exit_code == 0
    exported = FakeEdb.instances[-1].exported_dc_results
    assert exported["solution_name"] == "DC1"
    assert exported["output_folder"] == str(output_dir.resolve())
    assert all(Path(file).exists() for file in exported["files"])
    assert not any("power_tree" in file for file in exported["files"])


def test_export_gds_comp_xml(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "active.aedb")
    xml_path = tmp_path / "gds_components.xml"

    result = runner.invoke(
        app,
        [
            "export",
            "gds-comp-xml",
            "--path",
            str(edb_path),
            "--output",
            str(xml_path),
            "--component",
            "U1",
            "--component",
            "J1",
            "--unit",
            "mil",
        ],
    )

    assert result.exit_code == 0
    assert xml_path.exists()
    assert FakeEdb.instances[-1].exported_gds_xml == {
        "components": ["U1", "J1"],
        "unit": "mil",
        "path": str(xml_path.resolve()),
    }


def test_export_layout_component(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "active.aedb")
    component_path = tmp_path / "layout.aedbcomp"

    result = runner.invoke(
        app,
        ["export", "layout-component", "--path", str(edb_path), "--output", str(component_path)],
    )

    assert result.exit_code == 0
    assert component_path.exists()
    assert FakeEdb.instances[-1].exported_layout_component_path == str(component_path.resolve())


def test_config_apply_uses_explicit_paths(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "source.aedb")
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"general": {"anti_pads_always_on": False}}), encoding="utf-8")
    output_path = tmp_path / "configured.aedb"

    apply_result = runner.invoke(
        app,
        ["config", "apply", "--path", str(edb_path), "--config", str(config_path), "--output", str(output_path)],
    )

    assert apply_result.exit_code == 0
    assert FakeEdb.instances[-1].configuration.loaded[-1]["output_file"] == str(output_path.resolve())


def _make_subprocess_result(returncode=0, stdout="", stderr=""):
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


def test_exec_executes_inline_code(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "scripted.aedb")
    with patch.object(_subprocess, "run", return_value=_make_subprocess_result()) as mock_run:
        result = runner.invoke(app, ["exec", "--path", str(edb_path), "--code", "print('hello')"])

    assert result.exit_code == 0
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd[1] == "-c"
    assert cmd[2] == "print('hello')"
    assert mock_run.call_args.kwargs["env"]["PYEDB_EDB_PATH"] == str(edb_path.resolve())


def test_exec_executes_script_file(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "scripted.aedb")
    script = tmp_path / "my_script.py"
    script.write_text("print('hello')", encoding="utf-8")
    with patch.object(_subprocess, "run", return_value=_make_subprocess_result()) as mock_run:
        result = runner.invoke(app, ["exec", "--path", str(edb_path), str(script)])

    assert result.exit_code == 0
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd[-1] == str(script.resolve())
    assert mock_run.call_args.kwargs["env"]["PYEDB_EDB_PATH"] == str(edb_path.resolve())


def test_exec_propagates_subprocess_failure(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "scripted.aedb")
    with patch.object(_subprocess, "run", return_value=_make_subprocess_result(returncode=1, stderr="boom")):
        result = runner.invoke(app, ["exec", "--path", str(edb_path), "--code", "exit(1)"])

    assert result.exit_code != 0


def test_save_with_path_saves_copy(runner, tmp_path):
    edb_path = make_aedb(tmp_path / "source.aedb")
    output_path = tmp_path / "copy.aedb"

    result = runner.invoke(app, ["save", "--path", str(edb_path), "--output", str(output_path)])

    assert result.exit_code == 0
    assert output_path.exists()
    assert FakeEdb.instances[-1].saved_as_paths[-1] == str(output_path.resolve())


def test_attach_opens_interactive_console_namespace(runner, tmp_path, monkeypatch):
    edb_path = make_aedb(tmp_path / "interactive.aedb")
    captured = {}

    def fake_interact(banner, local):
        captured["banner"] = banner
        captured["local"] = local

    monkeypatch.setattr("pyedb.cli.code.interact", fake_interact)

    result = runner.invoke(app, ["attach", "--path", str(edb_path)])

    assert result.exit_code == 0
    assert "PyEDB interactive console" in captured["banner"]
    assert "edb" in captured["local"]
    assert "save" in captured["local"]
    assert "export_hfss" in captured["local"]
    assert FakeEdb.instances[-1].closed is True
