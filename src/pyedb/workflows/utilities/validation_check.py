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

import inspect
from pathlib import Path
import platform
import shutil
import subprocess  # nosec B404
from typing import Any

from pyedb.generic.general_methods import installed_ansys_em_versions


class ValidationCheckWorkflow:
    """Run Siwave validation/healing on an AEDB in static mode."""

    @staticmethod
    def _resolve_executable(active_edb: Any, executable_name: str) -> Path:
        suffix = "" if platform.system().lower() == "linux" else ".exe"
        executable = f"{executable_name}{suffix}"

        roots = []
        if active_edb and getattr(active_edb, "base_path", None):
            roots.append(Path(active_edb.base_path))
        elif active_edb and getattr(active_edb, "ansys_em_path", None):
            roots.append(Path(active_edb.ansys_em_path))
        else:
            installed = installed_ansys_em_versions()
            if installed:
                roots.append(Path(next(reversed(installed.values()))))

        if not roots:
            raise FileNotFoundError("Unable to locate Ansys EM root. Provide `ansys_em_root` explicitly.")

        for root in roots:
            for rel in (Path(), Path("Win64"), Path("Linux64")):
                candidate = (root / rel / executable).resolve()
                if candidate.is_file():
                    return candidate

        raise FileNotFoundError(f"Unable to find executable `{executable}` under: {', '.join(str(r) for r in roots)}")

    @staticmethod
    def _write_exec_files(temp_root: Path, validation_lines: list[str]) -> tuple[Path, Path, Path]:
        create_edb_exec = temp_root / "create_edb.exec"
        create_siw_exec = temp_root / "create_siw.exec"
        val_check_exec = temp_root / "val_check.exec"

        create_edb_exec.write_text("SaveEdb\n", encoding="utf-8")
        create_siw_exec.write_text("SaveSiw\n", encoding="utf-8")
        val_check_exec.write_text("\n".join(validation_lines) + "\n", encoding="utf-8")

        expected = {
            create_edb_exec: "SaveEdb\n",
            create_siw_exec: "SaveSiw\n",
            val_check_exec: "\n".join(validation_lines) + "\n",
        }
        for file_path, expected_content in expected.items():
            if not file_path.is_file() or file_path.read_text(encoding="utf-8") != expected_content:
                raise RuntimeError(f"Failed to create expected workflow file: {file_path}")

        return create_edb_exec, create_siw_exec, val_check_exec

    @staticmethod
    def _run_process(command: list[str], step_name: str, allowed_return_codes: tuple[int, ...] = (0,)) -> None:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # nosec B603
        stdout, stderr = process.communicate()
        if process.returncode not in allowed_return_codes:
            raise RuntimeError(
                f"{step_name} failed with return code {process.returncode}.\n"
                f"Command: {' '.join(command)}\n"
                f"STDOUT: {stdout}\n"
                f"STDERR: {stderr}\n"
                f"Accepted return codes: {allowed_return_codes}"
            )

    @staticmethod
    def run_validation_check(
        edb_path: str,
        validation_mode: str = "SYZ",
        num_cpus: int = 8,
        fix_self_intersections: bool = True,
        fix_disjoint_nets: bool = True,
        check_for_shorted_nets: bool = True,
        fix_overlapping_vias: bool = True,
        check_for_bondwire_errors: bool = True,
        fix_misalignments: bool = True,
        fix_floating_planes: bool = True,
        check_for_unreferenced_traces: bool = True,
        ignore_non_functional_pads: bool = True,
        correct_all_fixable_issues: bool = True,
        strict_disjoint_net_check: bool = True,
        save: bool = True,
        active_edb: Any = None,
    ) -> bool:
        """Run geometry validation/healing workflow through ``siwave_ng`` and ``siwavevalchk``.

        Parameters
        ----------
        edb_path : str
            Path to the source AEDB folder.
        validation_mode : str, optional
            Validation mode value passed as ``ValidationMode <mode>``. The default is ``"SYZ"``.
        num_cpus : int, optional
            Number of CPUs passed through ``SetNumCpus``. The default is ``8``.
        fix_self_intersections : bool, optional
            Add ``FixSelfIntersections`` when ``True``.
        fix_disjoint_nets : bool, optional
            Add ``FixDisjointNets`` when ``True``.
        check_for_shorted_nets : bool, optional
            Add ``CheckForShortedNets`` when ``True``.
        fix_overlapping_vias : bool, optional
            Add ``FixOverlappingVias`` when ``True``.
        check_for_bondwire_errors : bool, optional
            Add ``CheckForBondwireErrors`` when ``True``.
        fix_misalignments : bool, optional
            Add ``FixMisalignments`` when ``True``.
        fix_floating_planes : bool, optional
            Add ``FixFloatingPlanes`` when ``True``.
        check_for_unreferenced_traces : bool, optional
            Add ``CheckForUnreferencedTraces`` when ``True``.
        ignore_non_functional_pads : bool, optional
            Add ``IgnoreNonFunctionalPads`` when ``True``.
        correct_all_fixable_issues : bool, optional
            Add ``CorrectAllFixableIssues`` when ``True``.
        strict_disjoint_net_check : bool, optional
            Add ``StrictDisjointNetCheck`` when ``True``.
        save : bool, optional
            Add ``Save`` when ``True``.
        active_edb : Any, optional
            Active ``Edb`` instance. If open, it is closed before running and reopened afterwards.

        Returns
        -------
        bool
            ``True`` when the workflow succeeds and ``edb.def`` is copied back.
        """
        source_aedb = Path(edb_path).resolve()
        if not source_aedb.is_dir() or source_aedb.suffix.lower() != ".aedb":
            raise ValueError(f"`edb_path` must point to an existing .aedb folder. Received: {edb_path}")

        temp_root = source_aedb.parent / "_temp"
        temp_aedb = temp_root / source_aedb.name

        active_session_closed = False
        active_edb_version = None
        if active_edb and getattr(active_edb, "db", None) is not None:
            # Preserve the version used by the active session so reopen can reuse it when required.
            active_edb_version = getattr(active_edb, "version", None) or getattr(active_edb, "edbversion", None)
            active_edb.logger.info("Closing active EDB session before static validation check workflow.")
            active_edb.close()
            active_session_closed = True

        try:
            if temp_root.exists():
                shutil.rmtree(temp_root)
            temp_root.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source_aedb, temp_aedb)

            validation_lines = [f"ValidationMode {validation_mode}"]
            toggles = [
                (fix_self_intersections, "FixSelfIntersections"),
                (fix_disjoint_nets, "FixDisjointNets"),
                (check_for_shorted_nets, "CheckForShortedNets"),
                (fix_overlapping_vias, "FixOverlappingVias"),
                (check_for_bondwire_errors, "CheckForBondwireErrors"),
                (fix_misalignments, "FixMisalignments"),
                (fix_floating_planes, "FixFloatingPlanes"),
                (check_for_unreferenced_traces, "CheckForUnreferencedTraces"),
                (ignore_non_functional_pads, "IgnoreNonFunctionalPads"),
            ]
            validation_lines.extend(line for enabled, line in toggles if enabled)
            validation_lines.append(f"SetNumCpus {int(num_cpus)}")
            if correct_all_fixable_issues:
                validation_lines.append("CorrectAllFixableIssues")
            if strict_disjoint_net_check:
                validation_lines.append("StrictDisjointNetCheck")
            if save:
                validation_lines.append("Save")

            create_edb_exec, create_siw_exec, val_check_exec = ValidationCheckWorkflow._write_exec_files(
                temp_root=temp_root,
                validation_lines=validation_lines,
            )

            siwave_ng = ValidationCheckWorkflow._resolve_executable(
                active_edb=active_edb,
                executable_name="siwave_ng",
            )
            siwave_val_check = ValidationCheckWorkflow._resolve_executable(
                active_edb=active_edb,
                executable_name="siwavevalchk",
            )

            siw_path = (temp_root / f"{source_aedb.stem}.siw").resolve()
            ValidationCheckWorkflow._run_process(
                [str(siwave_ng), str(temp_aedb.resolve()), str(create_siw_exec.resolve())],
                "Create SIW",
            )
            ValidationCheckWorkflow._run_process(
                [str(siwave_val_check), str(siw_path), str(val_check_exec.resolve())],
                "Validation check",
                allowed_return_codes=(0, 1),
            )
            ValidationCheckWorkflow._run_process(
                [str(siwave_ng), str(siw_path), str(create_edb_exec.resolve())],
                "Write healed EDB",
            )

            healed_edb_def = (temp_aedb / "edb.def").resolve()
            if not healed_edb_def.is_file():
                raise RuntimeError(f"Expected healed file not found: {healed_edb_def}")

            shutil.copy2(healed_edb_def, (source_aedb / "edb.def").resolve())
            return True
        finally:
            if active_session_closed:
                active_edb.logger.info("Re-opening EDB session after static validation check workflow.")
                open_params = inspect.signature(active_edb.open).parameters
                if len(open_params) >= 2 and active_edb_version is not None:
                    active_edb.open(str(source_aedb), active_edb_version)
                else:
                    active_edb.open(str(source_aedb))


def run_validation_check(*args, **kwargs) -> bool:
    """Convenience function for running the validation workflow."""
    return ValidationCheckWorkflow.run_validation_check(*args, **kwargs)
