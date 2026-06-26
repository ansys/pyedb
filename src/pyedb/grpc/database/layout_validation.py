# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import inspect
from pathlib import Path
import platform
import re
import shutil
import subprocess  # nosec B404
from typing import Any, List, Optional, Union

from ansys.edb.core.database import ProductIdType as CoreProductIdType
from ansys.edb.core.net.net_class import NetClass as CoreNetClass

from pyedb.generic.general_methods import generate_unique_name, installed_ansys_em_versions
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance


class LayoutValidation:
    """Manages all layout validation capabilities."""

    def __init__(self, pedb: Any) -> None:
        self._pedb = pedb
        self._layout_instance = self._pedb.layout_instance

    def dc_shorts(self, net_list: Optional[Union[str, List[str]]] = None, fix: bool = False) -> List[List[str]]:
        """Find DC shorts on layout.

        Parameters
        ----------
        net_list : str or list[str], optional
            List of nets.
        fix : bool, optional
            If `True`, rename all the nets. (default)
            If `False`, only report dc shorts.

        Returns
        -------
        List[List[str, str]]
            [[net name, net name]].

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("edb_file")
        >>> # Find shorts without fixing
        >>> shorts = edb.layout_validation.dc_shorts()
        >>>
        >>> # Find and fix shorts on specific nets
        >>> fixed_shorts = edb.layout_validation.dc_shorts(net_list=["GND", "VCC"], fix=True)
        """
        if not net_list:
            net_list = list(self._pedb.nets.nets.keys())
        elif isinstance(net_list, str):
            net_list = [net_list]
        _objects_list = {}
        _padstacks_list = {}
        for prim in self._pedb.layout.primitives:
            n_name = prim.net_name
            if n_name in _objects_list:
                _objects_list[n_name].append(prim)
            else:
                _objects_list[n_name] = [prim]
        for pad in list(self._pedb.padstacks.instances.values()):
            n_name = pad.net_name
            if n_name in _padstacks_list:
                _padstacks_list[n_name].append(pad)
            else:
                _padstacks_list[n_name] = [pad]
        dc_shorts = []
        all_shorted_nets = []
        for net in net_list:
            if net in all_shorted_nets:
                continue
            objs = []
            for i in _objects_list.get(net, []):
                objs.append(i)
            for i in _padstacks_list.get(net, []):
                objs.append(i)
            if not len(objs):
                self._pedb.nets[net].delete()
                continue

            connected_objs = objs[0].get_connected_objects()
            connected_objs.append(objs[0])
            net_dc_shorts = [obj for obj in connected_objs]
            all_shorted_nets.append(net)
            if net_dc_shorts:
                dc_nets = list(set([obj.net.name for obj in net_dc_shorts]))
                dc_nets = [i for i in dc_nets if i != net]
                for dc in dc_nets:
                    if dc:
                        dc_shorts.append([net, dc])
                        all_shorted_nets.append(dc)
                if fix:
                    temp = []
                    for i in net_dc_shorts:
                        temp.append(i.net.name)
                    temp_key = set(temp)
                    temp_count = {temp.count(i): i for i in temp_key}
                    temp_count = dict(sorted(temp_count.items()))
                    while True:
                        temp_name = list(temp_count.values()).pop()
                        if not temp_name.lower().startswith("unnamed"):
                            break
                        elif temp_name.lower():
                            break
                        elif len(temp) == 0:
                            break
                    rename_shorts = [i for i in net_dc_shorts if i.net.name != temp_name]
                    for i in rename_shorts:
                        i.net = self._pedb.nets.nets[temp_name]
        return dc_shorts

    def disjoint_nets(
        self,
        net_list: Optional[Union[str, List[str]]] = None,
        keep_only_main_net: bool = False,
        clean_disjoints_less_than: float = 0.0,
        order_by_area: bool = False,
        keep_disjoint_pins: bool = False,
    ) -> List[str]:
        """Find and fix disjoint nets from a given netlist.

        Parameters
        ----------
        net_list : str, list, optional
            List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.
        keep_only_main_net : bool, optional
            Remove all secondary nets other than principal one (the one with more objects in it). Default is `False`.
        clean_disjoints_less_than : bool, optional
          Clean all disjoint nets with area less than specified area in square meters. Default is `0.0` to disable it.
        order_by_area : bool, optional
            Whether if the naming order has to be by number of objects (fastest) or area (slowest but more accurate).
            Default is ``False``.
        keep_disjoint_pins : bool, optional
            Whether if delete disjoints pins not connected to any other primitive or not. Default is ``False``.

        Returns
        -------
        List
            New nets created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("edb_file")
        >>> new_nets = edb.layout_validation.disjoint_nets()
        >>> # Clean disjoints on specific nets with advanced options
        >>> cleaned = edb.layout_validation.disjoint_nets(
        ...     net_list=["GND"],
        ...     keep_only_main_net=True,
        ...     clean_disjoints_less_than=1e-6,
        ...     order_by_area=True
        ... ))
        """
        timer_start = self._pedb.logger.reset_timer()

        def area_calc(elem: List[int]) -> float:
            """Calculate total area for a group of element ids.

            The layout groups are stored as lists of element ids; resolve to
            actual objects using ``obj_dict`` before computing area.
            """
            total = 0.0
            for el_id in elem:
                obj = obj_dict.get(el_id)
                if obj is None:
                    continue
                try:
                    if obj.layout_obj.obj_type.value == 0:
                        if not getattr(obj, "is_void", False):
                            total += obj.area()
                except Exception as e:
                    self._pedb._logger.warning(
                        f"A(n) {type(e).__name__} error occurred while calculating area "
                        f"for element {el_id} - Default value of 0 is used: {str(e)}"
                    )
            return total

        if not net_list:
            net_list = list(self._pedb.nets.nets.keys())
        elif isinstance(net_list, str):
            net_list = [net_list]
        _objects_list = {}
        _padstacks_list = {}
        for prim in self._pedb.layout.primitives:
            if not prim.net.is_null:
                n_name = prim.net.name
                if n_name in _objects_list:
                    _objects_list[n_name].append(prim)
                else:
                    _objects_list[n_name] = [prim]
        for pad in list(self._pedb.padstacks.instances.values()):
            if not pad.net.is_null:
                n_name = pad.net_name
                if n_name in _padstacks_list:
                    _padstacks_list[n_name].append(pad)
                else:
                    _padstacks_list[n_name] = [pad]
        new_nets = []
        disjoints_objects = []
        self._pedb.logger.reset_timer()
        for net in net_list:
            net_groups: List[List[int]] = []
            obj_dict: dict[int, Any] = {}
            for i in _objects_list.get(net, []):
                obj_dict[i.id] = i
            for i in _padstacks_list.get(net, []):
                obj_dict[i.id] = i
            objs = list(obj_dict.values())
            obj_dict_copy = {id: i for id, i in obj_dict.items()}
            l = len(objs)
            while l > 0:
                l1 = [
                    i.layout_obj.edb_uid
                    for i in self._layout_instance.get_connected_objects(objs[0].object_instance, False)
                ]
                l1.append(objs[0].id)
                repetition = False
                for group in net_groups:
                    if set(l1).intersection(group):
                        net_groups.append([i for i in l1 if i not in group])
                        repetition = True
                if not repetition:
                    net_groups.append(l1)
                obj_dict_copy = {id: i for id, i in obj_dict_copy.items() if id not in l1}
                objs = list(obj_dict_copy.values())
                l = len(objs)
            if len(net_groups) > 1:
                if order_by_area:
                    areas = [area_calc(i) for i in net_groups]
                    sorted_list = [x for _, x in sorted(zip(areas, net_groups), reverse=True)]
                else:
                    sorted_list = sorted(net_groups, key=len, reverse=True)
                for disjoints in sorted_list[1:]:
                    if keep_only_main_net:
                        for geo in disjoints:
                            try:
                                obj_dict[geo].delete()
                            except KeyError:
                                pass
                    elif len(disjoints) == 1 and (
                        clean_disjoints_less_than
                        and "area" in dir(obj_dict[disjoints[0]])
                        and obj_dict[disjoints[0]].area() < clean_disjoints_less_than
                    ):
                        try:
                            obj_dict[disjoints[0]].delete()
                        except KeyError:
                            pass
                    elif (
                        len(disjoints) == 1
                        and not keep_disjoint_pins
                        and isinstance(obj_dict[disjoints[0]], PadstackInstance)
                    ):
                        try:
                            obj_dict[disjoints[0]].delete()
                        except KeyError:
                            pass

                    else:
                        new_net_name = generate_unique_name(net, n=6)
                        net_obj = CoreNetClass.create(self._pedb.active_layout.core, new_net_name)
                        # net_obj = self._pedb.nets.find_or_create_net(new_net_name)
                        if net_obj:
                            new_nets.append(new_net_name)
                            for geo in disjoints:
                                try:
                                    obj_dict[geo].net_name = new_net_name
                                except KeyError:
                                    pass
                            disjoints_objects.extend(disjoints)
        self._pedb.logger.info("Found {} objects in {} new nets.".format(len(disjoints_objects), len(new_nets)))
        self._pedb.logger.info_timer("Disjoint Cleanup Completed.", timer_start)

        return new_nets

    def fix_self_intersections(self, net_list: Optional[Union[str, List[str]]] = None) -> bool:
        """Find and fix self intersections from a given netlist.

        Parameters
        ----------
        net_list : str, list, optional
            List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.

        Returns
        -------
        bool

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("edb_file")
        >>> # Fix self-intersections on all nets
        >>> edb.layout_validation.fix_self_intersections()
        >>>
        >>> # Fix self-intersections on specific nets
        >>> edb.layout_validation.fix_self_intersections(net_list=["RF_line"])
        """
        if not net_list:
            net_list = list(self._pedb.nets.nets.keys())
        elif isinstance(net_list, str):
            net_list = [net_list]
        new_prims = []
        for prim in self._pedb.layout.polygons:
            if prim.net_name in net_list:
                new_prims.extend(prim.fix_self_intersections())
        if new_prims:
            self._pedb.logger.info("Self-intersections detected and removed.")
        else:
            self._pedb.logger.info("Self-intersection not found.")
        return True

    def illegal_net_names(self, fix: bool = False) -> None:
        """Find and fix illegal net names.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("edb_file")
        >>> # Identify illegal net names
        >>> edb.layout_validation.illegal_net_names()
        >>>
        >>> # Find and automatically fix illegal names
        >>> edb.layout_validation.illegal_net_names(fix=True)
        """
        pattern = r"[\(\)\\\/:;*?<>\'\"|`~$]"

        nets = self._pedb.nets.nets

        renamed_nets = []
        for net, val in nets.items():
            if re.findall(pattern, net):
                renamed_nets.append(net)
                if fix:
                    new_name = re.sub(pattern, "_", net)
                    val.name = new_name

        self._pedb.logger.info("Found {} illegal net names.".format(len(renamed_nets)))
        return

    def illegal_rlc_values(self, fix: bool = False) -> List[str]:
        """Find and fix RLC illegal values.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("edb_file")
        >>> # Identify components with illegal RLC values
        >>> bad_components = edb.layout_validation.illegal_rlc_values()
        >>>
        # Automatically fix invalid inductor values
        #     edb.layout_validation.illegal_rlc_values(fix=True)
        """
        inductors = self._pedb.components.inductors

        temp = []
        for k, v in inductors.items():
            model = v.component_property.model
            if not len(model.pin_pairs()):  # pragma: no cover
                temp.append(k)
                if fix:
                    v.rlc_values = [0, 1, 0]
        self._pedb.logger.info(f"Found {len(temp)} inductors have no value.")
        return temp

    def padstacks_no_name(self, fix: bool = False) -> None:
        """Identify and fix padstacks without names.

        Examples
        --------
        # Use an Edb instance (see `dc_shorts` example above) and call:
        #     edb.layout_validation.padstacks_no_name()
        #
        # Automatically assign names to unnamed padstacks
        #     edb.layout_validation.padstacks_no_name(fix=True)
        """
        pds = self._pedb.layout.padstack_instances
        counts = 0
        via_count = 1
        for obj in pds:
            name = obj.core.get_product_property(CoreProductIdType.DESIGNER, 11)
            name = str(name).strip("'")
            if name == "":
                counts += 1
                if fix:
                    if not obj.component:
                        obj.set_product_property(CoreProductIdType.DESIGNER, 11, f"Via{via_count}")
                        via_count = via_count + 1
                    else:
                        obj.set_product_property(
                            CoreProductIdType.DESIGNER, 11, f"{obj.component.name}-{obj.component_pin}"
                        )
        self._pedb.logger.info(f"Found {counts}/{len(pds)} padstacks have no name.")

    def delete_empty_pin_groups(self) -> None:
        """Find and delete pin groups that have no pins.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("edb_file")
        >>> edb.layout_validation.delete_empty_pin_groups()

        """
        for name, pg in list(self._pedb.siwave.pin_groups.items()):
            if len(pg.pins) == 0:
                pg.delete()
                self._pedb.logger.info(f"Pin group {name} deleted because it has no pins.")

    def _resolve_siwave_executable(self, executable_name: str) -> Path:
        """Resolve the absolute path to a Siwave CLI executable."""
        is_linux = platform.system().lower() == "linux"
        suffix = "" if is_linux else ".exe"
        executable = f"{executable_name}{suffix}"

        roots = []
        if getattr(self._pedb, "base_path", None):
            roots.append(Path(self._pedb.base_path))
        else:
            installed = installed_ansys_em_versions()
            if installed:
                roots.append(Path(next(reversed(installed.values()))))

        if not roots:
            raise FileNotFoundError("Unable to locate Ansys EM root.")

        # Prefer platform-specific folders first.
        if is_linux:
            rel_paths = (Path("Linux64"), Path())
        else:
            rel_paths = (Path("Win64"), Path())

        for root in roots:
            root = root.expanduser().absolute()

            for rel in rel_paths:
                candidate = root / rel / executable

                # Do not use resolve() here, because on Linux siwave_ng may be
                # a symlink to .answrapper. resolve() would return .answrapper.
                if candidate.is_file():
                    return candidate.absolute()

        raise FileNotFoundError(f"Unable to locate executable '{executable}' under: {', '.join(str(r) for r in roots)}")

    @staticmethod
    def _write_siwave_exec_files(temp_root: Path, validation_lines: list[str]) -> tuple[Path, Path, Path]:
        """Write the three .exec script files consumed by siwave_ng / siwavevalchk."""
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
    def _run_siwave_process(command: list[str], step_name: str, allowed_return_codes: tuple[int, ...] = (0,)) -> None:
        """Run a subprocess and raise on unexpected return codes."""
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

    def run_siwave_validation_check(
        self,
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
        delete_temp_folder: bool = True,
        keep_log_files: bool = True,
    ) -> bool:
        """Run Siwave geometry validation/healing workflow through ``siwave_ng`` and ``siwavevalchk``.

        The active EDB session is closed before external tools run and reopened
        afterwards (only when this session's path matches the target AEDB).

        Parameters
        ----------
        validation_mode : str, optional
            Validation mode passed as ``ValidationMode <mode>``. Default is ``"SYZ"``.
        num_cpus : int, optional
            Number of CPUs for ``SetNumCpus``. Default is ``8``.
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
        delete_temp_folder : bool, optional
            Delete the temporary working folder after workflow completion. Default is ``True``.
        keep_log_files : bool, optional
            Copy all files produced by ``siwavevalchk`` (e.g. ``valchk.prof``,
            ``valchk.results``, ``valchk_error_warning.log``) from the temporary
            results folder ``_temp/<stem>.siwaveresults/valchk`` into a
            ``validation_check_log`` folder next to the source AEDB. Any
            pre-existing ``validation_check_log`` folder is deleted first. Default
            is ``True``.

        Returns
        -------
        bool
            ``True`` when the workflow succeeds and ``edb.def`` is written back.
        """
        source_aedb = Path(self._pedb.edbpath).resolve()

        temp_root = source_aedb.parent / "_temp"
        temp_aedb = temp_root / source_aedb.name

        # Close the active session only when it points to the same AEDB we will process.
        active_session_closed = False
        active_edb_version = None
        if getattr(self._pedb, "db", None) is not None:
            active_edb_version = getattr(self._pedb, "version", None) or getattr(self._pedb, "edbversion", None)
            self._pedb.logger.info("Closing active EDB session before static validation check workflow.")
            self._pedb.close()
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

            create_edb_exec, create_siw_exec, val_check_exec = LayoutValidation._write_siwave_exec_files(
                temp_root=temp_root,
                validation_lines=validation_lines,
            )

            siwave_ng = self._resolve_siwave_executable("siwave_ng")
            siwave_val_check = self._resolve_siwave_executable("siwavevalchk")

            siw_path = (temp_root / f"{source_aedb.stem}.siw").resolve()
            LayoutValidation._run_siwave_process(
                [str(siwave_ng), str(temp_aedb.resolve()), str(create_siw_exec.resolve())],
                "Create SIW",
            )
            # siwavevalchk returns 1 when it reports findings (not a fatal failure).
            LayoutValidation._run_siwave_process(
                [str(siwave_val_check), str(siw_path), str(val_check_exec.resolve())],
                "Validation check",
                allowed_return_codes=(0, 1),
            )
            LayoutValidation._run_siwave_process(
                [str(siwave_ng), str(siw_path), str(create_edb_exec.resolve())],
                "Write healed EDB",
            )

            healed_edb_def = (temp_aedb / "edb.def").resolve()
            if not healed_edb_def.is_file():
                raise RuntimeError(f"Expected healed file not found: {healed_edb_def}")

            shutil.copy2(healed_edb_def, (source_aedb / "edb.def").resolve())

            if keep_log_files:
                valchk_src = temp_root / f"{source_aedb.stem}.siwaveresults" / "valchk"
                log_dest = source_aedb.parent / "validation_check_log"
                if log_dest.exists():
                    shutil.rmtree(log_dest)
                log_dest.mkdir(parents=True, exist_ok=True)
                if valchk_src.is_dir():
                    copied = 0
                    for src_file in valchk_src.iterdir():
                        if src_file.is_file():
                            shutil.copy2(src_file, log_dest / src_file.name)
                            copied += 1
                    self._pedb.logger.info(f"{copied} validation log file(s) copied to: {log_dest}")
                else:
                    msg = f"Validation log folder not found, skipping: {valchk_src}"
                    log_warning = getattr(self._pedb.logger, "warning", None)
                    if callable(log_warning):
                        log_warning(msg)
                    else:
                        self._pedb.logger.info(msg)

            return True
        finally:
            if active_session_closed:
                self._pedb.logger.info("Re-opening EDB session after static validation check workflow.")
                open_params = inspect.signature(self._pedb.open).parameters
                if len(open_params) >= 2 and active_edb_version is not None:
                    self._pedb.open(str(source_aedb), active_edb_version)
                else:
                    self._pedb.open(str(source_aedb))
            if delete_temp_folder and temp_root.exists():
                shutil.rmtree(temp_root)
