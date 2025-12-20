# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Provides the main interface for interacting with Ansys Electronics Desktop Database (EDB).

This module contains the ``Edb`` class which serves as the primary interface for:
- Creating and managing EDB projects
- Importing/exporting layout files
- Configuring stackups, materials, and components
- Setting up simulations (HFSS, SIwave, RaptorX)
- Performing cutout operations
- Generating ports and excitations
- Parametrizing designs
- Exporting to various formats (IPC2581, HFSS, Q3D)

Key Functionality:
- Database initialization and management
- Layout manipulation and cutout generation
- Material and stackup configuration
- Net and component management
- Simulation setup and execution
- Design parametrization and optimization

Examples
--------
Basic EDB initialization:
>>> from pyedb.grpc.edb import Edb
>>> edb = Edb(edbpath="myproject.aedb")

Importing a board file:
>>> edb.import_layout_file("my_board.brd")

Creating a cutout:
>>> edb.cutout(signal_list=["Net1", "Net2"], reference_list=["GND"])

Exporting to HFSS:
>>> edb.export_hfss(r"C:\output_folder")
"""

from itertools import combinations
import os
import re
import shutil
import subprocess  # nosec B404
import sys
import tempfile
import time
import traceback
from typing import Dict, List, Union
import warnings
from zipfile import ZipFile as zpf

from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.layout_component import (
    LayoutComponent as GrpcLayoutComponent,
)
import ansys.edb.core.layout.cell
from ansys.edb.core.layout.cell import DesignMode as GrpcDesignMode
from ansys.edb.core.simulation_setup.siwave_dcir_simulation_setup import (
    SIWaveDCIRSimulationSetup as GrpcSIWaveDCIRSimulationSetup,
)
from ansys.edb.core.utility.value import Value as GrpcValue
import rtree

from pyedb.configuration.configuration import Configuration
from pyedb.generic.constants import unit_converter
from pyedb.generic.control_file import ControlFile
from pyedb.generic.general_methods import (
    generate_unique_name,
    get_string_version,
    is_linux,
    is_windows,
)
from pyedb.generic.process import SiwaveSolve
from pyedb.generic.settings import settings
from pyedb.grpc.database.components import Components
from pyedb.grpc.database.definition.materials import Materials
from pyedb.grpc.database.hfss import Hfss
from pyedb.grpc.database.layout.layout import Layout
from pyedb.grpc.database.layout_validation import LayoutValidation
from pyedb.grpc.database.modeler import Modeler
from pyedb.grpc.database.net.differential_pair import DifferentialPairs
from pyedb.grpc.database.net.extended_net import ExtendedNets
from pyedb.grpc.database.nets import NetClasses, Nets
from pyedb.grpc.database.padstacks import Padstacks
from pyedb.grpc.database.ports.ports import BundleWavePort, CoaxPort, GapPort, WavePort
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.rectangle import Rectangle
from pyedb.grpc.database.simulation_setup.hfss_simulation_setup import (
    HfssSimulationSetup,
)
from pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup import (
    RaptorXSimulationSetup,
)
from pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup import (
    SIWaveCPASimulationSetup,
)
from pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup import (
    SIWaveDCIRSimulationSetup,
)
from pyedb.grpc.database.simulation_setup.siwave_simulation_setup import (
    SiwaveSimulationSetup,
)
from pyedb.grpc.database.siwave import Siwave
from pyedb.grpc.database.source_excitations import SourceExcitation
from pyedb.grpc.database.stackup import Stackup
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.terminal.terminal import Terminal
from pyedb.grpc.database.utility.value import Value
from pyedb.grpc.edb_init import EdbInit
from pyedb.misc.decorators import deprecate_argument_name
from pyedb.modeler.geometry_operators import GeometryOperators
from pyedb.workflow import Workflow
from pyedb.workflows.utilities.cutout import Cutout

os.environ["no_proxy"] = "localhost,127.0.0.1"


class Edb(EdbInit):
    """Main class for interacting with Ansys Electronics Desktop Database (EDB).

    Provides comprehensive control over EDB projects including:
    - Project creation/management
    - Layout import/export
    - Material/stackup configuration
    - Component/net management
    - Simulation setup
    - Cutout operations
    - Parameterization

    Parameters
    ----------
    edbpath : str or Path, optional
        Full path to AEDB folder or layout file to import. Supported formats:
        BRD, MCM, XML (IPC2581), GDS, ODB++ (TGZ/ZIP), DXF.
        Default creates new AEDB in documents folder.
    cellname : str, optional
        Specific cell to open. Default opens first cell.
    isreadonly : bool, optional
        Open in read-only mode. Default False.
    edbversion : str, int, float, optional
        EDB version (e.g., "2023.2", 232, 23.2). Default uses latest.
    isaedtowned : bool, optional
        Launch from HFSS 3D Layout. Default False.
    oproject : object, optional
        Reference to AEDT project object.
    student_version : bool, optional
        Use student version. Default False.
    use_ppe : bool, optional
        Use PPE license. Default False.
    control_file : str, optional
        XML control file path for import.
    map_file : str, optional
        Layer map file for import.
    technology_file : str, optional
        Technology file for import (GDS only).
    layer_filter : str, optional
        Layer filter file for import.
    remove_existing_aedt : bool, optional
        Remove existing AEDT project files. Default False.
    restart_rpc_server : bool, optional
        Restart gRPC server. Use with caution. Default False.

    Examples
    --------
    >>> # Create new EDB:
    >>> edb = Edb()

    >>> # Open existing AEDB:
    >>> edb = Edb("myproject.aedb")

    >>> # Import board file:
    >>> edb = Edb("my_board.brd")
    """

    def __init__(
        self,
        edbpath: Union[str, Path] = None,
        cellname: str = None,
        isreadonly: bool = False,
        edbversion: str = None,
        isaedtowned: bool = False,
        oproject=None,
        use_ppe: bool = False,
        control_file: str = None,
        map_file: str = None,
        technology_file: str = None,
        layer_filter: str = None,
        restart_rpc_server=False,
    ):
        edbversion = get_string_version(edbversion)
        self._clean_variables()
        EdbInit.__init__(self, edbversion=edbversion)
        self.standalone = True
        self.oproject = oproject
        self._main = sys.modules["__main__"]
        self.version = edbversion
        if not float(self.version) >= 2025.2:
            raise "EDB gRPC is only supported with ANSYS release 2025R2 and higher."
        self.logger.info("Using PyEDB with gRPC as Beta until ANSYS 2025R2 official release.")
        self.isaedtowned = isaedtowned
        self.isreadonly = isreadonly
        self._setups = {}
        if cellname:
            self.cellname = cellname
        else:
            self.cellname = ""
        if not edbpath:
            if is_windows:
                edbpath = os.getenv("USERPROFILE")
                if not edbpath:
                    edbpath = os.path.expanduser("~")
                edbpath = os.path.join(edbpath, "Documents", generate_unique_name("layout") + ".aedb")
            else:
                edbpath = os.getenv("HOME")
                if not edbpath:
                    edbpath = os.path.expanduser("~")
                edbpath = os.path.join(edbpath, generate_unique_name("layout") + ".aedb")
            self.logger.info("No EDB is provided. Creating a new EDB {}.".format(edbpath))
        self.edbpath = edbpath
        self.log_name = None
        if edbpath:
            self.log_name = os.path.join(
                os.path.dirname(edbpath), "pyaedt_" + os.path.splitext(os.path.split(edbpath)[-1])[0] + ".log"
            )
        if edbpath[-3:] == "zip":
            self.edbpath = edbpath[:-4] + ".aedb"
            working_dir = os.path.dirname(edbpath)
            zipped_file = zpf(edbpath, "r")
            top_level_folders = {item.split("/")[0] for item in zipped_file.namelist()}
            if len(top_level_folders) == 1:
                self.logger.info("Unzipping ODB++...")
                zipped_file.extractall(working_dir)
            else:
                self.logger.info("Unzipping ODB++ before translating to EDB...")
                zipped_file.extractall(edbpath[:-4])
                self.logger.info("ODB++ unzipped successfully.")
            zipped_file.close()
            self.logger.info("Translating ODB++ to EDB...")
            if not self.import_layout_file(
                edbpath[:-4],
                working_dir,
                use_ppe=use_ppe,
                control_file=control_file,
                tech_file=technology_file,
                layer_filter=layer_filter,
                map_file=map_file,
            ):
                raise AttributeError("Translation was unsuccessful")
            if settings.enable_local_log_file and self.log_name:
                self.logger.add_file_logger(self.log_name, "Edb")
            self.logger.info("EDB %s was created correctly from %s file.", self.edbpath, edbpath)

        elif edbpath[-3:] in ["brd", "mcm", "gds", "xml", "dxf", "tgz"]:
            self.edbpath = edbpath[:-4] + ".aedb"
            working_dir = os.path.dirname(edbpath)
            if not self.import_layout_file(
                edbpath,
                working_dir,
                use_ppe=use_ppe,
                control_file=control_file,
                tech_file=technology_file,
                layer_filter=layer_filter,
                map_file=map_file,
            ):
                raise AttributeError("Translation was unsuccessful")
        elif edbpath.endswith("edb.def"):
            self.edbpath = os.path.dirname(edbpath)
            self.open(restart_rpc_server=restart_rpc_server)
        elif not os.path.exists(os.path.join(self.edbpath, "edb.def")):
            self.create(restart_rpc_server=restart_rpc_server)
            self.logger.info("EDB %s created correctly.", self.edbpath)
        elif ".aedb" in edbpath:
            self.edbpath = edbpath
            self.open(restart_rpc_server=restart_rpc_server)
        if self.active_cell:
            self.logger.info("EDB initialized.")
        else:
            self.logger.info("Failed to initialize EDB.")
        self._layout_instance = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """Context manager exit. Closes EDB and cleans up resources."""
        self._signal_handler(ex_type, ex_value)

    def __getitem__(self, variable_name):
        """Get project or design variable value.

        Parameters
        ----------
        variable_name : str
            Variable name with '$' for project variables.

        Returns
        -------
        float or None
            Variable value if exists, else None.
        """
        if self.variable_exists(variable_name):
            return self.variables[variable_name]
        return

    def __setitem__(self, variable_name, variable_value):
        """Set project or design variable.

        Parameters
        ----------
        variable_name : str
            Variable name (with '$' prefix for project variables).
        variable_value : str, float, int, list/tuple
            Value with units. List/tuple format: [value, description]
        """
        type_error_message = "Allowed values are str, numeric or two-item list with variable description."
        if type(variable_value) in [
            list,
            tuple,
        ]:  # Two-item list or tuple. 2nd argument is a str description.
            if len(variable_value) == 2:
                if type(variable_value[1]) is str:
                    description = variable_value[1] if len(variable_value[1]) > 0 else None
                else:
                    description = None
                    self.logger.warning("Invalid type for Edb variable description is ignored.")
                val = variable_value[0]
            else:
                raise TypeError(type_error_message)
        else:
            description = None
            val = variable_value
        if self.variable_exists(variable_name):
            self.change_design_variable_value(variable_name, val)
        else:
            if variable_name.startswith("$"):
                self.add_project_variable(variable_name, val)
            else:
                self.add_design_variable(variable_name, val)
        if description:  # Add the variable description if a two-item list is passed for variable_value.
            self.__getitem__(variable_name).description = description

    @property
    def core(self) -> "ansys.edb.core":
        """Ansys Edb Core module."""
        return ansys.edb.core

    @property
    def ansys_em_path(self):
        return self.base_path

    @staticmethod
    def number_with_units(value, units=None):
        """Convert a number to a string with units. If value is a string, it's returned as is.

        Parameters
        ----------
        value : float, int, str
            Input number or string.
        units : optional
            Units for formatting. The default is ``None``, which uses ``"meter"``.

        Returns
        -------
        str
           String concatenating the value and unit.

        """
        if units is None:
            units = "meter"
        if isinstance(value, str):
            return value
        else:
            return "{0}{1}".format(value, units)

    def _check_remove_project_files(self, edbpath: str, remove_existing_aedt: bool) -> None:
        aedt_file = os.path.splitext(edbpath)[0] + ".aedt"
        files = [aedt_file, aedt_file + ".lock"]
        for file in files:
            if os.path.isfile(file):
                if not remove_existing_aedt:
                    self.logger.warning(
                        f"AEDT project-related file {file} exists and may need to be deleted before opening the EDB in "
                        f"HFSS 3D Layout."
                        # noqa: E501
                    )
                else:
                    try:
                        os.unlink(file)
                        self.logger.info(f"Deleted AEDT project-related file {file}.")
                    except:
                        self.logger.info(f"Failed to delete AEDT project-related file {file}.")

    def _init_objects(self):
        self._components = Components(self)
        self._stackup = Stackup(self, self.layout.core.layer_collection)
        self._padstack = Padstacks(self)
        self._siwave = Siwave(self)
        self._hfss = Hfss(self)
        self._nets = Nets(self)
        self._modeler = Modeler(self)
        self._materials = Materials(self)
        self._source_excitation = SourceExcitation(self)
        self._differential_pairs = DifferentialPairs(self)
        self._extended_nets = ExtendedNets(self)

    def value(self, val) -> float:
        """Convert a value into a pyedb value."""
        if isinstance(val, GrpcValue):
            return Value(val)
        else:
            context = self.active_cell if not str(val).startswith("$") else self.active_db
            return Value(GrpcValue(val, context), context)

    @property
    def cell_names(self) -> List[str]:
        """List of all cell names in the database.

        Returns
        -------
        list[str]
            Names of all circuit cells.
        """
        return [cell.name for cell in self.active_db.top_circuit_cells]

    @property
    def design_variables(self) -> Dict[str, float]:
        """All design variables in active cell.

        Returns
        -------
        dict[str, float]
            Variable names and values.
        """
        return {i: Value(self.active_cell.get_variable_value(i)) for i in self.active_cell.get_all_variable_names()}

    @property
    def project_variables(self) -> Dict[str, float]:
        """All project variables in database.

        Returns
        -------
        dict[str, float]
            Variable names and values.
        """
        return {i: Value(self.active_db.get_variable_value(i)) for i in self.active_db.get_all_variable_names()}

    @property
    def layout_validation(self) -> LayoutValidation:
        """Layout validation utilities.

        Returns
        -------
        :class:`LayoutValidation <pyedb.grpc.database.layout_validation.LayoutValidation>`
            Tools for design rule checking and layout validation.
        """
        return LayoutValidation(self)

    @property
    def variables(self) -> Dict[str, float]:
        """All variables (project + design) in database.

        Returns
        -------
        dict[str, float]
            Combined dictionary of all variables.
        """
        all_vars = dict()
        for i, j in self.project_variables.items():
            all_vars[i] = j
        for i, j in self.design_variables.items():
            all_vars[i] = j
        return all_vars

    @property
    def terminals(self) -> Dict[str, Terminal]:
        """Terminals in active layout.

        Returns
        -------
        dict[str, :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
            Terminal names and objects.
        """
        return {i.name: i for i in self.layout.terminals}

    @property
    def excitations(self) -> Dict[str, GapPort]:
        """All layout excitations.

        Returns
        -------
        dict[str, :class:`GapPort <pyedb.grpc.database.ports.ports.GapPort>`]
            Excitation names and objects.
        """
        terms = [term for term in self.layout.terminals if term.boundary_type == "port"]
        temp = {}
        for term in terms:
            if not term.core.bundle_terminal.is_null:
                temp[term.name] = BundleWavePort(self, term)
            else:
                temp[term.name] = GapPort(self, term)
        return temp

    @property
    def ports(self) -> Dict[str, GapPort]:
        """All ports in design.

        Returns
        -------
        dict[str, list[:class:`GapPort` or :class:`WavePort` or :class:`CoaxPort`]]
            Port names and objects.
        """
        terminals = [term for term in self.layout.terminals if not term.is_reference_terminal]
        ports = {}
        from pyedb.grpc.database.ports.ports import WavePort
        from pyedb.grpc.database.terminal.bundle_terminal import BundleTerminal
        from pyedb.grpc.database.terminal.edge_terminal import EdgeTerminal
        from pyedb.grpc.database.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        for t in terminals:
            if isinstance(t, BundleTerminal):
                bundle_ter = WavePort(self, t.core)
                ports[bundle_ter.name] = bundle_ter
            elif isinstance(t, PadstackInstanceTerminal):
                ports[t.name] = CoaxPort(self, t.core)
            elif isinstance(t, EdgeTerminal):
                if t.is_wave_port:
                    ports[t.name] = WavePort(self, t.core)
                else:
                    ports[t.name] = EdgeTerminal(self, t.core)
            else:
                ports[t.name] = GapPort(self, t.core)
        return ports

    @property
    def excitations_nets(self) -> List[str]:
        """Nets with excitations defined.

        Returns
        -------
        list[str]
            Net names with excitations.
        """
        return list(set([i.net.name for i in self.layout.terminals if not i.is_reference_terminal]))

    @property
    def sources(self) -> Dict[str, Terminal]:
        """All layout sources.

        Returns
        -------
        dict[str, :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
            Source names and objects.
        """
        return {
            k: i
            for k, i in self.terminals.items()
            if "source" in i.boundary_type or "terminal" in i.boundary_type or i.is_reference_terminal
        }

    @property
    def voltage_regulator_modules(self):
        """Voltage regulator modules in design.

        Returns
        -------
        dict[str, :class:`VoltageRegulator <pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator>`]
            VRM names and objects.
        """
        vrms = self.layout.voltage_regulators
        _vrms = {}
        for vrm in vrms:
            _vrms[vrm.name] = vrm
        return _vrms

    @property
    def probes(self) -> Dict[str, Terminal]:
        """All layout probes.

        Returns
        -------
        dict[str, :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
            Probe names and objects.
        """
        terms = [term for term in self.layout.terminals if term.boundary_type == "voltage_probe"]
        return {ter.name: ter for ter in terms}

    def open(self, restart_rpc_server=False) -> bool:
        """Open EDB database.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> # Open an existing EDB database:
        >>> edb = Edb("myproject.aedb")
        """
        self.standalone = self.standalone
        n_try = 10
        while not self.db and n_try:
            try:
                self._open(
                    self.edbpath,
                    self.isreadonly,
                    restart_rpc_server=restart_rpc_server,
                )
                n_try -= 1
            except Exception as e:
                self.logger.error(e.args[0])
        if not self.db:
            raise ValueError("Failed during EDB loading.")
        else:
            if self.db.is_null:
                self.logger.warning("Error Opening db")
                self._active_cell = None
            self.logger.info(f"Database {os.path.split(self.edbpath)[-1]} Opened in {self.version}")
            self._active_cell = None
            if self.cellname:
                for cell in self.active_db.circuit_cells:
                    if cell.name == self.cellname:
                        self._active_cell = cell
            if self._active_cell is None:
                self._active_cell = self._db.circuit_cells[0]
            self.logger.info("Cell %s Opened", self._active_cell.name)
            if self._active_cell:
                self._init_objects()
                self.logger.info("Builder was initialized.")
            else:
                self.logger.error("Builder was not initialized.")
            return True

    def open_edb(self, restart_rpc_server=False) -> bool:
        """Open EDB database.

        .. deprecated:: 0.50.1
            Use :func:`open` instead.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn("`open_edb` is deprecated use `open` instead.", DeprecationWarning)
        return self.open(restart_rpc_server)

    def create(self, restart_rpc_server=False) -> any:
        """Create new EDB database.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        from ansys.edb.core.layout.cell import Cell as GrpcCell, CellType as GrpcCellType

        self.standalone = self.standalone
        n_try = 10
        while not self.db and n_try:
            try:
                self._create(self.edbpath, restart_rpc_server=restart_rpc_server)
                n_try -= 1
            except Exception as e:
                self.logger.error(e.args[0])
        if not self.db:
            raise ValueError("Failed creating EDB.")
            self._active_cell = None
        else:
            if not self.cellname:
                self.cellname = generate_unique_name("Cell")
            self._active_cell = GrpcCell.create(
                db=self.active_db, cell_type=GrpcCellType.CIRCUIT_CELL, cell_name=self.cellname
            )
        if self._active_cell:
            self._init_objects()
            return self
        return None

    def create_edb(self, restart_rpc_server=False) -> bool:
        """
        .. deprecated:: 0.50.1
            Use :func:`create` instead.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn("`create_edb` is deprecated use `create` instead.", DeprecationWarning)
        return self.create(restart_rpc_server)

    def import_layout_pcb(
        self,
        input_file,
        working_dir="",
        anstranslator_full_path="",
        use_ppe=False,
        control_file=None,
        map_file=None,
        tech_file=None,
        layer_filter=None,
    ):
        """Import layout file and generate AEDB.

        Supported formats: BRD, MCM, XML (IPC2581), GDS, ODB++ (TGZ/ZIP), DXF

        Parameters
        ----------
        input_file : str
            Full path to input file.
        working_dir : str, optional
            Output directory for AEDB.
        anstranslator_full_path : str, optional
            Path to Ansys translator executable.
        use_ppe : bool, optional
            Use PPE license. Default False.
        control_file : str, optional
            XML control file path.
        tech_file : str, optional
            Technology file path.
        map_file : str, optional
            Layer map file path.
        layer_filter : str, optional
            Layer filter file path.

        Returns
        -------
        str or bool
            AEDB path if successful, False otherwise.
        """
        self.logger.warning("import_layout_pcb method is deprecated, use import_layout_file instead.")
        return self.import_layout_file(
            input_file,
            working_dir,
            anstranslator_full_path,
            use_ppe,
            control_file,
            map_file,
            tech_file,
            layer_filter,
        )

    def import_layout_file(
        self,
        input_file,
        working_dir="",
        anstranslator_full_path="",
        use_ppe=False,
        control_file=None,
        map_file=None,
        tech_file=None,
        layer_filter=None,
    ):
        """Import a board file and generate an ``edb.def`` file in the working directory.

        This function supports all AEDT formats, including DXF, GDS, SML (IPC2581), BRD, MCM, SIP, ZIP and TGZ.

        .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        input_file : str
            Full path to the board file.
        working_dir : str, optional
            Directory in which to create the ``aedb`` folder. The name given to the AEDB file
            is the same as the name of the board file.
        anstranslator_full_path : str, optional
            Full path to the Ansys translator. The default is ``""``.
        use_ppe : bool
            Whether to use the PPE License. The default is ``False``.
        control_file : str, optional
            Path to the XML file. The default is ``None``, in which case an attempt is made to find
            the XML file in the same directory as the board file. To succeed, the XML file and board file
            must have the same name. Only the extension differs.
        tech_file : str, optional
            Technology file. The file can be *.ircx, *.vlc.tech, or *.itf
        map_file : str, optional
            Layer map .map file.
        layer_filter:str,optional
            Layer filter .txt file.

        Returns
        -------
        Full path to the AEDB file : str

        Examples
        --------
        >>> # Import a BRD file:
        >>> edb.import_layout_file("my_board.brd", r"C:/project")
        >>> # Import a GDS file with control file:
        >>> edb.import_layout_file("layout.gds", control_file="control.xml")
        """
        self._components = None
        self._core_primitives = None
        self._stackup = None
        self._padstack = None
        self._siwave = None
        self._hfss = None
        self._nets = None
        aedb_name = os.path.splitext(os.path.basename(input_file))[0] + ".aedb"
        if anstranslator_full_path and os.path.exists(anstranslator_full_path):
            executable_path = anstranslator_full_path
        else:
            executable_path = os.path.join(self.base_path, "anstranslator")
            if is_windows:
                executable_path += ".exe"

        if not working_dir:
            working_dir = os.path.dirname(input_file)
        cmd_translator = [
            executable_path,
            input_file,
            os.path.join(working_dir, aedb_name),
            "-l={}".format(os.path.join(working_dir, "Translator.log")),
        ]
        if not use_ppe:
            cmd_translator.append("-ppe=false")
        if control_file and input_file[-3:] not in ["brd", "mcm", "sip"]:
            if is_linux:
                cmd_translator.append("-c={}".format(control_file))
            else:
                cmd_translator.append('-c="{}"'.format(control_file))
        if map_file:
            cmd_translator.append('-g="{}"'.format(map_file))
        if tech_file:
            cmd_translator.append('-t="{}"'.format(tech_file))
        if layer_filter:
            cmd_translator.append('-f="{}"'.format(layer_filter))
        try:
            subprocess.run(cmd_translator, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError(
                "An error occurred while translating board file to ``edb.def`` file. Please check the log file."
            ) from e
        if not os.path.exists(os.path.join(working_dir, aedb_name)):
            raise RuntimeWarning(
                f"Translation failed. command : {' '.join(cmd_translator)}. Please check the log file."
            )
        else:
            self.logger.info("Translation successfully completed")
        self.edbpath = os.path.join(working_dir, aedb_name)
        return self.open_edb()

    def import_vlctech_stackup(
        self,
        vlctech_file,
        working_dir="",
        export_xml=None,
    ):
        """Import a vlc.tech file and generate an ``edb.def`` file in the working directory containing only the stackup.

        Parameters
        ----------
        vlctech_file : str
            Full path to the technology stackup file. It must be vlc.tech.
        working_dir : str, optional
            Directory in which to create the ``aedb`` folder. The name given to the AEDB file
            is the same as the name of the board file.
        export_xml : str, optional
            Export technology file in XML control file format.

        Returns
        -------
        Full path to the AEDB file : str

        """
        if not working_dir:
            working_dir = os.path.dirname(vlctech_file)
        command = os.path.join(self.base_path, "helic", "tools", "raptorh", "bin", "make-edb")
        if is_windows:
            command += ".exe"
        else:
            os.environ["HELIC_ROOT"] = os.path.join(self.base_path, "helic")
        cmd_make_edb = [
            command,
            "-t",
            "{}".format(vlctech_file),
            "-o",
            "{}".format(os.path.join(working_dir, "vlctech")),
        ]
        if export_xml:
            cmd_make_edb.extend(["-x", "{}".format(export_xml)])

        try:
            subprocess.run(cmd_make_edb, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError(
                "Failed to create edb. Please check if the executable is present in the base path."
            ) from e

        if not os.path.exists(os.path.join(working_dir, "vlctech.aedb")):
            self.logger.error("Failed to create edb. Please check if the executable is present in the base path.")
            return False
        else:
            self.logger.info("edb successfully created.")
        self.edbpath = os.path.join(working_dir, "vlctech.aedb")
        self.open()
        return self.edbpath

    def export_to_ipc2581(self, edbpath="", anstranslator_full_path="", ipc_path=None) -> str:
        """Export design to IPC2581 format.

        Parameters
        ----------
        edbpath: str
            Full path to aedb folder of the design to convert.
        anstranslator_full_path : str, optional
            Path to Ansys translator executable.
        ipc_path : str, optional
            Output XML file path. Default: <edb_path>.xml.

        Returns
        -------
        str
            Path to output IPC2581 file, and corresponding log file.

        Examples
        --------
        >>> # Export to IPC2581 format:
        >>> edb.export_to_ipc2581("output.xml")
        """
        if not float(self.version) >= 2025.2:
            raise AttributeError("This function is only supported with ANSYS release 2025R2 and higher.")
        if not edbpath:
            edbpath = self.edbpath
        if not ipc_path:
            ipc_path = edbpath[:-5] + ".xml"
        if anstranslator_full_path and os.path.exists(anstranslator_full_path):
            executable_path = anstranslator_full_path
        else:
            executable_path = os.path.join(self.base_path, "anstranslator")
            if is_windows:
                executable_path += ".exe"
        command = [executable_path, edbpath, ipc_path, "-i=edb", "-o=ipc2581"]
        try:
            subprocess.run(command, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError("Translation failed. Please check the log file.") from e
        if not os.path.exists(ipc_path):
            self.logger.error("Translation failed. Please check the log file.")
        else:
            self.logger.info("Translation successfully completed.")
        return ipc_path

    @property
    def configuration(self) -> Configuration:
        """Project configuration manager.

        Returns
        -------
        :class:`Configuration <pyedb.configuration.configuration.Configuration>`
            Configuration file interface.
        """
        if not self._configuration:
            self._configuration = Configuration(self)
        return self._configuration

    def edb_exception(self, ex_value, tb_data):
        """Log Python exceptions to EDB logger.

        Parameters
        ----------
        ex_value : Exception
            Exception value.
        tb_data : traceback
            Traceback object.
        """
        tb_trace = traceback.format_tb(tb_data)
        tblist = tb_trace[0].split("\n")
        self.logger.error(str(ex_value))
        for el in tblist:
            self.logger.error(el)

    @property
    def active_db(self):
        """Active database object.

        Returns
        -------
        :class:`ansys.edb.core.database.Database`
            Current database instance.
        """
        return self.db

    @property
    def active_cell(self):
        """Active cell in the database.

        Returns
        -------
        :class:`ansys.edb.core.layout.cell.Cell`
            Currently active cell.
        """
        return self._active_cell

    @active_cell.setter
    def active_cell(self, value):
        """Set active cell by name or object.

        Parameters
        ----------
        value : str or ansys.edb.core.layout.cell.Cell
            Cell name or object to set as active.

        Raises
        ------
        ValueError
            If cell not found in database.
        """
        self._layout = None
        if isinstance(value, str):
            _cell = [cell for cell in self.circuit_cells if cell.name == value]
            if _cell:
                self._active_cell = _cell[0]
                self._init_objects()
                self.logger.info(f"Design {value} set as active")
            else:
                raise f"Design {value} not found in database."
        elif isinstance(value, ansys.edb.core.layout.cell.Cell):
            self._active_cell = value
            self._init_objects()
            self.logger.info(f"Design {value.name} set as active")
        else:
            raise "No valid design."

    @property
    def components(self) -> Components:
        """Component management interface.

        Returns
        -------
        :class:`Components <pyedb.grpc.database.components.Components>`
            Component manipulation tools.
        """
        if not self._components and self.active_db:
            self._components = Components(self)
        return self._components

    @property
    def stackup(self) -> Stackup:
        """Stackup management interface.

        Returns
        -------
        :class:`Stackup <pyedb.grpc.database.stackup.Stackup>`
            Layer stack configuration tools.
        """
        if self.active_db:
            self._stackup = Stackup(self, self.active_cell.layout.layer_collection)
        return self._stackup

    @property
    def source_excitation(self) -> SourceExcitation:
        """Source excitation management.

        Returns
        -------
        :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`
            Source and port creation tools.
        """
        if self.active_db:
            return self._source_excitation

    @property
    def materials(self) -> Materials:
        """Material database interface.

        Returns
        -------
        :class:`Materials <pyedb.grpc.database.definition.materials.Materials>`
            Material definition and management.
        """
        if self.active_db:
            self._materials = Materials(self)
        return self._materials

    @property
    def padstacks(self) -> Padstacks:
        """Padstack management interface.

        Returns
        -------
        :class:`Padstacks <pyedb.grpc.database.padstack.Padstacks>`
            Padstack definition and editing.
        """
        if not self._padstack and self.active_db:
            self._padstack = Padstacks(self)
        return self._padstack

    @property
    def siwave(self) -> Siwave:
        """SIwave simulation interface.

        Returns
        -------
        :class:`Siwave <pyedb.grpc.database.siwave.Siwave>`
            SIwave analysis setup tools.
        """
        if not self._siwave and self.active_db:
            self._siwave = Siwave(self)
        return self._siwave

    @property
    def hfss(self) -> Hfss:
        """HFSS simulation interface.

        Returns
        -------
        :class:`Hfss <pyedb.grpc.database.hfss.Hfss>`
            HFSS analysis setup tools.
        """
        if not self._hfss and self.active_db:
            self._hfss = Hfss(self)
        return self._hfss

    @property
    def nets(self) -> Nets:
        """Net management interface.

        Returns
        -------
        :class:`Nets <pyedb.grpc.database.nets.Nets>`
            Net manipulation tools.
        """
        if not self._nets and self.active_db:
            self._nets = Nets(self)
        return self._nets

    @property
    def net_classes(self) -> NetClasses:
        """Net class management.

        Returns
        -------
        :class:`NetClass <pyedb.grpc.database.nets.NetClasses>`
            Net classes objects.
        """
        if self.active_db:
            return NetClasses(self)

    @property
    def extended_nets(self) -> ExtendedNets:
        """Extended net management.

        Returns
        -------
        :class:`ExtendedNets <pyedb.grpc.database.net.extended_net.ExtendedNets>`
            Extended net tools.
        """
        if not self._extended_nets:
            self._extended_nets = ExtendedNets(self)
        return self._extended_nets

    @property
    def differential_pairs(self) -> DifferentialPairs:
        """Differential pair management.

        Returns
        -------
        :class:`DifferentialPairs <pyedb.grpc.database.net.differential_par.DifferentialPairs>`
            Differential pair tools.
        """
        if not self._differential_pairs and self.active_db:
            self._differential_pairs = DifferentialPairs(self)
        return self._differential_pairs

    @property
    def modeler(self) -> Modeler:
        """Geometry modeling interface.

        Returns
        -------
        :class:`Modeler <pyedb.grpc.database.modeler.Modeler>`
            Geometry creation and editing.
        """
        if not self._modeler and self.active_db:
            self._modeler = Modeler(self)
        return self._modeler

    @property
    def layout(self) -> Layout:
        """Layout access interface.

        Returns
        -------
        :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`
            Layout manipulation tools.
        """
        if self._layout:
            return self._layout
        self._layout = Layout(self)
        return self._layout

    @property
    def active_layout(self) -> Layout:
        """Active layout access.

        Returns
        -------
        :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`
            Current layout tools.
        """
        return self.layout

    @property
    def layout_instance(self):
        """Layout instance object.

        Returns
        -------
        :class:`LayoutInstance <ansys.edb.core.layout_instance.layout_instance.LayoutInstance>`
            Current layout instance.
        """
        if not self._layout_instance:
            self._layout_instance = self.layout.core.layout_instance
        return self._layout_instance

    def get_connected_objects(self, layout_object_instance):
        """Get objects connected to a layout object.

        Parameters
        ----------
        layout_object_instance :
            Target layout object.

        Returns
        -------
        list
            Connected objects (padstacks, paths, polygons, etc.).
        """
        from ansys.edb.core.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal as GrpcPadstackInstanceTerminal,
        )

        temp = []
        try:
            for i in self.layout_instance.get_connected_objects(layout_object_instance, True):
                if isinstance(i.layout_obj, GrpcPadstackInstanceTerminal):
                    temp.append(PadstackInstanceTerminal(self, i.layout_obj))
                else:
                    layout_obj_type = i.layout_obj.layout_obj_type.name
                    if layout_obj_type == "PADSTACK_INSTANCE":
                        temp.append(PadstackInstance(self, i.layout_obj))
                    elif layout_obj_type == "PATH":
                        temp.append(Path(self, i.layout_obj))
                    elif layout_obj_type == "RECTANGLE":
                        temp.append(Rectangle(self, i.layout_obj))
                    elif layout_obj_type == "CIRCLE":
                        temp.append(Circle(self, i.layout_obj))
                    elif layout_obj_type == "POLYGON":
                        temp.append(Polygon(self, i.layout_obj))
                    else:
                        continue
        except:
            self.logger.warning(
                f"Failed to find connected objects on layout_obj {layout_object_instance.layout_obj.id}, skipping."
            )
            pass
        return temp

    def point_3d(self, x, y, z=0.0):
        """Create 3D point.

        Parameters
        ----------
        x : float, int, str
            X coordinate.
        y : float, int, str
            Y coordinate.
        z : float, int, str, optional
            Z coordinate.

        Returns
        -------
        :class:`Point3DData <pyedb.grpc.database.geometry.point_3d_data.Point3DData>`
            3D point object.
        """
        from pyedb.grpc.database.geometry.point_3d_data import Point3DData

        return Point3DData(x, y, z)

    def point_data(self, x, y=None):
        """Create 2D point.

        Parameters
        ----------
        x : float, int, str or PointData
            X coordinate or PointData object.
        y : float, int, str, optional
            Y coordinate.

        Returns
        -------
        :class:`PointData <pyedb.grpc.database.geometry.point_data.PointData>`
            2D point object.
        """
        from pyedb.grpc.database.geometry.point_data import PointData

        if y is None:
            return PointData(x)
        else:
            return PointData(x, y)

    @staticmethod
    def _is_file_existing(filename) -> bool:
        if os.path.exists(filename):
            return True
        else:
            return False

    def _wait_for_file_exists(self, timeout=30, file_to_release=None, wait_count=4):
        if not file_to_release:
            file_to_release = os.path.join(self.edbpath)
        tstart = time.time()
        times = 0
        while True:
            if self._is_file_existing(file_to_release):
                # print 'File is released'
                times += 1
                if times == wait_count:
                    return True
            elif time.time() - tstart > timeout:
                # print 'Timeout reached'
                return False
            else:
                times = 0
                time.sleep(0.250)

    def close_edb(self) -> bool:
        """Close EDB and clean up resources.

        ..deprecated:: 0.51.0
           Use :func:`close` instead.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        Close the EDB session:
        >>> edb.close_edb()
        """
        warnings.warn("Use method close instead.", DeprecationWarning)
        return self.close()

    def save_edb(self) -> bool:
        """Save current EDB database.

        ..deprecated:: 0.51.0
           Use :func:`save` instead.

        """
        warnings.warn("Use method save instead.", DeprecationWarning)
        return self.save()

    def save_edb_as(self, fname) -> bool:
        """Save EDB database to new location.

        ..deprecated:: 0.51.0
           Use :func:`save_as` instead.
        """
        warnings.warn("Use method save_as instead.", DeprecationWarning)
        return self.save_as(fname)

    def execute(self, func):
        """Execute EDB utility command (Not implemented in gRPC).

        Parameters
        ----------
        func : str
            Command to execute.
        """
        # return self.core.utility.utility.Command.Execute(func)
        pass

    def import_cadence_file(self, inputBrd, WorkDir=None, anstranslator_full_path="", use_ppe=False) -> bool:
        """Import Cadence board file.

        .. deprecated:: 0.50
        Use :func:`import_layout_file` instead.
        """
        if self.import_layout_pcb(
            inputBrd,
            working_dir=WorkDir,
            anstranslator_full_path=anstranslator_full_path,
            use_ppe=use_ppe,
        ):
            return True
        else:
            return False

    def import_gds_file(
        self,
        inputGDS,
        anstranslator_full_path="",
        use_ppe=False,
        control_file=None,
        tech_file=None,
        map_file=None,
        layer_filter=None,
    ):
        """Import GDS file.

        .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        inputGDS : str
            GDS file path.
        anstranslator_full_path : str, optional
            Ansys translator path.
        use_ppe : bool, optional
            Use PPE license. Default False.
        control_file : str, optional
            XML control file.
        tech_file : str, optional
            Technology file.
        map_file : str, optional
            Layer map file.
        layer_filter : str, optional
            Layer filter file.
        """
        control_file_temp = os.path.join(tempfile.gettempdir(), os.path.split(inputGDS)[-1][:-3] + "xml")
        if float(self.version) < 2024.1:
            if not is_linux and tech_file:
                self.logger.error("Technology files are supported only in Linux. Use control file instead.")
                return False

            ControlFile(xml_input=control_file, tecnhology=tech_file, layer_map=map_file).write_xml(control_file_temp)
            if self.import_layout_pcb(
                inputGDS,
                anstranslator_full_path=anstranslator_full_path,
                use_ppe=use_ppe,
                control_file=control_file_temp,
            ):
                return True
            else:
                return False
        else:
            temp_map_file = os.path.splitext(inputGDS)[0] + ".map"
            temp_layermap_file = os.path.splitext(inputGDS)[0] + ".layermap"

            if map_file is None:
                if os.path.isfile(temp_map_file):
                    map_file = temp_map_file
                elif os.path.isfile(temp_layermap_file):
                    map_file = temp_layermap_file
                else:
                    self.logger.error("Unable to define map file.")

            if tech_file is None:
                if control_file is None:
                    temp_control_file = os.path.splitext(inputGDS)[0] + ".xml"
                    if os.path.isfile(temp_control_file):
                        control_file = temp_control_file
                    else:
                        self.logger.error("Unable to define control file.")

                command = [anstranslator_full_path, inputGDS, f'-g="{map_file}"', f'-c="{control_file}"']
            else:
                command = [
                    anstranslator_full_path,
                    inputGDS,
                    f'-o="{control_file_temp}"-t="{tech_file}"',
                    f'-g="{map_file}"',
                    f'-f="{layer_filter}"',
                ]

            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)  # nosec
                print(result.stdout)
                print(command)
            except subprocess.CalledProcessError as e:  # nosec
                raise RuntimeError("An error occurred while converting file") from e
            temp_inputGDS = inputGDS.split(".gds")[0]
            self.edbpath = temp_inputGDS + ".aedb"
            return self.open()

    @deprecate_argument_name({"signal_list": "signal_nets", "reference_list": "reference_nets"})
    def cutout(
        self,
        signal_nets=None,
        reference_nets=None,
        extent_type="ConvexHull",
        expansion_size=0.002,
        use_round_corner=False,
        output_aedb_path=None,
        open_cutout_at_end=True,
        use_pyaedt_cutout=True,
        number_of_threads=1,
        use_pyaedt_extent_computing=True,
        extent_defeature=0,
        remove_single_pin_components=False,
        custom_extent=None,
        custom_extent_units="mm",
        include_partial_instances=False,
        keep_voids=True,
        check_terminals=False,
        include_pingroups=False,
        expansion_factor=0,
        maximum_iterations=10,
        preserve_components_with_model=False,
        simple_pad_check=True,
        keep_lines_as_path=False,
        include_voids_in_extents=False,
    ):
        """Create a cutout using an approach entirely based on PyAEDT.
        This method replaces all legacy cutout methods in PyAEDT.
        It does in sequence:
        - delete all nets not in list,
        - create a extent of the nets,
        - check and delete all vias not in the extent,
        - check and delete all the primitives not in extent,
        - check and intersect all the primitives that intersect the extent.

        Parameters
        ----------
         signal_nets : list
            List of signal strings.
        reference_nets : list, optional
            List of references to add. The default is ``["GND"]``.
        extent_type : str, optional
            Type of the extension. Options are ``"Conforming"``, ``"ConvexHull"``, and
            ``"Bounding"``. The default is ``"Conforming"``.
        expansion_size : float, str, optional
            Expansion size ratio in meters. The default is ``0.002``.
        use_round_corner : bool, optional
            Whether to use round corners. The default is ``False``.
        output_aedb_path : str, optional
            Full path and name for the new AEDB file. If None, then current aedb will be cutout.
        open_cutout_at_end : bool, optional
            Whether to open the cutout at the end. The default is ``True``.
        use_pyaedt_cutout : bool, optional
            Whether to use new PyAEDT cutout method or EDB API method.
            New method is faster than native API method since it benefits of multithread.
        number_of_threads : int, optional
            Number of thread to use. Default is 4. Valid only if ``use_pyaedt_cutout`` is set to ``True``.
        use_pyaedt_extent_computing : bool, optional
            Whether to use legacy extent computing (experimental) or EDB API.
        extent_defeature : float, optional
            Defeature the cutout before applying it to produce simpler geometry for mesh (Experimental).
            It applies only to Conforming bounding box. Default value is ``0`` which disable it.
        remove_single_pin_components : bool, optional
            Remove all Single Pin RLC after the cutout is completed. Default is `False`.
        custom_extent : list
            Points list defining the cutout shape. This setting will override `extent_type` field.
        custom_extent_units : str
            Units of the point list. The default is ``"mm"``. Valid only if `custom_extend` is provided.
        include_partial_instances : bool, optional
            Whether to include padstack instances that have bounding boxes intersecting with point list polygons.
            This operation may slow down the cutout export.Valid only if `custom_extend` and
            `use_pyaedt_cutout` is provided.
        keep_voids : bool
            Boolean used for keep or not the voids intersecting the polygon used for clipping the layout.
            Default value is ``True``, ``False`` will remove the voids.Valid only if `custom_extend` is provided.
        check_terminals : bool, optional
            Whether to check for all reference terminals and increase extent to include them into the cutout.
            This applies to components which have a model (spice, touchstone or netlist) associated.
        include_pingroups : bool, optional
            Whether to check for all pingroups terminals and increase extent to include them into the cutout.
            It requires ``check_terminals``.
        expansion_factor : int, optional
            The method computes a float representing the largest number between
            the dielectric thickness or trace width multiplied by the expansion_factor factor.
            The trace width search is limited to nets with ports attached. Works only if `use_pyaedt_cutout`.
            Default is `0` to disable the search.
        maximum_iterations : int, optional
            Maximum number of iterations before stopping a search for a cutout with an error.
            Default is `10`.
        preserve_components_with_model : bool, optional
            Whether to preserve all pins of components that have associated models (Spice or NPort).
            This parameter is applicable only for a PyAEDT cutout (except point list).
        simple_pad_check : bool, optional
            Whether to use the center of the pad to find the intersection with extent or use the bounding box.
            Second method is much slower and requires to disable multithread on padstack removal.
            Default is `True`.
        keep_lines_as_path : bool, optional
            Whether to keep the lines as Path after they are cutout or convert them to PolygonData.
            This feature works only in Electronics Desktop (3D Layout).
            If the flag is set to ``True`` it can cause issues in SiWave once the Edb is imported.
            Default is ``False`` to generate PolygonData of cut lines.
        include_voids_in_extents : bool, optional
            Whether to compute and include voids in pyaedt extent before the cutout. Cutout time can be affected.
            It works only with Conforming cutout.
            Default is ``False`` to generate extent without voids.


        Returns
        -------
        List
            List of coordinate points defining the extent used for clipping the design. If it failed return an empty
            list.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb(r"C:\\test.aedb", version="2022.2")
        >>> edb.logger.info_timer("Edb Opening")
        >>> edb.logger.reset_timer()
        >>> start = time.time()
        >>> signal_list = []
        >>> for net in edb.nets.netlist:
        >>>      if "3V3" in net:
        >>>           signal_list.append(net)
        >>> power_list = ["PGND"]
        >>> edb.cutout(signal_nets=signal_list, reference_nets=power_list, extent_type="Conforming")
        >>> end_time = str((time.time() - start) / 60)
        >>> edb.logger.info("Total legacy cutout time in min %s", end_time)
        >>> edb.nets.plot(signal_list, None, color_by_net=True)
        >>> edb.nets.plot(power_list, None, color_by_net=True)
        >>> edb.save()
        >>> edb.close()


        """
        cutout = Cutout(self)
        cutout.expansion_size = expansion_size
        cutout.signals = signal_nets
        cutout.references = reference_nets
        cutout.extent_type = extent_type
        cutout.expansion_size = expansion_size
        cutout.use_round_corner = use_round_corner
        cutout.output_file = output_aedb_path
        cutout.open_cutout_at_end = open_cutout_at_end
        cutout.use_pyaedt_cutout = use_pyaedt_cutout
        cutout.number_of_threads = number_of_threads
        cutout.use_pyaedt_extent_computing = use_pyaedt_extent_computing
        cutout.extent_defeatured = extent_defeature
        cutout.remove_single_pin_components = remove_single_pin_components
        cutout.custom_extent = custom_extent
        cutout.custom_extent_units = custom_extent_units
        cutout.include_partial_instances = include_partial_instances
        cutout.keep_voids = keep_voids
        cutout.check_terminals = check_terminals
        cutout.include_pingroups = include_pingroups
        cutout.expansion_factor = expansion_factor
        cutout.maximum_iterations = maximum_iterations
        cutout.preserve_components_with_model = preserve_components_with_model
        cutout.simple_pad_check = simple_pad_check
        cutout.keep_lines_as_path = keep_lines_as_path
        cutout.include_voids_in_extents = include_voids_in_extents
        return cutout.run()

    @staticmethod
    def write_export3d_option_config_file(path_to_output, config_dictionaries=None):
        """Write the options for a 3D export to a configuration file.

        Parameters
        ----------
        path_to_output : str
            Full path to the configuration file to save 3D export options to.

        config_dictionaries : dict, optional
            Configuration dictionaries. The default is ``None``.

        """
        option_config = {
            "UNITE_NETS": 1,
            "ASSIGN_SOLDER_BALLS_AS_SOURCES": 0,
            "Q3D_MERGE_SOURCES": 0,
            "Q3D_MERGE_SINKS": 0,
            "CREATE_PORTS_FOR_PWR_GND_NETS": 0,
            "PORTS_FOR_PWR_GND_NETS": 0,
            "GENERATE_TERMINALS": 0,
            "SOLVE_CAPACITANCE": 0,
            "SOLVE_DC_RESISTANCE": 0,
            "SOLVE_DC_INDUCTANCE_RESISTANCE": 1,
            "SOLVE_AC_INDUCTANCE_RESISTANCE": 0,
            "CreateSources": 0,
            "CreateSinks": 0,
            "LAUNCH_Q3D": 0,
            "LAUNCH_HFSS": 0,
        }
        if config_dictionaries:
            for el, val in config_dictionaries.items():
                option_config[el] = val
        with open(os.path.join(path_to_output, "options.config"), "w") as f:
            for el, val in option_config.items():
                f.write(el + " " + str(val) + "\n")
        return os.path.join(path_to_output, "options.config")

    def export_hfss(
        self,
        path_to_output,
        net_list=None,
        num_cores=None,
        aedt_file_name=None,
        hidden=False,
    ):
        """Export to HFSS project.

        Parameters
        ----------
        path_to_output : str
            Output directory.
        net_list : list, optional
            Nets to export.
        num_cores : int, optional
            Processing cores to use.
        aedt_file_name : str, optional
            Custom AEDT filename.
        hidden : bool, optional
            Run Siwave in background. Default False.

        Returns
        -------
        str
            Path to generated AEDT file.

        Examples
        --------
        >>> # Export to HFSS project:
        >>> edb.export_hfss(r"C:/output", net_list=["SignalNet"])
        """
        siwave_s = SiwaveSolve(self)
        return siwave_s.export_3d_cad("HFSS", path_to_output, net_list, num_cores, aedt_file_name, hidden=hidden)

    def export_q3d(
        self,
        path_to_output,
        net_list=None,
        num_cores=None,
        aedt_file_name=None,
        hidden=False,
    ):
        """Export to Q3D project.

        Parameters
        ----------
        path_to_output : str
            Output directory.
        net_list : list, optional
            Nets to export.
        num_cores : int, optional
            Processing cores to use.
        aedt_file_name : str, optional
            Custom AEDT filename.
        hidden : bool, optional
            Run Siwave in background. Default False.

        Returns
        -------
        str
            Path to generated AEDT file.

        Examples
        --------
        >>> # Export to Q3D project:
        >>> edb.export_q3d(r"C:/output")
        """
        siwave_s = SiwaveSolve(self)
        return siwave_s.export_3d_cad(
            "Q3D",
            path_to_output,
            net_list,
            num_cores=num_cores,
            aedt_file_name=aedt_file_name,
            hidden=hidden,
        )

    def export_maxwell(
        self,
        path_to_output,
        net_list=None,
        num_cores=None,
        aedt_file_name=None,
        hidden=False,
    ):
        """Export to Maxwell project.

        Parameters
        ----------
        path_to_output : str
            Output directory.
        net_list : list, optional
            Nets to export.
        num_cores : int, optional
            Processing cores to use.
        aedt_file_name : str, optional
            Custom AEDT filename.
        hidden : bool, optional
            Run Siwave in background. Default False.

        Returns
        -------
        str
            Path to generated AEDT file.

        Examples
        --------
        >>> # Export to Maxwell project:
        >>> edb.export_maxwell(r"C:/output")
        """
        siwave_s = SiwaveSolve(self)
        return siwave_s.export_3d_cad(
            "Maxwell",
            path_to_output,
            net_list,
            num_cores=num_cores,
            aedt_file_name=aedt_file_name,
            hidden=hidden,
        )

    def solve_siwave(self):
        """Solve with SIwave.

        Returns
        -------
        str
            Path to SIwave project.

        Examples
        --------
        >>> # Solve with SIwave:
        >>> edb.solve_siwave()
        """
        process = SiwaveSolve(self)
        try:
            self.close()
        except Exception as e:
            self.logger.warning(
                f"A(n) {type(e).__name__} error occurred while attempting to close the database {self}: {str(e)}"
            )
        process.solve()
        return self.edbpath[:-5] + ".siw"

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
        """Export SIwave DC results.

        Parameters
        ----------
        siwave_project : str
            SIwave project path.
        solution_name : str
            DC analysis name.
        output_folder : str, optional
            Custom output folder.
        html_report : bool, optional
            Generate HTML report. Default True.
        vias : bool, optional
            Export vias report. Default True.
        voltage_probes : bool, optional
            Export voltage probes. Default True.
        current_sources : bool, optional
            Export current sources. Default True.
        voltage_sources : bool, optional
            Export voltage sources. Default True.
        power_tree : bool, optional
            Export power tree. Default True.
        loop_res : bool, optional
            Export loop resistance. Default True.

        Returns
        -------
        list[str]
            Generated report files.
        """
        process = SiwaveSolve(self)
        try:
            self.close()
        except Exception as e:
            self.logger.warning(
                f"A(n) {type(e).__name__} error occurred while attempting to close the database {self}: {str(e)}"
            )
        return process.export_dc_report(
            siwave_project,
            solution_name,
            output_folder,
            html_report,
            vias,
            voltage_probes,
            current_sources,
            voltage_sources,
            power_tree,
            loop_res,
            hidden=True,
        )

    def variable_exists(self, variable_name):
        """Check if variable exists.

        Parameters
        ----------
        variable_name : str
            Variable name.

        Returns
        -------
        bool
            True if variable exists.
        """
        if "$" in variable_name:
            if variable_name.index("$") == 0:
                variables = self.active_db.get_all_variable_names()
            else:
                variables = self.active_cell.get_all_variable_names()
        else:
            variables = self.active_cell.get_all_variable_names()
        if variable_name in variables:
            return True
        return False

    def get_variable(self, variable_name):
        """Get variable value.

        Parameters
        ----------
        variable_name : str
            Variable name.

        Returns
        -------
        float or bool
            Variable value if exists, else False.
        """
        if self.variable_exists(variable_name):
            if variable_name.startswith("$"):
                variable = next(var for var in self.active_db.get_all_variable_names())
                return self.db.get_variable_value(variable)
            else:
                variable = next(var for var in self.active_cell.get_all_variable_names())
                return self.active_cell.get_variable_value(variable)
        self.logger.info(f"Variable {variable_name} doesn't exists.")
        return False

    def get_variable_value(self, variable_name):
        """
        Deprecated method to get the value of a variable.

        .. deprecated:: pyedb 0.55.0
           Use :func:`get_variable` instead.
        """
        warnings.warn(
            "`get_variable_value` is deprecated use `get_variable` instead.",
            DeprecationWarning,
        )
        return self.get_variable(variable_name)

    def get_all_variable_names(self) -> List[str]:
        """Method added for compatibility with grpc.

        Returns
        -------
        List[str]
            List of variable names.

        """
        return list(self.active_cell.get_all_variable_names())

    def add_project_variable(self, variable_name, variable_value, description=None) -> bool:
        """Add project variable.

        Parameters
        ----------
        variable_name : str
            Variable name (auto-prefixed with '$').
        variable_value : str, float
            Variable value with units.
        description : str, optional
            Variable description.

        Returns
        -------
        bool
            True if successful, False if variable exists.
        """
        if not variable_name.startswith("$"):
            variable_name = f"${variable_name}"
        if not self.variable_exists(variable_name):
            var = self.active_db.add_variable(variable_name, variable_value)
            if description:
                self.active_db.set_variable_desc(name=variable_name, desc=description)
            return var
        else:
            self.logger.error(f"Variable {variable_name} already exists.")
            return False

    def add_design_variable(self, variable_name, variable_value, is_parameter=False, description=None) -> bool:
        """Add design variable.

        Parameters
        ----------
        variable_name : str
            Variable name.
        variable_value : str, float
            Variable value with units.
        is_parameter : bool, optional
            Add as local variable. Default False.
        description : str, optional
            Variable description.

        Returns
        -------
        bool
            True if successful, False if variable exists.
        """
        if variable_name.startswith("$"):
            variable_name = variable_name[1:]
        if not self.variable_exists(variable_name):
            var = self.active_cell.add_variable(variable_name, variable_value)
            if description:
                self.active_cell.set_variable_desc(name=variable_name, desc=description)
            return var
        else:
            self.logger.error(f"Variable {variable_name} already exists.")
            return False

    def change_design_variable_value(self, variable_name, variable_value):
        """Update variable value.

        Parameters
        ----------
        variable_name : str
            Variable name.
        variable_value : str, float
            New value with units.
        """
        if self.variable_exists(variable_name):
            if variable_name in self.db.get_all_variable_names():
                self.db.set_variable_value(variable_name, Value(variable_value))
            elif variable_name in self.active_cell.get_all_variable_names():
                self.active_cell.set_variable_value(variable_name, Value(variable_value))

    @property
    def design_mode(self):
        """Get mode of the  edb design.
        Returns
        ----------
        str
            Value is either "General" or "IC".
        """
        return ("general", "ic")[self.active_cell.design_mode.value]

    @design_mode.setter
    def design_mode(self, value):
        """Update the design mode of the edb.
        Parameters
        ----------
        value : str
            It can be either "General" or "IC".
        """
        try:
            self.active_cell.design_mode = GrpcDesignMode(("general", "ic").index(value.lower()))
        except (AttributeError, ValueError):
            raise ValueError("Value must be 'general' or 'ic' (case-insensitive)")

    def get_bounding_box(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Get layout bounding box.

        Returns
        -------
        list
            list[list[min_x, min_y], list[max_x, max_y]] in meters.
        """
        lay_inst_polygon_data = [obj_inst.get_bbox() for obj_inst in self.layout_instance.query_layout_obj_instances()]
        layout_bbox = GrpcPolygonData.bbox_of_polygons(lay_inst_polygon_data)
        return ((Value(layout_bbox[0].x), Value(layout_bbox[0].y)), (Value(layout_bbox[1].x), Value(layout_bbox[1].y)))

    def get_statistics(self, compute_area=False):
        """Get layout statistics.

        Parameters
        ----------
        compute_area : bool, optional
            Calculate net areas. Default False.

        Returns
        -------
        :class:`LayoutStatistics <pyedb.grpc.database.utility.layout_statistics.LayoutStatistics>`
            Layout statistics report.
        """
        return self.modeler.get_layout_statistics(evaluate_area=compute_area, net_list=None)

    def are_port_reference_terminals_connected(self, common_reference=None):
        """Check if port reference terminals are connected.

        Parameters
        ----------
        common_reference : str, optional
            Reference net name to check.

        Returns
        -------
        bool
            True if all port references are connected.
        """
        all_sources = [i for i in self.excitations.values() if not isinstance(i, (WavePort, GapPort, BundleWavePort))]
        all_sources.extend([i for i in self.sources.values()])
        if not all_sources:
            return True
        self.logger.reset_timer()
        if not common_reference:
            ref_terminals = [term for term in all_sources if term.is_reference_terminal]
            common_reference = list(set([i.net.name for i in ref_terminals]))
            if len(common_reference) > 1:
                raise ValueError("Multiple reference nets found. Please specify one.")
            if not common_reference:
                raise ValueError("No reference net found. Please specify one.")
            common_reference = common_reference[0]
        all_sources = [i for i in all_sources if i.net.name != common_reference]
        layout_inst = self.layout.layout_instance
        layout_obj_inst = layout_inst.get_layout_obj_instance_in_context(all_sources[0], None)  # 2nd arg was []
        connected_objects = [loi.layout_obj.id for loi in layout_inst.get_connected_objects(layout_obj_inst, True)]
        connected_primitives = [self.modeler.get_primitive(obj, edb_uid=False) for obj in connected_objects]
        connected_primitives = [item for item in connected_primitives if item is not None]
        set_list = list(set([obj.net_name for obj in connected_primitives]))
        if len(set_list) != len(all_sources):
            self.logger.error("No Reference found.")
            return False
        cmps = [
            i
            for i in list(self.components.resistors.values())
            if i.num_pins == 2 and common_reference in i.nets and i.res_value <= 1
        ]
        cmps.extend(
            [i for i in list(self.components.inductors.values()) if i.num_pins == 2 and common_reference in i.nets]
        )

        for cmp in cmps:
            found = False
            ids = [v.id for i, v in cmp.pins.items()]
            for list_obj in set_list:
                if len(set(ids).intersection(list_obj)) == 1:
                    for list_obj2 in set_list:
                        if list_obj2 != list_obj and len(set(ids).intersection(list_obj)) == 1:
                            if (ids[0] in list_obj and ids[1] in list_obj2) or (
                                ids[1] in list_obj and ids[0] in list_obj2
                            ):
                                set_list[set_list.index(list_obj)] = list_obj.union(list_obj2)
                                set_list[set_list.index(list_obj2)] = list_obj.union(list_obj2)
                                found = True
                                break
                    if found:
                        break

        # Get the set intersections for all the ID sets.
        set_list = set(set_list)
        iDintersection = set.intersection(set_list)
        self.logger.info_timer(f"Terminal reference primitive IDs total intersections = {len(iDintersection)}\n\n")

        # If the intersections are non-zero, the terminal references are connected.
        return True if len(iDintersection) > 0 else False

    @property
    def setups(
        self,
    ) -> dict[
        str,
        Union[
            HfssSimulationSetup,
            SiwaveSimulationSetup,
            SIWaveDCIRSimulationSetup,
            RaptorXSimulationSetup,
            SIWaveCPASimulationSetup,
        ],
    ]:
        """Get the dictionary of all EDB HFSS and SIwave setups.

        Returns
        -------
        Dict[str,:class:`HfssSimulationSetup`] or
        Dict[str,:class:`SiwaveSimulationSetup`] or
        Dict[str,:class:`SIWaveDCIRSimulationSetup`] or
        Dict[str,:class:`RaptorXSimulationSetup`]
        Dict[str,:class:`SIWaveCPASimulationSetup`]

        """
        from ansys.edb.core.database import ProductIdType as GrpcProductIdType

        from pyedb.siwave_core.product_properties import SIwaveProperties

        setups = {}
        for setup in self.active_cell.simulation_setups:
            setup = setup.cast()
            setup_type = setup.type.name
            if setup_type == "HFSS":
                setups[setup.name] = HfssSimulationSetup(self, setup)
            elif setup_type == "SI_WAVE":
                setups[setup.name] = SiwaveSimulationSetup(self, setup)
            elif setup_type == "SI_WAVE_DCIR":
                setups[setup.name] = SIWaveDCIRSimulationSetup(self, setup)
            elif setup_type == "RAPTOR_X":
                setups[setup.name] = RaptorXSimulationSetup(self, setup)
        try:
            cpa_setup_name = self.active_cell.get_product_property(
                GrpcProductIdType.SIWAVE, SIwaveProperties.CPA_SIM_NAME
            ).value
        except:
            cpa_setup_name = ""
        if cpa_setup_name:
            setups[cpa_setup_name] = SIWaveCPASimulationSetup(self, cpa_setup_name)
        return setups

    @property
    def hfss_setups(self) -> dict[str, HfssSimulationSetup]:
        """Active HFSS setup in EDB.

        Returns
        -------
        Dict[str,
        :class:`HfssSimulationSetup <pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup>`]

        """
        setups = {}
        for setup in self.active_cell.simulation_setups:
            if setup.type.name == "HFSS":
                setups[setup.name] = HfssSimulationSetup(self, setup)
        return setups

    @property
    def siwave_dc_setups(self) -> dict[str, SIWaveDCIRSimulationSetup]:
        """Active Siwave DC IR Setups.

        Returns
        -------
        Dict[str,
        :class:`SIWaveDCIRSimulationSetup
        <pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup>`]
        """
        return {name: i for name, i in self.setups.items() if isinstance(i, SIWaveDCIRSimulationSetup)}

    @property
    def siwave_ac_setups(self) -> dict[str, SiwaveSimulationSetup]:
        """Active Siwave SYZ setups.

        Returns
        -------
        Dict[str,:class:`SiwaveSimulationSetup`]
        """
        return {name: i for name, i in self.setups.items() if isinstance(i, SiwaveSimulationSetup)}

    def create_hfss_setup(
        self, name=None, start_frequency="0GHz", stop_frequency="20GHz", step_frequency="10MHz"
    ) -> HfssSimulationSetup:
        """Create an HFSS simulation setup from a template.

        . deprecated:: pyedb 0.30.0
        Use :func:`pyedb.grpc.core.hfss.add_setup` instead.
        """
        warnings.warn(
            "`create_hfss_setup` is deprecated and is now located here `pyedb.grpc.core.hfss.add_setup` instead.",
            DeprecationWarning,
        )
        return self._hfss.add_setup(
            name=name,
            distribution="linear",
            start_freq=start_frequency,
            stop_freq=stop_frequency,
            step_freq=step_frequency,
        )

    def create_raptorx_setup(self, name=None) -> RaptorXSimulationSetup:
        """Create RaptorX analysis setup (2024R2+ only).

        Parameters
        ----------
        name : str, optional
            Setup name. Auto-generated if None.

        Returns
        -------
        :class:`RaptorXSimulationSetup`
            RaptorX setup or False if unsupported.
        """
        from ansys.edb.core.simulation_setup.raptor_x_simulation_setup import (
            RaptorXSimulationSetup as GrpcRaptorXSimulationSetup,
        )

        if name in self.setups:
            self.logger.error("Setup name already used in the layout")
            return False
        version = self.version.split(".")
        if int(version[0]) >= 2024 and int(version[-1]) >= 2 or int(version[0]) > 2024:
            setup = GrpcRaptorXSimulationSetup.create(cell=self.active_cell, name=name)
            return RaptorXSimulationSetup(self, setup)
        else:
            self.logger.error("RaptorX simulation only supported with Ansys release 2024R2 and higher")
            return False

    def create_hfsspi_setup(self, name=None):
        # """Create an HFSS PI simulation setup from a template.
        #
        # Parameters
        # ----------
        # name : str, optional
        #     Setup name.
        #
        # Returns
        # -------
        # :class:`legacy.database.edb_data.hfss_pi_simulation_setup_data.HFSSPISimulationSetup when succeeded, ``False``
        # when failed.
        #
        # """
        # if name in self.setups:
        #     self.logger.error("Setup name already used in the layout")
        #     return False
        # version = self.edbversion.split(".")
        # if float(self.edbversion) < 2024.2:
        #     self.logger.error("HFSSPI simulation only supported with Ansys release 2024R2 and higher")
        #     return False
        # return HFSSPISimulationSetup(self, name=name)

        #  TODO check HFSS-PI with Grpc. seems to defined at terminal level not setup.
        pass

    def create_siwave_syz_setup(self, name=None, **kwargs) -> SiwaveSimulationSetup:
        """Create SIwave SYZ analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name. Auto-generated if None.
        **kwargs
            Setup properties to modify.

        Returns
        -------
        :class:`SiwaveSimulationSetup`
            SYZ analysis setup.
        """
        if not name:
            name = generate_unique_name("Siwave_SYZ")
        if name in self.setups:
            return False
        from ansys.edb.core.simulation_setup.siwave_simulation_setup import (
            SIWaveSimulationSetup as GrpcSIWaveSimulationSetup,
        )

        setup = SiwaveSimulationSetup(self, GrpcSIWaveSimulationSetup.create(cell=self.active_cell, name=name))
        for k, v in kwargs.items():
            setattr(setup, k, v)
        return self.setups[name]

    def create_siwave_dc_setup(self, name=None, **kwargs) -> GrpcSIWaveDCIRSimulationSetup:
        """Create SIwave DC analysis setup.

        Parameters
        ----------
        name : str, optional
            Setup name. Auto-generated if None.
        **kwargs
            Setup properties to modify.

        Returns
        -------
        :class:`SIWaveDCIRSimulationSetup`
            DC analysis setup.
        """
        if not name:
            name = generate_unique_name("Siwave_DC")
        if name in self.setups:
            return False
        setup = SIWaveDCIRSimulationSetup(self, GrpcSIWaveDCIRSimulationSetup.create(cell=self.active_cell, name=name))
        for k, v in kwargs.items():
            setattr(setup, k, v)
        return setup

    def calculate_initial_extent(self, expansion_factor):
        """Compute a float representing the larger number between the dielectric thickness or trace width
        multiplied by the nW factor. The trace width search is limited to nets with ports attached.

        Parameters
        ----------
        expansion_factor : float
            Value for the width multiplier (nW factor).

        Returns
        -------
        float
        """
        nets = []
        for port in self.excitations.values():
            nets.append(port.net.name)
        for port in self.sources.values():
            nets.append(port.net.name)
        nets = list(set(nets))
        max_width = 0
        for net in nets:
            for primitive in self.nets[net].primitives:
                if primitive.type == "Path":
                    max_width = max(max_width, primitive.width)

        for layer in list(self.stackup.dielectric_layers.values()):
            max_width = max(max_width, layer.thickness)

        max_width = max_width * expansion_factor
        self.logger.info(f"The W factor is {expansion_factor}, The initial extent = {max_width}")
        return max_width

    def copy_zones(self, working_directory=None) -> dict[str, tuple[int, GrpcPolygonData]]:
        """Copy multi-zone EDB project to one new edb per zone.

        Parameters
        ----------
        working_directory : str
            Directory path where all EDB project are copied, if empty will use the current EDB project.

        Returns
        -------
        dict[str, tuple[int,:class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`]]

           Return a dictionary with edb path as key and tuple Zone Id as first item and EDB polygon Data defining
           the region as second item.

        """
        if working_directory:
            if not os.path.isdir(working_directory):
                os.mkdir(working_directory)
            else:
                shutil.rmtree(working_directory)
                os.mkdir(working_directory)
        else:
            working_directory = os.path.dirname(self.edbpath)
        self.layout.synchronize_bend_manager()
        zone_primitives = self.layout.zone_primitives
        zone_ids = self.stackup.zone_ids
        edb_zones = {}
        if not self.setups:
            self.siwave.add_siwave_syz_analysis()
            self.save()
        for zone_primitive in zone_primitives:
            if zone_primitive:
                edb_zone_path = os.path.join(working_directory, f"{zone_primitive.id}_{os.path.basename(self.edbpath)}")
                shutil.copytree(self.edbpath, edb_zone_path)
                poly_data = zone_primitive.polygon_data
                if self.version[0] >= 10:
                    edb_zones[edb_zone_path] = (zone_primitive.id, poly_data)
                elif len(zone_primitives) == len(zone_ids):
                    edb_zones[edb_zone_path] = (zone_ids[0], poly_data)
                else:
                    self.logger.info(
                        "Number of zone primitives is not equal to zone number. Zone information will be lost."
                        "Use Ansys 2024 R1 or later."
                    )
                    edb_zones[edb_zone_path] = (-1, poly_data)
        return edb_zones

    def cutout_multizone_layout(self, zone_dict, common_reference_net=None):
        """Create a multizone project cutout.

        Parameters
        ----------
        zone_dict : dict[str](EDB PolygonData)
            Dictionary with EDB path as key and EDB PolygonData as value defining the zone region.
            This dictionary is returned from the command copy_zones():
            >>> edb = Edb(edb_file)
            >>> zone_dict = edb.copy_zones(r"C:\Temp\test")

        common_reference_net : str
            the common reference net name. This net name must be provided to provide a valid project.

        Returns
        -------
        dict[str: str] or list[str]
            first dictionary defined_ports with edb name as key and existing port name list as value. Those ports are
            the ones defined before processing the multizone clipping. the second is the list of connected port.

        """
        terminals = {}
        defined_ports = {}
        project_connexions = None
        for edb_path, zone_info in zone_dict.items():
            edb = Edb(edbversion=self.version, edbpath=edb_path)
            edb.cutout(
                use_pyaedt_cutout=True,
                custom_extent=zone_info[1],
                open_cutout_at_end=True,
            )
            if not zone_info[0] == -1:
                layers_to_remove = [
                    lay.name for lay in list(edb.stackup.layers.values()) if not lay.is_in_zone(zone_info[0])
                ]
                for layer in layers_to_remove:
                    edb.stackup.remove_layer(layer)
            edb.stackup.stackup_mode = "Laminate"
            edb.cutout(
                use_pyaedt_cutout=True,
                custom_extent=zone_info[1],
                open_cutout_at_end=True,
            )
            edb.active_cell.name = os.path.splitext(os.path.basename(edb_path))[0]
            if common_reference_net:
                signal_nets = list(self.nets.signal.keys())
                defined_ports[os.path.splitext(os.path.basename(edb_path))[0]] = list(edb.excitations.keys())
                edb_terminals_info = edb.source_excitation.create_vertical_circuit_port_on_clipped_traces(
                    nets=signal_nets,
                    reference_net=common_reference_net,
                    user_defined_extent=zone_info[1],
                )
                if edb_terminals_info:
                    terminals[os.path.splitext(os.path.basename(edb_path))[0]] = edb_terminals_info
                project_connexions = self._get_connected_ports_from_multizone_cutout(terminals)
            edb.save_edb()
            edb.close_edb()
        return defined_ports, project_connexions

    @staticmethod
    def _get_connected_ports_from_multizone_cutout(terminal_info_dict):
        """Return connected port list from clipped multizone layout.

        Parameters
            terminal_info_dict : dict[str][str]
                dictionary terminals with edb name as key and created ports name on clipped signal nets.
                Dictionary is generated by the command cutout_multizone_layout:
                >>> edb = Edb(edb_file)
                >>> edb_zones = edb.copy_zones(r"C:\Temp\test")
                >>> defined_ports, terminals_info = edb.cutout_multizone_layout(edb_zones, common_reference_net)
                >>> project_connexions = get_connected_ports(terminals_info)

        Returns
        -------
        list[str]
            list of connected ports.
        """
        if terminal_info_dict:
            tolerance = 1e-8
            connected_ports_list = []
            project_list = list(terminal_info_dict.keys())
            project_combinations = list(combinations(range(0, len(project_list)), 2))
            for comb in project_combinations:
                terminal_set1 = terminal_info_dict[project_list[comb[0]]]
                terminal_set2 = terminal_info_dict[project_list[comb[1]]]
                project1_nets = [t[0] for t in terminal_set1]
                project2_nets = [t[0] for t in terminal_set2]
                net_with_connected_ports = list(set(project1_nets).intersection(project2_nets))
                if net_with_connected_ports:
                    for net_name in net_with_connected_ports:
                        project1_port_info = [term_info for term_info in terminal_set1 if term_info[0] == net_name]
                        project2_port_info = [term_info for term_info in terminal_set2 if term_info[0] == net_name]
                        port_list = [p[3] for p in project1_port_info] + [p[3] for p in project2_port_info]
                        port_combinations = list(combinations(port_list, 2))
                        for port_combination in port_combinations:
                            if not port_combination[0] == port_combination[1]:
                                port1 = [port for port in terminal_set1 if port[3] == port_combination[0]]
                                if not port1:
                                    port1 = [port for port in terminal_set2 if port[3] == port_combination[0]]
                                port2 = [port for port in terminal_set2 if port[3] == port_combination[1]]
                                if not port2:
                                    port2 = [port for port in terminal_set1 if port[3] == port_combination[1]]
                                port1 = port1[0]
                                port2 = port2[0]
                                if not port1[3] == port2[3]:
                                    port_distance = GeometryOperators.points_distance(port1[1:3], port2[1:3])
                                    if port_distance < tolerance:
                                        port1_connexion = None
                                        port2_connexion = None
                                        for (
                                            project_path,
                                            port_info,
                                        ) in terminal_info_dict.items():
                                            port1_map = [port for port in port_info if port[3] == port1[3]]
                                            if port1_map:
                                                port1_connexion = (
                                                    project_path,
                                                    port1[3],
                                                )
                                            port2_map = [port for port in port_info if port[3] == port2[3]]
                                            if port2_map:
                                                port2_connexion = (
                                                    project_path,
                                                    port2[3],
                                                )
                                        if port1_connexion and port2_connexion:
                                            if (
                                                not port1_connexion[0] == port2_connexion[0]
                                                or not port1_connexion[1] == port2_connexion[1]
                                            ):
                                                connected_ports_list.append((port1_connexion, port2_connexion))
            return connected_ports_list

    def create_port(self, terminal, ref_terminal=None, is_circuit_port=False, name=None):
        """Create a port.

        ..deprecated:: 0.51.0
           Use :func:`create_port` has been moved to source_excitation.create_port.

        """

        warnings.warn("Use create_port from edb.source_excitation.create_port", DeprecationWarning)
        return self.source_excitation.create_port(terminal, ref_terminal, is_circuit_port, name)

    def create_voltage_probe(self, terminal, ref_terminal):
        """Create a voltage probe.

        ..deprecated:: 0.50.0
           Use :func:`create_voltage_probe` has been moved to edb.source_excitation.create_voltage_probe.

        """
        warnings.warn("Use create_voltage_probe located in edb.source_excitation instead", DeprecationWarning)
        return self.source_excitation.create_voltage_probe(terminal, ref_terminal)

    def create_voltage_source(self, terminal, ref_terminal):
        """Create a voltage source.

        ..deprecated:: 0.50.0
           Use: func:`create_voltage_source` has been moved to edb.source_excitation.create_voltage_source.

        """
        warnings.warn(
            "use create_voltage_source located in edb.source_excitation.create_voltage_source instead",
            DeprecationWarning,
        )
        return self.source_excitation.create_voltage_source(terminal, ref_terminal)

    def create_current_source(self, terminal, ref_terminal):
        """Create a current source.

        ..deprecated:: 0.50.0
           Use :func:`create_current_source` has been moved to edb.source_excitation.create_current_source.

        """
        warnings.warn(
            "use create_current_source located in edb.source_excitation.create_current_source instead",
            DeprecationWarning,
        )
        return self.source_excitation.create_current_source(terminal, ref_terminal)

    def get_point_terminal(self, name, net_name, location, layer):
        """Place terminal between two points.

        ..deprecated:: 0.50.0
           Use: func:`get_point_terminal` has been moved to edb.source_excitation.get_point_terminal.
        """

        warnings.warn(
            "use get_point_terminal located in edb.source_excitation.get_point_terminal instead", DeprecationWarning
        )
        return self.source_excitation.get_point_terminal(name, net_name, location, layer)

    def auto_parametrize_design(
        self,
        layers=True,
        materials=True,
        via_holes=True,
        pads=True,
        antipads=True,
        traces=True,
        layer_filter=None,
        material_filter=None,
        padstack_definition_filter=None,
        trace_net_filter=None,
        use_single_variable_for_padstack_definitions=True,
        use_relative_variables=True,
        output_aedb_path=None,
        open_aedb_at_end=True,
        expand_polygons_size=0,
        expand_voids_size=0,
        via_offset=True,
    ):
        """Automatically parametrize design elements.

        Parameters
        ----------
        layers : bool, optional
            Parametrize layer thicknesses. Default True.
        materials : bool, optional
            Parametrize material properties. Default True.
        via_holes : bool, optional
            Parametrize via holes. Default True.
        pads : bool, optional
            Parametrize pads. Default True.
        antipads : bool, optional
            Parametrize antipads. Default True.
        traces : bool, optional
            Parametrize trace widths. Default True.
        layer_filter : list, optional
            Layers to include. All if None.
        material_filter : list, optional
            Materials to include. All if None.
        padstack_definition_filter : list, optional
            Padstacks to include. All if None.
        trace_net_filter : list, optional
            Nets to parametrize. All if None.
        use_single_variable_for_padstack_definitions : bool, optional
            Single variable per padstack. Default True.
        use_relative_variables : bool, optional
            Use delta variables. Default True.
        output_aedb_path : str, optional
            Output AEDB path.
        open_aedb_at_end : bool, optional
            Open AEDB when finished. Default True.
        expand_polygons_size : float, optional
            Polygon expansion size. Default 0.
        expand_voids_size : float, optional
            Void expansion size. Default 0.
        via_offset : bool, optional
            Parametrize via positions. Default True.

        Returns
        -------
        list[str]
            Created parameter names.

        Examples
        --------
        Parametrize design elements:
        >>> params = edb.auto_parametrize_design(
        >>>     layers=True,
        >>>     materials=True,
        >>>     trace_net_filter=["Clock"])
        """
        edb_original_path = self.edbpath
        if output_aedb_path:
            self.save_as(output_aedb_path)
        if isinstance(trace_net_filter, str):
            trace_net_filter = [trace_net_filter]
        parameters = []

        def _apply_variable(orig_name, orig_value):
            if use_relative_variables:
                var = f"{orig_name}_delta"
            else:
                var = f"{orig_name}_value"
            var = self._clean_string_for_variable_name(var)
            if var not in self.variables:
                if use_relative_variables:
                    if var.startswith("$"):
                        self.add_project_variable(var, 0.0)
                    else:
                        self.add_design_variable(var, 0.0)
                else:
                    if var.startswith("$"):
                        self.add_project_variable(var, orig_value)
                    else:
                        self.add_design_variable(var, orig_value)
            if use_relative_variables:
                return f"{orig_value}+{var}", var
            else:
                return var, var

        if layers:
            if not layer_filter:
                _layers = self.stackup.layers
            else:
                if isinstance(layer_filter, str):
                    layer_filter = [layer_filter]
                _layers = {k: v for k, v in self.stackup.layers.items() if k in layer_filter}
            for layer_name, layer in _layers.items():
                var, val = _apply_variable(f"${layer_name}", layer.thickness)
                layer.thickness = Value(var, self.active_db)
                parameters.append(val)
        if materials:
            if not material_filter:
                _materials = self.materials.materials
            else:
                _materials = {k: v for k, v in self.materials.materials.items() if k in material_filter}
            for mat_name, material in _materials.items():
                if not material.conductivity or material.conductivity < 1e4:
                    var, val = _apply_variable(f"$epsr_{mat_name}", material.permittivity)
                    material.permittivity = Value(var, self.active_db)
                    parameters.append(val)
                    var, val = _apply_variable(f"$loss_tangent_{mat_name}", material.dielectric_loss_tangent)
                    material.dielectric_loss_tangent = Value(var, self.active_db)
                    parameters.append(val)
                else:
                    var, val = _apply_variable(f"$sigma_{mat_name}", material.conductivity)
                    material.conductivity = Value(var, self.active_db)
                    parameters.append(val)
        if traces:
            if not trace_net_filter:
                paths = self.modeler.paths
            else:
                paths = [path for path in self.modeler.paths if path.net_name in trace_net_filter]
            for path in paths:
                net_name = path.net_name
                if use_relative_variables:
                    trace_width_variable = "trace"
                elif net_name:
                    trace_width_variable = f"{path.net_name}_{path.aedt_name}"
                else:
                    trace_width_variable = f"{path.aedt_name}"
                var, val = _apply_variable(trace_width_variable, path.width)
                path.width = Value(var, self.active_cell)
                parameters.append(val)
        if not padstack_definition_filter:
            if trace_net_filter:
                padstack_defs = {}
                for net in trace_net_filter:
                    for via in self.nets[net].padstack_instances:
                        padstack_defs[via.padstack_definition] = self.padstacks.definitions[via.padstack_definition]
            else:
                used_padsatck_defs = list(
                    set(
                        [padstack_inst.padstack_definition for padstack_inst in list(self.padstacks.instances.values())]
                    )
                )
                padstack_defs = {k: v for k, v in self.padstacks.definitions.items() if k in used_padsatck_defs}
        else:
            padstack_defs = {k: v for k, v in self.padstacks.definitions.items() if k in padstack_definition_filter}

        for def_name, padstack_def in padstack_defs.items():
            if not padstack_def.start_layer == padstack_def.stop_layer:
                if via_holes:  # pragma no cover
                    if use_relative_variables:
                        hole_variable = "$hole_diameter"
                    else:
                        hole_variable = f"${def_name}_hole_diameter"
                    if padstack_def.hole_diameter:
                        var, val = _apply_variable(hole_variable, padstack_def.hole_diameter)
                        padstack_def.hole_properties = Value(var, self.active_db)
                        parameters.append(val)
            if pads:
                for layer, pad in padstack_def.pad_by_layer.items():
                    if use_relative_variables:
                        pad_name = "$pad"
                    elif use_single_variable_for_padstack_definitions:
                        pad_name = f"${def_name}_pad"
                    else:
                        pad_name = f"${def_name}_{layer}_pad"

                    if pad.geometry_type in [1, 2]:
                        var, val = _apply_variable(pad_name, pad.parameters_values_string[0])
                        if pad.geometry_type == 1:
                            pad.parameters = {"Diameter": var}
                        else:
                            pad.parameters = {"Size": var}
                        parameters.append(val)
                    elif pad.geometry_type == 3:  # pragma no cover
                        if use_relative_variables:
                            pad_name_x = "$pad_x"
                            pad_name_y = "$pad_y"
                        elif use_single_variable_for_padstack_definitions:
                            pad_name_x = f"${def_name}_pad_x"
                            pad_name_y = f"${def_name}_pad_y"
                        else:
                            pad_name_x = f"${def_name}_{layer}_pad_x"
                            pad_name_y = f"${def_name}_pad_y"
                        var, val = _apply_variable(pad_name_x, pad.parameters_values_string[0])
                        var2, val2 = _apply_variable(pad_name_y, pad.parameters_values_string[1])

                        pad.parameters = {"XSize": var, "YSize": var2}
                        parameters.append(val)
                        parameters.append(val2)
            if antipads:
                for layer, antipad in padstack_def.antipad_by_layer.items():
                    if antipad:
                        if use_relative_variables:
                            pad_name = "$antipad"
                        elif use_single_variable_for_padstack_definitions:
                            pad_name = f"${def_name}_antipad"
                        else:
                            pad_name = f"${def_name}_{layer}_antipad"

                        if antipad.geometry_type in [1, 2]:
                            var, val = _apply_variable(pad_name, antipad.parameters_values_string[0])
                            if antipad.geometry_type == 1:  # pragma no cover
                                antipad.parameters = {"Diameter": var}
                            else:
                                antipad.parameters = {"Size": var}
                            parameters.append(val)
                        elif antipad.geometry_type == 3:  # pragma no cover
                            if use_relative_variables:
                                pad_name_x = "$antipad_x"
                                pad_name_y = "$antipad_y"
                            elif use_single_variable_for_padstack_definitions:
                                pad_name_x = f"${def_name}_antipad_x"
                                pad_name_y = f"${def_name}_antipad_y"
                            else:
                                pad_name_x = f"${def_name}_{layer}_antipad_x"
                                pad_name_y = f"${def_name}_antipad_y"

                            var, val = _apply_variable(pad_name_x, antipad.parameters_values_string[0])
                            var2, val2 = _apply_variable(pad_name_y, antipad.parameters_values_string[1])
                            antipad.parameters = {"XSize": var, "YSize": var2}
                            parameters.append(val)
                            parameters.append(val2)

        if via_offset:
            var_x = "via_offset_x"
            if var_x not in self.variables:
                self.add_design_variable(var_x, 0.0)
            var_y = "via_offset_y"
            if var_y not in self.variables:
                self.add_design_variable(var_y, 0.0)
            for via in self.padstacks.instances.values():
                if not via.is_pin and (not trace_net_filter or (trace_net_filter and via.net_name in trace_net_filter)):
                    via.position = [f"{via.position[0]}+via_offset_x", f"{via.position[1]}+via_offset_y"]

        if expand_polygons_size:
            for poly in self.modeler.polygons:
                if not poly.is_void:
                    poly.expand(expand_polygons_size)
        if expand_voids_size:
            for poly in self.modeler.polygons:
                if poly.is_void:
                    poly.expand(expand_voids_size, round_corners=False)
                elif poly.has_voids:
                    for void in poly.voids:
                        void.expand(expand_voids_size, round_corners=False)

        if not open_aedb_at_end and self.edbpath != edb_original_path:
            self.save()
            self.close()
            self.edbpath = edb_original_path
            self.open()
        return parameters

    @staticmethod
    def _clean_string_for_variable_name(variable_name):
        """Remove forbidden character for variable name.
        Parameters
        ----------
        variable_name : str
                Variable name.
        Returns
        -------
        str
            Edited name.
        """
        if "-" in variable_name:
            variable_name = variable_name.replace("-", "_")
        if "+" in variable_name:
            variable_name = variable_name.replace("+", "p")
        variable_name = re.sub(r"[() ]", "_", variable_name)

        return variable_name

    def create_model_for_arbitrary_wave_ports(
        self,
        temp_directory,
        mounting_side="top",
        signal_nets=None,
        terminal_diameter=None,
        output_edb=None,
        launching_box_thickness="100um",
    ):
        """Create simplified model for arbitrary wave port generation.

        Parameters
        ----------
        temp_directory : str
            Working directory.
        mounting_side : str, optional
            Board orientation ("top" or "bottom").
        signal_nets : list, optional
            Nets to include. All if None.
        terminal_diameter : float, optional
            Custom terminal diameter. Auto-calculated if None.
        output_edb : str, optional
            Output AEDB path.
        launching_box_thickness : str, optional
            Wave port box thickness.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not temp_directory:
            self.logger.error("Temp directory must be provided when creating model foe arbitrary wave port")
            return False
        if mounting_side not in ["top", "bottom"]:
            self.logger.error(
                "Mounting side must be provided and only `top` or `bottom` are supported. Setting to "
                "`top` will take the top layer from the current design as reference. Setting to `bottom` "
                "will take the bottom one."
            )
        if not output_edb:
            output_edb = os.path.join(temp_directory, "waveport_model.aedb")
        else:
            output_edb = os.path.join(temp_directory, output_edb)
        if os.path.isdir(temp_directory):
            shutil.rmtree(temp_directory)
        os.mkdir(temp_directory)
        reference_layer = list(self.stackup.signal_layers.keys())[0]
        if mounting_side.lower() == "bottom":
            reference_layer = list(self.stackup.signal_layers.keys())[-1]
        if not signal_nets:
            signal_nets = list(self.nets.signal.keys())

        used_padstack_defs = []
        padstack_instances_index = rtree.index.Index()
        for padstack_inst in list(self.padstacks.instances.values()):
            if not reference_layer in [padstack_inst.start_layer, padstack_inst.stop_layer]:
                padstack_inst.delete()
            else:
                if padstack_inst.net.name in signal_nets:
                    padstack_instances_index.insert(padstack_inst.edb_uid, padstack_inst.position)
                    if not padstack_inst.padstack_def.name in used_padstack_defs:
                        used_padstack_defs.append(padstack_inst.padstack_def.name)

        polys = [
            poly
            for poly in self.modeler.primitives
            if poly.layer.name == reference_layer and self.modeler.primitives[0].type == "polygon" and poly.has_voids
        ]
        if not polys:
            self.logger.error(
                f"No polygon found with voids on layer {reference_layer} during model creation for arbitrary wave ports"
            )
            return False
        void_padstacks = []
        for poly in polys:
            for void in poly.voids:
                void_bbox = void.bbox
                included_instances = list(padstack_instances_index.intersection(void_bbox))
                if included_instances:
                    void_padstacks.append((void, [self.padstacks.instances[edb_uid] for edb_uid in included_instances]))

        if not void_padstacks:
            self.logger.error(
                "No padstack instances found inside evaluated voids during model creation for arbitrary waveports"
            )
            return False
        cloned_edb = Edb(edbpath=output_edb, edbversion=self.version, restart_rpc_server=True)

        cloned_edb.stackup.add_layer(
            layer_name="ports",
            layer_type="signal",
            thickness=self.stackup.signal_layers[reference_layer].thickness,
            material="pec",
        )
        if launching_box_thickness:
            launching_box_thickness = str(Value(launching_box_thickness))
        cloned_edb.stackup.add_layer(
            layer_name="ref",
            layer_type="signal",
            thickness=0.0,
            material="pec",
            method=f"add_on_{mounting_side}",
            base_layer="ports",
        )
        cloned_edb.stackup.add_layer(
            layer_name="port_pec",
            layer_type="signal",
            thickness=launching_box_thickness,
            method=f"add_on_{mounting_side}",
            material="pec",
            base_layer="ports",
        )
        for void_info in void_padstacks:
            port_poly = cloned_edb.modeler.create_polygon(
                points=void_info[0].polygon_data, layer_name="ref", net_name="GND"
            )
            pec_poly = cloned_edb.modeler.create_polygon(
                points=port_poly.polygon_data, layer_name="port_pec", net_name="GND"
            )
            pec_poly.scale(1.5)

        for void_info in void_padstacks:
            for inst in void_info[1]:
                if not terminal_diameter:
                    pad_diameter = (
                        self.padstacks.definitions[inst.padstack_def.name]
                        .pad_by_layer[reference_layer]
                        .parameters_values
                    )
                else:
                    pad_diameter = Value(terminal_diameter)
                _temp_circle = cloned_edb.modeler.create_circle(
                    layer_name="ports",
                    x=inst.position[0],
                    y=inst.position[1],
                    radius=pad_diameter[0] / 2,
                    net_name=inst.net_name,
                )
                if not _temp_circle:
                    self.logger.error(
                        f"Failed to create circle for terminal during create_model_for_arbitrary_wave_ports"
                    )
        cloned_edb.save_as(output_edb)
        cloned_edb.close(terminate_rpc_session=False)
        return True

    @property
    def definitions(self):
        """EDB definitions access.

        Returns
        -------
        :class:`Definitions <pyedb.grpc.database.definitions.Definitions>`
            Definitions interface.
        """
        from pyedb.grpc.database.definitions import Definitions

        return Definitions(self)

    @property
    def workflow(self):
        """Workflow automation interface.

        Returns
        -------
        :class:`Workflow <pyedb.workflow.Workflow>`
            Workflow automation tools.
        """
        return Workflow(self)

    def export_gds_comp_xml(self, comps_to_export, gds_comps_unit="mm", control_path=None):
        """Export component data to GDS XML control file.

        Parameters
        ----------
        comps_to_export : list
            Components to export.
        gds_comps_unit : str, optional
            Output units. Default "mm".
        control_path : str, optional
            Output XML path.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        from pyedb.generic.general_methods import ET

        components = ET.Element("GDS_COMPONENTS")
        components.set("LengthUnit", gds_comps_unit)
        if not comps_to_export:
            comps_to_export = self.components
        for comp in comps_to_export:
            ocomp = self.components[comp]
            gds_component = ET.SubElement(components, "GDS_COMPONENT")
            for pin_name, pin in ocomp.pins.items():
                pins_position_unit = unit_converter(pin.position, output_units=gds_comps_unit)
                gds_pin = ET.SubElement(gds_component, "GDS_PIN")
                gds_pin.set("Name", pin_name)
                gds_pin.set("x", str(pins_position_unit[0]))
                gds_pin.set("y", str(pins_position_unit[1]))
                gds_pin.set("Layer", pin.placement_layer)
            component = ET.SubElement(gds_component, "Component")
            component.set("RefDes", ocomp.refdes)
            component.set("PartName", ocomp.partname)
            component.set("PartType", ocomp.type)
        tree = ET.ElementTree(components)
        ET.indent(tree, space="\t", level=0)
        tree.write(control_path)
        return True if os.path.exists(control_path) else False

    def compare(self, input_file, results=""):
        """Compares current open database with another one.

        .. warning::
            Do not execute this function with untrusted function argument, environment
            variables or pyedb global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        input_file : str
            Path to the edb file.
        results: str, optional
            Path to directory in which results will be saved. If no path is given, a new "_compare_results"
            directory will be created with the same naming and path as the .aedb folder.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.save()
        if not results:
            results = self.edbpath[:-5] + "_compare_results"
            os.mkdir(results)
        executable_path = os.path.join(self.base_path, "EDBDiff.exe")
        if is_linux:
            mono_path = os.path.join(self.base_path, "common/mono/Linux64/bin/mono")
            command = [mono_path, executable_path, input_file, self.edbpath, results]
        else:
            command = [executable_path, input_file, self.edbpath, results]
        try:
            subprocess.run(command, check=True)  # nosec
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError(
                "EDBDiff.exe execution failed. Please check if the executable is present in the base path."
            ) from e

        if not os.path.exists(os.path.join(results, "EDBDiff.csv")):
            self.logger.error("Comparison execution failed")
            return False
        else:
            self.logger.info("Comparison correctly completed")
            return True

    def import_layout_component(self, component_path) -> GrpcLayoutComponent:
        """Import a layout component inside the current layout and place it at the origin.
        This feature is only supported with PyEDB gRPC. Encryption is not yet supported.

        Parameters
        ----------
        component_path : str
            Layout component path (.aedbcomp file).

        Returns
        -------
            class:`LayoutComponent <ansys.edb.core.hierarchy.layout_component.LayoutComponent>`.
        """

        return GrpcLayoutComponent.import_layout_component(
            layout=self.active_layout.core, aedb_comp_path=component_path
        )

    def export_layout_component(self, component_path) -> bool:
        """Export a layout component from the current layout.
        This feature is only supported with PyEDB gRPC. Encryption is not yet supported.

        Parameters
        ----------
        component_path : str
            Layout component path (.aedbcomp file).

        Returns
        -------
        bool
            `True` if layout component is successfully exported, `False` otherwise.
        """

        return GrpcLayoutComponent.export_layout_component(
            layout=self.active_layout.core, output_aedb_comp_path=component_path
        )

    def copy_cell_from_edb(self, edb_path: Union[Path, str]):
        """Copy Cells from another Edb Database into this Database."""
        edb2 = Edb(edbpath=edb_path, edbversion=self.version)
        cells = self.copy_cells([edb2.active_cell])
        cell = cells[0]
        cell.is_blackbox = True
