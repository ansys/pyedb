"""Database."""
import os
import sys
import ansys.edb

from pyedb import __version__
from pyedb.edb_logger import pyedb_logger
from pyedb.generic.general_methods import settings
from ansys.edb.session import launch_session
from pyedb.misc.misc import list_installed_ansysem
from pyedb.generic.general_methods import env_path
from pyedb.generic.general_methods import env_path_student
from pyedb.generic.general_methods import env_value
from pyedb.generic.general_methods import is_linux


class EdbInit(object):
    """Edb Dot Net Class."""

    def __init__(self, edbversion, port):
        self._global_logger = pyedb_logger
        self.logger = pyedb_logger
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
        self.server_pid = 0
        if is_linux:  # pragma: no cover
            if env_value(self.edbversion) in os.environ:
                self.base_path = env_path(self.edbversion)
                sys.path.append(self.base_path)
            else:
                main = sys.modules["__main__"]
                edb_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
                if edb_path:
                    self.base_path = edb_path
                    sys.path.append(edb_path)
                    os.environ[env_value(self.edbversion)] = self.base_path
        else:
            self.base_path = env_path(self.edbversion)
            sys.path.append(self.base_path)
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oaDirectory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)
        "Starting grpc server"
        self.session = launch_session(self.base_path, port_num=port)
        if self.session:
            self.server_pid = self.session.local_server_proc.pid
            self.logger.info("Grpc session started")

    @property
    def db(self):
        """Active database object."""
        return self._db


    def create(self, db_path):
        """Create a Database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level database folder

        Returns
        -------
        Database
        """
        self._db = self.edb_api.database.Create(db_path)
        return self._db

    def open(self, db_path, read_only):
        """Open an existing Database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level Database folder.
        read_only : bool
            Obtain read-only access.

        Returns
        -------
        Database or None
            The opened Database object, or None if not found.
        """
        self._db = self.edb_api.database.Open(
            db_path,
            read_only,
        )
        return self._db

    def delete(self, db_path):
        """Delete a database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level database folder.
        """
        return self.edb_api.database.Delete(db_path)

    def save(self):
        """Save any changes into a file."""
        return self._db.Save()

    def close(self):
        """Close the database.

        .. note::
            Unsaved changes will be lost.
        """
        return self._db.Close()

    @property
    def top_circuit_cells(self):
        """Get top circuit cells.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [CellClassDotNet(self, i) for i in list(self._db.TopCircuitCells)]

    @property
    def circuit_cells(self):
        """Get all circuit cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [CellClassDotNet(self, i) for i in list(self._db.CircuitCells)]

    @property
    def footprint_cells(self):
        """Get all footprint cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [CellClassDotNet(self, i) for i in list(self._db.FootprintCells)]

    @property
    def edb_uid(self):
        """Get ID of the database.

        Returns
        -------
        int
            The unique EDB id of the Database.
        """
        return self._db.GetId()

    @property
    def is_read_only(self):
        """Determine if the database is open in a read-only mode.

        Returns
        -------
        bool
            True if Database is open with read only access, otherwise False.
        """
        return self._db.IsReadOnly()

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
        self.edb_api.database.FindById(db_id)

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
        return self._db.GetProductProperty(prod_id, attr_it)

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
        self._db.SetProductProperty(prod_id, attr_it, prop_value)

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
        return self._db.GetProductPropertyIds(prod_id)

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
        self._db.ImportMaterialFromControlFile(
            control_file,
            schema_dir,
            append,
        )

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
        return self._db.Scale(scale_factor)

    @property
    def source(self):
        """Get source name for this Database.

        This attribute is also used to set the source name.

        Returns
        -------
        str
            name of the source
        """
        return self._db.GetSource()

    @source.setter
    def source(self, source):
        """Set source name of the database."""
        self._db.SetSource(source)

    @property
    def source_version(self):
        """Get the source version for this Database.

        This attribute is also used to set the version.

        Returns
        -------
        str
            version string

        """
        return self._db.GetSourceVersion()

    @source_version.setter
    def source_version(self, source_version):
        """Set source version of the database."""
        self._db.SetSourceVersion(source_version)

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

    @property
    def apd_bondwire_defs(self):
        """Get all APD bondwire definitions in this Database.

        Returns
        -------
        list[:class:`ApdBondwireDef <ansys.edb.definition.ApdBondwireDef>`]
        """
        return list(self._db.APDBondwireDefs)

    @property
    def jedec4_bondwire_defs(self):
        """Get all JEDEC4 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec4BondwireDef <ansys.edb.definition.Jedec4BondwireDef>`]
        """
        return list(self._db.Jedec4BondwireDefs)

    @property
    def jedec5_bondwire_defs(self):
        """Get all JEDEC5 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec5BondwireDef <ansys.edb.definition.Jedec5BondwireDef>`]
        """
        return list(self._db.Jedec5BondwireDefs)

    @property
    def padstack_defs(self):
        """Get all Padstack definitions in this Database.

        Returns
        -------
        list[:class:`PadstackDef <ansys.edb.definition.PadstackDef>`]
        """
        return list(self._db.PadstackDefs)

    @property
    def package_defs(self):
        """Get all Package definitions in this Database.

        Returns
        -------
        list[:class:`PackageDef <ansys.edb.definition.PackageDef>`]
        """
        return list(self._db.PackageDefs)

    @property
    def component_defs(self):
        """Get all component definitions in the database.

        Returns
        -------
        list[:class:`ComponentDef <ansys.edb.definition.ComponentDef>`]
        """
        return list(self._db.ComponentDefs)

    @property
    def material_defs(self):
        """Get all material definitions in the database.

        Returns
        -------
        list[:class:`MaterialDef <ansys.edb.definition.MaterialDef>`]
        """
        return list(self._db.MaterialDefs)

    @property
    def dataset_defs(self):
        """Get all dataset definitions in the database.

        Returns
        -------
        list[:class:`DatasetDef <ansys.edb.definition.DatasetDef>`]
        """
        return list(self._db.DatasetDefs)

