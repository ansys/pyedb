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

"""This module contains the ``Edb`` class.

This module is implicitly loaded in HFSS 3D Layout when launched.

"""

from datetime import datetime
from itertools import combinations
import os
from pathlib import Path
import re
import shutil
import subprocess  # nosec B404
import sys
import time
import traceback
from typing import Union
import warnings
from zipfile import ZipFile as zpf

import rtree

from pyedb.configuration.configuration import Configuration
import pyedb.dotnet
from pyedb.dotnet.database.cell.layout import Layout
from pyedb.dotnet.database.cell.terminal.terminal import Terminal
from pyedb.dotnet.database.components import Components
import pyedb.dotnet.database.dotnet.database
from pyedb.dotnet.database.edb_data.design_options import EdbDesignOptions
from pyedb.dotnet.database.edb_data.ports import (
    BundleWavePort,
    CircuitPort,
    CoaxPort,
    ExcitationSources,
    GapPort,
    WavePort,
)
from pyedb.dotnet.database.edb_data.raptor_x_simulation_setup_data import (
    RaptorXSimulationSetup,
)
from pyedb.dotnet.database.edb_data.simulation_configuration import (
    SimulationConfiguration,
)
from pyedb.dotnet.database.edb_data.sources import SourceType
from pyedb.dotnet.database.edb_data.variables import Variable
from pyedb.dotnet.database.general import (
    LayoutObjType,
    Primitives,
    convert_py_list_to_net_list,
)
from pyedb.dotnet.database.hfss import EdbHfss
from pyedb.dotnet.database.layout_validation import LayoutValidation
from pyedb.dotnet.database.materials import Materials
from pyedb.dotnet.database.modeler import Modeler
from pyedb.dotnet.database.net_class import (
    EdbDifferentialPairs,
    EdbExtendedNets,
    EdbNetClasses,
)
from pyedb.dotnet.database.nets import EdbNets
from pyedb.dotnet.database.padstack import EdbPadstacks
from pyedb.dotnet.database.siwave import EdbSiwave
from pyedb.dotnet.database.source_excitations import SourceExcitation
from pyedb.dotnet.database.stackup import Stackup
from pyedb.dotnet.database.utilities.hfss_simulation_setup import (
    HFSSPISimulationSetup,
    HfssSimulationSetup,
)
from pyedb.dotnet.database.utilities.siwave_simulation_setup import (
    SiwaveDCSimulationSetup,
    SiwaveSimulationSetup,
)
from pyedb.dotnet.database.utilities.value import Value
from pyedb.dotnet.database.Variables import decompose_variable_value
from pyedb.generic.constants import AEDT_UNITS, SolverType, unit_converter
from pyedb.generic.general_methods import generate_unique_name, is_linux, is_windows
from pyedb.generic.process import SiwaveSolve
from pyedb.generic.settings import settings
from pyedb.misc.decorators import deprecate_argument_name, execution_timer
from pyedb.modeler.geometry_operators import GeometryOperators
from pyedb.siwave_core.product_properties import SIwaveProperties
from pyedb.workflow import Workflow
from pyedb.workflows.utilities.cutout import Cutout


class Edb:
    """Provides the EDB application interface.

    This module inherits all objects that belong to EDB.

    Parameters
    ----------
    edbpath : str, optional
        Full path to the ``aedb`` folder. The variable can also contain
        the path to a layout to import. Allowed formats are BRD, MCM,
        XML (IPC2581), GDS, ODB++(TGZ and ZIP) and DXF. The default is ``None``.
        For GDS import, the Ansys control file (also XML) should have the same
        name as the GDS file. Only the file extension differs.
    cellname : str, optional
        Name of the cell to select. The default is ``None``.
    isreadonly : bool, optional
        Whether to open EBD in read-only mode when it is
        owned by HFSS 3D Layout. The default is ``False``.
    version : str, int, float, optional
        Version of EDB to use. The default is ``None``.
        Examples of input values are ``232``, ``23.2``, ``2023.2``, ``"2023.2"``.
    isaedtowned : bool, optional
        Whether to launch EDB from HFSS 3D Layout. The
        default is ``False``.
    oproject : optional
        Reference to the AEDT project object.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False.``
    control_file : str, optional
            Path to the XML file. The default is ``None``, in which case an attempt is made to find
            the XML file in the same directory as the board file. To succeed, the XML file and board file
            must have the same name. Only the extension differs.
    map_file : str, optional
        Layer map .map file.
    technology_file : str, optional
        Full path to technology file to be converted to xml before importing or xml.
        Supported by GDS format only.
    layer_filter:str,optional
        Layer filter .txt file.

    Examples
    --------
    Create an ``Edb`` object and a new EDB cell.

    >>> from pyedb import Edb
    >>> app = Edb()

    Add a new variable named "s1" to the ``Edb`` instance.

    >>> app["s1"] = "0.25 mm"
    >>> app["s1"].tofloat
    >>> 0.00025
    >>> app["s1"].tostring
    >>> "0.25mm"

    or add a new parameter with description:

    >>> app["s2"] = ["20um", "Spacing between traces"]
    >>> app["s2"].value
    >>> 1.9999999999999998e-05
    >>> app["s2"].description
    >>> "Spacing between traces"

    Create an ``Edb`` object and open the specified project.

    >>> app = Edb("myfile.aedb")

    Create an ``Edb`` object from GDS and control files.
    The XML control file resides in the same directory as the GDS file: (myfile.xml).

    >>> app = Edb("/path/to/file/myfile.gds")

    """

    _db = None

    @property
    def logger(self):
        return settings.logger

    @property
    def version(self):
        return settings.specified_version

    @property
    def base_path(self):
        return settings.aedt_installation_path

    @execution_timer("EDB initialization")
    def __init__(
        self,
        edbpath: Union[str, Path] = None,
        cellname: str = None,
        isreadonly: bool = False,
        isaedtowned: bool = False,
        oproject=None,
        use_ppe: bool = False,
        control_file: str = None,
        map_file: str = None,
        technology_file: str = None,
        layer_filter: str = None,
        remove_existing_aedt: bool = False,
    ):
        now = datetime.now()
        self.logger.info(f"Star initializing Edb {now.time()}")

        if isinstance(edbpath, Path):
            edbpath = str(edbpath)

        self._clean_variables()
        self.__initialization()

        self.standalone = True
        self.oproject = oproject
        self._main = sys.modules["__main__"]
        self.isaedtowned = isaedtowned
        self.isreadonly = isreadonly
        self.cellname = cellname
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
                os.path.dirname(edbpath),
                "pyedb_" + os.path.splitext(os.path.split(edbpath)[-1])[0] + ".log",
            )
            if not isreadonly:
                self._check_remove_project_files(edbpath, remove_existing_aedt)

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
        elif edbpath[-3:] in ["brd", "mcm", "sip", "gds", "xml", "dxf", "tgz", "anf"]:
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
            if settings.enable_local_log_file and self.log_name:
                self.logger.add_file_logger(self.log_name, "Edb")
            self.logger.info("EDB %s was created correctly from %s file.", self.edbpath, edbpath[-2:])
        elif edbpath.endswith("edb.def"):
            self.edbpath = os.path.dirname(edbpath)
            if settings.enable_local_log_file and self.log_name:
                self.logger.add_file_logger(self.log_name, "Edb")
            self.open_edb()
        elif not os.path.exists(os.path.join(self.edbpath, "edb.def")):
            self.create_edb()
            if settings.enable_local_log_file and self.log_name:
                self.logger.add_file_logger(self.log_name, "Edb")
            self.logger.info("EDB %s created correctly.", self.edbpath)
        elif ".aedb" in edbpath:
            self.edbpath = edbpath
            if settings.enable_local_log_file and self.log_name:
                self.logger.add_file_logger(self.log_name, "Edb")
            self.open_edb()
        if not self.active_cell:
            raise AttributeError("Failed to initialize DLLs.")

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type:
            self.edb_exception(ex_value, ex_traceback)

    def __getitem__(self, variable_name):
        """Get or Set a variable to the Edb project. The variable can be project using ``$`` prefix or
        it can be a design variable, in which case the ``$`` is omitted.

        Parameters
        ----------
        variable_name : str

        Returns
        -------
        variable object : :class:`pyedb.dotnet.database.edb_data.variables.Variable`

        """
        if self.variable_exists(variable_name)[0]:
            return self.variables[variable_name]
        return

    def __setitem__(self, variable_name, variable_value):
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
                    self.logger.warning("Invalid type for Edb variable desciprtion is ignored.")
                val = variable_value[0]
            else:
                raise TypeError(type_error_message)
        else:
            description = None
            val = variable_value
        if self.variable_exists(variable_name)[0]:
            self.change_design_variable_value(variable_name, val)
        else:
            self.add_design_variable(variable_name, val)
        if description:  # Add the variable description if a two-item list is passed for variable_value.
            self.__getitem__(variable_name).description = description

    def __initialization(self):
        self.logger.info(f"Edb version {self.version}")

        """Initialize DLLs."""
        import ctypes

        from pyedb import __version__
        from pyedb.dotnet.clr_module import _clr, edb_initialized

        if not edb_initialized:  # pragma: no cover
            raise RuntimeWarning("Failed to initialize Dlls.")
        self.logger.info(f"Logger is initialized. Log file is saved to {self.logger.log_file}.")
        self.logger.info("legacy v%s", __version__)
        self.logger.info("Python version %s", sys.version)

        sys.path.append(self.base_path)
        if is_linux:
            ctypes.cdll.LoadLibrary(
                os.path.join(self.base_path, "common", "mono", "Linux64", "lib", "libmonosgen-2.0.so.1")
            )
            ctypes.cdll.LoadLibrary(os.path.join(self.base_path, "libEDBCWrapper.so"))
        _clr.AddReference("Ansys.Ansoft.Edb")
        _clr.AddReference("Ansys.Ansoft.EdbBuilderUtils")
        _clr.AddReference("Ansys.Ansoft.SimSetupData")
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oaDirectory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)
        edb = __import__("Ansys.Ansoft.Edb")
        edbbuilder = __import__("Ansys.Ansoft.EdbBuilderUtils")
        self.simSetup = __import__("Ansys.Ansoft.SimSetupData")
        self._edb = edb.Ansoft.Edb
        self.edbutils = edbbuilder.Ansoft.EdbBuilderUtils
        self.simsetupdata = self.simSetup.Ansoft.SimSetupData.Data

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

    def _clean_variables(self):
        """Initialize internal variables and perform garbage collection."""
        self._materials = None
        self._components = None
        self._core_primitives = None
        self._stackup = None
        self._stackup2 = None
        self._padstack = None
        self._siwave = None
        self._hfss = None
        self._nets = None
        self._layout_instance = None
        self._variables = None
        self._active_cell = None
        self._layout = None
        self._configuration = None
        self._source_excitation = None

    def _init_objects(self):
        self._components = Components(self)
        self._stackup = Stackup(self, self.layout.layer_collection)
        self._padstack = EdbPadstacks(self)
        self._siwave = EdbSiwave(self)
        self._hfss = EdbHfss(self)
        self._nets = EdbNets(self)
        self._core_primitives = Modeler(self)
        self._stackup2 = self._stackup
        self._materials = Materials(self)
        self._source_excitation = SourceExcitation(self)

    @property
    def pedb_class(self):
        return pyedb.dotnet

    def value(self, val):
        """Convert a value into a pyedb value."""
        val_ = val if isinstance(val, self._edb.Utility.Value) else self.edb_value(val)
        return Value(self, val_)

    @property
    def grpc(self):
        """grpc flag."""
        return False

    @property
    def cell_names(self):
        """Cell name container.

        Returns
        -------
        list of cell names : List[str]
        """
        names = []
        for cell in [i for i in list(self._db.CircuitCells)]:
            names.append(cell.GetName())
        return names

    @property
    def design_variables(self):
        """Get all edb design variables.

        Returns
        -------
        variable dictionary : Dict[str, :class:`pyedb.dotnet.database.edb_data.variables.Variable`]
        """
        d_var = dict()
        for i in self.active_cell.GetVariableServer().GetAllVariableNames():
            d_var[i] = Variable(self, i)
        return d_var

    @property
    def ansys_em_path(self):
        return self.base_path

    @property
    def project_variables(self):
        """Get all project variables.

        Returns
        -------
        variables dictionary : Dict[str, :class:`pyedb.dotnet.database.edb_data.variables.Variable`]

        """
        p_var = dict()
        for i in self._db.GetVariableServer().GetAllVariableNames():
            p_var[i] = Variable(self, i)
        return p_var

    @property
    def layout_validation(self):
        """:class:`pyedb.dotnet.database.edb_data.layout_validation.LayoutValidation`.

        Returns
        -------
        layout validation object : :class: 'pyedb.dotnet.database.layout_validation.LayoutValidation'
        """
        return LayoutValidation(self)

    @property
    def variables(self):
        """Get all Edb variables.

        Returns
        -------
        variables dictionary : Dict[str, :class:`pyedb.dotnet.database.edb_data.variables.Variable`]

        """
        all_vars = dict()
        for i, j in self.project_variables.items():
            all_vars[i] = j.value
        for i, j in self.design_variables.items():
            all_vars[i] = j.value
        return all_vars

    @property
    def terminals(self):
        """Get terminals belonging to active layout.

        Returns
        -------
        Dict
        """

        return {i.name: i for i in self.layout.terminals}

    @property
    def excitations(self):
        """Get all layout excitations."""
        terms = [term for term in self.layout.terminals if int(term._edb_object.GetBoundaryType()) == 0]
        temp = {}
        for ter in terms:
            if "BundleTerminal" in ter._edb_object.GetType().ToString():
                temp[ter.name] = BundleWavePort(self, ter._edb_object)
            else:
                temp[ter.name] = GapPort(self, ter._edb_object)
        return temp

    @property
    def ports(self):
        """Get all ports.

        Returns
        -------
        port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                   :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,]]

        """
        temp = [term for term in self.layout.terminals if not term.is_reference_terminal]

        ports = {}
        for t in temp:
            t2 = Terminal(self, t._edb_object)
            if not t2.boundary_type == "PortBoundary":
                continue

            if t2.is_circuit_port:
                port = CircuitPort(self, t._edb_object)
                ports[port.name] = port
            elif t2.terminal_type == "BundleTerminal":
                port = BundleWavePort(self, t._edb_object)
                ports[port.name] = port
            elif t2.hfss_type == "Wave":
                ports[t2.name] = WavePort(self, t._edb_object)
            elif t2.terminal_type == "PadstackInstanceTerminal":
                ports[t2.name] = CoaxPort(self, t._edb_object)
            else:
                ports[t2.name] = GapPort(self, t._edb_object)
        return ports

    @property
    def excitations_nets(self):
        """Get all excitations net names."""
        names = list(set([i.net.name for i in self.layout.terminals]))
        names = [i for i in names if i]
        return names

    @property
    def sources(self):
        """Get all layout sources."""
        terms = [term for term in self.layout.terminals if int(term._edb_object.GetBoundaryType()) in [3, 4, 7]]
        terms = [term for term in terms if not term._edb_object.IsReferenceTerminal()]
        return {ter.name: ExcitationSources(self, ter._edb_object) for ter in terms}

    @property
    def voltage_regulator_modules(self):
        """Get all voltage regulator modules"""
        vrms = self.layout.voltage_regulators
        _vrms = {}
        for vrm in vrms:
            _vrms[vrm.name] = vrm
        return _vrms

    @property
    def probes(self):
        """Get all layout probes."""
        temp = {}
        for name, val in self.terminals.items():
            if val.boundary_type == "kVoltageProbe":
                if not val.is_reference_terminal:
                    temp[name] = val
        return temp

    @execution_timer("open_edb")
    def open_edb(self):
        """Open EDB.

        Returns
        -------
        ``True`` when succeed ``False`` if failed : bool
        """
        # self.logger.info("EDB Path is %s", self.edbpath)
        # self.logger.info("EDB Version is %s", self.version)
        # if self.version > "2023.1":
        #     self.standalone = False

        self.core.Database.SetRunAsStandAlone(self.standalone)
        self._db = self.core.Database.Open(
            self.edbpath,
            self.isreadonly,
        )
        if self._db.IsNull():
            raise AttributeError(f"Failed to open edb file {self.edbpath}")

        self.logger.info("Database {} Opened in {}".format(os.path.split(self.edbpath)[-1], self.version))

        self._active_cell = None
        if self.cellname:
            for cell in [i for i in list(self._db.TopCircuitCells)]:
                if cell.GetName() == self.cellname:
                    self._active_cell = cell
        if self._active_cell is None:
            for cell in [i for i in list(self._db.CircuitCells)]:
                if cell.GetName() == self.cellname:
                    self._active_cell = cell
        # if self._active_cell is still None, set it to default cell
        if self._active_cell is None:
            self._active_cell = list(self._db.TopCircuitCells)[0]
        self.logger.info("Cell %s Opened", self._active_cell.GetName())
        if self._active_cell:
            self._init_objects()
            self.logger.info("Builder was initialized.")
        else:
            self.logger.error("Builder was not initialized.")

        return True

    @property
    def core(self):
        """Edb Dotnet Api class.

        Returns
        -------
        :class:`pyedb.dotnet.database.dotnet.database.CellDotNet`
        """
        return self._edb

    @execution_timer("create_edb")
    def create_edb(self):
        """Create EDB.

        Returns
        -------
        ``True`` when succeed ``False`` if failed : bool
        """
        # if self.version > "2023.1":
        #     self.standalone = False

        self.core.Database.SetRunAsStandAlone(self.standalone)
        if self._db:  # pragma no cover
            self._db.Close()
        self._db = self.core.Database.Create(self.edbpath)

        if not self._db:
            self.logger.warning("Error creating the database.")
            self._active_cell = None
            return None
        if not self.cellname:
            self.cellname = generate_unique_name("Cell")
        self._active_cell = self.core.Cell.Cell.Create(self._db, self.core.Cell.CellType.CircuitCell, self.cellname)
        if self._active_cell:
            self._init_objects()
            return True
        return None

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
        """Import a board file and generate an ``edb.def`` file in the working directory.

        .. deprecated:: 0.42.0
           Use :func:`import_layout_file` method instead.

        This function supports all AEDT formats, including DXF, GDS, SML (IPC2581), BRD, MCM, SIP, ZIP and TGZ.

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

    @execution_timer("import_layout_file")
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
        self.open_edb()
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
    def configuration(self):
        """Edb project configuration from file."""
        if not self._configuration:
            self._configuration = Configuration(self)
        return self._configuration

    def edb_exception(self, ex_value, tb_data):
        """Write the trace stack to AEDT when a Python error occurs.

        Parameters
        ----------
        ex_value :

        tb_data :


        Returns
        -------
        None

        """
        tb_trace = traceback.format_tb(tb_data)
        tblist = tb_trace[0].split("\n")
        self.logger.error(str(ex_value))
        for el in tblist:
            self.logger.error(el)

    @property
    def active_db(self):
        """Database object."""
        return self._db

    @property
    def active_cell(self):
        """Active cell."""
        return self._active_cell

    @active_cell.setter
    def active_cell(self, value):
        if isinstance(value, str):
            _cell = [cell for cell in self.circuit_cells if cell.GetName() == value]
            if _cell:
                self._active_cell = _cell[0]
                self._init_objects()
                self.logger.info(f"Cell {value} set as active")
            else:
                raise f"Design {value} not found in database."
        elif isinstance(value, pyedb.dotnet.database.dotnet.database.CellClassDotNet):
            self._active_cell = value
            self._init_objects()
            self.logger.info(f"Cell {value.GetName()} set as active")
        else:
            raise "No valid design."

    @property
    def core_components(self):  # pragma: no cover
        """Edb Components methods and properties.

        .. deprecated:: 0.6.62
           Use new property :func:`components` instead.

        Returns
        -------
        Instance of :class:`pyedb.dotnet.database.Components.Components`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> comp = edbapp.components.get_component_by_name("J1")
        """
        warnings.warn("Use new property :func:`components` instead.", DeprecationWarning)
        return self.components

    @property
    def components(self):
        """Edb Components methods and properties.

        Returns
        -------
        Instance of :class:`pyedb.dotnet.database.components.Components`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> comp = edbapp.components.get_component_by_name("J1")
        """
        if not self._components and self._db:
            self._components = Components(self)
        return self._components

    @property
    def core_stackup(self):
        """Core stackup.

        .. deprecated:: 0.6.5
            There is no need to use the ``core_stackup`` property anymore.
            You can instantiate a new ``stackup`` class directly from the ``Edb`` class.
        """
        mess = "`core_stackup` is deprecated.\n"
        mess += " Use `app.stackup` directly to instantiate new stackup methods."
        warnings.warn(mess, DeprecationWarning)
        if not self._stackup and self._db:
            self._stackup = Stackup(self)
        return self._stackup

    @property
    def design_options(self):
        """Edb Design Settings and Options.

        Returns
        -------
        Instance of :class:`pyedb.dotnet.database.edb_data.design_options.EdbDesignOptions`
        """
        return EdbDesignOptions(self.active_cell)

    @property
    def stackup(self):
        """Stackup manager.

        Returns
        -------
        Instance of :class: 'pyedb.dotnet.database.Stackup`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> edbapp.stackup.layers["TOP"].thickness = 4e-5
        >>> edbapp.stackup.layers["TOP"].thickness == 4e-05
        >>> edbapp.stackup.add_layer("Diel", "GND", layer_type="dielectric", thickness="0.1mm", material="FR4_epoxy")
        """
        return Stackup(self, self.layout.layer_collection)

    @property
    def source_excitation(self):
        return self._source_excitation

    @property
    def materials(self):
        """Material Database.

        Returns
        -------
        Instance of :class: `pyedb.dotnet.database.Materials`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb()
        >>> edbapp.materials.add_material("air", permittivity=1.0)
        >>> edbapp.materials.add_debye_material("debye_mat", 5, 3, 0.02, 0.05, 1e5, 1e9)
        >>> edbapp.materials.add_djordjevicsarkar_material("djord_mat", 3.3, 0.02, 3.3)
        """
        if not self._materials and self._db:
            self._materials = Materials(self)
        return self._materials

    @property
    def core_padstack(self):  # pragma: no cover
        """Core padstack.


        .. deprecated:: 0.6.62
           Use new property :func:`padstacks` instead.

        Returns
        -------
        Instance of :class: `pyedb.dotnet.database.padstack.EdbPadstack`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> p = edbapp.padstacks.create(padstackname="myVia_bullet", antipad_shape="Bullet")
        >>> edbapp.padstacks.get_pad_parameters(
        >>> ... p, "TOP", edbapp.padstacks.pad_type.RegularPad
        >>> ... )
        """

        warnings.warn("Use new property :func:`padstacks` instead.", DeprecationWarning)
        return self.padstacks

    @property
    def padstacks(self):
        """Core padstack.


        Returns
        -------
        Instance of :class: `legacy.database.padstack.EdbPadstack`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> p = edbapp.padstacks.create(padstackname="myVia_bullet", antipad_shape="Bullet")
        >>> edbapp.padstacks.get_pad_parameters(
        >>> ... p, "TOP", edbapp.padstacks.pad_type.RegularPad
        >>> ... )
        """

        if not self._padstack and self._db:
            self._padstack = EdbPadstacks(self)
        return self._padstack

    @property
    def core_siwave(self):  # pragma: no cover
        """Core SIWave methods and properties.

        .. deprecated:: 0.6.62
           Use new property :func:`siwave` instead.

        Returns
        -------
        Instance of :class: `pyedb.dotnet.database.siwave.EdbSiwave`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> p2 = edbapp.siwave.create_circuit_port_on_net("U2A5", "V3P3_S0", "U2A5", "GND", 50, "test")
        """
        warnings.warn("Use new property :func:`siwave` instead.", DeprecationWarning)
        return self.siwave

    @property
    def siwave(self):
        """Core SIWave methods and properties.

        Returns
        -------
        Instance of :class: `pyedb.dotnet.database.siwave.EdbSiwave`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> p2 = edbapp.siwave.create_circuit_port_on_net("U2A5", "V3P3_S0", "U2A5", "GND", 50, "test")
        """
        if not self._siwave and self._db:
            self._siwave = EdbSiwave(self)
        return self._siwave

    @property
    def core_hfss(self):  # pragma: no cover
        """Core HFSS methods and properties.

        .. deprecated:: 0.6.62
           Use new property :func:`hfss` instead.

        Returns
        -------
        Instance of :class:`legacy.database.hfss.EdbHfss`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> edbapp.hfss.configure_hfss_analysis_setup(sim_config)
        """
        warnings.warn("Use new property :func:`hfss` instead.", DeprecationWarning)
        return self.hfss

    @property
    def hfss(self):
        """Core HFSS methods and properties.

        Returns
        -------
        :class:`pyedb.dotnet.database.hfss.EdbHfss`

        See Also
        --------
        :class:`legacy.database.edb_data.simulation_configuration.SimulationConfiguration`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> sim_config = edbapp.new_simulation_configuration()
        >>> sim_config.mesh_freq = "10Ghz"
        >>> edbapp.hfss.configure_hfss_analysis_setup(sim_config)
        """
        if not self._hfss and self._db:
            self._hfss = EdbHfss(self)
        return self._hfss

    @property
    def core_nets(self):  # pragma: no cover
        """Core nets.

        .. deprecated:: 0.6.62
           Use new property :func:`nets` instead.

        Returns
        -------
        :class:`pyedb.dotnet.database.nets.EdbNets`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> edbapp.nets.find_or_create_net("GND")
        >>> edbapp.nets.find_and_fix_disjoint_nets("GND", keep_only_main_net=True)
        """
        warnings.warn("Use new property :func:`nets` instead.", DeprecationWarning)
        return self.nets

    @property
    def nets(self):
        """Core nets.

        Returns
        -------
        :class:`legacy.database.nets.EdbNets`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb"myproject.aedb")
        >>> edbapp.nets.find_or_create_net("GND")
        >>> edbapp.nets.find_and_fix_disjoint_nets("GND", keep_only_main_net=True)
        """

        if not self._nets and self._db:
            raise Exception("")
            self._nets = EdbNets(self)
        return self._nets

    @property
    def net_classes(self):
        """Get all net classes.

        Returns
        -------
        :class:`legacy.database.nets.EdbNetClasses`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> edbapp.net_classes
        """

        if self._db:
            return EdbNetClasses(self)

    @property
    def extended_nets(self):
        """Get all extended nets.

        Returns
        -------
        :class:`legacy.database.nets.EdbExtendedNets`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> edbapp.extended_nets
        """

        if self._db:
            return EdbExtendedNets(self)

    @property
    def differential_pairs(self):
        """Get all differential pairs.

        Returns
        -------
        :class:`legacy.database.nets.EdbDifferentialPairs`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> edbapp.differential_pairs
        """
        if self._db:
            return EdbDifferentialPairs(self)
        else:  # pragma: no cover
            return

    @property
    def core_primitives(self):  # pragma: no cover
        """Core primitives.

        .. deprecated:: 0.6.62
           Use new property :func:`modeler` instead.

        Returns
        -------
        Instance of :class: `legacy.database.layout.EdbLayout`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> top_prims = edbapp.modeler.primitives_by_layer["TOP"]
        """
        warnings.warn("Use new property :func:`modeler` instead.", DeprecationWarning)
        return self.modeler

    @property
    def modeler(self):
        """Core primitives modeler.

        Returns
        -------
        Instance of :class: `legacy.database.layout.EdbLayout`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> top_prims = edbapp.modeler.primitives_by_layer["TOP"]
        """
        if not self._core_primitives and self._db:
            self._core_primitives = Modeler(self)
        return self._core_primitives

    @property
    def layout(self) -> Layout:
        """Layout object.

        Returns
        -------
        :class:`legacy.database.dotnet.layout.Layout`
        """
        return Layout(self, self._active_cell.GetLayout())

    @property
    def active_layout(self):
        """Active layout.

        Returns
        -------
        Instance of EDB API Layout Class.
        """
        return self.layout._edb_object

    @property
    def layout_instance(self):
        """Edb Layout Instance."""
        return self.layout._edb_object.GetLayoutInstance()

    def get_connected_objects(self, layout_object_instance):
        """Get connected objects.

        Returns
        -------
        list
        """
        temp = []
        for i in list(
            [
                loi.GetLayoutObj()
                for loi in self.layout_instance.GetConnectedObjects(layout_object_instance._edb_object).Items
            ]
        ):
            obj_type = i.GetObjType().ToString()
            if obj_type == LayoutObjType.PadstackInstance.name:
                from pyedb.dotnet.database.edb_data.padstacks_data import (
                    EDBPadstackInstance,
                )

                temp.append(EDBPadstackInstance(i, self))
            elif obj_type == LayoutObjType.Primitive.name:
                prim_type = i.GetPrimitiveType().ToString()
                if prim_type == Primitives.Path.name:
                    from pyedb.dotnet.database.cell.primitive.path import Path

                    temp.append(Path(self, i))
                elif prim_type == Primitives.Rectangle.name:
                    from pyedb.dotnet.database.edb_data.primitives_data import (
                        EdbRectangle,
                    )

                    temp.append(EdbRectangle(i, self))
                elif prim_type == Primitives.Circle.name:
                    from pyedb.dotnet.database.edb_data.primitives_data import EdbCircle

                    temp.append(EdbCircle(i, self))
                elif prim_type == Primitives.Polygon.name:
                    from pyedb.dotnet.database.edb_data.primitives_data import (
                        EdbPolygon,
                    )

                    temp.append(EdbPolygon(i, self))
                else:
                    continue
            else:
                continue
        return temp

    @property
    def pins(self):
        """EDB padstack instance of the component.

        .. deprecated:: 0.6.62
           Use new method :func:`edb.padstacks.pins` instead.

        Returns
        -------
        dic[str, :class:`legacy.database.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.


        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myproject.aedb")
        >>> pin_net_name = edbapp.pins[424968329].netname
        """
        warnings.warn("Use new method :func:`edb.padstacks.pins` instead.", DeprecationWarning)
        return self.padstacks.pins

    class Boundaries:
        """Boundaries Enumerator.

        Returns
        -------
        int
        """

        (
            Port,
            Pec,
            RLC,
            CurrentSource,
            VoltageSource,
            NexximGround,
            NexximPort,
            DcTerminal,
            VoltageProbe,
        ) = range(0, 9)

    def edb_value(self, value, var_server=None):
        """Convert a value to an EDB value. Value can be a string, float or integer. Mainly used in internal calls.

        Parameters
        ----------
        value : str, float, int


        Returns
        -------
        Instance of `Edb.Utility.Value`

        """
        if isinstance(value, self.core.Utility.Value):
            return value
        if var_server:
            return self.core.Utility.Value(value, var_server)
        if isinstance(value, (int, float)):
            return self.core.Utility.Value(value)
        m1 = re.findall(r"(?<=[/+-/*//^/(/[])([a-z_A-Z/$]\w*)", str(value).replace(" ", ""))
        m2 = re.findall(r"^([a-z_A-Z/$]\w*)", str(value).replace(" ", ""))
        val_decomposed = list(set(m1).union(m2))
        if not val_decomposed:
            return self.core.Utility.Value(value)
        var_server_db = self._db.GetVariableServer()
        var_names = var_server_db.GetAllVariableNames()
        var_server_cell = self.active_cell.GetVariableServer()
        var_names_cell = var_server_cell.GetAllVariableNames()
        if set(val_decomposed).intersection(var_names_cell):
            return self.core.Utility.Value(value, var_server_cell)
        if set(val_decomposed).intersection(var_names):
            return self.core.Utility.Value(value, var_server_db)
        return self.core.Utility.Value(value)

    def point_3d(self, x, y, z=0.0):
        """Compute the Edb 3d Point Data.

        Parameters
        ----------
        x : float, int or str
            X value.
        y : float, int or str
            Y value.
        z : float, int or str, optional
            Z value.

        Returns
        -------
        ``Geometry.Point3DData``.
        """
        return self.core.Geometry.Point3DData(self.edb_value(x), self.edb_value(y), self.edb_value(z))

    def copy_cells(self, cells_to_copy):
        """Copy Cells from other Databases or this Database into this Database.

        Parameters
        ----------
        cells_to_copy : list[:class:`Cell <ansys.edb.layout.Cell>`]
            Cells to copy.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
            New Cells created in this Database.
        """
        if not isinstance(cells_to_copy, list):
            cells_to_copy = [cells_to_copy]
        _dbCells = convert_py_list_to_net_list(cells_to_copy)
        return self._db.CopyCells(_dbCells)

    def point_data(self, x, y=None):
        """Compute the Edb Point Data.

        Parameters
        ----------
        x : float, int or str
            X value.
        y : float, int or str, optional
            Y value.


        Returns
        -------
        ``Geometry.PointData``.
        """
        if y is None:
            return self.core.Geometry.PointData(self.edb_value(x))
        else:
            return self.core.Geometry.PointData(self.edb_value(x), self.edb_value(y))

    def _is_file_existing_and_released(self, filename):
        if os.path.exists(filename):
            try:
                os.rename(filename, filename + "_")
                os.rename(filename + "_", filename)
                return True
            except OSError as e:
                return False
        else:
            return False

    def _is_file_existing(self, filename):
        if os.path.exists(filename):
            return True
        else:
            return False

    def _wait_for_file_release(self, timeout=30, file_to_release=None):
        if not file_to_release:
            file_to_release = os.path.join(self.edbpath)
        tstart = time.time()
        while True:
            if self._is_file_existing_and_released(file_to_release):
                return True
            elif time.time() - tstart > timeout:
                return False
            else:
                time.sleep(0.250)

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

    def close_edb(self):
        """Close EDB and cleanup variables.

        . deprecated:: pyedb 0.47.0
        Use: func:`close` instead.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn("Use new property :func:`close` instead.", DeprecationWarning)
        return self.close()

    @execution_timer("Close Edb file")
    def close(self, **kwargs):
        """Close EDB and cleanup variables.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._db.Close()

        if self.log_name and settings.enable_local_log_file:
            self.logger.remove_all_file_loggers()
        self._wait_for_file_release()
        self._clean_variables()
        return True

    def save_edb(self):
        """Save the EDB file.

        . deprecated:: pyedb 0.47.0
        Use: func:`save` instead.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn("Use new method :func:`save` instead.", DeprecationWarning)
        return self.save()

    @execution_timer("Save Edb file")
    def save(self):
        """Save the EDB file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        self._db.Save()
        self._wait_for_file_release()
        return True

    def save_edb_as(self, path):
        """Save the EDB file as another file.

        . deprecated:: pyedb 0.47.0
        Use: func:`save_as` instead.


        Parameters
        ----------
        path : str
            Name of the new file to save to.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn("Use new property :func:`save_as` instead.", DeprecationWarning)
        return self.save_as(path)

    @execution_timer("EDB file save")
    def save_as(self, path):
        """Save the EDB file as another file.

        Parameters
        ----------
        path : str
            Name of the new file to save to.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        origin_name = "pyedb_" + os.path.splitext(os.path.split(self.edbpath)[-1])[0]
        self._db.SaveAs(path, "")
        self._wait_for_file_release()
        self.edbpath = self._db.GetDirectory()
        if self.log_name:
            self.logger.remove_file_logger(os.path.splitext(os.path.split(self.log_name)[-1])[0])

        self.log_name = os.path.join(
            os.path.dirname(path),
            "pyedb_" + os.path.splitext(os.path.split(path)[-1])[0] + ".log",
        )
        if settings.enable_local_log_file:
            self.logger.add_file_logger(self.log_name, "Edb")
            self.logger.remove_file_logger(origin_name)
        return True

    def execute(self, func):
        """Execute a function.

        Parameters
        ----------
        func : str
            Function to execute.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        return self.core.utility.utility.Command.Execute(func)

    def import_cadence_file(self, inputBrd, WorkDir=None, anstranslator_full_path="", use_ppe=False):
        """Import a board file and generate an ``edb.def`` file in the working directory.

        Parameters
        ----------
        inputBrd : str
            Full path to the board file.
        WorkDir : str, optional
            Directory in which to create the ``aedb`` folder. The default value is ``None``,
            in which case the AEDB file is given the same name as the board file. Only
            the extension differs.
        anstranslator_full_path : str, optional
            Full path to the Ansys translator.
        use_ppe : bool, optional
            Whether to use the PPE License. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.import_layout_file(
            inputBrd,
            working_dir=WorkDir,
            anstranslator_full_path=anstranslator_full_path,
            use_ppe=use_ppe,
        ):
            return True
        else:
            return False

    def _create_extent(
        self,
        net_signals,
        extent_type,
        expansion_size,
        use_round_corner,
        use_pyaedt_extent=False,
        smart_cut=False,
        reference_list=[],
        include_pingroups=True,
        pins_to_preserve=None,
        inlcude_voids_in_extents=False,
    ):
        if extent_type in [
            "Conforming",
            self.core.Geometry.ExtentType.Conforming,
            1,
        ]:
            if use_pyaedt_extent:
                _poly = self._create_conformal(
                    net_signals,
                    expansion_size,
                    1e-12,
                    use_round_corner,
                    expansion_size,
                    smart_cut,
                    reference_list,
                    pins_to_preserve,
                    inlcude_voids_in_extents=inlcude_voids_in_extents,
                )
            else:
                _poly = self.layout.expanded_extent(
                    net_signals,
                    self.core.Geometry.ExtentType.Conforming,
                    expansion_size,
                    False,
                    use_round_corner,
                    1,
                )
        elif extent_type in [
            "Bounding",
            self.core.Geometry.ExtentType.BoundingBox,
            0,
        ]:
            _poly = self.layout.expanded_extent(
                net_signals,
                self.core.Geometry.ExtentType.BoundingBox,
                expansion_size,
                False,
                use_round_corner,
                1,
            )
        else:
            if use_pyaedt_extent:
                _poly = self._create_convex_hull(
                    net_signals,
                    expansion_size,
                    1e-12,
                    use_round_corner,
                    expansion_size,
                    smart_cut,
                    reference_list,
                    pins_to_preserve,
                )
            else:
                _poly = self.layout.expanded_extent(
                    net_signals,
                    self.core.Geometry.ExtentType.Conforming,
                    expansion_size,
                    False,
                    use_round_corner,
                    1,
                )
                _poly_list = convert_py_list_to_net_list([_poly])
                _poly = self.core.geometry.polygon_data.get_convex_hull_of_polygons(_poly_list)
        return _poly

    def _create_conformal(
        self,
        net_signals,
        expansion_size,
        tolerance,
        round_corner,
        round_extension,
        smart_cutout=False,
        reference_list=[],
        pins_to_preserve=None,
        inlcude_voids_in_extents=False,
    ):
        names = []
        _polys = []
        for net in net_signals:
            names.append(net.name)
        if pins_to_preserve:
            insts = self.padstacks.instances
            for i in pins_to_preserve:
                p = insts[i].position
                pos_1 = [i - expansion_size for i in p]
                pos_2 = [i + expansion_size for i in p]
                plane = self.modeler.Shape("rectangle", pointA=pos_1, pointB=pos_2)
                rectangle_data = self.modeler.shape_to_polygon_data(plane)
                _polys.append(rectangle_data)

        for prim in self.modeler.primitives:
            if prim is not None and prim.net_name in names:
                _polys.append(prim)
        if smart_cutout:
            objs_data = self._smart_cut(reference_list, expansion_size)
            _polys.extend(objs_data)
        k = 0
        delta = expansion_size / 5
        while k < 10:
            unite_polys = []
            for i in _polys:
                if "PolygonData" not in str(i):
                    obj_data = i.primitive_object.GetPolygonData().Expand(
                        expansion_size, tolerance, round_corner, round_extension
                    )
                else:
                    obj_data = i.Expand(expansion_size, tolerance, round_corner, round_extension)
                if inlcude_voids_in_extents and "PolygonData" not in str(i) and i.has_voids and obj_data:
                    for void in i.voids:
                        void_data = void.primitive_object.GetPolygonData().Expand(
                            -1 * expansion_size, tolerance, round_corner, round_extension
                        )
                        if void_data:
                            for v in list(void_data):
                                obj_data[0].AddHole(v)
                if obj_data:
                    if not inlcude_voids_in_extents:
                        unite_polys.extend(list(obj_data))
                    else:
                        voids_poly = []
                        try:
                            if i.HasVoids():
                                area = i.area()
                                for void in i.Voids:
                                    void_polydata = void.GetPolygonData()
                                    if void_polydata.Area() >= 0.05 * area:
                                        voids_poly.append(void_polydata)
                                if voids_poly:
                                    obj_data = obj_data[0].Subtract(
                                        convert_py_list_to_net_list(list(obj_data)),
                                        convert_py_list_to_net_list(voids_poly),
                                    )
                        except Exception as e:
                            self.logger.error(
                                f"A(n) {type(e).__name__} error occurred in method _create_conformal of "
                                f"class Edb at iteration {k} for data {i}: {str(e)}"
                            )
                        finally:
                            unite_polys.extend(list(obj_data))
            _poly_unite = self.core.Geometry.PolygonData.Unite(convert_py_list_to_net_list(unite_polys))
            if len(_poly_unite) == 1:
                self.logger.info("Correctly computed Extension at first iteration.")
                return _poly_unite[0]
            k += 1
            expansion_size += delta
        if len(_poly_unite) == 1:
            self.logger.info("Correctly computed Extension in {} iterations.".format(k))
            return _poly_unite[0]
        else:
            self.logger.info("Failed to Correctly computed Extension.")
            areas = [i.Area() for i in _poly_unite]
            return _poly_unite[areas.index(max(areas))]

    def _smart_cut(self, reference_list=[], expansion_size=1e-12):
        from pyedb.dotnet.clr_module import Tuple

        _polys = []
        terms = [term for term in self.layout.terminals if int(term._edb_object.GetBoundaryType()) in [0, 3, 4, 7, 8]]
        locations = []
        for term in terms:
            if term._edb_object.GetTerminalType().ToString() == "PointTerminal" and term.net.name in reference_list:
                pd = term._edb_object.GetParameters()[1]
                locations.append([pd.X.ToDouble(), pd.Y.ToDouble()])
        for point in locations:
            pointA = self.core.geometry.point_data(
                self.edb_value(point[0] - expansion_size),
                self.edb_value(point[1] - expansion_size),
            )
            pointB = self.core.geometry.point_data(
                self.edb_value(point[0] + expansion_size),
                self.edb_value(point[1] + expansion_size),
            )

            points = Tuple[
                self.core.geometry.geometry.PointData,
                self.core.geometry.geometry.PointData,
            ](pointA, pointB)
            _polys.append(self.core.geometry.polygon_data.create_from_bbox(points))
        return _polys

    def _create_convex_hull(
        self,
        net_signals,
        expansion_size,
        tolerance,
        round_corner,
        round_extension,
        smart_cut=False,
        reference_list=[],
        pins_to_preserve=None,
    ):
        names = []
        _polys = []
        for net in net_signals:
            names.append(net.name)
        if pins_to_preserve:
            insts = self.padstacks.instances
            for i in pins_to_preserve:
                p = insts[i].position
                pos_1 = [i - 1e-12 for i in p]
                pos_2 = [i + 1e-12 for i in p]
                plane = self.modeler.Shape("rectangle", pointA=pos_1, pointB=pos_2)
                rectangle_data = self.modeler.shape_to_polygon_data(plane)
                _polys.append(rectangle_data)
        for prim in self.modeler.primitives:
            if prim is not None and prim.net_name in names:
                _polys.append(prim.primitive_object.GetPolygonData())
        if smart_cut:
            objs_data = self._smart_cut(reference_list, expansion_size)
            _polys.extend(objs_data)
        _poly = self.core.Geometry.PolygonData.GetConvexHullOfPolygons(convert_py_list_to_net_list(_polys))
        _poly = _poly.Expand(expansion_size, tolerance, round_corner, round_extension)[0]
        return _poly

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

    def _create_cutout_legacy(
        self,
        signal_list=[],
        reference_list=["GND"],
        extent_type="Conforming",
        expansion_size=0.002,
        use_round_corner=False,
        output_aedb_path=None,
        open_cutout_at_end=True,
        use_pyaedt_extent_computing=False,
        remove_single_pin_components=False,
        check_terminals=False,
        include_pingroups=True,
        inlcude_voids_in_extents=False,
    ):
        expansion_size = self.edb_value(expansion_size).ToDouble()

        # validate nets in layout
        net_signals = [net for net in self.layout.nets if net.name in signal_list]

        # validate references in layout
        _netsClip = convert_py_list_to_net_list(
            [net.api_object for net in self.layout.nets if net.name in reference_list]
        )

        _poly = self._create_extent(
            net_signals,
            extent_type,
            expansion_size,
            use_round_corner,
            use_pyaedt_extent_computing,
            smart_cut=check_terminals,
            reference_list=reference_list,
            include_pingroups=include_pingroups,
            inlcude_voids_in_extents=inlcude_voids_in_extents,
        )
        _poly1 = _poly.CreateFromArcs(_poly.GetArcData(), True)
        if inlcude_voids_in_extents:
            for hole in list(_poly.Holes):
                if hole.Area() >= 0.05 * _poly1.Area():
                    _poly1.AddHole(hole)
        _poly = _poly1
        # Create new cutout cell/design
        included_nets_list = signal_list + reference_list
        included_nets = convert_py_list_to_net_list(
            [net.api_object for net in self.layout.nets if net.name in included_nets_list]
        )
        _cutout = self.active_cell.CutOut(included_nets, _netsClip, _poly, True)
        # Analysis setups do not come over with the clipped design copy,
        # so add the analysis setups from the original here.
        id = 1
        for _setup in self.active_cell.SimulationSetups:
            # Empty string '' if coming from setup copy and don't set explicitly.
            _setup_name = _setup.GetName()
            if "GetSimSetupInfo" in dir(_setup):
                # setup is an Ansys.Ansoft.Edb.Utility.HFSSSimulationSetup object
                _hfssSimSetupInfo = _setup.GetSimSetupInfo()
                _hfssSimSetupInfo.Name = "HFSS Setup " + str(id)  # Set name of analysis setup
                # Write the simulation setup info into the cell/design setup
                _setup.SetSimSetupInfo(_hfssSimSetupInfo)
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design
                id += 1
            else:
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design

        _dbCells = [_cutout]

        if output_aedb_path:
            db2 = self.core.Database.Create(output_aedb_path)
            _success = db2.Save()
            _dbCells = convert_py_list_to_net_list(_dbCells)
            db2.CopyCells(_dbCells)  # Copies cutout cell/design to db2 project
            if len(list(db2.CircuitCells)) > 0:
                for net in list(list(db2.CircuitCells)[0].GetLayout().Nets):
                    if not net.GetName() in included_nets_list:
                        net.Delete()
                _success = db2.Save()
            for c in list(self._db.TopCircuitCells):
                if c.GetName() == _cutout.GetName():
                    c.Delete()
            if open_cutout_at_end:  # pragma: no cover
                self._db = db2
                self.edbpath = output_aedb_path
                self._active_cell = list(self.top_circuit_cells)[0]
                self.edbpath = self.directory
                self._init_objects()
                if remove_single_pin_components:
                    self.components.delete_single_pin_rlc()
                    self.logger.info_timer("Single Pins components deleted")
                    self.components.refresh_components()
            else:
                if remove_single_pin_components:
                    try:
                        layout = list(db2.CircuitCells)[0].GetLayout()
                        _cmps = [
                            l
                            for l in layout.Groups
                            if l.ToString() == "Ansys.Ansoft.Edb.Cell.Hierarchy.Component" and l.GetNumberOfPins() < 2
                        ]
                        for _cmp in _cmps:
                            _cmp.Delete()
                    except:
                        self.logger.error("Failed to remove single pin components.")
                db2.Close()
                source = os.path.join(output_aedb_path, "edb.def.tmp")
                target = os.path.join(output_aedb_path, "edb.def")
                self._wait_for_file_release(file_to_release=output_aedb_path)
                if os.path.exists(source) and not os.path.exists(target):
                    try:
                        shutil.copy(source, target)
                    except Exception as e:
                        self.logger.error(f"Failed to copy {source} to {target} - {type(e).__name__}: {str(e)}")
        elif open_cutout_at_end:
            self._active_cell = _cutout
            self._init_objects()
            if remove_single_pin_components:
                self.components.delete_single_pin_rlc()
                self.logger.info_timer("Single Pins components deleted")
                self.components.refresh_components()
        return [[pt.X.ToDouble(), pt.Y.ToDouble()] for pt in list(_poly.GetPolygonWithoutArcs().Points)]

    def create_cutout(
        self,
        signal_list=[],
        reference_list=["GND"],
        extent_type="Conforming",
        expansion_size=0.002,
        use_round_corner=False,
        output_aedb_path=None,
        open_cutout_at_end=True,
        use_pyaedt_extent_computing=False,
    ):
        """Create a cutout using an approach entirely based on legacy.
        It does in sequence:
        - delete all nets not in list,
        - create an extent of the nets,
        - check and delete all vias not in the extent,
        - check and delete all the primitives not in extent,
        - check and intersect all the primitives that intersect the extent.

        .. deprecated:: 0.6.58
           Use new method :func:`cutout` instead.

        Parameters
        ----------
        signal_list : list
            List of signal strings.
        reference_list : list, optional
            List of references to add. The default is ``["GND"]``.
        extent_type : str, optional
            Type of the extension. Options are ``"Conforming"``, ``"ConvexHull"``, and
            ``"Bounding"``. The default is ``"Conforming"``.
        expansion_size : float, str, optional
            Expansion size ratio in meters. The default is ``0.002``.
        use_round_corner : bool, optional
            Whether to use round corners. The default is ``False``.
        output_aedb_path : str, optional
            Full path and name for the new AEDB file.
        open_cutout_at_end : bool, optional
            Whether to open the cutout at the end. The default
            is ``True``.
        use_pyaedt_extent_computing : bool, optional
            Whether to use legacy extent computing (experimental).

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn("Use new method `cutout` instead.", DeprecationWarning)
        return self._create_cutout_legacy(
            signal_list=signal_list,
            reference_list=reference_list,
            extent_type=extent_type,
            expansion_size=expansion_size,
            use_round_corner=use_round_corner,
            output_aedb_path=output_aedb_path,
            open_cutout_at_end=open_cutout_at_end,
            use_pyaedt_extent_computing=use_pyaedt_extent_computing,
        )

    def _create_cutout_multithread(
        self,
        signal_list=[],
        reference_list=["GND"],
        extent_type="Conforming",
        expansion_size=0.002,
        use_round_corner=False,
        number_of_threads=4,
        custom_extent=None,
        output_aedb_path=None,
        remove_single_pin_components=False,
        use_pyaedt_extent_computing=False,
        extent_defeature=0.0,
        custom_extent_units="mm",
        check_terminals=False,
        include_pingroups=True,
        preserve_components_with_model=False,
        include_partial=False,
        simple_pad_check=True,
        keep_lines_as_path=False,
        inlcude_voids_in_extents=False,
    ):
        from concurrent.futures import ThreadPoolExecutor

        if output_aedb_path:
            self.save_as(output_aedb_path)
        self.logger.info("Cutout Multithread started.")
        expansion_size = self.edb_value(expansion_size).ToDouble()

        timer_start = self.logger.reset_timer()
        if custom_extent:
            if not reference_list and not signal_list:
                reference_list = self.nets.netlist[::]
                all_list = reference_list
            else:
                reference_list = reference_list + signal_list
                all_list = reference_list
        else:
            all_list = signal_list + reference_list
        pins_to_preserve = []
        nets_to_preserve = []
        if preserve_components_with_model:
            for el in self.layout.groups:
                if el.model_type in [
                    "SPICEModel",
                    "SParameterModel",
                    "NetlistModel",
                ] and list(set(el.nets[:]) & set(signal_list[:])):
                    pins_to_preserve.extend([i.id for i in el.pins.values()])
                    nets_to_preserve.extend(el.nets)
        if include_pingroups:
            for pingroup in self.padstacks.pingroups:
                for pin in pingroup.pins.values():
                    if pin.net_name in reference_list:
                        pins_to_preserve.append(pin.id)
        if check_terminals:
            terms = [
                term for term in self.layout.terminals if int(term._edb_object.GetBoundaryType()) in [0, 3, 4, 7, 8]
            ]
            for term in terms:
                if term._edb_object.GetTerminalType().ToString() == "PadstackInstanceTerminal":
                    if term._edb_object.GetParameters()[1].GetNet().GetName() in reference_list:
                        pins_to_preserve.append(term._edb_object.GetParameters()[1].GetId())

        for i in self.nets.nets.values():
            name = i.name
            if name not in all_list and name not in nets_to_preserve:
                i.net_object.Delete()
        reference_pinsts = []
        reference_prims = []
        reference_paths = []
        pins_to_delete = []

        def check_instances(item):
            net_name = item.net_name
            id = item.id
            if net_name not in all_list and id not in pins_to_preserve:
                pins_to_delete.append(item)
            elif net_name in reference_list and id not in pins_to_preserve:
                reference_pinsts.append(item)

        with ThreadPoolExecutor(number_of_threads) as pool:
            pool.map(lambda item: check_instances(item), self.layout.padstack_instances)

        for i in pins_to_delete:
            i.delete()

        prim_to_delete = []

        def check_prims(item):
            if item:
                net_name = item.net_name
                if net_name not in all_list:
                    prim_to_delete.append(item)
                elif net_name in reference_list and not item.is_void:
                    if keep_lines_as_path and item.type == "Path":
                        reference_paths.append(item)
                    else:
                        reference_prims.append(item)

        with ThreadPoolExecutor(number_of_threads) as pool:
            pool.map(lambda item: check_prims(item), self.modeler.primitives)

        for i in prim_to_delete:
            i.delete()

        self.logger.info_timer("Net clean up")
        self.logger.reset_timer()

        if custom_extent and isinstance(custom_extent, list):
            if custom_extent[0] != custom_extent[-1]:
                custom_extent.append(custom_extent[0])
            custom_extent = [
                [
                    self.number_with_units(i[0], custom_extent_units),
                    self.number_with_units(i[1], custom_extent_units),
                ]
                for i in custom_extent
            ]
            plane = self.modeler.Shape("polygon", points=custom_extent)
            _poly = self.modeler.shape_to_polygon_data(plane)
        elif custom_extent:
            _poly = custom_extent
        else:
            net_signals = [net for net in self.layout.nets if net.name in signal_list]
            _poly = self._create_extent(
                net_signals,
                extent_type,
                expansion_size,
                use_round_corner,
                use_pyaedt_extent_computing,
                smart_cut=check_terminals,
                reference_list=reference_list,
                include_pingroups=include_pingroups,
                pins_to_preserve=pins_to_preserve,
                inlcude_voids_in_extents=inlcude_voids_in_extents,
            )
            if extent_type in ["Conforming", self.core.Geometry.ExtentType.Conforming, 1]:
                if extent_defeature > 0:
                    _poly = _poly.Defeature(extent_defeature)
                _poly1 = _poly.CreateFromArcs(_poly.GetArcData(), True)
                if inlcude_voids_in_extents:
                    for hole in list(_poly.Holes):
                        if hole.Area() >= 0.05 * _poly1.Area():
                            _poly1.AddHole(hole)
                    self.logger.info(f"Number of voids included:{len(list(_poly1.Holes))}")
                _poly = _poly1
        if not _poly or _poly.IsNull():
            self.logger.error("Failed to create Extent.")
            return []
        self.logger.info_timer("Extent Creation")
        self.logger.reset_timer()
        _poly_list = convert_py_list_to_net_list([_poly])
        prims_to_delete = []
        poly_to_create = []
        pins_to_delete = []

        def intersect(poly1, poly2):
            if not isinstance(poly2, list):
                poly2 = [poly2]
            return list(
                poly1.Intersect(
                    convert_py_list_to_net_list(poly1),
                    convert_py_list_to_net_list(poly2),
                )
            )

        def subtract(poly, voids):
            return poly.Subtract(convert_py_list_to_net_list(poly), convert_py_list_to_net_list(voids))

        def clip_path(path):
            pdata = path.polygon_data._edb_object
            int_data = _poly.GetIntersectionType(pdata)
            if int_data == 0:
                prims_to_delete.append(path)
                return
            result = path._edb_object.SetClipInfo(_poly, True)
            if not result:
                self.logger.info("Failed to clip path {}. Clipping as polygon.".format(path.id))
                reference_prims.append(path)

        def clean_prim(prim_1):  # pragma: no cover
            pdata = prim_1.polygon_data._edb_object
            int_data = _poly.GetIntersectionType(pdata)
            if int_data == 2:
                if not inlcude_voids_in_extents:
                    return
                skip = False
                for hole in list(_poly.Holes):
                    if hole.GetIntersectionType(pdata) == 0:
                        prims_to_delete.append(prim_1)
                        return
                    elif hole.GetIntersectionType(pdata) == 1:
                        skip = True
                if skip:
                    return
            elif int_data == 0:
                prims_to_delete.append(prim_1)
                return
            list_poly = intersect(_poly, pdata)
            if list_poly:
                net = prim_1.net_name
                voids = prim_1.voids
                for p in list_poly:
                    if p.IsNull():
                        continue
                    # points = list(p.Points)
                    list_void = []
                    if voids:
                        voids_data = [void.polygon_data._edb_object for void in voids]
                        list_prims = subtract(p, voids_data)
                        for prim in list_prims:
                            if not prim.IsNull():
                                poly_to_create.append([prim, prim_1.layer.name, net, list_void])
                    else:
                        poly_to_create.append([p, prim_1.layer.name, net, list_void])

            prims_to_delete.append(prim_1)

        def pins_clean(pinst):
            if not pinst.in_polygon(_poly, include_partial=include_partial, simple_check=simple_pad_check):
                pins_to_delete.append(pinst)

        if not simple_pad_check:
            pad_cores = 1
        else:
            pad_cores = number_of_threads
        with ThreadPoolExecutor(pad_cores) as pool:
            pool.map(lambda item: pins_clean(item), reference_pinsts)

        for pin in pins_to_delete:
            pin.delete()

        self.logger.info_timer("{} Padstack Instances deleted.".format(len(pins_to_delete)))
        self.logger.reset_timer()

        with ThreadPoolExecutor(number_of_threads) as pool:
            pool.map(lambda item: clip_path(item), reference_paths)
        with ThreadPoolExecutor(number_of_threads) as pool:
            pool.map(lambda item: clean_prim(item), reference_prims)
        # for item in reference_paths:
        #     clip_path(item)
        # for prim in reference_prims:  # removing multithreading as failing with new layer from primitive
        #     clean_prim(prim)

        for el in poly_to_create:
            self.modeler.create_polygon(el[0], el[1], net_name=el[2], voids=el[3])

        for prim in prims_to_delete:
            prim.delete()

        self.logger.info_timer("{} Primitives deleted.".format(len(prims_to_delete)))
        self.logger.reset_timer()

        i = 0
        for _, val in self.components.instances.items():
            if val.numpins == 0:
                val.edbcomponent.Delete()
                i += 1
                i += 1
        self.logger.info("{} components deleted".format(i))
        if remove_single_pin_components:
            self.components.delete_single_pin_rlc()
            self.logger.info_timer("Single Pins components deleted")

        self.components.refresh_components()
        if output_aedb_path:
            self.save_edb()
        self.logger.info_timer("Cutout completed.", timer_start)
        self.logger.reset_timer()
        return [[pt.X.ToDouble(), pt.Y.ToDouble()] for pt in list(_poly.GetPolygonWithoutArcs().Points)]

    def create_cutout_multithread(
        self,
        signal_list=[],
        reference_list=["GND"],
        extent_type="Conforming",
        expansion_size=0.002,
        use_round_corner=False,
        number_of_threads=4,
        custom_extent=None,
        output_aedb_path=None,
        remove_single_pin_components=False,
        use_pyaedt_extent_computing=False,
        extent_defeature=0,
        keep_lines_as_path=False,
        return_extent=False,
    ):
        """Create a cutout using an approach entirely based on legacy.
        It does in sequence:
        - delete all nets not in list,
        - create a extent of the nets,
        - check and delete all vias not in the extent,
        - check and delete all the primitives not in extent,
        - check and intersect all the primitives that intersect the extent.


        .. deprecated:: 0.6.58
           Use new method :func:`cutout` instead.

        Parameters
        ----------
        signal_list : list
            List of signal strings.
        reference_list : list, optional
            List of references to add. The default is ``["GND"]``.
        extent_type : str, optional
            Type of the extension. Options are ``"Conforming"``, ``"ConvexHull"``, and
            ``"Bounding"``. The default is ``"Conforming"``.
        expansion_size : float, str, optional
            Expansion size ratio in meters. The default is ``0.002``.
        use_round_corner : bool, optional
            Whether to use round corners. The default is ``False``.
        number_of_threads : int, optional
            Number of thread to use. Default is 4
        custom_extent : list, optional
            Custom extent to use for the cutout. It has to be a list of points [[x1,y1],[x2,y2]....] or
            Edb PolygonData object. In this case, both signal_list and reference_list will be cut.
        output_aedb_path : str, optional
            Full path and name for the new AEDB file. If None, then current aedb will be cutout.
        remove_single_pin_components : bool, optional
            Remove all Single Pin RLC after the cutout is completed. Default is `False`.
        use_pyaedt_extent_computing : bool, optional
            Whether to use legacy extent computing (experimental).
        extent_defeature : float, optional
            Defeature the cutout before applying it to produce simpler geometry for mesh (Experimental).
            It applies only to Conforming bounding box. Default value is ``0`` which disable it.
        keep_lines_as_path : bool, optional
            Whether to keep the lines as Path after they are cutout or convert them to PolygonData.
            This feature works only in Electronics Desktop (3D Layout).
            If the flag is set to True it can cause issues in SiWave once the Edb is imported.
            Default is ``False`` to generate PolygonData of cut lines.
        return_extent : bool, optional
            When ``True`` extent used for clipping is returned, if ``False`` only the boolean indicating whether
            clipping succeed or not is returned. Not applicable with custom extent usage.
            Default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb(r"C:\\test.aedb", version="2022.2")
        >>> edb.logger.info_timer("Edb Opening")
        >>> edb.logger.reset_timer()
        >>> start = time.time()
        >>> signal_list = []
        >>> for net in edb.nets.nets.keys():
        >>>      if "3V3" in net:
        >>>           signal_list.append(net)
        >>> power_list = ["PGND"]
        >>> edb.create_cutout_multithread(signal_list=signal_list, reference_list=power_list, extent_type="Conforming")
        >>> end_time = str((time.time() - start) / 60)
        >>> edb.logger.info("Total legacy cutout time in min %s", end_time)
        >>> edb.nets.plot(signal_list, None, color_by_net=True)
        >>> edb.nets.plot(power_list, None, color_by_net=True)
        >>> edb.save_edb()
        >>> edb.close_edb()

        """
        warnings.warn("Use new method `cutout` instead.", DeprecationWarning)
        return self._create_cutout_multithread(
            signal_list=signal_list,
            reference_list=reference_list,
            extent_type=extent_type,
            expansion_size=expansion_size,
            use_round_corner=use_round_corner,
            number_of_threads=number_of_threads,
            custom_extent=custom_extent,
            output_aedb_path=output_aedb_path,
            remove_single_pin_components=remove_single_pin_components,
            use_pyaedt_extent_computing=use_pyaedt_extent_computing,
            extent_defeature=extent_defeature,
            keep_lines_as_path=keep_lines_as_path,
            return_extent=return_extent,
        )

    def get_conformal_polygon_from_netlist(self, netlist=None):
        """Return an EDB conformal polygon based on a netlist.

        Parameters
        ----------

        netlist : List of net names.
            list[str]

        Returns
        -------
        :class:`Edb.Cell.Primitive.Polygon`
            Edb polygon object.

        """
        temp_edb_path = self.edbpath[:-5] + "_temp_aedb.aedb"
        shutil.copytree(self.edbpath, temp_edb_path)
        temp_edb = Edb(temp_edb_path)
        for via in list(temp_edb.padstacks.instances.values()):
            via.pin.Delete()
        if netlist:
            nets = [net.net_obj for net in temp_edb.layout.nets if net.name in netlist]
            _poly = temp_edb.layout.expanded_extent(nets, self.core.Geometry.ExtentType.Conforming, 0.0, True, True, 1)
        else:
            nets = [net.api_object for net in temp_edb.layout.nets if "gnd" in net.name.lower()]
            _poly = temp_edb.layout.expanded_extent(nets, self.core.Geometry.ExtentType.Conforming, 0.0, True, True, 1)
            temp_edb.close_edb()
        if _poly:
            return _poly
        else:
            return False

    def number_with_units(self, value, units=None):
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

    def _decompose_variable_value(self, value, unit_system=None):
        val, units = decompose_variable_value(value)
        if units and unit_system and units in AEDT_UNITS[unit_system]:
            return AEDT_UNITS[unit_system][units] * val
        else:
            return val

    def _create_cutout_on_point_list(
        self,
        point_list,
        units="mm",
        output_aedb_path=None,
        open_cutout_at_end=True,
        nets_to_include=None,
        include_partial_instances=False,
        keep_voids=True,
    ):
        if point_list[0] != point_list[-1]:
            point_list.append(point_list[0])
        point_list = [[self.number_with_units(i[0], units), self.number_with_units(i[1], units)] for i in point_list]
        plane = self.modeler.Shape("polygon", points=point_list)
        polygonData = self.modeler.shape_to_polygon_data(plane)
        _ref_nets = []
        if nets_to_include:
            self.logger.info("Creating cutout on {} nets.".format(len(nets_to_include)))
        else:
            self.logger.info("Creating cutout on all nets.")  # pragma: no cover

        # Check Padstack Instances overlapping the cutout
        pinstance_to_add = []
        if include_partial_instances:
            if nets_to_include:
                pinst = [i for i in list(self.padstacks.instances.values()) if i.net_name in nets_to_include]
            else:
                pinst = [i for i in list(self.padstacks.instances.values())]
            for p in pinst:
                if p.in_polygon(polygonData):
                    pinstance_to_add.append(p)
        # validate references in layout
        for _ref in self.nets.nets:
            if nets_to_include:
                if _ref in nets_to_include:
                    _ref_nets.append(self.nets.nets[_ref].net_object)
            else:
                _ref_nets.append(self.nets.nets[_ref].net_object)  # pragma: no cover
        if keep_voids:
            voids = [p for p in self.modeler.circles if p.is_void]
            voids2 = [p for p in self.modeler.polygons if p.is_void]
            voids.extend(voids2)
        else:
            voids = []
        voids_to_add = []
        for circle in voids:
            if polygonData.GetIntersectionType(circle.primitive_object.GetPolygonData()) >= 3:
                voids_to_add.append(circle)

        _netsClip = convert_py_list_to_net_list(_ref_nets)
        # net_signals = convert_py_list_to_net_list([], type(_ref_nets[0]))

        # Create new cutout cell/design
        _cutout = self.active_cell.CutOut(_netsClip, _netsClip, polygonData)
        layout = _cutout.GetLayout()
        cutout_obj_coll = list(layout.PadstackInstances)
        ids = []
        for lobj in cutout_obj_coll:
            ids.append(lobj.GetId())

        if include_partial_instances:
            p_missing = [i for i in pinstance_to_add if i.id not in ids]
            self.logger.info("Added {} padstack instances after cutout".format(len(p_missing)))
            for p in p_missing:
                position = self.core.geometry.point_data(self.edb_value(p.position[0]), self.edb_value(p.position[1]))
                net = self.nets.find_or_create_net(p.net_name)
                rotation = self.edb_value(p.rotation)
                sign_layers = list(self.stackup.signal_layers.keys())
                if not p.start_layer:  # pragma: no cover
                    fromlayer = self.stackup.signal_layers[sign_layers[0]]._edb_layer
                else:
                    fromlayer = self.stackup.signal_layers[p.start_layer]._edb_layer

                if not p.stop_layer:  # pragma: no cover
                    tolayer = self.stackup.signal_layers[sign_layers[-1]]._edb_layer
                else:
                    tolayer = self.stackup.signal_layers[p.stop_layer]._edb_layer
                padstack = None
                for pad in list(self.padstacks.definitions.keys()):
                    if pad == p.padstack_definition:
                        padstack = self.padstacks.definitions[pad].edb_padstack
                        padstack_instance = self.core.Cell.primitive.padstack_instance.create(
                            _cutout.GetLayout(),
                            net,
                            p.name,
                            padstack,
                            position,
                            rotation,
                            fromlayer,
                            tolayer,
                            None,
                            None,
                        )
                        padstack_instance.SetIsLayoutPin(p.is_pin)
                        break

        for void_circle in voids_to_add:
            if void_circle.type == "Circle":
                (
                    res,
                    center_x,
                    center_y,
                    radius,
                ) = void_circle.primitive_object.GetParameters(0.0, 0.0, 0.0)
                cloned_circle = self.core.Cell.primitive.circle.create(
                    layout,
                    void_circle.layer_name,
                    void_circle.net,
                    self.edb_value(center_x),
                    self.edb_value(center_y),
                    self.edb_value(radius),
                )
                cloned_circle.SetIsNegative(True)
            elif void_circle.type == "Polygon":
                cloned_polygon = self.core.Cell.primitive.polygon.create(
                    layout,
                    void_circle.layer_name,
                    void_circle.net,
                    void_circle.primitive_object.GetPolygonData(),
                )
                cloned_polygon.SetIsNegative(True)
        layers = [i for i in list(self.stackup.signal_layers.keys())]
        for layer in layers:
            layer_primitves = self.modeler.get_primitives(layer_name=layer)
            if len(layer_primitves) == 0:
                self.modeler.create_polygon(plane, layer, net_name="DUMMY")
        self.logger.info("Cutout %s created correctly", _cutout.GetName())
        id = 1
        for _setup in self.active_cell.SimulationSetups:
            # Empty string '' if coming from setup copy and don't set explicitly.
            _setup_name = _setup.GetName()
            if "GetSimSetupInfo" in dir(_setup):
                # setup is an Ansys.Ansoft.Edb.Utility.HFSSSimulationSetup object
                _hfssSimSetupInfo = _setup.GetSimSetupInfo()
                _hfssSimSetupInfo.Name = "HFSS Setup " + str(id)  # Set name of analysis setup
                # Write the simulation setup info into the cell/design setup
                _setup.SetSimSetupInfo(_hfssSimSetupInfo)
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design
                id += 1
            else:
                _cutout.AddSimulationSetup(_setup)  # Add simulation setup to the cutout design

        _dbCells = [_cutout]
        if output_aedb_path:
            db2 = self.core.Database.Create(output_aedb_path)
            if not db2.Save():
                self.logger.error("Failed to create new Edb. Check if the path already exists and remove it.")
                return []
            _dbCells = convert_py_list_to_net_list(_dbCells)
            cell_copied = db2.CopyCells(_dbCells)  # Copies cutout cell/design to db2 project
            cell = list(cell_copied)[0]
            cell.SetName(os.path.basename(output_aedb_path[:-5]))
            db2.Save()
            for c in list(self._db.TopCircuitCells):
                if c.GetName() == _cutout.GetName():
                    c.Delete()
            if open_cutout_at_end:  # pragma: no cover
                _success = db2.Save()
                self._db = db2
                self.edbpath = output_aedb_path
                self._active_cell = cell
                self.edbpath = self.directory
                self._init_objects()
            else:
                db2.Close()
                source = os.path.join(output_aedb_path, "edb.def.tmp")
                target = os.path.join(output_aedb_path, "edb.def")
                self._wait_for_file_release(file_to_release=output_aedb_path)
                if os.path.exists(source) and not os.path.exists(target):
                    try:
                        shutil.copy(source, target)
                        self.logger.warning("aedb def file manually created.")
                    except Exception as e:
                        self.logger.error(f"Failed to copy {source} to {target} - {type(e).__name__}: {str(e)}")
        return [[pt.X.ToDouble(), pt.Y.ToDouble()] for pt in list(polygonData.GetPolygonWithoutArcs().Points)]

    def create_cutout_on_point_list(
        self,
        point_list,
        units="mm",
        output_aedb_path=None,
        open_cutout_at_end=True,
        nets_to_include=None,
        include_partial_instances=False,
        keep_voids=True,
    ):
        """Create a cutout on a specified shape and save it to a new AEDB file.

        .. deprecated:: 0.6.58
           Use new method :func:`cutout` instead.

        Parameters
        ----------
        point_list : list
            Points list defining the cutout shape.
        units : str
            Units of the point list. The default is ``"mm"``.
        output_aedb_path : str, optional
            Full path and name for the new AEDB file.
            The aedb folder shall not exist otherwise the method will return ``False``.
        open_cutout_at_end : bool, optional
            Whether to open the cutout at the end. The default is ``True``.
        nets_to_include : list, optional
            List of nets to include in the cutout. The default is ``None``, in
            which case all nets are included.
        include_partial_instances : bool, optional
            Whether to include padstack instances that have bounding boxes intersecting with point list polygons.
            This operation may slow down the cutout export.
        keep_voids : bool
            Boolean used for keep or not the voids intersecting the polygon used for clipping the layout.
            Default value is ``True``, ``False`` will remove the voids.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        warnings.warn("Use new method `cutout` instead.", DeprecationWarning)
        return self._create_cutout_on_point_list(
            point_list=point_list,
            units=units,
            output_aedb_path=output_aedb_path,
            open_cutout_at_end=open_cutout_at_end,
            nets_to_include=nets_to_include,
            include_partial_instances=include_partial_instances,
            keep_voids=keep_voids,
        )

    def write_export3d_option_config_file(self, path_to_output, config_dictionaries=None):
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
        """Export EDB to HFSS.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets to export if only certain ones are to be exported.
            The default is ``None``, in which case all nets are eported.
        num_cores : int, optional
            Number of cores to use for the export. The default is ``None``.
        aedt_file_name : str, optional
            Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
            in which case the default name is used.
        hidden : bool, optional
            Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

        Returns
        -------
        str
            Full path to the AEDT file.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edb = Edb(edbpath="C:\\temp\\myproject.aedb", version="2023.2")

        >>> options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        >>> edb.write_export3d_option_config_file(r"C:\\temp", options_config)
        >>> edb.export_hfss(r"C:\\temp")
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
        """Export EDB to Q3D.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets to export only if certain ones are to be exported.
            The default is ``None``, in which case all nets are eported.
        num_cores : int, optional
            Number of cores to use for the export. The default is ``None``.
        aedt_file_name : str, optional
            Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
            in which case the default name is used.
        hidden : bool, optional
            Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

        Returns
        -------
        str
            Full path to the AEDT file.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edb = Edb(edbpath="C:\\temp\\myproject.aedb", version="2021.2")
        >>> options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        >>> edb.write_export3d_option_config_file("C:\\temp", options_config)
        >>> edb.export_q3d("C:\\temp")
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
        """Export EDB to Maxwell 3D.

        Parameters
        ----------
        path_to_output : str
            Full path and name for saving the AEDT file.
        net_list : list, optional
            List of nets to export only if certain ones are to be
            exported. The default is ``None``, in which case all nets are exported.
        num_cores : int, optional
            Number of cores to use for the export. The default is ``None.``
        aedt_file_name : str, optional
            Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
            in which case the default name is used.
        hidden : bool, optional
            Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

        Returns
        -------
        str
            Full path to the AEDT file.

        Examples
        --------

        >>> from pyedb import Edb

        >>> edb = Edb(edbpath="C:\\temp\\myproject.aedb", version="2021.2")

        >>> options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        >>> edb.write_export3d_option_config_file("C:\\temp", options_config)
        >>> edb.export_maxwell("C:\\temp")
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
        """Close EDB and solve it with Siwave.

        Returns
        -------
        str
            Siwave project path.
        """
        process = SiwaveSolve(self)
        self.close()
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
        """Close EDB and solve it with Siwave.

        Parameters
        ----------
        siwave_project : str
            Siwave full project name.
        solution_name : str
            Siwave DC Analysis name.
        output_folder : str, optional
            Ouptu folder where files will be downloaded.
        html_report : bool, optional
            Either if generate or not html report. Default is `True`.
        vias : bool, optional
            Either if generate or not vias report. Default is `True`.
        voltage_probes : bool, optional
            Either if generate or not voltage probe report. Default is `True`.
        current_sources : bool, optional
            Either if generate or not current source report. Default is `True`.
        voltage_sources : bool, optional
            Either if generate or not voltage source report. Default is `True`.
        power_tree : bool, optional
            Either if generate or not power tree image. Default is `True`.
        loop_res : bool, optional
            Either if generate or not loop resistance report. Default is `True`.

        Returns
        -------
        list
            List of files generated.
        """
        process = SiwaveSolve(self)
        self.close()
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
        """Check if a variable exists or not.

        Returns
        -------
        tuple of bool and VariableServer
            It returns a booleand to check if the variable exists and the variable
            server that should contain the variable.
        """
        if "$" in variable_name:
            if variable_name.index("$") == 0:
                var_server = self._db.GetVariableServer()

            else:
                var_server = self.active_cell.GetVariableServer()

        else:
            var_server = self.active_cell.GetVariableServer()

        variables = var_server.GetAllVariableNames()
        if variable_name in list(variables):
            return True, var_server
        return False, var_server

    def get_all_variable_names(self):
        """Method added for compatibility with grpc.

        Returns
        -------
        List[Str]
            List of variables name.

        """
        return list(self.variable_exists("")[1].GetAllVariableNames())

    def get_variable(self, variable_name):
        """Return Variable Value if variable exists.

        Parameters
        ----------
        variable_name

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.edbvalue.EdbValue`
        """

        for i, j in self.project_variables.items():
            if i == variable_name:
                return j
        for i, j in self.design_variables.items():
            if i == variable_name:
                return j
        self.logger.info("Variable %s doesn't exists.", variable_name)
        return None

    def add_project_variable(self, variable_name, variable_value, description=""):
        """Add a variable to edb database (project). The variable will have the prefix `$`.

        ..note::
            User can use also the setitem to create or assign a variable. See example below.

        Parameters
        ----------
        variable_name : str
            Name of the variable. Name can be provided without ``$`` prefix.
        variable_value : str, float
            Value of the variable with units.
        description : str, optional
            Description of the variable.

        Returns
        -------
        tuple
            Tuple containing the ``AddVariable`` result and variable server.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edb_app = Edb()
        >>> boolean_1, ant_length = edb_app.add_project_variable("my_local_variable", "1cm")
        >>> print(edb_app["$my_local_variable"])  # using getitem
        >>> edb_app["$my_local_variable"] = "1cm"  # using setitem

        """
        if not variable_name.startswith("$"):
            variable_name = "${}".format(variable_name)
        return self.add_design_variable(
            variable_name=variable_name, variable_value=variable_value, description=description
        )

    def add_design_variable(self, variable_name, variable_value, is_parameter=False, description=""):
        """Add a variable to edb. The variable can be a design one or a project variable (using ``$`` prefix).

        ..note::
            User can use also the setitem to create or assign a variable. See example below.

        Parameters
        ----------
        variable_name : str
            Name of the variable. To added the variable as a project variable, the name
            must begin with ``$``.
        variable_value : str, float
            Value of the variable with units.
        is_parameter : bool, optional
            Whether to add the variable as a local variable. The default is ``False``.
            When ``True``, the variable is added as a parameter default.
        description : str, optional
            Description of the variable.
        Returns
        -------
        tuple
            Tuple containing the ``AddVariable`` result and variable server.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edb_app = Edb()
        >>> boolean_1, ant_length = edb_app.add_design_variable("my_local_variable", "1cm")
        >>> print(edb_app["my_local_variable"])  # using getitem
        >>> edb_app["my_local_variable"] = "1cm"  # using setitem
        >>> boolean_2, para_length = edb_app.change_design_variable_value("my_parameter", "1m", is_parameter=True
        >>> boolean_3, project_length = edb_app.change_design_variable_value("$my_project_variable", "1m")


        """
        var_server = self.variable_exists(variable_name)
        if not var_server[0]:
            var_server[1].AddVariable(variable_name, self.edb_value(variable_value), is_parameter)
            if description:
                var_server[1].SetVariableDescription(variable_name, description)
            return True, var_server[1]
        self.logger.error("Variable %s already exists.", variable_name)
        return False, var_server[1]

    def change_design_variable_value(self, variable_name, variable_value):
        """Change a variable value.

        ..note::
            User can use also the getitem to read the variable value. See example below.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        variable_value : str, float
            Value of the variable with units.

        Returns
        -------
        tuple
            Tuple containing the ``SetVariableValue`` result and variable server.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edb_app = Edb()
        >>> boolean, ant_length = edb_app.add_design_variable("ant_length", "1cm")
        >>> boolean, ant_length = edb_app.change_design_variable_value("ant_length", "1m")
        >>> print(edb_app["ant_length"])  # using getitem
        """
        var_server = self.variable_exists(variable_name)
        if var_server[0]:
            var_server[1].SetVariableValue(variable_name, self.edb_value(variable_value))
            return True, var_server[1]
        self.logger.error("Variable %s does not exists.", variable_name)
        return False, var_server[1]

    def get_bounding_box(self):
        """Get the layout bounding box.

        Returns
        -------
        list of list of double
            Bounding box as a [lower-left X, lower-left Y], [upper-right X, upper-right Y]) pair in meters.
        """
        bbox = self.edbutils.HfssUtilities.GetBBox(self.active_layout)
        return [
            [bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble()],
            [bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()],
        ]

    def build_simulation_project(self, simulation_setup):
        # type: (SimulationConfiguration) -> bool
        """Build a ready-to-solve simulation project.

        Parameters
        ----------
        simulation_setup : :class:`pyedb.dotnet.database.edb_data.simulation_configuration.SimulationConfiguration`.
            SimulationConfiguration object that can be instantiated or directly loaded with a
            configuration file.

        Returns
        -------
        bool
            ``True`` when successful, False when ``Failed``.

        Examples
        --------

        >>> from pyedb import Edb
        >>> from pyedb.dotnet.database.edb_data.simulation_configuration import SimulationConfiguration
        >>> config_file = path_configuration_file
        >>> source_file = path_to_edb_folder
        >>> edb = Edb(source_file)
        >>> sim_setup = SimulationConfiguration(config_file)
        >>> edb.build_simulation_project(sim_setup)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """
        self.logger.info("Building simulation project.")
        legacy_name = self.edbpath
        if simulation_setup.output_aedb:
            self.save_edb_as(simulation_setup.output_aedb)
        if simulation_setup.signal_layer_etching_instances:
            for layer in simulation_setup.signal_layer_etching_instances:
                if layer in self.stackup.layers:
                    idx = simulation_setup.signal_layer_etching_instances.index(layer)
                    if len(simulation_setup.etching_factor_instances) > idx:
                        self.stackup[layer].etch_factor = float(simulation_setup.etching_factor_instances[idx])

        if not simulation_setup.signal_nets and simulation_setup.components:
            nets_to_include = []
            pnets = list(self.nets.power.keys())[:]
            for el in simulation_setup.components:
                nets_to_include.append([i for i in self.components[el].nets if i not in pnets])
            simulation_setup.signal_nets = [
                i
                for i in list(set.intersection(*map(set, nets_to_include)))
                if i not in simulation_setup.power_nets and i != ""
            ]
        self.nets.classify_nets(simulation_setup.power_nets, simulation_setup.signal_nets)
        if not simulation_setup.power_nets or not simulation_setup.signal_nets:
            self.logger.info("Disabling cutout as no signals or power nets have been defined.")
            simulation_setup.do_cutout_subdesign = False
        if simulation_setup.do_cutout_subdesign:
            self.logger.info("Cutting out using method: {0}".format(simulation_setup.cutout_subdesign_type))
            if simulation_setup.use_default_cutout:
                old_cell_name = self.active_cell.GetName()
                if self.cutout(
                    signal_list=simulation_setup.signal_nets,
                    reference_list=simulation_setup.power_nets,
                    expansion_size=simulation_setup.cutout_subdesign_expansion,
                    use_round_corner=simulation_setup.cutout_subdesign_round_corner,
                    extent_type=simulation_setup.cutout_subdesign_type,
                    use_pyaedt_cutout=False,
                    use_pyaedt_extent_computing=False,
                ):
                    self.logger.info("Cutout processed.")
                    old_cell = self.active_cell.FindByName(
                        self._db,
                        self.core.Cell.CellType.CircuitCell,
                        old_cell_name,
                    )
                    if old_cell:
                        old_cell.Delete()
                else:  # pragma: no cover
                    self.logger.error("Cutout failed.")
            else:
                self.logger.info("Cutting out using method: {0}".format(simulation_setup.cutout_subdesign_type))
                self.cutout(
                    signal_list=simulation_setup.signal_nets,
                    reference_list=simulation_setup.power_nets,
                    expansion_size=simulation_setup.cutout_subdesign_expansion,
                    use_round_corner=simulation_setup.cutout_subdesign_round_corner,
                    extent_type=simulation_setup.cutout_subdesign_type,
                    use_pyaedt_cutout=True,
                    use_pyaedt_extent_computing=True,
                    remove_single_pin_components=True,
                )
                self.logger.info("Cutout processed.")
        else:
            if simulation_setup.include_only_selected_nets:
                included_nets = simulation_setup.signal_nets + simulation_setup.power_nets
                nets_to_remove = [net.name for net in list(self.nets.nets.values()) if not net.name in included_nets]
                self.nets.delete(nets_to_remove)
        self.logger.info("Deleting existing ports.")
        map(lambda port: port.Delete(), self.layout.terminals)
        map(lambda pg: pg.Delete(), self.layout.pin_groups)
        if simulation_setup.solver_type == SolverType.Hfss3dLayout:
            if simulation_setup.generate_excitations:
                self.logger.info("Creating HFSS ports for signal nets.")
                source_type = SourceType.CoaxPort
                if not simulation_setup.generate_solder_balls:
                    source_type = SourceType.CircPort
                for cmp in simulation_setup.components:
                    if isinstance(cmp, str):  # keep legacy component
                        self.components.create_port_on_component(
                            cmp,
                            net_list=simulation_setup.signal_nets,
                            do_pingroup=False,
                            reference_net=simulation_setup.power_nets,
                            port_type=source_type,
                        )
                    elif isinstance(cmp, dict):
                        if "refdes" in cmp:
                            if not "solder_balls_height" in cmp:  # pragma no cover
                                cmp["solder_balls_height"] = None
                            if not "solder_balls_size" in cmp:  # pragma no cover
                                cmp["solder_balls_size"] = None
                                cmp["solder_balls_mid_size"] = None
                            if not "solder_balls_mid_size" in cmp:  # pragma no cover
                                cmp["solder_balls_mid_size"] = None
                            self.components.create_port_on_component(
                                cmp["refdes"],
                                net_list=simulation_setup.signal_nets,
                                do_pingroup=False,
                                reference_net=simulation_setup.power_nets,
                                port_type=source_type,
                                solder_balls_height=cmp["solder_balls_height"],
                                solder_balls_size=cmp["solder_balls_size"],
                                solder_balls_mid_size=cmp["solder_balls_mid_size"],
                            )
                if simulation_setup.generate_solder_balls and not self.hfss.set_coax_port_attributes(
                    simulation_setup
                ):  # pragma: no cover
                    self.logger.error("Failed to configure coaxial port attributes.")
                self.logger.info("Number of ports: {}".format(self.hfss.get_ports_number()))
                self.logger.info("Configure HFSS extents.")
                if simulation_setup.generate_solder_balls and simulation_setup.trim_reference_size:  # pragma: no cover
                    self.logger.info(
                        "Trimming the reference plane for coaxial ports: {0}".format(
                            bool(simulation_setup.trim_reference_size)
                        )
                    )
                    self.hfss.trim_component_reference_size(simulation_setup)  # pragma: no cover
            self.hfss.configure_hfss_extents(simulation_setup)
            if not self.hfss.configure_hfss_analysis_setup(simulation_setup):
                self.logger.error("Failed to configure HFSS simulation setup.")
        if simulation_setup.solver_type == SolverType.SiwaveSYZ:
            if simulation_setup.generate_excitations:
                for cmp in simulation_setup.components:
                    if isinstance(cmp, str):  # keep legacy
                        self.components.create_port_on_component(
                            cmp,
                            net_list=simulation_setup.signal_nets,
                            do_pingroup=simulation_setup.do_pingroup,
                            reference_net=simulation_setup.power_nets,
                            port_type=SourceType.CircPort,
                        )
                    elif isinstance(cmp, dict):
                        if "refdes" in cmp:  # pragma no cover
                            self.components.create_port_on_component(
                                cmp["refdes"],
                                net_list=simulation_setup.signal_nets,
                                do_pingroup=simulation_setup.do_pingroup,
                                reference_net=simulation_setup.power_nets,
                                port_type=SourceType.CircPort,
                            )
            self.logger.info("Configuring analysis setup.")
            if not self.siwave.configure_siw_analysis_setup(simulation_setup):  # pragma: no cover
                self.logger.error("Failed to configure Siwave simulation setup.")
        if simulation_setup.solver_type == SolverType.SiwaveDC:
            if simulation_setup.generate_excitations:
                self.components.create_source_on_component(simulation_setup.sources)
            if not self.siwave.configure_siw_analysis_setup(simulation_setup):  # pragma: no cover
                self.logger.error("Failed to configure Siwave simulation setup.")
        self.padstacks.check_and_fix_via_plating()
        self.save_edb()
        if not simulation_setup.open_edb_after_build and simulation_setup.output_aedb:
            self.close_edb()
            self.edbpath = legacy_name
            self.open_edb()
        return True

    def get_statistics(self, compute_area=False):
        """Get the EDBStatistics object.

        Returns
        -------
        EDBStatistics object from the loaded layout.
        """
        return self.modeler.get_layout_statistics(evaluate_area=compute_area, net_list=None)

    def are_port_reference_terminals_connected(self, common_reference=None):
        """Check if all terminal references in design are connected.
        If the reference nets are different, there is no hope for the terminal references to be connected.
        After we have identified a common reference net we need to loop the terminals again to get
        the correct reference terminals that uses that net.

        Parameters
        ----------
        common_reference : str, optional
            Common Reference name. If ``None`` it will be searched in ports terminal.
            If a string is passed then all excitations must have such reference assigned.

        Returns
        -------
        bool
            Either if the ports are connected to reference_name or not.

        Examples
        --------
        >>> from pyedb import Edb
        >>>edb = Edb()
        >>> edb.hfss.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")
        >>> edb.hfss.create_edge_port_horizontal(
        >>> ... prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
        >>> ... )
        >>> edb.hfss.create_wave_port(traces[0].id, trace_paths[0][0], "wave_port")
        >>> edb.cutout(["Net1"])
        >>> assert edb.are_port_reference_terminals_connected()
        """
        all_sources = [i for i in self.excitations.values() if not isinstance(i, (WavePort, GapPort, BundleWavePort))]
        all_sources.extend([i for i in self.sources.values()])
        if not all_sources:
            return True
        self.logger.reset_timer()
        if not common_reference:
            common_reference = list(set([i.reference_net_name for i in all_sources if i.reference_terminal.net_name]))
            if len(common_reference) > 1:
                self.logger.error("More than 1 reference found.")
                return False
            if not common_reference:
                self.logger.error("No Reference found.")
                return False

            common_reference = common_reference[0]
        all_sources = [i for i in all_sources if i.net_name != common_reference]

        setList = [
            set(i.reference_object.get_connected_object_id_set())
            for i in all_sources
            if i.reference_object and i.reference_net_name == common_reference
        ]
        if len(setList) != len(all_sources):
            self.logger.error("No Reference found.")
            return False
        cmps = [
            i
            for i in list(self.components.resistors.values())
            if i.numpins == 2 and common_reference in i.nets and self._decompose_variable_value(i.res_value) <= 1
        ]
        cmps.extend(
            [i for i in list(self.components.inductors.values()) if i.numpins == 2 and common_reference in i.nets]
        )

        for cmp in cmps:
            found = False
            ids = [i.GetId() for i in cmp.pinlist]
            for list_obj in setList:
                if len(set(ids).intersection(list_obj)) == 1:
                    for list_obj2 in setList:
                        if list_obj2 != list_obj and len(set(ids).intersection(list_obj)) == 1:
                            if (ids[0] in list_obj and ids[1] in list_obj2) or (
                                ids[1] in list_obj and ids[0] in list_obj2
                            ):
                                setList[setList.index(list_obj)] = list_obj.union(list_obj2)
                                setList[setList.index(list_obj2)] = list_obj.union(list_obj2)
                                found = True
                                break
                    if found:
                        break

        # Get the set intersections for all the ID sets.
        iDintersection = set.intersection(*setList)
        self.logger.info_timer(
            "Terminal reference primitive IDs total intersections = {}\n\n".format(len(iDintersection))
        )

        # If the intersections are non-zero, the terminal references are connected.
        return True if len(iDintersection) > 0 else False

    def new_simulation_configuration(self, filename=None):
        # type: (str) -> SimulationConfiguration
        """New SimulationConfiguration Object.

        Parameters
        ----------
        filename : str, optional
            Input config file.

        Returns
        -------
        :class:`legacy.database.edb_data.simulation_configuration.SimulationConfiguration`
        """
        return SimulationConfiguration(filename, self)

    @property
    def setups(self):
        """Get the dictionary of all EDB HFSS and SIwave setups.

        Returns
        -------
        Dict[str, :class:`legacy.database.edb_data.hfss_simulation_setup_data.HfssSimulationSetup`] or
        Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveDCSimulationSetup`] or
        Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`]

        """

        setups = {}
        for i in list(self.active_cell.SimulationSetups):
            if i.GetType().ToString().endswith("kHFSS"):
                setups[i.GetName()] = HfssSimulationSetup(self, i)
            elif i.GetType().ToString().endswith("kSIWave"):
                setups[i.GetName()] = SiwaveSimulationSetup(self, i)
            elif i.GetType().ToString().endswith("kSIWaveDCIR"):
                setups[i.GetName()] = SiwaveDCSimulationSetup(self, i)
            elif i.GetType().ToString().endswith("kRaptorX"):
                setups[i.GetName()] = RaptorXSimulationSetup(self, i)
            elif i.GetType().ToString().endswith("kHFSSPI"):
                setups[i.GetName()] = HFSSPISimulationSetup(self, i)
        try:
            cpa_setup_name = self.active_cell.GetProductProperty(
                self._edb.ProductId.SIWave, SIwaveProperties.CPA_SIM_NAME
            )[-1]
        except:
            cpa_setup_name = ""
        if cpa_setup_name:
            from pyedb.dotnet.database.utilities.siwave_cpa_simulation_setup import (
                SIWaveCPASimulationSetup,
            )

            setups[cpa_setup_name] = SIWaveCPASimulationSetup(self, cpa_setup_name)
        return setups

    @property
    def hfss_setups(self):
        """Active HFSS setup in EDB.

        Returns
        -------
        Dict[str, :class:`legacy.database.edb_data.hfss_simulation_setup_data.HfssSimulationSetup`]

        """
        return {name: i for name, i in self.setups.items() if i.setup_type == "kHFSS"}

    @property
    def siwave_dc_setups(self):
        """Active Siwave DC IR Setups.

        Returns
        -------
        Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveDCSimulationSetup`]
        """
        return {name: i for name, i in self.setups.items() if isinstance(i, SiwaveDCSimulationSetup)}

    @property
    def siwave_ac_setups(self):
        """Active Siwave SYZ setups.

        Returns
        -------
        Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`]
        """
        return {name: i for name, i in self.setups.items() if isinstance(i, SiwaveSimulationSetup)}

    def create_hfss_setup(self, name=None):
        """Create an HFSS simulation setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`legacy.database.edb_data.hfss_simulation_setup_data.HfssSimulationSetup`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb()
        >>> setup1 = edbapp.create_hfss_setup("setup1")
        >>> setup1.hfss_port_settings.max_delta_z0 = 0.5
        """
        if name in self.setups:
            self.logger.info("setup already exists")
            return False
        elif not name:
            name = generate_unique_name("setup")
        setup = HfssSimulationSetup(self, name=name)
        setup.set_solution_single_frequency("1Ghz")
        return setup

    def create_raptorx_setup(self, name=None):
        """Create an RaptorX simulation setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`legacy.database.edb_data.raptor_x_simulation_setup_data.RaptorXSimulationSetup`

        """
        if name in self.setups:
            self.logger.error("Setup name already used in the layout")
            return False
        version = self.version.split(".")
        if int(version[0]) >= 2024 and int(version[-1]) >= 2 or int(version[0]) > 2024:
            setup = RaptorXSimulationSetup(self).create(name)
            return setup
        else:
            self.logger.error("RaptorX simulation only supported with Ansys release 2024R2 and higher")
            return False

    def create_hfsspi_setup(self, name=None):
        """Create an HFSS PI simulation setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`legacy.database.edb_data.hfss_pi_simulation_setup_data.HFSSPISimulationSetup when succeeded, ``False``
        when failed.

        """
        if name in self.setups:
            self.logger.error("Setup name already used in the layout")
            return False
        if float(self.version) < 2024.2:
            self.logger.error("HFSSPI simulation only supported with Ansys release 2024R2 and higher")
            return False
        return HFSSPISimulationSetup(self, name=name)

    def create_siwave_syz_setup(self, name=None, **kwargs):
        """Create a setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb()
        >>> setup1 = edbapp.create_siwave_syz_setup("setup1")
        >>> setup1.add_frequency_sweep(
        ...     frequency_sweep=[
        ...         ["linear count", "0", "1kHz", 1],
        ...         ["log scale", "1kHz", "0.1GHz", 10],
        ...         ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        ...     ]
        ... )
        """
        if not name:
            name = generate_unique_name("Siwave_SYZ")
        if name in self.setups:
            return False
        setup = SiwaveSimulationSetup(self, name=name)
        for k, v in kwargs.items():
            setattr(setup, k, v)
        return self.setups[name]

    def create_siwave_dc_setup(self, name=None, **kwargs):
        """Create a setup from a template.

        Parameters
        ----------
        name : str, optional
            Setup name.

        Returns
        -------
        :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb()
        >>> setup1 = edbapp.create_siwave_dc_setup("setup1")
        >>> setup1.mesh_bondwires = True

        """
        if not name:
            name = generate_unique_name("Siwave_DC")
        if name in self.setups:
            return False
        setup = SiwaveDCSimulationSetup(self, name=name)
        for k, v in kwargs.items():
            setattr(setup, k, v)
        return setup

    @execution_timer("calculate_initial_extent")
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
            nets.append(port.net_name)
        for port in self.sources.values():
            nets.append(port.net_name)
        nets = list(set(nets))
        max_width = 0
        for net in nets:
            for primitive in self.nets[net].primitives:
                if primitive.type == "Path":
                    max_width = max(max_width, primitive.width)

        for layer in list(self.stackup.dielectric_layers.values()):
            max_width = max(max_width, layer.thickness)

        max_width = max_width * expansion_factor
        self.logger.info("The W factor is {}, The initial extent = {:e}".format(expansion_factor, max_width))
        return max_width

    def copy_zones(self, working_directory=None):
        """Copy multizone EDB project to one new edb per zone.

        Parameters
        ----------
        working_directory : str
            Directory path where all EDB project are copied, if empty will use the current EDB project.

        Returns
        -------
           dict[str](int, EDB PolygonData)
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
        zone_primitives = list(self.layout.zone_primitives)
        zone_ids = list(self.stackup._layer_collection.GetZoneIds())
        edb_zones = {}
        if not self.setups:
            self.siwave.add_siwave_syz_analysis()
            self.save()
        for zone_primitive in zone_primitives:
            edb_zone_path = os.path.join(
                working_directory,
                "{}_{}".format(zone_primitive.GetId(), os.path.basename(self.edbpath)),
            )
            shutil.copytree(self.edbpath, edb_zone_path)
            poly_data = zone_primitive.GetPolygonData()
            if self._db.GetVersion()[0] >= 10:
                edb_zones[edb_zone_path] = (zone_primitive.GetZoneId(), poly_data)
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
            >>> zone_dict = edb.copy_zones("C:/Temp/test")

        common_reference_net : str
            the common reference net name. This net name must be provided to provide a valid project.

        Returns
        -------
        dict[str][str] , list of str
        first dictionary defined_ports with edb name as key and existing port name list as value. Those ports are the
        ones defined before processing the multizone clipping.
        second is the list of connected port.

        """
        terminals = {}
        defined_ports = {}
        project_connexions = None
        for edb_path, zone_info in zone_dict.items():
            edb = Edb(edbpath=edb_path)
            edb.cutout(
                use_pyaedt_cutout=True,
                custom_extent=zone_info[1],
                open_cutout_at_end=True,
            )
            if not zone_info[0] == -1:
                layers_to_remove = [
                    lay.name for lay in list(edb.stackup.layers.values()) if not lay._edb_layer.IsInZone(zone_info[0])
                ]
                for layer in layers_to_remove:
                    edb.stackup.remove_layer(layer)
            edb.stackup.stackup_mode = "Laminate"
            edb.cutout(
                use_pyaedt_cutout=True,
                custom_extent=zone_info[1],
                open_cutout_at_end=True,
            )
            edb.active_cell.SetName(os.path.splitext(os.path.basename(edb_path))[0])
            if common_reference_net:
                signal_nets = list(self.nets.signal.keys())
                defined_ports[os.path.splitext(os.path.basename(edb_path))[0]] = list(edb.excitations.keys())
                edb_terminals_info = edb.hfss.create_vertical_circuit_port_on_clipped_traces(
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

    def _get_connected_ports_from_multizone_cutout(self, terminal_info_dict):
        """Return connected port list from clipped multizone layout.

        Parameters
            terminal_info_dict : dict[str][str]
                dictionary terminals with edb name as key and created ports name on clipped signal nets.
                Dictionary is generated by the command cutout_multizone_layout:
                >>> edb = Edb(edb_file)
                >>> edb_zones = edb.copy_zones("C:/Temp/test")
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

        Parameters
        ----------
        terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            Positive terminal of the port.
        ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            optional
            Negative terminal of the port.
        is_circuit_port : bool, optional
            Whether it is a circuit port. The default is ``False``.
        name: str, optional
            Name of the created port. The default is None, a random name is generated.
        Returns
        -------
        list: [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
            :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,].
        """

        terminal.boundary_type = "PortBoundary"
        terminal.is_circuit_port = is_circuit_port

        if ref_terminal:
            ref_terminal.boundary_type = "PortBoundary"
            terminal.ref_terminal = ref_terminal
        if name:
            terminal.name = name

        if terminal.is_circuit_port:
            port = CircuitPort(self, terminal._edb_object)
        elif terminal.terminal_type == "BundleTerminal":
            port = BundleWavePort(self, terminal._edb_object)
        elif terminal.hfss_type == "Wave":
            port = WavePort(self, terminal._edb_object)
        elif terminal.terminal_type == "PadstackInstanceTerminal":
            port = CoaxPort(self, terminal._edb_object)
        else:
            port = GapPort(self, terminal._edb_object)
        return port

    def create_voltage_probe(self, terminal, ref_terminal):
        """Create a voltage probe.

        Parameters
        ----------
        terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            Positive terminal of the port.
        ref_terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
            Negative terminal of the probe.

        Returns
        -------
        pyedb.dotnet.database.edb_data.terminals.Terminal
        """
        term = Terminal(self, terminal._edb_object)
        term.boundary_type = "kVoltageProbe"

        ref_term = Terminal(self, ref_terminal._edb_object)
        ref_term.boundary_type = "kVoltageProbe"

        term.ref_terminal = ref_terminal
        return self.probes[term.name]

    def create_voltage_source(self, terminal, ref_terminal):
        """Create a voltage source.

        Parameters
        ----------
        terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
            Positive terminal of the port.
        ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`, \
            :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
            Negative terminal of the source.

        Returns
        -------
        class:`legacy.database.edb_data.ports.ExcitationSources`
        """
        term = Terminal(self, terminal._edb_object)
        term.boundary_type = "kVoltageSource"

        ref_term = Terminal(self, ref_terminal._edb_object)
        ref_term.boundary_type = "kVoltageSource"

        term.ref_terminal = ref_terminal
        return self.sources[term.name]

    def create_current_source(self, terminal, ref_terminal):
        """Create a current source.

        Parameters
        ----------
        terminal : :class:`legacy.database.edb_data.terminals.EdgeTerminal`,
            :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`legacy.database.edb_data.terminals.PointTerminal`,
            :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
            Positive terminal of the port.
        ref_terminal : class:`legacy.database.edb_data.terminals.EdgeTerminal`,
            :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
            :class:`legacy.database.edb_data.terminals.PointTerminal`,
            :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
            Negative terminal of the source.

        Returns
        -------
        :class:`legacy.edb_core.edb_data.ports.ExcitationSources`
        """
        term = Terminal(self, terminal._edb_object)
        term.boundary_type = "kCurrentSource"

        ref_term = Terminal(self, ref_terminal._edb_object)
        ref_term.boundary_type = "kCurrentSource"

        term.ref_terminal = ref_terminal
        return self.sources[term.name]

    def get_point_terminal(self, name, net_name, location, layer):
        """Place a voltage probe between two points.

        Parameters
        ----------
        name : str,
            Name of the terminal.
        net_name : str
            Name of the net.
        location : list
            Location of the terminal.
        layer : str,
            Layer of the terminal.

        Returns
        -------
        :class:`legacy.edb_core.edb_data.terminals.PointTerminal`
        """
        from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal

        point_terminal = PointTerminal(self)
        return point_terminal.create(name, net_name, location, layer)

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
        """Assign automatically design and project variables with current values.

        Parameters
        ----------
        layers : bool, optional
            Enable layer thickness parametrization. Default value is ``True``.
        materials : bool, optional
            Enable material parametrization. Default value is ``True``.
        via_holes : bool, optional
            Enable via diameter parametrization. Default value is ``True``.
        pads : bool, optional
            Enable pads size parametrization. Default value is ``True``.
        antipads : bool, optional
            Enable anti pads size parametrization. Default value is ``True``.
        traces : bool, optional
            Enable trace width parametrization. Default value is ``True``.
        layer_filter : str, List(str), optional
            Enable layer filter. Default value is ``None``, all layers are parametrized.
        material_filter : str, List(str), optional
            Enable material filter. Default value is ``None``, all material are parametrized.
        padstack_definition_filter : str, List(str), optional
            Enable padstack definition filter. Default value is ``None``, all padsatcks are parametrized.
        trace_net_filter : str, List(str), optional
            Enable nets filter for trace width parametrization. Default value is ``None``, all layers are parametrized.
        use_single_variable_for_padstack_definitions : bool, optional
            Whether to use a single design variable for each padstack definition or a variable per pad layer.
            Default value is ``True``.
        use_relative_variables : bool, optional
            Whether if use an absolute variable for each trace, padstacks and layers or a delta variable instead.
            Default value is ``True``.
        output_aedb_path : str, optional
            Full path and name for the new AEDB file. If None, then current aedb will be cutout.
        open_aedb_at_end : bool, optional
            Whether to open the cutout at the end. The default is ``True``.
        expand_polygons_size : float, optional
            Expansion size on polygons. Polygons will be expanded in all directions. The default is ``0``.
        expand_voids_size : float, optional
            Expansion size on polygon voids. Polygons voids will be expanded in all directions. The default is ``0``.
        via_offset : bool, optional
            Whether if offset the via position or not. The default is ``True``.

        Returns
        -------
        List(str)
            List of all parameters name created.
        """
        edb_original_path = self.edbpath
        if output_aedb_path:
            self.save_edb_as(output_aedb_path)
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
                    self.add_design_variable(var, 0.0)
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
                layer.thickness = var
                parameters.append(val)
        if materials:
            if not material_filter:
                _materials = self.materials.materials
            else:
                _materials = {k: v for k, v in self.materials.materials.items() if k in material_filter}
            for mat_name, material in _materials.items():
                if material.conductivity < 1e4:
                    var, val = _apply_variable(f"$epsr_{mat_name}", material.permittivity)
                    material.permittivity = var
                    parameters.append(val)
                    var, val = _apply_variable(f"$loss_tangent_{mat_name}", material.dielectric_loss_tangent)
                    material.dielectric_loss_tangent = var
                    parameters.append(val)
                else:
                    var, val = _apply_variable(f"$sigma_{mat_name}", material.conductivity)
                    material.conductivity = var
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
                path.width = var
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
            if not padstack_def.via_start_layer == padstack_def.via_stop_layer:
                if via_holes:  # pragma no cover
                    if use_relative_variables:
                        hole_variable = "$hole_diameter"
                    else:
                        hole_variable = f"${def_name}_hole_diameter"
                    var, val = _apply_variable(hole_variable, padstack_def.hole_diameter_string)
                    padstack_def.hole_properties = var
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
            self.save_edb()
            self.close_edb()
            self.edbpath = edb_original_path
            self.open_edb()
        return parameters

    def _clean_string_for_variable_name(self, variable_name):
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
        """Generate EDB design to be consumed by PyAEDT to generate arbitrary wave ports shapes.
        This model has to be considered as merged onto another one. The current opened design must have voids
        surrounding the pad-stacks where wave ports terminal will be created. THe open design won't be edited, only
        primitives like voids and pads-stack definition included in the voids are collected to generate a new design.

        Parameters
        ----------
        temp_directory : str
            Temporary directory used during the method execution.

        mounting_side : str
            Gives the orientation to be considered for the current design. 2 options are available ``"top"`` and
            ``"bottom". Default value is ``"top"``. If ``"top"`` is selected the method will voids at the top signal
            layer, and the bottom layer if ``"bottom"`` is used.

        signal_nets : List[str], optional
            Provides the nets to be included for the model creation. Default value is ``None``. If None is provided,
            all nets will be included.

        terminal_diameter : float, str, optional
            When ``None``, the terminal diameter is evaluated at each pads-tack instance found inside the voids. The top
            or bottom layer pad diameter will be taken, depending on ``mounting_side`` selected. If value is provided,
            it will overwrite the evaluated diameter.

        output_edb : str, optional
            The output EDB absolute. If ``None`` the edb is created in the ``temp_directory`` as default name
            `"waveport_model.aedb"``

        launching_box_thickness : float, str, optional
            Launching box thickness  used for wave ports. Default value is ``"100um"``.

        Returns
        -------
        bool
            ``True`` when succeeded, ``False`` if failed.
        """
        if not temp_directory:
            raise RuntimeWarning("Temp directory must be provided when creating model foe arbitrary wave port")
        if mounting_side not in ["top", "bottom"]:
            raise RuntimeWarning(
                "Mounting side must be provided and only `top` or `bottom` are supported. Setting to "
                "`top` will take the top layer from the current design as reference. Setting to `bottom` "
                "will take the bottom one."
            )
        if not output_edb:
            output_edb = os.path.join(temp_directory, "waveport_model.aedb")
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
                if padstack_inst.net_name in signal_nets:
                    padstack_instances_index.insert(padstack_inst.id, padstack_inst.position)
                    if not padstack_inst.padstack_definition in used_padstack_defs:
                        used_padstack_defs.append(padstack_inst.padstack_definition)

        polys = [
            poly
            for poly in self.modeler.primitives
            if poly.layer_name == reference_layer and poly.type == "Polygon" and poly.has_voids
        ]
        if not polys:
            raise RuntimeWarning(
                f"No polygon found with voids on layer {reference_layer} during model creation for arbitrary wave ports"
            )
        void_padstacks = []
        for poly in polys:
            for void in poly.voids:
                void_bbox = (
                    void.polygon_data._edb_object.GetBBox().Item1.X.ToDouble(),
                    void.polygon_data._edb_object.GetBBox().Item1.Y.ToDouble(),
                    void.polygon_data._edb_object.GetBBox().Item2.X.ToDouble(),
                    void.polygon_data._edb_object.GetBBox().Item2.Y.ToDouble(),
                )
                included_instances = list(padstack_instances_index.intersection(void_bbox))
                if included_instances:
                    void_padstacks.append((void, [self.padstacks.instances[edb_id] for edb_id in included_instances]))

        if not void_padstacks:
            raise RuntimeWarning(
                "No padstack instances found inside evaluated voids during model creation for arbitrary waveports"
            )
        cloned_edb = Edb(edbpath=output_edb)

        cloned_edb.stackup.add_layer(
            layer_name="ports",
            layer_type="signal",
            thickness=self.stackup.signal_layers[reference_layer].thickness,
            material="pec",
        )
        if launching_box_thickness:
            launching_box_thickness = self.edb_value(launching_box_thickness).ToString()
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
                main_shape=void_info[0].polygon_data._edb_object, layer_name="ref", net_name="GND"
            )
            port_poly.scale(1.1)
            pec_poly = cloned_edb.modeler.create_polygon(
                main_shape=port_poly.polygon_data._edb_object, layer_name="port_pec", net_name="GND"
            )
            pec_poly.scale(1.5)

        for void_info in void_padstacks:
            for inst in void_info[1]:
                if not terminal_diameter:
                    pad_diameter = (
                        self.padstacks.definitions[inst.padstack_definition]
                        .pad_by_layer[reference_layer]
                        .parameters_values[0]
                    )
                else:
                    pad_diameter = self.edb_value(terminal_diameter).ToDouble()
                _temp_circle = cloned_edb.modeler.create_circle(
                    layer_name="ports",
                    x=inst.position[0],
                    y=inst.position[1],
                    radius=pad_diameter / 2,
                    net_name=inst.net_name,
                )
                if not _temp_circle:
                    raise RuntimeWarning(
                        f"Failed to create circle for terminal during create_model_for_arbitrary_wave_ports"
                    )
        cloned_edb.save_as(output_edb)
        cloned_edb.close()
        return True

    @property
    def definitions(self):
        """Definitions class."""
        from pyedb.dotnet.database.definition.definitions import Definitions

        return Definitions(self)

    @property
    def workflow(self):
        """Workflow class."""
        return Workflow(self)

    def export_gds_comp_xml(self, comps_to_export, gds_comps_unit="mm", control_path=None):
        """Exports an XML file with selected components information for use in a GDS import.

        Parameters
        ----------
        comps_to_export : list
            List of components whose information will be exported to xml file.
        gds_comps_unit : str, optional
            GDS_COMPONENTS section units. Default is ``"mm"``.
        control_path : str, optional
            Path for outputting the XML file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        from pyedb.generic.general_methods import ET

        components = ET.Element("GDS_COMPONENTS")
        components.set("LengthUnit", gds_comps_unit)
        if not comps_to_export:
            comps_to_export = self.components.components
        for comp in comps_to_export:
            ocomp = self.components.components[comp]
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

    def get_variable_value(self, variable_name):
        """Added to get closer architecture as for grpc."""
        if variable_name in self.variables:
            return self.variables[variable_name]
        else:
            return False

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
            return str(Path(self.base_path).joinpath("EDBDiff.exe"))
        except subprocess.CalledProcessError as e:  # nosec
            raise RuntimeError(
                "EDBDiff.exe execution failed. Please check if the executable is present in the base path."
            ) from e
