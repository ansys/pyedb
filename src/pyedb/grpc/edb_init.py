# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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


"""Database."""
import os
import sys

import ansys.edb.core.database as database

from pyedb import __version__
from pyedb.edb_logger import pyedb_logger
from pyedb.generic.general_methods import env_path, env_value, is_linux
from pyedb.grpc.rpc_session import RpcSession
from pyedb.misc.misc import list_installed_ansysem


class EdbInit(object):
    """Edb Dot Net Class."""

    def __init__(self, edbversion):
        self.logger = pyedb_logger
        self._db = None
        if not edbversion:  # pragma: no cover
            try:
                edbversion = "20{}.{}".format(list_installed_ansysem()[0][-3:-1], list_installed_ansysem()[0][-1:])
                self.logger.info("Edb version " + edbversion)
            except IndexError:
                raise Exception("No ANSYSEM_ROOTxxx is found.")
        self.edbversion = edbversion
        self.logger.info("Logger is initialized in EDB.")
        self.logger.info("legacy v%s", __version__)
        self.logger.info("Python version %s", sys.version)
        self.session = None
        if is_linux:
            if env_value(self.edbversion) in os.environ:
                self.base_path = env_path(self.edbversion)
                sys.path.append(self.base_path)
            else:
                edb_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
                if edb_path:
                    self.base_path = edb_path
                    sys.path.append(edb_path)
                    os.environ[env_value(self.edbversion)] = self.base_path
        else:
            self.base_path = env_path(self.edbversion)
            sys.path.append(self.base_path)
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oa_directory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oa_directory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)

    @property
    def db(self):
        """Active database object."""
        return self._db

    def create(self, db_path, port=0, restart_rpc_server=False, kill_all_instances=False):
        """Create a Database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level database folder

        restart_rpc_server : optional, bool
            Force restarting RPC server when `True`.Default value is `False`

        kill_all_instances : optional, bool.
            Force killing all RPC server instances, must be used with caution. Default value is `False`.

        Returns
        -------
        Database
        """
        if not RpcSession.pid:
            RpcSession.start(
                edb_version=self.edbversion,
                port=port,
                restart_server=restart_rpc_server,
                kill_all_instances=kill_all_instances,
            )
            if not RpcSession.pid:
                self.logger.error("Failed to start RPC server.")
                return False
        self._db = database.Database.create(db_path)
        return self._db

    def open(self, db_path, read_only, port=0, restart_rpc_server=False, kill_all_instances=False):
        """Open an existing Database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level Database folder.
        read_only : bool
            Obtain read-only access.
        port : optional, int.
            Specify the port number.If not provided a randon free one is selected. Default value is `0`.
        restart_rpc_server : optional, bool
            Force restarting RPC server when `True`. Default value is `False`.
        kill_all_instances : optional, bool.
            Force killing all RPC server instances, must be used with caution. Default value is `False`.

        Returns
        -------
        Database or None
            The opened Database object, or None if not found.
        """
        if restart_rpc_server:
            RpcSession.pid = 0
        if not RpcSession.pid:
            RpcSession.start(
                edb_version=self.edbversion,
                port=port,
                restart_server=restart_rpc_server,
                kill_all_instances=kill_all_instances,
            )
            if not RpcSession.pid:
                self.logger.error("Failed to start RPC server.")
                return False
        self._db = database.Database.open(db_path, read_only)

    def delete(self, db_path):
        """Delete a database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level database folder.
        """
        return database.Database.delete(db_path)

    def save(self):
        """Save any changes into a file."""
        return self._db.save()

    def close(self, terminate_rpc_session=True, kill_all_instances=False):
        """Close the database.

        Parameters
        ----------
        terminate_rpc_session : bool, optional


        . note::
            Unsaved changes will be lost.
        """
        self._db.close()
        self._db = None
        if kill_all_instances:
            RpcSession._kill_all_instances()
            RpcSession.pid = 0
        elif terminate_rpc_session:
            RpcSession.rpc_session.disconnect()
            RpcSession.pid = 0
        return True

    @property
    def top_circuit_cells(self):
        """Get top circuit cells.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [i for i in self._db.top_circuit_cells]

    @property
    def circuit_cells(self):
        """Get all circuit cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [i for i in self._db.circuit_cells]

    @property
    def footprint_cells(self):
        """Get all footprint cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [i for i in self._db.footprint_cells]

    @property
    def edb_uid(self):
        """Get ID of the database.

        Returns
        -------
        int
            The unique EDB id of the Database.
        """
        return self._db.id

    @property
    def is_read_only(self):
        """Determine if the database is open in a read-only mode.

        Returns
        -------
        bool
            True if Database is open with read only access, otherwise False.
        """
        return self._db.is_read_only

    def find_by_id(self, db_id):
        """Find a database by ID.

        Parameters
        ----------
        db_id : int
            The Database's unique EDB id.

        Returns
        -------
        Database
            The Database or Null on failure.
        """
        return database.Database.find_by_id(db_id)

    def save_as(self, path, version=""):
        """Save this Database to a new location and older EDB version.

        Parameters
        ----------
        path : str
            New Database file location.
        version : str
            EDB version to save to. Empty string means current version.
        """
        self._db.save_as(path, version)

    @property
    def directory(self):
        """Get the directory of the Database.

        Returns
        -------
        str
            Directory of the Database.
        """
        return self._db.directory

    def get_product_property(self, prod_id, attr_it):
        """Get the product-specific property value.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.
        attr_it : int
            Attribute ID.

        Returns
        -------
        str
            Property value returned.
        """
        return self._db.get_product_property(prod_id, attr_it)

    def set_product_property(self, prod_id, attr_it, prop_value):
        """Set the product property associated with the given product and attribute ids.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.
        attr_it : int
            Attribute ID.
        prop_value : str
            Product property's new value
        """
        self._db.set_product_property(prod_id, attr_it, prop_value)

    def get_product_property_ids(self, prod_id):
        """Get a list of attribute ids corresponding to a product property id.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.

        Returns
        -------
        list[int]
            The attribute ids associated with this product property.
        """
        return self._db.get_product_property_ids(prod_id)

    def import_material_from_control_file(self, control_file, schema_dir=None, append=True):
        """Import materials from the provided control file.

        Parameters
        ----------
        control_file : str
            Control file name with full path.
        schema_dir : str
            Schema file path.
        append : bool
            True if the existing materials in Database are kept. False to remove existing materials in database.
        """
        self._db.import_material_from_control_file(control_file, schema_dir, append)

    @property
    def version(self):
        """Get version of the Database.

        Returns
        -------
        tuple(int, int)
            A tuple of the version numbers [major, minor]
        """
        major, minor = self._db.version
        return major, minor

    def scale(self, scale_factor):
        """Uniformly scale all geometry and their locations by a positive factor.

        Parameters
        ----------
        scale_factor : float
            Amount that coordinates are multiplied by.
        """
        return self._db.scale(scale_factor)

    @property
    def source(self):
        """Get source name for this Database.

        This attribute is also used to set the source name.

        Returns
        -------
        str
            name of the source
        """
        return self._db.source

    @source.setter
    def source(self, source):
        """Set source name of the database."""
        self._db.source = source

    @property
    def source_version(self):
        """Get the source version for this Database.

        This attribute is also used to set the version.

        Returns
        -------
        str
            version string

        """
        return self._db.source_version

    @source_version.setter
    def source_version(self, source_version):
        """Set source version of the database."""
        self._db.source_version = source_version

    def copy_cells(self, cells_to_copy):
        """Copy Cells from other Databases or this Database into this Database.

        Parameters
        ----------
        cells_to_copy : list[:class:`Cell <ansys.edb.core.layout.cell.Cell>`]
            Cells to copy.

        Returns
        -------
        list[:class:`Cell <ansys.edb.core.layout.cell.Cell>`]
        """
        if not isinstance(cells_to_copy, list):
            cells_to_copy = [cells_to_copy]
        return self._db.copy_cells(cells_to_copy)

    @property
    def apd_bondwire_defs(self):
        """Get all APD bondwire definitions in this Database.

        Returns
        -------
        list[:class:`ApdBondwireDef <ansys.edb.definition.ApdBondwireDef>`]
        """
        return list(self._db.apd_bondwire_defs)

    @property
    def jedec4_bondwire_defs(self):
        """Get all JEDEC4 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec4BondwireDef <ansys.edb.definition.Jedec4BondwireDef>`]
        """
        return list(self._db.jedec4_bondwire_defs)

    @property
    def jedec5_bondwire_defs(self):
        """Get all JEDEC5 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec5BondwireDef <ansys.edb.definition.Jedec5BondwireDef>`]
        """
        return list(self._db.jedec5_bondwire_defs)

    @property
    def padstack_defs(self):
        """Get all Padstack definitions in this Database.

        Returns
        -------
        list[:class:`PadstackDef <ansys.edb.definition.PadstackDef>`]
        """
        return list(self._db.padstack_defs)

    @property
    def package_defs(self):
        """Get all Package definitions in this Database.

        Returns
        -------
        list[:class:`PackageDef <ansys.edb.definition.PackageDef>`]
        """
        return list(self._db.package_defs)

    @property
    def component_defs(self):
        """Get all component definitions in the database.

        Returns
        -------
        list[:class:`ComponentDef <ansys.edb.definition.ComponentDef>`]
        """
        return list(self._db.component_defs)

    @property
    def material_defs(self):
        """Get all material definitions in the database.

        Returns
        -------
        list[:class:`MaterialDef <ansys.edb.definition.MaterialDef>`]
        """
        return list(self._db.material_defs)

    @property
    def dataset_defs(self):
        """Get all dataset definitions in the database.

        Returns
        -------
        list[:class:`DatasetDef <ansys.edb.definition.DatasetDef>`]
        """
        return list(self._db.dataset_defs)
